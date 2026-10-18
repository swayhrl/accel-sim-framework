import argparse,subprocess,sys,os,json,time,signal,importlib.util
from resource_accounting_r3 import snapshot,SHARED,reg as central_reg
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--memory-gib',default=2,type=int);p.add_argument('--output-mib',default=16,type=int);p.add_argument('--timeout',default=600,type=int);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args();assert a.command and a.command[0]!='--'
env=os.environ.copy();env['LANE2_COMMAND_JSON']=json.dumps(a.command);env.update(LANE2_MEM_GIB=str(a.memory_gib),LANE2_OUTPUT_MIB=str(a.output_mib),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
root=Path(os.environ.get('LANE2_MONITOR_ROOT','/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_R3_METADATA_AND_COST_OPT_lane2'))
def size():return sum(x.stat().st_size for x in root.rglob('*') if x.is_file())
subprocess.run([sys.executable,'/workspace/ep_l2_rtl_r3_metadata_cost/admit.py'],env=env,check=True)
spec=importlib.util.spec_from_file_location('r2registry','/workspace/ep_l2_rtl_r3_metadata_cost/registry_pinned.py');reg=importlib.util.module_from_spec(spec);spec.loader.exec_module(reg)
proc=None;initial=size();start=time.time();reason=None;peak_rss=0;last_aggregate_check=0
try:
 proc=subprocess.Popen(a.command,env=env,start_new_session=True)
 while proc.poll() is None:
  st=os.statvfs('/workspace');sh=os.statvfs('/root/share')
  group_rss=sum(int(line.split()[1])*1024 for line in subprocess.check_output(['ps','-eo','pgid=,rss='],text=True).splitlines() if line.split() and int(line.split()[0])==proc.pid)
  peak_rss=max(peak_rss,group_rss)
  if group_rss>a.memory_gib*2**30:reason='RESERVED_MEMORY_CAP'
  mem_available=next(int(x.split()[1])*1024 for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:'))
  if mem_available<64*2**30:reason='AVAILABLE_RAM_FLOOR'
  if time.time()-start>a.timeout:reason='BOUNDED_TIMEOUT'
  if time.time()>=1792312529:reason='ORIGINAL_R3_SIX_HOUR_DEADLINE'
  if size()-initial>a.output_mib*2**20:reason='EDA_PHASE_OUTPUT_CAP'
  floor_bytes=int(47.5*2**30) if env.get('LANE2_EXACT_EDA_EXCEPTION')=='1' else 48*2**30
  if st.f_bavail*st.f_frsize<floor_bytes or sh.f_bavail*sh.f_frsize<40*2**30:reason='DISK_SAFETY_FLOOR'
  if time.time()-last_aggregate_check>10:
   with central_reg.Registry(SHARED).locked() as state:account=snapshot(state)
   if account['shared_result_actual_bytes']+account['Lane2_outside_shared_results_plus_Git_bytes']>account['shared_limit_bytes']:reason='SHARED20G_ACTUAL_CEILING'
   if account['Lane2_owned_actual_plus_conservative_Git_reserve_bytes']>account['own_limit_bytes']:reason='LANE2_OWN12G_ACTUAL_CEILING'
   last_aggregate_check=time.time()
  if reason:
   os.killpg(proc.pid,signal.SIGTERM);proc.wait(timeout=10);break
  time.sleep(0.5)
 rc=proc.wait();print(json.dumps({'command':a.command,'rc':rc,'resource_stop':reason,'elapsed_seconds':time.time()-start,'new_artifact_bytes':size()-initial,'sampled_peak_group_rss_bytes':peak_rss}),flush=True)
finally:
 if proc is not None and proc.poll() is None:os.killpg(proc.pid,signal.SIGTERM);proc.wait(timeout=10)
 subprocess.run([sys.executable,'/workspace/ep_l2_rtl_r3_metadata_cost/admit.py','release'],env=env,check=True)
sys.exit(1 if reason else rc)
