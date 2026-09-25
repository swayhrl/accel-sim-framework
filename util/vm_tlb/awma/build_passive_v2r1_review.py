#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

STAGE = 'AWMA_PASSIVE_LAST_TRANSLATION_RESULT_FORWARDING_V2R1_BASELINE_PRESERVING'
REPO = Path('/root/workspace/accel-sim-framework-awma-passive-last-translation-result-forwarding-v2r1')
RUNTIME = Path('/root/awma_passive_last_translation_result_forwarding_v2r1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_passive_last_translation_result_forwarding_v2r1/raw')
MIXED = Path('/root/share/mnt164/huangrulin/awma_passive_last_translation_result_forwarding_v2/raw')
PACK = REPO / 'docs/vm_tlb/review_packs' / STAGE
SOURCE_FREEZE = '47cde7d19393869ecae448bee76c3624f5907fb5'
RUNNER_BINDING = '4e3244a3fb67e60e94805d0be9c730c03eb2b2f9'
PREREG = 'd450b2a06a0af18960d81b0ccbb46d047fe6cbae'
BINARY_SHA = '84d4af7c3d4c94501261d62fff483b95625226508d80c1c3f5328cda3f527a83'

TARGETS = {
    'T0': ('PREFILL_FLASH', 527896, 368696302, 224, 3090304, 3090304),
    'T1': ('PREFILL_GEMM', 665802, 369131520, 384, 7159808, 7160265),
    'T2': ('DECODE_GEMV', 93079, 43357696, 1216, 411008, 715333),
    'SPLITKV': ('FLASH_FWD_SPLITKV', 73923, 36599648, 126, 233814, 233814),
    'COMBINE': ('FLASH_FWD_SPLITKV_COMBINE', 10480, 72908, 2, 1099, 1099),
    'A1': ('DECODE_GEMV_PAIR_A_S2_T2048', 114123, 34883072, 224, 409024, 2191027),
    'A2': ('DECODE_GEMV_PAIR_A_T8192', 117698, 34883072, 224, 409024, 2375939),
}

BASE_KEYS = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_translation_lookup_requests', 'vm_l1_tlb_accesses',
    'vm_l2_tlb_accesses', 'vm_translation_mshr_allocations',
    'vm_translation_mshr_merges', 'vm_translation_walk_starts',
    'vm_pte_requests', 'vm_functional_completed',
    'vm_ready_application_duplicate_attempts',
    'vm_translation_lookup_entries', 'vm_translation_lookup_ready',
    'vm_translation_mshrs_entries', 'vm_translation_pwq_entries_active',
    'vm_translation_active_walks',
    'vm_translation_quiescent_invariants_hold',
    'vm_passive_v2r1_detached_prelaunches',
    'vm_passive_v2r1_detached_lookup_completions',
    'vm_passive_v2r1_detached_mshr_completions',
    'vm_passive_v2r1_detach_without_live_work',
    'vm_passive_v2r1_detached_waiters_final',
)

ACCOUNTING_KEYS = (
    'awma_passive_v2r1_lookups', 'awma_passive_v2r1_hits',
    'awma_passive_v2r1_misses',
    'awma_passive_v2r1_head_requests_avoided',
    'awma_passive_v2r1_prelaunch_work_not_saved',
    'awma_passive_v2r1_forwards_without_live_prelaunch',
    'awma_passive_v2r1_prelaunch_attempts',
    'awma_passive_v2r1_prelaunch_head_attempts',
    'awma_passive_v2r1_prelaunch_lookup_request_increments',
    'awma_passive_v2r1_head_translation_attempts',
    'awma_passive_v2r1_natural_completions',
    'awma_passive_v2r1_forwarded_applications',
    'awma_passive_v2r1_live_entries',
    'awma_passive_v2r1_ppn_consistency_faults',
    'awma_passive_v2r1_proactive_owner_attempts',
    'awma_passive_v2r1_proactive_duplicate_lookups',
)

