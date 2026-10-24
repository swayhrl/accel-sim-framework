import pathlib,json,time,subprocess,os,signal,hashlib,importlib.util,shutil,sys
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');ID='ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2';V=C/'validate_app_hot_resume_v4r3.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):
 with p.open('x')as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
approval=pathlib.Path(sys.argv[1]);grant=json.loads(approval.read_text());assert grant['supervisor_sha256']==sha(pathlib.Path(__file__))
controller=C/'resume_stencil_hot_cpu_epoch2_v1.py';assert sha(controller)==grant['controller_sha256']and sha(V)=='85ff5d68408632a4f15634bfa6a6d7a504429821ed8067f1ab8f39ce1b9a6909'
spec=importlib.util.spec_from_file_location('guard',V);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
deadline=time.time()+48*3600;known={};peak=0;failure=None
def interrupted(signum,frame):raise InterruptedError('outer supervisor signal '+str(signum))
signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
with(C/(ID+'_HOT_EPOCH2_CONTROLLER.log')).open('x')as log:p=subprocess.Popen(['python3','-B',str(controller),'--approval',str(approval)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
identity=m.proc(p.pid);known[p.pid]=identity;save(C/(ID+'_HOT_EPOCH2_SUPERVISOR.json'),{'supervisor_pid':os.getpid(),'supervisor_start_ticks':m.proc(os.getpid())['ticks'],'controller':identity,'deadline_unix':deadline,'no_GPU_replay':True})
def cleanup():
 for sig in(signal.SIGTERM,signal.SIGKILL):
  groups=set()
  for x in known.values():
   try:
    now=m.proc(x['pid'])
    if now['ticks']==x['ticks']and now['pgid']==x['pgid']:groups.add(now['pgid'])
   except(FileNotFoundError,ProcessLookupError):pass
  for pg in groups:
   assert pg!=os.getpgrp()
   try:os.killpg(pg,sig)
   except ProcessLookupError:pass
  time.sleep(3)
try:
 with(C/(ID+'_HOT_EPOCH2_RESOURCE_EVENTS.jsonl')).open('x')as f:
  while p.poll()is None:
   ps=m.descendants(p.pid)
   for x in ps:known[x['pid']]=x
   rss=sum(x['rss']for x in ps);peak=max(peak,rss);free=shutil.disk_usage(C).free
   f.write(json.dumps({'unix':time.time(),'RSS':rss,'free':free,'processes':ps})+'\n');f.flush()
   assert time.time()<deadline and rss<16*2**30 and free>9*2**30,'whole epoch deadline/RSS/free polled guard'
   time.sleep(.5)
  assert p.returncode==0,('controller exit',p.returncode)
except BaseException as e:failure=repr(e);cleanup()
save(C/(ID+'_HOT_EPOCH2_SUPERVISOR_TERMINAL.json'),{'status':'COMPLETE'if not failure else'FAILED_RETAINED','failure':failure,'controller_returncode':p.poll(),'recursive_RSS_peak_bytes':peak,'registered_own_processes':len(known),'source_KEEP':True,'no_GPU_replay':True})
if failure:sys.exit(1)
