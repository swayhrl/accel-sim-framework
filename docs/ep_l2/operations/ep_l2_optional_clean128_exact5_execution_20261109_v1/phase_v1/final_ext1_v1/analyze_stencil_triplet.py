#!/usr/bin/env python3
"""One pass over each accepted Stencil raw to compare EXT0/1/2 per kernel."""
import collections
import csv
import importlib.util
import json
from pathlib import Path

R = Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
N = Path('/root/data/ep_l2_dtc_l1_native_v2')
OUT = R / 'documents/EXT1_TRIPLET_PHASE_20261110_V1'
BASE = R / 'runtime/analyze_stencil_phase_ext1_base.py'
CASES = {0: 'EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1',
         1: 'EP_PERF_CLEAN128_STENCIL_WV_EXT1_20261110_V1',
         2: 'EP_PERF_CLEAN128_STENCIL_WV_EXT2_20261109_V1'}
REQUEST = 'EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1'
OLD_REQUEST = 'EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1'
OPTION = '-gpgpu_ep_l2_victim_extension'
METRICS = ('c7e_dram_successful_read_issues', 'ext_read_responses',
           'block_payload', 'bank_wait_cycles', 'lookup_wait_cycles',
           'ext_queries', 'selector_reads', 'ext_clean_installs', 'spills')


