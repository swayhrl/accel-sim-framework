#!/usr/bin/env python3
"""Qualify baseline-only memory counterfactuals and extract source-audited work."""
import argparse
import csv
import json
from pathlib import Path
import re
from collect_service_closure_attempts import collect
from service_closure_scientific_disposition import FORMAT_PENDING, disposition


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--promotion-hold-workload', action='append', default=[])
    a = ap.parse_args()
    rows = []
    for start in sorted(Path(a.root).glob('B0*/RUN_START.json')):
        run = start.parent
        spec = json.loads(start.read_text())['spec']
        r = collect(run)
        row = dict(workload=spec['workload'], attempt_uuid=r['attempt_uuid'],run_dir=str(run),
                   status=r['status'],cycles=r['cycles'],instructions=r['instructions'],
                   l1_sizes_kib='', effective_mshr='384_SOURCE_AND_EXECUTED_MODE0_PROOF',
                   l1_global_read_accesses='', l1_accesses='',l1_misses='',l2_accesses='',l2_misses='',
                   dram_read_commands='',dram_write_commands='', qualification='',
                   max_rss_kb=r['max_rss_kb'],elapsed_wall=r['elapsed_wall'],
                   claim_scope='OLD_SASS_MEMORY_PARAMETER_COUNTERFACTUAL_NOT_ADA_NATIVE_OR_DTC_SPEEDUP')
        row['scientific_promotion'] = ('HOLD_SHARED_TRACE_INTERPRETATION' if spec['workload'] in a.promotion_hold_workload else 'WITHIN_DECLARED_BASELINE_ONLY_SCOPE')
        if spec['workload'] in FORMAT_PENDING:
            row['scientific_promotion'] = disposition(spec['workload'])
        if r['status'] != 'RUNNING':
            text = (run/'simulator.stdout').read_text(errors='replace')
            m = dict(re.findall(r'^\s*(\w+)\s*=\s*(\d+)\s*$',text,re.M))
            sizes = re.findall(r'Reconfigure L1 cache to (\d+)KB',text)
            controllers = {}
            for ident,line in re.findall(r'DRAM\[(\d+)\]:[^\n]*\n(n_cmd=[^\n]+)',text):
                controllers[int(ident)] = dict(re.findall(r'(\w+)=(\d+)',line))
            checks = dict(terminal=r['status']=='PASS_CHECKED_SCOPE',
                legacy_mode0=bool(re.search(r'^-gpgpu_dtc_l1_mode\s+0\s',text,re.M)),
                no_dtc_frontend='DTC_L1_mode =' not in text,
                frozen_dl1=bool(re.search(r'^-gpgpu_cache:dl1\s+S:4:128:256,L:T:m:L:L,A:384:48,16:0,32\s',text,re.M)),
                actual_adaptive_sizes=bool(sizes), dram_controllers=set(controllers)==set(range(8)))
            row.update(l1_sizes_kib=','.join(sizes),l1_accesses=m.get('L1D_total_cache_accesses','UNAVAILABLE'),
                       l1_misses=m.get('L1D_total_cache_misses','UNAVAILABLE'),
                       l2_accesses=m.get('L2_total_cache_accesses','UNAVAILABLE'),l2_misses=m.get('L2_total_cache_misses','UNAVAILABLE'))
            loads=re.findall(r'Total_core_cache_stats_breakdown\[GLOBAL_ACC_R\]\[TOTAL_ACCESS\]\s*=\s*(\d+)',text)
            row['l1_global_read_accesses']=loads[-1] if loads else 'UNAVAILABLE'
            checks['executed_global_read_path']=bool(loads) and int(loads[-1])>0
            if checks['dram_controllers']:
                row['dram_read_commands']=sum(int(d['n_rd'])+int(d['n_rd_L2_A']) for d in controllers.values())
                row['dram_write_commands']=sum(int(d['n_write']) for d in controllers.values())
            row['qualification']=json.dumps(checks,sort_keys=True)
            row['status']='PASS_BASELINE_COUNTERFACTUAL_SCOPE' if all(checks.values()) else 'FAIL_PRESERVED'
        rows.append(row)
    with Path(a.output).open('x') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({s:sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})}))


if __name__=='__main__':
    main()
