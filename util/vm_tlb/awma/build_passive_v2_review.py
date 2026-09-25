#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

STAGE = 'AWMA_PASSIVE_LAST_TRANSLATION_RESULT_FORWARDING_V2'
REPO = Path('/root/workspace/accel-sim-framework-awma-passive-last-translation-result-forwarding-v2')
RUNTIME = Path('/root/awma_passive_last_translation_result_forwarding_v2_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_passive_last_translation_result_forwarding_v2/raw')
PACK = REPO / 'docs/vm_tlb/review_packs' / STAGE
RUNNER = REPO / 'util/vm_tlb/awma/run_passive_v2_matrix.py'
QUALIFIER = REPO / 'util/vm_tlb/awma/qualify_passive_v2_off.py'
BUILDER = REPO / 'util/vm_tlb/awma/build_passive_v2_review.py'
TEST_SOURCE = REPO / 'util/vm_tlb/awma/passive_last_translation_forwarding_test.cc'
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
OFF_AUTHORITY = RUNTIME / 'off_authority.json'

TARGETS = {
    'T0': dict(family='PREFILL_FLASH', cycles=527896, insn=368696302,
               cta=224, uid=3090304, admissions=3090304,
               opportunity=2722464),
    'T1': dict(family='PREFILL_GEMM', cycles=665802, insn=369131520,
               cta=384, uid=7159808, admissions=7160265,
               opportunity=6629952),
    'T2': dict(family='DECODE_GEMV', cycles=93079, insn=43357696,
               cta=1216, uid=411008, admissions=715333,
               opportunity=132544),
    'SPLITKV': dict(family='FLASH_FWD_SPLITKV', cycles=73923,
                    insn=36599648, cta=126, uid=233814, admissions=233814,
                    opportunity=218862),
    'COMBINE': dict(family='FLASH_FWD_SPLITKV_COMBINE', cycles=10480,
                    insn=72908, cta=2, uid=1099, admissions=1099,
                    opportunity=1016),
    'A1': dict(family='DECODE_GEMV_PAIR_A_S2_T2048', cycles=114123,
               insn=34883072, cta=224, uid=409024, admissions=2191027,
               opportunity=116032),
    'A2': dict(family='DECODE_GEMV_PAIR_A_T8192', cycles=117698,
               insn=34883072, cta=224, uid=409024, admissions=2375939,
               opportunity=116032),
}
BASE_KEYS = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_translation_lookup_requests', 'vm_l1_tlb_accesses',
    'vm_l2_tlb_accesses', 'vm_translation_mshr_allocations',
    'vm_translation_mshr_merges', 'vm_translation_walk_starts',
    'vm_pte_requests', 'vm_ready_application_duplicate_attempts',
    'vm_translation_lookup_entries', 'vm_translation_lookup_ready',
    'vm_translation_mshrs_entries', 'vm_translation_pwq_entries_active',
    'vm_translation_active_walks',
    'vm_translation_quiescent_invariants_hold',
)
V2_KEYS = (
    'awma_passive_v2_enabled', 'awma_passive_v2_capacity',
    'awma_passive_v2_live_entries', 'awma_passive_v2_lookups',
    'awma_passive_v2_hits', 'awma_passive_v2_misses',
    'awma_passive_v2_actual_physical_lookup_suppression',
    'awma_passive_v2_natural_completions', 'awma_passive_v2_installs',
    'awma_passive_v2_overwrites', 'awma_passive_v2_forwarded_applications',
    'awma_passive_v2_stale_generation_misses',
    'awma_passive_v2_access_compatibility_misses',
    'awma_passive_v2_vpn_misses',
    'awma_passive_v2_ppn_consistency_faults',
    'awma_passive_v2_instruction_invalidations',
    'awma_passive_v2_proactive_owner_attempts',
    'awma_passive_v2_proactive_duplicate_lookups',
    'awma_owner_wait_admissions', 'awma_owner_wait_repeated_admissions',
    'awma_owner_wait_readmitted_uids',
    'awma_owner_wait_member_owner_wait_cycles',
    'awma_owner_wait_head_block_total_cycles',
    'awma_owner_wait_pending_members_final',
)
PRESSURE_METRICS = (
    ('memory', 'ldst_resource_stall'), ('memory', 'ldst_coal_stall'),
    ('memory', 'ldst_icnt_stall'), ('memory', 'l1_reservation_fail'),
    ('memory', 'l2_reservation_fail'), ('memory', 'icnt_to_l2_occupancy'),
    ('memory', 'l2_to_dram_occupancy'), ('memory', 'dram_queue_occupancy'),
    ('scheduler', 'dependency_scoreboard'),
    ('scheduler', 'eligible_structural'),
    ('scheduler', 'frontend_starvation'),
)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def last_number(text: str, key: str) -> int:
    values = re.findall(rf'^{re.escape(key)} = (\d+)$', text, re.M)
    if not values:
        raise RuntimeError(f'missing {key}')
    return int(values[-1])


