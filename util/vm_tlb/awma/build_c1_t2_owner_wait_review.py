#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

REPO = Path('/root/workspace/accel-sim-framework-awma-c1-t2-owner-wait-retry-attribution-v1')
RUNTIME = Path('/root/awma_c1_t2_owner_wait_retry_attribution_v1_runtime')
ABLATION_RUNTIME = Path('/root/awma_c1_t2_owner_wait_retry_attribution_v1_ablation_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_c1_t2_owner_wait_retry_attribution_v1/raw')
PACK = REPO / 'docs/vm_tlb/review_packs/AWMA_C1_T2_OWNER_WAIT_RETRY_ATTRIBUTION_V1'
RUNNER = REPO / 'util/vm_tlb/awma/run_c1_t2_owner_wait_attribution.py'
TEST_SOURCE = REPO / 'util/vm_tlb/awma/awma_c1_owner_wait_attribution_test.cc'

EXPECTED = {
    'A1': (2795248, 2, 51250),
    'T0': (368696302, 224, 3090304),
    'T2': (43357696, 1216, 411008),
}
RUNS = (
    ('A1', 'C1', 863057, 51250, True),
    ('T0', 'OFF', 527896, 3090304, True),
    ('T0', 'C1', 487624, 3090304, True),
    ('T2', 'OFF', 93079, 715333, True),
    ('T2', 'C1', 94034, 832383, True),
    ('A1', 'C1_READY_ONLY_NO_WAIT', None, None, False),
    ('T2', 'C1_READY_ONLY_NO_WAIT', None, None, False),
)
NUMERIC_KEYS = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_translation_lookup_requests', 'vm_l1_tlb_accesses',
    'vm_l2_tlb_accesses', 'vm_ready_application_duplicate_attempts',
    'vm_translation_lookup_entries', 'vm_translation_lookup_ready',
    'vm_translation_mshrs_entries', 'vm_translation_pwq_entries_active',
    'vm_translation_active_walks',
    'vm_translation_quiescent_invariants_hold',
    'vm_awma_same_page_share_owner_ready',
    'vm_awma_same_page_share_deliveries',
    'awma_owner_wait_admissions', 'awma_owner_wait_unique_admitted_uids',
    'awma_owner_wait_repeated_admissions', 'awma_owner_wait_readmitted_uids',
    'awma_owner_wait_admission_count_max',
    'awma_owner_wait_owner_attempts',
    'awma_owner_wait_owner_retry_attempts',
    'awma_owner_wait_retried_owner_uids',
    'awma_owner_wait_owner_attempt_max',
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
    'awma_owner_wait_cohort_size_max',
    'awma_owner_wait_cohort_hist_2', 'awma_owner_wait_cohort_hist_3',
    'awma_owner_wait_cohort_hist_4', 'awma_owner_wait_cohort_hist_5_8',
    'awma_owner_wait_cohort_hist_9_16',
    'awma_owner_wait_cohort_hist_17_32',
    'awma_owner_wait_owner_service_l1',
    'awma_owner_wait_owner_service_l2',
    'awma_owner_wait_owner_service_mshr_merge',
    'awma_owner_wait_owner_service_ptw',
    'awma_owner_wait_owner_service_unobserved',
)
OPTIONAL_CONTROL_KEYS = (
    'awma_owner_wait_no_wait_fallback_members',
    'awma_owner_wait_no_wait_fallback_wait_completions',
    'awma_owner_wait_no_wait_fallback_wait_latency_total',
    'awma_owner_wait_no_wait_fallback_wait_latency_max',
)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def last_number(text: str, key: str, default: int | None = None) -> int:
    values = re.findall(rf'^{re.escape(key)} = (\d+)$', text, re.M)
    if not values:
        if default is not None:
            return default
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


def run_name(target: str, semantic: str) -> str:
    return f'{target}_{semantic}_OWNER_WAIT_TELEM_10_80'


