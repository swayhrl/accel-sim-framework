import json,gc,torch
from pathlib import Path
from safetensors import safe_open
from transformers import Qwen3Config
from transformers.cache_utils import DynamicCache
from transformers.models.qwen3.modeling_qwen3 import Qwen3DecoderLayer,Qwen3RotaryEmbedding
R=Path('/data/c16/models/.incoming/qwen3_8b/b968826d9c46dd6066d109eabc6255188de91218');c=Qwen3Config.from_pretrained(R,local_files_only=True);idx=json.loads((R/'model.safetensors.index.json').read_text())['weight_map'];pay=json.loads(Path('docs/vm_tlb/review_packs/C16_QWEN3_V2_INPUT_EXPORT_174NEW_V13/payloads/qwen3-8b__S2_TEXT.json').read_text());ids=pay['token_ids'][0]
def ten(k):
 with safe_open(R/idx[k],framework='pt',device='cpu') as s:return s.get_tensor(k)
def layer(i):
 l=Qwen3DecoderLayer(c,i).to(dtype=torch.bfloat16);l.load_state_dict({n:ten('model.layers.'+str(i)+'.'+n) for n in l.state_dict()},strict=True);return l.cuda().eval()
emb=torch.nn.Embedding(c.vocab_size,c.hidden_size,dtype=torch.bfloat16);emb.weight.data.copy_(ten('model.embed_tokens.weight'));emb=emb.cuda();x=emb(torch.tensor([ids],device='cuda'));p=torch.arange(len(ids),device='cuda').unsqueeze(0);rot=Qwen3RotaryEmbedding(config=c).cuda();pe=rot(x,p);cache=DynamicCache()
with torch.inference_mode():
 for i in range(c.num_hidden_layers):
  l=layer(i);x=l(x,position_ids=p,past_key_value=cache,use_cache=True,cache_position=torch.arange(len(ids),device='cuda'),position_embeddings=pe)[0];del l;torch.cuda.empty_cache();gc.collect()
torch.cuda.synchronize();print(json.dumps({'status':'PASS','layers':c.num_hidden_layers,'shape':list(x.shape),'kv_layers':len(cache.key_cache),'finite':bool(torch.isfinite(x).all()),'peak':torch.cuda.max_memory_reserved()}))
