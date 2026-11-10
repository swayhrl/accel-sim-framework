#!/usr/bin/env python3
"""Small, reproducible descriptive summary of accepted Stencil kernel rows."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / 'PHASE_EVIDENCE.json').read_text())
rows = data['rows']


def total(key, subset=rows):
    return sum(row[key] for row in subset)


def delta(key, subset=rows):
    return total('ext2_' + key, subset) - total('ext0_' + key, subset)


keys = ('cycles', 'read_responses', 'ext_read_responses', 'ext_clean_installs',
        'ext_queries', 'selector_reads', 'ext_indexed_reads', 'spills',
        'c7e_dram_successful_read_issues', 'c7e_dram_successful_read_bytes',
        'bank_wait_cycles', 'block_bank', 'block_payload',
        'm0_frontend_head_any_blocked_cycles',
        'm0_frontend_head_blocked_cycles_payload_capacity',
        'm0_frontend_head_blocked_cycles_payload_service',
        'lookup_wait_cycles', 'directory_queries', 'clean_installs',
        'dirty_installs', 'c7d_payload_capacity_allocation_denial',
        'c7d_payload_service_port_denial')


def stats(subset):
    return {key: {'ext0': total('ext0_' + key, subset),
                  'ext2': total('ext2_' + key, subset),
                  'delta': delta(key, subset)} for key in keys}


groups = []
for lo in range(0, 100, 10):
    subset = rows[lo:lo + 10]
    groups.append({'kernel_range': f'{lo + 1}-{lo + 10}',
                   'cycles_delta': total('delta_cycles', subset),
                   'ext2_ext_responses': total('ext2_ext_read_responses', subset),
                   'lower_reads_delta': delta('c7e_dram_successful_read_issues', subset),
                   'bank_wait_delta': delta('bank_wait_cycles', subset),
                   'lookup_wait_delta': delta('lookup_wait_cycles', subset),
                   'payload_block_delta': delta('block_payload', subset),
                   'selector_reads': total('ext2_selector_reads', subset)})

cycle_deltas = [row['delta_cycles'] for row in rows]
summary = {
    'schema': 'EP_L2_STENCIL_PHASE_SUMMARY_V1',
    'overall': stats(rows),
    'cycles_delta_population': {
        'positive_count': sum(v > 0 for v in cycle_deltas),
        'negative_count': sum(v < 0 for v in cycle_deltas),
        'zero_count': sum(v == 0 for v in cycle_deltas),
        'min': min(cycle_deltas), 'max': max(cycle_deltas),
        'median': sorted(cycle_deltas)[49:51],
        'first_10_sum': sum(cycle_deltas[:10]),
        'last_90_sum': sum(cycle_deltas[10:]),
    },
    'kernel_nonzero_counts': {key: sum(row['ext2_' + key] > 0 for row in rows)
                              for key in ('ext_read_responses', 'ext_clean_installs',
                                          'ext_queries', 'selector_reads',
                                          'ext_indexed_reads', 'spills')},
    'response_groups': {
        label: {'count': len(subset), 'cycles_delta': total('delta_cycles', subset),
                'ext_responses': total('ext2_ext_read_responses', subset),
                'lower_reads_delta': delta('c7e_dram_successful_read_issues', subset),
                'lookup_wait_delta': delta('lookup_wait_cycles', subset),
                'payload_block_delta': delta('block_payload', subset)}
        for label, subset in (
            ('with_ext_response', [row for row in rows if row['ext2_ext_read_responses'] > 0]),
            ('without_ext_response', [row for row in rows if row['ext2_ext_read_responses'] == 0]))
    },
    'top_slowdowns': [{'uid': row['uid'], 'delta_cycles': row['delta_cycles'],
                       'ext_responses': row['ext2_ext_read_responses'],
                       'lower_reads_delta': row['ext2_c7e_dram_successful_read_issues'] - row['ext0_c7e_dram_successful_read_issues']}
                      for row in sorted(rows, key=lambda row: row['delta_cycles'], reverse=True)[:10]],
    'top_speedups': [{'uid': row['uid'], 'delta_cycles': row['delta_cycles'],
                      'ext_responses': row['ext2_ext_read_responses'],
                      'lower_reads_delta': row['ext2_c7e_dram_successful_read_issues'] - row['ext0_c7e_dram_successful_read_issues']}
                     for row in sorted(rows, key=lambda row: row['delta_cycles'])[:10]],
    'ten_kernel_bins': groups,
}
with (ROOT / 'PHASE_SUMMARY.json').open('w', newline='\n') as stream:
    stream.write(json.dumps(summary, indent=2, sort_keys=True) + '\n')
print(json.dumps({k: v for k, v in summary.items() if k != 'overall'}, indent=2))
