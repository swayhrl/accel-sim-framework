"""Main-only additive exact48 attachment. Old controller source/frames/requests retained."""
from pathlib import Path
import json,os,sys,threading,hashlib,copy,importlib.util,datetime,fcntl
P=Path;R=P('/root/data/dtc_stage_iia_remaining48_20261104_v1');OLD=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');MARKER='DTC_STAGEII_REMAINING48_OWNER_ADDON_V1';KEEP=[]
def rd(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);b=v if isinstance(v,bytes)else(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
 with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
def atomic(p,v):
 p=P(p);b=v if isinstance(v,bytes)else(json.dumps(v,sort_keys=True,indent=2)+'\n').encode();t=p.with_name('.'+p.name+'.STAGEII48writing')
 with t.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.replace(t,p)
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def apply(directory):
 assert threading.current_thread()is threading.main_thread()and os.getpid()==1498278 and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 main=sys.modules['__main__'];assert not hasattr(main,MARKER),'OBSERVE_EXISTING_ADDON_NO_BLIND_REAPPLY';plan=rd(R/'control/EXECUTION_PLAN.json');qual=rd(R/'control/CPU_QUALIFICATION.json');assert qual['status']=='PASS'and qual['execution_plan_sha256']==sha(R/'control/EXECUTION_PLAN.json')and qual['registry_candidate_sha256']==sha(R/'control/REGISTRY_REQUEST_CANDIDATE.json'),'STALE_CPU_QUALIFICATION'
 for x in plan['source_pins']:assert sha(x['path'])==x['sha256'],'SOURCE_PIN_DRIFT '+x['path']
 candidate=rd(R/'control/REGISTRY_REQUEST_CANDIDATE.json');assert candidate['budget']==candidate['remaining']==48 and not candidate['consumed']and len(candidate['admitted_specs'])==48
 auth=rd(R/'control/SCIENCE_AUTHORIZATION.json');assert auth['explicit_user_approval']is True and auth['approval_request_sha256']==sha(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json')and set(auth['budgets'])==set(candidate['admitted_specs'])and all(x==1 for x in auth['budgets'].values())
 leasepath=T/'control/BATCH_LEASE.json';lease=rd(leasepath);assert lease['pid']==1498278 and lease['start_ticks']==977758783 and lease['controller_sha256']==plan['parent_controller_sha256']==sha(plan['parent_controller_path'])and plan['request']not in lease['additional_requests']
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
 for handle in handles:
  assert not handle.closed and'FLOCK'in(P('/proc/self/fdinfo')/str(handle.fileno())).read_text();KEEP.append(handle)
 e=load('stage2_main_engine',R/'tools/stage2_native.py');reg,epoch=e.authority();oldq=reg['registered_future_requests']['DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'];assert oldq['remaining']==0 and len(oldq['consumed'])==oldq['budget']==360
 for c,row in oldq['consumed'].items():
  proof=OLD/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
  if proof.exists():
   p=rd(proof);proc=P('/proc')/str(p['pid'])
   if proc.exists():assert int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])!=p['start_ticks']or(proc/'stat').read_text().rsplit(')',1)[1].split()[0]in['Z','X'],'OLD_STAGEI_MODEL_STILL_LIVE'
 prior16=reg['registered_future_requests']['DTC_STAGE_IIA_FIRST16_CH_MATCH_20261104_V1'];assert prior16['budget']==len(prior16['consumed'])==16 and prior16['remaining']==0
 priorroot=P('/root/data/dtc_stage_iia_first16_20261104_v1')
 for oldco,oldrow in prior16['consumed'].items():
  rr=rd(priorroot/'analysis'/(oldco+'.RESULT.json'));assert rr['state']=='PASS_STAGEII_CH_STRICT_ARCHIVE_NATIVE_RESTORE'and rr['uuid']==oldrow['uuid']
  pp=rd(priorroot/'DTC/run/results'/oldrow['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json');proc=P('/proc',str(pp['pid']),'stat')
  if proc.exists():
   st=proc.read_text().rsplit(')',1)[1].split();assert int(st[19])!=pp['start_ticks']or st[0]in['Z','X'],'FIRST16_MODEL_STILL_LIVE'
 assert plan['request']not in reg['registered_future_requests'];state=dict(phase='PREFLIGHT',same_OS_owner=True,old_controller_source_unchanged=True,old_source_frame=frame,old_keepers=KEEP);setattr(main,MARKER,state)
 try:
  D=R/'control/actual_owner_attach_v2';D.mkdir(exist_ok=True);put(D/'LEASE_BEFORE.json',lease);put(D/'OLD_REQUEST_IDENTITIES_BEFORE.json',{k:dict(budget=v.get('budget'),remaining=v.get('remaining'),consumed=v.get('consumed'))for k,v in reg['registered_future_requests'].items()})
  entry=N/'bin/native';before=entry.read_bytes();block=(R/'control/NATIVE_ROUTE_BLOCK.sh').read_bytes();anchor=b'#!/bin/sh\nset -eu\n';assert before.startswith(anchor)and block not in before and b'E2-DTC2A48-'not in before;after=anchor+block+before[len(anchor):];assert after.replace(block,b'',1)==before;put(D/'NATIVE_ENTRY_BEFORE.sh',before)
  def register(current):
   assert e.REQ not in current['registered_future_requests'];current['registered_future_requests'][e.REQ]=copy.deepcopy(candidate)
  e.update_authority(register);state['phase']='REGISTERED_EXACT48'
  assert entry.read_bytes()==before,'NATIVE_ROUTE_CONCURRENT_CHANGE_PRESERVE';tmp=entry.with_name('.native.STAGEII48writing');tmp.write_bytes(after);tmp.chmod(entry.stat().st_mode&0o777);os.replace(tmp,entry);put(D/'NATIVE_ROUTE_TRANSITION.json',dict(prior_sha256=hashlib.sha256(before).hexdigest(),new_sha256=sha(entry),exact_block_sha256=sha(R/'control/NATIVE_ROUTE_BLOCK.sh'),all_prior_bytes_preserved=True));state['phase']='EXACT_ROUTE_INSTALLED'
  new=copy.deepcopy(lease);new['additional_requests'].append(e.REQ);assert rd(leasepath)==lease;atomic(leasepath,new);state['phase']='OWNER_BOUND_EXISTING_LOCKS_RETAINED';e.assert_parent_lease();e.registered()
  ops=load('stage2_owner_finite16_ops',R/'tools/stage2_ops.py')
  def target():
   try:ops.run_scheduler()
   except BaseException as error:put(R/'analysis/OWNER_THREAD_ERROR.json',dict(error=repr(error),no_model_retry=True,registered_scope_preserved=True))
  worker=threading.Thread(target=target,name='DTC_STAGEII_REMAINING48_ONLY',daemon=False);state['thread']=worker
  ack=dict(schema='DTC_STAGEII_REMAINING48_OWNER_ACK_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='REGISTERED_EXACT48_SAME_OWNER_READY_TO_DISPATCH',owner_pid=os.getpid(),owner_start_ticks=977758783,old_primary_lease_request_unchanged=True,old_request_budgets_and_UUIDs_preserved=True,controller_sha256=lease['controller_sha256'],plan_sha256=sha(R/'control/EXECUTION_PLAN.json'),new_request=e.REQ,new_exact_credits=48,CPU_qualification_sha256=sha(R/'control/CPU_QUALIFICATION.json'),all_other_new_grants=0,old_models_signaled=0,original_lock_handles_retained=True,addon_sha256=sha(__file__),native_route_exact48=True)
  put(R/'control/PARENT_ADDON_ACK.json',ack);state.update(phase='ACKED',ACK=ack);worker.start();return ack
 except BaseException as error:
  state.update(phase='HOLD_FORWARD_RECONCILIATION',error=repr(error));put(R/'analysis/ADDON_ERROR_PRESERVE.json',dict(phase=state['phase'],error=repr(error),automatic_requeue=False,no_model_retries=True));raise
