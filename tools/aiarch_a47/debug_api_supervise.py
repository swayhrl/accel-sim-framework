"""One bounded CPU-backtrace API diagnostic, same GPU lock and cumulative ledger."""
import fcntl,json,os,pathlib,signal,subprocess,time,stat
from budget_io import ROOT,check_disk
os.sched_setaffinity(0,[0,2,4,6]);lock=pathlib.Path('/data/c16/locks/c16_gpu_campaign.lock');prior=json.loads((ROOT/'gpu_resource_receipt.json').read_text());started=None;p=None;fd=None;samples=[];peakrss=0;peakgpu=0;reason=None
try:
 fd=os.open(lock,os.O_RDWR|os.O_NOFOLLOW);assert stat.S_ISREG(os.fstat(fd).st_mode);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);started=time.monotonic()
 env=os.environ.copy();env.update(A47_GPU_LOCK_HELD='1',CUDA_VISIBLE_DEVICES='0',CUDA_CACHE_PATH=str(ROOT/'cache/driver'),CUPY_CACHE_DIR=str(ROOT/'cache/cupy'),HOME=str(ROOT/'cache/home'),XDG_CACHE_HOME=str(ROOT/'cache'),TMPDIR=str(ROOT/'tmp'),PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OMP_THREAD_LIMIT='4',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
 for k in ['LD_LIBRARY_PATH','CUDA_HOME','CUDA_PATH','PYTHONPATH']:env.pop(k,None)
 def apps():
  s=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True);return [(int(a.split(',')[0]),int(a.split(',')[1])) for a in s.splitlines() if a.strip()]
 assert apps()==[],'OTHER_GPU_TASK_PRESENT'
 log=(ROOT/'logs/small_api_gdb.log').open('w');p=subprocess.Popen(['gdb','--batch','-ex','set pagination off','-ex','set confirm off','-ex','run','-ex','thread apply all bt 16','-ex','quit','--args',str(ROOT/'venv/bin/python'),str(pathlib.Path(__file__).with_name('api_fixture.py'))],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 while p.poll() is None:
  table={}
  for entry in pathlib.Path('/proc').glob('[0-9]*'):
   try:a=entry.joinpath('stat').read_text().rsplit(')',1)[1].split();table[int(entry.name)]=int(a[1])
   except OSError:pass
  owned={p.pid}
  for _ in range(6):owned.update(k for k,v in table.items() if v in owned)
  current=apps();assert all(pid in owned for pid,_ in current),'EXTERNAL_GPU_TASK'
  gpu=sum(v for _,v in current);peakgpu=max(peakgpu,gpu);rss=0
  for pid in owned|{os.getpid()}:
   try:s=pathlib.Path(f'/proc/{pid}/status').read_text();rss+=int(next(x.split()[1] for x in s.splitlines() if x.startswith('VmRSS:')))*1024
   except (OSError,StopIteration):pass
  peakrss=max(peakrss,rss);samples.append({'monotonic':time.monotonic(),'GPU_mib':gpu,'rss_bytes':rss,'owned_pid_count':len(owned)})
  assert gpu<=12*1024 and rss<=8*1024**3;check_disk();assert time.monotonic()-started<90 and time.monotonic()-started+prior['cumulative_lock_seconds']<2680
  time.sleep(.25)
 p.wait();log.close();reason='DIAGNOSTIC_COMPLETE'
except Exception as e:reason=repr(e)
finally:
 if p is not None and p.poll() is None:
  os.killpg(p.pid,signal.SIGTERM)
  try:p.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
 held=time.monotonic()-started if started else 0
 if fd is not None:
  if started:fcntl.flock(fd,fcntl.LOCK_UN)
  os.close(fd)
 rec={'scope':'one small synthetic API diagnostic and CPU stack only; not scientific timing or second formal graph','reason':reason,'lock_seconds':held,'peak_gpu_mib_sampled':peakgpu,'peak_tree_rss_bytes_sampled':peakrss,'samples':samples,'gdb_returncode':None if p is None else p.returncode,'lock_released':True};prior['cumulative_lock_seconds']+=held;prior['attempts'].append(rec);(ROOT/'gpu_resource_receipt.json').write_text(json.dumps(prior,indent=2)+'\n');print('SMALL_API_DEBUG_DONE',reason,held,peakgpu,peakrss,flush=True)
