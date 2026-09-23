#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import statistics
import subprocess
from pathlib import Path

REPO = Path('/root/workspace/accel-sim-framework-awma-174-rtx4080-ada-platform-qualification-v1')
RUNTIME = Path('/root/awma_rtx4080_ada_platform_qualification_v1_runtime')
BUNDLE = Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/rtx4080_platform_anchors_v1_20260923T115000Z')
PACK = REPO / 'docs/vm_tlb/review_packs/AWMA_RTX4080_ADA_ACCELSIM_PLATFORM_QUALIFICATION_V1'
REPORT = REPO / 'docs/vm_tlb/codex_handoff/awma/RTX4080_ADA_ACCELSIM_PLATFORM_QUALIFICATION_174NEW_V1_REPORT.md'
CONFIG_DIR = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
BINARY = REPO / 'gpu-simulator/bin/release/accel-sim.out'
IMPLEMENTATION_SHA = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
ANCHOR_BRANCH_SHA = '6b75a3da3e3fedea6a359cd3657bf3e3fa2655d7'
CORE_SOURCE = RUNTIME / 'src/gpgpu-sim'
CORE_SOURCE_AUTHORITY = 'V2R1 reconstructed source; framework authority dccc11f05aece7ee8ef07ffd0bec7ad83d8eb1f8'


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + '\n')


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(header)
        w.writerows(rows)


def stat(log: Path, key: str) -> int:
    vals = re.findall(rf'^{re.escape(key)} = (\d+)$', log.read_text(errors='replace'), re.M)
    if not vals:
        raise RuntimeError(f'missing {key}: {log}')
    return int(vals[-1])


def terminal(log: Path) -> bool:
    t = log.read_text(errors='replace')
    return 'GPGPU-Sim: *** simulation thread exiting ***' in t and 'GPGPU-Sim: *** exit detected ***' in t


def unsupported(log: Path) -> list[str]:
    return re.findall(r'unsupported[^\n]*', log.read_text(errors='replace'), re.I)


def measured_bracket(log: Path) -> float:
    events = []
    for line in log.read_text(errors='replace').splitlines():
        m = re.match(r'awma_crosscal_event .* pc=0x([0-9a-f]+) cycle=(\d+)$', line)
        if m:
            events.append((int(m.group(1), 16), int(m.group(2))))
    pairs = []
    start = None
    for pc, cycle in events:
        if pc == 0x240:
            start = cycle
        elif pc == 0x10B0 and start is not None:
            pairs.append((cycle - start) / 512.0)
            start = None
    if len(pairs) != 2:
        raise RuntimeError(f'expected two brackets in {log}, got {pairs}')
    return pairs[1]


def median_col(files: list[Path], field: str) -> tuple[list[float], float]:
    medians = []
    for path in files:
        with path.open(newline='') as f:
            vals = [float(row[field]) for row in csv.DictReader(f, delimiter='\t')]
        medians.append(statistics.median(vals))
    return medians, statistics.median(medians)


def one_row_values(files: list[Path]) -> list[dict[str, str]]:
    rows = []
    for path in files:
        with path.open(newline='') as f:
            rows.append(next(csv.DictReader(f, delimiter='\t')))
    return rows


PACK.mkdir(parents=True, exist_ok=True)
v0_dir = PACK / 'RTX4080_BASE_CONFIG_V0'
final_dir = PACK / 'FINAL_RTX4080_BASE_CONFIG'
v0_dir.mkdir(exist_ok=True)
final_dir.mkdir(exist_ok=True)
shutil.copy2(CONFIG_DIR / 'gpgpusim.v0.config', v0_dir / 'gpgpusim.config')
shutil.copy2(TRACE_CONFIG, v0_dir / 'trace.config')
shutil.copy2(CONFIG_DIR / 'gpgpusim.config', final_dir / 'gpgpusim.config')
shutil.copy2(TRACE_CONFIG, final_dir / 'trace.config')

