"""Isolated CPU-only process: actual thread affinity and CPython fast-local mutation.
No production parent attachment, model, native entry or registry use.
"""
import pathlib,importlib.util,os,threading,time,json,hashlib,concurrent.futures,sys
P=pathlib.Path;B=P(__file__).parent;s=importlib.util.spec_from_file_location('affinity_amendment_fixture',B/'l2_scheduler_affinity_amendment_v1.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
allowed=sorted(os.sched_getaffinity(0));assert len(allowed)>=4;wide=allowed[:4];narrow=wide[:1];os.sched_setaffinity(0,narrow)
ready=threading.Event();advance=threading.Event();release=threading.Event();done=threading.Event();started=[];lock=threading.Lock();box={};old_stop=threading.Event()
def work():
 with lock:started.append(dict(tid=threading.get_native_id(),aff=sorted(os.sched_getaffinity(0))))
 release.wait(15)
def old_work():old_stop.wait(15)
old=threading.Thread(target=old_work,name='OLD_OWNER_UNCHANGED');old.start();old_aff=sorted(os.sched_getaffinity(old.native_id))
code='''def run_scheduler():
 max_workers=1
 pool=concurrent.futures.ThreadPoolExecutor(max_workers=max_workers,thread_name_prefix='L2MLP')
 claims={};running={}
 box['pool']=pool;box['claims_id']=id(claims);box['running_id']=id(running)
 pool.submit(work);ready.set();advance.wait(15)
 box['capacity_after']=max_workers
 for _ in range(max_workers-1):pool.submit(work)
 box['after_submit']=True
 release.wait(15);pool.shutdown(wait=True);done.set()
'''
path=B/'CPU_AFFINITY_FIXTURE_SCHEDULER.py';path.write_text(code);ns=globals().copy();exec(compile(code,str(path),'exec'),ns);scheduler=threading.Thread(target=ns['run_scheduler'],name='DTC_L2_MLP_ONE_OWNER');scheduler.start();assert ready.wait(10)
end=time.monotonic()+10
while len(started)<1 and time.monotonic()<end:time.sleep(.01)
checks=[]
def ck(name,ok):assert ok,name;checks.append(name)
try:
 ck('fixture_initial_worker_narrow',started[0]['aff']==narrow)
 try:m.amend_thread_in_process(scheduler,path,'wrong-sha',wide,4)
 except AssertionError:checks.append('wrong_source_pin_rejected')
 else:raise AssertionError('wrong source SHA accepted')
 proof=m.amend_thread_in_process(scheduler,path,m._sha(path),wide,4)
 ck('existing_pool_not_replaced',id(box['pool'])==proof['executor_object_id'])
 ck('main_affinity_unchanged',sorted(os.sched_getaffinity(0))==narrow)
 ck('old_thread_affinity_unchanged',sorted(os.sched_getaffinity(old.native_id))==old_aff)
 ck('scheduler_affinity_expanded',sorted(os.sched_getaffinity(scheduler.native_id))==wide)
 ck('executor_capacity_expanded',box['pool']._max_workers==4)
 ck('fast_local_capacity_expanded',m.find_scheduler_frame(scheduler,path).f_locals['max_workers']==4)
 ck('claims_running_object_ids_unchanged',id(m.find_scheduler_frame(scheduler,path).f_locals['claims'])==box['claims_id']and id(m.find_scheduler_frame(scheduler,path).f_locals['running'])==box['running_id']and proof['claims_and_running_objects_unchanged'])
 advance.set();end=time.monotonic()+10
 while len(started)<4 and time.monotonic()<end:time.sleep(.01)
 ck('new_capacity_used_by_scheduler',box.get('capacity_after')==4 and len(started)==4)
 ck('new_worker_threads_inherit_wide_affinity',all(x['aff']==wide for x in started[1:]))
 ck('existing_worker_affinity_expanded',all(sorted(os.sched_getaffinity(x['tid']))==wide for x in started))
 ck('parse_cgroup_cpu_ranges',m.parse_cpu_list('0-2,5,7-8')==[0,1,2,5,7,8])
finally:
 advance.set();release.set();old_stop.set();scheduler.join(15);old.join(15);os.sched_setaffinity(0,allowed)
ck('fixture_threads_naturally_closed',not scheduler.is_alive()and not old.is_alive())
result=dict(status='PASS',checks=checks,passed=len(checks),simulator_starts=0,production_parent_attached=False,production_registry_mutations=0,amendment_sha256=m._sha(B/'l2_scheduler_affinity_amendment_v1.py'),driver_sha256=m._sha(__file__),proof=proof)
(B/'AFFINITY_AMENDMENT_CPU_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
