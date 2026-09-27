#!/usr/bin/env python3
"""Single-process A0/D2 graph-node NCU pair: one D2 profile, shared autotune."""
from __future__ import annotations

import json

import torch

from arena import Persistence, capture_arena, make_arena
from core import ROOT, Discard, load_tiles


def main() -> None:
    prereg = json.loads((ROOT / 'D2_PERSISTENCE_PREREGISTRATION.json').read_text())
    gate = json.loads((ROOT / 'ARENA_NSYS_PATH_QUALIFICATION.json').read_text())['path_gate']
    assert gate['a0_d2_exact_nondiscard_name_grid_block_sequence_equal']
    x = load_tiles('discovery', 512)
    policy = Persistence()
    assert policy.set_limit(prereg['set_aside_requested_bytes']) == prereg['set_aside_requested_bytes']
    policy.reset()
    with torch.no_grad():
        a0_arena = make_arena(x)
        d2_arena = make_arena(x)
        a0_graph, a0, _ = capture_arena(x, a0_arena, None, None)
        d2_graph, d2, applied = capture_arena(x, d2_arena, Discard(), policy)
        assert applied == gate['attached_graph_kernel_nodes'] and torch.equal(a0, d2)
        expected = torch.load(ROOT / 'raw/semantic_outputs.pt',
                              weights_only=True, map_location='cpu')['K512_B0'].to('cuda:0')
        assert torch.equal(a0, expected)
        for arm, graph, output in (('A0', a0_graph, a0), ('D2', d2_graph, d2)):
            policy.reset()
            torch.cuda.synchronize()
            torch.cuda.nvtx.range_push(f'R101R1_NCU_ARENA_L512_{arm}')
            graph.replay()
            torch.cuda.synchronize()
            torch.cuda.nvtx.range_pop()
            good = bool(torch.equal(output, expected))
            print(json.dumps({'arm': arm, 'profiled_graph_output_bitwise': good}), flush=True)
            assert good
    policy.reset()
    receipt = {'a0_and_d2_same_process_autotune': True,
               'd2_profile_count': 1,
               'nvtx_children': ['R101R1_NCU_ARENA_L512_A0', 'R101R1_NCU_ARENA_L512_D2'],
               'outputs_bitwise_with_accepted_graph': True,
               'policy_nodes_attached_and_readback': applied,
               'app_replay_cache_control_none': True,
               'ncu_duration_not_primary': True}
    (ROOT / 'raw/ncu/ARENA_PAIR_TARGET_RECEIPT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