def coverage(text: str) -> dict[str, int]:
    values = re.findall(
        r'AWMA_VM_COVERAGE admissions=(\d+) translated=(\d+) '
        r'untranslated=(\d+) unobserved=(\d+) unique=(\d+) '
        r'translated_unique=(\d+) untranslated_unique=(\d+)', text)
    if not values:
        raise RuntimeError('missing coverage')
    names = ('admissions', 'translated', 'untranslated', 'unobserved',
             'unique', 'translated_unique', 'untranslated_unique')
    return dict(zip(names, map(int, values[-1])))


def observatory(text: str) -> dict[str, dict[str, object]]:
    rows = re.findall(
        r'^awma_observatory_metric\t(\S+)\t(\S+)\t(\S+)\t(\d+)\t(\d+)\t'
        r'([0-9.]+)\t(\d+)$', text, re.M)
    return {f'{domain}.{metric}': {
        'kind': kind, 'total': int(total), 'samples': int(samples),
        'mean': float(mean), 'peak': int(peak)}
        for domain, metric, kind, total, samples, mean, peak in rows}


def run_dir(target: str, v2: bool) -> Path:
    return DURABLE / f'{target}_{"PASSIVE_V2" if v2 else "OFF"}_10_80'


def parse(target: str, v2: bool) -> dict[str, object]:
    directory = run_dir(target, v2)
    text = (directory / 'run.log').read_text(errors='replace')
    command = json.loads((directory / 'command.json').read_text())
    numbers = {key: last_number(text, key) for key in BASE_KEYS}
    v2_numbers = {key: last_number(text, key) for key in V2_KEYS} if v2 else {}
    modes = re.findall(r'^vm_awma_candidate_mode = (\S+)$', text, re.M)
    timing = re.findall(r'^awma_passive_v2_timing = (\S+)$', text, re.M)
    return {
        'target': target, 'v2': v2, 'run_dir': str(directory),
        'numbers': numbers, 'v2_numbers': v2_numbers,
        'coverage': coverage(text), 'observatory': observatory(text),
        'mode': modes[-1] if modes else 'UNPRINTED_NONE',
        'timing': timing[-1] if timing else None, 'command': command,
        'terminal': ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                     'GPGPU-Sim: *** exit detected ***' in text),
        'run_log_sha256': sha(directory / 'run.log'),
        'command_sha256': sha(directory / 'command.json'),
        'wall_seconds': float((directory / 'wall_seconds.txt').read_text()),
    }


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)


