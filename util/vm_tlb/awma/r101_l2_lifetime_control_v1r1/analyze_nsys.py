#!/usr/bin/env python3
"""Qualify B0/D1 arithmetic kernel sequence and isolate discard nodes."""
from __future__ import annotations

import csv
import json
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_l2_lifetime_control_v1r1_20260927')
R101 = Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')


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
    return 'OTHER_ARITHMETIC_OR_NORMALIZATION'


def main() -> None:
    con = sqlite3.connect(ROOT / 'raw/nsys/d1_graph_path.sqlite')
    rows = []
    sequences = {}
    summary = {}
    for edge in (128, 512):
        for arm in ('B0', 'D1'):
            label = f'R101R1_OPERATOR_K{edge}_{arm}_GRAPH'
            ranges = con.execute('SELECT start,end FROM NVTX_EVENTS WHERE text=? AND end IS NOT NULL',
                                 (label,)).fetchall()
            assert len(ranges) == 1, (label, ranges)
            start, end = ranges[0]
            result = con.execute('''
                SELECT s.value,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ,
                       k.start,k.end
                FROM CUPTI_ACTIVITY_KIND_KERNEL k
                JOIN StringIds s ON s.id=k.demangledName
                WHERE k.start>=? AND k.end<=?
                ORDER BY k.start,k.end''', (start, end)).fetchall()
            assert result, label
            sequence = []
            counts = Counter()
            durations = Counter()
            for index, (name, gx, gy, gz, bx, by, bz, kernel_start, kernel_end) in enumerate(result):
                fam = family(name)
                counts[fam] += 1
                duration_ms = (kernel_end - kernel_start) / 1e6
                durations[fam] += duration_ms
                identity = (name, gx, gy, gz, bx, by, bz)
                sequence.append(identity)
                rows.append({
                    'edge': edge, 'arm': arm, 'launch_index_in_range': index,
                    'family': fam, 'exact_demangled_name': name,
                    'grid': f'{gx},{gy},{gz}', 'block': f'{bx},{by},{bz}',
                    'gpu_duration_ms_profiler_only': duration_ms,
                })
            sequences[(edge, arm)] = sequence
            summary[f'K{edge}_{arm}'] = {
                'nvtx_label': label,
                'family_counts': dict(counts),
                'family_kernel_duration_sum_ms_profiler_only': dict(durations),
                'kernel_count': len(result),
                'graph_nvtx_wall_ms_profiler_only': (end - start) / 1e6,
            }
    with (R101 / 'R101_OPERATOR_KERNEL_STRATA.tsv').open(newline='') as stream:
        accepted = list(csv.DictReader(stream, delimiter='\t'))
    for edge in (128, 512):
        b0 = sequences[(edge, 'B0')]
        d1 = sequences[(edge, 'D1')]
        d1_arithmetic = [item for item in d1 if family(item[0]) != 'DISCARD_128B']
        assert b0 == d1_arithmetic, f'arithmetic path changed for K{edge}'
        b0_counts = Counter(family(item[0]) for item in b0)
        d1_counts = Counter(family(item[0]) for item in d1)
        assert all(b0_counts[name] == 5 for name in (
            'AUTHOR_XXT', 'AUTHOR_BA_PLUS_CAA', 'AUTHOR_FUSED_BMM_ADD'))
        assert d1_counts['DISCARD_128B'] == 15
        accepted_strata = {
            (row['exact_demangled_name'], row['grid'], row['block'], int(row['launches']))
            for row in accepted
            if row['mode'] == 'GRAPH' and row['arm'] == ('K128' if edge == 128 else 'L512')
            and row['family'] in ('AUTHOR_XXT', 'AUTHOR_BA_PLUS_CAA', 'AUTHOR_FUSED_BMM_ADD')
        }
        current_strata = Counter((item[0], f'{item[1]},{item[2]},{item[3]}',
                                  f'{item[4]},{item[5]},{item[6]}')
                                 for item in b0 if family(item[0]).startswith('AUTHOR_'))
        current_set = {(*key, count) for key, count in current_strata.items()}
        matches_accepted = current_set == accepted_strata
        summary[f'K{edge}_PATH_GATE'] = {
            'b0_d1_exact_nondiscard_name_grid_block_sequence_equal': True,
            'accepted_r101_author_arithmetic_strata_equal': matches_accepted,
            'five_each_author_kernel_family': True,
            'd1_discard_kernel_count': 15,
            'ncu_baseline_recollection_decision':
                'recollect matching B0, because normalized wrapper/graph cubin identity is not proven from accepted R101 NCU',
        }
        if not matches_accepted:
            summary[f'K{edge}_PATH_GATE']['accepted_strata'] = sorted(accepted_strata)
            summary[f'K{edge}_PATH_GATE']['current_strata'] = sorted(current_set)
    with (ROOT / 'KERNEL_IDENTITY.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    (ROOT / 'NSYS_PATH_QUALIFICATION.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps({key: val for key, val in summary.items() if key.endswith('PATH_GATE')}, indent=2))


if __name__ == '__main__':
    main()
