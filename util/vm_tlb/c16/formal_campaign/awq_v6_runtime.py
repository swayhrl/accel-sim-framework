#!/usr/bin/env python3
"""Exact local Qwen2.5-7B-AWQ V6 runner; no tokenizer or fallback path."""
import argparse, hashlib, json, time
from pathlib import Path

MODEL=Path('/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641')
TOKENS=Path('/data/c16/inputs/.incoming/qwen2p5_7b_instruct_awq/S2_TEXT/payload/s2_text.json')
TOKEN_FILE_SHA='0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9'
TOKEN_CANONICAL_SHA='745e321e58c94422662576a9f37aae21363867ff9912e513fd08de44b4578cd6'
MODEL_REV='b25037543e9394b818fdfca67ab2a00ecc7dd641'

def main():
 p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True); p.add_argument('--tag',required=True); p.add_argument('--trace-path',type=Path); p.add_argument('--static-map',type=Path); p.add_argument('--target-id'); p.add_argument('--static-index'); p.add_argument('--function-occurrence'); p.add_argument('--address-context-out',type=Path); a=p.parse_args()
 import torch, awq_ext, awq_v2_ext
 from awq import AutoAWQForCausalLM
 raw=TOKENS.read_bytes(); ids=json.loads(raw)
 if hashlib.sha256(raw).hexdigest()!=TOKEN_FILE_SHA or hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest()!=TOKEN_CANONICAL_SHA or len(ids)!=2048: raise RuntimeError('frozen token binding mismatch')
 if not torch.cuda.is_available(): raise RuntimeError('CUDA unavailable; refusing fallback')
 torch.cuda.reset_peak_memory_stats()
 awq=AutoAWQForCausalLM.from_quantized(str(MODEL),max_seq_len=2080,fuse_layers=False,trust_remote_code=False,safetensors=True,device_map={'':0})
 model=awq.model.eval()
 if {x.device.type for x in model.parameters()} != {'cuda'}: raise RuntimeError('non-CUDA parameter / offload forbidden')
 ranges=[]
 for n,t in list(model.named_parameters())+list(model.named_buffers()):
  if getattr(t,'is_cuda',False) and t.numel():
   s=t.untyped_storage(); ptr=int(s.data_ptr()); size=int(s.nbytes())
   if ptr and size: ranges.append({'runtime_name':n,'address_start_hex':hex(ptr),'address_end_hex':hex(ptr+size),'storage_bytes':size,'dtype':str(t.dtype),'shape':list(t.shape),'class':'QUANT_METADATA' if any(k in n.lower() for k in ('scale','zero','g_idx')) else 'WEIGHT'})
 names=[(n,type(m).__module__+'.'+type(m).__name__) for n,m in model.named_modules()]
 fused=[x for x in names if 'WQLinear' in x[1]]
 prompt=torch.tensor([ids],device='cuda:0',dtype=torch.long)
 torch.cuda.synchronize(); start=time.perf_counter()
 with torch.inference_mode():
  torch.cuda.nvtx.range_push('C16_AWQ_V6_FULL_S2')
  torch.cuda.nvtx.range_push('C16_AWQ_V6_PREFILL')
  out=model(input_ids=prompt,use_cache=True)
  torch.cuda.nvtx.range_pop()
  past=out.past_key_values; cur=out.logits[:,-1,:].argmax(-1,keepdim=True); generated=[int(cur.item())]
  torch.cuda.nvtx.range_push('C16_AWQ_V6_DECODE')
  for step in range(1,32):
   torch.cuda.nvtx.range_push('C16_AWQ_V6_DECODE_STEP_'+str(step))
   out=model(input_ids=cur,past_key_values=past,use_cache=True)
   torch.cuda.nvtx.range_pop(); past=out.past_key_values; cur=out.logits[:,-1,:].argmax(-1,keepdim=True); generated.append(int(cur.item()))
  torch.cuda.nvtx.range_pop(); torch.cuda.nvtx.range_pop()
 torch.cuda.synchronize()
 payload={'schema':'C16_V6_AWQ_EXACT_RUNTIME_V1','status':'PASS','tag':a.tag,'model_id':'Qwen/Qwen2.5-7B-Instruct-AWQ','model_revision':MODEL_REV,'scenario':'S2_TEXT_B1_T2048_D32','token_file_sha256':TOKEN_FILE_SHA,'token_canonical_sha256':TOKEN_CANONICAL_SHA,'fuse_layers_argument':False,'quantization_implementation':'AUTOAWQ_FROM_QUANTIZED_WITH_BUILT_AWQ_EXT','awq_ext_file':awq_ext.__file__,'awq_v2_ext_file':awq_v2_ext.__file__,'fused_wqlinear_module_count':len(fused),'fused_wqlinear_module_examples':fused[:8],'generated_tokens':generated,'output_checksum':hashlib.sha256(json.dumps(generated,separators=(',',':')).encode()).hexdigest(),'elapsed_seconds':time.perf_counter()-start,'peak_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_reserved_bytes':torch.cuda.max_memory_reserved(),'torch':torch.__version__,'cuda':torch.version.cuda,'gpu_name':torch.cuda.get_device_properties(0).name}
 if a.address_context_out is not None:
  if not (a.trace_path and a.trace_path.is_file() and a.static_map and a.static_map.is_file() and a.target_id and a.static_index is not None and a.function_occurrence is not None): raise RuntimeError('same-process context requires completed trace/static target identity')
  def h(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
  gpu=torch.cuda.get_device_properties(0).name
  ctx={'schema_version':'C16_ADDRESS_CONTEXT_V1','address_space_id':hashlib.sha256((str(time.time_ns())+a.target_id).encode()).hexdigest(),'gpu_name':gpu,'target_id':a.target_id,'static_index':a.static_index,'function_occurrence':a.function_occurrence,'model_id':payload['model_id'],'revision':MODEL_REV,'scenario':'S2_TEXT','trace_path':str(a.trace_path),'trace_sha256':h(a.trace_path),'static_map_path':str(a.static_map),'static_map_sha256':h(a.static_map),'ranges':ranges,'binding_token_sha256':TOKEN_CANONICAL_SHA,'same_process_only':True}
  a.address_context_out.parent.mkdir(parents=True,exist_ok=True); a.address_context_out.write_text(json.dumps(ctx,indent=2,sort_keys=True)+'\n'); payload['address_context_path']=str(a.address_context_out); payload['address_context_sha256']=h(a.address_context_out)
 a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n'); print(json.dumps(payload,sort_keys=True))
if __name__=='__main__': main()
