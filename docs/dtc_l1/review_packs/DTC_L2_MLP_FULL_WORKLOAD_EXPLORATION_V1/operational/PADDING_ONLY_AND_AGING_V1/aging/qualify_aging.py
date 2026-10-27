"""CPU-only fairness/credit/owner-instance qualification. No real models/signals."""
import copy,hashlib,importlib.util,json,pathlib,types,os,time
from large_job_aging import AgingState,AgingChooser,G
P=pathlib.Path

def candidate(name='LAVA',cost=80*G,program='lavamd',digest='lava'):
    return dict(cohort=name,input_digest=digest,program=program,cell='DH',profile='P0',cost_bytes=cost,first_eligible_monotonic=-4000)
def live(name,pss,future,now=0):
    return dict(cohort=name,uuid=name+'-UUID',pid=101,start_ticks=1000,RSS_bytes=pss,
                anon_PSS_bytes=pss,PSS_sample_monotonic=now,effective_future_bytes=future)
def initial():
    return dict(now=0,budget_bytes=200*G,effective_total_growth_bytes=180*G,memory_utilization_fraction=.88,
        own_live=[live('A',20*G,10*G),live('B',100*G,60*G)],consumed={},claim_cohorts=[],closures=[],
        pending=[candidate(),candidate('SMALL',12*G,'small','small'),candidate('MEDIUM',30*G,'medium','medium')],
        active_input_digests=['old-active'],started_programs=['small','medium'],pressure_reasons=[],
        total_padding_discount_bytes=0,padding_discount_by_cohort={},accounted_growth_by_cohort={'A':10*G,'B':60*G})
def completed(frame,accepted=True,extra_slack=None):
    f=copy.deepcopy(frame);f['now']=5;f['own_live']=[f['own_live'][1]]
    f['closures']=[dict(cohort='A',uuid='A-UUID',natural_done=True,accepted_strict_archive_restore=accepted)]
    if extra_slack is None:f['budget_bytes']+=int(.88*20*G);f['effective_total_growth_bytes']-=10*G
    else:f['budget_bytes']+=extra_slack
    f['accounted_growth_by_cohort'].pop('A',None);return f

