"""CPU-only real frozen registry/journal/authority/memory interfaces.
All roots, authority files, resources, callbacks and actors are private fixtures.
No actual owner attachment, native prepare/Popen, model or production mutation.
"""
from pathlib import Path as P
import json,hashlib,copy,types,tempfile,threading,sys,importlib.util,os,time,ctypes
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');D=P(__file__).parent;G=1024**3;M=R/'control/operational_amendments/future_memory_admission_v1';J=R/'control/operational_amendments/registry_journal_v1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def raw(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw(v))
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
S=load('qualified_primary_scope_synchronizer',D/'scope_sync.py');checks=[];cases=[]
def ck(n,v):assert v,(n,getattr(globals().get('f'),'sync',None).last_issue);checks.append(n)
def rejected(n,fn):
 try:fn()
 except(AssertionError,RuntimeError):checks.append(n);return
 raise AssertionError(n+' not refused')
source_reg=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');source_epoch=read(N/'control/CURRENT_SCIENCE_EPOCH.json');source_matrix=read(R/'control/MATRIX_CURRENT.json');source_history=read(R/'control/SEARCH_HISTORY.json');source_plan=read(R/'control/EXECUTION_PLAN.json');source_scope=read(R/'control/SCOPE.json');mem_source_cfg=read(M/'ACTIVE_MEMORY.json')
fixture_run=P(tempfile.mkdtemp(prefix='CPU_SCOPE_SYNC_',dir=D));main=sys.modules['__main__'];REQ=S.REQ
class Lock:
 def __init__(self):self.real=threading.RLock();self.events=[]
 def __enter__(self):self.real.acquire();self.events.append(('acquire',threading.get_ident()));return self
 def __exit__(self,*a):self.events.append(('release',threading.get_ident()));self.real.release()
 def owned(self):return self.real._is_owned()
