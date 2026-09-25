#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
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
SOURCE_FREEZE = '2bbbceabb5261777fe385289ecb6579791e0f232'
REPO = Path('/root/workspace/accel-sim-framework-awma-prel1-translation-request-coalescing-discovery-prototype-v1')
RUNTIME = Path('/root/awma_prel1_coalescing_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescing_v1/development_raw')
CONFIG = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
CORE_LIB = RUNTIME / 'src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release'
INPUTS = RUNTIME / 'inputs'
BINARY_SHA = 'be4136f011255acbfc33b9c9cc5166f43450f7e7fa9dd589f4b3c9481a71b630'
TARGETS = {
    'T0': ('PREFILL_FLASH', 'kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz', 'd8fa338f82800f646c8501a6a1d1049afaae213fe0d7f70d4913fcfaa76ba67a'),
    'T1': ('PREFILL_GEMM', 'kernel-45-ctx_0x60d38cb72530.traceg.xz', 'e36178f9a92033cd91f3c1ff4b165321b7958157c7deed2a9aaa4696e7c73e8c'),
    'T2': ('DECODE_GEMV', 'kernel-17039-ctx_0x5ddb6907c160.traceg.xz', 'b87cd6cb6a2bc0f67e17616e26d1bf9091facad242d46a43f5f9c1ac274b6138'),
    'SPLITKV': ('FLASH_FWD_SPLITKV', 'kernel-17543-ctx_0x5be0856adcb0.traceg.xz', '282a9b18510bd0aaf54ec528c65bfb39d49b052902c6b87f3b85bb2973096371'),
    'COMBINE': ('FLASH_FWD_SPLITKV_COMBINE', 'kernel-16813-ctx_0x5c9946e7f280.traceg.xz', 'd153db1548517f24eebd80c1a5dc48785ab28ace173b2937dd4f7b4a7005dcb9'),
    'A1': ('DECODE_GEMV_PAIR_A_S2_T2048', 'kernel-16828-ctx_0x608ad97ab300.traceg.xz', '49f83c02fbb01dcc9167c6790271103e98d42f318c0344b5f26b8433b704d099'),
    'A2': ('DECODE_GEMV_PAIR_A_T8192', 'kernel-16828-ctx_0x573505e282b0.traceg.xz', 'c8135003bae105108707ab6b024ca56e50146df88d1692068d92e99511ada2ca'),
}
PHASE_TARGETS = {
    'candidate': tuple(TARGETS),
    'control': ('T0', 'T1', 'A2'),
    'plus-one': ('T0', 'T1', 'T2', 'A2'),
    'level2-off': ('T2', 'A1'),
    'level2-candidate': ('T2', 'A1'),
}


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


def gate_passed() -> bool:
    receipt = RUNTIME / 'zero_duplication_gate.json'
    return receipt.is_file() and json.loads(receipt.read_text()).get('status') == 'PASS'


