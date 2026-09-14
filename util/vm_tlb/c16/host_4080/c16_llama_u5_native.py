#!/usr/bin/env python3
"""C16 U5 RTX4080 native Llama baseline using supplied frozen IDs only."""
import argparse, hashlib, json, os, sys, time
from pathlib import Path

EXPECTED_MODEL="meta-llama/Llama-3.2-1B"; EXPECTED_REV="4e20de362430cd3b72f300e6b0f18e50e7166e08"
EXPECTED_OUTPUT="2c9e006bcd155e56a28d2c9948a31cf2d5bc60e8bb2b5f5af0e1cae35215383f"
EXPECTED_IDS="fc712eb0a158f0fe62231f7826feec3eaabfea51906ca6b1588a55ee81ae3624"

def shab(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--model",type=Path,required=True); ap.add_argument("--ids",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
 if a.output.exists(): raise SystemExit("refusing overwrite")
 assert os.environ.get("CUDA_MODULE_LOADING")=="EAGER" and os.environ.get("CUDA_VISIBLE_DEVICES")=="GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59"
 assert shab(a.ids)==EXPECTED_IDS
 ids=json.loads(a.ids.read_text()); assert isinstance(ids,list) and len(ids)==128 and all(isinstance(x,int) and x>=0 for x in ids)
 import torch
 from transformers import AutoModelForCausalLM
 assert torch.cuda.is_available() and torch.cuda.device_count()==1
 model=AutoModelForCausalLM.from_pretrained(str(a.model),local_files_only=True,torch_dtype=torch.float16,attn_implementation="sdpa",trust_remote_code=False).eval().to("cuda:0")
 assert getattr(model.config,"_attn_implementation",None)=="sdpa"
 assert {p.device.type for p in model.parameters()}=={"cuda"} and {str(p.dtype).removeprefix("torch.") for p in model.parameters()}=={"float16"}
 prompt=torch.tensor([ids],dtype=torch.long,device="cuda:0"); torch.cuda.synchronize(); start=time.perf_counter_ns(); generated=[]
 with torch.inference_mode():
  out=model(input_ids=prompt,use_cache=True); past=out.past_key_values; current=out.logits[:,-1,:].argmax(dim=-1,keepdim=True); generated+=current.detach().cpu().flatten().tolist()
  for _ in range(1,4): out=model(input_ids=current,past_key_values=past,use_cache=True); past=out.past_key_values; current=out.logits[:,-1,:].argmax(dim=-1,keepdim=True); generated+=current.detach().cpu().flatten().tolist()
 torch.cuda.synchronize(); checksum=hashlib.sha256(json.dumps(generated,separators=(",",":")).encode()).hexdigest()
 r={"status":"U5_NATIVE_PASS" if checksum==EXPECTED_OUTPUT else "U5_NATIVE_OUTPUT_CHECKSUM_MISMATCH","model_id":EXPECTED_MODEL,"revision":EXPECTED_REV,"dtype":"float16","attention_backend":"sdpa","prefill_tokens":128,"decode_tokens":4,"generated_token_ids":generated,"output_checksum":checksum,"historical_output_checksum":EXPECTED_OUTPUT,"duration_ms":(time.perf_counter_ns()-start)/1e6,"all_cuda":True,"tokenizer_invoked":False}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n"); print(r["status"]); return 0 if checksum==EXPECTED_OUTPUT else 1
if __name__=="__main__": sys.exit(main())