def fixture(name,finite=False):
 for marker in [S.MARKER,S.MEMORY,'DTC_L2_MLP_REGISTRY_JOURNAL_V1']:
  if hasattr(main,marker):delattr(main,marker)
 root=fixture_run/name;root.mkdir();privateN=root/'PRIVATE_NATIVE';rp=privateN/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';ep=privateN/'control/CURRENT_SCIENCE_EPOCH.json'
 (rp.parent/'request_history').mkdir(parents=True)
 reg=load('scope_registry_'+name,R/'tools/l2_registry.py');e=load('scope_native_'+name,R/'tools/l2_native.py');gen=load('scope_gen_'+name,R/'tools/l2_config_generator.py');jmod=load('scope_journal_'+name,J/'l2_registry_journal.py');lib=load('scope_memory_lib_'+name,M/'future_memory.py');owner=load('scope_memory_owner_'+name,M/'memory_owner.py')
 e.R=root;e.N=privateN;reg.R=root
 q=source_reg['registered_future_requests'][REQ];fake=copy.deepcopy(source_reg)
 # Explicit frozen, isolated control metadata; no symlink can write production.
 for n in ['EXECUTION_PLAN.json','SCOPE.json','BUILD_PROFILE.json','SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json','RESOURCE_POLICY.json']:
  p=root/'control'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((R/'control'/n).read_bytes())
 cpuplan=read(root/'control/EXECUTION_PLAN.json');cpuplan.update(parent_pid=os.getpid(),parent_start_ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]));put(root/'control/EXECUTION_PLAN.json',cpuplan)
 fake['registered_future_requests'][REQ]['execution_plan_sha256']=sha(root/'control/EXECUTION_PLAN.json')
 put(root/'control/MATRIX_CURRENT.json',source_matrix);put(root/'control/SEARCH_HISTORY.json',source_history)
 for c in set(q['admitted_specs'])|{p['cohort']for p in source_matrix['points']}:
  for rel in ['specs/'+c+'.json',c+'_SPEC.json']:
   p=root/'control'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((R/'control'/rel).read_bytes())
 (root/'control/qualification_ledger').mkdir();put(root/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={}))
 def authority():
  a=read(rp);b=read(ep);assert sha(rp)==b['native_registry_sha256'];return a,b
 e.authority=authority;e.assert_parent_lease=lambda:dict(CPU_FIXTURE=True)
 update_actual=e.update_authority;updates=[];lock=Lock();sync_box={}
 def update(fn):
  before=authority()[0];update_actual(fn);after=authority()[0];b=before['registered_future_requests'][REQ];a=after['registered_future_requests'][REQ]
  updates.append(dict(budget_delta=a['budget']-b['budget'],aging_lock_owned=lock.owned(),thread=threading.get_ident(),real_native_update_authority=True))
 e.update_authority=update
 epoch=copy.deepcopy(source_epoch);put(rp,fake);epoch['native_registry_sha256']=sha(rp);put(ep,epoch)
 reg.load=lambda n,f:e if f=='l2_native.py'else gen if f=='l2_config_generator.py'else (_ for _ in()).throw(AssertionError(f))
 manifest=dict(wrapper_sha256=sha(J/'l2_registry_journal.py'),registry_sha256=sha(R/'tools/l2_registry.py'),execution_plan_sha256=sha(root/'control/EXECUTION_PLAN.json'))
 journal=jmod.RegistryJournal(reg,e,manifest);setattr(main,'DTC_L2_MLP_REGISTRY_JOURNAL_V1',dict(guard=journal))
 # Reproduce the actual captured bound-method installation, then the planned
 # E resource qualification plain-function outer. The real dispatcher uses reg.
 reg.extend=journal.extend;captured_journal=reg.extend;E_calls=[]
 def E_resource_guard(proposal):E_calls.append(proposal['proposal_id']);return captured_journal(proposal)
 reg.extend=E_resource_guard
 baseline={p['cohort']for p in source_matrix['points']};nonprimary=sorted(set(q['admitted_specs'])-baseline)
 active=copy.deepcopy(mem_source_cfg)
 if not finite:active.update(scope_mode='ALL_UNSPENT_FUTURE',allowed_cohorts=sorted(baseline&set(q['admitted_specs'])))
 else:active.update(scope_mode='FINITE_CANARY',allowed_cohorts=[mem_source_cfg['allowed_cohorts'][0]])
 privatecfg=root/'control/MEMORY_ACTIVE.json';put(privatecfg,active)
 memory_full_record=fake['registered_future_requests'][REQ]['additional_operational_overlays'][lib.ID];memory_full_record.update(lib.record(active));memory_full_record['status']='ACTIVE'
 memory_full_record['CPU_FIXTURE_PROVENANCE_PRESERVE']={'production_extras_preserved':True}
 put(rp,fake);epoch['native_registry_sha256']=sha(rp);put(ep,epoch)
 sample=dict(host_MemAvailable_bytes=200*G,cgroup_effective_headroom_bytes=220*G,native_free_bytes=100*G,required_free_bytes=5*G,free_inodes=1000000,utc='CPU_ONLY',monotonic=1)
 base=dict(sample,source_module_sha256=sha(R/'tools/l2_resources.py'),policy_sha256=sha(R/'control/RESOURCE_POLICY.json'),total_projected_additional_RAM_bytes=2*G,RAM_reservation_entries=[],own_ram_forecasts=[dict(additional_reserved_bytes=2*G)],physical_RAM_pass=True,physical_disk_pass=True,own_write_ceiling_pass=True,admission_decision=dict(memory_utilization_fraction=.88,admission_RAM_budget_bytes=int(192*G*.88),additional_reserved_RAM_bytes=2*G,pass_admission=True,pressure_reasons=[]))
 runtime=dict(OLD_RUNTIME_OBJECT=True);calls=[];res=types.SimpleNamespace(resources=lambda s,fresh_source=False:copy.deepcopy(base)if fresh_source else runtime)
 def oldchoose(pending,sample,claims,history,previous=None,policy=None,dispatch_index=0):
  calls.append([x['cohort']for x in pending]);return dict(cohort=pending[0]['cohort'],CPU_FIXTURE=True)if pending else None
 res.choose_dispatch=oldchoose;consumer=types.SimpleNamespace(load=lambda *a:None);aging=types.SimpleNamespace(original=oldchoose,lock=lock,state=types.SimpleNamespace(previous_C=1,protected=7*G,pending_releases={'OLD':dict(credit=3*G)}));pool=object();claims={};frame=types.SimpleNamespace(f_locals=dict(engine=e,res=res,consumer=consumer,pool=pool,claims=claims,registry=reg,running={}))
 owner.install_on_frame(frame,active,aging,e.assert_parent_lease);memory=getattr(main,S.MEMORY)
 deps={p['path']:p['sha256']for p in source_plan['source_pins']};deps.update({str(M/n):sha(M/n)for n in ['future_memory.py','memory_owner.py','memory_frontend.py','memory_extra_strict.py','joint_padding_strict.py','joint_io_strict.py']});deps[str(J/'l2_registry_journal.py')]=sha(J/'l2_registry_journal.py');deps[str(P(__file__))]=sha(__file__)
 op=root/'control/scope_sync';op.mkdir();qa=op/'CPU_FIXTURE_QA.json';back=op/'CPU_FIXTURE_READBACK.json';join=dict(source_sha256=sha(D/'scope_sync.py'),dependency_pins=deps);put(qa,dict(join,status='PASS',actual_journal_and_memory_interfaces_qualified=True,CPU_FIXTURE_ONLY=True));put(back,dict(join,verified=True,QA_sha256=sha(qa),CPU_FIXTURE_ONLY=True))
 cfg=dict(status='ACTIVE_OPERATIONAL_APPEND_ONLY',request=REQ,overlay_id=S.ID,root=str(root),source_path=str(D/'scope_sync.py'),source_sha256=sha(D/'scope_sync.py'),dependency_pins=deps,QA_path=str(qa),QA_sha256=sha(qa),readback_path=str(back),readback_sha256=sha(back),preserved_nonprimary_cohorts=nonprimary,memory_active_path=str(privatecfg),directory=str(op/'receipts'))
 cfgpath=op/'INSTALL.json';put(cfgpath,cfg)
 def register_private(reg):reg['registered_future_requests'][REQ]['additional_operational_overlays'][S.ID]=S.record(cfg)
 e.update_authority(register_private);updates.clear();queued=[];queue_locks=[]
 def enqueue(path):
  queue_locks.append(dict(aging=lock.owned(),journal=journal.lock._is_owned(),sync=sync_box['sync'].lock._is_owned()));queued.append(path)
 proof=S.install_on_frame(frame,cfgpath,enqueue);sync=getattr(main,S.MARKER);sync_box['sync']=sync;sync.last_recovery_tick=time.monotonic()
 ids=sorted({p['input_digest']for p in source_scope['points']});proposal=dict(proposal_id='CPU_SYNC_'+name,profile='CPU_SYNC_'+name,parameters=dict(entries=1536),new_cells=[dict(input_digest=d,cell='DH')for d in ids]);old=read(root/'control/specs'/(next(c for c in baseline if c in q['admitted_specs']and c not in q['consumed'])+'.json'));initial=authority()[0]
 return types.SimpleNamespace(root=root,N=privateN,engine=e,registry=reg,journal=journal,lib=lib,owner=owner,memory=memory,res=res,aging=aging,frame=frame,claims=claims,scope=cfg,cfgpath=cfgpath,active=active,privatecfg=privatecfg,updates=updates,queued=queued,queue_locks=queue_locks,sync=sync,proposal=proposal,old=old,initial=initial,nonprimary=nonprimary,runtime=runtime,calls=calls,proof=proof,authority=authority,E_calls=E_calls,captured_journal=captured_journal,E_resource_guard=E_resource_guard)
