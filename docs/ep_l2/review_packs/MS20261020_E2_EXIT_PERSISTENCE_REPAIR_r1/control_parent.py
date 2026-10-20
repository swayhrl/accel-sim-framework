"""Bounded tiny process driver, never a complete simulator application."""
from pathlib import Path
import sys,os,json,time,signal
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import durable_exit as d
out=Path(sys.argv[1]);mode=sys.argv[2];out.mkdir();bounds=dict(disk_floor_bytes=5*2**30,monitor_reserve_bytes=2*2**30,maximum_result_bytes=2*2**20,monitor_interval_seconds=.02,termination_grace_seconds=.3,memory_bytes=128*2**20,timeout_seconds=.4 if mode=='timeout' else 8)
code="import os,signal,time; " + ("print('GPGPU-Sim: *** exit detected ***',flush=True);os._exit(7)" if mode=='exit7' else "os._exit(0)" if mode=='exit0' else "os.kill(os.getpid(),signal.SIGABRT)" if mode=='abort' else "time.sleep(8)")
try:
 with d.controller_signals(),(out/'raw.log').open('xb') as log:
  p=d.NativeProcess([sys.executable,'-c',code],out,log,os.environ.copy(),bounds,dict(control_case=mode,full_application=False))
  d.durable_json(out/'PARENT_CONTROL_READY.json',dict(parent=d.identity(os.getpid()),native=p.ready['native_process'],guardian=p.guardian_identity))
  p.release()
  while p.poll() is None:
   if d.STOP.is_set():
    os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=3);break
   time.sleep(.01)
  try: p.exit_evidence();p.binding={'wrong_case':True};p.exit_evidence();raise RuntimeError('wrong binding accepted')
  except AssertionError:pass
  d.durable_json(out/'PARENT_CONTROL_RESULT.json',dict(returncode=p.returncode,controller_stop=d.STOP.is_set(),wrong_binding_rejected=True))
except d.ExitEvidenceMissing as error:
 d.durable_json(out/'PARENT_CONTROL_RESULT.json',dict(status='INCOMPLETE',detail=str(error),success_inferred=False))
