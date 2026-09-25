#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import lzma
import os
import re
import shlex
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

STAGE = 'AWMA_PREL1_COALESCER_MINIMAL_INDEPENDENT_HOLDOUT_VALIDATION_V1'
MECHANISM_AUTHORITY = '163a8572f9272891b8109f9158aa79ca88d9e153'
SOURCE_FREEZE = '2bbbceabb5261777fe385289ecb6579791e0f232'
CAPTURE_AUTHORITY = 'a984735c1d39b8d155aec2ef25dde0502f7c940b'
REPO = Path('/root/workspace/accel-sim-framework-awma-prel1-coalescer-minimal-independent-holdout-validation-v1')
RUNTIME = Path('/root/awma_prel1_coalescing_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescer_minimal_independent_holdout_validation_v1/raw')
TRACE = Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/prel1_coalescer_independent_holdout_capture_20260925/primary_formal/raw/kernel-994-ctx_0x60474d7c4d80.traceg.xz')
TRACE_SHA = 'ed712fb618309fd4f08c5ccc284a807df8a78581df2880f76fc415fa8a3b9105'
CONFIG = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
CORE_LIB = RUNTIME / 'src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release'
BINARY_SHA = 'be4136f011255acbfc33b9c9cc5166f43450f7e7fa9dd589f4b3c9481a71b630'
LABELS = {'off': 'OFF', 'main': 'COALESCER', 'plus1': 'COALESCER_PLUS1'}


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


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


def trace_identity() -> dict[str, object]:
    with lzma.open(TRACE, 'rt', errors='replace') as stream:
        header = ''.join(stream.readline() for _ in range(20))
    def field(pattern: str) -> str:
        match = re.search(pattern, header)
        if not match:
            raise RuntimeError(f'missing trace header field {pattern}')
        return match.group(1)
    return {
        'kernel_name': field(r'-kernel name = (.+)'),
        'kernel_id': int(field(r'-kernel id = (\d+)')),
        'grid': field(r'-grid dim = \(([^)]+)\)'),
        'block': field(r'-block dim = \(([^)]+)\)'),
        'binary_version': int(field(r'-binary version = (\d+)')),
    }


def off_qualified() -> bool:
    receipt = DURABLE / 'OFF' / 'qualification.json'
    return receipt.is_file() and json.loads(receipt.read_text()).get('status') == 'PASS'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=tuple(LABELS))
    parser.add_argument('--timeout-seconds', type=int, default=3600)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    if sha(TRACE) != TRACE_SHA:
        raise RuntimeError('holdout trace SHA mismatch')
    if sha(BINARY) != BINARY_SHA:
        raise RuntimeError('frozen binary SHA mismatch')
    identity = trace_identity()
    if (identity['kernel_id'] != 994 or identity['grid'] != '1,1,1' or
            identity['block'] != '128,1,1' or
            'at::native::reduce_kernel' not in identity['kernel_name']):
        raise RuntimeError('holdout target identity mismatch')
    if args.mode != 'off' and not off_qualified():
        raise RuntimeError('candidate forbidden before OFF qualification PASS')
    label = LABELS[args.mode]
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
    (traces / TRACE.name).symlink_to(TRACE)
    (traces / 'kernelslist.g').write_text(f'{TRACE.name}\n')
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH', '')}"
    for key in tuple(env):
        if key.startswith('GPGPUSIM_AWMA_') or key in (
                'GPGPUSIM_READY_APPLICATION_V2',
                'GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH'):
            env.pop(key, None)
    env['GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH'] = '1'
    env['GPGPUSIM_AWMA_PASSIVE_MEMO_OBSERVER'] = '0'
    env['GPGPUSIM_AWMA_OWNER_WAIT_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_VM_COVERAGE_KERNEL_UID'] = '1'
    env['GPGPUSIM_READY_APPLICATION_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS'] = '1'
    if args.mode != 'off':
        env['GPGPUSIM_AWMA_TRANSLATION_CANDIDATE'] = 'prel1_exact_coalescer'
        env['GPGPUSIM_AWMA_PREL1_COMPARE_LATENCY'] = (
            '1' if args.mode == 'plus1' else '0')
        env['GPGPUSIM_AWMA_MECHANISM_DIAGNOSTICS'] = '1'
    cmd = ['nice', '-n', '10', str(BINARY), '-config', str(CONFIG),
           '-trace', 'traces/kernelslist.g'] + trace_args() + overlay()
    receipt = {
        'stage': STAGE, 'mode': label,
        'mechanism_authority': MECHANISM_AUTHORITY,
        'source_freeze': SOURCE_FREEZE,
        'capture_authority': CAPTURE_AUTHORITY,
        'capacity_per_sid': 0 if args.mode == 'off' else 2,
        'waiters_per_entry': 0 if args.mode == 'off' else 32,
        'compare_latency': 1 if args.mode == 'plus1' else 0,
        'trace_identity': identity, 'argv': cmd,
        'environment': {key: env.get(key) for key in sorted(env)
                        if key.startswith('GPGPUSIM_')},
        'binary_sha256': sha(BINARY),
        'core_library_sha256': sha(CORE_LIB / 'libcudart.so'),
        'config_sha256': sha(CONFIG),
        'trace_config_sha256': sha(TRACE_CONFIG),
        'trace': str(TRACE), 'trace_sha256': sha(TRACE),
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
