"""Finite CPU-only real process lifecycle qualification; never invokes main/engine/driver or production locks."""
from pathlib import Path
import os,sys,signal,time,json,hashlib,importlib.util,subprocess
N=Path('/root/data/closed_audit_offload_independent_review_20261025_v1');W=N/'copy_only_v2_cpu_qualification_A1';W.mkdir(exist_ok=False)
source=Path('/root/data/shared_sm70_trace_library_20261024_v1/tools/resume_archive_copy_only_v2.py');spec=importlib.util.spec_from_file_location('review_copyonly_v2',source);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
signal.signal(signal.SIGTERM,v.deferred_stop);signal.signal(signal.SIGINT,v.deferred_stop)
foreign=subprocess.Popen(['/usr/bin/python3','-c','import time;time.sleep(60)'],start_new_session=True);foreign_id=v.proc_identity(foreign.pid);handles=[];results=[]
def record_case(name,fields):results.append(dict(name=name,status='PASS',**fields))
def register(path):
 def f(d):
  with path.open('x')as out:out.write(json.dumps(d));out.flush();os.fsync(out.fileno())
 return f
def waitfile(p):
 until=time.monotonic()+3
 while not p.exists()and time.monotonic()<until:time.sleep(.01)
 assert p.exists(),str(p)
def command(code):return ['/usr/bin/python3','-B','-c',code]
def foreign_ok():
 q=v.proc_identity(foreign.pid);assert q and q['start_ticks']==foreign_id['start_ticks']and foreign.poll()is None
