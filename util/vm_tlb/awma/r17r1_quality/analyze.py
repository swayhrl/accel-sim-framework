#!/usr/bin/env python3
"""CPU-only formal Q1 and matched Q1/Q32 scientific boundary analysis."""
import csv
import json
import math
import statistics
from pathlib import Path

ROOT=Path('/data/c16/awma/r17r1_quality_requalification_20260930')
WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r17r1-quality-requalification-109-v1')
PACK=WT/'docs/vm_tlb/review_packs/AWMA_R17R1_GRAPH_SEARCH_109_V2'

def table(path):
    with path.open(newline='') as f:return list(csv.DictReader(f,delimiter='\t'))

def stats(xs):
    xs=sorted(xs);median=statistics.median(xs)
    return {'n':len(xs),'median':median,
        'MAD':statistics.median(abs(x-median) for x in xs),
        'p95':xs[math.ceil(0.95*len(xs))-1],
        'min':xs[0],'max':xs[-1]}

def main():
    c=json.loads((ROOT/'raw/stage_c_summary.json').read_text())
    d=json.loads((ROOT/'raw/stage_d_summary.json').read_text())
    assert c['Q1_STRONG_V2']=='Q1_MULTI_512_1'
    assert d['holdout_inspected'] is False
    q1=d['1']['per_search_batch_host_ms']['median']
    q32=d['32']['per_search_batch_host_ms']['median']
    assert q1<q32 and d['1']['recall_at_10_min']>=0.95 and d['32']['recall_at_10_min']>=0.95
    raw=table(ROOT/'raw/stage_d_per_batch.tsv')
    first=[float(x['complete_host_ms']) for x in raw if x['status']=='FORMAL' and x['query_batch']=='1']
    batch=[float(x['complete_host_ms']) for x in raw if x['status']=='FORMAL' and x['query_batch']=='32']
    assert len(first)==15*256 and len(batch)==15*8
    formal=table(PACK/'FORMAL_Q1_TIMING.tsv')
    assert len(formal)==42
    groups={}
    for g in range(3):
        groups[str(g)]={}
        for arm in ('Q1_SINGLE_512_1','Q1_MULTI_512_1'):
            xs=[float(x['complete_256_Q1_host_ms']) for x in formal if x['status']=='FORMAL' and x['group']==str(g) and x['arm']==arm]
            assert len(xs)==5
            groups[str(g)][arm]=stats(xs)
    result={'decision':'R17_CAGRA_EXISTING_SOFTWARE_SUFFICIENT',
      'Q1_STRONG_V2':c['Q1_STRONG_V2'],'index_sha256':c['index_sha256'],
      'formal_Q1':c['candidate_summary'],
      'matched_Q1_per_query_ms':stats(first),
      'matched_Q32_complete_batch_ms':stats(batch),
      'matched_Q1_256_set_ms':d['1']['complete_256_set_host_ms'],
      'matched_Q32_256_set_ms':d['32']['complete_256_set_host_ms'],
      'matched_recall_Q1_range':[d['1']['recall_at_10_min'],d['1']['recall_at_10_max']],
      'matched_recall_Q32_range':[d['32']['recall_at_10_min'],d['32']['recall_at_10_max']],
      'Q1_complete_request_latency_below_Q32_complete_batch_latency':q1<q32,
      'Q32_amortized_per_query_only_throughput_diagnostic':d['Q32_amortized_throughput_only_ms_per_query'],
      'Q32_div32_never_used_as_Q1_latency_bound':True,
      'stage_c_group_stats':groups,
      'wrapper_gate_status':'NOT_TRIGGERED; submit interval encloses potentially synchronous C API/GPU work and is not isolated host fraction',
      'GPU_event_time_status':d['GPU_event_time_status'],
      'profiler_status':'NOT_TRIGGERED_STAGE_D_SOFTWARE_SUFFICIENT',
      'holdout_status':'SEALED_NOT_OPENED'}
    (PACK/'MATCHED_ANALYSIS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'matched_Q1':result['matched_Q1_per_query_ms'],
        'matched_Q32':result['matched_Q32_complete_batch_ms'],
        'decision':result['decision']},sort_keys=True))

if __name__=='__main__':main()
