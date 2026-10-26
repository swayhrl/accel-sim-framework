"""Fresh G1 or G2 model context. Run only beneath the locked A79 supervisor."""
import pathlib,os,json,hashlib,time,sys,math,dataclasses,traceback
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/ai_workload_research/runs/AI_ARCH_A79_QWEN25_3B_NATIVE_WORKLOAD_SENSITIVITY_109_V1';P=OUT/'.private'
MODEL=pathlib.Path('/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct/aa8e72537993ba99e69dfaafa59ed015b17504d1')
def sha(x):return hashlib.sha256(x).hexdigest()
def save(path,obj):
 tmp=path.with_suffix('.writing');tmp.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n');tmp.replace(path)
def ids_hash(ids):return sha(json.dumps(ids,separators=(',',':')).encode())
def main():
 stage=sys.argv[1];assert stage in ['G1','G2'] and os.environ['A79_LOCK_OWNER'];started=time.monotonic();raw={'stage':stage,'status':'RUNNING','pid':os.getpid(),'started_wall':time.time(),'points':[]};path=OUT/'raw'/(stage+'.json');private_raw={'stage':stage,'points':[]};phase=['INIT'];graphs=[]
 try:
  import torch,vllm
  from vllm import LLM,SamplingParams
  from vllm.config.compilation import CompilationConfig,CompilationMode,CUDAGraphMode
  from vllm.compilation.counter import compilation_counter
  from vllm.compilation.decorators import TorchCompileWithNoGuardsWrapper
  from vllm.v1.worker.gpu.cudagraph_utils import ModelCudaGraphManager
  contract=json.loads((OUT/'FROZEN_SCIENCE_CONTRACT.json').read_text());inputs=json.loads((P/'inputs.json').read_text())
  runtime=json.loads((OUT/'SOURCE_AND_RUNTIME.json').read_text());site=pathlib.Path(vllm.__file__).parent
  hashes={k:sha((site/rel).read_bytes()) for k,rel in [('compilation.py','config/compilation.py'),('qwen2.py','model_executor/models/qwen2.py')]};assert hashes==runtime['vllm_installed_source_sha256']
  original=ModelCudaGraphManager.run_fullgraph
  def graph_counted(self,descriptor):
   value=original(self,descriptor)
   if phase[0] in ['WARMUP','FORMAL']:graphs.append(str(descriptor))
   return value
  ModelCudaGraphManager.run_fullgraph=graph_counted
  cap=544 if stage=='G1' else 2080;cache_root=pathlib.Path(os.environ['VLLM_CACHE_ROOT']).parent
  cc=CompilationConfig(mode=CompilationMode.VLLM_COMPILE,backend='inductor',cudagraph_mode=CUDAGraphMode.FULL_AND_PIECEWISE,cache_dir=str(cache_root/'compilation'))
  load_start=time.monotonic()
  llm=LLM(model=str(MODEL),tokenizer=str(MODEL),skip_tokenizer_init=True,dtype='bfloat16',quantization=None,model_impl='vllm',enforce_eager=False,tensor_parallel_size=1,max_model_len=cap,max_num_batched_tokens=cap,max_num_seqs=1,gpu_memory_utilization=0.92,cpu_offload_gb=0,enable_prefix_caching=False,seed=0,disable_log_stats=True,compilation_config=cc)
  runner=llm.llm_engine.model_executor.driver_worker.model_runner;config=runner.vllm_config;cc=config.compilation_config;model=runner.get_model();manager=runner.cudagraph_manager
  assert not config.model_config.enforce_eager and cc.mode==CompilationMode.VLLM_COMPILE and cc.backend=='inductor' and cc.cudagraph_mode==CUDAGraphMode.FULL_AND_PIECEWISE
  assert not bool(getattr(runner,'is_encoder_decoder',False));assert torch.cuda.get_device_capability(0)==(8,9)
  assert cc.local_cache_dir is None or pathlib.Path(cc.local_cache_dir).is_relative_to(cache_root)
  modules=list(model.named_modules());attention=sorted({type(m.impl).__name__ for _,m in modules if getattr(m,'impl',None) is not None and type(m.impl).__name__.endswith('AttentionImpl')});linear=sorted({type(m.quant_method).__name__ for _,m in modules if getattr(m,'quant_method',None) is not None and type(m.quant_method).__name__.endswith('LinearMethod')})
  assert attention==['FlashAttentionImpl'] and linear==['UnquantizedLinearMethod']
  raw['runtime']={'vllm':vllm.__version__,'torch':torch.__version__,'source_sha256':hashes,'attention':attention,'linear':linear,'max_model_len':cap,'max_num_batched_tokens':cap,'max_num_seqs':1,'compilation_mode':cc.mode.name,'backend':cc.backend,'cudagraph_mode':cc.cudagraph_mode.name,'cache_root':str(cache_root),'local_cache_dir':str(cc.local_cache_dir),'cache_identity':'NEW_MODE_A_COMPILATION_IDENTITY','initialization_compile_capture_wall_seconds':time.monotonic()-load_start,'semantic_module_hooks':False,'graph_dispatch_observation':'Accepted original manager-level run_fullgraph call counter only; no semantic hooks or profiler'}
  save(path,raw)
  points=contract['G1_points'] if stage=='G1' else contract['G2_points'];stable=('num_backend_compilations','num_cudagraph_captured','num_inductor_compiles','num_eager_compiles','num_cache_entries_updated','num_compiled_artifacts_saved','num_aot_compiles','num_aot_artifacts_saved')
  def compiled():return [{'name':n,'class':type(m).__name__,'do_not_compile':bool(getattr(m,'do_not_compile',True)),'compiled':bool(getattr(m,'compiled',False)),'aot_compiled_fn':getattr(m,'aot_compiled_fn',None) is not None} for n,m in model.named_modules() if isinstance(m,TorchCompileWithNoGuardsWrapper)]
  for point in points:
   key=point['source']+'_'+str(point['prompt_tokens']);prompt=inputs[key];output_n=point['output_tokens'];assert len(prompt)==point['prompt_tokens'];public={**point,'status':'RUNNING','warmups':[],'formal_samples':[]};secret={**point,'samples':[]};raw['points'].append(public);private_raw['points'].append(secret)
   sampling=SamplingParams(temperature=0.0,top_p=1.0,max_tokens=output_n,ignore_eos=True,detokenize=False,logprobs=20)
   reference=json.loads((P/'reference.json').read_text())['formal_rows'][0] if stage=='G1' and (P/'reference.json').exists() else None
   repeat_ids=None;repeat_probs=None
   for role,count in [('WARMUP',2),('FORMAL',5)]:
    for index in range(count):
     phase[0]=role;graphs.clear();before=dataclasses.asdict(compilation_counter.clone());gbefore={str(k) for k in manager.graphs}
     torch.cuda.synchronize();start=torch.cuda.Event(enable_timing=True);stop=torch.cuda.Event(enable_timing=True);start.record();host_start=time.perf_counter_ns()
     responses=llm.generate([{'prompt_token_ids':prompt}],sampling,use_tqdm=False)
     stop.record();torch.cuda.synchronize();host_end=time.perf_counter_ns();elapsed=float(start.elapsed_time(stop))
     assert math.isfinite(elapsed) and elapsed>0 and len(responses)==1 and len(responses[0].outputs)==1
     assert list(responses[0].prompt_token_ids)==prompt
     completion=responses[0].outputs[0];ids=[int(x) for x in completion.token_ids]
     # Persist the response before applying any scientific numeric gate.
     captured_probs=[{str(k):(float(v.logprob) if math.isfinite(float(v.logprob)) else str(float(v.logprob))) for k,v in step.items()} for step in completion.logprobs] if completion.logprobs is not None else None
     private_raw['last_received_response']={'point':point['point'],'role':role,'index':index,'token_ids':ids,'returned_logprobs':captured_probs}
     raw['last_received_response']={'point':point['point'],'role':role,'index':index,'request_gpu_elapsed_ms':elapsed,'host_generate_wall_ms':(host_end-host_start)/1e6,'output_token_count':len(ids),'output_token_ids_sha256':ids_hash(ids),'returned_logprobs_sha256':sha(json.dumps(captured_probs,sort_keys=True,separators=(',',':')).encode())}
     save(P/(stage+'_private_output.json'),private_raw);save(path,raw)
     assert len(ids)==output_n and completion.logprobs is not None and len(completion.logprobs)==output_n
     probs=[];allprobs=[]
     for step,token in enumerate(ids):
      assert token in completion.logprobs[step];values={str(k):float(v.logprob) for k,v in completion.logprobs[step].items()};assert all(math.isfinite(v) for v in values.values());allprobs.append(values);probs.append(float(completion.logprobs[step][token].logprob))
     if repeat_ids is None:repeat_ids=ids;repeat_probs=probs
     assert ids==repeat_ids,'Scoped token repeatability failed'
     assert all(abs(a-b)<=0.05+0.01*abs(b) for a,b in zip(probs,repeat_probs)),'Scoped sampled-logprob repeatability failed'
     historical='HISTORICAL_OUTPUT_NOT_REVERIFIED';maxdelta=None
     if reference is not None:
      assert ids==reference['tokens'],'Historical output token mismatch';maxdelta=max(abs(a-b) for a,b in zip(probs,reference['sampled_logprobs']));assert all(abs(a-b)<=0.05+0.01*abs(b) for a,b in zip(probs,reference['sampled_logprobs'])),'Historical logprob mismatch';historical='PASS_EXACT32_AND_FROZEN_LOGPROB_TOLERANCE'
     after=dataclasses.asdict(compilation_counter.clone());newgraphs={str(k) for k in manager.graphs}-gbefore;receipt=compiled();active=[r for r in receipt if r['class']=='Qwen2Model' and not r['do_not_compile'] and (r['compiled'] or r['aot_compiled_fn'])]
     sample={'role':role,'index':index,'request_gpu_elapsed_ms':elapsed,'host_generate_wall_ms':(host_end-host_start)/1e6,'prompt_token_count':len(prompt),'output_token_count':len(ids),'output_token_ids_sha256':ids_hash(ids),'sampled_logprobs_sha256':sha(json.dumps(probs,separators=(',',':')).encode()),'all_returned_logprobs_sha256':sha(json.dumps(allprobs,sort_keys=True,separators=(',',':')).encode()),'all_logprobs_finite':True,'scoped_self_repeatability':True,'historical_reference':historical,'historical_max_sampled_logprob_abs_delta':maxdelta,'graph_replay_count':len(graphs),'graph_replay_descriptors':sorted(set(graphs)),'new_graph_descriptors':sorted(newgraphs),'counters_before':before,'counters_after':after,'active_compiled_Qwen2Model':active}
     public['warmups' if role=='WARMUP' else 'formal_samples'].append(sample);secret['samples'].append({'role':role,'index':index,'token_ids':ids,'sampled_logprobs':probs,'all_returned_logprobs':allprobs})
     save(path,raw);save(P/(stage+'_private_output.json'),private_raw)
     if role=='FORMAL':
      assert active,'Strong compiled model inactive';assert not newgraphs and all(after[k]==before[k] for k in stable),'Formal compile/capture occurred'
      if output_n==32:assert len(graphs)>0,'Expected Mode A graph replay absent'
   public['status']='PASS';public['numeric_scope']='FROZEN_HISTORICAL_REFERENCE' if stage=='G1' else 'SCOPED_SELF_REPEATABILITY';save(path,raw)
  raw['status']='PASS'
 except BaseException as error:
  raw.update({'status':'STOP','error_type':type(error).__name__,'error':str(error),'traceback':traceback.format_exc()})
 finally:
  raw['context_total_seconds']=time.monotonic()-started;save(path,raw)
 print(json.dumps({'stage':stage,'status':raw['status'],'completed_points':sum(p['status']=='PASS' for p in raw['points'])}),flush=True)
 return 0 if raw['status']=='PASS' else 2
if __name__=='__main__':raise SystemExit(main())