binary_sha = sha256(BINARY)
final_config_sha = sha256(CONFIG_DIR / 'gpgpusim.config')
v0_config_sha = sha256(CONFIG_DIR / 'gpgpusim.v0.config')
pass1_config_sha = sha256(CONFIG_DIR / 'gpgpusim.pass1.config')
trace_config_sha = sha256(TRACE_CONFIG)
bundle_manifest_sha = sha256(BUNDLE / 'SHA256SUMS')

native_cal = {}
for point in ('P_L1', 'P_L2', 'P_DRAM'):
    reps, med = median_col(sorted((BUNDLE / 'timing').glob(f'{point}_rep*.tsv')), 'cycles_per_load')
    native_cal[point] = {'replicate_medians': reps, 'median': med}
bw_rows = one_row_values(sorted((BUNDLE / 'timing').glob('P_BW_rep*.tsv')))
native_bw = statistics.median(float(r['gb_per_s']) for r in bw_rows)

pass_specs = [
    ('V0', 'v0diag', {'P_L1': 39, 'P_L2': 187, 'P_DRAM': 254}, '05fe79751bbaab6bdb065ea7b014a10011786e591be2bf0ef00217b1d8ca578f'),
    ('TUNING_PASS_1', 'pass1', {'P_L1': 32, 'P_L2': 0, 'P_DRAM': 254}, 'f537f648629341d36cdaccb81b8e8f0d1dba3e92adb98ab970723f049f906e4b'),
    ('TUNING_PASS_2_FINAL', 'final_cal', {'P_L1': 32, 'P_L2': 0, 'P_DRAM': 190}, final_config_sha),
]
cal_rows = []
for pass_name, prefix, params, config_sha in pass_specs:
    for point in ('P_L1', 'P_L2', 'P_DRAM'):
        log = RUNTIME / f'{prefix}_{point}' / 'run.log'
        sim = measured_bracket(log)
        native = native_cal[point]['median']
        err = abs(sim - native) / native
        cal_rows.append([
            pass_name, point, f'{native:.9f}', f'{sim:.9f}', f'{err:.9f}',
            'MEASURED_OCCURRENCE1_CLOCK64_BRACKET', params['P_L1'], params['P_L2'], params['P_DRAM'],
            config_sha, sha256(log), 'TERMINAL_PASS' if terminal(log) else 'FAIL'
        ])
cal_rows.append([
    'V0', 'P_BW', f'{native_bw:.9f}', 'NA', 'NA', 'NATIVE_GB_PER_S', 39, 187, 254,
    '05fe79751bbaab6bdb065ea7b014a10011786e591be2bf0ef00217b1d8ca578f',
    sha256(RUNTIME / 'v0_P_BW/run.log'),
    'NOT_COMPARABLE_TRACE_SCALE_MISMATCH_NATIVE_67108864x100_TRACE_4096x1'
])
write_tsv(PACK / 'CALIBRATION_RESULTS.tsv', [
    'pass', 'point', 'native_metric', 'sim_metric', 'absolute_relative_error', 'metric_contract',
    'l1_latency', 'l2_rop_latency', 'dram_latency', 'config_sha256', 'run_log_sha256', 'status'
], cal_rows)

held_native = {}
for point in ('H_CACHE', 'H_STREAM', 'H_COMPUTE'):
    rows = one_row_values(sorted((BUNDLE / 'heldout/timing').glob(f'{point}_rep*.tsv')))
    held_native[point] = {
        'elapsed_ms': statistics.median(float(r['elapsed_ms']) for r in rows),
        'elements': int(rows[0]['elements']),
        'repetitions': int(rows[0]['repetitions']),
    }
