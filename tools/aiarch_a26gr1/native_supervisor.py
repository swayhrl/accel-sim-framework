"""One shared-lock native sequence, bounded resources; no profiling utilities."""
import fcntl,json,os,pathlib,signal,subprocess,time
from control import ROOT,WORK,state,save,check
assert json.loads((ROOT/'environment_qualified.json').read_text())['status']=='PASS'
lockpath=pathlib.Path('/data/c16/locks/c16_gpu_campaign.lock');assert lockpath.is_file();lock=lockpath.open('r+')
try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:
 (ROOT/'native_supervisor_receipt.json').write_text(json.dumps({'status':'GPU_LOCK_DEFERRED','native_steps':0})+'\n');raise SystemExit(75)
s=state();start=time.monotonic();remaining=7200-s['prior_gpu_lock_seconds']-s['new_gpu_lock_seconds'];deadline=start+remaining-20
peak_rss=0;peak_gpu=0;max_running=0;receipts=[];samples=[];terminal='PARTIAL'
env=os.environ.copy();env.update(A26R_GPU_LOCK_HELD='1',CUDA_VISIBLE_DEVICES='0',OMP_THREAD_LIMIT='16',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',TORCH_HOME=str(ROOT/'cache/torch'),TORCH_EXTENSIONS_DIR=str(ROOT/'build/torch_extensions'),XDG_CACHE_HOME=str(ROOT/'cache'),TMPDIR=str(ROOT/'tmp'),PIP_CACHE_DIR=str(ROOT/'pip_cache'),MAX_JOBS='4')
py=str(ROOT/'venv/bin/python');script=str(WORK/'tools/aiarch_a26gr1/native_runner.py')
try:
 for arm in ['host_wall','gpu_wall','host_diag']:
  if arm=='host_diag':assert json.loads((ROOT/'native/host_wall/functional_quality.json').read_text())['status']=='REAL_EARLY_FUNCTIONAL_PASS'
  out=ROOT/(arm+'_native.log');t=time.monotonic();last_step=205
  with out.open('wb') as f:
   child=subprocess.Popen([py,'-B',script,'--arm',arm,'--last-step',str(last_step)],cwd=WORK,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
   try:
    while child.poll() is None:
     check()
     if time.monotonic()>=deadline:raise RuntimeError('GPU_LOCK_CUMULATIVE_BUDGET_STOP')
     rss=0;running=0;own_pids=set()
     for p in pathlib.Path('/proc').iterdir():
      if not p.name.isdigit():continue
      try:
       st=p.joinpath('stat').read_text().split()
       if int(st[4])!=child.pid:continue
       own_pids.add(int(p.name));fields=dict(x.split(':',1) for x in p.joinpath('status').read_text().splitlines() if ':' in x);rss+=int(fields.get('VmRSS','0 kB').split()[0])*1024
       for tid in p.joinpath('task').iterdir():
        try:running+=tid.joinpath('stat').read_text().split()[2]=='R'
        except OSError:pass
      except (OSError,ValueError):continue
     peak_rss=max(peak_rss,rss);max_running=max(max_running,running)
     if rss>48*1024**3-512*1024**2:raise RuntimeError('TASK_RAM_CAP_STOP')
     if running+1>24:raise RuntimeError('EFFECTIVE_CPU_THREADS_CAP_STOP')
     n=subprocess.run(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5);gpu=0
     for line in n.stdout.splitlines():
      fields=line.split(',')
      if len(fields)==2 and fields[0].strip().isdigit() and fields[1].strip().isdigit() and int(fields[0]) in own_pids:gpu+=int(fields[1])
     peak_gpu=max(peak_gpu,gpu)
     if gpu>14*1024:raise RuntimeError('TASK_VRAM_CAP_STOP')
     samples.append({'arm':arm,'lock_elapsed_seconds':time.monotonic()-start,'rss_bytes':rss,'effective_running_threads':running,'gpu_process_mib':gpu})
     if len(samples)%10==0:(ROOT/'native_resource_samples.json').write_text(json.dumps(samples,indent=2)+'\n')
     time.sleep(.5)
   except BaseException:
    if child.poll() is None:os.killpg(child.pid,signal.SIGTERM);time.sleep(1)
    if child.poll() is None:os.killpg(child.pid,signal.SIGKILL)
    child.wait();raise
  receipt={'arm':arm,'returncode':child.returncode,'wall_seconds':time.monotonic()-t,'reached_step':last_step if (ROOT/'native'/arm/'completed.json').exists() else None};receipts.append(receipt)
  (ROOT/'native_arm_receipts.json').write_text(json.dumps(receipts,indent=2)+'\n');print('NATIVE_ARM_RETURN',arm,child.returncode,round(receipt['wall_seconds'],1),flush=True)
  if child.returncode:
   text=out.read_text(errors='replace')
   if arm=='gpu_wall' and ('CUDA out of memory' in text or 'OutOfMemoryError' in text):receipt['capacity_only']='CAPACITY_NO_TIMING_BASELINE';continue
   raise RuntimeError('NATIVE_ARM_FAILED '+arm)
 terminal='PASS_EARLY_ONLY'
finally:
 held=time.monotonic()-start;s=state();s['new_gpu_lock_seconds']+=held;save(s);fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
 (ROOT/'native_resource_samples.json').write_text(json.dumps(samples,indent=2)+'\n')
 (ROOT/'native_supervisor_receipt.json').write_text(json.dumps({'status':terminal,'arms':receipts,'held_lock_seconds':held,'gpu_lock_cumulative_seconds':s['prior_gpu_lock_seconds']+s['new_gpu_lock_seconds'],'gpu_peak_sampled_mib':peak_gpu,'sampling_interval_seconds':.5,'sampling_peak_limit':'discrete process-memory samples; Torch allocator capped at 13GiB with 1GiB context margin','host_process_tree_peak_rss_bytes':peak_rss,'effective_running_threads_sampled_max':max_running,'scientific_gpu_device':'same node109 RTX4080','all_gpu_actions_inside_nonblocking_shared_lock':True,'not_run':['200k full training','late fabricated states','NCU','NSYS','NVBit','simulator','SM quota sweep','new mechanism']},indent=2)+'\n')
 print('NATIVE_SHARED_LOCK_RELEASED',round(held,1),terminal,flush=True)
