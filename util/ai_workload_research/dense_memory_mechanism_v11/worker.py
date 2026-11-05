"""V9 native length curve and separately labeled optional evidence tasks."""
import os,sys,pathlib,json,time,math,hashlib,dataclasses,traceback,statistics
from persistence import save_json,safe_json
from shared_gate import identity
ROOT=pathlib.Path('/home/huangrulin/workspace/worktrees/accel-sim-aiarch-dense-memory-mechanism-convergence-109-v11')
OUT=ROOT/'docs/ai_workload_research/runs/QWEN_DENSE_MEMORY_MECHANISM_CONVERGENCE_109_V11'
P=OUT/'.private'
MODEL=pathlib.Path('/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct/aa8e72537993ba99e69dfaafa59ed015b17504d1')
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def save(path,value):save_json(path,value)
def append(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 data=json.dumps(safe_json(value),separators=(',',':'),allow_nan=False)+'\n'
 with path.open('a') as f:f.write(data);f.flush();os.fsync(f.fileno())
 return sha(data.encode())
def main():
 assert os.environ.get('WEIGHT_PROBE_LOCK_OWNER')
 task=sys.argv[1];altered=task=='NUMERIC';context=P/task;started=time.monotonic()
 owner=dict(task=task,nonce=os.environ['V9_WORKER_NONCE'],supervisor_pid=int(os.environ['WEIGHT_PROBE_LOCK_OWNER']),identity=identity(os.getpid()),worker_sha256=sha(pathlib.Path(__file__).read_bytes()))
 save(context/'WORKER_IDENTITY.json',owner)
 path=OUT/'raw'/(task+'.json')
 raw=dict(status='RUNNING',task=task,model_initializations=0,samples=[],optional=task!='CURVE',worker_identity=owner)
 phase=['INIT'];graphs={}
 try:
  if task.startswith('PILOT') or task.startswith('LOCAL'):
   from controlled_worker import run
   raw.update(run(task,context,OUT));return 0
  if os.environ.get('V9_OPTIONAL_SKIP_REASON'):
   raw.update(status='V9_OPTIONAL_UNAVAILABLE',error=os.environ['V9_OPTIONAL_SKIP_REASON'])
   return 0
  import torch,vllm
  from vllm import LLM,SamplingParams
  from vllm.config.compilation import CompilationConfig,CompilationMode,CUDAGraphMode
  from vllm.compilation.counter import compilation_counter
  from vllm.compilation.decorators import TorchCompileWithNoGuardsWrapper
  from vllm.v1.worker.gpu.cudagraph_utils import ModelCudaGraphManager
  c=json.load(open(OUT/'SCIENCE_CONTRACT.json'));inputs=json.load(open(P/'inputs.json'));old=json.load(open(OUT/'SOURCE_AND_RUNTIME.json'));reference=json.load(open(P/'reference.json'))['formal_rows'][0]
  site=pathlib.Path(vllm.__file__).parent
  hashes={k:sha((site/rel).read_bytes()) for k,rel in [('compilation.py','config/compilation.py'),('qwen2.py','model_executor/models/qwen2.py')]}
  assert hashes==old['vllm_installed_source_sha256'], 'VALIDITY: initialization model/source/runtime identity'
  original=ModelCudaGraphManager.run_fullgraph
  ncu_capture=[False]
  def counted(self,desc):
   label=str(desc)
   if phase[0]!='INIT':graphs[label]=graphs.get(label,0)+1
   profile=phase[0]=='PROFILED'
   first=profile and task.startswith('NCU') and not ncu_capture[0]
   if first:
    torch.cuda.synchronize();torch.cuda.profiler.start();ncu_capture[0]=True
   if profile:torch.cuda.nvtx.range_push('decodeGraph')
   try:
    value=original(self,desc)
    if first:torch.cuda.synchronize()
    return value
   finally:
    if profile:torch.cuda.nvtx.range_pop()
    if first:torch.cuda.profiler.stop()
  ModelCudaGraphManager.run_fullgraph=counted
  cache=pathlib.Path(os.environ['VLLM_CACHE_ROOT']).parent
  cc=CompilationConfig(mode=CompilationMode.NONE if altered else CompilationMode.VLLM_COMPILE,backend='inductor',cudagraph_mode=CUDAGraphMode.NONE if altered else CUDAGraphMode.FULL_AND_PIECEWISE,cache_dir=str(cache/'compilation'))
  init=time.monotonic();raw['model_initializations']=1;save(path,raw)
  llm=LLM(model=str(MODEL),tokenizer=str(MODEL),skip_tokenizer_init=True,dtype='bfloat16',quantization=None,model_impl='vllm',enforce_eager=altered,tensor_parallel_size=1,max_model_len=544,max_num_batched_tokens=1088,max_num_seqs=2,gpu_memory_utilization=0.92,cpu_offload_gb=0,enable_prefix_caching=False,seed=0,disable_log_stats=True,compilation_config=cc)
  runner=llm.llm_engine.model_executor.driver_worker.model_runner;cfg=runner.vllm_config;cc=cfg.compilation_config;model=runner.get_model();manager=runner.cudagraph_manager
  assert (cfg.model_config.enforce_eager and cc.mode==CompilationMode.NONE and cc.cudagraph_mode==CUDAGraphMode.NONE) if altered else (not cfg.model_config.enforce_eager and cc.mode==CompilationMode.VLLM_COMPILE and cc.backend=='inductor' and cc.cudagraph_mode==CUDAGraphMode.FULL_AND_PIECEWISE), 'VALIDITY: initialization model/source/runtime identity'
  assert cfg.model_config.dtype==torch.bfloat16 and cfg.model_config.quantization is None and cfg.parallel_config.tensor_parallel_size==1, 'VALIDITY: initialization model/source/runtime identity'
  assert cfg.model_config.max_model_len==544 and cfg.scheduler_config.max_num_batched_tokens==1088 and cfg.scheduler_config.max_num_seqs==2, 'VALIDITY: initialization model/source/runtime identity'
  assert not cfg.cache_config.enable_prefix_caching and torch.cuda.get_device_capability(0)==(8,9), 'VALIDITY: initialization model/source/runtime identity'
  assert cc.local_cache_dir is None or pathlib.Path(cc.local_cache_dir).is_relative_to(cache), 'VALIDITY: initialization model/source/runtime identity'
  mods=list(model.named_modules())
  raw['linear_weight_identity']=[dict(module=n,shape=list(m.weight.shape),stride=list(m.weight.stride()),dtype=str(m.weight.dtype),method=type(m.quant_method).__name__) for n,m in mods if getattr(m,'weight',None) is not None and getattr(m,'quant_method',None) is not None]
  attention=sorted({type(m.impl).__name__ for _,m in mods if getattr(m,'impl',None) is not None and type(m.impl).__name__.endswith('AttentionImpl')})
  linear=sorted({type(m.quant_method).__name__ for _,m in mods if getattr(m,'quant_method',None) is not None and type(m.quant_method).__name__.endswith('LinearMethod')})
  assert attention==['FlashAttentionImpl'] and linear==['UnquantizedLinearMethod'], 'VALIDITY: initialization model/source/runtime identity'
  raw['runtime']=dict(vllm=vllm.__version__,torch=torch.__version__,source_sha256=hashes,attention=attention,linear=linear,capacity=dict(max_model_len=544,max_num_batched_tokens=1088,max_num_seqs=2),compilation_mode=cc.mode.name,backend=cc.backend,cudagraph_mode=cc.cudagraph_mode.name,cache_root=str(cache),local_cache_dir=str(cc.local_cache_dir),cache_identity='V9_PRIVATE_COMPILATION_IDENTITY',initialization_seconds=time.monotonic()-init,graph_observation='Accepted manager-level fullgraph counter only; descriptors may contain padding and are not kernel/profiler observations.')
  def compiled():
   return [dict(name=n,cls=type(m).__name__,do_not_compile=bool(getattr(m,'do_not_compile',True)),compiled=bool(getattr(m,'compiled',False)),aot=getattr(m,'aot_compiled_fn',None) is not None) for n,m in model.named_modules() if isinstance(m,TorchCompileWithNoGuardsWrapper)]
  stable=('num_backend_compilations','num_cudagraph_captured','num_inductor_compiles','num_eager_compiles','num_cache_entries_updated','num_compiled_artifacts_saved','num_aot_compiles','num_aot_artifacts_saved')
  import inspect
  from numeric_observation import validate
  raw['runtime'].update(runner_class=type(runner).__module__+'.'+type(runner).__name__,
    sampler_class=type(runner.sampler).__module__+'.'+type(runner.sampler).__name__,sampler_source_sha256=sha(pathlib.Path(inspect.getsourcefile(type(runner.sampler))).read_bytes()),
    actual_enforce_eager=cfg.model_config.enforce_eager,altered_diagnostic_path=altered,logprobs=None,enable_prefix_caching=False)
  points={p['point']:p for p in c['points']}
  stable_names=stable
  public_journal=OUT/'raw'/(task+'_records.jsonl');private_journal=context/'completions.jsonl'
  profile_markers=None
  if task=='NSYS':
   from profile_markers import RunnerMarkers
   profile_markers=RunnerMarkers(runner,torch)
  boundary=None
  if altered:
   from sparse_boundaries import SparseBoundaries
   boundary=SparseBoundaries(runner,model,context/'boundaries',torch);boundary.install()
  def execute(point_id,role,ri,block='INITIAL'):
   point=points[point_id];sources=point['sources'];count=point['output_tokens'];prompts=[inputs[s+'_512'] for s in sources]
   assert all(len(x)==512 for x in prompts)
   sampling=SamplingParams(temperature=0,top_p=1,max_tokens=count,ignore_eos=True,detokenize=False,logprobs=None)
   phase[0]=role;graphs.clear();before=dataclasses.asdict(compilation_counter.clone());gbefore={str(k) for k in manager.graphs} if manager else set()
   if boundary:boundary.begin(point_id)
   if profile_markers:profile_markers.enabled=role=='PROFILED';profile_markers.begin(point_id)
   torch.cuda.synchronize();start=torch.cuda.Event(enable_timing=True);stop=torch.cuda.Event(enable_timing=True)
   if role=='PROFILED':torch.cuda.nvtx.range_push('V9_REQUEST_'+point_id)
   host_sync_start=time.perf_counter_ns();start.record();host_start=time.perf_counter_ns()
   responses=llm.generate([dict(prompt_token_ids=ids) for ids in prompts],sampling,use_tqdm=False)
   host_end=time.perf_counter_ns();stop.record();torch.cuda.synchronize();host_sync_end=time.perf_counter_ns()
   if role=='PROFILED':torch.cuda.nvtx.range_pop()
   elapsed=float(start.elapsed_time(stop));idx=len(raw['samples'])
   after=dataclasses.asdict(compilation_counter.clone());active=[m for m in compiled() if m['cls']=='Qwen2Model' and not m['do_not_compile'] and (m['compiled'] or m['aot'])]
   newgraphs=sorted(({str(k) for k in manager.graphs} if manager else set())-gbefore)
   record=dict(event='RETURNED_ALL_REQUESTS',index=idx,point=point_id,mode=point['mode'],sources=sources,output_tokens_each=count,role=role,round=ri,block=block,
     request_gpu_elapsed_ms=elapsed,host_generate_call_ms=(host_end-host_start)/1e6,host_synchronized_request_ms=(host_sync_end-host_sync_start)/1e6,
     returned_requests=len(responses),fullgraph_replay_count=sum(graphs.values()),graph_descriptors=dict(graphs),counters_before=before,counters_after=after,new_graph_descriptors=newgraphs,
     active_compiled_Qwen2Model=active,logprobs_observability='UNOBSERVED_NONE_PATH',altered_path=altered,outputs=[])
   secret=dict(index=idx,point=point_id,role=role,round=ri,outputs=[])
   for si,response in enumerate(responses):
    comps=[]
    for out in response.outputs:
     ids=[int(x) for x in out.token_ids]
     probs=[{str(k):float(v.logprob) for k,v in step.items()} for step in out.logprobs] if out.logprobs is not None else []
     comps.append(dict(tokens=ids,logprobs=probs,finish_reason=out.finish_reason,stop_reason=out.stop_reason))
    row=dict(source=sources[si] if si<len(sources) else None,request_id=str(response.request_id),returned_prompt_token_ids=list(response.prompt_token_ids),completions=comps,num_cached_tokens=getattr(response,'num_cached_tokens',None))
    secret['outputs'].append(row)
    record['outputs'].append(dict(source=row['source'],request_id=row['request_id'],prompt_sha256=digest(row['returned_prompt_token_ids']),completion_count=len(comps),
      token_sha256=[digest(x['tokens']) for x in comps],num_cached_tokens=row['num_cached_tokens']))
   # Everycompletion and execution snapshot is persisted before any validity gate.
   private_hash=append(private_journal,secret);public_hash=append(public_journal,record)
   entry={k:record[k] for k in ['index','point','mode','output_tokens_each','role','round','block','request_gpu_elapsed_ms','host_generate_call_ms','host_synchronized_request_ms','fullgraph_replay_count']}
   entry.update(status='CAPTURED_PRE_VALIDATION',private_record_sha256=private_hash,public_record_sha256=public_hash);raw['samples'].append(entry);save(path,raw)
   assert len(responses)==len(prompts),'VALIDITY:request count mismatch'
   assert math.isfinite(elapsed) and elapsed>0,'VALIDITY:invalid CUDA timing'
   for row,prompt in zip(secret['outputs'],prompts):validate(row,prompt,count,None)
   if not altered:
    assert active,'VALIDITY:strong compiled Qwen2Model inactive'
    if count>1:assert sum(graphs.values())==count-1,'VALIDITY:decode fullgraph count'
   contaminated=bool(role=='FORMAL' and (newgraphs or any(after[k]!=before[k] for k in stable_names)))
   entry.update(status='PASS_RUNTIME_VALID',formal_compile_capture=contaminated)
   append(public_journal,dict(event='VALIDATION',index=idx,status=entry['status'],formal_compile_capture=contaminated))
   save(path,raw)
   if boundary:boundary.finish(secret)
  if task=='CURVE':
   for role,orders in [('WARMUP',c['warmup_rounds']),('FORMAL',c['formal_rounds'])]:
    for ri,order in enumerate(orders):
     for point in order:execute(point,role,ri)
   trigger=False
   for point in points:
    rows=[s for s in raw['samples'] if s['point']==point and s['role']=='FORMAL'];vals=[s['request_gpu_elapsed_ms'] for s in rows];median=statistics.median(vals)
    if statistics.median(abs(x-median) for x in vals)/median>.05 or any(s['formal_compile_capture'] for s in rows):trigger=True
   raw['adaptive_decision']=dict(triggered=trigger,extra_rounds=5 if trigger else 0,all_points_symmetric=True);save(path,raw)
   if trigger:
    for ri,order in enumerate(c['formal_rounds'],start=5):
     for point in order:execute(point,'FORMAL',ri,'EXTRA')
   raw['point_completion']={p:sum(s['point']==p and s['role']=='FORMAL' for s in raw['samples']) for p in points}
   assert all(n>=5 for n in raw['point_completion'].values())
  elif altered:
   for p in ['A00_N1','A01_N1','B2_N1','A00_N2','A01_N2','B2_N2']:execute(p,'ALTERED_NUMERIC',0)
   raw['boundary_receipt']=boundary.receipt();boundary.restore()
  else:
   targets=c['profiles']['targets'] if task=='NSYS' else ['A00_N32' if task.startswith('NCU_B1') else 'B2_N32']
   warms=c['profiles']['warmup_points'] if task=='NSYS' else targets
   for ri in range(2):
    for p in warms:execute(p,'PROFILE_WARMUP',ri)
   if task=='NSYS':torch.cuda.profiler.start()
   try:
    for p in targets:execute(p,'PROFILED',0)
   finally:
    if task=='NSYS':torch.cuda.profiler.stop()
   raw['profile_capture']=dict(task=task,targets=targets,ncu_first_decode_graph_capture=ncu_capture[0],not_formal=True)
  if profile_markers:profile_markers.restore()
  raw['status']='V9_WORKER_COMPLETE'
 except BaseException as error:
  raw.update(status='V9_RUNTIME_ERROR',error=str(error),error_type=type(error).__name__,traceback=traceback.format_exc(),validity_stop='VALIDITY:' in str(error))
 finally:
  raw['context_seconds']=time.monotonic()-started;save(path,raw)
  save(context/'WORKER_FINISHED.json',dict(**owner,status=raw['status'],model_initializations=raw['model_initializations']))
 print(json.dumps(dict(status=raw['status'],task=task,samples=len(raw['samples']))),flush=True)
 return 0 if raw['status'] in ['V9_WORKER_COMPLETE','V9_OPTIONAL_UNAVAILABLE'] else 2
if __name__=='__main__':raise SystemExit(main())