trace_scale = {
    'H_CACHE': (1024, 1, 'COMPARABLE_SAME_ELEMENT_COUNT_PER_LAUNCH'),
    'H_STREAM': (4096, 1, 'INVALID_RUNTIME_COMPARISON_TRACE_SCALE_MISMATCH'),
    'H_COMPUTE': (1024, 1, 'INVALID_RUNTIME_COMPARISON_TRACE_SCALE_MISMATCH'),
}
held_rows = []
valid_errors = []
for point in ('H_CACHE', 'H_STREAM', 'H_COMPUTE'):
    log = RUNTIME / f'final_heldout_{point}' / 'run.log'
    cycles = stat(log, 'gpu_sim_cycle')
    sim_us = cycles / 2505.0
    native_us = held_native[point]['elapsed_ms'] * 1000.0 / held_native[point]['repetitions']
    trace_elements, trace_reps, validity = trace_scale[point]
    if validity.startswith('COMPARABLE'):
        error = abs(sim_us - native_us) / native_us
        valid_errors.append(error)
        error_text = f'{error:.9f}'
    else:
        error_text = 'NA'
    held_rows.append([
        point, held_native[point]['elements'], held_native[point]['repetitions'],
        f"{held_native[point]['elapsed_ms']:.9f}", f'{native_us:.9f}', trace_elements, trace_reps,
        cycles, f'{sim_us:.9f}', error_text, validity,
        stat(log, 'gpu_sim_insn'), stat(log, 'gpu_tot_issued_cta'), final_config_sha, sha256(log),
        'TERMINAL_PASS' if terminal(log) else 'FAIL'
    ])
write_tsv(PACK / 'HELDOUT_VALIDATION_RESULTS.tsv', [
    'point', 'native_elements', 'native_repetitions', 'native_elapsed_ms_median', 'native_us_per_launch',
    'trace_elements', 'trace_repetitions', 'sim_cycles', 'sim_us_per_launch_at_2505MHz',
    'absolute_relative_error', 'comparison_validity', 'sim_instructions', 'sim_cta',
    'config_sha256', 'run_log_sha256', 'status'
], held_rows)

parameter_rows = [
    ['compute_capability', '8.9', 'PUBLIC_RTX4080_SPEC', 'NVIDIA CUDA GPU table and RTX4080 product page', 'exact identity'],
    ['gpgpu_n_clusters', '76', 'PUBLIC_RTX4080_SPEC', 'NVIDIA Ada whitepaper Appendix B: RTX4080 SMs=76', 'one cluster/core per SM'],
    ['gpgpu_n_cores_per_cluster', '1', 'UPSTREAM_ADA_SCAFFOLD', 'dc56ca74 RTX4060 Ada scaffold', 'standard trace-driven topology'],
    ['gpgpu_unified_l1d_size', '128 KiB/SM', 'PUBLIC_RTX4080_SPEC', 'NVIDIA Ada whitepaper: Ada SM 128KB L1/shared', 'capacity authority'],
    ['gpgpu_cache_dl2', '64 MiB total; S:2048:128:16', 'PUBLIC_RTX4080_SPEC', 'NVIDIA Ada whitepaper RTX4080 L2=65536KB', 'geometry maps public capacity onto scaffold'],
    ['gpgpu_n_mem', '8', 'PUBLIC_RTX4080_SPEC', 'NVIDIA Ada whitepaper: eight 32-bit controllers', 'memory channel count'],
    ['gpgpu_dram_buswidth', '4 bytes', 'PUBLIC_RTX4080_SPEC', 'eight 32-bit controllers / 256-bit total', 'per-channel width'],
    ['gpgpu_clock_domains', '2505:2505:2505:5600 MHz', 'PUBLIC_RTX4080_SPEC', '2505MHz boost; 22.4Gbps GDDR6X /4 command clock', 'ICNT/L2 equal-core ratio inherited from Ada scaffold'],
    ['memory_bandwidth_class', '716.8 GB/s', 'PUBLIC_RTX4080_SPEC', 'NVIDIA Ada whitepaper Appendix B', '8*4B*16 burst*5600MHz/4'],
    ['gpgpu_shader_registers', '65536', 'PUBLIC_RTX4080_SPEC', '19456KB total register file / 76 SM / 4-byte register', 'also matches Ada scaffold'],
    ['pipeline_and_fu_topology', 'Ada scaffold values', 'UPSTREAM_ADA_SCAFFOLD', 'dc56ca74', 'not claimed as exact RTX4080 issue-port topology'],
    ['instruction_latencies', 'Ada scaffold values', 'UPSTREAM_ADA_SCAFFOLD', '0c840b27 trace config and dc56ca74 base config', 'subset support only'],
    ['scheduler', 'lrr; 4 schedulers', 'UPSTREAM_ADA_SCAFFOLD', 'dc56ca74', 'ASSUMED_LOW_SENSITIVITY for platform anchors'],
    ['l1_latency', '32 cycles', 'BOUNDED_CALIBRATION', 'P_L1 dedicated calibration anchor; pass1', '39->32'],
    ['l2_rop_latency', '0 cycles', 'BOUNDED_CALIBRATION', 'P_L2 dedicated calibration anchor; pass1', '187->0 removes scaffold fixed overcount; modeled L2 path remains'],
    ['dram_latency', '190 cycles', 'BOUNDED_CALIBRATION', 'P_DRAM dedicated calibration anchor; pass2', '254->190'],
    ['dram_timing_tuple', 'scaffold tuple unchanged', 'UPSTREAM_ADA_SCAFFOLD', 'dc56ca74', 'no undocumented knob sweep'],
    ['interconnect', 'built-in local xbar', 'ASSUMED_LOW_SENSITIVITY', 'dc56ca74 scaffold', 'not claimed as exact RTX4080 NoC'],
    ['vm_mode_during_platform_qualification', '0', 'NEAREST_VALIDATED_INHERITANCE', 'existing VM-disabled base path', 'no TLB/PTW parameter used for calibration'],
]
write_tsv(PACK / 'PARAMETER_PROVENANCE.tsv', ['parameter', 'value', 'provenance_class', 'authority', 'scope_note'], parameter_rows)

