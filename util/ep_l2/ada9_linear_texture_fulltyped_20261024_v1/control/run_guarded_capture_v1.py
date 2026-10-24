#!/usr/bin/env python3
from pathlib import Path
import os,json,subprocess,time,fcntl,re,signal,hashlib,sys,datetime,traceback,shutil
R=Path('/data/c16/ada_linear_texture_producer_v9_20261024_v1')
Q=Path(sys.argv[1]);B=sys.argv[2];jobs=json.loads(Q.read_text());C=R/'native_control';C.mkdir(exist_ok=True);SUMMARY=C/('NATIVE_BATCH_'+B+'.json');assert not SUMMARY.exists()
summary=[]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for x in iter(lambda:f.read(1024*1024),b''):h.update(x)
 return h.hexdigest()
def put(p,x):
 t=Path(str(p)+'.tmp');t.write_text(json.dumps(x,indent=2)+'\n');os.replace(t,p)
def ticks(pid):return (Path('/proc')/str(pid)/'stat').read_text().split(') ',1)[1].split()[19]
def query(args):return subprocess.check_output(['nvidia-smi']+args,text=True,timeout=15).strip()
def apps():
 out=query(['--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader,nounits']);rows={}
 for line in out.splitlines():
  if not line.strip():continue
  t=[x.strip() for x in line.split(',')];rows[int(t[0])]={'name':t[1],'vram_mib':int(t[2]) if t[2].isdigit() else None}
 return rows
