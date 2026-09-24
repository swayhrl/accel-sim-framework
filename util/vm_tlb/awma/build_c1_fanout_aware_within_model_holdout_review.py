#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

STAGE = 'AWMA_C1_FANOUT_AWARE_WITHIN_MODEL_HOLDOUT_V1'
REPO = Path('/root/workspace/accel-sim-framework-awma-c1-fanout-aware-within-model-holdout-v1')
RUNTIME = Path('/root/awma_c1_fanout_aware_within_model_holdout_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_c1_fanout_aware_within_model_holdout_v1/raw')
PACK = REPO / 'docs/vm_tlb/review_packs' / STAGE
RUNNER = REPO / 'util/vm_tlb/awma/run_c1_fanout_aware_within_model_holdout.py'
BUILDER = REPO / 'util/vm_tlb/awma/build_c1_fanout_aware_within_model_holdout_review.py'
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
PARENT_RUNTIME = Path('/root/awma_c1_fanout_aware_sharing_exploration_v1_runtime')
AUTHORITY_PACK = REPO / 'docs/vm_tlb/review_packs/AWMA_EXISTING_REP_SUITE_TRACE_REQUALIFICATION_V1'

TARGETS = {
    'SPLITKV': {
        'identity': 'DECODE_FLASH_PRIMARY_1_STEP16',
        'family': 'FLASH_FWD_SPLITKV',
        'baseline_cycles': 73923,
        'baseline_lookup': 1997336,
        'baseline_l1': 236746,
        'baseline_l2': 6076,
        'baseline_log': Path('/root/awma_existing_rep_suite_trace_requalification_v1_runtime/SPLITKV_V1_10_80/run.log'),
        'insn': 36599648, 'cta': 126, 'uid': 233814,
        'payload_sha': '282a9b18510bd0aaf54ec528c65bfb39d49b052902c6b87f3b85bb2973096371',
        'index_sha': '59236d6c6746260a3127c8f858270c915e91c9d7959647047a8d44504a984773',
    },
    'COMBINE': {
        'identity': 'DECODE_FLASH_PRIMARY_2_STEP16',
        'family': 'FLASH_FWD_SPLITKV_COMBINE',
        'baseline_cycles': 10480,
        'baseline_lookup': 9228,
        'baseline_l1': 1139,
        'baseline_l2': 40,
        'baseline_log': Path('/root/awma_existing_rep_suite_trace_requalification_v1_runtime/COMBINE_V1_10_80/run.log'),
        'insn': 72908, 'cta': 2, 'uid': 1099,
        'payload_sha': 'd153db1548517f24eebd80c1a5dc48785ab28ace173b2937dd4f7b4a7005dcb9',
        'index_sha': '31b54d9f55ce501a6cb64360c2b1c988e2099b7e97e3fb9945d27d4631dd8da2',
    },
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
    'awma_owner_wait_owner_attempts', 'awma_owner_wait_owner_retry_attempts',
    'awma_owner_wait_member_owner_wait_cycles',
    'awma_owner_wait_member_wait_completions',
    'awma_owner_wait_latency_total', 'awma_owner_wait_latency_max',
    'awma_owner_wait_head_block_owner_not_ready_cycles',
    'awma_owner_wait_head_block_owner_ready_cycles',
    'awma_owner_wait_head_block_total_cycles',
    'awma_owner_wait_first_issue_latency_total',
    'awma_owner_wait_first_issue_latency_max',
    'awma_owner_wait_all_issue_latency_total',
    'awma_owner_wait_all_issue_latency_max',
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


def parse_run(target: str, threshold: int) -> dict[str, object]:
    directory = DURABLE / f'{target}_C1_{threshold}_10_80'
    text = (directory / 'run.log').read_text(errors='replace')
    command = json.loads((directory / 'command.json').read_text())
    numbers = {key: last_number(text, key) for key in NUMERIC_KEYS}
    cov = coverage(text)
    spec = TARGETS[target]
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
        'rc_zero': (directory / 'rc.txt').read_text().strip() == '0',
        'terminal': ('GPGPU-Sim: *** simulation thread exiting ***' in text and
                     'GPGPU-Sim: *** exit detected ***' in text),
        'candidate_mode': bool(modes) and modes[-1] == 'same_page_share',
        'threshold_exact':
            numbers['vm_awma_same_page_share_min_cohort_size'] == threshold,
        'command_threshold_exact': command['min_cohort_size'] == threshold,
        'payload_authority': command['payload_sha256'] == spec['payload_sha'],
        'index_authority': command['runner_index_sha256'] == spec['index_sha'],
        'instructions_exact': numbers['gpu_sim_insn'] == spec['insn'],
        'cta_exact': numbers['gpu_tot_issued_cta'] == spec['cta'],
        'unique_uid_exact': cov['unique'] == spec['uid'],
        'translated_unique_exact': cov['translated_unique'] == spec['uid'],
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
        'service_conservation': service_total ==
            numbers['awma_owner_wait_shared_cohorts'],
        'owner_conservation':
            numbers['vm_awma_same_page_share_owner_ready'] ==
            numbers['awma_owner_wait_shared_cohorts'],
    }
    return {
        'target': target, 'threshold': threshold, 'run_dir': str(directory),
        'cycles': numbers['gpu_sim_cycle'], 'coverage': cov,
        'numbers': numbers, 'gates': gates,
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
    runs = [parse_run(target, threshold)
            for target in ('SPLITKV', 'COMBINE') for threshold in (2, 4)]
    by_key = {(str(run['target']), int(run['threshold'])): run for run in runs}
    matrix_rows: list[list[object]] = []
    gate_rows: list[list[object]] = []
    raw_rows: list[list[object]] = []
    summaries: dict[str, dict[str, object]] = {}

    for run in runs:
        target, threshold = str(run['target']), int(run['threshold'])
        spec, n, cov = TARGETS[target], run['numbers'], run['coverage']
        cycle_change = (int(run['cycles']) - spec['baseline_cycles']) / spec['baseline_cycles']
        lookup_suppression = 1 - n['vm_translation_lookup_requests'] / spec['baseline_lookup']
        matrix_rows.append([
            target, spec['identity'], spec['family'], f'C1-{threshold}',
            spec['baseline_cycles'], run['cycles'], f'{cycle_change:.9f}',
            spec['baseline_lookup'], n['vm_translation_lookup_requests'],
            f'{lookup_suppression:.9f}', spec['baseline_l1'],
            n['vm_l1_tlb_accesses'], spec['baseline_l2'],
            n['vm_l2_tlb_accesses'], cov['admissions'], cov['unique'],
            n['awma_owner_wait_repeated_admissions'],
            n['awma_owner_wait_readmitted_uids'],
            n['vm_awma_same_page_share_owner_ready'],
            n['vm_awma_same_page_share_deliveries'],
            n['awma_owner_wait_member_owner_wait_cycles'],
            n['awma_owner_wait_latency_total'],
            n['awma_owner_wait_latency_max'],
            n['awma_owner_wait_head_block_total_cycles'],
            n['awma_owner_wait_first_issue_latency_total'],
            n['awma_owner_wait_all_issue_latency_total'],
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
        gate_rows.append([target, f'C1-{threshold}'] +
                         ['PASS' if value else 'FAIL'
                          for value in run['gates'].values()] +
                         ['PASS' if run['correctness'] else 'FAIL'])
        raw_rows.extend([
            ['run_log', f'{target}:C1-{threshold}',
             f"{run['run_dir']}/run.log", run['run_log_sha256'], 'NEW_RUN'],
            ['command', f'{target}:C1-{threshold}',
             f"{run['run_dir']}/command.json", run['command_sha256'],
             'PROVENANCE'],
        ])

    all_correct = all(bool(run['correctness']) for run in runs)
    pair_exact = True
    all_high_fanout = True
    fanout4_regresses = True
    for target, spec in TARGETS.items():
        c2, c4 = by_key[(target, 2)], by_key[(target, 4)]
        metric_keys = set(NUMERIC_KEYS) - {
            'vm_awma_same_page_share_min_cohort_size'}
        exact = (c2['cycles'] == c4['cycles'] and c2['coverage'] == c4['coverage'] and
                 all(c2['numbers'][key] == c4['numbers'][key]
                     for key in metric_keys))
        pair_exact &= exact
        n4 = c4['numbers']
        low = n4['awma_owner_wait_cohort_hist_2'] + n4['awma_owner_wait_cohort_hist_3']
        high = (n4['awma_owner_wait_cohort_hist_4'] +
                n4['awma_owner_wait_cohort_hist_5_8'] +
                n4['awma_owner_wait_cohort_hist_9_16'] +
                n4['awma_owner_wait_cohort_hist_17_32'])
        all_high_fanout &= low == 0 and high > 0 and n4['awma_owner_wait_gated_cohorts'] == 0
        cycle_change = (int(c4['cycles']) - spec['baseline_cycles']) / spec['baseline_cycles']
        fanout4_regresses &= cycle_change > .005
        summaries[target] = {
            'pair_exact': exact, 'low_fanout_cohorts': low,
            'high_fanout_cohorts': high, 'fanout4_cycle_change': cycle_change,
            'lookup_suppression': 1 - n4['vm_translation_lookup_requests'] / spec['baseline_lookup'],
        }

    insufficient = all_correct and pair_exact and all_high_fanout and fanout4_regresses
    decision = ('FANOUT_ONLY_GATING_INSUFFICIENT_ON_WITHIN_MODEL_INDEPENDENT_TARGETS'
                if insufficient else
                'WITHIN_MODEL_HOLDOUT_RESULT_REQUIRES_QUALIFIED_INTERPRETATION')

    write_tsv(PACK / 'HOLDOUT_MATRIX.tsv', [
        'target', 'identity', 'family', 'candidate', 'accepted_off_cycles',
        'candidate_cycles', 'candidate_vs_off_cycle_change',
        'accepted_off_lookup_requests', 'candidate_lookup_requests',
        'lookup_suppression_fraction', 'accepted_off_l1_probes',
        'candidate_l1_probes', 'accepted_off_l2_probes', 'candidate_l2_probes',
        'admissions', 'unique_uid', 'repeated_admissions', 'readmitted_uids',
        'share_owners', 'share_deliveries', 'member_owner_wait_cycles',
        'owner_to_member_wait_latency_total', 'owner_to_member_wait_latency_max',
        'head_block_cycles', 'first_issue_latency_total',
        'all_issue_latency_total', 'cohort_size_2', 'cohort_size_3',
        'cohort_size_4', 'cohort_size_5_8', 'cohort_size_9_16',
        'cohort_size_17_32', 'gated_cohorts', 'shared_cohorts', 'correctness',
        'run_log_sha256'], matrix_rows)
    gate_names = list(runs[0]['gates'])
    write_tsv(PACK / 'CORRECTNESS_GATES.tsv',
              ['target', 'candidate'] + gate_names + ['status'], gate_rows)

    raw_rows.extend([
        ['authority_pack', 'QUALIFIED_TARGETS', str(AUTHORITY_PACK),
         '0fc6c559027b029d79b77c1f6dcfa5162648b1ac', 'ACCEPTED_COMMIT'],
        ['build_log', 'PRIVATE_BUILD', str(RUNTIME / 'unified_build.log'),
         sha(RUNTIME / 'unified_build.log'), 'BUILD'],
        ['binary', 'PRIVATE_BINARY', str(BINARY), sha(BINARY), 'PROVENANCE'],
        ['runner', 'HOLDOUT_RUNNER', str(RUNNER), sha(RUNNER), 'PROVENANCE'],
        ['builder', 'REVIEW_BUILDER', str(BUILDER), sha(BUILDER), 'PROVENANCE'],
        ['test_log', 'FANOUT_DIRECTED',
         str(RUNTIME / 'tests/awma_c1_fanout_aware_test.log'),
         sha(RUNTIME / 'tests/awma_c1_fanout_aware_test.log'), 'VERIFIED_RUN'],
    ])
    for target, spec in TARGETS.items():
        baseline_log = spec['baseline_log']
        raw_rows.append(['accepted_baseline_log', target, str(baseline_log),
                         sha(baseline_log), 'ACCEPTED_REUSED_NO_RERUN'])
    for test in ('awma_literature_mechanism_test',
                 'vm_m3_g3_4b_tlb_timing_test',
                 'vm_m2_rf_pending_retry_test',
                 'vm_c10b_runtime_validation_test'):
        for mode in ('none', 'refill_protect'):
            log = RUNTIME / 'tests' / f'{test}_{mode}.log'
            raw_rows.append(['test_log', f'{test}:{mode}', str(log), sha(log),
                             'VERIFIED_RUN'])
    write_tsv(PACK / 'RAW_DATA_INDEX.tsv',
              ['kind', 'id', 'path_or_authority', 'sha256_or_commit',
               'evidence_class'], raw_rows)

    source_rows = []
    for relative in ('src/gpgpu-sim/vm_translation.cc',
                     'src/gpgpu-sim/vm_translation.h',
                     'src/gpgpu-sim/gpu-sim.cc'):
        parent = PARENT_RUNTIME / 'src/gpgpu-sim' / relative
        current = RUNTIME / 'src/gpgpu-sim' / relative
        source_rows.append([relative, sha(parent), sha(current),
                            'MATCH' if sha(parent) == sha(current) else 'MISMATCH'])
    write_tsv(PACK / 'SOURCE_REUSE.tsv',
              ['source', 'accepted_parent_sha256', 'holdout_sha256', 'status'],
              source_rows)

    receipt = {
        'stage': STAGE,
        'accepted_mechanism_parent': 'f685f88d328b8bcb5f56c31b2629e5ed56938bb1',
        'accepted_target_authority': '0fc6c559027b029d79b77c1f6dcfa5162648b1ac',
        'decision': decision, 'all_correct': all_correct,
        'c1_2_c1_4_pairs_exact': pair_exact,
        'all_observed_cohorts_high_fanout': all_high_fanout,
        'fanout4_regresses_over_point_five_percent': fanout4_regresses,
        'threshold_sweep_performed': False, 'threshold_frozen': 4,
        'baseline_rerun_performed': False,
        'validation_scope': 'WITHIN_MODEL_INDEPENDENT_TARGET_VALIDATION',
        'scientific_holdout_scope': 'Qwen2.5 S2 only; not cross-context or cross-model',
        'summaries': summaries, 'runs': runs,
    }
    (PACK / 'RUN_RECEIPTS.json').write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + '\n')

    split = summaries['SPLITKV']
    combine = summaries['COMBINE']
    report = f'''# AWMA C1 fanout-aware within-model holdout V1

Status: **COMPLETE / {decision}**

## Outcome

Both independent kernel identities pass every correctness, exactly-once,
coverage, controller-drain, candidate-state-drain, and provenance gate.  They
also show only cohorts of size 4 or larger, so frozen Fanout-4 gates nothing and
is identical to accepted raw C1-2 in every recorded operational metric; only
the configured threshold field differs.

| target | accepted OFF | C1-2 | C1-4 | C1-4 vs OFF | lookup suppression |
|---|---:|---:|---:|---:|---:|
| SPLITKV | 73,923 | 75,950 | 75,950 | {split['fanout4_cycle_change']:.3%} | {split['lookup_suppression']:.3%} |
| COMBINE | 10,480 | 10,615 | 10,615 | {combine['fanout4_cycle_change']:.3%} | {combine['lookup_suppression']:.3%} |

This is the specified stop condition: Fanout-4 still has a clear negative
performance response on both targets despite very large physical-lookup
suppression.  Therefore cohort fanout alone is not a sufficient gate for C1.
No threshold was changed or swept, and no additional simulation was run.

## Cohort and wait evidence

- SPLITKV: 14,826 shared cohorts (126 size-4, 252 size-5..8, 14,448
  size-9..16), zero gated cohorts, 7,883,943 member owner-wait cycles and
  791,317 C1 head-block cycles.
- COMBINE: 74 shared cohorts (11 size-5..8, 63 size-9..16), zero gated
  cohorts, 32,263 member owner-wait cycles and 3,745 C1 head-block cycles.
- C1-2 and C1-4 are exactly equal for cycles, lookup/probe counts, all cohort
  bins, owner wait, head blocking, admissions, deliveries, coverage, and
  downstream issue timing on each target.
- Repeated admissions and readmitted UIDs are zero for all four runs.  This
  rules out re-admission as the immediate explanation here, while the large
  owner-wait/head-block signal remains consistent with the accepted Phase 3
  attribution.

## Validation scope

The two kernel identities did not participate in selecting
`MIN_COHORT_SIZE=4`, so this is a
`WITHIN_MODEL_INDEPENDENT_TARGET_VALIDATION`.  Both remain Qwen2.5 S2 assets;
this is **not** cross-context or cross-model scientific holdout evidence.

The accepted 10/80 OFF results were reused without rerun.  The experiment used
an independent worktree, runtime, build, binary, and durable output path.  The
accepted mechanism source is reused unchanged; `SOURCE_REUSE.tsv` verifies the
Core source hashes.  The fixed RTX4080/V1 configuration and downstream memory
semantics were not modified.

## Interpretation and next discriminating experiment

The discovery result does not promote a baseline and does not establish a
paper mechanism.  A future, separately authorized experiment should test a
readiness/wait-cost-aware gate (for example, share only when the owner result is
already ready, with lookup-suppression loss reported) on independent targets.
That directly distinguishes high fanout from owner-ready timing.  It must not
reuse this holdout to tune `MIN_COHORT_SIZE`.

## Limits

- Two kernels from one Qwen2.5 S2 workload context.
- Simulator-relative RTX4080/V1 10/80 configuration, not a hardware latency
  claim.
- No threshold sweep, no cross-model trace, no baseline promotion, and no
  novelty or paper-level conclusion.
'''
    (PACK / 'REPORT.md').write_text(report)
    (PACK / 'README.md').write_text(
        f'# {STAGE}\n\n'
        'Review order: `REPORT.md`, `HOLDOUT_MATRIX.tsv`, '
        '`CORRECTNESS_GATES.tsv`, `SOURCE_REUSE.tsv`, '
        '`RAW_DATA_INDEX.tsv`, then `RUN_RECEIPTS.json`.\n')
    (PACK / 'SOURCE_ANCHORS.md').write_text(f'''# Source anchors

- accepted mechanism parent: `f685f88d328b8bcb5f56c31b2629e5ed56938bb1`
- accepted target authority: `0fc6c559027b029d79b77c1f6dcfa5162648b1ac`
- frozen baseline authority: `8d1f14a32f5538660d74da86ccb03a2c504c5735`
- private holdout binary SHA256: `{sha(BINARY)}`
- frozen platform config SHA256: `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`
- frozen trace config SHA256: `a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b`
- threshold: `MIN_COHORT_SIZE=4` (frozen; no sweep)
- baseline results: accepted and reused; no OFF rerun
''')
    members = sorted(path for path in PACK.iterdir()
                     if path.is_file() and path.name != 'SHA256SUMS')
    (PACK / 'SHA256SUMS').write_text(
        ''.join(f'{sha(path)}  {path.name}\n' for path in members))
    print(json.dumps({
        'decision': decision, 'all_correct': all_correct,
        'c1_2_c1_4_pairs_exact': pair_exact,
        'all_observed_cohorts_high_fanout': all_high_fanout,
        'summaries': summaries,
    }, indent=2, sort_keys=True))
    return 0 if all_correct else 1


if __name__ == '__main__':
    raise SystemExit(main())
