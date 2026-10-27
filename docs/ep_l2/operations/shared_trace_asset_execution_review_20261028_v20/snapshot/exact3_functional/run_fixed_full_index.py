
#!/usr/bin/python3
# Private single full-index attempt. Default displays prepared scope; --run-reviewed is explicit.
from pathlib import Path
import json,os,sys,hashlib,subprocess,resource,time,signal,re,shutil
O=Path(__file__).resolve().parent
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def put(p,j):Path(p).write_text(json.dumps(j,indent=2)+'\n')
def need(c,m):
 if not c:raise RuntimeError(m)
def main():
 pins=json.loads((O/'PREPARED_RUN_PINS.json').read_text())
 if sys.argv[1:]!=['--run-reviewed']:
  print(json.dumps({'status':'PREPARED_ONLY_NOT_RUN','pins':str(O/'PREPARED_RUN_PINS.json'),'command_after_Root_review':['/usr/bin/python3',str(Path(__file__)), '--run-reviewed'],'scope':pins['scope'],'limits':pins['limits']},indent=2));return 0
 resource.setrlimit(resource.RLIMIT_AS,(2**30,4*2**30))
 for r in pins['must_match']:
  need(sha(r['path'])==r['sha256'],'input/runtime/provenance drift: '+r['path'])
 need(sha(__file__)==pins['runner_sha256'],'runner drift')
 need(shutil.disk_usage('/').free>=pins['limits']['Native_floor_bytes'],'Native free space below floor')
 cpu=pins['limits']['cpu'];need(cpu in os.sched_getaffinity(0)and cpu not in(500,501,502,503),'CPU availability/exclusion')
 R=O/'full_run_a001';need(not R.exists(),'one fixed attempt only; output exists');R.mkdir()
 cmd=pins['argv'];env=pins['environment'];core=pins['core_path']
 binding=subprocess.run(['/usr/bin/ldd',cmd[0]],env=env,capture_output=True,text=True,timeout=10)
 resolved=next((l.split('=>')[1].split()[0]for l in binding.stdout.splitlines()if'libcudart.so =>'in l),None)
 need(resolved and Path(resolved).resolve()==Path(core).resolve(),'loader selected different core')
 put(R/'LOADER_BINDING.json',{'stdout':binding.stdout,'core_sha256':sha(core)})
 put(R/'PREBOUND_PINS.json',pins)
 def limits():
  resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(pins['limits']['simulator_AS_bytes'],pins['limits']['simulator_AS_bytes']));resource.setrlimit(resource.RLIMIT_FSIZE,(128*2**20,128*2**20));os.sched_setaffinity(0,{cpu});os.nice(15)
 start=time.monotonic();reason=None;observed=None;p=None
 with(R/'stdout.log').open('wb')as out,(R/'stderr.log').open('wb')as err:
  p=subprocess.Popen(cmd,cwd=R,env=env,stdout=out,stderr=err,preexec_fn=limits,start_new_session=True)
  ticks=(Path('/proc')/str(p.pid)/'stat').read_text().split()[21]
  put(R/'PROCESS_START.json',{'pid':p.pid,'start_ticks':ticks,'cpu':cpu})
  def stop():
   if p.poll()is None:
    os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(timeout=3)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
  def interrupted(signum,frame):
   stop();put(R/'INTERRUPTED_TERMINAL.json',{'pid':p.pid,'start_ticks':ticks,'rc':p.returncode,'signal':signum,'joined':True});raise SystemExit(128+signum)
  signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
  try:
   while p.poll()is None:
    try:
     lines=(Path('/proc')/str(p.pid)/'maps').read_text().splitlines();libs={l.split()[-1]for l in lines if'/libcudart.so'in l}
     if libs and observed is None:
      need(libs=={core},'mapped unexpected core')
      observed={'pid':p.pid,'start_ticks':ticks,'core_path':core,'core_sha256':sha(core),'affinity':sorted(os.sched_getaffinity(p.pid)),'maps_lines':[l for l in lines if'/libcudart.so'in l]}
      need(observed['affinity']==[cpu],'actual CPU mismatch');put(R/'ACTUAL_PROCESS_CORE_MAP.json',observed)
    except FileNotFoundError:pass
    except Exception as e:reason='MAP_CHECK_FAILURE '+str(e)
    if time.monotonic()-start>pins['limits']['wall_seconds']:reason='WALL_CAP'
    if any((R/n).stat().st_size>=128*2**20 for n in('stdout.log','stderr.log')):reason='LOG_CAP'
    if reason:stop();break
    time.sleep(.1)
   rc=p.wait()
  except BaseException:
   stop();raise
 text=(R/'stdout.log').read_text(errors='replace');stderr=(R/'stderr.log').read_text(errors='replace')
 vals=lambda pattern:[int(x)for x in re.findall(pattern,text)]
 per=vals(r'(?m)^gpu_sim_insn\s*=\s*(\d+)');total=vals(r'(?m)^gpu_tot_sim_insn\s*=\s*(\d+)');ctas=vals(r'ctas_completed (\d+)');uids=vals(r'kernel_launch_uid\s*=\s*(\d+)');cycles=vals(r'(?m)^gpu_tot_sim_cycle\s*=\s*(\d+)')
 expected=pins['expected']
 checks={'rc0':rc==0,'no_wall_or_log_cap':reason is None,'normal_exit':'GPGPU-Sim: *** simulation thread exiting ***'in text,'mapped_private_core':observed is not None,'exact_kernel_uid_order':uids==expected['kernel_uids'],'all_CTAs':ctas==expected['CTAs_cumulative'],'per_kernel_source_plus_aux_retirement':per==expected['per_kernel_retired_active_lane_uops'],'total_nonzero_source_plus_aux_retirement':bool(total)and total[-1]==expected['total_retired_active_lane_uops']and total[-1]>0,'under_cycle_cap':bool(cycles)and cycles[-1]<pins['limits']['max_cycles'],'record_diagnostics_disabled':'ADA6_DECODE'not in stderr}
 result={'schema':'CURRENT3_EXACT_FULL_INDEX_V3_FUNCTIONAL_RESULT_V1','status':'PASS_EXACT_FULL_INPUT_FUNCTIONAL'if all(checks.values())else'FAILED_OR_BOUNDED_INCOMPLETE','checks':checks,'rc':rc,'stop_reason':reason,'wall_seconds':time.monotonic()-start,'kernel_uids':uids,'completed_CTAs_cumulative':ctas,'retired_lane_uops_per_kernel':per,'retired_lane_uops_total':total[-1]if total else None,'total_cycles':cycles[-1]if cycles else None,'stdout_sha256':sha(R/'stdout.log'),'stderr_sha256':sha(R/'stderr.log'),'process_terminal':{'pid':p.pid,'start_ticks':ticks,'rc':rc,'joined':True,'present_after_join':Path('/proc',str(p.pid)).exists()},'expected':expected,'stderr_tail':stderr[-3000:],'failure_stdout_tail':text[-6000:]if not all(checks.values())else None,'per_record_decoded_multiset_diagnostic':False,'numeric_science_performance_generic_ISA_qualification':False,'original_worker_success':False,'all_DSO_mapping':'UNKNOWN_NOT_PERSISTED','original86_and_exact6_unchanged':True}
 put(R/'RESULT.json',result);print(json.dumps(result,indent=2));return 0 if all(checks.values())else 2
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as e:print(json.dumps({'status':'PRECONDITION_OR_HARNESS_FAILURE','error':repr(e)}),file=sys.stderr);sys.exit(2)
