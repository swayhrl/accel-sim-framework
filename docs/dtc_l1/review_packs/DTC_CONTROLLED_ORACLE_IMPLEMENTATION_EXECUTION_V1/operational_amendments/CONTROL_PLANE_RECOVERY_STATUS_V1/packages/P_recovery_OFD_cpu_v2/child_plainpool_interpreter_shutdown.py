"""Real interpreter shutdown child. Main returns before private-pool submit."""
from pathlib import Path
import concurrent.futures as cf
import concurrent.futures.thread as ft
import hashlib,json,sys,threading,time,types,subprocess
sys.dont_write_bytecode=True
source=Path(sys.argv[1]);output=Path(sys.argv[2]);source_bytes=source.read_bytes();source_sha=hashlib.sha256(source_bytes).hexdigest();r=types.ModuleType('R_actual_plain_pool_shutdown_child');r.__file__=str(source);exec(compile(source_bytes,str(source),'exec'),r.__dict__)
assert __import__('os').getpid()!=r.OWNER_PID
events=[];lock=threading.Lock();keeper_released=threading.Event()
def event(name):
 with lock:events.append({'event':name,'monotonic':time.monotonic()})
old_empty_pool=cf.ThreadPoolExecutor(max_workers=1,thread_name_prefix='CPU_OLD_EMPTY_TPE')
def old_keeper():time.sleep(.15);event('OLD_KEEPER_RELEASED_NATURALLY');keeper_released.set()
keeper=threading.Thread(target=old_keeper,name='CPU_ORIGINAL_LIFETIME_KEEPER');keeper.start()
def original_lifetime_hook():event('ORIGINAL_LIFETIME_HOOK_ENTER');keeper.join();event('ORIGINAL_LIFETIME_HOOK_RETURN')
threading._register_atexit(original_lifetime_hook)
def recovery_master():
 try:
  deadline=time.monotonic()+4
  while not ft._shutdown:
   if time.monotonic()>deadline:raise AssertionError('REAL_INTERPRETER_GLOBAL_SHUTDOWN_NOT_REACHED')
   time.sleep(.005)
  event('FUTURES_GLOBAL_SHUTDOWN_NATURALLY_TRUE');assert keeper_released.is_set()
  try:old_empty_pool.submit(lambda:1);raise AssertionError('TPE_SUBMITTED_DURING_GLOBAL_SHUTDOWN')
  except RuntimeError as error:assert 'interpreter shutdown'in str(error)
  # This is the actual R library. No TPE/global flag reset or new atexit hook.
  pool=r.PlainPool(2,'CPU_ACTUAL_R_AFTER_INTERPRETER_RETURN',queue_capacity=4)
  jobs=[pool.submit(lambda x:x+1,x)for x in range(2)];values=[f.result(2)for f in jobs];assert values==[1,2];event('ACTUAL_PLAINPOOL_COMPLETED_AFTER_FUTURES_SHUTDOWN')
  cpu_only=pool.submit(lambda:subprocess.run(['/usr/bin/true'],check=True,timeout=2).returncode);assert cpu_only.result(3)==0;event('CPU_TRUE_SUBPROCESS_COMPLETED_AFTER_FUTURES_SHUTDOWN')
  pool.shutdown(True);assert all(not t.is_alive()for t in pool.threads);event('PLAINPOOL_SENTINELS_STOPPED_WORKERS');assert ft._shutdown is True
  assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha,'R_SOURCE_CHANGED_DURING_SHUTDOWN_TEST'
  output.write_text(json.dumps({'schema':'DTC_ACTUAL_R_PLAINPOOL_REAL_INTERPRETER_SHUTDOWN_V1','status':'PASS','events':events,'actual_R_source_sha256':source_sha,'future_global_flag_final':ft._shutdown,'global_flag_assignments_or_resets':0,'new_atexit_hooks_from_R_library':0,'private_worker_threads_stopped':True,'CPU_true_subprocess_after_shutdown_pass':True,'real_models':0,'owner_installs':0},indent=2)+'\n')
 except BaseException as error:
  output.write_text(json.dumps({'status':'FAIL','error':repr(error),'events':events},indent=2)+'\n')
  raise
master=threading.Thread(target=recovery_master,name='CPU_NONDAEMON_RECOVERY_MASTER',daemon=False);master.start();event('MAIN_BODY_RETURNING_NOW')
# The module really ends here. CPython invokes original hook, then the
# already registered futures exit hook, then waits for non-daemon master.
