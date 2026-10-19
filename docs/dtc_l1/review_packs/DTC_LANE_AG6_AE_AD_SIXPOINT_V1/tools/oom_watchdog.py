"""Independent 0.25s owned-root pidfd OOM guard; no process start API."""
import os,signal,threading,json,time
from pathlib import Path

def start(pid,destination,event_path=Path('/sys/fs/cgroup/memory.events'),baseline=None):
 def read():return {k:int(v) for k,v in (l.split() for l in event_path.read_text().splitlines())}
 initial=baseline if baseline is not None else read();pidfd=os.pidfd_open(pid);stop=threading.Event();state={'reason':None}
 def work():
  with Path(destination).open('x') as log:
   while not stop.is_set():
    try:
     events=read();reason='NEW_CGROUP_OOM_OR_OOM_KILL' if any(events[k]>initial[k] for k in ['oom','oom_kill']) else None
    except BaseException as exc:events=None;reason='OOM_WATCHDOG_FAILURE:'+repr(exc)
    log.write(json.dumps(dict(monotonic_ns=time.monotonic_ns(),events=events,reason=reason))+'\n');log.flush()
    if reason:
     state['reason']=reason
     try:signal.pidfd_send_signal(pidfd,signal.SIGTERM)
     except ProcessLookupError:pass
     return
    stop.wait(.25)
 thread=threading.Thread(target=work,name='AG3_owned_root_OOM_guard',daemon=False);thread.start()
 return stop,thread,state,pidfd

def finish(watch):
 watch[0].set();watch[1].join();os.close(watch[3])
