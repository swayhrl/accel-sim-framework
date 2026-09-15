#!/usr/bin/env python3
"""Exact frozen-binding runtime for C16 formal capture object-map closure."""
import argparse, hashlib, json, os, platform, socket, sys, time, subprocess
from pathlib import Path

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b)
 return h.hexdigest()
def add_storage(rows, seen, tensor, name, cls, stage, layer='UNKNOWN'):
 if not hasattr(tensor,'untyped_storage') or not getattr(tensor,'is_cuda',False): return
 s=tensor.untyped_storage(); ptr=int(s.data_ptr()); n=int(s.nbytes())
 if not ptr or not n:return
 key=(ptr,n,cls,stage)
 if key not in seen:
  rows.append({'address_start_hex':hex(ptr),'address_end_hex':hex(ptr+n),'storage_bytes':n,'class':cls,'runtime_name':name,'dtype':str(tensor.dtype),'shape':list(tensor.shape),'stage':stage,'layer':layer,'alias_group':f'{ptr:x}:{n}'})
  seen.add(key)
def walk_cache(x, rows, seen, stage, path='past_key_values'):
 if hasattr(x,'is_cuda'): add_storage(rows,seen,x,path,'KV_CACHE',stage)
 elif isinstance(x,(tuple,list)):
  for i,y in enumerate(x): walk_cache(y,rows,seen,stage,f'{path}[{i}]')
 elif hasattr(x,'key_cache'):
  walk_cache(x.key_cache,rows,seen,stage,path+'.key_cache');walk_cache(x.value_cache,rows,seen,stage,path+'.value_cache')
