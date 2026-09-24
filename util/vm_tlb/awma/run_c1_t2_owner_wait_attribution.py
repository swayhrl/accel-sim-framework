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

REPO = Path('/root/workspace/accel-sim-framework-awma-c1-t2-owner-wait-retry-attribution-v1')
RUNTIME = Path(os.environ.get(
    'AWMA_ATTRIBUTION_RUNTIME',
    '/root/awma_c1_t2_owner_wait_retry_attribution_v1_runtime'))
DURABLE = Path(os.environ.get(
    'AWMA_ATTRIBUTION_DURABLE',
    '/root/share/mnt164/huangrulin/awma_c1_t2_owner_wait_retry_attribution_v1/raw'))
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
CORE_LIB = RUNTIME / 'src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release'
CONFIG = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
SMOKE = Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/mechanism_sensitive_accessq_v1_20260923T114500Z/A1_CONTROL/raw')
TARGETS = {
    'T0': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native-contiguous-prefix_q05-contiguous-prefix_20260918T022749Z_1fea2d955d1c/traces/kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz'),
    'T2': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_decode-gemv-primary-step16_20260918T074437Z_b0dfb1af1ae1/traces/kernel-17039-ctx_0x5ddb6907c160.traceg.xz'),
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


def prepare_traces(run_dir: Path, target: str) -> tuple[Path | None, str]:
    traces = run_dir / 'traces'
    if traces.exists():
        shutil.rmtree(traces)
    if target == 'A1':
        shutil.copytree(SMOKE, traces, symlinks=True)
        return None, sha(traces / 'kernelslist.g')
    traces.mkdir(parents=True)
    payload = TARGETS[target]
    (traces / payload.name).symlink_to(payload)
    index = f'{payload.name}\n'
    (traces / 'kernelslist.g').write_text(index)
    return payload, hashlib.sha256(index.encode()).hexdigest()


def run_point(target: str, semantic: str, timeout: int,
              overwrite: bool) -> dict[str, object]:
    name = f'{target}_{semantic}_OWNER_WAIT_TELEM_10_80'
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
        'GPGPUSIM_AWMA_OWNER_WAIT_DIAGNOSTICS',
        'GPGPUSIM_AWMA_CROSSCAL_DIAGNOSTICS',
        'GPGPUSIM_AWMA_ACCESSQ_CARDINALITY_DIAGNOSTICS',
    ):
        env.pop(key, None)
    env['GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH'] = '1'
    if semantic in ('C1', 'C1_READY_ONLY_NO_WAIT'):
        env['GPGPUSIM_AWMA_TRANSLATION_CANDIDATE'] = 'same_page_share'
        env['GPGPUSIM_AWMA_SHARE_DELIVERY_SLOTS'] = '1'
    if semantic == 'C1_READY_ONLY_NO_WAIT':
        env['GPGPUSIM_AWMA_SHARE_ABLATION'] = 'ready_only_no_wait'
    env['GPGPUSIM_AWMA_MECHANISM_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_AWMA_OWNER_WAIT_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_VM_COVERAGE_KERNEL_UID'] = '2' if target == 'A1' else '1'
    env['GPGPUSIM_READY_APPLICATION_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS'] = '1'
    cmd = [str(BINARY), '-config', str(CONFIG), '-trace', 'traces/kernelslist.g']
    cmd += trace_args() + overlay()
    receipt = {
        'stage': 'AWMA_C1_T2_OWNER_WAIT_RETRY_ATTRIBUTION_V1',
        'accepted_parent': '070cb2f8b1ffea431f0f8acb9ca32a0dd16a0f14',
        'target': target, 'semantic': semantic, 'vm_config': '10/80',
        'argv': cmd,
        'environment': {key: env.get(key) for key in sorted(env)
                        if key.startswith('GPGPUSIM_')},
        'binary_sha256': sha(BINARY), 'config_sha256': sha(CONFIG),
        'trace_config_sha256': sha(TRACE_CONFIG),
        'payload': str(payload) if payload else str(SMOKE),
        'payload_sha256': sha(payload) if payload else None,
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
    (run_dir / 'wall_seconds.txt').write_text(f'{time.monotonic() - start:.6f}\n')
    return {'point': name, 'rc': rc, 'status': status}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'matrix', choices=('smoke', 'telemetry', 'ablation-smoke', 'ablation'))
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--timeout-seconds', type=int, default=21600)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    if args.matrix == 'smoke':
        points = [('A1', 'C1')]
    elif args.matrix == 'telemetry':
        points = [(target, semantic) for target in ('T0', 'T2')
                  for semantic in ('OFF', 'C1')]
    elif args.matrix == 'ablation-smoke':
        points = [('A1', 'C1_READY_ONLY_NO_WAIT')]
    else:
        points = [('T2', 'C1_READY_ONLY_NO_WAIT')]
    DURABLE.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_point, target, semantic,
                               args.timeout_seconds, args.overwrite)
                   for target, semantic in points]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, sort_keys=True), flush=True)
    results.sort(key=lambda row: str(row['point']))
    (RUNTIME / f'{args.matrix}_launcher_results.json').write_text(
        json.dumps(results, indent=2, sort_keys=True) + '\n')
    return 0 if all(row['rc'] == 0 for row in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
