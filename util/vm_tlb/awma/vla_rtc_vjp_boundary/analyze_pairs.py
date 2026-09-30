#!/usr/bin/env python3
"""Offline paired A0/A1 timing analysis; no profiling or GPU work."""
import csv
import json
import statistics
from pathlib import Path

ROOT=Path('/data/c16/awma/vla_rtc_vjp_boundary_20260930')
PACK=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-vla-rtc-vjp-boundary-109-v1/docs/vm_tlb/review_packs/AWMA_VLA_RTC_VJP_BOUNDARY_109_V1')

def load(name):
    with (PACK/name).open(newline='') as f:
        return [r for r in csv.DictReader(f,delimiter='\t') if r['status']=='FORMAL']

def medmad(values):
    med=statistics.median(values)
    return {'median_ms':med,'MAD_ms':statistics.median(abs(x-med) for x in values),
            'min_ms':min(values),'max_ms':max(values)}

def main():
    a0=load('A0_TIMING.tsv');a1=load('A1_TIMING.tsv')
    assert len(a0)==len(a1)==60
    paired=[]
    for x,y in zip(a0,a1):
        key=('episode','group','repeat','window_ordinal','frame_index','guided','delay_frames')
        assert all(x[k]==y[k] for k in key),(x,y)
        base=float(x['observation_ready_to_chunk_commit_ms'])
        new=float(y['observation_ready_to_chunk_commit_ms'])
        paired.append({'group':int(x['group']),'repeat':int(x['repeat']),
            'window':int(x['window_ordinal']),'guided':x['guided']=='True',
            'A0_ms':base,'A1_ms':new,'A1_minus_A0_ms':new-base,
            'A1_speedup_percent':100*(base-new)/base})
    groups={}
    for group in range(3):
        xs=[x for x in paired if x['group']==group and x['guided']]
        groups[str(group)]={'A0_guided':medmad([x['A0_ms'] for x in xs]),
            'A1_guided':medmad([x['A1_ms'] for x in xs]),
            'paired_difference':medmad([x['A1_minus_A0_ms'] for x in xs])}
    guided=[x for x in paired if x['guided']]
    first=[x for x in paired if not x['guided']]
    out={'paired_sample_count':len(paired),'guided_pairs':len(guided),
        'first_unguided_pairs':len(first),
        'guided_A0':medmad([x['A0_ms'] for x in guided]),
        'guided_A1':medmad([x['A1_ms'] for x in guided]),
        'guided_paired_difference':medmad([x['A1_minus_A0_ms'] for x in guided]),
        'guided_pair_speedup_percent':medmad([x['A1_speedup_percent'] for x in guided]),
        'first_unguided_paired_difference':medmad([x['A1_minus_A0_ms'] for x in first]),
        'by_group':groups,
        'caveat':'same frozen samples/seeds, but A0 and A1 were acquired sequentially after F3; small sub-1% differences are not a robust throughput claim'}
    (PACK/'PAIRED_TIMING_ANALYSIS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    with (PACK/'PAIRED_TIMING.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(paired[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(paired)
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__':main()
