"""Selected coordinator subreaper adapter. Frozen selected+5d bytes executed unchanged."""
import pathlib,os,sys,json,signal,runpy,resource
from owned_runtime_v1 import *
def main():
 D=pathlib.Path(__file__).resolve().parent
 mode,script,work,fdjson,*args=sys.argv[1:];fds=json.loads(fdjson);work=pathlib.Path(work)
 need(mode in ('POST','CPU_FIXTURE'),'fixed executor mode')
 allowed=[str(D/'selected_cpu248_v1.py')]if mode=='POST'else[str(D/'cpu_lifecycle_payload_v1.py')];need(script in allowed,'fixed script whitelist')
 set_subreaper();stopped=[False]
 def stop(sig,frame):
  if not stopped[0]:stopped[0]=True;raise RuntimeError('owned runner signal cleanup')
 for sig in (signal.SIGTERM,signal.SIGHUP,signal.SIGINT):signal.signal(sig,stop)
 try:
  sys.argv=[script,*args]
  runpy.run_path(script,run_name='__main__')
 finally:
  try:
   if children(ident(os.getpid())):cleanup(ident(os.getpid()))
   reap();need(not children(ident(os.getpid())),'runner unknown owned children')
   write(work/'RUNNER_CLOSED.json',dict(status='OWNED_ALL_CLOSED_BEFORE_FD_COPIES_CLOSE',owner=ident(os.getpid()),fds=fds))
  except BaseException as e:hold(work/'RUNNER_HOLD_UNKNOWN.json',e,fds)
  for fd in fds:os.close(fd) # close only, NEVER LOCK_UN
if __name__=='__main__':main()
