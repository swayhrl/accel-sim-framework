#!/usr/bin/env python3
"""Bind exact NCU units, qualify kernel strata, and aggregate only additive counters."""
from __future__ import annotations

import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('/data/c16/awma/r101r2_s128_native_profile_20260929')
ADDITIVE = {
    'smsp__inst_executed.sum', 'smsp__inst_issued.sum',
    'smsp__sass_inst_executed_op_global_ld.sum',
    'smsp__inst_executed_op_ldgsts.sum',
    'smsp__sass_inst_executed_op_global_st.sum',
    'smsp__sass_inst_executed_op_shared_ld.sum',
    'smsp__sass_inst_executed_op_shared_st.sum',
    'smsp__inst_executed_pipe_tensor_op_hmma.sum',
    'smsp__inst_executed_pipe_fma.sum',
    'smsp__inst_executed_pipe_alu.sum',
    'sm__cycles_active.sum',
    'l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum',
    'l1tex__t_sectors_pipe_lsu_mem_global_op_st.sum',
    'l1tex__t_bytes.sum',
    'lts__t_sectors_op_read.sum', 'lts__t_sectors_op_write.sum',
    'lts__t_bytes.sum', 'dram__bytes_read.sum', 'dram__bytes_write.sum',
}
NONADDITIVE = {
    'sm__warps_active.avg.pct_of_peak_sustained_active',
    'smsp__warps_eligible.avg.per_cycle_active',
    'launch__registers_per_thread', 'launch__shared_mem_per_block',
}
FAMILY_ORDER = ('F128_FUSED_NS5', 'K128_NORMALIZATION', 'K128_XXT',
                'K128_BA', 'K128_BMM_ADD', 'GRAPH_RUNTIME_OTHER')


def number(value: str | None) -> float | None:
    if value is None or value in ('', 'N/A', 'nan', 'NaN'):
        return None
    return float(value.replace(',', ''))


def family(name: str) -> str:
    low = name.lower()
    if 'ns5_smem_kernel' in low:
        return 'F128_FUSED_NS5'
    if 'xxt_kernel' in low:
        return 'K128_XXT'
    if 'ba_plus_caa_kernel' in low:
        return 'K128_BA'
    if 'bmm_add_kernel' in low:
        return 'K128_BMM_ADD'
    if 'norm' in low:
        return 'K128_NORMALIZATION'
    return 'GRAPH_RUNTIME_OTHER'


