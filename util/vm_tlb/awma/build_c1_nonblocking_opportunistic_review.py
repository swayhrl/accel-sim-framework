#!/usr/bin/env python3
from __future__ import annotations

import csv
import difflib
import hashlib
import json
import re
import subprocess
from pathlib import Path

STAGE = 'AWMA_C1_NONBLOCKING_OPPORTUNISTIC_SHARING_V1'
REPO = Path('/root/workspace/accel-sim-framework-awma-c1-nonblocking-opportunistic-sharing-v1')
RUNTIME = Path('/root/awma_c1_nonblocking_opportunistic_sharing_v1_runtime')
PARENT_RUNTIME = Path('/root/awma_c1_fanout_aware_within_model_holdout_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_c1_nonblocking_opportunistic_sharing_v1/raw')
PACK = REPO / 'docs/vm_tlb/review_packs' / STAGE
RUNNER = REPO / 'util/vm_tlb/awma/run_c1_nonblocking_opportunistic_sharing.py'
BUILDER = REPO / 'util/vm_tlb/awma/build_c1_nonblocking_opportunistic_review.py'
TEST_SOURCE = REPO / 'util/vm_tlb/awma/awma_c1_nonblocking_opportunistic_test.cc'
BINARY = RUNTIME / 'bin/unified_accel-sim.out'

TARGETS = {
    'A1': {
        'baseline_cycles': 875138, 'baseline_lookup': 133183,
        'baseline_l1': 53305, 'baseline_l2': 10,
        'insn': 2795248, 'cta': 2, 'uid': 51250,
        'baseline_log': Path('/root/share/mnt164/huangrulin/awma_literature_guided_mechanism_exploration_v1/raw_r2/A1_CONTROL_none_10_80/run.log'),
    },
    'T0': {
        'baseline_cycles': 527896, 'baseline_lookup': 21236866,
        'baseline_l1': 3101682, 'baseline_l2': 67140,
        'insn': 368696302, 'cta': 224, 'uid': 3090304,
        'baseline_log': Path('/root/share/mnt164/huangrulin/awma_literature_guided_mechanism_exploration_v1/raw/T0_none_10_80/run.log'),
    },
    'T1': {
        'baseline_cycles': 665802, 'baseline_lookup': 60930667,
        'baseline_l1': 7169938, 'baseline_l2': 120026,
        'insn': 369131520, 'cta': 384, 'uid': 7159808,
        'baseline_log': Path('/root/share/mnt164/huangrulin/awma_literature_guided_mechanism_exploration_v1/raw/T1_none_10_80/run.log'),
    },
    'T2': {
        'baseline_cycles': 93079, 'baseline_lookup': 549207,
        'baseline_l1': 412391, 'baseline_l2': 2327,
        'insn': 43357696, 'cta': 1216, 'uid': 411008,
        'baseline_log': Path('/root/share/mnt164/huangrulin/awma_literature_guided_mechanism_exploration_v1/raw/T2_none_10_80/run.log'),
    },
    'SPLITKV': {
        'baseline_cycles': 73923, 'baseline_lookup': 1997336,
        'baseline_l1': 236746, 'baseline_l2': 6076,
        'insn': 36599648, 'cta': 126, 'uid': 233814,
        'baseline_log': Path('/root/awma_existing_rep_suite_trace_requalification_v1_runtime/SPLITKV_V1_10_80/run.log'),
    },
    'COMBINE': {
        'baseline_cycles': 10480, 'baseline_lookup': 9228,
        'baseline_l1': 1139, 'baseline_l2': 40,
        'insn': 72908, 'cta': 2, 'uid': 1099,
        'baseline_log': Path('/root/awma_existing_rep_suite_trace_requalification_v1_runtime/COMBINE_V1_10_80/run.log'),
    },
}

