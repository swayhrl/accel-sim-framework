#!/usr/bin/env python3
"""Diagnostic exact graph-node strata joined to accepted R101 structural catalog."""
from __future__ import annotations

import csv
import json
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path('/data/c16/awma/r101r2_s128_native_profile_20260929')
R101 = Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')


def family(name: str) -> str:
    low = name.lower()
    if 'ns5_smem_kernel' in low:
        return 'F128_FUSED_NS5'
    if 'xxt_kernel' in low:
        return 'K128_XXT'
    if 'ba_plus_caa_kernel' in low:
        return 'K128_BA'
    if 'bmm_add_kernel' in low:
        return 'K128_BMM_ADD'
    if 'norm' in low:
        return 'K128_NORMALIZATION'
    return 'GRAPH_RUNTIME_OTHER'


def main() -> None:
    con = sqlite3.connect(ROOT / 'raw/nsys/s128_path.sqlite')
    rows = []
    summary = {}
    for arm in ('F128', 'K128'):
        label = f'R101R2_PATH_{arm}'
        ranges = con.execute('SELECT start,end FROM NVTX_EVENTS WHERE text=? AND end IS NOT NULL',
                             (label,)).fetchall()
        assert len(ranges) == 1, (label, ranges)
        start, end = ranges[0]
        result = con.execute('''SELECT s.value,k.gridX,k.gridY,k.gridZ,
            k.blockX,k.blockY,k.blockZ,k.start,k.end
            FROM CUPTI_ACTIVITY_KIND_KERNEL k JOIN StringIds s ON s.id=k.demangledName
            WHERE k.start>=? AND k.end<=? ORDER BY k.start,k.end''',
            (start, end)).fetchall()
        assert result
        counts = Counter()
        for index, (name, gx, gy, gz, bx, by, bz, kernel_start, kernel_end) in enumerate(result):
            fam = family(name)
            counts[fam] += 1
            rows.append({'arm': arm, 'roi_kernel_index': index, 'family': fam,
                         'exact_demangled_name': name, 'grid': f'{gx},{gy},{gz}',
                         'block': f'{bx},{by},{bz}',
                         'gpu_duration_ms_profiler_only': (kernel_end - kernel_start) / 1e6})
        summary[arm] = {'nvtx_label': label, 'family_counts': dict(counts),
                        'kernel_count_all_graph_nodes': len(result),
                        'nvtx_wall_ms_profiler_only': (end - start) / 1e6}
    assert summary['F128']['family_counts']['F128_FUSED_NS5'] == 1
    assert all(summary['K128']['family_counts'][family_] == 5 for family_ in
               ('K128_XXT', 'K128_BA', 'K128_BMM_ADD'))
    with (R101 / 'R101_OPERATOR_KERNEL_STRATA.tsv').open(newline='') as stream:
        accepted = list(csv.DictReader(stream, delimiter='\t'))
    family_map = {'F128_FUSED_NS5': 'AUTHOR_FUSED_NS5',
                  'K128_XXT': 'AUTHOR_XXT',
                  'K128_BA': 'AUTHOR_BA_PLUS_CAA',
                  'K128_BMM_ADD': 'AUTHOR_FUSED_BMM_ADD'}
    for arm in ('F128', 'K128'):
        now = Counter((row['exact_demangled_name'], row['grid'], row['block'])
                      for row in rows if row['arm'] == arm and row['family'] in family_map)
        old = Counter({(row['exact_demangled_name'], row['grid'], row['block']): int(row['launches'])
                       for row in accepted if row['mode'] == 'GRAPH' and row['arm'] == arm
                       and row['family'] in family_map.values()})
        assert now == old, (arm, now, old)
        summary[arm]['exact_author_kernel_name_grid_block_strata_match_accepted_R101'] = True
    with (ROOT / 'KERNEL_IDENTITY.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    (ROOT / 'PATH_QUALIFICATION.json').write_text(json.dumps({
        'arms': summary, 'accepted_source_commit': 'af89eda9a0176effed99e1fe19cc1f8a1a2c9588',
        'ncu_profile_must_reconfirm_its_own_kernel_strata': True,
        'nsys_duration_not_primary_timing': True,
    }, indent=2, sort_keys=True) + '\n')
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
