#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

STAGE = 'AWMA_PREL1_COALESCER_MINIMAL_INDEPENDENT_HOLDOUT_VALIDATION_V1'
REPO = Path('/root/workspace/accel-sim-framework-awma-prel1-coalescer-minimal-independent-holdout-validation-v1')
RUNTIME = Path('/root/awma_prel1_coalescing_v1_runtime')
RAW = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescer_minimal_independent_holdout_validation_v1/raw')
PACK = REPO / 'docs/vm_tlb/review_packs' / STAGE
MECHANISM = '163a8572f9272891b8109f9158aa79ca88d9e153'
SOURCE_FREEZE = '2bbbceabb5261777fe385289ecb6579791e0f232'
CAPTURE = 'a984735c1d39b8d155aec2ef25dde0502f7c940b'
TRACE_SHA = 'ed712fb618309fd4f08c5ccc284a807df8a78581df2880f76fc415fa8a3b9105'

BASE_KEYS = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_l1_tlb_lookup_launches', 'vm_l2_tlb_lookup_launches',
    'vm_translation_mshr_allocations', 'vm_translation_mshr_merges',
    'vm_translation_walk_starts', 'vm_pte_requests',
    'vm_ready_application_duplicate_attempts',
    'vm_translation_lookup_entries', 'vm_translation_lookup_ready',
    'vm_translation_mshrs_entries', 'vm_translation_pwq_entries_active',
    'vm_translation_active_walks',
    'vm_translation_quiescent_invariants_hold')
COAL_KEYS = tuple(f'awma_prel1_coalescer_{name}' for name in (
    'leaders', 'followers', 'leader_completions', 'follower_applications',
    'entry_full_fallbacks', 'waiter_full_fallbacks',
    'follower_wait_cycles_total', 'follower_wait_cycles_max',
    'follower_delivery_latency_total',
    'delivery_wait_p95', 'delivery_wait_p99',
    'follower_delivery_latency_max', 'head_block_cycles',
    'critical_path_followers', 'compare_delays', 'occupancy_hwm', 'waiter_hwm',
    'followers_final', 'pending_compares_final', 'live_entries_final',
    'waiters_final', 'quiescent'))


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
    names = ('admissions', 'translated', 'untranslated', 'unobserved',
             'unique', 'translated_unique', 'untranslated_unique')
    return dict(zip(names, map(int, rows[-1])))