def q(f):return f.engine.registered()[2]
def extend(f):return f.registry.extend(f.proposal)
def choose(f,cohorts):return f.res.choose_dispatch([f.engine.canonical(c)for c in cohorts],{},f.claims,{},None,{},0)
f=fixture('NORMAL35');before=q(f);rows=extend(f);new=[x['cohort']for x in rows];ck('real_journal_registry_generator_grants_exact35_private_only',len(new)==35 and q(f)['budget']==before['budget']+35 and len([u for u in f.updates if u['budget_delta']==35])==1)
ck('immutable_request_queue_after_COMMITTED_and_no_callback_locks',len(f.queued)==1 and all(not any(x.values())for x in f.queue_locks)and bool(list((f.sync.directory/'requests').glob('*.REQUEST.json'))))
ck('actual_registry_captured_journal_plus_E_plainFn_guard_preserved',f.E_calls==[f.proposal['proposal_id']]and f.journal.extend==f.captured_journal and f.registry.extend==f.sync.extend and f.sync.prior_extend is f.E_resource_guard)
ck('ACK_pending_filters_only_new_primary_while_old_work_passes',choose(f,[new[0],f.old['cohort']])['cohort']==f.old['cohort']and choose(f,[new[0]])is None)
immutable_old=read(f.privatecfg);old_full_record=copy.deepcopy(q(f)['additional_operational_overlays'][f.lib.ID]);protected=f.aging.state.protected;credits=copy.deepcopy(f.aging.state.pending_releases);state=f.sync.drain_in_main(f.engine.assert_parent_lease)
ck('real_existing_memory_Main_API_appends35_and_ACK',state['status']=='APPENDED_EXACT_COMMITTED_PRIMARY_IDENTITIES'and read(f.privatecfg)['allowed_cohorts']==immutable_old['allowed_cohorts']+sorted(new)and choose(f,[new[0]])['cohort']==new[0])
ck('no_new_grant_from_sync_budget_consumed_oldrows_exact',q(f)['budget']==before['budget']+35 and q(f)['consumed']==before['consumed']and f.aging.state.protected==protected and f.aging.state.pending_releases==credits and f.res.resources({},False)is f.runtime)
ck('real_production_memory_record_extras_preserved_exactly',all(q(f)['additional_operational_overlays'][f.lib.ID][k]==v for k,v in old_full_record.items()if k not in f.lib.record(immutable_old))and q(f)['additional_operational_overlays'][f.lib.ID]['CPU_FIXTURE_PROVENANCE_PRESERVE']==old_full_record['CPU_FIXTURE_PROVENANCE_PRESERVE'])
old_snapshot=dict(config=immutable_old,record=old_full_record);ck('historical_snapshot_record_replay_stays_valid_after_current_scope_append',all(old_snapshot['record'][k]==v for k,v in f.lib.record(old_snapshot['config']).items())and old_snapshot['config']!=read(f.privatecfg))
ck('operational_authority_callback_holds_aging_lock_and_no_addon_Main_API',all(u['aging_lock_owned']for u in f.updates if u['budget_delta']==0)and all(not u['aging_lock_owned']for u in f.updates if u['budget_delta']>0))
ck('repeat_extend_and_Main_drain_add_no_grants_or_duplicate_scope',extend(f)==[] and f.sync.drain_in_main(f.engine.assert_parent_lease)['status']=='NO_NEW_PRIMARY_UNSPENT_IDENTITIES'and len([u for u in f.updates if u['budget_delta']])==1)
committed=f.sync.committed
def costly_scan_not_expected():raise AssertionError('CPU should not rescan old COMMITTED/specs when no new identity exists')
f.sync.committed=costly_scan_not_expected;f.sync.last_issue=None;ck('idle_recovery_tick_does_not_reread_all_historical_specs',f.sync.enqueue_scan()is None and f.sync.last_issue is None and f.sync.drain_in_main(f.engine.assert_parent_lease)['status']=='NO_NEW_PRIMARY_UNSPENT_IDENTITIES');f.sync.committed=committed
ck('nonprimary_R2_never_appended_or_rewritten',set(f.nonprimary).isdisjoint(set(read(f.privatecfg)['allowed_cohorts'])-set(immutable_old['allowed_cohorts']))and all(q(f)['consumed'].get(c)==before['consumed'].get(c)for c in f.nonprimary))
ck('existing_request_and_tx_ACK_immutable',all(read(p)['source_sha256']==f.scope['source_sha256']for p in(f.sync.directory/'transactions').glob('*/ACK.json')))
if f.nonprimary:ck('existing_nonprimary_R2_prior_route_preserved',choose(f,[f.nonprimary[0]])['cohort']==f.nonprimary[0])
cases.append(dict(name='NORMAL35',root=str(f.root)))
f=fixture('FINITE',finite=True);before=read(f.privatecfg);rows=extend(f);ck('FINITE_canary_no_broadening_no_scope_append',f.sync.drain_in_main(f.engine.assert_parent_lease)['status']=='DEFERRED_UNTIL_CANARY_APPROVED_BROAD_SCOPE'and read(f.privatecfg)==before and f.memory['context']['cfg']==before)
ck('FINITE_existing_chooser_semantics_preserved',choose(f,[rows[0]['cohort']])['cohort']==rows[0]['cohort'])
# Real COMMITTED exists despite an exception/lost returned list.
f=fixture('LOST_RETURN');prior=f.sync.prior_extend
def lost(proposal):prior(proposal);raise RuntimeError('CPU after COMMITTED lost return')
f.sync.prior_extend=lost;ck('COMMITTED_then_exception_still_queues_and_returns_safe_no_grant_retry',extend(f)==[] and len(f.queued)==1 and len([u for u in f.updates if u['budget_delta']==35])==1)
ck('startup_recovery_scan_needs_no_returned_new_points',f.sync.drain_in_main(f.engine.assert_parent_lease)['status']=='APPENDED_EXACT_COMMITTED_PRIMARY_IDENTITIES')
for phase in ['AFTER_PREPARED','AFTER_AUTHORITY','AFTER_ACTIVE_FILE','AFTER_OWNER_CONTEXT']:
 f=fixture(phase);rows=extend(f);new=[x['cohort']for x in rows];before=q(f);f.sync.fault_hook=lambda where,_phase=phase:(_ for _ in()).throw(OSError('CPU '+where))if where==_phase else None
 outcome=f.sync.drain_in_main(f.engine.assert_parent_lease);ck(phase+'_failure_is_recoverable_no_extra_grant',outcome['status']=='ENGINEERING_PENDING_SAFE_TO_RECOVER'and q(f)['budget']==before['budget'])
 ck(phase+'_unACKed_new_identity_cannot_dispatch',choose(f,[new[0]])is None)
 f.sync.fault_hook=None;out=f.sync.drain_in_main(f.engine.assert_parent_lease);ck(phase+'_forward_recovery_real_memory_API_and_ACK',choose(f,[new[0]])['cohort']==new[0]and len(list((f.sync.directory/'transactions').glob('*/PREPARED.json')))==1 and len(list((f.sync.directory/'transactions').glob('*/ACK.json')))==1 and len([u for u in f.updates if u['budget_delta']==0])==1)
 cases.append(dict(name=phase,root=str(f.root)))
