import argparse,hashlib,json,time
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--tokens',type=Path,required=True);p.add_argument('--batch',type=int,required=True)
p.add_argument('--decode',type=int,required=True);p.add_argument('--scenario',required=True);p.add_argument('--out',type=Path,required=True)
a=p.parse_args(); ids=json.loads(a.tokens.read_text()); assert isinstance(ids,list)
import torch
from awq import AutoAWQForCausalLM
model=AutoAWQForCausalLM.from_quantized('/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641',max_seq_len=len(ids)+a.decode,fuse_layers=False,trust_remote_code=False,safetensors=True,device_map={'':0}).model.eval()
if {x.device.type for x in model.parameters()}!={'cuda'}: raise RuntimeError('CPU/offload forbidden')
x=torch.tensor([ids]*a.batch,device='cuda');torch.cuda.reset_peak_memory_stats();torch.cuda.synchronize();t=time.perf_counter()
with torch.inference_mode():
 torch.cuda.nvtx.range_push('C16_V7_'+a.scenario+'_PREFILL');o=model(input_ids=x,use_cache=True);torch.cuda.nvtx.range_pop();pref=time.perf_counter()-t;past=o.past_key_values;cur=o.logits[:,-1,:].argmax(-1,keepdim=True);out=[];d0=time.perf_counter();torch.cuda.nvtx.range_push('C16_V7_'+a.scenario+'_DECODE')
 for _ in range(a.decode):
  o=model(input_ids=cur,past_key_values=past,use_cache=True);past=o.past_key_values;cur=o.logits[:,-1,:].argmax(-1,keepdim=True);out+=cur.cpu().flatten().tolist()
 torch.cuda.nvtx.range_pop()
torch.cuda.synchronize()
q={'scenario':a.scenario,'tokens':len(ids),'batch':a.batch,'decode':a.decode,'token_file_sha256':hashlib.sha256(a.tokens.read_bytes()).hexdigest(),'output_checksum':hashlib.sha256(json.dumps(out,separators=(',',':')).encode()).hexdigest(),'prefill_seconds':pref,'decode_seconds':time.perf_counter()-d0,'peak_allocated':torch.cuda.max_memory_allocated(),'peak_reserved':torch.cuda.max_memory_reserved(),'wqlinear_count':sum('WQLinear' in type(m).__name__ for m in model.modules()),'attention':str(getattr(model.config,'_attn_implementation','UNRESOLVED')),'status':'PASS'}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
