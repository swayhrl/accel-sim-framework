"""Single-child CPU budget guardian; never reads GPU devices or campaign locks."""
import hashlib,json,os,pathlib,signal,subprocess,time,sys
ROOT=pathlib.Path('/data/c16/aiarch_a45h_cpuadam_cpuonly_109_20261014');OLD=pathlib.Path('/data/c16/aiarch_a26gr1_gsscale_rubble_109_20261014')
WORK=pathlib.Path(__file__).resolve().parents[2];pre=json.loads((ROOT/'preregister.json').read_text())
start=json.loads((ROOT/'start.json').read_text())['epoch'];deadline=start+1200
assert time.time()<deadline
baseenv=os.environ.copy();baseenv.update(A45H_OUTPUT=str(ROOT),A45H_OLD_READONLY=str(OLD),LD_LIBRARY_PATH='/data/c16/env/cpython-3.10.12/lib',PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',CUDA_VISIBLE_DEVICES='-1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',OMP_DYNAMIC='FALSE',HOME=str(ROOT/'home'),TMPDIR=str(ROOT/'tmp'),XDG_CACHE_HOME=str(ROOT/'cache'),TORCH_HOME=str(ROOT/'cache'),TORCH_EXTENSIONS_DIR=str(ROOT/'cache/disabled_extensions'))
baseenv.pop('PYTHONPATH',None);baseenv.pop('CUDA_HOME',None)
results=[];status='PASS';reasons=[];total_samples=0
for mode in (sys.argv[1:] or ['scan','update']):
 assert mode in ['scan','update']
 for limit in pre['design']['thread_limits']:
  env=baseenv.copy();env['OMP_THREAD_LIMIT']=str(limit)
  log=ROOT/'logs'/f'{mode}_{limit}.log';t=time.monotonic();peakrss=0;peakrun=0;peakresident=0;samples=[]
  with log.open('w') as out:
   p=subprocess.Popen([str(OLD/'venv/bin/python'),str(WORK/'tools/aiarch_a45h/cpu_component_probe.py'),mode,str(limit)],env=env,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
   while p.poll() is None:
    rss=0;run=0;resident=0
    for pid in [p.pid,os.getpid()]:
     try:
      stat=pathlib.Path(f'/proc/{pid}/status').read_text();rss+=int(next(x.split()[1] for x in stat.splitlines() if x.startswith('VmRSS:')))*1024
      tasks=list(pathlib.Path(f'/proc/{pid}/task').iterdir());resident+=len(tasks)
      for x in tasks:
       try:run+=x.joinpath('stat').read_text().split()[2]=='R'
       except OSError:pass
     except (OSError,StopIteration):pass
    peakrss=max(peakrss,rss);peakrun=max(peakrun,run);peakresident=max(peakresident,resident);total_samples+=1
    if len(samples)<160 and total_samples%3==0:samples.append({'elapsed':time.monotonic()-t,'rss':rss,'running':run,'resident':resident})
    disk=sum(x.stat().st_blocks*512 for x in ROOT.rglob('*') if x.is_file())+sum(x.stat().st_blocks*512 for x in WORK.rglob('*') if x.is_file())
    reason=None
    if rss>6*1024**3:reason='RSS_LIMIT'
    if run>24:reason='RUNNING_THREAD_LIMIT'
    if disk>50*1024**2:reason='NEW_FILE_LIMIT'
    if time.time()>deadline:reason='EXECUTION_TIME_LIMIT'
    if reason:
     reasons.append(reason);status='STOP';os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=5);break
    time.sleep(.005)
  rc=p.wait();item={'mode':mode,'limit':limit,'returncode':rc,'elapsed_seconds':time.monotonic()-t,'tree_peak_rss_bytes_sampled':peakrss,'tree_peak_running_threads_sampled':peakrun,'tree_peak_resident_threads_sampled':peakresident,'sample_interval_seconds':.005,'samples':samples};results.append(item)
  print('FINISH',mode,limit,rc,'RSS',peakrss,'RUNNING',peakrun,flush=True)
  if rc!=0:status='STOP';reasons.append(f'{mode}_{limit}_EXIT_{rc}')
  if status!='PASS':break
 if status!='PASS':break
unchanged=all(hashlib.sha256((OLD/p).read_bytes()).hexdigest()==v['sha256'] and (OLD/p).stat().st_mtime_ns==v['mtime_ns'] for p,v in pre['identity'].items())
assert unchanged
receipt={'status':status,'reasons':reasons,'old_referenced_assets_hash_and_mtime_unchanged':unchanged,'results':results,'execution_elapsed_seconds':time.time()-start,'total_resource_samples':total_samples,'gpu_lock_read_or_operation':False,'downloads_or_installs':0,'new_private_allocated_bytes':sum(x.stat().st_blocks*512 for x in ROOT.rglob('*') if x.is_file())}
(ROOT/'supervisor.json').write_text(json.dumps(receipt,indent=2)+'\n');print('SUPERVISOR',status,receipt['execution_elapsed_seconds'],flush=True)
