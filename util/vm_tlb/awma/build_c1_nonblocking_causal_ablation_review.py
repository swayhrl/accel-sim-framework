#!/usr/bin/env python3
from __future__ import annotations

import csv
import difflib
import hashlib
import json
import re
import subprocess
from pathlib import Path

STAGE = 'AWMA_C1_NONBLOCKING_SHARING_CAUSAL_ABLATION_V1'
REPO = Path('/root/workspace/accel-sim-framework-awma-c1-nonblocking-sharing-causal-ablation-v1')
RUNTIME = Path('/root/awma_c1_nonblocking_sharing_causal_ablation_v1_runtime')
FROZEN_RUNTIME = Path('/root/awma_c1_nonblocking_opportunistic_sharing_v1_runtime')
CONTROL_RAW = Path('/root/share/mnt164/huangrulin/awma_c1_nonblocking_sharing_causal_ablation_v1/raw')
FROZEN_RAW = Path('/root/share/mnt164/huangrulin/awma_c1_nonblocking_opportunistic_sharing_v1/raw')
PACK = REPO / 'docs/vm_tlb/review_packs' / STAGE
RUNNER = REPO / 'util/vm_tlb/awma/run_c1_nonblocking_owner_only_control.py'
BUILDER = REPO / 'util/vm_tlb/awma/build_c1_nonblocking_causal_ablation_review.py'
TEST_SOURCE = REPO / 'util/vm_tlb/awma/awma_c1_nonblocking_causal_ablation_test.cc'
DIAGNOSTIC_BINARY = RUNTIME / 'bin/unified_accel-sim.out'
FROZEN_BINARY = FROZEN_RUNTIME / 'bin/unified_accel-sim.out'

TARGETS = {
    'T0': {
        'off_cycles': 527896, 'off_lookup': 21236866,
        'off_l1': 3101682, 'off_l2': 67140,
        'insn': 368696302, 'cta': 224, 'uid': 3090304,
        'off_log': Path('/root/share/mnt164/huangrulin/awma_literature_guided_mechanism_exploration_v1/raw/T0_none_10_80/run.log'),
    },
    'T1': {
        'off_cycles': 665802, 'off_lookup': 60930667,
        'off_l1': 7169938, 'off_l2': 120026,
        'insn': 369131520, 'cta': 384, 'uid': 7159808,
        'off_log': Path('/root/share/mnt164/huangrulin/awma_literature_guided_mechanism_exploration_v1/raw/T1_none_10_80/run.log'),
    },
    'T2': {
        'off_cycles': 93079, 'off_lookup': 549207,
        'off_l1': 412391, 'off_l2': 2327,
        'insn': 43357696, 'cta': 1216, 'uid': 411008,
        'off_log': Path('/root/share/mnt164/huangrulin/awma_literature_guided_mechanism_exploration_v1/raw/T2_none_10_80/run.log'),
    },
    'SPLITKV': {
        'off_cycles': 73923, 'off_lookup': 1997336,
        'off_l1': 236746, 'off_l2': 6076,
        'insn': 36599648, 'cta': 126, 'uid': 233814,
        'off_log': Path('/root/awma_existing_rep_suite_trace_requalification_v1_runtime/SPLITKV_V1_10_80/run.log'),
    },
    'COMBINE': {
        'off_cycles': 10480, 'off_lookup': 9228,
        'off_l1': 1139, 'off_l2': 40,
        'insn': 72908, 'cta': 2, 'uid': 1099,
        'off_log': Path('/root/awma_existing_rep_suite_trace_requalification_v1_runtime/COMBINE_V1_10_80/run.log'),
    },
}

COMMON_KEYS = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_translation_lookup_requests', 'vm_l1_tlb_accesses',
    'vm_l2_tlb_accesses', 'vm_translation_mshr_merges',
    'vm_ready_application_duplicate_attempts',
    'vm_translation_lookup_entries', 'vm_translation_lookup_ready',
    'vm_translation_mshrs_entries', 'vm_translation_pwq_entries_active',
    'vm_translation_active_walks',
    'vm_translation_quiescent_invariants_hold',
    'vm_awma_same_page_share_owner_ready',
    'vm_awma_same_page_share_deliveries',
    'awma_owner_wait_admissions', 'awma_owner_wait_unique_admitted_uids',
    'awma_owner_wait_repeated_admissions', 'awma_owner_wait_readmitted_uids',
    'awma_owner_wait_owner_attempts', 'awma_owner_wait_owner_retry_attempts',
    'awma_owner_wait_member_owner_wait_cycles',
    'awma_owner_wait_head_block_total_cycles',
    'awma_owner_wait_pending_members_final',
    'awma_owner_wait_first_issue_latency_total',
    'awma_owner_wait_first_issue_latency_max',
    'awma_owner_wait_all_issue_latency_total',
    'awma_owner_wait_all_issue_latency_max',
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

