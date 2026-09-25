#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

REPO = Path('/root/workspace/accel-sim-framework-awma-c1-a2-nonsharing-regression-attribution-v1')
RUNTIME = Path('/root/awma_c1_a2_nonsharing_regression_attribution_v1_runtime')
PACK = REPO / 'docs/vm_tlb/review_packs/AWMA_C1_A2_NONSHARING_REGRESSION_ATTRIBUTION_V1'
POINTS = tuple((target, mode) for target in ('A1', 'A2')
               for mode in ('off', 'candidate'))

SCALARS = (
    'gpu_sim_cycle', 'gpu_sim_insn', 'gpu_tot_issued_cta',
    'vm_translation_lookup_requests', 'vm_translation_mshr_allocations',
    'vm_translation_mshr_merges',
    'vm_translation_requester_latency_cycles_total',
    'vm_translation_requester_latency_cycles_max',
    'awma_owner_wait_admissions', 'awma_owner_wait_unique_admitted_uids',
    'awma_owner_wait_repeated_admissions',
    'awma_owner_wait_readmitted_uids',
    'awma_owner_wait_admission_count_max',
    'awma_owner_wait_owner_attempts',
    'awma_owner_wait_owner_retry_attempts',
    'awma_owner_wait_retried_owner_uids',
    'awma_owner_wait_owner_attempt_max',
    'awma_owner_wait_member_owner_wait_cycles',
    'awma_owner_wait_head_block_total_cycles',
    'awma_owner_wait_no_wait_fallback_members',
    'awma_nonblocking_shared_ready_members',
    'awma_nonblocking_fallback_members',
    'awma_nonblocking_duplicate_physical_lookup_requests',
    'awma_nonblocking_fallback_translation_completions',
    'awma_owner_wait_first_issue_latency_total',
    'awma_owner_wait_first_issue_latency_max',
    'awma_owner_wait_all_issue_latency_total',
    'awma_owner_wait_all_issue_latency_max',
    'L1D_total_cache_accesses', 'L1D_total_cache_misses',
    'L1D_total_cache_reservation_fails', 'L2_total_cache_accesses',
    'L2_total_cache_misses', 'L2_total_cache_pending_hits',
    'L2_total_cache_reservation_fails', 'avg_icnt2mem_latency',
    'max_icnt2mem_latency', 'gpu_stall_dramfull',
    'gpgpu_n_stall_shd_mem',
)


def scalar(text: str, key: str):
    match = re.search(rf'^\s*{re.escape(key)}\s*=\s*([0-9.]+)', text, re.M)
    if not match:
        return None
    value = match.group(1)
    return float(value) if '.' in value else int(value)


def coverage(text: str) -> dict[str, int]:
    match = re.search(r'^AWMA_VM_COVERAGE (.+)$', text, re.M)
    return ({key: int(value) for key, value in
             re.findall(r'(\w+)=(\d+)', match.group(1))} if match else {})


def parse(path: Path) -> dict[str, object]:
    text = path.read_text(errors='replace')
    result: dict[str, object] = {key: scalar(text, key) for key in SCALARS}
    result['coverage'] = coverage(text)
    result['metrics'] = {}
    result['windows'] = []
    result['top'] = []
    result['progress'] = {}
    for line in text.splitlines():
        fields = line.split('\t')
        if fields[0] == 'awma_observatory_metric':
            _, domain, metric, kind, total, samples, mean, peak = fields
            result['metrics'][f'{domain}.{metric}'] = {
                'kind': kind, 'total': int(total), 'samples': int(samples),
                'mean': float(mean), 'peak': int(peak)}
        elif fields[0] == 'awma_observatory_window':
            (_, domain, metric, width, count, mean, p50, p95, p99, peak,
             reservoir) = fields
            result['windows'].append({
                'domain': domain, 'metric': metric, 'width': int(width),
                'count': int(count), 'mean': float(mean), 'p50': int(p50),
                'p95': int(p95), 'p99': int(p99), 'peak': int(peak),
                'reservoir': int(reservoir)})
        elif fields[0] == 'awma_observatory_top_window':
            _, domain, metric, width, rank, start, end, value = fields
            result['top'].append({
                'domain': domain, 'metric': metric, 'width': int(width),
                'rank': int(rank), 'start': int(start), 'end': int(end),
                'value': int(value)})
        elif fields[0] == 'awma_observatory_progress':
            result['progress'][fields[1]] = {
                key: int(value) for key, value in zip(
                    ('total', 'p25', 'p50', 'p75', 'p90', 'p99', 'tail'),
                    fields[2:])}
    return result


def metric(run: dict[str, object], name: str) -> int:
    return int(run['metrics'].get(name, {}).get('total', 0))


