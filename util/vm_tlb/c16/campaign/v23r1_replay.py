import hashlib,json,os
from pathlib import Path
import torch
from safetensors import safe_open
ROOT=Path('/data/c16/models/.incoming/deepseek_v2_lite/604d5664dddd88a0433dbae533b7fe9472482de0');STATE=Path('/data/c16/deepseek_v23r1/state');target=os.environ['C16_V23R1_TARGET']
def sha(t):return hashlib.sha256(t.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()
def info(t):
 s=t.untyped_storage();return {'shape':list(t.shape),'dtype':str(t.dtype),'stride':list(t.stride()),'ptr':hex(t.data_ptr()),'storage_ptr':hex(s.data_ptr()),'storage_bytes':s.nbytes(),'sha256':sha(t)}
if target=='MLA':
 st=torch.load(STATE/'MLA_TARGET_STATE.pt',weights_only=True);name='model.layers.0.self_attn.kv_b_proj.weight';src_name='MLA_KV_A_LATENT_NORM';dst_name='MLA_KV_B_EXPANDED';label='C16_V23R1_MLA_KV_B_EXPAND_REPLAY'
elif target=='MOE':
 st=torch.load(STATE/'MOE_TARGET_STATE.pt',weights_only=True);eid=int(st['selected_expert_id']);name=f'model.layers.1.mlp.experts.{eid}.down_proj.weight';src_name='ROUTED_EXPERT_DOWN_INPUT';dst_name='ROUTED_EXPERT_DOWN_OUTPUT';label='C16_V23R1_MOE_EXPERT_DOWN_REPLAY'
else:raise SystemExit('target')
idx=json.loads((ROOT/'model.safetensors.index.json').read_text())['weight_map']
with safe_open(ROOT/idx[name],framework='pt',device='cpu') as f:w=f.get_tensor(name)
inp=st['input'] if target=='MLA' else st['down_input'];expected=st['output'] if target=='MLA' else st['down_output'];lin=torch.nn.Linear(w.shape[1],w.shape[0],bias=False,dtype=w.dtype);lin.weight.data.copy_(w);lin=lin.cuda().eval();x=inp.cuda();torch.cuda.nvtx.range_push(label)
with torch.inference_mode():out=lin(x);torch.cuda.synchronize()
torch.cuda.nvtx.range_pop();eq=torch.equal(out.cpu(),expected);r={'schema_version':1,'target':target,'status':'PASS' if eq else 'FAIL','semantic_role':'layer0.self_attn.kv_b_proj' if target=='MLA' else f'layer1.mlp.experts.{eid}.down_proj','selected_expert_id':eid if target=='MOE' else None,'input':info(x),'output':info(out),'expected_output_sha256':sha(expected),'output_bitwise_equal':eq,'max_abs':float((out.cpu().float()-expected.float()).abs().max()),'weight':info(lin.weight),'nvtx_range':label}
trace=os.environ.get('C16_WARP_OUTPUT');ctx=os.environ.get('C16_V23R1_CONTEXT_OUT');static=os.environ.get('C16_V23R1_STATIC_MAP')
if trace and ctx and static and Path(trace).is_file():
 h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();ranges=[{'class':src_name,'address_start_hex':hex(x.data_ptr()),'storage_bytes':x.nbytes},{'class':dst_name,'address_start_hex':hex(out.data_ptr()),'storage_bytes':out.nbytes},{'class':'EXPERT_WEIGHT' if target=='MOE' else 'MLA_KV_B_WEIGHT','address_start_hex':hex(lin.weight.data_ptr()),'storage_bytes':lin.weight.nbytes}];Path(ctx).write_text(json.dumps({'schema_version':'C16_ADDRESS_CONTEXT_V1','same_process_only':True,'target':target,'semantic_role':r['semantic_role'],'selected_expert_id':r['selected_expert_id'],'trace_path':trace,'trace_sha256':h(trace),'static_map_path':static,'static_map_sha256':h(static),'static_index':os.environ.get('C16_WARP_STATIC'),'function_occurrence':os.environ.get('C16_WARP_FUNCTION_OCCURRENCE'),'ranges':ranges},indent=2,sort_keys=True)+'\n')
(STATE/f'{target}_REPLAY.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(r,sort_keys=True))
if not eq:raise SystemExit(1)
