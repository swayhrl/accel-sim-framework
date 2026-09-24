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

REPO = Path('/root/workspace/accel-sim-framework-awma-rtx4080-v1-ideal-translation-flash-extension-v1')
RUNTIME = Path('/root/awma_rtx4080_v1_ideal_translation_flash_extension_v1_runtime')
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
CONFIG = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
CORE_LIB = RUNTIME / 'src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release'

TARGETS = {
    'SPLITKV': {
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_v2-decode-flash-primary-1-step16_20260918T175706Z_891c75aa245e/traces/kernel-17543-ctx_0x5be0856adcb0.traceg.xz'),
        'index_content': 'kernel-17543-ctx_0x5be0856adcb0.traceg.xz\n',
    },
    'COMBINE': {
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_v2-decode-flash-primary-2-step16_20260918T185037Z_0d352ffacee3/traces/kernel-16813-ctx_0x5c9946e7f280.traceg.xz'),
        'index_content': 'kernel-16813-ctx_0x5c9946e7f280.traceg.xz\n',
    },
}

EXPECTED = {
    'SPLITKV': {'instructions': 36599648, 'cta': 126, 'unique_uid': 233814},
    'COMBINE': {'instructions': 72908, 'cta': 2, 'unique_uid': 1099},
}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def trace_args() -> list[str]:
    out: list[str] = []
    for line in TRACE_CONFIG.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            out.extend(shlex.split(line))
    return out


def overlay(l1: int) -> list[str]:
    return [
        '-gpgpu_vm_mode', '2', '-gpgpu_vm_page_size', '65536',
        '-gpgpu_vm_l1_tlb_entries', '32', '-gpgpu_vm_l1_tlb_assoc', '32',
        '-gpgpu_vm_l1_tlb_ports', '1', '-gpgpu_vm_l1_tlb_lookup_latency', str(l1),
        '-gpgpu_vm_l2_tlb_entries', '768', '-gpgpu_vm_l2_tlb_assoc', '16',
        '-gpgpu_vm_l2_tlb_ports', '1', '-gpgpu_vm_l2_tlb_lookup_latency', '80',
        '-gpgpu_vm_translation_mshr_entries', '32', '-gpgpu_vm_pwq_entries', '32',
        '-gpgpu_vm_walkers', '16', '-gpgpu_vm_ptw_mode', '1', '-gpgpu_vm_pt_levels', '4',
        '-gpgpu_vm_virtual_address_bits', '49', '-gpgpu_vm_pwc_mode', '1',
        '-gpgpu_vm_pwc_entries', '128', '-gpgpu_vm_pwc_lookup_latency', '1',
    ]