def parse_run(target: str, semantic: str, expected_cycles: int | None,
              expected_admissions: int | None,
              neutrality_required: bool) -> dict[str, object]:
    directory = DURABLE / run_name(target, semantic)
    text = (directory / 'run.log').read_text(errors='replace')
    command = json.loads((directory / 'command.json').read_text())
    numbers = {key: last_number(text, key) for key in NUMERIC_KEYS}
    numbers.update({key: last_number(text, key, 0)
                    for key in OPTIONAL_CONTROL_KEYS})
    cov = coverage(text)
    expected_insn, expected_cta, expected_uid = EXPECTED[target]
    modes = re.findall(r'^vm_awma_candidate_mode = (\S+)$', text, re.M)
    service_sum = sum(numbers[key] for key in (
        'awma_owner_wait_owner_service_l1',
        'awma_owner_wait_owner_service_l2',
        'awma_owner_wait_owner_service_mshr_merge',
        'awma_owner_wait_owner_service_ptw',
        'awma_owner_wait_owner_service_unobserved'))
    targeted_cohorts = sum(numbers[key] for key in (
        'awma_owner_wait_cohort_hist_2', 'awma_owner_wait_cohort_hist_3',
        'awma_owner_wait_cohort_hist_4', 'awma_owner_wait_cohort_hist_5_8',
        'awma_owner_wait_cohort_hist_9_16',
        'awma_owner_wait_cohort_hist_17_32'))
    expected_service_completions = (
        targeted_cohorts if target == 'A1'
        else numbers['vm_awma_same_page_share_owner_ready'])
    c1 = semantic != 'OFF'
    gates = {
        'rc': (directory / 'rc.txt').read_text().strip() == '0',
        'terminal': ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                     'GPGPU-Sim: *** exit detected ***' in text),
        'candidate_mode': bool(modes) and modes[-1] ==
            ('same_page_share' if c1 else 'none'),
        'instructions': numbers['gpu_sim_insn'] == expected_insn,
        'cta': numbers['gpu_tot_issued_cta'] == expected_cta,
        'unique_uid': cov['unique'] == expected_uid,
        'translated_unique': cov['translated_unique'] == expected_uid,
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
        'diagnostic_drain':
            numbers['awma_owner_wait_pending_members_final'] == 0,
        'owner_service_conservation':
            service_sum == expected_service_completions,
        'admission_conservation': numbers['awma_owner_wait_admissions'] ==
            cov['admissions'],
        'neutrality': (not neutrality_required or
                       (numbers['gpu_sim_cycle'] == expected_cycles and
                        cov['admissions'] == expected_admissions)),
    }
    return {
        'target': target, 'semantic': semantic, 'run_dir': str(directory),
        'cycles': numbers['gpu_sim_cycle'], 'coverage': cov,
        'numbers': numbers, 'gates': gates,
        'correctness': all(gates.values()),
        'run_log_sha256': sha(directory / 'run.log'),
        'command_sha256': sha(directory / 'command.json'),
        'command': command,
        'wall_seconds': float((directory / 'wall_seconds.txt').read_text()),
    }


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)


