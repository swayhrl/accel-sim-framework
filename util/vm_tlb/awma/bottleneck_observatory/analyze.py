#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SCHEDULER_CLASSES = (
    'issued', 'no_active_work', 'no_eligible_work',
    'dependency_scoreboard', 'sync_barrier', 'sync_membar',
    'frontend_starvation', 'eligible_structural', 'other')


def scalar(text: str, key: str, cast=int):
    match = re.search(rf'^\s*{re.escape(key)}\s*=\s*([^\s]+)', text, re.M)
    return cast(match.group(1)) if match else None


def parse(path: Path) -> dict[str, object]:
    text = path.read_text(errors='replace')
    metrics: dict[str, dict[str, float | int | str]] = {}
    windows: list[dict[str, float | int | str]] = []
    top_windows: list[dict[str, int | str]] = []
    for line in text.splitlines():
        fields = line.split('\t')
        if fields[0] == 'awma_observatory_metric':
            _, domain, metric, kind, total, samples, mean, peak = fields
            metrics[f'{domain}.{metric}'] = {
                'domain': domain, 'metric': metric, 'kind': kind,
                'total': int(total), 'samples': int(samples),
                'mean': float(mean), 'cycle_peak': int(peak)}
        elif fields[0] == 'awma_observatory_window':
            (_, domain, metric, width, count, mean, p50, p95, p99, peak,
             reservoir) = fields
            windows.append({
                'domain': domain, 'metric': metric, 'width': int(width),
                'count': int(count), 'mean': float(mean), 'p50': int(p50),
                'p95': int(p95), 'p99': int(p99), 'peak': int(peak),
                'reservoir': int(reservoir)})
        elif fields[0] == 'awma_observatory_top_window':
            _, domain, metric, width, rank, start, end, value = fields
            top_windows.append({
                'domain': domain, 'metric': metric, 'width': int(width),
                'rank': int(rank), 'start_cycle': int(start),
                'end_cycle': int(end), 'value': int(value)})
    coverage = re.search(r'^AWMA_VM_COVERAGE (.+)$', text, re.M)
    coverage_values = ({key: int(value) for key, value in
                        re.findall(r'(\w+)=(\d+)', coverage.group(1))}
                       if coverage else {})
    ready = next((line.split('\t')[1:] for line in text.splitlines()
                  if line.startswith('awma_observatory_ready_to_admission\t')),
                 None)
    progress = {}
    for line in text.splitlines():
        if not line.startswith('awma_observatory_progress\t'):
            continue
        fields = line.split('\t')
        progress[fields[1]] = {
            key: int(value) for key, value in zip(
                ('total', 'p25', 'p50', 'p75', 'p90', 'p99', 'tail'),
                fields[2:])}
    result: dict[str, object] = {
        'path': str(path), 'cycles': scalar(text, 'gpu_sim_cycle'),
        'instructions': scalar(text, 'gpu_sim_insn'),
        'ctas': scalar(text, 'gpu_tot_issued_cta'),
        'level': scalar(text, 'awma_observatory_level'),
        'metrics': metrics, 'windows': windows, 'top_windows': top_windows,
        'coverage': coverage_values, 'progress': progress,
    }
    if ready:
        result['ready_to_admission'] = {
            key: cast(value) for key, cast, value in zip(
                ('count', 'missing', 'repeat_observations', 'outstanding',
                 'mean', 'p50', 'p95', 'p99', 'max'),
                (int, int, int, int, float, int, int, int, int), ready)}
    return result


def metric_total(run: dict[str, object], domain: str, metric: str) -> int:
    value = run['metrics'].get(f'{domain}.{metric}')
    return int(value['total']) if value else 0


def metric_mean(run: dict[str, object], domain: str, metric: str) -> float:
    value = run['metrics'].get(f'{domain}.{metric}')
    return float(value['mean']) if value else 0.0


