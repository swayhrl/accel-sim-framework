#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

RUNTIME = Path('/root/awma_t1_negative_ideal_response_attribution_v1_runtime')
REPO = Path('/root/workspace/accel-sim-framework-awma-t1-negative-ideal-response-attribution-v1')
PACK = REPO / 'docs/vm_tlb/review_packs/AWMA_T1_NEGATIVE_IDEAL_RESPONSE_ATTRIBUTION_V1'
MODES = ('10_80', '0_80', 'ideal')
EXPECTED_CYCLES = {'10_80': 665802, '0_80': 664805, 'ideal': 715636}
EXPECTED_ADMISSIONS = {'10_80': 7160265, '0_80': 7234397, 'ideal': 7605378}


def scalar(text: str, key: str, numeric=float):
    match = re.search(rf'^\s*{re.escape(key)}\s*=\s*([^\s]+)', text, re.M)
    if not match:
        return None
    return numeric(match.group(1))


def tsv_lines(text: str, prefix: str) -> list[list[str]]:
    return [line.split('\t') for line in text.splitlines()
            if line.startswith(prefix + '\t')]


def parse_coverage(text: str) -> dict[str, int]:
    match = re.search(r'^AWMA_VM_COVERAGE (.+)$', text, re.M)
    if not match:
        return {}
    return {key: int(value) for key, value in re.findall(r'(\w+)=(\d+)', match.group(1))}


def parse_digest(text: str) -> dict[str, int]:
    match = re.search(r'^AWMA_VM_FUNCTIONAL_MAPPING_DIGEST unique=(\d+) fnv64=(\d+)', text, re.M)
    return ({'unique': int(match.group(1)), 'fnv64': int(match.group(2))}
            if match else {})


def parse_m4c(text: str) -> dict[str, float | int]:
    result: dict[str, float | int] = {}
    instruction = next((row for row in tsv_lines(
        text, 'm4c_telemetry_frontend_instruction') if row[1] == 'KERNEL'), None)
    if instruction:
        result['frontend_memory_instructions'] = int(instruction[4])
        result['frontend_active_lane_references'] = int(instruction[5])
    for key in ('frontend_transactions', 'frontend_requested_bytes',
                'frontend_transaction_bytes', 'frontend_sector_population'):
        result[key] = 0
    for row in tsv_lines(text, 'm4c_telemetry_frontend_transaction'):
        if row[1] != 'KERNEL' or row[4] not in {
                'DATA_UNKNOWN', 'DATA_WEIGHT', 'DATA_KV_CACHE'}:
            continue
        result['frontend_transactions'] += int(row[6])
        result['frontend_requested_bytes'] += int(row[7])
        result['frontend_transaction_bytes'] += int(row[8])
        result['frontend_sector_population'] += int(row[9])
    for prefix, out_prefix in (('m4c_telemetry', 'l1'),
                               ('m4c_telemetry_l2', 'l2')):
        for status in ('HIT', 'HIT_RESERVED', 'MISS', 'RESERVATION_FAIL',
                       'SECTOR_MISS'):
            result[f'{out_prefix}_{status.lower()}'] = 0
        for row in tsv_lines(text, prefix):
            if row[1] != 'KERNEL' or row[4] not in {
                    'DATA_UNKNOWN', 'DATA_WEIGHT', 'DATA_KV_CACHE'}:
                continue
            if row[5] in {'HIT', 'HIT_RESERVED', 'MISS', 'RESERVATION_FAIL',
                          'SECTOR_MISS'}:
                result[f'{out_prefix}_{row[5].lower()}'] += int(row[6])
    result['dram_data_requests'] = 0
    result['dram_data_bytes'] = 0
    for row in tsv_lines(text, 'm4c_telemetry_dram'):
        if row[1] == 'KERNEL' and row[4] in {
                'DATA_UNKNOWN', 'DATA_WEIGHT', 'DATA_KV_CACHE'}:
            result['dram_data_requests'] += int(row[5])
            result['dram_data_bytes'] += int(row[6])
    queue = next((row for row in tsv_lines(text, 'm4c_telemetry_l2_queue')
                  if row[1] == 'KERNEL'), None)
    if queue:
        names = ('samples', 'icnt_to_l2_total', 'l2_to_dram_total',
                 'dram_to_l2_total', 'l2_to_icnt_total', 'icnt_to_l2_hwm',
                 'l2_to_dram_hwm', 'dram_to_l2_hwm', 'l2_to_icnt_hwm')
        for name, value in zip(names, queue[4:]):
            result[f'l2q_{name}'] = int(value)
        samples = result['l2q_samples']
        for name in ('icnt_to_l2', 'l2_to_dram', 'dram_to_l2', 'l2_to_icnt'):
            result[f'l2q_{name}_mean'] = (result[f'l2q_{name}_total'] / samples
                                          if samples else 0.0)
    return result


