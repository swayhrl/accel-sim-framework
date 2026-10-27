"""Independent CPU-affinity/pool-capacity amendment. Importing performs no action.
Only the existing coordinating owner may call apply_in_owner(). No simulator,
controller, registry, lease, frozen file or running-model affinity is modified.
"""
import os,sys,pathlib,threading,ctypes,hashlib,math,time
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')

def _sha(path):return hashlib.sha256(P(path).read_bytes()).hexdigest()
def _ticks(pid):return int((P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19])
def parse_cpu_list(text):
 out=set()
 for item in text.strip().split(','):
  if not item:continue
  if '-'in item:
   lo,hi=map(int,item.split('-'));out.update(range(lo,hi+1))
  else:out.add(int(item))
 return sorted(out)

def find_scheduler_frame(thread,ops_path):
 assert thread.is_alive()and thread.ident is not None and thread.native_id is not None
 frame=sys._current_frames()[thread.ident];found=[]
 while frame is not None:
  if frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==P(ops_path):found.append(frame)
  frame=frame.f_back
 assert len(found)==1,'Must identify exactly one existing scheduler frame'
 return found[0]

def _set_fast_local(frame,key,value):
 # PyDLL keeps the GIL. No await, IO, lock acquire or GIL-releasing call occurs
 # between snapshotting f_locals and synchronizing the one changed fast local.
 loc=frame.f_locals;loc[key]=value
 fn=ctypes.pythonapi.PyFrame_LocalsToFast;fn.argtypes=[ctypes.py_object,ctypes.c_int];fn.restype=None;fn(frame,0)
 assert frame.f_locals[key]==value

def amend_thread_in_process(thread,ops_path,ops_sha,cpus,target_capacity):
 """Internal mechanism also exercised in an isolated CPU-only process."""
 assert _sha(ops_path)==ops_sha
 assert threading.current_thread()is threading.main_thread(),'Use existing main-thread GIL pending callback'
 assert thread is not threading.current_thread()and thread.native_id!=os.getpid()
 cpus=sorted(set(cpus));assert cpus and 1<=target_capacity<=len(cpus)
 frame=find_scheduler_frame(thread,ops_path);pool=frame.f_locals['pool']
 assert pool._thread_name_prefix=='L2MLP'and not pool._shutdown and not pool._broken
 # All submit mutations use this lock; never replace the executor or its queues.
 with pool._shutdown_lock:
  frame=find_scheduler_frame(thread,ops_path);old_capacity=frame.f_locals['max_workers'];assert old_capacity==pool._max_workers and target_capacity>=old_capacity
  workers=tuple(pool._threads);targets={thread.native_id}|{t.native_id for t in workers if t.is_alive()and t.native_id is not None};assert os.getpid()not in targets
  before={tid:sorted(os.sched_getaffinity(tid))for tid in targets};main_before=sorted(os.sched_getaffinity(0));objects={k:id(frame.f_locals[k])for k in ['claims','running']if k in frame.f_locals}
  try:
   for tid in targets:os.sched_setaffinity(tid,cpus)
   pool._max_workers=target_capacity;_set_fast_local(frame,'max_workers',target_capacity)
   assert all(sorted(os.sched_getaffinity(tid))==cpus for tid in targets)
   assert sorted(os.sched_getaffinity(0))==main_before
   assert all(id(frame.f_locals[k])==v for k,v in objects.items())
  except BaseException:
   pool._max_workers=old_capacity;_set_fast_local(frame,'max_workers',old_capacity)
   for tid,aff in before.items():
    try:os.sched_setaffinity(tid,aff)
    except ProcessLookupError:pass
   raise
 assert _sha(ops_path)==ops_sha
 return dict(status='AMENDED_EXISTING_OWNER_POOL_ONLY',owner_pid=os.getpid(),scheduler_ident=thread.ident,scheduler_native_id=thread.native_id,scheduler_source_path=str(ops_path),scheduler_source_sha256=ops_sha,prior_capacity=old_capacity,new_capacity=target_capacity,target_thread_native_ids=sorted(targets),prior_affinity_by_thread=before,new_allowed_cpus=cpus,main_thread_affinity_unchanged=main_before,executor_object_id=id(pool),claims_and_running_objects_unchanged=True,no_executor_replacement=True,no_registry_or_lease_or_frozen_file_write=True,no_running_model_or_old_thread_signalling=True)

def apply_in_owner():
 """Called ONLY by parent coordinator's existing GIL pending-call mechanism."""
 import json
 plan=json.loads((R/'control/EXECUTION_PLAN.json').read_bytes());assert os.getpid()==plan['parent_pid']==1498278 and _ticks(os.getpid())==plan['parent_start_ticks']
 ops=R/'tools/l2_ops.py';pin=next(x['sha256']for x in plan['source_pins']if P(x['path'])==ops);assert _sha(ops)==pin
 thread=getattr(sys.modules['__main__'],'DTC_L2_MLP_ADDON_THREAD');assert thread.name=='DTC_L2_MLP_ONE_OWNER'
 cpus=parse_cpu_list(P('/sys/fs/cgroup/cpuset.cpus.effective').read_text());quota=P('/sys/fs/cgroup/cpu.max').read_text().split();target=len(cpus)if quota[0]=='max'else min(len(cpus),max(1,int(int(quota[0])/int(quota[1]))))
 return amend_thread_in_process(thread,ops,pin,cpus,target)