write_tsv(PACK / 'PLATFORM_TUNING_LEDGER.tsv', [
    'pass', 'parameter', 'old_value', 'new_value', 'justification', 'evidence_anchor', 'effect'
], [
    ['TUNING_PASS_1', 'gpgpu_l1_latency', 39, 32, 'reduce steady-state L1-class excess only', 'P_L1', '61.328125 -> 54.341797 cycles/load; Native 52'],
    ['TUNING_PASS_1', 'gpgpu_l2_rop_latency', 187, 0, 'remove fixed Ada-scaffold L2/ROP overcount while retaining modeled L2 path', 'P_L2', '256.945312 -> 63.324219 cycles/load; Native 52'],
    ['TUNING_PASS_2', 'dram_latency', 254, 190, 'reduce remaining DRAM-class fixed latency excess', 'P_DRAM', '217.857422 -> 182.857422 cycles/load; Native 154'],
])

anchor_rows = [
    ['CALIBRATION', 'P_L1', 'small pointer chain', 'cycles/load', '52', '65536 bytes; 1 warp; 512 steps', 'same trace control flow; occurrence1 metric', 'a9488afa190ba1e27e58f840b07f1db092177c5a097773ce6a8934262e37357f'],
    ['CALIBRATION', 'P_L2', 'medium pointer chain', 'cycles/load', '52', '2097152 bytes; 1 warp; 512 steps', 'same trace control flow; occurrence1 metric', 'a9488afa190ba1e27e58f840b07f1db092177c5a097773ce6a8934262e37357f'],
    ['CALIBRATION', 'P_DRAM', 'large-stride pointer chain', 'cycles/load', '154', '2147483648 bytes; 1 warp; 512 steps', 'same trace control flow; occurrence1 metric', 'a9488afa190ba1e27e58f840b07f1db092177c5a097773ce6a8934262e37357f'],
    ['CALIBRATION', 'P_BW', 'stream copy', 'GB/s', f'{native_bw:.6f}', 'Native 67108864x100; trace 4096x1', 'NOT_COMPARABLE_TRACE_SCALE_MISMATCH', 'd38ee67742c8a972df36be9478346328ca8e53105234093b7b3d2240a4347265'],
    ['HELDOUT_VALIDATION', 'H_CACHE', 'cache-friendly', 'runtime/launch', f"{held_native['H_CACHE']['elapsed_ms']:.6f}ms/100", 'Native 1024x100; trace 1024x1', 'COMPARABLE_PER_LAUNCH', 'fa76556cb9e673e25954a6c03af66790091fbef074d6e558c270c5f5ae0cfb1c'],
    ['HELDOUT_VALIDATION', 'H_STREAM', 'streaming', 'runtime/launch', f"{held_native['H_STREAM']['elapsed_ms']:.6f}ms/100", 'Native 67108864x100; trace 4096x1', 'NOT_COMPARABLE_TRACE_SCALE_MISMATCH', 'fa76556cb9e673e25954a6c03af66790091fbef074d6e558c270c5f5ae0cfb1c'],
    ['HELDOUT_VALIDATION', 'H_COMPUTE', 'compute/mixed', 'runtime/launch', f"{held_native['H_COMPUTE']['elapsed_ms']:.6f}ms/100", 'Native 1048576x100; trace 1024x1', 'NOT_COMPARABLE_TRACE_SCALE_MISMATCH', 'fa76556cb9e673e25954a6c03af66790091fbef074d6e558c270c5f5ae0cfb1c'],
]
write_tsv(PACK / 'PLATFORM_ANCHOR_AUTHORITY.tsv', [
    'role', 'point', 'dimension', 'native_metric', 'native_value', 'workload_authority', 'comparison_scope', 'source_binary_sha256'
], anchor_rows)