OWNER_KEYS = (
    'awma_owner_wait_admissions', 'awma_owner_wait_repeated_admissions',
    'awma_owner_wait_readmitted_uids',
    'awma_owner_wait_member_owner_wait_cycles',
    'awma_owner_wait_head_block_total_cycles',
)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def number(text: str, key: str) -> int:
    values = re.findall(rf'^{re.escape(key)}\s*=\s*(\d+)\s*$', text, re.M)
    if not values:
        raise RuntimeError(f'missing {key}')
    return int(values[-1])


def compact(text: str, key: str) -> int:
    values = re.findall(rf'^{re.escape(key)}=(\d+)\s*$', text, re.M)
    if not values:
        raise RuntimeError(f'missing {key}')
    return int(values[-1])


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


def run_dir(target: str, candidate: bool) -> Path:
    label = 'PASSIVE_V2R1' if candidate else 'OFF'
    return DURABLE / f'{target}_{label}_10_80'


def parse(target: str, candidate: bool) -> dict[str, object]:
    directory = run_dir(target, candidate)
    text = (directory / 'run.log').read_text(errors='replace')
    command = json.loads((directory / 'command.json').read_text())
    values = {key: number(text, key) for key in BASE_KEYS + ACCOUNTING_KEYS}
    owners = {key: number(text, key) for key in OWNER_KEYS} if candidate else {}
    cov = coverage(text)
    modes = re.findall(r'^vm_awma_candidate_mode = (\S+)$', text, re.M)
    return {
        'target': target, 'candidate': candidate, 'dir': directory,
        'text': text, 'command': command, 'values': values, 'owners': owners,
        'coverage': cov,
        'icnt': compact(text, 'icnt_total_pkts_simt_to_mem'),
        'mode': modes[-1] if modes else 'none',
        'terminal': ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                     'GPGPU-Sim: *** exit detected ***' in text),
        'log_sha': sha(directory / 'run.log'),
        'command_sha': sha(directory / 'command.json'),
        'wall': float((directory / 'wall_seconds.txt').read_text()),
    }


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)


def pct(value: float) -> str:
    return f'{value * 100:.6f}'


