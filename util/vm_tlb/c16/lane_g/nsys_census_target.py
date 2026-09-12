#!/usr/bin/env python3
"""Build a hash-addressable full-range G1 discovery target from a frozen run.

This is deliberately a discovery target, not a Lane-C selector.  Kernel,
stream and correlation fields remain unresolved until the native Nsight report
is independently validated.  The builder only transports immutable binding
identity and observed runtime identity from an already-closed standalone
baseline into the parent-leased G1 wrapper.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json
from runtime_native_runner import git_head, load_binding, runtime_identity


RUNTIME_FIELDS = (
    "device", "gpu_uuid", "driver_version", "cuda_version", "torch_version",
    "attention_backend", "compile_state",
)

RUNTIME_EXECUTION_PATHS = (
    "util/vm_tlb/c16/lane_g/runtime_native_runner.py",
    "util/vm_tlb/c16/lane_g/model_adapters.py",
    "util/vm_tlb/c16/lane_g/execution_budget.py",
    "util/vm_tlb/c16/lane_g/profiler_wrapper.py",
)


def git_blob_sha256(commit: str, path: str) -> str:
    """Digest one committed execution-path blob without trusting worktree state."""
    try:
        blob = subprocess.check_output(
            ["git", "-C", str(Path(__file__).resolve().parents[4]), "show", f"{commit}:{path}"],
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContractError(f"cannot resolve committed runtime path {path} at {commit}") from exc
    return hashlib.sha256(blob).hexdigest()


def runtime_code_compatibility(source_commit: str, target_commit: str) -> dict[str, Any]:
    """Prove a new target-builder commit did not alter profiled execution code."""
    if not isinstance(source_commit, str) or len(source_commit) != 40:
        raise ContractError("G1 source receipt has no valid source commit")
    if source_commit == target_commit:
        return {
            "source_receipt_code_commit": source_commit,
            "target_code_commit": target_commit,
            "exact_runtime_execution_paths_unchanged": True,
            "paths": {path: {"source_sha256": git_blob_sha256(source_commit, path), "target_sha256": git_blob_sha256(target_commit, path)} for path in RUNTIME_EXECUTION_PATHS},
        }
    paths = {
        path: {"source_sha256": git_blob_sha256(source_commit, path), "target_sha256": git_blob_sha256(target_commit, path)}
        for path in RUNTIME_EXECUTION_PATHS
    }
    if any(item["source_sha256"] != item["target_sha256"] for item in paths.values()):
        raise ContractError("baseline and G1 source commits differ in a profiled execution path")
    return {
        "source_receipt_code_commit": source_commit,
        "target_code_commit": target_commit,
        "exact_runtime_execution_paths_unchanged": True,
        "paths": paths,
    }


def target_from_binding(
    binding: dict[str, Any], source_receipt: dict[str, Any], *, run_id: str,
    adapter: str, implementation_key: str, dtype: str, quantization: str,
) -> dict[str, Any]:
    """Return a non-selector target after proving source/binding compatibility."""
    args = argparse.Namespace(
        run_id=run_id, adapter=adapter, implementation_key=implementation_key,
        dtype=dtype, quantization=quantization,
    )
    identity = runtime_identity(binding, args)
    if identity["code_commit"] != git_head():
        raise ContractError("G1 target code identity is not hash-addressable")
    if source_receipt.get("execution_mode") != "NATIVE_GPU" or source_receipt.get("scientific_eligible") is not True:
        raise ContractError("G1 target requires an eligible native standalone source receipt")
    if source_receipt.get("artifacts", {}).get("terminal_status") != "COMPLETE":
        raise ContractError("G1 target source receipt is not complete")
    source_identity = source_receipt.get("identity")
    if not isinstance(source_identity, dict):
        raise ContractError("G1 target source receipt lacks identity")
    for field, value in identity.items():
        if field not in {"run_id", "code_commit"} and source_identity.get(field) != value:
            raise ContractError(f"G1 target source/binding identity mismatch: {field}")
    code_compatibility = runtime_code_compatibility(source_identity.get("code_commit"), identity["code_commit"])
    checks = source_receipt.get("checks")
    if not isinstance(checks, dict) or not all(checks.get(field) is True for field in ("model_all_cuda", "input_all_cuda", "cache_correct_decode")):
        raise ContractError("G1 target source has not proven CUDA/cache-correct standalone execution")
    loader = checks.get("adapter_load_evidence")
    if not isinstance(loader, dict) or loader.get("cpu_offload_forbidden") is not True:
        raise ContractError("G1 target source does not prove no-offload loader policy")
    source_runtime = source_receipt.get("runtime")
    if not isinstance(source_runtime, dict) or any(not isinstance(source_runtime.get(field), str) or not source_runtime[field] for field in RUNTIME_FIELDS):
        raise ContractError("G1 target source lacks observed runtime identity")
    scenario = binding["scenario"]
    return {
        "run_id": run_id,
        "deployment_id": identity["deployment_id"],
        "scenario_id": identity["scenario_id"],
        "phase": "FULL_FORWARD",
        "decode_step_bin": "ALL_DECODE_STEPS",
        "device": source_runtime["device"],
        "context": "PRIMARY_CUDA_CONTEXT",
        "stream": "PROFILED_DISCOVERY_PENDING",
        "correlation_id": "PROFILED_DISCOVERY_PENDING",
        "kernel_name": "NSYS_FULL_FROZEN_SCENARIO_CENSUS_REGION",
        "implementation_key": identity["implementation_key"],
        "grid": "PROFILED_DISCOVERY_PENDING",
        "block": "PROFILED_DISCOVERY_PENDING",
        "operator_class": "UNKNOWN_PRE_CENSUS",
        "layer_id": "UNKNOWN_PRE_CENSUS",
        "shape_key": f"B{scenario['batch_size']}_T{scenario['prefill_tokens']}_D{scenario['decode_tokens']}",
        "dtype_key": identity["dtype"],
        "semantic_evidence": "NSYS_BOUNDED_FULL_CENSUS_PRE_PARSE",
        "identity": identity,
        "runtime": {**{field: source_runtime[field] for field in RUNTIME_FIELDS}, "profiler_mode": "NSYS_LIGHTWEIGHT_CENSUS_PARENT_LEASED"},
        "source_baseline_runtime_code_compatibility": code_compatibility,
    }


def read_receipt(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read G1 source receipt: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("G1 source receipt root is not an object")
    return value


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
    if args.output.exists():
        raise ContractError("refusing to overwrite an existing G1 target")
    binding = load_binding(args.binding_receipt, canary=False)
    target = target_from_binding(
        binding, read_receipt(args.runtime_source_receipt), run_id=args.run_id,
        adapter=args.adapter, implementation_key=args.implementation_key,
        dtype=args.dtype, quantization=args.quantization,
    )
    atomic_json(args.output, target)
    print(f"PASS C16 frozen G1 discovery target: {args.output}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 frozen G1 discovery target: {exc}", file=sys.stderr)
        raise SystemExit(2)
