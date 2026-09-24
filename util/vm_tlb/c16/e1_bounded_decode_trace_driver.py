#!/usr/bin/env python3
"""Exact natural Qwen2.5-7B-AWQ D1-D3 driver for bounded native-SASS capture."""
import argparse,hashlib,json,os
from pathlib import Path
import torch
from awq import AutoAWQForCausalLM
from e1_residency_common import AWQ

TOKENS=Path("/data/c16/inputs/.incoming/qwen2p5_7b_instruct_raw/S2_TEXT/payload/token_ids.json")
TOKEN_SHA="0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9"
MODEL_REVISION="b25037543e9394b818fdfca67ab2a00ecc7dd641"
MODEL_CONFIG_SHA="ec0c1f5f875ad8bc1f78c5140c22dbdde1b55478442ad358e7a4d9ecf947a327"
EXPECTED_TOKENS=[23578,11,323,3950]
SELECTED=(1,2,3)
ROLES=("gate_proj","up_proj","down_proj")
EXPECTED_LOGIT_SHA=[
 "91d4b5c37b4118da1ebe289bd5bf8e022cefa6f8c23199df38e4bd1c55f8a0bf",
 "2b0e5fae10dd2dd7407d40c6ece0b847b25dbb74f0723347f0acbab12d42702c",
 "43457c99e2d878b6514ad87665865d16eda777bb24c638903aac612ff644e640",
 "068928405e7e2117110fc713043a398f1cf5e40b0428c9325bb41dae15c5daac",
]

def fsha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def tsha(t):
 raw=t.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()
 return hashlib.sha256(raw).hexdigest()
def out_tensor(value):
 if isinstance(value,torch.Tensor): return value
 if isinstance(value,(tuple,list)) and value and isinstance(value[0],torch.Tensor): return value[0]
 raise RuntimeError(f"unsupported output type {type(value)}")
def region(t,name):
 s=t.untyped_storage(); n=t.numel()*t.element_size()
 return {"tensor_name":name,"dtype":str(t.dtype),"shape":list(t.shape),"stride":list(t.stride()),
  "numel":t.numel(),"element_size_bytes":t.element_size(),"bytes":n,
  "data_ptr":t.data_ptr(),"data_ptr_hex":hex(t.data_ptr()),
  "storage_data_ptr":s.data_ptr(),"storage_data_ptr_hex":hex(s.data_ptr()),"storage_nbytes":s.nbytes(),
  "storage_offset_elements":t.storage_offset(),"storage_offset_bytes":t.storage_offset()*t.element_size(),
  "exact_tensor_span_begin":t.data_ptr(),"exact_tensor_span_end_exclusive":t.data_ptr()+n,
  "contiguous":t.is_contiguous(),"device":str(t.device)}
def emit(events,kind,**fields):
 row={"event_ordinal":len(events),"kind":kind,**fields};events.append(row)
 print("C16_TRACE_EVENT "+json.dumps(row,sort_keys=True),flush=True)
def cuda_ok(status): return getattr(status,"value",status)==0
def assert_nonoverlap(targets,catalog):
 collisions=[]
 for target in targets:
  lo,hi=target["exact_tensor_span_begin"],target["exact_tensor_span_end_exclusive"]
  for other in catalog:
   if other["tensor_name"]==target["tensor_name"]: continue
   olo,ohi=other["exact_tensor_span_begin"],other["exact_tensor_span_end_exclusive"]
   if max(lo,olo)<min(hi,ohi): collisions.append({"target":target["tensor_name"],"other":other["tensor_name"]})
 if collisions: raise RuntimeError(f"qweight span collision {collisions[:4]}")

