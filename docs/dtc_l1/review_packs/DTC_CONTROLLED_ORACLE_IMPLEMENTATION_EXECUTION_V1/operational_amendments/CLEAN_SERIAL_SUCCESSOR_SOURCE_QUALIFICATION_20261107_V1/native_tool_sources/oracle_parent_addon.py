"""Explicit Main-only Oracle attachment. Import is inert; never invokes apply.

CPU fixtures may call the pure route/lease/registry projections. Actual apply
is reserved for Main after immutable source/binary/Gate0/CPU qualification.
"""
from pathlib import Path
import copy,datetime,hashlib,json,os,sys,threading,types,fcntl,signal

BASE=Path('/root/data/dtc_controlled_oracle_20261106_v1')
N=Path('/root/data/ep_l2_dtc_l1_native_v2')
T=Path('/root/data/dtc_main_v100_sweep_20261025_v1')
OLD=Path('/root/data/dtc_l2_mlp_exploration_20261027_v1')
OWNER_PID=1498278; OWNER_START=977758783
AUTHORITY='18b1ee9d339902e555fc2e04ef51c84f77dfe1b1'
STAGES={'initial8':8,'remaining24':24}
KEEP=[]
def rd(p): return json.loads(Path(p).read_bytes())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encoded(v): return v if isinstance(v,bytes) else (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def put(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as h: h.write(encoded(v));h.flush();os.fsync(h.fileno())
def atomic(p,v):
 p=Path(p);tmp=p.with_name('.'+p.name+'.ORACLEwriting.'+str(os.getpid()))
 with tmp.open('xb') as h: h.write(encoded(v));h.flush();os.fsync(h.fileno())
 os.replace(tmp,p)
 fd=os.open(p.parent,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def load(name,p):
 m=types.ModuleType(name);m.__file__=str(p);exec(compile(Path(p).read_bytes(),str(p),'exec'),m.__dict__);return m
def stage_budget(stage,qualified_modes):
 assert stage in STAGES and qualified_modes and len(set(qualified_modes))==len(qualified_modes)
 assert set(qualified_modes)<={'M_DATAREAD','L2_DATAREAD','L1_DATAREADY'}
 return STAGES[stage]*(1+len(qualified_modes))
def exact_native_route(before,block,stage):
 anchor=b'#!/bin/sh\nset -eu\n';marker=('DTC_ORACLE_'+stage.upper()+'_V1_ROUTE').encode()
 assert stage in STAGES and before.startswith(anchor) and block and marker in block
 assert marker not in before and block not in before,'STAGE_ROUTE_ALREADY_PRESENT_NO_REAPPLY'
 after=anchor+block+before[len(anchor):]
 assert after.replace(block,b'',1)==before,'ALL_PRIOR_BYTES_MUST_REMAIN_EXACT'
 return after
def lease_projection(lease,plan):
 assert lease['pid']==plan['parent_pid']==OWNER_PID and lease['start_ticks']==plan['parent_start_ticks']==OWNER_START
 assert lease['controller_sha256']==plan['parent_controller_sha256']
 assert plan['request'] not in lease['additional_requests']
 new=copy.deepcopy(lease);new['additional_requests'].append(plan['request'])
 old=copy.deepcopy(new);old['additional_requests'].pop();assert old==lease
 return new
def validate_candidate(candidate,plan):
 assert candidate.get('mock') is not True and plan.get('mock') is not True,'MOCK_ARTIFACT_IS_NOT_SCIENCE'
 assert candidate.get('ready_for_registration') is True and plan.get('preparation_phase')=='SCIENCE_FINAL_FROZEN','CPU_DRAFT_IS_NOT_SCIENCE'
 n=stage_budget(plan['stage'],plan['qualified_modes'])
 assert candidate['request']==plan['request']
 assert candidate['budget']==candidate['remaining']==plan['expected_new_starts']==n
 assert not candidate['consumed'] and not candidate['sealed']
 assert len(candidate['admitted_specs'])==n and set(candidate['admitted_specs'])==set(plan['authorized_cohorts'])
 assert candidate['model_automatic_retries']==0 and candidate['new_registration_only'] is True
 assert candidate['approved_contract_commit']==plan['approved_contract_commit']==AUTHORITY
 assert candidate['owner_pid']==OWNER_PID and candidate['owner_start_ticks']==OWNER_START
 assert candidate['old_request_budget_reused'] is False
 return n
def register_exact_request(current,candidate,plan,evidence):
 """Pure passed-snapshot EX mutator. No file, lock, engine or authority read."""
 n=validate_candidate(candidate,plan)
 assert evidence['authority_commit']==AUTHORITY and evidence['exact_candidate_count']==n
 assert evidence['stage']==plan['stage'] and set(evidence['qualified_modes'])==set(plan['qualified_modes'])
 assert evidence['Gate0_CPU_source_strict_independent_review']=='PASS'
 if plan['stage']=='remaining24':
  assert evidence['Gate2_any_mode_fixed8_and_shared_OFF_accepted_independently_reviewed']=='PASS'
  assert set(evidence['Gate2_released_modes']) and set(evidence['Gate2_released_modes'])<=set(plan['qualified_modes'])
 assert candidate['request'] not in current['registered_future_requests']
 peers=copy.deepcopy(current['registered_future_requests']);history=copy.deepcopy((current.get('old_source_history'),current.get('qualification_history')))
 new=copy.deepcopy(candidate);new['runtime_release_evidence']=copy.deepcopy(evidence)
 current['registered_future_requests'][candidate['request']]=new
 assert all(current['registered_future_requests'][k]==v for k,v in peers.items())
 assert history==(current.get('old_source_history'),current.get('qualification_history'))
 return n
def retained_handles(main,plan,lease):
 frame=sys._getframe()
 while frame is not None:
  if frame.f_code.co_name=='main' and Path(frame.f_code.co_filename)==Path(plan['parent_controller_path']): break
  frame=frame.f_back
 if frame is not None: handles=[frame.f_locals[name] for name in ('held','owner')]
 else:
  prior=getattr(main,'DTC_L2_MLP_ADDON_THREAD');assert prior.is_alive()
  target=prior._target
  assert Path(target.__code__.co_filename)==OLD/'tools/l2_parent_addon.py'
  assert sha(OLD/'tools/l2_parent_addon.py')=='e72a5af7a41593d6eb8dd7a0b2940da63706437cc396407a464e59c66e4e72a0'
  handles=target.__globals__['_KEEPERS']
 assert len(handles)==2 and {h.fileno() for h in handles}=={3,4}
 assert os.readlink('/proc/self/fd/3')==str(T/'control/FINITE_CONTROLLER.lock')
 assert os.readlink('/proc/self/fd/4')==str(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock')
 assert lease['fd']==4
 for h in handles:
  assert not h.closed and 'FLOCK' in Path('/proc/self/fdinfo',str(h.fileno())).read_text()
 return handles
def owner_cpu_preflight(R,plan):
 """Read actual owner shutdown state and run one pure CPU task before grants.

 Never import a new futures module and never reset interpreter/private flags.
 The retained early lifetime hook may already set threading._SHUTTING_DOWN
 while existing futures.thread._shutdown remains False and usable.
 """
 assert threading.current_thread() is threading.main_thread()
 assert not sys.is_finalizing(),'INTERPRETER_FINALIZING_HOLD_NO_REGISTER'
 fm=sys.modules.get('concurrent.futures.thread')
 assert fm is not None and getattr(fm,'_shutdown',None) is False,'EXISTING_FUTURES_MODULE_NOT_AVAILABLE_HOLD'
 prior=signal.getsignal(signal.SIGWINCH)
 assert prior in (signal.SIG_DFL,signal.SIG_IGN),'MEANINGFUL_FOREIGN_SIGWINCH_HANDLER_HOLD_NO_REGISTER'
 pool=fm.ThreadPoolExecutor(max_workers=1,thread_name_prefix='DTC_ORACLE_CPU_PREFLIGHT')
 try:
  result=pool.submit(lambda:{'pid':os.getpid(),'worker_is_main':threading.current_thread() is threading.main_thread(),'kind':'PURE_CPU_NO_MODEL'}).result(timeout=5)
 finally:pool.shutdown(wait=True)
 assert result['pid']==OWNER_PID and result['worker_is_main'] is False
 # Exercise typed callback construction/restoration before registration. Do not
 # queue it. Actual arming is done once by the shared pool after attachment.
 pending=load('oracle_owner_pendingcall_preflight',R/'tools/oracle_pendingcall.py')
 probe=pending.OnceMainCallback(lambda:{'CPU_PREFLIGHT_ONLY':True})
 probe.restore_wake_handler();KEEP.extend((pending,probe))
 assert signal.getsignal(signal.SIGWINCH)==prior
 return {'schema':'DTC_ORACLE_REAL_OWNER_CPU_PREFLIGHT_V1','sys_is_finalizing':False,'threading_SHUTTING_DOWN_observed':getattr(threading,'_SHUTTING_DOWN',None),'existing_futures_thread_shutdown':fm._shutdown,'pure_CPU_task':result,'SIGWINCH_prior':str(prior),'typed_pending_callback_constructed_not_queued':True,'wake_handler_restored':True,'private_flags_written':False,'models_started':0}
def finalize_and_attach_extension(directory):
 """Once-only Main-thread continuation; all actual gates are read evidence.

 Called by the same owner's typed pending callback, never an external
 dispatcher. No mode gate is manufactured from performance or completion count.
 """
 assert Path(directory).resolve()==BASE.resolve() and threading.current_thread() is threading.main_thread()
 assert os.getpid()==OWNER_PID
 main=sys.modules['__main__'];initial=getattr(main,'DTC_CONTROLLED_ORACLE_INITIAL8_OWNER_ADDON_V1')
 assert not initial.get('extension_finalizer_entered',False),'EXTENSION_CALLBACK_ONCE_NO_BLIND_RETRY'
 initial['extension_finalizer_entered']=True
 R8=BASE/'initial8';plan=rd(R8/'control/EXECUTION_PLAN.json');ref=plan['extension_automation']
 assert sha(ref['path'])==ref['sha256'];auto=rd(ref['path'])
 assert auto['schema']=='DTC_ORACLE_EXTENSION_AUTOMATION_V1' and auto['remaining_root']==str(BASE/'remaining24')
 for key in ('builder','build_release_template','matrix'):assert sha(auto[key]['path'])==auto[key]['sha256'],'EXTENSION_AUTOMATION_PIN_DRIFT '+key
 resources=load('oracle_initial_extension_gate_reader',R8/'tools/oracle_resources.py')
 released=[];statuses={};witness=[]
 for mode in plan['qualified_modes']:
  try:
   ev=resources.verify_mode_extension_receipt(plan,mode);released.append(mode);statuses[mode]={'status':'PASS','evidence':ev};witness.append(ev)
  except resources.WaitInitialRuntimeGate as error:statuses[mode]={'status':'WAIT','reason':str(error)}
  except (AssertionError,KeyError,OSError,ValueError) as error:statuses[mode]={'status':'HOLD','reason':repr(error)}
 assert released,'NO_REAL_MODE_GATE2_PASS_NO_EXTENSION_REGISTER'
 release=rd(auto['build_release_template']['path'])
 assert set(release['qualified_modes'])==set(plan['qualified_modes'])
 gate={'schema':'DTC_ORACLE_GATE2_REGISTRATION_RELEASE_V1','status':'PASS','released_modes':released,'mode_releases':statuses,'fixed8_matched_OFF_and_mode_strict_archive_restore_independently_reviewed':True,'independent_mode_witnesses':witness,'all_other_modes_remain_individually_gated':True}
 serial=hashlib.sha256(encoded(gate)).hexdigest();G=BASE/'control/extension_automation'/serial
 G.mkdir(parents=True,exist_ok=False);put(G/'GATE2_REGISTRATION_RELEASE.json',gate)
 release['Gate2_mode_releases']=statuses;release['Gate2_release']={'path':str(G/'GATE2_REGISTRATION_RELEASE.json'),'sha256':sha(G/'GATE2_REGISTRATION_RELEASE.json')}
 put(G/'REGISTRATION_BUILD_INPUT.FROM_REAL_GATE2.json',release)
 builder=load('oracle_frozen_extension_plan_builder',auto['builder']['path'])
 built=builder.build(release,auto['matrix']['path'],'remaining24',phase='final',finalize_draft=True)
 # Final stage artifact validation and CPU qualification are independently
 # supplied predeclared engineering hooks, never a hidden scientific canary.
 hook=auto['final_artifact_qualifier'];assert sha(hook['path'])==hook['sha256']
 qual=load('oracle_extension_final_artifact_qualifier',hook['path'])
 qualification=getattr(qual,hook['function'])(str(BASE/'remaining24'))
 assert qualification['status']=='PASS','FINAL_EXTENSION_ARTIFACT_CPU_QUALIFICATION_FAILED'
 attached=apply(str(BASE),'remaining24')
 receipt={'schema':'DTC_ORACLE_AUTOMATIC_EXTENSION_MAINTHREAD_ACK_V1','released_modes_at_registration':released,'mode_statuses':statuses,'build':built,'qualification':qualification,'attachment':attached,'same_OS_owner':True,'new_dispatch_pool_threads':0,'all_Q_actual_consumption_still_per_mode_Gate2':True}
 put(G/'FINALIZATION_AND_ATTACHMENT_ACK.json',receipt);initial['extension_finalizer_ACK']=receipt;return receipt
def apply(directory,stage):
 """Side-effectful Main-only operation. NEVER called by this preparation."""
 assert Path(directory).resolve()==BASE.resolve() and stage in STAGES
 assert sys.dont_write_bytecode,'CALLER_MUST_DISABLE_BYTECODE_WRITES'
 assert threading.current_thread() is threading.main_thread()
 assert os.getpid()==OWNER_PID and int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==OWNER_START
 R=BASE/stage;main=sys.modules['__main__'];marker='DTC_CONTROLLED_ORACLE_'+stage.upper()+'_OWNER_ADDON_V1'
 assert not hasattr(main,marker),'OBSERVE_EXISTING_ADDON_NO_BLIND_REAPPLY'
 # Existing historical scheduler must be naturally finished; inspect its
 # retained state only. Never signal it or steal its dispatcher lock.
 prior=getattr(main,'DTC_PERFV2_CODESIGN16_LAYOUT_R1_OWNER_ADDON_V1',None)
 assert prior is not None and not prior['thread'].is_alive(),'OLD_R1_PRIVATE_DISPATCHER_STILL_LIVE'
 if stage=='remaining24':
  previous=getattr(main,'DTC_CONTROLLED_ORACLE_INITIAL8_OWNER_ADDON_V1')
  assert getattr(main,'DTC_CONTROLLED_ORACLE_SHARED_POOL_V1',None) is not None,'EXISTING_SHARED_POOL_REQUIRED'
 plan=rd(R/'control/EXECUTION_PLAN.json');candidate=rd(R/'control/REGISTRY_REQUEST_CANDIDATE.json')
 n=validate_candidate(candidate,plan)
 qual=rd(R/'control/CPU_QUALIFICATION.json')
 assert qual['status']=='PASS' and qual['execution_plan_sha256']==sha(R/'control/EXECUTION_PLAN.json') and qual['registry_candidate_sha256']==sha(R/'control/REGISTRY_REQUEST_CANDIDATE.json')
 for x in plan['source_pins']: assert sha(x['path'])==x['sha256'],'SOURCE_PIN_DRIFT '+x['path']
 independent=plan['independent_CPU_review_manifest'];assert sha(independent['path'])==independent['sha256']
 auth=rd(R/'control/SCIENCE_AUTHORIZATION.json')
 assert auth['explicit_user_approval'] is True and auth['authority_commit']==AUTHORITY
 assert auth['approval_request_sha256']==sha(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')
 assert set(auth['budgets'])==set(candidate['admitted_specs']) and all(v==1 for v in auth['budgets'].values())
 leasepath=T/'control/BATCH_LEASE.json';lease=rd(leasepath)
 assert plan['parent_controller_sha256']==sha(plan['parent_controller_path'])
 newlease=lease_projection(lease,plan);handles=retained_handles(main,plan,lease);KEEP.extend(handles)
 engine=load('oracle_'+stage+'_Main_engine',R/'tools/oracle_native.py')
 reg,epoch=engine.authority();assert epoch['epoch']==2
 resources=load('oracle_'+stage+'_Main_resources',R/'tools/oracle_resources.py')
 # All potentially lock-taking gate/source/archive checks happen BEFORE EX.
 evidence=resources.verify_registration_release(plan,candidate)
 preflight=owner_cpu_preflight(R,plan) if stage=='initial8' else {'same_shared_pool_attachment_only':True,'models_started':0}
 if stage=='initial8':
  auto_ref=plan['extension_automation'];assert sha(auto_ref['path'])==auto_ref['sha256']
  auto=rd(auto_ref['path']);assert auto['schema']=='DTC_ORACLE_EXTENSION_AUTOMATION_V1'
  for key in ('builder','build_release_template','matrix','final_artifact_qualifier'):assert sha(auto[key]['path'])==auto[key]['sha256']
 assert plan['request'] not in reg['registered_future_requests']
 entry=N/'bin/native';before=entry.read_bytes();block=(R/'control/NATIVE_ROUTE_BLOCK.sh').read_bytes();after=exact_native_route(before,block,stage)
 state={'phase':'PREFLIGHT','old_keepers':handles,'same_OS_owner':True};setattr(main,marker,state)
 try:
  D=R/'control/actual_owner_attach_v1';D.mkdir(exist_ok=False)
  put(D/'OWNER_REAL_CPU_PREFLIGHT.json',preflight)
  put(D/'LEASE_BEFORE.json',lease);put(D/'NATIVE_ENTRY_BEFORE.sh',before)
  put(D/'OLD_REQUEST_IDENTITIES_BEFORE.json',{k:{x:v.get(x) for x in ('budget','remaining','consumed')} for k,v in reg['registered_future_requests'].items()})
  # No authority(), registered(), canonical() or resource reader in closure.
  def register(snapshot):register_exact_request(snapshot,candidate,plan,evidence)
  engine.update_authority(register);state['phase']='REGISTERED_EXACT_CONDITIONAL_SCOPE'
  assert entry.read_bytes()==before,'CONCURRENT_NATIVE_ROUTE_CHANGE_FORWARD_RECONCILE'
  temp=entry.with_name('.native.ORACLE_'+stage+'.writing');
  with temp.open('xb') as h:h.write(after);h.flush();os.fsync(h.fileno())
  temp.chmod(entry.stat().st_mode&0o777);os.replace(temp,entry)
  put(D/'NATIVE_ROUTE_TRANSITION.json',{'prior_sha256':hashlib.sha256(before).hexdigest(),'new_sha256':sha(entry),'block_sha256':sha(R/'control/NATIVE_ROUTE_BLOCK.sh'),'all_prior_bytes_preserved':True})
  state['phase']='EXACT_ROUTE_INSTALLED';assert rd(leasepath)==lease,'LEASE_CONCURRENT_CHANGE_FORWARD_RECONCILE';atomic(leasepath,newlease)
  state['phase']='OWNER_BOUND_EXISTING_LOCKS_RETAINED';engine.assert_parent_lease();engine.registered()
  ops=load('oracle_'+stage+'_owner_ops',R/'tools/oracle_ops.py')
  attachment=ops.attach_registered_request(str(R))
  if stage=='remaining24':
   ack={'schema':'DTC_CONTROLLED_ORACLE_OWNER_ACK_V1','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':stage,'status':'REGISTERED_REQUEST_ATTACHED_EXISTING_SHARED_POOL','owner_pid':os.getpid(),'owner_start_ticks':OWNER_START,'request':plan['request'],'new_exact_credits':n,'plan_sha256':sha(R/'control/EXECUTION_PLAN.json'),'attachment':attachment,'new_dispatch_pool_threads':0,'old_request_budgets_UUIDs_preserved':True,'original_fd3_fd4_retained':True,'runtime_release_evidence':evidence}
   put(R/'control/PARENT_ADDON_ACK.json',ack);state.update(phase='ATTACHED_EXISTING_SHARED_POOL',ACK=ack);return ack
  callback=lambda:finalize_and_attach_extension(str(BASE))
  KEEP.append(callback);armed=ops.install_extension_callback(callback)
  def target():
   try:ops.run_scheduler()
   except BaseException as error:put(R/'analysis/OWNER_THREAD_ERROR.json',{'error':repr(error),'no_model_retry':True,'registered_scope_preserved':True})
  worker=threading.Thread(target=target,name='DTC_ORACLE_'+stage.upper()+'_ONLY',daemon=False);state['thread']=worker
  ack={'schema':'DTC_CONTROLLED_ORACLE_OWNER_ACK_V1','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':stage,'status':'REGISTERED_SAME_OWNER_READY_TO_DISPATCH','owner_pid':os.getpid(),'owner_start_ticks':OWNER_START,'request':plan['request'],'new_exact_credits':n,'plan_sha256':sha(R/'control/EXECUTION_PLAN.json'),'CPU_qualification_sha256':sha(R/'control/CPU_QUALIFICATION.json'),'addon_sha256':sha(__file__),'runtime_release_evidence':evidence,'all_other_new_grants':0,'old_request_budgets_UUIDs_preserved':True,'original_fd3_fd4_retained':True,'old_models_signaled':0}
  put(R/'control/PARENT_ADDON_ACK.json',ack);state.update(phase='ACKED',ACK=ack);worker.start();return ack
 except BaseException as error:
  state.update(phase='HOLD_FORWARD_RECONCILIATION',error=repr(error))
  put(R/'analysis/ADDON_ERROR_PRESERVE.json',{'phase':state['phase'],'error':repr(error),'automatic_requeue':False,'no_model_retry':True,'no_rollback_of_consumed_identity':True});raise
