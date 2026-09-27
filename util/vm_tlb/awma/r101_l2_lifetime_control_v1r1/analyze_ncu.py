#!/usr/bin/env python3
"""Separate author arithmetic and discard traffic for exact B0/D1 graphs."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_l2_lifetime_control_v1r1_20260927')
METRICS = (
    'dram__bytes_read.sum', 'dram__bytes_write.sum', 'lts__t_bytes.sum',
    'sm__cycles_active.sum', 'launch__registers_per_thread',
    'launch__shared_mem_per_block',
)


def number(value: str | None) -> float | None:
    if value is None or value in ('', 'N/A', 'nan'):
        return None
    return float(value.replace(',', ''))


def family(name: str) -> str:
    lower = name.lower()
    if 'r101r1_discard_lines' in lower:
        return 'DISCARD_128B'
    if 'xxt_kernel' in lower:
        return 'AUTHOR_XXT'
    if 'ba_plus_caa_kernel' in lower:
        return 'AUTHOR_BA_PLUS_CAA'
    if 'bmm_add_kernel' in lower:
        return 'AUTHOR_FUSED_BMM_ADD'
    if 'norm' in lower:
        return 'NORMALIZATION'
    return 'OTHER'


def main() -> None:
    all_rows = []
    summary = {}
    reports = {}
    units = None
    for shape in ('K128', 'L512'):
        for arm in ('B0', 'D1'):
            target = f'{shape}_{arm}'
            path = ROOT / 'raw/ncu' / target / f'{target}.raw.csv'
            with path.open(newline='') as stream:
                raw = list(csv.DictReader(stream))
            assert raw
            target_units = {metric: raw[0].get(metric, '') for metric in METRICS}
            assert target_units['dram__bytes_write.sum'] == 'Mbyte'
            if units is None:
                units = target_units
            else:
                assert units == target_units
            rows = []
            for item in raw:
                if not item['ID']:
                    continue
                name = item['Kernel Name']
                row = {
                    'target': target, 'family': family(name),
                    'exact_kernel_name': name,
                    'grid': item['Grid Size'], 'block': item['Block Size'],
                }
                for metric in METRICS:
                    row[metric] = number(item.get(metric))
                rows.append(row)
                all_rows.append(row)
            counts = Counter(row['family'] for row in rows)
            assert all(counts[name] == 5 for name in (
                'AUTHOR_XXT', 'AUTHOR_BA_PLUS_CAA', 'AUTHOR_FUSED_BMM_ADD'))
            assert counts['DISCARD_128B'] == (0 if arm == 'B0' else 15)
            assert json.loads((ROOT / 'raw/ncu' / target / 'TARGET_RECEIPT.json').read_text())['output_bitwise_with_untimed_canary']
            reports[target] = rows
            summary[target] = {
                'kernel_count': len(rows),
                'family_counts': dict(counts),
                'ns_family_metric_sums_reported_units': {
                    metric: sum(row[metric] or 0 for row in rows if row['family'].startswith('AUTHOR_'))
                    for metric in METRICS[:4]
                },
                'discard_metric_sums_reported_units': {
                    metric: sum(row[metric] or 0 for row in rows if row['family'] == 'DISCARD_128B')
                    for metric in METRICS[:4]
                },
                'all_metric_sums_reported_units': {
                    metric: sum(row[metric] or 0 for row in rows)
                    for metric in METRICS[:4]
                },
            }
    result_rows = []
    mismatches = {}
    for shape in ('K128', 'L512'):
        base, discard = (summary[f'{shape}_{arm}'] for arm in ('B0', 'D1'))
        base_arithmetic = Counter((row['exact_kernel_name'], row['grid'], row['block'])
                                  for row in reports[f'{shape}_B0']
                                  if row['family'].startswith('AUTHOR_'))
        discard_arithmetic = Counter((row['exact_kernel_name'], row['grid'], row['block'])
                                     for row in reports[f'{shape}_D1']
                                     if row['family'].startswith('AUTHOR_'))
        pair_qualified = base_arithmetic == discard_arithmetic
        if not pair_qualified:
            mismatches[shape] = {
                'baseline_only': list((base_arithmetic - discard_arithmetic).items()),
                'discard_only': list((discard_arithmetic - base_arithmetic).items()),
            }
        b = base['ns_family_metric_sums_reported_units']
        d = discard['ns_family_metric_sums_reported_units']
        discard_metrics = discard['discard_metric_sums_reported_units']
        total_metrics = discard['all_metric_sums_reported_units']
        reduction = 1 - d['dram__bytes_write.sum'] / b['dram__bytes_write.sum'] if pair_qualified else None
        result_rows.append({
            'shape': shape,
            'b0_ns_dram_read_Mbyte': b['dram__bytes_read.sum'],
            'd1_ns_dram_read_Mbyte': d['dram__bytes_read.sum'],
            'b0_ns_dram_write_Mbyte': b['dram__bytes_write.sum'],
            'd1_ns_dram_write_Mbyte': d['dram__bytes_write.sum'],
            'ns_dram_write_reduction_fraction': reduction,
            'b0_ns_l2_requested_Mbyte': b['lts__t_bytes.sum'],
            'd1_ns_l2_requested_Mbyte': d['lts__t_bytes.sum'],
            'b0_ns_sm_active_cycles_sum': b['sm__cycles_active.sum'],
            'd1_ns_sm_active_cycles_sum': d['sm__cycles_active.sum'],
            'd1_discard_dram_read_Mbyte': discard_metrics['dram__bytes_read.sum'],
            'd1_discard_dram_write_Mbyte': discard_metrics['dram__bytes_write.sum'],
            'd1_discard_l2_requested_Mbyte': discard_metrics['lts__t_bytes.sum'],
            'd1_discard_sm_active_cycles_sum': discard_metrics['sm__cycles_active.sum'],
            'd1_all_dram_write_Mbyte': total_metrics['dram__bytes_write.sum'],
            'arithmetic_kernel_name_grid_block_strata_equal': pair_qualified,
            'scientific_pair_status': 'QUALIFIED' if pair_qualified else 'UNQUALIFIED_AUTOTUNE_DRIFT_NO_REDUCTION_CLAIM',
            'ncu_app_replay_cache_control_none': True,
            'ncu_duration_not_primary': True,
        })
    if mismatches:
        (ROOT / 'NCU_AUTOTUNE_DRIFT_DIAGNOSTIC.json').write_text(
            json.dumps({'mismatches': mismatches,
                        'attempted_matching_b0_recollection': True,
                        'no_k128_reduction_claim': True,
                        'l512_pair_qualified': 'L512' not in mismatches}, indent=2) + '\n')
    with (ROOT / 'NCU_KERNEL_DIAGNOSTIC.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(all_rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(all_rows)
    with (ROOT / 'TRAFFIC_RESULTS.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(result_rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(result_rows)
    (ROOT / 'NCU_SUMMARY.json').write_text(json.dumps({
        'raw_metric_units': units, 'targets': summary,
        'd1_write_reduction_gate_l512': result_rows[1]['ns_dram_write_reduction_fraction'],
        'ncu_profile_durations_not_primary': True,
        'accepted_r101_baseline_ncu_not_used_as_denominator': True,
    }, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result_rows, indent=2))


if __name__ == '__main__':
    main()
