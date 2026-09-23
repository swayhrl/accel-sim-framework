#!/usr/bin/env python3
import hashlib,inspect,json,statistics,time
from pathlib import Path
import torch
from torch.profiler import profile,ProfilerActivity
from safetensors import safe_open
from transformers import Qwen2Config
from transformers.models.qwen2.modeling_qwen2 import Qwen2DecoderLayer
from awq import AutoAWQForCausalLM
RAW=Path('/data/c16/models/.incoming/qwen2p5_7b_instruct_raw/a09a35458c702b33eeacc393d103063234e8bc28');AWQ='/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641';AUTH=Path('/data/c16/e1_clean_baseline_v1/capture_a');OUT=Path('/data/c16/e1_clean_baseline_v1/transition')
def tsha(x):return hashlib.sha256(x.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()
def stat(v):return {'samples_ms':v,'min_ms':min(v),'median_ms':statistics.median(v),'max_ms':max(v),'cv':statistics.pstdev(v)/statistics.mean(v)}
def timed(fn):torch.cuda.synchronize();a=time.perf_counter_ns();y=fn();torch.cuda.synchronize();return y,(time.perf_counter_ns()-a)/1e6
def main():
 if OUT.exists():raise SystemExit('transition exists')
 cfg=Qwen2Config.from_pretrained(RAW);idx=json.loads((RAW/'model.safetensors.index.json').read_text())['weight_map']
 def ten(k):
  with safe_open(RAW/idx[k],framework='pt',device='cpu') as s:return s.get_tensor(k)
 layer=Qwen2DecoderLayer(cfg,0).to(dtype=torch.bfloat16);layer.load_state_dict({n:ten('model.layers.0.'+n) for n in layer.state_dict()},strict=True);m=layer.mlp.down_proj
 dense=torch.nn.Linear(m.in_features,m.out_features,bias=m.bias is not None,dtype=torch.float16);dense.weight.data.copy_(m.weight.to(torch.float16));dense=dense.cuda().eval()
 awq=AutoAWQForCausalLM.from_quantized(AWQ,fuse_layers=False);qm=awq.model.model.layers[0].mlp.down_proj
 full=torch.load(AUTH/'down_proj_M2048_input.pt',map_location='cpu',weights_only=True).to(torch.float16).cuda();rows=[]
 for M in (1023,1024):
  x=full[:,:M,:]
  for _ in range(2):dense(x);qm(x)
  raw=[];quant=[]
  for rep in range(7):
   order=[('RAW_FP16',dense),('AWQ_FP16_INPUT',qm)];order=order[rep%2:]+order[:rep%2]
   for name,mod in order:
    out,ms=timed(lambda mod=mod:mod(x));(raw if name=='RAW_FP16' else quant).append(ms)
  kernels={}
  for name,mod in [('RAW_FP16',dense),('AWQ_FP16_INPUT',qm)]:
   with profile(activities=[ProfilerActivity.CPU,ProfilerActivity.CUDA]) as p:mod(x);torch.cuda.synchronize()
   kernels[name]=sorted({e.key for e in p.key_averages() if e.device_time_total>0})
  rows += [{'M':M,'implementation':'RAW_FP16','input_sha256':tsha(x),'module_class':type(dense).__name__,'path':'TORCH_DENSE_LINEAR',**stat(raw),'kernel_names':kernels['RAW_FP16']},{'M':M,'implementation':'AWQ_FP16_INPUT','input_sha256':tsha(x),'module_class':type(qm).__name__,'path':'GEMM_QUANTIZED' if M>=1 and M<1024 else 'DEQUANTIZE_PLUS_TORCH_MATMUL','source_threshold_expression':'x.shape[0]*x.shape[1]>=1024','source_threshold_result':M>=1024,**stat(quant),'kernel_names':kernels['AWQ_FP16_INPUT']}]
 OUT.mkdir(parents=True);(OUT/'TRANSITION_RESULT.json').write_text(json.dumps({'status':'PASS','rows':rows,'same_canonical_M2048_source_sha256':tsha(full)},indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
