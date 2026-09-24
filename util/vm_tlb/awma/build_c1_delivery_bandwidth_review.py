#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

REPO = Path('/root/workspace/accel-sim-framework-awma-c1-delivery-bandwidth-diagnostic-v1')
RUNTIME = Path('/root/awma_c1_delivery_bandwidth_diagnostic_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_c1_delivery_bandwidth_diagnostic_v1/raw')
PACK = REPO / 'docs/vm_tlb/review_packs/AWMA_C1_DELIVERY_BANDWIDTH_DIAGNOSTIC_V1'
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
RUNNER = REPO / 'util/vm_tlb/awma/run_c1_delivery_bandwidth_diagnostic.py'
TEST_SOURCE = REPO / 'util/vm_tlb/awma/awma_c1_delivery_bandwidth_test.cc'

EXPECTED = {
    'A1': (2795248, 2, 51250),
    'T0': (368696302, 224, 3090304),
    'T2': (43357696, 1216, 411008),
}
PARENT = {
    'A1': {
        'off_cycles': 875138, 'one_cycles': 863057,
        'lookup_requests': 13366, 'l1_probes': 13366, 'l2_probes': 4,
        'share_owners': 13312, 'share_deliveries': 39936,
    },
    'T0': {
        'off_cycles': 527896, 'one_cycles': 487624,
        'lookup_requests': 393499, 'l1_probes': 369387, 'l2_probes': 8523,
        'share_owners': 364256, 'share_deliveries': 2722464,
    },
    'T2': {
        'off_cycles': 93079, 'one_cycles': 94034,
        'lookup_requests': 282838, 'l1_probes': 279190, 'l2_probes': 1218,
        'share_owners': 132544, 'share_deliveries': 132544,
    },
}
NUMERIC_KEYS = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_ready_application_duplicate_attempts',
    'vm_translation_lookup_entries', 'vm_translation_lookup_ready',
    'vm_translation_mshrs_entries', 'vm_translation_pwq_entries_active',
    'vm_translation_active_walks',
    'vm_translation_quiescent_invariants_hold',
    'vm_translation_lookup_requests', 'vm_l1_tlb_accesses',
    'vm_l2_tlb_accesses', 'vm_awma_same_page_share_owner_ready',
    'vm_awma_same_page_share_deliveries',
    'vm_awma_same_page_share_delivery_slots',
    'vm_awma_same_page_share_delivery_backlog_cycles',
    'vm_awma_same_page_share_delivery_backlog_member_cycles',
    'vm_awma_same_page_share_delivery_full_cycles',
    'vm_awma_same_page_share_delivery_backlog_max',
    'vm_awma_refill_pending_final',
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
    run_dir = DURABLE / f'{target}_C1_SLOTS2_10_80'
    command = json.loads((run_dir / 'command.json').read_text())
    text = (run_dir / 'run.log').read_text(errors='replace')
    expected_insn, expected_cta, expected_uid = EXPECTED[target]
    numbers = {key: last_number(text, key) for key in NUMERIC_KEYS}
    cov = coverage(text)
    modes = re.findall(r'^vm_awma_candidate_mode = (\S+)$', text, re.M)
    gates = {
        'rc': (run_dir / 'rc.txt').read_text().strip() == '0',
        'terminal': ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                     'GPGPU-Sim: *** exit detected ***' in text),
        'candidate_mode': bool(modes) and modes[-1] == 'same_page_share',
        'delivery_slots_two':
            numbers['vm_awma_same_page_share_delivery_slots'] == 2,
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
        'candidate_drain': numbers['vm_awma_refill_pending_final'] == 0,
        'mechanism_active': (
            numbers['vm_awma_same_page_share_owner_ready'] > 0 and
            numbers['vm_awma_same_page_share_deliveries'] > 0),
    }
    lookup_delta = abs(
        numbers['vm_translation_lookup_requests'] -
        PARENT[target]['lookup_requests']) / PARENT[target]['lookup_requests']
    l1_delta = abs(
        numbers['vm_l1_tlb_accesses'] -
        PARENT[target]['l1_probes']) / PARENT[target]['l1_probes']
    return {
        'target': target, 'run_dir': str(run_dir), 'command': command,
        'cycles': numbers['gpu_sim_cycle'], 'numbers': numbers,
        'coverage': cov, 'gates': gates,
        'correctness': all(gates.values()),
        'lookup_relative_delta': lookup_delta,
        'l1_relative_delta': l1_delta,
        'lookup_suppression_match': lookup_delta <= .01 and l1_delta <= .01,
        'run_log_sha256': sha(run_dir / 'run.log'),
        'command_sha256': sha(run_dir / 'command.json'),
        'wall_seconds': float((run_dir / 'wall_seconds.txt').read_text()),
    }


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)


