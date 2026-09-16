import json,hashlib,torch
from pathlib import Path
from safetensors import safe_open
from transformers import Qwen3Config
from transformers.cache_utils import DynamicCache
from transformers.models.qwen3.modeling_qwen3 import Qwen3DecoderLayer,Qwen3RotaryEmbedding
R=Path('/data/c16/models/.incoming/qwen3_8b/b968826d9c46dd6066d109eabc6255188de91218');c=Qwen3Config.from_pretrained(R,local_files_only=True);idx=json.loads((R/'model.safetensors.index.json').read_text());s=torch.load('/data/c16/qwen3_runtime_v14/attention_preattn_state.pt',weights_only=True)
def ten(k):
 with safe_open(R/idx['weight_map'][k],framework='pt',device='cpu') as f:return f.get_tensor(k)
l=Qwen3DecoderLayer(c,0).to(dtype=torch.bfloat16);l.load_state_dict({n:ten('model.layers.0.'+n) for n in l.state_dict()},strict=True);l=l.cuda().eval();cache=DynamicCache.from_legacy_cache(((s['key'].cuda(),s['value'].cuda()),));x=s['input'].cuda();p=s['position'].cuda();rot=Qwen3RotaryEmbedding(config=c).cuda()
torch.cuda.nvtx.range_push('C16_V18_QWEN3_DIRECT_REPLAY_LAYER0_SELF_ATTN')
with torch.inference_mode():out=l.self_attn(hidden_states=x,attention_mask=s['attention_mask'].cuda() if s['attention_mask'] is not None else None,position_embeddings=rot(x,p),past_key_values=cache,cache_position=torch.tensor([2048],device='cuda'))[0];torch.cuda.synchronize()
torch.cuda.nvtx.range_pop();o=out.cpu();eq=torch.equal(o,s['output']);q={'status':'PASS' if eq else 'FAIL','bitwise_equal':eq,'max_abs':(o.float()-s['output'].float()).abs().max().item(),'input_sha':hashlib.sha256(s['input'].view(torch.uint8).numpy().tobytes()).hexdigest(),'output_sha':hashlib.sha256(o.view(torch.uint8).numpy().tobytes()).hexdigest(),'k_sha':hashlib.sha256(s['key'].view(torch.uint8).numpy().tobytes()).hexdigest(),'v_sha':hashlib.sha256(s['value'].view(torch.uint8).numpy().tobytes()).hexdigest(),'shape':list(o.shape)};print(json.dumps(q))
