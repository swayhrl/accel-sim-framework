#!/usr/bin/env python3
"""Run one frozen-input, diagnostic-only NVBit model qualification forward.

This deliberately does not use the performance/baseline runner.  It validates
the same immutable S0 binding and model adapter, but records no timing result
and sets ``scientific_eligible`` false for every terminal state.  The caller
owns stdout/stderr/raw retention and supplies an exact NVBit tool identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, repo_root, sha256_file
from execution_budget import BudgetLease, MeasurementActive
from model_adapters import resolve_adapter
from runtime_native_runner import (
    assert_cuda_residency,
    dtype_for,
    load_binding,
    load_token_ids,
    load_runtime_model,
    smi_driver_version,
)


MODES = {
    "BASELINE",
    "OFFICIAL_MEM_TRACE",
    "C16_MEMORY_TRACER",
    "NVBIT_STATIC_MAP",
    "TARGETED_MEMORY_TRACE",
}
TRACE_CONFIGURATION_ENVIRONMENT = (
    "INSTR_BEGIN", "INSTR_END", "DYNAMIC_KERNEL_RANGE", "ACTIVE_FROM_START",
    "TERMINATE_UPON_LIMIT", "TRACE_FILE_COMPRESS", "TOOL_COMPRESS", "TRACES_FOLDER",
    "C16_NVBIT_TARGET_FUNCTION_MANGLED", "C16_NVBIT_TARGET_INSTR_INDEX",
    "C16_NVBIT_STATIC_MAP_PATH",
)


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "-C", str(repo_root()), "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContractError("model qualification requires a hash-addressable Git checkout") from exc


def raw_tree_bytes(root: Path) -> int:
    if not root.is_dir():
        raise ContractError("qualification raw directory is absent")
    return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())


def validate_tool_contract(mode: str, tool_path: Path | None, tool_sha256: str | None, preload_declaration: str | None) -> dict[str, str]:
    """Make injection identity exact; a baseline cannot silently preload code.

    The ELF dynamic loader may remove ``LD_PRELOAD`` before Python begins.  A
    profile launcher must therefore carry an exact, non-loader declaration in
    ``C16_NVBIT_LD_PRELOAD_DECLARATION`` as well as setting ``LD_PRELOAD`` at
    exec time.  The declared path/hash and tool-emitted raw evidence are all
    required; the declaration is not a substitute for either one.
    """
    if mode not in MODES:
        raise ContractError("unknown model qualification mode")
    if mode == "BASELINE":
        if tool_path is not None or tool_sha256 is not None or preload_declaration:
            raise ContractError("baseline qualification must not name or preload an NVBit tool")
        return {"mode": mode, "tool_path": "NA", "tool_sha256": "NA", "ld_preload_launch_declaration": "NA"}
    if tool_path is None or tool_sha256 is None:
        raise ContractError("NVBit qualification requires an exact tool path and SHA256")
    if not tool_path.is_file() or sha256_file(tool_path) != tool_sha256:
        raise ContractError("NVBit tool path/SHA256 is not closed")
    if preload_declaration != str(tool_path):
        raise ContractError("preload launch declaration does not exactly bind the declared NVBit tool")
    return {
        "mode": mode, "tool_path": str(tool_path), "tool_sha256": tool_sha256,
        "ld_preload_launch_declaration": preload_declaration,
        "ld_preload_visible_after_loader": os.environ.get("LD_PRELOAD", "UNSET_AFTER_DYNAMIC_LOADER"),
    }


def trace_evidence(
    *,
    raw_dir: Path,
    mode: str,
    trace_glob: str | None,
    trace_marker: str | None,
    kernel_catalog_glob: str | None,
    static_map_path: Path | None = None,
    target_instruction_receipt: Path | None = None,
) -> dict[str, Any]:
    """Close real trace evidence without treating a launcher banner as data.

    This check is intentionally specific to diagnostic qualification.  It
    proves that the requested tool emitted a materialized payload, but makes
    no kernel-name, timing, or frozen-C-target claim.
    """
    if mode == "BASELINE":
        if any(value is not None for value in (trace_glob, trace_marker, kernel_catalog_glob, static_map_path, target_instruction_receipt)):
            raise ContractError("baseline qualification cannot declare NVBit trace evidence")
        return {"required": False, "records": [], "kernel_catalogs": [], "configuration": {}}
    if mode == "NVBIT_STATIC_MAP":
        if trace_glob is not None or trace_marker is not None or kernel_catalog_glob is not None or target_instruction_receipt is not None:
            raise ContractError("NVBit-static-map mode accepts only a native static-map payload")
        if static_map_path is None or not static_map_path.is_file() or static_map_path.stat().st_size == 0:
            raise ContractError("NVBit-static-map mode emitted no nonzero native static-map payload")
        try:
            static_map_path.resolve().relative_to(raw_dir.resolve())
        except ValueError as exc:
            raise ContractError("NVBit-static-map payload must be inside the declared raw directory") from exc
        return {
            "required": True,
            "records": [{
                "path": str(static_map_path.relative_to(raw_dir)),
                "size_bytes": static_map_path.stat().st_size,
                "sha256": sha256_file(static_map_path),
            }],
            "kernel_catalogs": [],
            "configuration": {name: os.environ.get(name, "UNSET") for name in TRACE_CONFIGURATION_ENVIRONMENT},
        }
    if not trace_glob:
        raise ContractError("profile qualification requires --trace-evidence-glob")
    if Path(trace_glob).is_absolute() or ".." in Path(trace_glob).parts:
        raise ContractError("trace evidence glob must be a safe raw-directory-relative path")
    matches = sorted(path for path in raw_dir.glob(trace_glob) if path.is_file() and path.stat().st_size > 0)
    if not matches:
        raise ContractError("profile qualification emitted no nonzero declared trace evidence")
    records = [
        {"path": str(path.relative_to(raw_dir)), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in matches
    ]
    if trace_marker is not None:
        try:
            marker = re.compile(trace_marker)
        except re.error as exc:
            raise ContractError("trace evidence marker is not a valid regular expression") from exc
        if not any(marker.search(path.read_text(encoding="utf-8", errors="replace")) for path in matches):
            raise ContractError("profile qualification trace lacks the required real-record marker")
    catalogs: list[dict[str, Any]] = []
    if kernel_catalog_glob is not None:
        if Path(kernel_catalog_glob).is_absolute() or ".." in Path(kernel_catalog_glob).parts:
            raise ContractError("kernel catalog glob must be a safe raw-directory-relative path")
        catalog_paths = sorted(path for path in raw_dir.glob(kernel_catalog_glob) if path.is_file() and path.stat().st_size > 0)
        if not catalog_paths:
            raise ContractError("C16 tracer qualification emitted no nonzero kernel catalog")
        catalogs = [
            {"path": str(path.relative_to(raw_dir)), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in catalog_paths
        ]
    static_map: dict[str, Any] | None = None
    if static_map_path is not None:
        if not static_map_path.is_file() or static_map_path.stat().st_size == 0:
            raise ContractError("declared NVBit-native static map is absent or empty")
        static_map = {
            "path": str(static_map_path),
            "size_bytes": static_map_path.stat().st_size,
            "sha256": sha256_file(static_map_path),
        }
    target_binding: dict[str, Any] | None = None
    if mode == "TARGETED_MEMORY_TRACE":
        if static_map is None or target_instruction_receipt is None or not target_instruction_receipt.is_file():
            raise ContractError("targeted-memory mode requires its closed native map and target receipt")
        try:
            target = json.loads(target_instruction_receipt.read_text(encoding="utf-8"))
            target_index = int(target["target_instruction"]["nvbit_static_index"])
            target_mangled = str(target["function"]["mangled_name"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ContractError("targeted-memory target receipt is malformed") from exc
        if os.environ.get("C16_NVBIT_TARGET_INSTR_INDEX") != str(target_index):
            raise ContractError("NVBit environment target index differs from the closed target receipt")
        if os.environ.get("C16_NVBIT_TARGET_FUNCTION_MANGLED") != target_mangled:
            raise ContractError("NVBit environment function identity differs from the closed target receipt")
        target_binding = {
            "path": str(target_instruction_receipt),
            "sha256": sha256_file(target_instruction_receipt),
            "nvbit_static_index": target_index,
            "function_mangled_name": target_mangled,
        }
    return {
        "required": True,
        "records": records,
        "kernel_catalogs": catalogs,
        "native_static_map": static_map,
        "target_instruction_binding": target_binding,
        "configuration": {name: os.environ.get(name, "UNSET") for name in TRACE_CONFIGURATION_ENVIRONMENT},
    }


def output_checksum(logits: Any) -> tuple[str, list[int]]:
    """Use greedy terminal tokens, not a timing-dependent tensor serialization."""
    terminal = logits[:, -1, :].argmax(dim=-1).detach().to("cpu").flatten().tolist()
    if not terminal or any(not isinstance(token, int) or token < 0 for token in terminal):
        raise ContractError("model forward emitted malformed terminal token IDs")
    return hashlib.sha256(canonical_json(terminal).encode("utf-8")).hexdigest(), terminal


def runtime_identity(binding: dict[str, Any], args: argparse.Namespace, code_commit: str) -> dict[str, str]:
    return {
        "model_id": binding["model_id"],
        "model_revision": binding["model_revision"],
        "tokenizer_revision": binding["tokenizer_revision"],
        "deployment_id": binding["deployment_id"],
        "implementation_key": args.implementation_key,
        "dtype": args.dtype,
        "quantization": args.quantization,
        "scenario_id": binding["scenario"]["scenario_id"],
        "input_hash": binding["input"]["raw_input_sha256"],
        "run_id": args.run_id,
        "code_commit": code_commit,
    }


def execute(binding: dict[str, Any], args: argparse.Namespace, tool: dict[str, str], code_commit: str) -> dict[str, Any]:
    try:
        import torch
    except ImportError as exc:
        raise ContractError("hash-closed torch environment is unavailable") from exc
    if not torch.cuda.is_available():
        raise ContractError("CUDA unavailable; refusing CPU fallback")
    adapter = resolve_adapter(args.adapter, args.dtype, args.quantization)
    model_path = Path(binding["model_path"])
    if not model_path.is_dir():
        raise ContractError("bound local model directory is absent")
    token_ids = load_token_ids(binding)
    identity = runtime_identity(binding, args, code_commit)
    atomic_json(args.receipt.with_suffix(args.receipt.suffix + ".preflight.json"), {
        "schema_version": "C16_G_MODEL_NVBIT_QUALIFICATION_V1",
        "status": "PENDING_MODEL_FORWARD",
        "scientific_eligible": False,
        "identity": identity,
        "tool": tool,
        "binding_receipt": str(args.binding_receipt),
        "binding_receipt_sha256": sha256_file(args.binding_receipt),
        "raw_directory": str(args.raw_dir),
        "constraints": {
            "diagnostic_only_not_for_native_timing": True,
            "cpu_offload_forbidden": True,
            "frozen_s0_binding_required": True,
        },
    })
    torch.cuda.reset_peak_memory_stats()
    required_sequence_length = int(binding["scenario"]["prefill_tokens"]) + int(binding["scenario"]["decode_tokens"])
    model, loader_evidence = load_runtime_model(adapter, model_path, torch, args.dtype, required_sequence_length=required_sequence_length)
    _devices, parameter_dtypes = assert_cuda_residency(
        model, require_raw_dtype=args.dtype if adapter.model_loader == "TRANSFORMERS_CAUSAL_LM" else None,
    )
    prompt = torch.tensor([token_ids] * int(binding["scenario"]["batch_size"]), device="cuda:0", dtype=torch.long)
    if prompt.device.type != "cuda":
        raise ContractError("frozen prompt IDs did not reach CUDA")
    attention = str(getattr(model.config, "_attn_implementation", "UNRESOLVED"))
    if attention in {"", "UNRESOLVED", "None"}:
        raise ContractError("model attention backend is unresolved")
    if args.expected_attention_backend is not None and attention != args.expected_attention_backend:
        raise ContractError("model attention backend differs from the frozen baseline qualification")
    torch.cuda.synchronize()
    torch.cuda.nvtx.range_push("C16_MODEL_NVBIT_QUALIFICATION")
    try:
        with torch.inference_mode():
            output = model(input_ids=prompt, use_cache=False)
    finally:
        torch.cuda.nvtx.range_pop()
    torch.cuda.synchronize()
    checksum, terminal_tokens = output_checksum(output.logits)
    if args.expected_output_checksum is not None and checksum != args.expected_output_checksum:
        raise ContractError("model output checksum differs from the frozen baseline qualification")
    properties = torch.cuda.get_device_properties(0)
    evidence = trace_evidence(
        raw_dir=args.raw_dir,
        mode=args.mode,
        trace_glob=args.trace_evidence_glob,
        trace_marker=args.trace_evidence_marker,
        kernel_catalog_glob=args.kernel_catalog_glob,
        static_map_path=args.static_map_path,
        target_instruction_receipt=args.target_instruction_receipt,
    )
    return {
        "schema_version": "C16_G_MODEL_NVBIT_QUALIFICATION_V1",
        "status": "MODEL_NVBIT_QUALIFICATION_FORWARD_COMPLETE",
        "scientific_eligible": False,
        "identity": identity,
        "tool": tool,
        "binding": {
            "receipt": str(args.binding_receipt),
            "sha256": sha256_file(args.binding_receipt),
            "package_id": binding["package_id"],
            "package_fixed_commit": binding["package_fixed_commit"],
            "package_manifest_sha256": binding["package_manifest_sha256"],
            "wheelhouse_manifest_sha256": binding["wheelhouse_manifest_sha256"],
            "token_receipt_sha256": binding["input"]["token_receipt_sha256"],
        },
        "runtime": {
            "device": "cuda:0",
            "gpu_name": properties.name,
            "gpu_uuid": subprocess.check_output(["nvidia-smi", "--query-gpu=uuid", "--format=csv,noheader,nounits"], text=True).strip(),
            "driver_version": smi_driver_version(),
            "torch_version": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "attention_backend": attention,
            "compile_state": "EAGER_UNCOMPILED",
            "adapter_load_evidence": loader_evidence,
        },
        "checks": {
            "model_all_cuda": True,
            "input_all_cuda": True,
            "cpu_offload_forbidden": True,
            "parameter_dtype_set": sorted(parameter_dtypes),
            "output_checksum": checksum,
            "terminal_token_ids": terminal_tokens,
            "expected_output_checksum_matched": args.expected_output_checksum is not None,
            "expected_attention_backend_matched": args.expected_attention_backend is not None,
            "nvtx_model_range_emitted": True,
        },
        "artifacts": {
            "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
            "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
            "raw_bytes_observed_before_receipt": raw_tree_bytes(args.raw_dir),
            "trace_evidence": evidence,
            "terminal_status": "COMPLETE",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--binding-receipt", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--budget-ledger", type=Path, required=True)
    parser.add_argument("--mode", choices=sorted(MODES), required=True)
    parser.add_argument("--tool-path", type=Path)
    parser.add_argument("--tool-sha256")
    parser.add_argument("--trace-evidence-glob")
    parser.add_argument("--trace-evidence-marker")
    parser.add_argument("--kernel-catalog-glob")
    parser.add_argument("--static-map-path", type=Path)
    parser.add_argument("--target-instruction-receipt", type=Path)
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--implementation-key", required=True)
    parser.add_argument("--dtype", choices=("float16", "bfloat16"), required=True)
    parser.add_argument("--quantization", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--expected-output-checksum")
    parser.add_argument("--expected-attention-backend")
    parser.add_argument("--runtime-code-commit", required=True)
    args = parser.parse_args()
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id:
            raise ValueError
    except ValueError:
        parser.error("--run-id must be a canonical UUID")
    if args.expected_output_checksum is not None and (len(args.expected_output_checksum) != 64 or any(char not in "0123456789abcdef" for char in args.expected_output_checksum)):
        parser.error("--expected-output-checksum must be a lowercase SHA256")
    code_commit = git_head()
    if args.runtime_code_commit != code_commit:
        raise ContractError("declared runtime code commit differs from the checked-out source")
    binding = load_binding(args.binding_receipt, canary=True)
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    identity = runtime_identity(binding, args, code_commit)
    capture = args.mode != "BASELINE"
    operation = "NVBIT" if capture else "MODEL_QUALIFICATION_BASELINE"
    MeasurementActive.assert_available(args.budget_ledger)
    with BudgetLease(args.budget_ledger, identity, operation, capture=capture) as lease:
        with MeasurementActive(args.budget_ledger, identity, operation):
            try:
                tool = validate_tool_contract(
                    args.mode, args.tool_path, args.tool_sha256,
                    os.environ.get("C16_NVBIT_LD_PRELOAD_DECLARATION"),
                )
                receipt = execute(binding, args, tool, code_commit)
                raw_bytes = raw_tree_bytes(args.raw_dir)
                if capture and raw_bytes > lease.max_raw_bytes:
                    raise ContractError("diagnostic model trace exceeds the active NVBit raw-byte ceiling")
                lease.finish(
                    elapsed_seconds=lease.elapsed_seconds(), raw_bytes=raw_bytes if capture else 0,
                    terminal_status="COMPLETE", evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC",
                    diagnostic_reason="MODEL_NVBIT_QUALIFICATION_DIAGNOSTIC_ONLY",
                )
            except Exception:
                raw_bytes = raw_tree_bytes(args.raw_dir)
                lease.finish(
                    elapsed_seconds=lease.elapsed_seconds(), raw_bytes=raw_bytes if capture else 0,
                    terminal_status="FAILED_OR_ABORTED", evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC",
                    diagnostic_reason="MODEL_NVBIT_QUALIFICATION_FAILURE",
                )
                raise
    atomic_json(args.receipt, receipt)
    print(f"PASS C16 model NVBit qualification: {args.receipt}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 model NVBit qualification: {exc}", file=sys.stderr)
        raise SystemExit(2)
