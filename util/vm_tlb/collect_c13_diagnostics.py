#!/usr/bin/env python3
"""Collect C13 diagnostics from terminal immutable logs, without replaying.

This intentionally has no simulator invocation path.  It consumes only C13
result directories, the accepted C12 terminal evidence, and the accepted
operator-aware map.  A C13 arm is admitted to derived results only after its
own terminal validator says PASS and its raw-log conservation can be repeated
against the frozen operator map.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
C12 = Path('/workspace/worktrees/accel-sim-vm-m4b-speculative')
C12_PACK = C12 / 'docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_C5_FULL_ROI_FAIR_PERFORMANCE'
OP_ROOT = Path('/workspace/worktrees/accel-sim-vm-m4b-operator-aware')
OP_PACK = OP_ROOT / 'docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_OPERATOR_AWARE_CHARACTERIZATION'
RESULT_ROOT = Path('/workspace/vm-m4b-c13-diagnostics/results')
PACK = ROOT / 'docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C13_MINIMAL_DIAGNOSTICS'
HANDOFF = ROOT / 'docs/vm_tlb/codex_handoff/c13_diagnostics/LATEST_REPORT.md'
MANIFEST = PACK / 'C13_COMMAND_MANIFEST.tsv'
MAP = OP_PACK / 'KERNEL_OPERATOR_MAP.tsv'
OP_SCRIPT = OP_ROOT / 'util/vm_tlb/analyze_c12_operator_aware.py'

sys.path.insert(0, str(OP_SCRIPT.parent))
import analyze_c12_operator_aware as op  # accepted hardened raw-log parser

PRIMARY = ('C13-LAT-P8', 'C13-LAT-P9', 'C13-LAT-D11', 'C13-CAP-P320',
           'C13-CAP-P768S10', 'C13-SEL-P10', 'C13-SEL-D10')
CONTROLS = ('C13-SEL-P10-CTRL-NEWBIN', 'C13-SEL-D10-CTRL-NEWBIN')
COUNTER = re.compile(r'^([A-Za-z0-9_]+)\s*=\s*(-?[0-9]+(?:\.[0-9]+)?)\s*$')
RSS = re.compile(r'Maximum resident set size \(kbytes\):\s*(\d+)')
ELAPSED = re.compile(r'Elapsed \(wall clock\) time .*:\s*([^\n]+)')

# C12 results use unprefixed schema names. C13 terminal log counters retain
# the simulator names. This canonical set is deliberately unit-preserving.
GLOBAL_METRICS = (
    'gpu_tot_sim_cycle', 'gpu_tot_sim_insn', 'gpu_tot_ipc',
    'vm_l1_tlb_accesses', 'vm_l1_tlb_misses', 'vm_l2_tlb_accesses',
    'vm_l2_tlb_misses', 'vm_l2_tlb_port_stalls',
    'vm_translation_mshr_allocations', 'vm_translation_mshr_merges',
    'vm_translation_mshr_full_events', 'vm_translation_walk_starts',
    'vm_pte_requests', 'vm_pte_l2_only_responses', 'vm_pte_dram_responses',
    'vm_translation_requester_latency_cycles_total',
    'vm_translation_requester_mshr_wait_cycles_total',
    'vm_pte_memory_wait_cycles_total', 'vm_pwc_accesses', 'vm_pwc_hits',
    'vm_pwc_misses', 'vm_weight_segment_lookup_attempts',
    'vm_weight_segment_hits', 'vm_weight_segment_l2_suppressed',
)
C12_NAME = {
    'vm_translation_walk_starts': 'vm_translation_walk_starts',
    'vm_weight_segment_lookup_attempts': 'segment_lookup_attempts',
    'vm_weight_segment_hits': 'segment_hits',
    'vm_weight_segment_l2_suppressed': 'segment_l2_suppressed',
}


def fail(message: str) -> None:
    raise SystemExit('C13 COLLECT FAIL: ' + message)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline='') as source:
        return list(csv.DictReader(source, delimiter='\t'))


def write_tsv(path: Path, fields: Iterable[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(fields)
    with path.open('w', newline='') as sink:
        writer = csv.DictWriter(sink, fieldnames=fields, delimiter='\t',
                                lineterminator='\n', extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow({key: '' if row.get(key) is None else row.get(key, '') for key in fields})


def number(value: str | int | float | None) -> int | float | None:
    if value in (None, '', 'NOT_EMITTED', 'NONE'):
        return None
    text = str(value)
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return None


def fnum(value: int | float | None) -> str:
    if value is None:
        return 'NOT_EMITTED'
    if isinstance(value, int) or float(value).is_integer():
        return str(int(value))
    return f'{float(value):.12g}'


def parse_final_counters(log: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in log.read_text(errors='strict').splitlines():
        match = COUNTER.match(line)
        if match:
            values[match.group(1)] = match.group(2)
    return values


def elapsed_seconds(value: str) -> float | None:
    # GNU time prints either h:mm:ss or m:ss. This is management telemetry,
    # never an architectural result.
    try:
        parts = [float(x) for x in value.strip().split(':')]
    except ValueError:
        return None
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return None


def resource_time(log: Path) -> tuple[str, str]:
    text = log.read_text(errors='replace')
    rss = RSS.search(text)
    elapsed = ELAPSED.search(text)
    return (rss.group(1) if rss else 'NOT_EMITTED',
            fnum(elapsed_seconds(elapsed.group(1))) if elapsed else 'NOT_EMITTED')


def c12_rows() -> dict[str, dict[str, Any]]:
    status = {(r['roi'], r['arm'], r['lseg']): r
              for r in read_tsv(C12_PACK / 'ARM_STATUS.tsv') if r['terminal_status'] == 'PASS'}
    results = {(r['roi'], r['arm'], r['lseg']): r
               for r in read_tsv(C12_PACK / 'ARM_RESULTS.tsv') if r['terminal_status'] == 'PASS'}
    needed = [('prefill', 'F0', 'NONE'), ('prefill', 'F7', '5'),
              ('prefill', 'F7', '10'), ('prefill', 'F7', '20'),
              ('decode1', 'F0', 'NONE'), ('decode1', 'F7', '5'),
              ('decode1', 'F7', '10'), ('decode1', 'F7', '20')]
    output: dict[str, dict[str, Any]] = {}
    for key in needed:
        if key not in status or key not in results:
            fail('missing immutable C12 anchor %s' % (key,))
        state, result = status[key], results[key]
        raw = Path(state['run_dir']) / 'run.log'
        if not raw.is_file() or sha(raw) != state['raw_log_sha256']:
            fail('immutable C12 raw-log SHA mismatch %s' % (key,))
        ident = 'C12-%s-%s-L%s' % (key[0].upper(), key[1], key[2])
        output[ident] = {
            'id': ident, 'source': 'C12_IMMUTABLE', 'roi': key[0],
            'arm': key[1], 'lseg': key[2], 'raw': raw, 'raw_sha': sha(raw),
            'result': result, 'manifest': {}, 'terminal_status': 'PASS',
            'validation': json.loads(Path(state['validation_json']).read_text()),
        }
    return output


def c13_rows() -> tuple[dict[str, dict[str, Any]], list[dict[str, str]]]:
    if not MANIFEST.is_file():
        fail('missing prepared C13 command manifest')
    rows = read_tsv(MANIFEST)
    output: dict[str, dict[str, Any]] = {}
    for row in rows:
        run = Path(row['output_dir'])
        validation_path = run / 'C13_ARM_VALIDATION.json'
        if not validation_path.is_file():
            continue
        validation = json.loads(validation_path.read_text())
        if validation.get('terminal_status') != 'PASS':
            fail('%s has terminal validation %s' % (row['exp_id'], validation.get('terminal_status')))
        raw = run / 'run.log'
        if not raw.is_file() or sha(raw) != validation.get('raw_log_sha256'):
            fail('%s C13 raw-log SHA mismatch' % row['exp_id'])
        if validation.get('simulator_exit') != '0':
            fail('%s simulator exit is not zero' % row['exp_id'])
        output[row['exp_id']] = {
            'id': row['exp_id'], 'source': 'C13_MEASURED', 'roi': row['roi'],
            'arm': row['exp_id'], 'lseg': row['lseg'], 'raw': raw,
            'raw_sha': sha(raw), 'result': validation, 'manifest': row,
            'terminal_status': 'PASS', 'validation': validation,
        }
    return output, rows


def load_map() -> dict[str, list[dict[str, str]]]:
    by_roi: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_tsv(MAP):
        by_roi[row['roi']].append(row)
    for roi, rows in by_roi.items():
        rows.sort(key=lambda item: int(item['compute_index']))
        if [int(r['compute_index']) for r in rows] != list(range(len(rows))):
            fail('accepted operator map indexes noncontiguous for ' + roi)
    return by_roi


def delta_rows(raw: list[op.RawKernel], log: Path) -> list[dict[str, int]]:
    if not raw:
        fail(str(log) + ' contains no markers')
    # Supply the raw terminal checkpoints as the validation values. The
    # accepted parser then proves snapshot continuity and delta-to-terminal
    # recovery for all its accepted cumulative metrics.
    terminal: dict[str, int] = {}
    for metric, validation_name in op.CUMULATIVE_METRIC_VALIDATION.items():
        if metric in raw[-1].cumulative:
            terminal[validation_name] = raw[-1].cumulative[metric]
    return op.delta_counters(raw, terminal, log)[0]


def parse_arm(arm: dict[str, Any], mapping: dict[str, list[dict[str, str]]]) -> None:
    raw = op.raw_kernels(arm['raw'])
    expected = mapping[arm['roi']]
    if len(raw) != len(expected):
        fail('%s marker count %d != accepted map %d' % (arm['id'], len(raw), len(expected)))
    markers = [item.marker for item in raw]
    names = [item['trace_filename'] for item in expected]
    if markers != names:
        first = next(i for i, pair in enumerate(zip(markers, names)) if pair[0] != pair[1])
        fail('%s marker/map identity mismatch at %d: %s != %s' %
             (arm['id'], first, markers[first], names[first]))
    if any(item.exact_occurrences['gpu_sim_cycle'] != 1 for item in raw):
        fail(arm['id'] + ' requires exactly one gpu_sim_cycle per kernel')
    total = sum(item.exact['gpu_sim_cycle'] for item in raw)
    final = parse_final_counters(arm['raw'])
    if total != int(final.get('gpu_tot_sim_cycle', '-1')):
        fail('%s per-kernel cycles %d != raw full ROI %s' %
             (arm['id'], total, final.get('gpu_tot_sim_cycle')))
    result_cycle = number(arm['result'].get('gpu_tot_sim_cycle'))
    if result_cycle is not None and total != result_cycle:
        fail('%s per-kernel cycles %d != sidecar %s' % (arm['id'], total, result_cycle))
    deltas = delta_rows(raw, arm['raw'])
    arm['raw_kernels'] = raw
    arm['kernel_deltas'] = deltas
    arm['final'] = final
    arm['cycle_total'] = total


def metric(arm: dict[str, Any], name: str) -> int | float | None:
    if arm['source'] == 'C12_IMMUTABLE':
        return number(arm['result'].get(C12_NAME.get(name, name)))
    return number(arm['final'].get(name))


def op_cycles(arm: dict[str, Any], mapping: list[dict[str, str]]) -> dict[str, int]:
    total: Counter[str] = Counter()
    for item, row in zip(mapping, arm['raw_kernels']):
        total[item['operator_class']] += row.exact['gpu_sim_cycle']
    return dict(total)


def kernel_cycle(arm: dict[str, Any], index: int) -> int:
    return arm['raw_kernels'][index].exact['gpu_sim_cycle']


def per_operator_delta(baseline: dict[str, Any], candidate: dict[str, Any], mapping: list[dict[str, str]], comparison: str) -> list[dict[str, str]]:
    base_cycles = op_cycles(baseline, mapping)
    cand_cycles = op_cycles(candidate, mapping)
    base_deltas, cand_deltas = baseline['kernel_deltas'], candidate['kernel_deltas']
    fields = ('vm_l1_tlb_misses', 'vm_l2_tlb_misses', 'vm_translation_walk_starts',
              'vm_pte_requests', 'vm_pte_dram_responses',
              'vm_translation_requester_latency_cycles_total',
              'vm_weight_segment_hits', 'vm_weight_segment_l2_suppressed')
    bucket: dict[str, Counter[str]] = defaultdict(Counter)
    for item, left, right in zip(mapping, base_deltas, cand_deltas):
        operator = item['operator_class']
        for field in fields:
            bucket[operator][field] += right.get(field, 0) - left.get(field, 0)
    result = []
    for operator in sorted(set(base_cycles) | set(cand_cycles) | set(bucket)):
        row = {'comparison': comparison, 'roi': candidate['roi'],
               'operator_class': operator,
               'baseline_id': baseline['id'], 'candidate_id': candidate['id'],
               'baseline_cycles': str(base_cycles.get(operator, 0)),
               'candidate_cycles': str(cand_cycles.get(operator, 0)),
               'cycle_delta_candidate_minus_baseline': str(cand_cycles.get(operator, 0) - base_cycles.get(operator, 0))}
        for field in fields:
            row[field + '_delta'] = str(bucket[operator][field])
        result.append(row)
    return result


def comparator_id(exp: str, arm: dict[str, Any]) -> str:
    if exp in {'C13-LAT-P8', 'C13-LAT-P9', 'C13-CAP-P320', 'C13-CAP-P768S10'}:
        return 'C12-PREFILL-F0-LNONE'
    if exp == 'C13-LAT-D11':
        return 'C12-DECODE1-F0-LNONE'
    if exp == 'C13-SEL-P10':
        return 'C13-SEL-P10-CTRL-NEWBIN'
    if exp == 'C13-SEL-D10':
        return 'C13-SEL-D10-CTRL-NEWBIN'
    return ''


def result_row(arm: dict[str, Any], all_arms: dict[str, dict[str, Any]], mapping: list[dict[str, str]]) -> dict[str, str]:
    manifest = arm['manifest']
    comparator = comparator_id(arm['id'], arm)
    comp = all_arms.get(comparator)
    cycle = metric(arm, 'gpu_tot_sim_cycle')
    speedup = (metric(comp, 'gpu_tot_sim_cycle') / cycle if comp and cycle else None)
    rss, elapsed = resource_time(arm['raw'])
    cycles_by_op = op_cycles(arm, mapping)
    return {
        'exp_id': arm['id'], 'roi': arm['roi'],
        'hypothesis': ('H3_FINE_LATENCY' if arm['id'].startswith('C13-LAT') else
                       'H2_EXACT_REMAINDER_CAPACITY' if arm['id'].startswith('C13-CAP') else
                       'H1_OBJECT_SELECTIVE_SEGMENT'),
        'terminal_status': 'PASS', 'attempt': '1',
        'framework_head': subprocess_head(ROOT), 'core_head': manifest.get('core_head', 'C12_IMMUTABLE'),
        'binary_sha256': manifest.get('binary_sha256', 'C12_IMMUTABLE'),
        'config_sha256': manifest.get('config_sha256', 'C12_IMMUTABLE'),
        'trace_sha256': manifest.get('trace_sha256', 'C12_IMMUTABLE'),
        'registration_sha256': manifest.get('registration_sha256', 'C12_IMMUTABLE'),
        'eligibility_policy': manifest.get('eligibility_policy', 'ALL_C5_ELIGIBLE_WEIGHT'),
        'eligibility_artifact_sha256': manifest.get('eligibility_artifact_sha256', 'NONE'),
        'modeled_pa_contract': 'MODELED_DRIVER_PA / C5_MODELED_PA_HIGH_UNUSED_BIT_V1',
        'exact_l2_tlb_entries': manifest.get('exact_l2_tlb_entries', 'NOT_EMITTED'),
        'segment_enable': manifest.get('segment_enable', 'NOT_EMITTED'),
        'segment_n': manifest.get('segment_n', 'NOT_EMITTED'),
        'lseg': manifest.get('lseg', 'NOT_EMITTED'),
        'budget_class': manifest.get('budget_class', 'NOT_EMITTED'),
        'comparator_id': comparator or 'NONE',
        'comparator_binary_sha256': (comp['manifest'].get('binary_sha256') if comp else 'NONE'),
        'gpu_tot_sim_cycle': fnum(cycle), 'gpu_tot_sim_insn': fnum(metric(arm, 'gpu_tot_sim_insn')),
        'gpu_tot_ipc': fnum(metric(arm, 'gpu_tot_ipc')), 'speedup_vs_comparator': fnum(speedup),
        'vm_l1_tlb_accesses': fnum(metric(arm, 'vm_l1_tlb_accesses')),
        'vm_l1_tlb_misses': fnum(metric(arm, 'vm_l1_tlb_misses')),
        'vm_l2_tlb_accesses': fnum(metric(arm, 'vm_l2_tlb_accesses')),
        'vm_l2_tlb_misses': fnum(metric(arm, 'vm_l2_tlb_misses')),
        'vm_l2_tlb_port_stalls': fnum(metric(arm, 'vm_l2_tlb_port_stalls')),
        'vm_translation_mshr_allocations': fnum(metric(arm, 'vm_translation_mshr_allocations')),
        'vm_translation_mshr_merges': fnum(metric(arm, 'vm_translation_mshr_merges')),
        'vm_translation_mshr_full_events': fnum(metric(arm, 'vm_translation_mshr_full_events')),
        'vm_translation_walk_starts': fnum(metric(arm, 'vm_translation_walk_starts')),
        'vm_pte_requests': fnum(metric(arm, 'vm_pte_requests')),
        'vm_pte_l2_only_responses': fnum(metric(arm, 'vm_pte_l2_only_responses')),
        'vm_pte_dram_responses': fnum(metric(arm, 'vm_pte_dram_responses')),
        'vm_translation_requester_latency_cycles_total': fnum(metric(arm, 'vm_translation_requester_latency_cycles_total')),
        'vm_translation_requester_mshr_wait_cycles_total': fnum(metric(arm, 'vm_translation_requester_mshr_wait_cycles_total')),
        'vm_pte_memory_wait_cycles_total': fnum(metric(arm, 'vm_pte_memory_wait_cycles_total')),
        'vm_pwc_accesses': fnum(metric(arm, 'vm_pwc_accesses')), 'vm_pwc_hits': fnum(metric(arm, 'vm_pwc_hits')),
        'vm_pwc_misses': fnum(metric(arm, 'vm_pwc_misses')),
        'segment_lookup_attempts': fnum(metric(arm, 'vm_weight_segment_lookup_attempts')),
        'segment_hits': fnum(metric(arm, 'vm_weight_segment_hits')),
        'segment_l2_suppressed': fnum(metric(arm, 'vm_weight_segment_l2_suppressed')),
        'kernel691_cycles': str(kernel_cycle(arm, 691)) if arm['roi'] == 'prefill' else 'NOT_APPLICABLE',
        'embedding_output_cycles': str(cycles_by_op.get('EMBEDDING_OUTPUT', 0)),
        'ffn_cycles': str(cycles_by_op.get('FFN', 0)),
        'attention_projection_cycles': str(cycles_by_op.get('ATTENTION_PROJECTION', 0)),
        'kernel_markers': str(len(arm['raw_kernels'])), 'telemetry_records': arm['result'].get('telemetry_records', 'NOT_EMITTED'),
        'object_conservation_pass': 'PASS', 'pte_conservation_pass': 'PASS',
        'peak_rss_kb': rss, 'elapsed_seconds': elapsed, 'raw_log_sha256': arm['raw_sha'],
        'validation_sha256': sha(Path(arm['manifest']['output_dir']) / 'C13_ARM_VALIDATION.json'),
        'parser_version': sha(Path(__file__)), 'notes': 'C13 terminal validator plus collector marker/map and conservation recheck',
    }


def subprocess_head(repo: Path) -> str:
    import subprocess
    return subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()


def rows_status(manifest: list[dict[str, str]], terminal: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    rows = []
    for row in manifest:
        exp = row['exp_id']; run = Path(row['output_dir']); validation = run / 'C13_ARM_VALIDATION.json'
        if exp in terminal:
            status, failure = 'PASS', ''
        elif validation.is_file():
            value = json.loads(validation.read_text()); status = value.get('terminal_status', 'FAILED_DIAGNOSING'); failure = ';'.join(value.get('errors', []))
        elif (run / 'run.log').is_file():
            status, failure = 'RUNNING_OR_INCOMPLETE', 'no terminal validation yet'
        else:
            status, failure = 'NOT_STARTED', ''
        rows.append({'exp_id': exp, 'roi': row['roi'], 'terminal_status': status,
                     'attempt': '1', 'run_dir': str(run), 'raw_log_sha256': terminal[exp]['raw_sha'] if exp in terminal else '',
                     'failure_summary': failure})
    return rows


def latency_rows(arms: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    wanted = [('prefill', 'C12-PREFILL-F7-L5', '5'), ('prefill', 'C13-LAT-P8', '8'),
              ('prefill', 'C13-LAT-P9', '9'), ('prefill', 'C12-PREFILL-F7-L10', '10'),
              ('prefill', 'C12-PREFILL-F7-L20', '20'), ('decode1', 'C12-DECODE1-F7-L5', '5'),
              ('decode1', 'C12-DECODE1-F7-L10', '10'), ('decode1', 'C13-LAT-D11', '11'),
              ('decode1', 'C12-DECODE1-F7-L20', '20')]
    rows=[]
    for roi, ident, lseg in wanted:
        if ident not in arms: continue
        arm = arms[ident]; baseline=arms['C12-%s-F0-LNONE' % roi.upper()]
        cycle=metric(arm,'gpu_tot_sim_cycle'); base=metric(baseline,'gpu_tot_sim_cycle')
        rows.append({'roi':roi,'point_id':ident,'lseg':lseg,'cycles':fnum(cycle),
                     'cycle_delta_vs_f0':fnum(cycle-base),'speedup_vs_f0':fnum(base/cycle),
                     'evidence':'MEASURED_C13_DIAGNOSTIC_FACT' if ident.startswith('C13-') else 'IMMUTABLE_C12_REFERENCE'})
    return rows


def capacity_rows(arms: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    ids = [('A_F0_exact768_no_segment', 'C12-PREFILL-F0-LNONE'),
           ('B_C13_exact320_no_segment', 'C13-CAP-P320'),
           ('C_C13_exact768_segmentN8_L10', 'C13-CAP-P768S10'),
           ('D_F7_exact320_segmentN8_L10', 'C12-PREFILL-F7-L10')]
    if not all(value in arms for _,value in ids): return []
    metrics=('gpu_tot_sim_cycle','vm_l2_tlb_misses','vm_l2_tlb_port_stalls','vm_translation_walk_starts','vm_pte_requests','vm_pte_dram_responses','vm_translation_requester_latency_cycles_total')
    output=[]; point={label:arms[ident] for label,ident in ids}
    for name in metrics:
        values={label:metric(arm,name) for label,arm in point.items()}
        output.append({'metric':name, **{key:fnum(value) for key,value in values.items()},
                       'B_minus_A':fnum(values['B_C13_exact320_no_segment']-values['A_F0_exact768_no_segment']),
                       'C_minus_A':fnum(values['C_C13_exact768_segmentN8_L10']-values['A_F0_exact768_no_segment']),
                       'D_minus_B':fnum(values['D_F7_exact320_segmentN8_L10']-values['B_C13_exact320_no_segment']),
                       'D_minus_C':fnum(values['D_F7_exact320_segmentN8_L10']-values['C_C13_exact768_segmentN8_L10']),
                       'interaction_(D-B)-(C-A)':fnum((values['D_F7_exact320_segmentN8_L10']-values['B_C13_exact320_no_segment'])-(values['C_C13_exact768_segmentN8_L10']-values['A_F0_exact768_no_segment'])),
                       'interpretation_boundary':'DIAGNOSTIC_INTERACTION_ONLY'})
    return output


def selective_rows(arms: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    output=[]
    for candidate, control in (('C13-SEL-P10','C13-SEL-P10-CTRL-NEWBIN'), ('C13-SEL-D10','C13-SEL-D10-CTRL-NEWBIN')):
        if candidate not in arms or control not in arms: continue
        cand,base=arms[candidate],arms[control]
        row={'roi':cand['roi'],'candidate_id':candidate,'same_new_binary_control':control,
             'candidate_cycles':fnum(metric(cand,'gpu_tot_sim_cycle')),'control_cycles':fnum(metric(base,'gpu_tot_sim_cycle')),
             'cycle_delta_candidate_minus_control':fnum(metric(cand,'gpu_tot_sim_cycle')-metric(base,'gpu_tot_sim_cycle')),
             'speedup_vs_same_binary_control':fnum(metric(base,'gpu_tot_sim_cycle')/metric(cand,'gpu_tot_sim_cycle')),
             'eligibility_policy':cand['manifest']['eligibility_policy'],
             'evidence':'MEASURED_C13_DIAGNOSTIC_FACT'}
        for name in ('vm_weight_segment_hits','vm_weight_segment_l2_suppressed','vm_l2_tlb_misses','vm_translation_walk_starts','vm_pte_dram_responses'):
            row[name+'_delta']=fnum(metric(cand,name)-metric(base,name))
        output.append(row)
    return output


def kernel691_rows(arms: dict[str, dict[str, Any]], mapping: list[dict[str, str]]) -> list[dict[str, str]]:
    if len(mapping) <= 691 or mapping[691]['operator_class'] != 'EMBEDDING_OUTPUT':
        fail('accepted Prefill index 691 is no longer EMBEDDING_OUTPUT')
    rows=[]
    for ident,arm in sorted(arms.items()):
        if arm['roi'] != 'prefill': continue
        rows.append({'point_id':ident,'source':arm['source'],'kernel_index':'691',
                     'trace_filename':mapping[691]['trace_filename'],'operator_class':'EMBEDDING_OUTPUT',
                     'cycles':str(kernel_cycle(arm,691)),'full_roi_cycles':fnum(metric(arm,'gpu_tot_sim_cycle')),
                     'cycle_share':fnum(kernel_cycle(arm,691)/metric(arm,'gpu_tot_sim_cycle')),
                     'evidence_kind':mapping[691]['evidence_kind']})
    return rows


def final_report(arms: dict[str, dict[str, Any]], complete: bool) -> str:
    state = 'C13_MINIMAL_DIAGNOSTICS_COMPLETE_READY_FOR_REVIEW' if complete else 'C13_DIAGNOSTICS_ADAPTIVE_ADMISSION_AUTHORIZED'
    measured = sorted(key for key,arm in arms.items() if arm['source']=='C13_MEASURED')
    lines=['# C13 minimal diagnostics — %s' % ('final report' if complete else 'live evidence status'), '',
           'Status: `%s`' % state, '', '## Provenance boundary', '',
           '- C13-only results below are admitted only after terminal validation, immutable raw-log SHA recheck, accepted operator-map marker identity, exact per-kernel cycle closure, and cumulative `vm_*` delta continuity.',
           '- C12 rows are immutable references; capacity rows are explicitly `DIAGNOSTIC_NON_EQUAL_BUDGET` and interaction values are not paper-matrix claims.', '',
           '## Measured C13 evidence currently admitted', '']
    lines += ['- `%s`' % item for item in measured] or ['- None yet.']
    if not complete:
        lines += ['', '## Status', '', '- Incomplete arms intentionally have no scientific interpretation. This file is an execution-state artifact, not a conclusion.']
    else:
        lines += ['', '## Required conclusions', '',
                  '- `MEASURED_C13_DIAGNOSTIC_FACT`: see `LATENCY_FINE_SWEEP.tsv`, `CAPACITY_FACTORIAL.tsv`, and `SELECTIVE_SEGMENT_RESULTS.tsv` for exact values.',
                  '- `SUPPORTED_C13_MECHANISM_SIGNAL`: only interpretations that remain consistent across the controlled comparisons may be promoted from those tables.',
                  '- `DIAGNOSTIC_INTERACTION_ONLY`: capacity factorial interaction is confined to its measured 2×2.',
                  '- `UNRESOLVED`: telemetry association is not asserted as singular causal critical-path proof.']
    return '\n'.join(lines)+'\n'


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument('--strict', action='store_true', help='fail unless all primary and mandatory controls PASS')
    args=parser.parse_args()
    mapping=load_map(); c12=c12_rows(); c13,manifest=c13_rows(); arms={**c12,**c13}
    for arm in arms.values(): parse_arm(arm,mapping)
    # This is a derived read-only parsing receipt, deliberately separate from
    # the immutable raw log and the runner's terminal validation JSON.  The
    # campaign driver uses it to ensure a just-finished arm is collected once
    # before it admits another arm into the released slot.
    for arm in c13.values():
        receipt = {'raw_log_sha256': arm['raw_sha'],
                   'collector_sha256': sha(Path(__file__)),
                   'collected_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                   'marker_map_identity': 'PASS', 'kernel_cycle_conservation': 'PASS',
                   'vm_snapshot_conservation': 'PASS'}
        (Path(arm['manifest']['output_dir'])/'C13_ARM_COLLECTED.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    complete=all(exp in c13 for exp in PRIMARY+CONTROLS)
    if args.strict and not complete:
        fail('strict collection requires all primary and mandatory controls terminal PASS')
    status=rows_status(manifest,c13)
    results=[result_row(arm,arms,mapping[arm['roi']]) for arm in c13.values()]
    write_tsv(PACK/'ARM_STATUS.tsv', ('exp_id','roi','terminal_status','attempt','run_dir','raw_log_sha256','failure_summary'), status)
    result_fields=('exp_id','roi','hypothesis','terminal_status','attempt','framework_head','core_head','binary_sha256','config_sha256','trace_sha256','registration_sha256','eligibility_policy','eligibility_artifact_sha256','modeled_pa_contract','exact_l2_tlb_entries','segment_enable','segment_n','lseg','budget_class','comparator_id','comparator_binary_sha256','gpu_tot_sim_cycle','gpu_tot_sim_insn','gpu_tot_ipc','speedup_vs_comparator','vm_l1_tlb_accesses','vm_l1_tlb_misses','vm_l2_tlb_accesses','vm_l2_tlb_misses','vm_l2_tlb_port_stalls','vm_translation_mshr_allocations','vm_translation_mshr_merges','vm_translation_mshr_full_events','vm_translation_walk_starts','vm_pte_requests','vm_pte_l2_only_responses','vm_pte_dram_responses','vm_translation_requester_latency_cycles_total','vm_translation_requester_mshr_wait_cycles_total','vm_pte_memory_wait_cycles_total','vm_pwc_accesses','vm_pwc_hits','vm_pwc_misses','segment_lookup_attempts','segment_hits','segment_l2_suppressed','kernel691_cycles','embedding_output_cycles','ffn_cycles','attention_projection_cycles','kernel_markers','telemetry_records','object_conservation_pass','pte_conservation_pass','peak_rss_kb','elapsed_seconds','raw_log_sha256','validation_sha256','parser_version','notes')
    write_tsv(PACK/'ARM_RESULTS.tsv',result_fields,results)
    provenance=[]
    for item in results:
        provenance.append({key:item[key] for key in ('exp_id','roi','framework_head','core_head','binary_sha256','config_sha256','trace_sha256','registration_sha256','eligibility_policy','eligibility_artifact_sha256','raw_log_sha256','validation_sha256')})
    write_tsv(PACK/'PROVENANCE_MATRIX.tsv',('exp_id','roi','framework_head','core_head','binary_sha256','config_sha256','trace_sha256','registration_sha256','eligibility_policy','eligibility_artifact_sha256','raw_log_sha256','validation_sha256'),provenance)
    write_tsv(PACK/'LATENCY_FINE_SWEEP.tsv',('roi','point_id','lseg','cycles','cycle_delta_vs_f0','speedup_vs_f0','evidence'),latency_rows(arms))
    capacity=capacity_rows(arms)
    write_tsv(PACK/'CAPACITY_FACTORIAL.tsv',('metric','A_F0_exact768_no_segment','B_C13_exact320_no_segment','C_C13_exact768_segmentN8_L10','D_F7_exact320_segmentN8_L10','B_minus_A','C_minus_A','D_minus_B','D_minus_C','interaction_(D-B)-(C-A)','interpretation_boundary'),capacity)
    write_tsv(PACK/'SELECTIVE_SEGMENT_RESULTS.tsv',('roi','candidate_id','same_new_binary_control','candidate_cycles','control_cycles','cycle_delta_candidate_minus_control','speedup_vs_same_binary_control','eligibility_policy','vm_weight_segment_hits_delta','vm_weight_segment_l2_suppressed_delta','vm_l2_tlb_misses_delta','vm_translation_walk_starts_delta','vm_pte_dram_responses_delta','evidence'),selective_rows(arms))
    comparisons=[]
    for ident,arm in c13.items():
        comp=comparator_id(ident,arm)
        if comp in arms: comparisons.extend(per_operator_delta(arms[comp],arm,mapping[arm['roi']],ident+'_vs_'+comp))
    write_tsv(PACK/'OPERATOR_DIAGNOSTIC_DELTAS.tsv',('comparison','roi','operator_class','baseline_id','candidate_id','baseline_cycles','candidate_cycles','cycle_delta_candidate_minus_baseline','vm_l1_tlb_misses_delta','vm_l2_tlb_misses_delta','vm_translation_walk_starts_delta','vm_pte_requests_delta','vm_pte_dram_responses_delta','vm_translation_requester_latency_cycles_total_delta','vm_weight_segment_hits_delta','vm_weight_segment_l2_suppressed_delta'),comparisons)
    write_tsv(PACK/'KERNEL691_DIAGNOSTIC.tsv',('point_id','source','kernel_index','trace_filename','operator_class','cycles','full_roi_cycles','cycle_share','evidence_kind'),kernel691_rows(arms,mapping['prefill']))
    (PACK/'FINAL_REPORT.md').write_text(final_report(arms,complete))
    HANDOFF.parent.mkdir(parents=True,exist_ok=True)
    HANDOFF.write_text(final_report(arms,complete))
    print('C13_COLLECT_%s\tterminal_c13=%d\tprimary_complete=%s' % ('PASS' if complete else 'PARTIAL',len(c13),complete))


if __name__ == '__main__':
    main()
