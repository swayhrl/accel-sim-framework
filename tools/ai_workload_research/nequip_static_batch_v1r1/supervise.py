"""V1R1 resource supervisor. CPU mode never opens CUDA; GPU mode holds shared flock."""
import pathlib,subprocess,os,sys,time,signal,json,fcntl,re,datetime,resource
root=pathlib.Path(os.environ['TASK_DATA']);old=pathlib.Path(os.environ['OLD_TASK_DATA']);mode=sys.argv[1];cmd=sys.argv[2:];start=time.monotonic();lock=None
is_gpu=mode.startswith('gpu')
previous_gpu_seconds=sum(json.loads(p.read_text()).get('seconds',0) for p in (root/'raw').glob('RESOURCE_gpu_attempt*.json'))
route=subprocess.check_output(['ip','route','get','1.1.1.1'],text=True).split();iface=route[route.index('dev')+1];counter=pathlib.Path('/sys/class/net')/iface/'statistics/rx_bytes';before=int(counter.read_text());prior_file=root/'raw/NETWORK_LEDGER.json';prior=json.loads(prior_file.read_text())['new_accounted_bytes'] if prior_file.exists() else 1024*1024
receipt={'mode':mode,'command':cmd,'utc_start':datetime.datetime.now(datetime.timezone.utc).isoformat(),'peak_aggregate_rss_bytes':0,'peak_gpu_mib':0,'network_baseline_rx':before,'prior_new_accounted_bytes':prior,'new_limit_bytes':5256821765,'v1_accounted_bytes':3333112827,'gpu_lock_acquired':False,'sample_interval_seconds':1,'previous_gpu_lock_seconds':previous_gpu_seconds};file=root/'raw'/('RESOURCE_'+mode+'.json')
def save():
 receipt['seconds']=time.monotonic()-start;file.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');prior_file.write_text(json.dumps({'new_accounted_bytes':receipt.get('new_accounted_bytes',prior),'v1_accounted_bytes':3333112827,'cumulative_accounted_bytes':3333112827+receipt.get('new_accounted_bytes',prior),'method':'1MiB pre-monitor allowance + whole eno1 RX deltas across supervised phases, including TLS/SSH/other traffic; no reset across phases'},indent=2)+'\n')
if is_gpu:
 lock=open('/data/c16/locks/c16_gpu_campaign.lock','r+')
 try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:receipt['status']='RESOURCE_DEFERRED';save();sys.exit(75)
 receipt['gpu_lock_acquired']=True
 if subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip():receipt['status']='RESOURCE_DEFERRED_EXTERNAL_GPU_USER';fcntl.flock(lock,fcntl.LOCK_UN);lock.close();save();sys.exit(75)
 os.environ['TASK_GPU_LOCK_START_MONOTONIC']=str(start)
else:os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='8',MKL_NUM_THREADS='8',OPENBLAS_NUM_THREADS='8',MAX_JOBS='8',CMAKE_BUILD_PARALLEL_LEVEL='8',RAYON_NUM_THREADS='8',UV_CONCURRENT_BUILDS='1',UV_CONCURRENT_DOWNLOADS='8')
proc=subprocess.Popen(cmd,start_new_session=True);reason=None;tick=0
try:
 while proc.poll() is None:
  table=[]
  for p in pathlib.Path('/proc').iterdir():
   if p.name.isdigit():
    try:s=(p/'stat').read_text().rsplit(')',1)[1].split();table.append((int(p.name),int(s[1]),int(s[21])*os.sysconf('SC_PAGE_SIZE')))
    except (OSError,ValueError,IndexError):pass
  pids={proc.pid}
  for _ in range(12):
   n=len(pids);pids.update(pid for pid,ppid,_ in table if ppid in pids)
   if len(pids)==n:break
  rss=sum(v for pid,_,v in table if pid in pids);receipt['peak_aggregate_rss_bytes']=max(receipt['peak_aggregate_rss_bytes'],rss)
  if rss>32*2**30:reason='BUDGET_STOP_RAM'
  used=prior+max(0,int(counter.read_text())-before);receipt['new_accounted_bytes']=used
  if used>=5256821765-64*2**20:reason='BUDGET_STOP_NETWORK_SAFETY_MARGIN'
  if is_gpu:
   if time.monotonic()-start+previous_gpu_seconds>=5400:reason='BUDGET_STOP_GPU_LOCK'
   q=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True);gpu=0;external=[]
   for line in q.splitlines():
    pid,mem=[int(x.strip()) for x in line.split(',')]
    if pid in pids:gpu+=mem
    else:external.append(pid)
   receipt['peak_gpu_mib']=max(receipt['peak_gpu_mib'],gpu)
   if gpu>12288:reason='BUDGET_STOP_GPU_MEMORY'
   if external:reason='EXTERNAL_GPU_USER_STOP';receipt['external_gpu_pids']=external
  if tick%10==0:
   size=sum(int(subprocess.check_output(['du','-sb',str(p)],text=True).split()[0]) for p in [old,root]);free=os.statvfs(root).f_bavail*os.statvfs(root).f_frsize;raw=sum(p.stat().st_size for p in (root/'raw').rglob('*') if p.is_file());receipt.update(cumulative_directory_bytes=size,free_disk_bytes=free,raw_log_bytes=raw)
   if size>25*2**30:reason='BUDGET_STOP_DISK'
   if free<8*2**30:reason='BUDGET_STOP_FREE_DISK'
   if raw>256*2**20:reason='BUDGET_STOP_RAW'
   save()
  if reason:
   os.killpg(proc.pid,signal.SIGTERM)
   try:proc.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
   break
  tick+=1;time.sleep(1)
finally:
 try:
  os.killpg(proc.pid,signal.SIGTERM);time.sleep(1)
  try:os.killpg(proc.pid,signal.SIGKILL)
  except ProcessLookupError:pass
 except ProcessLookupError:pass
 receipt['child_maxrss_bytes']=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024
 receipt['new_accounted_bytes']=prior+max(0,int(counter.read_text())-before);receipt.update(status=reason or ('PASS' if proc.returncode==0 else 'CHILD_STOP'),returncode=proc.returncode,utc_end=datetime.datetime.now(datetime.timezone.utc).isoformat())
 if lock:fcntl.flock(lock,fcntl.LOCK_UN);lock.close();receipt['gpu_lock_released']=True
 save()
print(json.dumps(receipt),flush=True);sys.exit(0 if receipt['status']=='PASS' else 1)
