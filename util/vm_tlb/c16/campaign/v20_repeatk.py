import hashlib,json,os
from pathlib import Path
import torch
from transformers.models.qwen3.modeling_qwen3 import repeat_kv

scenario=os.environ['C16_V20_SCENARIO']
base=Path('/data/c16/qwen3_runtime_v14/v20')
state=torch.load(base/f'{scenario}_kpost_state.pt',weights_only=True)
def sha(t):return hashlib.sha256(t.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()
def desc(t):
 st=t.untyped_storage();return {'shape':list(t.shape),'dtype':str(t.dtype),'stride':list(t.stride()),'ptr':hex(t.data_ptr()),'storage_ptr':hex(st.data_ptr()),'storage_bytes':st.nbytes(),'sha256':sha(t)}
k_cpu=state['k_post'];expected=state['repeat_k']
source_sha=sha(k_cpu);k=k_cpu.cuda();torch.cuda.synchronize()
torch.cuda.nvtx.range_push(f'C16_V20_{scenario}_ISOLATED_REPEAT_K')
out=repeat_kv(k,4)
torch.cuda.synchronize();torch.cuda.nvtx.range_pop()
match=torch.equal(out.cpu(),expected);r={'schema_version':1,'scenario':scenario,'status':'PASS' if match and source_sha==sha(k_cpu) else 'FAIL','source_hash_matches_frozen_kpost':source_sha==sha(k_cpu),'repeat_output_bitwise_equals_in_context':match,'source':desc(k),'output':desc(out),'non_alias':k.untyped_storage().data_ptr()!=out.untyped_storage().data_ptr(),'typed_chain':'KV_POST_UPDATE_K -> KV_DERIVED_REPEAT_K','nvtx_range':f'C16_V20_{scenario}_ISOLATED_REPEAT_K'}
trace=os.environ.get('C16_WARP_OUTPUT');context=os.environ.get('C16_V20_CONTEXT_OUT');static=os.environ.get('C16_V20_STATIC_MAP')
if trace and context and static and Path(trace).is_file():
 h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();ctx={'schema_version':'C16_ADDRESS_CONTEXT_V1','same_process_only':True,'target_id':f'QWEN3_V20_{scenario}_ISOLATED_REPEAT_K','trace_path':trace,'trace_sha256':h(trace),'static_map_path':static,'static_map_sha256':h(static),'static_index':os.environ.get('C16_WARP_STATIC'),'function_occurrence':os.environ.get('C16_WARP_FUNCTION_OCCURRENCE'),'evidence_class':'KV_STORAGE_DIRECT_READ','semantic_role':'layer0.self_attn.repeat_kv(K)','ranges':[{'class':'KV_POST_UPDATE_K','runtime_name':'post_k','address_start_hex':hex(k.data_ptr()),'storage_bytes':k.nbytes},{'class':'KV_DERIVED_REPEAT_K','runtime_name':'repeat_k','address_start_hex':hex(out.data_ptr()),'storage_bytes':out.nbytes}]};Path(context).write_text(json.dumps(ctx,indent=2,sort_keys=True)+'\n')
(base/f'{scenario}_isolated_repeat_receipt.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(r,sort_keys=True))
if not r['status']=='PASS':raise SystemExit(1)
