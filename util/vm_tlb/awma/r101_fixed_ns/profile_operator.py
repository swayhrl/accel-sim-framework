#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
import torch
from himuon.optimizers.himuon import HiMuon
from himuon.triton_kernels import ns5_smem
from graph_control import graph_for,apply as graph_apply

ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
EAGER=['F128','K128','L256','L512']

def run_eager(arm,inputs):
    if arm=='F128':return ns5_smem(inputs[128],persistent=False)
    edge=int(arm[1:])
    return HiMuon._newton_schulz_3kernel(inputs[edge],steps=5)

def main():
    inputs={t:torch.load(ROOT/'raw'/f'discovery_tiles_T{t}.pt',map_location='cpu',weights_only=True).to('cuda:0')
            for t in (128,256,512)}
    frozen={k:v.to('cuda:0') for k,v in torch.load(ROOT/'raw/discovery_numerical_outputs.pt',
       map_location='cpu',weights_only=True).items()}
    results={}
    for arm in EAGER:
        for _ in range(2):run_eager(arm,inputs)
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_push(f'R101_OPERATOR_EAGER_{arm}')
        out=run_eager(arm,inputs)
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_pop()
        results[f'EAGER_{arm}']={'numerical_allclose':bool(torch.allclose(out,frozen[arm],rtol=1e-2,atol=1e-2)),
                                 'input_shape':list(inputs[128 if arm in ('F128','K128') else int(arm[1:])].shape)}
        if not results[f'EAGER_{arm}']['numerical_allclose']:raise ValueError(arm)
    for arm in ['F128_GRAPH','K128_GRAPH','L256_GRAPH','L512_GRAPH']:
        graph,out,canary=graph_for(arm,inputs,frozen)
        torch.cuda.nvtx.range_push(f'R101_OPERATOR_GRAPH_{arm}')
        graph.replay()
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_pop()
        results[f'GRAPH_{arm}']={'numerical_allclose':bool(torch.allclose(out,frozen[arm.split("_")[0]],rtol=1e-2,atol=1e-2)),
                                 'liveness':canary['perturbed_output_changed'] and canary['restored_output_matches']}
        if not results[f'GRAPH_{arm}']['numerical_allclose'] or not results[f'GRAPH_{arm}']['liveness']:
            raise ValueError(arm)
    (ROOT/'R101_OPERATOR_PATH_CANARY.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'ranges':len(results),'all_qualified':all(r['numerical_allclose'] for r in results.values())}))

if __name__=='__main__':main()
