#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,statistics,time,traceback
from pathlib import Path
import torch
from himuon.optimizers.himuon import HiMuon
from himuon.triton_kernels import ns5_smem

ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
ARMS=['F128','K128','L256','L512']

def sha_file(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def load_inputs():
    receipt=json.loads((ROOT/'R101_TILE_INPUT_RECEIPT_DISCOVERY.json').read_text())
    values={}
    for t in (128,256,512):
        path=ROOT/'raw'/f'discovery_tiles_T{t}.pt'
        assert sha_file(path)==receipt['tiles'][str(t)]['payload_sha256']
        values[t]=torch.load(path,map_location='cpu',weights_only=True).to('cuda:0')
    return values

def apply(arm,inputs):
    if arm=='F128':return ns5_smem(inputs[128],persistent=False)
    edge=int(arm[1:])
    return HiMuon._newton_schulz_3kernel(inputs[edge],steps=5)

def measure(arm,inputs,kind,rep):
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    start=torch.cuda.Event(enable_timing=True);end=torch.cuda.Event(enable_timing=True)
    host_start=time.perf_counter_ns()
    start.record()
    with torch.no_grad():out=apply(arm,inputs)
    end.record();torch.cuda.synchronize()
    host_end=time.perf_counter_ns()
    finite=bool(torch.isfinite(out).all())
    if not finite:raise ValueError(f'nonfinite {arm}/{kind}/{rep}')
    row={'arm':arm,'run_status':kind,'rep':rep,
      'tile_edge':128 if arm in ('F128','K128') else int(arm[1:]),
      'tile_count':len(inputs[128 if arm in ('F128','K128') else int(arm[1:])]),
      'complete_call_gpu_ms':start.elapsed_time(end),
      'host_elapsed_ms_secondary':(host_end-host_start)/1e6,
      'peak_allocated_bytes':torch.cuda.max_memory_allocated(),
      'output_finite':finite,'source_path':'author ns5_smem' if arm=='F128' else 'author compiled _newton_schulz_3kernel',
      'input_and_output_stable':'same frozen input; author wrapper returns fresh output'}
    return row

def main():
    qualifier=json.loads((ROOT/'R101_NUMERICAL_CANARY_RECEIPT_DISCOVERY.json').read_text())
    if qualifier['status']!='CANARY_COMPLETE' or not qualifier['same_map_pair_pass']:
        raise ValueError('numerical gate not passed')
    inputs=load_inputs()
    canaries=[measure(a,inputs,'CANARY',0) for a in ARMS]
    for warmup in range(2):
        for arm in ARMS:measure(arm,inputs,'WARMUP',warmup)
    formal=[]
    for rep in range(7):
        order=['F128','K128'] if rep%2==0 else ['K128','F128']
        order+=['L256','L512'] if rep%2==0 else ['L512','L256']
        for arm in order:
            row=measure(arm,inputs,'FORMAL',rep)
            formal.append(row)
            print(json.dumps({'arm':arm,'rep':rep,'gpu_ms':row['complete_call_gpu_ms']}))
    with (ROOT/'OPERATOR_TIMING.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(formal[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(formal)
    stats={}
    for arm in ARMS:
        vals=[r['complete_call_gpu_ms'] for r in formal if r['arm']==arm]
        med=statistics.median(vals)
        stats[arm]={'median_gpu_ms':med,'formal_gpu_ms':vals,
          'max_relative_jitter':max(abs(v-med) for v in vals)/med,
          'median_host_elapsed_ms_secondary':statistics.median(r['host_elapsed_ms_secondary'] for r in formal if r['arm']==arm),
          'tile_count':next(r['tile_count'] for r in formal if r['arm']==arm)}
    k=stats['K128'];f=stats['F128']
    improvement=(k['median_gpu_ms']-f['median_gpu_ms'])/k['median_gpu_ms']
    noise=max(k['max_relative_jitter'],f['max_relative_jitter'])
    decision={'same_map_improvement_fraction':improvement,
      'larger_max_relative_jitter':noise,
      'effect_over_jitter_ratio':improvement/noise if noise else None,
      'same_map_material_response':improvement>=0.05 and improvement>3*noise,
      'numerical_gate_pass':True,
      'interpretation_limit':'eager call response includes interkernel launch gaps; graph/NSYS needed before intermediate HBM causal claim'}
    (ROOT/'OPERATOR_TIMING_ANALYSIS.json').write_text(json.dumps({'arms':stats,'same_map':decision,'canaries':canaries},indent=2,sort_keys=True)+'\n')
    print(json.dumps({'arms':{a:v['median_gpu_ms'] for a,v in stats.items()},
      'same_map':decision},sort_keys=True))

if __name__=='__main__':main()
