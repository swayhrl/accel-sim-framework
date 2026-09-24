#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

REPO = Path('/root/workspace/accel-sim-framework-awma-c1-fanout-aware-sharing-exploration-v1')
RUNTIME = Path('/root/awma_c1_fanout_aware_sharing_exploration_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_c1_fanout_aware_sharing_exploration_v1/raw')
PACK = REPO / 'docs/vm_tlb/review_packs/AWMA_C1_FANOUT_AWARE_SHARING_EXPLORATION_V1'
RUNNER = REPO / 'util/vm_tlb/awma/run_c1_fanout_aware_exploration.py'
TEST_SOURCE = REPO / 'util/vm_tlb/awma/awma_c1_fanout_aware_test.cc'
BINARY = RUNTIME / 'bin/unified_accel-sim.out'

EXPECTED = {
    'A1': (2795248, 2, 51250),
    'T0': (368696302, 224, 3090304),
    'T1': (369131520, 384, 7159808),
    'T2': (43357696, 1216, 411008),
}
PARENT = {
    'A1': {'off': 875138, 'c1': 863057, 'c1_admissions': 51250,
           'c1_lookup': 13366, 'c1_l1': 13366, 'c1_l2': 4},
    'T0': {'off': 527896, 'c1': 487624, 'c1_admissions': 3090304,
           'c1_lookup': 393499, 'c1_l1': 369387, 'c1_l2': 8523},
    'T1': {'off': 665802, 'c1': 653485, 'c1_admissions': 7170373,
           'c1_lookup': 613449, 'c1_l1': 531081, 'c1_l2': 8877},
    'T2': {'off': 93079, 'c1': 94034, 'c1_admissions': 832383,
           'c1_lookup': 282838, 'c1_l1': 279190, 'c1_l2': 1218},
}
NUMERIC_KEYS = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_translation_lookup_requests', 'vm_l1_tlb_accesses',
    'vm_l2_tlb_accesses', 'vm_ready_application_duplicate_attempts',
    'vm_translation_lookup_entries', 'vm_translation_lookup_ready',
    'vm_translation_mshrs_entries', 'vm_translation_pwq_entries_active',
    'vm_translation_active_walks',
    'vm_translation_quiescent_invariants_hold',
    'vm_awma_same_page_share_min_cohort_size',
    'vm_awma_same_page_share_owner_ready',
    'vm_awma_same_page_share_deliveries',
    'awma_owner_wait_admissions', 'awma_owner_wait_unique_admitted_uids',
    'awma_owner_wait_repeated_admissions', 'awma_owner_wait_readmitted_uids',
    'awma_owner_wait_owner_attempts',
    'awma_owner_wait_owner_retry_attempts',
    'awma_owner_wait_member_owner_wait_cycles',
    'awma_owner_wait_head_block_total_cycles',
    'awma_owner_wait_pending_members_final',
    'awma_owner_wait_cohort_size_max', 'awma_owner_wait_gated_cohorts',
    'awma_owner_wait_shared_cohorts',
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


