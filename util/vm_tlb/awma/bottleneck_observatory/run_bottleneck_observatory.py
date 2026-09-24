#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import shlex
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/root/workspace/accel-sim-framework-awma-bottleneck-observatory-v1')
RUNTIME = Path('/root/awma_bottleneck_observatory_v1_runtime')
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
CONFIG = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
CORE_LIB = RUNTIME / 'src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release'

TARGETS = {
    'T1': {
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native_prefill-gemm-primary-occ0_20260918T052739Z_01540d931e17/traces/kernel-45-ctx_0x60d38cb72530.traceg.xz'),
        'index': 'kernel-45-ctx_0x60d38cb72530.traceg.xz\n',
        'instructions': 369131520, 'cta': 384, 'unique_uid': 7159808,
        'cycles': {'10_80': 665802, '0_80': 664805, 'ideal': 715636},
    },
    'T2': {
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_decode-gemv-primary-step16_20260918T074437Z_b0dfb1af1ae1/traces/kernel-17039-ctx_0x5ddb6907c160.traceg.xz'),
        'index': 'kernel-17039-ctx_0x5ddb6907c160.traceg.xz\n',
        'instructions': 43357696, 'cta': 1216, 'unique_uid': 411008,
        'cycles': {'10_80': 93079, '0_80': 83439, 'ideal': 83713},
    },
    'COMBINE': {
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_v2-decode-flash-primary-2-step16_20260918T185037Z_0d352ffacee3/traces/kernel-16813-ctx_0x5c9946e7f280.traceg.xz'),
        'index': 'kernel-16813-ctx_0x5c9946e7f280.traceg.xz\n',
        'instructions': 72908, 'cta': 2, 'unique_uid': 1099,
        'cycles': {'10_80': 10480, '0_80': 10312, 'ideal': 8835},
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
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


def overlay(translation: str) -> list[str]:
    l1_latency = '0' if translation == '0_80' else '10'
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
    ]


def run(target: str, translation: str, level: int, tag: str,
        timeout_seconds: int, domains: str) -> int:
    definition = TARGETS[target]
    run_dir = RUNTIME / 'runs' / target / translation / f'L{level}_{tag}'
    if run_dir.exists():
        raise SystemExit(f'refusing to overwrite {run_dir}')
    traces = run_dir / 'traces'
    traces.mkdir(parents=True)
    payload = definition['payload']
    (traces / payload.name).symlink_to(payload)
    (traces / 'kernelslist.g').write_text(definition['index'])

    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH', '')}"
    for key in tuple(env):
        if key.startswith('GPGPUSIM_AWMA_BOTTLENECK_') or key in {
                'GPGPUSIM_VM_IDEAL_TRANSLATION_CONTROL',
                'GPGPUSIM_T1_ATTRIBUTION_DIAGNOSTICS'}:
            env.pop(key, None)
    env.update({
        'GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH': '1',
        'GPGPUSIM_VM_PRELAUNCH_ELIGIBILITY_KERNEL_UID': '1',
        'GPGPUSIM_VM_MAPPING_DIGEST_DIAGNOSTICS': '1',
        'GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS': '1',
        'GPGPUSIM_VM_COVERAGE_KERNEL_UID': '1',
        'GPGPUSIM_READY_APPLICATION_DIAGNOSTICS': '1',
        'GPGPUSIM_AWMA_BOTTLENECK_OBSERVATORY': str(level),
        'GPGPUSIM_AWMA_BOTTLENECK_DOMAINS': domains,
    })
    if translation == 'ideal':
        env['GPGPUSIM_VM_IDEAL_TRANSLATION_CONTROL'] = '1'

    simulator = [str(BINARY), '-config', str(CONFIG), '-trace',
                 'traces/kernelslist.g'] + trace_args() + overlay(translation)
    time_file = run_dir / 'host_metrics.txt'
    command = simulator
    authority = {
        'stage': 'AWMA_BOTTLENECK_OBSERVATORY_V1',
        'target': target, 'translation': translation, 'level': level,
        'domains': domains, 'tag': tag, 'argv': command,
        'environment': {key: env[key] for key in sorted(env)
                        if key.startswith('GPGPUSIM_')},
        'payload': str(payload), 'payload_sha256': sha256(payload),
        'index_sha256': hashlib.sha256(definition['index'].encode()).hexdigest(),
        'binary_sha256': sha256(BINARY),
        'config_sha256': sha256(CONFIG),
        'trace_config_sha256': sha256(TRACE_CONFIG),
        'expected': {
            'cycles': definition['cycles'][translation],
            'instructions': definition['instructions'],
            'cta': definition['cta'], 'unique_uid': definition['unique_uid'],
        },
    }
    (run_dir / 'command.json').write_text(
        json.dumps(authority, indent=2, sort_keys=True) + '\n')
    (run_dir / 'start_utc.txt').write_text(utc() + '\n')
    start = time.monotonic()
    usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    with (run_dir / 'run.log').open('w') as stdout, \
            (run_dir / 'run.stderr').open('w') as stderr:
        try:
            proc = subprocess.run(command, cwd=run_dir, env=env, stdout=stdout,
                                  stderr=stderr, timeout=timeout_seconds,
                                  check=False)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            rc = 124
    elapsed = time.monotonic() - start
    usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
    time_file.write_text(
        f'wall_seconds={elapsed:.9f}\n'
        f'user_seconds={usage_after.ru_utime - usage_before.ru_utime:.9f}\n'
        f'system_seconds={usage_after.ru_stime - usage_before.ru_stime:.9f}\n'
        f'max_rss_kb={usage_after.ru_maxrss}\n'
        f'exit_status={rc}\n')
    (run_dir / 'rc.txt').write_text(f'{rc}\n')
    (run_dir / 'end_utc.txt').write_text(utc() + '\n')
    (run_dir / 'launcher_wall_seconds.txt').write_text(
        f'{elapsed:.6f}\n')
    output_bytes = sum(path.stat().st_size for path in
                       (run_dir / 'run.log', run_dir / 'run.stderr', time_file)
                       if path.exists())
    (run_dir / 'output_bytes.txt').write_text(f'{output_bytes}\n')
    print(json.dumps({'run_dir': str(run_dir), 'rc': rc}, sort_keys=True),
          flush=True)
    return rc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', choices=tuple(TARGETS), required=True)
    parser.add_argument('--translation', choices=('10_80', '0_80', 'ideal'),
                        default='10_80')
    parser.add_argument('--level', type=int, choices=(0, 1, 2, 3), required=True)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--domains', default='all')
    parser.add_argument('--timeout-seconds', type=int, default=21600)
    args = parser.parse_args()
    return run(args.target, args.translation, args.level, args.tag,
               args.timeout_seconds, args.domains)


if __name__ == '__main__':
    raise SystemExit(main())