def main():
    assert not OUT.exists(), 'phase analysis already exists; no automatic repetition'
    loader = importlib.util.spec_from_file_location('ep_l2_phase_base', BASE)
    phase = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(phase)
    registry = json.loads((N / 'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_bytes())
    request = registry['registered_future_requests'][REQUEST]
    assert request['budget'] == 1 and request['remaining'] == 0
    assert set(request['consumed']) == {CASES[1]}
    assert request['consumed'][CASES[1]]['state'] == 'CLOSED_ACCEPTED'
    cases = {}
    for mode, case in CASES.items():
        phase.GOAL = REQUEST if mode == 1 else OLD_REQUEST
        phase.CASES[mode] = case
        cases[mode] = phase.read_case(mode, registry)
    first = cases[0]
    for mode, case in cases.items():
        assert case['source_identity'] == first['source_identity']
        assert case['input_identity_sha256'] == first['input_identity_sha256']
        assert len(case['actual_options']) == 283 and case['actual_options'][OPTION] == str(mode)
        assert set(case['actual_options']) == set(first['actual_options'])
        assert {key for key in case['actual_options']
                if case['actual_options'][key] != first['actual_options'][key]} == ({OPTION} if mode else set())
        assert case['post_kernel_cycles'] == 106
        assert len(case['rows']) == 100
    rows = []
    for index in range(100):
        trio = {mode: cases[mode]['rows'][index] for mode in CASES}
        assert {item['uid'] for item in trio.values()} == {index + 1}
        record = {'uid': index + 1}
        for mode in CASES:
            record[f'ext{mode}_cycles'] = trio[mode]['cycles']
            for metric in METRICS:
                record[f'ext{mode}_{metric}'] = trio[mode][metric]
        record['migration_delta_cycles'] = trio[1]['cycles'] - trio[0]['cycles']
        record['clean_policy_delta_cycles'] = trio[2]['cycles'] - trio[1]['cycles']
        record['total_delta_cycles'] = trio[2]['cycles'] - trio[0]['cycles']
        assert record['migration_delta_cycles'] + record['clean_policy_delta_cycles'] == record['total_delta_cycles']
        rows.append(record)
    totals = {f'EXT{mode}': cases[mode]['total_cycles'] for mode in CASES}
    deltas = {'migration_EXT1_minus_EXT0': totals['EXT1'] - totals['EXT0'],
              'clean_policy_EXT2_minus_EXT1': totals['EXT2'] - totals['EXT1'],
              'total_EXT2_minus_EXT0': totals['EXT2'] - totals['EXT0']}
    assert sum(r['migration_delta_cycles'] for r in rows) == deltas['migration_EXT1_minus_EXT0']
    assert sum(r['clean_policy_delta_cycles'] for r in rows) == deltas['clean_policy_EXT2_minus_EXT1']
    assert sum(r['total_delta_cycles'] for r in rows) == deltas['total_EXT2_minus_EXT0']
    assert deltas['migration_EXT1_minus_EXT0'] + deltas['clean_policy_EXT2_minus_EXT1'] == deltas['total_EXT2_minus_EXT0']
    signs = {}
    for key in ('migration_delta_cycles', 'clean_policy_delta_cycles', 'total_delta_cycles'):
        signs[key] = dict(collections.Counter('slower' if row[key] > 0 else
                                              'faster' if row[key] < 0 else 'equal'
                                              for row in rows))
    groups = {}
    for label, subset in (('with_EXT2_response', [r for r in rows if r['ext2_ext_read_responses'] > 0]),
                          ('without_EXT2_response', [r for r in rows if r['ext2_ext_read_responses'] == 0])):
        groups[label] = {'count': len(subset),
                         'migration_delta_cycles': sum(r['migration_delta_cycles'] for r in subset),
                         'clean_policy_delta_cycles': sum(r['clean_policy_delta_cycles'] for r in subset),
                         'total_delta_cycles': sum(r['total_delta_cycles'] for r in subset),
                         'EXT2_responses': sum(r['ext2_ext_read_responses'] for r in subset)}
    assert sum(g['count'] for g in groups.values()) == 100
    mechanism = {}
    for metric in METRICS:
        values = {f'EXT{mode}': sum(row[f'ext{mode}_{metric}'] for row in rows) for mode in CASES}
        mechanism[metric] = {**values, 'migration_delta': values['EXT1'] - values['EXT0'],
                             'clean_policy_delta': values['EXT2'] - values['EXT1'],
                             'total_delta': values['EXT2'] - values['EXT0']}
    bins = []
    for start in range(0, 100, 10):
        subset = rows[start:start + 10]
        bins.append({'kernel_range': f'{start+1}-{start+10}',
                     'migration_delta_cycles': sum(r['migration_delta_cycles'] for r in subset),
                     'clean_policy_delta_cycles': sum(r['clean_policy_delta_cycles'] for r in subset),
                     'total_delta_cycles': sum(r['total_delta_cycles'] for r in subset)})
    evidence = {'schema': 'EP_L2_STENCIL_EXT012_PHASE_COMPARISON_V1',
                'source_identity': first['source_identity'],
                'input_identity_sha256': first['input_identity_sha256'],
                'population': '100 ordered paired kernels; 64 unique B0/M0 slice records per kernel and point',
                'option_count': 283, 'only_option_difference': OPTION,
                'points': {f'EXT{mode}': {key: value for key, value in case.items()
                                       if key not in ('rows', 'actual_options')}
                           for mode, case in cases.items()},
                'cycles': totals, 'delta_cycles': deltas, 'kernel_sign_counts': signs,
                'groups_by_EXT2_response': groups, 'ten_kernel_bins': bins,
                'mechanism_observations': mechanism,
                'definitions': {'cycles': 'gpu_sim_cycle per kernel; identical 106-cycle application tail',
                                'B0_M0': 'kernel_shared_delta over 64 slices',
                                'TVDV2_TVDX1': 'per-slice cumulative snapshots differenced between kernel ends',
                                'block_payload': 'broad event category, not disjoint GPU stall cycles',
                                'response': 'retained sector responses, not avoided DRAM requests'},
                'rows': rows}
    OUT.mkdir(parents=True)
    (OUT / 'TRIPLET_PHASE_EVIDENCE.json').write_text(json.dumps(evidence, indent=2, sort_keys=True) + '\n')
    with (OUT / 'TRIPLET_PHASE_ROWS.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    report = f'''# Stencil EXT0/1/2 阶段对照

三点同 Source、ELF、输入、100 个有序 kernel、283 项实际选项，只有 `{OPTION}` 为 0/1/2。每点均为 `CLOSED_ACCEPTED`，各自一次确定性完整应用；逐点压缩 raw 各只读一次，并与 Native DONE SHA、接受 bundle、每 kernel 的 64 个 B0/M0 slice 和末尾 106 cycles 守恒。

| 对照 | 应用 cycles | 净差 |
|---|---:|---:|
| EXT0 | {totals['EXT0']:,} | 基线 |
| EXT1 | {totals['EXT1']:,} | 迁移包 {deltas['migration_EXT1_minus_EXT0']:+,} |
| EXT2 | {totals['EXT2']:,} | CLEAN 策略包 {deltas['clean_policy_EXT2_minus_EXT1']:+,} |

总净差 EXT2−EXT0 为 {deltas['total_EXT2_minus_EXT0']:+,} cycles。100 个 kernel 的方向数：迁移包 {signs['migration_delta_cycles']}；CLEAN 策略包 {signs['clean_policy_delta_cycles']}。逐 kernel、每 10 kernel 箱、按 EXT2 response 有无分组及局部计数见 JSON/CSV。

EXT1−EXT0 识别的是扩展硬件迁移包的净效应；EXT2−EXT1 识别的是同扩展硬件下开启 CLEAN 策略包的净效应，包含查询、spill、占用和服务。局部 B0/M0/Ext 计数可能重叠，不能相加为应用关键路径周期。此对照不能证明物理 PPA、能耗、应用数值 oracle 或跨负载稳健收益。
'''
    (OUT / 'TRIPLET_PHASE_REPORT.md').write_text(report)
    print(json.dumps({'status': 'EXT012_PHASE_PASS', 'cycles': totals, 'deltas': deltas,
                      'rows': len(rows), 'output': str(OUT)}))


if __name__ == '__main__':
    main()
