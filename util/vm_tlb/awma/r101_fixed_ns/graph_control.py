#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,statistics,time,traceback
from pathlib import Path
import torch
from himuon.optimizers.himuon import HiMuon
from himuon.triton_kernels import ns5_smem

ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
ARMS=['F128_GRAPH','K128_GRAPH','L256_GRAPH','L512_GRAPH']

def apply(arm,inputs):
    if arm=='F128_GRAPH':return ns5_smem(inputs[128],persistent=False)
    edge=int(arm.split('_')[0][1:])
    return HiMuon._newton_schulz_3kernel(inputs[edge],steps=5)

def graph_for(arm,inputs,reference):
    edge=128 if arm.startswith(('F128','K128')) else int(arm.split('_')[0][1:])
    x=inputs[edge]
    side=torch.cuda.Stream()
    side.wait_stream(torch.cuda.current_stream())
    with torch.cuda.stream(side):
        for _ in range(3):apply(arm,inputs)
    side.synchronize()
    graph=torch.cuda.CUDAGraph()
    with torch.cuda.graph(graph,stream=side):
        output=apply(arm,inputs)
    graph.replay();torch.cuda.synchronize()
    expected=reference[arm.split('_')[0]]
    if not torch.allclose(output,expected,rtol=1e-2,atol=1e-2):
        raise ValueError(f'graph initial output differs from frozen author output {arm}')
    frozen=output.detach().clone()
    old=x[0,0,0].clone()
    x[0,0,0]=old+1.0
    graph.replay();torch.cuda.synchronize()
    changed=not torch.equal(output,frozen)
    x[0,0,0]=old
    graph.replay();torch.cuda.synchronize()
    restored=bool(torch.allclose(output,frozen,rtol=1e-2,atol=1e-2))
    if not changed or not restored:
        raise ValueError(f'graph liveness failed {arm}: changed={changed} restored={restored}')
    return graph,output,{'arm':arm,'input_edge':edge,'perturbed_output_changed':changed,
        'restored_output_matches':restored,'initial_matches_author_eager':True,
        'graph_input_pointer':int(x.data_ptr()),'graph_output_pointer':int(output.data_ptr())}

def measure(arm,graph,output,kind,rep):
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    start=torch.cuda.Event(enable_timing=True);end=torch.cuda.Event(enable_timing=True)
    host_start=time.perf_counter_ns()
    start.record()
    graph.replay()
    end.record();torch.cuda.synchronize()
    host_end=time.perf_counter_ns()
    if not torch.isfinite(output).all():raise ValueError(f'nonfinite graph output {arm}')
    return {'arm':arm,'run_status':kind,'rep':rep,
      'graph_replay_gpu_ms':start.elapsed_time(end),
      'host_elapsed_ms_secondary':(host_end-host_start)/1e6,
      'peak_allocated_bytes':torch.cuda.max_memory_allocated(),
      'output_finite':True,'graph_replay_liveness_qualified':True}

def main():
    prereg=json.loads((ROOT/'GRAPH_CONTROL_PREREGISTRATION.json').read_text())
    assert prereg['arms']==ARMS
    inputs={t:torch.load(ROOT/'raw'/f'discovery_tiles_T{t}.pt',weights_only=True,map_location='cpu').to('cuda:0')
            for t in (128,256,512)}
    reference={k:v.to('cuda:0') for k,v in torch.load(ROOT/'raw/discovery_numerical_outputs.pt',
        weights_only=True,map_location='cpu').items()}
    graphs={};outputs={};canaries={}
    for arm in ARMS:
        graph,out,canary=graph_for(arm,inputs,reference)
        graphs[arm]=graph;outputs[arm]=out;canaries[arm]=canary
    (ROOT/'GRAPH_CONTROL_CANARY.json').write_text(json.dumps(canaries,indent=2,sort_keys=True)+'\n')
    for warmup in range(2):
        for arm in ARMS:measure(arm,graphs[arm],outputs[arm],'WARMUP',warmup)
    formal=[]
    for rep in range(7):
        order=['F128_GRAPH','K128_GRAPH'] if rep%2==0 else ['K128_GRAPH','F128_GRAPH']
        order+=['L256_GRAPH','L512_GRAPH'] if rep%2==0 else ['L512_GRAPH','L256_GRAPH']
        for arm in order:
            row=measure(arm,graphs[arm],outputs[arm],'FORMAL',rep)
            formal.append(row)
            print(json.dumps({'arm':arm,'rep':rep,'graph_gpu_ms':row['graph_replay_gpu_ms']}))
    with (ROOT/'GRAPH_CONTROL_TIMING.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(formal[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(formal)
    stats={}
    for arm in ARMS:
        vals=[r['graph_replay_gpu_ms'] for r in formal if r['arm']==arm]
        med=statistics.median(vals)
        stats[arm]={'median_gpu_ms':med,'formal_gpu_ms':vals,
          'max_relative_jitter':max(abs(v-med) for v in vals)/med}
    k=stats['K128_GRAPH'];f=stats['F128_GRAPH']
    improvement=(k['median_gpu_ms']-f['median_gpu_ms'])/k['median_gpu_ms']
    noise=max(k['max_relative_jitter'],f['max_relative_jitter'])
    result={'arms':stats,'same_map_graph':{
      'improvement_fraction':improvement,'larger_max_relative_jitter':noise,
      'effect_over_jitter_ratio':improvement/noise if noise else None,
      'material_response':improvement>=0.05 and improvement>3*noise,
      'graph_removes_repeat_call_launch_path':True,
      'numerical_and_liveness_canaries_pass':True}}
    (ROOT/'GRAPH_CONTROL_ANALYSIS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result['same_map_graph'],sort_keys=True))

if __name__=='__main__':main()
