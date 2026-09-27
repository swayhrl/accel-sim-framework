#!/usr/bin/env python3
"""Require arithmetic node sequence equivalence under the exact A/B arena."""
from __future__ import annotations

import csv
import json
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_l2_lifetime_control_v1r1_20260927')


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
    return 'NORMALIZATION_OR_OTHER'


def main() -> None:
    con = sqlite3.connect(ROOT / 'raw/nsys/arena_d2_graph_path.sqlite')
    all_rows = []
    sequences = {}
    summary = {}
    for arm in ('A0', 'D2'):
        label = f'R101R1_ARENA_L512_{arm}_GRAPH'
        ranges = con.execute('SELECT start,end FROM NVTX_EVENTS WHERE text=? AND end IS NOT NULL',
                             (label,)).fetchall()
        assert len(ranges) == 1
        start, end = ranges[0]
        result = con.execute('''SELECT s.value,k.gridX,k.gridY,k.gridZ,
            k.blockX,k.blockY,k.blockZ,k.start,k.end
            FROM CUPTI_ACTIVITY_KIND_KERNEL k JOIN StringIds s ON s.id=k.demangledName
            WHERE k.start>=? AND k.end<=? ORDER BY k.start,k.end''',
            (start, end)).fetchall()
        assert result
        sequence = []
        counts = Counter()
        durations = Counter()
        for index, (name, gx, gy, gz, bx, by, bz, ks, ke) in enumerate(result):
            fam = family(name)
            identity = (name, gx, gy, gz, bx, by, bz)
            sequence.append(identity)
            counts[fam] += 1
            durations[fam] += (ke - ks) / 1e6
            all_rows.append({'arm': arm, 'launch_index_in_range': index, 'family': fam,
                             'exact_demangled_name': name, 'grid': f'{gx},{gy},{gz}',
                             'block': f'{bx},{by},{bz}',
                             'gpu_duration_ms_profiler_only': (ke - ks) / 1e6})
        sequences[arm] = sequence
        summary[arm] = {'family_counts': dict(counts),
                        'duration_sum_ms_profiler_only': dict(durations),
                        'kernel_count': len(result)}
    a0, d2 = sequences['A0'], sequences['D2']
    assert a0 == [item for item in d2 if family(item[0]) != 'DISCARD_128B']
    for arm in ('A0', 'D2'):
        assert all(summary[arm]['family_counts'][name] == 5 for name in (
            'AUTHOR_XXT', 'AUTHOR_BA_PLUS_CAA', 'AUTHOR_FUSED_BMM_ADD'))
    assert summary['D2']['family_counts']['DISCARD_128B'] == 15
    attached = json.loads((ROOT / 'D2_PERSISTENCE_RECEIPT.json').read_text())['policy_nodes_set_and_readback_verified']
    assert attached == summary['D2']['kernel_count'] - 2
    assert all(family(item[0]) == 'DISCARD_128B' for item in d2[attached:])
    summary['path_gate'] = {
        'a0_d2_exact_nondiscard_name_grid_block_sequence_equal': True,
        'all_relevant_producer_consumer_nodes_policy_attached_and_readback_verified': True,
        'two_terminal_discard_only_nodes_not_in_active_capture_snapshot': True,
        'd2_discard_launches': 15,
        'attached_graph_kernel_nodes': attached,
    }
    with (ROOT / 'ARENA_KERNEL_IDENTITY.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(all_rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(all_rows)
    (ROOT / 'ARENA_NSYS_PATH_QUALIFICATION.json').write_text(
        json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps(summary['path_gate']))


if __name__ == '__main__':
    main()
