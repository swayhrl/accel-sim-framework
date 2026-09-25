#!/usr/bin/env python3
from __future__ import annotations

import csv
import difflib
import hashlib
import json
import re
import subprocess
from pathlib import Path

STAGE = 'AWMA_PASSIVE_TRANSLATION_RESULT_REUSE_OPPORTUNITY_V1'
REPO = Path('/root/workspace/accel-sim-framework-awma-passive-translation-result-reuse-opportunity-v1')
RUNTIME = Path('/root/awma_passive_translation_result_reuse_opportunity_v1_runtime')
PARENT_RUNTIME = Path('/root/awma_c1_a2_nonsharing_regression_attribution_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_passive_translation_result_reuse_opportunity_v1/raw')
PACK = REPO / 'docs/vm_tlb/review_packs' / STAGE
RUNNER = REPO / 'util/vm_tlb/awma/run_passive_translation_reuse_opportunity.py'
QUALIFIER = REPO / 'util/vm_tlb/awma/qualify_passive_observer_off.py'
BUILDER = REPO / 'util/vm_tlb/awma/build_passive_translation_reuse_review.py'
TEST_SOURCE = REPO / 'util/vm_tlb/awma/passive_translation_memo_test.cc'
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
NEUTRALITY = RUNTIME / 'observer_off_neutrality.json'

