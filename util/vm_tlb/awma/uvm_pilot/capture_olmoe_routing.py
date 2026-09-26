#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer
MODEL=Path('/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e')
OUT=Path('/data/c16/awma/uvm_model_derived_characterization_20260926/routing');OUT.mkdir(parents=True,exist_ok=False)
TEXT=("Virtual memory systems translate program-visible addresses into physical storage while modern AI workloads exercise attention, dense matrix operations, routing, expert computation, reductions, and irregular data movement. This frozen paragraph is repeated only to create a deterministic bounded native workload. ")*64
tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True,trust_remote_code=False);ids=tok(TEXT,add_special_tokens=True,return_tensors='pt')['input_ids'][:,:256].to('cuda:0')
model=AutoModelForCausalLM.from_pretrained(MODEL,local_files_only=True,trust_remote_code=False,torch_dtype=torch.bfloat16,attn_implementation='sdpa').eval().to('cuda:0');topk=int(getattr(model.config,'num_experts_per_tok',8));events=[]
def record(logits,phase,base_token,step):
 for layer,x in enumerate(logits):
  z=torch.topk(x.detach().float(),topk,dim=-1).indices.cpu().tolist()
  for i,e in enumerate(z):events.append({'event_index':len(events),'phase':phase,'decode_step':step,'token_index':base_token+i,'layer':layer,'top_k':topk,'expert_ids':e})
with torch.inference_mode():
 out=model(input_ids=ids,use_cache=True,output_router_logits=True,return_dict=True);record(out.router_logits,'PREFILL',0,0);past=out.past_key_values;token=out.logits[:,-1,:].argmax(-1);generated=[]
 for step in range(1,9):
  generated.append(int(token.item()));out=model(input_ids=token[:,None],past_key_values=past,use_cache=True,output_router_logits=True,return_dict=True);record(out.router_logits,'DECODE',255+step,step);past=out.past_key_values;token=out.logits[:,-1,:].argmax(-1)
torch.cuda.synchronize();trace=OUT/'ROUTE_TRACE.jsonl';trace.write_text(''.join(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n' for x in events));receipt={'status':'OLMOE_READ_ONLY_ROUTING_CAPTURE_COMPLETE','model':'allenai/OLMoE-1B-7B-0125-Instruct','revision':MODEL.name,'scenario':'B1_T256_D8_BF16_SDPA','text_sha256':hashlib.sha256(TEXT.encode()).hexdigest(),'token_ids_sha256':hashlib.sha256(json.dumps(ids.cpu().tolist(),separators=(',',':')).encode()).hexdigest(),'route_trace_sha256':hashlib.sha256(trace.read_bytes()).hexdigest(),'event_count':len(events),'layers':len(out.router_logits),'top_k':topk,'generated':generated}
(OUT/'ROUTING_CAPTURE_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt,sort_keys=True))
