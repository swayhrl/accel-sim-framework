import pathlib,json,hashlib,importlib.util,subprocess,time,os,signal,shutil,sys
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');N=C.parent;ID='ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2';WORK=N/(ID+'_post_native_epoch3')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):
 with p.open('x')as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def module(p,name,h):
 assert sha(p)==h;s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
grantpath=pathlib.Path(sys.argv[1]);grant=json.loads(grantpath.read_text());assert grant['supervisor_sha256']==sha(pathlib.Path(__file__))
controller=C/'resume_stencil_native8_post_epoch3_v1.py';assert sha(controller)==grant['controller_sha256']
post=module(C/'post_app_parallel_v5.py','post','c6fdc374344f4bb1d9cdec8f396807a9aef8d9b1fcf4741fc8477b18b86a0c2a')
proc=module(C/'validate_app_hot_resume_v4r3.py','proc','85ff5d68408632a4f15634bfa6a6d7a504429821ed8067f1ab8f39ce1b9a6909')
authority=module(C/'read_native_foreign_reserve_v1.py','auth','441fec1917c436781cc0aa6e7e0b35f7a9aa0dc019b2fe96540fca27c78a29ba')
foreign=authority.snapshot();assert foreign['registry_sha256']==grant['foreign_registry_sha256']and foreign['epoch_sha256']==grant['foreign_epoch_sha256']and foreign['sum_all_records_reserved_write_bytes']==grant['foreign_reserved_sum_bytes']<=2281701376
stop_requested=[]
def interrupted(signum,frame):stop_requested.append(signum)
signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
known={};deadline=time.time()+48*3600;peakrss=peakbytes=0;failure=None;foreign_checked=0
with(C/(ID+'_POST_EPOCH3_CONTROLLER.log')).open('x')as f:p=subprocess.Popen(['python3','-B',str(controller),str(grantpath)],stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
immediate=proc.proc(p.pid);known[p.pid]=immediate
save(C/(ID+'_POST_EPOCH3_SUPERVISOR.json'),{'pid':os.getpid(),'start_ticks':proc.proc(os.getpid())['ticks'],'controller':immediate,'deadline_unix':deadline,'whole_workflow_Native_bytes_polled_bound':4*2**30,'whole_process_tree_plus_supervisor_RSS_polled_bound':16*2**30,'minimum_free_bytes':9*2**30,'foreign_reserve_bound':2281701376,'no_GPU_or_record_revalidation':True})
def refresh():
 try:now=proc.proc(p.pid)
 except(FileNotFoundError,ProcessLookupError):return
 if now['ticks']==immediate['ticks']:
  for q in proc.descendants(p.pid):known[q['pid']]=q
def cleanup():
 try:refresh()
 except(FileNotFoundError,ProcessLookupError):pass
 # Stop creators before the final descendant snapshot; then TERM before CONT prevents later spawns.
 end=time.monotonic()+3;previous=None
 while time.monotonic()<end:
  try:refresh()
  except(FileNotFoundError,ProcessLookupError):pass
  active=[]
  for q in list(known.values()):
   try:
    now=proc.proc(q['pid'])
    if now['ticks']==q['ticks']and now['pgid']==q['pgid']:
     active.append(now)
     try:os.kill(q['pid'],signal.SIGSTOP)
     except ProcessLookupError:pass
   except(FileNotFoundError,ProcessLookupError):pass
  ids={(q['pid'],q['ticks'])for q in active}
  if ids==previous:break
  previous=ids;time.sleep(.05)
 groups={q['pgid']for q in active};assert os.getpgrp()not in groups
 for sig in[signal.SIGTERM,signal.SIGKILL]:
  for pg in groups:
   try:os.killpg(pg,sig);os.killpg(pg,signal.SIGCONT)
   except ProcessLookupError:pass
  time.sleep(3)
 unresolved=[]
 for q in active:
  try:
   now=proc.proc(q['pid']);state=pathlib.Path('/proc',str(q['pid']),'stat').read_text().split(') ',1)[1].split()[0]
   if now['ticks']==q['ticks']and state!='Z':unresolved.append(now)
  except(FileNotFoundError,ProcessLookupError):pass
 return unresolved
unresolved=[]
try:
 with(C/(ID+'_POST_EPOCH3_RESOURCE_EVENTS.jsonl')).open('x')as log:
  while p.poll()is None:
   refresh();ps=proc.descendants(p.pid);rss=sum(q['rss']for q in ps)+proc.proc(os.getpid())['rss'];used=post.tree_size_race_safe(WORK);free=shutil.disk_usage(C).free;peakrss=max(peakrss,rss);peakbytes=max(peakbytes,used)
   if time.time()-foreign_checked>=10:foreign=authority.snapshot();assert foreign['sum_all_records_reserved_write_bytes']<=2281701376;foreign_checked=time.time()
   log.write(json.dumps({'unix':time.time(),'RSS_including_sort_and_supervisor':rss,'whole_epoch_Native_tree_bytes':used,'local_free':free,'foreign':foreign,'processes':ps})+'\n');log.flush()
   assert not stop_requested and time.time()<deadline and rss<16*2**30 and used<4*2**30 and free>9*2**30,'whole epoch stop/deadline/RSS/Native/free polled threshold'
   time.sleep(.5)
  assert not stop_requested and p.returncode==0,('CPU post controller exit',p.returncode)
except BaseException as e:failure=repr(e);unresolved=cleanup()
save(C/(ID+'_POST_EPOCH3_SUPERVISOR_TERMINAL.json'),{'status':'PASS'if not failure else'FAILED_RETAINED','failure':failure,'controller_returncode':p.poll(),'recursive_RSS_peak_bytes':peakrss,'whole_Native_tree_peak_bytes':peakbytes,'unresolved_exact_own_processes':unresolved,'source_KEEP':True,'no_GPU_or_SIM_runs':True,'bounds_are_polled_not_quotas':True})
if failure:sys.exit(1)
