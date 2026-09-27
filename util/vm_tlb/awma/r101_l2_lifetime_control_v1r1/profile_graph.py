#!/usr/bin/env python3
"""Separate NSYS graph-node qualification; profiler times are not primary."""
from __future__ import annotations

import json

import torch

from core import ROOT, Discard, capture, load_tiles


def main() -> None:
    receipt = json.loads((ROOT / 'SEMANTIC_RECEIPT.json').read_text())
    assert receipt['discovery_bitwise_and_liveness_qualified']
    discard = Discard()
    records = []
    with torch.no_grad():
        for edge in (128, 512):
            x = load_tiles('discovery', edge)
            b0_graph, b0 = capture(x, None)
            d1_graph, d1 = capture(x, discard)
            assert torch.equal(b0, d1)
            for arm, graph, output in (('B0', b0_graph, b0), ('D1', d1_graph, d1)):
                label = f'R101R1_OPERATOR_K{edge}_{arm}_GRAPH'
                torch.cuda.nvtx.range_push(label)
                graph.replay()
                torch.cuda.synchronize()
                torch.cuda.nvtx.range_pop()
                assert bool(torch.isfinite(output).all())
                records.append({'arm': f'K{edge}_{arm}_GRAPH', 'nvtx_label': label,
                                'output_finite': True})
                print(json.dumps(records[-1]), flush=True)
    (ROOT / 'NSYS_PROFILE_RECEIPT.json').write_text(json.dumps(records, indent=2) + '\n')


if __name__ == '__main__':
    main()
