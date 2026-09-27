#!/usr/bin/env python3
"""CPU-only exact input, producer, and full-five-step scope preregistration."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path('/data/c16/awma/r101_transient_l2_sim_capture_20260927')
WORKTREE = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-transient-l2-sim-capture-109-v1')
R101 = Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
PARENT = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-producer-authority-v1')
TRACER = WORKTREE / 'util/tracer_nvbit/route_b_1771'
POST = Path('/data/c16/awma/storage_sidelane_v1/producer_5143/bin/post-traces-processing_5143')
VALIDATOR = Path('/data/c16/awma/simcompat-v2/q05_routeb_basedelta_canary_20260916T154104Z/hotfix_fb5d0b_admission/traceg_grammar_smoke_fb5d0b')


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def write(name: str, value: object) -> None:
    (ROOT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def main() -> None:
    assert subprocess.check_output(['git', '-C', str(WORKTREE), 'rev-parse', 'HEAD'], text=True).strip() == '6533872601bb81dae1475b35d365f9dbe418cb23'
    assert subprocess.check_output(['git', '-C', str(PARENT), 'rev-parse', 'HEAD'], text=True).strip() == '5143b4e10aaf2fc47bb60492155d2464b0b726fd'
    payload = R101 / 'raw/discovery_tiles_T512.pt'
    assert sha(payload) == '1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234'
    assert sha(POST) == 'db0dec8aa8af92476d05c4f27343e3ed70098f4f16bcc6f20cd7ac4c9d2fb10e'
    assert sha(VALIDATOR) == '135761ac8e10a7fb6c98a3413cd477602d84b164a778c5d4f2a1bfb517be5b37'
    parent_format = PARENT / 'util/tracer_nvbit/route_b_1771/route_b_raw_formatter.hpp'
    assert sha(parent_format) == sha(TRACER / 'route_b_raw_formatter.hpp')
    audit = json.loads((ROOT / 'raw/audit/DRIVER_AUDIT.json').read_text())
    assert audit['normalization_bitwise'] and audit['output_bitwise_with_author']
    assert audit['output_sha256'] == '36aaed3f8360aa099301ae1d705bc2e6ab5ba61586adaf7ead93ecab808dc1b0'
    input_binding = {
        'sim_input_id': 'SIM_INPUT_R101_L512_TRANSIENT_V1',
        'relation_to_r101': 'EXACT_SCIENTIFIC_PAYLOAD_NEW_SIM_CAPTURE',
        'accepted_payload_id': 'R101_DISCOVERY_L512_ACCEPTED_PAYLOAD',
        'payload_path': str(payload), 'payload_sha256': sha(payload),
        'payload_shape': [44, 512, 512], 'dtype': 'bfloat16',
        'model': 'Qwen/Qwen2.5-0.5B-Instruct',
        'model_revision': '7ae557604adf67be50417f59c2c2f167def9a775',
        'source_repository': 'tang0389/himuon',
        'source_commit': 'af89eda9a0176effed99e1fe19cc1f8a1a2c9588',
        'accepted_r101_commit': 'cfbe6503585fa1b10d979db5d26fb9be3a80e563',
        'accepted_r101r1_commit': '422faf4d8fcdb5ac49068dcf19a6e783954a29a8',
        'accepted_output_sha256': audit['output_sha256'],
        'gradient_regeneration': False, 'new_model_download': False,
    }
    write('ACCEPTED_INPUT_BINDING.json', input_binding)
    src = TRACER / 'route_b_tracer.cu'
    tracer = {
        'parent_producer_commit': '5143b4e10aaf2fc47bb60492155d2464b0b726fd',
        'parent_route_b_source_sha256': sha(PARENT / 'util/tracer_nvbit/route_b_1771/route_b_tracer.cu'),
        'this_multi_mode_source_sha256': sha(src),
        'formatter_unchanged_sha256': sha(parent_format),
        'injection_source_sha256': sha(TRACER / 'accelsim_instrument_inst.cu'),
        'new_multi_binary_sha256': sha(ROOT / 'bin/route_b_r101_multi.so'),
        'accepted_parent_binary_sha256': sha(Path('/data/c16/awma/storage_sidelane_v1/producer_5143/bin/route_b_5143.so')),
        'postprocessor_sha256': sha(POST), 'postprocessor_path': str(POST),
        'validator_sha256': sha(VALIDATOR), 'validator_path': str(VALIDATOR),
        'nvbit_version': '1.7.7.1',
        'nvbit_root': '/data/c16/env/nvbit-1.7.7.1/core',
        'cuda_toolkit': '/usr/local/cuda-12.8',
        'gpu_target': 'RTX4080 SM89',
        'opt_in_extension': 'ROUTE_B_MULTI_SELECTED_COUNT + cuProfilerStart/Stop ROI; default single-kernel behavior unchanged',
        'trace_grammar_change': False,
        'formatter_selftest': (ROOT / 'logs/formatter_selftest.stdout.log').read_text().strip(),
    }
    write('TRACER_SOURCE_AND_BUILD_RECEIPT.json', tracer)
    free = shutil.disk_usage(ROOT).free
    scope = {
        'scope_id': 'R101_L512_FULL5_WITH_NORMALIZATION_V1',
        'formal_scope_preferred': 'normalization + five consecutive complete XXT/BA/BMM-add iterations',
        'fallback_only_if_volume_unsafe': 'R101_L512_NS_CONTEXT2_V1',
        'fallback_definition': 'first two consecutive complete iterations, first context and second later simulator ROI',
        'fallback_not_chosen_before_size_evidence': True,
        'tile_count': 44, 'tile_edge': 512, 'dtype': 'bfloat16',
        'ns_steps': 5, 'coefficients': [3.4445, -4.7750, 2.0315],
        'arithmetic_order_each_iteration': ['XXT', 'ba_plus_cAA', 'fused_bmm_add'],
        'buffer_regions': ['A', 'B', 'X0', 'X1'],
        'expected_logical_buffer_bytes_each': 23068672,
        'roi_control': 'cudaProfilerStart immediately before normalization, cudaProfilerStop after fifth BMM-add',
        'selector_regex_full': '.*',
        'selected_count': 'freeze from launch census before FORMAL',
        'driver_warmups_outside_roi': 3,
        'xxt_ba_launch_config_freeze': {
            'authority': 'accepted R101R1 L512 XXT and BA grid=2816,1,1 block=128,1,1 plus pinned HiMuon author config list',
            'functions': ['XXT_kernel', 'ba_plus_cAA_kernel'],
            'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 64,
            'GROUP_SIZE_M': 8, 'LOWER_UPPER': 1, 'num_stages': 3, 'num_warps': 4,
            'source_math_unchanged': True, 'not_performance_tuned': True,
        },
        'per_run_raw_cap_bytes': 32 * 1024**3,
        'time_cap_seconds': 7200,
        'free_bytes_before_capture': free,
        'output_contract_sha256': input_binding['accepted_output_sha256'],
        'no_performance_selected_roi': True,
    }
    write('CAPTURE_SCOPE_PREREGISTRATION.json', scope)
    print(json.dumps({'input_sha256': input_binding['payload_sha256'],
                      'tracer_source_sha256': tracer['this_multi_mode_source_sha256'],
                      'free_bytes': free, 'scope': scope['scope_id']}, sort_keys=True))


if __name__ == '__main__':
    main()
