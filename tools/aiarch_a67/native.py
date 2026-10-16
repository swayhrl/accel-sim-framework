"""A67 eager-only: one OFF canary, 6 windows of 2 warmup + 12 natural updates."""
import os
assert os.environ.get('A67_GPU_LOCK_HELD')=='1'
import gc,json,time,traceback,importlib.metadata
import numpy as np
from paths import OLD,R,W,save,event
from math_copy import (torch,dgl,gb,GraphSAGE,DataContext,train_step,validate_mb,
                       numeric_oracle,model_optimizer,state_hash,reserve_updates,
                       FEAT,LABEL,IP,IX,B,N,D,sync,deadline,digest_array)
PROGRESS={'stage':'NOT_STARTED','issued_updates':0,'confirmed_updates':0,'formal_issued':0}

def stage(name,**kw):
 deadline();PROGRESS.update(stage=name,**kw)
 save('current_phase.json',{'phase':name,'monotonic':time.monotonic(),**kw});event(name,**kw)

def boundary_snapshot():
 phase=json.loads((R/'current_phase.json').read_text())
 until=time.monotonic()+10
 while True:
  deadline()
  p=R/'supervisor_boundary_ack.json'
  if p.exists() and json.loads(p.read_text()).get('phase_monotonic')==phase['monotonic']:return
  assert time.monotonic()<until,'SUPERVISOR_BOUNDARY_EVIDENCE_MISSING'
  time.sleep(.02)

def parameters(model):return {n:p.detach().cpu().numpy().copy() for n,p in model.named_parameters()}

def finite(model,opt,steps):
 assert all(p.dtype==torch.float32 and torch.isfinite(p).all() and p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters()),'NONFINITE_OR_MISSING_MODEL_GRAD'
 assert all(int(opt.state[p]['step'].item())==steps for p in model.parameters()),'ADAM_STEP_COUNTER'
 return {'status':'PASS','all_parameter_and_gradient_finite':True,'actual_Adam_step_each_parameter':steps}

def residency(ctx,arm):
 if arm=='FULL_RESIDENT_GPU':
  assert ctx.gpu_features.is_cuda and tuple(ctx.gpu_features.shape)==(N,D) and ctx.gpu_features.dtype==torch.float32
  assert ctx.graph.indices.is_cuda and ctx.graph.csc_indptr.is_cuda
  assert ctx.graph.indices.numel()==13070502
  return {'full_resident':True,'FP32_feature_GPU_bytes':ctx.gpu_features.numel()*4,'CSC_edges_on_GPU':ctx.graph.indices.numel()}
 if arm=='PINNED_CACHE_ON':
  assert ctx.cache is not None and ctx.cache.cache_size_in_bytes==128*1024**2 and ctx.graph._gpu_graph_cache is not None
 else:assert ctx.cache is None and ctx.graph._gpu_graph_cache is None
 assert ctx.graph.indices.is_pinned() and ctx.graph.csc_indptr.is_pinned()
 return {'full_resident':False,'feature_cache_enabled':ctx.cache is not None,'graph_cache_enabled':ctx.graph._gpu_graph_cache is not None}

def cleanup():
 gc.collect();sync();torch.cuda.empty_cache()