try:
 # Actual child cannot exec before durable private register callback.
 v.STOP_REQUESTED=False;reg=W/'normal_registration.json';ran=W/'normal_executed';h=v.launch_gated(command('from pathlib import Path;assert Path('+repr(str(reg))+').exists();Path('+repr(str(ran))+').write_text("yes")'),subprocess.DEVNULL,register(reg),handles=handles);rc=v.wait_owned(h,time.monotonic()+3);assert rc==0 and ran.exists();assert v.proc_identity(h['identity']['pid'])['state']=='Z';c=v.cleanup_owned(h,term_seconds=.2,kill_seconds=.5);assert not c['unresolved'];record_case('registration_before_exec_and_unreaped_leader_reservation',{'cleanup':c})
 # Real TERM delivered precisely after Popen and identity capture, before register/release.
 v.STOP_REQUESTED=False;reg=W/'startup_stop_registration.json';ran=W/'startup_stop_executed'
 try:v.launch_gated(command('from pathlib import Path;Path('+repr(str(ran))+').write_text("forbidden")'),subprocess.DEVNULL,register(reg),after_spawn=lambda h:os.kill(os.getpid(),signal.SIGTERM),handles=handles);raise AssertionError('unexpected release')
 except RuntimeError as e:assert 'STOP_REQUESTED_BEFORE_EXEC_RELEASE'in str(e)
 assert reg.exists()and not ran.exists()and not v.owned_members(handles[-1]['identity']);record_case('real_TERM_afterspawn_beforeregister_no_exec',{'registered':True,'exec_marker_absent':True,'cleanup':handles[-1]['cleanup_receipt']})
 # Live own driver and child killed; independently created foreign process preserved.
 v.STOP_REQUESTED=False;pidfile=W/'live_child_pid.json';code='import subprocess,time,json;from pathlib import Path;p=subprocess.Popen(["/usr/bin/python3","-c","import time;time.sleep(60)"]);Path('+repr(str(pidfile))+').write_text(json.dumps({"pid":p.pid}));time.sleep(60)';h=v.launch_gated(command(code),subprocess.DEVNULL,register(W/'live_register.json'),handles=handles);waitfile(pidfile);os.kill(os.getpid(),signal.SIGTERM)
 try:v.wait_owned(h,time.monotonic()+3);raise AssertionError('stop ignored')
 except RuntimeError as e:assert 'STOP_REQUESTED'in str(e)
 c=v.cleanup_owned(h,term_seconds=.3,kill_seconds=.5);assert not c['unresolved'];assert any(x['pid']==json.loads(pidfile.read_text())['pid']for x in c['observed_members']);foreign_ok();record_case('TERM_live_driver_descendant_own_session_only',{'cleanup':c,'foreign_unchanged':True})
 # Driver first exits naturally, sender orphan remains same private session.
 v.STOP_REQUESTED=False;pidfile=W/'orphan_pid.json';code='import subprocess,json;from pathlib import Path;p=subprocess.Popen(["/usr/bin/python3","-c","import time;time.sleep(60)"]);Path('+repr(str(pidfile))+').write_text(json.dumps({"pid":p.pid}))';h=v.launch_gated(command(code),subprocess.DEVNULL,register(W/'orphan_register.json'),handles=handles);assert v.wait_owned(h,time.monotonic()+3)==0;waitfile(pidfile);assert v.proc_identity(h['identity']['pid'])['state']=='Z';orphan=json.loads(pidfile.read_text())['pid'];c=v.cleanup_owned(h,term_seconds=.3,kill_seconds=.5);assert not c['unresolved']and any(x['pid']==orphan for x in c['observed_members']);foreign_ok();same=v.cleanup_owned(h);assert same is c;record_case('leader_exit_orphan_stopped_without_rescanning_closed_session',{'cleanup':c,'foreign_unchanged':True})
 # Deadline is short-polled, not a blocking 72h child wait.
 v.STOP_REQUESTED=False;h=v.launch_gated(command('import time;time.sleep(60)'),subprocess.DEVNULL,register(W/'deadline_register.json'),handles=handles)
 try:v.wait_owned(h,time.monotonic()+.2);raise AssertionError('deadline ignored')
 except RuntimeError as e:assert 'deadline'in str(e)
 c=v.cleanup_owned(h,term_seconds=.3,kill_seconds=.5);assert not c['unresolved'];record_case('deadline_stops_own_session',{'cleanup':c})
 # Callback write failure never releases exec.
 v.STOP_REQUESTED=False;ran=W/'registration_fail_executed'
 def failreg(d):raise OSError('synthetic own metadata write failure')
 try:v.launch_gated(command('from pathlib import Path;Path('+repr(str(ran))+').write_text("forbidden")'),subprocess.DEVNULL,failreg,handles=handles);raise AssertionError('registration failure ignored')
 except OSError:pass
 assert not ran.exists()and not handles[-1]['cleanup_receipt']['unresolved'];record_case('registration_failure_no_exec',{'exec_marker_absent':True,'cleanup':handles[-1]['cleanup_receipt']})
 # Retry classification examines only newly appended own attempt bytes.
 p=W/'failure_tail.log';p.write_text('old RESOURCE_HOLD_DISK\n');offset=p.stat().st_size
 with p.open('a')as f:f.write('new fatal checksum mismatch\n')
 assert not v.resource_failure(v.new_failure_tail(p,offset))
 with p.open('a')as f:f.write('RESOURCE_HOLD_NEW_REAL_TEST\n')
 assert v.resource_failure(v.new_failure_tail(p,offset));record_case('old_RESOURCE_hold_cannot_mask_new_fatal',{})
 wrong=dict(foreign_id,start_ticks=foreign_id['start_ticks']+1);assert v.signal_exact(wrong,signal.SIGTERM)is False;foreign_ok();record_case('PID_startticks_mismatch_not_signalled',{'foreign_unchanged':True})
 finally_cleanup=[]
 for h in handles:
  c=v.cleanup_owned(h,term_seconds=.2,kill_seconds=.5);assert not c['unresolved'];finally_cleanup.append(c)
 result={'status':'PASS_FINITE_REAL_CPU_LIFECYCLE_ONLY','script':str(source),'script_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cases':len(results),'results':results,'production_main_invoked':False,'production_locks_opened':False,'production_engine_imported':False,'production_driver_started':False,'Source_or_trace_bytes_read':0,'sender_109_GPU_SIM':False,'own_processes_cleanup_unresolved':[],'foreign_sentinel_unchanged_during_all_cases':True,'observed_unix':time.time()};(W/'QUALIFICATION.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'path':str(W/'QUALIFICATION.json'),'sha256':hashlib.sha256((W/'QUALIFICATION.json').read_bytes()).hexdigest(),'cases':len(results),'script_sha256':result['script_sha256']}))
finally:
 for h in handles:v.cleanup_owned(h,term_seconds=.2,kill_seconds=.5)
 if foreign.poll()is None:
  assert v.proc_identity(foreign.pid)['start_ticks']==foreign_id['start_ticks'];foreign.terminate();foreign.wait(timeout=3)
