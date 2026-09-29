#!/usr/bin/env python3
"""One exact F128 or K128 CUDA Graph replay for frozen NCU metrics."""
from __future__ import annotations

import argparse
import json

import torch

from core import ROOT, capture, freeze_author_configs, load_input_and_reference


def main(arm: str) -> None:
    assert arm in ('F128', 'K128')
    prereg = json.loads((ROOT / 'INPUT_AUTHORITY_PREREG.json').read_text())
    path = json.loads((ROOT / 'PATH_QUALIFICATION.json').read_text())
    metrics = json.loads((ROOT / 'NCU_METRIC_SET.json').read_text())
    assert path['arms'][arm]['exact_author_kernel_name_grid_block_strata_match_accepted_R101']
    assert prereg['input_payload_sha256'] == '09358f3f21265a9c3a8cdd9681efdaa93a06db7c8d1e1afdbb017e60f0e85544'
    assert metrics['selected_profile_metrics'] and metrics['selected_launch_metrics']
    frozen = freeze_author_configs()
    x, reference = load_input_and_reference()
    with torch.no_grad():
        graph, output, canary = capture(arm, x, reference[arm])
        assert canary['graph_output_sha256'] == prereg[f'accepted_{arm.lower()}_output_sha256']
        label = f'R101R2_NCU_{arm}'
        torch.cuda.nvtx.range_push(label)
        graph.replay()
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_pop()
        output_bitwise = bool(torch.equal(output, reference[arm]))
        assert output_bitwise and bool(torch.isfinite(output).all())
    receipt = {'arm': arm, 'nvtx_label': label,
               'input_payload_sha256': prereg['input_payload_sha256'],
               'author_source_commit': prereg['author_source_commit'],
               'frozen_author_configs': frozen,
               'accepted_output_bitwise': output_bitwise,
               'graph_path_prequalified': True,
               'ncu_duration_not_primary': True,
               'graph_profiling': 'node', 'replay_mode': 'application',
               'cache_control': 'none', 'clock_control': 'none'}
    outdir = ROOT / 'raw/ncu' / arm
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'TARGET_RECEIPT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'arm': arm, 'accepted_output_bitwise': output_bitwise,
                      'nvtx_label': label}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--arm', choices=['F128', 'K128'], required=True)
    main(parser.parse_args().arm)
