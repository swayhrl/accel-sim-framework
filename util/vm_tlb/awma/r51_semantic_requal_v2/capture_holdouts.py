#!/usr/bin/env python3
from __future__ import annotations
import fcntl,hashlib,json
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM
ROOT=Path('/data/c16/awma/r51_semantic_requal_v2_20260926');V1=Path('/data/c16/awma/r51_r52_lifecycle_qualification_20260926');MODEL=Path('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775');TOKENS=Path('/data/c16/inputs/.incoming/qwen2p5_0p5b_instruct/S2_TEXT/payload/TEXT_S2_T2048_token_ids.json');LOCK='/data/c16/locks/c16_gpu_campaign.lock';ACCEPTED=[23578,11,323,3950,28360,1969,7146,6822,198,983,279,51572,1614,23578,12433,553,21272,362,624,34,16,21,93377,419]
def fsha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def tsha(t):return hashlib.sha256(t.detach().contiguous().view(torch.uint8).cpu().numpy().tobytes()).hexdigest()
def main():
 out=ROOT/'input';out.mkdir(parents=True,exist_ok=False);v1p=V1/'input/R51_TARGET_PAYLOAD.pt';v1=torch.load(v1p,map_location='cpu',weights_only=True);states={16:{'hidden':v1['background_hidden'],'reference':v1['background_reference'],'source':'V1_ACCEPTED'}}
 lock=open(LOCK,'a+');fcntl.flock(lock,fcntl.LOCK_EX)
 try:
  torch.manual_seed(0);torch.cuda.set_device(0);model=AutoModelForCausalLM.from_pretrained(MODEL,local_files_only=True,trust_remote_code=False,torch_dtype=torch.float16,attn_implementation='sdpa').eval().to('cuda:0');ids=torch.tensor([json.loads(TOKENS.read_text())],dtype=torch.long,device='cuda')
  with torch.inference_mode():
   z=model.model(input_ids=ids,use_cache=True,return_dict=True);token=model.lm_head(z.last_hidden_state[:,-1,:]).argmax(-1);past=z.past_key_values;generated=[]
   for step in range(1,25):
    generated.append(int(token.item()));z=model.model(input_ids=token[:,None],past_key_values=past,use_cache=True,return_dict=True);past=z.past_key_values;hidden=z.last_hidden_state.reshape(1,-1);logits=model.lm_head(hidden);token=logits.argmax(-1)
    if step in (8,24):states[step]={'hidden':hidden.cpu().contiguous(),'reference':logits.cpu().contiguous(),'source':'V2_HOLDOUT_CAPTURE'}
  torch.cuda.synchronize()
  if generated!=ACCEPTED:raise RuntimeError(f'trajectory mismatch {generated}')
  if tsha(states[16]['hidden'])!='bfa3c6e9c98d026dcd31ae2f363986d5e0fc0607c5f93ca4146a269b910818de' or tsha(states[16]['reference'])!='ca22d8289c455bdf2f4bc2c02e5ee1404096aa77e37446ca59a0d0148f0072fb':raise RuntimeError('V1 primary authority mismatch')
  payload={'states':states};pp=out/'R51_V2_SEMANTIC_STATES.pt';torch.save(payload,pp);receipt={'status':'R51_V2_HOLDOUT_STATES_CLOSED','model':'Qwen/Qwen2.5-0.5B-Instruct','revision':MODEL.name,'input_sha256':fsha(TOKENS),'trajectory_tokens_1_to_24':generated,'states':{str(s):{'source':x['source'],'hidden_shape':list(x['hidden'].shape),'hidden_sha256':tsha(x['hidden']),'reference_shape':list(x['reference'].shape),'reference_dtype':str(x['reference'].dtype),'reference_sha256':tsha(x['reference']),'argmax_token_id':int(x['reference'].argmax(-1).item()),'top8_token_ids':sorted(torch.topk(x['reference'].float(),8,dim=-1).indices[0].tolist()),'top1_top2_order':torch.topk(x['reference'].float(),2,dim=-1).indices[0].tolist()} for s,x in states.items()},'v1_payload_path':str(v1p),'v1_payload_sha256':fsha(v1p),'weight_sha256':'d74257dc547b48be5ae7b93f1c9af072c0c42dbbb85503078e25c59cd09e68d0','payload_sha256':fsha(pp),'torch':torch.__version__,'torch_cuda':torch.version.cuda};(ROOT/'HOLDOUT_STATE_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt,sort_keys=True))
 finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if __name__=='__main__':main()
