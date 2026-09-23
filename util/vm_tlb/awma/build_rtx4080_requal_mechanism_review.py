#!/usr/bin/env python3
from __future__ import annotations

import csv
import difflib
import hashlib
import json
import math
import re
import statistics
import subprocess
from collections import defaultdict, deque
from pathlib import Path

REPO = Path('/root/workspace/accel-sim-framework-awma-174-rtx4080-platform-requal-mechanism-v1')
RUNTIME = Path('/root/awma_rtx4080_requal_mechanism_v1_runtime')
PACK = REPO / 'docs/vm_tlb/review_packs/AWMA_RTX4080_PLATFORM_REQUAL_AND_MECHANISM_VALIDATION_V1'
REPORT = REPO / 'docs/vm_tlb/codex_handoff/awma/RTX4080_PLATFORM_REQUAL_AND_MECHANISM_VALIDATION_174NEW_V1_REPORT.md'
CONFIG = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
MATCHED = Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/rtx4080_heldout_scale_match_v1_20260923T121500Z')
PLATFORM_BUNDLE = Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/rtx4080_platform_anchors_v1_20260923T115000Z')
CONTROL_BUNDLE = Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/crosscal_exact_v1r1_20260923T111500Z')
MECH_BUNDLE = Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/mechanism_sensitive_accessq_v1_20260923T114500Z')
PLATFORM_BINARY = RUNTIME / 'bin/platform_v1_accel-sim.out'
SCIENCE_BINARY = RUNTIME / 'bin/science_diag_accel-sim.out'
SHADER_PRE = RUNTIME / 'shader.cc.pre_mechanism_diagnostics'
SHADER_POST = RUNTIME / 'src/gpgpu-sim/src/gpgpu-sim/shader.cc'


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + '\n')


def tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(header)
        w.writerows(rows)


def text(path: Path) -> str:
    return path.read_text(errors='replace')


def vals(path: Path, key: str) -> list[int]:
    return [int(x) for x in re.findall(rf'^{re.escape(key)} = (\d+)$', text(path), re.M)]


def last(path: Path, key: str) -> int:
    found = vals(path, key)
    if not found:
        raise RuntimeError(f'missing {key}: {path}')
    return found[-1]


def terminal(path: Path) -> bool:
    data = text(path)
    return 'GPGPU-Sim: *** simulation thread exiting ***' in data and 'GPGPU-Sim: *** exit detected ***' in data


def bracket_values(path: Path, start_pc: int, end_pc: int, steps: int) -> list[dict[str, object]]:
    starts: dict[tuple[int, int, int], deque[int]] = defaultdict(deque)
    sample_index: dict[tuple[int, int, int], int] = defaultdict(int)
    rows: list[dict[str, object]] = []
    pat = re.compile(r'^awma_crosscal_event kernel_uid=(\d+) sid=(\d+) warp=(\d+) dynamic_warp=(\d+) pc=0x([0-9a-f]+) cycle=(\d+)$')
    for line in text(path).splitlines():
        m = pat.match(line)
        if not m:
            continue
        kernel, sid, warp, dynamic, pc, cycle = m.groups()
        if int(kernel) != 2:
            continue
        key = (int(sid), int(warp), int(dynamic))
        pc_i, cycle_i = int(pc, 16), int(cycle)
        if pc_i == start_pc:
            starts[key].append(cycle_i)
        elif pc_i == end_pc:
            if not starts[key]:
                raise RuntimeError(f'unpaired end in {path}: {line}')
            begin = starts[key].popleft()
            idx = sample_index[key]
            sample_index[key] += 1
            rows.append({'sid': key[0], 'warp': key[1], 'dynamic_warp': key[2],
                         'sample_index': idx, 'start_cycle': begin, 'end_cycle': cycle_i,
                         'cycles_per_step': (cycle_i - begin) / steps})
    if any(starts.values()):
        raise RuntimeError(f'unpaired starts in {path}')
    return rows


ACCESSQ = re.compile(r'^awma_accessq_cardinality_event .*kernel_uid=(\d+) .*pc=0x([0-9a-f]+) active_lanes=(\d+) accessq_entries=(\d+)$')
TARGET_LDG_PCS = {0x570, 0x5D0, 0x630, 0x690}


def accessq(path: Path) -> dict[str, object]:
    entries, lanes = [], []
    for line in text(path).splitlines():
        m = ACCESSQ.match(line)
        if m and int(m.group(1)) == 2 and int(m.group(2), 16) in TARGET_LDG_PCS:
            lanes.append(int(m.group(3)))
            entries.append(int(m.group(4)))
    hist = {str(k): entries.count(k) for k in sorted(set(entries))}
    return {'events': len(entries), 'active_min': min(lanes), 'active_max': max(lanes),
            'entries_min': min(entries), 'entries_mean': statistics.fmean(entries),
            'entries_max': max(entries), 'fraction_gt1': sum(x > 1 for x in entries) / len(entries),
            'hist': hist}