smoke_specs = [
    ('P_L1', RUNTIME / 'final_cal_P_L1/run.log', 'PLATFORM_CALIBRATION'),
    ('P_L2', RUNTIME / 'final_cal_P_L2/run.log', 'PLATFORM_CALIBRATION'),
    ('P_DRAM', RUNTIME / 'final_cal_P_DRAM/run.log', 'PLATFORM_CALIBRATION'),
    ('H_CACHE', RUNTIME / 'final_heldout_H_CACHE/run.log', 'HELDOUT'),
    ('H_STREAM', RUNTIME / 'final_heldout_H_STREAM/run.log', 'HELDOUT'),
    ('H_COMPUTE', RUNTIME / 'final_heldout_H_COMPUTE/run.log', 'HELDOUT'),
    ('M0', RUNTIME / 'final_smoke_M0/run.log', 'PARSER_SMOKE_ONLY_NO_TUNING'),
    ('M1', RUNTIME / 'final_smoke_M1/run.log', 'PARSER_SMOKE_ONLY_NO_TUNING'),
    ('AI_T2', RUNTIME / 'final_smoke_AI_T2/run.log', 'PARSER_SMOKE_ONLY_NO_TUNING'),
]
subset_rows = []
runs = []
raw_rows = [['build_log', 'V0_COLD_BUILD', RUNTIME / 'v0_build.log', sha256(RUNTIME / 'v0_build.log'), 'VERIFIED_RUN']]
for name, log, role in smoke_specs:
    row = [name, role, stat(log, 'gpu_sim_cycle'), stat(log, 'gpu_sim_insn'), stat(log, 'gpu_tot_issued_cta'),
           len(unsupported(log)), 'PASS' if terminal(log) and not unsupported(log) else 'FAIL', sha256(log)]
    subset_rows.append(row)
    runs.append({'name': name, 'role': role, 'log': str(log), 'log_sha256': sha256(log),
                 'cycles': row[2], 'instructions': row[3], 'cta': row[4], 'terminal': terminal(log),
                 'unsupported_opcode_count': row[5]})
    raw_rows.append(['run_log', name, log, sha256(log), role])
for pass_name, prefix, _, _ in pass_specs[:2]:
    for point in ('P_L1', 'P_L2', 'P_DRAM'):
        log = RUNTIME / f'{prefix}_{point}/run.log'
        raw_rows.append(['calibration_run_log', f'{pass_name}:{point}', log, sha256(log), 'BOUNDED_CALIBRATION'])
