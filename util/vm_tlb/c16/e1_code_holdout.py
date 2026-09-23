#!/usr/bin/env python3
import hashlib,json,statistics,time
from pathlib import Path
import torch
from safetensors import safe_open
from transformers import Qwen2Config
from transformers.models.qwen2.modeling_qwen2 import Qwen2DecoderLayer,Qwen2RotaryEmbedding
from transformers.cache_utils import DynamicCache
from awq import AutoAWQForCausalLM
RAW=Path('/data/c16/models/.incoming/qwen2p5_7b_instruct_raw/a09a35458c702b33eeacc393d103063234e8bc28');AWQ='/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641';TOK=Path('/data/c16/inputs/.incoming/qwen2p5_7b_instruct_raw/S2_CODE/payload/token_ids.json');TOKEN_SHA='7acdc48f59cf204c192c5663d62abfb72fb8d754e6b0e92bd28d991b64fdafb8';OUT=Path('/data/c16/e1_clean_baseline_v1/code_holdout')
def fsha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tsha(x):return hashlib.sha256(x.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()
def timed(fn):torch.cuda.synchronize();a=time.perf_counter_ns();y=fn();torch.cuda.synchronize();return y,(time.perf_counter_ns()-a)/1e6
def stats(v):return {'samples_ms':v,'min_ms':min(v),'median_ms':statistics.median(v),'max_ms':max(v),'cv':statistics.pstdev(v)/statistics.mean(v)}
def main():
 if OUT.exists():raise SystemExit('output exists')
 if fsha(TOK)!=TOKEN_SHA:raise SystemExit('CODE token SHA')
 cfg=Qwen2Config.from_pretrained(RAW);idx=json.loads((RAW/'model.safetensors.index.json').read_text())['weight_map']
 def ten(k):
  with safe_open(RAW/idx[k],framework='pt',device='cpu') as s:return s.get_tensor(k)
 layer=Qwen2DecoderLayer(cfg,0).to(dtype=torch.bfloat16);layer.load_state_dict({n:ten('model.layers.0.'+n) for n in layer.state_dict()},strict=True);layer=layer.cuda().eval();cap={}
 hook=layer.mlp.down_proj.register_forward_pre_hook(lambda m,a:cap.update({'x':a[0].detach().clone()}))
 ids=json.loads(TOK.read_text());emb=torch.nn.Embedding(cfg.vocab_size,cfg.hidden_size,dtype=torch.bfloat16);emb.weight.data.copy_(ten('model.embed_tokens.weight'));emb=emb.cuda();h=emb(torch.tensor([ids],device='cuda'));pos=torch.arange(len(ids),device='cuda').unsqueeze(0);pe=Qwen2RotaryEmbedding(config=cfg).cuda()(h,pos)
 with torch.inference_mode():layer(h,position_ids=pos,past_key_value=DynamicCache(),use_cache=True,cache_position=torch.arange(len(ids),device='cuda'),position_embeddings=pe)
 hook.remove();src=cap['x'];raw=layer.mlp.down_proj
 dense=torch.nn.Linear(raw.in_features,raw.out_features,bias=False,dtype=torch.float16);dense.weight.data.copy_(raw.weight.detach().cpu().to(torch.float16));dense=dense.cuda().eval();awq=AutoAWQForCausalLM.from_quantized(AWQ,fuse_layers=False);quant=awq.model.model.layers[0].mlp.down_proj;rows=[]
 for M in (1,256):
  x=src[:,:M,:].to(torch.float16);back=x.to(torch.bfloat16)
  if not torch.isfinite(x).all():raise RuntimeError('CODE FP16 nonfinite')
  for _ in range(2):dense(x);quant(x)
  for name,mod in [('RAW_FP16',dense),('AWQ_FP16_INPUT',quant)]:
   vals=[];out=None
   for rep in range(7):out,ms=timed(lambda mod=mod:mod(x));vals.append(ms)
   rows.append({'M':M,'implementation':name,'input_sha256':tsha(x),'output_sha256':tsha(out),'module_class':type(mod).__name__,**stats(vals)})
 OUT.mkdir(parents=True);(OUT/'CODE_HOLDOUT.json').write_text(json.dumps({'status':'PASS_COMMON_CODE_AUTHORITY','token_sha256':TOKEN_SHA,'canonical_down_M2048_sha256':tsha(src),'rows':rows},indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
