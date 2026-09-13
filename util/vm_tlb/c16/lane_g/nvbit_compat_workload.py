#!/usr/bin/env python3
"""Small, marker-rich CUDA workloads for C16 NVBit compatibility diagnostics.

This program deliberately contains no C16 scenario, timing, selector, or
capture semantics.  Every successful invocation is diagnostic-only; the
stdout markers let an outer bounded harness localize failures without using a
profiler timestamp or a kernel-name heuristic as scientific evidence.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def mark(name: str) -> None:
    print(f"C16_NVBIT_DIAG_STAGE={name}", flush=True)


def torch_module():
    mark("PYTHON_START")
    import torch
    mark("TORCH_IMPORTED")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA_UNAVAILABLE")
    mark("TORCH_CUDA_INIT")
    return torch


def elementwise(torch) -> None:
    mark("ELEMENTWISE_PREPARE")
    x = torch.randn(4096, device="cuda")
    mark("ELEMENTWISE_INPUT_READY")
    _y = x + 1
    mark("ELEMENTWISE_LAUNCHED")
    torch.cuda.synchronize()
    mark("ELEMENTWISE_SYNCHRONIZED")


def gemm(torch) -> None:
    mark("GEMM_PREPARE")
    a = torch.randn((128, 128), device="cuda", dtype=torch.float32)
    b = torch.randn((128, 128), device="cuda", dtype=torch.float32)
    mark("GEMM_INPUT_READY")
    _y = a @ b
    mark("GEMM_LAUNCHED")
    torch.cuda.synchronize()
    mark("GEMM_SYNCHRONIZED")


def linear(torch) -> None:
    mark("LINEAR_PREPARE")
    layer = torch.nn.Linear(128, 128, bias=True, device="cuda", dtype=torch.float32).eval()
    x = torch.randn((1, 128), device="cuda", dtype=torch.float32)
    mark("LINEAR_INPUT_READY")
    with torch.inference_mode():
        _y = layer(x)
    mark("LINEAR_LAUNCHED")
    torch.cuda.synchronize()
    mark("LINEAR_SYNCHRONIZED")


def llama(torch, path: Path) -> None:
    mark("TRANSFORMERS_IMPORT_BEGIN")
    from transformers import AutoModelForCausalLM
    mark("TRANSFORMERS_IMPORTED")
    mark("MODEL_LOAD_BEGIN")
    model = AutoModelForCausalLM.from_pretrained(str(path), local_files_only=True, torch_dtype=torch.float16, trust_remote_code=False)
    mark("MODEL_LOADED_CPU")
    model.eval().to("cuda:0")
    torch.cuda.synchronize()
    mark("MODEL_LOADED_CUDA")
    ids = torch.ones((1, 16), dtype=torch.long, device="cuda:0")
    mark("MODEL_INPUT_READY")
    with torch.inference_mode():
        _out = model(input_ids=ids, use_cache=False)
    mark("MODEL_FIRST_FORWARD_LAUNCHED")
    torch.cuda.synchronize()
    mark("MODEL_FIRST_FORWARD_SYNCHRONIZED")


def awq_load(torch, path: Path) -> None:
    mark("AUTOAWQ_IMPORT_BEGIN")
    from awq import AutoAWQForCausalLM
    mark("AUTOAWQ_IMPORTED")
    mark("AUTOAWQ_LOAD_BEGIN")
    model = AutoAWQForCausalLM.from_quantized(
        str(path), max_seq_len=272, fuse_layers=False, trust_remote_code=False,
        safetensors=True, device_map={"": 0},
    )
    mark("AUTOAWQ_FROM_QUANTIZED_RETURNED")
    if getattr(model, "model", None) is None:
        raise RuntimeError("AUTOAWQ_NO_MODEL")
    torch.cuda.synchronize()
    mark("AUTOAWQ_CUDA_SYNCHRONIZED")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workload", choices=("elementwise", "gemm", "linear", "llama", "awq-load"), required=True)
    parser.add_argument("--model-path", type=Path)
    args = parser.parse_args()
    torch = torch_module()
    if args.workload == "elementwise":
        elementwise(torch)
    elif args.workload == "gemm":
        gemm(torch)
    elif args.workload == "linear":
        linear(torch)
    elif args.workload == "llama":
        if args.model_path is None:
            parser.error("--model-path is required for llama")
        llama(torch, args.model_path)
    else:
        if args.model_path is None:
            parser.error("--model-path is required for awq-load")
        awq_load(torch, args.model_path)
    mark("NORMAL_EXIT")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        mark("PYTHON_EXCEPTION_" + type(exc).__name__)
        print(str(exc), file=sys.stderr, flush=True)
        raise
