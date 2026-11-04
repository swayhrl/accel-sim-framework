"""One locked BF16 strong-Mode-A engine, six pre-frozen batched request points."""
import os,sys,pathlib,json,time,math,hashlib,dataclasses,traceback
from persistence import save_json
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/ai_workload_research/runs/QWEN_BF16_DECODE_WEIGHT_SUPPLY_PROBE_109_V2'
P=OUT/'.private'
MODEL=pathlib.Path('/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct/aa8e72537993ba99e69dfaafa59ed015b17504d1')
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def save(path,v):
 save_json(path,v)
def main():
 assert os.environ.get('WEIGHT_PROBE_LOCK_OWNER')
 started=time.monotonic();path=OUT/'raw/PROBE.json'
 raw=dict(status='RUNNING',pid=os.getpid(),samples=[],model_initializations=0);secret=dict(samples=[]);phase=['INIT'];graphs=[]
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
  llm=LLM(model=str(MODEL),tokenizer=str(MODEL),skip_tokenizer_init=True,dtype='bfloat16',quantization=None,model_impl='vllm',enforce_eager=False,tensor_parallel_size=1,max_model_len=544,max_num_batched_tokens=1088,max_num_seqs=2,gpu_memory_utilization=0.92,cpu_offload_gb=0,enable_prefix_caching=False,seed=0,disable_log_stats=True,compilation_config=cc)
  runner=llm.llm_engine.model_executor.driver_worker.model_runner;cfg=runner.vllm_config;cc=cfg.compilation_config;model=runner.get_model();manager=runner.cudagraph_manager
  assert not cfg.model_config.enforce_eager and cc.mode==CompilationMode.VLLM_COMPILE and cc.backend=='inductor' and cc.cudagraph_mode==CUDAGraphMode.FULL_AND_PIECEWISE
  assert cfg.model_config.dtype==torch.bfloat16 and cfg.model_config.quantization is None and cfg.parallel_config.tensor_parallel_size==1
  assert cfg.model_config.max_model_len==544 and cfg.scheduler_config.max_num_batched_tokens==1088 and cfg.scheduler_config.max_num_seqs==2
  assert not cfg.cache_config.enable_prefix_caching and torch.cuda.get_device_capability(0)==(8,9)
  assert cc.local_cache_dir is None or pathlib.Path(cc.local_cache_dir).is_relative_to(cache)
  mods=list(model.named_modules())
  attention=sorted({type(m.impl).__name__ for _,m in mods if getattr(m,'impl',None) is not None and type(m.impl).__name__.endswith('AttentionImpl')})
  linear=sorted({type(m.quant_method).__name__ for _,m in mods if getattr(m,'quant_method',None) is not None and type(m.quant_method).__name__.endswith('LinearMethod')})
  assert attention==['FlashAttentionImpl'] and linear==['UnquantizedLinearMethod']
  raw['runtime']=dict(vllm=vllm.__version__,torch=torch.__version__,source_sha256=hashes,attention=attention,linear=linear,capacity=dict(max_model_len=544,max_num_batched_tokens=1088,max_num_seqs=2),compilation_mode=cc.mode.name,backend=cc.backend,cudagraph_mode=cc.cudagraph_mode.name,cache_root=str(cache),local_cache_dir=str(cc.local_cache_dir),cache_identity='NEW_MODE_A_COMPILATION_IDENTITY',initialization_seconds=time.monotonic()-init,graph_observation='Accepted manager-level fullgraph counter only; descriptors may contain padding and are not kernel/profiler observations.')
  def compiled():
   return [dict(name=n,cls=type(m).__name__,do_not_compile=bool(getattr(m,'do_not_compile',True)),compiled=bool(getattr(m,'compiled',False)),aot=getattr(m,'aot_compiled_fn',None) is not None) for n,m in model.named_modules() if isinstance(m,TorchCompileWithNoGuardsWrapper)]
  stable=('num_backend_compilations','num_cudagraph_captured','num_inductor_compiles','num_eager_compiles','num_cache_entries_updated','num_compiled_artifacts_saved','num_aot_compiles','num_aot_artifacts_saved')
  points={p['point']:p for p in c['points']};repeat={};b1={};cross=[];save(path,raw)
  for role,rounds in [('WARMUP',c['warmup_rounds']),('FORMAL',c['formal_rounds'])]:
   for ri,order in enumerate(rounds):
    for point_id in order:
     point=points[point_id];sources=point['sources'];count=point['output_tokens'];prompts=[inputs[src+'_512'] for src in sources];assert all(len(x)==512 for x in prompts)
     sampling=SamplingParams(temperature=0,top_p=1,max_tokens=count,ignore_eos=True,detokenize=False,logprobs=20)
     phase[0]=role;graphs.clear();before=dataclasses.asdict(compilation_counter.clone());gbefore={str(k) for k in manager.graphs}
     torch.cuda.synchronize();start=torch.cuda.Event(enable_timing=True);stop=torch.cuda.Event(enable_timing=True)
     host_sync_start=time.perf_counter_ns();start.record();host_start=time.perf_counter_ns()
     responses=llm.generate([dict(prompt_token_ids=ids) for ids in prompts],sampling,use_tqdm=False)
     host_end=time.perf_counter_ns();stop.record();torch.cuda.synchronize();host_sync_end=time.perf_counter_ns()
     elapsed=float(start.elapsed_time(stop));assert math.isfinite(elapsed) and elapsed>0
     sample=dict(point=point_id,role=role,round=ri,index=len(raw['samples']),batch_size=len(sources),output_tokens_each=count,request_gpu_elapsed_ms=elapsed,host_generate_call_ms=(host_end-host_start)/1e6,host_synchronized_request_ms=(host_sync_end-host_sync_start)/1e6,outputs=[])
     raw['samples'].append(sample);private=dict(point=point_id,role=role,round=ri,outputs=[]);secret['samples'].append(private)
     assert len(responses)==len(prompts)
     for si,response in enumerate(responses):
      assert list(response.prompt_token_ids)==prompts[si] and len(response.outputs)==1
      output=response.outputs[0];ids=[int(x) for x in output.token_ids]
      allprobs=[{str(k):float(v.logprob) for k,v in step.items()} for step in output.logprobs] if output.logprobs is not None else []
      private['outputs'].append(dict(source=sources[si],tokens=ids,logprobs=allprobs))
      # Persist every received response before applying scientific gates.
      sample['outputs'].append(dict(source=sources[si],token_count=len(ids),token_sha256=digest(ids),logprob_sha256=digest(allprobs)))
      save(P/'PROBE_private_outputs.json',secret);save(path,raw)
      assert len(ids)==count and len(allprobs)==count and all(math.isfinite(v) for step in allprobs for v in step.values())
      probs=[allprobs[j][str(token)] for j,token in enumerate(ids)];key=(point_id,sources[si])
      if key not in repeat:repeat[key]=(ids,probs)
      oldids,oldprobs=repeat[key];assert ids==oldids,'Same-point token repeatability failure'
      assert all(abs(a-b)<=0.05+0.01*abs(b) for a,b in zip(probs,oldprobs)),'Same-point logprob repeatability failure'
      hist='NOT_APPLICABLE'
      if sources[si]=='TRAIN_A_DISCOVERY_00' and count==32:
       assert ids==reference['tokens'],'Historical A00 token mismatch'
       assert all(abs(a-b)<=0.05+0.01*abs(b) for a,b in zip(probs,reference['sampled_logprobs'])),'Historical A00 logprob mismatch'
       hist='PASS_EXACT32_AND_FROZEN_LOGPROBS'
      sample['outputs'][-1].update(sampled_logprob_sha256=digest(probs),all_finite=True,historical=hist)
      ck=(sources[si],count)
      if len(sources)==1 and ck not in b1:b1[ck]=(ids,probs)
      if len(sources)==2:
       assert ck in b1,'Frozen warmup order must establish B1 reference'
       tids,tprobs=b1[ck];assert ids==tids,'B1/B2 tokens mismatch'
       maxerr=max(abs(a-b) for a,b in zip(probs,tprobs));assert all(abs(a-b)<=0.05+0.01*abs(b) for a,b in zip(probs,tprobs)),'B1/B2 sampled logprob mismatch'
       cross.append(dict(point=point_id,role=role,round=ri,source=sources[si],token_exact=True,max_sampled_logprob_abs_delta=maxerr,tolerance_pass=True))
     after=dataclasses.asdict(compilation_counter.clone());newgraphs=sorted({str(k) for k in manager.graphs}-gbefore);active=[m for m in compiled() if m['cls']=='Qwen2Model' and not m['do_not_compile'] and (m['compiled'] or m['aot'])]
     sample.update(graph_replays=list(graphs),new_graph_descriptors=newgraphs,counters_before=before,counters_after=after,active_compiled_Qwen2Model=active,status='PASS')
     raw['B1_B2_numeric_checks']=cross
     if role=='FORMAL':
      assert active,'Compiled Qwen2Model inactive'
      assert not newgraphs and all(after[k]==before[k] for k in stable),'Formal compile or graph capture'
      if count==32:assert graphs,'32-token fullgraph replay absent'
     save(path,raw)
  assert sum(s['role']=='FORMAL' for s in raw['samples'])==30
  raw['status']='NATIVE_BATCH_SENSITIVITY_COMPLETE'
 except BaseException as e:
  raw.update(status='NUMERIC_OR_RUNTIME_NO_GO',error=str(e),error_type=type(e).__name__,traceback=traceback.format_exc())
 finally:
  raw['context_seconds']=time.monotonic()-started;save(path,raw);save(P/'PROBE_private_outputs.json',secret)
 print(json.dumps(dict(status=raw['status'],samples=len(raw['samples']))),flush=True)
 return 0 if raw['status']=='NATIVE_BATCH_SENSITIVITY_COMPLETE' else 2
if __name__=='__main__':raise SystemExit(main())
