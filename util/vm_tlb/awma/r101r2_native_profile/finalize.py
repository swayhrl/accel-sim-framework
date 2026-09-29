#!/usr/bin/env python3
"""Close R101R2 native-side facts without replacing accepted timing authority."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path('/data/c16/awma/r101r2_s128_native_profile_20260929')
R101 = Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
WORKTREE = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101r2-s128-native-profile-109-v1')
STATE = 'NATIVE_PROFILE_MIXED'


def read(name: str) -> dict:
    return json.loads((ROOT / name).read_text())


def rows(name: str) -> list[dict]:
    with (ROOT / name).open(newline='') as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def fmt(value: float, decimals: int = 3) -> str:
    return f'{value:,.{decimals}f}'


def main() -> None:
    input_ = read('INPUT_AUTHORITY_PREREG.json')
    canary = read('PATH_CANARY.json')
    path = read('PATH_QUALIFICATION.json')
    static = rows('STATIC_SASS_SUMMARY.tsv')
    metric_set = read('NCU_METRIC_SET.json')
    analysis = read('NCU_ANALYSIS.json')
    families = rows('NCU_FAMILY_SUMMARY.tsv')
    assert input_['input_payload_sha256'] == '09358f3f21265a9c3a8cdd9681efdaa93a06db7c8d1e1afdbb017e60f0e85544'
    assert canary['same_map_pair_author_tolerance_pass']
    assert all(path['arms'][arm]['exact_author_kernel_name_grid_block_strata_match_accepted_R101']
               for arm in ('F128', 'K128'))
    assert analysis['source_path_and_profile_strata_qualified']
    assert analysis['kernel_counts'] == {'F128': 3, 'K128': 18}
    assert len([row for row in static if row['cubin_sha256'] != 'UNAVAILABLE_LIBRARY_CUBIN']) == 5
    assert metric_set['bounded_metric_engineering_retry']['one_same_config_retry_per_arm']
    for arm in ('F128', 'K128'):
        target = read(f'raw/ncu/{arm}/TARGET_RECEIPT.json')
        assert target['accepted_output_bitwise']
        assert (ROOT / 'raw/ncu' / arm / f'{arm}.ncu-rep').is_file()
        assert (ROOT / 'raw/ncu' / arm / 'ATTEMPT0_OMITTED_LDGSTS_METRIC' / f'{arm}.ncu-rep').is_file()
    author_source = json.loads((R101 / 'R101_SOURCE_RECEIPT.json').read_text())
    model_identity = json.loads((R101 / 'MODEL_IDENTITY_RECEIPT.json').read_text())
    environment = json.loads((R101 / 'ENVIRONMENT_RECEIPT.json').read_text())
    receipt = {'stage': input_['stage'], 'status': 'R101R2_NATIVE_PROFILE_PASS',
               'native_side_classification': STATE,
               'accepted_input_payload_sha256': input_['input_payload_sha256'],
               'accepted_r101_timing_authority_sha': input_['accepted_r101_sha'],
               'source_commit': author_source['commit'],
               'source_sha256': author_source['source_sha256'],
               'accepted_model_identity': model_identity,
               'environment': environment,
               'accepted_F128_output_sha256': input_['accepted_f128_output_sha256'],
               'accepted_K128_output_sha256': input_['accepted_k128_output_sha256'],
               'canary_F128_output_sha256': canary['arms']['F128']['graph_output_sha256'],
               'canary_K128_output_sha256': canary['arms']['K128']['graph_output_sha256'],
               'same_map_author_tolerance_pass': True,
               'graph_kernel_counts': analysis['kernel_counts'],
               'exact_author_kernel_strata_match_accepted_R101': True,
               'static_selected_unique_cubins': 5,
               'NCU_final_profile_bundles': {'F128': 1, 'K128': 1},
               'NCU_bounded_retry': 'one prior attempt per arm archived due supported LDGSTS metric omission',
               'metric_set_sha256': sha(ROOT / 'NCU_METRIC_SET.json'),
               'NCU_time_not_primary': True,
               'no_new_gradient_model_holdout_or_timing_experiment': True}
    (ROOT / 'INPUT_AND_PATH_RECEIPT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    (ROOT / 'raw/ATTEMPT0_OMITTED_LDGSTS_METRIC/ATTEMPT_STATUS.json').write_text(
        json.dumps({'status': 'OBSOLETE_METRIC_ENGINEERING',
                    'reason': 'LDG/LD counter omits supported separate LDGSTS warp-instruction class seen in source SASS',
                    'not_selected_from_performance': True,
                    'same_frozen_source_config_for_bounded_retry': True,
                    'formal_results_only_from_retry': True}, indent=2, sort_keys=True) + '\n')
    total = analysis['total_additive_counters']
    units = analysis['metric_units']
    metrics = [
        ('Executed warp instructions', 'smsp__inst_executed.sum'),
        ('Issued warp instructions', 'smsp__inst_issued.sum'),
        ('Direct global LDG/LD warp instructions', 'smsp__sass_inst_executed_op_global_ld.sum'),
        ('Async global→shared LDGSTS warp instructions', 'smsp__inst_executed_op_ldgsts.sum'),
        ('Global STG/ST warp instructions', 'smsp__sass_inst_executed_op_global_st.sum'),
        ('L1/TEX requested bytes', 'l1tex__t_bytes.sum'),
        ('L2 requested bytes', 'lts__t_bytes.sum'),
        ('DRAM read bytes', 'dram__bytes_read.sum'),
        ('DRAM write bytes', 'dram__bytes_write.sum'),
        ('HMMA warp instructions', 'smsp__inst_executed_pipe_tensor_op_hmma.sum'),
        ('Active SM cycles summed across kernels', 'sm__cycles_active.sum'),
    ]
    table = ['| Measured quantity | F128 | K128 | F/K |', '| --- | ---: | ---: | ---: |']
    for label, metric in metrics:
        f, k = total['F128'][metric], total['K128'][metric]
        table.append(f'| {label} ({units[metric]}) | {fmt(f)} | {fmt(k)} | {fmt(f/k, 4) if k else "—"} |')
    combined = analysis['combined_global_read_issue']
    f_read = combined['F128']['derived_disjoint_LDG_LD_plus_LDGSTS_warp_instructions']
    k_read = combined['K128']['derived_disjoint_LDG_LD_plus_LDGSTS_warp_instructions']
    table.append(f'| Derived LDG/LD + LDGSTS issue (warp inst) | {fmt(f_read)} | {fmt(k_read)} | {fmt(f_read/k_read, 4)} |')
    family_table = [f'| Arm | Family | Launches | Executed warp inst | LDG/LD | LDGSTS | STG/ST | HMMA | Active cycles | Occupancy % | Eligible warps/active cycle | Registers/thread | Shared/block ({units["launch__shared_mem_per_block"]}) |',
                    '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for row in families:
        family_table.append('| ' + ' | '.join([
            row['arm'], row['family'], row['kernel_launches'],
            fmt(float(row['smsp__inst_executed.sum']), 0),
            fmt(float(row['smsp__sass_inst_executed_op_global_ld.sum']), 0),
            fmt(float(row['smsp__inst_executed_op_ldgsts.sum']), 0),
            fmt(float(row['smsp__sass_inst_executed_op_global_st.sum']), 0),
            fmt(float(row['smsp__inst_executed_pipe_tensor_op_hmma.sum']), 0),
            fmt(float(row['sm__cycles_active.sum']), 0),
            fmt(float(row['sm__warps_active.avg.pct_of_peak_sustained_active']), 2),
            fmt(float(row['smsp__warps_eligible.avg.per_cycle_active']), 2),
            fmt(float(row['launch__registers_per_thread']), 0),
            fmt(float(row['launch__shared_mem_per_block']), 3),
        ]) + ' |')
    accepted = input_['accepted_graph_median_ms']
    intro = (
        '# R101R2 S128 Native execution profile interpretation\n\n'
        f'**Native-side classification: `{STATE}`.** This is a diagnostic fact pack for joint '
        'review with Lane E O2, not the final R101R2 outcome. The accepted R101 graph timing '
        f'remains F128 {accepted["F128"]:.6f} ms versus K128 {accepted["K128"]:.6f} ms '
        f'({100*input_["accepted_same_map_graph_improvement_fraction"]:.4f}% F128 improvement). '
        'No NCU replay duration replaces that timing.\n\n'
        'All graph-node additive counters, including two small graph-runtime fill nodes per arm:\n\n'
    )
    outro = (
        'F128 removes 61.60% of executed warp instructions and changes NS core from 15 '
        'arithmetic kernel launches to one fused launch, yet executes 20% more HMMA warp '
        'instructions. It also removes most global-memory instruction and hierarchy traffic. '
        'These simultaneous changes support clear execution-work reduction but do not '
        'isolate whether instruction issue, dependency/launch organization, or memory service '
        'caused the accepted 20.86% timing response. Thus `NATIVE_PROFILE_MIXED` is the '
        'appropriate Native-only label.\n\n'
        'The direct global-load metric counts LDG/LD; K128 also uses LDGSTS global→shared '
        'instructions, measured separately. The derived sum above combines two distinct '
        'warp-opcode classes and is **not** one hardware counter or per-thread instruction '
        'count. Static SASS counts in `STATIC_SASS_SUMMARY.tsv` are per selected binary; '
        'they are not dynamic counts or weighted speedups. Active-cycle sums are profiler '
        'counters, not graph elapsed time. L1/TEX/L2 requested bytes and DRAM bytes are '
        'different hierarchy semantics, not interchangeable. No causality or novelty is '
        'claimed from these counters alone.\n\n'
        'Two requested names were not supported on this SM89 NCU build: '
        '`smsp__inst_executed_pipe_fp32.sum` and `smsp__warps_issued.sum`. FMA and issued '
        'instructions are separately named supported quantities, never silent substitutes. '
        'The first two reports omitted the available LDGSTS class and are archived as '
        'ATTEMPT0. One source-motivated metric-engineering retry per arm added exactly '
        '`smsp__inst_executed_op_ldgsts.sum` to the frozen set; it did not change input, '
        'source, configurations or performance selection. Full counter/unit/aggregation '
        'bindings are in `NCU_RAW_METRIC_BINDING.tsv`.\n'
    )
    text = (intro + '\n'.join(table) + '\n\n'
            + 'Family decomposition (resource entries are per-family medians in raw NCU units, not sums):\n\n'
            + '\n'.join(family_table) + '\n\n' + outro)
    (ROOT / 'NATIVE_PROFILE_INTERPRETATION.md').write_text(text)
    (ROOT / 'FINAL_DECISION.md').write_text(
        '# Final producer decision\n\n'
        '`R101R2_NATIVE_PROFILE_PASS`; Native-side label `NATIVE_PROFILE_MIXED`. '
        'Publish facts independently of Lane E, then STOP. No new mechanism, holdout, '
        'gradient, model, primary timing or Accel-Sim run is authorized here.\n'
    )
    print(json.dumps({'status': receipt['status'], 'classification': STATE,
                      'executed_instruction_ratio': total['F128']['smsp__inst_executed.sum'] / total['K128']['smsp__inst_executed.sum'],
                      'derived_global_read_issue_ratio': f_read / k_read,
                      'HMMA_ratio': total['F128']['smsp__inst_executed_pipe_tensor_op_hmma.sum'] / total['K128']['smsp__inst_executed_pipe_tensor_op_hmma.sum']}, sort_keys=True))


if __name__ == '__main__':
    main()
