#!/usr/bin/env python3
"""Machine-checkable R101R1 decision gates; no CUDA use."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_l2_lifetime_control_v1r1_20260927')
STATE = 'R101R1_EXISTING_L2_CONTROL_INSUFFICIENT_READY_FOR_ARCH_REVIEW'


def read(name: str) -> dict:
    return json.loads((ROOT / name).read_text())


def main() -> None:
    identity = read('R101R1_BASELINE_IDENTITY.json')
    capability = read('R101R1_L2_CAPABILITY_RECEIPT.json')
    semantic = read('SEMANTIC_RECEIPT.json')
    path = read('NSYS_PATH_QUALIFICATION.json')
    timing = read('TIMING_ANALYSIS.json')
    ncu = read('NCU_SUMMARY.json')
    d2 = read('D2_PERSISTENCE_RECEIPT.json')
    arena_path = read('ARENA_NSYS_PATH_QUALIFICATION.json')
    arena_timing = read('ARENA_TIMING_ANALYSIS.json')
    arena_ncu = read('ARENA_NCU_SUMMARY.json')['result']
    with (ROOT / 'TRAFFIC_RESULTS.tsv').open(newline='') as stream:
        traffic = {row['shape']: row for row in csv.DictReader(stream, delimiter='\t')}
    assert identity['accepted_r101_execution_sha'] == 'cfbe6503585fa1b10d979db5d26fb9be3a80e563'
    assert capability['runtime_smoke_passed'] and capability['device']['sm_major'] == 8
    assert semantic['discovery_bitwise_and_liveness_qualified']
    assert path['K128_PATH_GATE']['b0_d1_exact_nondiscard_name_grid_block_sequence_equal']
    assert path['K512_PATH_GATE']['b0_d1_exact_nondiscard_name_grid_block_sequence_equal']
    assert traffic['K128']['scientific_pair_status'] == 'UNQUALIFIED_AUTOTUNE_DRIFT_NO_REDUCTION_CLAIM'
    assert traffic['L512']['scientific_pair_status'] == 'QUALIFIED'
    d1_reduction = float(traffic['L512']['ns_dram_write_reduction_fraction'])
    assert abs(d1_reduction - ncu['d1_write_reduction_gate_l512']) < 1e-12
    assert d1_reduction < 0.5
    assert not timing['L512']['d1_material_speedup']
    assert d2['output_bitwise_with_A0']
    assert d2['set_aside_bytes'] == 46137344
    assert arena_path['path_gate']['a0_d2_exact_nondiscard_name_grid_block_sequence_equal']
    assert arena_path['path_gate']['all_relevant_producer_consumer_nodes_policy_attached_and_readback_verified']
    assert arena_ncu['a0_d2_arithmetic_strata_equal']
    assert arena_ncu['d2_ns_write_reduction_fraction_vs_a0_arena'] < 0.5
    assert not arena_timing['d2_material_speedup']
    holdout = {
        'run': False,
        'reason': 'Neither D1 nor D2 has a >=5% and >3x-noise timing benefit; Goal Section 12 forbids holdout',
        'accepted_holdout_payload_hashes_remain_verified': True,
    }
    (ROOT / 'HOLDOUT_GATE.json').write_text(json.dumps(holdout, indent=2, sort_keys=True) + '\n')
    gates = {
        'final_state': STATE,
        'accepted_r101_input_and_problem_preserved': True,
        'sm89_ptx_sass_runtime_discard_qualified': True,
        'd1_exact_semantics_and_liveness': True,
        'd1_arithmetic_identical_in_graph': True,
        'd1_l512_write_reduction_fraction': d1_reduction,
        'd1_l512_write_reduction_under_50pct': True,
        'd1_l512_timing_improvement_fraction': timing['L512']['d1_improvement_fraction'],
        'd1_l512_material_speedup': False,
        'd2_full_A_plus_B_window_and_setaside_bytes': d2['set_aside_bytes'],
        'd2_exact_semantics_and_liveness': True,
        'd2_relevant_graph_nodes_policy_readback': d2['policy_nodes_set_and_readback_verified'],
        'd2_l512_write_reduction_fraction_vs_arena_control':
            arena_ncu['d2_ns_write_reduction_fraction_vs_a0_arena'],
        'd2_l512_timing_improvement_fraction': arena_timing['d2_improvement_fraction'],
        'd2_material_speedup': False,
        'k128_ncu_write_reduction_claim': None,
        'k128_ncu_limitation': 'isolated NCU app autotune selected XXT block 128 B0 and 256 D1; two B0 attempts did not match; no K128 traffic ratio used',
        'holdout_run': False,
        'mechanism_or_simulator_executed': False,
    }
    (ROOT / 'FINAL_GATES.json').write_text(json.dumps(gates, indent=2, sort_keys=True) + '\n')
    print(json.dumps(gates, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
