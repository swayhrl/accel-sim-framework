"""CPU-only child resource guard; never touches CUDA, Torch, GPU or its lock."""
from evidence import *
import subprocess,signal,sys
target=sys.argv[1] if len(sys.argv)>1 else 'probe';assert target in ['probe','paper'];tag=sys.argv[2] if len(sys.argv)>2 else target;assert tag in ['probe','paper','paper_retry1'];start=time.monotonic();samples=[];p=subprocess.Popen(['python3',str(W/'tools/aiarch_a59_license'/(target+'.py'))],stdout=(R/'logs'/(tag+'.log')).open('w'),stderr=subprocess.STDOUT,start_new_session=True);reason=None;peak=0
while p.poll() is None:
 try:
  rss=0
  for pid in [p.pid,os.getpid()]:
   lines=pathlib.Path(f'/proc/{pid}/status').read_text().splitlines();rss+=int(next(x.split()[1] for x in lines if x.startswith('VmRSS:')))*1024
  disk=check();peak=max(peak,rss);samples.append({'epoch':time.time(),'RSS_parent_child_bytes':rss,'new_disk_bytes':disk});assert rss<240*1024**2,'RAM_MARGIN'
 except (OSError,StopIteration):pass
 except Exception as e:reason=repr(e);os.killpg(p.pid,signal.SIGTERM);break
 time.sleep(.2)
try:code=p.wait(timeout=3)
except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);code=p.wait()
x={'returncode':code,'stop_reason':reason,'CPU_affinity':sorted(os.sched_getaffinity(0)),'peak_sampled_parent_child_RSS_bytes':peak,'seconds':time.monotonic()-start,'RLIMIT_AS_each_bytes':256*1024**2,'samples':samples,'CUDA_GPU_lock_operations':0};(R/'raw'/(tag+'_resource_receipt.json')).write_text(json.dumps(x,indent=2));print(json.dumps({k:v for k,v in x.items() if k!='samples'}),flush=True)