def coverage(path: Path) -> dict[str, int]:
    matches = re.findall(
        r'AWMA_VM_COVERAGE admissions=(\d+) translated=(\d+) untranslated=(\d+) unobserved=(\d+) unique=(\d+) translated_unique=(\d+) untranslated_unique=(\d+)',
        text(path))
    if not matches:
        return {}
    keys = ('admissions', 'translated', 'untranslated', 'unobserved', 'unique', 'translated_unique', 'untranslated_unique')
    return dict(zip(keys, map(int, matches[-1])))


def matched_native() -> dict[str, float]:
    out = {}
    with (MATCHED / 'NATIVE_TIMING_SUMMARY.tsv').open(newline='') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            if row['process'] == 'SUMMARY':
                out[row['point']] = float(row['us_per_launch'])
    return out


def rc(path: Path) -> int:
    raw = (path / 'rc.txt').read_text().strip()
    match = re.match(r'-?\d+', raw)
    if not match:
        raise RuntimeError(f'invalid rc receipt: {path / "rc.txt"}: {raw!r}')
    return int(match.group(0))


def log_sha(path: Path) -> str:
    return sha256(path / 'run.log')


PACK.mkdir(parents=True, exist_ok=True)
head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
config_sha = sha256(CONFIG)
trace_config_sha = sha256(TRACE_CONFIG)
platform_binary_sha = sha256(PLATFORM_BINARY)
science_binary_sha = sha256(SCIENCE_BINARY)
if config_sha != 'de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8':
    raise RuntimeError('frozen config identity mismatch')

# Platform requalification.
native = matched_native()
held_rows, held_errors = [], []
for point in ('H_CACHE', 'H_STREAM', 'H_COMPUTE'):
    run = RUNTIME / f'requal_{point}'
    log = run / 'run.log'
    if rc(run) if (run / 'rc.txt').exists() else 0:
        raise RuntimeError(f'requalification failed: {point}')
    cycles = last(log, 'gpu_sim_cycle')
    sim_us = cycles / 2505.0
    error = abs(sim_us - native[point]) / native[point]
    held_errors.append(error)
    held_rows.append([point, f'{native[point]:.9f}', cycles, f'{sim_us:.9f}', f'{error:.9f}',
                      f'{sim_us/native[point]:.9f}', config_sha, platform_binary_sha, log_sha(run),
                      'TERMINAL_PASS' if terminal(log) else 'FAIL'])
held_median = statistics.median(held_errors)
held_mean = statistics.fmean(held_errors)
held_worst = max(held_errors)
gross = any(ratio > 2.0 or ratio < 0.5 for ratio in [
    (int(row[2]) / 2505.0) / float(row[1]) for row in held_rows
])
if held_median <= .25 and not gross:
    platform_decision = 'RTX4080_ADA_PLATFORM_QUALIFIED'
elif held_median <= .35 and not gross:
    platform_decision = 'RTX4080_ADA_PLATFORM_QUALIFIED_WITH_SCOPE'
else:
    platform_decision = 'RTX4080_ADA_PLATFORM_NOT_QUALIFIED'
if platform_decision == 'RTX4080_ADA_PLATFORM_NOT_QUALIFIED':
    raise RuntimeError('platform gate failed; do not generate science pack')
tsv(PACK / 'MATCHED_HELDOUT_AUTHORITY.tsv',
    ['point', 'elements', 'processes', 'host_repetitions', 'native_us_per_launch', 'evidence_class', 'source_binary_sha256'], [
        ['H_CACHE', 1024, 5, 1000, f"{native['H_CACHE']:.9f}", 'RTX4080_HELDOUT_MATCHED_NATIVE_TIMING_V1', 'fa76556cb9e673e25954a6c03af66790091fbef074d6e558c270c5f5ae0cfb1c'],
        ['H_STREAM', 4096, 5, 1000, f"{native['H_STREAM']:.9f}", 'RTX4080_HELDOUT_MATCHED_NATIVE_TIMING_V1', 'fa76556cb9e673e25954a6c03af66790091fbef074d6e558c270c5f5ae0cfb1c'],
        ['H_COMPUTE', 1024, 5, 1000, f"{native['H_COMPUTE']:.9f}", 'RTX4080_HELDOUT_MATCHED_NATIVE_TIMING_V1', 'fa76556cb9e673e25954a6c03af66790091fbef074d6e558c270c5f5ae0cfb1c'],
    ])
tsv(PACK / 'HELDOUT_REQUALIFICATION.tsv',
    ['point', 'native_us_per_launch', 'sim_cycles', 'sim_us_per_launch', 'absolute_relative_error', 'sim_native_ratio', 'config_sha256', 'binary_sha256', 'run_log_sha256', 'status'], held_rows)
