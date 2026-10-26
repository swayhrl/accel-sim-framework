#!/usr/bin/env python3
"""Reviewed candidate only. Remote child supervisor; no import-time actions."""
import os,sys,time,json,hashlib,pathlib,subprocess,select,signal,ctypes,threading
HEARTBEAT_GRACE=20
MIN_REMAINING=60
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
 assert ctypes.CDLL(None,use_errno=True).prctl(36,1,0,0,0)==0,'subreaper unavailable'
 me=ident(os.getpid());stop=[None]
 def request(sig,frame):stop[0]='signal '+str(sig)
 for sig in (signal.SIGTERM,signal.SIGHUP,signal.SIGINT):signal.signal(sig,request)
 for p,h in ((worker,wh),(job,jh)):
  assert hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==h,'frozen file changed '+p
 remaining=min(float(limit),float(deadline)-time.time())
 assert remaining>MIN_REMAINING,'deadline reserve exhausted'
 config=json.loads(pathlib.Path(job).read_text());task=config.get('task',{})
 attempt=ATTEMPT_ROOT/config['id']
 cap=config.get('resource_limits',{});cap_time=cap.get('capture_timeout_sec',task.get('capture_timeout_sec'));cap_bytes=cap.get('capture_max_bytes',task.get('capture_max_bytes'))
 last_budget=0
 # First heartbeat must arrive before any worker spawn.
 assert select.select([sys.stdin.buffer],[],[],15)[0],'no initial heartbeat'
 assert os.read(sys.stdin.fileno(),4096),'initial channel EOF'
 if stop[0]:raise RuntimeError(stop[0])
 proc=None;reason=None;last=time.monotonic();end=last+remaining
 chunks=[];output_limit=threading.Event();output_size=[0]
 try:
  proc=subprocess.Popen(['python3','-B',worker,job],stdout=subprocess.PIPE,stderr=None,text=True,start_new_session=True)
  def drain():
   while True:
    chunk=proc.stdout.read(8192)
    if not chunk:break
    output_size[0]+=len(chunk)
    if output_size[0]<=1048576:chunks.append(chunk)
    else:output_limit.set()
  reader=threading.Thread(target=drain,daemon=True);reader.start()
  while proc.poll() is None:
   now=time.monotonic()
   if stop[0]:reason=stop[0];break
   if output_limit.is_set():reason='worker stdout exceeds 1MiB';break
   if now>=end:reason='guard deadline';break
   if now-last>HEARTBEAT_GRACE:reason='heartbeat expired';break
   if now-last_budget>=5:
    last_budget=now
    startfile=attempt/'PROCESS_START.json'
    if startfile.exists() and not (attempt/'EXECUTION.json').exists():
     capture=json.loads(startfile.read_text());ci=ident(capture['capture_pid'])
     if ci and ci[1]==capture['capture_start_ticks']:
      age=float(pathlib.Path('/proc/uptime').read_text().split()[0])-int(ci[1])/os.sysconf('SC_CLK_TCK')
      if cap_time and age>cap_time:reason='declared capture time bound';break
      if cap_bytes and sum(p.stat().st_size for p in attempt.rglob('*') if p.is_file())>cap_bytes:reason='declared capture byte bound';break
   if select.select([sys.stdin.buffer],[],[],.2)[0]:
    b=os.read(sys.stdin.fileno(),4096)
    if not b:reason='parent channel EOF';break
    last=time.monotonic()
  if reason:
   killed=cleanup(me);print(json.dumps({'status':'FAILED_RETAINED','error':reason,'owned_cleanup':killed}),flush=True);return 74
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