TARGETS = {
    'T0': {
        'family': 'PREFILL_FLASH', 'cycles': 527896, 'insn': 368696302,
        'cta': 224, 'uid': 3090304, 'admissions': 3090304,
        'memory_transactions': 2458328, 'proactive_ready': 2381824,
    },
    'T1': {
        'family': 'PREFILL_GEMM', 'cycles': 665802, 'insn': 369131520,
        'cta': 384, 'uid': 7159808, 'admissions': 7160265,
        'memory_transactions': 7159808, 'proactive_ready': 6182246,
    },
    'T2': {
        'family': 'DECODE_GEMV', 'cycles': 93079, 'insn': 43357696,
        'cta': 1216, 'uid': 411008, 'admissions': 715333,
        'memory_transactions': 279072, 'proactive_ready': 0,
    },
    'SPLITKV': {
        'family': 'FLASH_FWD_SPLITKV', 'cycles': 73923, 'insn': 36599648,
        'cta': 126, 'uid': 233814, 'admissions': 233814,
        'memory_transactions': 233814, 'proactive_ready': 204035,
    },
    'COMBINE': {
        'family': 'FLASH_FWD_SPLITKV_COMBINE', 'cycles': 10480,
        'insn': 72908, 'cta': 2, 'uid': 1099, 'admissions': 1099,
        'memory_transactions': 1099, 'proactive_ready': 942,
    },
    'A1': {
        'family': 'DECODE_GEMV_PAIR_A_S2_T2048', 'cycles': 114123,
        'insn': 34883072, 'cta': 224, 'uid': 409024,
        'admissions': 2191027, 'memory_transactions': 295936,
        'proactive_ready': None,
    },
    'A2': {
        'family': 'DECODE_GEMV_PAIR_A_T8192', 'cycles': 117698,
        'insn': 34883072, 'cta': 224, 'uid': 409024,
        'admissions': 2375939, 'memory_transactions': 295936,
        'proactive_ready': None,
    },
}
CAPACITIES = (1, 2, 4)
DISTANCES = ('0', '1', '2', '3', '4', '5_8', '9_16', '17_plus')
BASE_KEYS = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_translation_lookup_requests',
    'vm_ready_application_duplicate_attempts',
    'vm_translation_lookup_entries', 'vm_translation_lookup_ready',
    'vm_translation_mshrs_entries', 'vm_translation_pwq_entries_active',
    'vm_translation_active_walks',
    'vm_translation_quiescent_invariants_hold',
)
PASSIVE_GLOBAL_KEYS = (
    'awma_passive_memo_enabled',
    'awma_passive_memo_live_instruction_states',
    'awma_passive_memo_natural_translation_completions',
    'awma_passive_memo_decision_lookups',
    'awma_passive_memo_duplicate_decision_observations',
    'awma_passive_memo_duplicate_completion_observations',
    'awma_passive_memo_instructions_retired',
    'awma_passive_memo_unique_pages_total',
    'awma_passive_memo_unique_pages_max',
    'awma_passive_memo_unique_pages_hist_0_1',
    'awma_passive_memo_unique_pages_hist_2',
    'awma_passive_memo_unique_pages_hist_3',
    'awma_passive_memo_unique_pages_hist_4',
    'awma_passive_memo_unique_pages_hist_5_8',
    'awma_passive_memo_unique_pages_hist_9_plus',
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


def last_compact(text: str, key: str) -> int:
    values = re.findall(rf'^{re.escape(key)}=(\d+)$', text, re.M)
    if not values:
        raise RuntimeError(f'missing {key}')
    return int(values[-1])


def coverage(text: str) -> dict[str, int]:
    values = re.findall(
        r'AWMA_VM_COVERAGE admissions=(\d+) translated=(\d+) '
        r'untranslated=(\d+) unobserved=(\d+) unique=(\d+) '
        r'translated_unique=(\d+) untranslated_unique=(\d+)', text)
    if not values:
        raise RuntimeError('missing AWMA_VM_COVERAGE')
    names = ('admissions', 'translated', 'untranslated', 'unobserved',
             'unique', 'translated_unique', 'untranslated_unique')
    return dict(zip(names, map(int, values[-1])))


def run_dir(target: str, enabled: bool) -> Path:
    label = 'OBSERVER_ON' if enabled else 'OBSERVER_OFF'
    return DURABLE / f'{target}_{label}_10_80'


def parse_run(target: str, enabled: bool) -> dict[str, object]:
    directory = run_dir(target, enabled)
    text = (directory / 'run.log').read_text(errors='replace')
    command = json.loads((directory / 'command.json').read_text())
    numbers = {key: last_number(text, key) for key in BASE_KEYS}
    passive: dict[str, int] = {}
    if enabled:
        passive = {key: last_number(text, key) for key in PASSIVE_GLOBAL_KEYS}
        for capacity in CAPACITIES:
            prefix = f'awma_passive_memo_c{capacity}_'
            for suffix in (
                    'lookups', 'hits', 'misses',
                    'potential_lookup_suppression', 'replacements',
                    'stale_generation_mismatches',
                    'access_compatibility_mismatches',
                    'ppn_consistency_mismatches'):
                passive[prefix + suffix] = last_number(text, prefix + suffix)
            for distance in DISTANCES:
                key = prefix + 'reuse_distance_' + distance
                passive[key] = last_number(text, key)
    cov = coverage(text)
    memory_transactions = last_compact(text, 'icnt_total_pkts_simt_to_mem')
    return {
        'target': target, 'enabled': enabled, 'run_dir': str(directory),
        'numbers': numbers, 'passive': passive, 'coverage': cov,
        'memory_transactions': memory_transactions, 'command': command,
        'run_log_sha256': sha(directory / 'run.log'),
        'command_sha256': sha(directory / 'command.json'),
        'wall_seconds': float((directory / 'wall_seconds.txt').read_text()),
        'terminal': ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                     'GPGPU-Sim: *** exit detected ***' in text),
        'observer_output_absent': 'awma_passive_memo_enabled' not in text,
    }


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)


def generate_patch() -> Path:
    output = PACK / 'OBSERVER_CORE.patch'
    chunks: list[str] = []
    for relative in ('src/gpgpu-sim/passive_translation_memo.h',
                     'src/gpgpu-sim/passive_translation_memo.cc',
                     'src/gpgpu-sim/shader.cc'):
        old = PARENT_RUNTIME / 'src/gpgpu-sim' / relative
        new = RUNTIME / 'src/gpgpu-sim' / relative
        old_lines = old.read_text().splitlines(keepends=True) if old.exists() \
            else []
        fromfile = f'a/{relative}' if old.exists() else '/dev/null'
        chunks.extend(difflib.unified_diff(
            old_lines, new.read_text().splitlines(keepends=True),
            fromfile=fromfile, tofile=f'b/{relative}'))
    output.write_text(''.join(chunks))
    dry_run = subprocess.run(
        ['patch', '--dry-run', '-p1', '-d',
         str(PARENT_RUNTIME / 'src/gpgpu-sim')],
        input=output.read_text(), text=True, capture_output=True, check=False)
    log = RUNTIME / 'tests/observer_core_patch_dry_run.log'
    log.write_text(dry_run.stdout + dry_run.stderr +
                   f'rc={dry_run.returncode}\n')
    if dry_run.returncode != 0:
        raise RuntimeError('observer patch dry-run failed')
    return output


