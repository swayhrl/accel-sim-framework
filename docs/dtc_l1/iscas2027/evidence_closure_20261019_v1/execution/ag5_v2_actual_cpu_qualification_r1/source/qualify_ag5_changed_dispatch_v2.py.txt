"""Full guard entry with real CPU children and explicitly synthetic reuse input.

Linux PID reuse is NOT forced. A wait adapter delivers one declared synthetic
SIGSTOP after a real helper's exit has been consumed. Only that retired PID's
/proc identity is substituted. Real ptrace operations targeting the synthetic
instance are intercepted before the syscall. This tests production dispatch,
not just Ownership.classify. Independent real-kernel cases qualify cleanup.
"""
import ctypes, fcntl, hashlib, json, os, signal, sys, time
from pathlib import Path
from unittest.mock import patch
HERE = Path(__file__).resolve().parent
RAW = Path('/workspace/dtc-evidence-closure-20261019-v1/coordinator')
sys.path.insert(0, str(HERE / 'vendor'))
sys.path.insert(0, str(HERE))
from common import write, now
from mapping_roles import Reject, require
import guarded_process as fixed
import ownership as ownmod
from legacy_authority_runtime import bind_frozen_procedures
from shared_authority import bind_current_review
proc, snapshot, _ = bind_frozen_procedures()
REGISTRATION = HERE.parent / 'CPU_AG5_CHANGED_DISPATCH_REGISTRATION_V2.json'
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def review(s, controller, ownership):
    # Uses actual current snapshot inside the same source-bound callback, never
    # an old child-pid fallback. This wrapper serves the generation injection.
    callback = bind_current_review(ownership, ownmod.identity, lambda: [],
         project_CPU_tracees=True, exact_controller_roles_provider=lambda:[REG['self_role']])
    return callback(controller)[1]
REG = None

