from __future__ import annotations
import fcntl,json,os
from pathlib import Path
ROOT=Path('/data/c16/awma/r54_checkpoint_lifecycle_20260927');MODEL=ROOT/'model/Qwen3_5_0_8B_c6046cd1';LOCK='/data/c16/locks/c16_gpu_campaign.lock'
def main():
 import torch
 from transformers import AutoTokenizer,Qwen3_5ForConditionalGeneration
 lock=open(LOCK,'a+');fcntl.flock(lock,fcntl.LOCK_EX)
 try:
  torch.cuda.set_device(0);tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True);model=Qwen3_5ForConditionalGeneration.from_pretrained(MODEL,local_files_only=True,torch_dtype=torch.bfloat16).eval().to('cuda:0');ids=tok('Exact recurrent checkpoint qualification uses a bounded text-only prefix fixture. '*8,return_tensors='pt',add_special_tokens=False)['input_ids'][:,:64].cuda();torch.cuda.nvtx.range_push('R54_FASTPATH_CANARY=PREFILL64');o=model(input_ids=ids,use_cache=True,return_dict=True);torch.cuda.nvtx.range_pop();torch.cuda.synchronize();r={'status':'CANARY_PASS','input_shape':list(ids.shape),'logits_shape':list(o.logits.shape),'past_type':type(o.past_key_values).__name__,'past_len':len(o.past_key_values) if o.past_key_values is not None else 0,'gpu':torch.cuda.get_device_name(0),'torch':torch.__version__};(ROOT/'R54_FASTPATH_CANARY_RECEIPT.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(r,sort_keys=True))
 finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if __name__=='__main__':main()
