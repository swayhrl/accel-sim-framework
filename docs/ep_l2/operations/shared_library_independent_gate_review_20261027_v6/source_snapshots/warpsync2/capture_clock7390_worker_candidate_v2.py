#!/usr/bin/env python3
"""One exact clock capture candidate. Root file approval + scoped supervisor required.
No import-time GPU/query/load actions. This file is not armed.
"""
import argparse,fcntl,hashlib,json,os,pathlib,re,resource,signal,subprocess,sys,time,shutil,importlib.util,math
D=pathlib.Path(__file__).resolve().parent
ASSET='WARPSYNC_CLOCK7390_STATICCTX_V2_HTOD_SOURCEQA_A001'
QUEUE_ID='ORD_EXT_clock_7390c0dfbbe1_A001'
BINARY_SHA='9f3d1c80c2a5c1b7d6d7c3c41766e2d3ea1df7287777f48c2b137f4f01cf7e17'
SO_SHA='77edc9b58a1575ea0de5f7fd250546cc595e69b6c820c5dc2dc447fe8385e4a5'
UUID='GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59'
ACTION='EXACT_CLOCK7390_ONE_PRIVATE_ADA8_STATICCTX_V2_SOURCEQA_CAPTURE'
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,o):
 with pathlib.Path(p).open('x')as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def ident(pid):
 try:
  t=(pathlib.Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()
  return {'pid':int(pid),'start_ticks':t[19],'state':t[0],'parent_pid':int(t[1]),'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
 except (FileNotFoundError,ProcessLookupError):return None
def validate_grant(package=D,now=None):
 package=pathlib.Path(package);p=package/'ROOT_CAPTURE_APPROVAL.json';need(p.is_file(),'ROOT_CAPTURE_APPROVAL absent; candidate NOT_ARMED')
 g=json.loads(p.read_text());now=time.time()if now is None else now
 need(g.get('schema')=='CLOCK7390_ROOT_PRIVATE_CAPTURE_APPROVAL_V2'and g.get('approved')is True and g.get('action')==ACTION,'Root approval/action')
 need(g.get('queue_id')==QUEUE_ID and g.get('asset_id')==ASSET and g.get('binary_sha256')==BINARY_SHA and g.get('producer_sha256')==SO_SHA,'exact approval scope')
 need(type(g.get('expires_unix'))in [int,float]and math.isfinite(g['expires_unix'])and g['expires_unix']-now>=60,'approval expiry')
 need(g.get('GPU_executions_max')==1 and g.get('window_seconds_max')==900 and g.get('capture_seconds_max')==120 and g.get('payload_bytes_max')==1073741824,'approval finite limits')
 need(g.get('source_QA_only')is True and g.get('science_qualification_granted')is False and g.get('native_controller_idle_boundary_and_leases_verified')is True,'Root idle/lease and qualification boundary')
 pins=package/'PROFILE_PINS_V2.json';need(pins.is_file()and sha(pins)==g.get('profile_pins_sha256'),'Root profile pin')
 tab=json.loads(pins.read_text());need(tab['schema']=='CLOCK7390_EXACT_PROFILE_PINS_V2','profile schema')
 required={'capture_clock7390_worker_candidate_v2.py','producer_warpsync_clock_input_v2.so','CAPTURE_JOB_CLOCK7390_V2.json','CLOCK_EXACT_JOB.json','CLOCK_STATIC_MANIFEST.json','CLOCK_SEMANTIC_MAP.tsv','CLOCK_SOURCE_ORACLE_V1.json','CLOCK_EXPECTED_HTOD_2048.bin','clock_record_consumer_v2.py','qualify_clock_input_capsule_v2.py','qualify_clock_source_qa_v2.py','remote_watchdog_clock_candidate_v2.py','ELF_RUNTIME_PINS_V2.json','SOURCE_FREEZE_V2.json','OFFLINE_BUILD_RESULT_V2.json'}
 need(set(tab['files'])==required,'complete exact profile member set required')
 for name,h in tab['files'].items():
  need(pathlib.PurePosixPath(name).name==name,'unsafe fixed package member');need((package/name).is_file()and not(package/name).is_symlink()and sha(package/name)==h,'profile file changed '+name)
 need(tab['files'].get('capture_clock7390_worker_candidate_v2.py')==sha(package/'capture_clock7390_worker_candidate_v2.py'),'worker self pin')
 need(sha(package/'producer_warpsync_clock_input_v2.so')==SO_SHA,'new producer changed')
 job=json.loads((package/'CAPTURE_JOB_CLOCK7390_V2.json').read_text());need(job['id']==ASSET and job['original_queue_id']==QUEUE_ID and job['task']['binary_sha256']==BINARY_SHA,'fixed job binding')
 need(job['task']['argv']==['/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/source/cuda-samples-11.8/Samples/0_Introduction/clock/clock'],'fixed original argv')
 return g,job,tab
def supervisor_proof(tab):
 parent=ident(os.getppid());need(parent is not None,'supervisor missing')
 path=D/'remote_watchdog_clock_candidate_v2.py';need(sha(path)==tab['files'][path.name],'watchdog source changed')
 args=(pathlib.Path('/proc')/str(parent['pid'])/'cmdline').read_bytes().split(b'\0')
 need(str(path).encode()in args,'scoped heartbeat/subreaper supervisor required')
 return parent
def preflight_sources(job):
 oracle=json.loads((D/'CLOCK_SOURCE_ORACLE_V1.json').read_text())
 need(sha(pathlib.Path(job['task']['argv'][0]))==BINARY_SHA,'current exact application changed')
 for r in oracle['source_file_refs']:
  p=pathlib.Path(r['path']);need(p.is_file()and p.stat().st_size==r['bytes']and sha(p)==r['sha256'],'source/helper bytes drift')
 deps=json.loads((D/'ELF_RUNTIME_PINS_V2.json').read_text())
 for r in deps['needed']:
  p=pathlib.Path(r['path']);need(p.is_file()and p.stat().st_size==r['bytes']and sha(p)==r['sha256'],'runtime dependency drift')
 return oracle,deps
def gpu_query(fields,kind='gpu'):
 args=['nvidia-smi']
 if kind=='gpu':args+=['--id='+UUID]
 args+=['--query-'+kind+'='+fields,'--format=csv,noheader,nounits']
 r=subprocess.run(args,capture_output=True,text=True,timeout=10);need(r.returncode==0,'GPU guard query failure');return [s.strip()for s in r.stdout.splitlines()if s.strip()]
def processes():
 out={}
 for line in gpu_query('pid,process_name,used_memory','compute-apps'):
  x=[z.strip()for z in line.split(',')];need(len(x)==3,'GPU process query grammar');pid=int(x[0]);proof=ident(pid);need(proof is not None,'compute identity disappeared');out[pid]={'proof':proof,'name':x[1],'mib':float(x[2])}
 return out
def check_resident_pmon(text,baseline):
 for line in text.splitlines():
  t=line.split()
  if len(t)>3 and t[1].isdigit()and int(t[1])in baseline:need(t[3]in ['0','-'],'resident became GPU-active; stop only owned capture')
def resident_activity_guard(baseline):
 r=subprocess.run(['nvidia-smi','pmon','-c','1','-s','u'],capture_output=True,text=True,timeout=10);need(r.returncode==0,'resident activity guard query failure');check_resident_pmon(r.stdout,baseline)
def gpu_state():
 lines=gpu_query('uuid,utilization.gpu,memory.free');need(len(lines)==1,'single GPU guard')
 p=[x.strip()for x in lines[0].split(',')];need(p[0]==UUID,'wrong GPU UUID');return float(p[1]),float(p[2])
def floor():
 need(min(shutil.disk_usage('/data/c16').free,shutil.disk_usage(D).free)>=5*1024**3,'5GiB Native/NAS floor')
def capture_child_limits():
 os.nice(0);os.sched_setaffinity(0,{0,1});resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_FSIZE,(67108864,67108864))
def cpu_limits():
 resource.setrlimit(resource.RLIMIT_AS,(2147483648,2147483648));resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.sched_setaffinity(0,{0,1})
def stop_owned(p,proof):
 if p.poll()is not None:return
 current=ident(p.pid);need(current is not None and current['start_ticks']==proof['start_ticks'],'capture PID reused; supervisor attention required')
 fd=os.pidfd_open(p.pid,0)
 try:
  current=ident(p.pid);need(current is not None and current['start_ticks']==proof['start_ticks'],'capture identity changed')
  signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
  try:p.wait(timeout=3)
  except subprocess.TimeoutExpired:signal.pidfd_send_signal(fd,signal.SIGKILL,None,0);p.wait(timeout=3)
 finally:os.close(fd)
def sample_maps(pid,proof,seen,required):
 current=ident(pid)
 if current is None or current['start_ticks']!=proof['start_ticks']:return
 try:lines=(pathlib.Path('/proc')/str(pid)/'maps').read_text().splitlines()
 except(FileNotFoundError,ProcessLookupError):return
 for line in lines:
  parts=line.split(maxsplit=5)
  if len(parts)<6 or not parts[5].startswith('/')or parts[5].endswith(' (deleted)'):continue
  raw=parts[5];p=pathlib.Path(raw)
  if not p.is_file():continue
  resolved=str(p.resolve());record=seen.setdefault(resolved,{'path':resolved,'first_observed_unix':time.time(),'size':p.stat().st_size,'scope':'sampled primary process host map, not every transient DSO/module'})
  if resolved in required and 'sha256'not in record:
   h=sha(p);need(h==required[resolved],'observed required host image SHA mismatch');record['sha256']=h
def capture(job_argument=None):
 # Approval and every immutable package pin close before any GPU guard call.
 g,job,tab=validate_grant()
 need(not(D/'capture_attempts'/ASSET).exists(),'existing attempt retained; no retry or overwrite')
 if job_argument is not None:need(pathlib.Path(job_argument).resolve()==(D/'CAPTURE_JOB_CLOCK7390_V2.json').resolve(),'no alternate job argument')
 need(D.resolve().is_relative_to(pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080/private_candidates').resolve()),'NAS mirror required')
 parent=supervisor_proof(tab);oracle,deps=preflight_sources(job)
 os.nice(15);os.sched_setaffinity(0,{0,1});resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 deadline=time.monotonic()+min(900,g['expires_unix']-time.time());floor();p=None;proof=None;owned_attempt=False;attempt=D/'capture_attempts'/ASSET;attempt.parent.mkdir(exist_ok=True)
 lease_io=open('/data/c16/rtx4080_suite_fill_20261024_v1/control/RTX4080_LOCAL_IO.lock','r+');lease_gpu=None
 try:
  fcntl.flock(lease_io,fcntl.LOCK_EX|fcntl.LOCK_NB)
  lease_gpu=open('/data/c16/locks/c16_gpu_campaign.lock','r+');fcntl.flock(lease_gpu,fcntl.LOCK_EX|fcntl.LOCK_NB)
  baseline=processes()
  for pid,x in baseline.items():
   cmd=(pathlib.Path('/proc')/str(pid)/'cmdline').read_bytes().replace(b'\0',b' ').decode()
   need('/home/huangrulin/workspace/image-lab/app/ComfyUI/main.py'in cmd,'foreign compute process')
  stable=0;idle_deadline=min(deadline,time.monotonic()+180)
  while stable<15:
   need(time.monotonic()<idle_deadline,'finite idle window failed');floor();current=processes();need(set(current)==set(baseline),'new compute before capture')
   for pid,x in current.items():need(x['proof']['start_ticks']==baseline[pid]['proof']['start_ticks']and x['mib']<=baseline[pid]['mib']+256,'resident identity/VRAM changed')
   util,free=gpu_state();need(free>=1024,'GPU headroom <1GiB');stable=stable+1 if util==0 else 0;time.sleep(1)
  attempt.mkdir(exist_ok=False);owned_attempt=True;(attempt/'tmp').mkdir();(attempt/'cuda_cache').mkdir()
  save(attempt/'CAPTURE_JOB.json',job);save(attempt/'ROOT_APPROVAL_FROZEN.json',g);save(attempt/'SOURCE_ORACLE_FROZEN.json',oracle)
  save(attempt/'WORKER_START.json',{'worker':ident(os.getpid()),'supervisor':parent,'approval_sha256':sha(D/'ROOT_CAPTURE_APPROVAL.json'),'profile_pins_sha256':sha(D/'PROFILE_PINS_V2.json'),'source_KEEP':True,'science_qualified':False})
  need(sha(pathlib.Path(job['task']['argv'][0]))==BINARY_SHA and sha(D/'producer_warpsync_clock_input_v2.so')==SO_SHA,'last prelaunch source/tool check')
  env={k:v for k,v in os.environ.items()if k in ['HOME','USER','LOGNAME','LANG','LC_ALL','TZ']}
  env.update(PATH='/usr/local/cuda-12.8/bin:/usr/bin:/bin',TMPDIR=str(attempt/'tmp'),TMP=str(attempt/'tmp'),TEMP=str(attempt/'tmp'),CUDA_CACHE_PATH=str(attempt/'cuda_cache'),CUDA_CACHE_MAXSIZE='67108864',CUDA_VISIBLE_DEVICES=UUID,LD_PRELOAD=str(D/'producer_warpsync_clock_input_v2.so')+':libcuda.so.1',ADA_SEMANTIC_MAP=str(D/'CLOCK_SEMANTIC_MAP.tsv'),TRACES_FOLDER=str(attempt),ADA_INPUT_SNAPSHOT='1',ADA_INPUT_MAX_COPY_BYTES='2048',ADA_INPUT_MAX_TOTAL_BYTES='2048',ACTIVE_FROM_START='1',TRACE_FILE_COMPRESS='1',TOOL_COMPRESS='1',DYNAMIC_KERNEL_RANGE='',INSTR_BEGIN='0',INSTR_END='4294967295',C16_EXACT_ROOT_FUNCTION_ONLY='0',C16_USE_NVBIT_STATIC_INDEX='0',ENABLE_SPINLOCK_FAST_FORWARD='0',SPINLOCK_ITER_TO_KEEP='1',TERMINATE_UPON_LIMIT='0',TRACE_LINEINFO='0',EXCLUDE_PRED_OFF='1',TOOL_VERBOSE='0',TOOL_TRACE_CORE='0',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',NVDISASM='/usr/local/cuda-12.8/bin/nvdisasm')
  required={str(pathlib.Path(r['path']).resolve()):r['sha256']for r in deps['needed']};required[str(pathlib.Path(job['task']['argv'][0]).resolve())]=BINARY_SHA;required[str((D/'producer_warpsync_clock_input_v2.so').resolve())]=SO_SHA;seen={}
  with(attempt/'stdout.log').open('xb')as out,(attempt/'stderr.log').open('xb')as err:
   started=time.time();p=subprocess.Popen(job['task']['argv'],cwd=attempt,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True,preexec_fn=capture_child_limits);proof=ident(p.pid);need(proof is not None,'capture exited before identity receipt')
   save(attempt/'PROCESS_START.json',{'capture_pid':p.pid,'capture_start_ticks':proof['start_ticks'],'worker':ident(os.getpid()),'supervisor':parent,'producer_sha256':SO_SHA,'binary_sha256':BINARY_SHA,'started_unix':started})
   capture_deadline=min(deadline,time.monotonic()+120);peak=0
   while p.poll()is None:
    need(time.monotonic()<capture_deadline,'capture absolute time cap');floor();need(sum(x.stat().st_size for x in attempt.rglob('*')if x.is_file())<=1073741824,'private payload cap')
    current=processes();need(set(current)<=set(baseline)|{p.pid},'new foreign GPU compute')
    for pid,x in baseline.items():
     need(pid in current and current[pid]['proof']['start_ticks']==x['proof']['start_ticks']and current[pid]['mib']<=x['mib']+256,'resident changed during capture')
    if p.pid in current:peak=max(peak,current[p.pid]['mib']);need(peak<=2048,'private GPU peak cap')
    resident_activity_guard(baseline);need(gpu_state()[1]>=512,'GPU free below512MiB');sample_maps(p.pid,proof,seen,required);time.sleep(.2)
   rc=p.wait()
  save(attempt/'EXECUTION.json',{'kind':'instrumented','job_id':ASSET,'tool_sha256':SO_SHA,'binary_sha256':BINARY_SHA,'capture_pid':p.pid,'capture_start_ticks':proof['start_ticks'],'started_unix':started,'exit_code':rc,'elapsed_seconds':time.time()-started,'GPU_peak_MiB':peak,'numerical_reference_pass':False,'numerical_status':'TIMING_PROBE_NO_RESULT_REFERENCE','source_KEEP':True})
  save(attempt/'SAMPLED_HOST_MAPS_V1.json',{'schema':'CLOCK7390_SAMPLED_HOST_MAPS_V1','samples':list(seen.values()),'required':required,'not_all_transient_DSO_or_device_module_coverage':True})
  need(rc==0,'application failed');need(all(path in seen and seen[path].get('sha256')==h for path,h in required.items()),'required actual host mappings not all sampled/verified')
  need(time.monotonic()<deadline,'whole worker deadline');need(sha(pathlib.Path(job['task']['argv'][0]))==BINARY_SHA and sha(D/'producer_warpsync_clock_input_v2.so')==SO_SHA,'post-capture executable/tool drift')
  cpuenv={'PATH':'/usr/bin:/bin','PYTHONDONTWRITEBYTECODE':'1','TMPDIR':str(attempt/'tmp'),'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
  with(attempt/'SOURCE_QA.stdout.log').open('xb')as out,(attempt/'SOURCE_QA.stderr.log').open('xb')as err:
   cp=subprocess.run(['/usr/bin/python3','-B',str(D/'qualify_clock_source_qa_v2.py'),str(attempt)],cwd=attempt,env=cpuenv,stdin=subprocess.DEVNULL,stdout=out,stderr=err,timeout=min(180,max(1,deadline-time.monotonic())),preexec_fn=cpu_limits)
  need(cp.returncode==0,'strict SourceQA failed; preserve private source')
  result=json.loads((attempt/'CLOCK_SOURCE_QA_RESULT_V2.json').read_text());need(result['trace_qualified']is False and result['science_qualified']is False,'SourceQA overclaim')
  save(attempt/'PRIVATE_WORKER_COMPLETE_V2.json',{'status':'PRIVATE_CLOCK_SOURCE_QA_COMPLETE_PENDING_ROOT_INDEPENDENT_REVIEW','result_sha256':sha(attempt/'CLOCK_SOURCE_QA_RESULT_V2.json'),'worker':ident(os.getpid()),'source_KEEP':True,'catalog_or_queue_publication':False,'trace_or_science_qualification_granted':False})
  print(json.dumps({'status':'PRIVATE_CLOCK_SOURCE_QA_COMPLETE_PENDING_ROOT_REVIEW','attempt':str(attempt),'source_KEEP':True,'trace_qualified':False}),flush=True)
 except BaseException as ex:
  if p is not None and proof is not None:stop_owned(p,proof)
  if owned_attempt and attempt.is_dir()and not(attempt/'FAILURE_RETAINED.json').exists():save(attempt/'FAILURE_RETAINED.json',{'error':repr(ex),'worker':ident(os.getpid()),'source_KEEP':True,'retry_automatic':False,'unix':time.time()})
  raise
 finally:
  if lease_gpu is not None:lease_gpu.close()
  lease_io.close()
def main():
 if sys.argv[1:]==['--describe']:
  print(json.dumps({'asset_id':ASSET,'queue_id':QUEUE_ID,'profile':'CLOCK7390_ONLY_NEW_ADA8_HTOD_SOURCEQA','Root_approval_required':True,'runnable_without_Root_approval':False,'new_SO_loaded_or_GPU_queried':False}));return
 # Positional fixed job is the unchanged supervisor protocol; no generic command.
 need(len(sys.argv)==2,'only --describe or exact fixed job path under scoped supervisor')
 capture(sys.argv[1])
if __name__=='__main__':main()
