#!/usr/bin/env python3
from __future__ import annotations
import csv,json,statistics,time
from pathlib import Path
import torch
from himuon.optimizers.himuon import HiMuon
from himuon.triton_kernels import ns5_smem
from graph_control import graph_for

ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
EAGER=['F128','K128','L512']
GRAPH=['F128_GRAPH','K128_GRAPH','L512_GRAPH']

def apply(arm,inputs):
    if arm=='F128':return ns5_smem(inputs[128],persistent=False)
    edge=128 if arm=='K128' else 512
    return HiMuon._newton_schulz_3kernel(inputs[edge],steps=5)

def measure_eager(arm,inputs,kind,rep):
    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats()
    start=torch.cuda.Event(enable_timing=True);end=torch.cuda.Event(enable_timing=True)
    host=time.perf_counter_ns();start.record()
    with torch.no_grad():out=apply(arm,inputs)
    end.record();torch.cuda.synchronize();elapsed=(time.perf_counter_ns()-host)/1e6
    if not torch.isfinite(out).all():raise ValueError(f'nonfinite {arm}')
    return {'scope':'EAGER_OPERATOR','arm':arm,'run_status':kind,'rep':rep,
      'complete_gpu_ms':start.elapsed_time(end),'host_ms_secondary':elapsed,
      'peak_allocated_bytes':torch.cuda.max_memory_allocated(),'output_finite':True}

def measure_graph(arm,graph,output,kind,rep):
    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats()
    start=torch.cuda.Event(enable_timing=True);end=torch.cuda.Event(enable_timing=True)
    host=time.perf_counter_ns();start.record()
    graph.replay()
    end.record();torch.cuda.synchronize();elapsed=(time.perf_counter_ns()-host)/1e6
    if not torch.isfinite(output).all():raise ValueError(f'nonfinite {arm}')
    return {'scope':'GRAPH_OPERATOR','arm':arm,'run_status':kind,'rep':rep,
      'complete_gpu_ms':start.elapsed_time(end),'host_ms_secondary':elapsed,
      'peak_allocated_bytes':torch.cuda.max_memory_allocated(),'output_finite':True}

def main():
    prereg=json.loads((ROOT/'HOLDOUT_PREREGISTRATION.json').read_text())
    assert prereg['tile_edges']==[128,512]
    numeric=json.loads((ROOT/'R101_NUMERICAL_CANARY_RECEIPT_HOLDOUT.json').read_text())
    if not numeric['same_map_pair_pass']:raise ValueError('holdout numeric gate fail')
    inputs={t:torch.load(ROOT/'raw'/f'holdout_tiles_T{t}.pt',weights_only=True,map_location='cpu').to('cuda:0')
            for t in [128,512]}
    frozen={k:v.to('cuda:0') for k,v in torch.load(ROOT/'raw/holdout_numerical_outputs.pt',
        weights_only=True,map_location='cpu').items()}
    graph_objects={};graph_outputs={};canaries={}
    for arm in EAGER:
        row=measure_eager(arm,inputs,'CANARY',0)
        out=apply(arm,inputs)
        if not torch.allclose(out,frozen[arm],rtol=1e-2,atol=1e-2):raise ValueError(arm)
        canaries[arm]={'numerical_allclose':True,'finite':row['output_finite']}
    for arm in GRAPH:
        graph,out,proof=graph_for(arm,inputs,frozen)
        graph_objects[arm]=graph;graph_outputs[arm]=out
        canaries[arm]={'numerical_allclose':proof['initial_matches_author_eager'],
                       'liveness':proof['perturbed_output_changed'] and proof['restored_output_matches']}
    (ROOT/'HOLDOUT_CANARY.json').write_text(json.dumps(canaries,indent=2,sort_keys=True)+'\n')
    for warm in range(2):
        for arm in EAGER:measure_eager(arm,inputs,'WARMUP',warm)
        for arm in GRAPH:measure_graph(arm,graph_objects[arm],graph_outputs[arm],'WARMUP',warm)
    formal=[]
    for rep in range(7):
        eager_order=['F128','K128'] if rep%2==0 else ['K128','F128']
        graph_order=['F128_GRAPH','K128_GRAPH'] if rep%2==0 else ['K128_GRAPH','F128_GRAPH']
        for arm in eager_order+['L512']:
            formal.append(measure_eager(arm,inputs,'FORMAL',rep))
        for arm in graph_order+['L512_GRAPH']:
            formal.append(measure_graph(arm,graph_objects[arm],graph_outputs[arm],'FORMAL',rep))
    with (ROOT/'HOLDOUT_RESULTS.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(formal[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(formal)
    stats={}
    for arm in EAGER+GRAPH:
        vals=[r['complete_gpu_ms'] for r in formal if r['arm']==arm]
        med=statistics.median(vals)
        stats[arm]={'median_gpu_ms':med,'values_gpu_ms':vals,
          'max_relative_jitter':max(abs(x-med) for x in vals)/med}
    gate={}
    for name,a,b in [('EAGER','F128','K128'),('GRAPH','F128_GRAPH','K128_GRAPH')]:
        fast=stats[a];slow=stats[b]
        improvement=(slow['median_gpu_ms']-fast['median_gpu_ms'])/slow['median_gpu_ms']
        noise=max(fast['max_relative_jitter'],slow['max_relative_jitter'])
        gate[name]={'improvement_fraction':improvement,'effect_over_jitter_ratio':improvement/noise if noise else None,
                    'material_same_map_direction':improvement>=0.05 and improvement>3*noise}
    result={'arms':stats,'same_map':gate,'numeric_pass':True,'l512_graph_ms':stats['L512_GRAPH']['median_gpu_ms']}
    (ROOT/'HOLDOUT_ANALYSIS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'same_map':gate,'medians':{k:v['median_gpu_ms'] for k,v in stats.items()}},sort_keys=True))

if __name__=='__main__':main()
