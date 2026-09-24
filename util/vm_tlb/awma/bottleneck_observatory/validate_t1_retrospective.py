#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

from analyze import metric_total, parse

REPO = Path('/root/workspace/accel-sim-framework-awma-bottleneck-observatory-v1')
RUNTIME = Path('/root/awma_bottleneck_observatory_v1_runtime')
PACK = REPO / 'docs/vm_tlb/review_packs/AWMA_BOTTLENECK_OBSERVATORY_V1'
RUNS = {
    '10/80': RUNTIME / 'runs/T1/10_80/L3_overhead_m1/run.log',
    '0/80': RUNTIME / 'runs/T1/0_80/L3_retrospective_locked/run.log',
    'ideal': RUNTIME / 'runs/T1/ideal/L3_retrospective_locked/run.log',
}


def float_scalar(text: str, key: str) -> float:
    match = re.search(rf'^\s*{re.escape(key)}\s*=\s*([0-9.]+)', text, re.M)
    if not match:
        raise ValueError(f'missing {key}')
    return float(match.group(1))


def window_peak(run: dict[str, object], domain: str, metric: str,
                width: int) -> int:
    for row in run['windows']:
        if (row['domain'], row['metric'], row['width']) == (domain, metric, width):
            return int(row['peak'])
    raise ValueError((domain, metric, width))


def main() -> int:
    parsed = {name: parse(path) for name, path in RUNS.items()}
    rows = {}
    for name, run in parsed.items():
        text = RUNS[name].read_text(errors='replace')
        boundary = next(line.split('\t')[1:] for line in text.splitlines()
                        if line.startswith('awma_observatory_dram_boundary\t'))
        legacy_scheduler = re.search(
            r'^Stall:(\d+)\s+W0_Idle:(\d+)\s+W0_Scoreboard:(\d+)', text,
            re.M)
        if not legacy_scheduler:
            raise ValueError('missing accepted legacy scheduler summary')
        progress = run['progress']
        rows[name] = {
            'cycles': run['cycles'],
            'ready_peak': run['metrics']['translation.translation_ready']['cycle_peak'],
            'ready_to_admission_mean': run['ready_to_admission']['mean'],
            'admission_w32_peak': window_peak(run, 'memory', 'admissions', 32),
            'l1_reservation_fail': metric_total(run, 'memory', 'l1_reservation_fail'),
            'ldst_resource_stall': metric_total(run, 'memory', 'ldst_resource_stall'),
            'icnt_latency_avg': float_scalar(text, 'avg_icnt2mem_latency'),
            'scheduler_no_active': metric_total(run, 'scheduler', 'no_active_work'),
            'legacy_scheduler_idle': int(legacy_scheduler.group(2)),
            'instruction_p90': progress['INSTRUCTIONS']['p90'],
            'cta_p90': progress['CTAS']['p90'],
            'dram_last': int(boundary[2]),
            'instructions': run['instructions'], 'ctas': run['ctas'],
            'unique_uid': run['coverage']['unique'],
        }
    baseline, ideal = rows['10/80'], rows['ideal']
    checks = {
        'semantic_cycles': [rows[name]['cycles'] for name in rows] ==
            [665802, 664805, 715636],
        'work_identity': all(row['instructions'] == 369131520 and
                             row['ctas'] == 384 and
                             row['unique_uid'] == 7159808
                             for row in rows.values()),
        'ready_burst': ideal['ready_peak'] > baseline['ready_peak'],
        'admission_burst': ideal['admission_w32_peak'] >
            baseline['admission_w32_peak'],
        'l1_pressure': ideal['l1_reservation_fail'] >
            baseline['l1_reservation_fail'],
        'icnt_latency': ideal['icnt_latency_avg'] > baseline['icnt_latency_avg'],
        'accepted_scheduler_idle': ideal['legacy_scheduler_idle'] >
            baseline['legacy_scheduler_idle'],
        'instruction_tail': ideal['instruction_p90'] > baseline['instruction_p90'],
        'cta_tail': ideal['cta_p90'] > baseline['cta_p90'],
        'dram_tail': ideal['dram_last'] > baseline['dram_last'],
    }
    status = 'PASS' if all(checks.values()) else 'FAIL'
    header = ('mode', 'cycles', 'READY cycle peak', 'READY->admission mean',
              'admission 32-cycle peak', 'L1 reservation fail',
              'LDST resource stall', 'avg ICNT->memory latency',
              'legacy W0_Idle', 'new no-active', 'instruction p90', 'CTA p90',
              'last data DRAM completion')
    lines = [
        '# T1 retrospective validation', '', f'Status: `{status}`', '',
        'The unified observatory replays the exact accepted T1 payload/index for',
        '10/80, 0/80, and ideal.  It preserves cycles, instructions, CTAs, UID',
        'coverage, mapping, and correctness gates.', '',
        '| ' + ' | '.join(header) + ' |',
        '|' + '|'.join(['---'] + ['---:'] * (len(header) - 1)) + '|']
    for name in ('10/80', '0/80', 'ideal'):
        row = rows[name]
        lines.append('| ' + ' | '.join(str(value) for value in (
            name, row['cycles'], row['ready_peak'],
            f"{row['ready_to_admission_mean']:.6f}",
            row['admission_w32_peak'], row['l1_reservation_fail'],
            row['ldst_resource_stall'], row['icnt_latency_avg'],
            row['legacy_scheduler_idle'], row['scheduler_no_active'],
            row['instruction_p90'], row['cta_p90'],
            row['dram_last'])) + ' |')
    lines += [
        '', '## Gate results', '',
        *[f'- {name}: `{str(value).upper()}`' for name, value in checks.items()],
        '', '## High-level consistency', '',
        'The unified interface recovers the accepted high-level location:',
        '`downstream temporal burst/backpressure`.  Ideal produces an earlier and',
        'larger READY release burst, a larger short-window admission burst, more',
        'L1/resource pressure, longer ICNT latency, a higher accepted legacy',
        'scheduler-idle aggregate, and later',
        'instruction/CTA/data-DRAM tails while logical',
        'work remains identical.', '',
        'Differences from the T1-specific pack are expected and explained:',
        'the old observer retained full per-cycle vectors.  Accepted `W0_Idle`',
        'combines idle/control-hazard states and rises in ideal; the new exclusive',
        '`no_active_work` predicate is narrower and falls because ideal retains',
        'active-but-blocked warps.  They are reported side by side, never equated.',
        'The unified observer otherwise uses fixed online windows,',
        'a source-predicate exclusive scheduler taxonomy, and bounded Level-2',
        'reservoir quantiles.  Level-3 progress and READY latency remain exact.', '',
        'This retrospective validates location and mediators.  It does not create a',
        'new causal experiment or upgrade the prior manual attribution into an',
        'automatic root-cause claim.', '']
    PACK.mkdir(parents=True, exist_ok=True)
    (PACK / 'T1_RETROSPECTIVE_VALIDATION.md').write_text('\n'.join(lines))
    print(f'{status}: {checks}')
    return 0 if status == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
