#!/usr/bin/env python3
"""Separate NSYS graph-node canary for A0 arena versus D2 persist+discard."""
from __future__ import annotations

import json

import torch

from arena import Persistence, capture_arena, make_arena
from core import ROOT, Discard, load_tiles


def main() -> None:
    assert json.loads((ROOT / 'D2_PERSISTENCE_RECEIPT.json').read_text())['output_bitwise_with_A0']
    prereg = json.loads((ROOT / 'D2_PERSISTENCE_PREREGISTRATION.json').read_text())
    x = load_tiles('discovery', 512)
    policy = Persistence()
    assert policy.set_limit(prereg['set_aside_requested_bytes']) == prereg['set_aside_requested_bytes']
    policy.reset()
    with torch.no_grad():
        a0_arena = make_arena(x)
        d2_arena = make_arena(x)
        a0_graph, a0, _ = capture_arena(x, a0_arena, None, None)
        d2_graph, d2, applied = capture_arena(x, d2_arena, Discard(), policy)
        assert torch.equal(a0, d2) and applied >= 30
        expected = torch.load(ROOT / 'raw/semantic_outputs.pt',
                              weights_only=True, map_location='cpu')['K512_B0'].to('cuda:0')
        for arm, graph, output in (
            ('A0', a0_graph, a0), ('D2', d2_graph, d2),
        ):
            label = f'R101R1_ARENA_L512_{arm}_GRAPH'
            torch.cuda.nvtx.range_push(label)
            graph.replay()
            torch.cuda.synchronize()
            torch.cuda.nvtx.range_pop()
            assert bool(torch.isfinite(output).all()) and bool(torch.equal(output, expected))
            print(json.dumps({'arm': arm, 'nvtx_label': label,
                              'output_finite': True}), flush=True)
    policy.reset()


if __name__ == '__main__':
    main()
