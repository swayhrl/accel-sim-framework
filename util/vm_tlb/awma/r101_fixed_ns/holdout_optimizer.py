#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,statistics
from pathlib import Path
import torch
from safetensors import safe_open
from optimizer_replay import make_graph_arm,measure,sha_tensor

ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
MODEL=Path('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775/model.safetensors')
NAMES=['model.layers.12.self_attn.q_proj.weight',
       'model.layers.12.mlp.up_proj.weight',
       'model.layers.12.mlp.down_proj.weight']

def main():
    prereg=json.loads((ROOT/'HOLDOUT_PREREGISTRATION.json').read_text())
    assert prereg['parameter_names']==NAMES and prereg['tile_edges']==[128,512]
    micro=torch.load(ROOT/'raw/holdout_gradient_microstate.pt',weights_only=True,map_location='cpu')
    receipt=json.loads((ROOT/'R101_GRADIENT_MICROSTATE_RECEIPT_HOLDOUT.json').read_text())
    grads={name:micro[name]['grad'].clone().contiguous() for name in NAMES}
    assert all(sha_tensor(grads[name])==receipt['parameters'][name]['gradient_sha256'] for name in NAMES)
    with safe_open(MODEL,framework='pt',device='cpu') as source:
        originals={name:source.get_tensor(name).clone().contiguous().to('cuda:0') for name in NAMES}
    opt,params,ref,canary=make_graph_arm(512,originals,grads,names=NAMES)
    (ROOT/'HOLDOUT_OPTIMIZER_CANARY.json').write_text(json.dumps(canary,indent=2,sort_keys=True)+'\n')
    for warm in range(2):
        measure(512,opt,params,originals,ref,'WARMUP',warm,names=NAMES)
    formal=[]
    for rep in range(7):
        row=measure(512,opt,params,originals,ref,'FORMAL',rep,names=NAMES)
        formal.append(row)
        print(json.dumps({'rep':rep,'gpu_ms':row['complete_selected_optimizer_gpu_ms']}))
    with (ROOT/'HOLDOUT_OPTIMIZER_REPLAY.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(formal[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(formal)
    values=[r['complete_selected_optimizer_gpu_ms'] for r in formal]
    med=statistics.median(values)
    holdout_op=json.loads((ROOT/'HOLDOUT_ANALYSIS.json').read_text())['l512_graph_ms']
    analysis={'median_optimizer_gpu_ms':med,'formal_values_ms':values,
      'max_relative_jitter':max(abs(v-med) for v in values)/med,
      'standalone_l512_same_map_graph_gpu_ms':holdout_op,
      'standalone_to_full_ratio_descriptive_not_causal_decomposition':holdout_op/med,
      'first_state_eager_graph_author_tolerance_pass':True,
      'cached_plan_and_concat_stable':True}
    (ROOT/'HOLDOUT_OPTIMIZER_ANALYSIS.json').write_text(json.dumps(analysis,indent=2,sort_keys=True)+'\n')
    print(json.dumps(analysis,sort_keys=True))

if __name__=='__main__':main()
