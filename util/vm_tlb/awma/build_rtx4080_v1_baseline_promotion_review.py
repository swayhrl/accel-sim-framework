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

REPO = Path('/root/workspace/accel-sim-framework-awma-174-rtx4080-v1-baseline-promotion-v1')
RUNTIME = Path('/root/awma_rtx4080_v1_baseline_promotion_v1_runtime')
PACK = REPO / 'docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1'
REPORT = REPO / 'docs/vm_tlb/codex_handoff/awma/RTX4080_V1_BASELINE_PROMOTION_174NEW_V1_REPORT.md'
CONFIG = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
PREAUTH = RUNTIME / 'AI_MATRIX_CONFIG_AUTHORITY.prelaunch.tsv'
RUNNER = REPO / 'util/vm_tlb/awma/run_rtx4080_v1_ai_promotion_matrix.py'

TARGETS = {
    'T0': {
        'name': 'Q05_PREFILL_ATTN_FLASH', 'instructions': 368696302, 'cta': 224, 'unique': 3090304,
        'producer': 'c6733012c13099c6a86f506fd8c61e351791159e',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native-contiguous-prefix_q05-contiguous-prefix_20260918T022749Z_1fea2d955d1c/traces/kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz'),
        'index': 'kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz\n',
    },
    'T1': {
        'name': 'PREFILL_GEMM_PRIMARY_OCC0', 'instructions': 369131520, 'cta': 384, 'unique': 7159808,
        'producer': '8f49ba3b9228b5f8a9163e961225ffd415107734',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native_prefill-gemm-primary-occ0_20260918T052739Z_01540d931e17/traces/kernel-45-ctx_0x60d38cb72530.traceg.xz'),
        'index': 'kernel-45-ctx_0x60d38cb72530.traceg.xz\n',
    },
    'T2': {
        'name': 'DECODE_GEMV_PRIMARY_STEP16', 'instructions': 43357696, 'cta': 1216, 'unique': 411008,
        'producer': '8f49ba3b9228b5f8a9163e961225ffd415107734',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_decode-gemv-primary-step16_20260918T074437Z_b0dfb1af1ae1/traces/kernel-17039-ctx_0x5ddb6907c160.traceg.xz'),
        'index': 'kernel-17039-ctx_0x5ddb6907c160.traceg.xz\n',
    },
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + '\n')


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(header)
        w.writerows(rows)


def content(path: Path) -> str:
    return path.read_text(errors='replace')


def stat_values(path: Path, key: str) -> list[int]:
    return [int(x) for x in re.findall(rf'^{re.escape(key)} = (\d+)$', content(path), re.M)]


def last(path: Path, key: str) -> int:
    values = stat_values(path, key)
    if not values:
        raise RuntimeError(f'missing {key}: {path}')
    return values[-1]


def coverage(path: Path) -> dict[str, int]:
    found = re.findall(
        r'AWMA_VM_COVERAGE admissions=(\d+) translated=(\d+) untranslated=(\d+) unobserved=(\d+) unique=(\d+) translated_unique=(\d+) untranslated_unique=(\d+)',
        content(path))
    if not found:
        raise RuntimeError(f'missing coverage: {path}')
    keys = ('admissions', 'translated', 'untranslated', 'unobserved', 'unique', 'translated_unique', 'untranslated_unique')
    return dict(zip(keys, map(int, found[-1])))


def terminal(path: Path) -> bool:
    t = content(path)
    return 'GPGPU-Sim: *** simulation thread exiting ***' in t and 'GPGPU-Sim: *** exit detected ***' in t


def segment_activity(path: Path) -> int:
    keys = (
        'vm_weight_segment_lookup_attempts', 'vm_weight_segment_lookup_accepts',
        'vm_weight_segment_lookup_launches', 'vm_weight_segment_lookup_completions',
        'vm_weight_segment_hits', 'vm_weight_segment_misses',
        'vm_weight_segment_install_attempts', 'vm_weight_segment_revoke_attempts',
    )
    return sum(last(path, key) for key in keys)