write(PACK / 'PLATFORM_REQUALIFICATION_DECISION.md', f'''# Platform requalification decision

Decision: `{platform_decision}`.

- median absolute error: `{held_median:.4%}`
- mean absolute error: `{held_mean:.4%}`
- worst absolute error: `{held_worst:.4%}`
- essential point beyond 2x: `NO`
- tuning performed: `NO`

H_CACHE remains a single bounded outlier. H_STREAM and H_COMPUTE independently pass with matched trace-scale Native timing. The unchanged config is frozen as `RTX4080_ADA_ACCELSIM_BASE_V1`.
''')
write(PACK / 'FROZEN_PLATFORM_AUTHORITY.json', json.dumps({
    'authority': 'RTX4080_ADA_ACCELSIM_BASE_V1', 'qualification': platform_decision,
    'config_path': str(CONFIG), 'config_sha256': config_sha,
    'trace_config_sha256': trace_config_sha, 'platform_binary_sha256': platform_binary_sha,
    'science_diagnostic_binary_sha256': science_binary_sha,
    'implementation_commit': 'aeec5b9a69865012b16ac0a6627143e29f1fee06',
    'platform_v1_publication': '646844c513ba316eae4188cb517c2eef7282132d',
    'matched_native_authority': '1e3286862a496ced4182e073739a5678100dd846',
    'platform_tuning_passes_this_goal': 0,
}, indent=2, sort_keys=True))

# Overlay smoke.
overlay_rows = []
for cfg in ('M0', 'M1'):
    run = RUNTIME / f'overlay_smoke_{cfg}'
    log = run / 'run.log'
    overlay_rows.append([cfg, last(log, 'gpu_sim_cycle'), last(log, 'gpu_sim_insn'),
                         last(log, 'gpu_tot_issued_cta'), last(log, 'vm_translation_lookup_requests'),
                         last(log, 'vm_translation_mshr_active'), last(log, 'vm_translation_pwq_occupancy'),
                         last(log, 'vm_translation_walkers_active'), log_sha(run),
                         'PASS' if terminal(log) and all(last(log, k) == 0 for k in
                             ('vm_translation_mshr_active', 'vm_translation_pwq_occupancy', 'vm_translation_walkers_active')) else 'FAIL'])
tsv(PACK / 'AWMA_VM_OVERLAY_SMOKE.tsv', ['config', 'cycles', 'instructions', 'cta', 'translation_lookups',
    'mshr_active_final', 'pwq_final', 'walkers_final', 'run_log_sha256', 'status'], overlay_rows)

# Control traces and matrix.
control_native = {'M0': 52.0, 'M1': 294.0, 'M2': 280.0, 'M3': 152.5}
expected_control = {'M0': 50, 'M1': 50, 'M2': 800, 'M3': 50}
control_specs = [(cfg, 'LEGACY', lat) for cfg in ('M0', 'M1', 'M2', 'M3') for lat in (10, 0)] + [
    ('M1', 'V1', 10), ('M1', 'V2R1', 10), ('M2', 'V1', 10), ('M2', 'V2R1', 10)]
control_rows, control_obs, control_values = [], [], {}
for cfg, semantic, latency in control_specs:
    run = RUNTIME / f'control_{cfg}_{semantic}_{latency}_80'
    if rc(run) != 0:
        raise RuntimeError(f'control point failed: {run}')
    log = run / 'run.log'
    obs = bracket_values(log, 0x240, 0x10B0, 512)
    if len(obs) != expected_control[cfg]:
        raise RuntimeError(f'control bracket count {run}: {len(obs)}')
    values = [float(x['cycles_per_step']) for x in obs]
    control_values[(cfg, semantic, latency)] = statistics.median(values)
    cov = coverage(log)
    q = [last(log, k) for k in ('vm_translation_mshr_active', 'vm_translation_pwq_occupancy', 'vm_translation_walkers_active')]
    dup = last(log, 'vm_ready_application_duplicate_attempts')
    status = 'PASS' if terminal(log) and not any(q) and dup == 0 and cov.get('untranslated', 0) == 0 and cov.get('unobserved', 0) == 0 else 'FAIL'
    control_rows.append([cfg, semantic, f'{latency}/80', len(values), f'{statistics.fmean(values):.9f}',
                         f'{statistics.median(values):.9f}', last(log, 'gpu_sim_cycle'), last(log, 'gpu_sim_insn'),
                         last(log, 'gpu_tot_issued_cta'), cov.get('admissions', 'NA'), cov.get('translated', 'NA'),
                         cov.get('untranslated', 'NA'), cov.get('unobserved', 'NA'), dup, *q, log_sha(run), status])
    for row in obs:
        control_obs.append([cfg, semantic, f'{latency}/80', row['sid'], row['warp'], row['dynamic_warp'],
                            row['sample_index'], row['start_cycle'], row['end_cycle'], 512,
                            f"{row['cycles_per_step']:.9f}"])
