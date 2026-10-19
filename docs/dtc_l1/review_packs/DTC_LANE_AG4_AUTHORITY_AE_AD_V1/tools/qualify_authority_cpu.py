from common import *
from freeze_static import freeze_executable
import guarded_process as guard
import ownership as ownmod
from ownership import identity,Ownership
from review_authority import review
from audit_site import snapshot,proc
from mapping_roles import Reject,require
from unittest.mock import patch
import time,ctypes,fcntl,copy,importlib.util

def main():
 dest=RAW/'cpu-qualification'/('authority-'+str(time.time_ns()));dest.mkdir(parents=True)
 target=BUILD/'ag4-cpu-authority';manifests={}
 for exe in [target,Path('/usr/bin/dash'),Path('/usr/bin/cat')]:
  m,_=freeze_executable(exe,BUILD);manifests[m['target']]=m
 env=dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',CUDA_VISIBLE_DEVICES='')
 write(dest/'PREREGISTRATION.json',dict(manifests=manifests,guard_sha256=sha(PACK/'tools/guarded_process.py'),authority_sha256=sha(PACK/'tools/review_authority.py'),ownership_sha256=sha(PACK/'tools/ownership.py'),confirmation_seconds=2.,simulator_starts=0,real_simulation_UUIDs=0))
 results=[];samples=[];current={'case':''};controller=proc(os.getpid())
 def observe(pid,full,ownership):
  if not full:return None
  s=snapshot()
  # CPU executable is deliberately projected as a simulator candidate to exercise
  # the unchanged production candidate branch; all PID/maps/events are real.
  candidates=set(ownership.confirmed)|set(ownership.pending)
  for p in s['processes']:
   if p['pid'] in candidates:p['is_simulator']=True
  auth=review(s,controller,ownership)
  row=dict(case=current['case'],utc=now(),full=full,authority=auth,ownership=ownership.snapshot())
  samples.append(row)
  with (dest/'OBSERVER.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
  if auth['status']=='STOP_AUTHORITY_NOT_CLOSED':return 'CPU_REAL_PERIODIC_AUTHORITY_REJECT'
  return None
 def run(label,mode='normal',expected=True,timeout=60,observer=observe,needle=None):
  current['case']=label
  with (RAW/'AG_execution.lock').open('a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   r=guard.run_guarded([str(target),mode],env,manifests,dest/label,'CPU_FIXTURE',timeout,observer=observer)
  with (RAW/'AG_execution.lock').open('a') as check:fcntl.flock(check,fcntl.LOCK_EX|fcntl.LOCK_NB)
  good=(r['status']=='PASS_GUARDED_NATURAL_EXIT0')==expected and r['owned_children_live']==0 and not r.get('unconfirmed_wait_pids') and not r.get('ownership',{}).get('pending')
  if needle:good=good and needle in str(r.get('forced_reason'))
  row=dict(case=label,expected_success=expected,expected_reason=needle,passed=good,result=r,own_FLOCK_released=True)
  results.append(row);write(dest/'RESULTS_IN_PROGRESS.json',results)
  assert good,(label,r)
  return r
 run('normal_fork_exec_exit')
 run('long_periodic_repeated_readers','long')
 assert len([s for s in samples if s['case']=='long_periodic_repeated_readers'])>=3
 for label,mode,reason in [('unknown_exec','unknownexec','UNKNOWN_EXEC_IMAGE'),('unknown_actual_mapping','unknownmap','UNREGISTERED_FILE_MAPPING'),('writable_cache','writablecache','DATA_MAPPING_NOT_READ_ONLY'),('nonzero_exit','nonzero','NONZERO_OWNED_PROCESS_EXIT')]:run(label,mode,False,needle=reason)
 run('timeout','hang',False,timeout=.8,needle='TIMEOUT_')
 run('observer_exception',expected=False,observer=lambda *a:(_ for _ in ()).throw(OSError('CPU_OBSERVER_EXCEPTION')),needle='CPU_OBSERVER_EXCEPTION')
 run('forced_stop',expected=False,observer=lambda *a:'CPU_FORCED_STOP',needle='CPU_FORCED_STOP')
 # Real parent wait event held by this declared wait-order adapter. No synthetic
 # ptrace proof is created: confirmation consumes original kernel event+GETEVENTMSG.
 original_wait=os.waitpid;original_deadline=Ownership.check_deadlines
 for label,missing,force in [('child_stop_before_parent_observer',False,False),('missing_event_finite_timeout',True,False),('stop_pending_event_cleanup',False,True)]:
  held=[];injected=[False];release=[False];seen=[]
  def deadline(self):
   try:return original_deadline(self)
   except Reject:release[0]=True;raise
  def reordered_wait(pid,flags):
   if held:
    if missing and not release[0]:return (0,0)
    return held.pop(0)
   child,status=original_wait(pid,flags)
   if child and status>>16 in (1,2,3) and not injected[0]:
    injected[0]=True;new=ctypes.c_ulonglong();lib=ctypes.CDLL(None,use_errno=True)
    assert lib.ptrace(0x4201,child,None,ctypes.byref(new))==0
    # The proof stays held; observer sees trace-stop before guard confirms it.
    frame=__import__('sys')._getframe(1);ownership=frame.f_locals['ownership']
    ownership.quarantine(int(new.value),'DECLARED_REAL_KERNEL_EVENT_REORDER')
    s=snapshot()
    for p in s['processes']:
     if p['pid'] in set(ownership.confirmed)|set(ownership.pending):p['is_simulator']=True
    auth=review(s,controller,ownership);seen.append(auth)
    held.append((child,status))
    assert auth['status']=='PENDING_QUARANTINED_NO_AUTHORITY_PASS',auth
    if force:raise Reject('CPU_STOP_WITH_PENDING_EVENT')
    if missing:return (0,0)
    # Deliver the actual child stop first, when available; otherwise observer-first
    # ordering above still genuinely covers the pre-parent-event state.
    other=original_wait(int(new.value),flags)
    if other[0]:return other
    return (0,0)
   return child,status
  with patch.object(guard.os,'waitpid',reordered_wait),patch.object(Ownership,'check_deadlines',deadline):
   run(label,expected=not(missing or force),needle='PARENT_EVENT_CONFIRMATION_TIMEOUT' if missing else ('CPU_STOP_WITH_PENDING_EVENT' if force else None))
  assert injected[0] and seen
  write(dest/(label+'_REORDER.json'),dict(real_parent_event_held=True,synthetic_ptrace_proof=False,observer_before_parent_consumption=seen))
 # Pure negative controls call the same production Ownership and review entry.
 negatives=[]
 root=os.getpid();o=Ownership(root);r=identity(root)
 def reject(label,fn,needle):
  try:fn()
  except (Reject,AssertionError) as e:
   assert needle in str(e),(label,e);negatives.append(dict(case=label,status='EXPECTED_REJECT',reason=str(e)));return
  raise AssertionError('NEGATIVE_ACCEPTED:'+label)
 fake=dict(proc(root),is_simulator=True,start_ticks=r['start_ticks']+1)
 reject('PID_reuse',lambda:o.classify(fake),'AUTHORITY_OWN_PID_REUSED')
 reject('wrong_parent',lambda:o.confirm(99999999,root,1),'WRONG_UNCONFIRMED_PARENT')
 wrong=Ownership(root)
 with patch.object(ownmod,'identity',side_effect=lambda p:r if p==root else dict(r,pid=p,ppid=999999,tgid=root+1,tracer_pid=root)):
  reject('parent_identity_changed',lambda:wrong.confirm(root,root+1,1),'PARENT_EVENT_ANCESTRY_CONTRADICTION')
 s=snapshot();s['processes'].append(dict(proc(root),pid=99999998,start_ticks=1,is_simulator=True,exe='/unregistered/accel-sim.out'))
 a=review(s,controller,o);assert a['status']=='STOP_AUTHORITY_NOT_CLOSED'
 negatives.append(dict(case='external_simulator_synthetic_snapshot_no_sim_start',status='EXPECTED_REJECT',reason=a['unknown_controls']))
 old=PACK.parent/'DTC_LANE_AG3_AE_AD_SCREEN_V1'
 spec=importlib.util.spec_from_file_location('ag3_old_review',old/'tools/review_authority.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 stopped=json.loads((old/'STOP_EVIDENCE.json').read_text());s=snapshot();s['processes']+=stopped['observed_processes']
 oldrepro=mod.review(s,dict(child_pid=4035496,child_start_ticks=907068035))
 assert any(x['pid']==4042390 for x in oldrepro['unknown_controls'])
 write(dest/'OLD_FAILURE_REPRODUCTION.json',dict(status='REPRODUCED_FROZEN_OLD_CLASSIFIER',historical_candidate_exec='UNAVAILABLE',parent_event='UNAVAILABLE_HISTORICALLY',result=oldrepro,old_source_sha256=sha(old/'tools/review_authority.py')))
 # Each positive naturally observed cache -> unmap; every exec uses original parser.
 for row in results:
  if row['expected_success']:
   events=[json.loads(l) for l in (dest/row['case']/'MAP_EVENTS.jsonl').read_text().splitlines()]
   assert any(e.get('cache_present') for e in events)
   assert any('/etc/ld.so.cache' in e.get('removed_files',[]) for e in events)
 write(PACK/'CPU_AUTHORITY_QUALIFICATION.json',dict(status='PASS_CPU_AUTHORITY_RACE_REPAIR',raw=str(dest),cases=results,negative_controls=negatives,full_periodic_samples=len(samples),long_fixture_full_samples=len([s for s in samples if s['case']=='long_periodic_repeated_readers']),old_failure_reproduced=True,simulator_starts=0,real_simulation_UUIDs=0,scope='Real CPU processes, kernel ptrace ancestry, loader and production observer; declared event-order adapters, synthetic external/PID negatives; no performance/model qualification'))
 print(json.dumps(dict(status='PASS_CPU_AUTHORITY_RACE_REPAIR',cases=len(results),negatives=len(negatives),raw=str(dest))))
if __name__=='__main__':main()
