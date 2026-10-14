"""Opt-in bounded execution of frozen author trainers; nominal schedule unchanged."""
import argparse,ast,copy,dataclasses,hashlib,importlib.util,json,math,os,pathlib,re,sys,time
from control import ROOT
p=argparse.ArgumentParser();p.add_argument('--arm',choices=['host_wall','gpu_wall','host_diag','host_late','host_late_verified'],required=True);p.add_argument('--last-step',type=int,default=205);a=p.parse_args()
assert os.environ.get('A26R_GPU_LOCK_HELD')=='1','GPU lock supervisor required before framework import'
import torch
assert torch.__version__=='2.2.0+cu121';torch.set_num_threads(1);torch.set_num_interop_threads(1)
torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(13/16,0)
assert 'RTX 4080' in torch.cuda.get_device_name(0)
base=ROOT/'software_sources/gsscale';sys.path[:0]=[str(base/'examples'),str(base/'cpu_adam'),str(base)]
path=base/'examples'/('simple_trainer.py' if a.arm=='gpu_wall' else 'simple_trainer_hybrid_optimized.py');src=path.read_text();tree=ast.parse(src)
spec=importlib.util.spec_from_file_location('a26r_author_'+a.arm,path);mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
preset=None
for node in ast.walk(tree):
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='configs' for t in node.targets) and isinstance(node.value,ast.Dict):
  for key,value in zip(node.value.keys,node.value.values):
   if isinstance(key,ast.Constant) and key.value=='rubble':preset=value.elts[1]
assert preset is not None
cfg=eval(compile(ast.Expression(preset),str(path),'eval'),mod.__dict__);cfg.data_dir=str(ROOT/'scene');cfg.result_dir=str(ROOT/'native'/a.arm);cfg.disable_viewer=True
assert cfg.max_steps==200000 and cfg.data_factor==4 and cfg.test_every==83 and cfg.test_after==-1
cfg.adjust_steps(cfg.steps_scaler);assert cfg.max_steps==200000
mod.cfg=cfg  # Preserve the original __main__ module-global used by author methods.
out=ROOT/'native'/a.arm;out.mkdir(parents=True,exist_ok=True)
conf=dataclasses.asdict(cfg);conf['data_dir']='isolated frozen Rubble scene';conf['result_dir']='isolated arm result directory'
(out/'config.json').write_text(json.dumps(conf,default=str,indent=2)+'\n')
current={'step':-1,'last_batch':None,'last_ids':None,'pred':None,'target':None,'loss':None,'regions':[],'gpu_events':[]};rows=[];quality=[];runner=None
OriginalLoader=torch.utils.data.DataLoader
class CaptureLoader(OriginalLoader):
 def __iter__(self):
  for batch in super().__iter__():
   current['last_batch']=batch;current['last_ids']=[int(v) for v in batch['image_id'].reshape(-1).tolist()];yield batch
torch.utils.data.DataLoader=CaptureLoader
orig_backward=torch.Tensor.backward

def backward(self,*args,**kwargs):
 if current['step']<=3 and self.numel()==1:current['loss']=float(self.detach().item())
 return orig_backward(self,*args,**kwargs)
torch.Tensor.backward=backward

# Timer statements surround original statements only in the opt-in diagnostic arm.
# CUDA-event spans retain their own time domain; they are not summed with CPU wall.
region_starts={}
def region_begin(tag):region_starts[(tag,current['step'])]=time.monotonic()
def region_end(tag):
 t=region_starts.pop((tag,current['step']),None)
 if t is not None:current['regions'].append({'tag':tag,'begin_host_monotonic':t,'end_host_monotonic':time.monotonic()})
