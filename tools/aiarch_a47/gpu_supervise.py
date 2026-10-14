"""Own all GPU children under the existing nonblocking campaign lock."""
import fcntl,hashlib,json,os,pathlib,signal,stat,subprocess,time
from budget_io import ROOT,check_disk
WORK=pathlib.Path(__file__).resolve().parents[2];LOCK=pathlib.Path('/data/c16/locks/c16_gpu_campaign.lock')
os.sched_setaffinity(0,[0,2,4,6]);lock_file=None;started=None;children=[];samples=[];stages=[];reason=None;peak_gpu=0;peak_rss=0
ledger=ROOT/'gpu_resource_receipt.json'
prior=json.loads(ledger.read_text()) if ledger.exists() else {'cumulative_lock_seconds':0,'attempts':[]}
def command(args):return subprocess.check_output(args,text=True,timeout=12).strip()
def gpu_apps():
 out=command(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader,nounits']);apps=[]
 for line in out.splitlines():
  if line.strip():
   a=line.split(',');apps.append({'pid':int(a[0]),'name':a[1].strip(),'mib':int(a[-1].strip())})
 return apps
try:
 assert json.loads((ROOT/'resolved_env_lock.json').read_text())['status']=='INSTALLED_OFFLINE_PIP_CHECK_PASS'
 assert json.loads((ROOT/'data_validation_receipt.json').read_text())['status']=='PASS'
 pids=json.loads((ROOT/'prepare_pids.json').read_text())
 for key,pid in pids.items():
  if isinstance(pid,int) and pathlib.Path(f'/proc/{pid}/stat').exists():assert pathlib.Path(f'/proc/{pid}/stat').read_text().split()[2]=='Z','PREP_HEAVY_WORK_STILL_RUNNING'
 assert not gpu_apps(),'OTHER_GPU_TASK_PRESENT'
 ls=LOCK.stat();assert stat.S_ISREG(ls.st_mode) and not LOCK.is_symlink(),'SHARED_LOCK_IDENTITY'
 fd=os.open(LOCK,os.O_RDWR|os.O_NOFOLLOW);lock_file=os.fdopen(fd,'r+')
 assert (os.fstat(fd).st_dev,os.fstat(fd).st_ino)==(ls.st_dev,ls.st_ino)
 try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:reason='GPU_LOCK_DEFERRED';raise RuntimeError(reason)
 started=time.monotonic();remaining=2700-prior['cumulative_lock_seconds'];assert remaining>60,'GPU_BUDGET_EXHAUSTED'
 deadline=started+remaining;assert not gpu_apps(),'OTHER_GPU_TASK_PRESENT_AFTER_LOCK'
 env=os.environ.copy();env.update(A47_GPU_LOCK_HELD='1',A47_GPU_DEADLINE=str(deadline),CUDA_VISIBLE_DEVICES='0',CUDA_CACHE_PATH=str(ROOT/'cache/driver'),CUPY_CACHE_DIR=str(ROOT/'cache/cupy'),HOME=str(ROOT/'cache/home'),XDG_CACHE_HOME=str(ROOT/'cache'),TMPDIR=str(ROOT/'tmp'),PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OMP_THREAD_LIMIT='4',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',HDF5_PLUGIN_PRELOAD='::')
 for key in ['LD_LIBRARY_PATH','CUDA_HOME','CUDA_PATH','PYTHONPATH']:env.pop(key,None)
 for mode,args in [('build_qualify',[]),('measure',['0']),('measure',['1']),('measure',['2'])]:
  baseline=check_disk();tag=mode+('_'+args[0] if args else '')
  if mode=='measure':assert json.loads((ROOT/'report_quality.json').read_text())['status']=='PASS'
  t=time.monotonic();log=(ROOT/'logs'/f'native_{tag}.log').open('w');p=subprocess.Popen([str(ROOT/'venv/bin/python'),str(WORK/'tools/aiarch_a47/native.py'),mode,*args],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);children.append(p)
  while p.poll() is None:
   apps=gpu_apps();unknown=[x for x in apps if x['pid']!=p.pid]
   if unknown:reason='EXTERNAL_GPU_LOAD_CONTAMINATION';break
   use=sum(x['mib'] for x in apps if x['pid']==p.pid);peak_gpu=max(peak_gpu,use)
   rss=0;running=0;resident=0
   for pid in [p.pid,os.getpid()]:
    try:
     text=pathlib.Path(f'/proc/{pid}/status').read_text();rss+=int(next(x.split()[1] for x in text.splitlines() if x.startswith('VmRSS:')))*1024
     tids=list(pathlib.Path(f'/proc/{pid}/task').iterdir());resident+=len(tids)
     for tid in tids:
      try:running+=tid.joinpath('stat').read_text().split()[2]=='R'
      except OSError:pass
    except (OSError,StopIteration):pass
   peak_rss=max(peak_rss,rss)
   if use>12*1024:reason='GPU_VRAM_BUDGET'
   if rss>8*1024**3:reason='HOST_RAM_BUDGET'
   if time.monotonic()>deadline-15:reason='GPU_LOCK_TIME_BUDGET'
   # No expensive full environment walks during formal measurement.
   if mode=='build_qualify':
    try:check_disk()
    except AssertionError:reason='DISK_OR_FREE_SPACE_BUDGET'
   elif os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize<64*1024**3:reason='FREE_SPACE_BUDGET'
   metadata=command(['nvidia-smi','--query-gpu=temperature.gpu,utilization.gpu,clocks.sm,clocks.mem,power.draw','--format=csv,noheader,nounits'])
   samples.append({'monotonic':time.monotonic(),'stage':tag,'pid':p.pid,'gpu_mib':use,'tree_rss_bytes':rss,'running_threads':running,'resident_threads':resident,'device_metadata_csv':metadata})
   if reason:break
   time.sleep(.5)
  if reason and p.poll() is None:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
  rc=p.wait();log.close();stages.append({'stage':tag,'returncode':rc,'elapsed_seconds':time.monotonic()-t});print('GPU_STAGE',tag,rc,stages[-1]['elapsed_seconds'],flush=True)
  if reason:break
  if rc!=0:
   reason='QUALITY_NO_GO' if rc==20 else 'NATIVE_ENGINEERING_OR_PLATFORM_FAILURE';break
except Exception as e:
 if reason is None:reason='PREFLIGHT_OR_PLATFORM_FAILURE '+repr(e)
finally:
 for p in children:
  if p.poll() is None:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
 held=0 if started is None else time.monotonic()-started
 if lock_file is not None:
  if started is not None:fcntl.flock(lock_file.fileno(),fcntl.LOCK_UN)
  lock_file.close()
 attempt={'status':'PASS_NATIVE_COMPLETE' if reason is None else 'STOP','reason':reason,'lock_seconds':held,'shared_lock_existing_inode':locals().get('ls').st_ino if 'ls' in locals() else None,'peak_gpu_mib_sampled':peak_gpu,'peak_tree_rss_bytes_sampled':peak_rss,'CPU_affinity':[0,2,4,6],'stages':stages,'samples':samples,'all_own_GPU_children_ended':all(p.poll() is not None for p in children),'lock_released':True,'no_next_task':True}
 final={'cumulative_lock_seconds':prior['cumulative_lock_seconds']+held,'attempts':prior['attempts']+[attempt]};ledger.write_text(json.dumps(final,indent=2)+'\n');print('GPU_STOP_RECEIPT',attempt['status'],reason,'CUMULATIVE',final['cumulative_lock_seconds'],'VRAM',peak_gpu,'RSS',peak_rss,flush=True)