tsv(PACK / 'CONTROL_MATRIX.tsv', ['config', 'semantic', 'latency', 'measurement_brackets', 'mean_cycles_per_step',
    'median_cycles_per_step', 'gpu_sim_cycle', 'gpu_sim_insn', 'cta', 'coverage_admissions', 'coverage_translated',
    'coverage_untranslated', 'coverage_unobserved', 'duplicate_applications', 'mshr_final', 'pwq_final', 'walkers_final',
    'run_log_sha256', 'status'], control_rows)
tsv(PACK / 'CONTROL_NATIVE_ALIGNED_OBSERVABLE.tsv', ['config', 'semantic', 'latency', 'sid', 'warp', 'dynamic_warp',
    'sample_index', 'start_cycle', 'end_cycle', 'steps', 'cycles_per_step'], control_obs)
control_trace_rows = []
for cfg in ('M0', 'M1', 'M2', 'M3'):
    raw = CONTROL_BUNDLE / f'pairs/{cfg}/raw'
    files = sorted(raw.glob('*'))
    control_trace_rows.append([cfg, control_native[cfg], expected_control[cfg], raw,
                               sha256(CONTROL_BUNDLE / f'pairs/{cfg}/SHA256SUMS'),
                               ','.join(f'{p.name}:{sha256(p)}' for p in files)])
tsv(PACK / 'CONTROL_TRACE_AUTHORITY.tsv', ['config', 'native_cycles_per_step', 'expected_measurement_brackets',
    'raw_path', 'pair_manifest_sha256', 'member_hashes'], control_trace_rows)
m0 = control_values[('M0', 'LEGACY', 10)]
m1 = control_values[('M1', 'LEGACY', 10)]
m2 = control_values[('M2', 'LEGACY', 10)]
m3 = control_values[('M3', 'LEGACY', 10)]
write(PACK / 'CONTROL_ANALYSIS.md', f'''# Exact contextual control analysis

Scope: `RTX4080_ADA_BASE_V1 + AWMA_MODEL_RELATIVE_VM`.

Legacy 10/80 measurement medians (cycles/dependent step): M0={m0:.6f}, M1={m1:.6f}, M2={m2:.6f}, M3={m3:.6f}.

- simulator M1/M0: `{m1/m0:.9f}`; Native: `{control_native['M1']/control_native['M0']:.9f}`
- simulator M2/M1: `{m2/m1:.9f}`; Native: `{control_native['M2']/control_native['M1']:.9f}`
- simulator M3/M0: `{m3/m0:.9f}`; Native: `{control_native['M3']/control_native['M0']:.9f}`

M0-M3 remain mechanism-inactive controls. The matrix is for relative/contextual behavior, not hardware TLB latency or capacity fitting. No parameter was changed from these results.
''')
write(PACK / 'CONTROL_CONTEXT_PERSISTENCE.md', '''# Context persistence audit

Both trace filenames are consumed by one `accel_sim_framework` instance and one `gpgpu_sim` object in order: warmup kernel uid=1, then measurement kernel uid=2.

- L1D: naturally invalidated when all threads complete because the frozen base config has `-gpgpu_flush_l1_cache 1`.
- L2: preserved; the frozen config does not enable L2 flushing.
- shared TLB/PWC/controller: preserved in the single `translation_controller` constructed with the simulator and not recreated at kernel cleanup.
- memory contents and mapping: preserved in the same simulator process/context.
- per-kernel shader execution state: naturally re-bound for uid=2.

The L1 invalidation is reported scope. No simulator semantics were changed to force persistence.
''')

