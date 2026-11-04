"""Explicit same-owner zero-model engineering continuation. Import is inert.
Never register a request, alter a scientific budget/spec, signal a process, or
rewrite route/lease. Root invokes once after separate STOP_ONLY and CPU review.
"""
from pathlib import Path
import os,sys,json,hashlib,copy,threading,fcntl,types,datetime,uuid,stat
P=Path
R=P('/root/data/dtc_perf_first_v2_codesign16_20261105_v1')
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_execution_20261105_v1')
O=A/'engineering_incidents/pre_intent_registry_lock_v1/owner_continuation_v1'
N=P('/root/data/ep_l2_dtc_l1_native_v2');T=P('/root/data/dtc_main_v100_sweep_20261025_v1')
REQ='DTC_PERF_FIRST_V2_PHYSICAL_PIB16_20261105_V1'
ADDON='DTC_PERFV2_CODESIGN16_OWNER_ADDON_V1';STOP='DTC_PERFV2_CODESIGN16_CONTROLLED_STOP_ONLY_V1';MARKER='DTC_PERFV2_CODESIGN16_ZERO_MODEL_ENGINEERING_CONTINUATION_V1'
NEW_ENGINE_SHA='5ef37b56961101681c61d4e849381e1395d7e8017efba0e240367622e78e42db'
NEW_OPS_SHA='5ceb606b84c435457f3a6c8841525c8018d52d7e0ba8cc7e7962bb9a11dd0d86'

