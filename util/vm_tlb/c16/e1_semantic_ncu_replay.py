#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
import torch
from safetensors import safe_open
from transformers import Qwen2Config
from transformers.models.qwen2.modeling_qwen2 import Qwen2DecoderLayer
from awq import AutoAWQForCausalLM
RAW=Path('/data/c16/models/.incoming/qwen2p5_7b_instruct_raw/a09a35458c702b33eeacc393d103063234e8bc28');AWQ='/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641';AUTH=Path('/data/c16/e1_clean_baseline_v1/capture_a')
EXPECTED={(1,'RAW_FP16'):'50d389317ff126f2aa1e18dbf36bbf17bd66ddac2753552fc73517c1b7c3d394',(1,'AWQ'):'5618125fc9563f42860d5df37ae9b4b6569dfc4af1d995eeb7922d9f60b31d99',(256,'RAW_FP16'):'01dbbf90e7d43b86ba49ce61805f11717b7ec9f28e67d7da0ff5f73065757413',(256,'AWQ'):'59b56af85d0480542fa396a655f23179f879eccaa9ab32a7b98ba88e8cb33d50'}
def tsha(x):return hashlib.sha256(x.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--M',type=int,choices=(1,256),required=True);p.add_argument('--impl',choices=('RAW_FP16','AWQ'),required=True);a=p.parse_args();x=torch.load(AUTH/f'up_proj_M{a.M}_input.pt',map_location='cpu',weights_only=True).to(torch.float16).cuda()
 if a.impl=='RAW_FP16':
  cfg=Qwen2Config.from_pretrained(RAW);idx=json.loads((RAW/'model.safetensors.index.json').read_text())['weight_map'];l=Qwen2DecoderLayer(cfg,0).to(dtype=torch.bfloat16)
  def ten(k):
   with safe_open(RAW/idx[k],framework='pt',device='cpu') as s:return s.get_tensor(k)
  l.load_state_dict({n:ten('model.layers.0.'+n) for n in l.state_dict()},strict=True);src=l.mlp.up_proj;mod=torch.nn.Linear(src.in_features,src.out_features,bias=src.bias is not None,dtype=torch.float16);mod.weight.data.copy_(src.weight.to(torch.float16));mod=mod.cuda().eval()
 else:mod=AutoAWQForCausalLM.from_quantized(AWQ,fuse_layers=False).model.model.layers[0].mlp.up_proj
 with torch.inference_mode():
  for _ in range(2):mod(x)
  torch.cuda.synchronize();name=f'C16_E1_NCU_UP_M{a.M}_{a.impl}';torch.cuda.nvtx.range_push(name);out=mod(x);torch.cuda.synchronize();torch.cuda.nvtx.range_pop()
 got=tsha(out)
 if got!=EXPECTED[(a.M,a.impl)]:raise SystemExit('output SHA '+got)
 print(json.dumps({'status':'PASS','M':a.M,'impl':a.impl,'range':name,'input_sha256':tsha(x),'output_sha256':got,'module_class':type(mod).__name__}))
if __name__=='__main__':main()
