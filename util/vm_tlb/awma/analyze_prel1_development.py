#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

STAGE = 'AWMA_PREL1_TRANSLATION_REQUEST_COALESCING_DISCOVERY_AND_PROTOTYPE_V1'
REPO = Path('/root/workspace/accel-sim-framework-awma-prel1-translation-request-coalescing-discovery-prototype-v1')
RUNTIME = Path('/root/awma_prel1_coalescing_v1_runtime')
OFF_ROOT = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescing_v1/phase_a_raw')
CAND_ROOT = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescing_v1/development_raw')
PACK = REPO / 'docs/vm_tlb/review_packs' / STAGE
TARGETS = {
    'T0': ('PREFILL_FLASH', 368696302, 224, 3090304),
    'T1': ('PREFILL_GEMM', 369131520, 384, 7159808),
    'T2': ('DECODE_GEMV', 43357696, 1216, 411008),
    'SPLITKV': ('FLASH_FWD_SPLITKV', 36599648, 126, 233814),
    'COMBINE': ('FLASH_FWD_SPLITKV_COMBINE', 72908, 2, 1099),
    'A1': ('DECODE_GEMV_PAIR_A_S2_T2048', 34883072, 224, 409024),
    'A2': ('DECODE_GEMV_PAIR_A_T8192', 34883072, 224, 409024),
}
BASE = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_translation_lookup_requests', 'vm_l1_tlb_lookup_launches',
    'vm_l2_tlb_lookup_launches', 'vm_l1_tlb_accesses',
    'vm_l2_tlb_accesses', 'vm_translation_mshr_allocations',
    'vm_translation_mshr_merges', 'vm_translation_walk_starts',
    'vm_pte_requests', 'vm_ready_application_duplicate_attempts',
    'vm_translation_lookup_entries', 'vm_translation_lookup_ready',
    'vm_translation_mshrs_entries', 'vm_translation_pwq_entries_active',
    'vm_translation_active_walks',
    'vm_translation_quiescent_invariants_hold',
)
COAL = tuple(f'awma_prel1_coalescer_{name}' for name in (
    'lookups', 'compare_delays', 'leaders', 'followers',
    'same_cycle_merges', 'inflight_merges', 'entry_full_fallbacks',
    'waiter_full_fallbacks', 'leader_completions',
    'follower_applications', 'follower_wait_cycles_total',
    'follower_wait_cycles_max', 'follower_delivery_latency_total',
    'follower_delivery_latency_max', 'leader_to_follower_latency_total',
    'leader_to_follower_latency_max', 'head_block_cycles',
    'critical_path_followers', 'l1_hit_leaders', 'l2_hit_leaders',
    'ptw_leaders', 'other_source_leaders', 'occupancy_hwm', 'waiter_hwm',
    'delivery_wait_p50', 'delivery_wait_p95', 'delivery_wait_p99',
    'followers_final', 'pending_compares_final', 'live_entries_final',
    'waiters_final', 'quiescent'))
OWNER = (
    'awma_owner_wait_admissions', 'awma_owner_wait_repeated_admissions',
    'awma_owner_wait_readmitted_uids')


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
    names = ('admissions', 'translated', 'untranslated', 'unobserved',
             'unique', 'translated_unique', 'untranslated_unique')
    return dict(zip(names, map(int, rows[-1])))


def parse(path: Path, candidate: bool) -> dict[str, object]:
    text = (path / 'run.log').read_text(errors='replace')
    values = {key: number(text, key) for key in BASE}
    if candidate:
        values.update({key: number(text, key) for key in COAL + OWNER})
    return {
        'path': path, 'text': text, 'values': values,
        'coverage': coverage(text),
        'terminal': ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                     'GPGPU-Sim: *** exit detected ***' in text),
    }


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)


