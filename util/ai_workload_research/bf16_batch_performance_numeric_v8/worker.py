"""One locked BF16 strong-Mode-A engine, six pre-frozen batched request points."""
import os,sys,pathlib,json,time,math,hashlib,dataclasses,traceback
from persistence import save_json
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/ai_workload_research/runs/QWEN_BF16_BATCH_PERFORMANCE_NUMERIC_STUDY_109_V8'
P=OUT/'.private'
MODEL=pathlib.Path('/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct/aa8e72537993ba99e69dfaafa59ed015b17504d1')
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def save(path,v):
 if path.parent==OUT/'raw' and 'samples' in v:
  shallow=dict(v);indices=[]
  folder=OUT/'raw'/(path.stem+'_samples');folder.mkdir(exist_ok=True)
  for sample in v['samples']:
   name=f"{sample['index']:04d}.json";target=folder/name
   from persistence import safe_json
   content=json.dumps(safe_json(sample),indent=2,allow_nan=False)+"\n"
   if not target.exists() or target.read_text()!=content:target.write_text(content)
   indices.append({k:sample.get(k) for k in ['index','config','point','role','round','block','batch_size','output_tokens_each','request_gpu_elapsed_ms','host_generate_call_ms','host_synchronized_request_ms','status']}|dict(file=str(target.relative_to(OUT)),sha256=sha(target.read_bytes())))
  shallow['samples']=indices;save_json(path,shallow)
 else:save_json(path,v)