T2_MATCH_KEYS = (
    'gpu_sim_cycle', 'vm_translation_lookup_requests',
    'vm_l1_tlb_accesses', 'vm_l2_tlb_accesses',
    'vm_translation_mshr_merges', 'vm_awma_same_page_share_owner_ready',
    'vm_awma_same_page_share_deliveries',
    'awma_owner_wait_admissions', 'awma_owner_wait_repeated_admissions',
    'awma_owner_wait_readmitted_uids', 'awma_owner_wait_owner_attempts',
    'awma_owner_wait_owner_retry_attempts',
    'awma_owner_wait_member_owner_wait_cycles',
    'awma_owner_wait_head_block_total_cycles',
    'awma_owner_wait_first_issue_latency_total',
    'awma_owner_wait_first_issue_latency_max',
    'awma_owner_wait_all_issue_latency_total',
    'awma_owner_wait_all_issue_latency_max',
    'awma_nonblocking_shared_ready_members',
    'awma_nonblocking_fallback_members',
    'awma_nonblocking_duplicate_physical_lookup_requests',
    'awma_nonblocking_fallback_translation_completions',
    'awma_nonblocking_fallback_service_l1',
    'awma_nonblocking_fallback_service_l2',
    'awma_nonblocking_fallback_service_mshr_merge',
    'awma_nonblocking_fallback_service_ptw',
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


def directory(target: str, control: bool) -> Path:
    if control:
        return CONTROL_RAW / f'{target}_OWNER_ONLY_NO_SHARE_10_80'
    return FROZEN_RAW / f'{target}_NONBLOCKING_SHARE_10_80'


def parse_run(target: str, control: bool) -> dict[str, object]:
    run = directory(target, control)
    text = (run / 'run.log').read_text(errors='replace')
    command = json.loads((run / 'command.json').read_text())
    numbers = {key: last_number(text, key) for key in COMMON_KEYS}
    if control:
        numbers['awma_nonblocking_owner_only_no_share_control'] = \
            last_number(text, 'awma_nonblocking_owner_only_no_share_control')
    cov = coverage(text)
    modes = re.findall(r'^vm_awma_candidate_mode = (\S+)$', text, re.M)
    expected = TARGETS[target]
    fallback_service_total = sum(numbers[key] for key in (
        'awma_nonblocking_fallback_service_l1',
        'awma_nonblocking_fallback_service_l2',
        'awma_nonblocking_fallback_service_mshr_merge',
        'awma_nonblocking_fallback_service_ptw',
        'awma_nonblocking_fallback_service_unobserved'))
    env = command['environment']
    gates = {
        'rc_zero': (run / 'rc.txt').read_text().strip() == '0',
        'terminal': ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                     'GPGPU-Sim: *** exit detected ***' in text),
        'candidate_mode': bool(modes) and modes[-1] ==
            'nonblocking_opportunistic_share',
        'control_env': (not control) or
            env.get('GPGPUSIM_AWMA_NONBLOCKING_CAUSAL_ABLATION') ==
            'owner_only_no_share',
        'control_flag': (not control) or
            numbers['awma_nonblocking_owner_only_no_share_control'] == 1,
        'control_ready_share_zero': (not control) or
            (numbers['awma_nonblocking_shared_ready_members'] == 0 and
             numbers['vm_awma_same_page_share_deliveries'] == 0),
        'no_threshold_env': 'GPGPUSIM_AWMA_SHARE_MIN_COHORT_SIZE' not in env,
        'no_other_ablation': 'GPGPUSIM_AWMA_SHARE_ABLATION' not in env,
        'instructions_exact': numbers['gpu_sim_insn'] == expected['insn'],
        'cta_exact': numbers['gpu_tot_issued_cta'] == expected['cta'],
        'unique_uid_exact': cov['unique'] == expected['uid'],
        'translated_unique_exact': cov['translated_unique'] == expected['uid'],
        'untranslated_zero': cov['untranslated'] == 0,
        'unobserved_zero': cov['unobserved'] == 0,
        'duplicate_application_zero':
            numbers['vm_ready_application_duplicate_attempts'] == 0,
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
        'owner_wait_zero':
            numbers['awma_owner_wait_member_owner_wait_cycles'] == 0,
        'head_block_zero':
            numbers['awma_owner_wait_head_block_total_cycles'] == 0,
    }
    return {
        'target': target, 'kind': 'control' if control else 'candidate',
        'run_dir': str(run), 'numbers': numbers, 'coverage': cov,
        'command': command, 'gates': gates, 'correctness': all(gates.values()),
        'run_log_sha256': sha(run / 'run.log'),
        'command_sha256': sha(run / 'command.json'),
        'wall_seconds': float((run / 'wall_seconds.txt').read_text()),
    }


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)


