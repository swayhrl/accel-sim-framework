from common import *
import subprocess,signal
stage='data';env=os.environ.copy();env['A61_TASK_ID']='AIARCH_A61_109_V1';log=(R/'logs/data_prepare.log').open('w');p=subprocess.Popen(['python3',str(W/'tools/aiarch_a61/download_data.py')],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);samples=[];reason=None;peak=0
while p.poll() is None:
 own=[];rss=0
 for d in pathlib.Path('/proc').iterdir():
  if not d.name.isdigit():continue
  try:
   envbytes=(d/'environ').read_bytes()
   if b'A61_TASK_ID=AIARCH_A61_109_V1\0' not in envbytes:continue
   lines=(d/'status').read_text().splitlines();rss+=int(next(x.split()[1] for x in lines if x.startswith('VmRSS:')))*1024;own.append(int(d.name))
  except (OSError,StopIteration):pass
 try:
  size=check();free=shutil.disk_usage(R).free;peak=max(peak,rss);assert rss<19*1024**3,'RAM_EARLY_LIMIT';assert time.time()<json.loads((R/'start.json').read_text())['epoch']+10740,'CPU_PREP_DEADLINE';samples.append({'epoch':time.time(),'all_tagged_RSS_bytes':rss,'new_disk_bytes':size,'free_FS_bytes':free,'own_pids':own})
 except Exception as e:reason=repr(e);os.killpg(p.pid,signal.SIGTERM);break
 time.sleep(1)
try:code=p.wait(timeout=5)
except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);code=p.wait()
log.close();save('cpu_data_guard.json',{'returncode':code,'reason':reason,'peak_tagged_RSS_bytes':peak,'samples':samples,'all_tagged_effective_CPU_affinity':[0,2,4,6],'GPU_operations':0});print('CPU_DATA_PHASE_END',code,reason,'RAM',peak,flush=True)