def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def qsha(v):return hashlib.sha256(js(v)).hexdigest()
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def rd(p):return json.loads(P(p).read_bytes())
def checked(ref):
 b=P(ref['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==ref['sha256'],'PIN_DRIFT '+ref['path'];return b

def put(p,value):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);b=value if isinstance(value,bytes)else js(value)
 with p.open('xb')as h:h.write(b);h.flush();os.fsync(h.fileno())

def atomic(p,b):
 p=P(p);mode=stat.S_IMODE(p.stat().st_mode)if p.exists()else 0o644;t=p.with_name('.'+p.name+'.ZERO_MODEL_CONTINUATION_V1writing')
 with t.open('xb')as h:h.write(b);h.flush();os.fsync(h.fileno())
 t.chmod(mode);os.replace(t,p);fd=os.open(p.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)

def project_request(old,contract,history,utc):
 assert old['request']==REQ and old['budget']==old['remaining']==len(old['admitted_specs'])==16 and old['consumed']=={}
 assert qsha(old)==contract['expected_old_request_sha256'],'REGISTERED_REQUEST_CAS_MISMATCH'
 for field,key in [('engine_sha256','expected_old_engine_sha256'),('controller_sha256','expected_old_controller_sha256'),('execution_plan_sha256','expected_old_plan_sha256')]:assert old[field]==contract[key]
 new=copy.deepcopy(old);new.update(engine_sha256=contract['new_native']['sha256'],controller_sha256=contract['new_ops']['sha256'],execution_plan_sha256=contract['new_plan']['sha256'])
 new.setdefault('engineering_source_history',[]).append(dict(operation='ZERO_MODEL_PRE_INTENT_REGISTRY_LOCK_FIX_SAME_REQUEST',UTC=utc,prior_request_sha256=qsha(old),prior_engine_sha256=old['engine_sha256'],new_engine_sha256=new['engine_sha256'],prior_controller_sha256=old['controller_sha256'],new_controller_sha256=new['controller_sha256'],prior_execution_plan_sha256=old['execution_plan_sha256'],new_execution_plan_sha256=new['execution_plan_sha256'],history=history,retired_pre_INTENT_UUIDs=contract['retired_pre_INTENT_UUIDs'],scientific_starts_before_continuation=0,budget_changed=False,request_reregistered=False,automatic_model_retry=False))
 changed={k for k in set(old)|set(new)if old.get(k)!=new.get(k)}
 assert changed<={'engine_sha256','controller_sha256','execution_plan_sha256','engineering_source_history'}
 assert new['budget']==new['remaining']==16 and new['consumed']==old['consumed']and new['admitted_specs']==old['admitted_specs']
 return new

def _owner_and_stopped():
 assert sys.dont_write_bytecode and threading.current_thread()is threading.main_thread()
 assert os.getpid()==1498278 and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 main=sys.modules['__main__'];assert not hasattr(main,MARKER),'CONTINUATION_ALREADY_ATTEMPTED_NO_BLIND_REAPPLY'
 state=getattr(main,ADDON);stop=getattr(main,STOP);worker=state['thread']
 assert stop['thread']is worker and not worker.is_alive(),'OLD_NEW16_THREAD_MUST_BE_DEAD'
 assert stop['source_sha256']=='af6ff22852e97baadfc254eecdd4795ba961ea4ca22c91d705e29b9fdb321ce0'
 for fd,target in [(3,T/'control/FINITE_CONTROLLER.lock'),(4,N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock')]:
  assert os.readlink('/proc/self/fd/'+str(fd))==str(target)and'FLOCK'in P('/proc/self/fdinfo',str(fd)).read_text(),'ORIGINAL_FD_KEEPER_MISSING'
 lease=rd(T/'control/BATCH_LEASE.json');assert lease['pid']==1498278 and lease['start_ticks']==977758783 and lease['additional_requests'].count(REQ)==1
 return main,state,worker,lease

def _zero_model_evidence(q,contract):
 assert q['request']==REQ and q['budget']==q['remaining']==len(q['admitted_specs'])==16 and q['consumed']=={}
 assert set(q['admitted_specs'])=={x['cohort']for x in rd(R/'control/MATRIX.fixed.json')['points']}
 configs=set()
 for c,digest in q['admitted_specs'].items():
  sp=R/'control/specs'/(c+'.json');assert sha(sp)==digest==sha(R/'control'/(c+'_SPEC.json')),'SCIENTIFIC_SPEC_CHANGED'
  spec=rd(sp);configs.update(x['path']for x in spec['configs'])
  assert spec['request']==REQ and spec['cohort']==c and spec['cell']=='DH'and spec['profile']in ['PHYS768_OOPIB192_TAG64x8','PHYS1024_OOPIB192_TAG64x8']
  for suffix in ['.INTENT.json','.DONE.json']:assert not(R/'control/qualification_ledger'/(c+suffix)).exists(),'SCIENTIFIC_IDENTITY_ALREADY_CONSUMED'
  assert not(R/'analysis'/(c+'.RESULT.json')).exists(),'SCIENTIFIC_RESULT_ALREADY_EXISTS'
 retired=[]
 for out in (R/'DTC/run/results').iterdir():
  assert out.is_dir()and not out.is_symlink(),'UNKNOWN_RESULT_ENTRY'
  uuid.UUID(out.name)
  assert not any((out/n).exists()for n in ['SIM_PID','SIM_PID.json','NATIVE_SIMULATOR_PID_AND_MAPS.json','NATIVE_LAUNCH.json']),'MODEL_OR_LAUNCH_EVIDENCE_EXISTS'
  retired.append(out.name)
 assert set(retired)==set(contract['retired_pre_INTENT_UUIDs'])and len(retired)==len(contract['retired_pre_INTENT_UUIDs'])and '2a6e4b2a-a060-4817-8c44-fa3577e5ef37'in retired,'PRE_INTENT_UUID_TOMBSTONE_SCOPE'
 live=[]
 for d in P('/proc').iterdir():
  if not d.name.isdigit()or int(d.name)==os.getpid():continue
  try:
   words=[x.decode(errors='replace')for x in(d/'cmdline').read_bytes().split(b'\0')if x]
   if not words:continue
   frontend=str(R/'tools/perf16_frontend.py')in words
   model=any('accel-sim.out'in x or P(x).name=='strace'for x in words)and any(x in configs or str(R)in x for x in words)
   if frontend or model:
    f=(d/'stat').read_text().rsplit(')',1)[1].split()
    if f[0]not in ['Z','X']:live.append(dict(pid=int(d.name),start_ticks=int(f[19]),argv=words))
  except(FileNotFoundError,ProcessLookupError):pass
 assert not live,'NEW_REQUEST_FRONTEND_OR_MODEL_STILL_LIVE '+repr(live)
 claims=rd(R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];assert set(claims)<=set(q['admitted_specs'])and all(v.get('observed_model')is False for v in claims.values()),'CLAIM_HAS_ACTUAL_MODEL'
 return dict(retired_UUIDs=sorted(retired),forecast_only_claims=claims,no_scientific_model=True,no_INTENT=True,all16_specs_unchanged=True)

def _check_plan(old,new,contract):
 assert new['request']==REQ and new['expected_new_starts']==new['initial_finite_budget']==16
 # Only source pin revisions and additive engineering narrative may differ.
 for k,v in old.items():
  if k!='source_pins':assert new[k]==v,'UNAPPROVED_PLAN_FIELD_CHANGE '+k
 oldpins={x['path']:x['sha256']for x in old['source_pins']};newpins={x['path']:x['sha256']for x in new['source_pins']}
 changes={str(R/'tools/perf16_native.py'):NEW_ENGINE_SHA,str(R/'tools/perf16_ops.py'):NEW_OPS_SHA}
 for path,digest in oldpins.items():assert newpins[path]==changes.get(path,digest),'UNAPPROVED_OLD_SOURCE_PIN_CHANGE '+path
 assert all(newpins[p]==v for p,v in changes.items())
 for pin in new['source_pins']:
  if pin['path']in changes:assert pin['sha256']==changes[pin['path']]
  else:assert sha(pin['path'])==pin['sha256'],'NEW_PLAN_SOURCE_DRIFT '+pin['path']


def resume(contract_path):
 main,addon,oldworker,lease=_owner_and_stopped();affinity=sorted(os.sched_getaffinity(0));lease_bytes=(T/'control/BATCH_LEASE.json').read_bytes();route_bytes=(N/'bin/native').read_bytes()
 cp=P(contract_path);contract=rd(cp);assert contract['schema']=='DTC_PERFV2_CODESIGN16_ZERO_MODEL_CONTINUATION_CONTRACT_V1'and contract['request']==REQ
 assert contract['new_native']['sha256']==NEW_ENGINE_SHA and contract['new_ops']['sha256']==NEW_OPS_SHA
 data={k:checked(contract[k])for k in ['new_native','new_ops','new_plan','CPU_qualification','independent_review']};newplan=json.loads(data['new_plan']);oldplan=rd(R/'control/EXECUTION_PLAN.json');assert sha(R/'control/EXECUTION_PLAN.json')==contract['expected_old_plan_sha256'];_check_plan(oldplan,newplan,contract)
 qual=json.loads(data['CPU_qualification']);assert qual['status']=='PASS'and qual['execution_plan_sha256']==contract['new_plan']['sha256']and qual['expected_old_request_sha256']==contract['expected_old_request_sha256']
 assert qual['native_sha256']==NEW_ENGINE_SHA and qual['ops_sha256']==NEW_OPS_SHA and qual['resume_source_sha256']==sha(__file__)and qual['barriers_to_retire']==contract['barriers_to_retire']
 expected_barriers={str(R/'control/ENGINEERING_PAUSE_NEW.json'),str(R/'control/ABORT')};actual_barriers={x for x in expected_barriers if P(x).exists()}
 assert str(R/'control/ENGINEERING_PAUSE_NEW.json')in actual_barriers and {x['path']for x in contract['barriers_to_retire']}==actual_barriers
 barrier_bytes={x['path']:checked(x)for x in contract['barriers_to_retire']}
 before_files={str(R/'tools/perf16_native.py'):contract['expected_old_engine_sha256'],str(R/'tools/perf16_ops.py'):contract['expected_old_controller_sha256'],str(R/'control/EXECUTION_PLAN.json'):contract['expected_old_plan_sha256']}
 for path,digest in before_files.items():assert not P(path).is_symlink()and sha(path)==digest,'OLD_INSTALLED_SOURCE_DRIFT'
 assert not(R/'control/DISPATCH_STARTED.CONTINUATION_V1.json').exists(),'CONTINUATION_START_ARTIFACT_EXISTS'
 record=O/'actual'/('continuation_'+sha(cp)[:16]);record.mkdir(parents=True,exist_ok=False);put(record/'CONTRACT.json',cp.read_bytes());put(record/'LEASE_BEFORE.json',lease_bytes);put(record/'NATIVE_ROUTE_BEFORE.sh',route_bytes)
 for path in before_files:put(record/('BEFORE_'+P(path).name),P(path).read_bytes())
 if (R/'control/CPU_QUALIFICATION.json').exists():put(record/'BEFORE_CPU_QUALIFICATION.json',(R/'control/CPU_QUALIFICATION.json').read_bytes())
 for path,b in barrier_bytes.items():put(record/('BEFORE_'+P(path).name),b)
 for name in ['POOL_DISPATCH_RESERVATIONS.json','DISPATCH_STARTED.json']:
  if(R/'control'/name).exists():put(record/('BEFORE_'+name),(R/'control'/name).read_bytes())
 state=dict(phase='ZERO_MODEL_PREFLIGHT',contract_sha256=sha(cp),record_directory=str(record),old_thread=oldworker,new_thread=None);setattr(main,MARKER,state)
 try:
  with(R/'control/DISPATCH_OWNER.lock').open('r+b')as dispatch:
   fcntl.flock(dispatch,fcntl.LOCK_EX|fcntl.LOCK_NB)
   with(N/'control/science_authority/REGISTRY_UPDATE.lock').open('r+b')as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    rp=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';ep=N/'control/CURRENT_SCIENCE_EPOCH.json';rb=rp.read_bytes();eb=ep.read_bytes();reg=json.loads(rb);epoch=json.loads(eb);assert epoch['native_registry_sha256']==hashlib.sha256(rb).hexdigest()
    old=copy.deepcopy(reg['registered_future_requests'][REQ]);assert qsha(old)==contract['expected_old_request_sha256'];zero=_zero_model_evidence(old,contract);put(record/'BEFORE_REGISTERED_REQUEST.json',old);put(record/'ZERO_MODEL_PREFLIGHT.json',zero)
    history=N/'control/science_authority/request_history'
    for path,b in [(rp,rb),(ep,eb)]:
     h=history/(path.stem+'.'+hashlib.sha256(b).hexdigest()+'.json')
     if not h.exists():put(h,b)
    revision=dict(directory=str(record),contract_sha256=sha(cp),CPU_qualification=contract['CPU_qualification'],independent_review=contract['independent_review'],native_registry_history_sha256=hashlib.sha256(rb).hexdigest(),old_epoch_history_sha256=hashlib.sha256(eb).hexdigest())
    newq=project_request(old,contract,revision,datetime.datetime.now(datetime.timezone.utc).isoformat());foreign={k:copy.deepcopy(v)for k,v in reg['registered_future_requests'].items()if k!=REQ};global_history=copy.deepcopy((reg['old_source_history'],reg['qualification_history']))
    # All installed destinations belong only to this new request; old V1 is untouched.
    atomic(R/'tools/perf16_native.py',data['new_native']);atomic(R/'tools/perf16_ops.py',data['new_ops']);atomic(R/'control/EXECUTION_PLAN.json',data['new_plan']);atomic(R/'control/CPU_QUALIFICATION.json',data['CPU_qualification']);state['phase']='NEW_PRIVATE_SOURCES_INSTALLED'
    reg['registered_future_requests'][REQ]=newq
    assert all(reg['registered_future_requests'][k]==v for k,v in foreign.items())and global_history==(reg['old_source_history'],reg['qualification_history'])
    atomic(rp,js(reg));epoch['native_registry_sha256']=sha(rp);epoch['request_revision']=dict(request_id=REQ,operation='ZERO_MODEL_PRE_INTENT_ENGINEERING_SOURCE_CONTINUATION',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_registry_sha256=hashlib.sha256(rb).hexdigest(),prior_current_epoch_sha256=hashlib.sha256(eb).hexdigest(),engineering_record_directory=str(record));atomic(ep,js(epoch));state['phase']='SAME_REQUEST_SOURCE_BINDING_CONTINUED'
   # EX registry lock released before true164 bulk history copies and new thread.
   put(record/'BEFORE_NATIVE_SCIENCE_REGISTRY.json',rb);put(record/'BEFORE_CURRENT_SCIENCE_EPOCH.json',eb)
   put(record/'RETIRED_PRE_INTENT_UUIDS.json',dict(UUIDs=zero['retired_UUIDs'],scientific_consumption=0,output_directories_preserved=True,reuse_forbidden=True,existing_out_mkdir_without_exist_ok_prevents_UUID_reuse=True))
   atomic(R/'control/POOL_DISPATCH_RESERVATIONS.json',js(dict(claims={})))
   for path,b in barrier_bytes.items():assert P(path).read_bytes()==b,'BARRIER_CHANGED_DURING_CONTINUATION';P(path).unlink()
   assert (T/'control/BATCH_LEASE.json').read_bytes()==lease_bytes and(N/'bin/native').read_bytes()==route_bytes and sorted(os.sched_getaffinity(0))==affinity
   for fd in [3,4]:assert'FLOCK'in P('/proc/self/fdinfo',str(fd)).read_text()
   newops=types.ModuleType('perf16_zero_model_continued_ops');newops.__file__=str(R/'tools/perf16_ops.py');exec(compile(data['new_ops'],newops.__file__,'exec'),newops.__dict__)
  # Old dispatch flock released first: the unique new scheduler takes it itself.
  def target():
   try:newops.run_scheduler()
   except BaseException as error:put(record/'OWNER_THREAD_CONTINUATION_ERROR.json',dict(error=repr(error),no_model_retry=True,same_request=True,healthy_models_not_signaled=True))
  worker=threading.Thread(target=target,name='DTC_PERFV2_CODESIGN16_CONTINUATION_V1',daemon=False);state['new_thread']=worker;addon.setdefault('engineering_previous_threads',[]).append(oldworker);addon['thread']=worker;addon['phase']='ENGINEERING_SOURCE_CONTINUED_SAME_REQUEST'
  ack=dict(schema='DTC_PERFV2_CODESIGN16_ZERO_MODEL_CONTINUATION_ACK_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner_pid=os.getpid(),owner_start_ticks=977758783,request=REQ,budget=16,consumed_before_continuation=0,remaining_before_continuation=16,new_engine_sha256=NEW_ENGINE_SHA,new_controller_sha256=NEW_OPS_SHA,new_plan_sha256=contract['new_plan']['sha256'],retired_pre_INTENT_UUIDs=zero['retired_UUIDs'],old_thread_verified_dead=True,original_DISPATCH_STARTED_preserved=True,original_keeper_FDs_retained=True,Main_affinity_unchanged=True,route_and_lease_unchanged=True,request_reregistered=False,budget_reset=False,direct_model_launcher_invocations=0,one_new_dispatch_thread=True,record_directory=str(record))
  put(record/'CONTINUATION_ACK.json',ack);state.update(phase='ACKED_NEW_SAME_OWNER_THREAD_READY',ACK=ack);worker.start();state['phase']='NEW_SAME_OWNER_THREAD_STARTED';return ack
 except BaseException as error:
  state.update(phase='HOLD_FORWARD_ENGINEERING_RECONCILIATION',error=repr(error));put(record/'CONTINUATION_HOLD_PRESERVE.json',dict(error=repr(error),phase=state['phase'],no_reregister=True,no_budget_refund=True,no_automatic_rollback_or_model_retry=True));raise