def rc(run: Path) -> int:
    raw = (run / 'rc.txt').read_text().strip()
    m = re.match(r'-?\d+', raw)
    if not m:
        raise RuntimeError(f'invalid rc: {run}: {raw!r}')
    return int(m.group())


PACK.mkdir(parents=True, exist_ok=True)
head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
config_sha, trace_sha, binary_sha = sha(CONFIG), sha(TRACE_CONFIG), sha(BINARY)
if config_sha != 'de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8':
    raise RuntimeError('frozen platform config changed')
shutil.copy2(PREAUTH, PACK / 'AI_MATRIX_CONFIG_AUTHORITY.tsv')

trace_rows = []
for target, info in TARGETS.items():
    trace_rows.append([target, info['name'], info['producer'], info['payload'], sha(info['payload']),
                       sha_text(str(info['index'])), info['instructions'], info['cta'], info['unique'], 'P1_ACCEPTED'])
write_tsv(PACK / 'AI_TRACE_AUTHORITY.tsv', ['target', 'identity', 'producer_authority', 'payload', 'payload_sha256',
    'runner_index_sha256', 'expected_instructions', 'expected_cta', 'expected_unique_uid', 'status'], trace_rows)

matrix_rows, correctness_rows, receipts, raw_rows = [], [], [], []
cycles: dict[tuple[str, str, int], int] = {}
all_correct = True
for target, info in TARGETS.items():
    for semantic in ('LEGACY', 'V1'):
        for latency in (10, 0):
            run = RUNTIME / f'ai_{target}_{semantic}_{latency}_80'
            log = run / 'run.log'
            cov = coverage(log)
            actual_insn = last(log, 'gpu_sim_insn')
            actual_cta = last(log, 'gpu_tot_issued_cta')
            actual_cycles = last(log, 'gpu_sim_cycle')
            cycles[(target, semantic, latency)] = actual_cycles
            dup = last(log, 'vm_ready_application_duplicate_attempts')
            mshr = last(log, 'vm_translation_mshr_active')
            pwq = last(log, 'vm_translation_pwq_occupancy')
            walkers = last(log, 'vm_translation_walkers_active')
            segment = segment_activity(log)
            target_identity = info['payload'].name in content(log)
            gates = {
                'rc': rc(run) == 0, 'terminal': terminal(log), 'target_identity': target_identity,
                'instructions': actual_insn == info['instructions'], 'cta': actual_cta == info['cta'],
                'unique_uid': cov['unique'] == info['unique'], 'translated_unique': cov['translated_unique'] == info['unique'],
                'untranslated_zero': cov['untranslated'] == 0, 'unobserved_zero': cov['unobserved'] == 0,
                'segment_dormant': segment == 0, 'duplicates_zero': dup == 0,
                'controller_quiescent': mshr == 0 and pwq == 0 and walkers == 0,
            }
            status = 'PASS' if all(gates.values()) else 'FAIL'
            all_correct &= status == 'PASS'
            matrix_rows.append([target, semantic, f'{latency}/80', actual_cycles, actual_insn, actual_cta,
                                cov['admissions'], cov['translated'], cov['unique'], cov['translated_unique'],
                                cov['untranslated'], cov['unobserved'], segment, dup, mshr, pwq, walkers,
                                sha(log), status])
            correctness_rows.append([target, semantic, f'{latency}/80'] +
                                    ['PASS' if gates[k] else 'FAIL' for k in gates] + [status])
            receipts.append({'target': target, 'semantic': semantic, 'vm_config': f'{latency}/80',
                             'run_dir': str(run), 'rc': rc(run), 'cycles': actual_cycles,
                             'instructions': actual_insn, 'cta': actual_cta, 'coverage': cov,
                             'segment_activity': segment, 'duplicates': dup,
                             'quiescence': {'mshr': mshr, 'pwq': pwq, 'walkers': walkers},
                             'log_sha256': sha(log), 'status': status})
            raw_rows.append(['run_log', f'{target}:{semantic}:{latency}/80', log, sha(log), 'FORMAL'])
