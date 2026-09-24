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

STAGE = 'AWMA_C1_FANOUT_AWARE_WITHIN_MODEL_HOLDOUT_V1'
REPO = Path('/root/workspace/accel-sim-framework-awma-c1-fanout-aware-within-model-holdout-v1')
RUNTIME = Path('/root/awma_c1_fanout_aware_within_model_holdout_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_c1_fanout_aware_within_model_holdout_v1/raw')
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
CORE_LIB = RUNTIME / 'src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release'
CONFIG = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
TARGETS = {
    'SPLITKV': {
        'identity': 'DECODE_FLASH_PRIMARY_1_STEP16',
        'family': 'FLASH_FWD_SPLITKV',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_v2-decode-flash-primary-1-step16_20260918T175706Z_891c75aa245e/traces/kernel-17543-ctx_0x5be0856adcb0.traceg.xz'),
        'payload_sha256': '282a9b18510bd0aaf54ec528c65bfb39d49b052902c6b87f3b85bb2973096371',
        'index_sha256': '59236d6c6746260a3127c8f858270c915e91c9d7959647047a8d44504a984773',
    },
    'COMBINE': {
        'identity': 'DECODE_FLASH_PRIMARY_2_STEP16',
        'family': 'FLASH_FWD_SPLITKV_COMBINE',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_v2-decode-flash-primary-2-step16_20260918T185037Z_0d352ffacee3/traces/kernel-16813-ctx_0x5c9946e7f280.traceg.xz'),
        'payload_sha256': 'd153db1548517f24eebd80c1a5dc48785ab28ace173b2937dd4f7b4a7005dcb9',
        'index_sha256': '31b54d9f55ce501a6cb64360c2b1c988e2099b7e97e3fb9945d27d4631dd8da2',
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


def prepare_traces(run_dir: Path, target: str) -> tuple[Path, str]:
    spec = TARGETS[target]
    payload = spec['payload']
    assert isinstance(payload, Path)
    if sha(payload) != spec['payload_sha256']:
        raise RuntimeError(f'{target}: payload authority mismatch')
    traces = run_dir / 'traces'
    if traces.exists():
        shutil.rmtree(traces)
    traces.mkdir(parents=True)
    (traces / payload.name).symlink_to(payload)
    index = f'{payload.name}\n'
    (traces / 'kernelslist.g').write_text(index)
    index_sha = hashlib.sha256(index.encode()).hexdigest()
    if index_sha != spec['index_sha256']:
        raise RuntimeError(f'{target}: runner/index authority mismatch')
    return payload, index_sha


def run_point(target: str, threshold: int, timeout: int,
              overwrite: bool) -> dict[str, object]:
    label = f'C1_{threshold}'
    name = f'{target}_{label}_10_80'
    run_dir = DURABLE / name
    rc_path = run_dir / 'rc.txt'
    if not overwrite and rc_path.is_file() and rc_path.read_text().strip() == '0':
        return {'point': name, 'rc': 0, 'status': 'SKIPPED_EXISTING_PASS'}
    run_dir.mkdir(parents=True, exist_ok=True)
    payload, index_sha = prepare_traces(run_dir, target)
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH', '')}"
    for key in (
        'GPGPUSIM_READY_APPLICATION_V2',
        'GPGPUSIM_AWMA_TRANSLATION_CANDIDATE',
        'GPGPUSIM_AWMA_SHARE_ABLATION',
        'GPGPUSIM_AWMA_SHARE_DELIVERY_SLOTS',
        'GPGPUSIM_AWMA_SHARE_MIN_COHORT_SIZE',
        'GPGPUSIM_AWMA_OWNER_WAIT_DIAGNOSTICS',
        'GPGPUSIM_AWMA_CROSSCAL_DIAGNOSTICS',
        'GPGPUSIM_AWMA_ACCESSQ_CARDINALITY_DIAGNOSTICS',
    ):
        env.pop(key, None)
    env['GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH'] = '1'
    env['GPGPUSIM_AWMA_TRANSLATION_CANDIDATE'] = 'same_page_share'
    env['GPGPUSIM_AWMA_SHARE_DELIVERY_SLOTS'] = '1'
    env['GPGPUSIM_AWMA_SHARE_MIN_COHORT_SIZE'] = str(threshold)
    env['GPGPUSIM_AWMA_MECHANISM_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_AWMA_OWNER_WAIT_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_VM_COVERAGE_KERNEL_UID'] = '1'
    env['GPGPUSIM_READY_APPLICATION_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS'] = '1'
    cmd = [str(BINARY), '-config', str(CONFIG), '-trace', 'traces/kernelslist.g']
    cmd += trace_args() + overlay()
    spec = TARGETS[target]
    receipt = {
        'stage': STAGE,
        'accepted_mechanism_parent': 'f685f88d328b8bcb5f56c31b2629e5ed56938bb1',
        'accepted_target_authority': '0fc6c559027b029d79b77c1f6dcfa5162648b1ac',
        'target': target, 'target_identity': spec['identity'],
        'target_family': spec['family'], 'candidate': label,
        'min_cohort_size': threshold, 'delivery_slots': 1,
        'vm_config': '10/80', 'argv': cmd,
        'environment': {key: env.get(key) for key in sorted(env)
                        if key.startswith('GPGPUSIM_')},
        'binary_sha256': sha(BINARY), 'config_sha256': sha(CONFIG),
        'trace_config_sha256': sha(TRACE_CONFIG),
        'payload': str(payload), 'payload_sha256': sha(payload),
        'runner_index_sha256': index_sha,
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
            status = 'PASS' if rc == 0 else 'NONZERO_EXIT'
        except subprocess.TimeoutExpired:
            rc, status = 124, 'TIMEOUT'
    rc_path.write_text(f'{rc}\n')
    (run_dir / 'end_utc.txt').write_text(utc() + '\n')
    (run_dir / 'wall_seconds.txt').write_text(
        f'{time.monotonic() - start:.6f}\n')
    return {'point': name, 'rc': rc, 'status': status}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--timeout-seconds', type=int, default=21600)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.workers <= 2:
        parser.error('holdout runner permits one or two workers only')
    DURABLE.mkdir(parents=True, exist_ok=True)
    points = [(target, threshold) for target in ('SPLITKV', 'COMBINE')
              for threshold in (2, 4)]
    results: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_point, target, threshold,
                               args.timeout_seconds, args.overwrite)
                   for target, threshold in points]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, sort_keys=True), flush=True)
    results.sort(key=lambda row: str(row['point']))
    (RUNTIME / 'launcher_results.json').write_text(
        json.dumps(results, indent=2, sort_keys=True) + '\n')
    return 0 if all(row['rc'] == 0 for row in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
