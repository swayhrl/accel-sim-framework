import hashlib,json,torch
from pathlib import Path
from safetensors import safe_open
from transformers import Qwen2Config
from transformers.cache_utils import DynamicCache
from transformers.models.qwen2.modeling_qwen2 import Qwen2DecoderLayer,Qwen2RotaryEmbedding
R=Path('/data/c16/models/.incoming/qwen2p5_7b_instruct_raw/a09a35458c702b33eeacc393d103063234e8bc28');cfg=Qwen2Config.from_pretrained(R);idx=json.loads((R/'model.safetensors.index.json').read_text())['weight_map']
def ten(k):
 with safe_open(R/idx[k],framework='pt',device='cpu') as s:return s.get_tensor(k)
def layer():
 l=Qwen2DecoderLayer(cfg,0).to(dtype=torch.bfloat16);l.load_state_dict({n:ten('model.layers.0.'+n) for n in l.state_dict()},strict=True);return l.cuda().eval()
state=torch.load('/data/c16/v8_target_layer0_decode.pt',weights_only=True);l=layer();cap={}
def hook(_m,x,o):cap['input']=x[0].detach().cpu().clone();cap['output']=o.detach().cpu().clone();return None
h=l.mlp.down_proj.register_forward_hook(hook);c=DynamicCache();c.key_cache=[state['key'].cuda()];c.value_cache=[state['value'].cuda()];x=state['decode_input'].cuda();p=state['position'].cuda();rot=Qwen2RotaryEmbedding(config=cfg).cuda()
with torch.inference_mode():l(x,position_ids=p,past_key_value=c,use_cache=True,cache_position=torch.tensor([2048],device='cuda'),position_embeddings=rot(x,p))
h.remove()
with torch.inference_mode():rep=l.mlp.down_proj(cap['input'].cuda()).cpu()
eq=torch.equal(rep,cap['output']);diff=(rep.float()-cap['output'].float()).abs().max().item();q={'schema':'C16_V9_RAW_SEMANTIC_MODULE_REPLAY_V1','status':'PASS' if eq else 'FAIL','layer':0,'role':'mlp.down_proj','phase':'DECODE_STEP_0','shape':list(cap['input'].shape),'input_sha256':hashlib.sha256(cap['input'].view(torch.uint8).numpy().tobytes()).hexdigest(),'output_sha256':hashlib.sha256(cap['output'].view(torch.uint8).numpy().tobytes()).hexdigest(),'bitwise_equal':eq,'max_abs':diff,'weight_sha256':hashlib.sha256(l.mlp.down_proj.weight.detach().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()};Path('/data/c16/v9_raw_module.json').write_text(json.dumps(q,indent=2)+'\n');torch.save({'input':cap['input'],'output':cap['output']},'/data/c16/v9_raw_module_state.pt');print(json.dumps(q))
