#!/usr/bin/env python3
"""Freeze region-level kernel-boundary lifetime before FORMAL capture."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_transient_l2_sim_capture_20260927')


def main() -> None:
    selector = json.loads((ROOT / 'CAPTURE_SELECTOR_FROZEN.json').read_text())
    assert selector['selected_kernel_count'] == 18
    rows = []
    for index in range(3):
        rows.append({'roi_launch_index': index, 'phase': 'NORMALIZATION',
                     'iteration': None, 'family': 'NORMALIZATION',
                     'A_after': 'UNDEFINED_NOT_READ', 'B_after': 'UNDEFINED_NOT_READ',
                     'X0_after': 'LIVE' if index == 2 else 'NOT_YET_LIVE',
                     'X1_after': 'UNDEFINED_NOT_READ',
                     'boundary_rule': 'X0 becomes fully normalized/live only after final normalization kernel'})
    for iteration in range(5):
        current = 'X0' if iteration % 2 == 0 else 'X1'
        next_ = 'X1' if iteration % 2 == 0 else 'X0'
        for position, family in enumerate(('XXT', 'BA', 'BMM_ADD')):
            status = {'A': 'DEAD', 'B': 'DEAD', current: 'LIVE', next_: 'DEAD'}
            if position == 0:
                status['A'] = 'LIVE'
                rule = 'XXT completely writes A; A is live for BA'
            elif position == 1:
                status['A'] = 'DEAD'
                status['B'] = 'LIVE'
                rule = 'BA consumed A and completely writes B; A dead, B live for BMM-add'
            else:
                status['B'] = 'DEAD'
                status[current] = 'DEAD'
                status[next_] = 'LIVE'
                rule = 'BMM-add consumed B and old X, completely writes next X; B/old X dead'
            rows.append({'roi_launch_index': 3 + 3 * iteration + position,
                         'phase': 'NS', 'iteration': iteration, 'family': family,
                         'A_after': status['A'], 'B_after': status['B'],
                         'X0_after': status['X0'], 'X1_after': status['X1'],
                         'boundary_rule': rule})
    assert len(rows) == 18
    template = {'scope_id': 'R101_L512_FULL5_WITH_NORMALIZATION_V1',
                'scientific_input_sha256': '1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234',
                'kernel_boundary_only': True, 'per_line_future_last_use': False,
                'regions': ['A', 'B', 'X0', 'X1'],
                'final_live_region': 'X1',
                'rows': rows}
    (ROOT / 'REGION_LIFETIME_TEMPLATE.json').write_text(json.dumps(template, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'frozen_kernel_boundaries': len(rows),
                      'final_live_region': template['final_live_region']}))


if __name__ == '__main__':
    main()
