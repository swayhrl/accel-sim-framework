"""Read-only model dtype audit; no output evaluation, casting, or modification."""
import os,pathlib,json,hashlib,sys
root=pathlib.Path(os.environ['TASK_DATA']);assert 'TASK_GPU_LOCK_START_MONOTONIC' in os.environ
import torch
from nequip.model.saved_models.load_utils import load_saved_model
model=load_saved_model(str(root/'inputs/NequIP-OAM-S-0.1.nequip.zip'),compile_mode='eager').eval();modules=dict(model.named_modules());parameters=[]
for name,p in model.named_parameters():
 owner=name.rsplit('.',1)[0];m=modules[owner];parameters.append({'name':name,'owner_class':str(type(m)),'dtype':str(p.dtype),'shape':list(p.shape),'requires_grad':p.requires_grad,'sha256_native_bytes':hashlib.sha256(p.detach().cpu().contiguous().numpy().tobytes()).hexdigest(),'native_module_out_dtype':str(getattr(m,'out_dtype',None))})
non32=[p for p in parameters if p['dtype']!='torch.float32'];r={'status':'READ_ONLY_DIAGNOSTIC','model_metadata':model.metadata,'model_dtype':str(model.model_dtype),'non_FP32_parameters':non32,'parameters':parameters,'model_evaluations':0,'tensor_casts_or_model_modifications':0,'cuda_is_initialized_after_CPU_load':torch.cuda.is_initialized(),'native_model_package_sha256':hashlib.sha256((root/'inputs/NequIP-OAM-S-0.1.nequip.zip').read_bytes()).hexdigest()}
r['all_non32_are_native_per_type_scale_shift']=bool(non32) and all(p['dtype']=='torch.float64' and '.PerTypeScaleShift' in p['owner_class'] and p['name'].rsplit('.',1)[-1] in ['scales','shifts'] and p['native_module_out_dtype']=='torch.float64' for p in non32)
(root/'raw/NATIVE_DTYPE_AUDIT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='parameters'},indent=2));assert r['all_non32_are_native_per_type_scale_shift'] and model.model_dtype==torch.float32
