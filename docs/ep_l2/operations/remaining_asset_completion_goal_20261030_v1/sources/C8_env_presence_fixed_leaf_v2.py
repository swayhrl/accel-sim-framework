#!/usr/bin/env python3
"""Frozen33 capture-only leaf. Outer guard retains GPU/IO and Native perasset leases."""
import pathlib,os,json,subprocess,time,fcntl,hashlib,signal,re,shutil,sys,traceback
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');N=R/'nas_rtx4080';S=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1')
TOOL=pathlib.Path('/data/c16/ada_trace_extensions_v8_20261024_v1/frozen/producer_v7_input_c8cfa41fcabc_r2/producer.so');CONTRACT=S/'frozen/ada7_contract_v1';VALIDATOR=pathlib.Path(__file__).parent/'tools/validate_v7_snapshot_v2.py';POST=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/control/frozen/post_v4_5d3ffcd3/postprocess_nas_sharded_v4.py');MAPPER=pathlib.Path(__file__).with_name('mapper_ordinal_candidate_v2_hexsize.py')
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
assert hashlib.sha256(_raw).hexdigest()=='0e05cc6b91bdd0bd03cdbae64f2ca40f3dbd538131862343b4c7faf2c92caa28'
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
prior_qa=C.qa_row(scope,job)
shared=None
receipt={'job_id':jobid,'task':task,'started':time.time(),'status':'PREPARING','worker_pid':os.getpid(),'worker_start_ticks':ticks(os.getpid()),'actual_gpu_uuid':'GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59','pipeline_sha256':sha(pathlib.Path(__file__))};gpu=None;io=None;p=None
try:
 assert leases is not None # outer guard owns original GPU and LOCAL_IO OFDs
 assert scope['queue_stage']=='CAPTURE'and scope['QA_instructionmap_skipped']is True
 assert sha(TOOL)=='c8cfa41fcabc90ff962159b77cda4a7b6c3ba0dd12236bf5d41849d159ad1352'
 assert sha(VALIDATOR)=='175943e30d6c89daa9d8ec65c526029a6d7d689c40567c73933a1b5ca53df2e8'
 assert sha(TOOL.parent/'CONTRACT.json')=='315fb51c10ca6351421afee22d8712767c609bce0c7f38577d7e63b5aadf975b'
 assert sha(TOOL.parent/'INPUT_INITIALIZATION_SCOPE_ADDENDUM.json')=='f7196678b81715dda1c2d45ebeed5b94351b29925f6450dbaa7bbab66dfc870a'
 copy(TOOL,root/'evidence/producer.so')
 assert sha(binary)==task['binary_sha256']
 copy(binary,root/'evidence/application')
 m={'binary_sha256':task['binary_sha256']}
 Map=C.rawmodule(pathlib.Path(__file__).parent/'same_execution_capture_contract_v1.py',mf['files']['same_execution_capture_contract_v1.py']['sha256'],'same_execution_capture_contract')
 static_source=pathlib.Path(__file__).parent/'CPU_SUPPORT_MAP_NOT_LOADED_QUALIFIED'
 for member in static_source.iterdir():
  assert member.is_file()and not member.is_symlink(),'EXACT_FROZEN_CPU_MAP_MEMBERS'
  copy(member,root/'map'/member.name)
 static_map=root/'map/manifest.json'
 static_gate=Map.static_gate(json.loads(static_map.read_bytes()),task['binary_sha256'])
 save(root/'STATIC_ISA_GATE_NOT_DYNAMIC_QUALIFIED.json',static_gate)
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
 assert scope['C8_snapshot_only']is False
 env.pop('LD_AUDIT',None)
 env.pop('ADA_INPUT_SNAPSHOT_ONLY',None)
 env.update(ADA_INPUT_SNAPSHOT='1',ADA_INPUT_MAX_COPY_BYTES='1048576',ADA_INPUT_MAX_TOTAL_BYTES='4194304')
 assert 'ADA_INPUT_SNAPSHOT_ONLY'not in env,'FROZEN_C8_SNAPSHOT_ONLY_IS_PRESENCE_TEST_NOT_BOOLEAN_STRING'
 receipt['input_observer_snapshot_only']=False;receipt['instruction_trace_requested']=True;receipt['kind']='instrumented'
 receipt['actual_input_environment']={k:env[k]for k in ['LD_PRELOAD','ADA_INPUT_SNAPSHOT','ADA_INPUT_SNAPSHOT_ONLY','ADA_INPUT_MAX_COPY_BYTES','ADA_INPUT_MAX_TOTAL_BYTES','ADA_SEMANTIC_MAP']if k in env}
 receipt['input_snapshot_only_environment_variable_absent']='ADA_INPUT_SNAPSHOT_ONLY'not in env
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
 assert parsed['profile']==prior_qa['parsed_profile']['profile'],'SAME_ORIGINAL_PARAMS_NOT_SEED_EQUALITY'
 qualifier=pathlib.Path(__file__).parent/'tools/qualify_input_capsule_v4.py';handle=pathlib.Path(__file__).parent/'tools/verify_c8_launch_handles_v1.py'
 assert sha(qualifier)=='7d00cf3524389ec5f9bfd28ec931cd9c88c45b3deaa4fb9ea0368c7cc0b58388'and sha(handle)=='3506403600ce5d3ba450a5e8d72aa6a72fd7cf9fe5c1163b7029ec86bc5b32aa'
 Oracle=C.rawmodule(pathlib.Path(__file__).parent/'sdk42_reduction_oracle_v1.py','d8d3d8fcfa49b9d433fb9537d79a0c3d6914e3e797881824429e5b71fb9ee78b','existing_C8_input_oracle')
 source_oracle=Oracle.validate_sources(pathlib.Path(__file__).parent/'sources');save(root/'SOURCE_INITIALIZATION_AND_LAUNCH_ORACLE.json',source_oracle)
 cq=subprocess.run(['/usr/bin/python3','-I','-S','-B',str(qualifier),str(root),'--trace-required','--max-copy-bytes','1048576','--max-total-bytes','4194304'],capture_output=True,text=True,timeout=60)
 (root/'INPUT_CAPSULE_VALIDATOR.log').write_text(cq.stdout+cq.stderr);assert cq.returncode==0,'ACTUAL_SOURCE_CAPSULE_NOT_CLOSED '+cq.stderr[-1000:]
 qualified=json.loads(cq.stdout)
 hj=subprocess.run(['/usr/bin/python3','-I','-S','-B',str(handle),str(root),'--expected-launch-count','3','--source-oracle-reference',str(root/'SOURCE_INITIALIZATION_AND_LAUNCH_ORACLE.json')],capture_output=True,text=True,timeout=60)
 (root/'HANDLE_JOIN.log').write_text(hj.stdout+hj.stderr);assert hj.returncode==0,'ACTUAL3_LAUNCH_HANDLE_JOIN_FAILED'
 joins=json.loads(hj.stdout)['joins'];actual_input=Oracle.validate_capsule(root,qualified,stdout,joins,source_oracle)
 save(root/'QUALIFIED_INPUT_CAPSULE.json',qualified);save(root/'REDUCTION_ACTUAL_SOURCE_INPUT_CHECK.json',actual_input)

 raw=Map.validate_raw_headers(root,source_oracle)
 save(root/'SAME_EXECUTION_RAW_HEADER_AND_STATS.json',raw)
 save(root/'SAME_EXECUTION_SOURCE_TRACE_BINDING.json',dict(schema='SDK42_REDUCTION_SAME_EXECUTION_SOURCE_TRACE_BINDING_V1',status='SOURCE_INPUT_INTEGER_QA_LAUNCH_AND_RAW_HEADERS_CLOSED_FULLF9_PENDING',execution_ref=C.ref(root/'EXECUTION.json'),capsule_ref=C.ref(root/'QUALIFIED_INPUT_CAPSULE.json'),actual_input_ref=C.ref(root/'REDUCTION_ACTUAL_SOURCE_INPUT_CHECK.json'),handle_join_ref=C.ref(root/'LAUNCH_FUNCTION_HANDLE_QUALIFICATION.json'),raw_headers_ref=C.ref(root/'SAME_EXECUTION_RAW_HEADER_AND_STATS.json'),scope_sha256=scope_sha,code_manifest_sha256=code_sha,cross_run_input_proof_reused=False,actual_source_copies=2,actual_source_bytes=262400,launches=3,full_record_POST_consumer_science_granted=False,source_KEEP=True))
 with(root/'FROZEN_JOB_RAW.json').open('xb')as out:out.write(job_path.read_bytes());out.flush();os.fsync(out.fileno())
 save(root/'LEAF_CAPTURED.json',dict(schema='EXACT33_CAPTURE_LEAF_FINISHED_V1',status='LEAF_CAPTURE_FINISHED_POST_UNVALIDATED',job_id=jobid,job_sha256=job_meta['job_sha256'],capture_exit=p.returncode,numerical_status='SAME_EXECUTION_ORIGINAL_INTEGER_GPU_CPU_AND_ACTUAL_INPUT_SUM_PASS',execution_sha256=sha(root/'EXECUTION.json'),map_manifest_sha256=sha(static_map),map_qualification_granted=False,producer_sha256=sha(TOOL),record_profile='ADA7_ORDINARY_STRICT_SINGLE_STREAM_F9_PENDING',tracer_control_flags=receipt['tracer_control_flags'],raw_file_metadata=raw['raw_files'],raw_file_body_SHA='DEFERRED_TO_CPU_POST',same_execution_source_binding_ref=C.ref(root/'SAME_EXECUTION_SOURCE_TRACE_BINDING.json'),cross_run_input_proof_reused=False,full_record_validation_complete=False,POST_complete=False,consumer_qualification=False,scientific_qualification=False,source_KEEP=True))


except BaseException as e:
 receipt.update(status='PILOT_COST_HOLD_RETAINED'if 'PILOT_WARP_RECORD_BUDGET_EXCEEDED'in str(e)else'NATIVE_QA_INCOMPLETE_RETAINED'if scope['queue_stage']=='NATIVE_QA'else'PENDING_SPECIALIST_EXTENSION'if any(x in str(e)for x in ['SPECIALIST','MAP_PREFLIGHT'])else'CAPTURE_INCOMPLETE_RETAINED',error=repr(e),traceback=traceback.format_exc(),resource_failure_not_workload_unavailable=True)
 save(root/'FAILURE.json',receipt)
 raise
finally:
 # Only the outer guard may release the shared OFDs, after exact descendant closure.
 pass