def main() -> int:
    PACK.mkdir(parents=True, exist_ok=True)
    gate = json.loads((RUNTIME / 'full_pipeline_gate.json').read_text())
    off_authority = json.loads((RUNTIME / 'v2r1_off_authority.json').read_text())
    assert gate['status'] == 'PASS'
    assert all(row['status'] == 'PASS' for row in off_authority['targets'].values())
    parsed = {target: (parse(target, False), parse(target, True))
              for target in TARGETS}

    gate_rows = []
    for key, exact in gate['exact'].items():
        gate_rows.append([key, gate['off']['values'][key],
                          gate['candidate']['values'][key], exact])
    for key, passed in gate['correctness'].items():
        gate_rows.append([key, '', '', passed])
    write_tsv(PACK / 'FULL_PIPELINE_ZERO_OPPORTUNITY.tsv',
              ['metric_or_gate', 'off', 'v2r1', 'pass'], gate_rows)

    development, prelaunch, physical, correctness = [], [], [], []
    all_correct = True
    regressions = []
    suppressions = []
    for target, (off, cand) in parsed.items():
        ov, cv = off['values'], cand['values']
        oc, cc = off['coverage'], cand['coverage']
        family, expected_cycles, expected_insn, expected_cta, expected_uid, expected_adm = TARGETS[target]
        speedup = (ov['gpu_sim_cycle'] - cv['gpu_sim_cycle']) / ov['gpu_sim_cycle']
        lookup_delta = ov['vm_translation_lookup_requests'] - cv['vm_translation_lookup_requests']
        lookup_fraction = lookup_delta / ov['vm_translation_lookup_requests']
        if speedup < -0.01:
            regressions.append(target)
        suppressions.append(abs(lookup_fraction))
        gates = {
            'rc_zero': (cand['dir'] / 'rc.txt').read_text().strip() == '0',
            'mode_exact': cand['mode'] == 'passive_last_result',
            'binary_exact': cand['command']['binary_sha256'] == BINARY_SHA,
            'cycles_off_authority': ov['gpu_sim_cycle'] == expected_cycles,
            'instructions_exact': (ov['gpu_sim_insn'] == cv['gpu_sim_insn'] == expected_insn),
            'cta_exact': (ov['gpu_tot_issued_cta'] == cv['gpu_tot_issued_cta'] == expected_cta),
            'unique_uid_exact': (oc['unique'] == cc['unique'] == expected_uid),
            'candidate_coverage_complete': (cc['untranslated'] == 0 and cc['unobserved'] == 0 and cc['translated_unique'] == cc['unique']),
            'duplicate_application_zero': cv['vm_ready_application_duplicate_attempts'] == 0,
            'terminal': cand['terminal'],
            'controller_quiescence': (cv['vm_translation_lookup_entries'] == 0 and cv['vm_translation_lookup_ready'] == 0 and cv['vm_translation_mshrs_entries'] == 0 and cv['vm_translation_pwq_entries_active'] == 0 and cv['vm_translation_active_walks'] == 0 and cv['vm_translation_quiescent_invariants_hold'] == 1),
            'memo_quiescence': cv['awma_passive_v2r1_live_entries'] == 0,
            'detached_quiescence': cv['vm_passive_v2r1_detached_waiters_final'] == 0,
            'hit_application_conservation': (cv['awma_passive_v2r1_hits'] == cv['awma_passive_v2r1_forwarded_applications'] == cv['awma_passive_v2r1_head_requests_avoided']),
            'prelaunch_not_saved_conservation': (cv['awma_passive_v2r1_hits'] == cv['awma_passive_v2r1_prelaunch_work_not_saved'] == cv['vm_passive_v2r1_detached_prelaunches'] == cv['vm_passive_v2r1_detached_lookup_completions'] + cv['vm_passive_v2r1_detached_mshr_completions']),
            'zero_forward_without_live_prelaunch': cv['awma_passive_v2r1_forwards_without_live_prelaunch'] == 0,
            'ppn_consistency': cv['awma_passive_v2r1_ppn_consistency_faults'] == 0,
            'zero_proactive_owner': cv['awma_passive_v2r1_proactive_owner_attempts'] == 0,
            'zero_proactive_duplicate': cv['awma_passive_v2r1_proactive_duplicate_lookups'] == 0,
            'zero_owner_wait': cand['owners']['awma_owner_wait_member_owner_wait_cycles'] == 0,
            'zero_head_block': cand['owners']['awma_owner_wait_head_block_total_cycles'] == 0,
        }
        all_correct &= all(gates.values())
        development.append([
            target, family, ov['gpu_sim_cycle'], cv['gpu_sim_cycle'],
            pct(speedup), cv['awma_passive_v2r1_hits'],
            ov['vm_translation_lookup_requests'], cv['vm_translation_lookup_requests'],
            lookup_delta, pct(lookup_fraction), ov['vm_l1_tlb_accesses'],
            cv['vm_l1_tlb_accesses'], ov['vm_l2_tlb_accesses'],
            cv['vm_l2_tlb_accesses'], ov['vm_translation_mshr_allocations'],
            cv['vm_translation_mshr_allocations'], ov['vm_translation_mshr_merges'],
            cv['vm_translation_mshr_merges'], ov['vm_translation_walk_starts'],
            cv['vm_translation_walk_starts'], ov['vm_pte_requests'],
            cv['vm_pte_requests'], oc['admissions'], cc['admissions'],
            cc['admissions'] - cc['unique'],
            cand['owners']['awma_owner_wait_readmitted_uids'],
            'PASS' if all(gates.values()) else 'FAIL'])
        prelaunch.append([
            target, off['values']['awma_passive_v2r1_prelaunch_attempts'],
            cv['awma_passive_v2r1_prelaunch_attempts'],
            off['values']['awma_passive_v2r1_head_translation_attempts'],
            cv['awma_passive_v2r1_head_translation_attempts'],
            cv['awma_passive_v2r1_hits'],
            cv['awma_passive_v2r1_head_requests_avoided'],
            cv['awma_passive_v2r1_prelaunch_work_not_saved'],
            cv['awma_passive_v2r1_forwards_without_live_prelaunch'],
            cv['vm_passive_v2r1_detached_lookup_completions'],
            cv['vm_passive_v2r1_detached_mshr_completions']])
        physical.append([
            target, cv['awma_passive_v2r1_hits'],
            cv['awma_passive_v2r1_head_requests_avoided'],
            cv['awma_passive_v2r1_prelaunch_work_not_saved'],
            ov['vm_translation_lookup_requests'], cv['vm_translation_lookup_requests'],
            lookup_delta, pct(lookup_fraction),
            'DERIVED_OFF_MINUS_V2R1_NOT_EQUATED_TO_HITS'])
        for gate_name, passed in gates.items():
            correctness.append([target, gate_name, passed])

    write_tsv(PACK / 'V2R1_DEVELOPMENT_MATRIX.tsv', [
        'target', 'family', 'off_cycles', 'v2r1_cycles', 'speedup_percent',
        'forward_hits', 'off_lookup_requests', 'v2r1_lookup_requests',
        'lookup_delta_off_minus_v2r1', 'lookup_delta_percent',
        'off_l1_probes', 'v2r1_l1_probes', 'off_l2_probes', 'v2r1_l2_probes',
        'off_mshr_alloc', 'v2r1_mshr_alloc', 'off_mshr_merge', 'v2r1_mshr_merge',
        'off_walk_starts', 'v2r1_walk_starts', 'off_pte_requests',
        'v2r1_pte_requests', 'off_coverage_admissions',
        'v2r1_coverage_admissions', 'v2r1_repeated_admissions',
        'v2r1_readmitted_uid', 'correctness'], development)
    write_tsv(PACK / 'PRELAUNCH_VS_HEAD_ACCOUNTING.tsv', [
        'target', 'off_prelaunch_attempts', 'v2r1_prelaunch_attempts',
        'off_head_translation_attempts', 'v2r1_head_translation_attempts',
        'A_forward_hits', 'B_head_requests_avoided',
        'C_prelaunch_work_already_issued_not_saved',
        'forward_without_live_prelaunch', 'detached_lookup_completions',
        'detached_mshr_completions'], prelaunch)
    write_tsv(PACK / 'PHYSICAL_LOOKUP_ACCOUNTING.tsv', [
        'target', 'A_forward_hits', 'B_head_requests_avoided',
        'C_prelaunch_work_already_issued_not_saved', 'off_physical_lookup_requests',
        'v2r1_physical_lookup_requests', 'D_total_physical_lookup_delta',
        'D_delta_percent', 'interpretation'], physical)
    write_tsv(PACK / 'CORRECTNESS_GATES.tsv',
              ['target', 'gate', 'pass'], correctness)

    a2_off, a2 = parsed['A2']
    mixed_log = (MIXED / 'A2_PASSIVE_V2_10_80/run.log').read_text(errors='replace')
    mixed_cov = coverage(mixed_log)
    mixed_cycles = number(mixed_log, 'gpu_sim_cycle')
    mixed_lookup = number(mixed_log, 'vm_translation_lookup_requests')
    mixed_hits = number(mixed_log, 'awma_passive_v2_hits')
    write_tsv(PACK / 'A2_V2_V2R1_COMPARISON.tsv', [
        'arm', 'evidence_class', 'cycles', 'speedup_vs_off_percent',
        'forward_hits', 'physical_lookup_requests', 'coverage_admissions',
        'admission_delta_vs_off', 'proactive_owner_attempts'], [
        ['OFF', 'FROZEN_V1', a2_off['values']['gpu_sim_cycle'], '0.000000', 0,
         a2_off['values']['vm_translation_lookup_requests'],
         a2_off['coverage']['admissions'], 0, 0],
        ['MIXED_V2', 'MIXED_INTERVENTION_DIAGNOSTIC', mixed_cycles,
         pct((a2_off['values']['gpu_sim_cycle'] - mixed_cycles) /
             a2_off['values']['gpu_sim_cycle']), mixed_hits, mixed_lookup,
         mixed_cov['admissions'], mixed_cov['admissions'] - a2_off['coverage']['admissions'], 0],
        ['V2R1', 'BASELINE_PRESERVING_DEVELOPMENT', a2['values']['gpu_sim_cycle'],
         pct((a2_off['values']['gpu_sim_cycle'] - a2['values']['gpu_sim_cycle']) /
             a2_off['values']['gpu_sim_cycle']),
         a2['values']['awma_passive_v2r1_hits'],
         a2['values']['vm_translation_lookup_requests'],
         a2['coverage']['admissions'],
         a2['coverage']['admissions'] - a2_off['coverage']['admissions'], 0],
    ])

    source_rows = [
        ['source_freeze_commit', 'FRAMEWORK', SOURCE_FREEZE, 'FROZEN_BEFORE_PERFORMANCE'],
        ['runner_binding_commit', 'FRAMEWORK', RUNNER_BINDING, 'FROZEN_BEFORE_PERFORMANCE'],
        ['holdout_preregistration_commit', 'FUTURE_HOLDOUT', PREREG, 'UNCHANGED_NOT_RUN'],
        ['binary', str(RUNTIME / 'bin/unified_accel-sim.out'), BINARY_SHA, 'FROZEN'],
    ]
    for name in ('passive_last_translation_forwarding.h',
                 'passive_last_translation_forwarding.cc', 'shader.cc',
                 'vm_translation.h', 'vm_translation.cc'):
        path = RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim' / name
        source_rows.append(['source', str(path), sha(path), 'FROZEN'])
    write_tsv(PACK / 'SOURCE_FREEZE.tsv',
              ['kind', 'path_or_identity', 'sha256_or_commit', 'status'], source_rows)

    raw = []
    for target in TARGETS:
        for candidate in (False, True):
            arm = 'V2R1' if candidate else 'OFF'
            directory = run_dir(target, candidate)
            for name in ('run.log', 'command.json', 'rc.txt', 'wall_seconds.txt'):
                path = directory / name
                raw.append(['development', target, arm, str(path), sha(path)])
    for arm in ('OFF', 'PASSIVE_V2R1'):
        directory = DURABLE / f'ZERO_M1_{arm}_10_80'
        for name in ('run.log', 'command.json', 'rc.txt', 'wall_seconds.txt'):
            path = directory / name
            raw.append(['full_pipeline_gate', 'ZERO_M1', arm, str(path), sha(path)])
    for kind, identity, path in (
        ('authority', 'gate_receipt', RUNTIME / 'full_pipeline_gate.json'),
        ('authority', 'off_authority', RUNTIME / 'v2r1_off_authority.json'),
        ('audit', 'frontend', RUNTIME / 'frontend_source_audit.json'),
        ('build', 'unified', RUNTIME / 'unified_build.log'),
        ('test', 'directed', RUNTIME / 'tests/passive_last_translation_forwarding_test.log'),
    ):
        raw.append([kind, identity, '', str(path), sha(path)])
    for identity, name in (
        ('runner', 'run_passive_v2r1_matrix.py'),
        ('off_qualifier', 'qualify_passive_v2r1_off.py'),
        ('gate_verifier', 'verify_passive_v2r1_full_pipeline_gate.py'),
        ('frontend_auditor', 'audit_passive_v2r1_frontend.py'),
        ('review_builder', 'build_passive_v2r1_review.py'),
        ('directed_test_source', 'passive_last_translation_forwarding_test.cc'),
    ):
        path = REPO / 'util/vm_tlb/awma' / name
        raw.append(['provenance', identity, '', str(path), sha(path)])
    raw.extend([
        ['commit', 'source_freeze', '', 'git', SOURCE_FREEZE],
        ['commit', 'runner_binding', '', 'git', RUNNER_BINDING],
        ['commit', 'future_holdout_preregistration', '', 'git', PREREG],
        ['commit', 'mixed_v2_authority', '', 'git',
         '8497fa5b7688ab6fe55aa90f4d13c5e4d6364331'],
    ])
    write_tsv(PACK / 'RAW_DATA_INDEX.tsv',
              ['kind', 'target_or_identity', 'arm', 'path', 'sha256'], raw)

    max_abs_suppression = max(suppressions)
    decision = 'PASSIVE_FORWARDING_OPPORTUNITY_ALREADY_PRELAUNCHED'
    report_rows = '\n'.join(
        f'| {r[0]} | {int(r[2]):,} | {int(r[3]):,} | {r[4]}% | '
        f'{int(r[5]):,} | {int(r[8]):,} ({r[9]}%) |'
        for r in development)
    (PACK / 'REPORT.md').write_text(f'''# Passive last-result forwarding V2R1

Status: **COMPLETE / {decision}**

V2R1 restores the frozen V1 resident-access prelaunch traversal and keeps the
one-entry instruction-local forwarding rule unchanged. All correctness gates
and the real full-pipeline zero-opportunity exact gate pass.

| target | OFF cycles | V2R1 cycles | speedup | forward hits | physical lookup delta |
|---|---:|---:|---:|---:|---:|
{report_rows}

The decisive accounting result is that every one of the
{sum(int(r[5]) for r in development):,} forwarding hits occurred after real
resident-prelaunch work had already been admitted. The number of hits is
therefore not physical-service suppression. Total lookup-request changes are
only -1,483 to +2,287 requests across targets (OFF-minus-V2R1 convention), and
the largest absolute fraction is {max_abs_suppression * 100:.6f}%. Some points
increase physical requests. This supports the preregistered negative outcome:
the passive opportunity observed at the head is already prelaunched by frozen
V1.

Cycle responses are retained as development evidence but are not attributed
to translation-service elimination. T0/T1 improve by 1.715%/1.323%; A1
regresses by 2.252%; these responses accompany scheduling/admission changes
while physical lookup service is essentially conserved. The stage therefore
does not advance to independent holdout.

A2 is 117,698 cycles OFF, 112,145 cycles in mixed V2 (diagnostic only), and
115,860 cycles in V2R1. V2R1 retains 116,032 forward hits but changes lookup
requests from 545,916 to 545,932 and reduces admissions versus OFF rather than
reintroducing the old proactive-owner +1.1M amplification. The mixed-V2
+4.718% result is not passive-only evidence.

The future holdout preregistration `{PREREG}` remains unchanged. Neither
`STR_e0922aa2a506` nor `STR_48b98b28a393` was captured or run.
''')
    (PACK / 'README.md').write_text(f'''# {STAGE}

Start with `REPORT.md`.

Decision: **{decision}**.

Evidence map:

- `BASELINE_FRONTEND_SOURCE_AUDIT.md`: frozen-V1 restoration audit;
- `FULL_PIPELINE_ZERO_OPPORTUNITY.tsv`: exact real-simulator gate;
- `V2R1_DEVELOPMENT_MATRIX.tsv`: seven development points;
- `PRELAUNCH_VS_HEAD_ACCOUNTING.tsv`: A/B/C accounting;
- `PHYSICAL_LOOKUP_ACCOUNTING.tsv`: comparative physical delta D;
- `A2_V2_V2R1_COMPARISON.tsv`: OFF/mixed/V2R1 comparison;
- `CORRECTNESS_GATES.tsv`, `SOURCE_FREEZE.tsv`, `RAW_DATA_INDEX.tsv`:
  correctness and provenance closure.
''')

    files = sorted(path for path in PACK.iterdir()
                   if path.is_file() and path.name != 'SHA256SUMS')
    (PACK / 'SHA256SUMS').write_text(''.join(
        f'{sha(path)}  {path.name}\n' for path in files))
    print(json.dumps({
        'status': 'PASS' if all_correct else 'FAIL',
        'decision': decision,
        'regressions_over_one_percent': regressions,
        'max_absolute_lookup_delta_fraction': max_abs_suppression,
    }, indent=2, sort_keys=True))
    return 0 if all_correct else 1


if __name__ == '__main__':
    raise SystemExit(main())
