#!/usr/bin/env python3
"""Frozen33 capture-only leaf. Outer guard retains GPU/IO and Native perasset leases."""
import pathlib,os,json,subprocess,time,fcntl,hashlib,signal,re,shutil,sys,traceback
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');N=R/'nas_rtx4080';S=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1')
TOOL=S/'frozen/producer_v7_55c6f482/producer.so';CONTRACT=S/'frozen/ada7_contract_v1';VALIDATOR=R/'control/validate_v7_stream_v3.py';POST=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/control/frozen/post_v4_5d3ffcd3/postprocess_nas_sharded_v4.py');MAPPER=pathlib.Path('/data/c16/ada_trace_extensions_v8_20261024_v1/frozen/mapper_v3_a2e7ee38aa72/make_semantic_map_elf_owner_v3.py')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def ticks(pid):return (pathlib.Path('/proc')/str(pid)/'stat').read_text().split(') ',1)[1].split()[19]
def save(p,o):
 with p.open('x') as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def copy(src,dest):
 dest.parent.mkdir(parents=True,exist_ok=True)
 with src.open('rb') as inp,dest.open('xb') as out:
  for b in iter(lambda:inp.read(1048576),b''):out.write(b)
  out.flush();os.fsync(out.fileno())
 assert sha(src)==sha(dest)
def query(fields,kind='gpu'):
 text=subprocess.check_output(['nvidia-smi','--query-'+kind+'='+fields,'--format=csv,noheader,nounits'],text=True).strip()
 return [x.strip() for x in text.splitlines() if x.strip()]
def procs():return [x.split(', ') for x in query('pid,process_name,used_memory','compute-apps')]
_cp=pathlib.Path(__file__).with_name('ordinary33_common_v1.py');_raw=_cp.read_bytes()
assert hashlib.sha256(_raw).hexdigest()=='1c3e485d9b25783a5bcbcbcba125af625fdf3d9388b7bb5f3b70b67b27ae178d'
C=type(sys)('ordinary33_common');C.__file__=str(_cp);exec(compile(_raw,str(_cp),'exec'),C.__dict__)
code_sha=sys.argv[5];mf=C.code_check(pathlib.Path(__file__).parent,code_sha);scope_path=pathlib.Path(sys.argv[3]);scope_sha=sys.argv[4];scope=C.readref(dict(path=str(scope_path),bytes=scope_path.stat().st_size,sha256=scope_sha));allowlist=json.loads((pathlib.Path(__file__).parent/'ALLOWLIST33.json').read_bytes());C.validate_scope(scope,allowlist)
jid=sys.argv[6];job_meta,limits=C.job_parameters(scope,allowlist,jid);job_path=pathlib.Path(sys.argv[1]);root=pathlib.Path(sys.argv[2])
C.need(pathlib.Path(__file__).resolve().parent==C.RB and job_path==C.RB/job_meta['job_relative']and C.sha(job_path)==job_meta['job_sha256'],'EXACT_FROZEN_JOB')
C.need(root==C.RB/'runs'/scope['campaign_id']/jid/'capture','EXACT_PRIVATE_CAPTURE_ROOT')
Lease,O=C.dependencies(pathlib.Path(__file__).parent,mf);desc=json.loads(os.environ[Lease.ENV]);bindings=dict(Root_sha256=scope_sha,campaign_id=scope['campaign_id'],job_id=jid);leases=Lease.adopt_worker(desc['guard'],bindings);leases.install_child_inheritance();inherited_gpu_and_IO_proven=True
Canon=C.rawmodule(pathlib.Path(__file__).with_name('canonical_comfy_fd_v1.py'),mf['files']['canonical_comfy_fd_v1.py']['sha256'],'canonicalFDleaf')
canonical_inherited=Canon.adopt(json.loads(os.environ[Canon.ENV]),bindings);canonical_inherited.install_child_inheritance()

