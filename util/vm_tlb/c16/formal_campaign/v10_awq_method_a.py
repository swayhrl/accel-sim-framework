import json,torch
from pathlib import Path
from awq import AutoAWQForCausalLM
ids=json.loads(Path('/data/c16/inputs/.incoming/qwen2p5_7b_instruct_awq/S2_TEXT/payload/s2_text.json').read_text())
m=AutoAWQForCausalLM.from_quantized('/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641',max_seq_len=2080,fuse_layers=False,trust_remote_code=False,safetensors=True,device_map={'':0}).model.eval();mod=m.model.layers[0].mlp.down_proj;cap={};counter={'n':0}
def pre(_m,x):counter['n']+=1;cap['active']=counter['n']==2; cap['input']=x[0].detach().cpu().clone() if cap['active'] else None; torch.cuda.nvtx.range_push('C16_V10_AWQ_FIRST_DECODE_LAYER0_DOWNPROJ') if cap['active'] else None;return None
def post(_m,x,o):
 if cap.get('active'): torch.cuda.synchronize();cap['o']=o.detach().cpu().clone();torch.cuda.nvtx.range_pop()
 return None
h1=mod.register_forward_pre_hook(pre);h2=mod.register_forward_hook(post);x=torch.tensor([ids],device='cuda')
with torch.inference_mode():o=m(input_ids=x,use_cache=True);c=o.logits[:,-1,:].argmax(-1,keepdim=True);m(input_ids=c,past_key_values=o.past_key_values,use_cache=True)
h1.remove();h2.remove();print('PASS',tuple(cap['o'].shape))
