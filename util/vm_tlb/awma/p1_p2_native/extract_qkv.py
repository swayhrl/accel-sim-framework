#!/usr/bin/env python3
from __future__ import annotations
import fcntl,hashlib,json
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM
import transformers.models.qwen2.modeling_qwen2 as qwen_mod

ROOT=Path('/data/c16/awma/p1_p2_native_qualification_20260926');MODEL=Path('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775');LOCK=Path('/data/c16/locks/c16_gpu_campaign.lock');LAYER=12
INPUTS={
 'S2_TEXT':Path('/data/c16/inputs/.incoming/qwen2p5_0p5b_instruct/S2_TEXT/payload/TEXT_S2_T2048_token_ids.json'),
 'S2_CODE':Path('/data/c16/inputs/.incoming/qwen2p5_0p5b_instruct/S2_CODE/payload/CODE_S2_T2048_token_ids.json'),
 'S2_STRUCTURED':Path('/data/c16/inputs/.incoming/qwen2p5_0p5b_instruct/S2_STRUCTURED/payload/STRUCTURED_S2_T2048_token_ids.json'),
 'S3_TEXT':Path('/data/c16/inputs/.incoming/qwen2p5_0p5b_instruct/S3_TEXT/payload/TEXT_S3_T8192_token_ids.json')}
