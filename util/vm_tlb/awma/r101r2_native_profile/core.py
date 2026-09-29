#!/usr/bin/env python3
"""Accepted S128 source paths and pre-frozen author-listed launch configurations."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import torch
from himuon.optimizers.himuon import HiMuon
from himuon.triton_kernels import ns5_smem
from himuon.triton_kernels.XXT import XXT_kernel
from himuon.triton_kernels.ba_plus_cAA import ba_plus_cAA_kernel
from himuon.triton_kernels.fused_bmm_add import bmm_add_kernel
from himuon.triton_kernels.ns5_smem import ns5_smem_kernel

ROOT = Path('/data/c16/awma/r101r2_s128_native_profile_20260929')
R101 = Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
PAYLOAD = R101 / 'raw/discovery_tiles_T128.pt'
PAYLOAD_SHA = '09358f3f21265a9c3a8cdd9681efdaa93a06db7c8d1e1afdbb017e60f0e85544'


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def sha_tensor(value: torch.Tensor) -> str:
    return hashlib.sha256(value.detach().contiguous().view(torch.uint8).cpu().numpy().tobytes()).hexdigest()


def freeze_author_configs() -> dict:
    frozen = {}
    chosen = [config for config in ns5_smem_kernel.configs
              if config.num_warps == 8 and config.num_stages == 2]
    assert len(chosen) == 1
    ns5_smem_kernel.configs = chosen
    frozen['F128_NS5'] = {'num_warps': 8, 'num_stages': 2,
                          'grid': '581,1,1', 'block': '256,1,1'}
    for name, kernel in (('K128_XXT', XXT_kernel), ('K128_BA', ba_plus_cAA_kernel)):
        candidates = [config for config in kernel.configs
                      if config.kwargs['BLOCK_SIZE_M'] == 64
                      and config.kwargs['BLOCK_SIZE_N'] == 64
                      and config.kwargs['BLOCK_SIZE_K'] == 64
                      and config.num_warps == 4 and config.num_stages == 3]
        assert len(candidates) == 1
        kernel.configs = candidates
        frozen[name] = {'kwargs': dict(candidates[0].kwargs),
                        'num_warps': 4, 'num_stages': 3,
                        'grid': '2324,1,1', 'block': '128,1,1'}
    candidates = [config for config in bmm_add_kernel.configs
                  if config.kwargs['BLOCK_SIZE_M'] == 128
                  and config.kwargs['BLOCK_SIZE_N'] == 128
                  and config.kwargs['BLOCK_SIZE_K'] == 32
                  and config.num_warps == 4 and config.num_stages == 4]
    assert len(candidates) == 1
    bmm_add_kernel.configs = candidates
    frozen['K128_BMM_ADD'] = {'kwargs': dict(candidates[0].kwargs),
                              'num_warps': 4, 'num_stages': 4,
                              'grid': '1,581,1', 'block': '128,1,1'}
    frozen['authority'] = 'first author-listed configs matching accepted R101 graph family/grid/block; frozen before NCU and without counter or timing feedback'
    return frozen


def load_input_and_reference() -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    assert sha_file(PAYLOAD) == PAYLOAD_SHA
    receipt = json.loads((R101 / 'R101_TILE_INPUT_RECEIPT_DISCOVERY.json').read_text())
    assert receipt['tiles']['128']['payload_sha256'] == PAYLOAD_SHA
    cpu = torch.load(PAYLOAD, weights_only=True, map_location='cpu')
    assert tuple(cpu.shape) == (581, 128, 128) and cpu.dtype == torch.bfloat16
    reference = torch.load(R101 / 'raw/discovery_numerical_outputs.pt',
                           weights_only=True, map_location='cpu')
    assert set(('F128', 'K128')).issubset(reference)
    return cpu.to('cuda:0'), {arm: reference[arm].to('cuda:0') for arm in ('F128', 'K128')}


def apply(arm: str, x: torch.Tensor) -> torch.Tensor:
    if arm == 'F128':
        return ns5_smem(x, persistent=False)
    assert arm == 'K128'
    return HiMuon._newton_schulz_3kernel(x, steps=5)


def capture(arm: str, x: torch.Tensor, expected: torch.Tensor) -> tuple[torch.cuda.CUDAGraph, torch.Tensor, dict]:
    side = torch.cuda.Stream()
    side.wait_stream(torch.cuda.current_stream())
    with torch.cuda.stream(side), torch.no_grad():
        for _ in range(3):
            apply(arm, x)
    side.synchronize()
    graph = torch.cuda.CUDAGraph()
    with torch.cuda.graph(graph, stream=side), torch.no_grad():
        output = apply(arm, x)
    graph.replay(); torch.cuda.synchronize()
    accepted_allclose = bool(torch.allclose(output, expected, rtol=1e-2, atol=1e-2))
    finite = bool(torch.isfinite(output).all())
    frozen = output.detach().clone()
    old = x[0, 0, 0].clone()
    x[0, 0, 0] = old + 1.0
    graph.replay(); torch.cuda.synchronize()
    changed = not bool(torch.equal(output, frozen))
    x[0, 0, 0] = old
    graph.replay(); torch.cuda.synchronize()
    restored = bool(torch.allclose(output, frozen, rtol=1e-2, atol=1e-2))
    assert accepted_allclose and finite and changed and restored
    receipt = {'arm': arm, 'accepted_output_tolerance_pass': accepted_allclose,
               'finite': finite, 'input_perturbation_changed_output': changed,
               'input_restoration_matches': restored,
               'graph_output_sha256': sha_tensor(output),
               'accepted_reference_sha256': sha_tensor(expected),
               'input_device_pointer_hex': hex(x.data_ptr()),
               'graph_output_pointer_hex': hex(output.data_ptr()),
               'accepted_tolerance': {'rtol': 1e-2, 'atol': 1e-2}}
    return graph, output, receipt