def parse_run(target: str) -> dict[str, object]:
    directory = DURABLE / f'{target}_C1_FANOUT4_10_80'
    text = (directory / 'run.log').read_text(errors='replace')
    command = json.loads((directory / 'command.json').read_text())
    numbers = {key: last_number(text, key) for key in NUMERIC_KEYS}
    cov = coverage(text)
    insn, cta, uid = EXPECTED[target]
    modes = re.findall(r'^vm_awma_candidate_mode = (\S+)$', text, re.M)
    cohort_total = sum(numbers[key] for key in (
        'awma_owner_wait_cohort_hist_2', 'awma_owner_wait_cohort_hist_3',
        'awma_owner_wait_cohort_hist_4', 'awma_owner_wait_cohort_hist_5_8',
        'awma_owner_wait_cohort_hist_9_16',
        'awma_owner_wait_cohort_hist_17_32'))
    service_total = sum(numbers[key] for key in (
        'awma_owner_wait_owner_service_l1',
        'awma_owner_wait_owner_service_l2',
        'awma_owner_wait_owner_service_mshr_merge',
        'awma_owner_wait_owner_service_ptw',
        'awma_owner_wait_owner_service_unobserved'))
    gates = {
        'rc': (directory / 'rc.txt').read_text().strip() == '0',
        'terminal': ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                     'GPGPU-Sim: *** exit detected ***' in text),
        'candidate_mode': bool(modes) and modes[-1] == 'same_page_share',
        'min_cohort_size_four':
            numbers['vm_awma_same_page_share_min_cohort_size'] == 4,
        'instructions': numbers['gpu_sim_insn'] == insn,
        'cta': numbers['gpu_tot_issued_cta'] == cta,
        'unique_uid': cov['unique'] == uid,
        'translated_unique': cov['translated_unique'] == uid,
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
        'admission_conservation': numbers['awma_owner_wait_admissions'] ==
            cov['admissions'],
        'cohort_conservation': cohort_total ==
            numbers['awma_owner_wait_gated_cohorts'] +
            numbers['awma_owner_wait_shared_cohorts'],
        'service_conservation': service_total ==
            numbers['awma_owner_wait_shared_cohorts'],
        'a1_neutrality': target != 'A1' or
            (numbers['gpu_sim_cycle'] == PARENT['A1']['c1'] and
             cov['admissions'] == PARENT['A1']['c1_admissions']),
    }
    return {
        'target': target, 'run_dir': str(directory), 'cycles': numbers['gpu_sim_cycle'],
        'coverage': cov, 'numbers': numbers, 'gates': gates,
        'correctness': all(gates.values()), 'command': command,
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
    PACK.mkdir(parents=True, exist_ok=True)
    runs = [parse_run(target) for target in ('A1', 'T0', 'T1', 'T2')]
    by_target = {str(run['target']): run for run in runs}
    rows = []
    gate_rows = []
    raw_rows = []
    for run in runs:
        target = str(run['target'])
        parent = PARENT[target]
        n = run['numbers']
        c = run['coverage']
        rows.append([
            target, parent['off'], parent['c1'], run['cycles'],
            f"{(run['cycles'] - parent['off']) / parent['off']:.9f}",
            f"{(run['cycles'] - parent['c1']) / parent['c1']:.9f}",
            c['admissions'], c['unique'],
            n['awma_owner_wait_repeated_admissions'],
            n['awma_owner_wait_readmitted_uids'],
            parent['c1_lookup'], n['vm_translation_lookup_requests'],
            parent['c1_l1'], n['vm_l1_tlb_accesses'],
            parent['c1_l2'], n['vm_l2_tlb_accesses'],
            n['vm_awma_same_page_share_owner_ready'],
            n['vm_awma_same_page_share_deliveries'],
            n['awma_owner_wait_owner_attempts'],
            n['awma_owner_wait_owner_retry_attempts'],
            n['awma_owner_wait_member_owner_wait_cycles'],
            n['awma_owner_wait_head_block_total_cycles'],
            n['awma_owner_wait_cohort_hist_2'],
            n['awma_owner_wait_cohort_hist_3'],
            n['awma_owner_wait_cohort_hist_4'],
            n['awma_owner_wait_cohort_hist_5_8'],
            n['awma_owner_wait_cohort_hist_9_16'],
            n['awma_owner_wait_cohort_hist_17_32'],
            n['awma_owner_wait_gated_cohorts'],
            n['awma_owner_wait_shared_cohorts'],
            'PASS' if run['correctness'] else 'FAIL', run['run_log_sha256'],
        ])
        gate_rows.append([target] + ['PASS' if value else 'FAIL'
                                    for value in run['gates'].values()] +
                         ['PASS' if run['correctness'] else 'FAIL'])
        raw_rows.extend([
            ['run_log', target, f"{run['run_dir']}/run.log",
             run['run_log_sha256'], 'P1_DISCOVERY'],
            ['command', target, f"{run['run_dir']}/command.json",
             run['command_sha256'], 'P3_PROVENANCE'],
        ])

    t0 = by_target['T0']
    t1 = by_target['T1']
    t2 = by_target['T2']
    t0_parent_saving = PARENT['T0']['off'] - PARENT['T0']['c1']
    t0_new_saving = PARENT['T0']['off'] - int(t0['cycles'])
    t0_retention = t0_new_saving / t0_parent_saving
    t2_relative_off = abs(int(t2['cycles']) - PARENT['T2']['off']) / PARENT['T2']['off']
    promising = (
        all(bool(run['correctness']) for run in runs) and
        t0_retention >= .75 and int(t1['cycles']) < PARENT['T1']['off'] and
        int(t2['cycles']) < PARENT['T2']['c1'] and t2_relative_off <= .0025)
    decision = ('FANOUT_AWARE_SHARING_PROMISING_DISCOVERY' if promising else
                'FANOUT_AWARE_SHARING_NOT_SUPPORTED')

    write_tsv(PACK / 'FANOUT_MATRIX.tsv', [
        'target', 'off_cycles', 'accepted_c1_cycles', 'fanout4_cycles',
        'fanout4_vs_off_cycle_change', 'fanout4_vs_c1_cycle_change',
        'admissions', 'unique_uid', 'repeated_admissions', 'readmitted_uids',
        'accepted_c1_lookup_requests', 'fanout4_lookup_requests',
        'accepted_c1_l1_probes', 'fanout4_l1_probes',
        'accepted_c1_l2_probes', 'fanout4_l2_probes', 'share_owners',
        'share_deliveries', 'owner_attempts', 'owner_retry_attempts',
        'member_owner_wait_cycles', 'head_block_cycles', 'cohort_size_2',
        'cohort_size_3', 'cohort_size_4', 'cohort_size_5_8',
        'cohort_size_9_16', 'cohort_size_17_32', 'gated_cohorts',
        'shared_cohorts', 'correctness', 'run_log_sha256'], rows)
    gate_names = list(runs[0]['gates'])
    write_tsv(PACK / 'CORRECTNESS_GATES.tsv',
              ['target'] + gate_names + ['status'], gate_rows)

    core_patch = PACK / 'CANDIDATE_CORE.patch'
    raw_rows.extend([
        ['parent_evidence', 'ATTRIBUTION_MATRIX',
         str(REPO / 'docs/vm_tlb/review_packs/AWMA_C1_T2_OWNER_WAIT_RETRY_ATTRIBUTION_V1/ATTRIBUTION_MATRIX.tsv'),
         sha(REPO / 'docs/vm_tlb/review_packs/AWMA_C1_T2_OWNER_WAIT_RETRY_ATTRIBUTION_V1/ATTRIBUTION_MATRIX.tsv'),
         'P1_ACCEPTED_PARENT'],
        ['build_log', 'FANOUT_BUILD', str(RUNTIME / 'unified_build.log'),
         sha(RUNTIME / 'unified_build.log'), 'P4_RUNTIME'],
        ['binary', 'FANOUT_BINARY', str(BINARY), sha(BINARY), 'P3_PROVENANCE'],
        ['source_patch', 'FINAL_CORE_PATCH', str(core_patch), sha(core_patch),
         'P3_PROVENANCE'],
        ['test_source', 'DIRECTED_TEST', str(TEST_SOURCE), sha(TEST_SOURCE),
         'P3_PROVENANCE'],
        ['runner', 'FANOUT_RUNNER', str(RUNNER), sha(RUNNER), 'P3_PROVENANCE'],
        ['builder', 'REVIEW_BUILDER', str(Path(__file__)), sha(Path(__file__)),
         'P3_PROVENANCE'],
        ['test_log', 'CORE_PATCH_DRY_RUN',
         str(RUNTIME / 'tests/candidate_core_patch_dry_run.log'),
         sha(RUNTIME / 'tests/candidate_core_patch_dry_run.log'),
         'VERIFIED_RUN'],
    ])
    for test in (
            'awma_literature_mechanism_test',
            'vm_m3_g3_4b_tlb_timing_test',
            'vm_m2_rf_pending_retry_test',
            'vm_c10b_runtime_validation_test'):
        for mode in ('none', 'refill_protect'):
            log = RUNTIME / 'tests' / f'{test}_{mode}.log'
            raw_rows.append(['test_log', f'{test}:{mode}', str(log), sha(log),
                             'VERIFIED_RUN'])
    write_tsv(PACK / 'RAW_DATA_INDEX.tsv',
              ['kind', 'id', 'path', 'sha256', 'evidence_class'], raw_rows)

    receipt = {
        'stage': 'AWMA_C1_FANOUT_AWARE_SHARING_EXPLORATION_V1',
        'accepted_parent': '82b82282d0a7b048d39c976304d2cabc03c341fa',
        'decision': decision, 'promising_discovery': promising,
        'min_cohort_size': 4, 'threshold_sweep_performed': False,
        'all_correct': all(bool(run['correctness']) for run in runs),
        'a1_neutrality_pass': bool(by_target['A1']['gates']['a1_neutrality']),
        't0_c1_saving_retention': t0_retention,
        't1_cycle_change_vs_off':
            (int(t1['cycles']) - PARENT['T1']['off']) / PARENT['T1']['off'],
        't2_cycle_change_vs_off':
            (int(t2['cycles']) - PARENT['T2']['off']) / PARENT['T2']['off'],
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
        'a1_neutrality_pass': receipt['a1_neutrality_pass'],
        't0_c1_saving_retention': t0_retention,
        't1_cycle_change_vs_off': receipt['t1_cycle_change_vs_off'],
        't2_cycle_change_vs_off': receipt['t2_cycle_change_vs_off'],
    }, indent=2, sort_keys=True))
    return 0 if receipt['all_correct'] and receipt['a1_neutrality_pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
