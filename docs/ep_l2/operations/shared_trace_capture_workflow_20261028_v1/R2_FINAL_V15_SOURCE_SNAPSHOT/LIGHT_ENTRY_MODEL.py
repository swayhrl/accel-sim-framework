
#!/usr/bin/python3
# Private single full-index attempt. Default displays prepared scope; --run-reviewed is explicit.
from pathlib import Path
import json,os,sys,hashlib,subprocess,resource,time,signal,re,shutil
O=Path(os.environ['CFI_MODEL_RUN_DIR'])
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def put(p,j):Path(p).write_text(json.dumps(j,indent=2)+'\n')
def need(c,m):
 if not c:raise RuntimeError(m)
FOUR_JOBS={'TRANSPOSE_CUDA118_REPEAT2_ORIGINAL1024_OBJECTLINK_V2', 'CUDA118_CONVOLUTION_SEPARABLE_ORIGINAL_3072_REPEAT2_V1', 'SCAN_CUDA118_ORIGINAL_N6815744_R2_ALL17_SEED2009_SM89_V1'}
def exact_budget(pins):
 q=pins.get('job_id');need(q in FOUR_JOBS and pins['scope']=='R2_ONE_COMPLETE_CTA_PERAPP_ENTRY_'+q,'exact4 bounded smoke identity')
 allowed=(120,250000)
 need(pins['qualification_label']=='ENTRY_COMPLETE_CTA_RUNTIME_STARTUP_RETIREMENT_ONLY'and(pins['limits']['wall_seconds'],pins['limits']['max_cycles'])==allowed,'exact Root4 per-case wall/cycle budget')
def budget_outcome(reason,rc,cycles,max_cycles,log_sizes):
 if reason=='WALL_CAP':return 'WALL_CAP'
 if reason=='LOG_CAP'or rc==-signal.SIGXFSZ or any(n>=32*2**20 for n in log_sizes):return 'LOG_CAP'
 if cycles is not None and cycles>=max_cycles:return 'CYCLE_CAP'
 return None
