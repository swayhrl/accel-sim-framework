#!/usr/bin/env python3
"""Reviewed candidate only. Remote child supervisor; no import-time actions."""
import os,sys,time,json,hashlib,pathlib,subprocess,select,signal,ctypes,threading,shutil
HEARTBEAT_GRACE=20
MIN_REMAINING=60
NATIVE_FLOOR_ROOT=pathlib.Path('/data/c16')
CLEANUP_RESERVE=20
IDENTITY_CLOSURE_GRACE=15
def execution_stop_unix(received,deadline,limit):
 assert 0<float(limit)<=3600,"scope limit"
 return min(float(deadline)-CLEANUP_RESERVE,float(received)+float(limit))
ATTEMPT_ROOT=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080/inflight')
def ident(pid):
 try:
  t=pathlib.Path('/proc',str(pid),'stat').read_text().split(') ',1)[1].split()
  return (int(pid),t[19],int(t[1]))
 except (FileNotFoundError,ProcessLookupError):return None
def alive(x):
 y=ident(x[0]);return y is not None and y[1]==x[1]
def children(root):
 out={root[0]:root};changed=True
 rows=[x for p in pathlib.Path('/proc').iterdir() if p.name.isdigit() and (x:=ident(int(p.name)))]
 while changed:
  changed=False
  for x in rows:
   if x[2] in out and x[0] not in out:out[x[0]]=x;changed=True
 return list(out.values())[1:]
def send(x,sig):
 # pidfd pins the process identity; ticks are checked after opening it.
 try:fd=os.pidfd_open(x[0],0)
 except ProcessLookupError:return False
 try:
  y=ident(x[0])
  if y is None or y[1]!=x[1]:return False
  signal.pidfd_send_signal(fd,sig,None,0);return True
 except ProcessLookupError:return False
 finally:os.close(fd)
def cleanup(me):
 # Subreaper retains orphans. Stop each known parent before enumerating descendants.
 frozen={}
 for _ in range(20):
  found=children(me)
  for x in found:send(x,signal.SIGSTOP);frozen[x[0]]=x
  current=children(me)
  if all(x[0] in frozen and frozen[x[0]][1]==x[1] for x in current):break
 else:raise RuntimeError('cannot stabilize owned descendants')
 for x in frozen.values():send(x,signal.SIGTERM)
 for x in frozen.values():send(x,signal.SIGCONT)
 until=time.monotonic()+3
 while time.monotonic()<until and children(me):
  try:
   while os.waitpid(-1,os.WNOHANG)[0]:pass
  except ChildProcessError:pass
  time.sleep(.05)
 # TERM handlers may spawn: stop parents, enumerate, then KILL exact identities.
 for _ in range(20):
  xs=children(me)
  if not xs:break
  for x in xs:send(x,signal.SIGSTOP)
  for x in children(me):send(x,signal.SIGSTOP);send(x,signal.SIGKILL)
  try:
   while os.waitpid(-1,os.WNOHANG)[0]:pass
  except ChildProcessError:pass
  time.sleep(.05)
 assert not children(me),'owned descendants survived cleanup'
 return [{'pid':x[0],'start_ticks':x[1]} for x in frozen.values()]
