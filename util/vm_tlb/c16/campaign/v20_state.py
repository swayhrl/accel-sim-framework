import gc, hashlib, json, os
from pathlib import Path
import torch
import transformers
import transformers.models.qwen3.modeling_qwen3 as q3
from safetensors import safe_open
from transformers import Qwen3Config
from transformers.cache_utils import DynamicCache
from transformers.models.qwen3.modeling_qwen3 import Qwen3DecoderLayer,Qwen3RMSNorm,Qwen3RotaryEmbedding

scenario=os.environ['C16_V20_SCENARIO']
label=os.environ.get('C16_V20_OUTPUT_LABEL',scenario)
spec={'S2_TEXT':(2048,32,'5913c573054d23a444477394a60f3f280311325e81175663b4ae2abd5ef6aafb'),'S3_TEXT':(8192,16,'4acf772ccf5596edb0a2589624b5fd0e61da447024ca23bf944118dc948c36c2')}[scenario]
root=Path('/data/c16/models/.incoming/qwen3_8b/b968826d9c46dd6066d109eabc6255188de91218')
wt=Path('/home/huangrulin/workspace/worktrees/accel-sim-qwen3-v20')
payload=wt/'docs/vm_tlb/review_packs/C16_QWEN3_V2_INPUT_EXPORT_174NEW_V13/payloads'/f'qwen3-8b__{scenario}.json'
out=Path('/data/c16/qwen3_runtime_v14/v20');out.mkdir(parents=True,exist_ok=True)
def fsha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def tsha(t):return hashlib.sha256(t.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()
def desc(t):
 s=t.untyped_storage();return {'shape':list(t.shape),'dtype':str(t.dtype),'stride':list(t.stride()),'storage_bytes':s.nbytes(),'tensor_sha256':tsha(t)}
if fsha(payload)!=spec[2]:raise SystemExit('payload SHA mismatch')
ids=json.loads(payload.read_text())['token_ids'][0]
if len(ids)!=spec[0]:raise SystemExit('token length mismatch')
c=Qwen3Config.from_pretrained(root,local_files_only=True);idx=json.loads((root/'model.safetensors.index.json').read_text())
def ten(k):
 with safe_open(root/idx['weight_map'][k],framework='pt',device='cpu') as h:return h.get_tensor(k)
def layer(i):
 l=Qwen3DecoderLayer(c,i).to(dtype=torch.bfloat16);l.load_state_dict({n:ten(f'model.layers.{i}.{n}') for n in l.state_dict()},strict=True);return l.cuda().eval()
chunk=int(os.environ.get('C16_V20_QUERY_CHUNK','0'))
original_eager=q3.eager_attention_forward
def chunked_eager(m,q,k,v,mask,scaling,dropout=0.0,**kw):
 ks=q3.repeat_kv(k,m.num_key_value_groups);vs=q3.repeat_kv(v,m.num_key_value_groups);parts=[]
 for begin in range(0,q.shape[-2],chunk):
  end=min(begin+chunk,q.shape[-2]);aw=torch.matmul(q[:,:,begin:end,:],ks.transpose(2,3))*scaling
  if mask is not None:aw=aw+mask[:,:,begin:end,:ks.shape[-2]]
  aw=torch.nn.functional.softmax(aw,dim=-1,dtype=torch.float32).to(q.dtype);aw=torch.nn.functional.dropout(aw,p=dropout,training=m.training);parts.append(torch.matmul(aw,vs))
 return torch.cat(parts,dim=-2).transpose(1,2).contiguous(),None
if chunk:q3.eager_attention_forward=chunked_eager
emb=torch.nn.Embedding(c.vocab_size,c.hidden_size,dtype=torch.bfloat16);emb.weight.data.copy_(ten('model.embed_tokens.weight'));emb=emb.cuda().eval();rot=Qwen3RotaryEmbedding(config=c).cuda().eval();cache=DynamicCache();x=emb(torch.tensor([ids],device='cuda'));pos=torch.arange(len(ids),device='cuda').unsqueeze(0)
with torch.inference_mode():
 for i in range(c.num_hidden_layers):
  l=layer(i);x=l(x,position_ids=pos,past_key_value=cache,use_cache=True,cache_position=torch.arange(len(ids),device='cuda'),position_embeddings=rot(x,pos))[0];del l;torch.cuda.empty_cache();gc.collect()
 norm=Qwen3RMSNorm(c.hidden_size,eps=c.rms_norm_eps).to(dtype=torch.bfloat16);norm.weight.data.copy_(ten('model.norm.weight'));head=torch.nn.Linear(c.hidden_size,c.vocab_size,bias=False,dtype=torch.bfloat16);head.weight.data.copy_(ten('lm_head.weight'));norm,head=norm.cuda().eval(),head.cuda().eval();nxt=head(norm(x)[:,-1,:]).argmax(-1,keepdim=True);del norm,head;torch.cuda.empty_cache();gc.collect();l0=layer(0);cap={};old=q3.eager_attention_forward
 def wrap(m,q,k,v,mask,scaling,dropout=0.0,**kw):
  torch.cuda.nvtx.range_push(f'C16_V20_{scenario}_INCONTEXT_REPEAT_K');rk=q3.repeat_kv(k,m.num_key_value_groups);torch.cuda.synchronize();torch.cuda.nvtx.range_pop();cap['k']=k.detach().cpu().clone();cap['rk']=rk.detach().cpu().clone();cap['non_alias']=k.untyped_storage().data_ptr()!=rk.untyped_storage().data_ptr();rv=q3.repeat_kv(v,m.num_key_value_groups);aw=torch.matmul(q,rk.transpose(2,3))*scaling
  if mask is not None:aw=aw+mask[:,:,:,:rk.shape[-2]]
  aw=torch.nn.functional.softmax(aw,dim=-1,dtype=torch.float32).to(q.dtype);aw=torch.nn.functional.dropout(aw,p=dropout,training=m.training);ao=torch.matmul(aw,rv);return ao.transpose(1,2).contiguous(),aw
 q3.eager_attention_forward=wrap;dp=torch.tensor([[len(ids)]],device='cuda');dx=emb(nxt)
 try:o=l0.self_attn(hidden_states=dx,attention_mask=None,position_embeddings=rot(dx,dp),past_key_value=cache,cache_position=torch.tensor([len(ids)],device='cuda'))[0];torch.cuda.synchronize()
 finally:q3.eager_attention_forward=old
if cache.get_seq_length(0)!=len(ids)+1 or list(cap['k'].shape)!=[1,8,len(ids)+1,128]:raise SystemExit('state shape/cache mismatch')
r={'schema_version':1,'scenario':scenario,'output_label':label,'model_id':'Qwen/Qwen3-8B','revision':'b968826d9c46dd6066d109eabc6255188de91218','dtype':'bfloat16','attention_backend':'eager','transformers':transformers.__version__,'payload_sha256':fsha(payload),'prefill_tokens':len(ids),'decode_tokens':spec[1],'decode_token':int(nxt.item()),'cache_length_after':cache.get_seq_length(0),'k_post':desc(cap['k']),'repeat_k':desc(cap['rk']),'in_context_attention_output':desc(o),'non_alias':cap['non_alias'],'typed_chain':'KV_POST_UPDATE_K -> KV_DERIVED_REPEAT_K','query_chunk':chunk}
torch.save({'k_post':cap['k'],'repeat_k':cap['rk']},out/f'{label}_kpost_state.pt');(out/f'{label}_kpost_receipt.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(r,sort_keys=True))
