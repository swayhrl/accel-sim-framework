"""Same-owner STOP_ONLY of the new exact16 scheduler; import is inert.
No signal, source/registry/lease/budget edit or new thread. Root invokes once.
"""
from pathlib import Path
import sys,os,json,threading,datetime,hashlib
P=Path
R=P('/root/data/dtc_perf_first_v2_codesign16_20261105_v1')
N=P('/root/data/ep_l2_dtc_l1_native_v2')
REQ='DTC_PERF_FIRST_V2_PHYSICAL_PIB16_20261105_V1'
ADDON='DTC_PERFV2_CODESIGN16_OWNER_ADDON_V1'
MARKER='DTC_PERFV2_CODESIGN16_CONTROLLED_STOP_ONLY_V1'
class ControlledStopOnly(BaseException):pass

def _install_private_stop(engine):
 assert engine.REQ==REQ and P(engine.__file__)==R/'tools/perf16_native.py'
 original=engine.registered
 def stop_registered(*args,**kwargs):raise ControlledStopOnly('ZERO_MODEL_PRE_INTENT_ENGINEERING_STOP_NEW16_THREAD_ONLY')
 engine.registered=stop_registered
 return original,stop_registered

def stop_only():
 assert sys.dont_write_bytecode and threading.current_thread()is threading.main_thread()
 assert os.getpid()==1498278 and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 main=sys.modules['__main__'];assert not hasattr(main,MARKER),'STOP_ONLY_ALREADY_INSTALLED_OBSERVE_STATE_NO_BLIND_REAPPLY'
 assert (R/'control/ENGINEERING_PAUSE_NEW.json').is_file(),'NEW_REQUEST_PAUSE_REQUIRED'
 # Direct atomic JSON read, deliberately NO authority()/registered()/SH flock.
 reg=json.loads((N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_bytes());q=reg['registered_future_requests'][REQ]
 assert q['request']==REQ and q['budget']==q['remaining']==len(q['admitted_specs'])==16 and q['consumed']=={},'ZERO_CONSUMED_FIXED16_REQUIRED'
 for c in q['admitted_specs']:
  assert not(R/'control/qualification_ledger'/(c+'.INTENT.json')).exists(),'INTENT_ALREADY_EXISTS_NO_STOP_ONLY'
  assert not(R/'control/qualification_ledger'/(c+'.DONE.json')).exists(),'DONE_ALREADY_EXISTS'
 for out in (R/'DTC/run/results').glob('*'):
  if out.is_dir():assert not any((out/x).exists()for x in ['SIM_PID','NATIVE_SIMULATOR_PID_AND_MAPS.json']),'MODEL_EVIDENCE_ALREADY_EXISTS'
 for fd,expected in [(3,'/root/data/dtc_main_v100_sweep_20261025_v1/control/FINITE_CONTROLLER.lock'),(4,str(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock'))]:
  assert os.readlink('/proc/self/fd/'+str(fd))==expected and'FLOCK'in P('/proc/self/fdinfo',str(fd)).read_text(),'ORIGINAL_KEEPER_FD_MISSING'
 addon=getattr(main,ADDON);worker=addon['thread'];assert worker.is_alive()and worker.ident!=threading.get_ident()
 frame=sys._current_frames().get(worker.ident);found=None
 while frame is not None:
  if frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==R/'tools/perf16_ops.py':found=frame;break
  frame=frame.f_back
 assert found is not None and'e'in found.f_locals,'EXACT_NEW16_SCHEDULER_FRAME_REQUIRED'
 engine=found.f_locals['e'];assert P(engine.registered.__code__.co_filename)==R/'tools/perf16_native.py'
 original,replacement=_install_private_stop(engine)
 state=dict(phase='CONTROLLED_STOP_ONLY_INSTALLED',thread=worker,engine=engine,original_registered=original,replacement_registered=replacement,exception_class=ControlledStopOnly,old_addon=addon,installed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),request=REQ,source_sha256=hashlib.sha256(P(__file__).read_bytes()).hexdigest(),no_signals=True,no_registry_or_source_writes=True)
 setattr(main,MARKER,state);worker.join(timeout=.2)
 result=dict(schema='DTC_PERFV2_CODESIGN16_STOP_ONLY_RECEIPT_V1',phase='OLD_NEW16_THREAD_EXITED'if not worker.is_alive()else'STOP_REQUEST_INSTALLED_AWAIT_ZERO_MODEL_FRONTEND_RELEASE',owner_pid=os.getpid(),owner_start_ticks=977758783,request=REQ,old_new16_thread_ident=worker.ident,thread_alive=worker.is_alive(),budget=16,consumed=0,remaining=16,registry_or_source_writes=0,models_or_owner_signaled=0,new_threads_started=0,Main_affinity_unchanged=True,source_sha256=state['source_sha256'])
 state['receipt']=result;state['phase']=result['phase'];return result