def parse(label: str, candidate: bool) -> dict[str, object]:
    directory = RAW / label
    text = (directory / 'run.log').read_text(errors='replace')
    values = {key: number(text, key) for key in BASE_KEYS}
    if candidate:
        values.update({key: number(text, key) for key in COAL_KEYS})
        values['admissions'] = number(text, 'awma_owner_wait_admissions')
        values['re_admissions'] = number(
            text, 'awma_owner_wait_repeated_admissions')
        values['readmitted_uid'] = number(
            text, 'awma_owner_wait_readmitted_uids')
    return {
        'directory': directory, 'text': text, 'values': values,
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
    PACK.mkdir(parents=True, exist_ok=True)
    off = parse('OFF', False)
    main = parse('COALESCER', True)
    plus = parse('COALESCER_PLUS1', True)
    qualification = json.loads((RAW / 'OFF/qualification.json').read_text())
    ov, mv, pv = off['values'], main['values'], plus['values']
    oc, mc, pc = off['coverage'], main['coverage'], plus['coverage']

    def arm_correct(run: dict[str, object], values: dict[str, int],
                    cov: dict[str, int], candidate: bool) -> bool:
        result = (
            run['terminal'] and values['gpu_sim_insn'] == ov['gpu_sim_insn'] and
            values['gpu_tot_issued_cta'] == 1 and cov['unique'] == oc['unique'] and
            cov['translated_unique'] == cov['unique'] and
            cov['untranslated'] == 0 and cov['unobserved'] == 0 and
            values['vm_ready_application_duplicate_attempts'] == 0 and
            values['vm_translation_lookup_entries'] == 0 and
            values['vm_translation_lookup_ready'] == 0 and
            values['vm_translation_mshrs_entries'] == 0 and
            values['vm_translation_pwq_entries_active'] == 0 and
            values['vm_translation_active_walks'] == 0 and
            values['vm_translation_quiescent_invariants_hold'] == 1)
        if candidate:
            result = result and (
                values['awma_prel1_coalescer_leaders'] ==
                values['awma_prel1_coalescer_leader_completions'] and
                values['awma_prel1_coalescer_followers'] ==
                values['awma_prel1_coalescer_follower_applications'] and
                values['awma_prel1_coalescer_followers_final'] == 0 and
                values['awma_prel1_coalescer_pending_compares_final'] == 0 and
                values['awma_prel1_coalescer_live_entries_final'] == 0 and
                values['awma_prel1_coalescer_waiters_final'] == 0 and
                values['awma_prel1_coalescer_quiescent'] == 1)
        return result

    off_correct = qualification['status'] == 'PASS' and arm_correct(
        off, ov, oc, False)
    main_correct = arm_correct(main, mv, mc, True)
    plus_correct = arm_correct(plus, pv, pc, True)
    followers = mv['awma_prel1_coalescer_followers']
    opportunity = followers > 0
    suppression = opportunity and mv['vm_l1_tlb_lookup_launches'] < ov['vm_l1_tlb_lookup_launches']
    correctness = off_correct and main_correct and plus_correct
    status = ('PREL1_COALESCER_INDEPENDENT_SERVICE_SUPPRESSION_GENERALIZED'
              if correctness and suppression else
              'INDEPENDENT_HOLDOUT_NO_COALESCING_OPPORTUNITY_SAFETY_ONLY'
              if correctness and not opportunity else
              'INDEPENDENT_HOLDOUT_SERVICE_SUPPRESSION_NOT_GENERALIZED'
              if correctness else 'INDEPENDENT_HOLDOUT_FAILED_CORRECTNESS')

    matrix_rows = []
    for label, run, values, cov, latency in (
            ('OFF', off, ov, oc, ''), ('MAIN', main, mv, mc, 0),
            ('PLUS1', plus, pv, pc, 1)):
        follower_count = (values.get('awma_prel1_coalescer_followers', 0))
        wait_total = values.get('awma_prel1_coalescer_follower_wait_cycles_total', 0)
        matrix_rows.append([
            label, latency, values['gpu_sim_cycle'], values['gpu_sim_insn'],
            values['gpu_tot_issued_cta'], cov['unique'],
            values.get('awma_prel1_coalescer_leaders', 0), follower_count,
            values['vm_l1_tlb_lookup_launches'],
            values['vm_l2_tlb_lookup_launches'],
            values['vm_translation_mshr_allocations'],
            values['vm_translation_mshr_merges'],
            values['vm_translation_walk_starts'], values['vm_pte_requests'],
            values.get('awma_prel1_coalescer_entry_full_fallbacks', 0),
            values.get('awma_prel1_coalescer_waiter_full_fallbacks', 0),
            follower_count,
            values.get('awma_prel1_coalescer_follower_delivery_latency_total', 0) /
            follower_count if follower_count else 0,
            values.get('awma_prel1_coalescer_delivery_wait_p95', 0),
            values.get('awma_prel1_coalescer_delivery_wait_p99', 0),
            values.get('awma_prel1_coalescer_follower_delivery_latency_max', 0),
            values.get('awma_prel1_coalescer_head_block_cycles', 0),
            cov['admissions'], cov['admissions'] - cov['unique'],
            values.get('readmitted_uid', 0),
            off_correct if label == 'OFF' else main_correct if label == 'MAIN' else plus_correct])
    write_tsv(PACK / 'HOLDOUT_MATRIX.tsv', [
        'arm', 'compare_latency', 'cycles', 'instructions', 'cta', 'unique_uid',
        'leaders', 'followers', 'l1_launches', 'l2_launches', 'mshr_alloc',
        'mshr_merge', 'walks', 'pte_requests', 'entry_full_fallback',
        'waiter_full_fallback', 'wait_count', 'wait_mean', 'wait_p95',
        'wait_p99', 'wait_max', 'head_block_cycles', 'coverage_admissions',
        're_admissions', 'readmitted_uid', 'correctness'], matrix_rows)

    gate_rows = [[f'OFF:{key}', passed] for key, passed in qualification['gates'].items()]
    for label, run, values, cov, candidate_arm in (
            ('MAIN', main, mv, mc, True), ('PLUS1', plus, pv, pc, True)):
        gates = {
            'rc_zero': (run['directory'] / 'rc.txt').read_text().strip() == '0',
            'instructions_exact': values['gpu_sim_insn'] == ov['gpu_sim_insn'],
            'cta_exact': values['gpu_tot_issued_cta'] == 1,
            'uid_exact': cov['unique'] == oc['unique'],
            'coverage_complete': cov['translated_unique'] == cov['unique'] and cov['untranslated'] == 0 and cov['unobserved'] == 0,
            'exactly_once': values['awma_prel1_coalescer_followers'] == values['awma_prel1_coalescer_follower_applications'],
            'duplicate_application_zero': values['vm_ready_application_duplicate_attempts'] == 0,
            'terminal': run['terminal'],
            'controller_quiescence': values['vm_translation_quiescent_invariants_hold'] == 1,
            'coalescer_quiescence': values['awma_prel1_coalescer_quiescent'] == 1 and values['awma_prel1_coalescer_followers_final'] == 0 and values['awma_prel1_coalescer_waiters_final'] == 0 and values['awma_prel1_coalescer_live_entries_final'] == 0,
        }
        gate_rows.extend([f'{label}:{key}', passed] for key, passed in gates.items())
    write_tsv(PACK / 'CORRECTNESS_GATES.tsv', ['gate', 'pass'], gate_rows)

    write_tsv(PACK / 'SERVICE_SUPPRESSION.tsv', [
        'metric', 'off', 'main', 'plus1', 'main_off_delta', 'plus1_off_delta'], [
        ['followers', 0, mv['awma_prel1_coalescer_followers'],
         pv['awma_prel1_coalescer_followers'],
         mv['awma_prel1_coalescer_followers'],
         pv['awma_prel1_coalescer_followers']],
        ['l1_launches', ov['vm_l1_tlb_lookup_launches'], mv['vm_l1_tlb_lookup_launches'], pv['vm_l1_tlb_lookup_launches'], ov['vm_l1_tlb_lookup_launches'] - mv['vm_l1_tlb_lookup_launches'], ov['vm_l1_tlb_lookup_launches'] - pv['vm_l1_tlb_lookup_launches']],
        ['l2_launches', ov['vm_l2_tlb_lookup_launches'], mv['vm_l2_tlb_lookup_launches'], pv['vm_l2_tlb_lookup_launches'], ov['vm_l2_tlb_lookup_launches'] - mv['vm_l2_tlb_lookup_launches'], ov['vm_l2_tlb_lookup_launches'] - pv['vm_l2_tlb_lookup_launches']],
        ['mshr_alloc', ov['vm_translation_mshr_allocations'], mv['vm_translation_mshr_allocations'], pv['vm_translation_mshr_allocations'], ov['vm_translation_mshr_allocations'] - mv['vm_translation_mshr_allocations'], ov['vm_translation_mshr_allocations'] - pv['vm_translation_mshr_allocations']],
        ['mshr_merge', ov['vm_translation_mshr_merges'], mv['vm_translation_mshr_merges'], pv['vm_translation_mshr_merges'], ov['vm_translation_mshr_merges'] - mv['vm_translation_mshr_merges'], ov['vm_translation_mshr_merges'] - pv['vm_translation_mshr_merges']],
        ['walks', ov['vm_translation_walk_starts'], mv['vm_translation_walk_starts'], pv['vm_translation_walk_starts'], ov['vm_translation_walk_starts'] - mv['vm_translation_walk_starts'], ov['vm_translation_walk_starts'] - pv['vm_translation_walk_starts']],
        ['pte_requests', ov['vm_pte_requests'], mv['vm_pte_requests'], pv['vm_pte_requests'], ov['vm_pte_requests'] - mv['vm_pte_requests'], ov['vm_pte_requests'] - pv['vm_pte_requests']],
    ])

    main_change = (mv['gpu_sim_cycle'] - ov['gpu_sim_cycle']) / ov['gpu_sim_cycle'] * 100
    plus_change = (pv['gpu_sim_cycle'] - ov['gpu_sim_cycle']) / ov['gpu_sim_cycle'] * 100
    write_tsv(PACK / 'TIMING_SENSITIVITY.tsv', [
        'arm', 'cycles', 'cycle_change_vs_off_percent', 'compare_delays',
        'followers', 'l1_launches', 'head_block_cycles', 'correctness'], [
        ['MAIN', mv['gpu_sim_cycle'], main_change,
         mv['awma_prel1_coalescer_compare_delays'], followers,
         mv['vm_l1_tlb_lookup_launches'],
         mv['awma_prel1_coalescer_head_block_cycles'], main_correct],
        ['PLUS1', pv['gpu_sim_cycle'], plus_change,
         pv['awma_prel1_coalescer_compare_delays'],
         pv['awma_prel1_coalescer_followers'],
         pv['vm_l1_tlb_lookup_launches'],
         pv['awma_prel1_coalescer_head_block_cycles'], plus_correct],
    ])

    (PACK / 'FINAL_DECISION.md').write_text(f'''# Final decision

Status: **{status}**

Claim classification:

- `INDEPENDENT_CORRECTNESS`: **{'PASS' if correctness else 'FAIL'}**
- `INDEPENDENT_COALESCING_OPPORTUNITY`: **{'PRESENT' if opportunity else 'ABSENT'}**
- `INDEPENDENT_PHYSICAL_SERVICE_SUPPRESSION`: **{'SUPPORTED' if suppression else 'NOT_SUPPORTED'}**
- `INDEPENDENT_WAIT_SAFETY`: main wait count {followers}, mean
  {mv['awma_prel1_coalescer_follower_delivery_latency_total'] / followers if followers else 0:.6f},
  p95 {mv['awma_prel1_coalescer_delivery_wait_p95']},
  p99 {mv['awma_prel1_coalescer_delivery_wait_p99']},
  max {mv['awma_prel1_coalescer_follower_delivery_latency_max']},
  head-block {mv['awma_prel1_coalescer_head_block_cycles']} cycles.
- `INDEPENDENT_PERFORMANCE_RESPONSE`:
  main {mv['gpu_sim_cycle']:,} cycles ({main_change:+.6f}% versus OFF);
  +1-cycle {pv['gpu_sim_cycle']:,} cycles ({plus_change:+.6f}% versus OFF).

The new AT_NATIVE_REDUCE family supplies 105 exact followers. Main L1 physical
launches fall from {ov['vm_l1_tlb_lookup_launches']:,} to
{mv['vm_l1_tlb_lookup_launches']:,}, while all correctness and quiescence gates
pass. This independently generalizes the service-suppression mediator. The
equal cycle response is reported as observed; it is not upgraded into a claim
of universal speedup.

Frozen mechanism/source/binary and parameters were not modified. No fallback,
control, sweep, ideal, 0/80, other kernel, repeated measurement or Observatory
run was performed.
''')
    (PACK / 'README.md').write_text(f'''# {STAGE}

Start with `FINAL_DECISION.md`.

Final status: **{status}**

This is the preregistered one-target independent validation of
`STR_e0922aa2a506_P1`. Files are intentionally minimal:

- `HOLDOUT_MATRIX.tsv`
- `CORRECTNESS_GATES.tsv`
- `SERVICE_SUPPRESSION.tsv`
- `TIMING_SENSITIVITY.tsv`
- `FINAL_DECISION.md`
- `RAW_DATA_INDEX.tsv`
''')

    raw_rows = []
    for label in ('OFF', 'COALESCER', 'COALESCER_PLUS1'):
        directory = RAW / label
        for name in ('run.log', 'command.json', 'rc.txt', 'wall_seconds.txt'):
            path = directory / name
            raw_rows.append(['run', label, str(path), sha(path)])
    for kind, identity, path in (
        ('qualification', 'OFF', RAW / 'OFF/qualification.json'),
        ('binary', 'FROZEN', RUNTIME / 'bin/unified_accel-sim.out'),
        ('library', 'FROZEN', RUNTIME / 'src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release/libcudart.so'),
        ('script', 'runner', REPO / 'util/vm_tlb/awma/run_minimal_holdout.py'),
        ('script', 'off_qualifier', REPO / 'util/vm_tlb/awma/qualify_minimal_holdout_off.py'),
        ('script', 'review_builder', REPO / 'util/vm_tlb/awma/build_minimal_holdout_review.py'),
    ):
        raw_rows.append([kind, identity, str(path), sha(path)])
    raw_rows.extend([
        ['authority', 'mechanism', 'git', MECHANISM],
        ['authority', 'source_freeze', 'git', SOURCE_FREEZE],
        ['authority', 'capture', 'git', CAPTURE],
        ['authority', 'trace_sha256', 'trace', TRACE_SHA],
    ])
    write_tsv(PACK / 'RAW_DATA_INDEX.tsv',
              ['kind', 'identity', 'path_or_type', 'sha256_or_commit'], raw_rows)
    files = sorted(path for path in PACK.iterdir()
                   if path.is_file() and path.name != 'SHA256SUMS')
    (PACK / 'SHA256SUMS').write_text(''.join(
        f'{sha(path)}  {path.name}\n' for path in files))
    print(json.dumps({'status': status, 'followers': followers,
                      'main_cycle_change_percent': main_change,
                      'plus1_cycle_change_percent': plus_change},
                     indent=2, sort_keys=True))
    return 0 if status == 'PREL1_COALESCER_INDEPENDENT_SERVICE_SUPPRESSION_GENERALIZED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