raw_rows.append(['anchor_manifest', 'NODE109_PLATFORM_BUNDLE', BUNDLE / 'SHA256SUMS', bundle_manifest_sha, 'P1_DURABLE_AUTHORITY'])
write_tsv(PACK / 'SM89_SUBSET_QUALIFICATION.tsv', [
    'trace', 'role', 'cycles', 'instructions', 'cta', 'unsupported_opcode_count', 'status', 'run_log_sha256'
], subset_rows)
write_tsv(PACK / 'RAW_DATA_INDEX.tsv', ['kind', 'id', 'path', 'sha256', 'evidence_class'], raw_rows)

write(PACK / 'AWMA_VM_OVERLAY_SMOKE.tsv',
      'test\tstatus\treason\nM0_10_80\tSKIPPED\tPLATFORM_NOT_QUALIFIED_PHASE_K_REQUIRES_PASS_OR_SCOPED_PASS\n'
      'M1_10_80\tSKIPPED\tPLATFORM_NOT_QUALIFIED_PHASE_K_REQUIRES_PASS_OR_SCOPED_PASS')

write(PACK / 'SOURCE_ANCHORS.md', f'''# Source anchors

- handoff HEAD: `de1ab24c6c550f8905adc845839ed8d7154a542d`
- implementation commit: `{IMPLEMENTATION_SHA}`
- execution branch: `hrl/awma-174-rtx4080-ada-platform-qualification-v1`
- prep authority: `a04085f73458c9d30537640c2f7daad4a3aa3dd7`
- exact Native control authority: `149af0566cc6720621fdfe88d3cd3ca9b32cba67`
- V1 authority: `ad6f38878bc1e7c268b17e65fdb3793a3899a84d`
- V2R1 authority: `dccc11f05aece7ee8ef07ffd0bec7ad83d8eb1f8`
- reconstructed Core source: `{CORE_SOURCE_AUTHORITY}`
- upstream Framework PR reference: `0c840b276bfecc6c7d1590efd7d5a22b8dff05f6`
- upstream gpgpu-sim Ada scaffold: `dc56ca74fa51d333cacb6a8aac91bce804301ae1`
- node109 platform-anchor publication commit: `{ANCHOR_BRANCH_SHA}`
- node164 bundle: `{BUNDLE}`
- node164 manifest SHA256: `{bundle_manifest_sha}`
- final binary SHA256: `{binary_sha}`
- final config SHA256: `{final_config_sha}`
- trace config SHA256: `{trace_config_sha}`
''')

write(PACK / 'UPSTREAM_ADA_REFERENCE.md', '''# Upstream Ada engineering reference

Reviewed, not merged wholesale:

- Framework PR #548: https://github.com/accel-sim/accel-sim-framework/pull/548
- exact Framework head: `0c840b276bfecc6c7d1590efd7d5a22b8dff05f6`
- matching contributor gpgpu-sim branch head: `dc56ca74fa51d333cacb6a8aac91bce804301ae1`

Selectively reused:

- binary version 89 constant;
- SM89 to Ampere opcode-map selection;
- trace-config conventions;
- closest available Ada base-config scaffold.

Not accepted as hardware authority: the PR is open/unmerged; the 4060 Laptop scale and undocumented pipeline values are not RTX4080 facts. The already-qualified local SM89 subset audit remains parser-admission evidence only, not full Ada ISA fidelity.
''')

write(PACK / 'RTX4080_PUBLIC_SPEC_AUTHORITY.md', '''# RTX4080 public specification authority

Primary public authorities:

1. NVIDIA GeForce RTX4080 family specifications: https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4080-family/
   - 9728 CUDA cores, 2.51 GHz boost, 2.21 GHz base, 16 GB GDDR6X, 256-bit interface, CUDA capability 8.9.
2. NVIDIA CUDA GPU compute-capability table: https://developer.nvidia.com/cuda/gpus
   - GeForce RTX4080 is compute capability 8.9.
3. NVIDIA Ada GPU Architecture whitepaper: https://images.nvidia.com/aem-dam/Solutions/geforce/ada/nvidia-ada-gpu-architecture.pdf
   - Appendix B identifies RTX4080 AD103 with 76 SMs, 128 CUDA cores/SM, 2505 MHz boost, 22.4 Gbps GDDR6X, 716.8 GB/s, 65536 KB L2, 9728 KB aggregate L1/shared, 19456 KB register file, and eight 32-bit memory controllers.

These sources establish scale and bandwidth class. They do not establish proprietary scheduler, cache-replacement, exact issue-port, or TLB/PTW details.
''')