def stop(p):
 if p and p.poll() is None:
  os.killpg(p.pid,signal.SIGTERM)
  try:p.wait(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
def ownexe(pid):return os.readlink('/proc/'+str(pid)+'/exe')
def classification(j,rc,text,bounded):
 kind=j.get('workload_kind','FINITE_GPU_WORKLOAD')
 if bounded:return 'NATIVE_BOUNDED_STOP_RETAINED'
 if kind=='EXPECTED_DEVICE_ASSERT_NEGATIVE_API_TEST':return 'EXPECTED_ASSERT_DIAGNOSTIC_COMPLETE' if 'device-side assert' in text.lower() and re.search(r'pass',text,re.I) else 'EXPECTED_ASSERT_DIAGNOSTIC_REVIEW'
 if kind=='GPU_COPY_API_ONLY_NO_SASS_KERNEL_EXPECTED':return 'NATIVE_COPY_API_COMPLETE_NO_SASS_EXPECTED' if rc==0 else 'NATIVE_FAILURE_RETAINED'
 negative=re.search(r"\b(?:FAILED|FAILURE)\b|DON.T\s+MATCH|MISMATCH|NON.?FINITE|CUDA.{0,30}ERROR|Test\s+failed",text,re.I)
 positive=re.search(r'\bPASSED\b|\bTest\s+OK\b|Result\s*=\s*PASS|TEST\s+PASS|All\s+tests\s+passed',text,re.I)
 # Old SDK wrappers preserve an explicit sample result, including original failures.
 expected=j.get('correctness',{}).get('stdout_regex')
 if expected and re.search(expected,text):positive=True
 if rc==0 and positive and not negative:return 'UPSTREAM_NATIVE_SELF_CHECK_PASS'
 if rc==0 and not negative:return 'NATIVE_EXECUTION_COMPLETE_NUMERICAL_REVIEW'
 return 'NATIVE_FAILURE_RETAINED'
put(C/('SUPERVISOR_'+B+'.json'),{'pid':os.getpid(),'start_ticks':ticks(os.getpid()),'manifest':str(Q),'manifest_sha256':sha(Q),'tasks':len(jobs),'start_unix':time.time(),'finite':True})
for index,j in enumerate(jobs):
 ident=j.get('task_id',j['program']+'_'+str(index));out=R/'native_attempts'/B/ident/'attempt001';out.mkdir(parents=True,exist_ok=False)
 rec={'task':j,'output':str(out),'index':index,'start_unix':time.time()};p=None;lock=None
 try:
  if j.get('workload_kind')=='OFFICIAL_TESTRUN_CPU_REFERENCE_ONLY':rec['status']='CPU_REFERENCE_CONFIGURATION_FROZEN_NO_GPU_WORK';continue
  if j['program']=='simpleP2P' and len(query(['--query-gpu=uuid','--format=csv,noheader']).splitlines())<2:rec['status']='PLATFORM_UNAVAILABLE_REQUIRES_2_GPUS';continue
  while Path('/data/c16/rtx4080_suite_fill_20261024_v1/control/GPU_QUEUE_PAUSE').exists():time.sleep(5)
  lock=open('/data/c16/locks/c16_gpu_campaign.lock','a');waitstart=time.monotonic()
  while True:
   try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);break
   except BlockingIOError:
    if time.monotonic()-waitstart>1800:raise RuntimeError('GPU_LOCK_BUSY_1800S')
    time.sleep(5)
  rec['lock_wait_seconds']=time.monotonic()-waitstart;base=apps();allowed=set(base)
  for pid,x in base.items():
   assert x['name']=='/home/huangrulin/workspace/image-lab/envs/comfyui/bin/python',base
   cmd=(Path('/proc')/str(pid)/'cmdline').read_bytes().replace(b'\0',b' ').decode();assert '/home/huangrulin/workspace/image-lab/app/ComfyUI/main.py' in cmd,(pid,cmd)
   x.update(start_ticks=ticks(pid),exe=ownexe(pid),cmdline=cmd)
  rec['resident_baseline']=base;rec['gpu']=query(['--query-gpu=name,uuid,driver_version,memory.total,memory.used,memory.free','--format=csv'])
  stable=0;idle=[];t0=time.monotonic()
  while stable<15:
   u=query(['--query-gpu=utilization.gpu,memory.free','--format=csv,noheader,nounits']).split(',');util=int(u[0]);free=int(u[1]);idle.append({'unix':time.time(),'util':util,'free_mib':free});stable=stable+1 if util==0 else 0
   assert time.monotonic()-t0<180,'NO_15S_IDLE_WINDOW_180S';assert free>2048,'LESS_THAN_2GIB_PRESTART_VRAM'
   now=apps();assert set(now)<=allowed,'NEW_COMPUTE_PRESTART'
   for pid,x in now.items():
    assert ticks(pid)==base[pid]['start_ticks'],'RESIDENT_PID_REUSED';assert x['vram_mib'] is None or base[pid]['vram_mib'] is None or x['vram_mib']<=base[pid]['vram_mib']+256,'RESIDENT_VRAM_GROWTH_PRESTART'
   time.sleep(1)
  rec['idle_gate']=idle
  assert sha(j['argv'][0])==j['binary_sha256'],'BINARY_SHA_MISMATCH'
  for f in j.get('source_files',[])+j.get('input_files',[]):assert sha(f['path'])==f['sha256'],('SOURCE_OR_INPUT_SHA_MISMATCH',f['path'])
  for link in j.get('runtime_links',[]):
   assert Path(link['name']).name==link['name']
   target=Path(link['target']);dest=out/link['name']
   if target.is_dir():
    dest.mkdir(exist_ok=False)
    for original in j.get('input_files',[]):
     op=Path(original['path'])
     try:rel=op.relative_to(target)
     except ValueError:continue
     dp=dest/rel;dp.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(op,dp);assert sha(dp)==original['sha256']
   else:shutil.copy2(target,dest)
  rec['input_staging']='Private independent regular-file copies of manifest-listed inputs; writable outputs cannot follow a directory symlink into source'
  env=dict(os.environ);env.update(j.get('env',{}));env.update(j.get('runtime_env',{}));env.update(PYTHONDONTWRITEBYTECODE='1',DISPLAY='')
  for k in ['LD_PRELOAD','CUDA_INJECTION64_PATH','PYTHONPATH','PYTHONHOME']:env.pop(k,None)
  if j.get('native_preload_libraries'):
   trusted=[]
   for item in j['native_preload_libraries']:
    lib=Path(item['path']);assert lib.is_absolute() and lib.resolve().is_relative_to(R.resolve()) and lib.is_file() and not lib.is_symlink(),'UNTRUSTED_NATIVE_PRELOAD_PATH'
    assert sha(lib)==item['sha256'],'NATIVE_PRELOAD_SHA_MISMATCH';trusted.append(str(lib))
   env['LD_PRELOAD']=':'.join(trusted);rec['native_only_preload_libraries']=j['native_preload_libraries']

  with (out/'stdout.log').open('x') as f:
   p=subprocess.Popen(j['argv'],cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,preexec_fn=lambda:os.nice(15));rec.update(pid=p.pid,start_ticks=ticks(p.pid));put(out/'NATIVE_RECEIPT.json',rec);t0=time.monotonic();monitors=[]
   while p.poll() is None:
    now=apps()
    for pid,x in now.items():
     if pid not in allowed|{p.pid}:
      try:owned_gpu_child=os.getpgid(pid)==p.pid and Path('/proc/'+str(pid)).stat().st_uid==os.getuid()
      except ProcessLookupError:owned_gpu_child=True # process already exited
      if not owned_gpu_child:rec['bounded_stop']='NEW_COMPUTE '+str(pid)
     if pid in allowed:
      if ticks(pid)!=base[pid]['start_ticks']:rec['bounded_stop']='RESIDENT_PID_REUSED'
      if x['vram_mib'] is not None and base[pid]['vram_mib'] is not None and x['vram_mib']>base[pid]['vram_mib']+256:rec['bounded_stop']='RESIDENT_VRAM_GROWTH_256MIB'
    free=int(query(['--query-gpu=memory.free','--format=csv,noheader,nounits']));rec['minimum_free_vram_mib']=min(free,rec.get('minimum_free_vram_mib',free))
    if free<512:rec['bounded_stop']='LESS_THAN_512MIB_LIVE_VRAM_HEADROOM'
    mon=subprocess.run(['nvidia-smi','pmon','-c','1','-s','u'],capture_output=True,text=True,timeout=15)
    for line in mon.stdout.splitlines():
     z=line.split()
     if len(z)>3 and z[1].isdigit() and int(z[1]) in allowed and z[3] not in ['0','-']:rec['bounded_stop']='RESIDENT_GPU_ACTIVE '+line
    monitors.append({'unix':time.time(),'free_mib':free,'compute':now,'pmon':mon.stdout});
    if (out/'stdout.log').stat().st_size>256*1024**2:rec['bounded_stop']='256MIB_STDOUT_BOUND'
    if time.monotonic()-t0>j.get('native_timeout_sec',600):rec['bounded_stop']='NATIVE_TIMEOUT'
    if rec.get('bounded_stop'):stop(p)
    time.sleep(.2)
   rec.update(exit=p.returncode,wall_seconds=time.monotonic()-t0);put(out/'GPU_MONITOR.json',monitors)
  with (out/'stdout.log').open('rb') as f:head=f.read(1024*1024);f.seek(max(0,(out/'stdout.log').stat().st_size-1024*1024));tail=f.read()
  text=(head+tail).decode(errors='replace');rec['status']=classification(j,p.returncode,text,rec.get('bounded_stop'));rec['stdout_sha256']=sha(out/'stdout.log')
  for x in j.get('input_files',[]):assert sha(x['path'])==x['sha256'],('INPUT_MUTATED',x['path'])
 except Exception as e:
  stop(p);rec['status']='NATIVE_RESOURCE_OR_SETUP_HOLD';rec['error']=repr(e);rec['traceback']=traceback.format_exc()
 finally:
  if lock:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
  rec['end_unix']=time.time();summary.append(rec);put(out/'NATIVE_RECEIPT.json',rec);put(SUMMARY,summary);print(index,j['program'],rec['status'],rec.get('exit'),flush=True)
put(C/('COMPLETE_'+B+'.json'),{'end_unix':time.time(),'tasks':len(summary),'manifest_sha256':sha(Q),'status_counts':{s:sum(x['status']==s for x in summary) for s in sorted(set(x['status'] for x in summary))}})
