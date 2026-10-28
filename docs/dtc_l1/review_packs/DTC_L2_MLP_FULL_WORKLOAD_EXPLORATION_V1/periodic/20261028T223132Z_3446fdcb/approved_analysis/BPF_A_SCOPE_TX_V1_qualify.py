"""Private authority/files, real frozen CPU2 library + owner updater only."""
import pathlib,json,hashlib,copy,types,threading,sys,tempfile,importlib.util,os
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');D=A/'agents/A/bpf_memory_scope_transaction_v1';R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
m=load('tx_candidate',D/'scope_transaction.py');prioritypath=A/'agents/A/bpf_engineering_resource_priority_v1/resource_priority.py';priority=load('frozen_scope_proposal',prioritypath)
bridgepath=A/'coordinator/bpf_canary_orchestration_v2/scope_bridge.py';bridge=load('main_scope_v2',bridgepath);planpath=A/'coordinator/strace_bpf_engineering_canary_plan_v1/DRAFT_PLAN.json';plan=read(planpath);scope=bridge.CanaryScope(plan);cp=A/'coordinator/bpf_canary_orchestration_v1/ENGINEERING_EXCLUSION_CONTRACT.json'
libpath=R/'control/operational_amendments/cpu_spare_memory_v2/cpu_memory.py';ownerpath=R/'control/operational_amendments/cpu_spare_memory_v2/cpu_owner.py';lib=load('actual_cpu2_library',libpath);owner=load('actual_cpu2_owner',ownerpath)
cfg=read(R/'control/operational_amendments/future_memory_admission_v1/ACTIVE_MEMORY.json');realq=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][lib.REQ];lib.validate(cfg,realq)
marker=owner.MEMORY;original=getattr(sys.modules['__main__'],marker,None);checks=[]
def check(name,value):assert value,name;checks.append(dict(name=name,status='PASS'))
def rejected(fn):
 try:fn()
 except Exception:return True
 return False