def main():
 pins=json.loads((O/'PREPARED_RUN_PINS.json').read_text());exact_budget(pins)
 if sys.argv[1:]!=['--run-reviewed']:
  print(json.dumps({'status':'PREPARED_ONLY_NOT_RUN','pins':str(O/'PREPARED_RUN_PINS.json'),'command_after_Root_review':['/usr/bin/python3',str(Path(__file__)), '--run-reviewed'],'scope':pins['scope'],'limits':pins['limits']},indent=2));return 0
 resource.setrlimit(resource.RLIMIT_AS,(256*2**20,4*2**30))
 for r in pins['must_match']:
  need(sha(r['path'])==r['sha256'],'input/runtime/provenance drift: '+r['path'])
 need(sha(__file__)==pins['runner_sha256'],'runner drift')
 need(shutil.disk_usage('/').free>=pins['limits']['Native_floor_bytes'],'Native free space below floor')
 cpu=pins['limits']['cpu'];need(cpu in os.sched_getaffinity(0)and cpu not in(500,501,502,503),'CPU availability/exclusion')
 R=O/'full_run_a001';need(not R.exists(),'one fixed attempt only; output exists');R.mkdir()
 cmd=pins['argv'];env=pins['environment'];core=pins['core_path']
 put(R/'LOADER_BINDING.json',{'method':'Explicit frozen109 loader/carrier; actual /proc/model/maps must bind privatecore83c and pinned private fixed consumer','core_sha256':sha(core),'consumer_sha256':sha(pins['actual_consumer_path'])})
 put(R/'PREBOUND_PINS.json',pins)
 def limits():
  resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(pins['limits']['simulator_AS_bytes'],pins['limits']['simulator_AS_bytes']));resource.setrlimit(resource.RLIMIT_FSIZE,(32*2**20,32*2**20));os.sched_setaffinity(0,{cpu});need(os.getpriority(os.PRIO_PROCESS,0)==15,'inherited model nice15')
 start=time.monotonic();reason=None;observed=None;p=None
 with(R/'stdout.log').open('wb')as out,(R/'stderr.log').open('wb')as err:
  p=subprocess.Popen(cmd,cwd=R,env=env,stdout=out,stderr=err,preexec_fn=limits,start_new_session=True,pass_fds=(int(os.environ['CFI_OWNED_LEASE_FD']),))
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
    if any((R/n).stat().st_size>=32*2**20 for n in('stdout.log','stderr.log')):reason='LOG_CAP'
    if reason:stop();break
    time.sleep(.1)
   rc=p.wait()
  except BaseException:
   stop();raise
 text=(R/'stdout.log').read_text(errors='replace');stderr=(R/'stderr.log').read_text(errors='replace')
 vals=lambda pattern:[int(x)for x in re.findall(pattern,text)]
 per=vals(r'(?m)^gpu_sim_insn\s*=\s*(\d+)');total=vals(r'(?m)^gpu_tot_sim_insn\s*=\s*(\d+)');ctas=vals(r'ctas_completed (\d+)');uids=vals(r'kernel_launch_uid\s*=\s*(\d+)');cycles=vals(r'(?m)^gpu_tot_sim_cycle\s*=\s*(\d+)')
 expected=pins['expected']
 checks={'rc0':rc==0,'no_wall_or_log_cap':reason is None,'normal_exit':'GPGPU-Sim: *** simulation thread exiting ***'in text,'mapped_private_core':observed is not None,'exact_kernel_uid_order':uids==expected['kernel_uids'],'all_CTAs':ctas==expected['CTAs_cumulative'],'per_kernel_source_plus_aux_retirement':per==expected['per_kernel_retired_active_lane_uops'],'total_nonzero_source_plus_aux_retirement':bool(total)and total[-1]==expected['total_retired_active_lane_uops']and total[-1]>0,'under_cycle_cap':bool(cycles)and cycles[-1]<pins['limits']['max_cycles'],'record_diagnostics_disabled':'ADA6_DECODE'not in stderr,'no_active_unknown_input':expected['active_unknown_records']==0}
 budget=budget_outcome(reason,rc,cycles[-1]if cycles else None,pins['limits']['max_cycles'],[(R/n).stat().st_size for n in('stdout.log','stderr.log')])
 result={'schema':'SELECTED_COMPLETE_CTA_REAL_CONSUMER_SMOKE_RESULT_V1','status':'PASS_ENTRY_COMPLETE_CTA_RUNTIME_STARTUP_RETIREMENT_ONLY'if all(checks.values())else'UNKNOWN_BUDGET'if budget is not None else'SMOKE_FAILED_OR_BOUNDED_INCOMPLETE','budget_reason':budget,'budget_is_not_compatibility_failure':budget is not None,'checks':checks,'rc':rc,'stop_reason':reason,'wall_seconds':time.monotonic()-start,'kernel_uids':uids,'completed_CTAs_cumulative':ctas,'retired_lane_uops_per_kernel':per,'retired_lane_uops_total':total[-1]if total else None,'total_cycles':cycles[-1]if cycles else None,'stdout_sha256':sha(R/'stdout.log'),'stderr_sha256':sha(R/'stderr.log'),'process_terminal':{'pid':p.pid,'start_ticks':ticks,'rc':rc,'joined':True,'present_after_join':Path('/proc',str(p.pid)).exists()},'expected':expected,'zero_CFI_selected_scope_allowed':True,'generic_CALL_RET_dynamic_support_claim':False,'stderr_tail':stderr[-3000:],'failure_stdout_tail':text[-6000:]if not all(checks.values())else None,'all_features_model_exercised':False,'qualification_label':'ENTRY_COMPLETE_CTA_RUNTIME_STARTUP_RETIREMENT_ONLY','whole_input_functional':False,'per_record_decoded_multiset_diagnostic':False,'numeric_science_performance_generic_ISA_qualification':False,'capture_application_returncode':0,'capture_execution_ref':pins.get('capture_execution_ref'),'all_DSO_mapping':'UNKNOWN_NOT_PERSISTED','prior_qualified_inputs_and_science_unchanged':True}
 put(R/'RESULT.json',result);print(json.dumps(result,indent=2));return 0 if all(checks.values())else 2
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as e:print(json.dumps({'status':'PRECONDITION_OR_HARNESS_FAILURE','error':repr(e)}),file=sys.stderr);sys.exit(2)
