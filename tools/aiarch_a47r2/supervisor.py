"""Single existing GPU lease; automatically executes C1 only after complete C0 PASS."""
import fcntl,json,os,pathlib,signal,stat,subprocess,time,shutil
ROOT=pathlib.Path('/data/c16/aiarch_a47r2_cagra_index_fields_109_20261015_v1');OLD=pathlib.Path('/data/c16/aiarch_a47_cagra_glove100_109_v1');WORK=pathlib.Path(__file__).resolve().parents[2];LOCK=pathlib.Path('/data/c16/locks/c16_gpu_campaign.lock');os.sched_setaffinity(0,[0,2])
fd=None;started=None;child=None;rows=[];samples=[];reason=None;peakrss=0;peakgpu=0

def apps():
 text=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True,timeout=10);return [{'pid':int(x.split(',')[0]),'MiB':int(x.split(',')[1])} for x in text.splitlines() if x.strip()]
def disk():
 size=sum(p.stat().st_blocks*512 for root in [ROOT,WORK] for p in root.rglob('*') if p.is_file());assert size<128*1024**2 and shutil.disk_usage(ROOT).free>=64*1024**3,'DISK_BUDGET';return size
try:
 assert json.loads((ROOT/'preflight.json').read_text())['status']=='PASS';assert time.time()-json.loads((ROOT/'start.json').read_text())['epoch']<1800;assert not apps(),'OTHER_GPU_TASK';disk()
 ls=LOCK.stat();assert stat.S_ISREG(ls.st_mode) and not LOCK.is_symlink();fd=os.open(LOCK,os.O_RDWR|os.O_NOFOLLOW);assert os.fstat(fd).st_ino==ls.st_ino
 try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:reason='GPU_LOCK_DEFERRED';raise RuntimeError(reason)
 started=time.monotonic();deadline=started+300;assert not apps(),'OTHER_GPU_TASK_AFTER_LOCK'
 env=os.environ.copy();env.update(A47R2_GPU_LOCK_HELD='1',A47R2_OUTPUT=str(ROOT),CUDA_VISIBLE_DEVICES='0',PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',CUDA_CACHE_PATH=str(ROOT/'cache/driver'),CUPY_CACHE_DIR=str(ROOT/'cache/cupy'),HOME=str(ROOT/'cache/home'),XDG_CACHE_HOME=str(ROOT/'cache'),TMPDIR=str(ROOT/'tmp'),OMP_NUM_THREADS='1',OMP_THREAD_LIMIT='2',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
 for key in ['LD_LIBRARY_PATH','CUDA_HOME','CUDA_PATH','PYTHONPATH']:env.pop(key,None)
 for arm in ['C0','C1']:
  if arm=='C1':assert rows[-1]['status']=='PASS'
  log=(ROOT/'logs'/f'{arm}.log').open('w');t=time.monotonic();child=subprocess.Popen([str(OLD/'venv/bin/python'),str(WORK/'tools/aiarch_a47r2/canary.py'),arm],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);ar_rss=0;ar_gpu=0
  while child.poll() is None:
   current=apps()
   if any(x['pid']!=child.pid for x in current):reason='EXTERNAL_GPU_LOAD';break
   gpu=sum(x['MiB'] for x in current);ar_gpu=max(ar_gpu,gpu);peakgpu=max(peakgpu,gpu);rss=0;running=0
   for pid in [child.pid,os.getpid()]:
    try:
     text=pathlib.Path(f'/proc/{pid}/status').read_text();rss+=int(next(x.split()[1] for x in text.splitlines() if x.startswith('VmRSS:')))*1024
     for tid in pathlib.Path(f'/proc/{pid}/task').iterdir():
      try:running+=tid.joinpath('stat').read_text().rsplit(')',1)[1].split()[0]=='R'
      except OSError:pass
    except (OSError,StopIteration):pass
   ar_rss=max(ar_rss,rss);peakrss=max(peakrss,rss);samples.append({'arm':arm,'monotonic':time.monotonic(),'GPU_MiB':gpu,'tree_RSS_bytes':rss,'running_threads':running})
   if gpu>2048 or rss>2*1024**3 or time.monotonic()>deadline-10:reason='BUDGET_STOP'
   try:disk()
   except AssertionError:reason='BUDGET_STOP'
   if LOCK.stat().st_ino!=ls.st_ino:reason='SHARED_LOCK_IDENTITY_CHANGED'
   if reason:break
   time.sleep(.1)
  if reason and child.poll() is None:
   os.killpg(child.pid,signal.SIGTERM)
   try:child.wait(timeout=3)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
  code=child.wait();log.close();events=[json.loads(x) for x in (ROOT/f'{arm}_events.jsonl').read_text().splitlines()] if (ROOT/f'{arm}_events.jsonl').exists() else [];phases=[x['phase'] for x in events];builds=phases.count('BUILD_ENTER');assert builds<=1
  result=json.loads((ROOT/f'{arm}_result.json').read_text()) if (ROOT/f'{arm}_result.json').exists() else None
  good=code==0 and result is not None and result['status']=='PASS' and all(result['assert_predicate_map'].values()) and 'BUILD_FIELDS_PASS' in phases and 'CLEAN_EXIT' in phases
  row={'arm':arm,'status':'PASS' if good and reason is None else 'STOP','exitcode':code,'signal':-code if code<0 else None,'build_calls':builds,'phases':phases,'result':result,'peak_RSS_bytes_sampled':ar_rss,'peak_GPU_MiB_sampled':ar_gpu,'budget_supervision_elapsed_seconds':time.monotonic()-t,'not_api_performance_measurement':True};rows.append(row);print('ARM_RESULT',arm,row['status'],code,None if result is None else result['fields'],flush=True)
  if not good or reason:break
 if reason:state='PACKAGING_OR_RESOURCE_STOP'
 elif not rows or rows[0]['status']!='PASS':state='C0_REAL_FIELD_OR_API_FAILURE'
 elif len(rows)<2 or rows[1]['status']!='PASS':state='C0_DEFAULT_PASS_C1_STREAM_SENSITIVE'
 else:
  assert rows[0]['result']['input_sha256']==rows[1]['result']['input_sha256'];assert rows[0]['result']['default_RMM_type']==rows[1]['result']['default_RMM_type'] and rows[0]['result']['default_CuPy_allocator']==rows[1]['result']['default_CuPy_allocator'];state='C0_C1_TINY_API_QUALIFIED_ORIGINAL_POOL_INTERACTION_UNRESOLVED'
except Exception as e:state='PACKAGING_OR_RESOURCE_STOP';reason=reason or repr(e)
finally:
 if child is not None and child.poll() is None:
  os.killpg(child.pid,signal.SIGTERM)
  try:child.wait(timeout=3)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
 held=0 if started is None else time.monotonic()-started
 if fd is not None:
  if started is not None:fcntl.flock(fd,fcntl.LOCK_UN)
  os.close(fd)
 receipt={'scientific_state':state,'reason':reason,'arms':rows,'C1_if_absent':'NOT_RUN_C0_UNQUALIFIED','GPU_process_count':len(rows),'total_build_calls':sum(x['build_calls'] for x in rows),'lock_seconds_cumulative':held,'peak_RSS_bytes_sampled':peakrss,'peak_GPU_MiB_sampled':peakgpu,'samples':samples,'sampling_limit':'short NVML samples may miss instantaneous peaks; tiny input/no large pool plus supervision, never treat sample0 as true0','all_own_children_ended':child is None or child.poll() is not None,'lock_released':True,'new_download_install_or_compile':0,'no_next_goal':True};(ROOT/'supervisor_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('R2_STOP',state,'LOCK',held,'RAM',peakrss,'VRAM',peakgpu,flush=True)
