"""CPU-only OFD handoff and scheduler-unwind fixtures; never actual owner."""
from pathlib import Path
import concurrent.futures as cf
import fcntl,hashlib,json,os,subprocess,sys,tempfile,threading,time,shutil
sys.dont_write_bytecode=True
A=Path(__file__).resolve().parent
assert os.getpid()!=1498278,'DO_NOT_RUN_CPU_FIXTURE_IN_ACTUAL_OWNER'
checks={};events=[]
def check(name,value):
 assert value,name
 checks[name]=True
def stamp(event,**fields):events.append(dict(monotonic=time.monotonic(),event=event,**fields))
def wait(predicate,seconds=3):
 deadline=time.monotonic()+seconds
 while time.monotonic()<deadline:
  if predicate():return True
  time.sleep(.005)
 return bool(predicate())
def can_lock(path):
 code="""from pathlib import Path
import fcntl,json,sys
p=Path(sys.argv[1]);assert str(p).startswith('/root/data/dtc_oracle_cpu_recovery_ofd_')
with p.open('a+b') as f:
 try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);print(json.dumps({'exclusive_acquired':True}))
 except BlockingIOError:print(json.dumps({'exclusive_acquired':False}))
"""
 result=subprocess.run([sys.executable,'-I','-B','-c',code,str(path)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=3)
 return json.loads(result.stdout)['exclusive_acquired']
class TypedHold(RuntimeError):pass
class StaleGeneration(RuntimeError):pass

tmp=Path(tempfile.mkdtemp(prefix='dtc_oracle_cpu_recovery_ofd_',dir='/root/data'))
assert tmp.stat().st_dev==2128
lock=tmp/'CPU_ONLY_DISPATCH.lock';release=threading.Event();started=threading.Event();old_finished=threading.Event();state={'generation':0,'started_once':True,'capture_done':False,'old_body_after_throw':False,'model_calls':0,'spawn_calls':[]};handoff_fd=None;handoff_fd2=None
def healthy_model():
 state['model_calls']+=1;started.set();stamp('CPU_HEALTHY_WORKER_STARTED')
 if not release.wait(8):raise AssertionError('CPU_WORKER_RELEASE_TIMEOUT')
 stamp('CPU_HEALTHY_WORKER_FINISHED');return {'CPU_ONLY_UUID':'CPU_ONLY_SPENT_UUID_A','CPU_ONLY_PID':12345}
def old_scheduler():
 try:
  with lock.open('a+b')as held:
   fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
   with cf.ThreadPoolExecutor(max_workers=2,thread_name_prefix='CPU_OLD_MODEL')as models,cf.ThreadPoolExecutor(max_workers=1,thread_name_prefix='CPU_OLD_ARCHIVE')as archives,cf.ThreadPoolExecutor(max_workers=1,thread_name_prefix='CPU_OLD_REVIEW')as reviews:
    state.update(held=held,models=models,archives=archives,reviews=reviews,thread_ident=threading.get_ident())
    future=models.submit(healthy_model);state['future']=future
    archives.submit(lambda:'CPU_ARCHIVE_DRAINED').result(timeout=2);reviews.submit(lambda:'CPU_REVIEW_DRAINED').result(timeout=2)
    assert started.wait(2);stamp('CPU_TYPED_HOLD_RAISED');raise TypedHold('RESOURCE_HOLD_CPU_ONLY')
    state['old_body_after_throw']=True
 except TypedHold:
  stamp('CPU_OLD_CONTEXTS_CLOSED')
 finally:old_finished.set()
def old_frame():
 fr=sys._current_frames().get(state.get('thread_ident'))
 while fr:
  if fr.f_code.co_name=='old_scheduler':return fr
  fr=fr.f_back
 return None
def old_awaiting_only_shutdown():
 if not started.is_set()or'state'not in globals()or'models'not in state:return False
 return (state['models']._shutdown and state['archives']._shutdown and state['reviews']._shutdown and not old_finished.is_set()and old_frame()is not None)
def capture_once():
 if state['capture_done']:raise RuntimeError('DUPLICATE_HANDOFF_FORBIDDEN')
 assert old_awaiting_only_shutdown();assert not state['future'].done();assert all(not t.is_alive()for t in state['archives']._threads|state['reviews']._threads)
 descriptor=os.dup(state['held'].fileno());state['capture_done']=True;state['generation']+=1
 return descriptor
def request_admission(generation):
 if generation!=state['generation']:raise StaleGeneration('OLD_GENERATION_ADMISSION_FORBIDDEN')
 if not state['capture_done']:raise RuntimeError('RECOVERY_NOT_CAPTURED')
 return True
old=threading.Thread(target=old_scheduler,name='CPU_OLD_SCHEDULER_NOT_REAL_OWNER')
try:
 old.start();check('actual_TPE_shutdown_joins_healthy_worker',wait(old_awaiting_only_shutdown));check('old_future_still_healthy_running',not state['future'].done())
 stack=[];fr=sys._current_frames().get(state['thread_ident'])
 while fr:stack.append({'function':fr.f_code.co_name,'file':fr.f_code.co_filename,'line':fr.f_lineno});fr=fr.f_back
 check('old_review_archive_threads_drained_stopped',all(not t.is_alive()for t in state['archives']._threads|state['reviews']._threads));check('foreign_EX_denied_before_handoff',not can_lock(lock))
 original_fd=state['held'].fileno();handoff_fd=capture_once();handoff_fd2=os.dup(handoff_fd)
 check('same_OFD_dup_foreign_EX_still_denied',not can_lock(lock));check('original_fd_still_valid_while_unwinding',os.fstat(original_fd).st_ino==os.fstat(handoff_fd).st_ino)
 try:capture_once();raise AssertionError('DUPLICATE_CAPTURE_ACCEPTED')
 except RuntimeError as e:check('duplicate_handoff_rejected','DUPLICATE_HANDOFF'in str(e))
 try:request_admission(0);raise AssertionError('OLD_GENERATION_ACCEPTED')
 except StaleGeneration:check('old_generation_cannot_admit',True)
 check('new_generation_admission_token_only',request_admission(1));check('original_started_flag_not_reset',state['started_once']is True)
 try:state['models'].submit(lambda:None);raise AssertionError('SHUTDOWN_EXECUTOR_REOPENED')
 except RuntimeError:check('old_executor_cannot_submit_after_shutdown',True)
 # Adoption observes the exact original future; it does not invoke a worker
 # again, create a fresh UUID or spawn a model/process.
 adopted={'CPU_ONLY_SPENT_UUID_A':{'pid':12345,'start_ticks':67890,'future':state['future']}}
 check('spent_UUID_PID_adopted_without_respawn',adopted['CPU_ONLY_SPENT_UUID_A']['future']is state['future']and state['model_calls']==1 and not state['spawn_calls'])
 release.set();old.join(timeout=3);check('healthy_completion_allows_old_shutdown_return',old_finished.is_set()and not old.is_alive());check('old_scheduler_body_never_resumes_admission',not state['old_body_after_throw'])
 check('original_file_closed_after_old_context_exit',state['held'].closed);check('dup_keeps_OFD_lock_after_original_close',not can_lock(lock));check('adopted_original_future_returns_once',adopted['CPU_ONLY_SPENT_UUID_A']['future'].result(timeout=1)['CPU_ONLY_UUID']=='CPU_ONLY_SPENT_UUID_A'and state['model_calls']==1)
 os.close(handoff_fd);handoff_fd=None;check('second_dup_still_holds_lock',not can_lock(lock));os.close(handoff_fd2);handoff_fd2=None;check('last_dup_close_releases_lock_to_foreign_EX',can_lock(lock))
 # Counterexample: LOCK_UN on *any* same-OFD duplicate releases the whole
 # flock, so recovery must retain the original close-only cleanup contract.
 with(tmp/'CPU_ONLY_EXPLICIT_UNLOCK_NEGATIVE.lock').open('a+b')as f:
  fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);d=os.dup(f.fileno())
  try:fcntl.flock(f,fcntl.LOCK_UN);check('explicit_LOCK_UN_would_break_dup_handoff',can_lock(Path(f.name)))
  finally:os.close(d)
 # A replacement state-machine fixture serializes only the short admission
 # phase. Already running fake CPU jobs concurrently wait outside that lock.
 admit_lock=threading.Lock();counter_lock=threading.Lock();run_release=threading.Event();counts={'admit':0,'admit_peak':0,'running':0,'running_peak':0,'deferred':0,'unexpected':False,'healthy_completed':0};consumed={'CPU_ONLY_SPENT_UUID_A'};new_starts=[]
 def run_job(uid):
  with counter_lock:counts['running']+=1;counts['running_peak']=max(counts['running_peak'],counts['running'])
  assert run_release.wait(5)
  with counter_lock:counts['running']-=1;counts['healthy_completed']+=1
  return uid
 def start_phase(uid,mode='ok'):
  with admit_lock:
   with counter_lock:counts['admit']+=1;counts['admit_peak']=max(counts['admit_peak'],counts['admit'])
   try:
    if counts['unexpected']:return 'FAIL_CLOSED_NO_NEW_ADMISSION'
    if uid in consumed:return 'ADOPT_EXISTING_IDENTITY_ONLY'
    if mode=='hold':counts['deferred']+=1;return 'DEFER_UNUSED_IDENTITY'
    if mode=='unexpected':counts['unexpected']=True;return 'PERMANENT_PAUSE_NEW_PRESERVE_HEALTHY'
    time.sleep(.01);consumed.add(uid);new_starts.append(uid);return runpool.submit(run_job,uid)
   finally:
    with counter_lock:counts['admit']-=1
 with cf.ThreadPoolExecutor(max_workers=6,thread_name_prefix='CPU_RECOVERY_RUNNING')as runpool:
  with cf.ThreadPoolExecutor(max_workers=6,thread_name_prefix='CPU_RECOVERY_START_PHASE')as starter:
   futures=[starter.submit(start_phase,'CPU_ONLY_NEW_'+str(i))for i in range(4)];jobs=[f.result(timeout=2)for f in futures]
  check('short_admission_serial_max1',counts['admit_peak']==1);check('running_jobs_still_high_parallel',wait(lambda:counts['running']==4)and counts['running_peak']>=4)
  check('adopted_spent_identity_never_relaunched',start_phase('CPU_ONLY_SPENT_UUID_A')=='ADOPT_EXISTING_IDENTITY_ONLY'and len(new_starts)==4)
  check('typed_HOLD_only_defers_unused_identity',start_phase('CPU_ONLY_UNUSED_HOLD','hold')=='DEFER_UNUSED_IDENTITY'and'CPU_ONLY_UNUSED_HOLD'not in consumed and counts['running']==4)
  check('unexpected_error_fail_closed_without_pool_unwind',start_phase('CPU_ONLY_UNUSED_ERROR','unexpected')=='PERMANENT_PAUSE_NEW_PRESERVE_HEALTHY'and counts['running']==4)
  check('unexpected_stop_cannot_be_reset_by_next_admission',start_phase('CPU_ONLY_AFTER_ERROR')=='FAIL_CLOSED_NO_NEW_ADMISSION'and'CPU_ONLY_AFTER_ERROR'not in consumed)
  run_release.set();check('healthy_jobs_finish_after_fail_closed',all(j.result(timeout=2).startswith('CPU_ONLY_NEW_')for j in jobs)and counts['healthy_completed']==4)
 pins=[]
 for p in [Path('/root/data/dtc_controlled_oracle_20261106_v1/initial8/tools/oracle_ops.py')]:
  if p.exists():pins.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 result={'schema':'DTC_RECOVERY_OFD_SHUTDOWN_HANDOFF_CPU_FIXTURE_V1','status':'PASS','checks':checks,'check_count':len(checks),'actual_old_thread_shutdown_stack':stack,'actual_source_reference_pins':pins,'CPU_fixture_events':events,'new_admission_state_machine_counts':counts,'CPU_fixture_native_path_removed':str(tmp),'fixture_pid':os.getpid(),'actual_owner_installed':False,'real_model_invocations':0,'actual_science_UUIDs_consumed':0,'registered_runtime_source_mutations':0,'registry_plan_mutations':0,'scope':'Actual native fcntl/OFD + actual TPE shutdown/join behavior; generation/adoption/admission policy is isolated fixture state, not qualification of R recovery implementation.'}
 (A/'CPU_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':len(checks),'fixture_pid':os.getpid(),'models':0,'real_owner_install':False}))
finally:
 release.set()
 if old.is_alive():old.join(timeout=3)
 for fd in [handoff_fd,handoff_fd2]:
  if fd is not None:
   try:os.close(fd)
   except OSError:pass
 assert str(tmp).startswith('/root/data/dtc_oracle_cpu_recovery_ofd_');shutil.rmtree(tmp)