def main():
 # argv: worker, worker_sha, job, job_sha, absolute_batch_deadline, max_seconds
 worker,wh,job,jh,deadline,limit=sys.argv[1:]
 os.nice(15);os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2])
 received_unix=time.time();stop_unix=execution_stop_unix(received_unix,deadline,limit)
 stop_mono=time.monotonic()+max(0,stop_unix-received_unix)
 boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()
 assert ctypes.CDLL(None,use_errno=True).prctl(36,1,0,0,0)==0,'subreaper unavailable'
 me=ident(os.getpid());stop=[None]
 def request(sig,frame):stop[0]='signal '+str(sig)
 for sig in (signal.SIGTERM,signal.SIGHUP,signal.SIGINT):signal.signal(sig,request)
 for p,h in ((worker,wh),(job,jh)):
  assert hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==h,'frozen file changed '+p
 assert 0<float(limit)<=3600,'scope guard exceeds3600s'
 remaining=stop_unix-time.time()
 assert remaining>MIN_REMAINING,'deadline reserve exhausted'
 config=json.loads(pathlib.Path(job).read_text());task=config.get('task',{})
 attempt=ATTEMPT_ROOT/config['id']
 private_temp=pathlib.Path(job).resolve().parent.parent/'guard_runtime'/('guard_'+str(me[0])+'_'+me[1])
 private_temp.mkdir(parents=True,exist_ok=False)
 os.environ.update(TMPDIR=str(private_temp),TMP=str(private_temp),TEMP=str(private_temp),CUDA_CACHE_PATH=str(private_temp/'cuda_cache'),CUDA_CACHE_MAXSIZE=str(64*1024**2),XDG_CACHE_HOME=str(private_temp/'xdg_cache'))
 cap=config.get('resource_limits',{});cap_time=cap.get('capture_timeout_sec',task.get('capture_timeout_sec'));cap_bytes=cap.get('capture_max_bytes',task.get('capture_max_bytes'))
 last_budget=0;uncertain_since={}
 # First heartbeat must arrive before any worker spawn.
 assert select.select([sys.stdin.buffer],[],[],15)[0],'no initial heartbeat'
 assert os.read(sys.stdin.fileno(),4096),'initial channel EOF'
 if stop[0]:raise RuntimeError(stop[0])
 proc=None;reason=None;last=time.monotonic();end=stop_mono
 chunks=[];output_limit=threading.Event();output_size=[0]
 def check_budget():
  now=time.monotonic();reason=None
  if shutil.disk_usage(NATIVE_FLOOR_ROOT).free<5*1024**3 or shutil.disk_usage(attempt.parent).free<5*1024**3:return 'physical5GiB floor'
  # Observer and instrumented app both have exact per-app600s budgets.
  # Start cleanup10s before the declared app cap; no600s claim from worker query loop alone.
  for app_root in (attempt/'observer',attempt):
   startfile=app_root/'PROCESS_START.json'
   if startfile.exists() and not (app_root/'EXECUTION.json').exists():
    capture=json.loads(startfile.read_text());ci=ident(capture['capture_pid'])
    if ci is None or ci[1]!=capture['capture_start_ticks']:
     key=str(startfile);uncertain_since.setdefault(key,now)
     if now-uncertain_since[key]>=IDENTITY_CLOSURE_GRACE:return 'capture identity unknown before execution closure'
     continue
    uncertain_since.pop(str(startfile),None)
    if ci and ci[1]==capture['capture_start_ticks']:
     owned={x[0]:x for x in children(me)}
     if ci[1]==capture['capture_start_ticks'] and (ci[0] not in owned or owned[ci[0]][1]!=ci[1]):return 'capture identity outside owned descendants'
     age=float(pathlib.Path('/proc/uptime').read_text().split()[0])-int(ci[1])/os.sysconf('SC_CLK_TCK')
     if cap_time and age>=max(0,cap_time-10):return 'declared app time cleanup reserve'
  if cap_bytes and sum(p.stat().st_size for base0 in (attempt,private_temp) for p in base0.rglob('*') if p.is_file())>cap_bytes:return 'declared total byte bound'
  return None
 budget_reason=[None];budget_progress=[time.monotonic()]
 def monitor_budget():
  while proc is not None and proc.poll() is None:
   try:
    result=check_budget()
    if result:budget_reason[0]=result;return
    budget_progress[0]=time.monotonic()
   except BaseException as e:budget_reason[0]='budget metadata unavailable '+type(e).__name__;return
   time.sleep(.2)
 try:
  assert time.monotonic()<stop_mono and time.time()<stop_unix,'deadline exhausted before spawn'
  proc=subprocess.Popen(['python3','-B',worker,job],stdout=subprocess.PIPE,stderr=None,text=True,start_new_session=True)
  def drain():
   while True:
    chunk=proc.stdout.read(8192)
    if not chunk:break
    output_size[0]+=len(chunk)
    if output_size[0]<=1048576:chunks.append(chunk)
    else:output_limit.set()
  reader=threading.Thread(target=drain,daemon=True);reader.start()
  budget_thread=threading.Thread(target=monitor_budget,daemon=True);budget_thread.start()
  while proc.poll() is None:
   now=time.monotonic()
   if stop[0]:reason=stop[0];break
   if output_limit.is_set():reason='worker stdout exceeds 1MiB';break
   if now>=end or time.time()>=stop_unix:reason='guard deadline';break
   if now-last>HEARTBEAT_GRACE:reason='heartbeat expired';break
   if budget_reason[0]:reason=budget_reason[0];break
   if now-budget_progress[0]>15:reason='budget metadata monitor stalled';break
   if select.select([sys.stdin.buffer],[],[],.2)[0]:
    b=os.read(sys.stdin.fileno(),4096)
    if not b:reason='parent channel EOF';break
    last=time.monotonic()
  if reason is None:
   budget_thread.join(timeout=1)
   if budget_thread.is_alive():reason='budget metadata monitor stalled'
   elif budget_reason[0]:reason=budget_reason[0]
  if reason:
   requested=time.time();killed=cleanup(me);print(json.dumps({'status':'FAILED_RETAINED','error':reason,'owned_cleanup':killed,'guard_pid':me[0],'guard_start_ticks':me[1],'boot_id':boot_id,'stop_requested_unix':requested,'absolute_deadline_unix':float(deadline),'cleanup_finished_unix':time.time()}),flush=True);return 74
  rc=proc.wait()
  leftovers=children(me)
  if leftovers:
   killed=cleanup(me);print(json.dumps({'status':'FAILED_RETAINED','error':'worker left descendants','owned_cleanup':killed}),flush=True);return 75
  reader.join(timeout=3)
  assert not reader.is_alive(),'stdout reader did not complete'
  assert not output_limit.is_set(),'worker stdout exceeds 1MiB'
  sys.stdout.write(''.join(chunks));sys.stdout.flush();return rc
 finally:
  if children(me):cleanup(me)
if __name__=='__main__':sys.exit(main())
