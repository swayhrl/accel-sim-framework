#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/root/workspace/accel-sim-framework-awma-t1-negative-ideal-response-attribution-v1')
RUNTIME = Path('/root/awma_t1_negative_ideal_response_attribution_v1_runtime')
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
CONFIG = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
CORE_LIB = RUNTIME / 'src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release'
PAYLOAD = Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native_prefill-gemm-primary-occ0_20260918T052739Z_01540d931e17/traces/kernel-45-ctx_0x60d38cb72530.traceg.xz')
INDEX_CONTENT = 'kernel-45-ctx_0x60d38cb72530.traceg.xz\n'
EXPECTED = {
    '10_80': {'cycles': 665802, 'instructions': 369131520, 'cta': 384,
              'unique_uid': 7159808},
    '0_80': {'cycles': 664805, 'instructions': 369131520, 'cta': 384,
             'unique_uid': 7159808},
    'ideal': {'cycles': 715636, 'instructions': 369131520, 'cta': 384,
              'unique_uid': 7159808},
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def utc() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def trace_args() -> list[str]:
    result: list[str] = []
    for raw in TRACE_CONFIG.read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith('#'):
            result.extend(shlex.split(line))
    return result


def overlay(mode: str) -> list[str]:
    l1_latency = '0' if mode == '0_80' else '10'
    return [
        '-gpgpu_vm_mode', '2', '-gpgpu_vm_page_size', '65536',
        '-gpgpu_vm_l1_tlb_entries', '32', '-gpgpu_vm_l1_tlb_assoc', '32',
        '-gpgpu_vm_l1_tlb_ports', '1',
        '-gpgpu_vm_l1_tlb_lookup_latency', l1_latency,
        '-gpgpu_vm_l2_tlb_entries', '768', '-gpgpu_vm_l2_tlb_assoc', '16',
        '-gpgpu_vm_l2_tlb_ports', '1',
        '-gpgpu_vm_l2_tlb_lookup_latency', '80',
        '-gpgpu_vm_translation_mshr_entries', '32',
        '-gpgpu_vm_pwq_entries', '32', '-gpgpu_vm_walkers', '16',
        '-gpgpu_vm_ptw_mode', '1', '-gpgpu_vm_pt_levels', '4',
        '-gpgpu_vm_virtual_address_bits', '49', '-gpgpu_vm_pwc_mode', '1',
        '-gpgpu_vm_pwc_entries', '128', '-gpgpu_vm_pwc_lookup_latency', '1',
        '-gpgpu_memory_telemetry_level', '2',
        '-gpgpu_memory_telemetry_window_transactions', '100000000',
    ]


def run(mode: str, timeout_s: int) -> int:
    run_dir = RUNTIME / f'attribution_T1_V1_{mode}'
    if run_dir.exists():
        raise SystemExit(f'refusing to overwrite existing run directory: {run_dir}')
    (run_dir / 'traces').mkdir(parents=True)
    (run_dir / 'traces' / PAYLOAD.name).symlink_to(PAYLOAD)
    (run_dir / 'traces/kernelslist.g').write_text(INDEX_CONTENT)

    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH', '')}"
    for key in tuple(env):
        if key.startswith('GPGPUSIM_') and key not in {
                'GPGPUSIM_ROOT', 'GPGPUSIM_CONFIG', 'GPGPUSIM_BRANCH',
                'GPGPUSIM_REPO', 'GPGPUSIM_SETUP_ENVIRONMENT_WAS_RUN',
                'GPGPUSIM_POWER_MODEL'}:
            env.pop(key, None)
    env.update({
        'GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH': '1',
        'GPGPUSIM_VM_PRELAUNCH_ELIGIBILITY_KERNEL_UID': '1',
        'GPGPUSIM_VM_MAPPING_DIGEST_DIAGNOSTICS': '1',
        'GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS': '1',
        'GPGPUSIM_VM_COVERAGE_KERNEL_UID': '1',
        'GPGPUSIM_READY_APPLICATION_DIAGNOSTICS': '1',
        'GPGPUSIM_T1_ATTRIBUTION_DIAGNOSTICS': '1',
    })
    if mode == 'ideal':
        env['GPGPUSIM_VM_IDEAL_TRANSLATION_CONTROL'] = '1'

    cmd = [str(BINARY), '-config', str(CONFIG), '-trace',
           'traces/kernelslist.g'] + trace_args() + overlay(mode)
    command = {
        'stage': 'AWMA_T1_NEGATIVE_IDEAL_RESPONSE_ATTRIBUTION_V1',
        'target': 'PREFILL_GEMM_PRIMARY_OCC0',
        'mode': mode,
        'argv': cmd,
        'environment': {k: env[k] for k in sorted(env)
                        if k.startswith('GPGPUSIM_')},
        'payload': str(PAYLOAD),
        'payload_sha256': sha256(PAYLOAD),
        'runner_index_sha256': hashlib.sha256(INDEX_CONTENT.encode()).hexdigest(),
        'binary_sha256': sha256(BINARY),
        'platform_config_sha256': sha256(CONFIG),
        'trace_config_sha256': sha256(TRACE_CONFIG),
        'expected': EXPECTED[mode],
    }
    (run_dir / 'command.json').write_text(
        json.dumps(command, indent=2, sort_keys=True) + '\n')
    (run_dir / 'start_utc.txt').write_text(utc() + '\n')
    start = time.monotonic()
    with (run_dir / 'run.log').open('w') as stdout, \
            (run_dir / 'run.stderr').open('w') as stderr:
        try:
            proc = subprocess.run(cmd, cwd=run_dir, env=env, stdout=stdout,
                                  stderr=stderr, timeout=timeout_s, check=False)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            rc = 124
    (run_dir / 'rc.txt').write_text(f'{rc}\n')
    (run_dir / 'end_utc.txt').write_text(utc() + '\n')
    (run_dir / 'wall_seconds.txt').write_text(
        f'{time.monotonic() - start:.6f}\n')
    print(json.dumps({'mode': mode, 'rc': rc, 'run_dir': str(run_dir)},
                     sort_keys=True), flush=True)
    return rc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=tuple(EXPECTED), required=True)
    parser.add_argument('--timeout-seconds', type=int, default=21600)
    args = parser.parse_args()
    return run(args.mode, args.timeout_seconds)


if __name__ == '__main__':
    raise SystemExit(main())
