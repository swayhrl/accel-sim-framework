import json,gc,hashlib,torch
from pathlib import Path
from safetensors import safe_open
from transformers import Qwen3Config
from transformers.cache_utils import DynamicCache
from transformers.models.qwen3.modeling_qwen3 import Qwen3DecoderLayer,Qwen3RotaryEmbedding,Qwen3RMSNorm
R=Path('/data/c16/models/.incoming/qwen3_8b/b968826d9c46dd6066d109eabc6255188de91218');c=Qwen3Config.from_pretrained(R,local_files_only=True);idx=json.loads((R/'model.safetensors.index.json').read_text());pay=json.loads(Path('docs/vm_tlb/review_packs/C16_QWEN3_V2_INPUT_EXPORT_174NEW_V13/payloads/qwen3-8b__S2_TEXT.json').read_text());ids=pay['token_ids'][0]
def ten(k):
 with safe_open(R/idx['weight_map'][k],framework='pt',device='cpu') as s:return s.get_tensor(k)
def layer(i):
 l=Qwen3DecoderLayer(c,i).to(dtype=torch.bfloat16);l.load_state_dict({n:ten('model.layers.'+str(i)+'.'+n) for n in l.state_dict()},strict=True);return l.cuda().eval()
emb=torch.nn.Embedding(c.vocab_size,c.hidden_size,dtype=torch.bfloat16);emb.weight.data.copy_(ten('model.embed_tokens.weight'));emb=emb.cuda();x=emb(torch.tensor([ids],device='cuda'));p=torch.arange(len(ids),device='cuda').unsqueeze(0);rot=Qwen3RotaryEmbedding(config=c).cuda();cache=DynamicCache()
with torch.inference_mode():
 for i in range(c.num_hidden_layers):
  l=layer(i);x=l(x,position_ids=p,past_key_value=cache,use_cache=True,cache_position=torch.arange(len(ids),device='cuda'),position_embeddings=rot(x,p))[0];del l;torch.cuda.empty_cache();gc.collect()
 norm=Qwen3RMSNorm(c.hidden_size,eps=c.rms_norm_eps).to(dtype=torch.bfloat16);norm.weight.data.copy_(ten('model.norm.weight'));norm=norm.cuda();head=torch.nn.Linear(c.hidden_size,c.vocab_size,bias=False,dtype=torch.bfloat16);head.weight.data.copy_(ten('lm_head.weight'));head=head.cuda();nxt=head(norm(x)[:,-1,:]).argmax(-1,keepdim=True);del norm,head;torch.cuda.empty_cache();l=layer(0);cap={}
def pre(_m,args,kwargs):
 cap['in']=kwargs['hidden_states'].detach().cpu().clone()
 cap['attention_mask']=kwargs.get('attention_mask').detach().cpu().clone() if kwargs.get('attention_mask') is not None else None
 return None
def hk(_m,inp,out):cap['out']=out[0].detach().cpu().clone() if isinstance(out,tuple) else out.detach().cpu().clone();return None
h0=l.self_attn.register_forward_pre_hook(pre,with_kwargs=True);h=l.self_attn.register_forward_hook(hk)
with torch.inference_mode():
 dx=emb(nxt);dp=torch.tensor([[len(ids)]],device='cuda');l(dx,position_ids=dp,past_key_value=cache,use_cache=True,cache_position=torch.tensor([len(ids)],device='cuda'),position_embeddings=rot(dx,dp))[0]
h.remove();h0.remove();s={'input':cap['in'],'output':cap['out'],'key':cache.key_cache[0][:,:,:-1,:].cpu().clone(),'value':cache.value_cache[0][:,:,:-1,:].cpu().clone(),'attention_mask':cap['attention_mask'],'decode_token':int(nxt.item()),'position':dp.cpu()};torch.save(s,'/data/c16/qwen3_runtime_v14/attention_preattn_state.pt');print(json.dumps({'status':'PASS','token':int(nxt.item()),'input_shape':list(cap['in'].shape),'output_shape':list(cap['out'].shape),'k_shape':list(s['key'].shape),'v_shape':list(s['value'].shape),'mask_shape':list(s['attention_mask'].shape) if s['attention_mask'] is not None else None}))
