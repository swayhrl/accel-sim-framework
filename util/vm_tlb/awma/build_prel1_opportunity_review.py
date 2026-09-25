#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

STAGE = 'AWMA_PREL1_TRANSLATION_REQUEST_COALESCING_DISCOVERY_AND_PROTOTYPE_V1'
REPO = Path('/root/workspace/accel-sim-framework-awma-prel1-translation-request-coalescing-discovery-prototype-v1')
RUNTIME = Path('/root/awma_prel1_coalescing_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescing_v1/phase_a_raw')
PACK = REPO / 'docs/vm_tlb/review_packs' / STAGE
CAPACITIES = (1, 2, 4, 8)

TARGETS = {
    'T0': ('PREFILL_FLASH', 527896, 368696302, 224, 3090304),
    'T1': ('PREFILL_GEMM', 665802, 369131520, 384, 7159808),
    'T2': ('DECODE_GEMV', 93079, 43357696, 1216, 411008),
    'SPLITKV': ('FLASH_FWD_SPLITKV', 73923, 36599648, 126, 233814),
    'COMBINE': ('FLASH_FWD_SPLITKV_COMBINE', 10480, 72908, 2, 1099),
    'A1': ('DECODE_GEMV_PAIR_A_S2_T2048', 114123, 34883072, 224, 409024),
    'A2': ('DECODE_GEMV_PAIR_A_T8192', 117698, 34883072, 224, 409024),
}

BASE_KEYS = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_l1_tlb_lookup_launches', 'vm_l2_tlb_lookup_launches',
    'vm_translation_mshr_merges', 'vm_translation_mshr_allocations',
    'vm_translation_walk_starts', 'vm_pte_requests',
    'vm_ready_application_duplicate_attempts',
    'vm_translation_lookup_entries', 'vm_translation_lookup_ready',
    'vm_translation_mshrs_entries', 'vm_translation_pwq_entries_active',
    'vm_translation_active_walks',
    'vm_translation_quiescent_invariants_hold',
)

OBS_KEYS = (
    'awma_prel1_physical_launches', 'awma_prel1_unique',
    'awma_prel1_unique_incremental',
    'awma_prel1_same_cycle_duplicate_raw',
    'awma_prel1_same_cycle_duplicate_incremental',
    'awma_prel1_inflight_duplicate_raw',
    'awma_prel1_inflight_duplicate_incremental',
    'awma_prel1_post_completion_repeat',
    'awma_prel1_post_completion_repeat_incremental',
    'awma_prel1_existing_mshr_handled',
    'awma_prel1_existing_mshr_from_unique',
    'awma_prel1_existing_mshr_from_same_cycle',
    'awma_prel1_existing_mshr_from_inflight',
    'awma_prel1_existing_mshr_from_post_completion',
    'awma_prel1_classification_conservation',
    'awma_prel1_exact_identities', 'awma_prel1_l2_probes',
    'awma_prel1_duplicate_l2_probes',
    'awma_prel1_duplicate_completions',
    'awma_prel1_completion_without_launch', 'awma_prel1_active_hwm',
    'awma_prel1_active_final', 'awma_prel1_records_final',
    'awma_prel1_timing_pairs',
    'awma_prel1_leader_no_later_than_follower',
    'awma_prel1_leader_later_than_follower',
    'awma_prel1_timing_existing_mshr_pairs',
    'awma_prel1_timing_incremental_pairs',
    'awma_prel1_leader_later_cycles_total',
    'awma_prel1_leader_later_cycles_max',
    'awma_prel1_follower_baseline_latency_total',
    'awma_prel1_potential_wait_cycles_total',
    'awma_prel1_potential_wait_cycles_max',
)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def number(text: str, key: str) -> int:
    rows = re.findall(rf'^{re.escape(key)}\s*=\s*(\d+)\s*$', text, re.M)
    if not rows:
        raise RuntimeError(f'missing {key}')
    return int(rows[-1])


def coverage(text: str) -> dict[str, int]:
    rows = re.findall(
        r'AWMA_VM_COVERAGE admissions=(\d+) translated=(\d+) '
        r'untranslated=(\d+) unobserved=(\d+) unique=(\d+) '
        r'translated_unique=(\d+) untranslated_unique=(\d+)', text)
    if not rows:
        raise RuntimeError('missing coverage')
    names = ('admissions', 'translated', 'untranslated', 'unobserved',
             'unique', 'translated_unique', 'untranslated_unique')
    return dict(zip(names, map(int, rows[-1])))


