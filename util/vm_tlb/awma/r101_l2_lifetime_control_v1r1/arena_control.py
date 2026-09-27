#!/usr/bin/env python3
"""Sequential A0 arena then D2 graph-policy semantic admission."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json

import torch

from arena import Persistence, capture_arena, make_arena
from core import ROOT, Discard, load_tiles


def tensor_sha(value: torch.Tensor) -> str:
    return hashlib.sha256(value.detach().contiguous().view(torch.uint8).cpu().numpy().tobytes()).hexdigest()


def check_liveness(graph: torch.cuda.CUDAGraph, output: torch.Tensor,
                   x: torch.Tensor, frozen: torch.Tensor) -> dict:
    repeated = []
    for _ in range(2):
        graph.replay()
        torch.cuda.synchronize()
        repeated.append(bool(torch.equal(output, frozen)))
    old = x[0, 0, 0].clone()
    x[0, 0, 0] = old + 1.0
    graph.replay()
    torch.cuda.synchronize()
    changed = not bool(torch.equal(output, frozen))
    x[0, 0, 0] = old
    graph.replay()
    torch.cuda.synchronize()
    restored = bool(torch.equal(output, frozen))
    return {'repeat_bitwise': all(repeated), 'perturb_changed': changed,
            'restore_bitwise': restored, 'finite': bool(torch.isfinite(output).all())}


def main(stage: str) -> None:
    prereg = json.loads((ROOT / 'D2_PERSISTENCE_PREREGISTRATION.json').read_text())
    assert prereg['region_choice'] == 'full A+B, no fallback to A only'
    x = load_tiles('discovery', 512)
    expected = torch.load(ROOT / 'raw/semantic_outputs.pt',
                          weights_only=True, map_location='cpu')['K512_B0'].to('cuda:0')
    policy = Persistence()
    actual_limit = policy.set_limit(prereg['set_aside_requested_bytes'])
    assert actual_limit == prereg['set_aside_requested_bytes']
    policy.reset()
    with torch.no_grad():
        a0_arena = make_arena(x)
        assert int(torch.count_nonzero(a0_arena)) == 0
        a0_graph, a0, a0_attrs = capture_arena(x, a0_arena, None, None)
        assert a0_attrs == 0
        a0_frozen = a0.detach().clone()
        a0_matches_original = bool(torch.equal(a0_frozen, expected))
        a0_liveness = check_liveness(a0_graph, a0, x, a0_frozen)
        a0_record = {
            'arm': 'L512_A0_ARENA_GRAPH', 'output_bitwise_with_B0': a0_matches_original,
            'output_sha256': tensor_sha(a0_frozen),
            'arena_shape': list(a0_arena.shape),
            'arena_base_128_aligned': a0_arena.data_ptr() % 128 == 0,
            'A_offset_bytes': 0, 'B_offset_bytes': a0_arena[1].data_ptr() - a0_arena[0].data_ptr(),
            'arena_initial_zero_verified': True,
            'set_aside_bytes': actual_limit,
            'graph_persistence_attributes': a0_attrs,
            **a0_liveness,
        }
        assert a0_matches_original and all(a0_liveness.values())
        (ROOT / 'ARENA_CONTROL_CANARY.json').write_text(json.dumps(a0_record, indent=2, sort_keys=True) + '\n')
        print(json.dumps(a0_record), flush=True)
        if stage == 'a0':
            with (ROOT / 'ARENA_CONTROL.tsv').open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=list(a0_record), delimiter='\t', lineterminator='\n')
                writer.writeheader()
                writer.writerow(a0_record)
            return
        assert (ROOT / 'ARENA_CONTROL.tsv').is_file()
        policy.reset()
        d2_arena = make_arena(x)
        assert int(torch.count_nonzero(d2_arena)) == 0
        d2_graph, d2, applied = capture_arena(x, d2_arena, Discard(), policy)
        d2_frozen = d2.detach().clone()
        d2_bitwise = bool(torch.equal(d2_frozen, a0_frozen))
        d2_liveness = check_liveness(d2_graph, d2, x, d2_frozen)
        d2_record = {
            'arm': 'L512_D2_PERSIST_DISCARD_GRAPH',
            'output_bitwise_with_A0': d2_bitwise,
            'output_sha256': tensor_sha(d2_frozen),
            'set_aside_bytes': actual_limit,
            'policy_window_base_ptr': d2_arena.data_ptr(),
            'policy_window_bytes': d2_arena.numel() * d2_arena.element_size(),
            'policy_nodes_set_and_readback_verified': applied,
            'policy_hit_ratio': 1.0,
            'policy_hit_property': 'cudaAccessPropertyPersisting',
            'policy_miss_property': 'cudaAccessPropertyNormal',
            'arena_initial_zero_verified': True,
            **d2_liveness,
        }
        print(json.dumps(d2_record), flush=True)
        if not (d2_bitwise and all(d2_liveness.values()) and applied >= 30):
            (ROOT / 'raw/D2_CANARY_DIAGNOSTIC_FAILURE.json').write_text(
                json.dumps(d2_record, indent=2, sort_keys=True) + '\n')
            raise AssertionError('D2 semantic/liveness/graph-policy-node gate failed')
        (ROOT / 'D2_PERSISTENCE_RECEIPT.json').write_text(json.dumps(d2_record, indent=2, sort_keys=True) + '\n')
        with (ROOT / 'D2_SEMANTIC_RESULTS.tsv').open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(d2_record), delimiter='\t', lineterminator='\n')
            writer.writeheader()
            writer.writerow(d2_record)
    policy.reset()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=['a0', 'd2'], required=True)
    main(parser.parse_args().stage)
