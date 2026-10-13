"""CPU-only re-read of completed tensor evidence; no model load/evaluation or CUDA context."""
import os,pathlib,json,hashlib
os.environ['CUDA_VISIBLE_DEVICES']=''
root=pathlib.Path(os.environ['TASK_DATA']);assert 'TASK_GPU_LOCK_START_MONOTONIC' in os.environ
import torch,numpy as np
torch.set_num_threads(8);assert not torch.cuda.is_initialized()
raw=root/'raw';out=raw/'trial_means';out.mkdir(exist_ok=True);records=[]
def collect(obj,prefix=''):
 result={}
 if isinstance(obj,torch.Tensor):
  assert obj.shape[0]==5 and torch.isfinite(obj).all();result[prefix]=(obj.double().mean(0).numpy(),str(obj.dtype));return result
 for key,value in obj.items():result.update(collect(value,prefix+('_' if prefix else '')+str(key)))
 return result
for file in sorted(raw.glob('*.pt')):
 obj=torch.load(file,map_location='cpu',weights_only=True);means=collect(obj);path=out/(file.stem+'.npz');np.savez_compressed(path,**{k:v[0] for k,v in means.items()});records.append({'source':file.name,'source_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'mean_file':str(path.relative_to(raw)),'mean_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'fields':{k:{'single_output_dtype':dtype,'mean_dtype':'float64','mean_shape':list(a.shape)} for k,(a,dtype) in means.items()}})
recomputed=[]
for proc in range(3):
 reference=torch.load(raw/f'formal_{proc}_reference_a.pt',map_location='cpu',weights_only=True)
 for label in ['reference_b','eager_oeq_single','eager_oeq_batch2','N-C2','N-G2','N-G4','N-G8','post_N-C2','post_N-G2','post_N-G4','post_N-G8']:
  candidate=torch.load(raw/f'formal_{proc}_{label}.pt',map_location='cpu',weights_only=True)
  for field in reference:
   a=reference[field].double().mean(0);b=candidate[field].double().mean(0);match=torch.isclose(a,b,atol=5e-5,rtol=5e-5);assert match.all();recomputed.append({'process':proc,'arm':label,'field':field,'max_abs_diff':(a-b).abs().max().item(),'failed_elements':int((~match).sum()),'pass':True})
assert len(recomputed)==132 and not torch.cuda.is_initialized()
r={'status':'PASS_CPU_RAW_RECOMPUTE_AND_EXPLICIT_TRIAL_MEANS','source_tensor_files':len(records),'records':records,'formal_field_checks_recomputed':132,'formal_recompute':recomputed,'mean_rule':'Original5 single outputs -> double -> mean along trial axis; exact pinned torch CPU implementation','CUDA_initialized':False,'model_evaluations':0,'new_gpu_observations':0};(raw/'TRIAL_MEANS_AND_RAW_RECOMPUTE.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['records','formal_recompute']}))
