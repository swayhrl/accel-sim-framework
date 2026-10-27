"""Read-only runtime-frame adapter candidate. No installation/dispatch on import.
PSS scanning is cached30s; existing owner and provider gates remain authoritative.
"""
import copy,hashlib,json,os,pathlib,re,threading,time
P=pathlib.Path
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()

class RuntimeFrames:
    def __init__(self,root,engine,res,consumer,effective_rows,pss_refresh_seconds=30,observe=None,generation=None):
        self.root=P(root);self.engine=engine;self.res=res;self.consumer=consumer;self.effective_rows=effective_rows
        assert 30<=pss_refresh_seconds<=60
        self.refresh=pss_refresh_seconds;self.observe=observe or self.observe_native
        self.generation=generation or self.read_generation
        self.pss={};self.last_pss_refresh=float('-inf');self.completion_cache={};self.last_frame=None
        qualification=self.root/'control/ACTUAL_CANARY_QUALIFICATION.json'
        # One immutable broad-qualification witness, never spec/retry mtime.
        self.first_eligible=time.monotonic()-max(0,time.time()-qualification.stat().st_mtime)
        self.first_eligible_source=dict(path=str(qualification),sha256=sha(qualification),mtime_ns=qualification.stat().st_mtime_ns)

    def assert_owner(self):
        assert threading.current_thread()is threading.main_thread()
        _,_,q,plan=self.engine.registered();assert q['request']==REQ
        assert os.getpid()==plan['parent_pid']and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==plan['parent_start_ticks']
        self.engine.assert_parent_lease()

    def observe_native(self,cohort,uuid):
        out=self.root/'DTC/run/results'/uuid;proof=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');pid=proof['pid'];start=proof['start_ticks']
        proc=P('/proc')/str(pid);fields=proc.joinpath('stat').read_text().rsplit(')',1)[1].split()
        if int(fields[19])!=start or fields[0]in('Z','X'):return None
        env=dict(p.split('=',1)for p in proc.joinpath('environ').read_bytes().decode(errors='replace').split('\0')if'='in p)
        if env.get('DTC_AG7_GENERATION')!=uuid:return None
        smaps=proc.joinpath('smaps_rollup').read_text();match=re.search(r'^Pss_Anon:\s+(\d+)\s+kB',smaps,re.M)
        if not match:return None # no RSS substitute for missing anonymous PSS
        if int(proc.joinpath('stat').read_text().rsplit(')',1)[1].split()[19])!=start:return None
        return dict(cohort=cohort,uuid=uuid,pid=pid,start_ticks=start,anon_PSS_bytes=int(match.group(1))*1024,
                    PSS_sample_monotonic=time.monotonic(),source='read-only Pss_Anon smaps_rollup + PID/start/generation',
                    native_pid_proof_path=str(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'),native_pid_proof_sha256=sha(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'))

    def read_generation(self,cohort,uuid):
        try:
            native=read(self.root/'DTC/run/results'/uuid/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
            fields=P('/proc',str(native['pid']),'stat').read_text().rsplit(')',1)[1].split()
            if int(fields[19])!=native['start_ticks']or fields[0]in('Z','X'):return None
            return native
        except(OSError,KeyError,ProcessLookupError,ValueError):return None

    def __call__(self,pending,sample,claims,history,previous,policy,dispatch_index):
        now=time.monotonic();_,_,q,_=self.engine.registered();matrix=read(self.root/'control/MATRIX_CURRENT.json')
        points={p['cohort']:p for p in matrix['points']};reference=next(iter(q['consumed']))
        baseline=self.res.resources({'cohort':reference},True)
        if 'additional_padding_admission_proof'in baseline:
            own=self.effective_rows(baseline);padding=baseline['additional_padding_admission_proof']
            discounts={x['cohort']:x['discount_bytes']for x in padding['discount_rows']}
        else:
            own=copy.deepcopy(baseline['own_ram_forecasts']);discounts={}
        # Only actual LIVE_MODEL rows can be projected as removable on natural
        # drain. Claims and uncertain generations remain in total/retained terms.
        live_rows=[r for r in own if r['kind']=='LIVE_MODEL'and r['cohort']in q['consumed']and 'execution_receipt'not in q['consumed'][r['cohort']]]
        if now-self.last_pss_refresh>=self.refresh:
            cache={}
            for row in live_rows:
                c=row['cohort'];uuid=q['consumed'][c]['uuid']
                try:v=self.observe(c,uuid)
                except(OSError,ValueError,KeyError,ProcessLookupError):v=None
                if v:cache[(c,uuid)]=v
            self.pss=cache;self.last_pss_refresh=time.monotonic()
        own_live=[];active=set()
        for row in own:
            point=points.get(row['cohort'])
            if point:active.add(point['input_digest'])
        for row in live_rows:
            c=row['cohort'];uuid=q['consumed'][c]['uuid'];cached=self.pss.get((c,uuid))
            native=self.generation(c,uuid)
            if native is None:continue
            if cached and(cached['pid']!=native['pid']or cached['start_ticks']!=native['start_ticks']):cached=None
            own_live.append(dict(cohort=c,uuid=uuid,pid=native['pid'],start_ticks=native['start_ticks'],RSS_bytes=row['RSS_bytes'],
                effective_future_bytes=row['additional_reserved_bytes'],anon_PSS_bytes=cached['anon_PSS_bytes']if cached else None,
                PSS_sample_monotonic=cached['PSS_sample_monotonic']if cached else None))
        consumed={};closures=[]
        for c,value in q['consumed'].items():
            d=value.get('execution_receipt');terminal=bool(d)
            consumed[c]=dict(uuid=value['uuid'],terminal=terminal)
            if not d:continue
            natural=d.get('stop_reason')is None and d.get('launcher_wait_returncode')==0
            accepted=False;rp=self.root/'analysis'/(c+'.RESULT.json')
            if rp.exists():
                marker=(str(rp),rp.stat().st_size,rp.stat().st_mtime_ns)
                if marker not in self.completion_cache:
                    v=read(rp);self.completion_cache[marker]=bool(v.get('uuid')==value['uuid']and self.consumer.accepted(v))
                accepted=self.completion_cache[marker]
            closures.append(dict(cohort=c,uuid=value['uuid'],natural_done=natural,
                accepted_strict_archive_restore=natural and accepted,
                DONE_path=str(self.root/'control/qualification_ledger'/(c+'.DONE.json')),
                strict_result_path=str(rp)if rp.exists()else None))
        costs=[]
        for spec in pending:
            forecast=self.res.forecast(spec,history,policy)
            costs.append(dict(cohort=spec['cohort'],input_digest=spec['input_digest'],program=spec['program'],cell=spec['cell'],profile=spec['profile'],
                cost_bytes=max(spec['estimated_peak_model_RAM_bytes'],forecast['predicted_peak_RAM_bytes']),first_eligible_monotonic=self.first_eligible))
        started={points[c]['program']for c in q['consumed']if c in points}
        frame=dict(now=time.monotonic(),budget_bytes=baseline['admission_decision']['admission_RAM_budget_bytes'],
            effective_total_growth_bytes=baseline['total_projected_additional_RAM_bytes'],memory_utilization_fraction=baseline['admission_decision']['memory_utilization_fraction'],
            total_padding_discount_bytes=sum(discounts.values()),padding_discount_by_cohort=discounts,
            accounted_growth_by_cohort={r['cohort']:r['additional_reserved_bytes']for r in own},
            own_live=own_live,consumed=consumed,claim_cohorts=list(claims),closures=closures,pending=costs,
            active_input_digests=list(active),started_programs=list(started),pressure_reasons=baseline['admission_decision']['pressure_reasons'],
            baseline_resource_UTC=baseline['utc'],first_eligibility_witness=self.first_eligible_source,
            cached_PSS_refresh_seconds=self.refresh,PSS_sample_count=len(self.pss),
            base_resource_forecasts_unchanged=True,candidate_predictions_full_original=True)
        self.last_frame=frame;return frame