def main():
 global REG
 REG=json.loads(REGISTRATION.read_text())
 require(REG['status']=='REGISTERED_CHANGED_DISPATCH_CPU_ONLY','EXACT_CHANGED_CPU_RELEASE_REQUIRED')
 for rel,digest in REG['prepared_source_sha256'].items():
  require(sha(HERE/rel)==digest,'QUALIFIER_SOURCE_CHANGED:'+rel)
 from cpu_admission_v2 import CPUAdmission, execution_binding
 if not CPUAdmission(REG,[REG['self_role']]).admit(Path(REG['admission_output'])):
  print('WAIT_RESOURCE_OR_AUTHORITY_NO_CPU_FIXTURE_STARTED',flush=True);return 3
 dest=Path(REG['output']);dest.mkdir(parents=True,exist_ok=False)
 manifest_path=Path(REG['manifests_path'])
 require(sha(manifest_path)==REG['manifests_sha256'],'MAPPING_MANIFEST_CHANGED')
 manifests=json.loads(manifest_path.read_text())
 target=RAW/'build/closure-cpu-ag5-v2'
 env=dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',CUDA_VISIBLE_DEVICES='')
 write(dest/'START.json',dict(utc=now(),**execution_binding(REGISTRATION,REG),purpose='TARGETED_CHANGED_AG5_BA_CPU_INTERFACES',kernel_PID_reuse_forced=False,simulator_starts=0),exclusive=True)
 rows=[]
 for label,engine,kind in [('fixed_retired_helper',fixed,'retired'),('fixed_retired_thread',fixed,'thread_retired'),('fixed_retired_root',fixed,'root_retired'),('fixed_current_instance_changed',fixed,'current_changed'),('fixed_stale_image_generation',fixed,'stale_image')]:
  original_wait=os.waitpid;original_identity=ownmod.identity;original_cdll=ctypes.CDLL;original_kill=os.kill
  token={};records=[];injected=[False];queue=[];rejected=[False]
  def frame_guard():
   f=__import__('sys')._getframe(1)
   while f and f.f_code.co_name!='run_guarded':f=f.f_back
   require(f is not None,'CPU_ADAPTER_NOT_IN_GUARD');return f
  def identify(p):
   if token and p==token['pid']:return token['new']
   return original_identity(p)
  class Ptrace:
   def __init__(self,fn):self.fn=fn
   def __call__(self,*a):
    if token and int(a[1])==token['pid']:
     records.append(dict(operation='ptrace',request=int(a[0]),pid=int(a[1]),blocked_before_kernel=True))
     raise Reject('CPU_UNPROVEN_PTRACE_OPERATION')
    return self.fn(*a)
  class Lib:
   def __init__(self,*a,**kw):
    self.lib=original_cdll(*a,**kw);self.ptrace=Ptrace(self.lib.ptrace)
    self.lib.ptrace.restype=ctypes.c_long
   def __getattr__(self,n):return getattr(self.lib,n)
  def kill(p,s):
   if token and p==token['pid']:
    records.append(dict(operation='signal',pid=p,blocked_before_kernel=True))
    raise Reject('CPU_UNPROVEN_SIGNAL_OPERATION')
   return original_kill(p,s)
  def wait(p,flags):
   if queue:return queue.pop(0)
   child,status=original_wait(p,flags)
   if child and not injected[0]:
    f=frame_guard();o=f.f_locals.get('ownership');root=f.f_locals.get('pid')
    terminal=os.WIFEXITED(status) or os.WIFSIGNALED(status)
    chosen=(kind=='root_retired' and child==root and terminal) or (kind in ('retired','thread_retired') and child!=root and terminal and os.waitstatus_to_exitcode(status)==0 and ((o.confirmed[child]['tgid']==child) if kind=='retired' else (o.confirmed[child]['tgid']!=child)))
    if o and chosen:
     prior=dict(o.confirmed[child]);token.update(pid=child,old=prior,new=dict(prior,start_ticks=prior['start_ticks']+1000000,state='t'))
     queue.append((child,(signal.SIGSTOP<<8)|0x7f));injected[0]=True
     # Root would otherwise end the loop; leave a real descendant alive in the
     # dedicated root fixture, so this status reaches the normal wait entry.
    elif o and kind in ('current_changed','stale_image') and child!=root and os.WIFSTOPPED(status) and child in f.f_locals.get('states',{}):
     if kind=='current_changed':
      prior=dict(o.confirmed[child]);token.update(pid=child,old=prior,new=dict(prior,start_ticks=prior['start_ticks']+1000000,state='t'))
     else:f.f_locals['states'][child]['start_ticks']-=1
     injected[0]=True
   return child,status
  def observe(pid,full,o):
   if kind in ('retired','thread_retired','root_retired') and token and token['pid'] in o.pending:
    f=frame_guard();assert token['pid'] not in o.confirmed and token['pid'] not in f.f_locals['states']
    a=review(snapshot(),proc(os.getpid()),o)
    assert a['status']=='PENDING_QUARANTINED_NO_AUTHORITY_PASS',a
    records.append(dict(operation='observer',authority=a['status'],retired_state_absent=True))
    rejected[0]=True
    return 'CPU_EXPECTED_RETIRED_PID_QUARANTINE'
   return None
  # After rejection the changed identity is only an input substitution, not a
  # real reused kernel PID: withdraw it for cleanup of the actual live fixture.
  old_same=ownmod.Ownership.same
  def same(o,p):
   try:return old_same(o,p)
   except Reject as e:
    if kind=='current_changed' and token and p==token['pid']:
     records.append(dict(operation='current_identity_reject',reason=str(e)))
     token.clear()
    raise
  with (RAW/'AG_execution.lock').open('a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   with patch.object(engine.os,'waitpid',wait),patch.object(ownmod,'identity',identify),patch.object(engine.ctypes,'CDLL',Lib),patch.object(engine.os,'kill',kill),patch.object(ownmod.Ownership,'same',same):
    r=engine.run_guarded([str(target),'root_exit_child' if kind=='root_retired' else 'normal'],env,manifests,dest/label,'CPU_FIXTURE',20,observer=observe)
  bad=[x for x in records if x['operation'] in ('ptrace','signal')]
  if kind in ('retired','thread_retired','root_retired'):
   ok=injected[0] and rejected[0] and not bad and 'CPU_EXPECTED_RETIRED_PID_QUARANTINE' in str(r['forced_reason'])
  else:
   needle='OWN_PID_REUSED' if kind=='current_changed' else 'STALE_IMAGE_GENERATION'
   ok=injected[0] and not bad and needle in str(r['forced_reason'])
  ok=ok and r['owned_children_live']==0 and r['status']=='STOP_GUARDED_PROCESS'
  row=dict(case=label,status='PASS_EXPECTED_RESULT' if ok else 'FAIL',records=records,terminal=r,synthetic_identity=token,kernel_PID_reuse_forced=False,synthetic_pending_is_not_a_real_live_process=kind in ('retired','thread_retired','root_retired'),simulator_starts=0)
  rows.append(row);write(dest/'RESULTS_IN_PROGRESS.json',rows)
  assert ok,row
 write(dest/'PRODUCTION_DISPATCH_GENERATION_TESTS.json',dict(status='PASS_BOUNDED_FULL_GUARD_DISPATCH',**execution_binding(REGISTRATION,REG),raw=str(dest),cases=rows,coverage='Actual run_guarded entry, real CPU loader/fork/exec/exit plus declared synthetic generation inputs; no forced kernel PID reuse; fixed integrated guard only; old AG5 counterexample receipt preserved without rerun',simulator_starts=0))
 run_real_changed_interfaces(dest, manifests, env)
 print('PASS_CHANGED_DISPATCH_AND_REAL_INTERFACES',len(rows),flush=True)

def run_real_changed_interfaces(dest, manifests, env):
 target=RAW/'build/closure-cpu-ag5-v2'
 controller=proc(os.getpid());rows=[]
 def observe(pid,full,ownership):
  if not full:return None
  verdict=review(None,controller,ownership)
  with (dest/'ACTUAL_AUTHORITY.jsonl').open('a') as stream:stream.write(json.dumps(verdict)+'\n')
  return 'ACTUAL_CHANGED_INTERFACE_AUTHORITY_STOP' if verdict['status']=='STOP_AUTHORITY_NOT_CLOSED' else None
 def run(label,mode='normal',expected=True,timeout=20,observer=observe,needle=None):
  with (RAW/'AG_execution.lock').open('a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   r=fixed.run_guarded([str(target),mode],env,manifests,dest/label,'CPU_FIXTURE',timeout,observer=observer)
  good=((r['status']=='PASS_GUARDED_NATURAL_EXIT0')==expected and
        r['owned_children_live']==0 and not r.get('unconfirmed_wait_pids') and
        not r.get('ownership',{}).get('pending') and r['simulator_starts']==0)
  if needle:good=good and needle in str(r.get('forced_reason'))
  rows.append(dict(case=label,passed=good,terminal=r));write(dest/'REAL_CHANGED_RESULTS_IN_PROGRESS.json',rows)
  require(good,'REAL_CHANGED_CASE_FAILED:'+label)
 # Actual terminal-root inheritance, with original real kernel statuses held.
 original=os.waitpid;held=[];root_reaped=[False];did_hold=[False]
 def parent_first_wait(pid,flags):
  if held and root_reaped[0]:return held.pop(0)
  child,status=original(pid,flags)
  if child:
   f=sys._getframe(1)
   while f and f.f_code.co_name!='run_guarded':f=f.f_back
   if f:
    if child!=f.f_locals['pid'] and os.WIFSTOPPED(status) and not did_hold[0]:
     did_hold[0]=True;held.append((child,status));return (0,0)
    if child==f.f_locals['pid'] and (os.WIFEXITED(status) or os.WIFSIGNALED(status)):root_reaped[0]=True
  return child,status
 with patch.object(fixed.os,'waitpid',parent_first_wait):run('real_child_first_stop_after_parent_reaped','root_exit_child')
 require(did_hold[0] and root_reaped[0] and not held,'REAL_PARENT_REAP_ORDER_NOT_OBSERVED')
 # Exact AG5 real event-reordering adapters for changed BA caller only.
 original_deadline=ownmod.Ownership.check_deadlines
 for label,missing,force in [('real_child_stop_before_parent_observer',False,False),('real_missing_event_finite_timeout',True,False),('real_stop_pending_event_cleanup',False,True)]:
  held=[];injected=[False];release=[False];seen=[]
  reorder_target=[None];reorder_deadline=[None]
  child_stop_delivered=[False];parent_event_delivered=[False]
  def deadline(o):
   try:return original_deadline(o)
   except Reject:release[0]=True;raise
  def reordered_wait(pid,flags):
   if held:
    if missing and not release[0]:return (0,0)
    if not missing and not force and not release[0] and not child_stop_delivered[0]:
     if time.monotonic()>=reorder_deadline[0]:
      release[0]=True
      raise Reject('CPU_REAL_CHILD_STOP_REORDER_BOUND_EXCEEDED')
     other=original(reorder_target[0],flags)
     if other[0]:
      try:require(other[0]==reorder_target[0] and os.WIFSTOPPED(other[1]),'ACTUAL_REORDER_CHILD_STOP_REQUIRED')
      except BaseException:release[0]=True;raise
      child_stop_delivered[0]=True
     return other
    parent_event_delivered[0]=True
    return held.pop(0)
   child,status=original(pid,flags)
   if child and status>>16 in (1,2,3) and not injected[0]:
    injected[0]=True;new=ctypes.c_ulonglong();lib=ctypes.CDLL(None,use_errno=True)
    require(lib.ptrace(0x4201,child,None,ctypes.byref(new))==0,'ACTUAL_GETEVENTMSG_FAILED')
    f=sys._getframe(1);o=f.f_locals['ownership']
    o.quarantine(int(new.value),'DECLARED_REAL_KERNEL_EVENT_REORDER')
    verdict=review(None,controller,o);seen.append(verdict);held.append((child,status))
    require(verdict['status']=='PENDING_QUARANTINED_NO_AUTHORITY_PASS','PENDING_GOT_AUTHORITY')
    if force:raise Reject('CPU_STOP_WITH_PENDING_EVENT')
    if missing:return (0,0)
    reorder_target[0]=int(new.value);reorder_deadline[0]=time.monotonic()+1.0
    return (0,0)
   return child,status
  with patch.object(fixed.os,'waitpid',reordered_wait),patch.object(ownmod.Ownership,'check_deadlines',deadline):
   run(label,expected=not(missing or force),needle='PARENT_EVENT_CONFIRMATION_TIMEOUT' if missing else ('CPU_STOP_WITH_PENDING_EVENT' if force else None))
  require(injected[0] and bool(seen),'ACTUAL_PENDING_ORDER_NOT_EXERCISED')
  if not missing and not force:
   require(child_stop_delivered[0] and parent_event_delivered[0] and not held,'ACTUAL_CHILD_STOP_BEFORE_PARENT_EVENT_NOT_DELIVERED')
  write(dest/(label+'_REORDER.json'),dict(real_parent_event_held=True,synthetic_ptrace_proof=False,observations=seen,actual_child_stop_delivered_before_parent_event=child_stop_delivered[0],actual_parent_event_delivered=parent_event_delivered[0],normal_reorder_wait_bound_seconds=1.0))
 run('real_observer_exception',expected=False,observer=lambda *a:(_ for _ in ()).throw(OSError('CPU_OBSERVER_EXCEPTION')),needle='CPU_OBSERVER_EXCEPTION')
 run('real_owned_timeout_cleanup','hang',expected=False,timeout=.8,needle='TIMEOUT_')
 # AG5 same() tracer/Tgid rejection is exercised on the actual imported owner.
 identity=ownmod.identity(os.getpid());o=ownmod.Ownership(os.getpid())
 for label,delta,needle in [('tracer',{'tracer_pid':-1},'OWN_TRACER_CHANGED'),('tgid',{'tracer_pid':o.tracer,'tgid':-1},'OWN_THREAD_GROUP_CHANGED')]:
  with patch.object(ownmod,'identity',return_value=dict(identity,**delta)):
   try:o.same(os.getpid())
   except Reject as exc:require(needle in str(exc),'WRONG_INSTANCE_REJECTION')
   else:raise Reject('INSTANCE_NEGATIVE_ACCEPTED:'+label)
 write(dest/'REAL_CHANGED_RESULTS.json',dict(status='PASS_TARGETED_CHANGED_REAL_CPU_INTERFACES',**__import__('cpu_admission_v2').execution_binding(REGISTRATION,REG),generation_receipt_sha256=sha(dest/'PRODUCTION_DISPATCH_GENERATION_TESTS.json'),cases=rows,declared_wait_order_adapters=True,kernel_PID_reuse_forced=False,simulator_starts=0,performance_qualification=False))

if __name__=='__main__':sys.exit(main() or 0)
