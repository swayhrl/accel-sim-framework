#!/usr/bin/env python3
from __future__ import annotations
import argparse,fcntl,hashlib,json,sys,time,types
from pathlib import Path
ROOT=Path('/data/c16/awma/r53_online_workset_qualification_20260927');MODEL=ROOT/'model/Fast_dLLM_v2_1.5B_25093b6f';SRC=ROOT/'source/Fast-dLLM/v2';sys.path.insert(0,str(SRC))
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer
import generation_functions
def tsha(t):return hashlib.sha256(t.detach().contiguous().view(torch.uint8).cpu().numpy().tobytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--batch',type=int,required=True);p.add_argument('--short',action='store_true');a=p.parse_args();req=json.loads((ROOT/'selected_requests.json').read_text())['GSM8K'][:a.batch];lock=open('/data/c16/locks/c16_gpu_campaign.lock','a+');fcntl.flock(lock,fcntl.LOCK_EX)
 try:
  torch.manual_seed(0);torch.cuda.set_device(0);tok=AutoTokenizer.from_pretrained(MODEL,trust_remote_code=True,local_files_only=True);model=AutoModelForCausalLM.from_pretrained(MODEL,trust_remote_code=True,local_files_only=True,torch_dtype=torch.bfloat16).eval().to('cuda:0');model.mdm_sample=types.MethodType(generation_functions.Fast_dLLM_QwenForCausalLM.batch_sample,model);calls={'total':0,'block_cache':0,'full_refresh':0,'reuse':0};orig=model.forward
  def wrapped(*args,**kwargs):
   calls['total']+=1
   if kwargs.get('use_block_cache'):calls['block_cache']+=1;calls['reuse' if kwargs.get('block_past_key_values') is not None else 'full_refresh']+=1
   return orig(*args,**kwargs)
  model.forward=wrapped
  ids=[torch.tensor([x['token_ids_json'] and json.loads(x['token_ids_json'])],dtype=torch.long,device='cuda') for x in req];lens=torch.tensor([x.shape[1] for x in ids],device='cuda');mx=max(x.shape[1] for x in ids);mask=151665;batch=torch.cat([torch.cat([x,torch.full((1,mx-x.shape[1]),mask,dtype=torch.long,device='cuda')],1) for x in ids],0);torch.cuda.reset_peak_memory_stats();t=time.perf_counter();out=model.mdm_sample(batch,tokenizer=tok,block_size=32,max_new_tokens=32 if a.short else 512,small_block_size=8,min_len=int(lens.min()),seq_len=lens,mask_id=mask,threshold=.9,stop_token=151645,use_block_cache=True,top_p=.95,temperature=0.0);torch.cuda.synchronize();wall=time.perf_counter()-t
  rows=[]
  for i in range(a.batch):z=out[i].cpu();rows.append({'request_id':req[i]['canonical_id'],'output_tokens':int(z.numel()),'output_sha256':tsha(z),'contains_mask':bool((z==mask).any()),'contains_stop':bool((z==151645).any())})
  r={'status':'CANARY_PASS','batch':a.batch,'short':a.short,'max_new_tokens':32 if a.short else 512,'wall_seconds':wall,'peak_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_reserved_bytes':torch.cuda.max_memory_reserved(),'forward_calls':calls,'outputs':rows,'policy':{'dtype':'bfloat16','block_size':32,'small_block_size':8,'threshold':.9,'temperature':0.0,'top_p':.95,'use_block_cache':True},'gpu':torch.cuda.get_device_name(0),'oom':False,'offload':False};path=ROOT/('B1_SHORT_CANARY.json' if a.short else f'B{a.batch}_RESOURCE_CANARY.json');path.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(r,sort_keys=True))
 except torch.OutOfMemoryError as e:
  r={'status':'OOM','batch':a.batch,'short':a.short,'oom':True,'error':str(e)};(ROOT/f'B{a.batch}_RESOURCE_CANARY.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(r));raise SystemExit(3)
 finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if __name__=='__main__':main()
