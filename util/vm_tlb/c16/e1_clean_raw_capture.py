#!/usr/bin/env python3
import argparse,gc,hashlib,json,os
from pathlib import Path
import torch
from safetensors import safe_open
from transformers import Qwen2Config
from transformers.models.qwen2.modeling_qwen2 import Qwen2DecoderLayer,Qwen2RotaryEmbedding
from transformers.cache_utils import DynamicCache
ROOT=Path('/data/c16/models/.incoming/qwen2p5_7b_instruct_raw/a09a35458c702b33eeacc393d103063234e8bc28');TOK=Path('/data/c16/inputs/.incoming/qwen2p5_7b_instruct_raw/S2_TEXT/payload/token_ids.json')
TOKEN_SHA='0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9'
def fsha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def tsha(t):return hashlib.sha256(t.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()
def info(t):return {'shape':list(t.shape),'stride':list(t.stride()),'dtype':str(t.dtype),'byte_sha256':tsha(t),'bytes':t.numel()*t.element_size()}
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 if a.out.exists() or Path(str(a.out)+'.partial').exists():raise SystemExit('output exists')
 if fsha(TOK)!=TOKEN_SHA:raise SystemExit('token authority')
 cfg=Qwen2Config.from_pretrained(ROOT);idx=json.loads((ROOT/'model.safetensors.index.json').read_text())['weight_map']
 def ten(k):
  with safe_open(ROOT/idx[k],framework='pt',device='cpu') as s:return s.get_tensor(k)
 def layer(i):
  x=Qwen2DecoderLayer(cfg,i).to(dtype=torch.bfloat16);x.load_state_dict({n:ten(f'model.layers.{i}.'+n) for n in x.state_dict()},strict=True);return x.cuda().eval()
 ids=json.loads(TOK.read_text());
 if len(ids)!=2048:raise SystemExit('token count')
 emb=torch.nn.Embedding(cfg.vocab_size,cfg.hidden_size,dtype=torch.bfloat16);emb.weight.data.copy_(ten('model.embed_tokens.weight'));emb=emb.cuda().eval();x=emb(torch.tensor([ids],device='cuda'));pos=torch.arange(2048,device='cuda').unsqueeze(0);rot=Qwen2RotaryEmbedding(config=cfg).cuda();pe=rot(x,pos);cache=DynamicCache();cap={};points={}
 with torch.inference_mode():
  for i in range(cfg.num_hidden_layers):
   l=layer(i);hooks=[]
   if i==0:
    def hook(role):
     def f(module,args):cap[role]=args[0].detach().clone()
     return f
    hooks=[l.self_attn.q_proj.register_forward_pre_hook(hook('q_proj')),l.mlp.down_proj.register_forward_pre_hook(hook('down_proj')),l.mlp.up_proj.register_forward_pre_hook(hook('up_proj'))]
   x=l(x,position_ids=pos,past_key_value=cache,use_cache=True,cache_position=torch.arange(2048,device='cuda'),position_embeddings=pe)[0]
   if i==0:
    for h in hooks:h.remove()
    for role,module in [('q_proj',l.self_attn.q_proj),('down_proj',l.mlp.down_proj),('up_proj',l.mlp.up_proj)]:
     for m in (2048,256,1):
      inp=cap[role] if m==2048 else cap[role][:,:m,:]
      out1=module(inp);out2=module(inp)
      if not torch.equal(out1,out2):raise RuntimeError(role+f' M{m} direct repeat')
      points[f'{role}_M{m}']={'input':inp.detach().cpu().clone(),'output':out1.detach().cpu().clone(),'input_info':info(inp),'output_info':info(out1)}
   del l;torch.cuda.empty_cache();gc.collect()
 partial=Path(str(a.out)+'.partial');partial.mkdir(parents=True)
 rec={'status':'PASS_C16_E1_CANONICAL_RAW_ACTIVATION_CAPTURE','model_revision':ROOT.name,'model_root':str(ROOT),'token_path':str(TOK),'token_sha256':TOKEN_SHA,'recipe':'V8 natural M2048 stream; live Layer0 q_proj/down_proj/up_proj pre-hooks; first-row/first-256 slices','points':{}}
 for name,d in points.items():
  torch.save(d['input'],partial/(name+'_input.pt'));torch.save(d['output'],partial/(name+'_raw_bf16_oracle.pt'));rec['points'][name]={'input_file':name+'_input.pt','oracle_file':name+'_raw_bf16_oracle.pt','input':d['input_info'],'output':d['output_info']}
 (partial/'CANONICAL_RAW_CAPTURE_RECEIPT.json').write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n');os.rename(partial,a.out);print(json.dumps({'status':rec['status'],'out':str(a.out)}))
if __name__=='__main__':main()
