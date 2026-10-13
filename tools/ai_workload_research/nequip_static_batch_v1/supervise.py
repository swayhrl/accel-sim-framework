import os,sys,time,json,pathlib,subprocess,signal,fcntl,datetime
root=pathlib.Path(os.environ['TASK_DATA']); mode=sys.argv[1];cmd=sys.argv[2:];start=time.monotonic();lock=None;receipt={'mode':mode,'command':cmd,'utc_start':datetime.datetime.now(datetime.timezone.utc).isoformat(),'peak_rss_bytes':0,'peak_gpu_mib':0,'monitor_interval_seconds':1,'gpu_lock_acquired':False}
def save():
 (root/'raw'/('supervisor_'+mode+'.json')).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
if mode=='gpu':
 lock=open('/data/c16/locks/c16_gpu_campaign.lock','r+')
 try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:receipt['status']='RESOURCE_DEFERRED';save();sys.exit(75)
 receipt['gpu_lock_acquired']=True;save()
 q=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True)
 if q.strip():receipt['status']='RESOURCE_DEFERRED_EXTERNAL_GPU_USER';save();sys.exit(75)
 os.environ['TASK_GPU_LOCK_START_MONOTONIC']=str(start)
os.environ.update(RAYON_NUM_THREADS='8',UV_CONCURRENT_BUILDS='1',UV_CONCURRENT_INSTALLS='8',UV_CONCURRENT_DOWNLOADS='8',MAX_JOBS='8',CMAKE_BUILD_PARALLEL_LEVEL='8',OMP_NUM_THREADS='8',MKL_NUM_THREADS='8',OPENBLAS_NUM_THREADS='8')
proc=subprocess.Popen(cmd,start_new_session=True);reason=None;tick=0
try:
 while proc.poll() is None:
  elapsed=time.monotonic()-start
  if mode=='gpu' and elapsed>=5400:reason='BUDGET_STOP_GPU_LOCK_90MIN'
  pids={proc.pid};rss=0
  table=[]
  for p in pathlib.Path('/proc').iterdir():
   if p.name.isdigit():
    try:
     s=(p/'stat').read_text().rsplit(')',1)[1].split();table.append((int(p.name),int(s[1]),int(s[21])*os.sysconf('SC_PAGE_SIZE')))
    except (OSError,ValueError,IndexError):pass
  for _ in range(8):
   old=len(pids);pids.update(pid for pid,ppid,_ in table if ppid in pids)
   if old==len(pids):break
  rss=sum(mem for pid,_,mem in table if pid in pids);receipt['peak_rss_bytes']=max(receipt['peak_rss_bytes'],rss)
  if rss>32*2**30:reason='BUDGET_STOP_RAM_32GIB'
  if mode=='gpu':
   q=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True)
   gpu=0;external=[]
   for l in q.splitlines():
    pid,mem=l.split(',');pid=int(pid);mem=int(mem)
    if pid in pids:gpu+=mem
    else:external.append(pid)
   receipt['peak_gpu_mib']=max(receipt['peak_gpu_mib'],gpu)
   if gpu>12288:reason='BUDGET_STOP_GPU_12GIB'
   if external:reason='TIMING_CONTAMINATED_EXTERNAL_GPU_USER';receipt['external_gpu_pids']=external
  if tick%10==0:
   disk=int(subprocess.check_output(['du','-sb',str(root)],text=True).split()[0]);raw=int(subprocess.check_output(['du','-sb',str(root/'raw')],text=True).split()[0]);free=os.statvfs(root).f_bavail*os.statvfs(root).f_frsize
   receipt.update(incremental_disk_bytes=disk,raw_log_bytes=raw,free_disk_bytes=free)
   if disk>25*2**30:reason='BUDGET_STOP_DISK_25GIB'
   if raw>256*2**20:reason='BUDGET_STOP_RAW_256MIB'
   if free<8*2**30:reason='BUDGET_STOP_FREE_DISK_8GIB'
   if mode=='download':
    wheels=sum(p.stat().st_size for p in (root/'wheels').rglob('*') if p.is_file());receipt['wheels_bytes']=wheels
    if wheels+256*2**20>8*2**30:reason='BUDGET_STOP_DOWNLOAD_8GIB'
   receipt['elapsed_seconds']=elapsed;save()
  if reason:
   os.killpg(proc.pid,signal.SIGTERM)
   try:proc.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
   break
  tick+=1;time.sleep(1)
finally:
 # End any descendants still in our private process group before releasing the lock.
 try:
  os.killpg(proc.pid,signal.SIGTERM);time.sleep(1)
  try:os.killpg(proc.pid,signal.SIGKILL)
  except ProcessLookupError:pass
 except ProcessLookupError:pass
 receipt.update(status=reason or ('PASS' if proc.returncode==0 else 'CHILD_FAILED'),returncode=proc.returncode,elapsed_seconds=time.monotonic()-start,utc_end=datetime.datetime.now(datetime.timezone.utc).isoformat())
 if lock:fcntl.flock(lock,fcntl.LOCK_UN);lock.close();receipt['gpu_lock_released']=True
 save()
print(json.dumps(receipt),flush=True)
sys.exit(0 if receipt['status']=='PASS' else 1)