EXPECTED={'S2_TEXT':'0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9','S2_CODE':'7acdc48f59cf204c192c5663d62abfb72fb8d754e6b0e92bd28d991b64fdafb8','S2_STRUCTURED':'890eea663a639ed021e39f49c2d70f661a6f61012d357f7b0dd18fb9682dbe8b','S3_TEXT':'9e127ae9363358c3b2ed3b09608d9268fd3fc799070d58688aa540be019a3bb4'}
ACCEPTED_S2_PREFIX=[23578,11,323,3950,28360,1969,7146,6822,198,983,279,51572,1614,23578,12433,553]
def fsha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def tsha(t):return hashlib.sha256(t.detach().contiguous().view(torch.uint8).cpu().numpy().tobytes()).hexdigest()
def main():
 out=ROOT/'input';out.mkdir(parents=True,exist_ok=False);ids={n:json.loads(p.read_text()) for n,p in INPUTS.items()}
 for n,p in INPUTS.items():
  if fsha(p)!=EXPECTED[n]:raise RuntimeError(f'{n} hash mismatch')
 ids['S2_CODE_ROLL1_DERIVED_CONTROL']=ids['S2_CODE'][1:]+ids['S2_CODE'][:1]
 lock=open(LOCK,'a+');fcntl.flock(lock,fcntl.LOCK_EX)
 try:
  torch.manual_seed(0);torch.cuda.set_device(0);model=AutoModelForCausalLM.from_pretrained(MODEL,local_files_only=True,trust_remote_code=False,torch_dtype=torch.float16,attn_implementation='sdpa').eval().to('cuda:0');cap={'capture':False,'active':False,'q':None};orig=qwen_mod.apply_rotary_pos_emb
  def wrapped(q,k,cos,sin,position_ids=None,unsqueeze_dim=1):
   qr,kr=orig(q,k,cos,sin,position_ids,unsqueeze_dim)
   if cap['active'] and cap['q'] is None:cap['q']=qr.detach().clone()
   return qr,kr
  def pre(*_):cap['active']=cap['capture']
  def post(*_):cap['active']=False
  target=model.model.layers[LAYER].self_attn;ha=target.register_forward_pre_hook(pre);hb=target.register_forward_hook(post);qwen_mod.apply_rotary_pos_emb=wrapped
  def scenario(name,tokens,steps):
   x=torch.tensor([tokens],dtype=torch.long,device='cuda');cap.update(capture=False,active=False,q=None)
   with torch.inference_mode():
    preout=model.model(input_ids=x,use_cache=True,return_dict=True);token=model.lm_head(preout.last_hidden_state[:,-1,:]).argmax(-1);past=preout.past_key_values;generated=[]
    for step in range(1,steps+1):
     generated.append(int(token.item()));cap['capture']=step==steps;torch.cuda.nvtx.range_push(f'QUAL=INPUT_EXTRACTION;SCENARIO={name};STEP={step};LAYER={LAYER}');z=model.model(input_ids=token[:,None],past_key_values=past,use_cache=True,return_dict=True);torch.cuda.nvtx.range_pop();past=z.past_key_values;token=model.lm_head(z.last_hidden_state[:,-1,:]).argmax(-1)
    torch.cuda.synchronize()
   q=cap['q'].cpu().contiguous();k=past[LAYER][0].detach().cpu().contiguous();v=past[LAYER][1].detach().cpu().contiguous();return {'q':q,'k':k,'v':v},generated
  try:
   p1={};gens={}
   for name in ('S2_TEXT','S2_CODE','S2_STRUCTURED','S2_CODE_ROLL1_DERIVED_CONTROL'):p1[name],gens[name]=scenario(name,ids[name],16)
   p2,gens['S3_TEXT']=scenario('S3_TEXT',ids['S3_TEXT'],1)
  finally:qwen_mod.apply_rotary_pos_emb=orig;ha.remove();hb.remove()
  if gens['S2_TEXT']!=ACCEPTED_S2_PREFIX:raise RuntimeError(f'accepted S2 generation mismatch {gens["S2_TEXT"]}')
  if gens['S3_TEXT'][0]!=21:raise RuntimeError(f'accepted S3 first token mismatch {gens["S3_TEXT"]}')
  for n,x in p1.items():
   if tuple(x['q'].shape)!=(1,14,1,64) or tuple(x['k'].shape)!=(1,2,2064,64):raise RuntimeError(f'P1 shape {n} {x["q"].shape} {x["k"].shape}')
  if tuple(p2['q'].shape)!=(1,14,1,64) or tuple(p2['k'].shape)!=(1,2,8193,64):raise RuntimeError(f'P2 shape {p2["q"].shape} {p2["k"].shape}')
  payload={'p1':p1,'p2':p2};pp=out/'QWEN25_0P5B_P1_P2_QKV.pt';torch.save(payload,pp)
  tensor_ids={n:{z:tsha(x[z]) for z in ('q','k','v')} for n,x in {**p1,'S3_TEXT':p2}.items()};receipt={'status':'MODEL_DERIVED_QKV_EXTRACTED','model_id':'Qwen/Qwen2.5-0.5B-Instruct','revision':MODEL.name,'model_path':str(MODEL),'layer':LAYER,'dtype':'float16','attention':'sdpa','p1_target':'S2_TEXT_DECODE_STEP16','p1_companions':['S2_CODE','S2_STRUCTURED','S2_CODE_ROLL1_DERIVED_CONTROL'],'p1_shapes':{z:list(p1['S2_TEXT'][z].shape) for z in ('q','k','v')},'p2_target':'S3_TEXT_T8192_DECODE_STEP1','p2_history_tokens_used':8192,'p2_shapes':{z:list(p2[z].shape) for z in ('q','k','v')},'input_files':{n:{'path':str(INPUTS[n]),'sha256':EXPECTED[n]} for n in INPUTS},'derived_companion_rule':'S2_CODE token stream cyclic left roll by 1; DERIVED_COMPANION_CONTROL','generated_tokens':gens,'tensor_sha256':tensor_ids,'payload_sha256':fsha(pp),'config_sha256':fsha(MODEL/'config.json'),'model_safetensors_sha256':fsha(MODEL/'model.safetensors'),'accepted_s2_driver_sha256':'824f88b975580288a6a68b6997aa4ce5a611e241c42fd347fc2f59e933faab6c','accepted_s3_driver_sha256':'715cd144995d065a195d79aa39e14297c4405366132243fead67494f6b8329ed','accepted_census_commits':['24f21db0aa921190ca40e4d3969aced7471347b6','0a01aa5de4ab7132ab52d18d689e61b635061ae8'],'torch':torch.__version__,'torch_cuda':torch.version.cuda,'transformers':__import__('transformers').__version__,'gpu':torch.cuda.get_device_name(0)}
  (out/'P2_INPUT_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt,sort_keys=True))
 finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if __name__=='__main__':main()
