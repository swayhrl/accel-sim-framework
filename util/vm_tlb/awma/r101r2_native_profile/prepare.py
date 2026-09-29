#!/usr/bin/env python3
"""Offline accepted S128 payload/source/timing inheritance closure."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path('/data/c16/awma/r101r2_s128_native_profile_20260929')
R101 = Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
SOURCE = R101 / 'source/himuon'
WORKTREE = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101r2-s128-native-profile-109-v1')
PAYLOAD = R101 / 'raw/discovery_tiles_T128.pt'
EXPECTED_SHA = '09358f3f21265a9c3a8cdd9681efdaa93a06db7c8d1e1afdbb017e60f0e85544'


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def main() -> None:
    assert subprocess.check_output(['git', '-C', str(WORKTREE), 'rev-parse', 'HEAD'], text=True).strip() == '8542a4d37372d586591ff9911929e523645e88f5'
    assert subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip() == 'af89eda9a0176effed99e1fe19cc1f8a1a2c9588'
    assert sha(PAYLOAD) == EXPECTED_SHA
    tile = json.loads((R101 / 'R101_TILE_INPUT_RECEIPT_DISCOVERY.json').read_text())['tiles']['128']
    assert tile['payload_sha256'] == EXPECTED_SHA and tile['shape'] == [581, 128, 128]
    source = json.loads((R101 / 'R101_SOURCE_RECEIPT.json').read_text())
    for rel, expected in source['source_sha256'].items():
        assert sha(SOURCE / rel) == expected
    numerical = (R101 / 'NUMERICAL_QUALIFICATION_DISCOVERY.tsv').read_text()
    assert 'b47a423eb93fbe95fd79218c577524e9241178f9c838b6e82bdd4f3b2669d53a' in numerical
    assert 'f3cdbddef0a3ca9849100f5460bb2ef3ea2021caede8c61ec468854975c482cf' in numerical
    timing = json.loads((R101 / 'GRAPH_CONTROL_ANALYSIS.json').read_text())
    assert abs(timing['same_map_graph']['improvement_fraction'] - 0.20863274448675112) < 1e-12
    assert json.loads((ROOT / 'NCU_METRIC_SET.json').read_text())['selected_profile_metrics']
    receipt = {
        'stage': 'AWMA_R101R2_S128_NATIVE_EXECUTION_PROFILE_V1',
        'handoff_sha': '8542a4d37372d586591ff9911929e523645e88f5',
        'accepted_r101_sha': 'cfbe6503585fa1b10d979db5d26fb9be3a80e563',
        'input_payload_path': str(PAYLOAD),
        'input_payload_sha256': EXPECTED_SHA,
        'input_shape': [581, 128, 128],
        'input_dtype': 'torch.bfloat16',
        'scientific_input_class': 'REAL_MODEL_FIRST_STEP_GRADIENT_DERIVED_MICROSTATE',
        'author_source_commit': source['commit'],
        'author_source_sha256': source['source_sha256'],
        'coefficients': source['coefficients'], 'steps': 5,
        'accepted_f128_output_sha256': 'b47a423eb93fbe95fd79218c577524e9241178f9c838b6e82bdd4f3b2669d53a',
        'accepted_k128_output_sha256': 'f3cdbddef0a3ca9849100f5460bb2ef3ea2021caede8c61ec468854975c482cf',
        'accepted_graph_median_ms': {
            'F128': timing['arms']['F128_GRAPH']['median_gpu_ms'],
            'K128': timing['arms']['K128_GRAPH']['median_gpu_ms'],
        },
        'accepted_same_map_graph_improvement_fraction': timing['same_map_graph']['improvement_fraction'],
        'accepted_author_numeric_tolerance': {'rtol': 1e-2, 'atol': 1e-2},
        'new_gradient_generation': False, 'new_model_download': False,
        'new_timing_authority': False,
    }
    (ROOT / 'INPUT_AUTHORITY_PREREG.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    (ROOT / 'R101_INHERITANCE.md').write_text(
        '# R101 inheritance\n\n'
        'Accepted R101 at `cfbe6503585fa1b10d979db5d26fb9be3a80e563` remains frozen. '
        f'The exact S128 discovery payload `{EXPECTED_SHA}`, pinned HiMuon source and '
        'numerical outputs were hash-verified. Accepted graph medians are F128 '
        f'{receipt["accepted_graph_median_ms"]["F128"]:.6f} ms and K128 '
        f'{receipt["accepted_graph_median_ms"]["K128"]:.6f} ms; '
        f'F128 improvement {100*receipt["accepted_same_map_graph_improvement_fraction"]:.4f}%. '
        'They are timing authority; R101R2 NCU durations are diagnostic only. '
        'No gradient, model, tile, step, coefficient or holdout was regenerated.\n'
    )
    print(json.dumps({'payload_sha256': EXPECTED_SHA,
                      'source_commit': source['commit'],
                      'accepted_graph_improvement': receipt['accepted_same_map_graph_improvement_fraction']}))


if __name__ == '__main__':
    main()