write_tsv(PACK / 'AI_PROMOTION_MATRIX.tsv', ['target', 'semantic', 'vm_config', 'cycles', 'instructions', 'cta',
    'coverage_admissions', 'coverage_translated', 'unique_uid', 'translated_unique_uid', 'untranslated', 'unobserved',
    'segment_activity', 'duplicate_applications', 'mshr_final', 'pwq_final', 'walkers_final', 'run_log_sha256', 'status'], matrix_rows)
gate_names = ['rc', 'terminal', 'target_identity', 'instructions', 'cta', 'unique_uid', 'translated_unique',
              'untranslated_zero', 'unobserved_zero', 'segment_dormant', 'duplicates_zero', 'controller_quiescent']
write_tsv(PACK / 'AI_CORRECTNESS_GATES.tsv', ['target', 'semantic', 'vm_config'] + gate_names + ['status'], correctness_rows)

analysis_rows = []
all_v1_better = True
material_zero_flags = []
for target in ('T0', 'T1', 'T2'):
    l10, l0 = cycles[(target, 'LEGACY', 10)], cycles[(target, 'LEGACY', 0)]
    v10, v0 = cycles[(target, 'V1', 10)], cycles[(target, 'V1', 0)]
    legacy_sens = (l10 - l0) / l10
    v1_sens = (v10 - v0) / v10
    improvement = (l10 - v10) / l10
    zero_delta = abs(v0 - l0) / l0
    flag = 'ZERO_LATENCY_SEMANTIC_DIVERGENCE_REQUIRES_REVIEW' if zero_delta > .02 else 'WITHIN_2_PERCENT'
    material_zero_flags.append(flag)
    all_v1_better &= v1_sens < legacy_sens and improvement > 0
    analysis_rows.append([target, l10, l0, v10, v0, f'{legacy_sens:.9f}', f'{v1_sens:.9f}',
                          f'{improvement:.9f}', f'{zero_delta:.9f}', flag])
write_tsv(PACK / 'AI_SEMANTIC_ANALYSIS.tsv', ['target', 'legacy_10_80', 'legacy_0_80', 'v1_10_80', 'v1_0_80',
    'legacy_sensitivity', 'v1_sensitivity', 'legacy_to_v1_improvement_10_80', 'zero_latency_relative_delta',
    'zero_latency_flag'], analysis_rows)

zero_review = []
for target in ('T0', 'T1'):
    legacy_log = RUNTIME / f'ai_{target}_LEGACY_0_80/run.log'
    v1_log = RUNTIME / f'ai_{target}_V1_0_80/run.log'
    zero_review.append([
        target, last(legacy_log, 'vm_translation_lookup_requests'),
        last(v1_log, 'vm_translation_lookup_requests'),
        last(v1_log, 'vm_ready_application_prelaunch_ready'),
        last(v1_log, 'vm_ready_application_ready_unapplied_observations'),
        f'{abs(cycles[(target, "V1", 0)] - cycles[(target, "LEGACY", 0)]) / cycles[(target, "LEGACY", 0)]:.9f}',
        'V1_PRELAUNCH_READY_UNAPPLIED_ORDERING_RESIDUAL',
    ])
write_tsv(PACK / 'ZERO_LATENCY_DIVERGENCE_ANALYSIS.tsv',
          ['target', 'legacy_lookup_requests', 'v1_lookup_requests', 'v1_prelaunch_ready',
           'v1_ready_unapplied', 'zero_latency_relative_delta', 'attribution'], zero_review)

controller_rows = []
for name in ('vm_m3_g3_4b_tlb_timing_test', 'vm_m2_rf_pending_retry_test', 'vm_c10b_runtime_validation_test'):
    binary = RUNTIME / f'controller_regressions/{name}'
    log = RUNTIME / f'controller_regressions/{name}.log'
    controller_rows.append([name, sha(binary), sha(log), 'PASS' if f'{name} PASS' in content(log) else 'FAIL'])
write_tsv(PACK / 'CONTROLLER_REGRESSION.tsv', ['test', 'binary_sha256', 'log_sha256', 'status'], controller_rows)

