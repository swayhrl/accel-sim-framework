#!/usr/bin/env python3
import argparse, hashlib, json, os, statistics, sys, time
from pathlib import Path

MODEL="meta-llama/Llama-3.2-1B"; REV="4e20de362430cd3b72f300e6b0f18e50e7166e08"; OUT="2c9e006bcd155e56a28d2c9948a31cf2d5bc60e8bb2b5f5af0e1cae35215383f"; IDS="fc712eb0a158f0fe62231f7826feec3eaabfea51906ca6b1588a55ee81ae3624"
def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def run(model,prompt,torch):
 torch.cuda.synchronize(); t=time.perf_counter_ns(); gs=[]
 with torch.inference_mode():
  o=model(input_ids=prompt,use_cache=True); past=o.past_key_values; cur=o.logits[:,-1,:].argmax(-1,keepdim=True); gs.append(cur)
  for _ in range(1,4): o=model(input_ids=cur,past_key_values=past,use_cache=True); past=o.past_key_values; cur=o.logits[:,-1,:].argmax(-1,keepdim=True); gs.append(cur)
 torch.cuda.synchronize(); ms=(time.perf_counter_ns()-t)/1e6; ids=torch.cat(gs,dim=1).detach().cpu().flatten().tolist(); return ms,hashlib.sha256(json.dumps(ids,separators=(",",":")).encode()).hexdigest(),ids
def main():
 p=argparse.ArgumentParser(); p.add_argument('--model',type=Path,required=True); p.add_argument('--ids',type=Path,required=True); p.add_argument('--u4-receipt',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
 if a.output.exists(): raise RuntimeError('overwrite refused')
 if os.environ.get('CUDA_MODULE_LOADING')!='EAGER' or os.environ.get('CUDA_VISIBLE_DEVICES')!='GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59': raise RuntimeError('env identity')
 if sha(a.ids)!=IDS: raise RuntimeError('frozen IDs hash')
 u4=json.loads(a.u4_receipt.read_text());
 if u4.get('status')!='U4_LOCAL_ASSET_EXACT_CLOSURE_PASS' or Path(u4.get('promoted_to',''))!=a.model: raise RuntimeError('U4 binding')
 ids=json.loads(a.ids.read_text());
 if not isinstance(ids,list) or len(ids)!=128: raise RuntimeError('IDs shape')
 import torch
 from transformers import AutoModelForCausalLM
 if not torch.cuda.is_available() or torch.cuda.device_count()!=1: raise RuntimeError('CUDA')
 model=AutoModelForCausalLM.from_pretrained(str(a.model),local_files_only=True,torch_dtype=torch.float16,attn_implementation='sdpa',trust_remote_code=False).eval().to('cuda:0')
 if getattr(model.config,'_attn_implementation',None)!='sdpa' or {x.device.type for x in model.parameters()}!={'cuda'} or {str(x.dtype).removeprefix('torch.') for x in model.parameters()}!={'float16'}: raise RuntimeError('runtime binding')
 prompt=torch.tensor([ids],dtype=torch.long,device='cuda:0'); warm=run(model,prompt,torch)
 if warm[1]!=OUT: raise RuntimeError('warmup checksum')
 reps=[run(model,prompt,torch) for _ in range(5)]
 if any(x[1]!=OUT for x in reps): raise RuntimeError('repetition checksum')
 d=[x[0] for x in reps]; r={'status':'R5_U5_CLEAN_PASS','warmup_ms':warm[0],'durations_ms':d,'median_ms':statistics.median(d),'min_ms':min(d),'max_ms':max(d),'output_checksum':OUT,'generated_token_ids':reps[0][2],'u4_receipt_sha256':sha(a.u4_receipt),'frozen_ids_sha256':sha(a.ids),'tokenizer_invoked':False}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n'); print(r['status'])
if __name__=='__main__': main()
