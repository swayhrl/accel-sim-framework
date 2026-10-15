"""Persistent original GPU lease and total budgets; one full build invocation only."""
import os,pathlib,json,fcntl,subprocess,signal,time,shutil,stat
ROOT=pathlib.Path('/data/c16/aiarch_a50g_glove100_default_full_109_v1');OLD=pathlib.Path('/data/c16/aiarch_a47_cagra_glove100_109_v1');WORK=pathlib.Path(__file__).resolve().parents[2];LOCK=pathlib.Path('/data/c16/locks/c16_gpu_campaign.lock');os.sched_setaffinity(0,[0,2,4,6])
fd=None;start=None;child=None;reason=None;stages=[];samples=[];peak_rss=0;peak_gpu=0;peak_disk=0

def disk(full=True):
 if full:return sum(p.stat().st_blocks*512 for root in [ROOT,WORK] for p in root.rglob('*') if p.is_file())
 return sum(p.stat().st_blocks*512 for root in [ROOT/'cache',ROOT/'tmp',ROOT/'logs',ROOT/'raw'] for p in root.rglob('*') if p.is_file())+sum(p.stat().st_blocks*512 for p in ROOT.glob('*') if p.is_file())+2*1024**2

def apps():
 out=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True,timeout=10)
 return [(int(x.split(',')[0]),int(x.split(',')[1])) for x in out.splitlines() if x.strip()]