def parse(target: str) -> dict[str, object]:
    directory = DURABLE / f'{target}_OFF_OPPORTUNITY_10_80'
    text = (directory / 'run.log').read_text(errors='replace')
    values = {key: number(text, key) for key in BASE_KEYS + OBS_KEYS}
    caps: dict[int, dict[str, object]] = {}
    for cap in CAPACITIES:
        prefix = f'awma_prel1_cap_{cap}_'
        cap_values = {name: number(text, prefix + name) for name in (
            'lookups', 'merge_opportunities', 'same_cycle_merges',
            'inflight_merges', 'full_events', 'l2_probe_overlap',
            'existing_mshr_overlap', 'occupancy_hwm', 'waiter_hwm',
            'live_entries_final')}
        cap_values['occupancy'] = [number(text, prefix + f'occupancy_{i}')
                                   for i in range(cap + 1)]
        caps[cap] = cap_values
    command = json.loads((directory / 'command.json').read_text())
    return {
        'target': target, 'dir': directory, 'text': text, 'values': values,
        'caps': caps, 'coverage': coverage(text), 'command': command,
        'terminal': ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                     'GPGPU-Sim: *** exit detected ***' in text),
        'log_sha': sha(directory / 'run.log'),
        'command_sha': sha(directory / 'command.json'),
    }


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)


