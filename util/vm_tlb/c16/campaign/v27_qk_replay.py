import hashlib,json,os
from pathlib import Path
import torch
from transformers import AutoConfig,AutoModelForCausalLM
ROOT=Path('/data/c16/models/.incoming/deepseek_v2_lite/604d5664dddd88a0433dbae533b7fe9472482de0');cfg=AutoConfig.from_pretrained(ROOT,trust_remote_code=True,local_files_only=True)
with torch.device('meta'):meta=AutoModelForCausalLM.from_config(cfg,trust_remote_code=True)
S=Path('/data/c16/deepseek_v27/state/PERSISTENT_MLA_STATE.pt');state=torch.load(S,weights_only=True);q=state['qk']['query'].cuda();key=state['cache_after_decode1']['key'].cuda();expected=state['qk']['output'];scale=meta.model.layers[0].self_attn.softmax_scale
def sha(t):return hashlib.sha256(t.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()
def info(t):
 s=t.untyped_storage();return {'shape':list(t.shape),'dtype':str(t.dtype),'stride':list(t.stride()),'ptr':hex(t.data_ptr()),'storage_ptr':hex(s.data_ptr()),'storage_bytes':s.nbytes(),'sha256':sha(t)}
torch.cuda.nvtx.range_push('C16_V27_MIXED_PERSISTENT_QK_REPLAY')
with torch.inference_mode():out=torch.matmul(q,key.transpose(2,3));torch.cuda.synchronize()
torch.cuda.nvtx.range_pop();eq=torch.equal(out.cpu(),expected);r={'status':'PASS' if eq else 'FAIL','target':'layer0.self_attn.QK_matmul','evidence_class':'MIXED_PERSISTENT_CACHE_CONSUMER','persistent_component':'DynamicCache.key_cache[0] prefix positions 0..8191','current_component':'position 8192 appended before consumer','runtime_softmax_scale':scale,'output_bitwise_equal':eq,'max_abs':float((out.cpu().float()-expected.float()).abs().max()),'query':info(q),'key_cache_after':info(key),'output':info(out),'expected_sha256':sha(expected),'persistent_fraction_by_sequence_positions':8192/8193}
ctx=os.environ.get('C16_V27_CONTEXT_OUT');trace=os.environ.get('C16_WARP_OUTPUT');static=os.environ.get('C16_V27_STATIC_MAP')
if ctx and trace and static and Path(trace).is_file():
 ranges=[{'class':'QUERY_CURRENT_TOKEN','address_start_hex':r['query']['ptr'],'storage_bytes':r['query']['storage_bytes']},{'class':'QK_OUTPUT','address_start_hex':r['output']['ptr'],'storage_bytes':r['output']['storage_bytes']}]
 hstride=8193*192*2
 for head in (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15):
  start=int(r['key_cache_after']['ptr'],16)+head*hstride;ranges.append({'class':'PERSISTENT_KEY_PREFIX','head':head,'address_start_hex':'%#x'%start,'storage_bytes':8192*192*2});ranges.append({'class':'CURRENT_KEY_APPEND','head':head,'address_start_hex':'%#x'%(start+8192*192*2),'storage_bytes':192*2})
 Path(ctx).write_text(json.dumps({'schema_version':'C16_ADDRESS_CONTEXT_V1','same_process_only':True,'target':r['target'],'evidence_class':r['evidence_class'],'trace_path':trace,'static_map_path':static,'static_index':os.environ.get('C16_WARP_STATIC'),'function_occurrence':os.environ.get('C16_WARP_FUNCTION_OCCURRENCE'),'ranges':ranges},indent=2,sort_keys=True)+'\n')
Path('/data/c16/deepseek_v27/QK_REPLAY.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(r,sort_keys=True))
if not eq:raise SystemExit(1)
