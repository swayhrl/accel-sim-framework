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

REPO = Path('/root/workspace/accel-sim-framework-awma-c1-a2-nonsharing-regression-attribution-v1')
RUNTIME = Path('/root/awma_c1_a2_nonsharing_regression_attribution_v1_runtime')
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
CORE_LIB = RUNTIME / 'src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release'
CONFIG = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
TARGETS = {
    'A1': {
        'scenario': 'S2',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/runtime_identity_bridge_batch1_20260924/A1_formal/raw/kernel-16828-ctx_0x608ad97ab300.traceg.xz'),
        'payload_sha': '49f83c02fbb01dcc9167c6790271103e98d42f318c0344b5f26b8433b704d099',
        'index_sha': 'c3537cc9d89d73c30e1f416fd5c61b07e10059d8cb7b18b250ef13cf79b6d210',
        'cycles': {'off': 114123, 'candidate': 112023},
    },
    'A2': {
        'scenario': 'T8192',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/runtime_identity_bridge_batch1_20260924/A2_formal/raw/kernel-16828-ctx_0x573505e282b0.traceg.xz'),
        'payload_sha': 'c8135003bae105108707ab6b024ca56e50146df88d1692068d92e99511ada2ca',
        'index_sha': 'db6427e3ab7ece5f07791732ddde2f7f6c696b26112593eea61177a7f637eeb1',
        'cycles': {'off': 117698, 'candidate': 125427},
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def utc() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def trace_args() -> list[str]:
    result = []
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


def run(target: str, mode: str, level: int, tag: str, domains: str,
        timeout_seconds: int) -> int:
    spec = TARGETS[target]
    payload = spec['payload']
    if sha256(payload) != spec['payload_sha']:
        raise RuntimeError(f'{target}: payload authority mismatch')
    index = f'{payload.name}\n'
    if hashlib.sha256(index.encode()).hexdigest() != spec['index_sha']:
        raise RuntimeError(f'{target}: index authority mismatch')
    run_dir = RUNTIME / 'runs' / target / mode / f'L{level}_{tag}'
    if run_dir.exists():
        raise RuntimeError(f'refusing to overwrite {run_dir}')
    traces = run_dir / 'traces'
    traces.mkdir(parents=True)
    (traces / payload.name).symlink_to(payload)
    (traces / 'kernelslist.g').write_text(index)

    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH', '')}"
    for key in tuple(env):
        if key.startswith('GPGPUSIM_AWMA_') or key in {
                'GPGPUSIM_READY_APPLICATION_V2',
                'GPGPUSIM_T1_ATTRIBUTION_DIAGNOSTICS'}:
            env.pop(key, None)
    env.update({
        'GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH': '1',
        'GPGPUSIM_VM_COVERAGE_KERNEL_UID': '1',
        'GPGPUSIM_VM_MAPPING_DIGEST_DIAGNOSTICS': '1',
        'GPGPUSIM_READY_APPLICATION_DIAGNOSTICS': '1',
        'GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS': '1',
        'GPGPUSIM_AWMA_BOTTLENECK_OBSERVATORY': str(level),
        'GPGPUSIM_AWMA_BOTTLENECK_DOMAINS': domains,
    })
    if mode == 'candidate':
        env.update({
            'GPGPUSIM_AWMA_TRANSLATION_CANDIDATE':
                'nonblocking_opportunistic_share',
            'GPGPUSIM_AWMA_MECHANISM_DIAGNOSTICS': '1',
            'GPGPUSIM_AWMA_OWNER_WAIT_DIAGNOSTICS': '1',
        })

    command = [str(BINARY), '-config', str(CONFIG), '-trace',
               'traces/kernelslist.g'] + trace_args() + overlay()
    receipt = {
        'stage': 'AWMA_C1_A2_NONSHARING_REGRESSION_ATTRIBUTION_V1',
        'frozen_mechanism_authority':
            'c0602ee06e647d9a3cf84b0adbb8d98075021f99',
        'observatory_authority':
            'b85d388abe98e5da70b749b52075c33fad7cede4',
        'pair_a_authority': '9e7e6e3bbe3f3867dbf089ec3b97d5d51507776f',
        'target': target, 'scenario': spec['scenario'], 'decode_step': 16,
        'mode': mode, 'level': level, 'domains': domains, 'tag': tag,
        'argv': command,
        'environment': {key: env[key] for key in sorted(env)
                        if key.startswith('GPGPUSIM_')},
        'binary_sha256': sha256(BINARY), 'core_library_sha256':
            sha256(CORE_LIB / 'libcudart.so'),
        'config_sha256': sha256(CONFIG),
        'trace_config_sha256': sha256(TRACE_CONFIG),
        'payload': str(payload), 'payload_sha256': sha256(payload),
        'runner_index_sha256': hashlib.sha256(index.encode()).hexdigest(),
        'expected': {'cycles': spec['cycles'][mode], 'instructions': 34883072,
                     'cta': 224, 'unique_uid': 409024},
    }
    (run_dir / 'command.json').write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    (run_dir / 'start_utc.txt').write_text(utc() + '\n')
    start = time.monotonic()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
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
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    (run_dir / 'host_metrics.txt').write_text(
        f'wall_seconds={elapsed:.9f}\n'
        f'user_seconds={after.ru_utime - before.ru_utime:.9f}\n'
        f'system_seconds={after.ru_stime - before.ru_stime:.9f}\n'
        f'max_rss_kb={after.ru_maxrss}\nexit_status={rc}\n')
    (run_dir / 'rc.txt').write_text(f'{rc}\n')
    (run_dir / 'end_utc.txt').write_text(utc() + '\n')
    print(json.dumps({'run_dir': str(run_dir), 'rc': rc}, sort_keys=True),
          flush=True)
    return rc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', choices=tuple(TARGETS), required=True)
    parser.add_argument('--mode', choices=('off', 'candidate'), required=True)
    parser.add_argument('--level', choices=(0, 1, 2, 3), type=int, required=True)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--domains', default='all')
    parser.add_argument('--timeout-seconds', type=int, default=21600)
    args = parser.parse_args()
    return run(args.target, args.mode, args.level, args.tag, args.domains,
               args.timeout_seconds)


if __name__ == '__main__':
    raise SystemExit(main())
