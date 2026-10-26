#!/usr/bin/env python3
"""Single immutable ordinary-input capture. Native174 owns global transport leases."""
import pathlib,os,json,subprocess,time,fcntl,hashlib,signal,re,shutil,sys,traceback
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');N=R/'nas_rtx4080';S=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1')
TOOL=S/'frozen/producer_v7_55c6f482/producer.so';CONTRACT=S/'frozen/ada7_contract_v1';VALIDATOR=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080/private_candidates/ordinary_validator_parallel_prepare_20261027_v1/candidate/parallel_ordinary_validator_v1.py');POST=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/control/frozen/post_v4_5d3ffcd3/postprocess_nas_sharded_v4.py');MAPPER=pathlib.Path('/data/c16/ada_trace_extensions_v8_20261024_v1/frozen/mapper_v3_a2e7ee38aa72/make_semantic_map_elf_owner_v3.py')
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
v2cfg=job['ordinary_validator_cpu2_v1']
assert type(v2cfg['rate_bytes_sec'])is int and 0<v2cfg['rate_bytes_sec']<=256*2**20
assert 0<v2cfg['deadline_sec']<=86400
assert sha(pathlib.Path(v2cfg['grant_file']))==v2cfg['grant_sha256']
validator_parallel_started=False;validator_parallel_closed=False
receipt={'job_id':jobid,'task':task,'started':time.time(),'status':'PREPARING','worker_pid':os.getpid(),'worker_start_ticks':ticks(os.getpid()),'actual_gpu_uuid':'GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59','pipeline_sha256':sha(pathlib.Path(__file__))};gpu=None;io=None;p=None
try:
 io=open(R/'control/RTX4080_LOCAL_IO.lock','a');fcntl.flock(io,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert sha(POST)=='5d3ffcd3cf000e1f72e2adf97b4185217a51e1fe0c147c5c39500130e418e66d'
 assert sha(R/'control/ssh_rate_bridge_v2.py')=='8ff3e634870ae34071362afb834245291a49f8d9e37e524462515e3a95771295'
 assert sha(MAPPER)=='a2e7ee38aa722465250c53096aea50bcd93623fea5b60114486538429dce1f6e'
 assert sha(binary)==task['binary_sha256']
 assert sha(TOOL)=='55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73'
 assert sha(CONTRACT/'CONTRACT.json')=='97901eb373fc94b041c5ef6923e0e5ca1635edd1bac4213d53c28271abb6c184'
 assert sha(VALIDATOR)=='9add4f4b4002ec8ef130a7889d380d4a3ef47c1b7a46116a66721135efb20a6e'

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
 validator_argv=['python3','-B',str(VALIDATOR),str(root),str(root/'map/manifest.json'),'--work',str(root/'validator_parallel2'),'--lease-fd',str(io.fileno()),'--owner-pid',str(os.getpid()),'--owner-start-ticks',ticks(os.getpid()),'--rate-bytes-sec',str(v2cfg['rate_bytes_sec']),'--workers','2','--deadline-sec',str(v2cfg['deadline_sec']),'--grant-file',v2cfg['grant_file'],'--grant-sha',v2cfg['grant_sha256']]
 gate=subprocess.run(validator_argv+['--admission-only'],pass_fds=(io.fileno(),),capture_output=True,text=True,timeout=60)
 save(root/'VALIDATOR_CPU2_PREFLIGHT.json',{'returncode':gate.returncode,'stdout':gate.stdout,'stderr':gate.stderr,'GPU_query_started':False})
 assert gate.returncode==0,'Root exact CPU2 validator admission missing; no GPU launch'
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
 
 validator_parallel_started=True
 cp=subprocess.run(validator_argv,pass_fds=(io.fileno(),),capture_output=True,text=True,timeout=min(86410,v2cfg['deadline_sec']+10))
 (root/'VALIDATOR.log').write_text(cp.stdout+cp.stderr)
 ack=root/'validator_parallel2/OWNED_WORKERS_CLOSED.json'
 if ack.is_file():
  closed=json.loads(ack.read_text())
  validator_parallel_closed=closed['schema']=='ORDINARY_VALIDATOR_OWNED_WORKERS_CLOSED_V1'and closed['status']=='ALL_OWNED_WORKERS_REAPED'and all(x['exitcode']is not None for x in closed['workers'])
 assert validator_parallel_closed,'VALIDATOR_CHILD_CLOSURE_UNKNOWN_RETAIN_LOCK_REFERENCE'
 assert cp.returncode==0,cp.stderr
 val=json.loads(cp.stdout);assert val['status']=='ADA7_ORDINARY_FULL_RECORD_PASS'
 assert val['validator_sha256']==sha(VALIDATOR)and val['frozen_validator_sha256']=='f9f8a05ca7e0f8afe60e7d9a34f4884a9d1cb920b2212e41ed9a4faf19975af1'
 if 'expected_kernel_count' in job:assert val['kernels']==job['expected_kernel_count'],'expected kernel count'
 (root/'FULL_RECORD_STREAM_VALIDATION.json').rename(root/'FULL_RECORD_VALIDATION.json')
 # Candidate POST integration: caller still owns LOCAL_IO and Native174 writer leases.
 scheduler=N/'private_candidates/cpu_post_parallel_20261026_v1/post_app_parallel_109_candidate_v1.py'
 assert sha(scheduler)=='9308c508d85c84db7e9b8d49e465ffaffc426fef638a92d05eec4c6dc7cae423'
 parallel_dir=root/'post_parallel2'
 parallel_result=root/'POST_PARALLEL_CLOSED.json'
 with (root/'POST_PARALLEL.stdout.log').open('x') as out,(root/'POST_PARALLEL.stderr.log').open('x') as err:
  q=subprocess.run(['python3','-B',str(scheduler),str(root),'--post',str(POST),'--dest-root',str(parallel_dir),'--output',str(parallel_result),'--workers','2','--deadline-sec','86400'],stdout=out,stderr=err,timeout=86500)
 assert q.returncode==0,'parallel POST incomplete; SourceKEEP'
 result=json.loads(parallel_result.read_text())
 assert result['status']=='WHOLE_APP_PARALLEL_V4_GROUPING_CLOSED_PASS'
 assert result['postprocessor_sha256']==sha(POST) and result['max_concurrent_kernel_postprocessors']==2
 assert result['kernels']==val['kernels'] and result['records']==val['counts']['sass_records']
 post_receipts=[];relocations=[]
 for gr in result['per_kernel']:
  source=pathlib.Path(gr['grouped'])
  assert source.parent.resolve()==parallel_dir.resolve() and source.is_file()
  dest=root/'traces'/source.name
  assert not dest.exists() and sha(source)==gr['grouped_sha256']
  source.rename(dest)
  assert sha(dest)==gr['grouped_sha256']
  relocations.append({'from':str(source),'to':str(dest),'sha256':gr['grouped_sha256']})
  post_receipts.append(dict(gr,grouped=str(dest)))
 expected={pathlib.Path(gr['grouped']).name for gr in post_receipts}
 assert {p.name for p in (root/'traces').glob('*.traceg.xz')}==expected
 save(root/'POST_PARALLEL_RELOCATION.json',{'source_KEEP':True,'files':relocations,'only_after_whole_app_closed':True})
 save(root/'POSTPROCESS_NAS.json',post_receipts)
 copy(scheduler,root/'tools/post_app_parallel_109_candidate_v1.py')
 ctx=next((root/'traces').glob('kernelslist_ctx_*'));lines=[]
 for line in ctx.read_text().splitlines():
  lines.append(line.replace('.trace.xz','.traceg.xz') if line.startswith('kernel-') else line)
 (root/'traces/kernelslist.g').write_text('\n'.join(lines)+'\n')
 binary_member='bin/vectorAdd' if task['program']=='vectorAdd' else 'bin/application'
 copy(binary,root/binary_member);copy(TOOL,root/'tools/producer.so')
 for name,src in [('postprocess_nas_sharded_v4.py',POST),('ssh_rate_bridge_v2.py',R/'control/ssh_rate_bridge_v2.py'),('capture_ordinary_worker.py',pathlib.Path(__file__)),('make_semantic_map_elf_owner_v3.py',MAPPER)]:copy(src,root/'tools'/name)
 for qname in ['POSTPROCESS_NAS_V4_QUALIFICATION_RECEIPT.json','POSTPROCESS_NAS_V4_NEGATIVE_QUALIFICATION.json']:
  copy(POST.parent/qname,root/'qualification'/qname)
 for f in CONTRACT.iterdir():
  if f.is_file():copy(f,root/'contract'/f.name)
 source_items=list(task.get('sources',task.get('source_files',[])))
 if not source_items and task.get('source'):source_items=[{'path':task['source'],'sha256':task['source_sha256']}]
 source_items+=list(task.get('correctness',{}).get('checker_source_files',[]))
 for i,x in enumerate(source_items):
  f=pathlib.Path(x['path']);assert sha(f)==x['sha256'];copy(f,root/'source'/('%03d_'%i+f.name))
 save(root/'TASK.json',task);save(root/'NATIVE_QUALIFICATION.json',job['native_receipt'])
 asset={'schema':'RTX4080_FULL_TRACE_ASSET_V1','kind':'FULL_APPLICATION_TRACE','asset_id':job['asset_id'],'suite':task['suite'],'source_version':task.get('version',task.get('source_version','UNKNOWN')),'program':task['program'],'variant':task.get('variant','DECLARED_DEFAULT'),'input_identity':task.get('input_identity',task.get('input_files')),'argv':task['argv'],'binary_member':binary_member,'binary_sha256':m['binary_sha256'],'capture_gpu_uuid':receipt['actual_gpu_uuid'],'actual_cubin_arch':89,'embedded_PTX_listing':subprocess.check_output(['/usr/local/cuda-12.8/bin/cuobjdump','-lptx',str(binary)],text=True),'producer_sha256':sha(TOOL),'contract_sha256':sha(CONTRACT/'CONTRACT.json'),'validator_sha256':sha(VALIDATOR),'frozen_parser_sha256':sha(CONTRACT/'validate_v7.py'),'map_manifest_sha256':sha(root/'map/manifest.json'),'map_maker_sha256':sha(MAPPER),'postprocessor_sha256':sha(POST),'pump_sha256':sha(R/'control/ssh_rate_bridge_v2.py'),'worker_sha256':sha(pathlib.Path(__file__)),'full_application':{'kernel_launches':val['kernels'],'ctas':val['ctas'],'warps':val['warps'],'records':val['counts']['sass_records'],'all_warps_terminate':True,'expected_kernel_presence':'YES_SOURCE_ORACLE','expected_kernel_count':job.get('expected_kernel_count'),'context_count':1,'stream_ids':val['stream_ids'],'sampling':'NONE','commandlist':'traces/kernelslist.g'},'tracer_control_flags':receipt['tracer_control_flags'],'capture_limits':receipt['capture_limits'],'numerical_status':numerical,'input_byte_identity_qualification':job.get('input_byte_identity_qualification','DECLARED_FILE_SHA_OR_DETERMINISTIC_SOURCE;NO_UNRECORDED_SEED_CLAIM'),'native_state':job.get('native_state'),'producer_semantic_qualification':'ADA7_ORDINARY_FULL_RECORD_PASS','consumer_qualification':'NOT_AUTOMATICALLY_GRANTED; per-profile required','hardware_timing_calibration':'NOT_GRANTED','source_keep':True,'release_bytes':0}
 asset['ordinary_validator_cpu2']={'profile':'ORDINARY_WHOLEJOB_VALIDATOR_CPU2_CANDIDATE_V1','frozen_validator_sha256':val['frozen_validator_sha256'],'adapter_sha256':sha(VALIDATOR),'closure_ack':closed,'Root_grant_sha256':v2cfg['grant_sha256'],'rate_bytes_sec':v2cfg['rate_bytes_sec'],'does_not_grant_consumer_or_science':True}
 package=VALIDATOR.parent.parent;code_manifest=json.loads((VALIDATOR.parent/'CODE_MANIFEST.json').read_text())
 for relative,row in code_manifest['files'].items():
  source=package/relative;assert sha(source)==row['sha256'];copy(source,root/'tools/validator_cpu2'/relative)
 copy(VALIDATOR.parent/'CODE_MANIFEST.json',root/'tools/validator_cpu2/candidate/CODE_MANIFEST.json')
 asset['ordinary_validator_cpu2']['code_manifest_sha256']=sha(VALIDATOR.parent/'CODE_MANIFEST.json')
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
 if io:
  # No explicit UNLOCK on unknown descendant closure. Closing only our local
  # reference leaves the whole-job OFD lock with any surviving inherited refs.
  if not validator_parallel_started or validator_parallel_closed:fcntl.flock(io,fcntl.LOCK_UN)
  io.close()