f=fixture('CONCURRENT');results=[]
threads=[threading.Thread(target=lambda:results.append(extend(f)))for _ in range(2)]
for t in threads:t.start()
for t in threads:t.join()
ck('two_concurrent_journal_calls_one35grant_dedup_request',sorted(map(len,results))==[0,35]and len(list((f.sync.directory/'requests').glob('*.REQUEST.json')))==1 and len([u for u in f.updates if u['budget_delta']==35])==1)
inside=[];benign_cohort=next(iter(q(f)['consumed']));benign_before=copy.deepcopy(q(f)['consumed'][benign_cohort])
def reenter(phase):
 if phase=='AFTER_PREPARED':
  inside.append(f.sync.drain_in_main(f.engine.assert_parent_lease))
  f.engine.update_authority(lambda reg:reg['registered_future_requests'][REQ]['consumed'][benign_cohort].update(CPU_fixture_benign_receipt={'synthetic':True}))
f.sync.fault_hook=reenter;f.sync.drain_in_main(f.engine.assert_parent_lease);ck('Main_reentrance_no_second_transaction',inside[0]['status']=='REENTRANT_ALREADY_DRAINING'and len(list((f.sync.directory/'transactions').glob('*/ACK.json')))==1)
ck('benign_concurrent_receipt_prefix_not_overwritten',all(q(f)['consumed'][benign_cohort][k]==v for k,v in benign_before.items())and q(f)['consumed'][benign_cohort]['CPU_fixture_benign_receipt']==dict(synthetic=True))
errors=[]
def addon_illegal():
 try:f.sync.drain_in_main(f.engine.assert_parent_lease)
 except AssertionError:errors.append('REFUSED')