def main() -> int:
    PACK.mkdir(parents=True, exist_ok=True)
    runs = [parse_run(*spec) for spec in RUNS]
    by_key = {(str(run['target']), str(run['semantic'])): run for run in runs}
    rows = []
    gate_rows = []
    raw_rows = []
    for run in runs:
        n = run['numbers']
        c = run['coverage']
        unique = c['unique']
        rows.append([
            run['target'], run['semantic'], run['cycles'], c['admissions'],
            unique, n['awma_owner_wait_repeated_admissions'],
            n['awma_owner_wait_readmitted_uids'],
            f"{n['awma_owner_wait_repeated_admissions'] / unique:.9f}",
            n['awma_owner_wait_admission_count_max'],
            n['vm_translation_lookup_requests'], n['vm_l1_tlb_accesses'],
            n['vm_l2_tlb_accesses'], n['awma_owner_wait_owner_attempts'],
            n['awma_owner_wait_owner_retry_attempts'],
            n['awma_owner_wait_member_owner_wait_cycles'],
            n['awma_owner_wait_member_wait_completions'],
            n['awma_owner_wait_no_wait_fallback_members'],
            n['awma_owner_wait_no_wait_fallback_wait_completions'],
            n['awma_owner_wait_head_block_owner_not_ready_cycles'],
            n['awma_owner_wait_head_block_owner_ready_cycles'],
            n['awma_owner_wait_head_block_total_cycles'],
            f"{n['awma_owner_wait_head_block_total_cycles'] / unique:.9f}",
            n['awma_owner_wait_latency_total'],
            n['awma_owner_wait_latency_max'],
            n['awma_owner_wait_first_issue_latency_total'],
            f"{n['awma_owner_wait_first_issue_latency_total'] / unique:.9f}",
            n['awma_owner_wait_all_issue_latency_total'],
            n['awma_owner_wait_all_issue_latency_max'],
            n['awma_owner_wait_cohort_size_max'],
            n['awma_owner_wait_cohort_hist_2'],
            n['awma_owner_wait_cohort_hist_3'],
            n['awma_owner_wait_cohort_hist_4'],
            n['awma_owner_wait_cohort_hist_5_8'],
            n['awma_owner_wait_cohort_hist_9_16'],
            n['awma_owner_wait_cohort_hist_17_32'],
            n['awma_owner_wait_owner_service_l1'],
            n['awma_owner_wait_owner_service_l2'],
            n['awma_owner_wait_owner_service_mshr_merge'],
            n['awma_owner_wait_owner_service_ptw'],
            n['awma_owner_wait_owner_service_unobserved'],
            'PASS' if run['correctness'] else 'FAIL', run['run_log_sha256'],
        ])
        gate_rows.append([run['target'], run['semantic']] +
                         ['PASS' if value else 'FAIL'
                          for value in run['gates'].values()] +
                         ['PASS' if run['correctness'] else 'FAIL'])
        raw_rows.extend([
            ['run_log', f"{run['target']}:{run['semantic']}",
             f"{run['run_dir']}/run.log", run['run_log_sha256'],
             'P1_DIAGNOSTIC'],
            ['command', f"{run['target']}:{run['semantic']}",
             f"{run['run_dir']}/command.json", run['command_sha256'],
             'P3_PROVENANCE'],
        ])

    t0_c1 = by_key[('T0', 'C1')]
    t2_off = by_key[('T2', 'OFF')]
    t2_c1 = by_key[('T2', 'C1')]
    t2_control = by_key[('T2', 'C1_READY_ONLY_NO_WAIT')]
    t0_head_per_uid = (t0_c1['numbers']['awma_owner_wait_head_block_total_cycles'] /
                       t0_c1['coverage']['unique'])
    t2_head_per_uid = (t2_c1['numbers']['awma_owner_wait_head_block_total_cycles'] /
                       t2_c1['coverage']['unique'])
    owner_total = t2_c1['numbers']['vm_awma_same_page_share_owner_ready']
    l1_fraction = (t2_c1['numbers']['awma_owner_wait_owner_service_l1'] /
                   owner_total)
    telemetry_supports = (
        t2_c1['numbers']['awma_owner_wait_repeated_admissions'] >
        t2_off['numbers']['awma_owner_wait_repeated_admissions'] and
        t2_c1['numbers']['awma_owner_wait_readmitted_uids'] >
        t2_off['numbers']['awma_owner_wait_readmitted_uids'] and
        t2_head_per_uid > t0_head_per_uid and
        t2_c1['numbers']['awma_owner_wait_cohort_hist_2'] == owner_total and
        l1_fraction > .9)
    control_supports = (
        t2_control['cycles'] < t2_c1['cycles'] and
        t2_control['numbers']['awma_owner_wait_head_block_total_cycles'] <
            t2_c1['numbers']['awma_owner_wait_head_block_total_cycles'] / 2 and
        t2_control['numbers']['awma_owner_wait_no_wait_fallback_members'] > 0)
    decision = (
        'SUPPORTS_OWNER_WAIT_HEAD_BLOCKING_AS_MAJOR_T2_REGRESSION_CAUSE'
        if telemetry_supports and control_supports else
        'DOES_NOT_SUPPORT_OWNER_WAIT_HEAD_BLOCKING_AS_MAJOR_T2_CAUSE')

    write_tsv(PACK / 'ATTRIBUTION_MATRIX.tsv', [
        'target', 'semantic', 'cycles', 'admissions', 'unique_uid',
        'repeated_admissions', 'readmitted_uids',
        'repeated_admissions_per_uid', 'admission_count_max',
        'lookup_requests', 'l1_probes', 'l2_probes', 'owner_attempts',
        'owner_retry_attempts', 'member_owner_wait_cycles',
        'member_wait_completions', 'no_wait_fallback_members',
        'no_wait_fallback_wait_completions',
        'head_block_owner_not_ready_cycles',
        'head_block_owner_ready_cycles', 'head_block_total_cycles',
        'head_block_cycles_per_uid', 'owner_member_wait_latency_total',
        'owner_member_wait_latency_max', 'first_issue_latency_total',
        'first_issue_latency_per_uid', 'all_issue_latency_total',
        'all_issue_latency_max', 'cohort_size_max', 'cohort_size_2',
        'cohort_size_3', 'cohort_size_4', 'cohort_size_5_8',
        'cohort_size_9_16', 'cohort_size_17_32', 'owner_service_l1',
        'owner_service_l2', 'owner_service_mshr_merge', 'owner_service_ptw',
        'owner_service_unobserved', 'correctness', 'run_log_sha256'], rows)
    gate_names = list(runs[0]['gates'])
    write_tsv(PACK / 'CORRECTNESS_GATES.tsv',
              ['target', 'semantic'] + gate_names + ['status'], gate_rows)

    core_patch = PACK / 'CANDIDATE_CORE.patch'
    raw_rows.extend([
        ['parent_evidence', 'PHASE2_MATRIX',
         str(REPO / 'docs/vm_tlb/review_packs/AWMA_C1_DELIVERY_BANDWIDTH_DIAGNOSTIC_V1/DIAGNOSTIC_MATRIX.tsv'),
         sha(REPO / 'docs/vm_tlb/review_packs/AWMA_C1_DELIVERY_BANDWIDTH_DIAGNOSTIC_V1/DIAGNOSTIC_MATRIX.tsv'),
         'P1_ACCEPTED_PARENT'],
        ['build_log', 'TELEMETRY_BUILD', str(RUNTIME / 'unified_build.log'),
         sha(RUNTIME / 'unified_build.log'), 'P4_RUNTIME'],
        ['binary', 'TELEMETRY_BINARY', str(RUNTIME / 'bin/unified_accel-sim.out'),
         sha(RUNTIME / 'bin/unified_accel-sim.out'), 'P3_PROVENANCE'],
        ['build_log', 'ABLATION_BUILD',
         str(ABLATION_RUNTIME / 'unified_build.log'),
         sha(ABLATION_RUNTIME / 'unified_build.log'), 'P4_RUNTIME'],
        ['binary', 'ABLATION_BINARY',
         str(ABLATION_RUNTIME / 'bin/unified_accel-sim.out'),
         sha(ABLATION_RUNTIME / 'bin/unified_accel-sim.out'), 'P3_PROVENANCE'],
        ['source_patch', 'FINAL_CORE_PATCH', str(core_patch), sha(core_patch),
         'P3_PROVENANCE'],
        ['test_source', 'DIRECTED_TEST', str(TEST_SOURCE), sha(TEST_SOURCE),
         'P3_PROVENANCE'],
        ['runner', 'ATTRIBUTION_RUNNER', str(RUNNER), sha(RUNNER),
         'P3_PROVENANCE'],
        ['builder', 'REVIEW_BUILDER', str(Path(__file__)), sha(Path(__file__)),
         'P3_PROVENANCE'],
        ['test_log', 'CORE_PATCH_DRY_RUN',
         str(ABLATION_RUNTIME / 'tests/candidate_core_patch_dry_run.log'),
         sha(ABLATION_RUNTIME / 'tests/candidate_core_patch_dry_run.log'),
         'VERIFIED_RUN'],
    ])
    for test in (
            'awma_literature_mechanism_test',
            'vm_m3_g3_4b_tlb_timing_test',
            'vm_m2_rf_pending_retry_test',
            'vm_c10b_runtime_validation_test'):
        for mode in ('none', 'refill_protect'):
            log = ABLATION_RUNTIME / 'tests' / f'{test}_{mode}.log'
            raw_rows.append(['test_log', f'{test}:{mode}', str(log), sha(log),
                             'VERIFIED_RUN'])
    write_tsv(PACK / 'RAW_DATA_INDEX.tsv',
              ['kind', 'id', 'path', 'sha256', 'evidence_class'], raw_rows)

    receipt = {
        'stage': 'AWMA_C1_T2_OWNER_WAIT_RETRY_ATTRIBUTION_V1',
        'accepted_parent': '070cb2f8b1ffea431f0f8acb9ca32a0dd16a0f14',
        'decision': decision,
        'telemetry_supports_owner_wait': telemetry_supports,
        'ready_only_control_supports_causality': control_supports,
        'all_correct': all(bool(run['correctness']) for run in runs),
        'observational_neutrality_pass': all(
            bool(run['gates']['neutrality']) for run in runs[:5]),
        't0_head_block_cycles_per_uid': t0_head_per_uid,
        't2_head_block_cycles_per_uid': t2_head_per_uid,
        't2_owner_l1_fraction': l1_fraction,
        't2_control_cycle_change_vs_c1':
            (t2_control['cycles'] - t2_c1['cycles']) / t2_c1['cycles'],
        't2_control_cycle_change_vs_off':
            (t2_control['cycles'] - t2_off['cycles']) / t2_off['cycles'],
        't2_lookup_requests': {
            'off': t2_off['numbers']['vm_translation_lookup_requests'],
            'c1': t2_c1['numbers']['vm_translation_lookup_requests'],
            'ready_only_control':
                t2_control['numbers']['vm_translation_lookup_requests'],
        },
        'no_additional_ablation_or_bandwidth_sweep': True,
        'runs': runs,
    }
    (PACK / 'RUN_RECEIPTS.json').write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    members = sorted(path for path in PACK.iterdir()
                     if path.is_file() and path.name != 'SHA256SUMS')
    (PACK / 'SHA256SUMS').write_text(
        ''.join(f'{sha(path)}  {path.name}\n' for path in members))
    print(json.dumps({
        'decision': decision, 'all_correct': receipt['all_correct'],
        'observational_neutrality_pass':
            receipt['observational_neutrality_pass'],
        'telemetry_supports_owner_wait': telemetry_supports,
        'ready_only_control_supports_causality': control_supports,
        't2_control_cycle_change_vs_c1':
            receipt['t2_control_cycle_change_vs_c1'],
        't2_control_cycle_change_vs_off':
            receipt['t2_control_cycle_change_vs_off'],
    }, indent=2, sort_keys=True))
    return 0 if receipt['all_correct'] and receipt['observational_neutrality_pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
