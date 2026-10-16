"""Original shared nonblocking GPU lease, cumulative guards and own-child cleanup."""
from common import *
import subprocess,signal,stat,sys
LOCK=pathlib.Path('/data/c16/locks/c16_gpu_campaign.lock');old=json.loads((R/'gpu_ledger.json').read_text()) if (R/'gpu_ledger.json').exists() else {'cumulative_seconds':0,'attempts':[]};prior=old['cumulative_seconds'];assert prior<1760,'NO_REMAINING_GPU_BUDGET';fd=None;start=None;child=None;reason=None;stages=[];samples=[];peak=0;peakgpu=0;baseline=check();attempt=len(old['attempts'])
def apps():
 s=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True,timeout=8);return [(int(x.split(',')[0]),int(x.split(',')[1])) for x in s.splitlines() if x.strip()]
def group_pids(pgid):
 out=[]
 for d in pathlib.Path('/proc').iterdir():
  if not d.name.isdigit():continue
  try:
   v=(d/'stat').read_text().rsplit(')',1)[1].split()
   if int(v[2])==pgid:out.append(int(d.name))
  except (OSError,ValueError,IndexError):pass
 return out
try:
 assert json.loads((R/'environment_prepared.json').read_text())['status'].startswith('PASS');assert json.loads((R/'graph_cpu_identity.json').read_text())['status'].startswith('PASS');assert json.loads((R/'data_extraction.json').read_text())['status']=='PASS';assert time.time()-json.loads((R/'start.json').read_text())['epoch']<=10800,'CPU_PREP_LIMIT'
 st=LOCK.stat();assert stat.S_ISREG(st.st_mode) and not LOCK.is_symlink();fd=os.open(LOCK,os.O_RDWR|os.O_NOFOLLOW);assert os.fstat(fd).st_ino==st.st_ino
 try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:reason='GPU_LOCK_DEFERRED';raise RuntimeError(reason)
 start=time.monotonic();deadline=start+(1800-prior);assert not apps(),'EXTERNAL_GPU_COMPUTE_TASK';device=subprocess.check_output(['nvidia-smi','--query-gpu=name,driver_version,memory.total,memory.free','--format=csv,noheader,nounits'],text=True,timeout=8).strip();save('gpu_admission_metadata.json',{'device':device,'prior_GPU_seconds':prior,'lock_inode':st.st_ino,'new_disk_before_GPU':baseline})
 env=os.environ.copy();env.update(A61_GPU_LOCK_HELD='1',A61_GPU_DEADLINE=str(deadline),CUDA_VISIBLE_DEVICES='0',A61_TASK_ID='AIARCH_A61_109_V1',DGLBACKEND='pytorch',HOME=str(R/'cache/home'),TMPDIR=str(R/'tmp'),XDG_CACHE_HOME=str(R/'cache'),TORCH_HOME=str(R/'cache/torch'),TORCHINDUCTOR_CACHE_DIR=str(R/'cache/inductor'),TRITON_CACHE_DIR=str(R/'cache/triton'),TORCH_EXTENSIONS_DIR=str(R/'cache/extensions'),CUDA_CACHE_PATH=str(R/'cache/driver'),PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',LD_LIBRARY_PATH='/data/c16/env/cpython-3.10.12/lib',OMP_NUM_THREADS='1',OMP_THREAD_LIMIT='4',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',TORCHINDUCTOR_COMPILE_THREADS='1',MAX_JOBS='4')
 for k in ['PYTHONPATH','CUDA_HOME','CUDA_PATH']:env.pop(k,None)
 for execution in range(2):
  eager=execution==1 or '--eager-only' in sys.argv;tag=f'native_attempt{attempt}_'+('eager' if eager else 'compile');log=(R/'logs'/(tag+'.log')).open('w');t=time.monotonic();child=subprocess.Popen([str(R/'venv/bin/python'),str(W/'tools/aiarch_a61/native.py'),*(['--eager-only'] if eager else [])],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);soft=False
  while child.poll() is None:
   current=apps();rss=0
   if any(pid!=child.pid for pid,_ in current):reason='EXTERNAL_OR_EXTRA_GPU_PROCESS';break
   gpu=sum(x for _,x in current);peakgpu=max(peakgpu,gpu)
   for pid in group_pids(child.pid)+[os.getpid()]:
    try:rss+=int(next(x.split()[1] for x in pathlib.Path(f'/proc/{pid}/status').read_text().splitlines() if x.startswith('VmRSS:')))*1024
    except (OSError,StopIteration):pass
   peak=max(peak,rss);phase=json.loads((R/'gpu_current_phase.json').read_text()) if (R/'gpu_current_phase.json').exists() else {};free=shutil.disk_usage(R).free
   if gpu>11520:reason='BUDGET_STOP_VRAM_MARGIN'
   if rss>19*1024**3:reason='BUDGET_STOP_RAM_MARGIN'
   if free<int(64.125*1024**3):reason='BUDGET_STOP_FREE_FS'
   if time.monotonic()>deadline-12:reason='BUDGET_STOP_GPU_TIME'
   if LOCK.stat().st_ino!=st.st_ino:reason='SHARED_LOCK_IDENTITY_FAILED'
   if phase.get('phase')=='COMPILE_CANARY' and time.monotonic()-phase['monotonic']>180 and not eager:soft=True;reason='COMPILE_SOFT_TIMEOUT_EAGER_RECOVERY'
   # No old asset hashes or environment scans during formal timing.
   growth=sum(p.stat().st_blocks*512 for root in [R/'cache',R/'tmp',R/'logs',R/'raw'] for p in root.rglob('*') if p.is_file() and not p.is_symlink());allocated_bound=baseline+growth+32*1024**2
   if allocated_bound>14*1024**3:reason='BUDGET_STOP_NEW_DISK_MARGIN'
   meta=subprocess.check_output(['nvidia-smi','--query-gpu=temperature.gpu,utilization.gpu,clocks.sm,clocks.mem,power.draw','--format=csv,noheader,nounits'],text=True,timeout=8).strip();samples.append({'monotonic':time.monotonic(),'phase':phase.get('phase'),'GPU_MiB':gpu,'tree_RSS_bytes':rss,'new_disk_conservative_bound_bytes':allocated_bound,'FS_free_bytes':free,'device_temp_util_SMclock_memclock_power_csv':meta})
   if reason:break
   time.sleep(.5)
  if child.poll() is None:
   os.killpg(child.pid,signal.SIGTERM)
   try:child.wait(timeout=4)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
  code=child.wait();log.close();stages.append({'tag':tag,'returncode':code,'seconds':time.monotonic()-t,'reason':reason,'eager':eager});print('GPU_CHILD_END',tag,code,reason,flush=True)
  if soft and execution==0:
   reason=None;continue
  if code!=0 and reason is None:reason='NATIVE_EXECUTION_FAILED_REQUIRES_EVIDENCE_INSPECTION'
  break
except Exception as e:reason=reason or repr(e)
finally:
 if child is not None and child.poll() is None:
  os.killpg(child.pid,signal.SIGTERM)
  try:child.wait(timeout=4)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
 held=0 if start is None else time.monotonic()-start
 if fd is not None:
  if start is not None:fcntl.flock(fd,fcntl.LOCK_UN)
  os.close(fd)
 rec={'status':'PASS_NATIVE_COMPLETE' if reason is None else 'STOP','reason':reason,'lock_seconds_this_attempt':held,'lock_seconds_cumulative':prior+held,'stages':stages,'peak_tree_RSS_bytes_sampled':peak,'peak_GPU_MiB_sampled':peakgpu,'samples':samples,'all_own_GPU_children_ended':child is None or child.poll() is not None,'shared_lock_released':True,'sampling_limit':'half-second plus NVML command latency, instantaneous peaks can be missed; allocator .70 and early margins used','no_future_GPU_task':True};old['cumulative_seconds']=prior+held;old['attempts'].append(rec);save('gpu_ledger.json',old);print('GPU_SUPERVISOR_STOP',rec['status'],reason,prior+held,peak,peakgpu,flush=True)
