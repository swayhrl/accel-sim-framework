"""ROOT-REVIEW CANDIDATE: foreground engineering child on an existing E lease.
Never reserves a lease, appends an application, adopts authority or runs by import.
Root must review/copy/source-pin before actual use. No nohup or orphan controller.
"""
import argparse,fcntl,hashlib,json,os,signal,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
E=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
sys.path.insert(0,str(E/'util/ep_l2/mechanism_e'))
import coordinator as c
import durable_exit as durable
import r5_preparation as prep
GIB=2**30;LOG_CAP=32*2**20;ACTIVE={'RESERVED','RUNNING','START_INTENT_UNRECONCILED'}
def require(ok,message):
 if not ok:raise ValueError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def exact_live(identity):
 try:return durable.identity(identity['pid'])==identity
 except (OSError,ProcessLookupError):return False
def stop_owned(process):
 if exact_live(process.ready['native_process']):
  require(os.getpgid(process.pid)==process.pid,'native owned processgroup changed')
  os.killpg(process.pid,signal.SIGTERM);os.kill(process.pid,signal.SIGCONT)
  deadline=time.monotonic()+3
  while process.poll() is None and time.monotonic()<deadline:time.sleep(.05)
  if process.poll() is None and exact_live(process.ready['native_process']):os.killpg(process.pid,signal.SIGKILL)
 # Collection, not process disappearance, determines actual exit status.
 process.wait(timeout=15)
def read_lease(lease_id):
 raw=(c.SHARED/'RUN_REGISTRY.json').read_bytes();d=json.loads(raw);return d,d['resource_leases'][lease_id],hashlib.sha256(raw).hexdigest()