try:
 assert json.loads((ROOT/'preflight.json').read_text())['status']=='PASS';assert time.time()-json.loads((ROOT/'start.json').read_text())['epoch']<1800,'CPU_PREPARATION_LIMIT';assert not apps(),'EXTERNAL_GPU_TASK'
 assert disk()<2*1024**3 and shutil.disk_usage(ROOT).free>=64*1024**3
 ls=LOCK.stat();assert stat.S_ISREG(ls.st_mode) and not LOCK.is_symlink();fd=os.open(LOCK,os.O_RDWR|os.O_NOFOLLOW);assert os.fstat(fd).st_ino==ls.st_ino
 try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:reason='GPU_LOCK_DEFERRED';raise RuntimeError(reason)
 start=time.monotonic();deadline=start+2700;assert not apps(),'EXTERNAL_GPU_TASK_AFTER_LOCK'
 env=os.environ.copy();env.update(A50G_GPU_LOCK_HELD='1',A50G_OUTPUT=str(ROOT),A50G_DEADLINE=str(deadline),CUDA_VISIBLE_DEVICES='0',HOME=str(ROOT/'cache/home'),TMPDIR=str(ROOT/'tmp'),XDG_CACHE_HOME=str(ROOT/'cache'),CUPY_CACHE_DIR=str(ROOT/'cache/cupy'),CUDA_CACHE_PATH=str(ROOT/'cache/driver'),PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',OMP_NUM_THREADS='1',OMP_THREAD_LIMIT='4',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
 for key in ['CUDA_HOME','CUDA_PATH','PYTHONPATH','LD_LIBRARY_PATH']:env.pop(key,None)
 for mode,args in [('build_qualify',[]),('measure',['0']),('measure',['1']),('measure',['2'])]:
  if mode=='measure':assert json.loads((ROOT/'report_quality.json').read_text())['status']=='PASS'
  tag=mode+('_'+args[0] if args else '');t=time.monotonic();log=(ROOT/'logs'/f'{tag}.log').open('w');child=subprocess.Popen([str(OLD/'venv/bin/python'),str(WORK/'tools/aiarch_a50g/native.py'),mode,*args],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  # No heavy CPU/hash/recursive old-environment scan during formal timing.
  while child.poll() is None:
   current=apps()
   if any(pid!=child.pid for pid,_ in current):reason='EXTERNAL_GPU_TASK';break
   gpu=sum(x for _,x in current);peak_gpu=max(peak_gpu,gpu);rss=0;run=0
   for pid in [child.pid,os.getpid()]:
    try:
     text=pathlib.Path(f'/proc/{pid}/status').read_text();rss+=int(next(x.split()[1] for x in text.splitlines() if x.startswith('VmRSS:')))*1024
     for tid in pathlib.Path(f'/proc/{pid}/task').iterdir():
      try:run+=tid.joinpath('stat').read_text().rsplit(')',1)[1].split()[0]=='R'
      except OSError:pass
    except (OSError,StopIteration):pass
   peak_rss=max(peak_rss,rss);allocated=disk(full=mode!='measure');peak_disk=max(peak_disk,allocated);free=shutil.disk_usage(ROOT).free
   if gpu>11520:reason='BUDGET_STOP_VRAM_EARLY_MARGIN'
   if rss>int(7.5*1024**3):reason='BUDGET_STOP_RAM_EARLY_MARGIN'
   if allocated>int(1.875*1024**3) or free<64*1024**3:reason='BUDGET_STOP_DISK_EARLY_MARGIN'
   if sum(p.stat().st_size for p in (ROOT/'raw').rglob('*') if p.is_file())>64*1024**2:reason='BUDGET_STOP_RAW'
   if time.monotonic()>deadline-15:reason='BUDGET_STOP_TIME'
   if LOCK.stat().st_ino!=ls.st_ino:reason='SHARED_LOCK_IDENTITY_FAILURE'
   meta=subprocess.check_output(['nvidia-smi','--query-gpu=temperature.gpu,utilization.gpu,clocks.sm,clocks.mem,power.draw','--format=csv,noheader,nounits'],text=True,timeout=10).strip()
   samples.append({'stage':tag,'monotonic':time.monotonic(),'gpu_MiB':gpu,'tree_RSS_bytes':rss,'running_threads':run,'allocated_new_bytes':allocated,'free_bytes':free,'temperature_util_SMclock_memclock_power_csv':meta})
   if reason:break
   time.sleep(.25)
  if reason and child.poll() is None:
   os.killpg(child.pid,signal.SIGTERM)
   try:child.wait(timeout=4)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
  code=child.wait();log.close();stages.append({'stage':tag,'returncode':code,'signal':-code if code<0 else None,'budget_elapsed_seconds':time.monotonic()-t});print('STAGE_EXIT',tag,code,stages[-1]['budget_elapsed_seconds'],flush=True)
  if reason:break
  if code!=0:
   reason='QUALITY_NO_GO' if code==20 else 'NATIVE_STAGE_FAILURE';break
except Exception as e:reason=reason or 'PREFLIGHT_OR_WRAPPER_FAILURE '+repr(e)
finally:
 if child is not None and child.poll() is None:
  os.killpg(child.pid,signal.SIGTERM)
  try:child.wait(timeout=4)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
 held=0 if start is None else time.monotonic()-start
 if fd is not None:
  if start is not None:fcntl.flock(fd,fcntl.LOCK_UN)
  os.close(fd)
 receipt={'execution_status':'PASS_COMPLETE_NATIVE' if reason is None else 'STOP','reason':reason,'GPU_lock_seconds_cumulative':held,'stages':stages,'peak_GPU_MiB_sampled':peak_gpu,'peak_tree_RSS_bytes_sampled':peak_rss,'peak_new_allocated_bytes_sampled':peak_disk,'samples':samples,'sampling_limits':'quarter-second requested plus metadata-command latency; instantaneous peaks may be missed; early margin thresholds used, no large explicit pool','CPU_affinity':[0,2,4,6],'all_own_GPU_children_ended':child is None or child.poll() is not None,'shared_lock_released':True,'new_download_install_core_compile':0,'no_next_goal':True};(ROOT/'supervisor_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('SUPERVISOR_STOP',receipt['execution_status'],reason,'LOCK',held,'RAM',peak_rss,'VRAM',peak_gpu,'DISK',peak_disk,flush=True)
