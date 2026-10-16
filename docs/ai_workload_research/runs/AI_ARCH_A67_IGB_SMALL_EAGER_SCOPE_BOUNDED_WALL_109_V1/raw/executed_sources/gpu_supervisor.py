"""A67 PID-complete original shared GPU lease and bounded resource supervision."""
import fcntl,json,os,signal,stat,subprocess,time,shutil
from pathlib import Path
from paths import R,W,OLD,DISPATCH_EPOCH,save,sha,usage,allocated,new_raw_allocated
from ownership import classify_snapshot,parse_nvml_csv
LOCK=Path('/data/c16/locks/c16_gpu_campaign.lock')

def proc(pid):
 try:
  row=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
  return {'pid':pid,'state':row[0],'ppid':int(row[1]),'pgid':int(row[2]),'sid':int(row[3]),'start_ticks':int(row[19]),'UID':Path(f'/proc/{pid}').stat().st_uid}
 except (FileNotFoundError,ProcessLookupError):return None

def group(pgid):
 out=[]
 for p in Path('/proc').iterdir():
  if p.name.isdigit():
   try:x=proc(int(p.name))
   except PermissionError:continue
   if x and x['pgid']==pgid and x['state']!='Z':out.append(x)
 return out

def rss(pids):
 total=0
 for pid in set(pids):
  try:total+=int(next(x.split()[1] for x in Path(f'/proc/{pid}/status').read_text().splitlines() if x.startswith('VmRSS:')))*1024
  except (FileNotFoundError,ProcessLookupError,StopIteration):pass
 return total

def query_apps():
 start=time.monotonic();raw=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True,timeout=3)
 rows=[]
 try:
  rows=parse_nvml_csv(raw)
 except Exception:
  save('NVML_parse_failure.json',{'raw':raw,'query_start':start,'query_end':time.monotonic()});raise
 return start,time.monotonic(),raw,rows

def append_snapshot(value):
 with (R/'raw/gpu_pid_snapshots.jsonl').open('a') as f:f.write(json.dumps(value)+'\n')

def sample(child,known,phase):
 before={pid:proc(pid) for pid in known};terminal_before=child.poll() is not None if child else True
 qs,qe,raw,rows=query_apps();after={pid:proc(pid) for pid in set(known)|{x[0] for x in rows}}
 terminal=child.poll() is not None if child else True
 decision=classify_snapshot(rows,known,before,after,terminal)
 value={'epoch':time.time(),'query_start':qs,'query_end':qe,'phase':phase,'raw_NVML_csv':raw,'known_child_identities':known,'proc_before':before,'proc_after':after,'child_terminal_before':terminal_before,'child_terminal_after':terminal,'child_returncode':None if child is None else child.returncode,**decision}
 append_snapshot(value)
 return value,rows

def end_group(child):
 if child is None:return
 if group(child.pid):
  try:os.killpg(child.pid,signal.SIGTERM)
  except ProcessLookupError:pass
  until=time.monotonic()+2
  while group(child.pid) and time.monotonic()<until:time.sleep(.05)
  if group(child.pid):os.killpg(child.pid,signal.SIGKILL)
 child.wait(timeout=3);assert not group(child.pid),'OWN_PROCESS_GROUP_NOT_CLEAN'