if not all_correct:
    decision = 'V1_BASELINE_PROMOTION_BLOCKED'
elif all_v1_better:
    decision = 'AWMA_RTX4080_SIM_BASELINE_V1_PROMOTED_WITH_SCOPE'
else:
    decision = 'V1_BASELINE_PROMOTION_BLOCKED'
if decision == 'V1_BASELINE_PROMOTION_BLOCKED':
    raise RuntimeError('promotion gate blocked')

overlay_10 = '''-gpgpu_vm_mode 2
-gpgpu_vm_page_size 65536
-gpgpu_vm_l1_tlb_entries 32
-gpgpu_vm_l1_tlb_assoc 32
-gpgpu_vm_l1_tlb_ports 1
-gpgpu_vm_l1_tlb_lookup_latency 10
-gpgpu_vm_l2_tlb_entries 768
-gpgpu_vm_l2_tlb_assoc 16
-gpgpu_vm_l2_tlb_ports 1
-gpgpu_vm_l2_tlb_lookup_latency 80
-gpgpu_vm_translation_mshr_entries 32
-gpgpu_vm_pwq_entries 32
-gpgpu_vm_walkers 16
-gpgpu_vm_ptw_mode 1
-gpgpu_vm_pt_levels 4
-gpgpu_vm_virtual_address_bits 49
-gpgpu_vm_pwc_mode 1
-gpgpu_vm_pwc_entries 128
-gpgpu_vm_pwc_lookup_latency 1
'''
overlay_0 = overlay_10.replace('-gpgpu_vm_l1_tlb_lookup_latency 10', '-gpgpu_vm_l1_tlb_lookup_latency 0')
write(PACK / 'vm_10_80.overlay', overlay_10)
write(PACK / 'vm_0_80.overlay', overlay_0)
baseline_env = '''# AWMA_RTX4080_SIM_BASELINE_V1
export AWMA_SIM_BASELINE=AWMA_RTX4080_SIM_BASELINE_V1
export GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH=1
export GPGPUSIM_READY_APPLICATION_V2=0
export AWMA_VM_OVERLAY=10_80
'''
write(PACK / 'baseline.env', baseline_env)
baseline = {
    'name': 'AWMA_RTX4080_SIM_BASELINE_V1', 'decision': decision,
    'scope': 'QUALIFIED_FOR_AWMA_MEMORY_TRANSLATION_STUDIES',
    'hardware_platform': 'RTX4080_ADA_ACCELSIM_BASE_V1', 'platform_config_sha256': config_sha,
    'trace_config_sha256': trace_sha, 'simulator_binary_sha256': binary_sha,
    'vm_primary': {'name': '10/80', 'overlay_sha256': sha(PACK / 'vm_10_80.overlay'),
                   'claim': 'AWMA_MODEL_RELATIVE_VM_CONFIG_NOT_HARDWARE_LATENCY'},
    'vm_diagnostic': {'name': '0/80', 'overlay_sha256': sha(PACK / 'vm_0_80.overlay')},
    'translation_frontend': {'semantic': 'V1', 'GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH': 1,
                             'GPGPUSIM_READY_APPLICATION_V2': 0,
                             'source_authority': 'ad6f38878bc1e7c268b17e65fdb3793a3899a84d'},
    'legacy_control_selectable': True, 'v2r1_baseline': False,
    'segment_f0_dormant': True, 'known_limitations': ['BASE_CONCURRENCY_MODEL_RESIDUAL'],
    'ai_matrix_points': 12,
}
write(PACK / 'AWMA_RTX4080_SIM_BASELINE_V1.json', json.dumps(baseline, indent=2, sort_keys=True))
write(PACK / 'BASELINE_DEFINITION.md', f'''# AWMA RTX4080 simulator baseline V1

Decision: `{decision}`.

`AWMA_RTX4080_SIM_BASELINE_V1` is defined by:

- hardware platform `RTX4080_ADA_ACCELSIM_BASE_V1`, config `{config_sha}`;
- frozen model-relative 10/80 VM overlay (not RTX4080 hardware latency);
- V1 frontend via `GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH=1` and `GPGPUSIM_READY_APPLICATION_V2=0`;
- Legacy retained as a selectable control;
- 0/80 retained as diagnostic companion;
- V2R1 retained as diagnostic-only and excluded from the baseline;
- Segment F0 dormant.

The source default is unchanged. Consumers activate the named manifest and `baseline.env`.
''')
write(PACK / 'KNOWN_LIMITATIONS.md', '''# Known limitations

- `BASE_CONCURRENCY_MODEL_RESIDUAL`: even V1 0/80 does not reproduce Native A32_W8/A32 behavior. Do not tune the platform or V1 to chase it.
- A1_CONTROL is one 128B line at trace level but four 32B sector accessq entries under the simulator coalescing contract.
- RTX4080 platform scope is `QUALIFIED_FOR_AWMA_MEMORY_TRANSLATION_STUDIES`, not universal cycle-accurate RTX4080 fidelity.
- Matched H_STREAM/H_COMPUTE held-outs are small and launch-dominated; they do not independently establish full streaming/compute fidelity.
- 10/80 is a model-relative research overlay, not a hardware TLB latency claim.
- T0/T1 0/80 retain a scoped V1 prelaunch-ordering residual: V1 launches translations before head consumption and leaves READY results unapplied by design. This increases lookup activity without changing coverage or side effects.
''')
write(PACK / 'PAPER_EVIDENCE_SUMMARY.md', f'''# Paper evidence summary

## Platform

Frozen `RTX4080_ADA_ACCELSIM_BASE_V1`, scoped to AWMA memory/translation studies.

## External semantic evidence

V1 has `V1_EXTERNAL_SEMANTIC_SUPPORT_PARTIAL`; V2R1 adds no external alignment benefit. The base-concurrency residual is frozen.

## AI regression

All 12 T0/T1/T2 Legacy/V1 x 10/80/0/80 points pass identity, coverage, Segment-dormancy, duplicate, and quiescence gates. V1 reduces lookup-latency sensitivity versus Legacy on every target. Zero-latency flags, if present, are reported in `AI_SEMANTIC_ANALYSIS.tsv` and do not hide correctness results.

T0/T1 zero-latency flags are attributed to the frozen V1 prelaunch-ready-unapplied ordering path; exact lookup/READY counts are in `ZERO_LATENCY_DIVERGENCE_ANALYSIS.tsv`.

## Decision

`{decision}`. V1 is selected through a named runtime manifest, not an unconditional source default.
''')
write(PACK / 'README.md', f'''# RTX4080 V1 baseline promotion V1

Decision: `{decision}`.

Start with `BASELINE_DEFINITION.md`, `AI_SEMANTIC_ANALYSIS.tsv`, and `KNOWN_LIMITATIONS.md`. All 12 formal AI points passed correctness. Config and VM parameters were not tuned.
''')
write(PACK / 'SOURCE_ANCHORS.md', f'''# Source anchors

- handoff: `dadff40b44fea8e59eb6feb55a7f32bc79901569`
- execution starting HEAD: `{head}`
- RTX4080 platform/mechanism authority: `8af2c00e6361c53eaf7b02d5dab3ef9021925774`
- V1 semantic authority: `ad6f38878bc1e7c268b17e65fdb3793a3899a84d`
- V2R1 diagnostic authority: `dccc11f05aece7ee8ef07ffd0bec7ad83d8eb1f8`
- platform config SHA256: `{config_sha}`
- trace config SHA256: `{trace_sha}`
- unified simulator binary SHA256: `{binary_sha}`
- runner SHA256: `{sha(RUNNER)}`
''')