def main():
 stage('IMPORT_DEVICE_AND_FROZEN_SOFTWARE')
 save('child_identity_start.json',{'PID':os.getpid(),'PGID':os.getpgrp(),'SID':os.getsid(0),'epoch':time.time()})
 versions={n:importlib.metadata.version(n) for n in ['torch','dgl','torch-geometric','numpy','triton']}
 assert versions=={'torch':'2.2.0+cu121','dgl':'2.4.0+cu121','torch-geometric':'2.6.1','numpy':'1.26.4','triton':'2.2.0'}
 assert '4080' in torch.cuda.get_device_name(0) and torch.cuda.get_device_capability(0)==(8,9)
 torch.set_num_threads(4);torch.set_num_interop_threads(1);torch.set_float32_matmul_precision('highest')
 torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.cuda.set_per_process_memory_fraction(.70,0)
 assert torch.get_default_dtype()==torch.float32
 save('device_and_software.json',{'versions':versions,'Torch_CUDA':torch.version.cuda,'device':torch.cuda.get_device_name(0),'capability':list(torch.cuda.get_device_capability(0)),'scope':'EAGER_ONLY','FP32':True,'TF32':False,'allocator_fraction':.70,'CPU_affinity':sorted(os.sched_getaffinity(0)),'Torch_threads':4,'DataLoader_workers':0,'A61_A65_STOP_preserved':True})
 orders={s:np.load(OLD/f'order_{s}.npy',mmap_mode='r') for s in [20261015,20261016]}
 stage('PIN_ONCE_ORIGINAL_AUTHOR_TABLE_AND_CSC');t=time.monotonic()
 pinned=(torch.from_numpy(IP).pin_memory(),torch.from_numpy(IX).pin_memory(),torch.from_numpy(FEAT).pin_memory());sync()
 assert all(p.is_pinned() for p in pinned)
 save('pinned_preparation.json',{'seconds':time.monotonic()-t,'FP32_feature_bytes':pinned[2].numel()*4,'CSC_bytes':sum(p.numel()*p.element_size() for p in pinned[:2]),'excluded_from_formal_wall':True})
 # Sole new qualification update. The exact original FP64 small-oracle routine is reused.
 stage('G1_OFF_CANARY');ctx=DataContext('PINNED_CACHE_OFF',pinned);model,opt=model_optimizer(20261015)
 np.savez_compressed(R/'raw/G1_OFF_initial.npz',**parameters(model))
 loader=ctx.loader(orders[20261015][:B]);iterator=iter(loader);mb=next(iterator);sync()
 sample=validate_mb(mb,'A67_G1_OFF');save('G1_OFF_sample.json',sample)
 PROGRESS['issued_updates']+=1
 numeric=numeric_oracle(mb,model,opt,'A67_G1_OFF');PROGRESS['confirmed_updates']+=1
 np.savez_compressed(R/'raw/G1_OFF_updated.npz',**parameters(model))
 np.savez_compressed(R/'raw/G1_OFF_gradient.npz',**{n:p.grad.detach().cpu().numpy().copy() for n,p in model.named_parameters()})
 numeric['state_finite']=finite(model,opt,1);numeric['residency']=residency(ctx,'PINNED_CACHE_OFF')
 try:next(iterator);raise AssertionError('OFF_CANARY_EXTRA_BATCH')
 except StopIteration:pass
 save('G1_OFF_numeric.json',numeric)
 del mb,iterator,loader,ctx,model,opt;cleanup()
 schedule=json.loads((R/'preregistration.json').read_text())['schedule'];results=[];initial_by_seed={}
 for position,(arm,seed) in enumerate(schedule):
  label=f'{seed}_{arm}';stage('PREPARE_WINDOW',arm=arm,seed=seed,position=position)
  torch.cuda.reset_peak_memory_stats();t=time.monotonic();ctx=DataContext(arm,pinned);sync();prep_seconds=time.monotonic()-t
  model,opt=model_optimizer(seed);initial=state_hash(model)
  if seed in initial_by_seed:assert initial==initial_by_seed[seed],'INITIAL_MODEL_CHANGED_BETWEEN_ARMS'
  else:initial_by_seed[seed]=initial
  assert all(p.dtype==torch.float32 for p in model.parameters())
  warm_ids=np.asarray(orders[seed][:2*B]);formal_ids=np.asarray(orders[seed][2*B:14*B]);assert len(formal_ids)==12*B
  gb.seed(seed);loader=ctx.loader(warm_ids);warm=[];reserve_updates(2,label,'WARMUP')
  stage('WARMUP',arm=arm,seed=seed,position=position);t=time.monotonic()
  for i,mb in enumerate(loader):
   PROGRESS['issued_updates']+=1;loss=train_step(mb,opt,model);sync();PROGRESS['confirmed_updates']+=1
   assert torch.isfinite(loss),'WARMUP_NONFINITE_LOSS'
   assert np.array_equal(mb.seeds.cpu().numpy(),warm_ids[i*B:(i+1)*B])
   audit=validate_mb(mb,f'A67_WARM_{label}_{i}');assert i<2
   warm.append({'batch':i,'loss':float(loss),'sample':audit,'cache':ctx.stats(),'residency':residency(ctx,arm),'finite':finite(model,opt,i+1)})
  sync();warm_seconds=time.monotonic()-t;assert len(warm)==2
  save('warmup_'+label+'.json',{'status':'PASS','rows':warm,'preparation_seconds':prep_seconds,'warmup_seconds_including_qualification_audits':warm_seconds,'initial_model_sha256':initial,'Torch_peak_allocated_bytes':torch.cuda.max_memory_allocated(),'Torch_peak_reserved_bytes':torch.cuda.max_memory_reserved()})
  if arm=='FULL_RESIDENT_GPU':save('G1_FULL_residency_'+str(seed)+'.json',{'status':'PASS_ACTUAL_WARMUP_CAPACITY','residency':residency(ctx,arm),'warmup_updates_in_main_budget':2,'Torch_peak_reserved_bytes':torch.cuda.max_memory_reserved()})
  if arm=='PINNED_CACHE_ON':save('G1_ON_'+str(seed)+'.json',{'status':'PASS_NEW_INPUT_FINITE_CACHE_AND_ACCEPTED_HISTORICAL_ORACLE','warmup_qualification_rows':warm,'historical_oracle':'A61 accepted, no new extra qualification updates'})
  del mb,loader;gc.collect();sync()
  before_cache=ctx.stats();preformal=state_hash(model);loader=ctx.loader(formal_ids);sync();torch.cuda.reset_peak_memory_stats()
  reserve_updates(12,label,'FORMAL');stage('FORMAL_UNINSTRUMENTED',arm=arm,seed=seed,position=position)
  boundary_snapshot()
  # Do not put synchronization, scalar readback, logging, hashing or numerical audits here.
  losses=[];meta=[];seed_tensors=[];count=0;t0=time.perf_counter()
  iterator=iter(loader)
  for mb in iterator:
   PROGRESS['issued_updates']+=1;PROGRESS['formal_issued']+=1
   loss=train_step(mb,opt,model);losses.append(loss);count+=1
   seed_tensors.append(mb.seeds)
   meta.append({'batch':count-1,'input_nodes':int(mb.input_nodes.numel()),'feature_rows':int(mb.node_features['feat'].shape[0]),'logical_feature_request_bytes':int(mb.node_features['feat'].numel()*4),'sampled_edges_each_layer':[int(s.sampled_csc.indices.numel()) for s in mb.sampled_subgraphs]})
  sync();wall=time.perf_counter()-t0
  PROGRESS['confirmed_updates']+=count
  row={'status':'WALL_PRESERVED_PENDING_POSTCHECKS','seed':seed,'arm':arm,'position':position,'completed_updates':count,'expected_updates':12,'full_train_step_wall_seconds':wall,'mean_complete_batch_wall_seconds':wall/count if count else None,'natural_seed_nodes_per_second':count*B/wall,'wall_boundary':'before iterator creation through final GPU synchronization, includes iterator exhaustion','no_perstep_sync_loss_item_profiler':True,'initial_model_sha256':initial,'preformal_model_sha256':preformal,'formal_node_order_expected_sha256':digest_array(formal_ids),'preparation_seconds':prep_seconds,'warmup_seconds_including_qualification_audits':warm_seconds,'preparation_excluded_not_free':True,'cache_before':before_cache,'Torch_peak_allocated_bytes':torch.cuda.max_memory_allocated(),'Torch_peak_reserved_bytes':torch.cuda.max_memory_reserved()}
  save('wall_'+label+'.json',row);stage('FORMAL_WALL_SAVED',arm=arm,seed=seed,position=position)
  boundary_snapshot()
  assert count==12,'FORMAL_COUNT'
  values=torch.stack(losses).detach().cpu().numpy();actual_ids=torch.cat(seed_tensors).cpu().numpy()
  assert np.array_equal(actual_ids,formal_ids),'ACTUAL_FORMAL_NODE_ORDER'
  assert np.isfinite(values).all(),'FORMAL_NONFINITE_LOSSES'
  state=finite(model,opt,14);last_sample=validate_mb(mb,'A67_FINAL_'+label)
  assert np.array_equal(mb.labels.cpu().numpy(),LABEL[actual_ids[-B:]].astype(np.int64))
  row.update(status='PASS',losses=values.tolist(),sample_counts=meta,formal_node_order_actual_sha256=digest_array(actual_ids),post_model_sha256=state_hash(model),finite=state,last_sample_audit=last_sample,cache_after=ctx.stats(),residency=residency(ctx,arm),CONVERGENCE_NOT_EVALUATED=True,NEIGHBORHOODS_NOT_BITWISE_PAIRED=True)
  save('wall_'+label+'.json',row);results.append(row);save('native_results.json',{'status':'IN_PROGRESS','windows':results,'formal_updates':sum(x['completed_updates'] for x in results),'scope':'EAGER_ONLY'})
  del mb,iterator,loader,ctx,model,opt,loss,losses,seed_tensors,values,actual_ids,warm,meta;cleanup()
 assert len(results)==6 and sum(x['completed_updates'] for x in results)==72
 assert PROGRESS['issued_updates']==85 and PROGRESS['confirmed_updates']==85
 save('native_results.json',{'status':'PASS_ALL_6_EAGER_WINDOWS','windows':results,'formal_updates':72,'warmup_updates':12,'qualification_updates':1,'total_updates':85,'scope':'EAGER_ONLY','no_compiled_path_qualification':True,'CONVERGENCE_NOT_EVALUATED':True})
 save('child_identity_end.json',{'PID':os.getpid(),'PGID':os.getpgrp(),'SID':os.getsid(0),'epoch':time.time(),'status':'85_UPDATES_COMPLETE'})
 stage('COMPLETE_ALL_OBSERVATIONS_STOP')

if __name__=='__main__':
 try:main()
 except BaseException as e:
  save('native_failure.json',{'error':repr(e),'traceback':traceback.format_exc(),'progress':PROGRESS,'no_extra_training_retry':True});raise