job=json.loads(job_path.read_bytes());task=job['task'];jobid=job['id'];binary=pathlib.Path(task['argv'][0]);root.mkdir(exist_ok=False)
C.input_libc_identity(task,verify=True)
prior_qa=C.qa_row(scope,job)if scope['queue_stage']=='CAPTURE'else None
shared=None
receipt={'job_id':jobid,'task':task,'started':time.time(),'status':'PREPARING','worker_pid':os.getpid(),'worker_start_ticks':ticks(os.getpid()),'actual_gpu_uuid':'GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59','pipeline_sha256':sha(pathlib.Path(__file__))};gpu=None;io=None;p=None
try:
 assert leases is not None # outer guard owns original GPU and LOCAL_IO OFDs
 assert sha(MAPPER)=='a2e7ee38aa722465250c53096aea50bcd93623fea5b60114486538429dce1f6e'
 assert sha(binary)==task['binary_sha256']
 assert sha(TOOL)=='55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73'
 assert sha(CONTRACT/'CONTRACT.json')=='97901eb373fc94b041c5ef6923e0e5ca1635edd1bac4213d53c28271abb6c184'
 assert sha(VALIDATOR)=='f9f8a05ca7e0f8afe60e7d9a34f4884a9d1cb920b2212e41ed9a4faf19975af1'
 copy(binary,root/'evidence/application');copy(TOOL,root/'evidence/producer.so');copy(MAPPER,root/'evidence/make_semantic_map_elf_owner_v3.py');copy(VALIDATOR,root/'evidence/validate_v7_stream_v3.py')
 for q in CONTRACT.iterdir():
  if q.is_file():copy(q,root/'contract'/q.name)

 LISTER=pathlib.Path('/usr/local/cuda-12.8/bin/cuobjdump')
 assert sha(LISTER)=='9d515ac6f60c246ef63fe87b0a95d209b00ff3e25b716f8f263520010760e8f8'
 listing=subprocess.run([str(LISTER),'-lelf',str(binary)],capture_output=True,text=True,timeout=120)
 assert listing.returncode==0,'STATIC_IMAGE_ENUMERATION_PENDING listing failure'
 names=re.findall(r'^ELF file\s+\d+:\s+(.+)$',listing.stdout,re.M)
 from collections import Counter
 collisions={n:c for n,c in Counter(names).items() if c>1}
 save(root/'STATIC_IMAGE_ENUMERATION_CENSUS.json',{'binary_sha256':sha(binary),'tool_sha256':sha(LISTER),'listing':listing.stdout,'listing_sha256':hashlib.sha256(listing.stdout.encode()).hexdigest(),'cubin_names':names,'duplicate_basenames':collisions,'status':'STATIC_IMAGE_ENUMERATION_PENDING_DUPLICATE_BASENAME' if collisions else 'NO_DUPLICATE_CUBIN_BASENAME_ENUMERATION_PASS','scope':'No-collision census is separate from actual-loaded code and full static-map proof'})
 if collisions:
  save(root/'PENDING_SPECIALIST_EXTENSION.json',{'reason':'STATIC_IMAGE_ENUMERATION_PENDING duplicate cubin basename; frozen mapper xelf-all could overwrite images','source_KEEP':True})
  raise RuntimeError('PENDING_SPECIALIST_EXTENSION STATIC_IMAGE_ENUMERATION_PENDING duplicate basename')

 (root/'map').parent.mkdir(exist_ok=True)
 cp=subprocess.run(['python3',str(MAPPER),str(binary),str(root/'map')],capture_output=True,text=True,timeout=300)
 (root/'MAP_PREFLIGHT.log').write_text(cp.stdout+cp.stderr)
 if cp.returncode:raise RuntimeError('MAP_PREFLIGHT_HOLD '+cp.stderr[-2000:])
 m=json.loads((root/'map/manifest.json').read_text());assert m['binary_sha256']==task['binary_sha256']
 bad=[]
 for ins in m['instructions']:
  toks=ins['sass'].split();op=toks[1] if toks[0].startswith('@') else toks[0]
  if any(op.startswith(x) for x in ['CALL','RET','JMX','BRX','LDGSTS','CPASYNC','TEX','TLD','SULD','SUST','SUATOM','UTMA','WGMMA','WARPSYNC','BAR.WARP']):bad.append({'function':ins['function'],'pc':ins['pc'],'sass':ins['sass']})
 if bad:
  save(root/'PENDING_SPECIALIST_EXTENSION.json',{'unsupported_static_sites':bad,'source_keep':True})
  raise RuntimeError('PENDING_SPECIALIST_EXTENSION static domain')
 (root/'runtime').mkdir();runtime=root/'runtime'
 # Explicit declared runtime data is copied, never a writable symlink to shared inputs.
 declared=task.get('input_files',task.get('input_identity',[]))
 declared=declared if isinstance(declared,list) else []
 staged=[]
 for x in task.get('runtime_links',[]):
  rel=x.get('link',x.get('name'));source=pathlib.Path(x.get('target',x.get('source')));dest=runtime/rel
  assert runtime.resolve() in dest.resolve().parents
  if source.is_dir():
   dest.mkdir(parents=True,exist_ok=False)
   relevant=[v for v in declared if source.resolve() in pathlib.Path(v['path']).resolve().parents]
   assert relevant,'runtime directory has no declared input files'
   for v in relevant:
    original=pathlib.Path(v['path']);assert sha(original)==v['sha256']
    target=dest/original.resolve().relative_to(source.resolve());copy(original,target)
    staged.append({'source':str(original),'member':str(target.relative_to(root)),'sha256':v['sha256']})
  else:
   expected=next(v['sha256'] for v in declared if pathlib.Path(v['path']).resolve()==source.resolve())
   assert sha(source)==expected;copy(source,dest)
   staged.append({'source':str(source),'member':str(dest.relative_to(root)),'sha256':expected})
 for v in declared:
  assert sha(pathlib.Path(v['path']))==v['sha256']
 save(root/'INPUT_STAGING.json',{'policy':'ONLY_MANIFEST_DECLARED_REGULAR_FILES;PRIVATE_COPIES','files':staged,'absolute_input_files_verified':len(declared)})
 env=os.environ.copy();env.update(task.get('runtime_env',{}));env.update(task.get('env',{}))
 for k in list(env):
  if k.startswith(('TRACE_','TOOL_','DYNAMIC_','NVBIT_','C16_')) or k in ['LD_PRELOAD','CUDA_INJECTION64_PATH','ACTIVE_FROM_START']:env.pop(k,None)
 env.update(LD_PRELOAD=str(TOOL)+':libcuda.so.1',ADA_SEMANTIC_MAP=str(root/'map/semantic-map.tsv'),TRACES_FOLDER=str(root),ACTIVE_FROM_START='1',TRACE_FILE_COMPRESS='1',TOOL_COMPRESS='1',DYNAMIC_KERNEL_RANGE='',PATH='/usr/local/cuda-12.8/bin:'+env.get('PATH',''),NVDISASM='/usr/local/cuda-12.8/bin/nvdisasm',CUDA_VISIBLE_DEVICES='GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
 tracer_flags={'INSTR_BEGIN': '0', 'INSTR_END': '4294967295', 'C16_EXACT_ROOT_FUNCTION_ONLY': '0', 'C16_USE_NVBIT_STATIC_INDEX': '0', 'ENABLE_SPINLOCK_FAST_FORWARD': '0', 'SPINLOCK_ITER_TO_KEEP': '1', 'TERMINATE_UPON_LIMIT': '0', 'TRACE_LINEINFO': '0', 'EXCLUDE_PRED_OFF': '1', 'TOOL_VERBOSE': '0', 'TOOL_TRACE_CORE': '0'}
 env.update(tracer_flags);receipt['tracer_control_flags']=tracer_flags
 if scope['queue_stage']=='NATIVE_QA':
  for k in list(env):
   if k.startswith(('TRACE_','TOOL_','DYNAMIC_','NVBIT_','C16_','ADA_','CUDA_INJECTION'))or k in ['LD_PRELOAD','LD_AUDIT','CUDA_INJECTION64_PATH','ACTIVE_FROM_START','TRACES_FOLDER']:env.pop(k,None)
  receipt['tracer_control_flags']={};receipt['native_QA_no_injection']=True
 limits={'capture_timeout_sec':min(limits['capture_timeout_sec'],int(scope['queue_absolute_deadline_unix']-time.time()-30)),'capture_max_bytes':limits['capture_max_bytes']};assert limits['capture_timeout_sec']>0;receipt['capture_limits']=limits
 assert inherited_gpu_and_IO_proven # no second acquisition and no leaf LOCK_UN
 baseline=procs()
 r=scope.get('Root_known_comfy_nonperformance_policy_ref')
 if r is not None:
  mod=C.rawmodule(pathlib.Path(__file__).with_name('known_comfy_policy_v1.py'),mf['files']['known_comfy_policy_v1.py']['sha256'],'RootKnownComfy')
  policy=C.readref(dict(path=r['remote_path'],bytes=r['bytes'],sha256=r['sha256']));shared=mod.Policy(policy,scope)
  assert query('uuid')==[policy['gpu_uuid']],'exact target GPU UUID'
  shared.validate_compute(baseline);allowed={shared.pid}
 else:
  allowed={int(x[0]) for x in baseline}
  assert all(x[1]=='/home/huangrulin/workspace/image-lab/envs/comfyui/bin/python' for x in baseline)
 for pid in allowed:assert '/home/huangrulin/workspace/image-lab/app/ComfyUI/main.py' in (pathlib.Path('/proc')/str(pid)/'cmdline').read_bytes().replace(b'\0',b' ').decode()
 base_mem={int(x[0]):float(x[2]) for x in baseline};base_ticks={pid:ticks(pid) for pid in allowed};receipt['resident_baseline']={'processes':baseline,'start_ticks':base_ticks};stable=0;deadline=time.monotonic()+180
 while stable<15:
  assert time.monotonic()<deadline,'bounded readiness window'
  if shared is not None:
   pm=subprocess.run(['nvidia-smi','pmon','-c','1','-s','u'],capture_output=True,text=True,timeout=10);assert pm.returncode==0,'pmon query failed'
   current_free=float(query('memory.free')[0])
   try:shared.observe(procs(),pm.stdout,current_free);stable+=1
   except ValueError as e:
    if str(e)=='LOW_VRAM_RESERVE':stable=0
    else:raise
  else:
   assert all(int(x[0]) in allowed for x in procs()),'new compute before capture'
   util=float(query('utilization.gpu')[0]);stable=stable+1 if util==0 else 0
  time.sleep(1)
 free=float(query('memory.free')[0]);assert free>=1024,'GPU free headroom<1GiB'
 receipt['gpu_free_mib_before']=free;receipt['gpu_before']=query('name,uuid,driver_version,memory.total,memory.free')
 assert sha(binary)==task['binary_sha256']
 start=time.monotonic();peak=0.;min_free=free;mon=[]
 with (root/'stdout.log').open('x') as out,(root/'stderr.log').open('x') as err:
  assert time.time()<scope['queue_absolute_deadline_unix']-10,'fresh original deadline before app'
  p=subprocess.Popen(task['argv'],cwd=runtime,env=env,stdout=out,stderr=err,start_new_session=True,preexec_fn=lambda:os.nice(15));subprocess.run(['ionice','-c','2','-n','7','-p',str(p.pid)],capture_output=True)
  receipt.update(capture_pid=p.pid,capture_start_ticks=ticks(p.pid));save(root/'PROCESS_START.json',receipt)
  while p.poll() is None:
   seen=procs()
   if shared is not None:
    for x in seen:
     if int(x[0])==p.pid:peak=max(peak,float(x[2]))
    pm=subprocess.run(['nvidia-smi','pmon','-c','1','-s','u'],capture_output=True,text=True,timeout=10)
    try:
     assert pm.returncode==0,'pmon query failed'
     shared.observe(seen,pm.stdout,float(query('memory.free')[0]),p.pid)
    except (ValueError,AssertionError) as e:receipt['bounded_stop']='shared_known_GPU_protection '+str(e)
   else:
    for x in seen:
     pid=int(x[0]);mem=float(x[2])
     if pid not in allowed|{p.pid}:receipt['bounded_stop']='new compute '+str(x)
     if pid==p.pid:peak=max(peak,mem)
     if pid in allowed and (ticks(pid)!=base_ticks[pid] or mem>base_mem[pid]+64):receipt['bounded_stop']='resident changed or VRAM growth '+str(x)
    pm=subprocess.run(['nvidia-smi','pmon','-c','1','-s','u'],capture_output=True,text=True,timeout=10)
    for line in pm.stdout.splitlines():
     t=line.split()
     if len(t)>3 and t[1].isdigit() and int(t[1]) in allowed and t[3] not in ['0','-']:receipt['bounded_stop']='resident active '+line
   current_free=float(query('memory.free')[0]);min_free=min(min_free,current_free)
   if current_free<512:receipt['bounded_stop']='GPU free headroom<512MiB'
   if time.monotonic()-start>limits['capture_timeout_sec']or time.time()>=scope['queue_absolute_deadline_unix']-10:receipt['bounded_stop']='capture wall bound'
   size=sum(x.stat().st_size for x in root.rglob('*') if x.is_file())
   if size>limits['capture_max_bytes']:receipt['bounded_stop']='capture byte bound'
   if shutil.disk_usage(root).free<20*1024**3:receipt['bounded_stop']='NAS free reserve<20GiB'
   if receipt.get('bounded_stop') and p.poll() is None:
    os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(timeout=10)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   time.sleep(.2)
  out.flush();os.fsync(out.fileno());err.flush();os.fsync(err.fileno())
 if shared is not None:receipt['known_GPU_shared_nonperformance_telemetry']=shared.summary()
 receipt.update(exit_code=p.returncode,capture_elapsed_s=time.monotonic()-start,peak_observed_gpu_mib=peak,min_observed_gpu_free_mib=min_free,binary_sha256=sha(binary),tool_sha256=sha(TOOL),ended=time.time())
 # Outer guard retains GPU and LOCAL_IO through all owned cleanup.
 assert receipt['binary_sha256']==m['binary_sha256']
 save(root/'EXECUTION.json',receipt)
 assert p.returncode in job.get('allowed_capture_exits',[0]) and not receipt.get('bounded_stop'),'capture did not reach declared completion'
 stdout=(root/'stdout.log').read_text(errors='replace')
 parsed=C.profile_stdout(job,stdout)
 if scope['queue_stage']=='NATIVE_QA':
  save(root/'NATIVE_QA_RESULT.json',dict(schema='REPEAT_ONLY4_REAL_NATIVE_QA_RESULT_V1',status='NATIVE_QA_PASS_NOT_CAPTURED',job_id=jobid,argv=task['argv'],binary_sha256=task['binary_sha256'],libc_sha256=C.input_libc_identity(task),parsed_profile=parsed,exit_code=p.returncode,no_tracer_injection=True,stdout_ref=C.ref(root/'stdout.log'),execution_ref=C.ref(root/'EXECUTION.json'),scope_sha256=scope_sha,code_manifest_sha256=code_sha,no_capture_or_consumer_science_grant=True))
 else:
  assert parsed==prior_qa['parsed_profile'],'NATIVE_QA_CAPTURE_SAME_FROZEN_PARAMS_AND_ORIGINAL_QA_NOT_BYTE_SHA'
  numerical=job.get('numerical_policy','NATIVE_AND_CAPTURE_QA_PASS')
  correctness=task.get('correctness',{})
  if correctness.get('postcheck_command'):
   check=[x.replace('{attempt}',str(runtime)) for x in correctness['postcheck_command']]
   checker_env=env.copy()
   for key in ['LD_PRELOAD','CUDA_INJECTION64_PATH','ADA_SEMANTIC_MAP','TRACES_FOLDER','ACTIVE_FROM_START']:checker_env.pop(key,None)
   for item in correctness.get('checker_source_files',[]):assert sha(pathlib.Path(item['path']))==item['sha256']
   if task.get('golden_output'):assert sha(pathlib.Path(task['golden_output']['path']))==task['golden_output']['sha256']
   pc=subprocess.run(check,cwd=runtime,env=checker_env,capture_output=True,text=True,timeout=correctness.get('postcheck_timeout_sec',180))
   (root/'CAPTURE_NUMERICAL_CHECK.log').write_text(pc.stdout+pc.stderr)
   numerical='CAPTURE_REFERENCE_PASS' if pc.returncode==0 else 'CAPTURE_REFERENCE_NEGATIVE_NOT_SCIENTIFICALLY_ACCEPTED'
  elif numerical=='NATIVE_AND_CAPTURE_QA_PASS':
   assert re.search(correctness['stdout_regex'],stdout),'capture numerical QA marker missing'
  
  # No whole validator, grouping, sender/archive or catalog code is reachable here.
  files=[]
  for f in sorted((root/'traces').glob('*')):
   if f.is_file():
    st=f.stat();files.append(dict(name=f.name,bytes=st.st_size,mtime_ns=st.st_mtime_ns,ctime_ns=st.st_ctime_ns))
  assert files and sum(v['name'].endswith('.trace.xz')for v in files)==task['profile']['expected_kernels'],'EXACT_SMALL_FULL_LAUNCH_COUNT_1_OR3'
  assert len(files)<=scope['max_capture_files'],'capture metadata file count bound'
  import csv
  stats=list((root/'traces').glob('stats_ctx_*'));assert len(stats)==1 and stats[0].stat().st_size<=65536,'PILOT_SMALL_STATS_COMPLETE_CONTEXT_BOUND'
  with stats[0].open()as f:statrows=list(csv.DictReader(f,skipinitialspace=True))
  assert len(statrows)==task['profile']['expected_kernels'],'PILOT_ALL_EXPECTED_KERNEL_STATS'
  assert {r['kernel id'].strip()for r in statrows}=={r['name']for r in files if r['name'].endswith('.trace.xz')},'PILOT_STATS_TRACE_SET'
  assert all(r['total_reported_insts'].strip().isdecimal()for r in statrows),'PILOT_TYPED_REPORTED_RECORDS'
  reported=sum(int(r['total_reported_insts'])for r in statrows)
  save(root/'CLOSED_PRODUCER_STATS_DECLARATION.json',dict(producer_declared_warp_records=reported,actual_record_POST_not_yet_done=True,record_count_truncation_policy=False,time_and_compressed_byte_poll_bounds_still_apply=True,no_science_or_consumer_grant=True))
  with(root/'FROZEN_JOB_RAW.json').open('xb')as out:out.write(job_path.read_bytes());out.flush();os.fsync(out.fileno())
  save(root/'LEAF_CAPTURED.json',dict(schema='EXACT33_CAPTURE_LEAF_FINISHED_V1',status='LEAF_CAPTURE_FINISHED_POST_UNVALIDATED',job_id=jobid,job_sha256=job_meta['job_sha256'],capture_exit=p.returncode,numerical_status=numerical,execution_sha256=sha(root/'EXECUTION.json'),map_manifest_sha256=sha(root/'map/manifest.json'),producer_sha256=sha(TOOL),tracer_control_flags=receipt['tracer_control_flags'],raw_file_metadata=files,raw_file_body_SHA='DEFERRED_TO_CPU_POST',full_record_validation_complete=False,POST_complete=False,consumer_qualification=False,scientific_qualification=False,source_KEEP=True))
except BaseException as e:
 receipt.update(status='PILOT_COST_HOLD_RETAINED'if 'PILOT_WARP_RECORD_BUDGET_EXCEEDED'in str(e)else'NATIVE_QA_INCOMPLETE_RETAINED'if scope['queue_stage']=='NATIVE_QA'else'PENDING_SPECIALIST_EXTENSION'if any(x in str(e)for x in ['SPECIALIST','MAP_PREFLIGHT'])else'CAPTURE_INCOMPLETE_RETAINED',error=repr(e),traceback=traceback.format_exc(),resource_failure_not_workload_unavailable=True)
 save(root/'FAILURE.json',receipt)
 raise
finally:
 # Only the outer guard may release the shared OFDs, after exact descendant closure.
 pass
