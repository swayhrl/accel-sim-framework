#!/usr/bin/env python3
"""One exact graph replay for separate B0/D1 NCU traffic profiling."""
from __future__ import annotations

import argparse
import json

import torch

from core import ROOT, Discard, capture, load_tiles


def main(shape: str, arm: str) -> None:
    edge = 128 if shape == 'K128' else 512
    assert shape in ('K128', 'L512') and arm in ('B0', 'D1')
    gate = json.loads((ROOT / 'NSYS_PATH_QUALIFICATION.json').read_text())
    assert gate[f'K{edge}_PATH_GATE']['b0_d1_exact_nondiscard_name_grid_block_sequence_equal']
    x = load_tiles('discovery', edge)
    with torch.no_grad():
        graph, output = capture(x, None if arm == 'B0' else Discard())
        expected = torch.load(ROOT / 'raw/semantic_outputs.pt',
                              weights_only=True, map_location='cpu')[f'K{edge}_{arm}'].to('cuda:0')
        assert torch.equal(output, expected)
        label = f'R101R1_NCU_{shape}_{arm}'
        torch.cuda.nvtx.range_push(label)
        graph.replay()
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_pop()
        assert torch.equal(output, expected)
    receipt = {'shape': shape, 'arm': arm, 'edge': edge,
               'nvtx_label': label, 'graph_node_profiling': True,
               'app_replay_cache_control_none': True,
               'output_bitwise_with_untimed_canary': True,
               'ncu_duration_not_primary': True}
    path = ROOT / 'raw/ncu' / f'{shape}_{arm}'
    path.mkdir(parents=True, exist_ok=True)
    (path / 'TARGET_RECEIPT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--shape', choices=['K128', 'L512'], required=True)
    parser.add_argument('--arm', choices=['B0', 'D1'], required=True)
    args = parser.parse_args()
    main(args.shape, args.arm)