def diagnose(run: dict[str, object]) -> dict[str, object]:
    dependency = metric_total(run, 'scheduler', 'dependency_scoreboard')
    structural = metric_total(run, 'scheduler', 'eligible_structural')
    sync = (metric_total(run, 'scheduler', 'sync_barrier') +
            metric_total(run, 'scheduler', 'sync_membar'))
    frontend = metric_total(run, 'scheduler', 'frontend_starvation')
    memory_stalls = sum(metric_total(run, 'memory', name) for name in (
        'ldst_resource_stall', 'ldst_coal_stall', 'ldst_icnt_stall',
        'ldst_data_port_stall', 'ldst_other_stall'))
    cache_pressure = (
        metric_total(run, 'memory', 'l1_reservation_fail') +
        metric_total(run, 'memory', 'l2_reservation_fail'))
    memory_pressure = (
        cache_pressure +
        metric_total(run, 'memory', 'ldst_resource_stall') +
        metric_total(run, 'memory', 'ldst_icnt_stall'))
    dram_queue = metric_mean(run, 'memory', 'dram_queue_occupancy')

    scheduler_candidates = {
        'SCHEDULER_DEPENDENCY_SCOREBOARD': dependency,
        'SCHEDULER_ELIGIBLE_STRUCTURAL': structural,
        'SYNC_BARRIER_MEMBAR': sync,
        'FRONTEND_STARVATION': frontend,
    }
    scheduler_location, scheduler_value = max(
        scheduler_candidates.items(), key=lambda item: item[1])

    if cache_pressure or dram_queue >= 1.0:
        primary = 'MEMORY_DOWNSTREAM_PRESSURE'
        secondary = scheduler_location if scheduler_value else 'UNRESOLVED'
    elif scheduler_value > 2 * max(memory_stalls, 1):
        primary = f'NOT_MEMORY_DOMINATED:{scheduler_location}'
        secondary = 'MEMORY_PIPELINE_STALLS' if memory_stalls else 'UNRESOLVED'
    elif scheduler_value:
        primary = scheduler_location
        secondary = 'UNRESOLVED'
    else:
        primary = 'UNRESOLVED'
        secondary = 'UNRESOLVED'

    mediators = []
    ready = run.get('ready_to_admission', {})
    if float(ready.get('mean', 0)) > 0 or int(ready.get('p95', 0)) > 0:
        mediators.append('TRANSLATION_READY_TIMING_OBSERVED')
    if metric_total(run, 'memory', 'l1_reservation_fail'):
        mediators.append('L1_RESERVATION_PRESSURE')
    if metric_total(run, 'memory', 'ldst_icnt_stall'):
        mediators.append('ICNT_BACKPRESSURE')
    if dram_queue >= 1.0:
        mediators.append('DRAM_QUEUE_OCCUPANCY')
    if dependency:
        mediators.append('SCOREBOARD_DEPENDENCY')
    if sync:
        mediators.append('BARRIER_OR_MEMBAR_WAIT')

    return {
        'PRIMARY_OBSERVED_LOCATION': primary,
        'SECONDARY_OBSERVED_LOCATION': secondary,
        'SUPPORTED_MEDIATORS': mediators,
        'NOT_SUPPORTED': [],
        'UNRESOLVED': [
            'CAUSE_REQUIRES_CONTROLLED_EXPERIMENT_OR_MANUAL_DIRECTIONAL_ATTRIBUTION'],
        'evidence': {
            'scheduler_dependency': dependency,
            'scheduler_structural': structural, 'scheduler_sync': sync,
            'scheduler_frontend': frontend, 'memory_stalls': memory_stalls,
            'cache_pressure': cache_pressure, 'memory_pressure': memory_pressure,
            'dram_queue_mean': dram_queue,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('logs', nargs='+', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    runs = []
    for path in args.logs:
        parsed = parse(path)
        parsed['diagnosis'] = diagnose(parsed)
        runs.append(parsed)
    result = {
        'schema': 'AWMA_BOTTLENECK_OBSERVATORY_ANALYSIS_V1',
        'cause_policy': 'NO_AUTOMATIC_ROOT_CAUSE', 'runs': runs}
    rendered = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    else:
        print(rendered, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
