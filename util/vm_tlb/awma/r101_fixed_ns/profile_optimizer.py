#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import torch
from optimizer_replay import ROOT,NAMES,load_authority,make_graph_arm,reset,compare

def main(edge):
    original_cpu,gradients=load_authority()
    originals={k:v.to('cuda:0') for k,v in original_cpu.items()}
    opt,params,reference,canary=make_graph_arm(edge,originals,gradients)
    reset(opt,params,originals)
    torch.cuda.nvtx.range_push(f'R101_SELECTED_OPTIMIZER_L{edge}_GRAPH')
    with torch.no_grad():opt.step()
    torch.cuda.synchronize()
    torch.cuda.nvtx.range_pop()
    good,checks=compare(reference,params)
    if not good:raise ValueError(f'profile first-state semantic failed L{edge}')
    payload={'edge':edge,'source':'pinned HiMuon cross-layer batch/plan/concat/compile/CUDA Graph',
      'first_state_eager_equivalence':good,'plan':canary['cross_layer_plan'],
      'concat_buffers_stable':canary['concat_buffers_stable'],
      'parameter_checks':checks,'profile_time_is_not_primary':True}
    out=ROOT/'raw/nsys'/f'optimizer_L{edge}'
    out.mkdir(parents=True,exist_ok=True)
    (out/'PROFILE_RECEIPT.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'edge':edge,'semantic_equivalence':good,'plan_calls':[x['n_calls'] for x in canary['cross_layer_plan']]}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--edge',type=int,choices=[256,512],required=True)
    main(p.parse_args().edge)