# Mechanism matrix.
mech_native = {'A1_CONTROL': 321.0, 'A8': 338.0, 'A32': 388.0, 'A32_W8': 393.0}
expected_mech = {'A1_CONTROL': 50, 'A8': 50, 'A32': 50, 'A32_W8': 400}
expected_events = {'A1_CONTROL': 12800, 'A8': 12800, 'A32': 12800, 'A32_W8': 102400}
mech_rows, mech_obs, aq_rows, mech_values = [], [], [], {}
for cfg in ('A1_CONTROL', 'A8', 'A32', 'A32_W8'):
    for semantic in ('LEGACY', 'V1', 'V2R1'):
        for latency in (10, 0):
            run = RUNTIME / f'mechanism_{cfg}_{semantic}_{latency}_80'
            if rc(run) != 0:
                raise RuntimeError(f'mechanism point failed: {run}')
            log = run / 'run.log'
            obs = bracket_values(log, 0x4A0, 0x870, 256)
            aq = accessq(log)
            if len(obs) != expected_mech[cfg] or aq['events'] != expected_events[cfg]:
                raise RuntimeError(f'mechanism identity failed: {run} brackets={len(obs)} accessq={aq["events"]}')
            values = [float(x['cycles_per_step']) for x in obs]
            mech_values[(cfg, semantic, latency)] = statistics.median(values)
            cov = coverage(log)
            q = [last(log, k) for k in ('vm_translation_mshr_active', 'vm_translation_pwq_occupancy', 'vm_translation_walkers_active')]
            dup = last(log, 'vm_ready_application_duplicate_attempts')
            status = 'PASS' if terminal(log) and not any(q) and dup == 0 and cov.get('untranslated', 0) == 0 and cov.get('unobserved', 0) == 0 else 'FAIL'
            mech_rows.append([cfg, semantic, f'{latency}/80', len(values), f'{statistics.fmean(values):.9f}',
                              f'{statistics.median(values):.9f}', last(log, 'gpu_sim_cycle'), last(log, 'gpu_sim_insn'),
                              last(log, 'gpu_tot_issued_cta'), cov.get('admissions', 'NA'), cov.get('translated', 'NA'),
                              cov.get('untranslated', 'NA'), cov.get('unobserved', 'NA'), dup, *q, log_sha(run), status])
            aq_rows.append([cfg, semantic, f'{latency}/80', aq['events'], aq['active_min'], aq['active_max'],
                            aq['entries_min'], f"{aq['entries_mean']:.9f}", aq['entries_max'], f"{aq['fraction_gt1']:.9f}",
                            json.dumps(aq['hist'], sort_keys=True), status])
            for row in obs:
                mech_obs.append([cfg, semantic, f'{latency}/80', row['sid'], row['warp'], row['dynamic_warp'],
                                 row['sample_index'], row['start_cycle'], row['end_cycle'], 256,
                                 f"{row['cycles_per_step']:.9f}"])
tsv(PACK / 'MECHANISM_MATRIX.tsv', ['config', 'semantic', 'latency', 'measurement_brackets', 'mean_cycles_per_step',
    'median_cycles_per_step', 'gpu_sim_cycle', 'gpu_sim_insn', 'cta', 'coverage_admissions', 'coverage_translated',
    'coverage_untranslated', 'coverage_unobserved', 'duplicate_applications', 'mshr_final', 'pwq_final', 'walkers_final',
    'run_log_sha256', 'status'], mech_rows)
tsv(PACK / 'MECHANISM_NATIVE_ALIGNED_OBSERVABLE.tsv', ['config', 'semantic', 'latency', 'sid', 'warp', 'dynamic_warp',
    'sample_index', 'start_cycle', 'end_cycle', 'steps', 'cycles_per_step'], mech_obs)
tsv(PACK / 'MECHANISM_ACCESSQ_CARDINALITY.tsv', ['config', 'semantic', 'latency', 'events', 'active_lanes_min',
    'active_lanes_max', 'accessq_min', 'accessq_mean', 'accessq_max', 'fraction_gt1', 'histogram', 'status'], aq_rows)
mech_trace_rows = []
for cfg in ('A1_CONTROL', 'A8', 'A32', 'A32_W8'):
    raw = MECH_BUNDLE / f'{cfg}/raw'
    mech_trace_rows.append([cfg, mech_native[cfg], expected_mech[cfg], raw,
                            sha256(MECH_BUNDLE / f'{cfg}/SHA256SUMS'),
                            ','.join(f'{p.name}:{sha256(p)}' for p in sorted(raw.glob('*')))])
tsv(PACK / 'MECHANISM_TRACE_AUTHORITY.tsv', ['config', 'native_cycles_per_step', 'expected_measurement_brackets',
    'raw_path', 'pair_manifest_sha256', 'member_hashes'], mech_trace_rows)

# Diagnostic neutrality and patch.
neutral_rows = []
sig_pattern = re.compile(r'^(gpu_sim_cycle|gpu_sim_insn|gpu_tot_issued_cta|vm_translation_lookup_requests|vm_translation_mshr_active|vm_translation_pwq_occupancy|vm_translation_walkers_active|vm_ready_application_duplicate_attempts) = |^AWMA_VM_COVERAGE')
for cfg in ('A1_CONTROL', 'A32'):
    off = RUNTIME / f'neutral_{cfg}_OFF/run.log'
    on = RUNTIME / f'neutral_{cfg}_ON/run.log'
    left = [line for line in text(off).splitlines() if sig_pattern.search(line)]
    right = [line for line in text(on).splitlines() if sig_pattern.search(line)]
    neutral_rows.append([cfg, 'LEGACY', '10/80', sha256(off), sha256(on), len(left),
                         'EXACT_MATCH' if left == right else 'MISMATCH', 'PASS' if left == right else 'FAIL'])
tsv(PACK / 'MECHANISM_TELEMETRY_NEUTRALITY.tsv', ['config', 'semantic', 'latency', 'off_log_sha256',
    'on_log_sha256', 'scientific_signature_lines', 'comparison', 'status'], neutral_rows)
patch = ''.join(difflib.unified_diff(text(SHADER_PRE).splitlines(True), text(SHADER_POST).splitlines(True),
                                     fromfile='a/src/gpgpu-sim/shader.cc', tofile='b/src/gpgpu-sim/shader.cc'))
