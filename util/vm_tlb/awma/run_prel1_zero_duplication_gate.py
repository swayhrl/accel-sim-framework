#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

STAGE = 'AWMA_PREL1_TRANSLATION_REQUEST_COALESCING_DISCOVERY_AND_PROTOTYPE_V1'
REPO = Path('/root/workspace/accel-sim-framework-awma-prel1-translation-request-coalescing-discovery-prototype-v1')
RUNTIME = Path('/root/awma_prel1_coalescing_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescing_v1/zero_duplication_gate')
CONFIG = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
CORE_LIB = RUNTIME / 'src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release'
BINARY_SHA = 'be4136f011255acbfc33b9c9cc5166f43450f7e7fa9dd589f4b3c9481a71b630'
INPUTS = RUNTIME / 'inputs'
TRACES = (
    ('kernel-1-ctx_0x58c3f6d68f70.traceg.xz',
     '960f63d7b59aa53394e799577c31875ce7f19f294daabaf09999f401892dea38'),
    ('kernel-2-ctx_0x58c3f6d68f70.traceg.xz',
     'cb9e23a3ec9f6113051891053d22256a340f68524741faa986c9c00be7087bc8'),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def trace_args() -> list[str]:
    result: list[str] = []
    for raw in TRACE_CONFIG.read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith('#'):
            result.extend(shlex.split(line))
    return result


def overlay() -> list[str]:
    return [
        '-gpgpu_vm_mode', '2', '-gpgpu_vm_page_size', '65536',
        '-gpgpu_vm_l1_tlb_entries', '32', '-gpgpu_vm_l1_tlb_assoc', '32',
        '-gpgpu_vm_l1_tlb_ports', '1', '-gpgpu_vm_l1_tlb_lookup_latency', '10',
        '-gpgpu_vm_l2_tlb_entries', '768', '-gpgpu_vm_l2_tlb_assoc', '16',
        '-gpgpu_vm_l2_tlb_ports', '1', '-gpgpu_vm_l2_tlb_lookup_latency', '80',
        '-gpgpu_vm_translation_mshr_entries', '32', '-gpgpu_vm_pwq_entries', '32',
        '-gpgpu_vm_walkers', '16', '-gpgpu_vm_ptw_mode', '1',
        '-gpgpu_vm_pt_levels', '4', '-gpgpu_vm_virtual_address_bits', '49',
        '-gpgpu_vm_pwc_mode', '1', '-gpgpu_vm_pwc_entries', '128',
        '-gpgpu_vm_pwc_lookup_latency', '1',
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('off', 'candidate'))
    parser.add_argument('--timeout-seconds', type=int, default=3600)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    if sha(BINARY) != BINARY_SHA:
        raise RuntimeError('candidate binary SHA mismatch')
    for name, expected in TRACES:
        if sha(INPUTS / name) != expected:
            raise RuntimeError(f'{name}: staged input SHA mismatch')
    label = 'OFF' if args.mode == 'off' else 'COALESCER'
    run_dir = DURABLE / label
    rc_path = run_dir / 'rc.txt'
    if not args.overwrite and rc_path.is_file() and rc_path.read_text().strip() == '0':
        print(json.dumps({'mode': label, 'status': 'SKIPPED_EXISTING_PASS'}))
        return 0
    run_dir.mkdir(parents=True, exist_ok=True)
    traces = run_dir / 'traces'
    if traces.exists():
        shutil.rmtree(traces)
    traces.mkdir()
    for name, _ in TRACES:
        (traces / name).symlink_to(INPUTS / name)
    (traces / 'kernelslist.g').write_text(''.join(f'{name}\n' for name, _ in TRACES))
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH', '')}"
    for key in tuple(env):
        if key.startswith('GPGPUSIM_AWMA_') or key in (
                'GPGPUSIM_READY_APPLICATION_V2',
                'GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH'):
            env.pop(key, None)
    env['GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH'] = '1'
    env['GPGPUSIM_AWMA_PASSIVE_MEMO_OBSERVER'] = '0'
    env['GPGPUSIM_AWMA_BOTTLENECK_OBSERVATORY'] = '1'
    env['GPGPUSIM_VM_COVERAGE_KERNEL_UID'] = '2'
    env['GPGPUSIM_READY_APPLICATION_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS'] = '1'
    if args.mode == 'candidate':
        env['GPGPUSIM_AWMA_TRANSLATION_CANDIDATE'] = 'prel1_exact_coalescer'
        env['GPGPUSIM_AWMA_PREL1_COMPARE_LATENCY'] = '0'
        env['GPGPUSIM_AWMA_MECHANISM_DIAGNOSTICS'] = '1'
    cmd = ['nice', '-n', '10', str(BINARY), '-config', str(CONFIG),
           '-trace', 'traces/kernelslist.g'] + trace_args() + overlay()
    receipt = {
        'stage': STAGE, 'phase': 'ZERO_DUPLICATION_FULL_PIPELINE',
        'mode': label, 'source_state': 'PRE_SOURCE_FREEZE_CORRECTNESS_GATE',
        'argv': cmd,
        'environment': {key: env.get(key) for key in sorted(env)
                        if key.startswith('GPGPUSIM_')},
        'binary_sha256': sha(BINARY),
        'core_library_sha256': sha(CORE_LIB / 'libcudart.so'),
        'config_sha256': sha(CONFIG),
        'trace_config_sha256': sha(TRACE_CONFIG),
        'inputs': [{'path': str(INPUTS / name), 'sha256': expected}
                   for name, expected in TRACES],
    }
    (run_dir / 'command.json').write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    (run_dir / 'start_utc.txt').write_text(utc() + '\n')
    start = time.monotonic()
    with (run_dir / 'run.log').open('w') as out, \
            (run_dir / 'run.stderr').open('w') as err:
        try:
            proc = subprocess.run(cmd, cwd=run_dir, env=env, stdout=out,
                                  stderr=err, timeout=args.timeout_seconds,
                                  check=False)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            rc = 124
    rc_path.write_text(f'{rc}\n')
    (run_dir / 'end_utc.txt').write_text(utc() + '\n')
    (run_dir / 'wall_seconds.txt').write_text(
        f'{time.monotonic() - start:.6f}\n')
    print(json.dumps({'mode': label, 'rc': rc,
                      'status': 'PASS' if rc == 0 else 'FAIL'}))
    return 0 if rc == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