hcache_error = valid_errors[0]
decision = f'''# Qualification decision

Decision: `RTX4080_ADA_PLATFORM_NOT_QUALIFIED`

The best defensible config was frozen after exactly two tuning passes. Calibration-anchor occurrence1 errors are P_L1 4.50%, P_L2 21.78%, and P_DRAM 18.74%, with the correct L1 < L2 < DRAM direction.

The predeclared held-out gate cannot pass:

- H_CACHE is the only scale-comparable held-out point. Native is 1.762880 us/launch and simulator is 2.529341 us/launch, absolute error `{hcache_error:.2%}`, above the 35% scoped ceiling.
- H_STREAM changes from 67,108,864 elements x100 Native to 4,096 elements x1 in the trace.
- H_COMPUTE changes from 1,048,576 elements x100 Native to 1,024 elements x1 in the trace.
- The latter two are parser-valid but not valid runtime-error points; treating their raw runtimes as comparable would fabricate evidence.

Therefore there are not three valid held-out points and even the sole comparable point exceeds the scoped threshold. No `RTX4080_ADA_ACCELSIM_BASE_V1` authority is promoted. No third tuning pass, held-out-driven tuning, VM/TLB tuning, M0-M3 tuning, or mechanism study was performed.

Required recovery is external evidence, not more simulator tuning: publish workload-scale-matched held-out traces or a predeclared, defensible scale-normalized observable, then rerun the frozen config without changing it.
'''
write(PACK / 'QUALIFICATION_DECISION.md', decision)

write(PACK / 'README.md', f'''# AWMA RTX4080 Ada Accel-Sim Platform Qualification V1

Start with `QUALIFICATION_DECISION.md`.

Outcome: `RTX4080_ADA_PLATFORM_NOT_QUALIFIED`.

The engineering portion succeeded: public RTX4080 scale, reviewed upstream SM89/Ada support, a cold-built binary, terminal parser execution for generic anchors plus M0/M1/AI T2, and exactly two bounded calibration passes. The frozen candidate has calibration errors below 22% for the three comparable pointer anchors.

The qualification gate failed because only one of three held-out traces preserves Native workload scale, and that point has 43.48% error. The other two traces are useful parser smokes but cannot support runtime error. This pack intentionally does not promote a publication baseline and does not run the post-qualification AWMA VM overlay smoke.

Implementation commit: `{IMPLEMENTATION_SHA}`. Final config SHA256: `{final_config_sha}`. Binary SHA256: `{binary_sha}`.
''')