def parse_attribution(text: str) -> dict[str, float | int]:
    result: dict[str, float | int] = {}
    release = tsv_lines(text, 'awma_t1_release_delay')
    if release:
        names = ('count', 'total', 'missing', 'p50', 'p95', 'p99', 'max')
        for name, value in zip(names, release[0][1:]):
            result[f'release_delay_{name}'] = int(value)
        result['release_delay_mean'] = (
            result['release_delay_total'] / result['release_delay_count']
            if result['release_delay_count'] else 0.0)
    accessq = tsv_lines(text, 'awma_t1_accessq_summary')
    if accessq:
        names = ('samples', 'entries_total', 'ready_total', 'entries_max',
                 'ready_max')
        for name, value in zip(names, accessq[0][1:]):
            result[f'accessq_{name}'] = int(value)
        result['accessq_entries_mean'] = (
            result['accessq_entries_total'] / result['accessq_samples'])
        result['accessq_ready_mean'] = (
            result['accessq_ready_total'] / result['accessq_samples'])
    for row in tsv_lines(text, 'awma_t1_cycle_summary'):
        metric = row[1].lower()
        for name, value in zip(('span_cycles', 'total', 'active_cycles',
                                'all_cycle_p95', 'peak'), row[2:]):
            result[f'{metric}_{name}'] = int(value)
        result[f'{metric}_per_span_cycle'] = (
            result[f'{metric}_total'] / result[f'{metric}_span_cycles'])
        result[f'{metric}_per_active_cycle'] = (
            result[f'{metric}_total'] / result[f'{metric}_active_cycles'])
    for row in tsv_lines(text, 'awma_t1_window_summary'):
        metric = row[1].lower()
        width = row[2]
        for name, value in zip(('windows', 'nonzero', 'p50', 'p95', 'p99',
                                'peak'), row[3:]):
            result[f'{metric}_w{width}_{name}'] = int(value)
    for row in tsv_lines(text, 'awma_t1_progress_summary'):
        metric = row[1].lower()
        for name, value in zip(('total', 'p25_cycle', 'p50_cycle',
                                'p75_cycle', 'p90_cycle', 'p99_cycle'), row[2:]):
            result[f'{metric}_{name}'] = int(value)
    dram = tsv_lines(text, 'awma_t1_dram_completion_summary')
    if dram:
        for name, value in zip(('count', 'first_cycle', 'last_cycle'), dram[0][1:]):
            result[f'dram_completion_{name}'] = int(value)
    return result