def fixture():
 root=P(tempfile.mkdtemp(prefix='PRIVATE_SCOPE_TX_',dir=D));put(root/'control/MATRIX_CURRENT.json',read(R/'control/MATRIX_CURRENT.json'));put(root/'control/SCOPE.json',read(R/'control/SCOPE.json'));put(root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
 specs={r['cohort']:read(r['draft_spec_path'])for r in plan['rows']};q=copy.deepcopy(realq)
 for c,s in specs.items():put(root/'control/specs'/(c+'.json'),s);q['admitted_specs'][c]=sha(root/'control/specs'/(c+'.json'))
 q['budget']+=4;q['remaining']+=4;q['authorized_engineering_observation_canaries']=[dict(cohort=c,role=bridge.ROLE,mode=r['mode'],science_projection_sha256=r['science_projection_sha256'],primary_statistics_excluded=True,validated_union_authorized=False)for c,r in scope.rows.items()]
 reg={'registered_future_requests':{lib.REQ:q}};regpath=root/'PRIVATE_REGISTRY.json';put(regpath,reg);active=root/'ACTIVE_MEMORY.json';put(active,cfg)
 trace=[];fail_resource=[False];lease_bad=[False]
 def authority():return read(regpath)
 def registered():return authority(),None,authority()['registered_future_requests'][lib.REQ],None
 def lease():
  assert not lease_bad[0],'WRONG_LEASE_FIXTURE';return dict(pid=os.getpid(),start_ticks=m.birth())
 def update(fn):
  assert getattr(memory['aging'].lock,'_is_owned')()and getattr(sync.lock,'_is_owned')(),'LOCK_ORDER_MISSING'
  trace.append('AUTHORITY_INTERNAL');reg=authority();fn(reg);put(regpath,reg)
 engine=types.SimpleNamespace(registered=registered,canonical=lambda c:copy.deepcopy(specs[c])if c in specs else {'cohort':c},assert_parent_lease=lease,update_authority=update)
 lock=threading.RLock();state=types.SimpleNamespace(previous_C=71,protected=36*1024**3,pending_releases={'preserved':17});aging=types.SimpleNamespace(lock=lock,state=state,original=lambda *a:None)
 def resources(*a):
  if fail_resource[0]:raise RuntimeError('PRIVATE_PHYSICAL_RESOURCE_LEAF_FAILURE')
  return dict(admission_decision=dict(admission_RAM_budget_bytes=1000),total_projected_additional_RAM_bytes=11)
 res=types.SimpleNamespace(resources=resources);memory=dict(lib=lib,context={'cfg':copy.deepcopy(cfg)},cfg=copy.deepcopy(cfg),engine=engine,aging=aging,res=res,new_resources=resources,new_choose=aging.original)
 class Sync:
  def check(self):return engine.registered()[2],{}
  def stable_memory(self):
   q,_=self.check();value=read(active);assert value==memory['context']['cfg'];lib.validate(value,q);return q,value
 sync=Sync();sync.memory=memory;sync.engine=engine;sync.root=root;sync.cfg={'memory_active_path':str(active)};sync.lock=threading.RLock();sync.owner_module=owner
 setattr(sys.modules['__main__'],marker,memory)
 pins={str(p):sha(p)for p in[P(m.__file__),prioritypath,bridgepath,planpath,cp,libpath,ownerpath]}
 tx=m.ScopeTransaction(sync,scope,cp,priority,pins,dict(pid=os.getpid(),start_ticks=m.birth()),root/'transactions')
 return types.SimpleNamespace(tx=tx,root=root,regpath=regpath,active=active,memory=memory,sync=sync,authority=authority,engine=engine,trace=trace,fail_resource=fail_resource,lease_bad=lease_bad,specs=specs)
try:
 f=fixture();qbefore=copy.deepcopy(f.engine.registered()[2]);cfgbytes=f.active.read_bytes();p=f.tx.prepare();prepared=read(p)
 check('prepare_saves_exact_old_bytes_full_records_no_mutation',f.active.read_bytes()==cfgbytes and f.engine.registered()[2]==qbefore and p.with_name('OLD_ACTIVE_MEMORY.json').read_bytes()==cfgbytes)
 result=f.tx.apply(p);qafter=f.engine.registered()[2];expected=copy.deepcopy(qbefore);expected['additional_operational_overlays'][lib.ID]=prepared['new_record']
 check('real_official_CPU2_update_scope_and_stable_ACK',qafter==expected and result['status']=='EXACT4_CPU2_SCOPE_APPEND_ACK'and f.memory['context']['cfg']==prepared['new_config'])
 check('only_CPU2_fullrow_changes_preserving_extras_budget_consumed',qafter['budget']==qbefore['budget']and qafter['remaining']==qbefore['remaining']and qafter['consumed']==qbefore['consumed']and all(qafter['additional_operational_overlays'][k]==v for k,v in qbefore['additional_operational_overlays'].items()if k!=lib.ID))
 check('official_owner_rebases_previous_C_without_R_tokens_release',f.memory['aging'].state.previous_C==989 and f.memory['aging'].state.protected==36*1024**3 and f.memory['aging'].state.pending_releases=={'preserved':17}and result['policy_change_completion_credit_bytes']==0)
 beforecount=len(f.trace);acksha=sha(p.with_name('ACK.json'));again=f.tx.apply(p)
 check('repeat_ACK_idempotent_no_authority_write',again==result and len(f.trace)==beforecount and sha(p.with_name('ACK.json'))==acksha)
 for phase in ['AFTER_AUTHORITY','AFTER_ACTIVE_FILE','AFTER_OWNER_CONTEXT']:
  f=fixture();p=f.tx.prepare()
  def fault(x):
   if x==phase:raise RuntimeError('SIMULATED_CRASH_'+x)
  f.tx.fault_hook=fault;check('inject_crash_'+phase,rejected(lambda:f.tx.apply(p))and not p.with_name('ACK.json').exists());f.tx.fault_hook=None;ack=f.tx.apply(p)
  check('recover_same_PREPARED_'+phase,ack['status']=='EXACT4_CPU2_SCOPE_APPEND_ACK'and len(f.trace)==1 and f.sync.stable_memory()[1]==read(p)['new_config'])
 for kind in ['unknown_record','unknown_active','unknown_context']:
  f=fixture();p=f.tx.prepare()
  if kind=='unknown_record':reg=f.authority();reg['registered_future_requests'][lib.REQ]['additional_operational_overlays'][lib.ID]['UNKNOWN_THIRD_PARTY']=True;put(f.regpath,reg)
  elif kind=='unknown_active':v=read(f.active);v['UNKNOWN_THIRD_PARTY']=True;put(f.active,v)
  else:f.memory['context']['cfg']=dict(f.memory['context']['cfg'],UNKNOWN_THIRD_PARTY=True)
  regbytes=f.regpath.read_bytes();activebytes=f.active.read_bytes();check(kind+'_HOLD_before_any_overwrite',rejected(lambda:f.tx.apply(p))and f.regpath.read_bytes()==regbytes and f.active.read_bytes()==activebytes)
 f=fixture();p=f.tx.prepare();reg=f.authority();reg['registered_future_requests'][lib.REQ]['benign_concurrent_receipt']={'uuid':'PRIVATE_OTHER_RECEIPT'};put(f.regpath,reg);f.tx.apply(p)
 check('benign_other_receipts_preserved_not_whole_registry_hash_locked',f.engine.registered()[2]['benign_concurrent_receipt']=={'uuid':'PRIVATE_OTHER_RECEIPT'})
 f=fixture();p=f.tx.prepare();f.fail_resource[0]=True;check('official_owner_resource_failure_rolls_context_back',rejected(lambda:f.tx.apply(p))and f.memory['context']['cfg']==read(p)['old_config']and f.memory['aging'].state.previous_C==71);f.fail_resource[0]=False;f.tx.apply(p)
 check('resume_after_official_owner_failure_no_second_registry_write',len(f.trace)==1 and f.sync.stable_memory()[1]==read(p)['new_config'])
 for kind in ['claim','INTENT','spent','bound_CPU','wrong_owner','wrong_lease']:
  f=fixture();c=next(iter(f.specs))
  if kind=='claim':put(f.root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{c:{}}})
  elif kind=='INTENT':put(f.root/'control/qualification_ledger'/(c+'.INTENT.json'),{})
  elif kind=='spent':reg=f.authority();reg['registered_future_requests'][lib.REQ]['consumed'][c]={'uuid':'PRIVATE_SPENT'};put(f.regpath,reg)
  elif kind=='bound_CPU':f.specs[c]['host_cpu']=0;put(f.root/'control/specs'/(c+'.json'),f.specs[c]);reg=f.authority();reg['registered_future_requests'][lib.REQ]['admitted_specs'][c]=sha(f.root/'control/specs'/(c+'.json'));put(f.regpath,reg)
  elif kind=='wrong_owner':f.tx.owner['start_ticks']+=1
  else:f.lease_bad[0]=True
  check(kind+'_reject_before_prepare',rejected(f.tx.prepare))
 f=fixture();errors=[]
 def wrong_thread():errors.append(rejected(f.tx.prepare))
 t=threading.Thread(target=wrong_thread);t.start();t.join();check('non_Main_thread_rejected',errors==[True])
 f=fixture();p=f.tx.prepare();before=f.regpath.read_bytes();oldvalidate=lib.validate
 try:
  lib.validate=lambda *a:(_ for _ in()).throw(RuntimeError('SIX_SOURCE_OR_QA_DRIFT_PRIVATE_FIXTURE'))
  check('official_all_six_source_validation_precedes_any_mutation',rejected(lambda:f.tx.apply(p))and f.regpath.read_bytes()==before)
 finally:lib.validate=oldvalidate
 proof=dict(schema='BPF_EXACT4_MEMORY_SCOPE_TRANSACTION_CPU_QUALIFICATION_V1',status='PASS',qualification_only=True,checks=checks,source_sha256=sha(m.__file__),driver_sha256=sha(__file__),source_pins=f.tx.pins,actual_owner_function='CPU2 cpu_owner.update_scope_in_owner',owner_function_source_sha256=sha(ownerpath),physical_resources_leaf='EXPLICIT_PRIVATE_MOCK_ONLY',scope='Private registry/config/files, same driver PID/birth/Main; real frozenCPU2 lib.validate/record and officialowner function. No actual production owner, authority write, grant, dispatch or model.',production_changes=0,new_grants=0,model_starts=0)
 put(D/'CPU_QUALIFICATION.json',proof);print(json.dumps(dict(path=str(D),source_sha256=sha(m.__file__),QA_sha256=sha(D/'CPU_QUALIFICATION.json'),checks=len(checks))))
finally:
 if original is None:
  if hasattr(sys.modules['__main__'],marker):delattr(sys.modules['__main__'],marker)
 else:setattr(sys.modules['__main__'],marker,original)