def diagnostic_patch() -> Path:
    relative = 'src/gpgpu-sim/shader.cc'
    old = FROZEN_RUNTIME / 'src/gpgpu-sim' / relative
    new = RUNTIME / 'src/gpgpu-sim' / relative
    output = PACK / 'DIAGNOSTIC_CORE.patch'
    output.write_text(''.join(difflib.unified_diff(
        old.read_text().splitlines(keepends=True),
        new.read_text().splitlines(keepends=True),
        fromfile=f'a/{relative}', tofile=f'b/{relative}')))
    dry_run = subprocess.run(
        ['patch', '--dry-run', '-p1', '-d',
         str(FROZEN_RUNTIME / 'src/gpgpu-sim')],
        input=output.read_text(), text=True, capture_output=True, check=False)
    log = RUNTIME / 'tests/diagnostic_core_patch_dry_run.log'
    log.write_text(dry_run.stdout + dry_run.stderr +
                   f'rc={dry_run.returncode}\n')
    if dry_run.returncode != 0:
        raise RuntimeError('diagnostic patch dry-run failed')
    return output


def main() -> int:
    PACK.mkdir(parents=True, exist_ok=True)
    patch = diagnostic_patch()
    controls = {target: parse_run(target, True) for target in TARGETS}
    candidates = {target: parse_run(target, False) for target in TARGETS}
    rows: list[list[object]] = []
    gate_rows: list[list[object]] = []
    raw_rows: list[list[object]] = []
    summaries: dict[str, dict[str, object]] = {}

    for target, expected in TARGETS.items():
        control, candidate = controls[target], candidates[target]
        cn, fn = control['numbers'], candidate['numbers']
        candidate_minus_owner = fn['gpu_sim_cycle'] - cn['gpu_sim_cycle']
        candidate_vs_owner = candidate_minus_owner / cn['gpu_sim_cycle']
        owner_vs_off = (cn['gpu_sim_cycle'] - expected['off_cycles']) / expected['off_cycles']
        candidate_vs_off = (fn['gpu_sim_cycle'] - expected['off_cycles']) / expected['off_cycles']
        rows.append([
            target, expected['off_cycles'], cn['gpu_sim_cycle'],
            fn['gpu_sim_cycle'], f'{owner_vs_off:.9f}',
            f'{candidate_vs_off:.9f}', candidate_minus_owner,
            f'{candidate_vs_owner:.9f}', expected['off_lookup'],
            cn['vm_translation_lookup_requests'],
            fn['vm_translation_lookup_requests'],
            fn['vm_translation_lookup_requests'] -
                cn['vm_translation_lookup_requests'],
            cn['awma_nonblocking_shared_ready_members'],
            fn['awma_nonblocking_shared_ready_members'],
            cn['awma_nonblocking_fallback_members'],
            fn['awma_nonblocking_fallback_members'],
            cn['awma_nonblocking_duplicate_physical_lookup_requests'],
            fn['awma_nonblocking_duplicate_physical_lookup_requests'],
            cn['awma_owner_wait_owner_attempts'],
            fn['awma_owner_wait_owner_attempts'],
            cn['vm_translation_mshr_merges'],
            fn['vm_translation_mshr_merges'],
            cn['awma_owner_wait_admissions'],
            fn['awma_owner_wait_admissions'],
            cn['awma_owner_wait_repeated_admissions'],
            fn['awma_owner_wait_repeated_admissions'],
            cn['awma_owner_wait_readmitted_uids'],
            fn['awma_owner_wait_readmitted_uids'],
            cn['awma_owner_wait_first_issue_latency_total'],
            fn['awma_owner_wait_first_issue_latency_total'],
            cn['awma_owner_wait_all_issue_latency_total'],
            fn['awma_owner_wait_all_issue_latency_total'],
            cn['vm_l1_tlb_accesses'], fn['vm_l1_tlb_accesses'],
            cn['vm_l2_tlb_accesses'], fn['vm_l2_tlb_accesses'],
            'PASS' if control['correctness'] else 'FAIL',
            control['run_log_sha256'], candidate['run_log_sha256'],
        ])
        gate_rows.append([target] +
                         ['PASS' if value else 'FAIL'
                          for value in control['gates'].values()] +
                         ['PASS' if control['correctness'] else 'FAIL'])
        summaries[target] = {
            'off_cycles': expected['off_cycles'],
            'owner_only_cycles': cn['gpu_sim_cycle'],
            'candidate_cycles': fn['gpu_sim_cycle'],
            'candidate_minus_owner_cycles': candidate_minus_owner,
            'candidate_vs_owner_cycle_change': candidate_vs_owner,
            'owner_only_ready_share':
                cn['awma_nonblocking_shared_ready_members'],
            'candidate_ready_share':
                fn['awma_nonblocking_shared_ready_members'],
        }
        raw_rows.extend([
            ['control_run_log', target, f"{control['run_dir']}/run.log",
             control['run_log_sha256'], 'NEW_RUN'],
            ['control_command', target, f"{control['run_dir']}/command.json",
             control['command_sha256'], 'PROVENANCE'],
            ['frozen_candidate_run_log', target,
             f"{candidate['run_dir']}/run.log", candidate['run_log_sha256'],
             'ACCEPTED_REUSED_NO_RERUN'],
            ['accepted_off_run_log', target, str(expected['off_log']),
             sha(expected['off_log']), 'ACCEPTED_REUSED_NO_RERUN'],
        ])

    all_control_correct = all(bool(run['correctness'])
                              for run in controls.values())
    control_ready_zero = all(
        run['numbers']['awma_nonblocking_shared_ready_members'] == 0 and
        run['numbers']['vm_awma_same_page_share_deliveries'] == 0
        for run in controls.values())
    t2_exact = all(controls['T2']['numbers'][key] ==
                   candidates['T2']['numbers'][key]
                   for key in T2_MATCH_KEYS) and \
        controls['T2']['coverage'] == candidates['T2']['coverage']
    t0_t1_incremental = all(
        summaries[target]['candidate_vs_owner_cycle_change'] <= -.01
        for target in ('T0', 'T1'))
    supports_reuse = (all_control_correct and control_ready_zero and t2_exact and
                      t0_t1_incremental)
    decision = ('SUPPORTS_ACTUAL_READY_RESULT_REUSE_AS_INDEPENDENT_INCREMENTAL_VALUE'
                if supports_reuse else
                'DOES_NOT_SUPPORT_INDEPENDENT_READY_RESULT_REUSE_VALUE')

    write_tsv(PACK / 'CAUSAL_MATRIX.tsv', [
        'target', 'off_cycles', 'owner_only_cycles', 'candidate_cycles',
        'owner_only_vs_off_cycle_change', 'candidate_vs_off_cycle_change',
        'candidate_minus_owner_only_cycles',
        'candidate_vs_owner_only_cycle_change', 'off_lookup_requests',
        'owner_only_lookup_requests', 'candidate_lookup_requests',
        'candidate_minus_owner_only_lookup_requests',
        'owner_only_ready_share', 'candidate_ready_share',
        'owner_only_fallback', 'candidate_fallback',
        'owner_only_duplicate_lookup', 'candidate_duplicate_lookup',
        'owner_only_owner_attempts', 'candidate_owner_attempts',
        'owner_only_mshr_merges', 'candidate_mshr_merges',
        'owner_only_admissions', 'candidate_admissions',
        'owner_only_repeated_admissions', 'candidate_repeated_admissions',
        'owner_only_readmitted_uids', 'candidate_readmitted_uids',
        'owner_only_first_issue_latency_total',
        'candidate_first_issue_latency_total',
        'owner_only_all_issue_latency_total',
        'candidate_all_issue_latency_total', 'owner_only_l1_probes',
        'candidate_l1_probes', 'owner_only_l2_probes',
        'candidate_l2_probes', 'control_correctness',
        'control_run_log_sha256', 'candidate_run_log_sha256'], rows)
    write_tsv(PACK / 'CONTROL_CORRECTNESS_GATES.tsv',
              ['target'] + list(next(iter(controls.values()))['gates']) +
              ['status'], gate_rows)

    raw_rows.extend([
        ['accepted_commit', 'FROZEN_CANDIDATE',
         'c0602ee06e647d9a3cf84b0adbb8d98075021f99', '', 'ACCEPTED'],
        ['diagnostic_binary', 'OWNER_ONLY_BINARY', str(DIAGNOSTIC_BINARY),
         sha(DIAGNOSTIC_BINARY), 'PROVENANCE'],
        ['frozen_binary', 'FROZEN_CANDIDATE_BINARY', str(FROZEN_BINARY),
         sha(FROZEN_BINARY), 'ACCEPTED_REUSED'],
        ['diagnostic_patch', 'SOLE_INTERVENTION', str(patch), sha(patch),
         'PROVENANCE'],
        ['build_log', 'DIAGNOSTIC_BUILD', str(RUNTIME / 'unified_build.log'),
         sha(RUNTIME / 'unified_build.log'), 'BUILD'],
        ['runner', 'CONTROL_RUNNER', str(RUNNER), sha(RUNNER), 'PROVENANCE'],
        ['builder', 'REVIEW_BUILDER', str(BUILDER), sha(BUILDER), 'PROVENANCE'],
        ['test_source', 'CAUSAL_DIRECTED_TEST', str(TEST_SOURCE),
         sha(TEST_SOURCE), 'PROVENANCE'],
        ['test_log', 'CAUSAL_DIRECTED_TEST',
         str(RUNTIME / 'tests/awma_c1_nonblocking_causal_ablation_test.log'),
         sha(RUNTIME / 'tests/awma_c1_nonblocking_causal_ablation_test.log'),
         'VERIFIED_RUN'],
        ['test_log', 'DIAGNOSTIC_PATCH_DRY_RUN',
         str(RUNTIME / 'tests/diagnostic_core_patch_dry_run.log'),
         sha(RUNTIME / 'tests/diagnostic_core_patch_dry_run.log'),
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
            suffix = '' if mode == '' else f'_{mode}'
            log = RUNTIME / 'tests' / f'{test}{suffix}.log'
            raw_rows.append(['test_log', f'{test}:{mode or "directed"}',
                             str(log), sha(log), 'VERIFIED_RUN'])
    write_tsv(PACK / 'RAW_DATA_INDEX.tsv',
              ['kind', 'id', 'path_or_authority', 'sha256', 'evidence_class'],
              raw_rows)

    frozen_shader = FROZEN_RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/shader.cc'
    diagnostic_shader = RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/shader.cc'
    write_tsv(PACK / 'SOURCE_MATCH.tsv', [
        'item', 'frozen_sha256', 'diagnostic_sha256', 'status'], [[
            'vm_translation.h',
            sha(FROZEN_RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/vm_translation.h'),
            sha(RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/vm_translation.h'),
            'MATCH'], [
            'vm_translation.cc',
            sha(FROZEN_RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/vm_translation.cc'),
            sha(RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/vm_translation.cc'),
            'MATCH'], [
            'shader.cc', sha(frozen_shader), sha(diagnostic_shader),
            'SOLE_DIAGNOSTIC_DELTA'],
    ])

    receipt = {
        'stage': STAGE,
        'frozen_candidate': 'c0602ee06e647d9a3cf84b0adbb8d98075021f99',
        'decision': decision,
        'all_control_correct': all_control_correct,
        'control_ready_share_zero': control_ready_zero,
        't2_matched_exactly': t2_exact,
        't0_t1_candidate_incremental_value': t0_t1_incremental,
        'off_rerun_performed': False,
        'frozen_candidate_rerun_performed': False,
        'cross_context_holdout_used': False,
        'parameter_tuning_performed': False,
        'causal_contrast_not_runtime_fraction': True,
        'summaries': summaries,
        'controls': controls,
        'candidates': candidates,
    }
    (PACK / 'RUN_RECEIPTS.json').write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + '\n')

    report = f'''# AWMA C1 nonblocking sharing causal ablation V1

Status: **COMPLETE / {decision}**

## Matched intervention

The frozen candidate at `c0602ee06e647d9a3cf84b0adbb8d98075021f99`
is unchanged and was not rerun. The sole diagnostic intervention is
`NONBLOCKING_OWNER_ONLY_NO_SHARE_CONTROL`: same-page legality, group detection,
owner selection, proactive owner translation, nonblocking member fallback,
baseline V1 path, ordering/arbitration, and finite resources are retained;
only member consumption of an already-READY owner result is disabled.

No owner waits or is cancelled, no port/threshold/parameter changes, and every
control reports zero READY shares.

## Three-way development comparison

| target | OFF | OwnerOnly | Frozen candidate | Candidate - OwnerOnly | Candidate vs OwnerOnly |
|---|---:|---:|---:|---:|---:|
| T0 | 527,896 | 1,001,842 | 506,778 | -495,064 | {summaries['T0']['candidate_vs_owner_cycle_change']:.3%} |
| T1 | 665,802 | 1,354,934 | 643,076 | -711,858 | {summaries['T1']['candidate_vs_owner_cycle_change']:.3%} |
| T2 | 93,079 | 89,689 | 89,689 | 0 | 0.000% |
| SPLITKV | 73,923 | 85,796 | 74,361 | -11,435 | {summaries['SPLITKV']['candidate_vs_owner_cycle_change']:.3%} |
| COMBINE | 10,480 | 14,153 | 10,484 | -3,669 | {summaries['COMBINE']['candidate_vs_owner_cycle_change']:.3%} |

`Candidate - OwnerOnly` is a matched causal contrast on the same
owner/prelaunch structure. It is **not** interpreted as an additive runtime
fraction.

## Attribution

- T0 and T1 are decisively faster with READY-result reuse enabled, supporting
  independent incremental value from actual sharing rather than attributing
  their development speedups only to owner/prelaunch/order effects.
- T2 has zero READY shares in both conditions. Candidate and OwnerOnly are
  exactly equal in cycles and every prespecified matching metric, validating
  the control construction.
- SPLITKV and COMBINE show the same direction: disabling result reuse while
  retaining proactive owners increases cycles and physical lookup work.
- OwnerOnly is much slower than OFF on four targets. Proactive owner work
  without result reuse is therefore a cost, not an alternative explanation
  for the candidate gains on those targets.

All control correctness, coverage, exactly-once, owner-wait/head-block zero,
fallback accounting, and full controller/candidate quiescence gates pass.
`CAUSAL_MATRIX.tsv` retains physical lookup requests, READY shares, fallback
and duplicate work, owner activity, MSHR merges, admissions/re-admissions,
probe counts, and downstream issue timing for both matched conditions.

## Scope and limits

These five targets remain development evidence. The result supports a causal
role for READY-result reuse but does not quantify an additive runtime fraction,
promote a baseline, or establish a final mechanism or paper claim. The
pre-frozen cross-context scientific holdout was not viewed or used. No further
tuning or experiment is authorized by this stage.
'''
    (PACK / 'REPORT.md').write_text(report)
    (PACK / 'README.md').write_text(
        f'# {STAGE}\n\nReview `REPORT.md`, `CAUSAL_MATRIX.tsv`, '
        '`CONTROL_CORRECTNESS_GATES.tsv`, `SOURCE_MATCH.tsv`, '
        '`RAW_DATA_INDEX.tsv`, and `RUN_RECEIPTS.json`.\n')
    (PACK / 'SOURCE_ANCHORS.md').write_text(f'''# Source anchors

- frozen candidate commit: `c0602ee06e647d9a3cf84b0adbb8d98075021f99`
- frozen candidate binary SHA256: `{sha(FROZEN_BINARY)}`
- diagnostic binary SHA256: `{sha(DIAGNOSTIC_BINARY)}`
- diagnostic patch SHA256: `{sha(patch)}`
- platform config SHA256: `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`
- trace config SHA256: `a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b`
''')
    members = sorted(path for path in PACK.iterdir()
                     if path.is_file() and path.name != 'SHA256SUMS')
    (PACK / 'SHA256SUMS').write_text(
        ''.join(f'{sha(path)}  {path.name}\n' for path in members))
    print(json.dumps({
        'decision': decision,
        'all_control_correct': all_control_correct,
        'control_ready_share_zero': control_ready_zero,
        't2_matched_exactly': t2_exact,
        't0_t1_candidate_incremental_value': t0_t1_incremental,
        'summaries': summaries,
    }, indent=2, sort_keys=True))
    return 0 if all_control_correct and t2_exact else 1


if __name__ == '__main__':
    raise SystemExit(main())