def run_point(target: str, mode: str, timeout_s: int) -> dict[str, object]:
    run_dir = RUNTIME / f'ai_{target}_V1_{mode}'
    rc_file = run_dir / 'rc.txt'
    if rc_file.is_file() and rc_file.read_text().strip() == '0':
        return {'point': run_dir.name, 'rc': 0, 'status': 'SKIPPED_EXISTING_PASS'}
    run_dir.mkdir(parents=True, exist_ok=True)
    traces = run_dir / 'traces'
    traces.mkdir(exist_ok=True)
    payload = TARGETS[target]['payload']
    link = traces / payload.name
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(payload)
    index = str(TARGETS[target]['index_content'])
    (traces / 'kernelslist.g').write_text(index)

    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH', '')}"
    for key in (
        'GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH', 'GPGPUSIM_READY_APPLICATION_V2',
        'GPGPUSIM_AWMA_CROSSCAL_DIAGNOSTICS', 'GPGPUSIM_AWMA_ACCESSQ_CARDINALITY_DIAGNOSTICS',
    ):
        env.pop(key, None)
    env['GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH'] = '1'
    env['GPGPUSIM_VM_PRELAUNCH_ELIGIBILITY_KERNEL_UID'] = '1'
    env['GPGPUSIM_VM_MAPPING_DIGEST_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS'] = '1'
    if mode == 'ideal':
        env['GPGPUSIM_VM_IDEAL_TRANSLATION_CONTROL'] = '1'
    env['GPGPUSIM_VM_COVERAGE_KERNEL_UID'] = '1'
    env['GPGPUSIM_READY_APPLICATION_DIAGNOSTICS'] = '1'

    cmd = [str(BINARY), '-config', str(CONFIG), '-trace', 'traces/kernelslist.g']
    cmd += trace_args() + overlay(10)
    authority = {
        'target': target, 'semantic': f'V1_{mode.upper()}_TRANSLATION_CONTROL', 'latency': mode,
        'argv': cmd, 'environment': {k: env.get(k) for k in sorted(env) if k.startswith('GPGPUSIM_')},
        'payload': str(payload), 'payload_sha256': sha_bytes(payload.read_bytes()),
        'runner_index_sha256': sha_bytes(index.encode()),
    }
    (run_dir / 'command.json').write_text(json.dumps(authority, indent=2, sort_keys=True) + '\n')
    (run_dir / 'start_utc.txt').write_text(utc() + '\n')
    start = time.monotonic()
    with (run_dir / 'run.log').open('w') as out, (run_dir / 'run.stderr').open('w') as err:
        try:
            p = subprocess.run(cmd, cwd=run_dir, env=env, stdout=out, stderr=err,
                               timeout=timeout_s, check=False)
            rc = p.returncode
            status = 'PASS' if rc == 0 else 'NONZERO_EXIT'
        except subprocess.TimeoutExpired:
            rc, status = 124, 'TIMEOUT'
    (run_dir / 'rc.txt').write_text(f'{rc}\n')
    (run_dir / 'end_utc.txt').write_text(utc() + '\n')
    (run_dir / 'wall_seconds.txt').write_text(f'{time.monotonic() - start:.6f}\n')
    return {'point': run_dir.name, 'rc': rc, 'status': status}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=1)
    ap.add_argument('--timeout-seconds', type=int, default=21600)
    ap.add_argument('--mode', choices=('ideal', 'off'), default='ideal')
    ap.add_argument('--targets', nargs='+', choices=('SPLITKV', 'COMBINE'),
                    default=('SPLITKV', 'COMBINE'))
    args = ap.parse_args()
    points = [(t, args.mode) for t in args.targets]
    binary_sha = sha_bytes(BINARY.read_bytes())
    config_sha = sha_bytes(CONFIG.read_bytes())
    trace_config_sha = sha_bytes(TRACE_CONFIG.read_bytes())
    authority = RUNTIME / 'AI_MATRIX_CONFIG_AUTHORITY.prelaunch.tsv'
    with authority.open('w', newline='') as f:
        import csv
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(['target', 'semantic', 'vm_config', 'payload', 'payload_sha256',
                    'runner_index_sha256', 'platform_config_sha256', 'trace_config_sha256',
                    'binary_sha256', 'pipeline_launch', 'ready_application_v2', 'output_directory',
                    'expected_instructions', 'expected_cta', 'expected_unique_uid'])
        for target, mode in points:
            payload = TARGETS[target]['payload']
            index = str(TARGETS[target]['index_content'])
            w.writerow([target, f'V1_{mode.upper()}_TRANSLATION_CONTROL', mode, payload, sha_bytes(payload.read_bytes()),
                        sha_bytes(index.encode()), config_sha, trace_config_sha, binary_sha,
                        1, 0, RUNTIME / f'ai_{target}_V1_{mode}',
                        EXPECTED[target]['instructions'], EXPECTED[target]['cta'],
                        EXPECTED[target]['unique_uid']])
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_point, *point, args.timeout_seconds) for point in points]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, sort_keys=True), flush=True)
    results.sort(key=lambda x: str(x['point']))
    (RUNTIME / 'ai_matrix_launcher_results.json').write_text(json.dumps(results, indent=2, sort_keys=True) + '\n')
    return 0 if all(r['rc'] == 0 for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
