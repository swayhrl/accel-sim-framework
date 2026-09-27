#!/usr/bin/env python3
"""Qualified same-process A0/D2 NCU traffic and policy-control gate."""
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
    path = ROOT / 'raw/ncu/ARENA_PAIR/ARENA_PAIR.raw.csv'
    with path.open(newline='') as stream:
        raw = list(csv.DictReader(stream))
    assert raw
    units = {metric: raw[0].get(metric, '') for metric in METRICS}
    assert units['dram__bytes_write.sum'] == 'Mbyte'
    arms = {'A0': [], 'D2': []}
    nvtx_columns = [name for name in raw[0] if 'Range' in name and 'Msg' in name]
    for item in raw:
        if not item['ID']:
            continue
        ranges = ' '.join(item.get(name, '') for name in nvtx_columns)
        matches = [arm for arm in arms if f'R101R1_NCU_ARENA_L512_{arm}' in ranges]
        assert len(matches) == 1, (item['ID'], ranges)
        arm = matches[0]
        name = item['Kernel Name']
        row = {'arm': arm, 'family': family(name), 'exact_kernel_name': name,
               'grid': item['Grid Size'], 'block': item['Block Size']}
        for metric in METRICS:
            row[metric] = number(item.get(metric))
        arms[arm].append(row)
    for arm in arms:
        counts = Counter(row['family'] for row in arms[arm])
        assert all(counts[name] == 5 for name in (
            'AUTHOR_XXT', 'AUTHOR_BA_PLUS_CAA', 'AUTHOR_FUSED_BMM_ADD'))
        assert counts['DISCARD_128B'] == (0 if arm == 'A0' else 15)
    a0_arithmetic = Counter((row['exact_kernel_name'], row['grid'], row['block'])
                            for row in arms['A0'] if row['family'].startswith('AUTHOR_'))
    d2_arithmetic = Counter((row['exact_kernel_name'], row['grid'], row['block'])
                            for row in arms['D2'] if row['family'].startswith('AUTHOR_'))
    assert a0_arithmetic == d2_arithmetic
    def metric_sum(arm: str, metric: str, category: str) -> float:
        return sum(row[metric] or 0 for row in arms[arm]
                   if (row['family'].startswith('AUTHOR_') if category == 'NS' else
                       row['family'] == 'DISCARD_128B' if category == 'DISCARD' else True))
    b_write = metric_sum('A0', 'dram__bytes_write.sum', 'NS')
    d_write = metric_sum('D2', 'dram__bytes_write.sum', 'NS')
    reduction = 1 - d_write / b_write
    result = {
        'shape': 'L512',
        'a0_arena_ns_dram_read_Mbyte': metric_sum('A0', 'dram__bytes_read.sum', 'NS'),
        'd2_ns_dram_read_Mbyte': metric_sum('D2', 'dram__bytes_read.sum', 'NS'),
        'a0_arena_ns_dram_write_Mbyte': b_write,
        'd2_ns_dram_write_Mbyte': d_write,
        'd2_ns_write_reduction_fraction_vs_a0_arena': reduction,
        'a0_arena_ns_l2_requested_Mbyte': metric_sum('A0', 'lts__t_bytes.sum', 'NS'),
        'd2_ns_l2_requested_Mbyte': metric_sum('D2', 'lts__t_bytes.sum', 'NS'),
        'a0_arena_ns_active_cycles_sum': metric_sum('A0', 'sm__cycles_active.sum', 'NS'),
        'd2_ns_active_cycles_sum': metric_sum('D2', 'sm__cycles_active.sum', 'NS'),
        'd2_discard_dram_read_Mbyte': metric_sum('D2', 'dram__bytes_read.sum', 'DISCARD'),
        'd2_discard_dram_write_Mbyte': metric_sum('D2', 'dram__bytes_write.sum', 'DISCARD'),
        'd2_discard_l2_requested_Mbyte': metric_sum('D2', 'lts__t_bytes.sum', 'DISCARD'),
        'd2_discard_active_cycles_sum': metric_sum('D2', 'sm__cycles_active.sum', 'DISCARD'),
        'd2_all_dram_write_Mbyte': metric_sum('D2', 'dram__bytes_write.sum', 'ALL'),
        'a0_d2_arithmetic_strata_equal': True,
        'same_process_autotune': True,
        'ncu_duration_not_primary': True,
    }
    rows = arms['A0'] + arms['D2']
    with (ROOT / 'ARENA_NCU_KERNEL_DIAGNOSTIC.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    with (ROOT / 'ARENA_TRAFFIC_RESULTS.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(result), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerow(result)
    (ROOT / 'ARENA_NCU_SUMMARY.json').write_text(json.dumps({
        'raw_metric_units': units, 'family_counts': {
            arm: dict(Counter(row['family'] for row in arms[arm])) for arm in arms},
        'result': result, 'one_d2_ncu_profile': True,
    }, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
