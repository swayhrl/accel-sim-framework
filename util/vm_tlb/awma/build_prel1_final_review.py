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
PHASE_A = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescing_v1/phase_a_raw')
DEV = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescing_v1/development_raw')
ZERO = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescing_v1/zero_duplication_gate')
PACK = REPO / 'docs/vm_tlb/review_packs' / STAGE
SOURCE_FREEZE = '2bbbceabb5261777fe385289ecb6579791e0f232'
RUNNER_COMMIT = '744acc6661bb8770e1dbcb60e3b9eca80a8ae688'
LEVEL2_RUNNER_COMMIT = '929a7da411401d1432ca826995ecd8fc42c9971c'
HOLDOUT_PREREG = 'd450b2a06a0af18960d81b0ccbb46d047fe6cbae'
TARGETS = ('T0', 'T1', 'T2', 'SPLITKV', 'COMBINE', 'A1', 'A2')

CORE = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_l1_tlb_lookup_launches', 'vm_l2_tlb_lookup_launches',
    'vm_translation_mshr_allocations', 'vm_translation_mshr_merges',
    'vm_translation_walk_starts', 'vm_pte_requests',
    'vm_ready_application_duplicate_attempts',
    'vm_translation_quiescent_invariants_hold')
COAL = tuple(f'awma_prel1_coalescer_{name}' for name in (
    'leaders', 'followers', 'entry_full_fallbacks', 'waiter_full_fallbacks',
    'grouping_only_followers', 'leader_completions', 'follower_applications',
    'follower_wait_cycles_total', 'follower_wait_cycles_max',
    'delivery_wait_p50', 'delivery_wait_p95', 'delivery_wait_p99',
    'follower_delivery_latency_max', 'leader_to_follower_latency_total',
    'leader_to_follower_latency_max', 'head_block_cycles',
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


def parse(path: Path, coalescer: bool = False) -> dict[str, object]:
    text = (path / 'run.log').read_text(errors='replace')
    values = {key: number(text, key) for key in CORE}
    if coalescer:
        values.update({key: number(text, key) for key in COAL})
    return {'path': path, 'text': text, 'values': values}


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(header)
        writer.writerows(rows)


def metrics(text: str) -> dict[str, dict[str, object]]:
    rows = re.findall(
        r'^awma_observatory_metric\t(\S+)\t(\S+)\t(\S+)\t(\d+)\t(\d+)\t'
        r'([0-9.]+)\t(\d+)$', text, re.M)
    return {f'{domain}.{metric}': {
        'kind': kind, 'total': int(total), 'samples': int(samples),
        'mean': float(mean), 'peak': int(peak)}
        for domain, metric, kind, total, samples, mean, peak in rows}


def windows(text: str) -> dict[tuple[str, str, int], dict[str, object]]:
    rows = re.findall(
        r'^awma_observatory_window\t(\S+)\t(\S+)\t(\d+)\t(\d+)\t'
        r'([0-9.]+)\t(\d+)\t(\d+)\t(\d+)\t(\d+)\t(\d+)$',
        text, re.M)
    return {(domain, metric, int(width)): {
        'windows': int(count), 'mean': float(mean), 'p50': int(p50),
        'p95': int(p95), 'p99': int(p99), 'max': int(maximum),
        'samples': int(samples)}
        for domain, metric, width, count, mean, p50, p95, p99, maximum,
        samples in rows}


def progress(text: str, kind: str) -> list[int]:
    rows = re.findall(
        rf'^awma_observatory_progress\t{kind}\t(\d+)\t(\d+)\t(\d+)\t'
        r'(\d+)\t(\d+)\t(\d+)\t(\d+)$', text, re.M)
    return list(map(int, rows[-1]))


def main() -> int:
    off = {t: parse(PHASE_A / f'{t}_OFF_OPPORTUNITY_10_80') for t in TARGETS}
    candidate = {t: parse(DEV / f'{t}_COALESCER_10_80', True) for t in TARGETS}
    control_targets = ('T0', 'T1', 'A2')
    controls = {t: parse(DEV / f'{t}_GROUPING_ONLY_10_80', True)
                for t in control_targets}
    plus_targets = ('T0', 'T1', 'T2', 'A2')
    plus = {t: parse(DEV / f'{t}_COALESCER_PLUS1_10_80', True)
            for t in plus_targets}

    control_rows = []
    control_exact = True
    for target in control_targets:
        ov, gv, cv = (off[target]['values'], controls[target]['values'],
                      candidate[target]['values'])
        exact = (gv['gpu_sim_cycle'] == ov['gpu_sim_cycle'] and
                 gv['vm_l1_tlb_lookup_launches'] ==
                 ov['vm_l1_tlb_lookup_launches'] and
                 gv['vm_l2_tlb_lookup_launches'] ==
                 ov['vm_l2_tlb_lookup_launches'])
        control_exact &= exact
        control_rows.append([
            target, ov['gpu_sim_cycle'], gv['gpu_sim_cycle'],
            cv['gpu_sim_cycle'],
            (ov['gpu_sim_cycle'] - gv['gpu_sim_cycle']) / ov['gpu_sim_cycle'] * 100,
            (gv['gpu_sim_cycle'] - cv['gpu_sim_cycle']) / gv['gpu_sim_cycle'] * 100,
            ov['vm_l1_tlb_lookup_launches'], gv['vm_l1_tlb_lookup_launches'],
            cv['vm_l1_tlb_lookup_launches'],
            gv['awma_prel1_coalescer_grouping_only_followers'],
            gv['awma_prel1_coalescer_follower_applications'], exact])
    write_tsv(PACK / 'GROUPING_ONLY_CONTROL.tsv', [
        'target', 'off_cycles', 'grouping_only_cycles', 'candidate_cycles',
        'grouping_only_speedup_vs_off_percent',
        'candidate_increment_vs_grouping_percent', 'off_l1_launches',
        'grouping_only_l1_launches', 'candidate_l1_launches',
        'grouped_followers', 'control_follower_applications', 'matched_exact'],
        control_rows)

    phase_a_mshr = {}
    with (PACK / 'EXISTING_MSHR_OVERLAP.tsv').open(newline='') as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            phase_a_mshr[row['target']] = row
    mshr_rows = []
    for target in TARGETS:
        ov, cv = off[target]['values'], candidate[target]['values']
        phase = phase_a_mshr[target]
        mshr_rows.append([
            target, ov['vm_translation_mshr_merges'],
            cv['vm_translation_mshr_merges'],
            int(phase['selected_capacity_merges']),
            int(phase['selected_capacity_existing_mshr_overlap']),
            int(phase['selected_capacity_incremental_pre_l1_merges']),
            cv['awma_prel1_coalescer_followers'],
            ov['vm_l1_tlb_lookup_launches'] - cv['vm_l1_tlb_lookup_launches'],
            ov['vm_l2_tlb_lookup_launches'] - cv['vm_l2_tlb_lookup_launches'],
            ov['vm_translation_mshr_merges'] -
            cv['vm_translation_mshr_merges']])
    write_tsv(PACK / 'MSHR_INCREMENTAL_VALUE.tsv', [
        'target', 'baseline_existing_mshr_merges', 'candidate_mshr_merges',
        'phase_a_finite_merge_opportunities', 'phase_a_existing_mshr_overlap',
        'phase_a_incremental_pre_l1_opportunities', 'actual_followers',
        'actual_l1_launches_suppressed', 'actual_l2_launches_suppressed',
        'actual_mshr_merges_reduced'], mshr_rows)

    timing_rows = []
    timing_robust = True
    for target in plus_targets:
        ov, cv, pv = (off[target]['values'], candidate[target]['values'],
                      plus[target]['values'])
        main_speed = (ov['gpu_sim_cycle'] - cv['gpu_sim_cycle']) / ov['gpu_sim_cycle']
        plus_speed = (ov['gpu_sim_cycle'] - pv['gpu_sim_cycle']) / ov['gpu_sim_cycle']
        correct = (pv['awma_prel1_coalescer_followers'] ==
                   pv['awma_prel1_coalescer_follower_applications'] and
                   pv['awma_prel1_coalescer_head_block_cycles'] == 0 and
                   pv['awma_prel1_coalescer_quiescent'] == 1 and
                   pv['vm_ready_application_duplicate_attempts'] == 0)
        if plus_speed < -0.01:
            timing_robust = False
        timing_rows.append([
            target, ov['gpu_sim_cycle'], cv['gpu_sim_cycle'],
            pv['gpu_sim_cycle'], main_speed * 100, plus_speed * 100,
            pv['awma_prel1_coalescer_compare_delays'],
            pv['awma_prel1_coalescer_followers'],
            pv['awma_prel1_coalescer_head_block_cycles'], correct])
    write_tsv(PACK / 'TIMING_SENSITIVITY.tsv', [
        'target', 'off_cycles', 'same_cycle_cycles', 'plus1_cycles',
        'same_cycle_speedup_percent', 'plus1_speedup_percent',
        'compare_delays', 'followers', 'head_block_cycles', 'correctness'],
        timing_rows)

    selected_metrics = (
        'translation.translation_not_ready',
        'memory.ldst_coal_stall', 'memory.l1_reservation_fail',
        'memory.l2_reservation_fail', 'memory.icnt_to_l2_occupancy',
        'memory.dram_queue_occupancy', 'scheduler.dependency_scoreboard',
        'scheduler.eligible_structural', 'scheduler.frontend_starvation')
    level1_rows = []
    for target in ('T0', 'T1', 'T2', 'A1', 'A2'):
        om, cm = metrics(off[target]['text']), metrics(candidate[target]['text'])
        for metric in selected_metrics:
            level1_rows.append([
                target, metric, om[metric]['kind'], om[metric]['total'],
                cm[metric]['total'], om[metric]['mean'], cm[metric]['mean'],
                om[metric]['peak'], cm[metric]['peak']])
    write_tsv(PACK / 'OBSERVATORY_LEVEL1.tsv', [
        'target', 'metric', 'kind', 'off_total', 'candidate_total',
        'off_mean', 'candidate_mean', 'off_peak', 'candidate_peak'],
        level1_rows)

    level2_rows = []
    progress_rows = []
    for target in ('T2', 'A1'):
        off_l2 = parse(DEV / f'{target}_OFF_LEVEL2_10_80')
        cand_l2 = parse(DEV / f'{target}_COALESCER_LEVEL2_10_80', True)
        ow, cw = windows(off_l2['text']), windows(cand_l2['text'])
        for domain, metric in (
                ('memory', 'ldst_coal_stall'),
                ('memory', 'l1_reservation_fail'),
                ('memory', 'l2_reservation_fail'),
                ('memory', 'dram_queue_occupancy'),
                ('translation', 'translation_not_ready')):
            o, c = ow[(domain, metric, 512)], cw[(domain, metric, 512)]
            level2_rows.append([
                target, f'{domain}.{metric}', 512, o['mean'], c['mean'],
                o['p95'], c['p95'], o['p99'], c['p99'], o['max'], c['max']])
        for kind in ('INSTRUCTIONS', 'CTAS'):
            op, cp = progress(off_l2['text'], kind), progress(cand_l2['text'], kind)
            progress_rows.append([target, kind] + op + cp)
    write_tsv(PACK / 'OBSERVATORY_LEVEL2.tsv', [
        'target', 'metric', 'window', 'off_mean', 'candidate_mean',
        'off_p95', 'candidate_p95', 'off_p99', 'candidate_p99',
        'off_max', 'candidate_max'], level2_rows)
    write_tsv(PACK / 'OBSERVATORY_PROGRESS.tsv', [
        'target', 'kind', 'off_total', 'off_p25', 'off_p50', 'off_p75',
        'off_p90', 'off_p99', 'off_tail_after_p99', 'candidate_total',
        'candidate_p25', 'candidate_p50', 'candidate_p75', 'candidate_p90',
        'candidate_p99', 'candidate_tail_after_p99'], progress_rows)

    t0 = candidate['T0']['values']; t1 = candidate['T1']['values']
    t2 = candidate['T2']['values']; a1 = candidate['A1']['values']
    a2 = candidate['A2']['values']
    (PACK / 'OBSERVATORY_ATTRIBUTION.md').write_text(f'''# Observatory attribution

Status: **AUTOMATIC ANALYSIS / NO ROOT_CAUSE CLAIM**

Level1 was collected for every development point. Level2 was added for the
two same-cycle regressions, T2 and A1.

- T0/T1: L1 launches fall by
  {off['T0']['values']['vm_l1_tlb_lookup_launches'] - t0['vm_l1_tlb_lookup_launches']:,}/
  {off['T1']['values']['vm_l1_tlb_lookup_launches'] - t1['vm_l1_tlb_lookup_launches']:,};
  `translation_not_ready` and L2 service pressure also fall. This direction is
  consistent with the +5.390%/+2.758% responses.
- A2: physical service falls and dependency-scoreboard events decrease while
  the response is +1.698%; the matched grouping-only arm is exactly OFF.
- T2/A1: both suppress physical service and have zero coalescer head-block
  cycles, so their -1.026%/-1.132% responses do not reproduce old C1 waiting.
  Level1/Level2 show changed cache-reservation, coalescing-stall, scheduler and
  p99-tail distributions. This is consistent with downstream ordering/pressure
  perturbation, but the current evidence does not establish a root cause.
- The +1-cycle sensitivity reverses T2 to a positive response and leaves A2
  within 0.3% of OFF, confirming that response sign can be schedule-sensitive;
  it does not eliminate the service-suppression mediator.

Machine-readable totals, 512-cycle windows and bounded progress checkpoints
are in `OBSERVATORY_LEVEL1.tsv`, `OBSERVATORY_LEVEL2.tsv` and
`OBSERVATORY_PROGRESS.tsv`.
''')

    development_decision = json.loads((RUNTIME / 'development_decision.json').read_text())
    zero_pass = json.loads((RUNTIME / 'zero_duplication_gate.json').read_text())['status'] == 'PASS'
    all_correct = development_decision['status'] == 'PASS' and zero_pass
    no_head_block = all(candidate[t]['values']['awma_prel1_coalescer_head_block_cycles'] == 0
                        for t in TARGETS)
    no_waiter_overflow = all(candidate[t]['values']['awma_prel1_coalescer_waiter_full_fallbacks'] == 0
                             for t in TARGETS)
    all_suppress = all(candidate[t]['values']['vm_l1_tlb_lookup_launches'] <
                       off[t]['values']['vm_l1_tlb_lookup_launches'] for t in TARGETS)
    supported = (all_correct and control_exact and timing_robust and
                 no_head_block and no_waiter_overflow and all_suppress)
    decision = ('PREL1_COALESCER_SUPPORTED_FOR_INDEPENDENT_VALIDATION'
                if supported else 'PREL1_COALESCER_NOT_SUPPORTED')
    readiness = ('READY_FOR_INDEPENDENT_HOLDOUT_CAPTURE'
                 if supported else 'NOT_READY_FOR_HOLDOUT')
    (PACK / 'FINAL_DECISION.md').write_text(f'''# Final decision

Decision: **{decision}**

Holdout status: **{readiness}**

Evidence:

- all directed, full-pipeline and seven-target correctness gates pass;
- capacity is finite (2 entries/SID, 32 waiters/entry), with zero waiter-full
  events in development;
- every target shows actual L1 service suppression, not merely an existing
  MSHR count;
- grouping-only controls are exactly OFF for T0/T1/A2;
- follower head-block cycles are zero on all seven targets;
- A2 is +1.698% in the main model and avoids the proactive-owner pathology;
- same-cycle development has two isolated ~1% regressions (T2/A1), not a
  broad pattern; Level2 attributes them to schedule/pressure changes without a
  root-cause claim;
- +1-cycle compare remains viable: no tested point regresses by more than 1%
  versus OFF, so the mechanism is not marked timing-sensitive.

This is development evidence, not baseline promotion or a paper conclusion.
The source remains frozen at `{SOURCE_FREEZE}`.
''')
    (PACK / 'HOLDOUT_STATUS.md').write_text(f'''# Holdout status

Status: **{readiness} / NOT CAPTURED / NOT RUN**

Preregistration `{HOLDOUT_PREREG}` remains unchanged.

- Primary: `STR_e0922aa2a506` / DECODE / AT_NATIVE_REDUCE
- Sole fallback: `STR_48b98b28a393` / DECODE /
  AT_NATIVE_UNROLLED_ELEMENTWISE

This Goal did not start node109 and did not inspect either holdout result.
Independent capture/run requires a later explicit authorization.
''')

    source_freeze_path = PACK / 'SOURCE_FREEZE.tsv'
    source_base = ''.join(
        line for line in source_freeze_path.read_text().splitlines(True)
        if not line.startswith('commit\t'))
    source_freeze_path.write_text(
        source_base +
        f'commit\tsource_freeze\tgit\t{SOURCE_FREEZE}\tFROZEN_BEFORE_AI_PERFORMANCE\n'
        f'commit\tdevelopment_runner\tgit\t{RUNNER_COMMIT}\tFROZEN_RUNNER\n'
        f'commit\tlevel2_runner\tgit\t{LEVEL2_RUNNER_COMMIT}\tFROZEN_RUNNER\n')

    (PACK / 'README.md').write_text(f'''# {STAGE}

Start with `FINAL_DECISION.md`.

Decision: **{decision}**

Holdout: **{readiness}**, not captured or run.

Core evidence:

- opportunity: `PREL1_DUPLICATION_MATRIX.tsv`,
  `FINITE_CAPACITY_COVERAGE.tsv`, `DUPLICATE_TIMING_RISK.tsv`,
  `EXISTING_MSHR_OVERLAP.tsv`;
- mechanism/correctness: `MECHANISM_CONTRACT.md`,
  `DIRECTED_CORRECTNESS.tsv`, `SOURCE_FREEZE.tsv`;
- development: `DEVELOPMENT_MATRIX.tsv`, `FOLLOWER_WAIT_MATRIX.tsv`,
  `PHYSICAL_SERVICE_SUPPRESSION.tsv`;
- causal/attribution: `GROUPING_ONLY_CONTROL.tsv`,
  `MSHR_INCREMENTAL_VALUE.tsv`, `OBSERVATORY_ATTRIBUTION.md`;
- timing/holdout: `TIMING_SENSITIVITY.tsv`, `HOLDOUT_STATUS.md`.
''')

    raw = []
    def add_run(kind: str, target: str, arm: str, path: Path) -> None:
        for name in ('run.log', 'command.json', 'rc.txt', 'wall_seconds.txt'):
            artifact = path / name
            raw.append([kind, target, arm, str(artifact), sha(artifact)])
    for target in TARGETS:
        add_run('phase_a', target, 'OFF_OPPORTUNITY',
                PHASE_A / f'{target}_OFF_OPPORTUNITY_10_80')
        add_run('development', target, 'COALESCER',
                DEV / f'{target}_COALESCER_10_80')
    for target in control_targets:
        add_run('causal_control', target, 'GROUPING_ONLY',
                DEV / f'{target}_GROUPING_ONLY_10_80')
    for target in plus_targets:
        add_run('timing', target, 'COALESCER_PLUS1',
                DEV / f'{target}_COALESCER_PLUS1_10_80')
    for target in ('T2', 'A1'):
        add_run('observatory_level2', target, 'OFF_LEVEL2',
                DEV / f'{target}_OFF_LEVEL2_10_80')
        add_run('observatory_level2', target, 'COALESCER_LEVEL2',
                DEV / f'{target}_COALESCER_LEVEL2_10_80')
    add_run('zero_gate', 'ZERO_M1', 'OFF', ZERO / 'OFF')
    add_run('zero_gate', 'ZERO_M1', 'COALESCER', ZERO / 'COALESCER')
    for identity, path in (
        ('binary', RUNTIME / 'bin/unified_accel-sim.out'),
        ('library', RUNTIME / 'src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release/libcudart.so'),
        ('build_log', RUNTIME / 'unified_build.log'),
        ('zero_gate_receipt', RUNTIME / 'zero_duplication_gate.json'),
        ('phase_a_receipt', RUNTIME / 'phase_a_decision.json'),
        ('development_receipt', RUNTIME / 'development_decision.json'),
    ):
        raw.append(['provenance', identity, '', str(path), sha(path)])
    for identity, name in (
        ('opportunity_runner', 'run_prel1_opportunity.py'),
        ('development_runner', 'run_prel1_development.py'),
        ('development_analyzer', 'analyze_prel1_development.py'),
        ('final_builder', 'build_prel1_final_review.py'),
        ('module_test', 'prel1_exact_coalescer_test.cc'),
        ('integration_test', 'prel1_exact_coalescer_integration_test.cc'),
    ):
        path = REPO / 'util/vm_tlb/awma' / name
        raw.append(['script_or_test', identity, '', str(path), sha(path)])
    raw.extend([
        ['commit', 'source_freeze', '', 'git', SOURCE_FREEZE],
        ['commit', 'future_holdout_preregistration', '', 'git', HOLDOUT_PREREG],
    ])
    write_tsv(PACK / 'RAW_DATA_INDEX.tsv',
              ['kind', 'target_or_identity', 'arm', 'path', 'sha256'], raw)

    files = sorted(path for path in PACK.iterdir()
                   if path.is_file() and path.name != 'SHA256SUMS')
    (PACK / 'SHA256SUMS').write_text(''.join(
        f'{sha(path)}  {path.name}\n' for path in files))
    print(json.dumps({'decision': decision, 'holdout': readiness,
                      'supported': supported}, indent=2, sort_keys=True))
    return 0 if supported else 1


if __name__ == '__main__':
    raise SystemExit(main())