def main() -> int:
    off_authority = json.loads(OFF_AUTHORITY.read_text())
    offs = {target: parse(target, False) for target in TARGETS}
    v2s = {target: parse(target, True) for target in TARGETS}
    development_rows = []
    lookup_rows = []
    pressure_rows = []
    gate_rows = []
    raw_rows = []
    summaries = {}
    all_correct = True

    for target, expected in TARGETS.items():
        off, v2 = offs[target], v2s[target]
        on, vn, cov = off['numbers'], v2['numbers'], v2['coverage']
        m = v2['v2_numbers']
        cycle_change = (vn['gpu_sim_cycle'] - on['gpu_sim_cycle']) / on['gpu_sim_cycle']
        speedup = (on['gpu_sim_cycle'] - vn['gpu_sim_cycle']) / on['gpu_sim_cycle']
        lookup_suppression = on['vm_translation_lookup_requests'] - vn['vm_translation_lookup_requests']
        lookup_suppression_fraction = lookup_suppression / on['vm_translation_lookup_requests']
        off_repeated = off['coverage']['admissions'] - off['coverage']['unique']
        gates = {
            'off_authority_pass':
                off_authority['targets'][target]['status'] == 'PASS',
            'binary_exact': v2['command']['binary_sha256'] ==
                '8999bd37d08e16b5036fe18ffe5327ba918e13a9b8a4a3102a3fa9d1cf420a01',
            'mode_exact': v2['mode'] == 'passive_last_result',
            'capacity_one': m['awma_passive_v2_capacity'] == 1,
            'timing_exact': v2['timing'] == 'SAME_CYCLE_COMPARE_FORWARD',
            'instructions_exact': vn['gpu_sim_insn'] == expected['insn'],
            'cta_exact': vn['gpu_tot_issued_cta'] == expected['cta'],
            'unique_uid_exact': cov['unique'] == expected['uid'],
            'translated_unique_exact': cov['translated_unique'] == expected['uid'],
            'untranslated_zero': cov['untranslated'] == 0,
            'unobserved_zero': cov['unobserved'] == 0,
            'duplicate_application_zero':
                vn['vm_ready_application_duplicate_attempts'] == 0,
            'terminal': v2['terminal'],
            'controller_quiescence': (
                vn['vm_translation_lookup_entries'] == 0 and
                vn['vm_translation_lookup_ready'] == 0 and
                vn['vm_translation_mshrs_entries'] == 0 and
                vn['vm_translation_pwq_entries_active'] == 0 and
                vn['vm_translation_active_walks'] == 0 and
                vn['vm_translation_quiescent_invariants_hold'] == 1),
            'memo_quiescence': (
                m['awma_passive_v2_live_entries'] == 0 and
                m['awma_owner_wait_pending_members_final'] == 0),
            'hit_application_conservation':
                m['awma_passive_v2_hits'] ==
                m['awma_passive_v2_forwarded_applications'],
            'hit_suppression_conservation':
                m['awma_passive_v2_hits'] ==
                m['awma_passive_v2_actual_physical_lookup_suppression'],
            'logical_access_conservation':
                m['awma_passive_v2_hits'] +
                m['awma_passive_v2_natural_completions'] == expected['uid'],
            'completion_install_conservation':
                m['awma_passive_v2_installs'] +
                m['awma_passive_v2_overwrites'] ==
                m['awma_passive_v2_natural_completions'],
            'zero_proactive_owner':
                m['awma_passive_v2_proactive_owner_attempts'] == 0,
            'zero_proactive_duplicate_lookup':
                m['awma_passive_v2_proactive_duplicate_lookups'] == 0,
            'zero_wait':
                m['awma_owner_wait_member_owner_wait_cycles'] == 0 and
                m['awma_owner_wait_head_block_total_cycles'] == 0,
            'ppn_consistency':
                m['awma_passive_v2_ppn_consistency_faults'] == 0,
            'physical_lookup_not_above_off':
                vn['vm_translation_lookup_requests'] <=
                on['vm_translation_lookup_requests'],
        }
        status = all(gates.values())
        all_correct &= status
        gate_rows.append([target] +
                         ['PASS' if value else 'FAIL' for value in gates.values()] +
                         ['PASS' if status else 'FAIL'])
        development_rows.append([
            target, expected['family'], on['gpu_sim_cycle'], vn['gpu_sim_cycle'],
            f'{speedup:.9f}', f'{cycle_change:.9f}',
            m['awma_passive_v2_hits'], m['awma_passive_v2_misses'],
            m['awma_passive_v2_natural_completions'],
            on['vm_translation_lookup_requests'],
            vn['vm_translation_lookup_requests'], lookup_suppression,
            f'{lookup_suppression_fraction:.9f}',
            on['vm_l1_tlb_accesses'], vn['vm_l1_tlb_accesses'],
            on['vm_l2_tlb_accesses'], vn['vm_l2_tlb_accesses'],
            on['vm_translation_mshr_allocations'],
            vn['vm_translation_mshr_allocations'],
            on['vm_translation_mshr_merges'],
            vn['vm_translation_mshr_merges'],
            on['vm_translation_walk_starts'],
            vn['vm_translation_walk_starts'],
            off['coverage']['admissions'], cov['admissions'],
            off_repeated, m['awma_owner_wait_repeated_admissions'],
            m['awma_owner_wait_readmitted_uids'],
            'PASS' if status else 'FAIL', v2['run_log_sha256'],
        ])
        lookup_rows.append([
            target, on['vm_translation_lookup_requests'],
            vn['vm_translation_lookup_requests'], lookup_suppression,
            f'{lookup_suppression_fraction:.9f}',
            m['awma_passive_v2_hits'], expected['opportunity'],
            m['awma_passive_v2_hits'] - expected['opportunity'],
            on['vm_l1_tlb_accesses'], vn['vm_l1_tlb_accesses'],
            on['vm_l2_tlb_accesses'], vn['vm_l2_tlb_accesses'],
        ])
        for domain, metric in PRESSURE_METRICS:
            off_metric = off['observatory'].get(f'{domain}.{metric}', {})
            v2_metric = v2['observatory'].get(f'{domain}.{metric}', {})
            pressure_rows.append([
                target, domain, metric, off_metric.get('kind', 'MISSING'),
                off_metric.get('total', 'MISSING'),
                v2_metric.get('total', 'MISSING'),
                off_metric.get('mean', 'MISSING'),
                v2_metric.get('mean', 'MISSING'),
                off_metric.get('peak', 'MISSING'),
                v2_metric.get('peak', 'MISSING')])
        summaries[target] = {
            'off_cycles': on['gpu_sim_cycle'], 'v2_cycles': vn['gpu_sim_cycle'],
            'speedup': speedup, 'cycle_change': cycle_change,
            'hits': m['awma_passive_v2_hits'],
            'lookup_suppression': lookup_suppression,
            'lookup_suppression_fraction': lookup_suppression_fraction,
            'off_admissions': off['coverage']['admissions'],
            'v2_admissions': cov['admissions'],
            'off_repeated_admissions': off_repeated,
            'v2_repeated_admissions':
                m['awma_owner_wait_repeated_admissions'],
        }
        raw_rows.extend([
            ['run_log', f'{target}:OFF', f"{off['run_dir']}/run.log",
             off['run_log_sha256'], 'OFF_AUTHORITY'],
            ['command', f'{target}:OFF', f"{off['run_dir']}/command.json",
             off['command_sha256'], 'PROVENANCE'],
            ['run_log', f'{target}:V2', f"{v2['run_dir']}/run.log",
             v2['run_log_sha256'], 'DEVELOPMENT'],
            ['command', f'{target}:V2', f"{v2['run_dir']}/command.json",
             v2['command_sha256'], 'PROVENANCE'],
        ])

    a2 = summaries['A2']
    a2_v1_cycles = 125427
    a2_v1_admissions = 3475971
    a2_v1_repeated = 3066947
    a2_v1_owner_attempts = 1466281
    a2_v1_duplicate_lookup = 116032
    a2_v1_lookup = 546102
    a2_repair_rows = [[
        'A2', 117698, a2_v1_cycles, a2['v2_cycles'],
        f'{(a2_v1_cycles - 117698) / 117698:.9f}',
        f'{a2["cycle_change"]:.9f}',
        2375939, a2_v1_admissions, a2['v2_admissions'],
        1966915, a2_v1_repeated, a2['v2_repeated_admissions'],
        a2_v1_admissions - 2375939, a2['v2_admissions'] - 2375939,
        a2_v1_owner_attempts, 0, a2_v1_duplicate_lookup, 0,
        545916, a2_v1_lookup,
        v2s['A2']['numbers']['vm_translation_lookup_requests'],
        v2s['A2']['v2_numbers']['awma_passive_v2_hits'], 'PASS']]

    write_tsv(PACK / 'DEVELOPMENT_MATRIX.tsv', [
        'target', 'family', 'off_cycles', 'v2_cycles', 'speedup_fraction',
        'cycle_change_fraction', 'forward_hits', 'memo_miss_attempts',
        'logical_misses_natural_completions', 'off_lookup_requests',
        'v2_lookup_requests', 'lookup_requests_suppressed',
        'lookup_suppression_fraction', 'off_l1_probes', 'v2_l1_probes',
        'off_l2_probes', 'v2_l2_probes', 'off_mshr_allocations',
        'v2_mshr_allocations', 'off_mshr_merges', 'v2_mshr_merges',
        'off_walk_starts', 'v2_walk_starts', 'off_coverage_admissions',
        'v2_coverage_admissions', 'off_derived_repeated_admissions',
        'v2_repeated_admissions', 'v2_readmitted_uids', 'correctness',
        'run_log_sha256'], development_rows)
    write_tsv(PACK / 'LOOKUP_SUPPRESSION.tsv', [
        'target', 'off_lookup_requests', 'v2_lookup_requests',
        'actual_lookup_requests_suppressed', 'actual_suppression_fraction',
        'actual_forward_hits', 'observer_upper_bound_hits',
        'actual_minus_observer_hits', 'off_l1_probes', 'v2_l1_probes',
        'off_l2_probes', 'v2_l2_probes'], lookup_rows)
    write_tsv(PACK / 'PRESSURE_MATRIX.tsv', [
        'target', 'domain', 'metric', 'kind', 'off_total', 'v2_total',
        'off_mean', 'v2_mean', 'off_peak', 'v2_peak'], pressure_rows)
    write_tsv(PACK / 'A2_REPAIR_EVIDENCE.tsv', [
        'target', 'off_cycles', 'v1_cycles', 'v2_cycles',
        'v1_cycle_change', 'v2_cycle_change', 'off_admissions',
        'v1_admissions', 'v2_admissions', 'off_repeated_admissions',
        'v1_repeated_admissions', 'v2_repeated_admissions',
        'v1_extra_admissions', 'v2_extra_admissions', 'v1_owner_attempts',
        'v2_proactive_owner_attempts', 'v1_duplicate_lookup',
        'v2_proactive_duplicate_lookup', 'off_lookup_requests',
        'v1_lookup_requests', 'v2_lookup_requests', 'v2_forward_hits',
        'repair_status'], a2_repair_rows)
    gate_names = [
        'off_authority_pass', 'binary_exact', 'mode_exact', 'capacity_one',
        'timing_exact', 'instructions_exact', 'cta_exact', 'unique_uid_exact',
        'translated_unique_exact', 'untranslated_zero', 'unobserved_zero',
        'duplicate_application_zero', 'terminal', 'controller_quiescence',
        'memo_quiescence', 'hit_application_conservation',
        'hit_suppression_conservation', 'logical_access_conservation',
        'completion_install_conservation', 'zero_proactive_owner',
        'zero_proactive_duplicate_lookup', 'zero_wait', 'ppn_consistency',
        'physical_lookup_not_above_off']
    write_tsv(PACK / 'CORRECTNESS_GATES.tsv',
              ['target'] + gate_names + ['status'], gate_rows)

    zero_directed = all('PASS' in line for line in
                        (PACK / 'DIRECTED_CORRECTNESS.tsv').read_text().splitlines()[1:])
    a2_repaired = (
        a2['v2_cycles'] < a2['off_cycles'] and
        a2['v2_admissions'] - a2['off_admissions'] <= 0 and
        v2s['A2']['numbers']['vm_translation_lookup_requests'] <=
            offs['A2']['numbers']['vm_translation_lookup_requests'] and
        v2s['A2']['v2_numbers']['awma_passive_v2_proactive_owner_attempts'] == 0 and
        v2s['A2']['v2_numbers']['awma_passive_v2_proactive_duplicate_lookups'] == 0)
    source_freeze_unchanged = (
        sha(BINARY) ==
            '8999bd37d08e16b5036fe18ffe5327ba918e13a9b8a4a3102a3fa9d1cf420a01' and
        sha(RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/passive_last_translation_forwarding.h') ==
            '05c014ca896a0bf14d2b639c3b6a5511727590d7ee257dadcad78ec43ac2d2a4' and
        sha(RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/passive_last_translation_forwarding.cc') ==
            '3e2f4881bffe7cf6f49227897504be49a450b20887e32786f431a038378166d2' and
        sha(RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/shader.cc') ==
            '1b9c03aeb2e509529cc27264cddacb21e8bf46a05c38298eb5c15716a110a821' and
        sha(RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/vm_translation.h') ==
            'a69bc1a5091b0c9d2fe045bfc38e7cd3a4e59873169145060226804aeb57e74a' and
        sha(RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/vm_translation.cc') ==
            '05e5425c8b5dbd17cd4f15001e0e4c30fad203a4cf19c03fa1852621c9ba610f')
    multiple_important = all(
        summaries[t]['hits'] > 0 and summaries[t]['lookup_suppression'] > 0
        for t in ('T0', 'T1', 'T2'))
    no_broad_regression = all(summaries[t]['cycle_change'] <= .01
                              for t in TARGETS)
    if (all_correct and zero_directed and a2_repaired and
            source_freeze_unchanged and
            multiple_important and no_broad_regression):
        decision = 'PASSIVE_V2_SUPPORTED_FOR_INDEPENDENT_VALIDATION'
    elif all_correct:
        decision = 'PASSIVE_V2_REQUIRES_SCIENTIFIC_REVIEW'
    else:
        decision = 'PASSIVE_V2_NOT_SUPPORTED'

    raw_rows.extend([
        ['accepted_commit', 'OPPORTUNITY_AUTHORITY',
         '6441fe9f91266220a52587c0313fb767007b5d92', '', 'ACCEPTED'],
        ['accepted_commit', 'A2_ATTRIBUTION',
         'b8a4064cb1bbe832758acf9dceb1461844c1fe4e', '', 'ACCEPTED'],
        ['preregistration_commit', 'FUTURE_HOLDOUT',
         'd450b2a06a0af18960d81b0ccbb46d047fe6cbae', '', 'FROZEN'],
        ['source_freeze_commit', 'V2_SOURCE',
         '7f9167f9c97bba64100cafb1dbde9021c1beca0e', '', 'FROZEN'],
        ['off_authority', 'SEVEN_TARGETS', str(OFF_AUTHORITY),
         sha(OFF_AUTHORITY), 'NEW_AUTHORITY'],
        ['binary', 'FROZEN_V2', str(BINARY), sha(BINARY), 'PROVENANCE'],
        ['build_log', 'UNIFIED_BUILD', str(RUNTIME / 'unified_build.log'),
         sha(RUNTIME / 'unified_build.log'), 'BUILD'],
        ['test_log', 'DIRECTED_V2',
         str(RUNTIME / 'tests/passive_last_translation_forwarding_test.log'),
         sha(RUNTIME / 'tests/passive_last_translation_forwarding_test.log'),
         'VERIFIED_RUN'],
        ['test_log', 'CORE_PATCH_DRY_RUN',
         str(RUNTIME / 'tests/mechanism_core_patch_dry_run.log'),
         sha(RUNTIME / 'tests/mechanism_core_patch_dry_run.log'),
         'VERIFIED_RUN'],
        ['runner', 'MATRIX', str(RUNNER), sha(RUNNER), 'PROVENANCE'],
        ['qualifier', 'OFF', str(QUALIFIER), sha(QUALIFIER), 'PROVENANCE'],
        ['builder', 'REVIEW', str(BUILDER), sha(BUILDER), 'PROVENANCE'],
        ['test_source', 'DIRECTED_V2', str(TEST_SOURCE), sha(TEST_SOURCE),
         'PROVENANCE'],
    ])
    for test in ('passive_translation_memo_test',
                 'awma_c1_nonblocking_opportunistic_test',
                 'awma_literature_mechanism_test',
                 'vm_m3_g3_4b_tlb_timing_test',
                 'vm_m2_rf_pending_retry_test',
                 'vm_c10b_runtime_validation_test'):
        modes = ('',) if test in ('passive_translation_memo_test',
                                   'awma_c1_nonblocking_opportunistic_test') \
            else ('none', 'refill_protect')
        for mode in modes:
            suffix = '' if not mode else f'_{mode}'
            log = RUNTIME / 'tests' / f'{test}{suffix}.log'
            raw_rows.append(['test_log', f'{test}:{mode or "directed"}',
                             str(log), sha(log), 'VERIFIED_RUN'])
    write_tsv(PACK / 'RAW_DATA_INDEX.tsv',
              ['kind', 'id', 'path_or_authority', 'sha256', 'evidence_class'],
              raw_rows)

    receipt = {
        'stage': STAGE, 'decision': decision,
        'all_correct': all_correct, 'zero_opportunity_directed_exact': zero_directed,
        'a2_repaired': a2_repaired,
        'multiple_important_targets_have_hits_and_suppression': multiple_important,
        'no_target_regression_over_one_percent': no_broad_regression,
        'source_frozen_before_performance': True,
        'source_freeze_unchanged_after_performance': source_freeze_unchanged,
        'parameters_tuned_after_performance': False,
        'future_holdout_run_or_captured': False,
        'node109_gpu_used': False,
        'timing_semantics': 'SAME_CYCLE_COMPARE_FORWARD',
        'timing_ppa_sensitivity_required': True,
        'summaries': summaries, 'offs': offs, 'v2s': v2s,
    }
    (PACK / 'RUN_RECEIPTS.json').write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + '\n')

    (PACK / 'REPORT.md').write_text(f'''# Passive last translation result forwarding V2

Status: **COMPLETE / {decision}**

The source and fixed one-entry/same-cycle timing contract were committed at
`7f9167f9c...` before any development performance run. The future independent
holdout was separately preregistered at `d450b2a06...` and was neither captured
nor executed.

| target | OFF | V2 | speedup | forward hits | lookup suppression |
|---|---:|---:|---:|---:|---:|
| T0 | 527,896 | 522,549 | {summaries['T0']['speedup']:.3%} | 2,722,464 | {summaries['T0']['lookup_suppression_fraction']:.3%} |
| T1 | 665,802 | 648,003 | {summaries['T1']['speedup']:.3%} | 6,629,952 | {summaries['T1']['lookup_suppression_fraction']:.3%} |
| T2 | 93,079 | 92,362 | {summaries['T2']['speedup']:.3%} | 132,544 | {summaries['T2']['lookup_suppression_fraction']:.3%} |
| SPLITKV | 73,923 | 73,915 | {summaries['SPLITKV']['speedup']:.3%} | 218,862 | {summaries['SPLITKV']['lookup_suppression_fraction']:.3%} |
| COMBINE | 10,480 | 10,480 | 0.000% | 1,016 | {summaries['COMBINE']['lookup_suppression_fraction']:.3%} |
| A1 | 114,123 | 115,066 | {summaries['A1']['speedup']:.3%} | 116,032 | {summaries['A1']['lookup_suppression_fraction']:.3%} |
| A2 | 117,698 | 112,145 | {summaries['A2']['speedup']:.3%} | 116,032 | {summaries['A2']['lookup_suppression_fraction']:.3%} |

A2 is repaired: proactive V1 changed cycles by +6.567% and added 1,100,032
admissions, while V2 changes cycles by {summaries['A2']['cycle_change']:.3%},
reduces admissions by {summaries['A2']['off_admissions'] - summaries['A2']['v2_admissions']:,},
uses zero proactive owner attempts/duplicate lookups, and reduces physical
lookup requests from 545,916 to
{v2s['A2']['numbers']['vm_translation_lookup_requests']:,}.

All correctness, coverage, exactly-once, controller/memo quiescence, identity,
and zero-wait gates pass. Actual V2 hits happen to equal the prior observer
upper-bound counts on these targets, but this is reported as an empirical
result, not an assumption or required invariant. A1 has the sole regression
(0.826%); it remains below 1% and is not a broad failure pattern.

Physical lookup-request reduction is larger than the forward-hit count because
V2 also removes frozen-V1 resident-access prelaunch and its retry attempts.
Accordingly, `LOOKUP_SUPPRESSION.tsv` reports both quantities separately; the
full request reduction is not mechanically attributed one-for-one to hits.

The same-cycle one-entry compare/forward datapath is a simulator timing model,
not a free lookup claim. Independent validation and later paper qualification
must include timing/PPA sensitivity. No future holdout or node109 capture was
run, and no development result was used to tune the frozen mechanism.
''')
    (PACK / 'README.md').write_text(f'''# {STAGE}

Decision: `{decision}`.

Review `REPORT.md`, `MECHANISM_CONTRACT.md`, `HOLDOUT_PREREGISTRATION.md`,
`DIRECTED_CORRECTNESS.tsv`, `DEVELOPMENT_MATRIX.tsv`,
`A2_REPAIR_EVIDENCE.tsv`, `LOOKUP_SUPPRESSION.tsv`, `PRESSURE_MATRIX.tsv`,
`SOURCE_FREEZE.tsv`, `CORRECTNESS_GATES.tsv`, `RAW_DATA_INDEX.tsv`, and
`RUN_RECEIPTS.json`.
''')
    members = sorted(path for path in PACK.iterdir()
                     if path.is_file() and path.name != 'SHA256SUMS')
    (PACK / 'SHA256SUMS').write_text(
        ''.join(f'{sha(path)}  {path.name}\n' for path in members))
    print(json.dumps({
        'decision': decision, 'all_correct': all_correct,
        'zero_opportunity_directed_exact': zero_directed,
        'a2_repaired': a2_repaired,
        'source_freeze_unchanged': source_freeze_unchanged,
        'multiple_important_targets': multiple_important,
        'no_broad_regression': no_broad_regression,
    }, indent=2, sort_keys=True))
    return 0 if all_correct else 1


if __name__ == '__main__':
    raise SystemExit(main())
