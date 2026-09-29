#!/usr/bin/env python3
"""Numerical/liveness and one diagnostic NSYS launch-path canary."""
from __future__ import annotations

import json

import torch

from core import ROOT, capture, freeze_author_configs, load_input_and_reference


def main() -> None:
    prereg = json.loads((ROOT / 'INPUT_AUTHORITY_PREREG.json').read_text())
    assert prereg['input_payload_sha256'] == '09358f3f21265a9c3a8cdd9681efdaa93a06db7c8d1e1afdbb017e60f0e85544'
    frozen = freeze_author_configs()
    x, reference = load_input_and_reference()
    arms = {}
    outputs = {}
    with torch.no_grad():
        for arm in ('F128', 'K128'):
            graph, output, receipt = capture(arm, x, reference[arm])
            arms[arm] = receipt
            outputs[arm] = output.detach().clone()
            torch.cuda.nvtx.range_push(f'R101R2_PATH_{arm}')
            graph.replay(); torch.cuda.synchronize()
            torch.cuda.nvtx.range_pop()
            assert torch.allclose(output, reference[arm], rtol=1e-2, atol=1e-2)
    same_map_pair = bool(torch.allclose(outputs['F128'], outputs['K128'], rtol=1e-2, atol=1e-2))
    assert same_map_pair
    result = {'stage': 'AWMA_R101R2_S128_NATIVE_EXECUTION_PROFILE_V1',
              'source_commit': 'af89eda9a0176effed99e1fe19cc1f8a1a2c9588',
              'input_payload_sha256': prereg['input_payload_sha256'],
              'tile_count': 581, 'tile_edge': 128,
              'frozen_author_launch_configs': frozen,
              'same_map_pair_author_tolerance_pass': same_map_pair,
              'arms': arms,
              'no_new_primary_timing': True}
    (ROOT / 'PATH_CANARY.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'same_map_pair_pass': same_map_pair,
                      'arm_output_hashes': {arm: row['graph_output_sha256'] for arm, row in arms.items()}},
                     sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