def main():
 for name in ['CPU_preflight.json','library_RECORD_pre.json','supervisor_cpu_tests.json']:
  assert json.loads((R/name).read_text())['status']=='PASS'
 assert time.time()-DISPATCH_EPOCH<3600,'CPU_PREP_ONE_HOUR'
 assert shutil.disk_usage(R).free>=64*1024**3
 assert allocated()+64*1024**2<256*1024**2
 assert not (R/'gpu_ledger.json').exists(),'ONE_AUTHORIZED_GPU_ATTEMPT_ONLY'
 identities={str(p.relative_to(W)):sha(p) for p in (W/'tools/aiarch_a67').glob('*.py')}
 guard=R/'runtime/lib/python3.10/site-packages/sitecustomize.py';identities[str(guard)]=sha(guard)
 save('pre_GPU_script_identity.json',identities)
 (R/'executed_sources').mkdir()
 for name in ['native.py','math_copy.py','paths.py','gpu_supervisor.py','ownership.py']:
  shutil.copyfile(W/'tools/aiarch_a67'/name,R/'executed_sources'/name)
 shutil.copyfile(guard,R/'executed_sources/sitecustomize.py')
 fd=None;started=None;child=None;known={};reason=None;values=[];final_empty=False;code=None;acquired=False
 baseline_W=usage([W]);remaining_CPU_prep=time.time()-DISPATCH_EPOCH
 try:
  st=LOCK.lstat();assert stat.S_ISREG(st.st_mode) and not LOCK.is_symlink()
  fd=os.open(LOCK,os.O_RDWR|os.O_NOFOLLOW);assert os.fstat(fd).st_ino==st.st_ino
  try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:reason='GPU_LOCK_DEFERRED';return
  acquired=True;started=time.monotonic();deadline=started+900
  admission,rows=sample(None,{},'ADMISSION_BEFORE_CUDA')
  if rows:reason='EXTERNAL_GPU_TASK_STOP';return
  dev=subprocess.check_output(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total,memory.free','--format=csv,noheader,nounits'],text=True,timeout=3).strip()
  old=json.loads((OLD/'gpu_admission_metadata.json').read_text())['device']
  assert dev.split(',')[2].strip()==old.split(',')[1].strip(),'DRIVER_IDENTITY_CHANGED'
  save('GPU_admission.json',{'device':dev,'lock_path':str(LOCK),'lock_inode':st.st_ino,'nonblocking':True,'CPU_prepare_seconds':remaining_CPU_prep})
  env=os.environ.copy();env.update(A67_GPU_LOCK_HELD='1',A67_GPU_DEADLINE=str(deadline),CUDA_VISIBLE_DEVICES='0',DGLBACKEND='pytorch',HOME=str(R/'cache/home'),TMPDIR=str(R/'tmp'),XDG_CACHE_HOME=str(R/'cache'),TORCH_HOME=str(R/'cache/torch'),TORCHINDUCTOR_CACHE_DIR=str(R/'cache/inductor'),TRITON_CACHE_DIR=str(R/'cache/triton'),TORCH_EXTENSIONS_DIR=str(R/'cache/extensions'),CUDA_CACHE_PATH=str(R/'cache/driver'),PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',LD_LIBRARY_PATH='/data/c16/env/cpython-3.10.12/lib',OMP_NUM_THREADS='1',OMP_THREAD_LIMIT='4',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',MAX_JOBS='4')
  for k in ['PYTHONPATH','CUDA_HOME','CUDA_PATH']:env.pop(k,None)
  with (R/'raw/native.log').open('w') as log:
   child=subprocess.Popen([str(R/'runtime/bin/python'),str(W/'tools/aiarch_a67/native.py')],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   birth=proc(child.pid);assert birth is not None and birth['pgid']==child.pid and birth['sid']==child.pid,'CHILD_IDENTITY_NOT_PROVEN'
   known={child.pid:birth};save('GPU_child_launch.json',{'identity':birth,'parent_PID':os.getpid(),'monotonic':time.monotonic()})
   while child.poll() is None:
    phase=json.loads((R/'current_phase.json').read_text()) if (R/'current_phase.json').exists() else {'phase':'PYTHON_IMPORT'}
    snapshot,rows=sample(child,known,phase['phase'])
    g=group(child.pid);memory=rss([x['pid'] for x in g]+[os.getpid()]);vram=sum(x[1] for x in rows);disk=baseline_W+usage([R])+8*1024**2;free=shutil.disk_usage(R).free;rawbytes=usage([R])
    value={'monotonic':time.monotonic(),'phase':phase,'RSS_bytes':memory,'GPU_MiB':vram,'new_disk_bound_bytes':disk,'raw_conservative_bound_bytes':rawbytes,'free_bytes':free,'owned_process_group':g,'PID_snapshot_query_start':snapshot['query_start']};values.append(value)
    reason=snapshot['stop_reason']
    if reason is None and phase['phase'] in ['FORMAL_UNINSTRUMENTED','FORMAL_WALL_SAVED']:
     save('supervisor_boundary_ack.json',{'phase_monotonic':phase['monotonic'],'PID_snapshot_query_start':snapshot['query_start'],'PID_snapshot_query_end':snapshot['query_end'],'phase':phase['phase']})
    if memory>int(15.5*1024**3):reason='BUDGET_STOP_RAM_MARGIN'
    if vram>11520:reason='BUDGET_STOP_VRAM_MARGIN'
    if disk>224*1024**2:reason='BUDGET_STOP_NEW_DISK_MARGIN'
    if rawbytes>28*1024**2:reason='BUDGET_STOP_RAW_MARGIN'
    if free<64*1024**3:reason='BUDGET_STOP_FREE_FS'
    if time.monotonic()>deadline-20:reason='BUDGET_STOP_GPU_TIME_MARGIN'
    if LOCK.stat().st_ino!=st.st_ino:reason='SHARED_LOCK_IDENTITY_CHANGED'
    if reason:break
    time.sleep(.5)
   end_group(child);code=child.returncode
   if code and reason is None:reason='NATIVE_EXIT_NONZERO'
 except BaseException as e:reason=reason or repr(e)
 finally:
  try:
   end_group(child)
   if acquired:
    drain_until=time.monotonic()+3
    while True:
     snap,rows=sample(child,known,'FINAL_DRAIN_AFTER_OWN_EXIT')
     if snap['stop_reason']:reason=reason or snap['stop_reason'];break
     if not rows:final_empty=True;break
     if time.monotonic()>=drain_until:reason=reason or 'GPU_EXCLUSIVITY_UNRESOLVED_NVML_DRAIN';break
     time.sleep(.1)
  except BaseException as e:reason=reason or 'GPU_EXCLUSIVITY_UNRESOLVED '+repr(e)
  finally:
   held=0 if started is None else time.monotonic()-started
   if fd is not None:
    if acquired:fcntl.flock(fd,fcntl.LOCK_UN)
    os.close(fd)
   exclusivity=acquired and final_empty and reason is None
   rec={'status':'COMPLETE' if reason is None else 'STOP','reason':reason,'cumulative_lock_seconds':held,'child_PID':None if child is None else child.pid,'known_child_identities':known,'child_returncode':code,'all_owned_processes_ended':child is None or not group(child.pid),'shared_lock_acquired':acquired,'shared_lock_released':acquired,'final_NVML_empty':final_empty,'exclusivity_evidence_complete':exclusivity,'peak_sampled_RSS_bytes':max((x['RSS_bytes'] for x in values),default=0),'peak_sampled_GPU_MiB':max((x['GPU_MiB'] for x in values),default=0),'samples':values,'sampling_limit':'transient peaks can be missed; allocator.70 and early margins retained','no_next_GPU_task':True}
   save('gpu_ledger.json',rec);print('A67_GPU_SUPERVISOR_STOP',reason,held,exclusivity,flush=True)

if __name__=='__main__':main()
