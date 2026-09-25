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

STAGE = 'AWMA_PREL1_COALESCER_PAPER_QUALIFICATION_V1'
REPO = Path('/root/workspace/accel-sim-framework-awma-prel1-coalescer-paper-qualification-v1')
RUNTIME = Path('/root/awma_prel1_coalescing_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescer_paper_qualification_v1/pair_c_raw')
INPUTS = RUNTIME / 'inputs'
CONFIG = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
CORE_LIB = RUNTIME / 'src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release'
SOURCE_FREEZE = '2bbbceabb5261777fe385289ecb6579791e0f232'
BINARY_SHA = 'be4136f011255acbfc33b9c9cc5166f43450f7e7fa9dd589f4b3c9481a71b630'
CONFIG_SHA = 'de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8'
TRACE_CONFIG_SHA = 'a46fe47a14f3ca4116a35c5bf1dc156f4e861484b91278e8b3f6e09519bd7e5b'
TARGETS = {
    'H1': {
        'scientific_id': 'STR_8a5773a1d265', 'scenario': 'S2',
        'decode_step': 16, 'kernel_id': 16795, 'grid': '224,1,1',
        'block': '32,4,1', 'recurrence': 'STABLE_48',
        'name': 'kernel-16795-ctx_0x5bd5f19c5280.traceg.xz',
        'sha': 'ba73fd184217b066682f93e09969a1a9e05dc1b119e5644ee62a0be530585e3c',
        'off_cycles': 19578, 'sim_instructions': 10601472,
        'sim_cta': 224, 'sim_uid': 102144,
        'off_log': '/root/share/mnt164/huangrulin/awma_c1_nonblocking_cross_context_holdout_v1/raw/H1_OFF_10_80/run.log',
        'off_log_sha': '3e582b4bdf6e876d19cd8fdd8207d31dd192cdc93a3dc6a80d845d9b34e9115f',
    },
    'H2': {
        'scientific_id': 'STR_8a5773a1d265', 'scenario': 'D128',
        'decode_step': 96, 'kernel_id': 101035, 'grid': '224,1,1',
        'block': '32,4,1', 'recurrence': 'STABLE_48',
        'name': 'kernel-101035-ctx_0x56928de701b0.traceg.xz',
        'sha': '4c601dcad31f1afdb931602671bbb54556ca12734f1ee853dc41a89779f44320',
        'off_cycles': 19778, 'sim_instructions': 10601472,
        'sim_cta': 224, 'sim_uid': 102144,
        'off_log': '/root/share/mnt164/huangrulin/awma_c1_nonblocking_cross_context_holdout_v1/raw/H2_OFF_10_80/run.log',
        'off_log_sha': 'e9ae765eef1c835c586121e69acea9ac90ecbb9483cf31626acb652a09ddce7d',
    },
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


def run_target(target: str, timeout: int, overwrite: bool) -> dict[str, object]:
    spec = TARGETS[target]
    payload = INPUTS / str(spec['name'])
    if sha(payload) != spec['sha']:
        raise RuntimeError(f'{target}: trace SHA mismatch')
    if sha(Path(str(spec['off_log']))) != spec['off_log_sha']:
        raise RuntimeError(f'{target}: accepted OFF authority hash mismatch')
    if sha(BINARY) != BINARY_SHA or sha(CONFIG) != CONFIG_SHA or \
            sha(TRACE_CONFIG) != TRACE_CONFIG_SHA:
        raise RuntimeError('frozen mechanism/platform authority mismatch')
    run_dir = DURABLE / f'{target}_COALESCER_10_80'
    rc_path = run_dir / 'rc.txt'
    if not overwrite and rc_path.is_file() and rc_path.read_text().strip() == '0':
        return {'target': target, 'rc': 0, 'status': 'SKIPPED_EXISTING_PASS'}
    run_dir.mkdir(parents=True, exist_ok=True)
    traces = run_dir / 'traces'
    if traces.exists():
        shutil.rmtree(traces)
    traces.mkdir()
    (traces / payload.name).symlink_to(payload)
    (traces / 'kernelslist.g').write_text(f'{payload.name}\n')
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH', '')}"
    for key in tuple(env):
        if key.startswith('GPGPUSIM_AWMA_') or key in (
                'GPGPUSIM_READY_APPLICATION_V2',
                'GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH'):
            env.pop(key, None)
    env['GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH'] = '1'
    env['GPGPUSIM_AWMA_TRANSLATION_CANDIDATE'] = 'prel1_exact_coalescer'
    env['GPGPUSIM_AWMA_PREL1_COMPARE_LATENCY'] = '0'
    env['GPGPUSIM_AWMA_PASSIVE_MEMO_OBSERVER'] = '0'
    env['GPGPUSIM_AWMA_MECHANISM_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_AWMA_OWNER_WAIT_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_VM_COVERAGE_KERNEL_UID'] = '1'
    env['GPGPUSIM_READY_APPLICATION_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS'] = '1'
    cmd = ['nice', '-n', '10', str(BINARY), '-config', str(CONFIG),
           '-trace', 'traces/kernelslist.g'] + trace_args() + overlay()
    receipt = {
        'stage': STAGE, 'role': 'ADDITIONAL_FROZEN_EVALUATION',
        'source_freeze': SOURCE_FREEZE, 'target': target,
        'scientific_id': spec['scientific_id'], 'scenario': spec['scenario'],
        'decode_step': spec['decode_step'], 'kernel_id': spec['kernel_id'],
        'grid': spec['grid'], 'block': spec['block'],
        'recurrence': spec['recurrence'], 'capacity_per_sid': 2,
        'waiters_per_entry': 32, 'compare_latency': 0,
        'accepted_off_cycles': spec['off_cycles'],
        'accepted_off_run_log': spec['off_log'],
        'accepted_off_run_log_sha256': spec['off_log_sha'],
        'argv': cmd,
        'environment': {key: env.get(key) for key in sorted(env)
                        if key.startswith('GPGPUSIM_')},
        'binary_sha256': sha(BINARY), 'config_sha256': sha(CONFIG),
        'trace_config_sha256': sha(TRACE_CONFIG),
        'trace': str(payload), 'trace_sha256': sha(payload),
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
    return {'target': target, 'rc': rc,
            'status': 'PASS' if rc == 0 else 'FAIL'}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--timeout-seconds', type=int, default=3600)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    if args.workers not in (1, 2):
        parser.error('one or two low-priority workers only')
    DURABLE.mkdir(parents=True, exist_ok=True)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_target, target, args.timeout_seconds,
                               args.overwrite) for target in TARGETS]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, sort_keys=True), flush=True)
    results.sort(key=lambda row: str(row['target']))
    (DURABLE / 'launcher_results.json').write_text(
        json.dumps(results, indent=2, sort_keys=True) + '\n')
    return 0 if all(row['rc'] == 0 for row in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
