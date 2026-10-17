#!/usr/bin/env python3
"""Synthetic address sets: distinguish read reuse, line alias and byte conflict."""
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from cross_kernel_reuse import compare,reusable_distinct_lines

ROOT=Path(__file__).resolve().parents[1]


def entry(r=0,w=0):
    return dict(r=r,w=w,r_pcs={'0x100':r} if r else {},w_pcs={'0x200':w} if w else {})


if __name__=='__main__':
    old={'lines':{'128':entry(15,15),'256':entry(15,0)}}
    now={'lines':{'128':entry(240,0),'256':entry(3,0),'384':entry(15,0)}}
    r=compare(old,now)
    assert r['prior_read_current_read_distinct_lines']==2
    assert r['prior_read_current_read_byte_overlap_lines']==1
    assert r['prior_write_current_read_distinct_lines']==1
    assert r['prior_write_current_read_byte_overlap_lines']==0
    assert r['pc_pairs'][0]['sector_overlap_line_count']==1
    assert r['pc_pairs'][0]['byte_overlap_line_count']==0
    assert r['pc_pairs'][0]['actual_old_mapping_exposure']=='UNAVAILABLE'
    union=reusable_distinct_lines([old,old],now)
    assert union==dict(read_lines_seen_in_any_prior_kernel=2,read_lines_written_in_any_prior_kernel=1)
    overlap={'lines':{'128':entry(60,0)}}
    assert compare(old,overlap)['prior_write_current_read_byte_overlap_lines']==1
    assert compare({'lines':{}},now)['prior_read_current_read_distinct_lines']==0
    result=dict(status='PASS_SYNTHETIC_CROSS_KERNEL_ONLY',
        checked=['exact_read_read_intersection','same_sector_without_byte_conflict',
                 'positive_byte_conflict','pc_candidate_counts','distinct_union_not_sum','empty_history'],
        reducer_sha256=hashlib.sha256((ROOT/'scripts/cross_kernel_reuse.py').read_bytes()).hexdigest(),
        test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        original_trace_body_opens=0,native_or_simulator_executions=0,
        measured_original_workload_reuse='UNAVAILABLE')
    (ROOT/'CPU_CROSS_KERNEL_PREFLIGHT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
