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

STAGE = 'AWMA_C1_NONBLOCKING_OPPORTUNISTIC_SHARING_V1'
REPO = Path('/root/workspace/accel-sim-framework-awma-c1-nonblocking-opportunistic-sharing-v1')
RUNTIME = Path('/root/awma_c1_nonblocking_opportunistic_sharing_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_c1_nonblocking_opportunistic_sharing_v1/raw')
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
CORE_LIB = RUNTIME / 'src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release'
CONFIG = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
SMOKE = Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/mechanism_sensitive_accessq_v1_20260923T114500Z/A1_CONTROL/raw')
TARGETS = {
    'T0': {
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native-contiguous-prefix_q05-contiguous-prefix_20260918T022749Z_1fea2d955d1c/traces/kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz'),
        'payload_sha': 'd8fa338f82800f646c8501a6a1d1049afaae213fe0d7f70d4913fcfaa76ba67a',
        'index_sha': 'a8b4ba1cf33f34be345b38908cb39572c0d14972170fd1972b4b080e81154fd5',
    },
    'T1': {
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native_prefill-gemm-primary-occ0_20260918T052739Z_01540d931e17/traces/kernel-45-ctx_0x60d38cb72530.traceg.xz'),
        'payload_sha': 'e36178f9a92033cd91f3c1ff4b165321b7958157c7deed2a9aaa4696e7c73e8c',
        'index_sha': 'c9dd68f84606deceb8d7dcece6e35c93750b16bf507ac3666c3adb2a0e0cdc41',
    },
    'T2': {
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_decode-gemv-primary-step16_20260918T074437Z_b0dfb1af1ae1/traces/kernel-17039-ctx_0x5ddb6907c160.traceg.xz'),
        'payload_sha': 'b87cd6cb6a2bc0f67e17616e26d1bf9091facad242d46a43f5f9c1ac274b6138',
        'index_sha': '2a458d31a945cf11ce465b563582e6ab29292ae692bd3d2acd74bf4e8b5c2c4a',
    },
    'SPLITKV': {
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_v2-decode-flash-primary-1-step16_20260918T175706Z_891c75aa245e/traces/kernel-17543-ctx_0x5be0856adcb0.traceg.xz'),
        'payload_sha': '282a9b18510bd0aaf54ec528c65bfb39d49b052902c6b87f3b85bb2973096371',
        'index_sha': '59236d6c6746260a3127c8f858270c915e91c9d7959647047a8d44504a984773',
    },
    'COMBINE': {
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_v2-decode-flash-primary-2-step16_20260918T185037Z_0d352ffacee3/traces/kernel-16813-ctx_0x5c9946e7f280.traceg.xz'),
        'payload_sha': 'd153db1548517f24eebd80c1a5dc48785ab28ace173b2937dd4f7b4a7005dcb9',
        'index_sha': '31b54d9f55ce501a6cb64360c2b1c988e2099b7e97e3fb9945d27d4631dd8da2',
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


def prepare_traces(run_dir: Path, target: str) -> tuple[Path | None, str]:
    traces = run_dir / 'traces'
    if traces.exists():
        shutil.rmtree(traces)
    if target == 'A1':
        shutil.copytree(SMOKE, traces, symlinks=True)
        return None, sha(traces / 'kernelslist.g')
    spec = TARGETS[target]
    payload = spec['payload']
    assert isinstance(payload, Path)
    if sha(payload) != spec['payload_sha']:
        raise RuntimeError(f'{target}: payload authority mismatch')
    traces.mkdir(parents=True)
    (traces / payload.name).symlink_to(payload)
    index = f'{payload.name}\n'
    (traces / 'kernelslist.g').write_text(index)
    index_sha = hashlib.sha256(index.encode()).hexdigest()
    if index_sha != spec['index_sha']:
        raise RuntimeError(f'{target}: runner/index authority mismatch')
    return payload, index_sha


def run_point(target: str, timeout: int, overwrite: bool) -> dict[str, object]:
    name = f'{target}_NONBLOCKING_SHARE_10_80'
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
    env['GPGPUSIM_AWMA_TRANSLATION_CANDIDATE'] = \
        'nonblocking_opportunistic_share'
    env['GPGPUSIM_AWMA_MECHANISM_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_AWMA_OWNER_WAIT_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_VM_COVERAGE_KERNEL_UID'] = '2' if target == 'A1' else '1'
    env['GPGPUSIM_READY_APPLICATION_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS'] = '1'
    cmd = [str(BINARY), '-config', str(CONFIG), '-trace', 'traces/kernelslist.g']
    cmd += trace_args() + overlay()
    receipt = {
        'stage': STAGE,
        'accepted_parent': 'b2762f0cf6112018de37d78624b69adce08893aa',
        'target': target, 'candidate': 'NONBLOCKING_OPPORTUNISTIC_SHARE',
        'fanout_threshold_used': False, 'delivery_rule': 'HEAD_ONLY_ONE_PER_CYCLE',
        'vm_config': '10/80', 'argv': cmd,
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
    (run_dir / 'wall_seconds.txt').write_text(
        f'{time.monotonic() - start:.6f}\n')
    return {'point': name, 'rc': rc, 'status': status}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('matrix', choices=('smoke', 'development'))
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--timeout-seconds', type=int, default=21600)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.workers <= 2:
        parser.error('runner permits one or two workers only')
    targets = ('A1',) if args.matrix == 'smoke' else \
        ('T0', 'T1', 'T2', 'SPLITKV', 'COMBINE')
    DURABLE.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_point, target, args.timeout_seconds,
                               args.overwrite) for target in targets]
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