def main() -> int:
    development, wait_rows, physical, correctness = [], [], [], []
    summary = {}
    all_correct = True
    regressions = []
    material = []
    for target, (family, insn, cta, uid) in TARGETS.items():
        off = parse(OFF_ROOT / f'{target}_OFF_OPPORTUNITY_10_80', False)
        cand = parse(CAND_ROOT / f'{target}_COALESCER_10_80', True)
        ov, cv = off['values'], cand['values']
        oc, cc = off['coverage'], cand['coverage']
        speedup = (ov['gpu_sim_cycle'] - cv['gpu_sim_cycle']) / ov['gpu_sim_cycle']
        if speedup < -0.005:
            regressions.append(target)
        if abs(speedup) > 0.005:
            material.append(target)
        gates = {
            'rc_zero': (cand['path'] / 'rc.txt').read_text().strip() == '0',
            'instructions_exact': ov['gpu_sim_insn'] == cv['gpu_sim_insn'] == insn,
            'cta_exact': ov['gpu_tot_issued_cta'] == cv['gpu_tot_issued_cta'] == cta,
            'uid_exact': oc['unique'] == cc['unique'] == uid,
            'coverage_complete': (cc['untranslated'] == 0 and cc['unobserved'] == 0 and cc['translated_unique'] == cc['unique']),
            'duplicate_application_zero': cv['vm_ready_application_duplicate_attempts'] == 0,
            'terminal': cand['terminal'],
            'controller_quiescence': (cv['vm_translation_lookup_entries'] == 0 and cv['vm_translation_lookup_ready'] == 0 and cv['vm_translation_mshrs_entries'] == 0 and cv['vm_translation_pwq_entries_active'] == 0 and cv['vm_translation_active_walks'] == 0 and cv['vm_translation_quiescent_invariants_hold'] == 1),
            'coalescer_quiescence': (cv['awma_prel1_coalescer_followers_final'] == 0 and cv['awma_prel1_coalescer_pending_compares_final'] == 0 and cv['awma_prel1_coalescer_live_entries_final'] == 0 and cv['awma_prel1_coalescer_waiters_final'] == 0 and cv['awma_prel1_coalescer_quiescent'] == 1),
            'leader_completion_conservation': cv['awma_prel1_coalescer_leaders'] == cv['awma_prel1_coalescer_leader_completions'],
            'follower_application_conservation': cv['awma_prel1_coalescer_followers'] == cv['awma_prel1_coalescer_follower_applications'],
            'capacity_bound': cv['awma_prel1_coalescer_occupancy_hwm'] <= 2,
            'waiter_bound': cv['awma_prel1_coalescer_waiter_hwm'] <= 32,
            'physical_l1_suppression': cv['vm_l1_tlb_lookup_launches'] < ov['vm_l1_tlb_lookup_launches'],
        }
        all_correct &= all(gates.values())
        for gate, passed in gates.items():
            correctness.append([target, gate, passed])
        l1_delta = ov['vm_l1_tlb_lookup_launches'] - cv['vm_l1_tlb_lookup_launches']
        l2_delta = ov['vm_l2_tlb_lookup_launches'] - cv['vm_l2_tlb_lookup_launches']
        development.append([
            target, family, ov['gpu_sim_cycle'], cv['gpu_sim_cycle'],
            speedup * 100, ov['vm_l1_tlb_lookup_launches'],
            cv['vm_l1_tlb_lookup_launches'], l1_delta,
            ov['vm_l2_tlb_lookup_launches'], cv['vm_l2_tlb_lookup_launches'],
            l2_delta, ov['vm_translation_mshr_allocations'],
            cv['vm_translation_mshr_allocations'],
            ov['vm_translation_mshr_merges'],
            cv['vm_translation_mshr_merges'],
            ov['vm_translation_walk_starts'], cv['vm_translation_walk_starts'],
            ov['vm_pte_requests'], cv['vm_pte_requests'],
            cv['awma_prel1_coalescer_leaders'],
            cv['awma_prel1_coalescer_followers'],
            cv['awma_prel1_coalescer_entry_full_fallbacks'],
            cv['awma_prel1_coalescer_waiter_full_fallbacks'],
            cc['admissions'], cc['admissions'] - cc['unique'],
            cv['awma_owner_wait_readmitted_uids'],
            'PASS' if all(gates.values()) else 'FAIL'])
        wait_count = cv['awma_prel1_coalescer_follower_applications']
        wait_rows.append([
            target, wait_count,
            cv['awma_prel1_coalescer_follower_wait_cycles_total'],
            cv['awma_prel1_coalescer_follower_wait_cycles_total'] / wait_count if wait_count else 0,
            cv['awma_prel1_coalescer_delivery_wait_p50'],
            cv['awma_prel1_coalescer_delivery_wait_p95'],
            cv['awma_prel1_coalescer_delivery_wait_p99'],
            cv['awma_prel1_coalescer_follower_delivery_latency_max'],
            cv['awma_prel1_coalescer_leader_to_follower_latency_total'],
            cv['awma_prel1_coalescer_leader_to_follower_latency_max'],
            cv['awma_prel1_coalescer_head_block_cycles'],
            cv['awma_prel1_coalescer_critical_path_followers']])
        physical.append([
            target, cv['awma_prel1_coalescer_followers'], l1_delta,
            l1_delta / ov['vm_l1_tlb_lookup_launches'], l2_delta,
            ov['vm_translation_mshr_merges'] - cv['vm_translation_mshr_merges'],
            ov['vm_translation_walk_starts'] - cv['vm_translation_walk_starts'],
            ov['vm_pte_requests'] - cv['vm_pte_requests'],
            cv['awma_prel1_coalescer_entry_full_fallbacks'],
            cv['awma_prel1_coalescer_waiter_full_fallbacks']])
        summary[target] = {
            'off_cycles': ov['gpu_sim_cycle'], 'candidate_cycles': cv['gpu_sim_cycle'],
            'speedup_fraction': speedup, 'followers': cv['awma_prel1_coalescer_followers'],
            'l1_suppressed': l1_delta, 'l2_suppressed': l2_delta,
            'head_block_cycles': cv['awma_prel1_coalescer_head_block_cycles'],
            'correctness': all(gates.values()),
        }

    write_tsv(PACK / 'DEVELOPMENT_MATRIX.tsv', [
        'target', 'family', 'off_cycles', 'candidate_cycles', 'speedup_percent',
        'off_l1_launches', 'candidate_l1_launches', 'l1_suppressed',
        'off_l2_launches', 'candidate_l2_launches', 'l2_suppressed',
        'off_mshr_alloc', 'candidate_mshr_alloc', 'off_mshr_merge',
        'candidate_mshr_merge', 'off_walks', 'candidate_walks',
        'off_pte', 'candidate_pte', 'leaders', 'followers',
        'entry_full_fallback', 'waiter_full_fallback',
        'coverage_admissions', 're_admissions', 'readmitted_uid', 'correctness'],
        development)
    write_tsv(PACK / 'FOLLOWER_WAIT_MATRIX.tsv', [
        'target', 'follower_count', 'wait_cycles_total', 'wait_cycles_mean',
        'delivery_wait_p50', 'delivery_wait_p95', 'delivery_wait_p99',
        'delivery_wait_max', 'leader_to_follower_latency_total',
        'leader_to_follower_latency_max', 'head_block_cycles',
        'critical_path_followers'], wait_rows)
    write_tsv(PACK / 'PHYSICAL_SERVICE_SUPPRESSION.tsv', [
        'target', 'followers', 'l1_launches_suppressed',
        'l1_suppression_fraction', 'l2_launches_suppressed',
        'mshr_merges_reduced', 'walks_reduced', 'pte_requests_reduced',
        'entry_full_fallback', 'waiter_full_fallback'], physical)
    write_tsv(PACK / 'DEVELOPMENT_CORRECTNESS.tsv',
              ['target', 'gate', 'pass'], correctness)
    # A broad failure means a majority pattern, not two isolated development
    # regressions that still require the preregistered matched control.
    survived = all_correct and len(regressions) * 2 < len(TARGETS)
    receipt = {
        'stage': STAGE, 'status': 'PASS' if all_correct else 'FAIL',
        'candidate_survives_for_controls': survived,
        'material_response_targets': material,
        'regression_over_half_percent_targets': regressions,
        'targets': summary,
    }
    (RUNTIME / 'development_decision.json').write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if all_correct else 1


if __name__ == '__main__':
    raise SystemExit(main())