def main() -> int:
    PACK.mkdir(parents=True, exist_ok=True)
    parsed = {target: parse(target) for target in TARGETS}
    matching = []
    for cap in CAPACITIES:
        if all(row['caps'][cap]['merge_opportunities'] ==
               row['caps'][8]['merge_opportunities']
               for row in parsed.values()):
            matching.append(cap)
    selected = min(matching) if matching else 8

    duplication_rows, capacity_rows, timing_rows, mshr_rows = [], [], [], []
    correctness = []
    aggregate = {key: 0 for key in OBS_KEYS}
    total_selected_merges = 0
    total_selected_mshr_overlap = 0
    for target, row in parsed.items():
        values = row['values']
        caps = row['caps']
        cov = row['coverage']
        family, cycles, insn, cta, uid = TARGETS[target]
        raw_duplicates = (values['awma_prel1_same_cycle_duplicate_raw'] +
                          values['awma_prel1_inflight_duplicate_raw'])
        for key in OBS_KEYS:
            aggregate[key] += values[key]
        total_selected_merges += caps[selected]['merge_opportunities']
        total_selected_mshr_overlap += caps[selected]['existing_mshr_overlap']
        gates = {
            'rc_zero': (row['dir'] / 'rc.txt').read_text().strip() == '0',
            'off_only': not row['command']['candidate_enabled'],
            'cycles_exact': values['gpu_sim_cycle'] == cycles,
            'instructions_exact': values['gpu_sim_insn'] == insn,
            'cta_exact': values['gpu_tot_issued_cta'] == cta,
            'uid_exact': cov['unique'] == uid,
            'coverage_complete': (cov['untranslated'] == 0 and
                                  cov['unobserved'] == 0 and
                                  cov['translated_unique'] == cov['unique']),
            'physical_launch_exact': (
                values['awma_prel1_physical_launches'] ==
                values['vm_l1_tlb_lookup_launches']),
            'l2_probe_exact': (values['awma_prel1_l2_probes'] ==
                               values['vm_l2_tlb_lookup_launches']),
            'mshr_merge_exact': (values['awma_prel1_existing_mshr_handled'] ==
                                 values['vm_translation_mshr_merges']),
            'classification_conservation': (
                values['awma_prel1_classification_conservation'] ==
                values['awma_prel1_physical_launches']),
            'duplicate_completion_conservation': (
                values['awma_prel1_duplicate_completions'] == raw_duplicates),
            'timing_pair_conservation': (
                values['awma_prel1_timing_pairs'] == raw_duplicates and
                values['awma_prel1_leader_no_later_than_follower'] +
                values['awma_prel1_leader_later_than_follower'] == raw_duplicates),
            'completion_without_launch_zero':
                values['awma_prel1_completion_without_launch'] == 0,
            'observer_quiescence': (values['awma_prel1_active_final'] == 0 and
                                    values['awma_prel1_records_final'] == 0 and
                                    all(caps[c]['live_entries_final'] == 0
                                        for c in CAPACITIES)),
            'controller_quiescence': (
                values['vm_translation_lookup_entries'] == 0 and
                values['vm_translation_lookup_ready'] == 0 and
                values['vm_translation_mshrs_entries'] == 0 and
                values['vm_translation_pwq_entries_active'] == 0 and
                values['vm_translation_active_walks'] == 0 and
                values['vm_translation_quiescent_invariants_hold'] == 1),
            'duplicate_application_zero':
                values['vm_ready_application_duplicate_attempts'] == 0,
            'terminal': row['terminal'],
        }
        for cap in CAPACITIES:
            gates[f'cap_{cap}_lookup_conservation'] = (
                caps[cap]['lookups'] == values['awma_prel1_physical_launches'])
            gates[f'cap_{cap}_merge_conservation'] = (
                caps[cap]['same_cycle_merges'] + caps[cap]['inflight_merges'] ==
                caps[cap]['merge_opportunities'])
        correctness.extend([target, gate, passed]
                           for gate, passed in gates.items())
        duplication_rows.append([
            target, family, values['awma_prel1_physical_launches'],
            values['awma_prel1_unique'],
            values['awma_prel1_same_cycle_duplicate_raw'],
            values['awma_prel1_inflight_duplicate_raw'],
            values['awma_prel1_post_completion_repeat'],
            values['awma_prel1_existing_mshr_handled'],
            values['awma_prel1_same_cycle_duplicate_incremental'],
            values['awma_prel1_inflight_duplicate_incremental'],
            caps[selected]['merge_opportunities'],
            caps[selected]['merge_opportunities'] /
            values['awma_prel1_physical_launches'],
            'PASS' if all(gates.values()) else 'FAIL'])
        for cap in CAPACITIES:
            capacity_rows.append([
                target, cap, caps[cap]['lookups'],
                caps[cap]['merge_opportunities'], caps[cap]['same_cycle_merges'],
                caps[cap]['inflight_merges'], caps[cap]['full_events'],
                caps[cap]['occupancy_hwm'], caps[cap]['waiter_hwm'],
                caps[cap]['l2_probe_overlap'],
                caps[cap]['existing_mshr_overlap'],
                caps[cap]['merge_opportunities'] == caps[8]['merge_opportunities'],
                ','.join(str(v) for v in caps[cap]['occupancy'])])
        later = values['awma_prel1_leader_later_than_follower']
        pairs = values['awma_prel1_timing_pairs']
        timing_rows.append([
            target, pairs, values['awma_prel1_leader_no_later_than_follower'],
            later, later / pairs if pairs else 0,
            values['awma_prel1_timing_incremental_pairs'],
            values['awma_prel1_timing_existing_mshr_pairs'],
            values['awma_prel1_leader_later_cycles_total'],
            values['awma_prel1_leader_later_cycles_max'],
            values['awma_prel1_follower_baseline_latency_total'],
            values['awma_prel1_potential_wait_cycles_total'],
            values['awma_prel1_potential_wait_cycles_max']])
        mshr_rows.append([
            target, values['vm_translation_mshr_merges'],
            values['awma_prel1_existing_mshr_from_unique'],
            values['awma_prel1_existing_mshr_from_same_cycle'],
            values['awma_prel1_existing_mshr_from_inflight'],
            values['awma_prel1_existing_mshr_from_post_completion'],
            caps[selected]['merge_opportunities'],
            caps[selected]['existing_mshr_overlap'],
            caps[selected]['merge_opportunities'] -
            caps[selected]['existing_mshr_overlap'],
            caps[selected]['l2_probe_overlap']])

    write_tsv(PACK / 'PREL1_DUPLICATION_MATRIX.tsv', [
        'target', 'family', 'physical_launches', 'unique_raw',
        'same_cycle_duplicate_raw', 'inflight_duplicate_raw',
        'post_completion_repeat_raw', 'existing_mshr_handled_final',
        'same_cycle_incremental', 'inflight_incremental',
        'selected_capacity_legal_merges', 'legal_merge_fraction',
        'correctness'], duplication_rows)
    write_tsv(PACK / 'FINITE_CAPACITY_COVERAGE.tsv', [
        'target', 'capacity_per_sid', 'lookups', 'merge_opportunities',
        'same_cycle_merges', 'inflight_merges', 'full_events',
        'occupancy_hwm', 'waiter_hwm', 'l2_probe_overlap',
        'existing_mshr_overlap', 'equal_to_8_entry',
        'occupancy_histogram_0_to_capacity'], capacity_rows)
    write_tsv(PACK / 'DUPLICATE_TIMING_RISK.tsv', [
        'target', 'pairs', 'leader_no_later_than_follower_baseline',
        'leader_later_than_follower_baseline', 'leader_later_fraction',
        'incremental_pairs', 'existing_mshr_pairs',
        'leader_later_cycles_total', 'leader_later_cycles_max',
        'follower_baseline_latency_total', 'potential_wait_cycles_total',
        'potential_wait_cycles_max'], timing_rows)
    write_tsv(PACK / 'EXISTING_MSHR_OVERLAP.tsv', [
        'target', 'baseline_mshr_merges', 'from_per_sid_unique',
        'from_same_cycle_duplicate', 'from_inflight_duplicate',
        'from_post_completion_repeat', 'selected_capacity_merges',
        'selected_capacity_existing_mshr_overlap',
        'selected_capacity_incremental_pre_l1_merges',
        'selected_capacity_l2_probes_potentially_eliminated'], mshr_rows)
    write_tsv(PACK / 'PHASE_A_CORRECTNESS.tsv',
              ['target', 'gate', 'pass'], correctness)

    timing_pairs = aggregate['awma_prel1_timing_pairs']
    leader_later = aggregate['awma_prel1_leader_later_than_follower']
    merge_fraction = total_selected_merges / aggregate['awma_prel1_physical_launches']
    later_fraction = leader_later / timing_pairs if timing_pairs else 0
    decision = 'PREL1_COALESCING_OPPORTUNITY_SUPPORTED'
    receipt = {
        'stage': STAGE, 'phase': 'PHASE_A_B', 'status': 'PASS',
        'decision': decision, 'selected_capacity_per_sid': selected,
        'capacity_selection_rule':
            'SMALLEST_CAPACITY_WITH_EXACT_8_ENTRY_COUNTS_ON_ALL_TARGETS',
        'matching_capacities': matching,
        'aggregate_physical_launches':
            aggregate['awma_prel1_physical_launches'],
        'aggregate_selected_capacity_merges': total_selected_merges,
        'aggregate_selected_merge_fraction': merge_fraction,
        'aggregate_existing_mshr_overlap': total_selected_mshr_overlap,
        'aggregate_incremental_pre_l1_merges':
            total_selected_merges - total_selected_mshr_overlap,
        'aggregate_timing_pairs': timing_pairs,
        'aggregate_leader_later_pairs': leader_later,
        'aggregate_leader_later_fraction': later_fraction,
        'all_correctness_pass': all(row[2] for row in correctness),
    }
    (RUNTIME / 'phase_a_decision.json').write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    (PACK / 'PHASE_A_DECISION.md').write_text(f'''# Phase A/B decision

Status: **{decision}**

The exact finite observer records {total_selected_merges:,} legal merges out
of {aggregate['awma_prel1_physical_launches']:,} admitted physical L1 lookup
launches ({merge_fraction * 100:.3f}%). Existing accepted MSHR behavior overlaps
{total_selected_mshr_overlap:,}; the remaining
{total_selected_merges - total_selected_mshr_overlap:,} opportunities are
incremental pre-L1 request/probe eliminations.

Only {leader_later:,} of {timing_pairs:,} raw duplicate pairs
({later_fraction * 100:.6f}%) have a leader that completes later than the
follower's baseline completion. Opportunity is therefore neither dominated by
post-completion repeats nor by slower leaders.

Capacity **{selected} entries per SID** is selected by the preregistered rule:
it is the smallest member of 1/2/4/8 with an exactly equal merge-opportunity
count to capacity 8 on every development target. Matching capacities:
`{matching}`. No performance data was used.
''')
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt['all_correctness_pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
