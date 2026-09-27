#!/usr/bin/env python3
"""Freeze full-five-step launch selector and exact author arithmetic strata."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_transient_l2_sim_capture_20260927')
R101R1 = Path('/data/c16/awma/r101_l2_lifetime_control_v1r1_20260927')
LOG = ROOT / 'logs/census.stdout.log'
LAUNCH = re.compile(r'^ROUTEB_CENSUS_LAUNCH grid_launch_id=(\d+) function=(.*) grid=(\d+,\d+,\d+) block=(\d+,\d+,\d+) stream=(\d+)$')
BOUNDARY = re.compile(r'^ROUTEB_MULTI_ROI_(START|STOP) grid_launch_id=(\d+)')


def family(name: str) -> str:
    if 'XXT_kernel' in name:
        return 'XXT'
    if 'ba_plus_cAA_kernel' in name:
        return 'BA'
    if 'bmm_add_kernel' in name:
        return 'BMM_ADD'
    return 'NORMALIZATION'


def main() -> None:
    text = LOG.read_text()
    markers = [(match.group(1), int(match.group(2))) for line in text.splitlines()
               if (match := BOUNDARY.match(line))]
    assert len(markers) == 2 and markers[0][0] == 'START' and markers[1][0] == 'STOP'
    start, stop = markers[0][1], markers[1][1]
    assert stop - start == 18
    rows = []
    for line in text.splitlines():
        match = LAUNCH.match(line)
        if match is None:
            continue
        gid = int(match.group(1))
        if not start <= gid < stop:
            continue
        name, grid, block, stream = match.groups()[1:]
        rows.append({'roi_launch_index': len(rows), 'census_global_launch_id': gid,
                     'family': family(name), 'exact_function': name,
                     'grid': grid, 'block': block, 'stream': stream,
                     'phase': 'NORMALIZATION' if len(rows) < 3 else 'NS',
                     'iteration': '' if len(rows) < 3 else (len(rows) - 3) // 3,
                     'position': '' if len(rows) < 3 else (len(rows) - 3) % 3})
    assert len(rows) == 18
    assert [row['family'] for row in rows[:3]] == ['NORMALIZATION'] * 3
    assert [row['family'] for row in rows[3:]] == ['XXT', 'BA', 'BMM_ADD'] * 5
    assert {row['stream'] for row in rows} == {'0'}
    with (R101R1 / 'ARENA_KERNEL_IDENTITY.tsv').open(newline='') as stream:
        accepted = [row for row in csv.DictReader(stream, delimiter='\t')
                    if row['arm'] == 'A0' and row['family'].startswith('AUTHOR_')]
    assert len(accepted) == 15
    differences = []
    for row, old in zip(rows[3:], accepted):
        assert row['exact_function'] == old['exact_demangled_name']
        if row['grid'] != old['grid'] or row['block'] != old['block']:
            differences.append({'roi_launch_index': row['roi_launch_index'],
                              'family': row['family'],
                              'current_grid': row['grid'], 'current_block': row['block'],
                              'accepted_grid': old['grid'], 'accepted_block': old['block']})
    if differences:
        print(json.dumps({'stratum_mismatches': differences}, indent=2))
        raise AssertionError('author arithmetic geometry differs from accepted R101R1')
    with (ROOT / 'NATIVE_KERNEL_BINDING_PREREG.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    scope = json.loads((ROOT / 'CAPTURE_SCOPE_PREREGISTRATION.json').read_text())
    assert scope['scope_id'] == 'R101_L512_FULL5_WITH_NORMALIZATION_V1'
    scope['selected_count'] = 18
    scope['exact_selector'] = {'function_regex': '.*',
                               'roi_start': 'cudaProfilerStart',
                               'roi_stop': 'cudaProfilerStop',
                               'selected_kernel_count': 18,
                               'census_global_launch_start_diagnostic_only': start,
                               'census_global_launch_end_exclusive_diagnostic_only': stop}
    (ROOT / 'CAPTURE_SCOPE_PREREGISTRATION.json').write_text(json.dumps(scope, indent=2, sort_keys=True) + '\n')
    receipt = {'scope_id': scope['scope_id'], 'selected_kernel_count': 18,
               'normalization_kernels': 3, 'ns_arithmetic_kernels': 15,
               'census_stdout_sha256': hashlib.sha256(LOG.read_bytes()).hexdigest(),
               'all_ns_exact_function_grid_block_match_accepted_r101r1': True,
               'census_global_start': start, 'census_global_end_exclusive': stop,
               'selector_uses_roi_marker_not_census_global_id': True,
               'output_exact': json.loads((ROOT / 'raw/census/DRIVER_RUN_RECEIPT.json').read_text())['output_exact']}
    (ROOT / 'CAPTURE_SELECTOR_FROZEN.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
