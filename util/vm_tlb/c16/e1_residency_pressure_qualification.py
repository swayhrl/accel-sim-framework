#!/usr/bin/env python3
"""Profile sparse and dense pressure over one shared 256 MiB allocation."""

import json

import torch

from e1_residency_common import PRESSURE_ELEMENTS, SPARSE_STRIDE_ELEMENTS, cuda_timed


def main():
    buffer = torch.ones(PRESSURE_ELEMENTS, dtype=torch.float32, device="cuda")
    torch.cuda.synchronize()
    timings = {}
    with torch.inference_mode():
        torch.cuda.nvtx.range_push("C16_E1_PRESSURE_SPARSE_256MIB")
        _, timings["SPARSE_PAGE_PRESSURE"] = cuda_timed(lambda: buffer[::SPARSE_STRIDE_ELEMENTS].sum())
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_pop()
        torch.cuda.nvtx.range_push("C16_E1_PRESSURE_DENSE_256MIB")
        _, timings["DENSE_MEMORY_PRESSURE"] = cuda_timed(lambda: buffer.sum())
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_pop()
    print(
        json.dumps(
            {
                "status": "PASS",
                "buffer_ptr": buffer.data_ptr(),
                "buffer_bytes": buffer.numel() * buffer.element_size(),
                "dtype": str(buffer.dtype),
                "sparse_stride_elements": SPARSE_STRIDE_ELEMENTS,
                "sparse_stride_bytes": SPARSE_STRIDE_ELEMENTS * buffer.element_size(),
                "sparse_selected_elements": buffer[::SPARSE_STRIDE_ELEMENTS].numel(),
                "dense_selected_elements": buffer.numel(),
                "timings_ms": timings,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