def parse(mode: str) -> dict[str, object]:
    run_dir = RUNTIME / f'attribution_T1_V1_{mode}'
    text = (run_dir / 'run.log').read_text(errors='replace')
    command = json.loads((run_dir / 'command.json').read_text())
    result: dict[str, object] = {
        'mode': mode,
        'run_dir': str(run_dir),
        'command': command,
        'cycles': scalar(text, 'gpu_sim_cycle', int),
        'instructions': scalar(text, 'gpu_sim_insn', int),
        'ctas': scalar(text, 'gpu_tot_issued_cta', int),
        'l1d_accesses': scalar(text, 'L1D_total_cache_accesses', int),
        'l1d_misses': scalar(text, 'L1D_total_cache_misses', int),
        'l1d_pending_hits': scalar(text, 'L1D_total_cache_pending_hits', int),
        'l1d_reservation_fails': scalar(text, 'L1D_total_cache_reservation_fails', int),
        'l2_accesses': scalar(text, 'L2_total_cache_accesses', int),
        'l2_misses': scalar(text, 'L2_total_cache_misses', int),
        'l2_pending_hits': scalar(text, 'L2_total_cache_pending_hits', int),
        'l2_reservation_fails': scalar(text, 'L2_total_cache_reservation_fails', int),
        'icnt_simt_to_mem': scalar(text, 'icnt_total_pkts_simt_to_mem', int),
        'icnt_mem_to_simt': scalar(text, 'icnt_total_pkts_mem_to_simt', int),
        'avg_icnt2mem_latency': scalar(text, 'avg_icnt2mem_latency', float),
        'max_icnt2mem_latency': scalar(text, 'max_icnt2mem_latency', int),
        'gpu_stall_dramfull': scalar(text, 'gpu_stall_dramfull', int),
        'shader_memory_stalls': scalar(text, 'gpgpu_n_stall_shd_mem', int),
        'global_resource_stalls': scalar(text, 'gpgpu_stall_shd_mem[gl_mem][resource_stall]', int),
        'global_coal_stalls': scalar(text, 'gpgpu_stall_shd_mem[gl_mem][coal_stall]', int),
        'vm_translation_stall_cycles': scalar(text, 'vm_translation_stall_cycles', int),
        'partition_level_parallelism': scalar(text, 'partiton_level_parallism', float),
        'coverage': parse_coverage(text),
        'mapping_digest': parse_digest(text),
        'duplicate_attempts': scalar(text, 'vm_ready_application_duplicate_attempts', int),
        'quiescent': scalar(text, 'vm_translation_quiescent_invariants_hold', int),
    }
    stall = re.search(r'^Stall:(\d+)\s+W0_Idle:(\d+)\s+W0_Scoreboard:(\d+)', text, re.M)
    if stall:
        result.update({'scheduler_stall': int(stall.group(1)),
                       'scheduler_idle': int(stall.group(2)),
                       'scoreboard_stall': int(stall.group(3))})
    queue_avgs = [float(x) for x in re.findall(r'^queue_avg = ([0-9.]+)', text, re.M)]
    bw_utils = [float(x) for x in re.findall(r'\bbw_util=([0-9.]+)', text)]
    result['dram_queue_avg_mean'] = sum(queue_avgs) / len(queue_avgs)
    result['dram_queue_avg_max_channel'] = max(queue_avgs)
    result['dram_bw_util_mean'] = sum(bw_utils) / len(bw_utils)
    result.update(parse_m4c(text))
    result.update(parse_attribution(text))
    return result


