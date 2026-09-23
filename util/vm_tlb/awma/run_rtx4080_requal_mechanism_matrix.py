#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import shlex
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/root/workspace/accel-sim-framework-awma-174-rtx4080-platform-requal-mechanism-v1')
RUNTIME = Path('/root/awma_rtx4080_requal_mechanism_v1_runtime')
BINARY = RUNTIME / 'bin/science_diag_accel-sim.out'
CONFIG = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
CONTROL_BUNDLE = Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/crosscal_exact_v1r1_20260923T111500Z')
MECHANISM_BUNDLE = Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/mechanism_sensitive_accessq_v1_20260923T114500Z')
CORE_LIB = RUNTIME / 'src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release'


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def trace_args() -> list[str]:
    args: list[str] = []
    for line in TRACE_CONFIG.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            args.extend(shlex.split(line))
    return args


def overlay_args(l1_latency: int) -> list[str]:
    return [
        '-gpgpu_vm_mode', '2',
        '-gpgpu_vm_page_size', '65536',
        '-gpgpu_vm_l1_tlb_entries', '32',
        '-gpgpu_vm_l1_tlb_assoc', '32',
        '-gpgpu_vm_l1_tlb_ports', '1',
        '-gpgpu_vm_l1_tlb_lookup_latency', str(l1_latency),
        '-gpgpu_vm_l2_tlb_entries', '768',
        '-gpgpu_vm_l2_tlb_assoc', '16',
        '-gpgpu_vm_l2_tlb_ports', '1',
        '-gpgpu_vm_l2_tlb_lookup_latency', '80',
        '-gpgpu_vm_translation_mshr_entries', '32',
        '-gpgpu_vm_pwq_entries', '32',
        '-gpgpu_vm_walkers', '16',
        '-gpgpu_vm_ptw_mode', '1',
        '-gpgpu_vm_pt_levels', '4',
        '-gpgpu_vm_virtual_address_bits', '49',
        '-gpgpu_vm_pwc_mode', '1',
        '-gpgpu_vm_pwc_entries', '128',
        '-gpgpu_vm_pwc_lookup_latency', '1',
    ]


def matrix_points(kind: str) -> list[tuple[str, str, int]]:
    if kind == 'mechanism':
        return [(cfg, semantic, latency)
                for cfg in ('A1_CONTROL', 'A8', 'A32', 'A32_W8')
                for semantic in ('LEGACY', 'V1', 'V2R1')
                for latency in (10, 0)]
    if kind == 'control-m2-legacy':
        return [('M2', 'LEGACY', 10), ('M2', 'LEGACY', 0)]
    return [
        ('M1', 'V1', 10), ('M1', 'V2R1', 10),
        ('M2', 'V1', 10), ('M2', 'V2R1', 10),
    ]


def run_point(kind: str, cfg: str, semantic: str, latency: int, timeout_s: int,
              overwrite: bool) -> dict[str, object]:
    prefix = 'mechanism' if kind == 'mechanism' else 'control'
    run_dir = RUNTIME / f'{prefix}_{cfg}_{semantic}_{latency}_80'
    rc_file = run_dir / 'rc.txt'
    if not overwrite and rc_file.is_file() and rc_file.read_text().strip() == '0':
        return {'point': run_dir.name, 'rc': 0, 'status': 'SKIPPED_EXISTING_PASS'}
    run_dir.mkdir(parents=True, exist_ok=True)
    bundle = MECHANISM_BUNDLE if kind == 'mechanism' else CONTROL_BUNDLE / 'pairs'
    src = bundle / cfg / 'raw'
    traces = run_dir / 'traces'
    if traces.exists():
        shutil.rmtree(traces)
    shutil.copytree(src, traces, symlinks=True)

    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH', '')}"
    for key in (
        'GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH',
        'GPGPUSIM_READY_APPLICATION_V2',
        'GPGPUSIM_AWMA_CROSSCAL_DIAGNOSTICS',
        'GPGPUSIM_AWMA_ACCESSQ_CARDINALITY_DIAGNOSTICS',
    ):
        env.pop(key, None)
    if semantic in ('V1', 'V2R1'):
        env['GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH'] = '1'
    if semantic == 'V2R1':
        env['GPGPUSIM_READY_APPLICATION_V2'] = '1'
    env['GPGPUSIM_VM_COVERAGE_KERNEL_UID'] = '2'
    env['GPGPUSIM_READY_APPLICATION_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_AWMA_CROSSCAL_DIAGNOSTICS'] = '1'
    if kind == 'mechanism':
        env['GPGPUSIM_AWMA_ACCESSQ_CARDINALITY_DIAGNOSTICS'] = '1'

    cmd = [str(BINARY), '-config', str(CONFIG), '-trace', 'traces/kernelslist.g']
    cmd += trace_args()
    cmd += overlay_args(latency)
    (run_dir / 'command.json').write_text(json.dumps({'argv': cmd, 'environment': {
        k: env.get(k) for k in sorted(env) if k.startswith('GPGPUSIM_')
    }}, indent=2, sort_keys=True) + '\n')
    (run_dir / 'start_utc.txt').write_text(utc_now() + '\n')
    start = time.monotonic()
    with (run_dir / 'run.log').open('w') as out, (run_dir / 'run.stderr').open('w') as err:
        try:
            proc = subprocess.run(cmd, cwd=run_dir, env=env, stdout=out, stderr=err,
                                  timeout=timeout_s, check=False)
            rc = proc.returncode
            status = 'PASS' if rc == 0 else 'NONZERO_EXIT'
        except subprocess.TimeoutExpired:
            rc = 124
            status = 'TIMEOUT'
    (run_dir / 'end_utc.txt').write_text(utc_now() + '\n')
    rc_file.write_text(f'{rc}\n')
    (run_dir / 'wall_seconds.txt').write_text(f'{time.monotonic() - start:.6f}\n')
    return {'point': run_dir.name, 'rc': rc, 'status': status}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('kind', choices=('mechanism', 'control-sentinels', 'control-m2-legacy'))
    ap.add_argument('--workers', type=int, default=24)
    ap.add_argument('--timeout-seconds', type=int, default=1200)
    ap.add_argument('--overwrite', action='store_true')
    args = ap.parse_args()
    points = matrix_points(args.kind)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_point, args.kind, *p, args.timeout_seconds, args.overwrite)
                   for p in points]
        for f in concurrent.futures.as_completed(futures):
            result = f.result()
            results.append(result)
            print(json.dumps(result, sort_keys=True), flush=True)
    results.sort(key=lambda x: str(x['point']))
    (RUNTIME / f'{args.kind}_launcher_results.json').write_text(
        json.dumps(results, indent=2, sort_keys=True) + '\n')
    return 0 if all(r['rc'] == 0 for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
