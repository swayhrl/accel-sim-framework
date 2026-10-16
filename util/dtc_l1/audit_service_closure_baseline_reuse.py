#!/usr/bin/env python3
"""Audit canonical SG1 receipts without rewriting any historical artifact."""
import argparse
import csv
import json
from pathlib import Path
import re
from collect_service_closure_attempts import sha


def kv(path):
    return dict(s.split('\t', 1) for s in path.read_text().splitlines() if '\t' in s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    candidates = {}
    for p in Path(args.root).glob('*/*VALIDATION*.json'):
        d = json.loads(p.read_text())
        if d.get('schema') != 'SG1_NORMAL_STRICT_VALIDATION_V1':
            continue
        if d.get('status') != 'PASS' or not all(d['checks'].values()):
            continue
        run = p.parent
        m = kv(run / 'RUN_MANIFEST.tsv')
        if m.get('core_source_head') != '6582b9d171330d88b17e8d5294c97704229e3823':
            continue
        if m.get('simulator_sha256') != '4fcac62cd7bdccc5a49cc77950ffc45c60d5fce7c4ee44bba877e1fef2d07ef9':
            continue
        if d['variant'] not in ['B16-N', 'TC80-N']:
            continue
        end = kv(run / 'RUN_TERMINAL.tsv')
        log = run / 'simulator.stdout'
        assert end['simulator_exit_status'] == '0'
        assert sha(log) == end['stdout_sha256']
        text = log.read_text(errors='replace')
        metrics = dict(re.findall(r'^\s*(\w+)\s*=\s*(\d+)\s*$', text, re.M))
        row = dict(workload=d['workload'], variant=d['variant'], attempt_uuid=m['attempt_uuid'],
                   run_dir=str(run), core=m['core_source_head'], binary_sha256=m['simulator_sha256'],
                   strict_receipt_path=str(p), strict_receipt_sha256=sha(p),
                   stdout_sha256=end['stdout_sha256'], trace_list_sha256=m['trace_list_sha256'],
                   base_config_sha256=m['base_config_sha256'], overlay_config_sha256=m['overlay_config_sha256'],
                   instructions=d['instructions'], cycles=d['cycles'],
                   lower_cap_events=metrics.get('DTC_L1_lower_cap_full_events', 'UNAVAILABLE'),
                   lower_cap_peak=metrics.get('DTC_L1_lower_outstanding_peak', 'UNAVAILABLE'),
                   reuse='EXACT_CANONICAL_BASELINE_ORIGINAL_IDENTITY_NOT_RECOMPUTED')
        assert row['instructions'] == int(metrics['gpu_tot_sim_insn'])
        assert row['cycles'] == int(metrics['gpu_tot_sim_cycle'])
        key = (d['workload'], d['variant'])
        rank = (0 if m['stage'] == 'FAST12' else 1 if m['stage'] == 'G6' else 2, str(run))
        if key not in candidates or rank < candidates[key][0]:
            candidates[key] = (rank, row)
    data = [v[1] for _, v in sorted(candidates.items())]
    assert len(data) == 24, len(data)
    with Path(args.output).open('x') as f:
        w = csv.DictWriter(f, fieldnames=list(data[0]), delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(data)
    print(json.dumps(dict(rows=len(data), lower_cap_events=sorted({r['lower_cap_events'] for r in data}))))


if __name__ == '__main__':
    main()
