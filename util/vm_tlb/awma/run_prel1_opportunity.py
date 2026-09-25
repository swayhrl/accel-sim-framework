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
REPO = Path('/root/workspace/accel-sim-framework-awma-prel1-translation-request-coalescing-discovery-prototype-v1')
RUNTIME = Path('/root/awma_prel1_coalescing_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_prel1_coalescing_v1/phase_a_raw')
CONFIG = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
CORE_LIB = RUNTIME / 'src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release'
BINARY_SHA = '1c58566a8684b424ad082bc5a55a7277faf00d81024ce79005b04a681c9e6125'
SOURCE_COMMIT = 'b9b8fc18a0020e61ac960f8bfa7da7c1e722fc42'

TARGETS = {
    'T0': {
        'family': 'PREFILL_FLASH',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native-contiguous-prefix_q05-contiguous-prefix_20260918T022749Z_1fea2d955d1c/traces/kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz'),
        'sha': 'd8fa338f82800f646c8501a6a1d1049afaae213fe0d7f70d4913fcfaa76ba67a',
    },
    'T1': {
        'family': 'PREFILL_GEMM',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native_prefill-gemm-primary-occ0_20260918T052739Z_01540d931e17/traces/kernel-45-ctx_0x60d38cb72530.traceg.xz'),
        'sha': 'e36178f9a92033cd91f3c1ff4b165321b7958157c7deed2a9aaa4696e7c73e8c',
    },
    'T2': {
        'family': 'DECODE_GEMV',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_decode-gemv-primary-step16_20260918T074437Z_b0dfb1af1ae1/traces/kernel-17039-ctx_0x5ddb6907c160.traceg.xz'),
        'sha': 'b87cd6cb6a2bc0f67e17616e26d1bf9091facad242d46a43f5f9c1ac274b6138',
    },
    'SPLITKV': {
        'family': 'FLASH_FWD_SPLITKV',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_v2-decode-flash-primary-1-step16_20260918T175706Z_891c75aa245e/traces/kernel-17543-ctx_0x5be0856adcb0.traceg.xz'),
        'sha': '282a9b18510bd0aaf54ec528c65bfb39d49b052902c6b87f3b85bb2973096371',
    },
    'COMBINE': {
        'family': 'FLASH_FWD_SPLITKV_COMBINE',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_v2-decode-flash-primary-2-step16_20260918T185037Z_0d352ffacee/traces/kernel-16813-ctx_0x5c9946e7f280.traceg.xz'),
        'sha': 'd153db1548517f24eebd80c1a5dc48785ab28ace173b2937dd4f7b4a7005dcb9',
    },
    'A1': {
        'family': 'DECODE_GEMV_PAIR_A_S2_T2048',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/runtime_identity_bridge_batch1_20260924/A1_formal/raw/kernel-16828-ctx_0x608ad97ab300.traceg.xz'),
        'sha': '49f83c02fbb01dcc9167c6790271103e98d42f318c0344b5f26b8433b704d099',
    },
    'A2': {
        'family': 'DECODE_GEMV_PAIR_A_T8192',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/runtime_identity_bridge_batch1_20260924/A2_formal/raw/kernel-16828-ctx_0x573505e282b0.traceg.xz'),
        'sha': 'c8135003bae105108707ab6b024ca56e50146df88d1692068d92e99511ada2ca',
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
    payload = spec['payload']
    assert isinstance(payload, Path)
    if sha(payload) != spec['sha']:
        raise RuntimeError(f'{target}: trace SHA mismatch')
    if sha(BINARY) != BINARY_SHA:
        raise RuntimeError('Phase-A binary SHA mismatch')
    run_dir = DURABLE / f'{target}_OFF_OPPORTUNITY_10_80'
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
    env['GPGPUSIM_AWMA_PREL1_OPPORTUNITY'] = '1'
    env['GPGPUSIM_AWMA_PASSIVE_MEMO_OBSERVER'] = '0'
    env['GPGPUSIM_AWMA_BOTTLENECK_OBSERVATORY'] = '1'
    env['GPGPUSIM_VM_COVERAGE_KERNEL_UID'] = '1'
    env['GPGPUSIM_READY_APPLICATION_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS'] = '1'
    cmd = ['nice', '-n', '10', str(BINARY), '-config', str(CONFIG),
           '-trace', 'traces/kernelslist.g'] + trace_args() + overlay()
    receipt = {
        'stage': STAGE, 'phase': 'PHASE_A_OFF_ONLY_OPPORTUNITY',
        'source_commit': SOURCE_COMMIT, 'target': target,
        'family': spec['family'], 'candidate_enabled': False,
        'vm_config': '10/80', 'argv': cmd,
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
            status = 'PASS' if rc == 0 else 'NONZERO_EXIT'
        except subprocess.TimeoutExpired:
            rc, status = 124, 'TIMEOUT'
    rc_path.write_text(f'{rc}\n')
    (run_dir / 'end_utc.txt').write_text(utc() + '\n')
    (run_dir / 'wall_seconds.txt').write_text(
        f'{time.monotonic() - start:.6f}\n')
    return {'target': target, 'rc': rc, 'status': status}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--timeout-seconds', type=int, default=21600)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    if args.workers not in (1, 2):
        parser.error('Phase A permits one or two low-priority workers')
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
    (RUNTIME / 'phase_a_launcher_results.json').write_text(
        json.dumps(results, indent=2, sort_keys=True) + '\n')
    return 0 if all(row['rc'] == 0 for row in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
