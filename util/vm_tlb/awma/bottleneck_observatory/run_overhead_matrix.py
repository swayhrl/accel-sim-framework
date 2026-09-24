#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path('/root/workspace/accel-sim-framework-awma-bottleneck-observatory-v1')
RUNTIME = Path('/root/awma_bottleneck_observatory_v1_runtime')
RUNNER = REPO / 'util/vm_tlb/awma/bottleneck_observatory/run_bottleneck_observatory.py'
PACK = REPO / 'docs/vm_tlb/review_packs/AWMA_BOTTLENECK_OBSERVATORY_V1'
TARGETS = ('COMBINE', 'T2', 'T1')
LEVELS = (0, 1, 2, 3)


def scalar(text: str, key: str) -> int:
    match = re.search(rf'^\s*{re.escape(key)}\s*=\s*(\d+)', text, re.M)
    if not match:
        raise ValueError(f'missing {key}')
    return int(match.group(1))


def host_metrics(path: Path) -> dict[str, float | int]:
    result: dict[str, float | int] = {}
    for line in path.read_text().splitlines():
        key, value = line.split('=', 1)
        result[key] = int(value) if key in {'max_rss_kb', 'exit_status'} \
            else float(value)
    return result


def run_dir(target: str, level: int, tag: str) -> Path:
    return RUNTIME / 'runs' / target / '10_80' / f'L{level}_{tag}'


def valid_existing(path: Path) -> bool:
    return (path / 'rc.txt').is_file() and (path / 'rc.txt').read_text().strip() == '0'


def execute(target: str, level: int, tag: str) -> None:
    path = run_dir(target, level, tag)
    if valid_existing(path):
        print(json.dumps({'status': 'REUSE', 'run_dir': str(path)}), flush=True)
        return
    command = [sys.executable, str(RUNNER), '--target', target,
               '--translation', '10_80', '--level', str(level), '--tag', tag]
    subprocess.run(command, cwd=REPO, check=True)


def collect() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    tags = [('warmup', 0)] + [(f'm{rep}', rep) for rep in range(1, 4)]
    for target in TARGETS:
        for level in LEVELS:
            for suffix, repetition in tags:
                tag = f'overhead_{suffix}'
                path = run_dir(target, level, tag)
                if not valid_existing(path):
                    continue
                text = (path / 'run.log').read_text(errors='replace')
                host = host_metrics(path / 'host_metrics.txt')
                rows.append({
                    'target': target, 'level': level,
                    'phase': 'warmup' if repetition == 0 else 'measured',
                    'repetition': repetition, 'cycles': scalar(text, 'gpu_sim_cycle'),
                    'instructions': scalar(text, 'gpu_sim_insn'),
                    'cta': scalar(text, 'gpu_tot_issued_cta'),
                    'wall_seconds': host['wall_seconds'],
                    'user_seconds': host['user_seconds'],
                    'system_seconds': host['system_seconds'],
                    'max_rss_kb': host['max_rss_kb'],
                    'output_bytes': int((path / 'output_bytes.txt').read_text()),
                    'run_dir': str(path),
                })
    return rows


def summarize(rows: list[dict[str, object]]) -> None:
    PACK.mkdir(parents=True, exist_ok=True)
    baseline: dict[str, dict[str, float]] = {}
    for target in TARGETS:
        selected = [row for row in rows if row['target'] == target and
                    row['level'] == 0 and row['phase'] == 'measured']
        if len(selected) != 3:
            continue
        baseline[target] = {
            key: sum(float(row[key]) for row in selected) / len(selected)
            for key in ('wall_seconds', 'max_rss_kb', 'output_bytes')}
    for row in rows:
        reference = baseline.get(str(row['target']))
        if reference:
            row['runtime_overhead'] = (
                float(row['wall_seconds']) / reference['wall_seconds'] - 1)
            row['rss_delta_kb'] = (
                float(row['max_rss_kb']) - reference['max_rss_kb'])
            row['output_delta_bytes'] = (
                float(row['output_bytes']) - reference['output_bytes'])
        else:
            row['runtime_overhead'] = ''
            row['rss_delta_kb'] = ''
            row['output_delta_bytes'] = ''
    fields = (
        'target', 'level', 'phase', 'repetition', 'cycles', 'instructions',
        'cta', 'wall_seconds', 'user_seconds', 'system_seconds', 'max_rss_kb',
        'output_bytes', 'runtime_overhead', 'rss_delta_kb',
        'output_delta_bytes', 'run_dir')
    with (PACK / 'OBSERVATORY_OVERHEAD_MATRIX.tsv').open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=fields, delimiter='\t',
                                lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    aggregates = []
    for target in TARGETS:
        for level in LEVELS:
            selected = [row for row in rows if row['target'] == target and
                        row['level'] == level and row['phase'] == 'measured']
            if len(selected) != 3:
                continue
            averages = {key: sum(float(row[key]) for row in selected) / 3
                        for key in ('wall_seconds', 'user_seconds',
                                    'system_seconds', 'max_rss_kb',
                                    'output_bytes')}
            reference = baseline[target]
            aggregates.append({
                'target': target, 'level': level, **averages,
                'runtime_overhead': averages['wall_seconds'] /
                    reference['wall_seconds'] - 1,
                'rss_delta_kb': averages['max_rss_kb'] -
                    reference['max_rss_kb'],
                'output_delta_bytes': averages['output_bytes'] -
                    reference['output_bytes'],
            })
    (PACK / 'OVERHEAD_AGGREGATES.json').write_text(
        json.dumps({'schema': 'AWMA_OBSERVATORY_OVERHEAD_V1',
                    'baseline': baseline, 'aggregates': aggregates},
                   indent=2, sort_keys=True) + '\n')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--summarize-only', action='store_true')
    args = parser.parse_args()
    if not args.summarize_only:
        for target in TARGETS:
            for level in LEVELS:
                execute(target, level, 'overhead_warmup')
            for repetition in range(1, 4):
                for level in LEVELS:
                    execute(target, level, f'overhead_m{repetition}')
    rows = collect()
    summarize(rows)
    print(json.dumps({'rows': len(rows), 'matrix': str(
        PACK / 'OBSERVATORY_OVERHEAD_MATRIX.tsv')}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