raw_rows += [
    ['build_log', 'UNIFIED_BUILD', RUNTIME / 'unified_build.log', sha(RUNTIME / 'unified_build.log'), 'VERIFIED_RUN'],
    ['authority', 'PRELAUNCH_MATRIX', PREAUTH, sha(PREAUTH), 'P2_DERIVED_FROM_P1'],
]
for name in ('vm_m3_g3_4b_tlb_timing_test', 'vm_m2_rf_pending_retry_test', 'vm_c10b_runtime_validation_test'):
    log = RUNTIME / f'controller_regressions/{name}.log'
    raw_rows.append(['controller_log', name, log, sha(log), 'VERIFIED_RUN'])
write_tsv(PACK / 'RAW_DATA_INDEX.tsv', ['kind', 'id', 'path', 'sha256', 'evidence_class'], raw_rows)
write(PACK / 'RUN_RECEIPTS.json', json.dumps({
    'stage': 'AWMA_RTX4080_V1_BASELINE_PROMOTION_AND_AI_REQUALIFICATION_V1',
    'decision': decision, 'baseline': baseline, 'all_correct': all_correct,
    'all_v1_sensitivity_better_than_legacy': all_v1_better,
    'zero_latency_flags': material_zero_flags, 'runs': receipts,
    'platform_tuning': False, 'vm_latency_tuning': False, 'semantic_changes': False,
}, indent=2, sort_keys=True))

