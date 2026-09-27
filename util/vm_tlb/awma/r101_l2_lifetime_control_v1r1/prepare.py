#!/usr/bin/env python3
"""Offline authority, capability, and preregistration closure for R101R1."""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_l2_lifetime_control_v1r1_20260927')
R101 = Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
WORKTREE = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-l2-lifetime-control-v1r1')
SOURCE = R101 / 'source/himuon'
EXPECTED = {
    'discovery': {
        128: '09358f3f21265a9c3a8cdd9681efdaa93a06db7c8d1e1afdbb017e60f0e85544',
        512: '1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234',
    },
    'holdout': {
        128: 'c80a3fb58fa9d5fbee34215148906c7c37bd620f2994206505518d73b571de28',
        512: '0011efb22ae9ed85d87d53e6814fc708042a928cae6fd305a2b310efc04e3769',
    },
}


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def write(name: str, obj: object) -> None:
    (ROOT / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def main() -> None:
    assert subprocess.check_output(['git', '-C', str(WORKTREE), 'rev-parse', 'HEAD'], text=True).strip() == 'e0e70f0bb247d1b6b6da98cd594d00ecf6dc6abc'
    assert subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'], text=True).strip() == 'af89eda9a0176effed99e1fe19cc1f8a1a2c9588'
    payloads = {}
    for fixture, group in EXPECTED.items():
        receipt = json.loads((R101 / f'R101_TILE_INPUT_RECEIPT_{fixture.upper()}.json').read_text())
        for edge, expected in group.items():
            path = R101 / 'raw' / f'{fixture}_tiles_T{edge}.pt'
            assert sha(path) == expected == receipt['tiles'][str(edge)]['payload_sha256']
            payloads[f'{fixture}_T{edge}'] = {
                'path': str(path), 'sha256': expected,
                'shape': receipt['tiles'][str(edge)]['shape'],
                'tensor_sha256': receipt['tiles'][str(edge)]['tensor_sha256'],
            }
    accepted = json.loads((R101 / 'R101_SOURCE_RECEIPT.json').read_text())
    for rel, expected in accepted['source_sha256'].items():
        assert sha(SOURCE / rel) == expected
    source = WORKTREE / 'util/vm_tlb/awma/r101_l2_lifetime_control_v1r1/discard.cu'
    build = ROOT / 'build'
    device = json.loads((ROOT / 'R101R1_DEVICE_CAPABILITY_RAW.json').read_text())
    assert (device['sm_major'], device['sm_minor']) == (8, 9)
    assert all(device[key] == 0 for key in device if key.startswith('status_'))
    ptx = (build / 'discard.ptx').read_text()
    sass = (build / 'discard.sass.txt').read_text()
    assert 'discard.global.L2' in ptx and 'CCTL.E.RML2' in sass
    capability = {
        'device': device,
        'nvcc_version': (build / 'nvcc_version.txt').read_text().strip(),
        'compile_arch': 'sm_89',
        'ptx_target': '.target sm_89',
        'ptx_opcode': 'discard.global.L2 [ptr], 128',
        'sass_opcode_observed': 'CCTL.E.RML2',
        'runtime_smoke_passed': True,
        'source_sha256': sha(source),
        'ptx_sha256': sha(build / 'discard.ptx'),
        'cubin_sha256': sha(build / 'discard.cubin'),
        'library_sha256': sha(build / 'libdiscard.so'),
        'capability_executable_sha256': sha(build / 'capability'),
        'ptx_spec_url': 'https://docs.nvidia.com/cuda/archive/13.0.0/parallel-thread-execution/index.html',
        'cuda_l2_spec_url': 'https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/l2-cache-control.html',
        'bounded_engineering_repair': 'C printf size_t formatting corrected before scientific execution; no ISA or kernel semantic change',
    }
    write('R101R1_L2_CAPABILITY_RECEIPT.json', capability)
    write('R101R1_BASELINE_IDENTITY.json', {
        'stage': 'AWMA_R101_L2_LIFETIME_CONTROL_REQUALIFICATION_V1R1',
        'accepted_r101_execution_sha': 'cfbe6503585fa1b10d979db5d26fb9be3a80e563',
        'handoff_sha': 'e0e70f0bb247d1b6b6da98cd594d00ecf6dc6abc',
        'author_repository': 'tang0389/himuon',
        'author_commit': accepted['commit'],
        'author_source_sha256': accepted['source_sha256'],
        'model_identity': json.loads((R101 / 'MODEL_IDENTITY_RECEIPT.json').read_text()),
        'input_identity': json.loads((R101 / 'R101_INPUT_RECEIPT.json').read_text()),
        'tile_payloads': payloads,
        'arithmetic': ['normalization', '5x [XXT(X,out=A); ba_plus_cAA(A,out=B); fused_bmm_add(B,X,a,out=C); X,C=C,X]'],
        'coefficients': [3.4445, -4.775, 2.0315],
        'norm_epsilon': 1e-7,
        'new_algorithm_or_model_download': False,
    })
    env_path = R101 / 'ENVIRONMENT_RECEIPT.json'
    write('ENVIRONMENT_RECEIPT.json', {
        'python': sys.version, 'platform': platform.platform(),
        'interpreter': sys.executable,
        'accepted_r101_environment_receipt_sha256': sha(env_path),
        'accepted_r101_environment': json.loads(env_path.read_text()),
        'runtime_reuse': 'read-only accepted R101 environment; isolated R101R1 worktree/build/JIT/TMP/raw',
        'triton_cache': str(ROOT / 'cache/triton'),
        'inductor_cache': str(ROOT / 'cache/inductor'),
        'cuda_cache': str(ROOT / 'cache/cuda'),
        'tmpdir': str(ROOT / 'tmp'),
    })
    write('PREREGISTRATION.json', {
        'stage': 'AWMA_R101_L2_LIFETIME_CONTROL_REQUALIFICATION_V1R1',
        'frozen_before_d1_correctness_and_timing': True,
        'discovery_fixture': 'accepted layer0 discovery T128 and T512 exact payloads',
        'holdout_fixture': 'accepted layer12 holdout T128 and T512 exact payloads, conditional only',
        'arms': ['K128_B0_GRAPH', 'K128_D1_DISCARD_GRAPH', 'L512_B0_GRAPH', 'L512_D1_DISCARD_GRAPH'],
        'arithmetic_unchanged': True,
        'bitwise_d1_b0_required': True,
        'liveness': 'perturb one input element, graph output changes; restore and output returns bitwise',
        'repetitions': {'canary': 1, 'warmup': 2, 'formal': 7},
        'formal_order': 'paired/interleaved B0,D1 on even rep; D1,B0 on odd rep, per shape',
        'primary_gpu_ms': 'CUDA events around complete graph replay; no profiler',
        'material_runtime': '>=5% median speedup and >3x max relative jitter',
        'ncu_metrics': ['dram__bytes_read.sum', 'dram__bytes_write.sum', 'lts__t_bytes.sum', 'sm__cycles_active.sum', 'launch__registers_per_thread', 'launch__shared_mem_per_block'],
        'ncu_new_d1_profile_cap': 2,
        'baseline_ncu_recollect_if_source_or_kernel_identity_not_exact': True,
        'write_reduction_gate': '1-D1_NS_family_DRAM_write/B0_NS_family_DRAM_write; L512 >=50% forbids D2',
        'd2_only_if_d1_l512_write_reduction_below_50pct': True,
        'd2_region': 'A+B if full region fits both set-aside and window; otherwise A only if one full buffer fits; never outcome-selected',
        'd2_persist_hit_ratio': 1.0,
        'd2_persist_hit_property': 'cudaAccessPropertyPersisting',
        'd2_persist_miss_property': 'cudaAccessPropertyNormal',
        'no_parameter_sweep': True,
    })
    (ROOT / 'R101_INHERITANCE.md').write_text(
        '# R101 inheritance\n\nAccepted R101 stays frozen at `cfbe6503585fa1b10d979db5d26fb9be3a80e563`. '
        'R101R1 is an ISA/software boundary test, not a reinterpretation. The same layer0 discovery and '
        'layer12 holdout payload files, their exact SHA256 values, pinned HiMuon source and accepted '
        'Qwen model/input authority are listed in `R101R1_BASELINE_IDENTITY.json`. No gradient generation '
        'or model download is performed in R101R1.\n'
    )
    (ROOT / 'R101R1_LIFETIME_CONTRACT.md').write_text(
        '# Dead-value lifetime\n\nOne ordered CUDA stream/graph contains all operations. After '
        '`ba_plus_cAA(A,out=B)` completes, A is dead and the next XXT fully overwrites A. '
        'After `fused_bmm_add(B,X,out=C)` completes, B and old X are dead; next iteration '
        'fully overwrites B and uses old X only as the future C output destination. '
        'D1 discards A immediately after BA and B plus old X immediately after BMM-add, '
        'one 128-byte aligned line per CUDA thread. The final live new-X output is never discarded. '
        'No CPU synchronization occurs in graph capture or timed replay. Same-stream kernel ordering '
        'prevents discard racing the preceding consumer or following producer.\n'
    )
    print(json.dumps({'payloads': payloads, 'capability': capability}, indent=2))


if __name__ == '__main__':
    main()