def write_wide_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['mode'] + fields, delimiter='\t',
                                lineterminator='\n', extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    PACK.mkdir(parents=True, exist_ok=True)
    rows = [parse(mode) for mode in MODES]
    validation: dict[str, object] = {'checks': {}, 'status': 'PASS'}
    checks: dict[str, bool] = validation['checks']  # type: ignore[assignment]
    for row in rows:
        mode = str(row['mode'])
        coverage = row['coverage']
        checks[f'{mode}_cycle_neutrality'] = row['cycles'] == EXPECTED_CYCLES[mode]
        checks[f'{mode}_instructions'] = row['instructions'] == 369131520
        checks[f'{mode}_ctas'] = row['ctas'] == 384
        checks[f'{mode}_uid_coverage'] = coverage.get('unique') == 7159808
        checks[f'{mode}_admission_signature'] = (
            coverage.get('admissions') == EXPECTED_ADMISSIONS[mode])
        checks[f'{mode}_untranslated_zero'] = coverage.get('untranslated') == 0
        checks[f'{mode}_unobserved_zero'] = coverage.get('unobserved') == 0
        checks[f'{mode}_duplicates_zero'] = row['duplicate_attempts'] == 0
        checks[f'{mode}_quiescent'] = row['quiescent'] == 1
        checks[f'{mode}_release_complete'] = (
            row.get('release_delay_missing') == 0 and
            row.get('release_delay_count') == coverage.get('unique') and
            row.get('downstream_admissions_total') == coverage.get('unique'))
    digests = {(row['mapping_digest'].get('unique'),
                row['mapping_digest'].get('fnv64')) for row in rows}
    checks['functional_mapping_digest_identity'] = len(digests) == 1
    checks['functional_mapping_digest_authority'] = (
        digests == {(493, 12947203714122211934)})
    ideal_text = (RUNTIME / 'attribution_T1_V1_ideal/run.log').read_text(errors='replace')
    ideal_zero_keys = (
        'vm_translation_lookup_requests', 'vm_translation_mshr_allocations',
        'vm_translation_mshr_active', 'vm_translation_pwq_occupancy',
        'vm_translation_walkers_active', 'vm_pte_requests', 'vm_pwc_hits',
        'vm_pwc_misses', 'vm_pte_responses', 'vm_pte_dram_responses')
    for key in ideal_zero_keys:
        checks[f'ideal_{key}_zero'] = scalar(ideal_text, key, int) == 0
    validation['status'] = 'PASS' if all(checks.values()) else 'FAIL'

    timeline_fields = [
        'cycles', 'release_delay_count', 'release_delay_missing',
        'release_delay_mean', 'release_delay_p50', 'release_delay_p95',
        'release_delay_p99', 'release_delay_max', 'ready_releases_total',
        'ready_releases_active_cycles', 'ready_releases_all_cycle_p95',
        'ready_releases_peak', 'downstream_admissions_total',
        'downstream_admissions_active_cycles',
        'downstream_admissions_per_span_cycle',
        'downstream_admissions_per_active_cycle',
        'downstream_admissions_all_cycle_p95', 'downstream_admissions_peak',
        'downstream_admissions_w32_p50', 'downstream_admissions_w32_p95',
        'downstream_admissions_w32_p99', 'downstream_admissions_w32_peak',
        'downstream_admissions_w64_p50', 'downstream_admissions_w64_p95',
        'downstream_admissions_w64_p99', 'downstream_admissions_w64_peak',
        'downstream_admissions_w128_p50', 'downstream_admissions_w128_p95',
        'downstream_admissions_w128_p99', 'downstream_admissions_w128_peak',
        'accessq_samples', 'accessq_entries_mean', 'accessq_ready_mean',
        'accessq_entries_max', 'accessq_ready_max', 'instructions_p25_cycle',
        'instructions_p50_cycle', 'instructions_p75_cycle',
        'instructions_p90_cycle', 'instructions_p99_cycle', 'ctas_p25_cycle',
        'ctas_p50_cycle', 'ctas_p75_cycle', 'ctas_p90_cycle', 'ctas_p99_cycle',
        'dram_completion_count', 'dram_completion_first_cycle',
        'dram_completion_last_cycle']
    pressure_fields = [
        'cycles', 'l1d_accesses', 'l1d_misses', 'l1d_pending_hits',
        'l1d_reservation_fails', 'l2_accesses', 'l2_misses', 'l2_pending_hits',
        'l2_reservation_fails', 'l2_hit', 'l2_hit_reserved', 'l2_miss',
        'l2_reservation_fail', 'avg_icnt2mem_latency', 'max_icnt2mem_latency',
        'gpu_stall_dramfull', 'shader_memory_stalls', 'global_resource_stalls',
        'global_coal_stalls', 'scheduler_stall', 'scheduler_idle',
        'scoreboard_stall', 'partition_level_parallelism',
        'dram_queue_avg_mean', 'dram_queue_avg_max_channel',
        'dram_bw_util_mean', 'l2q_samples', 'l2q_icnt_to_l2_mean',
        'l2q_l2_to_dram_mean', 'l2q_dram_to_l2_mean',
        'l2q_l2_to_icnt_mean', 'l2q_icnt_to_l2_hwm', 'l2q_l2_to_dram_hwm',
        'l2q_dram_to_l2_hwm', 'l2q_l2_to_icnt_hwm']
    work_fields = [
        'cycles', 'instructions', 'ctas', 'icnt_simt_to_mem', 'icnt_mem_to_simt',
        'frontend_memory_instructions', 'frontend_active_lane_references',
        'frontend_transactions', 'frontend_requested_bytes',
        'frontend_transaction_bytes', 'frontend_sector_population',
        'dram_data_requests', 'dram_data_bytes']
    write_wide_tsv(PACK / 'DOWNSTREAM_TIMELINE_SUMMARY.tsv', rows, timeline_fields)
    write_wide_tsv(PACK / 'MEMORY_PRESSURE_SUMMARY.tsv', rows, pressure_fields)
    write_wide_tsv(PACK / 'WORK_CONSERVATION.tsv', rows, work_fields)

    by_mode = {str(row['mode']): row for row in rows}
    baseline, ideal = by_mode['10_80'], by_mode['ideal']
    logical_work_keys = [
        'instructions', 'ctas', 'icnt_simt_to_mem',
        'frontend_memory_instructions', 'frontend_active_lane_references',
        'frontend_transactions', 'frontend_requested_bytes',
        'frontend_transaction_bytes', 'frontend_sector_population']
    logical_work_equal = all(baseline.get(key) == ideal.get(key)
                             for key in logical_work_keys)
    downstream_work_equal = all(
        baseline.get(key) == ideal.get(key)
        for key in ('dram_data_requests', 'dram_data_bytes'))
    h1 = (ideal['downstream_admissions_w32_p95'] > baseline['downstream_admissions_w32_p95']
          and ideal['avg_icnt2mem_latency'] > baseline['avg_icnt2mem_latency']
          and ideal['global_resource_stalls'] > baseline['global_resource_stalls']
          and ideal['max_icnt2mem_latency'] > baseline['max_icnt2mem_latency']
          and logical_work_equal)
    h2 = (ideal['dram_data_requests'] != baseline['dram_data_requests'] or
          ideal['dram_data_bytes'] != baseline['dram_data_bytes'])
    h3 = (ideal['instructions_p90_cycle'] > baseline['instructions_p90_cycle']
          and ideal['scheduler_idle'] > baseline['scheduler_idle'])
    hypotheses = [
        {'hypothesis': 'H1_burstiness_queue_pressure',
         'decision': 'SUPPORTED' if h1 else 'NOT_SUPPORTED',
         'evidence': 'release/admission cycle windows; ICNT latency; global resource stalls; max memory latency; conserved work'},
        {'hypothesis': 'H2_locality_order',
         'decision': 'SUPPORTED' if h2 else 'NOT_SUPPORTED',
         'evidence': 'data-only L2 outcome counts and DRAM request counts'},
        {'hypothesis': 'H3_reduced_latency_hiding_progress',
         'decision': 'SUPPORTED_SECONDARY' if h3 else 'NOT_SUPPORTED',
         'evidence': 'instruction progress quantiles and scheduler idle cycles'},
        {'hypothesis': 'H4_not_localized',
         'decision': 'REJECTED' if (h1 or h2 or h3) else 'REMAINS',
         'evidence': 'directional chain closure across release, pressure, and progress telemetry'},
    ]
    with (PACK / 'HYPOTHESIS_DECISION.tsv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=('hypothesis', 'decision', 'evidence'),
                                delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(hypotheses)
    validation['logical_work_conserved_10_80_vs_ideal'] = logical_work_equal
    validation['downstream_dram_work_conserved_10_80_vs_ideal'] = downstream_work_equal
    validation['hypotheses'] = hypotheses
    validation['rows'] = rows
    (PACK / 'ATTRIBUTION_SUMMARY.json').write_text(
        json.dumps(validation, indent=2, sort_keys=True) + '\n')
    (PACK / 'VALIDATION.json').write_text(json.dumps(
        {'status': validation['status'], 'checks': checks}, indent=2,
        sort_keys=True) + '\n')
    print(json.dumps({'status': validation['status'],
                      'pack': str(PACK), 'hypotheses': hypotheses},
                     indent=2, sort_keys=True))
    return 0 if validation['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