def main() -> int:
    PACK.mkdir(parents=True, exist_ok=True)
    runs = [parse_run(target) for target in ('A1', 'T0', 'T2')]
    rows = []
    gates = []
    raw = []
    for run in runs:
        target = str(run['target'])
        parent = PARENT[target]
        numbers = run['numbers']
        two_cycles = int(run['cycles'])
        rows.append([
            target, parent['off_cycles'], parent['one_cycles'], two_cycles,
            f"{(two_cycles - parent['one_cycles']) / parent['one_cycles']:.9f}",
            f"{(two_cycles - parent['off_cycles']) / parent['off_cycles']:.9f}",
            parent['lookup_requests'], numbers['vm_translation_lookup_requests'],
            f"{run['lookup_relative_delta']:.9f}",
            parent['l1_probes'], numbers['vm_l1_tlb_accesses'],
            f"{run['l1_relative_delta']:.9f}",
            parent['l2_probes'], numbers['vm_l2_tlb_accesses'],
            parent['share_owners'], numbers['vm_awma_same_page_share_owner_ready'],
            parent['share_deliveries'],
            numbers['vm_awma_same_page_share_deliveries'],
            numbers['vm_awma_same_page_share_delivery_backlog_cycles'],
            numbers['vm_awma_same_page_share_delivery_backlog_member_cycles'],
            numbers['vm_awma_same_page_share_delivery_full_cycles'],
            numbers['vm_awma_same_page_share_delivery_backlog_max'],
            'PASS' if run['correctness'] else 'FAIL',
            'PASS' if run['lookup_suppression_match'] else 'FAIL',
            run['run_log_sha256'],
        ])
        gates.append([target] +
                     ['PASS' if value else 'FAIL'
                      for value in run['gates'].values()] +
                     ['PASS' if run['correctness'] else 'FAIL'])
        raw.extend([
            ['run_log', target, f"{run['run_dir']}/run.log",
             run['run_log_sha256'], 'P1_DIAGNOSTIC'],
            ['command', target, f"{run['run_dir']}/command.json",
             run['command_sha256'], 'P3_PROVENANCE'],
        ])

    t2 = next(run for run in runs if run['target'] == 'T2')
    one_excess = PARENT['T2']['one_cycles'] - PARENT['T2']['off_cycles']
    two_excess = int(t2['cycles']) - PARENT['T2']['off_cycles']
    shrink_fraction = (
        1.0 if two_excess <= 0
        else (one_excess - two_excess) / one_excess)
    supports = (
        all(bool(run['correctness']) for run in runs) and
        bool(t2['lookup_suppression_match']) and
        (two_excess <= 0 or shrink_fraction >= .5))
    decision = (
        'SUPPORTS_ONE_SLOT_DELIVERY_SERIALIZATION_AS_MAJOR_T2_CAUSE'
        if supports else
        'DOES_NOT_SUPPORT_ONE_SLOT_DELIVERY_SERIALIZATION_AS_MAJOR_T2_CAUSE')

    write_tsv(PACK / 'DIAGNOSTIC_MATRIX.tsv', [
        'target', 'off_cycles', 'one_slot_cycles', 'two_slot_cycles',
        'two_vs_one_cycle_change', 'two_vs_off_cycle_change',
        'one_slot_lookup_requests', 'two_slot_lookup_requests',
        'lookup_relative_delta', 'one_slot_l1_probes', 'two_slot_l1_probes',
        'l1_relative_delta', 'one_slot_l2_probes', 'two_slot_l2_probes',
        'one_slot_share_owners', 'two_slot_share_owners',
        'one_slot_share_deliveries', 'two_slot_share_deliveries',
        'two_slot_backlog_cycles', 'two_slot_backlog_member_cycles',
        'two_slot_full_cycles_with_backlog', 'two_slot_backlog_max',
        'correctness', 'lookup_suppression_match', 'run_log_sha256'], rows)
    gate_names = list(runs[0]['gates'])
    write_tsv(PACK / 'CORRECTNESS_GATES.tsv',
              ['target'] + gate_names + ['status'], gates)

    core_patch = PACK / 'CANDIDATE_CORE.patch'
    raw.extend([
        ['parent_evidence', 'PHASE1_MATRIX',
         str(REPO / 'docs/vm_tlb/review_packs/AWMA_LITERATURE_GUIDED_MECHANISM_EXPLORATION_V1/EXPLORATION_MATRIX.tsv'),
         sha(REPO / 'docs/vm_tlb/review_packs/AWMA_LITERATURE_GUIDED_MECHANISM_EXPLORATION_V1/EXPLORATION_MATRIX.tsv'),
         'P1_ACCEPTED_PARENT'],
        ['build_log', 'PHASE2_BUILD', str(RUNTIME / 'unified_build.log'),
         sha(RUNTIME / 'unified_build.log'), 'P4_RUNTIME'],
        ['binary', 'PHASE2_BINARY', str(BINARY), sha(BINARY), 'P3_PROVENANCE'],
        ['source_patch', 'PHASE2_CORE_PATCH', str(core_patch), sha(core_patch),
         'P3_PROVENANCE'],
        ['test_source', 'PHASE2_DIRECTED_TEST', str(TEST_SOURCE),
         sha(TEST_SOURCE), 'P3_PROVENANCE'],
        ['runner', 'PHASE2_RUNNER', str(RUNNER), sha(RUNNER), 'P3_PROVENANCE'],
        ['builder', 'PHASE2_REVIEW_BUILDER', str(Path(__file__)),
         sha(Path(__file__)), 'P3_PROVENANCE'],
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
            raw.append(['test_log', f'{test}:{mode}', str(log), sha(log),
                        'VERIFIED_RUN'])
    write_tsv(PACK / 'RAW_DATA_INDEX.tsv',
              ['kind', 'id', 'path', 'sha256', 'evidence_class'], raw)

    receipt = {
        'stage': 'AWMA_C1_DELIVERY_BANDWIDTH_DIAGNOSTIC_V1',
        'accepted_parent': '4cf2ee8294fbf761f735ae7089313a048ba0066b',
        'candidate_binary_sha256': sha(BINARY),
        'decision': decision, 'supports_serialization_explanation': supports,
        'one_slot_t2_excess_cycles': one_excess,
        'two_slot_t2_excess_cycles': two_excess,
        't2_excess_shrink_fraction': shrink_fraction,
        'all_correct': all(bool(run['correctness']) for run in runs),
        't2_lookup_suppression_match': bool(t2['lookup_suppression_match']),
        'no_four_or_eight_slot_runs': True,
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
        't2_lookup_suppression_match': receipt['t2_lookup_suppression_match'],
        'one_slot_t2_excess_cycles': one_excess,
        'two_slot_t2_excess_cycles': two_excess,
        't2_excess_shrink_fraction': shrink_fraction,
    }, indent=2, sort_keys=True))
    return 0 if receipt['all_correct'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
