#!/usr/bin/env python3
"""Accepted R101 L512 payload, fixed five-step HiMuon map, address-frozen capture."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import torch
from himuon.optimizers.himuon import HiMuon
from himuon.triton_kernels import XXT, ba_plus_cAA, fused_bmm_add
from himuon.triton_kernels.XXT import XXT_kernel
from himuon.triton_kernels.ba_plus_cAA import ba_plus_cAA_kernel

ROOT = Path('/data/c16/awma/r101_transient_l2_sim_capture_20260927')
R101 = Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
PAYLOAD = R101 / 'raw/discovery_tiles_T512.pt'
PAYLOAD_SHA = '1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234'
OUTPUT_SHA = '36aaed3f8360aa099301ae1d705bc2e6ab5ba61586adaf7ead93ecab808dc1b0'


def freeze_author_arithmetic_launch_configs() -> dict:
    # Accepted R101R1 L512 XXT and BA both use grid 2816,1,1 / block 128,1,1.
    # Pick the first author-listed config matching those strata, before any
    # profile.  No Triton kernel source or NS mathematics is modified.
    frozen = {}
    for name, kernel in (('XXT', XXT_kernel), ('BA', ba_plus_cAA_kernel)):
        eligible = [config for config in kernel.configs
                    if config.kwargs['BLOCK_SIZE_M'] == 64
                    and config.kwargs['BLOCK_SIZE_N'] == 64
                    and config.num_warps == 4]
        assert eligible
        selected = eligible[0]
        assert selected.kwargs['BLOCK_SIZE_K'] == 64
        assert selected.num_stages == 3
        kernel.configs = [selected]
        frozen[name] = {'kwargs': dict(selected.kwargs),
                        'num_stages': selected.num_stages,
                        'num_warps': selected.num_warps}
    frozen['authority'] = 'pinned HiMuon get_polar_autotune_configs first accepted-grid/block-compatible entry'
    return frozen


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def sha_tensor(value: torch.Tensor) -> str:
    return hashlib.sha256(value.detach().contiguous().view(torch.uint8).cpu().numpy().tobytes()).hexdigest()


@torch.compile(dynamic=False, fullgraph=True)
def normalization_into(G: torch.Tensor, X0: torch.Tensor) -> torch.Tensor:
    X = G.bfloat16()
    X = X / (X.norm(dim=(-2, -1), keepdim=True) + 1e-7)
    X0.copy_(X)
    return X0


@torch.compile(dynamic=False, fullgraph=True)
def accepted_style_normalization(G: torch.Tensor) -> torch.Tensor:
    X = G.bfloat16()
    X = X / (X.norm(dim=(-2, -1), keepdim=True) + 1e-7)
    return X.contiguous()


def run_five(G: torch.Tensor, X0: torch.Tensor, X1: torch.Tensor,
             A: torch.Tensor, B: torch.Tensor, with_roi: bool) -> torch.Tensor:
    if with_roi:
        status = torch.cuda.cudart().cudaProfilerStart()
        if status != 0:
            raise RuntimeError(f'cudaProfilerStart failed: {status}')
    current = normalization_into(G, X0)
    next_ = X1
    for _ in range(5):
        XXT(current, out=A)
        ba_plus_cAA(A, alpha=2.0315, beta=-4.7750, out=B)
        fused_bmm_add(B, current, 3.4445, out=next_)
        current, next_ = next_, current
    if with_roi:
        torch.cuda.synchronize()
        status = torch.cuda.cudart().cudaProfilerStop()
        if status != 0:
            raise RuntimeError(f'cudaProfilerStop failed: {status}')
    return current


def binding(G: torch.Tensor, X0: torch.Tensor, X1: torch.Tensor,
            A: torch.Tensor, B: torch.Tensor) -> dict:
    regions = {}
    for name, tensor, relation in (
        ('A', A, 'XXT output / BA input'),
        ('B', B, 'BA output / BMM-add input'),
        ('X0', X0, 'normalized accepted payload / ping-pong X'),
        ('X1', X1, 'BMM-add output C / ping-pong X'),
    ):
        assert tensor.is_contiguous() and tensor.dtype == torch.bfloat16
        pointer = tensor.data_ptr()
        size = tensor.numel() * tensor.element_size()
        assert size == 23068672 and pointer % 128 == 0
        regions[name] = {'base_device_address': pointer, 'base_hex': hex(pointer),
                         'bytes': size, 'end_exclusive_hex': hex(pointer + size),
                         'aligned_128_bytes': True, 'shape': list(tensor.shape),
                         'stride_elements': list(tensor.stride()), 'dtype': 'bfloat16',
                         'allocation_identity': name + '_stable_preallocated',
                         'relation': relation}
    spans = sorted((value['base_device_address'], value['base_device_address'] + value['bytes'])
                   for value in regions.values())
    assert all(spans[index][1] <= spans[index + 1][0] for index in range(len(spans) - 1))
    return {'input_payload_sha256': PAYLOAD_SHA, 'input_device_pointer_hex': hex(G.data_ptr()),
            'regions': regions,
            'A_B_arena_contiguous': B.data_ptr() - A.data_ptr() == A.numel() * A.element_size(),
            'region_map_frozen_before_profiler_start': True}


def main(mode: str, outdir: Path) -> None:
    frozen_arithmetic = freeze_author_arithmetic_launch_configs()
    assert sha_file(PAYLOAD) == PAYLOAD_SHA
    receipt = json.loads((R101 / 'R101_TILE_INPUT_RECEIPT_DISCOVERY.json').read_text())
    assert receipt['tiles']['512']['payload_sha256'] == PAYLOAD_SHA
    G = torch.load(PAYLOAD, weights_only=True, map_location='cpu').to('cuda:0')
    assert G.shape == (44, 512, 512) and G.dtype == torch.bfloat16
    arena = torch.zeros((2, *G.shape), dtype=G.dtype, device=G.device)
    A, B = arena[0], arena[1]
    X0 = torch.empty_like(G)
    X1 = torch.empty_like(G)
    regions = binding(G, X0, X1, A, B)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'BUFFER_REGIONS_RUNTIME.json').write_text(json.dumps(regions, indent=2, sort_keys=True) + '\n')
    with torch.no_grad():
        if mode == 'audit':
            reference_norm = accepted_style_normalization(G)
            control = normalization_into(G, X0)
            norm_bitwise = bool(torch.equal(reference_norm, control))
            accepted = HiMuon._newton_schulz_3kernel(G, steps=5)
            output = run_five(G, X0, X1, A, B, False)
            output_bitwise = bool(torch.equal(output, accepted))
            result = {'mode': mode, 'normalization_bitwise': norm_bitwise,
                      'output_bitwise_with_author': output_bitwise,
                      'output_sha256': sha_tensor(output),
                      'finite': bool(torch.isfinite(output).all()),
                      'frozen_author_arithmetic_config': frozen_arithmetic,
                      'regions': regions}
            (outdir / 'DRIVER_AUDIT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
            print(json.dumps({key: value for key, value in result.items() if key != 'regions'}), flush=True)
            assert norm_bitwise and output_bitwise and result['output_sha256'] == OUTPUT_SHA
            return
        for _ in range(3):
            run_five(G, X0, X1, A, B, False)
        torch.cuda.synchronize()
        output = run_five(G, X0, X1, A, B, True)
        finite = bool(torch.isfinite(output).all())
        output_hash = sha_tensor(output)
        result = {'mode': mode, 'input_sha256': PAYLOAD_SHA,
                  'output_sha256': output_hash, 'accepted_output_sha256': OUTPUT_SHA,
                  'output_exact': output_hash == OUTPUT_SHA, 'finite': finite,
                  'region_map_sha256': sha_file(outdir / 'BUFFER_REGIONS_RUNTIME.json'),
                  'roi_rule': 'cudaProfilerStart before normalization, cudaProfilerStop after fifth BMM-add',
                  'frozen_author_arithmetic_config': frozen_arithmetic,
                  'five_complete_iterations': True}
        (outdir / 'DRIVER_RUN_RECEIPT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        print('R101_L512_NATIVE_INVOCATION_COMPLETE ' + json.dumps(result, sort_keys=True), flush=True)
        assert finite and output_hash == OUTPUT_SHA


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['audit', 'census', 'canary1', 'canary_multi', 'formal'], required=True)
    parser.add_argument('--outdir', type=Path, required=True)
    args = parser.parse_args()
    main(args.mode, args.outdir)
