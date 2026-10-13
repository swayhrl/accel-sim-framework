import os,pathlib,subprocess,time,json,fcntl,signal,sys,datetime,resource
root=pathlib.Path(os.environ['TASK_DATA']);mode=sys.argv[1];cmd=sys.argv[2:];start=time.monotonic();lock=None;r={'mode':mode,'command':cmd,'utc_start':datetime.datetime.now(datetime.timezone.utc).isoformat(),'peak_sampled_aggregate_rss_bytes':0,'peak_sampled_gpu_mib':0,'gpu_lock_acquired':False,'RAM_limit_bytes':12*2**30,'GPU_limit_mib':4096,'gpu_lock_limit_seconds':600,'new_disk_limit_bytes':512*2**20,'downloads':0,'installs':0,'CPU_workers_limit':4}
def save():(root/'raw'/('RESOURCE_'+mode+'.json')).write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
if mode=='gpu':
 lock=open('/data/c16/locks/c16_gpu_campaign.lock','r+')
 try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:r['status']='RESOURCE_DEFERRED';save();sys.exit(75)
 r['gpu_lock_acquired']=True
 if subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip():r['status']='RESOURCE_DEFERRED_EXTERNAL_GPU_TASK';fcntl.flock(lock,fcntl.LOCK_UN);lock.close();save();sys.exit(75)
 identity=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,compute_cap,driver_version','--format=csv,noheader'],text=True);r['GPU_identity']=identity
 if 'GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59' not in identity or '8.9' not in identity:r['status']='GPU_IDENTITY_STOP';fcntl.flock(lock,fcntl.LOCK_UN);lock.close();save();sys.exit(1)
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',MAX_JOBS='4',CMAKE_BUILD_PARALLEL_LEVEL='4',TORCHINDUCTOR_COMPILE_THREADS='4')
proc=subprocess.Popen(cmd,start_new_session=True);reason=None
try:
 while proc.poll() is None:
  table=[]
  for p in pathlib.Path('/proc').iterdir():
   if p.name.isdigit():
    try:s=(p/'stat').read_text().rsplit(')',1)[1].split();table.append((int(p.name),int(s[1]),int(s[21])*os.sysconf('SC_PAGE_SIZE')))
    except (OSError,ValueError,IndexError):pass
  pids={proc.pid}
  for _ in range(10):
   n=len(pids);pids.update(pid for pid,parent,_ in table if parent in pids)
   if len(pids)==n:break
  rss=sum(v for pid,_,v in table if pid in pids);r['peak_sampled_aggregate_rss_bytes']=max(r['peak_sampled_aggregate_rss_bytes'],rss)
  if rss>12*2**30:reason='BUDGET_STOP_RAM'
  if mode=='gpu':
   if time.monotonic()-start>=600:reason='BUDGET_STOP_GPU_LOCK'
   out=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True);memory=0
   for line in out.splitlines():
    pid,mem=[int(x.strip()) for x in line.split(',')]
    if pid in pids:memory+=mem
    else:reason='EXTERNAL_GPU_TASK_STOP';r['external_gpu_pid']=pid
   r['peak_sampled_gpu_mib']=max(r['peak_sampled_gpu_mib'],memory)
   if memory>4096:reason='BUDGET_STOP_GPU_MEMORY'
  size=int(subprocess.check_output(['du','-sb',str(root)],text=True).split()[0]);r['task_directory_bytes']=size;r['seconds']=time.monotonic()-start
  if size>512*2**20:reason='BUDGET_STOP_DISK'
  save()
  if reason:
   os.killpg(proc.pid,signal.SIGTERM)
   try:proc.wait(timeout=2)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
   break
  time.sleep(.1 if mode=='cpu_build' else .2)
finally:
 try:
  os.killpg(proc.pid,signal.SIGTERM)
  try:os.killpg(proc.pid,signal.SIGKILL)
  except ProcessLookupError:pass
 except ProcessLookupError:pass
 r.update(status=reason or ('PASS' if proc.returncode==0 else 'GATE_STOP'),returncode=proc.returncode,seconds=time.monotonic()-start,completed_child_maxrss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024)
 if lock:fcntl.flock(lock,fcntl.LOCK_UN);lock.close();r['gpu_lock_released']=True
 save()
print(json.dumps(r),flush=True);sys.exit(0 if proc.returncode==0 and not reason else 1)