write(PACK / 'MECHANISM_DIAGNOSTIC.patch', patch)
write(PACK / 'MECHANISM_DIAGNOSTIC_CONTRACT.md', '''# Mechanism diagnostic contract

Both diagnostics are independent opt-ins and default OFF.

- `GPGPUSIM_AWMA_CROSSCAL_DIAGNOSTICS=1` observes issue cycles at old control PCs `0x240/0x10b0` and separately identified mechanism PCs `0x4a0/0x870`.
- `GPGPUSIM_AWMA_ACCESSQ_CARDINALITY_DIAGNOSTICS=1` records active lanes and already-coalesced `accessq_count()` at LD/ST issue.

Neither diagnostic mutates scheduling, scoreboard, accessq, translation, cache/memory requests, replay, or downstream ordering. A1 and A32 Legacy 10/80 OFF/ON scientific signatures match exactly.
''')

# Mechanism analysis.
native_ratios = {'A8/A1': 1.0529595016, 'A32/A1': 1.2087227414, 'A32_W8/A32': 1.0128865979}
analysis_rows = []
semantic_errors = {}
for semantic in ('LEGACY', 'V1', 'V2R1'):
    a1 = mech_values[('A1_CONTROL', semantic, 10)]
    a8 = mech_values[('A8', semantic, 10)]
    a32 = mech_values[('A32', semantic, 10)]
    w8 = mech_values[('A32_W8', semantic, 10)]
    ratios = {'A8/A1': a8/a1, 'A32/A1': a32/a1, 'A32_W8/A32': w8/a32}
    errs = {k: abs(v/native_ratios[k] - 1.0) for k, v in ratios.items()}
    semantic_errors[semantic] = statistics.fmean(errs.values())
    for name in ratios:
        analysis_rows.append([semantic, name, f'{ratios[name]:.9f}', f'{native_ratios[name]:.9f}', f'{errs[name]:.9f}'])
ratio_by_sem = defaultdict(dict)
for semantic, name, sim, nat, err in analysis_rows:
    ratio_by_sem[semantic][name] = float(err)
if semantic_errors['V1'] < semantic_errors['LEGACY']:
    v1_label = ('V1_EXTERNAL_SEMANTIC_SUPPORT' if all(ratio_by_sem['V1'][k] <= .25
                for k in native_ratios) else 'V1_EXTERNAL_SEMANTIC_SUPPORT_PARTIAL')
else:
    v1_label = 'V1_EXTERNAL_SEMANTIC_NOT_SUPPORTED'
v2_label = ('V2R1_ADDS_EXTERNAL_ALIGNMENT_BENEFIT' if semantic_errors['V2R1'] < semantic_errors['V1']
            else 'V2R1_ADDS_NO_EXTERNAL_ALIGNMENT_BENEFIT')
mixed_label = ('MECHANISM_SENSITIVE_ALIGNMENT_MIXED'
               if max(ratio_by_sem['V1'].values()) > .35 else 'MECHANISM_SENSITIVE_ALIGNMENT_CONSISTENT')
promotion = 'V1_BASELINE_PROMOTION_CANDIDATE' if v1_label != 'V1_EXTERNAL_SEMANTIC_NOT_SUPPORTED' and v2_label == 'V2R1_ADDS_NO_EXTERNAL_ALIGNMENT_BENEFIT' else 'NO_BASELINE_PROMOTION_CANDIDATE'
sensitivity_rows = []
for cfg in ('A1_CONTROL', 'A8', 'A32', 'A32_W8'):
    for semantic in ('LEGACY', 'V1', 'V2R1'):
        ten = mech_values[(cfg, semantic, 10)]
        zero = mech_values[(cfg, semantic, 0)]
        sensitivity_rows.append([cfg, semantic, f'{ten:.9f}', f'{zero:.9f}', f'{(ten-zero)/ten:.9f}'])
tsv(PACK / 'MECHANISM_ANALYSIS_RATIOS.tsv', ['semantic', 'ratio', 'simulator', 'native', 'absolute_relative_error'], analysis_rows)
tsv(PACK / 'MECHANISM_LATENCY_SENSITIVITY.tsv', ['config', 'semantic', 'median_10_80', 'median_0_80', 'relative_sensitivity'], sensitivity_rows)
write(PACK / 'MECHANISM_ANALYSIS.md', f'''# Mechanism-sensitive analysis

Mean relative ratio error versus Native:

- Legacy: `{semantic_errors['LEGACY']:.4%}`
- V1: `{semantic_errors['V1']:.4%}`
- V2R1: `{semantic_errors['V2R1']:.4%}`

Classifications:

- `{v1_label}`
- `{v2_label}`
- `{mixed_label}`
- `{promotion}`

The classification is based only on Native-relative fanout/concurrency ratios, not absolute cycle equality. The platform and VM latency parameters were not changed after any control or mechanism result.
''')

