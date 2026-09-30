#!/usr/bin/env python3
"""Compact factual extraction from the three bounded R101R5 NCU reports."""
import csv
import json
import re
from pathlib import Path

ROOT = Path('/data/c16/awma/r101r5_native_post_l1_downstream_20260930/raw/phase_b')
REVIEW = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101r5-native-post-l1-downstream-109-v1/docs/vm_tlb/review_packs/AWMA_R101R5_NATIVE_POST_L1_DOWNSTREAM_109_V1')
FAMILIES = ['XXT_kernel', 'ba_plus_cAA_kernel', 'bmm_add_kernel']

def tsv(name, rows):
    if not rows: return
    with (REVIEW / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        w.writeheader(); w.writerows(rows)

def number(s):
    if not s or s == '-': return 0.0
    return float(s.replace(',', ''))

def pc_kind(sass):
    s = re.sub(r'^@!?P\d+\s+', '', sass.strip())
    if s.startswith('LDGDEPBAR'): return 'ASYNC_GLOBAL_LOAD_DEPENDENCY_BARRIER'
    if re.match(r'^(LDGSTS|LDSM)', s): return 'LDGSTS_OR_SHARED_LOAD'
    if re.match(r'^(LDG\.|LD\.)', s): return 'DIRECT_GLOBAL_LD'
    if re.match(r'^(STG\.|ST\.)', s): return 'DIRECT_GLOBAL_ST'
    return 'OTHER_OR_DEPENDENT_PC'

def main():
    receipts = json.loads((ROOT / 'command_receipts.json').read_text())
    fact_rows, stall_rows, pc_rows, aggregate_rows = [], [], [], []
    for family, receipt in zip(FAMILIES, receipts):
        assert receipt['target'] == family and receipt['returncode'] == 0
        assert receipt['actual_kernel'] == family and receipt['replayer_passes'] == '11.000000'
        numerical = json.loads((ROOT / f'{family}.numerical_receipt.json').read_text())
        assert numerical['same_numerical_output_with_author_tolerance']
        with (ROOT / f'{family}.raw.csv').open(newline='') as f:
            reader = csv.DictReader(f); units = next(reader); rows = list(reader)
        assert len(rows) == 1 and rows[0]['Kernel Name'] == family
        r = rows[0]
        def get(metric): return r.get(metric, 'COUNTER_UNAVAILABLE')
        prefix = 'smsp__warp_issue_stalled_'
        stalls = [(k[len(prefix):-len('_per_warp_active.pct')], number(v))
                  for k,v in r.items() if k.startswith(prefix) and k.endswith('_per_warp_active.pct')
                  and k != prefix + 'long_scoreboard_pipe_l1tex_per_warp_active.pct']
        stalls.sort(key=lambda x:x[1], reverse=True)
        for rank, (name, value) in enumerate(stalls, 1):
            stall_rows.append({'target':family, 'rank':rank, 'stall_category':name,
                               'pct_of_active_warp_cycles':f'{value:.6f}',
                               'denominator':'active warp-cycles; source metric smsp__warp_issue_stalled_*_per_warp_active.pct'})
        facts = {
            'target':family, 'accepted_launch_id':receipt['accepted_launch_id'],
            'recurrence':'2_of_5', 'occurrence_0based':1,
            'function':r['Kernel Name'], 'grid':r['Grid Size'], 'block':r['Block Size'],
            'dynamic_LDG_LD_warp_inst':get('sm__sass_inst_executed_op_global_ld.sum'),
            'dynamic_STG_ST_warp_inst':get('sm__sass_inst_executed_op_global_st.sum'),
            'dynamic_LDGSTS_warp_inst':get('sm__sass_inst_executed_op_ldgsts.sum'),
            'L1TEX_global_load_sectors_32B':get('l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum'),
            'L1TEX_global_store_sectors_32B':get('l1tex__t_sectors_pipe_lsu_mem_global_op_st.sum'),
            'L2_requested_Mbyte':get('lts__t_bytes.sum'),
            'DRAM_read_Mbyte':get('dram__bytes_read.sum'),
            'DRAM_write_Mbyte':get('dram__bytes_write.sum'),
            'SM_active_cycles_sum':get('sm__cycles_active.sum'),
            'active_warps_pct_peak':get('sm__warps_active.avg.pct_of_peak_sustained_active'),
            'eligible_warps_per_active_cycle':get('smsp__warps_eligible.avg.per_cycle_active'),
            'active_warps_per_active_cycle':get('smsp__warps_active.avg.per_cycle_active'),
            'math_pipe_throttle_pct_active_warp':get(prefix+'math_pipe_throttle_per_warp_active.pct'),
            'long_scoreboard_pct_active_warp':get(prefix+'long_scoreboard_per_warp_active.pct'),
            'LG_throttle_pct_active_warp':get(prefix+'lg_throttle_per_warp_active.pct'),
            'MIO_throttle_pct_active_warp':get(prefix+'mio_throttle_per_warp_active.pct'),
            'short_scoreboard_pct_active_warp':get(prefix+'short_scoreboard_per_warp_active.pct'),
            'barrier_pct_active_warp':get(prefix+'barrier_per_warp_active.pct'),
            'wait_pct_active_warp':get(prefix+'wait_per_warp_active.pct'),
            'not_selected_pct_active_warp':get(prefix+'not_selected_per_warp_active.pct'),
            'selected_pct_active_warp':get(prefix+'selected_per_warp_active.pct'),
            'top3_stalls':','.join(f'{a}:{b:.2f}%' for a,b in stalls[:3]),
            'NCU_internal_replay_passes':receipt['replayer_passes'],
            'report_sha256':receipt['report_sha256'],
            'source_PC_status':'AVAILABLE_SASS_PC_SAMPLES',
        }
        fact_rows.append(facts)
        with (ROOT / f'{family}.source.csv').open(newline='') as f:
            cr = csv.reader(f)
            metadata = next(cr); header = next(cr)
            assert metadata[:2] == ['Kernel Name',family]
            source = [dict(zip(header,row)) for row in cr if row and row[0].startswith('0x')]
        for pc in source:
            for kind in ('stall_long_sb', 'stall_lg', 'stall_math'):
                n = number(pc.get(kind, '0'))
                if n:
                    pc_rows.append({'target':family, 'pc':pc['Address'], 'SASS':pc['Source'].strip(),
                                    'PC_instruction_class':pc_kind(pc['Source']),
                                    'sample_reason':kind, 'sample_count':int(n),
                                    'denominator':'sampled warp-stall events for this reason; not cycles or causality'})
        for kind in ('stall_long_sb', 'stall_lg', 'stall_math'):
            matching = [x for x in pc_rows if x['target']==family and x['sample_reason']==kind]
            matching.sort(key=lambda x:x['sample_count'], reverse=True)
            total = sum(x['sample_count'] for x in matching)
            for rank,x in enumerate(matching[:12],1):
                aggregate_rows.append(dict(rank=rank, total_reason_samples=total, **x))
    tsv('NATIVE_DOWNSTREAM_PROFILE.tsv', fact_rows)
    tsv('STALL_COMPOSITION.tsv', stall_rows)
    tsv('SOURCE_PC_ATTRIBUTION.tsv', aggregate_rows)
    summaries = []
    for family in FAMILIES:
        for reason in ('stall_long_sb','stall_lg','stall_math'):
            matching = [x for x in pc_rows if x['target']==family and x['sample_reason']==reason]
            by_class = {}
            for x in matching:
                by_class[x['PC_instruction_class']] = by_class.get(x['PC_instruction_class'],0) + x['sample_count']
            top = sorted(matching,key=lambda x:x['sample_count'],reverse=True)[:3]
            summaries.append({'target':family,'reason':reason,'total_samples':sum(x['sample_count'] for x in matching),
                              'by_sampled_PC_class':by_class,'top3_PCs':[(x['SASS'],x['sample_count']) for x in top]})
    (REVIEW / 'SOURCE_PC_SUMMARY.json').write_text(json.dumps(summaries, indent=2, sort_keys=True)+'\n')
    print(json.dumps(summaries, indent=2))

if __name__ == '__main__': main()