def main():
 assert os.environ.get('WEIGHT_PROBE_LOCK_OWNER')
 started=time.monotonic();task=sys.argv[1];prefix_enabled=task=='PREFIX';path=OUT/'raw'/(task+'.json')
 raw=dict(status='RUNNING',pid=os.getpid(),samples=[],model_initializations=0,task=task);secret=dict(samples=[]);phase=['INIT'];graphs=[]
 try:
  import torch,vllm
  from vllm import LLM,SamplingParams
  from vllm.config.compilation import CompilationConfig,CompilationMode,CUDAGraphMode
  from vllm.compilation.counter import compilation_counter
  from vllm.compilation.decorators import TorchCompileWithNoGuardsWrapper
  from vllm.v1.worker.gpu.cudagraph_utils import ModelCudaGraphManager
  c=json.load(open(OUT/'SCIENCE_CONTRACT.json'));inputs=json.load(open(P/'inputs.json'));old=json.load(open(OUT/'SOURCE_AND_RUNTIME.json'));reference=json.load(open(P/'reference.json'))['formal_rows'][0]
  site=pathlib.Path(vllm.__file__).parent
  hashes={k:sha((site/rel).read_bytes()) for k,rel in [('compilation.py','config/compilation.py'),('qwen2.py','model_executor/models/qwen2.py')]}
  assert hashes==old['vllm_installed_source_sha256']
  original=ModelCudaGraphManager.run_fullgraph
  def counted(self,desc):
   value=original(self,desc)
   if phase[0]!='INIT':
    graphs.append(dict(num_tokens=desc.num_tokens,num_reqs=desc.num_reqs,uniform_token_count=desc.uniform_token_count,max_query_len=desc.max_query_len,cg_mode=str(desc.cg_mode),descriptor=str(desc)))
   return value
  ModelCudaGraphManager.run_fullgraph=counted
  cache=pathlib.Path(os.environ['VLLM_CACHE_ROOT']).parent
  cc=CompilationConfig(mode=CompilationMode.VLLM_COMPILE,backend='inductor',cudagraph_mode=CUDAGraphMode.FULL_AND_PIECEWISE,cache_dir=str(cache/'compilation'))
  init=time.monotonic();raw['model_initializations']=1;save(path,raw)
  llm=LLM(model=str(MODEL),tokenizer=str(MODEL),skip_tokenizer_init=True,dtype='bfloat16',quantization=None,model_impl='vllm',enforce_eager=False,tensor_parallel_size=1,max_model_len=544,max_num_batched_tokens=1088,max_num_seqs=2,gpu_memory_utilization=0.92,cpu_offload_gb=0,enable_prefix_caching=prefix_enabled,seed=0,disable_log_stats=True,compilation_config=cc)
  runner=llm.llm_engine.model_executor.driver_worker.model_runner;cfg=runner.vllm_config;cc=cfg.compilation_config;model=runner.get_model();manager=runner.cudagraph_manager
  assert not cfg.model_config.enforce_eager and cc.mode==CompilationMode.VLLM_COMPILE and cc.backend=='inductor' and cc.cudagraph_mode==CUDAGraphMode.FULL_AND_PIECEWISE
  assert cfg.model_config.dtype==torch.bfloat16 and cfg.model_config.quantization is None and cfg.parallel_config.tensor_parallel_size==1
  assert cfg.model_config.max_model_len==544 and cfg.scheduler_config.max_num_batched_tokens==1088 and cfg.scheduler_config.max_num_seqs==2
  assert cfg.cache_config.enable_prefix_caching==prefix_enabled and torch.cuda.get_device_capability(0)==(8,9)
  assert cc.local_cache_dir is None or pathlib.Path(cc.local_cache_dir).is_relative_to(cache)
  mods=list(model.named_modules())
  attention=sorted({type(m.impl).__name__ for _,m in mods if getattr(m,'impl',None) is not None and type(m.impl).__name__.endswith('AttentionImpl')})
  linear=sorted({type(m.quant_method).__name__ for _,m in mods if getattr(m,'quant_method',None) is not None and type(m.quant_method).__name__.endswith('LinearMethod')})
  assert attention==['FlashAttentionImpl'] and linear==['UnquantizedLinearMethod']
  raw['runtime']=dict(vllm=vllm.__version__,torch=torch.__version__,source_sha256=hashes,attention=attention,linear=linear,capacity=dict(max_model_len=544,max_num_batched_tokens=1088,max_num_seqs=2),compilation_mode=cc.mode.name,backend=cc.backend,cudagraph_mode=cc.cudagraph_mode.name,cache_root=str(cache),local_cache_dir=str(cc.local_cache_dir),cache_identity='NEW_MODE_A_COMPILATION_IDENTITY',initialization_seconds=time.monotonic()-init,graph_observation='Accepted manager-level fullgraph counter only; descriptors may contain padding and are not kernel/profiler observations.')
  def compiled():
   return [dict(name=n,cls=type(m).__name__,do_not_compile=bool(getattr(m,'do_not_compile',True)),compiled=bool(getattr(m,'compiled',False)),aot=getattr(m,'aot_compiled_fn',None) is not None) for n,m in model.named_modules() if isinstance(m,TorchCompileWithNoGuardsWrapper)]
  stable=('num_backend_compilations','num_cudagraph_captured','num_inductor_compiles','num_eager_compiles','num_cache_entries_updated','num_compiled_artifacts_saved','num_aot_compiles','num_aot_artifacts_saved')
  import inspect,statistics
  from capture import capture_batch
  from numeric_observation import compare,validate
  raw['runtime'].update(runner_class=type(runner).__module__+'.'+type(runner).__name__,sampler_class=type(runner.sampler).__module__+'.'+type(runner.sampler).__name__,
    sampler_source=inspect.getsourcefile(type(runner.sampler)),sampler_source_sha256=sha(pathlib.Path(inspect.getsourcefile(type(runner.sampler))).read_bytes()),
    sampler_logprobs_mode=runner.sampler.logprobs_mode,lm_head_dtype=str(model.lm_head.weight.dtype),
    logits_head_dtype=str(getattr(model.logits_processor,'head_dtype',None)),enable_prefix_caching=prefix_enabled)
  points={p['point']:p for p in c['points']};repeat={};b1={};observations=[];completed={}
  private_path=P/(task+'_private_outputs.json')
  current_config=['']
  def execute(config,point_id,role,ri,block='INITIAL',override_count=None):
   point=points[point_id];sources=point['sources'];count=point['output_tokens'] if override_count is None else override_count
   prompts=[inputs[src+'_512'] for src in sources];assert all(len(x)==512 for x in prompts)
   lp=None if config=='LP_NONE' else 20
   sampling=SamplingParams(temperature=0,top_p=1,max_tokens=count,ignore_eos=True,detokenize=False,logprobs=lp)
   phase[0]=role;current_config[0]=config;graphs.clear();before=dataclasses.asdict(compilation_counter.clone());gbefore={str(k) for k in manager.graphs}
   torch.cuda.synchronize();start=torch.cuda.Event(enable_timing=True);stop=torch.cuda.Event(enable_timing=True)
   host_sync_start=time.perf_counter_ns();start.record();host_start=time.perf_counter_ns()
   responses=llm.generate([dict(prompt_token_ids=ids) for ids in prompts],sampling,use_tqdm=False)
   host_end=time.perf_counter_ns();stop.record();torch.cuda.synchronize();host_sync_end=time.perf_counter_ns()
   elapsed=float(start.elapsed_time(stop))
   sample=dict(config=config,point=point_id,role=role,round=ri,block=block,index=len(raw['samples']),batch_size=len(sources),output_tokens_each=count,
     request_gpu_elapsed_ms=elapsed,host_generate_call_ms=(host_end-host_start)/1e6,host_synchronized_request_ms=(host_sync_end-host_sync_start)/1e6)
   after=dataclasses.asdict(compilation_counter.clone());newgraphs=sorted({str(k) for k in manager.graphs}-gbefore)
   active=[m for m in compiled() if m['cls']=='Qwen2Model' and not m['do_not_compile'] and (m['compiled'] or m['aot'])]
   execution=dict(graph_replays=list(graphs),new_graph_descriptors=newgraphs,counters_before=before,counters_after=after,active_compiled_Qwen2Model=active,
     actual_request_description=dict(requests=len(responses),input_lengths=[len(x) for x in prompts],requested_output_tokens=count,source_order=list(sources)),
     sampling=dict(temperature=0,top_p=1,max_tokens=count,ignore_eos=True,detokenize=False,logprobs=lp),prefix_enabled=prefix_enabled)
   private=capture_batch(responses,sources,prompts,sample,raw,secret,path,private_path,execution,persist=save)
   private.update(config=config,index=sample['index'],block=block)
   save(private_path,secret)
   assert len(responses)==len(prompts),'Wrong request count'
   assert math.isfinite(elapsed) and elapsed>0,'Invalid CUDA-event time'
   assert sample['host_synchronized_request_ms']>0 and math.isfinite(sample['host_synchronized_request_ms'])
   assert active,'Compiled Qwen2Model inactive'
   if count==32:assert graphs,'32-token fullgraph replay absent'
   sample['validity']=dict(INPUT_AND_RUNTIME_VALIDITY='PASS',PERFORMANCE_MEASUREMENT_VALIDITY='VALID_DIAGNOSTIC_ONLY' if role in ['OBSERVER','CACHE_PRIME'] else 'VALID',
      TOKEN_SEQUENCE_IDENTITY='OBSERVED_SEPARATELY',LOGPROB_NUMERIC_SENSITIVITY='OBSERVED_SEPARATELY' if lp is not None else 'UNOBSERVED_NONE_PATH',ARCHITECTURAL_CAUSAL_EVIDENCE='NOT_ESTABLISHED')
   sample['formal_compile_or_capture']=bool(role=='FORMAL' and (newgraphs or any(after[k]!=before[k] for k in stable)))
   for si,row in enumerate(private['outputs']):
    validate(row,prompts[si],count,lp)
    ids=row['tokens'];prob=row['logprobs']
    sample['outputs'][si].update(sampled_logprob_sha256=digest(row['completions'][0]['sampled_token_logprobs']) if lp is not None else None,all_finite=True)
    observation=dict(config=config,index=sample['index'],source=sources[si],point=point_id,role=role,round=ri)
    if role not in ['CACHE_PRIME','OBSERVER']:
     key=(config,point_id,sources[si],count)
     if key not in repeat:repeat[key]=row
     observation['same_point']=compare(repeat[key],row,lp is not None)
     ck=(config,sources[si],count)
     if len(sources)==1 and ck not in b1:b1[ck]=row
     if len(sources)==2 and ck in b1:observation['B1_B2']=compare(b1[ck],row,lp is not None)
     if sources[si]=='TRAIN_A_DISCOVERY_00' and count==32:
      reference_row=dict(tokens=reference['tokens'],logprobs=[{str(token):val} for token,val in zip(reference['tokens'],reference['sampled_logprobs'])])
      observation['historical']=compare(reference_row,row,lp is not None)
    sample.setdefault('numeric_observations',[]).append(observation)
   sample['status']='PASS_RUNTIME_VALID';save(path,raw)
   return sample
  def noisy(configs):
   for config in configs:
    for point in points:
     rows=[s for s in raw['samples'] if s['config']==config and s['point']==point and s['role']=='FORMAL']
     if not rows:continue
     vals=[s['request_gpu_elapsed_ms'] for s in rows];median=statistics.median(vals)
     if statistics.median(abs(x-median) for x in vals)/median>.05 or any(s['formal_compile_or_capture'] for s in rows):return True
   return False
  def series(configs,apc=False):
   for role,orders in [('WARMUP',c['warmup_rounds']),('FORMAL',c['formal_rounds'])]:
    for ri,order in enumerate(orders):
     for pi,point_id in enumerate(order):
      ordered=configs if (ri+pi)%2==0 else list(reversed(configs))
      for config in ordered:
       if apc:
        assert llm.reset_prefix_cache() is True,'Prefix reset failed'
        if config=='APC_WARM':execute(config,point_id,'CACHE_PRIME',ri,block=role,override_count=1)
       execute(config,point_id,role,ri)
   trigger=noisy(configs);raw.setdefault('adaptive_decisions',[]).append(dict(configs=configs,triggered=trigger,extra_rounds=5 if trigger else 0,reason='MAD/median>0.05 or formal compile/capture;allconfigsandpointsrepeat,no selection'))
   save(path,raw)
   if trigger:
    for ri,order in enumerate(c['formal_rounds'],start=5):
     for pi,point_id in enumerate(order):
      for config in (configs if (ri+pi)%2==0 else list(reversed(configs))):
       if apc:
        assert llm.reset_prefix_cache() is True,'Prefix reset failed'
        if config=='APC_WARM':execute(config,point_id,'CACHE_PRIME',ri,block='EXTRA',override_count=1)
       execute(config,point_id,'FORMAL',ri,block='EXTRA')
   for config in configs:
    counts={point:sum(s['config']==config and s['point']==point and s['role']=='FORMAL' for s in raw['samples']) for point in points}
    assert all(n>=5 for n in counts.values())
    completed[config]=counts
   raw['config_completion']=completed;save(path,raw)
  if task=='BASE':
   series(['MAIN'])
   series(['LP20_CONTROL','LP_NONE'])
   raw['optional_observer']={'status':'NOT_STARTED'};save(path,raw)
   from local_observer import LocalObserver
   observer=LocalObserver(runner,model,P/'OBSERVER',torch)
   try:
    observer.install()
    for point_id in ['P4','P5','P6']:
     observer.begin(point_id)
     execute('LOCAL_OBSERVER',point_id,'OBSERVER',0)
     observer.finish()
    raw['optional_observer']=observer.receipt()
   except (AttributeError,NotImplementedError) as error:
    raw['optional_observer']=dict(status='OPTIONAL_UNSUPPORTED',error=str(error))
   finally:
    observer.restore();save(path,raw)
  else:
   assert callable(getattr(llm,'reset_prefix_cache',None))
   series(['APC_COLD','APC_WARM'],apc=True)
  raw['status']='V8_WORKER_COMPLETE'
 except BaseException as e:
  raw.update(status='V8_WORKER_OPTIONAL_UNAVAILABLE' if task=='PREFIX' and (isinstance(e,(AttributeError,NotImplementedError)) or str(e)=='Prefix reset failed') else 'NUMERIC_OR_RUNTIME_NO_GO',error=str(e),optional_error=str(e),error_type=type(e).__name__,traceback=traceback.format_exc())
 finally:
  raw['context_seconds']=time.monotonic()-started;save(path,raw);save(P/(task+'_private_outputs.json'),secret)
 print(json.dumps(dict(status=raw['status'],samples=len(raw['samples']))),flush=True)
 return 0 if raw['status'] in ['V8_WORKER_COMPLETE','V8_WORKER_OPTIONAL_UNAVAILABLE'] else 2
if __name__=='__main__':raise SystemExit(main())
