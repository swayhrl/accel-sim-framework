#!/usr/bin/env python3
"""Admit full-five-step capture from real first-iteration canary volume."""
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_transient_l2_sim_capture_20260927')


def main() -> None:
    canary = ROOT / 'raw/canary_multi'
    terminal = json.loads((canary / 'TERMINAL_RECEIPT.json').read_text())
    assert terminal['status'] == 'COMPLETE' and terminal['selected_kernels'] == 3
    assert terminal['drop_count'] == terminal['overflow_count'] == 0
    with (canary / 'TRACE_MEMBER_MANIFEST.tsv').open(newline='') as stream:
        rows = list(csv.DictReader(stream, delimiter='\t'))
    assert len(rows) == 3 and all(row['grammar_status'] == 'PASS' for row in rows)
    raw_one = sum(int(row['raw_bytes']) for row in rows)
    traceg_one = sum(int(row['traceg_bytes']) for row in rows)
    scope = json.loads((ROOT / 'CAPTURE_SCOPE_PREREGISTRATION.json').read_text())
    assert scope['selected_count'] == 18
    # Five exact repetitions of these three NS families; conservatively add
    # one extra whole iteration for the three normalization kernels.
    conservative_raw = 6 * raw_one
    free = shutil.disk_usage(ROOT).free
    admit = conservative_raw < scope['per_run_raw_cap_bytes'] and conservative_raw * 2 < free
    result = {
        'first_complete_iteration_raw_bytes': raw_one,
        'first_complete_iteration_traceg_bytes': traceg_one,
        'full5_conservative_raw_bound_bytes_six_iteration_equivalents': conservative_raw,
        'formal_raw_cap_bytes': scope['per_run_raw_cap_bytes'],
        'free_bytes_at_admission': free,
        'full5_admitted': admit,
        'scope_chosen': 'R101_L512_FULL5_WITH_NORMALIZATION_V1' if admit else 'VOLUME_BLOCKED_NEEDS_CONTEXT2_PREREG',
        'not_selected_from_performance': True,
    }
    (ROOT / 'VOLUME_ADMISSION.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2))
    assert admit


if __name__ == '__main__':
    main()
