"""Original source builds under nonblocking shared lock before any CUDA query."""
import fcntl,json,os,pathlib,signal,subprocess,time
from control import ROOT,state,save,check,allocated
lockpath=pathlib.Path('/data/c16/locks/c16_gpu_campaign.lock');assert lockpath.is_file();lock=lockpath.open('r+')
try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:
 (ROOT/'build_and_thread_status.json').write_text(json.dumps({'status':'GPU_LOCK_DEFERRED','cuda_import_or_operation':False})+'\n');raise SystemExit(75)
start=time.monotonic();s=state();remaining=7200-s['prior_gpu_lock_seconds']-s['new_gpu_lock_seconds'];deadline=time.monotonic()+remaining-20
receipts=[];status='FAIL'
env=os.environ.copy();env.update(PATH=str(ROOT/'venv/bin')+os.pathsep+env['PATH'],TMPDIR=str(ROOT/'tmp'),TORCH_EXTENSIONS_DIR=str(ROOT/'build/torch_extensions'),CUDA_HOME='/usr/local/cuda',TORCH_CUDA_ARCH_LIST='8.9',MAX_JOBS='4',OMP_THREAD_LIMIT='16',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='0',PIP_CACHE_DIR=str(ROOT/'pip_cache'))
py=str(ROOT/'venv/bin/python');rss_peak=0;gpu_peak_mib=0
commands=[('pycolmap',[py,'-B','-m','pip','install','--no-index','--no-deps','--no-cache-dir','--no-build-isolation','--no-compile','.']),('cpu_adam',[py,'-B','setup.py','build_ext','--inplace']),('fused_ssim',[py,'-B','-m','pip','install','--no-index','--no-deps','--no-cache-dir','--no-build-isolation','--no-compile','.']),('gsscale',[py,'-B','-m','pip','install','--no-index','--no-deps','--no-cache-dir','--no-build-isolation','--no-compile','.'])]
try:
 for name,args in commands:
  folder=ROOT/'software_sources'/('gsscale/cpu_adam' if name=='cpu_adam' else name);log=ROOT/(name+'_build.log');t=time.monotonic()
  check()
  with log.open('wb') as out:
   child=subprocess.Popen(args,cwd=folder,env=env,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
   try:
    while child.poll() is None:
     check()
     if time.monotonic()>=deadline:raise RuntimeError('GPU_LOCK_CUMULATIVE_DEADLINE')
     rss=0
     for p in pathlib.Path('/proc').iterdir():
      if not p.name.isdigit():continue
      try:
       st=p.joinpath('stat').read_text().split()
       if int(st[4])!=child.pid:continue
       fields=dict(x.split(':',1) for x in p.joinpath('status').read_text().splitlines() if ':' in x);rss+=int(fields.get('VmRSS','0 kB').split()[0])*1024
      except (OSError,ValueError):continue
     rss_peak=max(rss_peak,rss)
     if rss>48*1024**3-512*1024**2:raise RuntimeError('HOST_RAM_CAP')
     n=subprocess.run(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5)
     for line in n.stdout.splitlines():
      fields=line.split(',')
      if len(fields)==2 and fields[1].strip().isdigit():gpu_peak_mib=max(gpu_peak_mib,int(fields[1].strip()))
     if gpu_peak_mib>14*1024:raise RuntimeError('GPU_VRAM_CAP')
     time.sleep(1)
   except BaseException:
    if child.poll() is None:os.killpg(child.pid,signal.SIGTERM);time.sleep(1)
    if child.poll() is None:os.killpg(child.pid,signal.SIGKILL)
    child.wait();raise
  receipts.append({'source_name':name,'returncode':child.returncode,'wall_seconds':time.monotonic()-t,'original_source_build':True})
  (ROOT/'build_receipts.json').write_text(json.dumps(receipts,indent=2)+'\n');print('SOURCE_BUILD_RESULT',name,child.returncode,round(time.monotonic()-t,1),flush=True)
  if child.returncode:raise RuntimeError('SOURCE_BUILD_FAILED '+name)
 status='PASS'
finally:
 held=time.monotonic()-start;s=state();s['new_gpu_lock_seconds']+=held;save(s);fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
 (ROOT/'build_and_thread_status.json').write_text(json.dumps({'build_status':status,'source_builds':receipts,'gpu_lock_this_stage_seconds':held,'gpu_peak_sampled_mib':gpu_peak_mib,'gpu_sampling_interval_seconds':1,'process_tree_peak_rss_bytes':rss_peak,'cpu_worker_compile_max_jobs':4,'cpu_adam_thread_qualification':'PENDING_ACTUAL_CPU_CANARY','toolkit_or_driver_upgraded':False},indent=2)+'\n')
 print('BUILD_LOCK_RELEASED',round(held,1),'STATUS',status,flush=True)
