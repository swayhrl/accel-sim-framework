"""Full guard entry with real CPU children and explicitly synthetic reuse input.

Linux PID reuse is NOT forced. A wait adapter delivers one declared synthetic
SIGSTOP after a real helper's exit has been consumed. Only that retired PID's
/proc identity is substituted. Real ptrace operations targeting the synthetic
instance are intercepted before the syscall. This tests production dispatch,
not just Ownership.classify. Independent real-kernel cases qualify cleanup.
"""
from common import *
from mapping_roles import Reject,require
from freeze_static import freeze_executable
from audit_site import snapshot,proc
from review_authority import review
import guarded_process as fixed
import ownership as ownmod
import ctypes,signal,time,types,fcntl
from unittest.mock import patch


def main():
 dest=RAW/'dispatch-generation'/str(time.time_ns());dest.mkdir(parents=True)
 target=BUILD/'ag5-cpu-authority';manifests={}
 for exe in [target,Path('/usr/bin/dash'),Path('/usr/bin/cat')]:
  m,_=freeze_executable(exe,BUILD);manifests[m['target']]=m
 env=dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',CUDA_VISIBLE_DEVICES='')
 oldpath=PACK.parent/'DTC_LANE_AG4_AUTHORITY_AE_AD_V1/tools/guarded_process.py'
 # Only CPU target/root namespace changes. Dispatch logic stays frozen.
 oldtext=oldpath.read_text().replace('/workspace/dtc-lane-ag4-authority-aead-174-v1',str(RAW.parent)).replace('ag4-cpu-','ag5-cpu-')
 old=types.ModuleType('frozen_ag4_guard_cpu_namespace_only')
 exec(compile(oldtext,str(oldpath)+':CPU_NAMESPACE_ONLY','exec'),old.__dict__)
 write(dest/'PREREGISTRATION.json',dict(utc=now(),manifests=manifests,old_source_sha=sha(oldpath),fixed_source_sha=sha(PACK/'tools/guarded_process.py'),old_change_scope='CPU root and basename only; no dispatch changes',kernel_PID_reuse_forced=False,synthetic_wait_status=True,simulator_starts=0),exclusive=True)
 rows=[]
 for label,engine,kind in [('old_retired_helper',old,'retired'),('fixed_retired_helper',fixed,'retired'),('fixed_retired_thread',fixed,'thread_retired'),('fixed_retired_root',fixed,'root_retired'),('fixed_current_instance_changed',fixed,'current_changed'),('fixed_stale_image_generation',fixed,'stale_image')]:
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
  if engine is old:
   ok=injected[0] and bool(bad) and bad[0]['operation']=='ptrace' and bad[0]['request']==7
  elif kind in ('retired','thread_retired','root_retired'):
   ok=injected[0] and rejected[0] and not bad and 'CPU_EXPECTED_RETIRED_PID_QUARANTINE' in str(r['forced_reason'])
  else:
   needle='OWN_PID_REUSED' if kind=='current_changed' else 'STALE_IMAGE_GENERATION'
   ok=injected[0] and not bad and needle in str(r['forced_reason'])
  ok=ok and r['owned_children_live']==0 and r['status']=='STOP_GUARDED_PROCESS'
  row=dict(case=label,status='PASS_EXPECTED_RESULT' if ok else 'FAIL',records=records,terminal=r,synthetic_identity=token,kernel_PID_reuse_forced=False,synthetic_pending_is_not_a_real_live_process=kind in ('retired','thread_retired','root_retired'),simulator_starts=0)
  rows.append(row);write(dest/'RESULTS_IN_PROGRESS.json',rows)
  assert ok,row
 write(PACK/'PRODUCTION_DISPATCH_GENERATION_TESTS.json',dict(status='PASS_BOUNDED_FULL_GUARD_DISPATCH',raw=str(dest),cases=rows,coverage='Actual run_guarded entry, real CPU loader/fork/exec/exit plus declared synthetic generation inputs; no forced kernel PID reuse; old guard uses new Ownership but unchanged defective dispatch',simulator_starts=0))
 print('PASS_PRODUCTION_DISPATCH_GENERATION',len(rows))

if __name__=='__main__':main()
