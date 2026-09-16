import json,torch,hashlib
from pathlib import Path
from safetensors import safe_open
from transformers import Qwen3Config
from transformers.cache_utils import DynamicCache
from transformers.models.qwen3.modeling_qwen3 import Qwen3DecoderLayer,Qwen3RotaryEmbedding
import transformers.models.qwen3.modeling_qwen3 as q3
R=Path('/data/c16/models/.incoming/qwen3_8b/b968826d9c46dd6066d109eabc6255188de91218');c=Qwen3Config.from_pretrained(R,local_files_only=True);idx=json.loads((R/'model.safetensors.index.json').read_text());s=torch.load('/data/c16/qwen3_runtime_v14/attention_preattn_state.pt',weights_only=True);ev=[]
def ten(k):
 with safe_open(R/idx['weight_map'][k],framework='pt',device='cpu') as f:return f.get_tensor(k)
def d(n,t):
 z=t.untyped_storage();return {'name':n,'shape':list(t.shape),'dtype':str(t.dtype),'stride':list(t.stride()),'ptr':hex(t.data_ptr()),'storage_ptr':hex(z.data_ptr()),'storage_bytes':z.nbytes()}
l=Qwen3DecoderLayer(c,0).to(dtype=torch.bfloat16);l.load_state_dict({n:ten('model.layers.0.'+n) for n in l.state_dict()},strict=True);l=l.cuda().eval();cache=DynamicCache.from_legacy_cache(((s['key'].cuda(),s['value'].cuda()),));old_update=cache.update
def upd(k,v,li,kw):
 ev.append({'op':'PREEXISTING_KV_STORAGE','K':d('K_pre',cache.key_cache[0]),'V':d('V_pre',cache.value_cache[0])});o=old_update(k,v,li,kw);ev.append({'op':'POST_UPDATE_KV_STORAGE','K':d('K_post',o[0]),'V':d('V_post',o[1])});return o
cache.update=upd
old=q3.eager_attention_forward
def wrap(m,q,k,v,mask,scaling,dropout=0.0,**kw):
 torch.cuda.nvtx.range_push('C16_V18R2_KV_REPEAT_K');ks=q3.repeat_kv(k,m.num_key_value_groups);torch.cuda.synchronize();torch.cuda.nvtx.range_pop();ev.append({'op':'KV_DERIVED_REPEAT_BUFFER_K','source':d('K_post',k),'derived':d('K_repeat',ks),'alias':k.untyped_storage().data_ptr()==ks.untyped_storage().data_ptr()})
 torch.cuda.nvtx.range_push('C16_V18R2_KV_REPEAT_V');vs=q3.repeat_kv(v,m.num_key_value_groups);torch.cuda.synchronize();torch.cuda.nvtx.range_pop();ev.append({'op':'KV_DERIVED_REPEAT_BUFFER_V','source':d('V_post',v),'derived':d('V_repeat',vs),'alias':v.untyped_storage().data_ptr()==vs.untyped_storage().data_ptr()})
 torch.cuda.nvtx.range_push('C16_V18R2_ATTN_QK_MATMUL');aw=torch.matmul(q,ks.transpose(2,3))*scaling;torch.cuda.synchronize();torch.cuda.nvtx.range_pop();ev.append({'op':'ATTENTION_CORE_OPERAND_QK','K_operand':d('K_repeat',ks)})
 if mask is not None:aw=aw+mask[:,:,:,:ks.shape[-2]]
 torch.cuda.nvtx.range_push('C16_V18R2_ATTN_SOFTMAX');aw=torch.nn.functional.softmax(aw,dim=-1,dtype=torch.float32).to(q.dtype);aw=torch.nn.functional.dropout(aw,p=dropout,training=m.training);torch.cuda.synchronize();torch.cuda.nvtx.range_pop()
 torch.cuda.nvtx.range_push('C16_V18R2_ATTN_AV_MATMUL');ao=torch.matmul(aw,vs);torch.cuda.synchronize();torch.cuda.nvtx.range_pop();ev.append({'op':'ATTENTION_CORE_OPERAND_AV','V_operand':d('V_repeat',vs)})
 return ao.transpose(1,2).contiguous(),aw
q3.eager_attention_forward=wrap;x=s['input'].cuda();p=s['position'].cuda()
with torch.inference_mode():o=l.self_attn(hidden_states=x,attention_mask=None,position_embeddings=Qwen3RotaryEmbedding(config=c).cuda()(x,p),past_key_value=cache,cache_position=torch.tensor([2048],device='cuda'))[0];torch.cuda.synchronize()
q3.eager_attention_forward=old;out=o.cpu();r={'status':'PASS' if torch.equal(out,s['output']) and cache.get_seq_length(0)==2049 else 'FAIL','bitwise_equal':torch.equal(out,s['output']),'max_abs':(out.float()-s['output'].float()).abs().max().item(),'cache_after':cache.get_seq_length(0),'events':ev};Path('/data/c16/qwen3_runtime_v14/v18r2_dataflow.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'events':len(ev)}))
