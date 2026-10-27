"""Real isolated subprocess lifecycle tests; no production attachment or models."""
import pathlib,sys,subprocess,json,hashlib
P=pathlib.Path;B=P(__file__).parent;source=B/'l2_owner_lifetime_amendment_v1.py';checks=[]
def ck(name,value):assert value,name;checks.append(name)
child=r'''
import pathlib,sys,json,threading,time,atexit,importlib.util,concurrent.futures,concurrent.futures.thread as ft
out=pathlib.Path(sys.argv[1]);mode=sys.argv[2];source=pathlib.Path(sys.argv[3]);s=importlib.util.spec_from_file_location('owner_lifetime_fixture',source);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);events=[];data={'mode':mode,'events':events};ready=threading.Event()
def older_hook():events.append('OLDER_HOOK')
def later_hook():events.append('LATER_HOOK')
threading._register_atexit(older_hook)
def addon():
 pool=concurrent.futures.ThreadPoolExecutor(max_workers=1,thread_name_prefix='L2MLP_FIXTURE');pool.submit(lambda:17).result();ready.set()
 while not threading._SHUTTING_DOWN:time.sleep(.005)
 time.sleep(.05);data['shutdown_at_first_new_submit']=ft._shutdown;events.append('ADDON_AFTER_OLD_MAIN_RETURN')
 try:
  with pool._shutdown_lock:pool._max_workers=3
  data['existing_pool_results']=[f.result()for f in[pool.submit(lambda x:x*x,i)for i in range(9)]]
  new=concurrent.futures.ThreadPoolExecutor(max_workers=2,thread_name_prefix='AFTER_OLD_MAIN_RETURN');data['new_pool_results']=[f.result()for f in[new.submit(lambda x:x+1,i)for i in range(4)]];new.shutdown(wait=True);pool.shutdown(wait=True);data['shutdown_at_addon_natural_end']=ft._shutdown;data['addon_complete']=True;events.append('ADDON_NATURALLY_CLOSED')
 except BaseException as e:data['caught_error']=repr(e)
t=threading.Thread(target=addon,name='DTC_L2_MLP_ONE_OWNER',daemon=False);t.start();assert ready.wait(5)
if mode=='hook':
 # Simulate CPython 3.8 API absence: must reject without mutation, then restore.
 api=threading._register_atexit;del threading._register_atexit
 try:m.register_keepalive(t)
 except AssertionError:data['missing_private_api_rejected']=True
 finally:threading._register_atexit=api
 data['proof']=m.register_keepalive(t);data['repeat_proof']=m.register_keepalive(t);threading._register_atexit(later_hook)
def save():
 data['futures_shutdown_at_final_atexit']=ft._shutdown
 marker=getattr(sys.modules['__main__'],m.MARKER,None)
 if marker:data['hook_state']=marker['state']
 out.write_text(json.dumps(data,indent=2)+'\n')
atexit.register(save);events.append('OLD_MAIN_RETURNS')
'''
fixture=B/'CPU_OWNER_LIFETIME_SUBPROCESS.py';fixture.write_text(child)
records={}
for mode in ['control','hook']:
 output=B/('CPU_OWNER_LIFETIME_'+mode.upper()+'.json');r=subprocess.run([sys.executable,'-B',str(fixture),str(output),mode,str(source)],capture_output=True,text=True,timeout=15);ck(mode+'_subprocess_exit_zero',r.returncode==0);records[mode]=dict(result=json.loads(output.read_bytes()),stdout=r.stdout,stderr=r.stderr)
a=records['control']['result'];b=records['hook']['result']
ck('control_reproduces_global_shutdown_before_new_submit',a['shutdown_at_first_new_submit']and'cannot schedule new futures after'in a['caught_error'])
ck('hook_global_shutdown_false_on_new_submit',b['shutdown_at_first_new_submit']is False)
ck('hook_existing_executor_accepts_post_main_jobs',b['existing_pool_results']==[i*i for i in range(9)])
ck('hook_new_executor_creates_threads_after_main_return',b['new_pool_results']==[1,2,3,4])
ck('hook_addon_naturally_closed',b['addon_complete']and b['shutdown_at_addon_natural_end']is False)
ck('global_shutdown_only_after_addon_finished',b['futures_shutdown_at_final_atexit']and b['hook_state']['futures_shutdown_on_return']is False)
ck('missing_38_private_api_fails_closed',b['missing_private_api_rejected'])
ck('repeat_registration_idempotent',b['repeat_proof']['idempotent_existing_registration'])
ck('reverse_hook_order_understood',b['events'].index('LATER_HOOK')<b['events'].index('ADDON_NATURALLY_CLOSED')<b['events'].index('OLDER_HOOK'))
ck('hook_enters_before_global_tpe_exit',b['hook_state']['futures_shutdown_on_entry']is False)
result=dict(status='PASS',passed=len(checks),checks=checks,simulator_starts=0,production_parent_attached=False,amendment_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),driver_sha256=hashlib.sha256(P(__file__).read_bytes()).hexdigest(),python_version=sys.version,subprocess_cases=records,cpython38_source_notes=dict(threading_private_register_atexit_available=False,thread_pool_workers_daemon=True,thread_pool_exit_registration='atexit.register(_python_exit)',sources=['https://raw.githubusercontent.com/python/cpython/v3.8.20/Lib/threading.py','https://raw.githubusercontent.com/python/cpython/v3.8.20/Lib/concurrent/futures/thread.py'],source_inspection_only_not_a_38_runtime_test=True))
(B/'OWNER_LIFETIME_AMENDMENT_CPU_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='subprocess_cases'},indent=2))
