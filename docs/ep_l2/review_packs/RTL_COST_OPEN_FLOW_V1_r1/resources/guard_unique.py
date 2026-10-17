import argparse,subprocess,sys,os,json,time,signal
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--memory-gib',default=2,type=int);p.add_argument('--output-mib',default=16,type=int);p.add_argument('--timeout',default=600,type=int);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args();assert a.command and a.command[0]!='--'
env=os.environ.copy();env.update(LANE2_MEM_GIB=str(a.memory_gib),LANE2_OUTPUT_MIB=str(a.output_mib),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
root=Path(os.environ.get('LANE2_MONITOR_ROOT','/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_OPEN_FLOW_V1_lane2_r1'))
def size():return sum(x.stat().st_size for x in root.rglob('*') if x.is_file())
subprocess.run([sys.executable,'/workspace/ep_l2_rtl_cost_open_flow_v1/admit.py'],env=env,check=True)
proc=None;initial=size();start=time.time();reason=None;peak_rss=0
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
  if size()-initial>a.output_mib*2**20:reason='EDA_PHASE_OUTPUT_CAP'
  if st.f_bavail*st.f_frsize<48*2**30 or sh.f_bavail*sh.f_frsize<40*2**30:reason='DISK_SAFETY_FLOOR'
  if reason:
   os.killpg(proc.pid,signal.SIGTERM);proc.wait(timeout=10);break
  time.sleep(0.5)
 rc=proc.wait();print(json.dumps({'command':a.command,'rc':rc,'resource_stop':reason,'elapsed_seconds':time.time()-start,'new_artifact_bytes':size()-initial,'sampled_peak_group_rss_bytes':peak_rss}),flush=True)
finally:
 if proc is not None and proc.poll() is None:os.killpg(proc.pid,signal.SIGTERM);proc.wait(timeout=10)
 subprocess.run([sys.executable,'/workspace/ep_l2_rtl_cost_open_flow_v1/admit.py','release'],env=env,check=True)
sys.exit(1 if reason else rc)