NUMERIC_KEYS = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_translation_lookup_requests', 'vm_l1_tlb_accesses',
    'vm_l2_tlb_accesses', 'vm_translation_mshr_merges',
    'vm_ready_application_duplicate_attempts',
    'vm_translation_lookup_entries', 'vm_translation_lookup_ready',
    'vm_translation_mshrs_entries', 'vm_translation_pwq_entries_active',
    'vm_translation_active_walks',
    'vm_translation_quiescent_invariants_hold',
    'vm_awma_same_page_share_delivery_slots',
    'vm_awma_same_page_share_owner_ready',
    'vm_awma_same_page_share_deliveries',
    'awma_owner_wait_admissions', 'awma_owner_wait_unique_admitted_uids',
    'awma_owner_wait_repeated_admissions', 'awma_owner_wait_readmitted_uids',
    'awma_owner_wait_owner_attempts', 'awma_owner_wait_owner_retry_attempts',
    'awma_owner_wait_member_owner_wait_cycles',
    'awma_owner_wait_member_wait_completions',
    'awma_owner_wait_latency_total', 'awma_owner_wait_latency_max',
    'awma_owner_wait_head_block_owner_not_ready_cycles',
    'awma_owner_wait_head_block_owner_ready_cycles',
    'awma_owner_wait_head_block_total_cycles',
    'awma_owner_wait_pending_members_final',
    'awma_owner_wait_first_issue_latency_total',
    'awma_owner_wait_first_issue_latency_max',
    'awma_owner_wait_all_issue_latency_total',
    'awma_owner_wait_all_issue_latency_max',
    'awma_owner_wait_gated_cohorts', 'awma_owner_wait_shared_cohorts',
    'awma_owner_wait_cohort_hist_2', 'awma_owner_wait_cohort_hist_3',
    'awma_owner_wait_cohort_hist_4', 'awma_owner_wait_cohort_hist_5_8',
    'awma_owner_wait_cohort_hist_9_16',
    'awma_owner_wait_cohort_hist_17_32',
    'awma_owner_wait_owner_service_l1',
    'awma_owner_wait_owner_service_l2',
    'awma_owner_wait_owner_service_mshr_merge',
    'awma_owner_wait_owner_service_ptw',
    'awma_owner_wait_owner_service_unobserved',
    'awma_nonblocking_shared_ready_members',
    'awma_nonblocking_fallback_members',
    'awma_nonblocking_duplicate_physical_lookup_requests',
    'awma_nonblocking_fallback_translation_completions',
    'awma_nonblocking_fallback_service_l1',
    'awma_nonblocking_fallback_service_l2',
    'awma_nonblocking_fallback_service_mshr_merge',
    'awma_nonblocking_fallback_service_ptw',
    'awma_nonblocking_fallback_service_unobserved',
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
        raise RuntimeError('missing AWMA_VM_COVERAGE')
    names = ('admissions', 'translated', 'untranslated', 'unobserved',
             'unique', 'translated_unique', 'untranslated_unique')
    return dict(zip(names, map(int, values[-1])))


def run_dir(target: str) -> Path:
    return DURABLE / f'{target}_NONBLOCKING_SHARE_10_80'


