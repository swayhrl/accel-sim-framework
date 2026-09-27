#!/usr/bin/env python3
"""Exact contiguous A/B arena and existing CUDA graph-node L2 policy control."""
from __future__ import annotations

import ctypes

import torch
from himuon.triton_kernels import XXT, ba_plus_cAA, fused_bmm_add

from core import ROOT, COEFFICIENTS, Discard, _author_normalization

_CAPTURE_ARENAS: list[torch.Tensor] = []  # external graph pointers must outlive every replay


class Persistence:
    def __init__(self) -> None:
        lib = ctypes.CDLL(str(ROOT / 'build/libpersist.so'))
        self.lib = lib
        self.set_limit_fn = lib.r101r1_set_persisting_limit
        self.set_limit_fn.argtypes = (ctypes.c_ulonglong, ctypes.POINTER(ctypes.c_ulonglong))
        self.set_limit_fn.restype = ctypes.c_int
        self.attach_fn = lib.r101r1_attach_persisting_to_active_capture
        self.attach_fn.argtypes = (ctypes.c_ulonglong, ctypes.c_void_p,
                                   ctypes.c_ulonglong, ctypes.POINTER(ctypes.c_uint))
        self.attach_fn.restype = ctypes.c_int
        self.reset_fn = lib.r101r1_reset_persisting_lines
        self.reset_fn.argtypes = ()
        self.reset_fn.restype = ctypes.c_int

    def set_limit(self, requested: int) -> int:
        actual = ctypes.c_ulonglong()
        status = self.set_limit_fn(requested, ctypes.byref(actual))
        if status != 0:
            raise RuntimeError(f'cudaDeviceSetLimit/get failed status={status}')
        return actual.value

    def attach_active_capture(self, arena: torch.Tensor) -> int:
        stream = torch.cuda.current_stream(arena.device).cuda_stream
        count = ctypes.c_uint()
        bytes_ = arena.numel() * arena.element_size()
        status = self.attach_fn(stream, arena.data_ptr(), bytes_, ctypes.byref(count))
        if status != 0:
            raise RuntimeError(f'cudaGraphKernelNodeSetAttribute failed status={status}')
        return count.value

    def reset(self) -> None:
        status = self.reset_fn()
        if status != 0:
            raise RuntimeError(f'cudaCtxResetPersistingL2Cache failed status={status}')


def make_arena(x: torch.Tensor) -> torch.Tensor:
    assert x.ndim == 3 and x.shape[1:] == (512, 512) and len(x) == 44
    arena = torch.zeros((2, *x.shape), device=x.device, dtype=x.dtype)
    assert arena.is_contiguous() and arena.data_ptr() % 128 == 0
    assert arena.numel() * arena.element_size() == 46137344
    assert arena[1].data_ptr() - arena[0].data_ptr() == 23068672
    return arena


def run_arena_map(G: torch.Tensor, arena: torch.Tensor,
                  discard: Discard | None = None) -> torch.Tensor:
    X = _author_normalization(G)
    A, B = arena[0], arena[1]
    C = torch.empty_like(X)
    a, b, c = COEFFICIENTS
    for _ in range(5):
        XXT(X, out=A)
        ba_plus_cAA(A, alpha=c, beta=b, out=B)
        if discard is not None:
            discard(A)
        fused_bmm_add(B, X, a, out=C)
        if discard is not None:
            discard(B)
            discard(X)
        X, C = C, X
    return X


def capture_arena(G: torch.Tensor, arena: torch.Tensor,
                  discard: Discard | None,
                  persistence: Persistence | None) -> tuple[torch.cuda.CUDAGraph, torch.Tensor, int]:
    side = torch.cuda.Stream()
    side.wait_stream(torch.cuda.current_stream())
    with torch.cuda.stream(side), torch.no_grad():
        for _ in range(3):
            run_arena_map(G, arena, discard)
    side.synchronize()
    graph = torch.cuda.CUDAGraph()
    applied = 0
    with torch.cuda.graph(graph, stream=side), torch.no_grad():
        output = run_arena_map(G, arena, discard)
        if persistence is not None:
            applied = persistence.attach_active_capture(arena)
    _CAPTURE_ARENAS.append(arena)
    graph.replay()
    torch.cuda.synchronize()
    return graph, output, applied
