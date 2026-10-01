#!/usr/bin/env python3
"""Tiny engineering-only direct nvtxRangePushA + known Warp CUDA kernel canary."""

import ctypes
import os
from pathlib import Path

import warp as wp


ROOT = Path("/data/c16/awma/r20r3p1_profiler_repair_resume_20261001")


@wp.kernel
def known_kernel(data: wp.array(dtype=wp.int32)):
    i = wp.tid()
    data[i] = i + 7


def main():
    if os.environ.get("R20R3P1_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU campaign lock receipt absent")
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    device = wp.get_device("cuda:0")
    values = wp.zeros(1024, dtype=wp.int32, device=device)
    wp.launch(known_kernel, dim=1024, inputs=[values], device=device)
    wp.synchronize_device(device)
    lib = ctypes.CDLL("libnvToolsExt.so.1")
    lib.nvtxRangePushA.argtypes = [ctypes.c_char_p]
    lib.nvtxRangePushA.restype = ctypes.c_int
    lib.nvtxRangePop.argtypes = []
    lib.nvtxRangePop.restype = ctypes.c_int
    depth = lib.nvtxRangePushA(b"R20R3P1_CANARY")
    # Nsight's direct-function interception can report -1 here even when the
    # matching range is captured. The admission gate is the exported range and
    # CUDA kernel row, not this advisory stack-depth return value.
    wp.launch(known_kernel, dim=1024, inputs=[values], device=device)
    wp.synchronize_device(device)
    lib.nvtxRangePop()
    result = values.numpy()
    if result[0] != 7 or result[-1] != 1030:
        raise RuntimeError("Known Warp kernel result mismatch")
    print(f"R20R3P1_CANARY_KERNEL_OK NVTX_PUSH_DEPTH={depth}", flush=True)


if __name__ == "__main__":
    main()