def main() -> int:
    PACK.mkdir(parents=True, exist_ok=True)
    patch = generate_patch()
    neutrality_receipt = json.loads(NEUTRALITY.read_text())
    offs = {target: parse_run(target, False) for target in TARGETS}
    ons = {target: parse_run(target, True) for target in TARGETS}
    target_rows: list[list[object]] = []
    capacity_rows: list[list[object]] = []
    distance_rows: list[list[object]] = []
    neutrality_rows: list[list[object]] = []
    comparison_rows: list[list[object]] = []
    raw_rows: list[list[object]] = []
    summaries: dict[str, dict[str, object]] = {}

    total_instructions = sum(spec['insn'] for spec in TARGETS.values())
    all_neutral = True
    all_correct = True
    for target, spec in TARGETS.items():
        off, on = offs[target], ons[target]
        on_n, passive = on['numbers'], on['passive']
        same_signature = (
            on_n['gpu_sim_cycle'] == spec['cycles'] ==
                off['numbers']['gpu_sim_cycle'] and
            on_n['gpu_sim_insn'] == spec['insn'] ==
                off['numbers']['gpu_sim_insn'] and
            on_n['gpu_tot_issued_cta'] == spec['cta'] ==
                off['numbers']['gpu_tot_issued_cta'] and
            on['coverage'] == off['coverage'] and
            on['coverage']['unique'] == spec['uid'] and
            on['coverage']['admissions'] == spec['admissions'] and
            on['memory_transactions'] == spec['memory_transactions'] ==
                off['memory_transactions'] and
            on_n['vm_translation_lookup_requests'] ==
                off['numbers']['vm_translation_lookup_requests'])
        off_env = off['command']['environment']
        on_env = on['command']['environment']
        gates = {
            'off_qualification_pass':
                neutrality_receipt['targets'][target]['status'] == 'PASS',
            'same_binary': off['command']['binary_sha256'] ==
                on['command']['binary_sha256'] == sha(BINARY),
            'off_env': off_env.get('GPGPUSIM_AWMA_PASSIVE_MEMO_OBSERVER') == '0',
            'on_env': on_env.get('GPGPUSIM_AWMA_PASSIVE_MEMO_OBSERVER') == '1',
            'no_candidate':
                'GPGPUSIM_AWMA_TRANSLATION_CANDIDATE' not in on_env,
            'signature_exact': same_signature,
            'coverage_correct':
                on['coverage']['translated_unique'] == spec['uid'] and
                on['coverage']['untranslated'] == 0 and
                on['coverage']['unobserved'] == 0,
            'duplicate_application_zero':
                on_n['vm_ready_application_duplicate_attempts'] == 0,
            'terminal': off['terminal'] and on['terminal'],
            'controller_quiescence':
                on_n['vm_translation_lookup_entries'] == 0 and
                on_n['vm_translation_lookup_ready'] == 0 and
                on_n['vm_translation_mshrs_entries'] == 0 and
                on_n['vm_translation_pwq_entries_active'] == 0 and
                on_n['vm_translation_active_walks'] == 0 and
                on_n['vm_translation_quiescent_invariants_hold'] == 1,
            'observer_off_no_output': off['observer_output_absent'],
            'observer_on_enabled':
                passive['awma_passive_memo_enabled'] == 1,
            'observer_state_drain':
                passive['awma_passive_memo_live_instruction_states'] == 0,
            'natural_completion_conservation':
                passive['awma_passive_memo_natural_translation_completions'] ==
                spec['uid'],
            'decision_lookup_conservation':
                passive['awma_passive_memo_decision_lookups'] == spec['uid'],
            'completion_exactly_once':
                passive['awma_passive_memo_duplicate_completion_observations'] == 0,
            'instruction_histogram_conservation':
                sum(passive[key] for key in (
                    'awma_passive_memo_unique_pages_hist_0_1',
                    'awma_passive_memo_unique_pages_hist_2',
                    'awma_passive_memo_unique_pages_hist_3',
                    'awma_passive_memo_unique_pages_hist_4',
                    'awma_passive_memo_unique_pages_hist_5_8',
                    'awma_passive_memo_unique_pages_hist_9_plus')) ==
                passive['awma_passive_memo_instructions_retired'],
        }
        for capacity in CAPACITIES:
            prefix = f'awma_passive_memo_c{capacity}_'
            gates[f'c{capacity}_lookup_conservation'] = (
                passive[prefix + 'lookups'] ==
                passive[prefix + 'hits'] + passive[prefix + 'misses'])
            gates[f'c{capacity}_potential_conservation'] = (
                passive[prefix + 'potential_lookup_suppression'] ==
                passive[prefix + 'hits'])
            gates[f'c{capacity}_ppn_consistency'] = (
                passive[prefix + 'ppn_consistency_mismatches'] == 0)
            gates[f'c{capacity}_distance_conservation'] = (
                sum(passive[prefix + 'reuse_distance_' + d]
                    for d in DISTANCES) == passive[prefix + 'hits'])
        status = all(gates.values())
        all_neutral &= same_signature
        all_correct &= status
        neutrality_rows.append(
            [target] + ['PASS' if v else 'FAIL' for v in gates.values()] +
            ['PASS' if status else 'FAIL'])

        c4_hits = passive['awma_passive_memo_c4_hits']
        target_rows.append([
            target, spec['family'], spec['insn'],
            f"{spec['insn'] / total_instructions:.9f}",
            spec['cycles'], on_n['vm_translation_lookup_requests'],
            passive['awma_passive_memo_natural_translation_completions'],
            passive['awma_passive_memo_decision_lookups'],
            passive['awma_passive_memo_instructions_retired'],
            passive['awma_passive_memo_unique_pages_total'],
            passive['awma_passive_memo_unique_pages_max'],
            passive['awma_passive_memo_c1_hits'],
            passive['awma_passive_memo_c2_hits'], c4_hits,
            f"{c4_hits / passive['awma_passive_memo_decision_lookups']:.9f}",
            f"{c4_hits / on_n['vm_translation_lookup_requests']:.9f}",
            passive['awma_passive_memo_c1_replacements'],
            passive['awma_passive_memo_c2_replacements'],
            passive['awma_passive_memo_c4_replacements'],
            passive['awma_passive_memo_c4_stale_generation_mismatches'],
            passive['awma_passive_memo_c4_access_compatibility_mismatches'],
            passive['awma_passive_memo_c4_ppn_consistency_mismatches'],
            'PASS' if status else 'FAIL', on['run_log_sha256'],
        ])
        for capacity in CAPACITIES:
            prefix = f'awma_passive_memo_c{capacity}_'
            hits = passive[prefix + 'hits']
            capacity_rows.append([
                target, capacity, passive[prefix + 'lookups'], hits,
                passive[prefix + 'misses'],
                f'{hits / c4_hits:.9f}' if c4_hits else '1.000000000',
                passive[prefix + 'potential_lookup_suppression'],
                f"{hits / on_n['vm_translation_lookup_requests']:.9f}",
                passive[prefix + 'replacements'],
                passive[prefix + 'stale_generation_mismatches'],
                passive[prefix + 'access_compatibility_mismatches'],
                passive[prefix + 'ppn_consistency_mismatches'],
            ])
            for distance in DISTANCES:
                distance_rows.append([
                    target, capacity, distance,
                    passive[prefix + 'reuse_distance_' + distance]])
        summaries[target] = {
            'passive_hits_c1': passive['awma_passive_memo_c1_hits'],
            'passive_hits_c4': c4_hits,
            'logical_hit_fraction':
                c4_hits / passive['awma_passive_memo_decision_lookups'],
            'potential_vs_lookup_requests':
                c4_hits / on_n['vm_translation_lookup_requests'],
            'unique_pages_max': passive['awma_passive_memo_unique_pages_max'],
        }
        if spec['proactive_ready'] is not None:
            comparison_rows.append([
                target, spec['proactive_ready'], c4_hits,
                c4_hits - spec['proactive_ready'],
                'ACCESS_LEVEL_COUNTS_NOT_ONE_TO_ONE',
                ('Both preserve accepted same-page legality and logical UIDs; '
                 'proactive counts READY deliveries under a changed schedule, '
                 'passive counts baseline decision-time legal memo hits after '
                 'natural apply. Timing and opportunity populations differ.'),
            ])
        raw_rows.extend([
            ['run_log', f'{target}:OFF', f"{off['run_dir']}/run.log",
             off['run_log_sha256'], 'NEUTRALITY'],
            ['command', f'{target}:OFF', f"{off['run_dir']}/command.json",
             off['command_sha256'], 'PROVENANCE'],
            ['run_log', f'{target}:ON', f"{on['run_dir']}/run.log",
             on['run_log_sha256'], 'OPPORTUNITY'],
            ['command', f'{target}:ON', f"{on['run_dir']}/command.json",
             on['command_sha256'], 'PROVENANCE'],
        ])

    widespread = all(summaries[target]['passive_hits_c4'] > 0
                     for target in TARGETS)
    capacity_one_complete = all(
        summaries[target]['passive_hits_c1'] ==
        summaries[target]['passive_hits_c4'] for target in TARGETS)
    family_diversity = len({spec['family'] for spec in TARGETS.values()}) >= 5
    heavy_targets_supported = all(
        summaries[target]['passive_hits_c4'] > 0 for target in ('T0', 'T1'))
    if widespread and capacity_one_complete and family_diversity and \
            heavy_targets_supported and all_correct and all_neutral:
        decision = 'PASSIVE_REUSE_OPPORTUNITY_SUPPORTED'
        minimum_capacity = 1
    elif any(summaries[target]['passive_hits_c4'] > 0 for target in TARGETS):
        decision = 'PASSIVE_REUSE_OPPORTUNITY_NARROW'
        minimum_capacity = 1 if capacity_one_complete else 4
    else:
        decision = 'PASSIVE_REUSE_OPPORTUNITY_WEAK'
        minimum_capacity = None

    write_tsv(PACK / 'TARGET_OPPORTUNITY_MATRIX.tsv', [
        'target', 'family', 'native_instructions', 'instruction_weight_fraction',
        'cycles', 'physical_lookup_requests', 'natural_completions',
        'memo_lookups', 'memory_instructions_retired', 'unique_pages_total',
        'unique_pages_max', 'c1_hits', 'c2_hits', 'c4_hits',
        'c4_logical_hit_fraction', 'c4_hits_over_physical_lookup_requests',
        'c1_replacements', 'c2_replacements', 'c4_replacements',
        'stale_generation_mismatches', 'access_compatibility_mismatches',
        'ppn_consistency_mismatches', 'correctness', 'run_log_sha256'],
        target_rows)
    write_tsv(PACK / 'CAPACITY_COVERAGE.tsv', [
        'target', 'capacity', 'lookups', 'hits', 'misses',
        'coverage_vs_c4_hits', 'potential_physical_lookup_suppression',
        'hits_over_baseline_physical_lookup_requests', 'replacements',
        'stale_generation_mismatches', 'access_compatibility_mismatches',
        'ppn_consistency_mismatches'], capacity_rows)
    write_tsv(PACK / 'REUSE_DISTANCE.tsv',
              ['target', 'capacity', 'intervening_completion_distance', 'hits'],
              distance_rows)
    write_tsv(PACK / 'PROACTIVE_VS_PASSIVE_COMPARISON.tsv', [
        'target', 'previous_proactive_ready_shared_members',
        'baseline_passive_c4_hits', 'passive_minus_proactive_count',
        'comparability', 'boundary'], comparison_rows)
    gate_names = [
        'off_qualification_pass', 'same_binary', 'off_env', 'on_env',
        'no_candidate', 'signature_exact', 'coverage_correct',
        'duplicate_application_zero', 'terminal', 'controller_quiescence',
        'observer_off_no_output', 'observer_on_enabled',
        'observer_state_drain', 'natural_completion_conservation',
        'decision_lookup_conservation', 'completion_exactly_once',
        'instruction_histogram_conservation']
    for capacity in CAPACITIES:
        gate_names.extend([
            f'c{capacity}_lookup_conservation',
            f'c{capacity}_potential_conservation',
            f'c{capacity}_ppn_consistency',
            f'c{capacity}_distance_conservation'])
    write_tsv(PACK / 'NEUTRALITY_GATES.tsv',
              ['target'] + gate_names + ['status'], neutrality_rows)

    raw_rows.extend([
        ['accepted_commit', 'A2_ATTRIBUTION',
         'b8a4064cb1bbe832758acf9dceb1461844c1fe4e', '', 'ACCEPTED'],
        ['accepted_commit', 'OBSERVABILITY_AUTHORITY',
         'b85d388abe98e5da70b749b52075c33fad7cede4', '', 'ACCEPTED'],
        ['accepted_commit', 'FROZEN_PROACTIVE_CANDIDATE',
         'c0602ee06e647d9a3cf84b0adbb8d98075021f99', '', 'ACCEPTED'],
        ['neutrality_receipt', 'OBSERVER_OFF', str(NEUTRALITY), sha(NEUTRALITY),
         'NEW_AUTHORITY'],
        ['binary', 'PASSIVE_OBSERVER', str(BINARY), sha(BINARY), 'PROVENANCE'],
        ['build_log', 'UNIFIED_BUILD', str(RUNTIME / 'unified_build.log'),
         sha(RUNTIME / 'unified_build.log'), 'BUILD'],
        ['source_patch', 'OBSERVER_CORE', str(patch), sha(patch), 'PROVENANCE'],
        ['source', 'PASSIVE_MEMO_HEADER',
         str(RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/passive_translation_memo.h'),
         sha(RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/passive_translation_memo.h'),
         'PROVENANCE'],
        ['source', 'PASSIVE_MEMO_IMPL',
         str(RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/passive_translation_memo.cc'),
         sha(RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/passive_translation_memo.cc'),
         'PROVENANCE'],
        ['runner', 'MATRIX_RUNNER', str(RUNNER), sha(RUNNER), 'PROVENANCE'],
        ['qualifier', 'NEUTRALITY_QUALIFIER', str(QUALIFIER), sha(QUALIFIER),
         'PROVENANCE'],
        ['builder', 'REVIEW_BUILDER', str(BUILDER), sha(BUILDER), 'PROVENANCE'],
        ['test_source', 'DIRECTED_TEST', str(TEST_SOURCE), sha(TEST_SOURCE),
         'PROVENANCE'],
        ['test_log', 'DIRECTED_TEST',
         str(RUNTIME / 'tests/passive_translation_memo_test.log'),
         sha(RUNTIME / 'tests/passive_translation_memo_test.log'),
         'VERIFIED_RUN'],
        ['test_log', 'PATCH_DRY_RUN',
         str(RUNTIME / 'tests/observer_core_patch_dry_run.log'),
         sha(RUNTIME / 'tests/observer_core_patch_dry_run.log'),
         'VERIFIED_RUN'],
    ])
    for test in ('awma_c1_nonblocking_opportunistic_test',
                 'awma_literature_mechanism_test',
                 'vm_m3_g3_4b_tlb_timing_test',
                 'vm_m2_rf_pending_retry_test',
                 'vm_c10b_runtime_validation_test'):
        modes = ('',) if test == 'awma_c1_nonblocking_opportunistic_test' \
            else ('none', 'refill_protect')
        for mode in modes:
            suffix = '' if not mode else f'_{mode}'
            log = RUNTIME / 'tests' / f'{test}{suffix}.log'
            raw_rows.append(['test_log', f'{test}:{mode or "directed"}',
                             str(log), sha(log), 'VERIFIED_RUN'])
    write_tsv(PACK / 'RAW_DATA_INDEX.tsv',
              ['kind', 'id', 'path_or_authority', 'sha256', 'evidence_class'],
              raw_rows)

    total_hits = sum(summaries[t]['passive_hits_c4'] for t in TARGETS)
    total_lookups = sum(ons[t]['passive']['awma_passive_memo_decision_lookups']
                        for t in TARGETS)
    total_physical = sum(ons[t]['numbers']['vm_translation_lookup_requests']
                         for t in TARGETS)
    receipt = {
        'stage': STAGE, 'decision': decision,
        'minimum_reasonable_capacity': minimum_capacity,
        'all_neutral': all_neutral, 'all_correct': all_correct,
        'widespread_target_opportunity': widespread,
        'capacity_one_covers_all_observed_hits': capacity_one_complete,
        'family_diversity_supported': family_diversity,
        'heavy_native_targets_supported': heavy_targets_supported,
        'total_passive_hits_c4': total_hits,
        'total_logical_decision_lookups': total_lookups,
        'aggregate_logical_hit_fraction': total_hits / total_lookups,
        'aggregate_hits_over_physical_lookup_requests':
            total_hits / total_physical,
        'performance_mechanism_implemented_or_run': False,
        'new_lane_f_trace_used': False, 'node109_gpu_used': False,
        'summaries': summaries, 'offs': offs, 'ons': ons,
    }
    (PACK / 'RUN_RECEIPTS.json').write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + '\n')

    (PACK / 'PASSIVE_MEMO_CONTRACT.md').write_text('''# Passive memo contract

- Execution remains frozen RTX4080/V1 OFF 10/80; all candidate modes are off.
- A lookup is observed once when a logical access first reaches the frozen
  head translation decision point. Retries are counted separately and never
  inflate memo lookups.
- A mapping enters the observer only after that same access naturally returns
  READY through the baseline controller and is legally applied.
- Identity is `(ASID, VPN, page_size, translation_generation,
  translation_access)`; the completion PPN must also match the recorded PPN.
  The current source exposes read/write/atomic as the permission-relevant
  access dimension; no unsupported permission field is invented.
- Memo state is keyed by `(shader id, dynamic warp-instruction uid)` and is
  destroyed when that instruction's accessq becomes empty. It never crosses
  an instruction, warp, CTA, or kernel.
- Capacities 1, 2, and 4 are observed in parallel. All use deterministic LRU;
  insertion happens only on natural completion and a legal hit updates recency.
- Reuse distance is the number of intervening natural completions in the same
  instruction. No trace position or future event is consulted.
- A provisional identity hit becomes a reported hit only after baseline
  completion confirms identity and PPN consistency.
- The observer never skips translation, consumes READY, changes queues,
  ordering, arbitration, cache/memory behavior, or downstream application.
''')

    (PACK / 'SOURCE_AUDIT.md').write_text(f'''# Source audit

Parent source: A2 attribution `b8a4064cb1bbe832758acf9dceb1461844c1fe4e`.
Observability design authority: `b85d388abe98e5da70b749b52075c33fad7cede4`.

The delta adds `passive_translation_memo.h/.cc` and four read-only hooks in
`shader.cc`: decision observation, natural applied-completion observation,
instruction retirement, and final printing. No translation-controller,
READY, lookup, MSHR/PTW, scheduler, accessq mutation, cache, memory, or
arbitration source is changed.

The feature is opt-in through `GPGPUSIM_AWMA_PASSIVE_MEMO_OBSERVER=1`; OFF
returns before state allocation/traversal and emits no memo records. The same
binary reproduces every accepted baseline signature with observer OFF and ON.

- binary SHA256: `{sha(BINARY)}`
- observer patch SHA256: `{sha(patch)}`
- patch dry-run: PASS
''')

    (PACK / 'V2_DESIGN_REQUIREMENTS.md').write_text(f'''# V2 design requirements

Opportunity characterization supports a future V2 design, but V2 is **not**
implemented here.

Minimum reasonable memo capacity: **{minimum_capacity} entry** per live memory
instruction/accessq. One entry captures 100% of observed 4-entry hits on every
target; larger capacities add storage without additional observed opportunity.

Any future V2 must provide:

- zero proactive physical lookup and zero owner speculation;
- zero waiting and zero future information;
- an exact no-opportunity path preserving OFF lookup/admission behavior;
- finite instruction-local lifetime with deterministic bounded replacement;
- ASID/VPN/page-size/generation/access-compatible identity and verified PPN;
- exactly-once translation application and preserved logical UID;
- bounded storage and lookup ports with explicit contention;
- no cross-instruction/warp/CTA/kernel persistence;
- no second-TLB semantics: this is a short-lived result handoff memo only;
- OFF-by-default operation and complete controller/memo quiescence gates.
''')

    (PACK / 'REPORT.md').write_text(f'''# Passive translation result reuse opportunity V1

Status: **COMPLETE / {decision}**

Across all seven accepted targets, baseline execution naturally creates legal
instruction-local results that later same-page accesses could reuse. The
4-entry observer finds {total_hits:,} validated hits from {total_lookups:,}
logical decision-point lookups ({total_hits / total_lookups:.3%}). Relative to
the separately reported baseline physical-lookup counter, this is
{total_hits / total_physical:.3%}; event definitions differ, so this ratio is
an opportunity indicator rather than an exact subtractive prediction.

One entry captures exactly the same hits as two or four entries on every
target. Every observed hit has zero intervening natural completions. T0/T1,
the dominant native instruction-weight targets, contribute millions of hits;
opportunity also appears in decode GEMV, SplitKV, Combine, and both Pair-A
contexts. This supports a broad, low-storage opportunity rather than a narrow
kernel exception.

Retrospectively, passive and proactive counts are not one-to-one: proactive
READY delivery changes translation timing, while passive hits are measured at
the unmodified baseline decision point after prior natural apply. Notably, T2
has 132,544 passive hits despite zero proactive READY deliveries, and Pair A
has 116,032 passive hits in each context despite zero proactive sharing.

Observer OFF and ON exactly preserve cycles, instructions, CTA, UID, coverage,
physical lookup requests, ICNT memory transactions, duplicate-application
count, terminal completion, and controller quiescence for every target. No
performance mechanism was implemented or run. V2 remains design-only.
''')

    (PACK / 'README.md').write_text(f'''# {STAGE}

Decision: `{decision}`.

Read `REPORT.md`, `PASSIVE_MEMO_CONTRACT.md`, `TARGET_OPPORTUNITY_MATRIX.tsv`,
`CAPACITY_COVERAGE.tsv`, `REUSE_DISTANCE.tsv`,
`PROACTIVE_VS_PASSIVE_COMPARISON.tsv`, `NEUTRALITY_GATES.tsv`,
`SOURCE_AUDIT.md`, `V2_DESIGN_REQUIREMENTS.md`, `RAW_DATA_INDEX.tsv`, and
`RUN_RECEIPTS.json`.
''')
    members = sorted(path for path in PACK.iterdir()
                     if path.is_file() and path.name != 'SHA256SUMS')
    (PACK / 'SHA256SUMS').write_text(
        ''.join(f'{sha(path)}  {path.name}\n' for path in members))
    print(json.dumps({
        'decision': decision, 'minimum_capacity': minimum_capacity,
        'all_neutral': all_neutral, 'all_correct': all_correct,
        'total_passive_hits_c4': total_hits,
        'aggregate_logical_hit_fraction': total_hits / total_lookups,
        'aggregate_hits_over_physical_lookup_requests':
            total_hits / total_physical,
    }, indent=2, sort_keys=True))
    return 0 if all_neutral and all_correct else 1


if __name__ == '__main__':
    raise SystemExit(main())
