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

STAGE = 'AWMA_C1_OPPORTUNITY_PORTABILITY_PAIR_A_V1'
REPO = Path('/root/workspace/accel-sim-framework-awma-c1-opportunity-portability-pair-a-v1')
RUNTIME = Path('/root/awma_c1_opportunity_portability_pair_a_v1_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_c1_opportunity_portability_pair_a_v1/raw')
CONFIG = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
QUALIFICATION = RUNTIME / 'baseline_qualification.json'
MODES = {
    'baseline': {
        'binary': RUNTIME / 'baseline/bin/unified_accel-sim.out',
        'lib': RUNTIME / 'baseline/lib',
        'label': 'OFF',
        'binary_sha': 'a866c219b7d71a3075e032c9179bcd679074d6f2e9f1750b435170aabb413b24',
    },
    'candidate': {
        'binary': RUNTIME / 'candidate/bin/unified_accel-sim.out',
        'lib': RUNTIME / 'candidate/lib',
        'label': 'NONBLOCKING_SHARE',
        'binary_sha': 'fa4346fcb4b4bddcf493606b7ce3e87ccd3e6241c26258f62c2c0cb79d4cda47',
    },
}
TARGETS = {
    'A1': {
        'scenario': 'S2', 'decode_step': 16,
        'target_id': 'A1', 'producer_global_navigation': 16828,
        'producer_selector_ordinal': 1097,
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/runtime_identity_bridge_batch1_20260924/A1_formal/raw/kernel-16828-ctx_0x608ad97ab300.traceg.xz'),
        'payload_sha': '49f83c02fbb01dcc9167c6790271103e98d42f318c0344b5f26b8433b704d099',
        'index_sha': 'c3537cc9d89d73c30e1f416fd5c61b07e10059d8cb7b18b250ef13cf79b6d210',
        'identity': Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/runtime_identity_bridge_batch1_20260924/A1_formal/IDENTITY.json'),
    },
    'A2': {
        'scenario': 'T8192', 'decode_step': 16,
        'target_id': 'A2', 'producer_global_navigation': 16828,
        'producer_selector_ordinal': 1097,
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/runtime_identity_bridge_batch1_20260924/A2_formal/raw/kernel-16828-ctx_0x573505e282b0.traceg.xz'),
        'payload_sha': 'c8135003bae105108707ab6b024ca56e50146df88d1692068d92e99511ada2ca',
        'index_sha': 'db6427e3ab7ece5f07791732ddde2f7f6c696b26112593eea61177a7f637eeb1',
        'identity': Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/runtime_identity_bridge_batch1_20260924/A2_formal/IDENTITY.json'),
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


def validate_input(target: str) -> tuple[Path, str, dict[str, object]]:
    spec = TARGETS[target]
    payload = spec['payload']
    identity_path = spec['identity']
    assert isinstance(payload, Path) and isinstance(identity_path, Path)
    if sha(payload) != spec['payload_sha']:
        raise RuntimeError(f'{target}: traceg SHA authority mismatch')
    identity = json.loads(identity_path.read_text())
    expected = {
        'scientific_target_id': 'STR_8bc741e5debc',
        'scenario': spec['scenario'], 'decode_step': spec['decode_step'],
        'phase': 'DECODE', 'grid': '224,1,1', 'block': '16,4,1',
        'accepted_recurrence': 'STABLE_24',
        'producer_global_navigation': spec['producer_global_navigation'],
        'producer_selector_ordinal': spec['producer_selector_ordinal'],
    }
    for key, value in expected.items():
        if identity.get(key) != value:
            raise RuntimeError(
                f'{target}: identity mismatch {key}={identity.get(key)!r}')
    subprocess.run(['xz', '-t', str(payload)], check=True)
    index = f'{payload.name}\n'
    index_sha = hashlib.sha256(index.encode()).hexdigest()
    if index_sha != spec['index_sha']:
        raise RuntimeError(f'{target}: runner/index authority mismatch')
    return payload, index_sha, identity


def prepare_traces(run_dir: Path, payload: Path) -> None:
    traces = run_dir / 'traces'
    if traces.exists():
        shutil.rmtree(traces)
    traces.mkdir(parents=True)
    (traces / payload.name).symlink_to(payload)
    (traces / 'kernelslist.g').write_text(f'{payload.name}\n')


def qualified_targets() -> set[str]:
    if not QUALIFICATION.is_file():
        raise RuntimeError('candidate phase requires baseline_qualification.json')
    receipt = json.loads(QUALIFICATION.read_text())
    if receipt.get('stage') != STAGE:
        raise RuntimeError('baseline qualification stage mismatch')
    return {target for target, row in receipt['targets'].items()
            if row.get('status') == 'PASS'}


def run_point(target: str, mode: str, timeout: int,
              overwrite: bool) -> dict[str, object]:
    mode_spec = MODES[mode]
    label = mode_spec['label']
    run_name = f'{target}_{label}_10_80'
    run_dir = DURABLE / run_name
    rc_path = run_dir / 'rc.txt'
    if not overwrite and rc_path.is_file() and rc_path.read_text().strip() == '0':
        return {'point': run_name, 'rc': 0, 'status': 'SKIPPED_EXISTING_PASS'}
    payload, index_sha, identity = validate_input(target)
    binary = mode_spec['binary']
    core_lib = mode_spec['lib']
    assert isinstance(binary, Path) and isinstance(core_lib, Path)
    if sha(binary) != mode_spec['binary_sha']:
        raise RuntimeError(f'{mode}: frozen binary SHA mismatch')
    run_dir.mkdir(parents=True, exist_ok=True)
    prepare_traces(run_dir, payload)
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = f"{core_lib}:{env.get('LD_LIBRARY_PATH', '')}"
    for key in (
        'GPGPUSIM_READY_APPLICATION_V2',
        'GPGPUSIM_AWMA_TRANSLATION_CANDIDATE',
        'GPGPUSIM_AWMA_SHARE_ABLATION',
        'GPGPUSIM_AWMA_SHARE_DELIVERY_SLOTS',
        'GPGPUSIM_AWMA_SHARE_MIN_COHORT_SIZE',
        'GPGPUSIM_AWMA_NONBLOCKING_CAUSAL_ABLATION',
        'GPGPUSIM_AWMA_OWNER_WAIT_DIAGNOSTICS',
        'GPGPUSIM_AWMA_CROSSCAL_DIAGNOSTICS',
        'GPGPUSIM_AWMA_ACCESSQ_CARDINALITY_DIAGNOSTICS',
    ):
        env.pop(key, None)
    env['GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH'] = '1'
    if mode == 'candidate':
        env['GPGPUSIM_AWMA_TRANSLATION_CANDIDATE'] = \
            'nonblocking_opportunistic_share'
        env['GPGPUSIM_AWMA_MECHANISM_DIAGNOSTICS'] = '1'
        env['GPGPUSIM_AWMA_OWNER_WAIT_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_VM_COVERAGE_KERNEL_UID'] = '1'
    env['GPGPUSIM_READY_APPLICATION_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS'] = '1'
    cmd = [str(binary), '-config', str(CONFIG), '-trace', 'traces/kernelslist.g']
    cmd += trace_args() + overlay()
    receipt = {
        'stage': STAGE,
        'phase': 'PHASE_1_OFF_QUALIFICATION' if mode == 'baseline'
                 else 'PHASE_2_FROZEN_CANDIDATE',
        'capture_authority': 'c8549227a7c581a6f32c1fb63087ea117134fddc',
        'frozen_mechanism_authority':
            'c0602ee06e647d9a3cf84b0adbb8d98075021f99',
        'target': target, 'mode': label, 'vm_config': '10/80',
        'scientific_target_id': identity['scientific_target_id'],
        'scenario': identity['scenario'], 'decode_step': identity['decode_step'],
        'grid': identity['grid'], 'block': identity['block'],
        'recurrence': identity['accepted_recurrence'],
        'argv': cmd,
        'environment': {key: env.get(key) for key in sorted(env)
                        if key.startswith('GPGPUSIM_')},
        'binary_sha256': sha(binary), 'core_library_sha256': sha(core_lib / 'libcudart.so'),
        'config_sha256': sha(CONFIG),
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
    return {'point': run_name, 'rc': rc, 'status': status}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('baseline', 'candidate'))
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--timeout-seconds', type=int, default=21600)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.workers <= 2:
        parser.error('holdout runner permits one or two workers only')
    targets = ('A1', 'A2')
    if args.phase == 'candidate':
        passed = qualified_targets()
        missing = set(targets) - passed
        if missing:
            raise RuntimeError(
                f'candidate forbidden for unqualified targets: {sorted(missing)}')
    DURABLE.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_point, target, args.phase,
                               args.timeout_seconds, args.overwrite)
                   for target in targets]
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