def main():
    checks=[]
    def ck(n,c):assert c,n;checks.append(n)
    f=initial();before=copy.deepcopy(f);state=AgingState();d0=state.advance(f)
    ck('one never-started Lava DH-P0 target armed',d0['target']['cohort']=='LAVA'and d0['protected_bytes']==0)
    ck('input/spec/claim frame unchanged',f==before)
    ck('own-drain feasibility retains all peer and unknown growth',d0['feasibility']['retained_peer_claim_unknown_growth_bytes']==110*G)
    sgemm=candidate('SGEMM',18*G,'sgemm','sgemm');sgemm['first_eligible_monotonic']=-9000
    f2=initial();f2['pending'].append(sgemm);f2['started_programs'].append('sgemm')
    ck('never-started program preferred over older already-started input',AgingState().advance(f2)['target']['cohort']=='LAVA')
    f2=initial();f2['active_input_digests'].append('lava')
    ck('input already live or claimed cannot become second target',AgingState().advance(f2)['target']['cohort']!='LAVA')
    f2=initial()
    for p in f2['pending']:p['first_eligible_monotonic']=-1799
    ck('less than30min does not reserve',AgingState().advance(f2)['target']is None)
    d1=state.advance(completed(f));expected=int(.75*(10*G+int(.88*20*G)))
    ck('strict natural completion earns75percent estimated release',d1['protected_bytes']==expected)
    ck('25percent remains available to ordinary small backfill','SMALL'in d1['backfill_cohorts']and'MEDIUM'not in d1['backfill_cohorts'])
    ck('credit labeled estimate and bounded by actual positive C',all(e.get('actual_positive_margin_credit_bytes',0)<=e.get('raw_release_bytes',0)for e in d1['new_credit_events']if e['kind']=='STRICT_NATURAL_COMPLETION_CREDIT'))
    repeat=state.advance(completed(f));ck('same accepted completion never double-counted',repeat['protected_bytes']==expected)
    partial=AgingState();partial.advance(f);d=partial.advance(completed(f,extra_slack=8*G))
    ck('actual8GiB slack rise caps raw27.6GiB credit to6GiB protection',d['protected_bytes']==6*G)
    external=AgingState();external.advance(f);e=copy.deepcopy(f);e['now']=5;e['budget_bytes']+=40*G
    ck('external free alone gives no completion credit',external.advance(e)['protected_bytes']==0)
    heap=AgingState();heap.advance(f);h=copy.deepcopy(f);h['now']=5;h['budget_bytes']+=40*G;h['own_live'][0]['RSS_bytes']=5*G
    ck('heap shrink alone gives no credit',heap.advance(h)['protected_bytes']==0 and heap.last_live[('A','A-UUID')]['anon_PSS_bytes']==5*G)
    delayed=AgingState();delayed.advance(f);q=completed(f,accepted=False);d=delayed.advance(q)
    ck('natural DONE before strict acceptance earns no protected credit',d['protected_bytes']==0 and d['pending_unaccepted_release_tokens'])
    q['now']=6;q['closures'][0]['accepted_strict_archive_restore']=True;d=delayed.advance(q)
    ck('later strict acceptance can use unspent recorded true slack',d['protected_bytes']==expected)
    pending=AgingState();pending.advance(f);q=completed(f,accepted=False);pending.advance(q);q['now']=6;q['effective_total_growth_bytes']+=20*G;pending.advance(q)
    q['now']=7;q['closures'][0]['accepted_strict_archive_restore']=True;d=pending.advance(q)
    ck('new claims consume unaccepted tokens before later strict credit',d['protected_bytes']==int(.75*(10*G+int(.88*20*G)-20*G)))
    negative=AgingState();negative.advance(f);q=completed(f);q['closures'][0]['natural_done']=False
    ck('failed or interrupted point gives no natural-release credit',negative.advance(q)['protected_bytes']==0)
    stale=AgingState();stale.advance(f);q=completed(f);q['now']=70;q['own_live'][0]['PSS_sample_monotonic']=70
    d=stale.advance(q)
    ck('expired last-live or PSS witness gives no credit',d['protected_bytes']==0 and any(e['kind']=='STALE_RELEASE_WITNESS_NO_CREDIT'for e in d['new_credit_events']))
    risk=initial();risk['budget_bytes']=50*G;risk['effective_total_growth_bytes']=45*G;risk['own_live']=[live('B',5*G,5*G)]
    d=AgingState().advance(risk)
    ck('external own-drain impossibility releases throttling',d['protected_bytes']==0 and d['phase']=='OWN_DRAIN_NOT_PROVEN_RELEASE_THROTTLE'and'SMALL'in d['backfill_cohorts'])
    # Actual padding effective-row helper: no basefuture double count.
    bfile=P(__file__).parent.parent.parent/'B/padding_only_overlay_v1/padding_overlay.py'
    sp=importlib.util.spec_from_file_location('B_effective_rows',bfile);B=importlib.util.module_from_spec(sp);sp.loader.exec_module(B)
    raw=dict(additional_padding_admission_proof=dict(base_own_growth_rows=[dict(cohort='A',kind='LIVE_MODEL',RSS_bytes=20*G,additional_reserved_bytes=20*G)],
        discount_rows=[dict(cohort='A',discount_bytes=8*G)],claim_candidate_topups=[]))
    view=B.effective_own_rows(raw)
    ck('B helper yields effective12GiB future not base20GiB',view[0]['additional_reserved_bytes']==12*G and raw['additional_padding_admission_proof']['base_own_growth_rows'][0]['additional_reserved_bytes']==20*G)
    pf=initial();pf['own_live'][0]['effective_future_bytes']=12*G;pf['padding_discount_by_cohort']={'A':8*G};pf['total_padding_discount_bytes']=8*G
    padded=AgingState();padded.advance(pf);p2=completed(pf,extra_slack=12*G);p2['padding_discount_by_cohort']={'B':3*G};p2['total_padding_discount_bytes']=3*G
    d=padded.advance(p2)
    ck('per-cohort positive padding expansion excluded despite negative net discount movement',d['padding_expansion_not_credited_bytes']==3*G and d['protected_bytes']==int(.75*9*G))
    # Full real claim/unknown already carries target cost; R must not double-book.
    claimed=AgingState();claimed.advance(f);claimed.advance(completed(f));cf=completed(f);cf['now']=6;cf['budget_bytes']=300*G;cf['effective_total_growth_bytes']=250*G
    cf['claim_cohorts']=['LAVA'];cf['accounted_growth_by_cohort']['LAVA']=80*G
    d=claimed.advance(cf)
    ck('full target claim turns virtual R0 while keeping saved credit',d['phase']=='TARGET_CLAIM_INFLIGHT'and d['protected_bytes']==0 and d['saved_protected_credit_bytes']==expected)
    ck('full claim does not permanently block other legal fits','MEDIUM'in d['backfill_cohorts'])
    cf['now']=7;cf['claim_cohorts']=[];cf['consumed']={'LAVA':{'uuid':'NEW-UUID','terminal':False}}
    d=claimed.advance(cf)
    ck('spent uncertain fully accounted target visible but never resubmitted',d['phase']=='SPENT_UNCERTAIN_NO_RETRY'and d['offer_target_first']is None and d['protected_bytes']==0)
    cf['now']=8;cf['consumed']={};cf['accounted_growth_by_cohort'].pop('LAVA');cf['pending']=[p for p in cf['pending']if p['cohort']!='LAVA']
    d=claimed.advance(cf)
    ck('zero-start defer without accounted real claim restores saved virtual protection',d['phase']=='TARGET_ZERO_START_DEFER_RESERVATION_RETAINED'and d['protected_bytes']==expected)
    cf['now']=9;cf['consumed']={'LAVA':{'uuid':'NEW-UUID','terminal':False}};cf['own_live'].append(live('LAVA',2*G,80*G,now=9));cf['own_live'][-1]['uuid']='NEW-UUID';cf['active_input_digests'].append('lava')
    d=claimed.advance(cf)
    ck('observed legitimate target model clears target and reservation',d['target']is None or d['target']['cohort']!='LAVA')
    cap=AgingState();cap.advance(f);big=completed(f,extra_slack=200*G);big['own_live'][0]['anon_PSS_bytes']=100*G
    cap.last_live[('A','A-UUID')]['effective_future_bytes']=200*G
    d=cap.advance(big);ck('saved R never exceeds full target cost',d['saved_protected_credit_bytes']<=80*G)
    # Instance wrapper delegates all original gates, race checks, and restores.
    current=initial();calls=[]
    def provider(*args):return copy.deepcopy(current)
    def original(pool,*args):calls.append([p['cohort']for p in pool]);return dict(cohort=pool[0]['cohort'],original_gates=True)if pool else None
    choose=AgingChooser(original,provider);mod=types.SimpleNamespace(choose_dispatch=original);owner=[]
    choose.install(mod,lambda:owner.append(True));ck('single existing chooser instance installation',mod.choose_dispatch is choose.wrapper)
    specs=[dict(cohort=p['cohort'])for p in current['pending']];claims={};before=copy.deepcopy(claims)
    value=mod.choose_dispatch(specs,{},claims,{},None,{},0)
    ck('ordinary fits delegated through original provider unchanged',value['original_gates']and claims==before)
    current=completed(initial());value=mod.choose_dispatch(specs,{},claims,{},None,{},0)
    ck('outer fence only filters, never bypasses original gates',calls[-1]==['SMALL']and value['cohort']=='SMALL')
    current=copy.deepcopy(current);current['now']=6;current['budget_bytes']+=80*G
    value=mod.choose_dispatch(specs,{},claims,{},None,{},0)
    ck('target offered first when full unchanged cost fits',value['cohort']=='LAVA'and calls[-1]==['LAVA'])
    current['pressure_reasons']=['ACTIVE_SWAP_OUT'];count=len(calls)
    ck('external pressure blocks admission not healthy progress',mod.choose_dispatch(specs,{},claims,{},None,{},0)is None and len(calls)==count)
    current['pressure_reasons']=[]
    def racing(pool,*args):current['consumed']['LAVA']={'uuid':'SPENT-RACE','terminal':False};return {'cohort':'LAVA'}
    race=AgingChooser(racing,provider)
    ck('consumed race after chooser never returns a resubmission',race.choose(specs,{},claims,{},None,{},0)is None)
    choose.restore(lambda:owner.append(True));ck('restore returns exact prior chooser and leaves claims untouched',mod.choose_dispatch is original and claims==before and len(owner)==2)
    # Small complete owner-port integration: real adapter + actual consumer
    # schema + B effective rows, synthetic isolated filesystem only.
    asp=importlib.util.spec_from_file_location('aging_adapter_candidate',P(__file__).with_name('aging_runtime_frames.py'));adapter_module=importlib.util.module_from_spec(asp);asp.loader.exec_module(adapter_module)
    fixture_root=P(__file__).parent/'runtime_fixture';(fixture_root/'control').mkdir(parents=True,exist_ok=True);(fixture_root/'analysis').mkdir(exist_ok=True)
    def save(path,value):path.write_bytes(json.dumps(value).encode())
    save(fixture_root/'control/ACTUAL_CANARY_QUALIFICATION.json',{'CPU_ONLY':True})
    pts=[dict(cohort=c,input_digest='old-'+c,program=c)for c in('A','B')]
    save(fixture_root/'control/MATRIX_CURRENT.json',{'points':pts})
    ownq={'request':'DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1','consumed':{c:{'uuid':c+'-UUID'}for c in('A','B')}}
    baseline=dict(utc='SYNTHETIC_CPU_ONLY',admission_decision={'admission_RAM_budget_bytes':200*G,'memory_utilization_fraction':.88,'pressure_reasons':[]},
        total_projected_additional_RAM_bytes=180*G,
        own_ram_forecasts=[dict(cohort='A',kind='LIVE_MODEL',RSS_bytes=20*G,additional_reserved_bytes=20*G),dict(cohort='B',kind='LIVE_MODEL',RSS_bytes=100*G,additional_reserved_bytes=60*G)],
        additional_padding_admission_proof=dict(base_own_growth_rows=[dict(cohort='A',kind='LIVE_MODEL',RSS_bytes=20*G,additional_reserved_bytes=20*G),dict(cohort='B',kind='LIVE_MODEL',RSS_bytes=100*G,additional_reserved_bytes=60*G)],discount_rows=[dict(cohort='A',discount_bytes=8*G)],claim_candidate_topups=[]))
    fake_res=types.SimpleNamespace(resources=lambda*args:copy.deepcopy(baseline),forecast=lambda s,h,p:{'predicted_peak_RAM_bytes':s['estimated_peak_model_RAM_bytes']})
    local_start=0 if os.name=='nt'else int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])
    engine=types.SimpleNamespace(registered=lambda:({}, {},ownq,{'parent_pid':os.getpid(),'parent_start_ticks':local_start}))
    # Owner PID/start guard is tested on POSIX; Windows pure CPU uses synthetic
    # registered reads but never attempts a real/native lease installation.
    dfile=P(__file__).parent.parent.parent/'D/l2_results.py';ds=importlib.util.spec_from_file_location('actual_consumer_schema',dfile);D=importlib.util.module_from_spec(ds);ds.loader.exec_module(D)
    observed=[]
    def obs(c,u):
        observed.append(c);return dict(cohort=c,uuid=u,pid=101,start_ticks=1000,anon_PSS_bytes=(20 if c=='A' else 100)*G,PSS_sample_monotonic=time.monotonic())
    def gen(c,u):return None if'execution_receipt'in ownq['consumed'][c]else dict(pid=101,start_ticks=1000)
    runtime=adapter_module.RuntimeFrames(fixture_root,engine,fake_res,D,B.effective_own_rows,observe=obs,generation=gen);runtime.first_eligible=time.monotonic()-4000
    pending_spec=[dict(cohort='LAVA',input_digest='lava',program='lavamd',cell='DH',profile='P0',estimated_peak_model_RAM_bytes=80*G)]
    rframe=runtime(pending_spec,{}, {},{},None,{},0)
    ck('runtime adapter uses B effective future12 not base20',next(r['effective_future_bytes']for r in rframe['own_live']if r['cohort']=='A')==12*G)
    ck('runtime frame full candidate forecast unchanged',rframe['pending'][0]['cost_bytes']==80*G)
    runtime(pending_spec,{}, {},{},None,{},0);ck('repeated chooser calls do not rescan smaps before30seconds',len(observed)==2)
    engine.assert_parent_lease=lambda:True
    # On Windows no /proc: owner guard stays uninvoked; all observation is injected.
    ownq['consumed']['A']['execution_receipt']={'stop_reason':None,'launcher_wait_returncode':0}
    good=dict(state=D.PASS,uuid='A-UUID',cycles=100,proof={'performance_accepted':True,'cycles':100},archive={'CPU_ONLY':True})
    save(fixture_root/'analysis/A.RESULT.json',good);baseline['additional_padding_admission_proof']['base_own_growth_rows']=baseline['additional_padding_admission_proof']['base_own_growth_rows'][1:];baseline['additional_padding_admission_proof']['discount_rows']=[]
    fresh=runtime(pending_spec,{}, {},{},None,{},0)
    ck('runtime requires actual consumer strict archived acceptance before credit',next(c for c in fresh['closures']if c['cohort']=='A')['accepted_strict_archive_restore'])
    # PSS cache cadence is a separately visible adapter contract.
    adapter=P(__file__).with_name('aging_runtime_frames.py');compile(adapter.read_bytes(),str(adapter),'exec')
    result=dict(schema='DTC_LARGE_JOB_AGING_CPU_QUALIFICATION_V1',status='PASS',checks=len(checks),names=checks,
        B_effective_helper_sha256=hashlib.sha256(bfile.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(P(__file__).with_name('large_job_aging.py').read_bytes()).hexdigest(),
        adapter_sha256=hashlib.sha256(adapter.read_bytes()).hexdigest(),model_launches=0,signals_sent=0,production_changes=0,production_applied=False)
    P(__file__).with_name('CPU_QUALIFICATION.json').write_bytes((json.dumps(result,indent=2,sort_keys=True)+'\n').encode())
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
