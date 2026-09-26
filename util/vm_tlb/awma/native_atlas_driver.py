#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer

TEXT=("Virtual memory systems translate program-visible addresses into physical storage while modern AI workloads "
      "exercise attention, dense matrix operations, routing, expert computation, reductions, and irregular data movement. "
      "This frozen paragraph is repeated only to create a deterministic bounded native workload. ")*64

def main():
 p=argparse.ArgumentParser(); p.add_argument('--model',type=Path,required=True); p.add_argument('--model-id',required=True); p.add_argument('--revision',required=True); p.add_argument('--scenario',required=True); p.add_argument('--prompt-tokens',type=int,default=256); p.add_argument('--decode-tokens',type=int,default=8); a=p.parse_args()
 torch.manual_seed(0)
 tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True,trust_remote_code=False)
 ids=tok(TEXT,add_special_tokens=True,return_tensors='pt')['input_ids'][0]
 if len(ids)<a.prompt_tokens: raise SystemExit('frozen text tokenization too short')
 ids=ids[:a.prompt_tokens].unsqueeze(0).to('cuda:0')
 model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,trust_remote_code=False,torch_dtype=torch.bfloat16,attn_implementation='sdpa').eval().to('cuda:0')
 def run(mark):
  with torch.inference_mode():
   if mark: torch.cuda.nvtx.range_push(f'ATLAS_PHASE=PREFILL;SCENARIO={a.scenario};B=1;T={a.prompt_tokens};D={a.decode_tokens}')
   out=model(input_ids=ids,use_cache=True)
   if mark: torch.cuda.nvtx.range_pop()
   past=out.past_key_values; token=out.logits[:,-1,:].argmax(-1); gen=[]
   for step in range(1,a.decode_tokens+1):
    if mark: torch.cuda.nvtx.range_push(f'ATLAS_PHASE=DECODE;STEP={step};SCENARIO={a.scenario};B=1;T=1')
    gen.append(int(token.item())); out=model(input_ids=token[:,None],past_key_values=past,use_cache=True)
    if mark: torch.cuda.nvtx.range_pop()
    past=out.past_key_values; token=out.logits[:,-1,:].argmax(-1)
   torch.cuda.synchronize(); return gen
 warm=run(False); auth=run(True)
 receipt={'status':'ATLAS_NATIVE_SCENARIO_COMPLETE','scenario':a.scenario,'model_id':a.model_id,'revision':a.revision,'batch':1,'prompt_tokens':a.prompt_tokens,'decode_tokens':a.decode_tokens,'dtype':'bfloat16','quantization':'NONE','attention':'sdpa','text_sha256':hashlib.sha256(TEXT.encode()).hexdigest(),'token_ids_sha256':hashlib.sha256(json.dumps(ids.cpu().tolist(),separators=(',',':')).encode()).hexdigest(),'warmup_generated':warm,'authoritative_generated':auth,'torch':torch.__version__,'torch_cuda':torch.version.cuda}
 print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__': main()
