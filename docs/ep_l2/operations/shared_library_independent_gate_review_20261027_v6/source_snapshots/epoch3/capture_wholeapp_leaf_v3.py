#!/usr/bin/env python3
"""Fixed old SDK42 whole-app capture only. No import-time GPU activity."""
import pathlib,os,sys,json,hashlib,time,subprocess,fcntl,shutil,resource,re
if sys.flags.optimize:raise RuntimeError('optimized Python unsupported')

D=pathlib.Path(__file__).resolve().parent
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1')
NAS=R/'nas_rtx4080'
REMOTE=NAS/'private_candidates/simpletemplates_epoch8_exact_leaf_prepare_20261027_v3'
PROFILE='SDK42_SIMPLETEMPLATES_EPOCH8_EXACT_V3'
BINARY=pathlib.Path('/home/huangrulin/workspace/rtx4080_cuda_polybench_20261024_v1/bin/sdk42_v3_simpleTemplates')
def need(x,msg):
 if not x:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(p,x):
 with pathlib.Path(p).open('x') as f:json.dump(x,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def ticks(pid):
 try:return pathlib.Path('/proc',str(pid),'stat').read_text().split(') ',1)[1].split()[19]
 except FileNotFoundError:return None
def verify_ref(r):
 p=pathlib.Path(r['path']);need(p.is_file() and not p.is_symlink() and sha(p)==r['sha256'],'fresh file ref mismatch');return p
def grant(job):
 p=D/'ROOT_EXACT_CAPTURE_GRANT.json';need(sha(p)==job['grant_sha256'],'Root grant pin')
 a=json.loads(p.read_text());now=time.time()
 need(a['schema']=='EPOCH8_ROOT_EXACT_CAPTURE_GRANT_V3' and a['approved'] is True and a['profile']==PROFILE,'exact Root grant')
 need(0<a['absolute_deadline_unix']-a['not_before_unix']<=600 and a['not_before_unix']<=now<a['absolute_deadline_unix']-60,'Root absolute600s')
 need(a['release_manifest_sha256']==sha(D/'RELEASE_CODE_MANIFEST.json'),'release manifest pin')
 manifest=json.loads((D/'RELEASE_CODE_MANIFEST.json').read_text())
 for r in manifest['files']:
  p=D/r['relative'];need(p.resolve().is_relative_to(D.resolve()) and p.is_file() and not p.is_symlink() and sha(p)==r['sha256'],'release changed')
 runtime=json.loads(verify_ref(a['runtime_admission_ref']).read_text())
 need(runtime['schema']=='EPOCH8_FRESH_RUNTIME_ADMISSION_V3' and runtime['profile']==PROFILE and runtime['expires_unix']>now and 0<=now-runtime['created_unix']<=30 and 0<runtime['expires_unix']-runtime['created_unix']<=30,'fresh runtime scope/TTL')
 need(runtime['binary_sha256']==sha(BINARY)==job['binary_sha256'],'binary runtime drift')
 for r in job['source_files']:verify_ref(r)
 need(runtime['source_files']==job['source_files'],'exact source runtime refs')
 need(runtime['foreign_registry_snapshot_refs'],'missing all-foreign registry snapshots')
 for r in runtime['foreign_registry_snapshot_refs']:verify_ref(r)
 need(runtime['foreign_reservations_reported'] is True and runtime['native_physical_floor_bytes']>=5*1024**3,'foreign reservations/floor admission')
 need(runtime['elf_and_disk_libraries_only'] is True and runtime['loaded_gpu_modules_claimed'] is False,'runtime provenance scope')
 need(runtime['resolved_library_refs'],'empty exact library baseline')
 for r in runtime['resolved_library_refs']:verify_ref(r)
 return a,runtime
def query():
 p=subprocess.run(['/usr/bin/nvidia-smi','--query-compute-apps=pid,process_name,used_gpu_memory','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5)
 need(p.returncode==0,'bounded GPU query failed')
 rows=[]
 for line in p.stdout.splitlines():
  z=[v.strip() for v in line.split(',')];need(len(z)==3 and z[0].isdigit(),'unknown query output')
  rows.append(dict(pid=int(z[0]),name=z[1],memory_mib=float(z[2]),start_ticks=ticks(int(z[0]))))
 return rows
def pmon_idle_evidence(text,expected,owned_pid=None):
 header=None;observed={}
 for line in text.splitlines():
  fields=line.split()
  if not fields:continue
  if fields[0]=='#':
   cols=fields[1:]
   if cols and cols[0]=='gpu':
    need(header is None,'duplicate pmon header')
    need(cols[:3]==['gpu','pid','type'] and cols[-1]=='command','unknown pmon header')
    engines=cols[3:-1]
    need(engines[:2]==['sm','mem'] and len(set(engines))==len(engines) and set(engines)<=set(['sm','mem','enc','dec','jpg','ofa']),'unknown pmon activity columns')
    header=cols
   continue
  need(header is not None and len(fields)>=len(header),'pmon data without complete header')
  need(re.fullmatch(r'0|[1-9][0-9]*',fields[0]),'pmon GPU index')
  # NVIDIA empty-device row has no PID/type/activity. It proves no knownPID idle state.
  if fields[1]=='-':
   need(all(v=='-' for v in fields[1:]),'malformed empty pmon row');continue
  need(re.fullmatch(r'[1-9][0-9]*',fields[1]) and fields[2] in ('C','G','C+G'),'unknown pmon PID/type')
  pid=int(fields[1])
  if pid==owned_pid:continue
  need(pid in expected,'foreign pmon process')
  need(pid not in observed,'duplicate/conflicting known pmon row')
  util=fields[3:len(header)-1]
  need(all(re.fullmatch(r'0|[1-9][0-9]*',v) and int(v)<=100 for v in util),'unknown/unavailable pmon activity')
  need(all(int(v)==0 for v in util),'knownresident active')
  observed[pid]=dict(type=fields[2],activity=dict(zip(header[3:-1],map(int,util))))
 need(header is not None and set(observed)==set(expected),'missing knownresident activity evidence')
 return observed
def residents(a,owned_pid=None):
 expected={x['pid']:x for x in a['known_residents']};need(len(expected)==len(a['known_residents']),'duplicate knownresident grant')
 actual=query();need(len({x['pid'] for x in actual})==len(actual),'duplicate compute query PID')
 for x in actual:
  if x['pid']==owned_pid:continue
  need(x['pid'] in expected,'foreign GPU process')
  e=expected[x['pid']]
  need(x['start_ticks']==e['start_ticks'] and x['name']==e['name'] and x['memory_mib']<=e['memory_mib']+64,'knownresident changed')
 need({x['pid'] for x in actual if x['pid']!=owned_pid}==set(expected),'knownresident missing/changed')
 p=subprocess.run(['/usr/bin/nvidia-smi','pmon','-c','1','-s','u'],capture_output=True,text=True,timeout=5)
 need(p.returncode==0,'bounded pmon failed')
 evidence=pmon_idle_evidence(p.stdout,expected,owned_pid)
 for x in actual:
  if x['pid'] in evidence:x['pmon_zero_activity_evidence']=evidence[x['pid']]
 return actual
def main():
 os.umask(0o077)
 os.setpriority(os.PRIO_PROCESS,0,15);os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2]);resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_FSIZE,(16*1024**2,16*1024**2))
 need(D.resolve()==REMOTE.resolve(),'fixed remote release')
 job=json.loads(pathlib.Path(sys.argv[1]).read_text());a,rt=grant(job) # Must precede every GPU query.
 need(job['id']=='SDK42_SIMPLETEMPLATES_EPOCH8_EXACT_V3_SINGLE','single fixed scope')
 root=D/'runs'/job['id'];root.mkdir(parents=True,exist_ok=False);save(root/'ROOT_GRANT_FROZEN.json',a);save(root/'RUNTIME_ADMISSION_FROZEN.json',rt)
 for disk in (R,NAS):need(shutil.disk_usage(disk).free>=5*1024**3,'physical5GiB floor')
 locks=[]
 try:
  for p in [R/'control/RTX4080_LOCAL_IO.lock',pathlib.Path('/data/c16/locks/c16_gpu_campaign.lock')]:
   f=p.open('r+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
  uu=subprocess.run(['/usr/bin/nvidia-smi','--query-gpu=uuid','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5)
  need(uu.returncode==0 and uu.stdout.strip()==a['gpu_uuid']==rt['gpu_uuid'],'exact GPU UUID admission')
  baseline=residents(a);save(root/'PRE_GPU_RESIDENTS.json',baseline)
  env={k:v for k,v in os.environ.items() if k not in ('LD_PRELOAD','CUDA_INJECTION64_PATH') and not k.startswith(('ADA_','TRACE_','NVBIT_','TOOL_','INSTR_','C16_','DYNAMIC_'))}
  env.update(LD_PRELOAD=str(D/'candidate/producer_epoch8_candidate.so'),ADA_SEMANTIC_MAP=str(D/'preimages/map/semantic-map.tsv'),TRACES_FOLDER=str(root),CUDA_VISIBLE_DEVICES='0',TRACE_FILE_COMPRESS='1',TOOL_COMPRESS='1',ACTIVE_FROM_START='1',INSTR_BEGIN='0',INSTR_END='4294967295',EXCLUDE_PRED_OFF='0',ENABLE_SPINLOCK_FAST_FORWARD='0',TERMINATE_UPON_LIMIT='0',C16_EXACT_ROOT_FUNCTION_ONLY='0',C16_USE_NVBIT_STATIC_INDEX='0',TRACE_LINEINFO='0',TOOL_TRACE_CORE='0',TOOL_VERBOSE='0')
  started=time.time();mapped=False
  with (root/'stdout.log').open('xb') as out,(root/'stderr.log').open('xb') as err:
   p=subprocess.Popen([str(BINARY)],cwd=root,env=env,stdout=out,stderr=err,start_new_session=True)
   identity=dict(capture_pid=p.pid,capture_start_ticks=ticks(p.pid),boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),started_unix=started)
   save(root/'PROCESS_START.json',identity)
   try:
    while p.poll() is None:
     need(time.time()<min(started+520,a['absolute_deadline_unix']-40),'capture deadline')
     try:
      maps=pathlib.Path('/proc',str(p.pid),'maps').read_text()
      if str(D/'candidate/producer_epoch8_candidate.so') in maps and str(BINARY) in maps:
       if not mapped:save(root/'LOADED_MAPS.json',dict(pid=p.pid,start_ticks=ticks(p.pid),boot_id=identity['boot_id'],maps=maps,producer_sha256=sha(D/'candidate/producer_epoch8_candidate.so'),binary_sha256=sha(BINARY),claim='proc mapped pathname plus separately hashed disk files; not memory-page hash'));mapped=True
     except FileNotFoundError:pass
     residents(a,p.pid)
     need(shutil.disk_usage(R).free>=5*1024**3 and shutil.disk_usage(NAS).free>=5*1024**3,'physical floor')
     need(sum(x.stat().st_size for x in root.rglob('*') if x.is_file())<=1024**3,'1GiB wholeattempt bound')
     time.sleep(.25)
   except BaseException:
    # Guard subreaper performs exact owned cleanup; never signal foreign identities here.
    raise
  need(p.returncode==0 and mapped,'application failed or actual mapped SO/binary evidence absent')
  execution=dict(binary_sha256=job['binary_sha256'],tool_sha256=sha(D/'candidate/producer_epoch8_candidate.so'),exit_code=p.returncode,task=dict(argv=[str(BINARY)]),candidate_profile_id=PROFILE,source_files=job['source_files'],map_manifest_sha256=sha(D/'preimages/map/manifest.json'),process_identity=identity,ended_unix=time.time())
  save(root/'EXECUTION.json',execution)
  refs=['EXECUTION.json','stdout.log','traces/context_lifecycle.jsonl','traces/launch-bindings.jsonl','traces/output-copies.jsonl','traces/loaded-static.tsv','traces/kernel-1-epoch_1.trace.xz','traces/kernel-2-epoch_2.trace.xz','LOADED_MAPS.json']
  save(root/'SOURCE_QA_BOUND.json',dict(schema='EPOCH8_SOURCE_QA_BOUND_V3',producer_sha256=execution['tool_sha256'],file_sha256={r:sha(root/r) for r in refs}))

  post=subprocess.run(['/usr/bin/python3','-B',str(D/'candidate/postprocess_epoch8_app.py'),str(root),str(D/'preimages/map/manifest.json'),str(D/'candidate/PROFILE_CANDIDATE.json')],stdout=(root/'POST.log').open('xb'),stderr=subprocess.STDOUT,timeout=max(1,min(40,a['absolute_deadline_unix']-time.time()-20)),env={k:v for k,v in os.environ.items() if k not in ('LD_PRELOAD','CUDA_INJECTION64_PATH')})
  need(post.returncode==0,'strict postprocessor failed')
  residents(a);save(root/'POST_GPU_RESIDENTS.json',residents(a))
  save(root/'LEAF_RESULT.json',dict(status='PRIVATE_CANDIDATE_CAPTURE_POST_PASS_REQUIRES_RECEIVER',profile=PROFILE,production_trace_qualified=False,science_qualified=False,native_qualified=False,elapsed=time.time()-started))
 finally:
  for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
if __name__=='__main__':main()