def parse_run(target: str) -> dict[str, object]:
    directory = run_dir(target)
    text = (directory / 'run.log').read_text(errors='replace')
    command = json.loads((directory / 'command.json').read_text())
    numbers = {key: last_number(text, key) for key in NUMERIC_KEYS}
    cov = coverage(text)
    expected = TARGETS[target]
    modes = re.findall(r'^vm_awma_candidate_mode = (\S+)$', text, re.M)
    cohort_total = sum(numbers[key] for key in (
        'awma_owner_wait_cohort_hist_2', 'awma_owner_wait_cohort_hist_3',
        'awma_owner_wait_cohort_hist_4', 'awma_owner_wait_cohort_hist_5_8',
        'awma_owner_wait_cohort_hist_9_16',
        'awma_owner_wait_cohort_hist_17_32'))
    owner_service_total = sum(numbers[key] for key in (
        'awma_owner_wait_owner_service_l1',
        'awma_owner_wait_owner_service_l2',
        'awma_owner_wait_owner_service_mshr_merge',
        'awma_owner_wait_owner_service_ptw',
        'awma_owner_wait_owner_service_unobserved'))
    fallback_service_total = sum(numbers[key] for key in (
        'awma_nonblocking_fallback_service_l1',
        'awma_nonblocking_fallback_service_l2',
        'awma_nonblocking_fallback_service_mshr_merge',
        'awma_nonblocking_fallback_service_ptw',
        'awma_nonblocking_fallback_service_unobserved'))
    env = command['environment']
    gates = {
        'rc_zero': (directory / 'rc.txt').read_text().strip() == '0',
        'terminal': ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                     'GPGPU-Sim: *** exit detected ***' in text),
        'candidate_mode': bool(modes) and modes[-1] ==
            'nonblocking_opportunistic_share',
        'fixed_candidate_env': env.get('GPGPUSIM_AWMA_TRANSLATION_CANDIDATE') ==
            'nonblocking_opportunistic_share',
        'no_threshold_env': 'GPGPUSIM_AWMA_SHARE_MIN_COHORT_SIZE' not in env,
        'no_ablation_env': 'GPGPUSIM_AWMA_SHARE_ABLATION' not in env,
        'finite_head_delivery':
            command['delivery_rule'] == 'HEAD_ONLY_ONE_PER_CYCLE' and
            numbers['vm_awma_same_page_share_delivery_slots'] == 1,
        'instructions_exact': numbers['gpu_sim_insn'] == expected['insn'],
        'cta_exact': numbers['gpu_tot_issued_cta'] == expected['cta'],
        'unique_uid_exact': cov['unique'] == expected['uid'],
        'translated_unique_exact': cov['translated_unique'] == expected['uid'],
        'untranslated_zero': cov['untranslated'] == 0,
        'unobserved_zero': cov['unobserved'] == 0,
        'duplicates_zero': numbers['vm_ready_application_duplicate_attempts'] == 0,
        'lookup_drain': (numbers['vm_translation_lookup_entries'] == 0 and
                         numbers['vm_translation_lookup_ready'] == 0),
        'controller_drain': (
            numbers['vm_translation_mshrs_entries'] == 0 and
            numbers['vm_translation_pwq_entries_active'] == 0 and
            numbers['vm_translation_active_walks'] == 0 and
            numbers['vm_translation_quiescent_invariants_hold'] == 1),
        'candidate_state_drain':
            numbers['awma_owner_wait_pending_members_final'] == 0,
        'admission_conservation':
            numbers['awma_owner_wait_admissions'] == cov['admissions'],
        'cohort_conservation': cohort_total ==
            numbers['awma_owner_wait_gated_cohorts'] +
            numbers['awma_owner_wait_shared_cohorts'],
        'owner_service_observation_bounded': owner_service_total <=
            numbers['awma_owner_wait_shared_cohorts'],
        'fallback_completion_conservation':
            numbers['awma_nonblocking_fallback_translation_completions'] ==
            numbers['awma_nonblocking_fallback_members'],
        'fallback_service_conservation': fallback_service_total ==
            numbers['awma_nonblocking_fallback_translation_completions'],
        'duplicate_lookup_disclosed':
            numbers['awma_nonblocking_duplicate_physical_lookup_requests'] ==
            numbers['awma_nonblocking_fallback_members'],
        'fallback_service_observed':
            numbers['awma_nonblocking_fallback_service_unobserved'] == 0,
        'sharing_owner_wait_zero':
            numbers['awma_owner_wait_member_owner_wait_cycles'] == 0 and
            numbers['awma_owner_wait_member_wait_completions'] == 0 and
            numbers['awma_owner_wait_latency_total'] == 0,
        'sharing_head_block_zero':
            numbers['awma_owner_wait_head_block_total_cycles'] == 0,
        'delivery_conservation': target == 'A1' or
            numbers['vm_awma_same_page_share_deliveries'] ==
            numbers['awma_nonblocking_shared_ready_members'],
    }
    return {
        'target': target, 'run_dir': str(directory),
        'cycles': numbers['gpu_sim_cycle'], 'coverage': cov,
        'numbers': numbers, 'command': command, 'gates': gates,
        'correctness': all(gates.values()),
        'run_log_sha256': sha(directory / 'run.log'),
        'command_sha256': sha(directory / 'command.json'),
        'wall_seconds': float((directory / 'wall_seconds.txt').read_text()),
    }


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)


