#!/usr/bin/env python3
"""Exact author arithmetic with an optional last-use L2 discard control."""
from __future__ import annotations

import ctypes
import hashlib
import json
from pathlib import Path

import torch
from himuon.optimizers.himuon import HiMuon
from himuon.triton_kernels import XXT, ba_plus_cAA, fused_bmm_add

ROOT = Path('/data/c16/awma/r101_l2_lifetime_control_v1r1_20260927')
R101 = Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
AUTHOR_COMMIT = 'af89eda9a0176effed99e1fe19cc1f8a1a2c9588'
COEFFICIENTS = (3.4445, -4.7750, 2.0315)


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def load_tiles(fixture: str, edge: int) -> torch.Tensor:
    assert fixture in ('discovery', 'holdout') and edge in (128, 512)
    receipt = json.loads((R101 / f'R101_TILE_INPUT_RECEIPT_{fixture.upper()}.json').read_text())
    assert receipt['author_source_commit'] == AUTHOR_COMMIT
    record = receipt['tiles'][str(edge)]
    path = R101 / 'raw' / f'{fixture}_tiles_T{edge}.pt'
    assert sha_file(path) == record['payload_sha256']
    value = torch.load(path, map_location='cpu', weights_only=True)
    assert tuple(value.shape) == tuple(record['shape'])
    assert value.dtype == torch.bfloat16 and value.is_contiguous()
    return value.to('cuda:0')


class Discard:
    def __init__(self) -> None:
        self.library = ctypes.CDLL(str(ROOT / 'build/libdiscard.so'))
        fn = self.library.r101r1_discard
        fn.argtypes = (ctypes.c_void_p, ctypes.c_ulonglong, ctypes.c_ulonglong)
        fn.restype = ctypes.c_int
        self.fn = fn

    def __call__(self, tensor: torch.Tensor) -> None:
        assert tensor.is_cuda and tensor.is_contiguous()
        pointer = tensor.data_ptr()
        size = tensor.numel() * tensor.element_size()
        assert pointer % 128 == 0 and size % 128 == 0
        stream = torch.cuda.current_stream(tensor.device).cuda_stream
        status = self.fn(pointer, size, stream)
        if status != 0:
            raise RuntimeError(f'discard launch failed: {status}')


@torch.compile(dynamic=False, fullgraph=True)
def _author_normalization(G: torch.Tensor) -> torch.Tensor:
    X = G.bfloat16()
    if G.size(-2) > G.size(-1):
        X = X.transpose(-2, -1)
    X = X / (X.norm(dim=(-2, -1), keepdim=True) + 1e-7)
    return X.contiguous()


def run_map(G: torch.Tensor, discard: Discard | None = None) -> torch.Tensor:
    """Follow pinned HiMuon._newton_schulz_3kernel, inserting only dead-line hints."""
    assert G.ndim == 3 and G.shape[-1] == G.shape[-2]
    assert G.dtype == torch.bfloat16
    original_dtype = G.dtype
    X = _author_normalization(G)
    A = torch.empty((*X.shape[:-1], X.size(-2)), device=X.device, dtype=X.dtype)
    B = torch.empty_like(A)
    C = torch.empty_like(X)
    a, b, c = COEFFICIENTS
    for _ in range(5):
        XXT(X, out=A)
        ba_plus_cAA(A, alpha=c, beta=b, out=B)
        if discard is not None:
            discard(A)  # dead after BA; next iteration XXT completely overwrites A
        fused_bmm_add(B, X, a, out=C)
        if discard is not None:
            discard(B)  # dead after BMM-add; next BA completely overwrites B
            discard(X)  # old X is dead; its buffer becomes a future output C
        X, C = C, X
    return X.to(original_dtype)  # final live X is never discarded


def author_reference(G: torch.Tensor) -> torch.Tensor:
    return HiMuon._newton_schulz_3kernel(G, steps=5)


def capture(G: torch.Tensor, discard: Discard | None) -> tuple[torch.cuda.CUDAGraph, torch.Tensor]:
    side = torch.cuda.Stream()
    side.wait_stream(torch.cuda.current_stream())
    with torch.cuda.stream(side), torch.no_grad():
        for _ in range(3):
            run_map(G, discard)
    side.synchronize()
    graph = torch.cuda.CUDAGraph()
    with torch.cuda.graph(graph, stream=side), torch.no_grad():
        output = run_map(G, discard)
    graph.replay()
    torch.cuda.synchronize()
    return graph, output
