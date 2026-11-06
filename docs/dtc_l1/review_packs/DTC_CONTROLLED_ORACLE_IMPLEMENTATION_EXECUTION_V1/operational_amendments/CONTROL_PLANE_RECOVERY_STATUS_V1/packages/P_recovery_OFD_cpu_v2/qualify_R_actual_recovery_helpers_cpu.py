"""Actual R helper CPU tests with isolated frames and native lock inode."""
from pathlib import Path
import sys,types,hashlib,json,tempfile,threading,time,fcntl,os,shutil,subprocess
sys.dont_write_bytecode=True
A=Path(__file__).resolve().parent
SOURCE=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1/agents/R_same_owner_scheduler_recovery_v1/oracle_scheduler_recovery.py')
source_bytes=SOURCE.read_bytes();source_sha=hashlib.sha256(source_bytes).hexdigest();r=types.ModuleType('actual_R_recovery_cpu_only');r.__file__=str(SOURCE);exec(compile(source_bytes,str(SOURCE),'exec'),r.__dict__)
assert os.getpid()!=r.OWNER_PID
tmp=Path(tempfile.mkdtemp(prefix='dtc_oracle_cpu_recovery_helpers_',dir='/root/data'));ops=tmp/'initial8/tools/oracle_ops.py';ops.parent.mkdir(parents=True);(tmp/'control').mkdir();lock=tmp/'control/SHARED_DISPATCH_OWNER.lock';checks={};release=threading.Event();state={'started_once':True};cap=None
def ck(k,v):assert v,k;checks[k]=True
def wait(fn):
 end=time.monotonic()+3
 while time.monotonic()<end:
  if fn():return True
  time.sleep(.005)
 return False
code='''import concurrent.futures,threading,fcntl
def run_scheduler(state,lock_path,release):
 try:
  with lock_path.open('a+b')as held:
   fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
   with concurrent.futures.ThreadPoolExecutor(max_workers=1)as workers,concurrent.futures.ThreadPoolExecutor(max_workers=1)as archives,concurrent.futures.ThreadPoolExecutor(max_workers=1)as review_pool:
    work=lambda:release.wait(6);review=lambda:True
    future=workers.submit(work);running={future:({'CPU_ONLY':True},'CPU_SPENT_NO_MODEL')};post={};reviews={};dispatch_index=7
    archives.submit(review).result();review_pool.submit(review).result()
    state.update(thread_ident=threading.get_ident(),workers=workers,archives=archives,review_pool=review_pool,held=held,future=future)
    raise RuntimeError('RESOURCE_HOLD_CPU_ONLY_ORIGINAL_UNWIND')
 except RuntimeError as error:
  state['original_caught_after_shutdown']=str(error)
'''
ops.write_text(code);m=types.ModuleType('CPU_fake_old_ops_frame');m.__file__=str(ops);exec(compile(code,str(ops),'exec'),m.__dict__);thread=threading.Thread(target=m.run_scheduler,args=(state,lock,release),name='CPU_OLD_FRAME_NOT_REAL_OWNER')
try:
 thread.start();ck('actual_R_inspect_requires_real_shutdown_wait',wait(lambda:'workers'in state and state['workers']._shutdown and state['archives']._shutdown and state['review_pool']._shutdown))
 observed=r.inspect_unwinding_scheduler(state['thread_ident'],ops);ck('actual_R_inspect_captures_running_original_future',len(observed['running'])==1 and state['future']in observed['running']and not state['future'].done())
 cap=r.capture_handoff(state,ops);ck('actual_R_capture_osdup_same_inode_noninheritable',cap['lock_identity']['same_OFD_by_os_dup']and not os.get_inheritable(cap['held_duplicate'].fileno()))
 # install holds state.lock around capture and generation marker publication.
 # This fixture tests the helper's guarded precondition without calling install.
 state[r.GENERATION]={'CPU_ONLY_CAPTURED':True}
 try:r.capture_handoff(state,ops);raise AssertionError('DUPLICATE_CAPTURE_ACCEPTED')
 except AssertionError as e:ck('actual_R_duplicate_generation_guard',str(e)=='RECOVERY_ALREADY_INSTALLED_NO_DUPLICATE')
 release.set();thread.join(3);ck('actual_R_original_held_closes_duplicate_survives',not thread.is_alive()and state['held'].closed and not cap['held_duplicate'].closed)
 # Actual PlainPool must retain valid workers across task HOLD/unexpected
 # exceptions; exception transport must not unwind the master/controller.
 pool=r.PlainPool(1,'CPU_R_ACTUAL_PLAIN',queue_capacity=1);gate=threading.Event();began=threading.Event();calls=[]
 def block():began.set();assert gate.wait(3);calls.append('first');return 1
 f1=pool.submit(block);assert began.wait(1);f2=pool.submit(lambda:calls.append('second')or 2)
 try:pool.submit(lambda:calls.append('forbidden'));raise AssertionError('QUEUE_OVERFLOW_ACCEPTED')
 except r.PoolBusy as error:ck('actual_R_bounded_queue_HOLD_no_hidden_work',r.resource_hold(error))
 gate.set();ck('actual_R_plain_futures_return_expected',f1.result(2)==1 and f2.result(2)==2 and calls==['first','second'])
 def fail_hold():raise RuntimeError('RESOURCE_HOLD_CPU_TASK_ONLY')
 fh=pool.submit(fail_hold)
 try:fh.result(2);raise AssertionError('TASK_HOLD_LOST')
 except RuntimeError as error:ck('actual_R_plain_future_preserves_typed_HOLD',r.resource_hold(error))
 fe=pool.submit(lambda:(_ for _ in()).throw(ValueError('CPU_UNEXPECTED')))
 try:fe.result(2);raise AssertionError('UNEXPECTED_EXCEPTION_LOST')
 except ValueError as error:ck('actual_R_unexpected_not_misclassified_HOLD',not r.resource_hold(error))
 ck('actual_R_pool_survives_task_exception',pool.submit(lambda:3).result(2)==3);pool.shutdown(True);ck('actual_R_plain_sentinel_workers_stop',all(not t.is_alive()for t in pool.threads))
 ck('original_started_flag_never_reset',state['started_once']is True)
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_sha,'R_SOURCE_CHANGED_DURING_CPU_TEST'
 result={'schema':'DTC_ACTUAL_R_RECOVERY_HELPERS_CPU_QUALIFICATION_V1','status':'PASS','check_count':len(checks),'checks':checks,'R_source_path':str(SOURCE),'R_source_sha256':source_sha,'fixture_scope':'Actual R inspect/capture/PlainPool methods; isolated source-compatible old scheduler frame, no install.','model_invocations':0,'owner_installs':0,'registry_source_plan_mutations':0,'CPU_native_temp_removed':str(tmp)};(A/'R_ACTUAL_HELPERS_CPU_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print('R_ACTUAL_HELPERS_PASS',len(checks))
finally:
 release.set();thread.join(3)
 if cap is not None:cap['held_duplicate'].close()
 assert str(tmp).startswith('/root/data/dtc_oracle_cpu_recovery_helpers_');shutil.rmtree(tmp)