source_gpu_work=mod.Runner.gpu_forward_backward
source_train_ast=copy.deepcopy(next(n for n in next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Runner').body if isinstance(n,ast.FunctionDef) and n.name=='train'))
def diag_enabled(step):
 return a.arm=='host_diag' or (a.arm in {'host_late','host_late_verified'} and any(lo<=step<lo+50 for lo in [100,14500,15100]))
if a.arm in {'host_diag','host_late','host_late_verified'}:
 mod.__dict__.update(_a26_begin=region_begin,_a26_end=region_end,_a26_diag_enabled=diag_enabled)
 class Instrument(ast.NodeTransformer):
  def visit_FunctionDef(self,node):
   if node.name not in {'train','gpu_forward_backward'}:return node
   node=self.generic_visit(node);return node
  def visit_Assign(self,node):return self.wrap(node)
  def visit_Expr(self,node):return self.wrap(node)
  def wrap(self,node):
   text=ast.get_source_segment(src,node) or '';tag=None
   if 'torch.cuda.synchronize()' in text:tag='synchronize'
   elif 'subthread.join()' in text:tag='join'
   elif 'cpu_optimizer_parallel(' in text:tag='cpu_adam'
   elif 'calculate_update_ids(' in text:tag='cpu_id_selection'
   elif 'adam_for_next_with_counter(' in text:tag='cpu_parameter_forwarding_adam'
   elif 'frustum_culling_gpu(' in text:tag='frustum_launch_host'
   elif '.pin_memory().to(' in text:tag='parameter_H2D_enqueue'
   elif '.to("cpu"' in text:
    tag='ID_D2H_host' if 'valid_ids_cpu' in text and 'info[' not in text else 'metadata_D2H_host'
   elif '.copy_(' in text:
    calls=[c for c in ast.walk(node) if isinstance(c,ast.Call) and isinstance(c.func,ast.Attribute) and c.func.attr=='copy_']
    def base_name(n):
     while isinstance(n,(ast.Subscript,ast.Attribute)):n=n.value
     return n.id if isinstance(n,ast.Name) else None
    bases={base_name(c.func.value) for c in calls}
    if bases & {'colorsN','colors0','opacities'}:tag='parameter_H2D_enqueue'
    elif bases & {'opacities_cpu_grad','colors0_cpu_grad','colorsN_cpu_grad'}:tag='gradient_D2H_host'
    else:tag='unclassified_copy_host'
   if tag is None:return node
   tag=tag+'@L'+str(node.lineno)
   before=ast.Expr(ast.Call(ast.Name('_a26_begin',ast.Load()),[ast.Constant(tag)],[]));after=ast.Expr(ast.Call(ast.Name('_a26_end',ast.Load()),[ast.Constant(tag)],[]))
   return [ast.copy_location(before,node),node,ast.copy_location(after,node)]
 target_class=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Runner')
 for fn in target_class.body:
  if isinstance(fn,ast.FunctionDef) and fn.name in {'train','gpu_forward_backward'}:
   transformed=Instrument().visit(fn)
   if a.arm in {'host_late','host_late_verified'} and fn.name=='train':
    original_loop=next(n for n in ast.walk(source_train_ast) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='step')
    modified_loop=next(n for n in ast.walk(transformed) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='step')
    branch=ast.If(test=ast.Call(ast.Name('_a26_diag_enabled',ast.Load()),[ast.Name('step',ast.Load())],[]),body=modified_loop.body,orelse=copy.deepcopy(original_loop.body));modified_loop.body=[ast.copy_location(branch,modified_loop)]
   ast.fix_missing_locations(transformed);module_ast=ast.Module(body=[transformed],type_ignores=[]);ns=mod.__dict__;exec(compile(module_ast,str(path)+'[opt-in-observer]','exec'),ns);setattr(mod.Runner,fn.name,ns[fn.name])

event_pairs=[]
if a.arm in {'host_diag','host_late','host_late_verified'}:
 original_gpu_work=mod.Runner.gpu_forward_backward
 def gpu_event_work(self,*args,**kwargs):
  step=args[0]
  if not diag_enabled(step):return source_gpu_work(self,*args,**kwargs)
  begin=torch.cuda.Event(enable_timing=True);end=torch.cuda.Event(enable_timing=True)
  h0=time.monotonic();begin.record()
  result=original_gpu_work(self,*args,**kwargs)
  end.record();h1=time.monotonic()
  event_pairs.append({'step':step,'begin':begin,'end':end,'host_worker_begin':h0,'host_worker_end':h1})
  return result
 mod.Runner.gpu_forward_backward=gpu_event_work
orig_tqdm=mod.tqdm.tqdm
class BoundedProgress:
 def __init__(self,iterable,*args,**kwargs):self.it=iterable;self.inner=orig_tqdm(iterable,*args,**kwargs)
 def __getattr__(self,n):return getattr(self.inner,n)
 def set_description(self,text,*args,**kwargs):
  match=re.search(r'loss=([^|]+)',text)
  if match:assert math.isfinite(float(match.group(1))),'NONFINITE_REAL_TRAIN_LOSS'
  return self.inner.set_description(text,*args,**kwargs)
 def __iter__(self):
  for step in self.it:
   if step>a.last_step:break
   current.update(step=step,loss=None,regions=[],gpu_events=[])
   entry_camera=current['last_ids'];t=time.monotonic();yield step;wall=time.monotonic()-t
   if step==0:continue
   camera=current['last_ids'] if a.arm=='gpu_wall' else entry_camera
   if step<=3:
    assert current['pred'] is not None and current['target'] is not None and current['loss'] is not None
    assert math.isfinite(current['loss'])
    with torch.no_grad():
     pred=current['pred'][...,:3].clamp(0,1).permute(0,3,1,2);gt=current['target'].to('cuda').float().permute(0,3,1,2)/255
     assert pred.shape==gt.shape==(1,3,864,1152) and torch.isfinite(pred).all()
     metrics={'psnr':float(runner.psnr(pred,gt)),'ssim':float(runner.ssim(pred,gt)),'lpips':float(runner.lpips(pred,gt))};assert all(math.isfinite(v) for v in metrics.values())
     assert all(v.dtype==torch.float32 and torch.isfinite(v).all() for v in runner.splats.values())
     opts=runner.optimizers if a.arm=='gpu_wall' else {**runner.optimizers_gpu,**runner.optimizers_cpu}
     moment_nonzero={}
     for name,opt in opts.items():
      vals=list(opt.state.values());moment_nonzero[name]=any('exp_avg' in v and bool(torch.count_nonzero(v['exp_avg']).item()) for v in vals)
     assert any(moment_nonzero.values()),moment_nonzero
     if a.arm!='gpu_wall':assert moment_nonzero['opacities'] or moment_nonzero['sh0'],moment_nonzero
     q={'step':step,'camera_ids':camera,'loss':current['loss'],'metrics':metrics,'gaussians':len(runner.splats['means']),'all_parameter_values_finite':True,'optimizer_moment_nonzero_by_group':moment_nonzero,'inactive_SH_degree_groups_not_required_to_update':True,'dtype':'float32','application_quality':'REAL_EARLY_FUNCTIONAL_AND_METRIC_API_ONLY','long_convergence_quality_matched':False};quality.append(q)
     (out/'functional_quality.json').write_text(json.dumps({'status':'REAL_EARLY_FUNCTIONAL_PASS' if len(quality)>=3 else 'PARTIAL','samples':quality,'bitwise_equivalence_claimed':False},indent=2)+'\n')
   if step==3:torch.Tensor.backward=orig_backward
   if step>3:assert len(quality)>=3,'FUNCTIONAL_GATE_NOT_PASSED'
   row={'step':step,'camera_ids':camera,'gaussians':len(runner.splats['means']),'whole_pipeline_cycle_wall_seconds':wall,'timing_kind':'opt_in_diagnostic' if diag_enabled(step) else 'outer_wall_original_train_body','allocated_bytes':torch.cuda.memory_allocated(),'reserved_bytes':torch.cuda.memory_reserved(),'regions':current['regions']}
   if step>=100:rows.append(row)
   if step%20==0 and step<=205 or step%200==0:print('REAL_TRAIN_STEP',a.arm,step,'wall',round(wall,4),'N',row['gaussians'],flush=True)
   with (out/'raw_steps.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
  self.inner.close()
mod.tqdm.tqdm=BoundedProgress
runner=mod.Runner(0,0,1,cfg)
initial={'gaussians':len(runner.splats['means']),'image_count':len(runner.parser.image_names),'train_count':len(runner.trainset),'test_count':len(runner.valset),'dtype_by_parameter':{k:str(v.dtype) for k,v in runner.splats.items()},'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'nominal_max_steps':cfg.max_steps,'effective_thread_policy':'OMP_THREAD_LIMIT=16; Torch/BLAS=1; author hardcoded 64 unchanged'}
(out/'initialized.json').write_text(json.dumps(initial,indent=2)+'\n');assert initial['gaussians']==1694315 and initial['image_count']==1678
name='rasterize_splats' if a.arm=='gpu_wall' else 'rasterize_splats_only';original_raster=getattr(runner,name)
def raster(*args,**kwargs):
 result=original_raster(*args,**kwargs)
 if current['step']<=3:
  current['pred']=result[0].detach();current['target']=current['last_batch']['image'].detach()
 return result
setattr(runner,name,raster)
started=time.monotonic();runner.train();torch.cuda.synchronize()
if a.arm in {'host_diag','host_late','host_late_verified'}:
 spans=[{'step':x['step'],'gpu_forward_backward_optimizer_span_ms':x['begin'].elapsed_time(x['end']),'host_worker_begin':x['host_worker_begin'],'host_worker_end':x['host_worker_end'],'time_domain':'CUDA event span includes GPU launch gaps; no direct sum or exact clock alignment with CPU durations'} for x in event_pairs]
 (out/'gpu_event_spans.json').write_text(json.dumps(spans,indent=2)+'\n')
(out/'completed.json').write_text(json.dumps({'status':'PASS','arm':a.arm,'reached_step':a.last_step,'real_phase':'LATE_CONTINUOUS_REACHED' if a.last_step>=15100 else 'EARLY_ONLY','nominal_schedule_max_steps':200000,'whole_run_wall_seconds':time.monotonic()-started,'late_state_not_evaluated':a.last_step<15100,'ordinary_splats_checkpoint_not_used_for_resume':True,'last_cpu_pipeline_gradient_may_remain_pending_at_external_stop':a.arm!='gpu_wall','window_samples':len(rows),'gpu_max_allocated':torch.cuda.max_memory_allocated(),'gpu_max_reserved':torch.cuda.max_memory_reserved()},indent=2)+'\n');print('REAL_EARLY_ARM_COMPLETE',a.arm,a.last_step,len(rows),flush=True)
