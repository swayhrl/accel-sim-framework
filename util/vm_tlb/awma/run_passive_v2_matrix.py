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

STAGE = 'AWMA_PASSIVE_LAST_TRANSLATION_RESULT_FORWARDING_V2'
REPO = Path('/root/workspace/accel-sim-framework-awma-passive-last-translation-result-forwarding-v2')
RUNTIME = Path('/root/awma_passive_last_translation_result_forwarding_v2_runtime')
DURABLE = Path('/root/share/mnt164/huangrulin/awma_passive_last_translation_result_forwarding_v2/raw')
CONFIG = REPO / 'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG = REPO / 'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
QUALIFICATION = RUNTIME / 'off_authority.json'
MODES = {
    'off': {
        'label': 'OFF',
    },
    'v2': {
        'label': 'PASSIVE_V2',
    },
}
BINARY = RUNTIME / 'bin/unified_accel-sim.out'
CORE_LIB = RUNTIME / 'src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release'
TARGETS = {
    'T0': {
        'family': 'PREFILL_FLASH',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native-contiguous-prefix_q05-contiguous-prefix_20260918T022749Z_1fea2d955d1c/traces/kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz'),
        'payload_sha': 'd8fa338f82800f646c8501a6a1d1049afaae213fe0d7f70d4913fcfaa76ba67a',
        'index_sha': 'a8b4ba1cf33f34be345b38908cb39572c0d14972170fd1972b4b080e81154fd5',
    },
    'T1': {
        'family': 'PREFILL_GEMM',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native_prefill-gemm-primary-occ0_20260918T052739Z_01540d931e17/traces/kernel-45-ctx_0x60d38cb72530.traceg.xz'),
        'payload_sha': 'e36178f9a92033cd91f3c1ff4b165321b7958157c7deed2a9aaa4696e7c73e8c',
        'index_sha': 'c9dd68f84606deceb8d7dcece6e35c93750b16bf507ac3666c3adb2a0e0cdc41',
    },
    'T2': {
        'family': 'DECODE_GEMV',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_decode-gemv-primary-step16_20260918T074437Z_b0dfb1af1ae1/traces/kernel-17039-ctx_0x5ddb6907c160.traceg.xz'),
        'payload_sha': 'b87cd6cb6a2bc0f67e17616e26d1bf9091facad242d46a43f5f9c1ac274b6138',
        'index_sha': '2a458d31a945cf11ce465b563582e6ab29292ae692bd3d2acd74bf4e8b5c2c4a',
    },
    'SPLITKV': {
        'family': 'FLASH_FWD_SPLITKV',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_v2-decode-flash-primary-1-step16_20260918T175706Z_891c75aa245e/traces/kernel-17543-ctx_0x5be0856adcb0.traceg.xz'),
        'payload_sha': '282a9b18510bd0aaf54ec528c65bfb39d49b052902c6b87f3b85bb2973096371',
        'index_sha': '59236d6c6746260a3127c8f858270c915e91c9d7959647047a8d44504a984773',
    },
    'COMBINE': {
        'family': 'FLASH_FWD_SPLITKV_COMBINE',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_v2-decode-flash-primary-2-step16_20260918T185037Z_0d352ffacee3/traces/kernel-16813-ctx_0x5c9946e7f280.traceg.xz'),
        'payload_sha': 'd153db1548517f24eebd80c1a5dc48785ab28ace173b2937dd4f7b4a7005dcb9',
        'index_sha': '31b54d9f55ce501a6cb64360c2b1c988e2099b7e97e3fb9945d27d4631dd8da2',
    },
    'A1': {
        'family': 'DECODE_GEMV_PAIR_A_S2_T2048',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/runtime_identity_bridge_batch1_20260924/A1_formal/raw/kernel-16828-ctx_0x608ad97ab300.traceg.xz'),
        'payload_sha': '49f83c02fbb01dcc9167c6790271103e98d42f318c0344b5f26b8433b704d099',
        'index_sha': 'c3537cc9d89d73c30e1f416fd5c61b07e10059d8cb7b18b250ef13cf79b6d210',
    },
    'A2': {
        'family': 'DECODE_GEMV_PAIR_A_T8192',
        'payload': Path('/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/runtime_identity_bridge_batch1_20260924/A2_formal/raw/kernel-16828-ctx_0x573505e282b0.traceg.xz'),
        'payload_sha': 'c8135003bae105108707ab6b024ca56e50146df88d1692068d92e99511ada2ca',
        'index_sha': 'db6427e3ab7ece5f07791732ddde2f7f6c696b26112593eea61177a7f637eeb1',
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


def validate_input(target: str) -> tuple[Path, str]:
    spec = TARGETS[target]
    payload = spec['payload']
    assert isinstance(payload, Path)
    if sha(payload) != spec['payload_sha']:
        raise RuntimeError(f'{target}: traceg SHA authority mismatch')
    subprocess.run(['xz', '-t', str(payload)], check=True)
    index = f'{payload.name}\n'
    index_sha = hashlib.sha256(index.encode()).hexdigest()
    if index_sha != spec['index_sha']:
        raise RuntimeError(f'{target}: runner/index authority mismatch')
    return payload, index_sha


def prepare_traces(run_dir: Path, payload: Path) -> None:
    traces = run_dir / 'traces'
    if traces.exists():
        shutil.rmtree(traces)
    traces.mkdir(parents=True)
    (traces / payload.name).symlink_to(payload)
    (traces / 'kernelslist.g').write_text(f'{payload.name}\n')


def qualified_targets() -> set[str]:
    if not QUALIFICATION.is_file():
        raise RuntimeError('v2 requires off_authority.json')
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
    payload, index_sha = validate_input(target)
    binary = BINARY
    core_lib = CORE_LIB
    if sha(binary) != '8999bd37d08e16b5036fe18ffe5327ba918e13a9b8a4a3102a3fa9d1cf420a01':
        raise RuntimeError('frozen V2 binary SHA mismatch')
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
        'GPGPUSIM_AWMA_PASSIVE_MEMO_OBSERVER',
        'GPGPUSIM_AWMA_BOTTLENECK_OBSERVATORY',
        'GPGPUSIM_AWMA_BOTTLENECK_DOMAINS',
        'GPGPUSIM_AWMA_MECHANISM_DIAGNOSTICS',
    ):
        env.pop(key, None)
    env['GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH'] = '1'
    env['GPGPUSIM_AWMA_PASSIVE_MEMO_OBSERVER'] = '0'
    env['GPGPUSIM_AWMA_BOTTLENECK_OBSERVATORY'] = '1'
    if mode == 'v2':
        env['GPGPUSIM_AWMA_TRANSLATION_CANDIDATE'] = 'passive_last_result'
        env['GPGPUSIM_AWMA_MECHANISM_DIAGNOSTICS'] = '1'
        env['GPGPUSIM_AWMA_OWNER_WAIT_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_VM_COVERAGE_KERNEL_UID'] = '1'
    env['GPGPUSIM_READY_APPLICATION_DIAGNOSTICS'] = '1'
    env['GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS'] = '1'
    cmd = [str(binary), '-config', str(CONFIG), '-trace', 'traces/kernelslist.g']
    cmd += trace_args() + overlay()
    receipt = {
        'stage': STAGE,
        'phase': 'OFF_AUTHORITY_CHECK' if mode == 'off'
                 else 'FROZEN_PASSIVE_V2_DEVELOPMENT',
        'source_freeze_commit': '7f9167f9c97bba64100cafb1dbde9021c1beca0e',
        'holdout_preregistration_commit':
            'd450b2a06a0af18960d81b0ccbb46d047fe6cbae',
        'observability_authority': 'b85d388abe98e5da70b749b52075c33fad7cede4',
        'target': target, 'mode': label, 'vm_config': '10/80',
        'family': TARGETS[target]['family'],
        'performance_mechanism_enabled': mode == 'v2',
        'fixed_capacity': 1,
        'timing_semantics': 'SAME_CYCLE_COMPARE_FORWARD',
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
    parser.add_argument('phase', choices=('off', 'v2'))
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--timeout-seconds', type=int, default=21600)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        parser.error('runner permits one to four workers only')
    targets = ('T0', 'T1', 'T2', 'SPLITKV', 'COMBINE', 'A1', 'A2')
    if args.phase == 'v2':
        passed = qualified_targets()
        missing = set(targets) - passed
        if missing:
            raise RuntimeError(
                f'v2 forbidden for unqualified OFF targets: {sorted(missing)}')
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
