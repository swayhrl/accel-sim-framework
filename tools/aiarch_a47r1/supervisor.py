"""Nonblocking existing GPU lock; C0 failure forbids C1; no crash retry."""
import fcntl,json,os,pathlib,signal,stat,subprocess,time,shutil
ROOT=pathlib.Path('/data/c16/aiarch_a47r1_cagra_stream_rmm_minicanary_109_20261015_v1');OLD=pathlib.Path('/data/c16/aiarch_a47_cagra_glove100_109_v1');WORK=pathlib.Path(__file__).resolve().parents[2];LOCK=pathlib.Path('/data/c16/locks/c16_gpu_campaign.lock');os.sched_setaffinity(0,[0,2])
prior=json.loads((ROOT/'packaging_attempt1_supervisor_receipt.json').read_text());assert prior['GPU_process_count']==1 and prior['C0']['build_calls']==0
started=None;fd=None;child=None;rows=[];samples=[];reason=None;peakmem=0;peakgpu=0

def apps():
 s=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True,timeout=10)
 return [{'pid':int(x.split(',')[0]),'MiB':int(x.split(',')[1])} for x in s.splitlines() if x.strip()]
def disk():
 size=sum(p.stat().st_blocks*512 for root in [ROOT,WORK] for p in root.rglob('*') if p.is_file());assert size<=128*1024**2 and shutil.disk_usage(ROOT).free>=64*1024**3,'OUTPUT_OR_FREE_DISK_BUDGET';return size
