#!/usr/bin/env python3
"""Freeze exact SM89-supported NCU metric semantics before profiling."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path('/data/c16/awma/r101r2_s128_native_profile_20260929')

# (scientific quantity, exact requested name, collection, additive across kernels)
REQUESTS = [
    ('executed_warp_instructions', 'smsp__inst_executed.sum', 'profiling', True),
    ('issued_warp_instructions', 'smsp__inst_issued.sum', 'profiling', True),
    ('global_load_warp_instructions', 'smsp__sass_inst_executed_op_global_ld.sum', 'profiling', True),
    ('async_global_to_shared_LDGSTS_warp_instructions', 'smsp__inst_executed_op_ldgsts.sum', 'profiling', True),
    ('global_store_warp_instructions', 'smsp__sass_inst_executed_op_global_st.sum', 'profiling', True),
    ('shared_load_warp_instructions', 'smsp__sass_inst_executed_op_shared_ld.sum', 'profiling', True),
    ('shared_store_warp_instructions', 'smsp__sass_inst_executed_op_shared_st.sum', 'profiling', True),
    ('tensor_hmma_warp_instructions', 'smsp__inst_executed_pipe_tensor_op_hmma.sum', 'profiling', True),
    ('fma_pipe_warp_instructions', 'smsp__inst_executed_pipe_fma.sum', 'profiling', True),
    ('alu_pipe_warp_instructions', 'smsp__inst_executed_pipe_alu.sum', 'profiling', True),
    ('fp32_pipe_warp_instructions', 'smsp__inst_executed_pipe_fp32.sum', 'profiling', True),
    ('issued_warps', 'smsp__warps_issued.sum', 'profiling', True),
    ('active_sm_cycles', 'sm__cycles_active.sum', 'profiling', True),
    ('active_warps_pct_occupancy', 'sm__warps_active.avg.pct_of_peak_sustained_active', 'profiling', False),
    ('eligible_warps_per_active_cycle', 'smsp__warps_eligible.avg.per_cycle_active', 'profiling', False),
    ('l1tex_global_load_sectors', 'l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum', 'profiling', True),
    ('l1tex_global_store_sectors', 'l1tex__t_sectors_pipe_lsu_mem_global_op_st.sum', 'profiling', True),
    ('l1tex_requested_bytes_total', 'l1tex__t_bytes.sum', 'profiling', True),
    ('l2_read_sectors', 'lts__t_sectors_op_read.sum', 'profiling', True),
    ('l2_write_sectors', 'lts__t_sectors_op_write.sum', 'profiling', True),
    ('l2_requested_bytes_total', 'lts__t_bytes.sum', 'profiling', True),
    ('dram_read_bytes', 'dram__bytes_read.sum', 'profiling', True),
    ('dram_write_bytes', 'dram__bytes_write.sum', 'profiling', True),
    ('registers_per_thread', 'launch__registers_per_thread', 'launch', False),
    ('shared_memory_per_block', 'launch__shared_mem_per_block', 'launch', False),
]


def parse_names(path: Path) -> set[str]:
    names = set()
    for line in path.read_text().splitlines():
        tokens = line.split()
        if len(tokens) > 1 and tokens[1] in ('Counter', 'Ratio', 'Throughput'):
            names.add(tokens[0])
    return names


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    profiling_file = ROOT / 'raw/ncu_supported_all.txt'
    launch_file = ROOT / 'raw/ncu_supported_launch.txt'
    available = {'profiling': parse_names(profiling_file), 'launch': parse_names(launch_file)}
    rows = []
    selected = []
    for meaning, metric, collection, additive in REQUESTS:
        support = metric in available[collection]
        rows.append({'scientific_quantity': meaning, 'exact_requested_metric': metric,
                     'collection': collection, 'availability': 'SUPPORTED' if support else 'UNSUPPORTED',
                     'selected_metric': metric if support else 'UNSUPPORTED',
                     'additive_across_kernel_launches': additive,
                     'semantic_note': 'Nearest metrics are separate rows; no silent substitution.'})
        if support:
            selected.append(metric)
    assert 'smsp__inst_executed.sum' in selected
    assert 'smsp__sass_inst_executed_op_global_ld.sum' in selected
    assert 'smsp__inst_executed_op_ldgsts.sum' in selected
    assert 'smsp__sass_inst_executed_op_global_st.sum' in selected
    assert 'dram__bytes_read.sum' in selected and 'dram__bytes_write.sum' in selected
    with (ROOT / 'NCU_METRIC_BINDING_PREREG.tsv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    profile_metrics = [row['selected_metric'] for row in rows
                       if row['collection'] == 'profiling' and row['availability'] == 'SUPPORTED']
    launch_metrics = [row['selected_metric'] for row in rows
                      if row['collection'] == 'launch' and row['availability'] == 'SUPPORTED']
    receipt = {'gpu': (ROOT / 'raw/gpu_identity.txt').read_text().strip(),
               'ncu_version': (ROOT / 'raw/ncu_version.txt').read_text().strip(),
               'query_all_sha256': sha(profiling_file),
               'query_launch_sha256': sha(launch_file),
               'selected_profile_metrics': profile_metrics,
               'selected_launch_metrics': launch_metrics,
               'unsupported_requested_metrics': [row['exact_requested_metric'] for row in rows
                                                 if row['availability'] == 'UNSUPPORTED'],
               'bounded_metric_engineering_retry': {
                   'reason': 'static SASS reveals K128 LDGSTS global-to-shared instructions; the initially frozen LDG/LD metric does not include that distinct opcode class',
                   'supported_added_metric': 'smsp__inst_executed_op_ldgsts.sum',
                   'attempt0_f128_k128_reports_archived': True,
                   'one_same_config_retry_per_arm': True,
                   'not_selected_from_counter_values_or_timing': True,
               },
               'ncu_execution_contract': {
                   'graph_profiling': 'node', 'replay_mode': 'application',
                   'cache_control': 'none', 'clock_control': 'none',
                   'pipeline_boost_state': 'dynamic',
                   'nvtx_one_exact_arm_per_profile': True,
                   'ncu_replay_duration_not_primary_timing': True,
               }}
    (ROOT / 'NCU_METRIC_SET.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    (ROOT / 'NCU_METRIC_PREREGISTRATION.md').write_text(
        '# NCU metric preregistration — RTX4080/SM89\n\n'
        f'Query authority: `{profiling_file}` SHA256 `{receipt["query_all_sha256"]}` and '
        f'launch query SHA256 `{receipt["query_launch_sha256"]}`. '
        f'Installed version: `{receipt["ncu_version"]}`. '
        f'Device: `{receipt["gpu"]}`.\n\n'
        'The exact supported set is frozen in `NCU_METRIC_SET.json` and every requested '
        'quantity, including `UNSUPPORTED` entries, is recorded separately in '
        '`NCU_METRIC_BINDING_PREREG.tsv`. Counters are warp-instruction or hardware '
        'transaction metrics as named; they are not silently equated to per-thread '
        'instructions, bytes, or timing. Add only additive counters across launches; '
        'occupancy, eligible warps and launch resources remain per-kernel/family weighted '
        'descriptives. This is one bounded, source-motivated metric-engineering retry per arm: '
        'ATTEMPT0 omitted the supported LDGSTS warp-instruction counter and is archived. '
        'The LDG/LD counter and LDGSTS counter are kept as distinct measured quantities; '
        'their sum, when shown, is labeled as a derived combined global-read issue count. '
        'NCU replay duration is not a timing authority.\n'
    )
    print(json.dumps({'selected_profile_metrics': len(profile_metrics),
                      'selected_launch_metrics': len(launch_metrics),
                      'unsupported': receipt['unsupported_requested_metrics']}))


if __name__ == '__main__':
    main()