t=threading.Thread(target=addon_illegal);t.start();t.join();ck('addon_cannot_call_Main_only_memory_update',errors==['REFUSED'])
# Register a second real profile but remove only its COMMITTED receipt in this
# private CPU root. It must never be inferred from q/matrix alone.
f=fixture('MISSING_COMMIT');rows=extend(f);cp=f.journal.journals/f.proposal['proposal_id']/'COMMITTED.json';saved=cp.read_bytes();cp.unlink();ck('missing_COMMITTED_no_scope_release_even_q_has_grant',f.sync.drain_in_main(f.engine.assert_parent_lease)['status']=='NO_NEW_PRIMARY_UNSPENT_IDENTITIES'and choose(f,[rows[0]['cohort']])is None);cp.write_bytes(saved)
ck('recovered_committed_scan_releases_without_reextend_grant',f.sync.drain_in_main(f.engine.assert_parent_lease)['status']=='APPENDED_EXACT_COMMITTED_PRIMARY_IDENTITIES')
# Drift refusal, exact restore preservation, and snapshot replay independence.
f=fixture('DRIFT');rows=extend(f);orig=read(f.cfgpath);changed=copy.deepcopy(orig);changed['status']='WRONG';put(f.cfgpath,changed);ck('source_authority_activation_drift_failclosed',f.sync.drain_in_main(f.engine.assert_parent_lease)['status']=='ENGINEERING_PENDING_SAFE_TO_RECOVER'and choose(f,[rows[0]['cohort']])is None);put(f.cfgpath,orig)
rejected('restore_refuses_unsynchronized_new_primary',lambda:S.restore_in_owner())
f.sync.drain_in_main(f.engine.assert_parent_lease);oldextend=f.sync.prior_extend;oldchoose=f.sync.prior_choose;restored=S.restore_in_owner();ck('exact_restore_retains_appended_scope_and_receipts_without_grant_changes',f.registry.extend==oldextend and f.journal.extend==f.captured_journal and f.res.choose_dispatch is oldchoose and restored['scope_not_shrunk'])
ck('restored_retained_callback_cannot_mutate_authority_or_scope',f.sync.drain_in_main(f.engine.assert_parent_lease)['status']=='RESTORED_SYNC_NOOP')
strict_text=(M/'memory_extra_strict.py').read_text();ck('old_worker_memory_strict_reads_own_snapshot_not_current_ACTIVE_MEMORY',"cfg=snap['config']"in strict_text and "snap['record']"in strict_text and 'ACTIVE_MEMORY.json'not in strict_text)
ck('all_frozen_MEM6_and_native46_and_original21pins_unchanged',all(sha(mem_source_cfg[r+'_path'])==mem_source_cfg[r+'_sha256']for r in ['library','frontend','owner','extra_strict','joint_padding','joint_io'])and all(sha(x['path'])==x['sha256']for x in source_plan['source_pins'])and sha(N/'bin/native')=='46c69a74154e0690afd82324a348da236baf90189d9a7e474b4b14eb01ab4f0e')
# Actual CPython main-thread pending delivery, using a retained callback. Only
# scalar CPU fixture functions are scheduled; no actual owner or model exists.
callback_rows=[];queue=S.RetainedMainQueue(lambda:callback_rows.append(dict(Main=threading.current_thread()is threading.main_thread(),ident=threading.get_ident()))or dict(status='CPU_ONLY_MAIN_ACK'))
t=threading.Thread(target=lambda:queue('CPU_ONLY_REQUEST'));t.start();t.join()
deadline=time.monotonic()+2
while not callback_rows and time.monotonic()<deadline:time.sleep(.001)
ck('actual_retained_Py_AddPendingCall_delivers_only_in_Main',len(callback_rows)==1 and callback_rows[0]['Main']and queue.last_result['status']=='CPU_ONLY_MAIN_ACK'and queue.pending is False)
api=queue._api;queue._api=lambda *a:-1;rejected('pending_queue_full_retains_request_and_allows_retry',lambda:queue('CPU_FULL'));ck('pending_queue_full_resets_inflight_flag',queue.pending is False and queue.last_request=='CPU_FULL');queue._api=api
t=threading.Thread(target=lambda:queue('CPU_RETRY'));t.start();t.join();ck('pending_queue_can_retry_after_full_without_new_grant',len(callback_rows)==2 and queue.pending is False)
# Private recovery tick schedules a recorded transaction after a queue failure;
# queue-only fake here avoids changing any actual owner or globally running VM.
f=fixture('RECOVERY_TICK');rows=extend(f);f.sync.fault_hook=lambda phase:(_ for _ in()).throw(OSError('CPU tick recovery'))if phase=='AFTER_PREPARED'else None;f.sync.drain_in_main(f.engine.assert_parent_lease);count=len(f.queued);f.sync.recovery_tick(force=True);ck('bounded_addon_recovery_tick_requeues_immutable_pending_transaction',len(f.queued)==count+1 and f.queued[-1].endswith('PREPARED.json'));f.sync.fault_hook=None;f.sync.drain_in_main(f.engine.assert_parent_lease)
f=fixture('AUTO_PENDING');S.restore_in_owner();S.install_on_frame(f.frame,f.cfgpath);f.sync=getattr(main,S.MARKER);automatic_rows=[]
t=threading.Thread(target=lambda:automatic_rows.extend(extend(f)));t.start()
while t.is_alive():t.join(.02)
deadline=time.monotonic()+3
while f.sync.main_queue.pending and time.monotonic()<deadline:time.sleep(.001)
ck('default_installer_real_Main_pending_callback_executes_scope_transaction',len(automatic_rows)==35 and f.sync.main_queue.last_result['status']=='APPENDED_EXACT_COMMITTED_PRIMARY_IDENTITIES'and f.sync.main_queue.last_error is None and len(list((f.sync.directory/'transactions').glob('*/ACK.json')))==1)
ck('default_Main_callback_preserves_E_guard_journal_and_has_no_model_or_grant_retry',f.journal.extend==f.captured_journal and f.E_calls==[f.proposal['proposal_id']]and len([u for u in f.updates if u['budget_delta']==35])==1)
retained=getattr(main,S.ID+'_RETAINED_MAIN_QUEUES');queue=f.sync.main_queue;ck('default_C_callback_is_explicitly_retained_in_Main_for_owner_lifetime',queue in retained)
budget=q(f)['budget'];active_sha=sha(f.privatecfg);S.restore_in_owner();t=threading.Thread(target=lambda:queue('CPU_POST_RESTORE_NOOP'));t.start();t.join();ck('retained_post_restore_real_Main_callback_is_metadata_NOOP',queue in retained and queue.last_result['status']=='RESTORED_SYNC_NOOP'and q(f)['budget']==budget and sha(f.privatecfg)==active_sha)
deps={x['path']:x['sha256']for x in source_plan['source_pins']};deps.update({str(M/n):sha(M/n)for n in ['future_memory.py','memory_owner.py','memory_frontend.py','memory_extra_strict.py','joint_padding_strict.py','joint_io_strict.py']});deps[str(J/'l2_registry_journal.py')]=sha(J/'l2_registry_journal.py')
report=dict(schema='FUTURE_MEMORY_PRIMARY_SCOPE_SYNC_CPU_V1',status='PASS',actual_journal_and_memory_interfaces_qualified=True,checks=checks,passed=len(checks),source_sha256=sha(D/'scope_sync.py'),driver_sha256=sha(__file__),dependency_pins=deps,fixture=str(fixture_run),cases=cases,actual_native_registered_canonical_update_authority_and_registry_extend_used_in_private_roots=True,original_production_grants_added=0,CPU_fixture_grants_not_scientific_or_production=True,callback_queue_and_Main_drain_manually_driven_in_CPU_fixture=True,resource_values_and_aging_objects_are_CPU_fixtures=True,production_owner_attached=False,production_mutations=0,model_starts=0,signals=0)
put(D/'CPU_QUALIFICATION.json',report);print(json.dumps(dict(status='PASS',checks=len(checks),path=str(D/'CPU_QUALIFICATION.json'),source_sha256=report['source_sha256'])))
