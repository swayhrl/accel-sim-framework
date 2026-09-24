#!/usr/bin/env python3
"""Trace-side runtime-VA canary for exact up_proj qweight intervals."""
import argparse,csv,json,lzma
from pathlib import Path

def addresses(line):
 p=line.split()
 if len(p)<12 or p[0].startswith(("-","#")):return []
 i=4;i+=1;mask=int(p[i],16);i+=1;nd=int(p[i]);i+=1+nd;i+=1;ns=int(p[i]);i+=1+ns
 width=int(p[i]);i+=1
 if width==0:return []
 mode=int(p[i]);i+=1;active=mask.bit_count()
 if mode==0:return [int(x,16) for x in p[i:i+active]]
 if mode==1:
  base=int(p[i],16);stride=int(p[i+1]);return [base+stride*j for j in range(active)]
 if mode==2:
  base=int(p[i],16);return [base+int(x) for x in p[i+1:i+1+active]]
 raise RuntimeError(f"address mode {mode}")
def main():
 p=argparse.ArgumentParser();p.add_argument("--run",type=Path,required=True);p.add_argument("--kernel-tsv",type=Path,required=True)
 p.add_argument("--qweights",type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--decode",type=int,default=2)
 p.add_argument("--layers",default="0,14,27");p.add_argument("--required-hits",type=int,default=32);a=p.parse_args()
 layers=[int(x) for x in a.layers.split(",")];q=json.loads(a.qweights.read_text());targets={x["layer_index"]:x for x in q["targets"]}
 with a.kernel_tsv.open(newline="") as f:rows=list(csv.DictReader(f,delimiter="\t"))
 results=[]
 for layer in layers:
  candidates=[r for r in rows if int(r["decode_iteration"])==a.decode and int(r["semantic_layer"])==layer and r["semantic_identity"]=="up_proj" and r["exact_function"]=="awq_gemm_kernel"]
  if len(candidates)!=1:raise RuntimeError(f"layer {layer} GEMM candidates {len(candidates)}")
  row=candidates[0];artifact=a.run/"raw"/row["trace_artifact"];target=targets[layer];lo=target["exact_tensor_span_begin"];hi=target["exact_tensor_span_end_exclusive"]
  hits=[];memory_addresses=0;records=0
  with lzma.open(artifact,"rt",errors="strict") as f:
   for line in f:
    records+=1
    for address in addresses(line):
     memory_addresses+=1
     if lo<=address<hi:
      hits.append(address)
      if len(hits)>=a.required_hits:break
    if len(hits)>=a.required_hits:break
  if len(hits)<a.required_hits:raise RuntimeError(f"layer {layer} qweight trace canary absent")
  results.append({"layer_index":layer,"decode_index":a.decode,"kernel_id":int(row["global_dynamic_order"]),
   "trace_artifact":row["trace_artifact"],"runtime_interval_begin":lo,"runtime_interval_end_exclusive":hi,
   "runtime_interval_begin_hex":hex(lo),"runtime_interval_end_exclusive_hex":hex(hi),
   "direct_trace_hit_count":len(hits),"first_trace_hit":hits[0],"first_trace_hit_hex":hex(hits[0]),
   "min_trace_hit":min(hits),"max_trace_hit":max(hits),"records_scanned":records,"memory_addresses_scanned":memory_addresses})
 result={"schema":"C16_E1_TRACE_ADDRESS_NAMESPACE_AUDIT_V1","status":"PASS",
  "runtime_pointer_domain":"CUDA runtime virtual address returned by Tensor.data_ptr/untyped_storage.data_ptr",
  "trace_address_domain":"NVBit MREF address serialized by Route-B native SASS tracer",
  "trace_side_relation":"DIRECT_NUMERIC_EQUALITY_CONFIRMED_BY_REAL_ARTIFACT_CANARIES",
  "simulator_l2_relation":"TRACE_SIDE_VALIDATED_SIM_L2_MAPPING_PENDING_174",
  "no_simulator_internal_transform_claim":True,"canary_layers":layers,"canaries":results}
 a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