try:
 assert json.loads((ROOT/'preflight_preregistration.json').read_text())['G0_status']=='PASS';assert time.time()-json.loads((ROOT/'start.json').read_text())['epoch']<1800,'PREPARATION_TIME_BUDGET'
 assert not apps(),'OTHER_GPU_TASK_PRESENT';disk();ls=LOCK.stat();assert stat.S_ISREG(ls.st_mode) and not LOCK.is_symlink();fd=os.open(LOCK,os.O_RDWR|os.O_NOFOLLOW);assert os.fstat(fd).st_ino==ls.st_ino
 try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:reason='RESOURCE_OR_GPU_LOCK_DEFERRED';raise RuntimeError('GPU_LOCK_BUSY')
 started=time.monotonic();deadline=started+300-prior['lock_seconds_cumulative'];assert not apps(),'OTHER_GPU_TASK_AFTER_LOCK'
 env=os.environ.copy();env.update(A47R1_GPU_LOCK_HELD='1',A47R1_OUTPUT=str(ROOT),CUDA_VISIBLE_DEVICES='0',PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',CUDA_CACHE_PATH=str(ROOT/'cache/driver'),CUPY_CACHE_DIR=str(ROOT/'cache/cupy'),HOME=str(ROOT/'cache/home'),XDG_CACHE_HOME=str(ROOT/'cache'),TMPDIR=str(ROOT/'tmp'),OMP_NUM_THREADS='1',OMP_THREAD_LIMIT='2',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
 for key in ['LD_LIBRARY_PATH','CUDA_HOME','CUDA_PATH','PYTHONPATH']:env.pop(key,None)
 (ROOT/'environment_policy.json').write_text(json.dumps({'CPU_affinity':[0,2],'OMP_THREAD_LIMIT':2,'OMP_BLAS_threads':1,'isolated_cache_tmp_home':True,'original_venv_readonly':True,'allocator_overrides':False,'pool_overrides':False},indent=2)+'\n')
 for arm in ['C0']:
  if arm=='C1':
   assert rows[-1]['status']=='PASS';r=json.loads((ROOT/'C0_result.json').read_text());assert r['status']=='PASS'
  log=(ROOT/'logs'/f'{arm}.log').open('w');t=time.monotonic();child=subprocess.Popen([str(OLD/'venv/bin/python'),str(WORK/'tools/aiarch_a47r1/minicanary.py'),arm],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  ar_peak_gpu=0;ar_peak_rss=0
  while child.poll() is None:
   current=apps()
   if any(a['pid']!=child.pid for a in current):reason='EXTERNAL_GPU_TASK';break
   gpu=sum(a['MiB'] for a in current);ar_peak_gpu=max(ar_peak_gpu,gpu);peakgpu=max(peakgpu,gpu);rss=0;run=0
   for pid in [child.pid,os.getpid()]:
    try:
     s=pathlib.Path(f'/proc/{pid}/status').read_text();rss+=int(next(x.split()[1] for x in s.splitlines() if x.startswith('VmRSS:')))*1024
     for tid in pathlib.Path(f'/proc/{pid}/task').iterdir():
      try:run+=tid.joinpath('stat').read_text().rsplit(')',1)[1].split()[0]=='R'
      except OSError:pass
    except (OSError,StopIteration):pass
   ar_peak_rss=max(ar_peak_rss,rss);peakmem=max(peakmem,rss);samples.append({'arm':arm,'monotonic':time.monotonic(),'GPU_MiB':gpu,'tree_RSS_bytes':rss,'running_threads':run})
   if gpu>2048 or rss>2*1024**3:reason='BUDGET_STOP'
   if time.monotonic()>deadline-10:reason='BUDGET_STOP'
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
  passed=code==0 and result is not None and result['status']=='PASS' and 'BUILD_PASS' in phases and 'CLEAN_EXIT' in phases and builds==1
  row={'arm':arm,'pid':child.pid,'status':'PASS' if passed and reason is None else 'STOP','exitcode':code,'signal':-code if code<0 else None,'phases':phases,'build_calls':builds,'resource_supervision_elapsed_seconds':time.monotonic()-t,'not_a_performance_measurement':True,'peak_GPU_MiB_sampled':ar_peak_gpu,'peak_tree_RSS_bytes_sampled':ar_peak_rss,'result':result};rows.append(row);print('CANARY_EXIT',arm,code,row['status'],'PHASES',phases,flush=True)
  if not passed or reason:break
 if reason:state='BUDGET_STOP' if reason=='BUDGET_STOP' else 'INCOMPLETE_EVIDENCE_STOP'
 elif not rows or rows[0]['status']!='PASS':state='DEFAULT_API_STILL_FAILS'
 elif len(rows)<2:state='INCOMPLETE_EVIDENCE_STOP';reason='PROCESS_CAP_2_CONSUMED_BY_PREBUILD_PACKAGING_FAILURE_AND_ACTUAL_C0'
 elif rows[1]['status']!='PASS':state='DEFAULT_PASS_EXPLICIT_STREAM_FAILS'
 else:
  assert rows[0]['result']['input_sha256']==rows[1]['result']['input_sha256'];assert rows[0]['result']['default_RMM_type']==rows[1]['result']['default_RMM_type'] and rows[0]['result']['default_CuPy_allocator']==rows[1]['result']['default_CuPy_allocator'];state='BOTH_TINY_CONFIGS_PASS_ORIGINAL_COMBINATION_UNRESOLVED'
except Exception as e:
 state=reason if reason in ['RESOURCE_OR_GPU_LOCK_DEFERRED','BUDGET_STOP'] else 'INCOMPLETE_EVIDENCE_STOP';reason=reason or repr(e)
finally:
 if child is not None and child.poll() is None:
  os.killpg(child.pid,signal.SIGTERM)
  try:child.wait(timeout=3)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
 held=0 if started is None else time.monotonic()-started
 if fd is not None:
  if started is not None:fcntl.flock(fd,fcntl.LOCK_UN)
  os.close(fd)
 receipt={'scientific_state':state,'reason':reason,'C0':next((x for x in rows if x['arm']=='C0'),{'status':'NOT_RUN'}),'C1':next((x for x in rows if x['arm']=='C1'),{'status':'NOT_RUN','reason':reason or 'C0 did not qualify'}),'GPU_process_count':prior['GPU_process_count']+len(rows),'prebuild_packaging_attempt':prior,'lock_seconds_cumulative':prior['lock_seconds_cumulative']+held,'peak_GPU_MiB_sampled':max(peakgpu,prior['peak_GPU_MiB_sampled']),'peak_tree_RSS_bytes_sampled':max(peakmem,prior['peak_tree_RSS_bytes_sampled']),'samples':samples,'sampling_warning':'short lifetimes may escape NVML sampling; sample0 is not true0; tiny input/default resources/no large explicit pool and watchdog jointly constrain budget','all_own_children_ended':child is None or child.poll() is not None,'shared_lock_released':True,'no_download_or_install':True,'no_next_goal':True}
 (ROOT/'supervisor_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('MINICANARY_STOP',state,'LOCK_SECONDS',held,'VRAM_MiB',peakgpu,'RAM_BYTES',peakmem,flush=True)