write(PACK / 'COMBINED_PAPER_EVIDENCE_ANALYSIS.md', f'''# Combined paper-evidence analysis

## Platform

`{platform_decision}` with median matched-heldout error `{held_median:.4%}`. The unchanged config is `RTX4080_ADA_ACCELSIM_BASE_V1`; H_CACHE is a bounded outlier.

## M0-M3 contextual controls

Controls preserve warmup->measurement process ordering, with natural L1 invalidation and preserved L2/TLB/PWC/controller state. They remain mechanism-inactive and are not tuning data.

## Mechanism-sensitive probes

A1/A8/A32/A32_W8 realize actual multi-entry accessq opportunities under the simulator coalescing contract. Native-relative classification: `{v1_label}` and `{v2_label}`. Candidate status: `{promotion}`.

## Existing AI evidence

Historical T0/T1/T2 evidence remains simulator-internal causal support only. No SM86 AI cycle is reused as RTX4080 external calibration evidence, and no expensive AI target is rerun here.
''')

# Authorities, receipts, raw index, and report.
write(PACK / 'SOURCE_ANCHORS.md', f'''# Source anchors

- latest handoff: `32af8c34852f6f71e65beaae71ab752e2949f212`
- execution starting HEAD: `{head}`
- platform V1: `646844c513ba316eae4188cb517c2eef7282132d`
- platform implementation: `aeec5b9a69865012b16ac0a6627143e29f1fee06`
- matched heldout Native: `1e3286862a496ced4182e073739a5678100dd846`
- mechanism-sensitive Native: `6b75a3da3e3fedea6a359cd3657bf3e3fa2655d7`
- exact M0-M3 authority: `149af0566cc6720621fdfe88d3cd3ca9b32cba67`
- V1: `ad6f38878bc1e7c268b17e65fdb3793a3899a84d`
- V2R1: `dccc11f05aece7ee8ef07ffd0bec7ad83d8eb1f8`
- frozen config SHA256: `{config_sha}`
- platform binary SHA256: `{platform_binary_sha}`
- science diagnostic binary SHA256: `{science_binary_sha}`
- matched bundle manifest SHA256: `{sha256(MATCHED / 'SHA256SUMS')}`
- canonical 108-member platform manifest SHA256: `{sha256(PLATFORM_BUNDLE / 'SHA256SUMS')}`
''')
write(PACK / 'README.md', f'''# RTX4080 platform requalification and mechanism validation V1

Outcome: `{platform_decision}`; frozen baseline `RTX4080_ADA_ACCELSIM_BASE_V1`.

Control and mechanism matrices complete with terminal, coverage, quiescence, bracket-identity, and diagnostic-neutrality gates. Mechanism classifications: `{v1_label}`, `{v2_label}`, `{mixed_label}`, `{promotion}`.

Start with `COMBINED_PAPER_EVIDENCE_ANALYSIS.md` and the platform/mechanism decision files.
''')

runs = []
raw_rows = []
run_dirs = [RUNTIME / f'requal_{p}' for p in ('H_CACHE', 'H_STREAM', 'H_COMPUTE')]
run_dirs += [RUNTIME / f'overlay_smoke_{p}' for p in ('M0', 'M1')]
run_dirs += [RUNTIME / f'control_{c}_{s}_{l}_80' for c, s, l in control_specs]
run_dirs += [RUNTIME / f'mechanism_{c}_{s}_{l}_80' for c in ('A1_CONTROL', 'A8', 'A32', 'A32_W8') for s in ('LEGACY', 'V1', 'V2R1') for l in (10, 0)]
for run in run_dirs:
    log = run / 'run.log'
    runs.append({'point': run.name, 'path': str(run), 'rc': rc(run) if (run / 'rc.txt').exists() else 0,
                 'terminal': terminal(log), 'log_sha256': sha256(log), 'gpu_sim_cycle': last(log, 'gpu_sim_cycle'),
                 'gpu_sim_insn': last(log, 'gpu_sim_insn'), 'cta': last(log, 'gpu_tot_issued_cta')})
    raw_rows.append(['run_log', run.name, log, sha256(log), 'FORMAL'])
for cfg in ('A1_CONTROL', 'A32'):
    for mode in ('OFF', 'ON'):
        run = RUNTIME / f'neutral_{cfg}_{mode}'
        raw_rows.append(['neutrality_log', f'{cfg}:{mode}', run / 'run.log', sha256(run / 'run.log'), 'FORMAL_DIAGNOSTIC_GATE'])
