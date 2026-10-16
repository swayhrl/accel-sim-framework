"""A61 actual qualification then bounded natural training; no profiler/new mechanism."""
import os,sys,time,json,gc,traceback,pathlib
assert os.environ.get('A61_GPU_LOCK_HELD')=='1'
from native_utils import *
EAGER_ONLY='--eager-only' in sys.argv
stage('IMPORT_AND_IDENTITY');assert '4080' in torch.cuda.get_device_name(0);assert torch.cuda.get_device_capability(0)==(8,9)
save('device_and_software.json',{'torch':torch.__version__,'torch_cuda':torch.version.cuda,'DGL':dgl.__version__,'PyG':importlib.metadata.version('torch-geometric'),'device':torch.cuda.get_device_name(0),'capability':list(torch.cuda.get_device_capability()),'driver_API':'RECORDED_PARENT_NVML','TF32':False,'FP32':True,'allocator_fraction':.70,'backend':'PYG_SAGE','preregistration_sha256':sha(R/'preregistration.json')})
orders=create_splits_and_orders();stage('PIN_AUTHOR_FEATURE_GRAPH');t=time.monotonic();pinned=(torch.from_numpy(IP).pin_memory(),torch.from_numpy(IX).pin_memory(),torch.from_numpy(FEAT).pin_memory());sync();save('pinned_preparation.json',{'seconds':time.monotonic()-t,'feature_bytes':pinned[2].numel()*pinned[2].element_size(),'all_pinned':all(x.is_pinned() for x in pinned),'source_feature_SHA256':sha(R/'data/small/processed/paper/node_feat.npy')});assert all(x.is_pinned() for x in pinned)
canaries=[];full=True;compiled=None;compile_status={'status':'STRONG_COMPILED_PATH_UNQUALIFIED','reason':'bounded cold-compile recovery; all arms eager'} if EAGER_ONLY else {'status':'NOT_ATTEMPTED'}
for arm in ['FULL_RESIDENT_GPU','PINNED_CACHE_ON','PINNED_CACHE_OFF']:
 deadline();ctx=mb=model=opt=None
 if EAGER_ONLY and (R/('G1_'+arm+'.json')).exists():
  record=json.loads((R/('G1_'+arm+'.json')).read_text());canaries.append(record);full=full and record['status']=='PASS' if arm=='FULL_RESIDENT_GPU' else full;event('REUSE_PASSED_G1_AFTER_COMPILE_RECOVERY',arm=arm);continue
 stage('G1_CANARY',arm=arm)
 try:
  torch.cuda.empty_cache();torch.cuda.reset_peak_memory_stats();ctx=DataContext(arm,pinned);model,opt=model_optimizer(20261015);gb.seed(20261015);loader=ctx.loader(orders[20261015][:B]);it=iter(loader);mb=next(it);sync();sample=validate_mb(mb,'G1_'+arm);numeric=numeric_oracle(mb,model,opt,'G1_'+arm)
  # Complete the finite one-batch pipeline; do not leave prefetch work behind.
  try:next(it);raise AssertionError('G1_FINITE_LOADER_OVERFLOW')
  except StopIteration:pass
  record={'arm':arm,'status':'PASS','sample':sample,'numeric':numeric,'cache_stats':ctx.stats(),'max_Torch_allocated_bytes':torch.cuda.max_memory_allocated(),'max_Torch_reserved_bytes':torch.cuda.max_memory_reserved()}
  if arm=='FULL_RESIDENT_GPU':
   assert ctx.gpu_features.is_cuda and ctx.gpu_features.shape==(N,D) and ctx.graph.indices.is_cuda and ctx.graph.csc_indptr.is_cuda;record['full_graph_and_FP32_features_device_resident']=True;record['bulk_feature_GPU_bytes']=ctx.gpu_features.numel()*4
  if arm=='PINNED_CACHE_ON':
   assert ctx.cache is not None and ctx.cache.cache_size_in_bytes>0 and ctx.graph._gpu_graph_cache is not None,'STRONG_GRAPH_AND_FEATURE_CACHE_NOT_CREATED';q=mb.input_nodes[:128];a=ctx.cache.read(q);sync();first_rate=float(ctx.cache.miss_rate);b=ctx.cache.read(q);sync();second_rate=float(ctx.cache.miss_rate);expected=torch.from_numpy(np.array(FEAT[q.cpu().numpy()],copy=True));assert torch.equal(a.cpu(),expected) and torch.equal(b.cpu(),expected),'CACHE_HIT_OR_FALLBACK_VALUES_FAILED';record['functional_feature_hit_miss_replay']={'natural_request_IDs':128,'first_miss_rate_cumulative':first_rate,'second_miss_rate_cumulative':second_rate,'values_exact':True,'scope':'correctness-only repeat of actualnaturalIDs, excluded from training/cache timing; formal caches reinitialized'}
   replay_loader=ctx.loader(orders[20261015][:B]);gb.seed(20261015);replay_it=iter(replay_loader);replay_mb=next(replay_it);sync();record['graph_hit_replay_sample']=validate_mb(replay_mb,'G1_PINNED_CACHE_ON_GRAPH_REPLAY');record['graph_stats_after_replay']=ctx.stats();record['graph_hit_observed']=record['graph_stats_after_replay'].get('graph_cache_total_queries',0)>record['graph_stats_after_replay'].get('graph_cache_total_misses',0)
   try:next(replay_it);raise AssertionError('REPLAY_FINITE_LOADER_OVERFLOW')
   except StopIteration:pass
   del replay_it,replay_mb,replay_loader;gc.collect()
   save('G1_'+arm+'.json',record)
   # Same actual minibatch and same initialization: compiled update must match eager.
   if not EAGER_ONLY:
    model2,opt2=model_optimizer(20261015);stage('COMPILE_CANARY',arm=arm);ct=time.monotonic();reserve_updates(1,'compile_probe','G1_COMPILE_RESERVATION')
    try:
     torch._dynamo.config.cache_size_limit=32;compiled=torch.compile(train_step,dynamic=True);loss2=compiled(mb,opt2,model2);sync();assert torch.isfinite(loss2) and abs(float(loss2)-numeric['full_batch_loss'])<=1e-5+1e-4*abs(numeric['full_batch_loss']),'COMPILED_LOSS_NUMERIC_GATE'
     for (n,p),(n2,z) in zip(model.named_parameters(),model2.named_parameters()):assert n==n2 and torch.allclose(p.detach(),z.detach(),atol=1e-6,rtol=1e-4),'COMPILED_UPDATE_NUMERIC_GATE '+n
     compile_status={'status':'PASS_COMPILED_TRAIN_STEP_NUMERIC','cold_seconds':time.monotonic()-ct,'scope':'official train_step forward/crossentropy/backward/Adam; dynamic=True; actualgraph-break counts recorded'}
    except Exception as e:
     if isinstance(e,AssertionError) or any(s in str(e).lower() for s in ['illegal memory','device-side assert','out of memory']):raise
     compile_status={'status':'STRONG_COMPILED_PATH_UNQUALIFIED','cold_seconds':time.monotonic()-ct,'error':repr(e),'traceback':traceback.format_exc(),'policy':'all formal paths eager scope; no hardware-headroom claim'};compiled=None;event('COMPILE_ENGINEERING_FALLBACK_EAGER',error=repr(e));torch._dynamo.reset()
    finally:del model2,opt2
   else:compile_status={'status':'STRONG_COMPILED_PATH_UNQUALIFIED','reason':'bounded parent cold-compile timeout recovery; all arms eager'}
   save('compile_qualification.json',compile_status)
  save('G1_'+arm+'.json',record);canaries.append(record);save('G1_canaries.json',{'status':'IN_PROGRESS','arms':canaries,'full_resident_qualified':full})
 except torch.cuda.OutOfMemoryError as e:
  if arm!='FULL_RESIDENT_GPU':raise
  full=False;failed={'arm':arm,'status':'FULL_RESIDENT_NOT_QUALIFIED_CAPACITY','error':repr(e),'allocator_fraction':.70,'no_precision_or_graph_change':True};save('G1_'+arm+'.json',failed);canaries.append(failed);save('G1_canaries.json',{'status':'IN_PROGRESS','arms':canaries,'full_resident_qualified':False});event('FULL_RESIDENT_CAPACITY_NOT_QUALIFIED',error=repr(e))
 finally:
  ctx=mb=model=opt=loader=it=None;gc.collect();sync();torch.cuda.empty_cache()
