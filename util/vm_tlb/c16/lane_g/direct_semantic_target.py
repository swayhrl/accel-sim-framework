#!/usr/bin/env python3
"""Build a hash-addressable target for a non-timing direct-semantic nsys pass."""
from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json
from runtime_native_runner import git_head, load_binding, runtime_identity


def target_from_binding(binding: dict[str, Any], *, run_id: str, adapter: str, implementation_key: str, dtype: str, quantization: str, runtime: dict[str, Any]) -> dict[str, Any]:
    """Return a discovery target; its kernel fields are explicitly not a selector."""
    args = argparse.Namespace(
        run_id=run_id, adapter=adapter, implementation_key=implementation_key,
        dtype=dtype, quantization=quantization,
    )
    identity = runtime_identity(binding, args)
    if identity["code_commit"] != git_head():
        raise ContractError("direct semantic target code identity is not hash-addressable")
    required_runtime = ("device", "gpu_uuid", "driver_version", "cuda_version", "torch_version", "attention_backend", "compile_state")
    if any(not isinstance(runtime.get(field), str) or not runtime[field] for field in required_runtime):
        raise ContractError("direct semantic target requires an observed CUDA runtime identity")
    return {
        "run_id": run_id,
        "deployment_id": identity["deployment_id"],
        "scenario_id": identity["scenario_id"],
        "phase": "FULL_FORWARD",
        "decode_step_bin": "ALL_DECODE_STEPS",
        "device": runtime["device"],
        "context": "PRIMARY_CUDA_CONTEXT",
        "stream": "SEMANTIC_DISCOVERY_PENDING",
        "correlation_id": "SEMANTIC_DISCOVERY_PENDING",
        "kernel_name": "DIRECT_RUNTIME_SEMANTIC_DISCOVERY",
        "implementation_key": identity["implementation_key"],
        "grid": "SEMANTIC_DISCOVERY_PENDING",
        "block": "SEMANTIC_DISCOVERY_PENDING",
        "operator_class": "UNKNOWN",
        "layer_id": "UNKNOWN",
        "shape_key": "SEMANTIC_DISCOVERY_FROM_FROZEN_BINDING",
        "dtype_key": identity["dtype"],
        "semantic_evidence": "DIRECT_RUNTIME_NVTX_AND_MODULE_ID_PENDING",
        "identity": identity,
        "runtime": {**runtime, "profiler_mode": "NSYS_DIRECT_SEMANTIC_DIAGNOSTIC"},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binding-receipt", type=Path, required=True)
    parser.add_argument("--runtime-source-receipt", type=Path, required=True)
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--implementation-key", required=True)
    parser.add_argument("--dtype", choices=("float16", "bfloat16"), required=True)
    parser.add_argument("--quantization", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id:
            raise ValueError
    except ValueError:
        parser.error("--run-id must be a canonical UUID")
    binding = load_binding(args.binding_receipt, canary=False)
    try:
        import json
        source = json.loads(args.runtime_source_receipt.read_text(encoding="utf-8"))
        runtime = source["runtime"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ContractError(f"cannot use runtime source receipt: {exc}") from exc
    atomic_json(args.output, target_from_binding(
        binding, run_id=args.run_id, adapter=args.adapter, implementation_key=args.implementation_key,
        dtype=args.dtype, quantization=args.quantization, runtime=runtime,
    ))
    print(f"PASS C16 direct semantic target: {args.output}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 direct semantic target: {exc}", file=sys.stderr)
        raise SystemExit(2)