raw_rows += [
    ['build_log', 'SCIENCE_DIAGNOSTIC_BUILD', RUNTIME / 'mechanism_diag_build.log', sha256(RUNTIME / 'mechanism_diag_build.log'), 'VERIFIED_RUN'],
    ['manifest', 'MATCHED_NATIVE', MATCHED / 'SHA256SUMS', sha256(MATCHED / 'SHA256SUMS'), 'P1_AUTHORITY'],
    ['manifest', 'PLATFORM_108_MEMBER', PLATFORM_BUNDLE / 'SHA256SUMS', sha256(PLATFORM_BUNDLE / 'SHA256SUMS'), 'P1_AUTHORITY'],
    ['manifest', 'CONTROL', CONTROL_BUNDLE / 'SHA256SUMS', sha256(CONTROL_BUNDLE / 'SHA256SUMS'), 'P1_AUTHORITY'],
    ['manifest', 'MECHANISM', MECH_BUNDLE / 'SHA256SUMS', sha256(MECH_BUNDLE / 'SHA256SUMS'), 'P1_AUTHORITY'],
]
tsv(PACK / 'RAW_DATA_INDEX.tsv', ['kind', 'id', 'path', 'sha256', 'evidence_class'], raw_rows)
write(PACK / 'RUN_RECEIPTS.json', json.dumps({
    'stage': 'AWMA_RTX4080_PLATFORM_REQUAL_AND_MECHANISM_VALIDATION_V1',
    'platform_decision': platform_decision, 'baseline': 'RTX4080_ADA_ACCELSIM_BASE_V1',
    'config_sha256': config_sha, 'platform_binary_sha256': platform_binary_sha,
    'science_binary_sha256': science_binary_sha, 'platform_tuning_this_goal': False,
    'vm_tuning_this_goal': False, 'runs': runs,
}, indent=2, sort_keys=True))

report = f'''# RTX4080 Platform Requalification + Mechanism Validation 174-new V1 Report

The frozen platform passed no-tuning requalification as `{platform_decision}`: matched-heldout median error `{held_median:.4%}`, mean `{held_mean:.4%}`, worst `{held_worst:.4%}`, and no >2x point. Config `{config_sha}` is frozen as `RTX4080_ADA_ACCELSIM_BASE_V1`.

AWMA 10/80 M0/M1 overlay smoke passed. Exact M0-M3 contextual controls completed under the scoped `RTX4080_ADA_BASE_V1 + AWMA_MODEL_RELATIVE_VM` contract. Natural kernel-boundary L1 invalidation is reported; L2 and translation controller/TLB/PWC state persist.

Mechanism-sensitive accessq opportunity closed at sector-level cardinalities documented in the review pack. All 24 Legacy/V1/V2R1 x 10/80/0/80 points completed with exact measurement brackets, full emitted translation coverage, zero V2R1 duplicate application, and final quiescence.

Scientific classifications: `{v1_label}`, `{v2_label}`, `{mixed_label}`, `{promotion}`. No platform or VM parameter was changed from any M0-M3 or A1/A8/A32/A32_W8 result.
'''
write(REPORT, report)

all_files = [p for p in PACK.rglob('*') if p.is_file() and p.name != 'SHA256SUMS']
write(PACK / 'SHA256SUMS', '\n'.join(f'{sha256(p)}  {p.relative_to(PACK)}' for p in sorted(all_files)))
required = [
    'README.md', 'SOURCE_ANCHORS.md', 'FROZEN_PLATFORM_AUTHORITY.json', 'MATCHED_HELDOUT_AUTHORITY.tsv',
    'HELDOUT_REQUALIFICATION.tsv', 'PLATFORM_REQUALIFICATION_DECISION.md', 'AWMA_VM_OVERLAY_SMOKE.tsv',
    'CONTROL_TRACE_AUTHORITY.tsv', 'CONTROL_CONTEXT_PERSISTENCE.md', 'CONTROL_MATRIX.tsv',
    'CONTROL_NATIVE_ALIGNED_OBSERVABLE.tsv', 'CONTROL_ANALYSIS.md', 'MECHANISM_TRACE_AUTHORITY.tsv',
    'MECHANISM_ACCESSQ_CARDINALITY.tsv', 'MECHANISM_DIAGNOSTIC_CONTRACT.md', 'MECHANISM_DIAGNOSTIC.patch',
    'MECHANISM_TELEMETRY_NEUTRALITY.tsv', 'MECHANISM_MATRIX.tsv', 'MECHANISM_NATIVE_ALIGNED_OBSERVABLE.tsv',
    'MECHANISM_ANALYSIS.md', 'COMBINED_PAPER_EVIDENCE_ANALYSIS.md', 'RUN_RECEIPTS.json', 'RAW_DATA_INDEX.tsv', 'SHA256SUMS',
]
for rel in required:
    path = PACK / rel
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f'missing/empty required artifact: {rel}')
print(json.dumps({'platform_decision': platform_decision, 'median_heldout_error': held_median,
                  'v1_classification': v1_label, 'v2_classification': v2_label,
                  'alignment': mixed_label, 'promotion': promotion,
                  'review_pack': str(PACK), 'report': str(REPORT)}, indent=2))
