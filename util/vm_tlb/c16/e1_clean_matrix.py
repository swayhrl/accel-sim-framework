#!/usr/bin/env python3
import gc,hashlib,inspect,json,math,statistics,time
from pathlib import Path
import torch
from safetensors import safe_open
from transformers import Qwen2Config
from transformers.models.qwen2.modeling_qwen2 import Qwen2DecoderLayer
from awq import AutoAWQForCausalLM
RAW=Path('/data/c16/models/.incoming/qwen2p5_7b_instruct_raw/a09a35458c702b33eeacc393d103063234e8bc28');AWQ='/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641'
AUTH=Path('/data/c16/e1_clean_baseline_v1/capture_a');OUT=Path('/data/c16/e1_clean_baseline_v1/matrix')
def tsha(x):return hashlib.sha256(x.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()
def info(x):return {'dtype':str(x.dtype),'shape':list(x.shape),'stride':list(x.stride()),'sha256':tsha(x)}
def cast_audit(src,dst):
 back=dst.to(torch.bfloat16);neq=src.ne(back);den=src.float().abs();diff=(src.float()-back.float()).abs();sign=(torch.signbit(src)!=torch.signbit(back)) & src.ne(0) & back.ne(0)
 return {'source_bf16_sha256':tsha(src),'destination_fp16_sha256':tsha(dst),'element_count':src.numel(),'source_finite_count':int(torch.isfinite(src).sum()),'destination_finite_count':int(torch.isfinite(dst).sum()),'source_nonfinite_count':int((~torch.isfinite(src)).sum()),'destination_nonfinite_count':int((~torch.isfinite(dst)).sum()),'roundtrip_changed_count':int(neq.sum()),'roundtrip_changed_fraction':float(neq.float().mean()),'roundtrip_max_abs_diff':float(diff.max()),'roundtrip_max_relative_diff_nonzero_denominator':float((diff[den!=0]/den[den!=0]).max()) if bool((den!=0).any()) else 0.0,'zeros_introduced':int(dst.eq(0).logical_and(src.ne(0)).sum()),'sign_changes_excluding_zero':int(sign.sum()),'source_abs_min':float(src.float().abs().min()),'source_abs_max':float(src.float().abs().max()),'destination_abs_min':float(dst.float().abs().min()),'destination_abs_max':float(dst.float().abs().max())}
def stats(v):return {'samples_ms':v,'min_ms':min(v),'median_ms':statistics.median(v),'max_ms':max(v),'cv':statistics.pstdev(v)/statistics.mean(v)}
def timeit(fn):
 torch.cuda.synchronize();a=time.perf_counter_ns();y=fn();torch.cuda.synchronize();return y,(time.perf_counter_ns()-a)/1e6
def main():
 if OUT.exists():raise SystemExit('matrix exists')
 cfg=Qwen2Config.from_pretrained(RAW);idx=json.loads((RAW/'model.safetensors.index.json').read_text())['weight_map']
 def ten(k):
  with safe_open(RAW/idx[k],framework='pt',device='cpu') as s:return s.get_tensor(k)
 layer=Qwen2DecoderLayer(cfg,0).to(dtype=torch.bfloat16);layer.load_state_dict({n:ten('model.layers.0.'+n) for n in layer.state_dict()},strict=True)
 rawmods={'q_proj':layer.self_attn.q_proj.cuda().eval(),'down_proj':layer.mlp.down_proj.cuda().eval(),'up_proj':layer.mlp.up_proj.cuda().eval()}
 fpmods={};weight_audits={}
 for role,m in rawmods.items():
  z=torch.nn.Linear(m.in_features,m.out_features,bias=m.bias is not None,dtype=torch.float16);z.weight.data.copy_(m.weight.detach().cpu().to(torch.float16));
  if m.bias is not None:z.bias.data.copy_(m.bias.detach().cpu().to(torch.float16))
  fpmods[role]=z.cuda().eval()
  weight_audits[role]={'weight':cast_audit(m.weight.detach().cpu(),z.weight.detach().cpu()),'bias':cast_audit(m.bias.detach().cpu(),z.bias.detach().cpu()) if m.bias is not None else None}
 awq=AutoAWQForCausalLM.from_quantized(AWQ,fuse_layers=False);al=awq.model.model.layers[0];awqmods={'q_proj':al.self_attn.q_proj,'down_proj':al.mlp.down_proj,'up_proj':al.mlp.up_proj}
 points={}; fpchecks={}
 for role in rawmods:
  for M in (1,256):
   x=torch.load(AUTH/(f'{role}_M{M}_input.pt'),map_location='cpu',weights_only=True).cuda();xf=x.to(torch.float16);back=xf.to(torch.bfloat16)
   if not torch.isfinite(xf).all():raise RuntimeError('FP16 nonfinite '+role+str(M))
   fpchecks[f'{role}_M{M}']={'bf16':info(x),'fp16':info(xf),'cast_audit':cast_audit(x,xf),'same_fp16_for_raw_awq':True}
   points[(role,M)]={'bf16':x,'fp16':xf}
 rows=[];order=[('RAW_BF16',rawmods),('RAW_FP16',fpmods),('AWQ_FP16_INPUT',awqmods)]
 for warm in range(2):
  for role,M in [(r,m) for r in rawmods for m in (1,256)]:
   for impl,mods in order:mods[role](points[(role,M)]['bf16' if impl=='RAW_BF16' else 'fp16'])
 torch.cuda.synchronize()
 for rep in range(7):
  rotated=order[rep%3:]+order[:rep%3]
  for role in rawmods:
   for M in (1,256):
    for impl,mods in rotated:
     inp=points[(role,M)]['bf16' if impl=='RAW_BF16' else 'fp16'];out,ms=timeit(lambda m=mods[role],x=inp:m(x));key=(role,M,impl);rows.append((key,ms,info(inp),info(out),type(mods[role]).__name__))
 result=[]
 for role in rawmods:
  for M in (1,256):
   for impl,_ in order:
    rs=[x for (k,x,*_) in rows if k==(role,M,impl)];meta=next(z for z in rows if z[0]==(role,M,impl));result.append({'role':role,'M':M,'implementation':impl,**stats(rs),'input':meta[2],'output':meta[3],'module_class':meta[4],'path_fingerprint':'GEMM_QUANTIZED' if impl.startswith('AWQ') else 'TORCH_DENSE_LINEAR','output_sha256':meta[3]['sha256']})
 OUT.mkdir(parents=True);(OUT/'CORE_18_POINT_RESULT.json').write_text(json.dumps({'status':'PASS','fp16_activation_bridge':fpchecks,'fp16_weight_bias_cast_audit':weight_audits,'rows':result,'awq_gemm_source_sha256':hashlib.sha256(inspect.getsource(type(al.mlp.down_proj)).encode()).hexdigest()},indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':'PASS','points':len(result)}))
if __name__=='__main__':main()