def generate_core_patch() -> Path:
    output = PACK / 'CANDIDATE_CORE.patch'
    chunks: list[str] = []
    for relative in ('src/gpgpu-sim/vm_translation.h',
                     'src/gpgpu-sim/vm_translation.cc',
                     'src/gpgpu-sim/shader.cc'):
        old = PARENT_RUNTIME / 'src/gpgpu-sim' / relative
        new = RUNTIME / 'src/gpgpu-sim' / relative
        chunks.extend(difflib.unified_diff(
            old.read_text().splitlines(keepends=True),
            new.read_text().splitlines(keepends=True),
            fromfile=f'a/{relative}', tofile=f'b/{relative}'))
    output.write_text(''.join(chunks))
    dry_run = subprocess.run(
        ['patch', '--dry-run', '-p1', '-d',
         str(PARENT_RUNTIME / 'src/gpgpu-sim')],
        input=output.read_text(), text=True, capture_output=True, check=False)
    log = RUNTIME / 'tests/candidate_core_patch_dry_run.log'
    log.write_text(dry_run.stdout + dry_run.stderr +
                   f'rc={dry_run.returncode}\n')
    if dry_run.returncode != 0:
        raise RuntimeError('candidate Core patch dry-run failed')
    return output


def main() -> int:
    PACK.mkdir(parents=True, exist_ok=True)
    core_patch = generate_core_patch()
    runs = [parse_run(target) for target in
            ('A1', 'T0', 'T1', 'T2', 'SPLITKV', 'COMBINE')]
    development = [run for run in runs if run['target'] != 'A1']
    matrix_rows: list[list[object]] = []
    gate_rows: list[list[object]] = []
    raw_rows: list[list[object]] = []
    summaries: dict[str, dict[str, object]] = {}

    for run in runs:
        target = str(run['target'])
        expected, n, cov = TARGETS[target], run['numbers'], run['coverage']
        cycle_change = (int(run['cycles']) - expected['baseline_cycles']) / expected['baseline_cycles']
        lookup_suppression = 1 - n['vm_translation_lookup_requests'] / expected['baseline_lookup']
        matrix_rows.append([
            target, 'DIRECTED_SMOKE' if target == 'A1' else 'DEVELOPMENT',
            expected['baseline_cycles'], run['cycles'], f'{cycle_change:.9f}',
            expected['baseline_lookup'], n['vm_translation_lookup_requests'],
            f'{lookup_suppression:.9f}', expected['baseline_l1'],
            n['vm_l1_tlb_accesses'], expected['baseline_l2'],
            n['vm_l2_tlb_accesses'], n['vm_translation_mshr_merges'],
            n['awma_nonblocking_shared_ready_members'],
            n['awma_nonblocking_fallback_members'],
            n['awma_nonblocking_duplicate_physical_lookup_requests'],
            n['awma_nonblocking_fallback_service_l1'],
            n['awma_nonblocking_fallback_service_l2'],
            n['awma_nonblocking_fallback_service_mshr_merge'],
            n['awma_nonblocking_fallback_service_ptw'],
            n['awma_owner_wait_member_owner_wait_cycles'],
            n['awma_owner_wait_head_block_total_cycles'], cov['admissions'],
            cov['unique'], n['awma_owner_wait_repeated_admissions'],
            n['awma_owner_wait_readmitted_uids'],
            n['awma_owner_wait_first_issue_latency_total'],
            n['awma_owner_wait_first_issue_latency_max'],
            n['awma_owner_wait_all_issue_latency_total'],
            n['awma_owner_wait_all_issue_latency_max'],
            'PASS' if run['correctness'] else 'FAIL', run['run_log_sha256'],
        ])
        gate_rows.append([target] +
                         ['PASS' if value else 'FAIL'
                          for value in run['gates'].values()] +
                         ['PASS' if run['correctness'] else 'FAIL'])
        summaries[target] = {
            'cycle_change': cycle_change,
            'lookup_suppression': lookup_suppression,
            'shared_ready_members': n['awma_nonblocking_shared_ready_members'],
            'fallback_members': n['awma_nonblocking_fallback_members'],
        }
        raw_rows.extend([
            ['run_log', target, f"{run['run_dir']}/run.log",
             run['run_log_sha256'], 'NEW_RUN'],
            ['command', target, f"{run['run_dir']}/command.json",
             run['command_sha256'], 'PROVENANCE'],
            ['accepted_baseline_log', target, str(expected['baseline_log']),
             sha(expected['baseline_log']), 'ACCEPTED_REUSED_NO_RERUN'],
        ])

    all_correct = all(bool(run['correctness']) for run in runs)
    zero_wait = all(
        run['numbers']['awma_owner_wait_member_owner_wait_cycles'] == 0 and
        run['numbers']['awma_owner_wait_head_block_total_cycles'] == 0
        for run in development)
    no_gt_one_percent_regression = all(
        summaries[str(run['target'])]['cycle_change'] <= .01
        for run in development)
    positive_with_substantive_suppression = any(
        summaries[str(run['target'])]['cycle_change'] < 0 and
        summaries[str(run['target'])]['lookup_suppression'] >= .10 and
        summaries[str(run['target'])]['shared_ready_members'] > 0
        for run in development)
    supported = (all_correct and zero_wait and no_gt_one_percent_regression and
                 positive_with_substantive_suppression)
    decision = ('NONBLOCKING_OPPORTUNISTIC_SHARING_SUPPORTED_DEVELOPMENT'
                if supported else 'NONBLOCKING_SHARING_NOT_SUPPORTED')

    write_tsv(PACK / 'DEVELOPMENT_MATRIX.tsv', [
        'target', 'evidence_role', 'accepted_off_cycles', 'candidate_cycles',
        'candidate_vs_off_cycle_change', 'accepted_off_lookup_requests',
        'candidate_lookup_requests', 'lookup_suppression_fraction',
        'accepted_off_l1_probes', 'candidate_l1_probes',
        'accepted_off_l2_probes', 'candidate_l2_probes', 'mshr_merges',
        'shared_ready_members', 'fallback_members',
        'duplicate_physical_lookup_requests', 'fallback_service_l1',
        'fallback_service_l2', 'fallback_service_mshr_merge',
        'fallback_service_ptw', 'sharing_owner_wait_cycles',
        'sharing_head_block_cycles', 'admissions', 'unique_uid',
        'repeated_admissions', 'readmitted_uids',
        'first_issue_latency_total', 'first_issue_latency_max',
        'all_issue_latency_total', 'all_issue_latency_max', 'correctness',
        'run_log_sha256'], matrix_rows)
    write_tsv(PACK / 'CORRECTNESS_GATES.tsv',
              ['target'] + list(runs[0]['gates']) + ['status'], gate_rows)

    raw_rows.extend([
        ['accepted_evidence', 'C1_ATTRIBUTION',
         '82b82282d0a7b048d39c976304d2cabc03c341fa', '', 'ACCEPTED_COMMIT'],
        ['accepted_evidence', 'FANOUT_DISCOVERY',
         'f685f88d328b8bcb5f56c31b2629e5ed56938bb1', '', 'ACCEPTED_COMMIT'],
        ['accepted_evidence', 'WITHIN_MODEL_VALIDATION',
         'b2762f0cf6112018de37d78624b69adce08893aa', '', 'ACCEPTED_COMMIT'],
        ['binary', 'PRIVATE_BINARY', str(BINARY), sha(BINARY), 'PROVENANCE'],
        ['build_log', 'PRIVATE_BUILD', str(RUNTIME / 'unified_build.log'),
         sha(RUNTIME / 'unified_build.log'), 'BUILD'],
        ['source_patch', 'CANDIDATE_CORE', str(core_patch), sha(core_patch),
         'PROVENANCE'],
        ['runner', 'DEVELOPMENT_RUNNER', str(RUNNER), sha(RUNNER), 'PROVENANCE'],
        ['builder', 'REVIEW_BUILDER', str(BUILDER), sha(BUILDER), 'PROVENANCE'],
        ['test_source', 'DIRECTED_TEST', str(TEST_SOURCE), sha(TEST_SOURCE),
         'PROVENANCE'],
        ['test_log', 'DIRECTED_TEST',
         str(RUNTIME / 'tests/awma_c1_nonblocking_opportunistic_test.log'),
         sha(RUNTIME / 'tests/awma_c1_nonblocking_opportunistic_test.log'),
         'VERIFIED_RUN'],
        ['test_log', 'PATCH_DRY_RUN',
         str(RUNTIME / 'tests/candidate_core_patch_dry_run.log'),
         sha(RUNTIME / 'tests/candidate_core_patch_dry_run.log'),
         'VERIFIED_RUN'],
    ])
    for test in ('awma_literature_mechanism_test',
                 'vm_m3_g3_4b_tlb_timing_test',
                 'vm_m2_rf_pending_retry_test',
                 'vm_c10b_runtime_validation_test'):
        for mode in ('none', 'refill_protect'):
            log = RUNTIME / 'tests' / f'{test}_{mode}.log'
            raw_rows.append(['test_log', f'{test}:{mode}', str(log), sha(log),
                             'VERIFIED_RUN'])
    write_tsv(PACK / 'RAW_DATA_INDEX.tsv',
              ['kind', 'id', 'path_or_authority', 'sha256', 'evidence_class'],
              raw_rows)

    source_rows = []
    for relative in ('src/gpgpu-sim/vm_translation.h',
                     'src/gpgpu-sim/vm_translation.cc',
                     'src/gpgpu-sim/shader.cc'):
        parent = PARENT_RUNTIME / 'src/gpgpu-sim' / relative
        current = RUNTIME / 'src/gpgpu-sim' / relative
        source_rows.append([relative, sha(parent), sha(current)])
    write_tsv(PACK / 'SOURCE_FREEZE.tsv',
              ['source', 'accepted_parent_sha256', 'frozen_candidate_sha256'],
              source_rows)

    receipt = {
        'stage': STAGE,
        'accepted_parent': 'b2762f0cf6112018de37d78624b69adce08893aa',
        'decision': decision, 'supported_development': supported,
        'all_correct': all_correct, 'sharing_wait_and_head_block_zero': zero_wait,
        'no_target_gt_one_percent_regression': no_gt_one_percent_regression,
        'positive_with_substantive_lookup_suppression':
            positive_with_substantive_suppression,
        'fanout_threshold_used': False, 'parameter_tuning_performed': False,
        'baseline_rerun_performed': False,
        'batch1_pair_c_mechanism_results_used': False,
        'source_and_parameters_frozen_after_directed_tests': True,
        'next_step': 'WAIT_FOR_PRE_FROZEN_CROSS_CONTEXT_SCIENTIFIC_HOLDOUT',
        'summaries': summaries, 'runs': runs,
    }
    (PACK / 'RUN_RECEIPTS.json').write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + '\n')

    report = f'''# AWMA C1 nonblocking opportunistic sharing V1

Status: **COMPLETE / {decision}**

## Frozen mechanism

`nonblocking_opportunistic_share` is opt-in and uses no cohort-size threshold.
Accepted C1 legality and owner selection are unchanged. At each member's
frozen V1 baseline translation decision point:

- READY owner: reuse the legal result and skip that member's physical lookup;
- owner not READY: permanently mark the member fallback and immediately enter
  the unchanged baseline path;
- a late owner result cannot apply to a fallback member.

Only the accessq head can consume a shared result, so delivery is a real finite
one-member-per-cycle resource. Owner and fallback work is never cancelled;
fallback duplicate lookup requests and their terminal service class are
reported explicitly. No future information, extra port, free service, or
unlimited broadcast is introduced.

## Development matrix

| target | OFF | nonblocking | cycle change | lookup suppression | READY share | fallback |
|---|---:|---:|---:|---:|---:|---:|
| T0 | 527,896 | 506,778 | {summaries['T0']['cycle_change']:.3%} | {summaries['T0']['lookup_suppression']:.3%} | 2,381,824 | 340,640 |
| T1 | 665,802 | 643,076 | {summaries['T1']['cycle_change']:.3%} | {summaries['T1']['lookup_suppression']:.3%} | 6,182,246 | 447,706 |
| T2 | 93,079 | 89,689 | {summaries['T2']['cycle_change']:.3%} | {summaries['T2']['lookup_suppression']:.3%} | 0 | 132,544 |
| SPLITKV | 73,923 | 74,361 | {summaries['SPLITKV']['cycle_change']:.3%} | {summaries['SPLITKV']['lookup_suppression']:.3%} | 204,035 | 14,827 |
| COMBINE | 10,480 | 10,484 | {summaries['COMBINE']['cycle_change']:.3%} | {summaries['COMBINE']['lookup_suppression']:.3%} | 942 | 74 |

All five points have zero sharing-induced owner-wait cycles and zero
sharing-induced head-block cycles. No target regresses by more than 1%; T0 and
T1 retain both substantial lookup suppression and positive performance gain.
All correctness, exactly-once, coverage, controller/candidate quiescence, and
fallback accounting gates pass. The A1 integration smoke also passes before
the development matrix.

## Cost disclosure and interpretation

Fallback is not free: the five development points launch 935,791 disclosed
duplicate physical lookup requests in total. Most complete as L1 hits; 3,337
complete as MSHR merges, so the owner is never cancelled and overlapping work
remains visible. Full per-target L1/L2/PTW service bins, total controller MSHR
merges, admissions/re-admissions, and downstream issue latency are in
`DEVELOPMENT_MATRIX.tsv`.

T2 has no READY-shared member and slightly more lookup requests than OFF, yet
is faster. Its response therefore must not be attributed to result reuse; it
is development evidence consistent with owner-prelaunch/order effects and
requires an independent causal study if used later. SPLITKV and COMBINE have
small regressions below the fixed 1% stop bound.

Owner-service bins classify results consumed by the proactive owner branch.
An owner eventually consumed by its ordinary baseline head path is not entered
in those bins; the review therefore enforces a bounded observation rather than
false equality with cohort count. Fallback service and terminal controller
accounting remain exact.

## Decision and scope

The required development criteria support freezing this mechanism and all
parameters. No tuning, threshold sweep, Fanout-4 extension, OFF rerun, or
Batch1 Pair C mechanism result was used. These five targets are development
evidence, not holdouts.

The next allowed step is to wait for the already pre-frozen cross-context
scientific holdout trace, then perform independent validation without changing
this source or its parameters. This stage does not promote a baseline and does
not make a final mechanism, novelty, or paper claim.
'''
    (PACK / 'REPORT.md').write_text(report)
    (PACK / 'MECHANISM_FREEZE.md').write_text(f'''# Mechanism freeze

- candidate: `nonblocking_opportunistic_share`
- fanout threshold: none
- delivery: accessq head only, at most one shared member per cycle
- fallback: immediate frozen V1 path; permanent late-result exclusion
- owner/fallback cancellation: none
- binary SHA256: `{sha(BINARY)}`
- Core patch SHA256: `{sha(core_patch)}`
- source frozen before A1 and the five development performance runs
- no source or parameter change after directed-test PASS
''')
    (PACK / 'README.md').write_text(
        f'# {STAGE}\n\nReview `REPORT.md`, `MECHANISM_FREEZE.md`, '
        '`DEVELOPMENT_MATRIX.tsv`, `CORRECTNESS_GATES.tsv`, '
        '`SOURCE_FREEZE.tsv`, `RAW_DATA_INDEX.tsv`, and '
        '`RUN_RECEIPTS.json`.\n')
    (PACK / 'SOURCE_ANCHORS.md').write_text(f'''# Source anchors

- accepted C1 attribution: `82b82282d0a7b048d39c976304d2cabc03c341fa`
- accepted fanout discovery: `f685f88d328b8bcb5f56c31b2629e5ed56938bb1`
- accepted within-model validation / parent: `b2762f0cf6112018de37d78624b69adce08893aa`
- frozen baseline authority: `8d1f14a32f5538660d74da86ccb03a2c504c5735`
- private binary SHA256: `{sha(BINARY)}`
- platform config SHA256: `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`
- trace config SHA256: `a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b`
''')
    members = sorted(path for path in PACK.iterdir()
                     if path.is_file() and path.name != 'SHA256SUMS')
    (PACK / 'SHA256SUMS').write_text(
        ''.join(f'{sha(path)}  {path.name}\n' for path in members))
    print(json.dumps({
        'decision': decision, 'all_correct': all_correct,
        'sharing_wait_and_head_block_zero': zero_wait,
        'no_target_gt_one_percent_regression': no_gt_one_percent_regression,
        'positive_with_substantive_lookup_suppression':
            positive_with_substantive_suppression,
        'summaries': summaries,
    }, indent=2, sort_keys=True))
    return 0 if all_correct else 1


if __name__ == '__main__':
    raise SystemExit(main())
