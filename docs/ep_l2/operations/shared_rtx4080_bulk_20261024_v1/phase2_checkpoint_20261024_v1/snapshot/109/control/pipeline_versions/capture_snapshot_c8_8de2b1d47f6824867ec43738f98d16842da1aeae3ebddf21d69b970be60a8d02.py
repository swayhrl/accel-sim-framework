#!/usr/bin/env python3
"""Single immutable ordinary-input capture. Native174 owns global transport leases."""
import pathlib,os,json,subprocess,time,fcntl,hashlib,signal,re,shutil,sys,traceback
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');N=R/'nas_rtx4080';S=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1')
F=pathlib.Path('/data/c16/ada_trace_extensions_v8_20261024_v1/frozen/producer_v7_input_c8cfa41fcabc_r2');TOOL=F/'producer.so';CONTRACT=F;VALIDATOR=F/'validate_v7_snapshot_v2.py';POST=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/control/frozen/post_v4_5d3ffcd3/postprocess_nas_sharded_v4.py');MAPPER=pathlib.Path('/data/c16/ada_trace_extensions_v8_20261024_v1/frozen/mapper_v3_a2e7ee38aa72/make_semantic_map_elf_owner_v3.py')
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
job=json.loads(pathlib.Path(sys.argv[1]).read_text());task=job['task'];jobid=job['id'];root=N/'inflight'/jobid;binary=pathlib.Path(task['argv'][0]);root.mkdir(exist_ok=False)
receipt={'kind':'instrumented','job_id':jobid,'task':task,'started':time.time(),'status':'PREPARING','worker_pid':os.getpid(),'worker_start_ticks':ticks(os.getpid()),'actual_gpu_uuid':'GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59','pipeline_sha256':sha(pathlib.Path(__file__))};gpu=None;io=None;p=None
try:
 io=open(R/'control/RTX4080_LOCAL_IO.lock','a');fcntl.flock(io,fcntl.LOCK_EX|fcntl.LOCK_NB)
 save(root/'CAPTURE_JOB.json',job)
 receipt['capture_job_sha256']=sha(root/'CAPTURE_JOB.json')
 assert sha(POST)=='5d3ffcd3cf000e1f72e2adf97b4185217a51e1fe0c147c5c39500130e418e66d'
 assert sha(R/'control/ssh_rate_bridge_v2.py')=='8ff3e634870ae34071362afb834245291a49f8d9e37e524462515e3a95771295'
 assert sha(MAPPER)=='a2e7ee38aa722465250c53096aea50bcd93623fea5b60114486538429dce1f6e'
 assert sha(binary)==task['binary_sha256']
 assert sha(TOOL)=='c8cfa41fcabc90ff962159b77cda4a7b6c3ba0dd12236bf5d41849d159ad1352'
 assert sha(CONTRACT/'CONTRACT.json')=='315fb51c10ca6351421afee22d8712767c609bce0c7f38577d7e63b5aadf975b'
 assert sha(VALIDATOR)=='175943e30d6c89daa9d8ec65c526029a6d7d689c40567c73933a1b5ca53df2e8'
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
  if k.startswith(('TRACE_','TOOL_','DYNAMIC_','NVBIT_','C16_','ADA_')) or k in ['LD_PRELOAD','CUDA_INJECTION64_PATH','ACTIVE_FROM_START']:env.pop(k,None)
 env.update(LD_PRELOAD=str(TOOL)+':libcuda.so.1',ADA_SEMANTIC_MAP=str(root/'map/semantic-map.tsv'),TRACES_FOLDER=str(root),ACTIVE_FROM_START='1',TRACE_FILE_COMPRESS='1',TOOL_COMPRESS='1',DYNAMIC_KERNEL_RANGE='',PATH='/usr/local/cuda-12.8/bin:'+env.get('PATH',''),NVDISASM='/usr/local/cuda-12.8/bin/nvdisasm',CUDA_VISIBLE_DEVICES='GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
 tracer_flags={'INSTR_BEGIN': '0', 'INSTR_END': '4294967295', 'C16_EXACT_ROOT_FUNCTION_ONLY': '0', 'C16_USE_NVBIT_STATIC_INDEX': '0', 'ENABLE_SPINLOCK_FAST_FORWARD': '0', 'SPINLOCK_ITER_TO_KEEP': '1', 'TERMINATE_UPON_LIMIT': '0', 'TRACE_LINEINFO': '0', 'EXCLUDE_PRED_OFF': '1', 'TOOL_VERBOSE': '0', 'TOOL_TRACE_CORE': '0'}
 env.update(tracer_flags);receipt['tracer_control_flags']=tracer_flags
 assert sha(R/'control/PARENT_C8_OBSERVED_HTOD_RELEASE_V1.json')=='14c56c21a34dcedf2524248a9787bf7e005d6a574c0b97d6a1e77b718565ef6e'
 assert job['snapshot_scope_oracle']['program']=='CUDA118_VECTORADD_DEFAULT_50000'
 for x in task['source_files']:assert sha(pathlib.Path(x['path']))==x['sha256']
 assert task['program']=='vectorAdd' and len(task['argv'])==1
 assert task['binary_sha256']=='d32e5d43c17d19a6a249e20d1f06c95a5f3453558a671a57d64831fb727bb95c'
 assert sha(F/'qualify_input_capsule_v4.py')=='7d00cf3524389ec5f9bfd28ec931cd9c88c45b3deaa4fb9ea0368c7cc0b58388'
 assert sha(F/'INPUT_INITIALIZATION_SCOPE_ADDENDUM.json')=='f7196678b81715dda1c2d45ebeed5b94351b29925f6450dbaa7bbab66dfc870a'
 HANDLE=pathlib.Path('/data/c16/ada_trace_extensions_v8_20261024_v1/frozen/c8_handle_join_v1/verify_c8_launch_handles_v1.py')
 assert sha(HANDLE)=='3506403600ce5d3ba450a5e8d72aa6a72fd7cf9fe5c1163b7029ec86bc5b32aa'
 env.update(ADA_INPUT_SNAPSHOT='1',ADA_INPUT_MAX_COPY_BYTES=str(job['snapshot_limits']['max_copy_bytes']),ADA_INPUT_MAX_TOTAL_BYTES=str(job['snapshot_limits']['max_total_bytes']))
 env.pop('ADA_INPUT_SNAPSHOT_ONLY',None)
 receipt['explicit_capture_environment']={k:v for k,v in env.items() if k.startswith(('ADA_','TRACE_','TOOL_','DYNAMIC_','NVBIT_','C16_','INSTR_')) or k in ['LD_PRELOAD','ACTIVE_FROM_START','CUDA_VISIBLE_DEVICES','NVDISASM','ENABLE_SPINLOCK_FAST_FORWARD','SPINLOCK_ITER_TO_KEEP','TERMINATE_UPON_LIMIT','EXCLUDE_PRED_OFF']}
 receipt['explicit_capture_environment']['ADA_INPUT_SNAPSHOT_ONLY']='UNSET_BY_WORKER'
 save(root/'SOURCE_INITIALIZATION_AND_LAUNCH_ORACLE.json',job['snapshot_scope_oracle'])

 limits=job.get('resource_limits',{'capture_timeout_sec':max(172800,task.get('capture_timeout_sec',0)),'capture_max_bytes':max(2*1024**4,task.get('capture_max_bytes',0))});receipt['capture_limits']=limits
 gpu=open('/data/c16/locks/c16_gpu_campaign.lock','a');fcntl.flock(gpu,fcntl.LOCK_EX)
 baseline=procs();allowed={int(x[0]) for x in baseline}
 assert all(x[1]=='/home/huangrulin/workspace/image-lab/envs/comfyui/bin/python' for x in baseline)
 for pid in allowed:assert '/home/huangrulin/workspace/image-lab/app/ComfyUI/main.py' in (pathlib.Path('/proc')/str(pid)/'cmdline').read_bytes().replace(b'\0',b' ').decode()
 base_mem={int(x[0]):float(x[2]) for x in baseline};base_ticks={pid:ticks(pid) for pid in allowed};receipt['resident_baseline']={'processes':baseline,'start_ticks':base_ticks};stable=0;deadline=time.monotonic()+180
 while stable<15:
  assert time.monotonic()<deadline,'no idle window'
  assert all(int(x[0]) in allowed for x in procs()),'new compute before capture'
  util=float(query('utilization.gpu')[0]);stable=stable+1 if util==0 else 0;time.sleep(1)
 free=float(query('memory.free')[0]);assert free>=1024,'GPU free headroom<1GiB'
 receipt['gpu_free_mib_before']=free;receipt['gpu_before']=query('name,uuid,driver_version,memory.total,memory.free')
 assert sha(binary)==task['binary_sha256']
 obsroot=root/'observer';obsroot.mkdir();obsruntime=obsroot/'runtime';obsruntime.mkdir()
 obsenv=env.copy();obsenv.update(ADA_INPUT_SNAPSHOT_ONLY='1',TRACES_FOLDER=str(obsroot))
 obsreceipt=dict(receipt,kind='native_observer',snapshot_only=True)
 obsreceipt['explicit_capture_environment']=dict(receipt['explicit_capture_environment'],ADA_INPUT_SNAPSHOT_ONLY='1',TRACES_FOLDER=str(obsroot))
 start=time.monotonic();peak=0.;min_free=free;mon=[]
 with (obsroot/'stdout.log').open('x') as out,(obsroot/'stderr.log').open('x') as err:
  p=subprocess.Popen(task['argv'],cwd=obsruntime,env=obsenv,stdout=out,stderr=err,start_new_session=True,preexec_fn=lambda:os.nice(15));subprocess.run(['ionice','-c','2','-n','7','-p',str(p.pid)],capture_output=True)
  obsreceipt.update(capture_pid=p.pid,capture_start_ticks=ticks(p.pid));save(obsroot/'PROCESS_START.json',obsreceipt)
  while p.poll() is None:
   seen=procs()
   for x in seen:
    pid=int(x[0]);mem=float(x[2])
    if pid not in allowed|{p.pid}:obsreceipt['bounded_stop']='new compute '+str(x)
    if pid==p.pid:peak=max(peak,mem)
    if pid in allowed and (ticks(pid)!=base_ticks[pid] or mem>base_mem[pid]+256):obsreceipt['bounded_stop']='resident changed or VRAM growth '+str(x)
   pm=subprocess.run(['nvidia-smi','pmon','-c','1','-s','u'],capture_output=True,text=True,timeout=10)
   for line in pm.stdout.splitlines():
    t=line.split()
    if len(t)>3 and t[1].isdigit() and int(t[1]) in allowed and t[3] not in ['0','-']:obsreceipt['bounded_stop']='resident active '+line
   current_free=float(query('memory.free')[0]);min_free=min(min_free,current_free)
   if current_free<512:obsreceipt['bounded_stop']='GPU free headroom<512MiB'
   if time.monotonic()-start>limits['capture_timeout_sec']:obsreceipt['bounded_stop']='capture wall bound'
   size=sum(x.stat().st_size for x in root.rglob('*') if x.is_file())
   if size>limits['capture_max_bytes']:obsreceipt['bounded_stop']='capture byte bound'
   if shutil.disk_usage(root).free<20*1024**3:obsreceipt['bounded_stop']='NAS free reserve<20GiB'
   if obsreceipt.get('bounded_stop') and p.poll() is None:
    os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(timeout=10)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   time.sleep(.2)
  out.flush();os.fsync(out.fileno());err.flush();os.fsync(err.fileno())
 obsreceipt.update(exit_code=p.returncode,capture_elapsed_s=time.monotonic()-start,peak_observed_gpu_mib=peak,min_observed_gpu_free_mib=min_free,binary_sha256=sha(binary),tool_sha256=sha(TOOL),ended=time.time())

 save(obsroot/'EXECUTION.json',obsreceipt)
 assert p.returncode==0 and not obsreceipt.get('bounded_stop'),'native-observer did not complete'
 assert re.search(task['correctness']['stdout_regex'],(obsroot/'stdout.log').read_text()),'observer source numerical QA missing'
 obsreceipt['numerical_reference_pass']=True
 start=time.monotonic();peak=0.;min_free=free;mon=[]
 with (root/'stdout.log').open('x') as out,(root/'stderr.log').open('x') as err:
  p=subprocess.Popen(task['argv'],cwd=runtime,env=env,stdout=out,stderr=err,start_new_session=True,preexec_fn=lambda:os.nice(15));subprocess.run(['ionice','-c','2','-n','7','-p',str(p.pid)],capture_output=True)
  receipt.update(capture_pid=p.pid,capture_start_ticks=ticks(p.pid));save(root/'PROCESS_START.json',receipt)
  while p.poll() is None:
   seen=procs()
   for x in seen:
    pid=int(x[0]);mem=float(x[2])
    if pid not in allowed|{p.pid}:receipt['bounded_stop']='new compute '+str(x)
    if pid==p.pid:peak=max(peak,mem)
    if pid in allowed and (ticks(pid)!=base_ticks[pid] or mem>base_mem[pid]+256):receipt['bounded_stop']='resident changed or VRAM growth '+str(x)
   pm=subprocess.run(['nvidia-smi','pmon','-c','1','-s','u'],capture_output=True,text=True,timeout=10)
   for line in pm.stdout.splitlines():
    t=line.split()
    if len(t)>3 and t[1].isdigit() and int(t[1]) in allowed and t[3] not in ['0','-']:receipt['bounded_stop']='resident active '+line
   current_free=float(query('memory.free')[0]);min_free=min(min_free,current_free)
   if current_free<512:receipt['bounded_stop']='GPU free headroom<512MiB'
   if time.monotonic()-start>limits['capture_timeout_sec']:receipt['bounded_stop']='capture wall bound'
   size=sum(x.stat().st_size for x in root.rglob('*') if x.is_file())
   if size>limits['capture_max_bytes']:receipt['bounded_stop']='capture byte bound'
   if shutil.disk_usage(root).free<20*1024**3:receipt['bounded_stop']='NAS free reserve<20GiB'
   if receipt.get('bounded_stop') and p.poll() is None:
    os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(timeout=10)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   time.sleep(.2)
  out.flush();os.fsync(out.fileno());err.flush();os.fsync(err.fileno())
 receipt.update(exit_code=p.returncode,capture_elapsed_s=time.monotonic()-start,peak_observed_gpu_mib=peak,min_observed_gpu_free_mib=min_free,binary_sha256=sha(binary),tool_sha256=sha(TOOL),ended=time.time())
 fcntl.flock(gpu,fcntl.LOCK_UN);gpu.close();gpu=None
 assert receipt['binary_sha256']==m['binary_sha256']
 save(root/'EXECUTION.json',receipt)
 assert p.returncode in job.get('allowed_capture_exits',[0]) and not receipt.get('bounded_stop'),'capture did not reach declared completion'
 stdout=(root/'stdout.log').read_text(errors='replace')
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
 
 # Independent source oracle constrains initialization and whole app, not only journal self consistency.
 capsule_qualifications=[]
 import struct,math
 for attempt,is_trace in [(obsroot,False),(root,True)]:
  cmd=['python3','-B',str(F/'qualify_input_capsule_v4.py'),str(attempt),'--max-copy-bytes',str(job['snapshot_limits']['max_copy_bytes']),'--max-total-bytes',str(job['snapshot_limits']['max_total_bytes'])]
  if is_trace:cmd.append('--trace-required')
  cp0=subprocess.run(cmd,capture_output=True,text=True,timeout=300)
  (attempt/'CAPSULE_VALIDATOR.log').write_text(cp0.stdout+cp0.stderr);assert cp0.returncode==0,cp0.stderr
  cq=json.loads(cp0.stdout);assert len(cq['copies'])==2 and cq['total_bytes']==400000
  for copyrow in cq['copies'].values():
   assert copyrow['bytes']==200000 and copyrow['api'] in ['cuMemcpyHtoD_v2','cuMemcpyHtoD_v2_ptds']
   data=(attempt/copyrow['restorable_relative_path']).read_bytes()
   assert all(math.isfinite(v[0]) and 0<=v[0]<=1 for v in struct.iter_unpack('<f',data))
  cp1=subprocess.run(['python3','-B',str(HANDLE),str(attempt),'--expected-launch-count','1','--source-oracle-reference',str(root/'SOURCE_INITIALIZATION_AND_LAUNCH_ORACLE.json')],capture_output=True,text=True,timeout=60)
  (attempt/'HANDLE_JOIN.log').write_text(cp1.stdout+cp1.stderr);assert cp1.returncode==0,cp1.stderr
  joins=json.loads(cp1.stdout)['joins'];assert len(joins)==1 and 'vectorAdd' in joins[0]['function']
  capsule_qualifications.append(cq)
 assert re.search(task['correctness']['stdout_regex'],stdout),'instrumented full source numerical QA missing'
 snapshot_identity={'scope':'OBSERVED_SUPPORTED_HTOD_SOURCE_BYTES_ONLY','observer_ordered_sha256':capsule_qualifications[0]['ordered_input_identity_sha256'],'trace_ordered_sha256':capsule_qualifications[1]['ordered_input_identity_sha256'],'comparison':'MATCH' if capsule_qualifications[0]['ordered_input_identity_sha256']==capsule_qualifications[1]['ordered_input_identity_sha256'] else 'INPUT_DIFF','native_observer_is_not_unloaded_native':True,'complete_CUDA_initialization_snapshot':False,'source_initialization_oracle':job['snapshot_scope_oracle'],'copy_caps':job['snapshot_limits'],'source_numerical_reference':'Full50000 element CPU comparison within each same-instrumented process, source epsilon1e-5; snapshot floats independently finite0..1'}
 save(root/'INPUT_SNAPSHOT_PAIR_IDENTITY.json',snapshot_identity)
 numerical='SOURCE_FABS_REFERENCE_REPORTED_PASS_NO_EXPLICIT_OUTPUT_FINITE_CHECK;OBSERVER_SOURCE_FABS_REPORTED_PASS'
 cp=subprocess.run(['python3',str(VALIDATOR),str(root),str(root/'map/manifest.json')],capture_output=True,text=True,timeout=86400);(root/'VALIDATOR.log').write_text(cp.stdout+cp.stderr);assert cp.returncode==0,cp.stderr
 val=json.loads(cp.stdout);assert val['status']=='ADA7_ORDINARY_FULL_RECORD_PASS'
 if 'expected_kernel_count' in job:assert val['kernels']==job['expected_kernel_count'],'expected kernel count'
 assert val['kernels']==1 and val['ctas']==196 and val['warps']==1568
 raw_headers=[]
 for raw in (root/'traces').glob('*.trace.xz'):
  import lzma
  h={}
  with lzma.open(raw,'rt') as f:
   for line in f:
    if line.startswith('-grid dim = '):h['grid']=tuple(map(int,re.findall(r'\d+',line)))
    if line.startswith('-block dim = '):h['block']=tuple(map(int,re.findall(r'\d+',line)));break
  assert h=={'grid':(196,1,1),'block':(256,1,1)},'source oracle launch geometry mismatch'

 (root/'FULL_RECORD_STREAM_VALIDATION.json').rename(root/'FULL_RECORD_VALIDATION.json')
 post_receipts=[]
 for raw in sorted((root/'traces').glob('*.trace.xz')):
  dest=raw.with_name(raw.name.replace('.trace.xz','.traceg.xz'));work=root/'postprocess_work'/raw.stem
  q=subprocess.run(['python3',str(POST),str(raw),str(dest),str(work)],capture_output=True,text=True,timeout=86400);(root/('POSTPROCESS_'+raw.name+'.log')).write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
  gr=json.loads(q.stdout);post_receipts.append(gr)
  assert root.resolve() in work.resolve().parents and 'postprocess_work' in work.parts;shutil.rmtree(work)
 (root/'POSTPROCESS_NAS.json').write_text(json.dumps(post_receipts,indent=2)+'\n')
 ctx=next((root/'traces').glob('kernelslist_ctx_*'));lines=[]
 for line in ctx.read_text().splitlines():
  lines.append(line.replace('.trace.xz','.traceg.xz') if line.startswith('kernel-') else line)
 (root/'traces/kernelslist.g').write_text('\n'.join(lines)+'\n')
 binary_member='bin/vectorAdd' if task['program']=='vectorAdd' else 'bin/application'
 copy(binary,root/binary_member);copy(TOOL,root/'tools/producer.so')
 for name,src in [('validate_v7_stream_v3.py',VALIDATOR),('postprocess_nas_sharded_v4.py',POST),('ssh_rate_bridge_v2.py',R/'control/ssh_rate_bridge_v2.py'),('capture_ordinary_worker.py',pathlib.Path(__file__)),('make_semantic_map_elf_owner_v3.py',MAPPER)]:copy(src,root/'tools'/name)
 for qname in ['POSTPROCESS_NAS_V4_QUALIFICATION_RECEIPT.json','POSTPROCESS_NAS_V4_NEGATIVE_QUALIFICATION.json']:
  copy(POST.parent/qname,root/'qualification'/qname)
 for name in ['CONTRACT.json','INPUT_INITIALIZATION_SCOPE_ADDENDUM.json','qualify_input_capsule_v4.py','validate_v7_snapshot_v2.py']:
  copy(CONTRACT/name,root/'contract'/name)
 copy(HANDLE,root/'tools/verify_c8_launch_handles_v1.py')
 copy(S/'frozen/ada7_contract_v1/validate_v7.py',root/'contract/validate_v7.py')
 copy(R/'control/PARENT_C8_OBSERVED_HTOD_RELEASE_V1.json',root/'qualification/PARENT_C8_OBSERVED_HTOD_RELEASE_V1.json')
 source_items=list(task.get('sources',task.get('source_files',[])))
 if not source_items and task.get('source'):source_items=[{'path':task['source'],'sha256':task['source_sha256']}]
 source_items+=list(task.get('correctness',{}).get('checker_source_files',[]))
 for i,x in enumerate(source_items):
  f=pathlib.Path(x['path']);assert sha(f)==x['sha256'];copy(f,root/'source'/('%03d_'%i+f.name))
 save(root/'TASK.json',task);save(root/'NATIVE_QUALIFICATION.json',job['native_receipt'])
 asset={'schema':'RTX4080_FULL_TRACE_ASSET_V1','kind':'FULL_APPLICATION_TRACE','asset_id':job['asset_id'],'suite':task['suite'],'source_version':task.get('version',task.get('source_version','UNKNOWN')),'program':task['program'],'variant':task.get('variant','DECLARED_DEFAULT'),'input_identity':task.get('input_identity',task.get('input_files')),'argv':task['argv'],'binary_member':binary_member,'binary_sha256':m['binary_sha256'],'capture_gpu_uuid':receipt['actual_gpu_uuid'],'actual_cubin_arch':89,'embedded_PTX_listing':subprocess.check_output(['/usr/local/cuda-12.8/bin/cuobjdump','-lptx',str(binary)],text=True),'producer_sha256':sha(TOOL),'contract_sha256':sha(CONTRACT/'CONTRACT.json'),'validator_sha256':sha(VALIDATOR),'frozen_parser_sha256':'f4a811c779e9b106c0977af45634d1b7dc01025c9e9b2805b74de6c6c82b879b','map_manifest_sha256':sha(root/'map/manifest.json'),'map_maker_sha256':sha(MAPPER),'postprocessor_sha256':sha(POST),'pump_sha256':sha(R/'control/ssh_rate_bridge_v2.py'),'worker_sha256':sha(pathlib.Path(__file__)),'full_application':{'kernel_launches':val['kernels'],'ctas':val['ctas'],'warps':val['warps'],'records':val['counts']['sass_records'],'all_warps_terminate':True,'expected_kernel_presence':'YES_SOURCE_ORACLE','expected_kernel_count':job.get('expected_kernel_count'),'context_count':1,'stream_ids':val['stream_ids'],'sampling':'NONE','commandlist':'traces/kernelslist.g'},'tracer_control_flags':receipt['tracer_control_flags'],'capture_limits':receipt['capture_limits'],'numerical_status':numerical,'input_byte_identity_qualification':job.get('input_byte_identity_qualification','DECLARED_FILE_SHA_OR_DETERMINISTIC_SOURCE;NO_UNRECORDED_SEED_CLAIM'),'native_state':job.get('native_state'),'producer_semantic_qualification':'ADA7_ORDINARY_FULL_RECORD_PASS','consumer_qualification':'NOT_AUTOMATICALLY_GRANTED; per-profile required','hardware_timing_calibration':'NOT_GRANTED','source_keep':True,'release_bytes':0}
 asset.update(numerical_qualification_limitations='Canonical CPU oracle uses fabs(diff)>1e-5 without explicit output isfinite; input capsules are independently finite, output finite not independently asserted; source reported PASS only',capture_job_sha256=sha(root/'CAPTURE_JOB.json'),input_snapshot_pair=snapshot_identity,input_byte_identity_qualification='ACTUAL_TWO_SYNC_HTOD_ARRAYS_FULL_BYTES_FROZEN;OTHER_INITIALIZATION_SOURCE_RULE_NOT_DEVICE_SNAPSHOT',snapshot_capsule_validator_sha256=sha(F/'qualify_input_capsule_v4.py'),handle_join_sha256=sha(HANDLE),initialization_addendum_sha256=sha(F/'INPUT_INITIALIZATION_SCOPE_ADDENDUM.json'))
 save(root/'ASSET.json',asset)
 files=[{'path':str(f.relative_to(root)),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(root.rglob('*')) if f.is_file()]
 sender={'asset':asset,'files':files};save(root/'SENDER_MANIFEST.json',sender)
 print(json.dumps({'status':'SENDER_COMPLETE','inflight':str(root.relative_to(N)),'asset_id':asset['asset_id'],'sender_manifest_sha256':sha(root/'SENDER_MANIFEST.json'),'payload_files':len(files),'payload_bytes':sum(x['bytes'] for x in files)}))
except Exception as e:
 receipt.update(status='PENDING_SPECIALIST_EXTENSION' if any(x in str(e) for x in ['SPECIALIST','MAP_PREFLIGHT']) else 'FAILED_RETAINED',error=repr(e),traceback=traceback.format_exc())
 if p and p.poll() is None:
  os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=10)
 save(root/'FAILURE.json',receipt)
 print(json.dumps({'status':receipt['status'],'inflight':str(root.relative_to(N)),'error':repr(e)}))
finally:
 if gpu:fcntl.flock(gpu,fcntl.LOCK_UN);gpu.close()
 if io:fcntl.flock(io,fcntl.LOCK_UN);io.close()

