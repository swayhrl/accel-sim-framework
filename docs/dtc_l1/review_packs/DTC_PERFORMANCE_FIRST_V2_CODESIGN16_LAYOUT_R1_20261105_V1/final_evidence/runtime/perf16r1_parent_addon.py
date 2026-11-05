"""Main-only additive exact16 Physical x PIB attachment under new explicit V2 authorization. Explicit apply only; import is inert. Old controller source/frames/requests retained."""
from pathlib import Path
import json,os,sys,threading,hashlib,copy,importlib.util,datetime,fcntl
P=Path;R=P('/root/data/dtc_perf_first_v2_codesign16_layout_r1_20261105_v1');OLD=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');MARKER='DTC_PERFV2_CODESIGN16_LAYOUT_R1_OWNER_ADDON_V1';KEEP=[]
def rd(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);b=v if isinstance(v,bytes)else(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
 with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
def atomic(p,v):
 p=P(p);b=v if isinstance(v,bytes)else(json.dumps(v,sort_keys=True,indent=2)+'\n').encode();t=p.with_name('.'+p.name+'.PERFV2_CODESIGN16writing')
 with t.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.replace(t,p)
def load(n,p):
 m=__import__('types').ModuleType(n);m.__file__=str(p);exec(compile(P(p).read_bytes(),str(p),'exec'),m.__dict__);return m
def exact_native_route(before,block):
 anchor=b'#!/bin/sh\nset -eu\n'
 assert before.startswith(anchor)and block and block not in before and b'E2-DTCPFV2R1-'not in before
 assert b'E2-DTCPFV2R1-'in block,'EXACT_V2_CODESIGN16_ROUTE_MARKER_REQUIRED'
 after=anchor+block+before[len(anchor):]
 assert after.replace(block,b'',1)==before
 return after
def apply(directory):
 assert P(directory).resolve()==R.resolve(),'EXACT_NEW_EXECUTION_DIRECTORY_REQUIRED'
 assert sys.dont_write_bytecode,'CALLER_MUST_DISABLE_BYTECODE_WRITES_BEFORE_APPLY'
 assert threading.current_thread()is threading.main_thread()and os.getpid()==1498278 and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 main=sys.modules['__main__'];prior=getattr(main,'DTC_PERFV2_CODESIGN16_OWNER_ADDON_V1');assert not prior['thread'].is_alive(),'OLD16_PRIVATE_DISPATCHER_STILL_LIVE'
 with P('/root/data/dtc_perf_first_v2_codesign16_20261105_v1/control/DISPATCH_OWNER.lock').open('rb')as oldlock:fcntl.flock(oldlock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not hasattr(main,MARKER),'OBSERVE_EXISTING_ADDON_NO_BLIND_REAPPLY';plan=rd(R/'control/EXECUTION_PLAN.json');qual=rd(R/'control/CPU_QUALIFICATION.json');assert qual['status']=='PASS'and qual['execution_plan_sha256']==sha(R/'control/EXECUTION_PLAN.json')and qual['registry_candidate_sha256']==sha(R/'control/REGISTRY_REQUEST_CANDIDATE.json'),'STALE_CPU_QUALIFICATION'
 for x in plan['source_pins']:assert sha(x['path'])==x['sha256'],'SOURCE_PIN_DRIFT '+x['path']
 candidate=rd(R/'control/REGISTRY_REQUEST_CANDIDATE.json');assert candidate['budget']==candidate['remaining']==16 and not candidate['consumed']and len(candidate['admitted_specs'])==16
 assert set(candidate['admitted_specs'])==set(EXPECTED16_COHORTS),'EXACT_AUTHORIZED_COMBO16_ONLY'
 assert plan['expected_new_starts']==16
 auth=rd(R/'control/SCIENCE_AUTHORIZATION.json');assert auth['explicit_user_approval']is True and auth['approval_request_sha256']==sha(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')and set(auth['budgets'])==set(candidate['admitted_specs'])and all(x==1 for x in auth['budgets'].values())
 leasepath=T/'control/BATCH_LEASE.json';lease=rd(leasepath);assert lease['pid']==1498278 and lease['start_ticks']==977758783 and lease['controller_sha256']==plan['parent_controller_sha256']==sha(plan['parent_controller_path'])and plan['request']==candidate['request']=='DTC_PERF_FIRST_V2_CODESIGN16_LAYOUT_R1_20261105_V1'and plan['request']not in lease['additional_requests']
 for k in ['fd']:
  assert'FLOCK'in(P('/proc/self/fdinfo')/str(lease[k])).read_text()
 assert os.readlink('/proc/self/fd/'+str(lease['fd']))==str(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock')
 frame=sys._getframe()
 while frame is not None:
  if frame.f_code.co_name=='main'and P(frame.f_code.co_filename)==P(plan['parent_controller_path']):break
  frame=frame.f_back
 if frame is not None:
  handles=[frame.f_locals[name]for name in ['held','owner']]
 else:
  # The original main has returned into the qualified lifetime holder. Reuse
  # the same retained file objects; never recreate or seize either old lock.
  prior=getattr(main,'DTC_L2_MLP_ADDON_THREAD');assert prior.is_alive()
  target=prior._target;assert P(target.__code__.co_filename)==OLD/'tools/l2_parent_addon.py'and sha(OLD/'tools/l2_parent_addon.py')=='e72a5af7a41593d6eb8dd7a0b2940da63706437cc396407a464e59c66e4e72a0'
  handles=target.__globals__['_KEEPERS'];assert len(handles)==2 and handles[0].fileno()==lease['fd']
 assert {h.fileno()for h in handles}=={3,4},'EXACT_EXISTING_KEEPER_FDS_REQUIRED'
 assert os.readlink('/proc/self/fd/3')==str(T/'control/FINITE_CONTROLLER.lock')
 assert os.readlink('/proc/self/fd/4')==str(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock')
 for handle in handles:
  assert not handle.closed and'FLOCK'in(P('/proc/self/fdinfo')/str(handle.fileno())).read_text();KEEP.append(handle)
 e=load('perf16r1_main_engine',R/'tools/perf16r1_native.py');reg,epoch=e.authority();assert epoch['epoch']==2
 resources16=load('perf16r1_apply_readonly_resources',R/'tools/perf16r1_resources.py');actual_release=resources16.verify_direction_release(plan)
 independent=plan['independent_CPU_review_manifest'];assert sha(independent['path'])==independent['sha256'],'NEW16_INDEPENDENT_CPU_REVIEW_DRIFT'
 assert plan['request']not in reg['registered_future_requests'];state=dict(phase='PREFLIGHT',same_OS_owner=True,old_controller_source_unchanged=True,old_source_frame=frame,old_keepers=KEEP);setattr(main,MARKER,state)
 try:
  D=R/'control/actual_owner_attach_v1';D.mkdir(exist_ok=True);put(D/'LEASE_BEFORE.json',lease);put(D/'OLD_REQUEST_IDENTITIES_BEFORE.json',{k:dict(budget=v.get('budget'),remaining=v.get('remaining'),consumed=v.get('consumed'))for k,v in reg['registered_future_requests'].items()})
  entry=N/'bin/native';before=entry.read_bytes();block=(R/'control/NATIVE_ROUTE_BLOCK.sh').read_bytes();after=exact_native_route(before,block);put(D/'NATIVE_ENTRY_BEFORE.sh',before)
  def register(current):
   assert e.REQ not in current['registered_future_requests'];register_exact_request(current,candidate,actual_release)
  e.update_authority(register);state['phase']='REGISTERED_EXACT16'
  assert entry.read_bytes()==before,'NATIVE_ROUTE_CONCURRENT_CHANGE_PRESERVE';tmp=entry.with_name('.native.PERFV2_CODESIGN16writing');tmp.write_bytes(after);tmp.chmod(entry.stat().st_mode&0o777);os.replace(tmp,entry);put(D/'NATIVE_ROUTE_TRANSITION.json',dict(prior_sha256=hashlib.sha256(before).hexdigest(),new_sha256=sha(entry),exact_block_sha256=sha(R/'control/NATIVE_ROUTE_BLOCK.sh'),all_prior_bytes_preserved=True));state['phase']='EXACT_ROUTE_INSTALLED'
  new=copy.deepcopy(lease);new['additional_requests'].append(e.REQ);assert rd(leasepath)==lease;atomic(leasepath,new);state['phase']='OWNER_BOUND_EXISTING_LOCKS_RETAINED';e.assert_parent_lease();e.registered()
  ops=load('perf16r1_owner_finite16_ops',R/'tools/perf16r1_ops.py')
  def target():
   try:ops.run_scheduler()
   except BaseException as error:put(R/'analysis/OWNER_THREAD_ERROR.json',dict(error=repr(error),no_model_retry=True,registered_scope_preserved=True))
  worker=threading.Thread(target=target,name='DTC_PERFV2_CODESIGN16_LAYOUT_R1_ONLY',daemon=False);state['thread']=worker
  ack=dict(schema='DTC_PERFV2_CODESIGN16_LAYOUT_R1_OWNER_ACK_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='REGISTERED_EXACT16_SAME_OWNER_READY_TO_DISPATCH',owner_pid=os.getpid(),owner_start_ticks=977758783,old_primary_lease_request_unchanged=True,old_request_budgets_and_UUIDs_preserved=True,controller_sha256=lease['controller_sha256'],plan_sha256=sha(R/'control/EXECUTION_PLAN.json'),new_request=e.REQ,new_exact_credits=16,CPU_qualification_sha256=sha(R/'control/CPU_QUALIFICATION.json'),all_other_new_grants=0,old_models_signaled=0,old_remaining48_completion_required=False,only_fixed_authorized_combo16_granted=True,no_unplanned_variant_or_input=True,original_lock_handles_retained=True,addon_sha256=sha(__file__),native_route_exact16=True,runtime_release_evidence=actual_release)
  put(R/'control/PARENT_ADDON_ACK.json',ack);state.update(phase='ACKED',ACK=ack);worker.start();return ack
 except BaseException as error:
  state.update(phase='HOLD_FORWARD_RECONCILIATION',error=repr(error));put(R/'analysis/ADDON_ERROR_PRESERVE.json',dict(phase=state['phase'],error=repr(error),automatic_requeue=False,no_model_retries=True));raise

EXPECTED16_COHORTS=['E2-DTCPFV2R1-d984ea5475a581ad-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-d984ea5475a581ad-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-fc0705ae3721e999-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-fc0705ae3721e999-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-4114a3dc0d06b55b-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-4114a3dc0d06b55b-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-6df3a84b612086e8-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-6df3a84b612086e8-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-eededb785179fc04-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-eededb785179fc04-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-f437190767aaed49-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-f437190767aaed49-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-ae34174fbbdf83b2-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-ae34174fbbdf83b2-DH-PHYS1024-OOPIB192-V1', 'E2-DTCPFV2R1-e7bb67e63e3c3847-DH-PHYS768-OOPIB192-V1', 'E2-DTCPFV2R1-e7bb67e63e3c3847-DH-PHYS1024-OOPIB192-V1']

def register_exact_request(current,candidate,evidence):
 """Pure registration projection; actual authority write is exclusively parent's update_authority."""
 assert candidate['request']=='DTC_PERF_FIRST_V2_CODESIGN16_LAYOUT_R1_20261105_V1'
 assert candidate['budget']==candidate['remaining']==16 and not candidate['consumed']
 assert len(candidate['admitted_specs'])==16 and set(candidate['admitted_specs'])==set(EXPECTED16_COHORTS)
 assert candidate['request']not in current['registered_future_requests']
 assert evidence['authority_commit']=='425ff55a5b57eb28d968bfc8f79eb5f5060e6ebe'and evidence['exact_candidate_count']==16
 new=copy.deepcopy(candidate);new['runtime_release_evidence']=copy.deepcopy(evidence);current['registered_future_requests'][candidate['request']]=new