def main():
 p=argparse.ArgumentParser();p.add_argument("--mode",choices=("census","canary","formal"),required=True)
 p.add_argument("--receipt",type=Path,required=True);p.add_argument("--qweight-sidecar",type=Path,required=True)
 p.add_argument("--events",type=Path,required=True);a=p.parse_args()
 if fsha(TOKENS)!=TOKEN_SHA: raise RuntimeError("token authority mismatch")
 model_root=Path(AWQ)
 if model_root.name!=MODEL_REVISION or fsha(model_root/"config.json")!=MODEL_CONFIG_SHA: raise RuntimeError("model authority mismatch")
 torch.manual_seed(0);wrapper=AutoAWQForCausalLM.from_quantized(str(model_root),fuse_layers=False)
 model=wrapper.model.eval();layers=model.model.layers
 if len(layers)!=28: raise RuntimeError("layer cardinality")
 targets=[];catalog=[]
 for li,layer in enumerate(layers):
  for role in ROLES:
   module=getattr(layer.mlp,role)
   for component in ("qweight","qzeros","scales"):
    t=getattr(module,component);row=region(t,f"model.layers.{li}.mlp.{role}.{component}")
    row.update({"layer_index":li,"role":role,"component":component});catalog.append(row)
    if role=="up_proj" and component=="qweight":
     row["content_sha256_before"]=tsha(t);targets.append(row)
 if len(targets)!=28 or len({x["storage_data_ptr"] for x in targets})!=28: raise RuntimeError("qweight allocation cardinality")
 if any(not x["contiguous"] for x in targets) or len({x["bytes"] for x in targets})!=1: raise RuntimeError("qweight layout")
 assert_nonoverlap(targets,catalog)

 events=[];active={"decode":None};captured={};handles=[]
 def pre(li,cat):
  def hook(module,args):
   d=active["decode"]
   if d is None:return
   emit(events,"SEMANTIC_BEGIN",decode_index=d,layer_index=li,category=cat)
   if cat=="up_proj" and d in SELECTED:captured[(d,li)]={"input":args[0].detach(),"module_class":type(module).__name__}
  return hook
 def post(li,cat):
  def hook(module,args,result):
   d=active["decode"]
   if d is None:return
   if cat=="up_proj" and d in SELECTED:captured[(d,li)]["output"]=out_tensor(result).detach()
   emit(events,"SEMANTIC_END",decode_index=d,layer_index=li,category=cat)
  return hook
 for li,layer in enumerate(layers):
  handles += [layer.self_attn.register_forward_pre_hook(pre(li,"self_attn")),
              layer.self_attn.register_forward_hook(post(li,"self_attn"))]
  for role in ROLES:
   module=getattr(layer.mlp,role)
   handles += [module.register_forward_pre_hook(pre(li,role)),module.register_forward_hook(post(li,role))]

 ids=torch.tensor([json.loads(TOKENS.read_text())],dtype=torch.long,device="cuda");generated=[];logits=[];started=False
 with torch.inference_mode():
  emit(events,"PREFILL_BEGIN");prefill=model(input_ids=ids,use_cache=True)
  current=torch.argmax(prefill.logits[:,-1,:],dim=-1,keepdim=True);past=prefill.past_key_values;del prefill
  emit(events,"PREFILL_END")
  for d in range(4):
   generated.append(current.detach());active["decode"]=d
   if d==1:
    status=torch.cuda.cudart().cudaProfilerStart()
    if not cuda_ok(status):raise RuntimeError(f"cudaProfilerStart {status}")
    started=True;emit(events,"PROFILE_RANGE_BEGIN",first_decode=1,last_decode=3)
   emit(events,"DECODE_BEGIN",decode_index=d)
   result=model(input_ids=current,past_key_values=past,use_cache=True);past=result.past_key_values
   logits.append(result.logits.detach())
   current=torch.argmax(result.logits[:,-1,:],dim=-1,keepdim=True);del result
   emit(events,"DECODE_END",decode_index=d)
   if d==3:
    status=torch.cuda.cudart().cudaProfilerStop()
    if not cuda_ok(status):raise RuntimeError(f"cudaProfilerStop {status}")
    started=False;emit(events,"PROFILE_RANGE_END",first_decode=1,last_decode=3)
   active["decode"]=None
 if started:torch.cuda.cudart().cudaProfilerStop();raise RuntimeError("unterminated profiler range")
 torch.cuda.synchronize()
 for h in handles:h.remove()
 token_ids=[int(x.item()) for x in generated]
 if token_ids!=EXPECTED_TOKENS:raise RuntimeError(f"token drift {token_ids}")
 logit_sha=[tsha(x) for x in logits]
 logit_match=[actual==expected for actual,expected in zip(logit_sha,EXPECTED_LOGIT_SHA)]
 if len(captured)!=84:raise RuntimeError(f"up occurrence closure {len(captured)}")
 occurrences=[]
 for d,li in sorted(captured):
  row=captured[(d,li)]
  occurrences.append({"decode_index":d,"layer_index":li,"role":"up_proj","module_class":row["module_class"],
   "input_sha256":tsha(row["input"]),"output_sha256":tsha(row["output"]),
   "input_shape":list(row["input"].shape),"output_shape":list(row["output"].shape)})
 after={}
 for li,layer in enumerate(layers):
  t=layer.mlp.up_proj.qweight;row=region(t,f"model.layers.{li}.mlp.up_proj.qweight");row["content_sha256_after"]=tsha(t);after[li]=row
 for row in targets:
  end=after[row["layer_index"]];row["data_ptr_after"]=end["data_ptr"];row["storage_data_ptr_after"]=end["storage_data_ptr"]
  row["content_sha256_after"]=end["content_sha256_after"];row["pointer_stable"]=row["data_ptr"]==end["data_ptr"]
  row["storage_pointer_stable"]=row["storage_data_ptr"]==end["storage_data_ptr"]
  row["content_stable"]=row["content_sha256_before"]==end["content_sha256_after"]
 if not all(x["pointer_stable"] and x["storage_pointer_stable"] and x["content_stable"] for x in targets):raise RuntimeError("qweight stability")
 sidecar={"schema":"C16_E1_ORACLE_QWEIGHT_REGIONS_V1","status":"PASS","process_id":os.getpid(),
  "capture_interval":{"decode_indices":list(SELECTED),"profiler_api":"cudaProfilerStart/Stop"},
  "model_revision":MODEL_REVISION,"accepted_producer":"86ef7dcfb49241bd87ff4a8d59b4d950d53de0a5",
  "token_ids_sha256":TOKEN_SHA,"target_count":len(targets),"unique_allocation_count":len({x["storage_data_ptr"] for x in targets}),
  "single_qweight_bytes":targets[0]["bytes"],"all_target_bytes":sum(x["bytes"] for x in targets),"targets":targets,
  "excluded_component_catalog":catalog,"target_spans_disjoint_from_all_other_catalog_entries":True}
 receipt={"schema":"C16_E1_BOUNDED_DECODE_TRACE_DRIVER_V1","status":"PASS","mode":a.mode,
  "model_id":"Qwen/Qwen2.5-7B-Instruct-AWQ","model_revision":MODEL_REVISION,"model_root":str(model_root),
  "model_config_sha256":MODEL_CONFIG_SHA,"token_source":str(TOKENS),"token_ids_sha256":TOKEN_SHA,
  "generated_token_ids_D0_D3":token_ids,"lm_head_output_sha256_D0_D3":logit_sha,
  "accepted_lm_head_output_sha256_D0_D3":EXPECTED_LOGIT_SHA,"lm_head_bitwise_match_D0_D3":logit_match,
  "lm_head_sha_status":"EXACT_ACCEPTED_MATCH" if all(logit_match) else "BITWISE_VARIATION_TOKEN_AND_KERNEL_PATH_STABLE",
  "selected_decode_indices":list(SELECTED),"natural_full_model_decode":True,
  "cuda_persisting_l2_intervention":False,"access_policy_windows":False,"isolated_operator_replay":False,
  "up_proj_occurrence_count":len(occurrences),"up_proj_occurrences":occurrences,"up_proj_occurrence_sha_status":"POST_RUN_ALIAS_TELEMETRY_NOT_FORMAL_IDENTITY",
  "torch_version":torch.__version__,"torch_cuda_version":torch.version.cuda}
 a.qweight_sidecar.parent.mkdir(parents=True,exist_ok=True)
 a.qweight_sidecar.write_text(json.dumps(sidecar,indent=2,sort_keys=True)+"\n")
 receipt["qweight_sidecar_sha256"]=fsha(a.qweight_sidecar)
 a.events.write_text("".join(json.dumps(x,sort_keys=True)+"\n" for x in events))
 a.receipt.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
 print("C16_TRACE_DRIVER_COMPLETE "+json.dumps(receipt,sort_keys=True),flush=True)
if __name__=="__main__":main()
