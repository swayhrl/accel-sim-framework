#!/usr/bin/env python3
"""Single immutable ordinary-input capture. Native174 owns global transport leases."""
import pathlib,os,json,subprocess,time,fcntl,hashlib,signal,re,shutil,sys,traceback
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1');N=R/'nas_rtx4080';S=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1')
TOOL=S/'frozen/producer_v7_55c6f482/producer.so';CONTRACT=S/'frozen/ada7_contract_v1';VALIDATOR=R/'control/validate_v7_stream_v3.py';POST=R/'control/postprocess_nas_sharded_v2.py';MAPPER=R/'control/make_semantic_map_v2.py'
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
receipt={'job_id':jobid,'task':task,'started':time.time(),'status':'PREPARING','worker_pid':os.getpid(),'worker_start_ticks':ticks(os.getpid()),'actual_gpu_uuid':'GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59','pipeline_sha256':sha(pathlib.Path(__file__))};gpu=None;io=None;p=None
try:
 io=open(R/'control/RTX4080_LOCAL_IO.lock','a');fcntl.flock(io,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert sha(binary)==task['binary_sha256']
 assert sha(TOOL)=='55c6f4829e8c92e11e0ab54496bf8f507f6cfa3a10cd01a857c6de147ee68b73'
 assert sha(CONTRACT/'CONTRACT.json')=='97901eb373fc94b041c5ef6923e0e5ca1635edd1bac4213d53c28271abb6c184'
 assert sha(VALIDATOR)=='f9f8a05ca7e0f8afe60e7d9a34f4884a9d1cb920b2212e41ed9a4faf19975af1'
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
 for x in task.get('runtime_links',[]):
  rel=x.get('link',x.get('name'));src=pathlib.Path(x.get('target',x.get('source')));dest=runtime/rel
  assert runtime.resolve() in dest.resolve().parents
  if src.is_dir():shutil.copytree(src,dest)
  else:copy(src,dest)
 env=os.environ.copy();env.update(task.get('runtime_env',{}));env.update(task.get('env',{}))
 for k in list(env):
  if k.startswith(('TRACE_','TOOL_','DYNAMIC_','NVBIT_','C16_')) or k in ['LD_PRELOAD','CUDA_INJECTION64_PATH','ACTIVE_FROM_START']:env.pop(k,None)
 env.update(LD_PRELOAD=str(TOOL)+':libcuda.so.1',ADA_SEMANTIC_MAP=str(root/'map/semantic-map.tsv'),TRACES_FOLDER=str(root),ACTIVE_FROM_START='1',TRACE_FILE_COMPRESS='1',TOOL_COMPRESS='1',DYNAMIC_KERNEL_RANGE='',PATH='/usr/local/cuda-12.8/bin:'+env.get('PATH',''),NVDISASM='/usr/local/cuda-12.8/bin/nvdisasm',CUDA_VISIBLE_DEVICES='GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
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
   if time.monotonic()-start>task.get('capture_timeout_sec',21600):receipt['bounded_stop']='capture wall bound'
   size=sum(x.stat().st_size for x in root.rglob('*') if x.is_file())
   if size>task.get('capture_max_bytes',80*1024**3):receipt['bounded_stop']='capture byte bound'
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
 assert p.returncode==0 and not receipt.get('bounded_stop'),'capture did not finish normally'
 stdout=(root/'stdout.log').read_text(errors='replace');assert re.search(task['correctness']['stdout_regex'],stdout),'capture numerical QA marker missing'
 cp=subprocess.run(['python3',str(VALIDATOR),str(root),str(root/'map/manifest.json')],capture_output=True,text=True,timeout=86400);(root/'VALIDATOR.log').write_text(cp.stdout+cp.stderr);assert cp.returncode==0,cp.stderr
 val=json.loads(cp.stdout);assert val['status']=='ADA7_ORDINARY_FULL_RECORD_PASS'
 if 'expected_kernel_count' in job:assert val['kernels']==job['expected_kernel_count'],'expected kernel count'
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
 for name,src in [('validate_v7_stream_v3.py',VALIDATOR),('postprocess_nas_sharded_v2.py',POST),('ssh_rate_bridge.py',R/'control/ssh_rate_bridge.py'),('capture_ordinary_worker.py',pathlib.Path(__file__)),('make_semantic_map_v2.py',MAPPER)]:copy(src,root/'tools'/name)
 for f in CONTRACT.iterdir():
  if f.is_file():copy(f,root/'contract'/f.name)
 for i,x in enumerate(task.get('sources',[])):
  f=pathlib.Path(x['path']);assert sha(f)==x['sha256'];copy(f,root/'source'/('%03d_'%i+f.name))
 save(root/'TASK.json',task);save(root/'NATIVE_QUALIFICATION.json',job['native_receipt'])
 asset={'schema':'RTX4080_FULL_TRACE_ASSET_V1','kind':'FULL_APPLICATION_TRACE','asset_id':job['asset_id'],'suite':task['suite'],'source_version':task['version'],'program':task['program'],'variant':task['variant'],'input_identity':task.get('input_identity'),'argv':task['argv'],'binary_member':binary_member,'binary_sha256':m['binary_sha256'],'capture_gpu_uuid':receipt['actual_gpu_uuid'],'actual_cubin_arch':89,'embedded_PTX_listing':subprocess.check_output(['/usr/local/cuda-12.8/bin/cuobjdump','-lptx',str(binary)],text=True),'producer_sha256':sha(TOOL),'contract_sha256':sha(CONTRACT/'CONTRACT.json'),'validator_sha256':sha(VALIDATOR),'frozen_parser_sha256':sha(CONTRACT/'validate_v7.py'),'map_manifest_sha256':sha(root/'map/manifest.json'),'map_maker_sha256':sha(MAPPER),'postprocessor_sha256':sha(POST),'pump_sha256':sha(R/'control/ssh_rate_bridge.py'),'worker_sha256':sha(pathlib.Path(__file__)),'full_application':{'kernel_launches':val['kernels'],'ctas':val['ctas'],'warps':val['warps'],'records':val['counts']['sass_records'],'all_warps_terminate':True,'expected_kernel_presence':'YES_SOURCE_ORACLE','expected_kernel_count':job.get('expected_kernel_count'),'context_count':1,'stream_ids':val['stream_ids'],'sampling':'NONE','commandlist':'traces/kernelslist.g'},'numerical_status':'NATIVE_AND_CAPTURE_QA_PASS','producer_semantic_qualification':'ADA7_ORDINARY_FULL_RECORD_PASS','consumer_qualification':'NOT_AUTOMATICALLY_GRANTED; per-profile required','hardware_timing_calibration':'NOT_GRANTED','source_keep':True,'release_bytes':0}
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

