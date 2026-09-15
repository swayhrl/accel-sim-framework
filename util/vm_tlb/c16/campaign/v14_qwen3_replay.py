import json,hashlib,torch,os
from pathlib import Path
from safetensors import safe_open
from transformers import Qwen3Config
from transformers.models.qwen3.modeling_qwen3 import Qwen3DecoderLayer
R=Path('/data/c16/models/.incoming/qwen3_8b/b968826d9c46dd6066d109eabc6255188de91218');c=Qwen3Config.from_pretrained(R,local_files_only=True);idx=json.loads((R/'model.safetensors.index.json').read_text())['weight_map'];s=torch.load('/data/c16/qwen3_runtime_v14/layer0_first_decode_state.pt',weights_only=True);l=Qwen3DecoderLayer(c,0).to(dtype=torch.bfloat16);d={}
for n in l.state_dict():
 k='model.layers.0.'+n
 with safe_open(R/idx[k],framework='pt',device='cpu') as f:d[n]=f.get_tensor(k)
l.load_state_dict(d,strict=True);l=l.cuda().eval()
torch.cuda.nvtx.range_push('C16_V14_QWEN3_DIRECT_REPLAY_LAYER0_DOWNPROJ')
with torch.inference_mode():o=l.mlp.down_proj(s['input'].cuda()).cpu();torch.cuda.synchronize()
torch.cuda.nvtx.range_pop()
eq=torch.equal(o,s['output']);q={'status':'PASS' if eq else 'FAIL','bitwise_equal':eq,'max_abs':(o.float()-s['output'].float()).abs().max().item(),'shape':list(o.shape),'weight_sha256':hashlib.sha256(l.mlp.down_proj.weight.detach().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()}
tr=os.environ.get('C16_WARP_OUTPUT');co=os.environ.get('C16_V14_CONTEXT_OUT');sm=os.environ.get('C16_V14_STATIC_MAP')
if tr and co and sm and Path(tr).is_file():
 h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();ctx={'schema_version':'C16_ADDRESS_CONTEXT_V1','same_process_only':True,'target_id':'QWEN3_S2_DECODE_LAYER0_MLP_DOWN','trace_path':tr,'trace_sha256':h(tr),'static_map_path':sm,'static_map_sha256':h(sm),'static_index':os.environ.get('C16_WARP_STATIC'),'function_occurrence':os.environ.get('C16_WARP_FUNCTION_OCCURRENCE'),'semantic_role':'model.layers.0.mlp.down_proj','ranges':[{'class':'WEIGHT','runtime_name':'model.layers.0.mlp.down_proj.weight','address_start_hex':hex(l.mlp.down_proj.weight.data_ptr()),'storage_bytes':l.mlp.down_proj.weight.nbytes},{'class':'ACTIVATION','runtime_name':'input','address_start_hex':hex(s['input'].data_ptr()),'storage_bytes':s['input'].nbytes},{'class':'ACTIVATION','runtime_name':'output','address_start_hex':hex(o.data_ptr()),'storage_bytes':o.nbytes}]};Path(co).write_text(json.dumps(ctx,indent=2)+'\n')
print(json.dumps(q))
