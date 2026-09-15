import hashlib,json,torch
from pathlib import Path
from awq import AutoAWQForCausalLM
ids=json.loads(Path('/data/c16/inputs/.incoming/qwen2p5_7b_instruct_awq/S2_TEXT/payload/s2_text.json').read_text())
m=AutoAWQForCausalLM.from_quantized('/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641',max_seq_len=2080,fuse_layers=False,trust_remote_code=False,safetensors=True,device_map={'':0}).model.eval();mod=m.model.layers[0].mlp.down_proj;cap={}
def hook(_m,x,o):cap['input']=x[0].detach().cpu().clone();cap['output']=o.detach().cpu().clone();return None
h=mod.register_forward_hook(hook);x=torch.tensor([ids],device='cuda')
with torch.inference_mode():o=m(input_ids=x,use_cache=True);c=o.logits[:,-1,:].argmax(-1,keepdim=True);o=m(input_ids=c,past_key_values=o.past_key_values,use_cache=True)
h.remove();inp=cap['input'].cuda()
with torch.inference_mode():rep=mod(inp).cpu()
eq=torch.equal(rep,cap['output']);diff=(rep.float()-cap['output'].float()).abs().max().item()
def info(n,t):return {'name':n,'shape':list(t.shape),'dtype':str(t.dtype),'bytes':t.nbytes,'sha256':hashlib.sha256(t.detach().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()}
q={'schema':'C16_V9_AWQ_SEMANTIC_MODULE_REPLAY_V1','status':'PASS' if eq else 'FAIL','layer':0,'role':'mlp.down_proj','phase':'DECODE_STEP_0','input_sha256':hashlib.sha256(cap['input'].view(torch.uint8).numpy().tobytes()).hexdigest(),'output_sha256':hashlib.sha256(cap['output'].view(torch.uint8).numpy().tobytes()).hexdigest(),'shape':list(cap['input'].shape),'bitwise_equal':eq,'max_abs':diff,'tensors':[info(n,t) for n,t in [('qweight',mod.qweight),('qzeros',mod.qzeros),('scales',mod.scales),('bias',mod.bias)] if t is not None]};Path('/data/c16/v9_awq_module.json').write_text(json.dumps(q,indent=2)+'\n');torch.save({'input':cap['input'],'output':cap['output']},'/data/c16/v9_awq_module_state.pt');print(json.dumps(q))
