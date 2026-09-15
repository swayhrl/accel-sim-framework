import gc,json,torch
from pathlib import Path
from safetensors import safe_open
from transformers import Qwen2Config
from transformers.models.qwen2.modeling_qwen2 import Qwen2DecoderLayer,Qwen2RotaryEmbedding,Qwen2RMSNorm
from transformers.cache_utils import DynamicCache
R=Path('/data/c16/models/.incoming/qwen2p5_7b_instruct_raw/a09a35458c702b33eeacc393d103063234e8bc28');cfg=Qwen2Config.from_pretrained(R);idx=json.loads((R/'model.safetensors.index.json').read_text())['weight_map']
def ten(k):
 with safe_open(R/idx[k],framework='pt',device='cpu') as s:return s.get_tensor(k)
def load_layer(i):
 l=Qwen2DecoderLayer(cfg,i).to(dtype=torch.bfloat16);l.load_state_dict({n:ten(f'model.layers.{i}.'+n) for n in l.state_dict()},strict=True);return l.cuda().eval()
ids=json.loads(Path('/data/c16/inputs/.incoming/qwen2p5_7b_instruct_raw/S2_TEXT/payload/token_ids.json').read_text());emb=torch.nn.Embedding(cfg.vocab_size,cfg.hidden_size,dtype=torch.bfloat16);emb.weight.data.copy_(ten('model.embed_tokens.weight'));emb=emb.cuda().eval();x=emb(torch.tensor([ids],device='cuda'));pos=torch.arange(len(ids),device='cuda').unsqueeze(0);rot=Qwen2RotaryEmbedding(config=cfg).cuda();pe=rot(x,pos);cache=DynamicCache()
with torch.inference_mode():
 for i in range(cfg.num_hidden_layers):
  l=load_layer(i);o=l(x,position_ids=pos,past_key_value=cache,use_cache=True,cache_position=torch.arange(len(ids),device='cuda'),position_embeddings=pe);x=o[0];del l;torch.cuda.empty_cache();gc.collect()
 norm=Qwen2RMSNorm(cfg.hidden_size,eps=cfg.rms_norm_eps).to(dtype=torch.bfloat16);norm.weight.data.copy_(ten('model.norm.weight'));norm=norm.cuda();x=norm(x);head=torch.nn.Linear(cfg.hidden_size,cfg.vocab_size,bias=False,dtype=torch.bfloat16);head.weight.data.copy_(ten('lm_head.weight'));head=head.cuda();nxt=head(x[:,-1,:]).argmax(-1,keepdim=True);print('RAW_NEXT',int(nxt.item()))
Path('/data/c16/v8_raw_full_stream.json').write_text(json.dumps({'status':'PASS','layers':cfg.num_hidden_layers,'next_token':int(nxt.item()),'kv_layers':len(cache.key_cache),'hidden_shape':list(x.shape)})+'\n')
