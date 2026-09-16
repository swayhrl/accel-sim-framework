import json,torch,hashlib,os
from pathlib import Path
from safetensors import safe_open
from transformers import Qwen3Config
from transformers.cache_utils import DynamicCache
from transformers.models.qwen3.modeling_qwen3 import Qwen3DecoderLayer,Qwen3RotaryEmbedding,apply_rotary_pos_emb,repeat_kv
R=Path('/data/c16/models/.incoming/qwen3_8b/b968826d9c46dd6066d109eabc6255188de91218');c=Qwen3Config.from_pretrained(R,local_files_only=True);idx=json.loads((R/'model.safetensors.index.json').read_text());s=torch.load('/data/c16/qwen3_runtime_v14/attention_preattn_state.pt',weights_only=True)
def ten(k):
 with safe_open(R/idx['weight_map'][k],framework='pt',device='cpu') as f:return f.get_tensor(k)
l=Qwen3DecoderLayer(c,0).to(dtype=torch.bfloat16);l.load_state_dict({n:ten('model.layers.0.'+n) for n in l.state_dict()},strict=True);l=l.cuda().eval();a=l.self_attn;cache=DynamicCache.from_legacy_cache(((s['key'].cuda(),s['value'].cuda()),));x=s['input'].cuda();p=s['position'].cuda();shape=(*x.shape[:-1],-1,a.head_dim)
with torch.inference_mode():
 k=a.k_norm(a.k_proj(x).view(shape)).transpose(1,2);v=a.v_proj(x).view(shape).transpose(1,2);q=a.q_norm(a.q_proj(x).view(shape)).transpose(1,2);cos,sin=Qwen3RotaryEmbedding(config=c).cuda()(x,p);q,k=apply_rotary_pos_emb(q,k,cos,sin);k,v=cache.update(k,v,0,{'sin':sin,'cos':cos,'cache_position':torch.tensor([2048],device='cuda')});torch.cuda.nvtx.range_push('C16_V18R2_REPEAT_K_DIRECT');out=repeat_kv(k,a.num_key_value_groups);torch.cuda.synchronize();torch.cuda.nvtx.range_pop();out2=repeat_kv(k,a.num_key_value_groups);torch.cuda.synchronize()
def d(t):z=t.untyped_storage();return {'shape':list(t.shape),'dtype':str(t.dtype),'ptr':hex(t.data_ptr()),'storage_ptr':hex(z.data_ptr()),'storage_bytes':z.nbytes(),'sha':hashlib.sha256(t.cpu().contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()}
res={'status':'PASS' if torch.equal(out,out2) and cache.get_seq_length(0)==2049 else 'FAIL','repeat_bitwise':torch.equal(out,out2),'cache_after':cache.get_seq_length(0),'post_k':d(k),'derived_k_repeat':d(out),'alias':k.untyped_storage().data_ptr()==out.untyped_storage().data_ptr()}
tr=os.environ.get('C16_WARP_OUTPUT');co=os.environ.get('C16_V18R2_CONTEXT_OUT');sm=os.environ.get('C16_V18R2_STATIC_MAP')
if tr and co and sm and Path(tr).is_file():
 h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();ctx={'schema_version':'C16_ADDRESS_CONTEXT_V1','same_process_only':True,'target_id':'QWEN3_S2_ATTN_K_REPEAT_K','trace_path':tr,'trace_sha256':h(tr),'static_map_path':sm,'static_map_sha256':h(sm),'static_index':os.environ.get('C16_WARP_STATIC'),'function_occurrence':os.environ.get('C16_WARP_FUNCTION_OCCURRENCE'),'evidence_class':'KV_STORAGE_DIRECT_READ','semantic_role':'layer0.self_attn.repeat_kv(K)','ranges':[{'class':'KV_POST_UPDATE_K','runtime_name':'post_k','address_start_hex':hex(k.data_ptr()),'storage_bytes':k.nbytes},{'class':'KV_DERIVED_REPEAT_K','runtime_name':'repeat_k','address_start_hex':hex(out.data_ptr()),'storage_bytes':out.nbytes}]};Path(co).write_text(json.dumps(ctx,indent=2)+'\n')
Path('/data/c16/qwen3_runtime_v14/v18r2_repeatk.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