def run_point(target: str, phase: str, timeout: int,
              overwrite: bool) -> dict[str, object]:
    family, name, expected_sha = TARGETS[target]
    payload = INPUTS / name
    if sha(payload) != expected_sha:
        raise RuntimeError(f'{target}: staged input SHA mismatch')
    if sha(BINARY) != BINARY_SHA:
        raise RuntimeError('frozen candidate binary SHA mismatch')
    label = {'candidate': 'COALESCER', 'control': 'GROUPING_ONLY',
             'plus-one': 'COALESCER_PLUS1', 'level2-off': 'OFF_LEVEL2',
             'level2-candidate': 'COALESCER_LEVEL2'}[phase]
    run_dir = DURABLE / f'{target}_{label}_10_80'
    rc_path = run_dir / 'rc.txt'
    if not overwrite and rc_path.is_file() and rc_path.read_text().strip() == '0':
        return {'point': run_dir.name, 'rc': 0,
                'status': 'SKIPPED_EXISTING_PASS'}
    run_dir.mkdir(parents=True, exist_ok=True)
    traces = run_dir / 'traces'
    if traces.exists():
        shutil.rmtree(traces)
    traces.mkdir()
    (traces / name).symlink_to(payload)
    (traces / 'kernelslist.g').write_text(f'{name}\n')
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH', '')}"
    for key in tuple(env):
        if key.startswith('GPGPUSIM_AWMA_') or key in (
                'GPGPUSIM_READY_APPLICATION_V2',
                'GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH'):
            env.pop(key, None)
    env['GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH'] = '1'
    if phase != 'level2-off':
        env['GPGPUSIM_AWMA_TRANSLATION_CANDIDATE'] = 'prel1_exact_coalescer'
        env['GPGPUSIM_AWMA_PREL1_COMPARE_LATENCY'] = (
            '1' if phase == 'plus-one' else '0')
        if phase == 'control':
            env['GPGPUSIM_AWMA_PREL1_CONTROL'] = 'grouping_only'
    env['GPGPUSIM_AWMA_PASSIVE_MEMO_OBSERVER'] = '0'
    env['GPGPUSIM_AWMA_BOTTLENECK_OBSERVATORY'] = (
        '2' if phase.startswith('level2-') else '1')
    env['GPGPUSIM_AWMA_MECHANISM_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_AWMA_OWNER_WAIT_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_VM_COVERAGE_KERNEL_UID'] = '1'
    env['GPGPUSIM_READY_APPLICATION_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS'] = '1'
    cmd = ['nice', '-n', '10', str(BINARY), '-config', str(CONFIG),
           '-trace', 'traces/kernelslist.g'] + trace_args() + overlay()
    receipt = {
        'stage': STAGE, 'phase': phase, 'source_freeze': SOURCE_FREEZE,
        'target': target, 'family': family, 'arm': label,
        'candidate_enabled': phase != 'level2-off',
        'capacity_per_sid': 0 if phase == 'level2-off' else 2,
        'waiters_per_entry': 0 if phase == 'level2-off' else 32,
        'compare_latency': 1 if phase == 'plus-one' else 0,
        'argv': cmd,
        'environment': {key: env.get(key) for key in sorted(env)
                        if key.startswith('GPGPUSIM_')},
        'binary_sha256': sha(BINARY),
        'core_library_sha256': sha(CORE_LIB / 'libcudart.so'),
        'config_sha256': sha(CONFIG),
        'trace_config_sha256': sha(TRACE_CONFIG),
        'payload': str(payload), 'payload_sha256': sha(payload),
    }
    (run_dir / 'command.json').write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    (run_dir / 'start_utc.txt').write_text(utc() + '\n')
    start = time.monotonic()
    with (run_dir / 'run.log').open('w') as out, \
            (run_dir / 'run.stderr').open('w') as err:
        try:
            proc = subprocess.run(cmd, cwd=run_dir, env=env, stdout=out,
                                  stderr=err, timeout=timeout, check=False)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            rc = 124
    rc_path.write_text(f'{rc}\n')
    (run_dir / 'end_utc.txt').write_text(utc() + '\n')
    (run_dir / 'wall_seconds.txt').write_text(
        f'{time.monotonic() - start:.6f}\n')
    return {'point': run_dir.name, 'rc': rc,
            'status': 'PASS' if rc == 0 else 'FAIL'}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=tuple(PHASE_TARGETS))
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--timeout-seconds', type=int, default=21600)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    if args.workers not in (1, 2):
        parser.error('one or two low-priority workers only')
    if not gate_passed():
        raise RuntimeError('development forbidden before zero gate PASS')
    DURABLE.mkdir(parents=True, exist_ok=True)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_point, target, args.phase,
                               args.timeout_seconds, args.overwrite)
                   for target in PHASE_TARGETS[args.phase]]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, sort_keys=True), flush=True)
    results.sort(key=lambda row: str(row['point']))
    (RUNTIME / f'{args.phase}_launcher_results.json').write_text(
        json.dumps(results, indent=2, sort_keys=True) + '\n')
    return 0 if all(row['rc'] == 0 for row in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
