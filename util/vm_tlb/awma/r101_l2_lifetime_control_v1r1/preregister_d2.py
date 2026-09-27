#!/usr/bin/env python3
"""Admit and freeze one A+B L512 access-policy window before D2 GPU work."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_l2_lifetime_control_v1r1_20260927')
WORKTREE = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-l2-lifetime-control-v1r1')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ncu = json.loads((ROOT / 'NCU_SUMMARY.json').read_text())
    reduction = ncu['d1_write_reduction_gate_l512']
    assert reduction < 0.5
    device = json.loads((ROOT / 'R101R1_L2_CAPABILITY_RECEIPT.json').read_text())['device']
    one = 44 * 512 * 512 * 2
    both = 2 * one
    assert one == 23068672 and both == 46137344
    assert device['persisting_l2_max_bytes'] >= both
    assert device['access_policy_max_window_bytes'] >= both
    layout = {
        'fixture': 'accepted discovery L512, 44 BF16 512x512 tiles',
        'arena_shape': [2, 44, 512, 512],
        'arena_dtype': 'torch.bfloat16',
        'arena_contiguous': True,
        'A_offset_bytes': 0,
        'B_offset_bytes': one,
        'one_buffer_bytes': one,
        'A_plus_B_bytes': both,
        'initial_arena_content': 'all zero; no scientific input, fully overwritten before use',
    }
    layout_sha = hashlib.sha256(json.dumps(layout, sort_keys=True).encode()).hexdigest()
    path = WORKTREE / 'util/vm_tlb/awma/r101_l2_lifetime_control_v1r1/persist.cu'
    prereg = {
        'd1_l512_qualified_write_reduction_fraction': reduction,
        'd2_admitted_because_d1_under_50pct': True,
        'region_choice': 'full A+B, no fallback to A only',
        'arena_layout': layout,
        'arena_layout_sha256': layout_sha,
        'set_aside_requested_bytes': both,
        'window_base': 'arena.data_ptr() at runtime, must be 128-byte aligned',
        'window_bytes': both,
        'hit_ratio': 1.0,
        'hit_property': 'cudaAccessPropertyPersisting',
        'miss_property': 'cudaAccessPropertyNormal',
        'graph_policy_api': 'cudaGraphKernelNodeSetAttribute on all kernel nodes of active capture graph',
        'A0_control': 'same contiguous arena, same arithmetic, no persistence, no discard',
        'D2': 'same contiguous arena and arithmetic, graph node persistence plus D1 dead-point discard',
        'paired_formal_repetitions': 7,
        'd2_ncu_profile_cap': 1,
        'no_parameter_sweep': True,
        'persist_source_sha256': sha(path),
        'persist_binary_sha256': sha(ROOT / 'build/libpersist.so'),
        'K128_ncu_pair_unqualified_due_autotune_drift': True,
        'L512_ncu_pair_qualified_and_decision_driving': True,
    }
    (ROOT / 'D2_PERSISTENCE_PREREGISTRATION.json').write_text(
        json.dumps(prereg, indent=2, sort_keys=True) + '\n')
    print(json.dumps(prereg, indent=2))


if __name__ == '__main__':
    main()