def write_tsv(path: Path, rows: list[dict]) -> None:
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    metric_set = json.loads((ROOT / 'NCU_METRIC_SET.json').read_text())
    selected = metric_set['selected_profile_metrics'] + metric_set['selected_launch_metrics']
    assert set(selected) == ADDITIVE | NONADDITIVE
    prereg = {row['exact_requested_metric']: row
              for row in csv.DictReader((ROOT / 'NCU_METRIC_BINDING_PREREG.tsv').open(newline=''), delimiter='\t')}
    accepted_path = json.loads((ROOT / 'PATH_QUALIFICATION.json').read_text())
    canary = json.loads((ROOT / 'PATH_CANARY.json').read_text())
    raw_rows = []
    arm_rows = {}
    units_by_arm = {}
    for arm in ('F128', 'K128'):
        path = ROOT / 'raw/ncu' / arm / f'{arm}.raw.csv'
        with path.open(newline='') as stream:
            original = list(csv.DictReader(stream))
        assert original
        assert all(metric in original[0] for metric in selected)
        units = {metric: original[0][metric] for metric in selected}
        units_by_arm[arm] = units
        rows = []
        for index, item in enumerate(original):
            if not item['ID']:
                continue
            name = item['Kernel Name']
            row = {'arm': arm, 'kernel_index_in_report': len(rows),
                   'family': family(name), 'exact_kernel_name': name,
                   'grid': item['Grid Size'], 'block': item['Block Size']}
            for metric in selected:
                row[metric] = number(item[metric])
            rows.append(row); raw_rows.append(row)
        assert len(rows) == accepted_path['arms'][arm]['kernel_count_all_graph_nodes']
        assert json.loads((ROOT / 'raw/ncu' / arm / 'TARGET_RECEIPT.json').read_text())['accepted_output_bitwise']
        arm_rows[arm] = rows
    assert units_by_arm['F128'] == units_by_arm['K128']
    units = units_by_arm['F128']
    assert all(units[metric] for metric in selected)
    for arm, expected in (('F128', {'F128_FUSED_NS5': 1, 'GRAPH_RUNTIME_OTHER': 2}),
                          ('K128', {'K128_NORMALIZATION': 1, 'K128_XXT': 5,
                                    'K128_BA': 5, 'K128_BMM_ADD': 5,
                                    'GRAPH_RUNTIME_OTHER': 2})):
        counts = Counter(row['family'] for row in arm_rows[arm])
        assert dict(counts) == expected, (arm, counts)
        frozen = canary['frozen_author_launch_configs']
        for row in arm_rows[arm]:
            if row['family'] == 'GRAPH_RUNTIME_OTHER':
                continue
            name = row['exact_kernel_name']
            if row['family'] == 'F128_FUSED_NS5':
                freeze = frozen['F128_NS5']
            elif row['family'] == 'K128_NORMALIZATION':
                continue
            else:
                freeze = frozen[row['family']]
            assert row['grid'].strip('() ').replace(' ', '') == freeze['grid']
            assert row['block'].strip('() ').replace(' ', '') == freeze['block']
        # The current profile must independently retain the author graph strata.
        observed = Counter((row['exact_kernel_name'], row['grid'].strip('() ').replace(' ', ''),
                            row['block'].strip('() ').replace(' ', '')) for row in arm_rows[arm]
                           if row['family'] not in ('GRAPH_RUNTIME_OTHER', 'K128_NORMALIZATION'))
        canary_rows = list(csv.DictReader((ROOT / 'KERNEL_IDENTITY.tsv').open(newline=''), delimiter='\t'))
        expected_strata = Counter((row['exact_demangled_name'], row['grid'], row['block'])
                                  for row in canary_rows if row['arm'] == arm
                                  and row['family'] not in ('GRAPH_RUNTIME_OTHER', 'K128_NORMALIZATION'))
        assert observed == expected_strata, (arm, observed, expected_strata)
    for row in raw_rows:
        for metric in ADDITIVE:
            assert row[metric] is not None, (row['arm'], row['family'], metric)
    write_tsv(ROOT / 'NCU_KERNEL_METRICS.tsv', raw_rows)
    bindings = []
    for metric, row in prereg.items():
        status = row['availability']
        bindings.append({'scientific_quantity': row['scientific_quantity'],
                         'exact_requested_metric': metric,
                         'support_status': status,
                         'selected_metric': metric if status == 'SUPPORTED' else 'UNSUPPORTED',
                         'raw_report_unit': units.get(metric, 'UNSUPPORTED'),
                         'aggregation': 'SUM_ACROSS_LAUNCHES' if metric in ADDITIVE else
                                        'PER_KERNEL_MEDIAN_RANGE_ONLY' if metric in NONADDITIVE else
                                        'UNSUPPORTED',
                         'semantic_substitution': 'NONE'})
    write_tsv(ROOT / 'NCU_RAW_METRIC_BINDING.tsv', bindings)
    families = defaultdict(list)
    for row in raw_rows:
        families[(row['arm'], row['family'])].append(row)
    summary_rows = []
    for arm in ('F128', 'K128'):
        for fam in FAMILY_ORDER:
            group = families.get((arm, fam))
            if not group:
                continue
            output = {'arm': arm, 'family': fam, 'kernel_launches': len(group)}
            for metric in selected:
                values = [row[metric] for row in group if row[metric] is not None]
                if metric in ADDITIVE:
                    output[metric] = sum(values)
                else:
                    output[metric] = statistics.median(values) if values else 'UNAVAILABLE'
                    output[metric + '__min'] = min(values) if values else 'UNAVAILABLE'
                    output[metric + '__max'] = max(values) if values else 'UNAVAILABLE'
            summary_rows.append(output)
    # Normalize mixed extra min/max columns to the shared table schema.
    columns = list(summary_rows[0])
    assert all(set(row) == set(columns) for row in summary_rows)
    write_tsv(ROOT / 'NCU_FAMILY_SUMMARY.tsv', summary_rows)
    totals = {}
    for arm in ('F128', 'K128'):
        totals[arm] = {metric: sum(row[metric] for row in arm_rows[arm]) for metric in ADDITIVE}
        totals[arm]['kernel_launches_all_nodes'] = len(arm_rows[arm])
        totals[arm]['kernel_launches_NS_core'] = 1 if arm == 'F128' else 15
    comparisons = []
    for metric in sorted(ADDITIVE):
        f, k = totals['F128'][metric], totals['K128'][metric]
        comparisons.append({'quantity': prereg[metric]['scientific_quantity'],
                            'metric': metric, 'unit': units[metric],
                            'F128_all_graph_nodes': f, 'K128_all_graph_nodes': k,
                            'F128_over_K128_ratio': f / k if k else 'UNDEFINED_ZERO_DENOMINATOR',
                            'aggregation': 'SUM_ADDITIVE_COUNTERS',
                            'ncu_time_not_primary': True})
    write_tsv(ROOT / 'NCU_OPERATOR_COMPARISON.tsv', comparisons)
    core_totals = {}
    for arm in ('F128', 'K128'):
        relevant = [row for row in arm_rows[arm] if row['family'] in
                    (('F128_FUSED_NS5',) if arm == 'F128' else
                     ('K128_XXT', 'K128_BA', 'K128_BMM_ADD'))]
        core_totals[arm] = {metric: sum(row[metric] for row in relevant) for metric in ADDITIVE}
    core_rows = []
    for metric in sorted(ADDITIVE):
        f, k = core_totals['F128'][metric], core_totals['K128'][metric]
        core_rows.append({'quantity': prereg[metric]['scientific_quantity'],
                          'metric': metric, 'unit': units[metric],
                          'F128_fused_NS_core': f, 'K128_15_kernel_NS_core': k,
                          'F128_over_K128_ratio': f / k if k else 'UNDEFINED_ZERO_DENOMINATOR',
                          'aggregation': 'SUM_ADDITIVE_COUNTERS', 'NCU_duration_not_primary': True})
    write_tsv(ROOT / 'NCU_CORE_COMPARISON.tsv', core_rows)
    combined_global_issue = {}
    for arm in ('F128', 'K128'):
        ld = totals[arm]['smsp__sass_inst_executed_op_global_ld.sum']
        async_ld = totals[arm]['smsp__inst_executed_op_ldgsts.sum']
        combined_global_issue[arm] = {'direct_LDG_LD_warp_instructions': ld,
                                       'direct_LDGSTS_warp_instructions': async_ld,
                                       'derived_disjoint_LDG_LD_plus_LDGSTS_warp_instructions': ld + async_ld,
                                       'derivation_not_a_single_hardware_counter': True}
    static = {row['family']: row for row in csv.DictReader((ROOT / 'STATIC_SASS_SUMMARY.tsv').open(newline=''), delimiter='\t')}
    decomposition = []
    for row in summary_rows:
        fam = row['family']
        record = static.get(fam)
        decomposition.append({'arm': row['arm'], 'family': fam,
                              'kernel_launches': row['kernel_launches'],
                              'static_unique_binary_instructions': record['static_instruction_count'] if record else 'UNAVAILABLE',
                              'static_cubin_sha256': record['cubin_sha256'] if record else 'UNAVAILABLE',
                              'dynamic_executed_warp_instructions': row['smsp__inst_executed.sum'],
                              'dynamic_global_load_warp_instructions': row['smsp__sass_inst_executed_op_global_ld.sum'],
                              'dynamic_global_store_warp_instructions': row['smsp__sass_inst_executed_op_global_st.sum'],
                              'dynamic_hmma_warp_instructions': row['smsp__inst_executed_pipe_tensor_op_hmma.sum'],
                              'active_sm_cycles_sum': row['sm__cycles_active.sum'],
                              'registers_per_thread_median': row['launch__registers_per_thread'],
                              'shared_memory_per_block_reported_unit': units['launch__shared_mem_per_block'],
                              'shared_memory_per_block_median': row['launch__shared_mem_per_block'],
                              'static_counts_not_dynamic': True})
    write_tsv(ROOT / 'KERNEL_DECOMPOSITION_ACCOUNTING.tsv', decomposition)
    (ROOT / 'NCU_ANALYSIS.json').write_text(json.dumps({
        'metric_units': units, 'kernel_counts': {arm: len(rows) for arm, rows in arm_rows.items()},
        'total_additive_counters': totals,
        'core_NS_additive_counters': core_totals,
        'combined_global_read_issue': combined_global_issue,
        'unsupported_metrics': metric_set['unsupported_requested_metrics'],
        'source_path_and_profile_strata_qualified': True,
        'no_new_primary_timing': True,
        'nonadditive_metrics_not_summed': True,
    }, indent=2, sort_keys=True) + '\n')
    requested = ('smsp__inst_executed.sum',
                 'smsp__sass_inst_executed_op_global_ld.sum',
                 'smsp__inst_executed_op_ldgsts.sum',
                 'smsp__sass_inst_executed_op_global_st.sum',
                 'lts__t_bytes.sum', 'dram__bytes_read.sum', 'dram__bytes_write.sum',
                 'smsp__inst_executed_pipe_tensor_op_hmma.sum', 'sm__cycles_active.sum')
    print(json.dumps({metric: {'F128': totals['F128'][metric], 'K128': totals['K128'][metric],
                               'ratio': totals['F128'][metric] / totals['K128'][metric]
                               if totals['K128'][metric] else None, 'unit': units[metric]}
                      for metric in requested}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