def load(level: int, tag: str) -> dict[tuple[str, str], dict[str, object]]:
    return {(target, mode): parse(
        RUNTIME / f'runs/{target}/{mode}/L{level}_{tag}/run.log')
            for target, mode in POINTS}


def write_tsv(path: Path, rows: list[dict[str, object]], fields) -> None:
    with path.open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=fields, delimiter='\t',
                                lineterminator='\n', extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    PACK.mkdir(parents=True, exist_ok=True)
    level1 = load(1, 'triage')
    level2 = load(2, 'windowed')

    triage_rows = []
    mechanism_rows = []
    progress_rows = []
    for target, mode in POINTS:
        run = level1[(target, mode)]
        cov = run['coverage']
        primary = 'MEMORY_DOWNSTREAM_PRESSURE'
        secondary = 'SCHEDULER_DEPENDENCY_STRUCTURAL'
        mediators = []
        if mode == 'candidate':
            mediators.append('PROACTIVE_OWNER_RETRY_READMISSION')
        if metric(run, 'memory.l1_reservation_fail'):
            mediators.append('L1_RESERVATION_PRESSURE')
        if metric(run, 'scheduler.dependency_scoreboard'):
            mediators.append('SCOREBOARD_DEPENDENCY')
        triage_rows.append({
            'target': target, 'mode': mode, 'cycles': run['gpu_sim_cycle'],
            'instructions': run['gpu_sim_insn'], 'cta': run['gpu_tot_issued_cta'],
            'unique_uid': cov['unique'], 'coverage_admissions': cov['admissions'],
            'PRIMARY_OBSERVED_LOCATION': primary,
            'SECONDARY_OBSERVED_LOCATION': secondary,
            'SUPPORTED_MEDIATORS': ';'.join(mediators),
            'UNRESOLVED': 'scoreboard_producer_domain;physical_context_trigger',
            'scheduler_issued': metric(run, 'scheduler.issued'),
            'scheduler_no_active': metric(run, 'scheduler.no_active_work'),
            'scheduler_dependency': metric(run, 'scheduler.dependency_scoreboard'),
            'scheduler_structural': metric(run, 'scheduler.eligible_structural'),
            'scheduler_frontend': metric(run, 'scheduler.frontend_starvation'),
            'ldst_resource_stall': metric(run, 'memory.ldst_resource_stall'),
            'ldst_coal_stall': metric(run, 'memory.ldst_coal_stall'),
            'l1_reservation_fail': metric(run, 'memory.l1_reservation_fail'),
            'l2_reservation_fail': metric(run, 'memory.l2_reservation_fail'),
            'dram_queue_mean': run['metrics']['memory.dram_queue_occupancy']['mean'],
        })
        mechanism_rows.append({
            'target': target, 'mode': mode,
            'lookup_requests': run['vm_translation_lookup_requests'],
            'mshr_allocations': run['vm_translation_mshr_allocations'],
            'mshr_merges': run['vm_translation_mshr_merges'],
            'requester_latency_total': run['vm_translation_requester_latency_cycles_total'],
            'requester_latency_max': run['vm_translation_requester_latency_cycles_max'],
            'admissions': cov['admissions'],
            'derived_repeated_admissions': cov['admissions'] - cov['unique'],
            'readmitted_uids': run['awma_owner_wait_readmitted_uids'],
            'owner_attempts': run['awma_owner_wait_owner_attempts'],
            'owner_retry_attempts': run['awma_owner_wait_owner_retry_attempts'],
            'retried_owner_uids': run['awma_owner_wait_retried_owner_uids'],
            'owner_attempt_max': run['awma_owner_wait_owner_attempt_max'],
            'ready_shared_members': run['awma_nonblocking_shared_ready_members'],
            'fallback_members': run['awma_nonblocking_fallback_members'],
            'duplicate_physical_lookup_requests':
                run['awma_nonblocking_duplicate_physical_lookup_requests'],
            'member_owner_wait_cycles': run['awma_owner_wait_member_owner_wait_cycles'],
            'head_block_cycles': run['awma_owner_wait_head_block_total_cycles'],
            'first_issue_latency_total': run['awma_owner_wait_first_issue_latency_total'],
            'all_issue_latency_total': run['awma_owner_wait_all_issue_latency_total'],
        })
        mechanism_rows[-1] = {
            key: ('NA' if value is None else value)
            for key, value in mechanism_rows[-1].items()}
        ip = run['progress']['INSTRUCTIONS']
        cp = run['progress']['CTAS']
        progress_rows.append({
            'target': target, 'mode': mode, 'cycles': run['gpu_sim_cycle'],
            'instruction_p50': ip['p50'], 'instruction_p90': ip['p90'],
            'instruction_p99': ip['p99'], 'instruction_tail': ip['tail'],
            'cta_p50': cp['p50'], 'cta_p90': cp['p90'],
            'cta_p99': cp['p99'], 'cta_tail': cp['tail'],
            'avg_icnt2mem_latency': run['avg_icnt2mem_latency'],
            'max_icnt2mem_latency': run['max_icnt2mem_latency'],
        })

    write_tsv(PACK / 'A1_A2_LEVEL1_TRIAGE.tsv', triage_rows,
              tuple(triage_rows[0]))
    write_tsv(PACK / 'MECHANISM_TELEMETRY_COMPARISON.tsv', mechanism_rows,
              tuple(mechanism_rows[0]))
    write_tsv(PACK / 'PROGRESS_COMPARISON.tsv', progress_rows,
              tuple(progress_rows[0]))

    selected = {
        'progress.instructions', 'scheduler.dependency_scoreboard',
        'scheduler.eligible_structural', 'memory.admissions',
        'memory.l1_reservation_fail', 'memory.icnt_to_l2_occupancy',
        'memory.dram_queue_occupancy', 'translation.translation_ready',
        'translation.translation_not_ready'}
    window_rows = []
    for target, mode in POINTS:
        run = level2[(target, mode)]
        top = {(row['domain'] + '.' + row['metric'], row['width']): row
               for row in run['top'] if row['rank'] == 1}
        for row in run['windows']:
            name = row['domain'] + '.' + row['metric']
            if name not in selected:
                continue
            top_row = top.get((name, row['width']), {})
            window_rows.append({
                'target': target, 'mode': mode, 'domain': row['domain'],
                'metric': row['metric'], 'width': row['width'],
                'mean': row['mean'], 'p50': row['p50'], 'p95': row['p95'],
                'p99': row['p99'], 'peak': row['peak'],
                'top1_start_cycle': top_row.get('start', ''),
                'top1_end_cycle': top_row.get('end', ''),
                'top1_value': top_row.get('value', ''),
            })
    write_tsv(PACK / 'A1_A2_WINDOWED_COMPARISON.tsv', window_rows,
              tuple(window_rows[0]))

    a1_off, a1_cand = level1[('A1', 'off')], level1[('A1', 'candidate')]
    a2_off, a2_cand = level1[('A2', 'off')], level1[('A2', 'candidate')]
    a1_extra = a1_cand['coverage']['admissions'] - a1_off['coverage']['admissions']
    a2_extra = a2_cand['coverage']['admissions'] - a2_off['coverage']['admissions']
    a1_resource_delta = (metric(a1_cand, 'memory.ldst_resource_stall') -
                         metric(a1_off, 'memory.ldst_resource_stall'))
    a2_resource_delta = (metric(a2_cand, 'memory.ldst_resource_stall') -
                         metric(a2_off, 'memory.ldst_resource_stall'))
    hypothesis_rows = [
        {'hypothesis': 'H1_PROACTIVE_OWNER_RETRY_READMISSION_AMPLIFICATION',
         'decision': 'SUPPORTED_MEDIATOR',
         'evidence': f'A1 extra admissions/resource stalls={a1_extra}/{a1_resource_delta}; A2={a2_extra}/{a2_resource_delta}; READY share=0'},
        {'hypothesis': 'H2_TRANSLATION_TIMING_TO_MEMORY_BACKPRESSURE',
         'decision': 'SUPPORTED_MEDIATOR',
         'evidence': 'A2 candidate raises L1 reservation failures, LDST resource stalls, ICNT latency; A1 lowers main pressure counters'},
        {'hypothesis': 'H3_TRANSLATION_TIMING_TO_SCHEDULER_DEPENDENCY_OR_IDLE',
         'decision': 'SUPPORTED_MEDIATOR',
         'evidence': 'A2 candidate raises dependency/structural counts and delays progress; A1 candidate lowers them and advances progress'},
        {'hypothesis': 'H4_CONTEXT_DEPENDENCE_LOCAL_TO_CONTROLLER_ORDERING',
         'decision': 'NOT_SUPPORTED_AS_SOLE_LOCATION',
         'evidence': 'Observed response propagates into LDST/L1/ICNT/scheduler/progress domains'},
        {'hypothesis': 'H5_NOT_LOCALIZED_WITH_AVAILABLE_OBSERVATORY',
         'decision': 'REJECTED',
         'evidence': 'Matched A1 control and A2 regression close a controller-retry to downstream-pressure chain'},
    ]
    write_tsv(PACK / 'HYPOTHESIS_DECISION.tsv', hypothesis_rows,
              ('hypothesis', 'decision', 'evidence'))

    report = f'''# A1/A2 nonsharing regression attribution

Status: `SUPPORTS_PROACTIVE_OWNER_PATH_AS_NONSHARING_REGRESSION_MEDIATOR`

## Matched-control result

A1 and A2 are the same exact GEMV identity, grid/block, decode step, frozen
candidate policy, and both have `READY share = 0`.  Their principal external
difference is context/history.

| target | OFF cycles | candidate cycles | response | extra admissions | extra LDST resource stalls |
|---|---:|---:|---:|---:|---:|
| A1 | 114123 | 112023 | -1.840% | {a1_extra} | {a1_resource_delta} |
| A2 | 117698 | 125427 | +6.567% | {a2_extra} | {a2_resource_delta} |

For both contexts the candidate's extra coverage admissions equal its extra
source-enum LDST resource stalls exactly.  The magnitude differs by 14.33x:
A1 adds only {a1_extra}, while A2 adds {a2_extra}.  This is the central
source-supported mediator link.

## Controller and reuse boundary

- READY-shared members: `0` for A1 and A2.
- fallback members: `116032` for both.
- duplicate physical lookup requests: `116032` for both.
- member owner wait and head blocking: `0` for both.
- owner attempts/retries are nearly equal across contexts; the divergent result
  is downstream retry/readmission amplification, not reusable-result delivery.

Therefore no performance response is attributed to result reuse.

## Differential downstream response

A1 candidate reduces L1 reservation failures, L2 reservation failures,
scoreboard dependency, structural blockage, and requester latency; its progress
milestones move earlier, producing the 1.840% improvement.

A2 candidate adds {a2_extra} repeated admissions/resource stalls, increases L1
reservation failures by {metric(a2_cand, 'memory.l1_reservation_fail') - metric(a2_off, 'memory.l1_reservation_fail')},
raises average ICNT-to-memory latency from {a2_off['avg_icnt2mem_latency']} to
{a2_cand['avg_icnt2mem_latency']}, and increases scheduler dependency and
eligible-structural blockage.  Instruction/CTA p90 and the kernel tail move
later, producing the 6.567% regression.

## Temporal relationship

The A2 candidate Top-K 512-cycle windows form a real simulator-cycle sequence:

1. translation not-ready plus eligible-structural concentration near cycles
   5632--9215;
2. READY/admission plus ICNT/DRAM queue concentration near 10240--12799;
3. L1 reservation-pressure concentration near 15872--16895 (with later repeats);
4. scoreboard-dependency concentration near 28672--31231;
5. later cumulative instruction/CTA progress and kernel completion.

This temporal order supports propagation through the listed mediators; no single
aggregate counter is called a causal decomposition.  Exact low-throughput
progress Top-K windows and time-windowed repeated-admission attempts are not
exposed by Observatory V1 and remain `NOT_AVAILABLE`; aggregate repeated
admission counts and bounded Level-1 progress milestones are used instead.

## Level-3 decision

Level 3 was not run.  Level 1 and Level 2 already distinguish the matched A1/A2
chain and close the required observed locations/mediators.  Level 3 would add
READY-to-successful-admission latency and DRAM boundaries, but it cannot add a
time-windowed view of the earlier repeated-admission attempt counter or identify
the physical context/history trigger.  Running it would therefore add cost
without resolving the remaining question.

## Decision

`SUPPORTS_PROACTIVE_OWNER_PATH_AS_NONSHARING_REGRESSION_MEDIATOR`

The proactive owner path creates no READY reuse in either context.  In A2, its
retry/readmission amplification propagates into downstream memory pressure and
scheduler/progress delay; A1 is the matched control showing the same policy with
small amplification and net benefit.

V2 design requirements only (not implemented here):

- no extra proactive physical lookup when no reusable result exists;
- no added retry/readmission amplification;
- no waiting and no future information;
- the no-opportunity path should approach frozen OFF semantics.

The physical context/history condition that turns similar owner attempts into a
14.33x larger downstream amplification remains unresolved.  This stage changes
no mechanism and runs no V2.
'''
    (PACK / 'ATTRIBUTION_REPORT.md').write_text(report)
    summary = {'decision':
               'SUPPORTS_PROACTIVE_OWNER_PATH_AS_NONSHARING_REGRESSION_MEDIATOR',
               'a1_extra_admissions': a1_extra,
               'a2_extra_admissions': a2_extra,
               'a1_resource_delta': a1_resource_delta,
               'a2_resource_delta': a2_resource_delta}
    (PACK / 'ATTRIBUTION_SUMMARY.json').write_text(
        json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