def run(request):
 c.tooling_binding();coord=c.Coordinator();mode=request['mode'];require(mode in ('build','native'),'only bounded engineering build/native')
 lease_id=request['lease_id'];logdir=Path(request['output_directory']).resolve();require(logdir.is_relative_to(c.OUTPUT.resolve()) and not logdir.exists(),'fresh original OUTPUT directory only')
 command=request['command'];require(type(command) is list and command and all(type(x) is str and x for x in command),'explicit exact argv required, no implicit shell')
 timeout=request['timeout_seconds'];require(timeout is None or (type(timeout) is int and timeout>0),'explicit engineering timeout int/null')
 env=os.environ.copy();env.update(request.get('environment',{}));env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
 cpus=sorted(os.sched_getaffinity(0))[:2];require(0<len(cpus)<=2,'real allowed CPU affinity required')
 # Native child and all compiler descendants inherit at most two allowed CPUs.
 command=['/usr/bin/taskset','--cpu-list',','.join(map(str,cpus)),*command]
 process=None;bound=False;released=False;result={'schema':'E2_R5_ENGINEERING_DURABLE_WORK_RECEIPT_V1','engineering_only':True,'scientific_acceptance':'NOT_EVALUATED','new_full_application_starts':0,'work_lease_id':lease_id,'mode':mode}
 lock=(c.HANDOFF/'CONTROLLER.lock').open('a+')
 with lock,durable.controller_signals():
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  item=coord.snapshot();require(item['controller']['state']=='STOPPED' and item['actual_starts']==55,'original controller must be STOPPED55')
  d,lease,before=read_lease(lease_id)
  require(lease.get('experiment_id')==c.CAMPAIGN and lease.get('owner')=='mechanism_E' and lease.get('role')==lease.get('executor_role')=='E' and lease.get('status') in ACTIVE,'existing exact E lease required')
  require(not any(r.get('experiment_id')==c.CAMPAIGN and r.get('status') in ACTIVE and (g=='runs' or ((r.get('role')=='E' or r.get('owner')=='mechanism_E') and k!=lease_id)) for g in ('runs','resource_leases') for k,r in d[g].items()),'no simultaneous own app/other E lease')
  require(lease['disk_floor_bytes']==5*GIB and lease['monitor_reserve_bytes']>=2*GIB,'original5+2 guard required')
  require(1<=lease['cpu_units']<=2 and lease['memory_bytes']==8*GIB,'bounded CPU2/RAM8GiB engineering lease')
  if mode=='build':
   authority=prep.authority();require(lease['kind']=='MECHANISM_BUILD' and lease['build_owner']=='E2_R5_FORMAL_PRODUCER' and lease['build_identity']==authority['build_identity'] and lease['output_directory']==prep.BUILD_PATH and lease['r5_preparation_authority_ref']==prep.PREP_AUTHORITY_REF,'source-bound E2 isolated build lease')
   require(0<lease['disk_growth_bytes']<=GIB and lease['result_growth_bytes']==0,'bounded build scratch1GiB')
   artifact=Path(prep.BUILD_PATH);base=c.retained_tree_bytes(artifact) if artifact.exists() else 0
   require(base==0,'first isolated formalbuild output must be fresh/empty; repair needs explicit reviewed baseline')
  else:
   require(lease['kind']=='MECHANISM_TEST' and Path(lease['output_directory']).resolve()==logdir and lease['result_growth_bytes']==lease['disk_growth_bytes'],'original E/test output-accounted lease')
   require(0<lease['disk_growth_bytes']<=LOG_CAP,'explicit bounded native log cap32MiB')
   artifact=None;base=0
  resources=c.local_resources();usage=c.output_usage()
  require(resources['disk_free_bytes']>=5*GIB+2*GIB+lease['disk_growth_bytes']+LOG_CAP,'explicit physical output headroom, separate from monitor')
  require(usage['new_bytes']+LOG_CAP<=10*GIB and usage['total_bytes']+LOG_CAP<=24*GIB,'build log new/total generation forecast, not a second lease')
  logdir.mkdir(parents=True,exist_ok=False)
  bounds={k:lease[k] for k in ('policy_id','disk_floor_bytes','monitor_reserve_bytes','monitor_interval_seconds','termination_grace_seconds')}
  bounds.update(maximum_result_bytes=LOG_CAP,memory_bytes=8*GIB,timeout_seconds=timeout,intake_deadline_unix=None,additional_results_max_bytes=10*GIB,old_plus_new_results_max_bytes=24*GIB)
  binding=dict(work_lease_id=lease_id,engineering_only=True,executor_role='E',build_owner=lease.get('build_owner'),kind=lease['kind'],build_identity=lease.get('build_identity'),r5_preparation_authority_ref=lease.get('r5_preparation_authority_ref'),source_publication_commit=json.loads((c.HANDOFF/'CLIENT_CONTRACT.json').read_bytes())['source_publication_commit'])
  durable.durable_json(logdir/'ENGINEERING_REQUEST.json',dict(request=request,actual_affinity_cpus=cpus,actual_command=command,bounds=bounds,binding=binding,artifact_baseline_allocated_bytes=base,registry_sha256_before=before))
  try:
   with (logdir/'raw.log').open('xb') as stdout:
    process=durable.NativeProcess(command,logdir,stdout,env,bounds,binding)
    identity=coord.bind_work_process(lease_id,'E',process.pid);bound=True
    require(identity==process.ready['native_process'],'lease bound exact stopped native PID/start_ticks/boot')
    # No app start is recorded; release means original work lease owns this child.
    process.release();released=True;reason=None
    while process.poll() is None:
     if durable.STOP.is_set():reason={'kind':'OWNER_INTERRUPTED','signal':durable.STOP_SIGNAL}
     if artifact is not None:
      size=c.retained_tree_bytes(artifact) if artifact.exists() else 0
      if size-base>=lease['disk_growth_bytes']:reason={'kind':'BUILD_SCRATCH_RESOURCE_LIMIT','actual_allocated_bytes':size,'baseline_allocated_bytes':base,'limit_growth_bytes':lease['disk_growth_bytes']}
     if reason is not None:stop_owned(process);break
     time.sleep(bounds['monitor_interval_seconds'])
    exitcode=process.wait(timeout=15);evidence=process.exit_evidence()
    require(not exact_live(process.ready['native_process']),'native remains live after wait receipt')
    require(evidence['released_to_native'] is True and evidence['command']==command and evidence['binding']==binding,'durable engineering command/lease differs')
    result.update(status='COMPLETE_ENGINEERING_EXIT0' if exitcode==0 and reason is None and evidence['stop_reason'] is None else 'FAILED_OR_RESOURCE_STOP',actual_exit_code=exitcode,native_exit_ref={'path':str(logdir/'NATIVE_EXIT.json'),'sha256':sha(logdir/'NATIVE_EXIT.json')},owner_stop_reason=reason,collector_stop_reason=evidence['stop_reason'],actual_peak_rss_kib=evidence['child_rusage']['maxrss_kib'],artifact_final_allocated_bytes=c.retained_tree_bytes(artifact) if artifact is not None and artifact.exists() else None)
   coord.release_work(lease_id,'E',detail='R5 engineering durable wait completed; receipt '+str(logdir/'ENGINEERING_RECEIPT.json'));result['work_lease_released']=True
  except BaseException as error:
   result.update(status='ENGINEERING_INCOMPLETE',error=type(error).__name__+': '+str(error),work_lease_released=False,native_release_written=released)
   if process is not None:
    try:
     stop_owned(process);evidence=process.exit_evidence();result['actual_exit_code']=evidence['exit_code'];result['native_exit_ref']={'path':str(logdir/'NATIVE_EXIT.json'),'sha256':sha(logdir/'NATIVE_EXIT.json')}
     if bound:coord.release_work(lease_id,'E',detail='R5 engineering failed; actual durable native exit preserved');result['work_lease_released']=True
    except BaseException as cleanup:result['cleanup_error']=type(cleanup).__name__+': '+str(cleanup)
   # Constructor/readiness failures may have forked a child. Keep lease active,
   # preserve evidence; never claim no_child_started or infer success.
  finally:
   result['actual_starts_after']=coord.snapshot()['actual_starts'];require(result['actual_starts_after']==55,'engineering must never change app count')
   durable.durable_json(logdir/'ENGINEERING_RECEIPT.json',result)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--request',required=True);args=p.parse_args();print(json.dumps(run(json.loads(Path(args.request).read_bytes())),indent=2))
