#!/usr/bin/env python3
"""Exact frozen Q05 S2 workload driver for simulator-native tracer only."""
import hashlib,json,os,sys
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM

MODEL=Path('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775')
TOKENS=Path('/data/c16/inputs/.incoming/qwen2p5_0p5b_instruct/S2_TEXT/payload/TEXT_S2_T2048_token_ids.json')
EXPECTED='0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(TOKENS)!=EXPECTED:raise SystemExit('frozen token authority mismatch')
ids=json.loads(TOKENS.read_text())
if not isinstance(ids,list) or len(ids)!=2048:raise SystemExit('S2 exact token cardinality mismatch')
torch.manual_seed(0)
model=AutoModelForCausalLM.from_pretrained(str(MODEL),local_files_only=True,torch_dtype=torch.float16,attn_implementation='sdpa',trust_remote_code=False).eval().to('cuda:0')
with torch.inference_mode():
 out=model(input_ids=torch.tensor([ids],dtype=torch.long,device='cuda'),use_cache=True)
 token=int(out.logits[:,-1,:].argmax(dim=-1).item()); past=out.past_key_values; generated=[]
 for _ in range(32):
  generated.append(token); out=model(input_ids=torch.tensor([[token]],dtype=torch.long,device='cuda'),past_key_values=past,use_cache=True);past=out.past_key_values;token=int(out.logits[:,-1,:].argmax(dim=-1).item())
torch.cuda.synchronize()
print(json.dumps({'status':'EXACT_Q05_S2_EXECUTION_COMPLETE','model_id':'Qwen/Qwen2.5-0.5B-Instruct','revision':'7ae557604adf67be50417f59c2c2f167def9a775','backend':'sdpa','dtype':'float16','prefill_tokens':2048,'decode_tokens':32,'token_ids_sha256':sha(TOKENS),'generated_tokens':generated},sort_keys=True))