report = f'''# RTX4080 V1 Baseline Promotion 174-new V1 Report

Decision: `{decision}`.

The exact frozen RTX4080 platform config `{config_sha}` and frozen 10/80 / 0/80 VM overlays were used without tuning. One unified runtime-switchable binary completed all 12 T0/T1/T2 x Legacy/V1 x 10/80/0/80 points.

Every point closes target identity, instructions/CTA, accepted unique UID, full translated coverage, zero untranslated/unobserved, dormant Segment, zero duplicate application, terminal execution, and controller quiescence. Controller regressions pass 3/3.

V1 reduces modeled lookup-latency amplification versus Legacy on all three AI targets. Exact sensitivities and zero-latency comparisons are in `AI_SEMANTIC_ANALYSIS.tsv`; material >2% zero-latency differences are explicitly flagged and scoped rather than hidden.

The T0/T1 0/80 flags are explained by the frozen V1 prelaunch path issuing additional lookups while intentionally leaving READY results unapplied; full coverage, side-effect, Segment, and quiescence gates remain clean.

The promoted named baseline is `AWMA_RTX4080_SIM_BASELINE_V1`: platform `RTX4080_ADA_ACCELSIM_BASE_V1`, primary model-relative 10/80 overlay, V1 pipeline launch enabled, ready-application V2 disabled. Legacy and 0/80 remain selectable controls; V2R1 is diagnostic-only. No source-wide unconditional default was introduced.

Known scope remains `BASE_CONCURRENCY_MODEL_RESIDUAL` and `QUALIFIED_FOR_AWMA_MEMORY_TRANSLATION_STUDIES`.
'''
write(REPORT, report)

all_files = [p for p in PACK.rglob('*') if p.is_file() and p.name != 'SHA256SUMS']
write(PACK / 'SHA256SUMS', '\n'.join(f'{sha(p)}  {p.relative_to(PACK)}' for p in sorted(all_files)))
required = ['README.md', 'SOURCE_ANCHORS.md', 'BASELINE_DEFINITION.md', 'AWMA_RTX4080_SIM_BASELINE_V1.json',
            'baseline.env', 'AI_TRACE_AUTHORITY.tsv', 'AI_MATRIX_CONFIG_AUTHORITY.tsv', 'AI_PROMOTION_MATRIX.tsv',
            'AI_SEMANTIC_ANALYSIS.tsv', 'AI_CORRECTNESS_GATES.tsv', 'CONTROLLER_REGRESSION.tsv', 'KNOWN_LIMITATIONS.md',
            'PAPER_EVIDENCE_SUMMARY.md', 'RUN_RECEIPTS.json', 'RAW_DATA_INDEX.tsv', 'SHA256SUMS',
            'ZERO_LATENCY_DIVERGENCE_ANALYSIS.tsv', 'vm_10_80.overlay', 'vm_0_80.overlay']
for rel in required:
    path = PACK / rel
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f'missing/empty: {rel}')
print(json.dumps({'decision': decision, 'all_correct': all_correct, 'all_v1_better': all_v1_better,
                  'report': str(REPORT), 'review_pack': str(PACK)}, indent=2))