assert any(x['arm']=='PINNED_CACHE_ON' and x['status']=='PASS' for x in canaries) and any(x['arm']=='PINNED_CACHE_OFF' and x['status']=='PASS' for x in canaries)
save('G1_canaries.json',{'status':'PASS','arms':canaries,'full_resident_qualified':full,'compile':compile_status});nformal=32 if full else 56;arms=['FULL_RESIDENT_GPU','PINNED_CACHE_ON','PINNED_CACHE_OFF'] if full else ['PINNED_CACHE_ON','PINNED_CACHE_OFF'];save('formal_admission.json',{'status':'FROZEN_BEFORE_TIMING','arms':arms,'formal_batches_each':nformal,'full_resident_qualified':full,'feature_cache_bytes':128*1024**2,'graph_cache_edges':1000000,'compile':compile_status,'timing_boundary':PRE['formal_wall'],'preregistration_sha256':sha(R/'preregistration.json')})
# No source/data hashing or this task's download work overlaps formal measurement.
step=compiled if compiled is not None else train_step;results=[]
for seed in SEEDS:
 schedule=arms if seed==20261015 or not full else ['PINNED_CACHE_ON','FULL_RESIDENT_GPU','PINNED_CACHE_OFF']
 for arm in schedule:
  deadline();label=f'{seed}_{arm}';stage('FORMAL_ARM_PREPARATION',seed=seed,arm=arm);ctx=DataContext(arm,pinned);model,opt=model_optimizer(seed);initial=state_hash(model);gb.seed(seed);warm_ids=orders[seed][:4*B];formal_ids=orders[seed][4*B:(4+nformal)*B];warm_loader=ctx.loader(warm_ids);reserve_updates(4,label,'NATURAL_WARMUP');t=time.monotonic()
  for mb in warm_loader:loss=step(mb,opt,model)
  sync();warm_seconds=time.monotonic()-t;del mb,warm_loader;gc.collect();sync();preformal=state_hash(model);model_state={n:p.detach().cpu().clone() for n,p in model.state_dict().items()};opt_state=opt.state_dict()
  # CPU copy of tiny optimizer state for a later controlled two-batch diagnostic.
  import copy
  opt_cpu=copy.deepcopy(opt_state)
  for v in opt_cpu['state'].values():
   for k,x in v.items():
    if isinstance(x,torch.Tensor):v[k]=x.detach().cpu().clone()
  loader=ctx.loader(formal_ids);sync();torch.cuda.reset_peak_memory_stats();reserve_updates(nformal,label,'FORMAL');stage('FORMAL_UNINSTRUMENTED',seed=seed,arm=arm,batches=nformal);dynamo_before=dict(torch._dynamo.utils.counters.get('stats',{}));losses=[];count=0;start=time.perf_counter()
  iterator=iter(loader)
  for mb in iterator:
   losses.append(step(mb,opt,model));count+=1
  sync();wall=time.perf_counter()-start
  # First preserve the complete wall receipt, before postprocessing or diagnostics.
  row={'seed':seed,'arm':arm,'completed_optimizer_updates':count,'formal_batches_expected':nformal,'B':B,'uninst_full_train_wall_seconds':wall,'mean_complete_batch_wall_seconds':wall/count,'training_seed_nodes_per_second':count*B/wall,'warmup_batches':4,'warmup_seconds':warm_seconds,'same_initial_model_sha256':initial,'preformal_model_sha256':preformal,'formal_seed_ID_sha256':digest_array(formal_ids),'compile_status':compile_status['status'],'formal_sync_policy':'no perstep sync or loss.item; one finalsync beforetimerstop','formal_iterator_prologue_included':True,'Torch_peak_allocated_bytes':torch.cuda.max_memory_allocated(),'Torch_peak_reserved_bytes':torch.cuda.max_memory_reserved(),'status':'WALL_PRESERVED'};save('wall_'+label+'.json',row);stage('FORMAL_WINDOW_FINISHED',seed=seed,arm=arm)
  assert count==nformal;values=torch.stack(losses).detach().cpu().numpy();assert np.isfinite(values).all(),'FORMAL_NONFINITE_LOSS';assert all(torch.isfinite(p).all() and p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters()),'FORMAL_NONFINITE_MODEL_GRADIENT';assert np.array_equal(mb.seeds.cpu().numpy(),formal_ids[-B:]);row.update(status='PASS',losses=values.tolist(),loss_mean=float(values.mean()),post_model_sha256=state_hash(model),cache_stats=ctx.stats(),dynamo_stats_before=dynamo_before,dynamo_stats_after=dict(torch._dynamo.utils.counters.get('stats',{})),CONVERGENCE_NOT_EVALUATED=True);save('wall_'+label+'.json',row);results.append(row);save('native_results.json',{'status':'IN_PROGRESS','arms':results});del losses,values,iterator,loader,mb,ctx,model,opt;gc.collect();sync();torch.cuda.empty_cache()
  # Separate diagnostic replay, same approved first2formal batches and preformal weights.
  stage('DIAGNOSTIC_CONTROLLED',seed=seed,arm=arm);ctx=DataContext(arm,pinned);model,opt=model_optimizer(seed);model.load_state_dict(model_state);opt.load_state_dict(opt_cpu);gb.seed(seed);diag_loader=ctx.loader(formal_ids[:2*B]);reserve_updates(2,label,'DIAGNOSTIC');diag=[];iterator=iter(diag_loader)
  for i in range(2):
   sync();t0=time.perf_counter();mb=next(iterator);host_next=time.perf_counter()-t0;sync();ready=time.perf_counter();loss=step(mb,opt,model);sync();end=time.perf_counter();assert torch.isfinite(loss);diag.append({'batch':i,'host_iterator_next_seconds':host_next,'controlled_data_ready_sync_wall_seconds':ready-t0,'controlled_train_completion_wall_seconds':end-ready,'loss':float(loss),'input_nodes':int(mb.input_nodes.numel()),'sampled_edges_each_layer':[int(s.sampled_csc.indices.numel()) for s in mb.sampled_subgraphs],'logical_feature_request_bytes':int(mb.node_features['feat'].numel()*4),'logical_request_not_DRAM_or_PCIe_bytes':True})
  save('diagnostic_'+label+'.json',{'status':'PASS','seed':seed,'arm':arm,'rows':diag,'cache_stats':ctx.stats(),'overlap_disturbed_by_sync':True,'stage_times_cannot_be_added_to_formal_wall':True,'sample_prefix':'same first2approved formal node batches; sampler RNG reset, distribution control not bitwise causality','preformal_weights_reloaded':True});del iterator,diag_loader,mb,ctx,model,opt,model_state,opt_state,opt_cpu;gc.collect();sync();torch.cuda.empty_cache()
save('native_results.json',{'status':'PASS_ALL_BOUNDED_ARMS','arms':results,'full_resident_qualified':full,'compile':compile_status,'no_hardware_mechanism':True,'CONVERGENCE_NOT_EVALUATED':True});stage('NATIVE_COMPLETE_STOP');print('A61_NATIVE_COMPLETE',len(results),flush=True)
