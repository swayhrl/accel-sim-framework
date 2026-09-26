#!/usr/bin/env python3
from __future__ import annotations
import fcntl,hashlib,json,shutil
from pathlib import Path
import torch
import torch.nn.functional as F
from torch.nn.attention import sdpa_kernel,SDPBackend
from transformers import AutoModelForCausalLM

ROOT=Path('/data/c16/awma/r51_r52_lifecycle_qualification_20260926');MODEL=Path('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775');TOKENS=Path('/data/c16/inputs/.incoming/qwen2p5_0p5b_instruct/S2_TEXT/payload/TEXT_S2_T2048_token_ids.json');PRIOR=Path('/data/c16/awma/p1_p2_native_qualification_20260926');LOCK=Path('/data/c16/locks/c16_gpu_campaign.lock');ACCEPTED=[23578,11,323,3950,28360,1969,7146,6822,198,983,279,51572,1614,23578,12433,553]
def fsha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def tsha(t):return hashlib.sha256(t.detach().contiguous().view(torch.uint8).cpu().numpy().tobytes()).hexdigest()
def main():
 out=ROOT/'input';out.mkdir(parents=True,exist_ok=False)
 if fsha(TOKENS)!='0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9':raise RuntimeError('S2 token authority mismatch')
 prior_payload=PRIOR/'input/QWEN25_0P5B_P1_P2_QKV.pt';prior_ref=PRIOR/'runs/P1_STOCK_FLASH_SDPA_B1/target_output.pt';pp=torch.load(prior_payload,map_location='cpu',weights_only=True);fg=pp['p1']['S2_TEXT'];fg_ref=torch.load(prior_ref,map_location='cpu',weights_only=True);fg_ref=fg_ref.unsqueeze(0) if fg_ref.ndim==3 else fg_ref
 lock=open(LOCK,'a+');fcntl.flock(lock,fcntl.LOCK_EX)
 try:
  torch.manual_seed(0);torch.cuda.set_device(0);model=AutoModelForCausalLM.from_pretrained(MODEL,local_files_only=True,trust_remote_code=False,torch_dtype=torch.float16,attn_implementation='sdpa').eval().to('cuda:0');ids=torch.tensor([json.loads(TOKENS.read_text())],dtype=torch.long,device='cuda')
  with torch.inference_mode():
   z=model.model(input_ids=ids,use_cache=True,return_dict=True);token=model.lm_head(z.last_hidden_state[:,-1,:]).argmax(-1);past=z.past_key_values;generated=[]
   for step in range(1,16):
    generated.append(int(token.item()));z=model.model(input_ids=token[:,None],past_key_values=past,use_cache=True,return_dict=True);past=z.past_key_values;token=model.lm_head(z.last_hidden_state[:,-1,:]).argmax(-1)
   captured={}
   def pre(mod,args):captured['hidden']=args[0].detach().clone()
   def post(mod,args,o):captured['output']=o.detach().clone()
   emb=model.get_output_embeddings();ha=emb.register_forward_pre_hook(pre);hb=emb.register_forward_hook(post);generated.append(int(token.item()));torch.cuda.nvtx.range_push('R51_TARGET_CAPTURE=LM_HEAD;SCENARIO=S2_TEXT;STEP=16');full=model(input_ids=token[:,None],past_key_values=past,use_cache=True,return_dict=True);torch.cuda.nvtx.range_pop();torch.cuda.synchronize();ha.remove();hb.remove()
   hidden=captured['hidden'].reshape(1,-1);ref=captured['output'].reshape(1,-1);weight=emb.weight.detach();replay=F.linear(hidden,weight)
   if not torch.equal(ref,replay):raise RuntimeError(f'lm_head replay mismatch max={float((ref-replay).abs().max())}')
   q=fg['q'].cuda();groups=q.shape[1]//fg['k'].shape[1];k=fg['k'].cuda().repeat_interleave(groups,dim=1).contiguous();v=fg['v'].cuda().repeat_interleave(groups,dim=1).contiguous()
   with sdpa_kernel(SDPBackend.FLASH_ATTENTION):fg_out=F.scaled_dot_product_attention(q,k,v,dropout_p=0.0,is_causal=False)
   if not torch.equal(fg_out.cpu(),fg_ref):raise RuntimeError('foreground accepted output mismatch')
  if generated!=ACCEPTED:raise RuntimeError(f'accepted decode sequence mismatch {generated}')
  payload={'background_hidden':hidden.cpu().contiguous(),'background_weight':weight.cpu().contiguous(),'background_reference':ref.cpu().contiguous(),'foreground_q':fg['q'].contiguous(),'foreground_k':k.cpu().contiguous(),'foreground_v':v.cpu().contiguous(),'foreground_reference':fg_ref.contiguous()};target=out/'R51_TARGET_PAYLOAD.pt';torch.save(payload,target)
  receipt={'status':'R51_TARGET_IDENTITIES_CLOSED','background_role':'LM_HEAD_BACKGROUND','semantic_binding':'hook on model.get_output_embeddings() during accepted S2 decode step16','model':'Qwen/Qwen2.5-0.5B-Instruct','revision':MODEL.name,'input_sha256':fsha(TOKENS),'decode_step':16,'generated_tokens':generated,'background_hidden_shape':list(hidden.shape),'background_weight_shape':list(weight.shape),'background_output_shape':list(ref.shape),'background_hidden_sha256':tsha(hidden),'background_weight_sha256':tsha(weight),'background_output_sha256':tsha(ref),'background_replay_bitwise':True,'foreground_role':'P1_ACCEPTED_LAYER12_FLASH_SDPA_B1','foreground_q_shape':list(fg['q'].shape),'foreground_k_shape':list(k.shape),'foreground_v_shape':list(v.shape),'foreground_q_sha256':tsha(fg['q']),'foreground_k_sha256':tsha(k),'foreground_v_sha256':tsha(v),'foreground_output_sha256':tsha(fg_ref),'foreground_replay_bitwise':True,'prior_payload_path':str(prior_payload),'prior_payload_sha256':fsha(prior_payload),'prior_reference_sha256':fsha(prior_ref),'payload_sha256':fsha(target),'model_config_sha256':fsha(MODEL/'config.json'),'model_safetensors_sha256':fsha(MODEL/'model.safetensors'),'torch':torch.__version__,'torch_cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0)};(ROOT/'TARGET_IDENTITY_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt,sort_keys=True))
 finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if __name__=='__main__':main()
