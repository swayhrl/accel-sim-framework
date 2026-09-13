#!/usr/bin/env python3
"""Bounded exact-kernel NVBit-native map reproducer for Retry570.

This is deliberately a diagnostic workload, not a C16 scenario or timing
run.  It performs a finite, recorded set of ``torch.index_select`` candidates
under the same immutable PyTorch/CUDA/libtorch/GPU/driver identity as the
Llama candidate receipt.  Exact equivalence is granted only when the injected
NVBit mapper emits a nonempty map whose full mangled function identity equals
the requested target exactly.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, repo_root, sha256_file, valid_sha256
from execution_budget import BudgetLease, MeasurementActive
from nvbit_native_static_map import read_native_map, target_receipt


SCHEMA = "C16_G_RETRY570_INDEXSELECT_MICROREPRODUCER_V1"
DIAGNOSTIC_DEPLOYMENT = "c16_retry570_indexselect_microreproducer"

# This is intentionally finite.  The ranks/dimensions/index dtypes are the
# only varying inputs, and every candidate is printed before execution so the
# resulting map is never attributed to an unrecorded workload.
CANDIDATES: tuple[dict[str, object], ...] = (
    {"candidate_id": "R2_D0_I64", "shape": (8192, 128), "dim": 0, "index_dtype": "int64"},
    {"candidate_id": "R2_D1_I64", "shape": (128, 8192), "dim": 1, "index_dtype": "int64"},
    {"candidate_id": "R2_D0_I32", "shape": (8192, 128), "dim": 0, "index_dtype": "int32"},
    {"candidate_id": "R2_D1_I32", "shape": (128, 8192), "dim": 1, "index_dtype": "int32"},
    {"candidate_id": "R3_D0_I64", "shape": (512, 32, 16), "dim": 0, "index_dtype": "int64"},
    {"candidate_id": "R3_D1_I64", "shape": (32, 512, 16), "dim": 1, "index_dtype": "int64"},
    {"candidate_id": "R3_D2_I64", "shape": (32, 16, 512), "dim": 2, "index_dtype": "int64"},
)


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "-C", str(repo_root()), "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContractError("microreproducer requires a hash-addressable Git checkout") from exc


def nvidia_smi_value(query: str) -> str:
    try:
        return subprocess.check_output(
            ["nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader,nounits"], text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContractError(f"cannot obtain NVIDIA identity {query}") from exc


def libtorch_cuda_path(torch: Any) -> Path:
    path = Path(torch.__file__).resolve().parent / "lib" / "libtorch_cuda.so"
    if not path.is_file():
        raise ContractError("installed torch has no hashable libtorch_cuda.so")
    return path


def assert_runtime_identity(args: argparse.Namespace) -> tuple[Any, dict[str, str]]:
    try:
        import torch
    except ImportError as exc:
        raise ContractError("hash-closed torch environment is unavailable") from exc
    if not torch.cuda.is_available():
        raise ContractError("CUDA unavailable; refusing any CPU microreproducer fallback")
    if torch.__version__ != args.expected_torch_version or torch.version.cuda != args.expected_torch_cuda:
        raise ContractError("microreproducer torch/CUDA wheel differs from the Llama candidate receipt")
    library = libtorch_cuda_path(torch)
    library_sha = sha256_file(library)
    if library_sha != args.expected_libtorch_cuda_sha256:
        raise ContractError("libtorch_cuda.so SHA differs from the Llama candidate receipt")
    properties = torch.cuda.get_device_properties(0)
    uuid_value = nvidia_smi_value("uuid")
    driver = nvidia_smi_value("driver_version")
    if properties.name != args.expected_gpu_name or driver != args.expected_driver:
        raise ContractError("GPU model or driver differs from the Llama candidate receipt")
    if args.expected_gpu_uuid is not None and uuid_value != args.expected_gpu_uuid:
        raise ContractError("GPU UUID differs from the Llama candidate receipt")
    return torch, {
        "torch_version": torch.__version__,
        "torch_cuda": str(torch.version.cuda),
        "libtorch_cuda_path": str(library),
        "libtorch_cuda_sha256": library_sha,
        "gpu_name": properties.name,
        "gpu_uuid": uuid_value,
        "driver_version": driver,
    }


def run_candidates(torch: Any) -> list[dict[str, object]]:
    completed: list[dict[str, object]] = []
    torch.manual_seed(570)
    for candidate in CANDIDATES:
        shape = tuple(int(value) for value in candidate["shape"])
        dim = int(candidate["dim"])
        dtype = torch.int64 if candidate["index_dtype"] == "int64" else torch.int32
        index_count = min(4096, shape[dim])
        # Repeat indices to make every candidate large-index capable without
        # relying on an unbounded shape search or a model artifact.
        indices = (torch.arange(index_count, device="cuda:0", dtype=torch.int64) * 17) % shape[dim]
        indices = indices.to(dtype=dtype)
        print(
            "C16_INDEXSELECT_MICRO_CANDIDATE_BEGIN "
            + json.dumps({**candidate, "index_count": index_count}, sort_keys=True),
            flush=True,
        )
        source = torch.randn(shape, device="cuda:0", dtype=torch.float16)
        output = torch.index_select(source, dim, indices)
        torch.cuda.synchronize()
        expected_shape = list(shape)
        expected_shape[dim] = index_count
        if output.device.type != "cuda" or list(output.shape) != expected_shape:
            raise ContractError("index_select produced an invalid microreproducer output")
        completed.append({**candidate, "index_count": index_count, "output_shape": list(output.shape)})
        print(f"C16_INDEXSELECT_MICRO_CANDIDATE_COMPLETE {candidate['candidate_id']}", flush=True)
        del output, source, indices
    torch.cuda.synchronize()
    return completed


def validate_tool(args: argparse.Namespace) -> dict[str, str]:
    if not args.tool_path.is_file() or sha256_file(args.tool_path) != args.tool_sha256:
        raise ContractError("microreproducer NVBit tool path/SHA is not closed")
    if os.environ.get("C16_NVBIT_LD_PRELOAD_DECLARATION") != str(args.tool_path):
        raise ContractError("microreproducer preload declaration does not bind the exact NVBit tool")
    if os.environ.get("C16_NVBIT_TARGET_FUNCTION_MANGLED") != args.exact_mangled_function:
        raise ContractError("NVBit mapper function environment differs from the requested exact identity")
    if os.environ.get("C16_NVBIT_STATIC_MAP_PATH") != str(args.static_map):
        raise ContractError("NVBit mapper static-map environment differs from the declared raw path")
    if os.environ.get("C16_NVBIT_CODE_OBJECT_SHA256") != args.expected_libtorch_cuda_sha256:
        raise ContractError("NVBit mapper code-object SHA differs from the runtime identity")
    return {"path": str(args.tool_path), "sha256": args.tool_sha256}


def write_failure(args: argparse.Namespace, *, message: str, identity: dict[str, str] | None) -> None:
    atomic_json(args.receipt, {
        "schema_version": SCHEMA,
        "status": "FAIL_CLOSED_MICROREPRODUCER_NOT_EQUIVALENT",
        "scientific_eligible": False,
        "message": message,
        "exact_mangled_function_required": args.exact_mangled_function,
        "runtime_identity": identity,
        "static_map_path": str(args.static_map),
        "static_map_materialized": args.static_map.is_file() and args.static_map.stat().st_size > 0,
    })


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--static-map", type=Path, required=True)
    parser.add_argument("--target-receipt", type=Path, required=True)
    parser.add_argument("--budget-ledger", type=Path, required=True)
    parser.add_argument("--tool-path", type=Path, required=True)
    parser.add_argument("--tool-sha256", required=True)
    parser.add_argument("--exact-mangled-function", required=True)
    parser.add_argument("--expected-torch-version", required=True)
    parser.add_argument("--expected-torch-cuda", required=True)
    parser.add_argument("--expected-libtorch-cuda-sha256", required=True)
    parser.add_argument("--expected-gpu-name", default="NVIDIA GeForce RTX 3090")
    parser.add_argument("--expected-driver", default="570.124.04")
    parser.add_argument("--expected-gpu-uuid")
    parser.add_argument("--runtime-code-commit", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if not valid_sha256(args.tool_sha256) or not valid_sha256(args.expected_libtorch_cuda_sha256):
        parser.error("tool and libtorch CUDA SHA256 values must be lowercase SHA256")
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id:
            raise ValueError
    except ValueError:
        parser.error("--run-id must be a canonical UUID")
    if args.runtime_code_commit != git_head():
        raise ContractError("declared runtime code commit differs from this source checkout")
    args.static_map.parent.mkdir(parents=True, exist_ok=True)
    if args.static_map.exists():
        raise ContractError("microreproducer refuses to overwrite a pre-existing NVBit-native map")
    identity: dict[str, str] | None = None
    lease_identity = {
        "deployment_id": DIAGNOSTIC_DEPLOYMENT,
        "run_id": args.run_id,
        "scenario_id": "INDEXSELECT_EXACT_FUNCTION_STATIC_MAP",
        "implementation_key": "TORCH_INDEX_SELECT_MICROREPRODUCER",
    }
    MeasurementActive.assert_available(args.budget_ledger)
    with BudgetLease(args.budget_ledger, lease_identity, "NVBIT", capture=True) as lease:
        with MeasurementActive(args.budget_ledger, lease_identity, "NVBIT"):
            try:
                tool = validate_tool(args)
                torch, identity = assert_runtime_identity(args)
                completed = run_candidates(torch)
                instructions = read_native_map(args.static_map, args.exact_mangled_function)
                target = target_receipt(args.static_map, args.exact_mangled_function)
                if target["function"]["libtorch_cuda_sha256"] != args.expected_libtorch_cuda_sha256:
                    raise ContractError("NVBit-native map code-object SHA differs from the verified microreproducer")
                atomic_json(args.target_receipt, target)
                raw_bytes = args.static_map.stat().st_size
                if raw_bytes > lease.max_raw_bytes:
                    raise ContractError("microreproducer map exceeds active NVBit raw-byte ceiling")
                receipt = {
                    "schema_version": SCHEMA,
                    "status": "EXACT_FUNCTION_REPRODUCED_NVBIT_NATIVE_MAP",
                    "scientific_eligible": False,
                    "diagnostic_only": True,
                    "exact_mangled_function": args.exact_mangled_function,
                    "runtime_identity": identity,
                    "tool": tool,
                    "candidate_search": {"bounded": True, "candidates": completed},
                    "native_map": {
                        "path": str(args.static_map), "size_bytes": raw_bytes,
                        "sha256": sha256_file(args.static_map), "static_instruction_count": len(instructions),
                    },
                    "memory_instruction_target": {"path": str(args.target_receipt), "sha256": sha256_file(args.target_receipt)},
                    "terminal_status": "COMPLETE",
                }
                lease.finish(
                    elapsed_seconds=lease.elapsed_seconds(), raw_bytes=raw_bytes, terminal_status="COMPLETE",
                    evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC",
                    diagnostic_reason="EXACT_INDEXSELECT_NVBIT_STATIC_MAP_DIAGNOSTIC_ONLY",
                )
            except Exception as exc:
                raw_bytes = args.static_map.stat().st_size if args.static_map.is_file() else 0
                write_failure(args, message=str(exc), identity=identity)
                lease.finish(
                    elapsed_seconds=lease.elapsed_seconds(), raw_bytes=raw_bytes, terminal_status="FAILED_OR_ABORTED",
                    evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC",
                    diagnostic_reason="FAIL_CLOSED_MICROREPRODUCER_NOT_EQUIVALENT",
                )
                raise
    atomic_json(args.receipt, receipt)
    print(f"PASS exact indexSelect microreproducer: {args.receipt}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL exact indexSelect microreproducer: {exc}", file=sys.stderr)
        raise SystemExit(2)
