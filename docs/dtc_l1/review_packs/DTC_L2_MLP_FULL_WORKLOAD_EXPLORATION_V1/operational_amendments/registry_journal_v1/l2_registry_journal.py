"""Qualified-instance candidate: additive journal around frozen registry.extend.

No production application on import. DTC-MAIN must supply an independently pinned
manifest, the actual sole-owner registry/engine modules, and explicitly install
guard.extend into that registry instance after review. No model launch exists.
"""
import copy,datetime,hashlib,json,pathlib,threading,time
P=pathlib.Path

def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256((json.dumps(v,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
def put(p,v):
    p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
    if p.exists() and p.read_bytes()==data:return
    tmp=p.with_name('.'+p.name+'.JOURNALwriting')
    with tmp.open('wb')as h:h.write(data);h.flush();__import__('os').fsync(h.fileno())
    tmp.replace(p)
    fd=__import__('os').open(p.parent,__import__('os').O_RDONLY)
    try:__import__('os').fsync(fd)
    finally:__import__('os').close(fd)

def scientific_spec(s):
    """Only the three qualified dynamic memory fields may differ after registration."""
    s=copy.deepcopy(s);s.pop('estimated_peak_model_RAM_bytes',None)
    for k in ('max_process_tree_rss_bytes','max_process_tree_vms_bytes'):s.get('limits',{}).pop(k,None)
    return s

class RegistryJournal:
    def __init__(self,registry,engine,manifest,fault_hook=None):
        self.registry=registry;self.engine=engine;self.manifest=copy.deepcopy(manifest)
        self.original_extend=registry.extend;self.lock=threading.RLock();self.fault_hook=fault_hook
        self.root=P(registry.R);self.journals=self.root/'control/extension_journal_v1'
        self.last_issue=None

    def check(self):
        m=self.manifest
        assert sha(__file__)==m['wrapper_sha256'],'WRAPPER_SOURCE_PIN_MISMATCH'
        assert sha(self.registry.__file__)==m['registry_sha256'],'REGISTRY_SOURCE_PIN_MISMATCH'
        reg,ep,q,plan=self.engine.registered() # exact existing source/plan authority checks
        assert sha(self.root/'control/EXECUTION_PLAN.json')==m['execution_plan_sha256'],'EXECUTION_PLAN_PIN_MISMATCH'
        assert q['request']==self.engine.REQ
        for pin in plan['source_pins']:assert sha(pin['path'])==pin['sha256'],'PLAN_SOURCE_PIN_MISMATCH'
        assert q['budget']==len(q['admitted_specs']) and q['remaining']==q['budget']-len(q['consumed'])
        return reg,ep,q,plan

    def event(self,folder,kind,**values):
        put(folder/(str(time.time_ns())+'.'+kind+'.json'),dict(kind=kind,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),**values))

    def checkpoint(self,name):
        if self.fault_hook:self.fault_hook(name)

    def matrix(self):
        matrix=read(self.root/'control/MATRIX_CURRENT.json');scope=read(self.root/'control/SCOPE.json')
        assert matrix['base_scope_sha256']==sha(self.root/'control/SCOPE.json'),'BASE_SCOPE_SHA_MISMATCH'
        assert type(matrix['revision'])is int and matrix['revision']>=0,'INVALID_MATRIX_REVISION'
        points={p['cohort']:p for p in matrix['points']};assert len(points)==len(matrix['points']),'DUPLICATE_MATRIX_COHORT'
        assert all(points.get(p['cohort'])==p for p in scope['points']),'INITIAL_MATRIX_IDENTITY_CHANGED'
        assert {p['input_digest']for p in matrix['points']}=={p['input_digest']for p in scope['points']},'FROZEN_INPUT_DOMAIN_CHANGED'
        return matrix

    def prepare(self,proposal,q,plan):
        pid=proposal['proposal_id'];assert pid and all(c.isalnum()or c=='_'for c in pid)
        folder=self.journals/pid;prepared=folder/'PREPARED.json'
        if prepared.exists():
            v=read(prepared);assert v['proposal']==proposal,'PROPOSAL_ID_REUSED_WITH_DIFFERENT_CONTENT'
            assert v['wrapper_manifest']==self.manifest,'PREPARED_WRAPPER_MANIFEST_MISMATCH'
            return folder,v
        matrix=self.matrix();history=read(self.root/'control/SEARCH_HISTORY.json')
        gen=self.registry.load('journal_generator','l2_config_generator.py')
        parameters=gen.normalize(proposal['parameters']);profile=proposal['profile']
        assert profile and all(c.isalnum()or c=='_'for c in profile)
        if profile in history['profiles']:assert gen.normalize(history['profiles'][profile]['parameters'])==parameters,'PROFILE_PARAMETER_COLLISION'
        points={p['cohort']:p for p in matrix['points']};assert len(points)==len(matrix['points'])
        planned=[];seen=set()
        for want in proposal['new_cells']:
            d=want.get('input_digest',want.get('workload'));cell=want.get('cell',want.get('design'))
            assert cell in ('CH','DH')
            cohort='E2-DTCL2MLP-'+d[:16]+'-'+cell+'-'+profile+'-V1'
            assert cohort not in seen,'DUPLICATE_PROPOSAL_CELL';seen.add(cohort)
            basepoint=next(p for p in matrix['points']if p['input_digest']==d and p['cell']==cell and p['profile']=='P0')
            point=dict(basepoint,cohort=cohort,profile=profile)
            if cohort in points:
                assert points[cohort]==point,'EXISTING_MATRIX_IDENTITY_MISMATCH'
                continue
            base=read(self.root/'control/specs'/(basepoint['cohort']+'.json'))
            texts=[P(x['path']).read_text()for x in base['configs']];after,config_manifest=gen.generate(texts,parameters)
            cfg=[dict(path=str(self.root/'DTC/env'/(cell+'_'+profile)/('config-'+str(i)+'.config')),
                      sha256=hashlib.sha256(t.encode()).hexdigest())for i,t in enumerate(after)]
            s=copy.deepcopy(base);s.update(cohort=cohort,downstream_profile=profile,profile=profile,configs=cfg,host_cpu=None)
            opts=gen.effective_options(after)
            for k in ('-gpgpu_cache:dl2','-gpgpu_frfcfs_dram_sched_queue_size'):s['expected_options'][k]=[opts[k]]
            s['native_simulator_argv']=[base['native_simulator_argv'][0],'-trace',base['native_simulator_argv'][2]]
            for c in cfg:s['native_simulator_argv']+=['-config',c['path']]
            planned.append(dict(point=point,spec_sha256=digest(s),scientific_spec_sha256=digest(scientific_spec(s)),
                                expected_options_count=len(s['expected_options']),configs=cfg))
        v=dict(schema='L2_MLP_EXTENSION_PREPARED_V1',proposal=copy.deepcopy(proposal),parameters=parameters,
               planned=planned,base_matrix_revision=matrix['revision'],expected_next_revision=matrix['revision']+bool(planned),
               base_matrix_sha256=sha(self.root/'control/MATRIX_CURRENT.json'),base_scope_sha256=matrix['base_scope_sha256'],
               execution_plan_sha256=self.manifest['execution_plan_sha256'],source_pins=plan['source_pins'],
               authority_before=dict(budget=q['budget'],remaining=q['remaining'],admitted_specs_sha256=digest(q['admitted_specs']),
                   consumed_sha256=digest(q['consumed']),consumed_uuids={k:v.get('uuid')for k,v in q['consumed'].items()}),
               wrapper_manifest=self.manifest)
        put(prepared,v)
        return folder,v

    def reconcile(self,folder,v):
        _,_,q,_=self.check();proposal=v['proposal'];pid=proposal['proposal_id']
        matrix=self.matrix();history=read(self.root/'control/SEARCH_HISTORY.json')
        assert matrix['base_scope_sha256']==v['base_scope_sha256'],'BASE_SCOPE_CHANGED'
        current={p['cohort']:p for p in matrix['points']};assert len(current)==len(matrix['points'])
        planned=v['planned'];granted=[p for p in planned if p['point']['cohort']in q['admitted_specs']]
        if not granted and planned:
            assert not any(p['point']['cohort']in current for p in planned),'MATRIX_WITHOUT_AUTHORITY'
            return dict(state='UNGRANTED_SAFE_TO_RETRY',new_points=[])
        assert len(granted)==len(planned),'PARTIAL_AUTHORITY_GRANTS_REQUIRE_REVIEW'
        if planned:
            extensions=[x for x in q.get('authorized_extensions',[])if x['proposal_id']==pid]
            assert len(extensions)==1,'MISSING_OR_DUPLICATE_EXTENSION_AUTHORITY'
            x=extensions[0]
            assert x['profile']==proposal['profile'] and x['parameters']==v['parameters'] and x['new_starts']==len(planned),'EXTENSION_AUTHORITY_MISMATCH'
        before_consumed=copy.deepcopy(q['consumed']);before_budget=q['budget'];before_remaining=q['remaining']
        missing=[];amendments=[]
        for item in planned:
            p=item['point'];c=p['cohort'];sp=self.root/'control/specs'/(c+'.json');s=read(sp)
            assert q['admitted_specs'][c]==sha(sp)==sha(self.root/'control'/(c+'_SPEC.json')),'REGISTERED_SPEC_SHA_MISMATCH'
            assert digest(scientific_spec(s))==item['scientific_spec_sha256'],'SCIENTIFIC_IDENTITY_MISMATCH'
            assert len(s['expected_options'])==item['expected_options_count'],'RESOLVED_OPTION_POPULATION_CHANGED'
            assert c in q['admitted_inputs'][p['input_digest']]['specs'],'INPUT_AUTHORITY_LINK_MISSING'
            assert q['admitted_inputs'][p['input_digest']]['specs'].count(c)==1,'DUPLICATE_INPUT_AUTHORITY_LINK'
            assert all(sha(x['path'])==x['sha256']for x in item['configs']),'CONFIG_SHA_MISMATCH'
            if sha(sp)!=item['spec_sha256']:amendments.append(dict(cohort=c,current_spec_sha256=sha(sp),prepared_spec_sha256=item['spec_sha256'],reason='Only qualified dynamic RSS/AS fields differ'))
            if c in current:assert current[c]==p,'MATRIX_ROW_IDENTITY_MISMATCH'
            else:missing.append(p)
        # No authority mutation occurs here: already granted and spent IDs stay exact.
        if missing:
            revision=matrix['revision']+1
            put(self.root/'control/matrix_revisions'/(str(revision).zfill(5)+'.JOURNAL_RECOVERY.json'),
                dict(proposal=proposal,new_points=missing,base_scope_sha256=v['base_scope_sha256'],recovery_from=str(folder/'PREPARED.json')))
            matrix['points']+=missing;matrix['revision']=revision
            put(self.root/'control/MATRIX_CURRENT.json',matrix)
        if pid not in history['proposal_ids']:history['proposal_ids'].append(pid)
        profile=proposal['profile']
        if profile in history['profiles']:assert history['profiles'][profile]['parameters']==v['parameters'],'HISTORY_PARAMETER_MISMATCH'
        else:history['profiles'][profile]={'parameters':v['parameters']}
        put(self.root/'control/SEARCH_HISTORY.json',history)
        _,_,after,_=self.check()
        # Original live workers may append receipts concurrently. Their existing
        # consumed identities must be preserved; new receipts are never overwritten.
        assert after['budget']==before_budget,'RECOVERY_CHANGED_BUDGET'
        assert all(k in after['consumed']and all(after['consumed'][k].get(kk)==vv for kk,vv in old.items())
                   for k,old in before_consumed.items()),'RECOVERY_CHANGED_SPENT_IDENTITY'
        receipt=dict(schema='L2_MLP_EXTENSION_COMMITTED_V1',proposal_id=pid,
            prepared_sha256=sha(folder/'PREPARED.json'),matrix_sha256=sha(self.root/'control/MATRIX_CURRENT.json'),
            matrix_revision=matrix['revision'],history_sha256=sha(self.root/'control/SEARCH_HISTORY.json'),
            registered_points=len(planned),reconstructed_matrix_rows=len(missing),budget=after['budget'],
            consumed_uuids={p['point']['cohort']:after['consumed'].get(p['point']['cohort'],{}).get('uuid')for p in planned},
            resource_only_spec_amendments=amendments,authority_mutations_during_recovery=0,
            remaining_before_recovery=before_remaining,remaining_after_recovery=after['remaining'])
        put(folder/'COMMITTED.json',receipt)
        return dict(state='COMMITTED_OR_RECONCILED',new_points=[p['point']for p in planned],receipt=receipt)

    def recover_pending(self):
        """Installation/restart sweep; reconcile grants, never create a new grant."""
        with self.lock:
            self.check();results=[]
            for prepared in sorted(self.journals.glob('*/PREPARED.json')):
                folder=prepared.parent
                if (folder/'COMMITTED.json').exists():continue
                v=read(prepared)
                try:
                    assert v['wrapper_manifest']==self.manifest,'PREPARED_WRAPPER_MANIFEST_MISMATCH'
                    result=self.reconcile(folder,v)
                    results.append(dict(proposal_id=v['proposal']['proposal_id'],**result))
                except Exception as exc:
                    self.event(folder,'STARTUP_RECONCILIATION_HOLD',error=repr(exc))
                    results.append(dict(proposal_id=v['proposal']['proposal_id'],state='RECONCILIATION_HOLD_REQUIRES_REVIEW',error=repr(exc)))
            status=self.blocking_status()
            self.last_issue=None if status['safe_for_scientific_completion'] else dict(state='PENDING_EXTENSION_JOURNALS',pending=status['pending'])
            return dict(results=results,status=status,authority_updates=0,new_model_starts=0)

    def blocking_status(self):
        """Read-only finalization gate; pending never interrupts healthy models."""
        self.check();pending=[]
        for p in sorted(self.journals.glob('*/PREPARED.json')):
            if not (p.parent/'COMMITTED.json').exists():
                v=read(p);pending.append(dict(proposal_id=v['proposal']['proposal_id'],prepared_sha256=sha(p),journal=str(p.parent)))
        return dict(schema='L2_MLP_EXTENSION_JOURNAL_STATUS_V1',pending=pending,
                    safe_for_scientific_completion=not pending,requires_engineering_review=bool(pending),
                    healthy_models_must_continue=True,admission_owner_unchanged=True)

    def guard_decision(self,decision):
        """Pair with the adaptive instance at installation; preserve proposals/stats."""
        result=copy.deepcopy(decision);status=self.blocking_status();result['registry_journal_status']=status
        if not status['safe_for_scientific_completion']:
            result.update(scientific_stage_complete=False,adoption_ready=False,requires_engineering_review=True,
                          state='REGISTRY_JOURNAL_ENGINEERING_HOLD_CONTINUE_HEALTHY_MODELS')
        return result

    def extend(self,proposal):
        with self.lock:
            _,_,q,plan=self.check()
            folder,v=self.prepare(proposal,q,plan)
            if (folder/'COMMITTED.json').exists():return []
            try:
                self.checkpoint('AFTER_PREPARED')
                existing=self.reconcile(folder,v)
                if existing['state']=='COMMITTED_OR_RECONCILED':return existing['new_points']
                original_load=self.registry.load;original_put=self.registry.put;patched=[]
                def load(name,f):
                    mod=original_load(name,f)
                    if f=='l2_native.py':
                        update=mod.update_authority
                        def invoke(fn):
                            update(fn);self.checkpoint('AFTER_AUTHORITY')
                        mod.update_authority=invoke;patched.append((mod,update))
                    return mod
                def stage_put(path,value):
                    original_put(path,value)
                    if P(path)==self.root/'control/MATRIX_CURRENT.json':self.checkpoint('AFTER_MATRIX')
                    if P(path)==self.root/'control/SEARCH_HISTORY.json':self.checkpoint('AFTER_HISTORY')
                self.registry.load=load;self.registry.put=stage_put
                try:self.original_extend(proposal)
                finally:
                    self.registry.load=original_load;self.registry.put=original_put
                    for mod,update in reversed(patched):mod.update_authority=update
                result=self.reconcile(folder,v)
                assert result['state']=='COMMITTED_OR_RECONCILED','ORIGINAL_EXTENSION_RETURNED_WITHOUT_GRANT'
                self.last_issue=None
                return result['new_points']
            except Exception as exc:
                self.event(folder,'ORIGINAL_OR_RECOVERY_ERROR',error=repr(exc))
                try:
                    recovered=self.reconcile(folder,v)
                    if recovered['state']=='COMMITTED_OR_RECONCILED':
                        self.last_issue=None
                        return recovered['new_points']
                    self.last_issue=dict(state='UNGRANTED_ENGINEERING_HOLD_SAFE_TO_RETRY',error=repr(exc),journal=str(folder))
                except Exception as recovery_error:
                    self.last_issue=dict(state='EXTENSION_RECONCILIATION_HOLD_REQUIRES_REVIEW',error=repr(exc),recovery_error=repr(recovery_error),journal=str(folder))
                self.event(folder,'ENGINEERING_HOLD',**self.last_issue)
                return []
