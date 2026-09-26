#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

ROOT=Path('/data/c16/awma/uvm_model_derived_characterization_20260926')

def read_tsv(p): return list(csv.DictReader(p.open(),delimiter='\t'))
def write_tsv(p,rows,fields=None):
    fields=fields or list(rows[0])
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

meta=read_tsv(ROOT/'MODEL_ASSET_METADATA.tsv')
route=[json.loads(x) for x in (ROOT/'routing/ROUTE_TRACE.jsonl').read_text().splitlines()]

# Preserve the immutable safetensors inventory order emitted by the metadata audit.
dense=[x for x in meta if x['asset_role']=='DENSE_SELECTED']
off=0; dr=[]
for i,x in enumerate(dense):
    b=int(x['byte_count']);dr.append({'order':i,'offset_bytes':off,'byte_count':b,'tensor_name':x['tensor_name'],'source_file':x['source_file'],'source_file_sha256':x['source_file_sha256']});off+=b
write_tsv(ROOT/'D1_DENSE_TENSOR_RANGES.tsv',dr)

moe=[x for x in meta if x['asset_role']=='MOE_SELECTED']
off=0; mr=[]
for i,x in enumerate(moe):
    b=int(x['byte_count']);mr.append({'order':i,'offset_bytes':off,'byte_count':b,'tensor_group':x['tensor_group'],'layer_id':x['layer_id'],'expert_id':x['expert_id'],'tensor_name':x['tensor_name']});off+=b
write_tsv(ROOT/'D3_MOE_TENSOR_RANGES.tsv',mr)

# Bounded actual sequence: every layer event from all eight actual decode tokens.
decode=[x for x in route if x['phase']=='DECODE']
rr=[]
for e in decode:
    rr.append({'event_index':e['event_index'],'decode_step':e['decode_step'],'token_index':e['token_index'],'layer':e['layer'],'top_k':e['top_k'],'expert_ids':','.join(map(str,e['expert_ids']))})
write_tsv(ROOT/'D3_DECODE_ROUTE.tsv',rr)

kv=read_tsv(ROOT/'KV_LAYOUT_POINTS.tsv')
rows=[
 {'contract':'D1','pattern':'DENSE_TENSOR_STREAM','model':'Qwen3-8B','revision':dense[0]['revision'],'allocation_bytes':off if False else sum(int(x['byte_count']) for x in dense),'steps':'3','frozen_access':'All 399 tensor regions in inventory order once per step','m0':'demand','m1':'current tensor cudaMemPrefetchAsync before demand','fidelity':'EXACT_METADATA_SIZE_ORDER; ACCESS_REPLAY_NOT_MODEL_EXECUTION'},
]
for x in kv:
    rows.append({'contract':'D2_'+x['point_id'],'pattern':'KV_GROWTH','model':'Llama-3.2-1B','revision':next(z['revision'] for z in meta if z['asset_role']=='KV_SELECTED'),'allocation_bytes':x['total_kv_bytes'],'steps':'16','frozen_access':f"context=4096 concurrency={x['concurrent_sequences']}; append 256-token block/step (= exact 256 x per-token bytes); scan active prefix",'m0':'demand','m1':'current appended block cudaMemPrefetchAsync before demand','fidelity':'LAYOUT_EXACT; ACCESS_APPROXIMATE_BLOCKED_REPLAY'})
rows.append({'contract':'D3','pattern':'MOE_ACTUAL_ROUTE','model':'OLMoE-1B-7B','revision':next(z['revision'] for z in meta if z['asset_role']=='MOE_SELECTED'),'allocation_bytes':sum(int(x['byte_count']) for x in moe),'steps':str(len(rr)),'frozen_access':'128 actual decode token-layer events; exact top-8 expert IDs and exact expert tensor region sizes; non-expert tensors scanned once per decode token','m0':'demand','m1':'current selected expert regions cudaMemPrefetchAsync after route known','fidelity':'EXACT_METADATA_AND_ROUTE; ACCESS_REPLAY_NOT_MODEL_EXECUTION'})
write_tsv(ROOT/'MODEL_DERIVED_PATTERN_PREREG.tsv',rows)

files=['MODEL_ASSET_METADATA.tsv','MODEL_ASSET_SUMMARY.tsv','KV_LAYOUT_POINTS.tsv','routing/ROUTE_TRACE.jsonl','routing/ROUTING_CAPTURE_RECEIPT.json','D1_DENSE_TENSOR_RANGES.tsv','D3_MOE_TENSOR_RANGES.tsv','D3_DECODE_ROUTE.tsv','MODEL_DERIVED_PATTERN_PREREG.tsv']
receipt={'status':'MODEL_DERIVED_CONTRACTS_FROZEN_BEFORE_UVM_RESULTS','files':{f:sha(ROOT/f) for f in files},'d1_total_bytes':sum(int(x['byte_count']) for x in dense),'d1_tensor_count':len(dense),'d3_total_bytes':sum(int(x['byte_count']) for x in moe),'d3_expert_bytes':sum(int(x['byte_count']) for x in moe if x['tensor_group']=='EXPERT'),'d3_nonexpert_bytes':sum(int(x['byte_count']) for x in moe if x['tensor_group']=='NON_EXPERT'),'d3_decode_route_events':len(rr)}
(ROOT/'PREREG_FREEZE_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(receipt,sort_keys=True))