report = f'''# RTX4080 / Ada Accel-Sim Platform Qualification 174-new V1 Report

Qualification result: `RTX4080_ADA_PLATFORM_NOT_QUALIFIED`.

The RTX4080/Ada candidate was implemented from reviewed upstream SM89 support and the closest Ada scaffold, with public RTX4080 scale substituted explicitly. It cold-built and terminally replayed all platform anchors, M0, M1, and one AI T2 trace with no unsupported opcode in the exercised subset. This is subset admission, not full Ada ISA fidelity.

V0 used public 76-SM / 64-MiB-L2 / 256-bit / 22.4-Gbps / 2.505-GHz scale. Exactly two calibration passes were used: L1 latency 39->32, fixed L2/ROP latency 187->0, and DRAM latency 254->190. Final calibration errors are 4.50% (P_L1), 21.78% (P_L2), and 18.74% (P_DRAM), with correct hierarchy direction. P_BW Native is 609.014 GB/s, but its 4K-element trace is not comparable to the 67M-element Native timing and was not used to tune.

Held-out validation is insufficient and above threshold. H_CACHE preserves scale but has 43.48% runtime error. H_STREAM and H_COMPUTE shrink workload size by 16,384x and 1,024x respectively, so their trace runtimes are invalid as error points. The required three-point held-out median cannot be computed honestly.

The best candidate is frozen after pass 2, but no `RTX4080_ADA_ACCELSIM_BASE_V1` is promoted. Phase-K AWMA 10/80 overlay smoke is skipped because it is authorized only after PASS or scoped PASS. Recovery requires corrected held-out evidence and a no-tuning replay of the frozen config.

Review pack: `docs/vm_tlb/review_packs/AWMA_RTX4080_ADA_ACCELSIM_PLATFORM_QUALIFICATION_V1/`.
'''
write(REPORT, report)

receipts = {
    'stage': 'AWMA_RTX4080_ADA_ACCELSIM_PLATFORM_QUALIFICATION_V1',
    'decision': 'RTX4080_ADA_PLATFORM_NOT_QUALIFIED',
    'implementation_commit': IMPLEMENTATION_SHA,
    'runtime_root': str(RUNTIME),
    'core_source': str(CORE_SOURCE),
    'core_source_authority': CORE_SOURCE_AUTHORITY,
    'binary_sha256': binary_sha,
    'final_config_sha256': final_config_sha,
    'v0_config_sha256_whitespace_normalized_publication_copy': v0_config_sha,
    'pass1_config_sha256_whitespace_normalized_publication_copy': pass1_config_sha,
    'trace_config_sha256': trace_config_sha,
    'anchor_bundle': str(BUNDLE),
    'anchor_manifest_sha256': bundle_manifest_sha,
    'anchor_manifest_check': 'PASS',
    'tuning_passes_used': 2,
    'heldout_tuning_performed': False,
    'm0_m1_tuning_performed': False,
    'vm_tlb_tuning_performed': False,
    'runs': runs,
}
write(PACK / 'RUN_RECEIPTS.json', json.dumps(receipts, indent=2, sort_keys=True))

all_files = [p for p in PACK.rglob('*') if p.is_file() and p.name != 'SHA256SUMS']
write(PACK / 'SHA256SUMS', '\n'.join(f'{sha256(p)}  {p.relative_to(PACK)}' for p in sorted(all_files)))

required = [
    'README.md', 'SOURCE_ANCHORS.md', 'UPSTREAM_ADA_REFERENCE.md', 'RTX4080_PUBLIC_SPEC_AUTHORITY.md',
    'PARAMETER_PROVENANCE.tsv', 'SM89_SUBSET_QUALIFICATION.tsv', 'PLATFORM_ANCHOR_AUTHORITY.tsv',
    'CALIBRATION_RESULTS.tsv', 'PLATFORM_TUNING_LEDGER.tsv', 'HELDOUT_VALIDATION_RESULTS.tsv',
    'QUALIFICATION_DECISION.md', 'AWMA_VM_OVERLAY_SMOKE.tsv', 'RUN_RECEIPTS.json', 'RAW_DATA_INDEX.tsv', 'SHA256SUMS',
    'RTX4080_BASE_CONFIG_V0/gpgpusim.config', 'RTX4080_BASE_CONFIG_V0/trace.config',
    'FINAL_RTX4080_BASE_CONFIG/gpgpusim.config', 'FINAL_RTX4080_BASE_CONFIG/trace.config',
]
for rel in required:
    p = PACK / rel
    if not p.is_file() or p.stat().st_size == 0:
        raise RuntimeError(f'missing/empty required artifact: {rel}')
print(json.dumps({'pack': str(PACK), 'report': str(REPORT), 'required_files': len(required),
                  'decision': 'RTX4080_ADA_PLATFORM_NOT_QUALIFIED', 'implementation_sha': IMPLEMENTATION_SHA}, indent=2))