def main():
 a=argparse.ArgumentParser();a.add_argument('--deployment',required=True,choices=['qwen05','qwen7awq','llama']);a.add_argument('--token-ids',type=Path,required=True);a.add_argument('--object-map-out',type=Path,required=True);a.add_argument('--receipt-out',type=Path,required=True);a.add_argument('--decode-steps',type=int,required=True);a.add_argument('--address-context-out',type=Path);a.add_argument('--trace-path',type=Path);a.add_argument('--target-id');a.add_argument('--static-index');a.add_argument('--function-occurrence');a.add_argument('--static-map',type=Path);x=a.parse_args()
 spec={'qwen05':('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775','float16','TRANSFORMERS_SDPA','Qwen/Qwen2.5-0.5B-Instruct','7ae557604adf67be50417f59c2c2f167def9a775'),'qwen7awq':('/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641','float16','AUTOAWQ_UNFUSED','Qwen/Qwen2.5-7B-Instruct-AWQ','b25037543e9394b818fdfca67ab2a00ecc7dd641'),'llama':('/data/c16/models/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08','float16','TRANSFORMERS_SDPA','meta-llama/Llama-3.2-1B','4e20de362430cd3b72f300e6b0f18e50e7166e08')}[x.deployment]
 import torch
 if x.deployment=='qwen7awq':
  from awq import AutoAWQForCausalLM
  model=AutoAWQForCausalLM.from_quantized(spec[0],max_seq_len=32768,trust_remote_code=False,fuse_layers=True,use_exllama=False,device_map={'':0}); root=model.model
 else:
  from transformers import AutoModelForCausalLM
  model=AutoModelForCausalLM.from_pretrained(spec[0],local_files_only=True,torch_dtype=torch.float16,trust_remote_code=False);model.eval().to('cuda');root=model
 if x.deployment=='qwen7awq': model.eval()
 ids=json.loads(x.token_ids.read_text()); assert isinstance(ids,list) and ids and all(isinstance(v,int) for v in ids)
 torch.cuda.reset_peak_memory_stats(); rows=[];seen=set()
 for n,t in list(root.named_parameters())+list(root.named_buffers()):
  cls='WEIGHT'
  if x.deployment=='qwen7awq' and any(k in n.lower() for k in ('scales','qzeros','g_idx','zero_point')): cls='QUANT_METADATA'
  add_storage(rows,seen,t,n,cls,'MODEL_LOADED',n.split('.')[1] if n.startswith('model.layers.') else 'MODEL')
 inp=torch.tensor([ids],device='cuda'); started=time.monotonic()
 with torch.inference_mode():
  out=model(input_ids=inp,use_cache=True); torch.cuda.synchronize(); walk_cache(out.past_key_values,rows,seen,'PREFILL_COMPLETE')
  generated=[]; nxt=out.logits[:,-1,:].argmax(-1,keepdim=True)
  for step in range(1,x.decode_steps+1):
   generated.append(int(nxt.item())); out=model(input_ids=nxt,past_key_values=out.past_key_values,use_cache=True); torch.cuda.synchronize(); nxt=out.logits[:,-1,:].argmax(-1,keepdim=True)
   if step in (1,x.decode_steps): walk_cache(out.past_key_values,rows,seen,f'DECODE_{step}')
 result={'schema_version':'C16_FORMAL_RUNTIME_RECEIPT_V1','status':'PASS','deployment':x.deployment,'model_id':spec[3],'revision':spec[4],'model_path':spec[0],'token_ids_path':str(x.token_ids),'token_ids_sha256':sha(x.token_ids),'token_count':len(ids),'decode_steps':x.decode_steps,'dtype':'float16','attention_backend':getattr(root.config,'_attn_implementation',spec[2]),'implementation':spec[2],'output_tokens':generated,'output_checksum':hashlib.sha256(json.dumps(generated,separators=(',',':')).encode()).hexdigest(),'object_map_path':str(x.object_map_out),'peak_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_reserved_bytes':torch.cuda.max_memory_reserved(),'elapsed_seconds':time.monotonic()-started,'host':socket.gethostname(),'python':sys.version,'torch':torch.__version__,'cuda':torch.version.cuda}
 x.object_map_out.parent.mkdir(parents=True,exist_ok=True);x.object_map_out.write_text(json.dumps({'schema_version':'C16_OBJECT_MAP_V1','runtime':result,'ranges':rows,'unmatched_policy':'UNKNOWN_RUNTIME'},indent=2,sort_keys=True)+'\n');result['object_map_sha256']=sha(x.object_map_out);
 if x.address_context_out is not None:
  if x.trace_path is None or not x.trace_path.is_file(): raise RuntimeError('same-process ADDRESS_CONTEXT requires a completed trace path')
  if x.static_map is None or not x.static_map.is_file(): raise RuntimeError('same-process ADDRESS_CONTEXT requires exact static map')
  gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid','--format=csv,noheader'],text=True).strip()
  ctx={'schema_version':'C16_ADDRESS_CONTEXT_V1','address_space_id':hashlib.sha256((str(os.getpid())+str(time.time_ns())+gpu).encode()).hexdigest(),'process_pid':os.getpid(),'process_started_monotonic':started,'gpu_uuid':gpu,'target_id':x.target_id,'static_index':x.static_index,'function_occurrence':x.function_occurrence,'model_id':spec[3],'revision':spec[4],'scenario':'S2_TEXT','trace_path':str(x.trace_path),'trace_sha256':sha(x.trace_path),'static_map_path':str(x.static_map),'static_map_sha256':sha(x.static_map),'object_map_sha256':result['object_map_sha256'],'allocator':os.environ.get('PYTORCH_CUDA_ALLOC_CONF','UNSET'),'ranges':rows,'alignment_bytes':[4096,65536,2097152]}
  x.address_context_out.parent.mkdir(parents=True,exist_ok=True);x.address_context_out.write_text(json.dumps(ctx,indent=2,sort_keys=True)+'\n');result['address_context_path']=str(x.address_context_out);result['address_context_sha256']=sha(x.address_context_out)
 x.receipt_out.parent.mkdir(parents=True,exist_ok=True);x.receipt_out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
