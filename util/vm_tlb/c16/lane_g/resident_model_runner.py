#!/usr/bin/env python3
"""Independent, unprofiled C16 resident-model baseline runner.

This entry point deliberately reuses the standalone ``decode_once`` primitive.
It changes only model lifetime; profiler/capture invocation remains on the
qualified standalone path until a separate resident NVTX-targeting gate passes.
"""
from __future__ import annotations

import argparse
import gc
import json
import statistics
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, sha256_file
from execution_budget import BudgetLease, MeasurementActive
from model_adapters import resolve_adapter
from run_schema import validate_receipt
from runtime_native_runner import (
    decode_once,
    dtype_for,
    git_head,
    load_binding,
    load_token_ids,
    runtime_identity,
    smi_driver_version,
    smi_row,
)


PLAN_SCHEMA = "C16_G_RESIDENT_PLAN_V1"
RESET_POLICIES = {"GC_ONLY", "GC_AND_EMPTY_CACHE"}


def require_uuid(value: str, field: str) -> None:
    try:
        if str(uuid.UUID(value)) != value:
            raise ValueError
    except ValueError as exc:
        raise ContractError(f"resident {field} must be a canonical UUID") from exc


def load_plan(path: Path) -> dict[str, Any]:
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read resident plan: {exc}") from exc
    required = {"schema_version", "session_id", "reset_policy", "scenarios"}
    if not isinstance(plan, dict) or set(plan) != required:
        raise ContractError("resident plan has an unexpected schema")
    if plan["schema_version"] != PLAN_SCHEMA:
        raise ContractError("resident plan schema version differs")
    require_uuid(plan["session_id"], "session ID")
    if plan["reset_policy"] not in RESET_POLICIES:
        raise ContractError("resident plan reset policy is not qualified")
    if not isinstance(plan["scenarios"], list) or not plan["scenarios"]:
        raise ContractError("resident plan must contain an ordered scenario list")
    run_ids, receipt_paths = set(), set()
    for index, row in enumerate(plan["scenarios"]):
        if not isinstance(row, dict) or set(row) != {"binding_receipt", "run_id", "receipt"}:
            raise ContractError(f"resident plan row {index} has an unexpected schema")
        if not all(isinstance(row[key], str) and row[key] for key in row):
            raise ContractError(f"resident plan row {index} has an invalid path or run ID")
        require_uuid(row["run_id"], f"scenario {index} run ID")
        if row["run_id"] in run_ids or row["receipt"] in receipt_paths:
            raise ContractError("resident plan duplicates a scenario run ID or receipt path")
        run_ids.add(row["run_id"])
        receipt_paths.add(row["receipt"])
    return plan


def same_model_binding(first: dict[str, Any], other: dict[str, Any]) -> bool:
    fields = (
        "deployment_id", "model_id", "model_revision", "tokenizer_revision", "model_path",
        "package_id", "package_fixed_commit", "package_manifest_sha256",
        "wheelhouse_manifest_sha256", "model_files",
    )
    return all(first[field] == other[field] for field in fields)


def apply_reset(torch: Any, reset_policy: str) -> None:
    torch.cuda.synchronize()
    gc.collect()
    if reset_policy == "GC_AND_EMPTY_CACHE":
        torch.cuda.empty_cache()
    torch.cuda.synchronize()


def session_identity(binding: dict[str, Any], args: argparse.Namespace, run_id: str) -> dict[str, str]:
    return runtime_identity(binding, argparse.Namespace(
        implementation_key=args.implementation_key,
        dtype=args.dtype,
        quantization=args.quantization,
        run_id=run_id,
    ))


def execute_scenario(
    model: Any,
    binding: dict[str, Any],
    row: dict[str, str],
    args: argparse.Namespace,
    torch: Any,
    budget: BudgetLease,
    model_live_allocated: int,
    reset_policy: str,
) -> dict[str, Any]:
    identity = session_identity(binding, args, row["run_id"])
    token_ids = load_token_ids(binding)
    apply_reset(torch, reset_policy)
    pre_allocated = torch.cuda.memory_allocated()
    pre_reserved = torch.cuda.memory_reserved()
    if pre_allocated != model_live_allocated:
        raise ContractError("resident scenario begins above the qualified model-only live allocation envelope")
    torch.cuda.reset_peak_memory_stats()
    prompt = None
    results: list[tuple[float, str]] = []
    started = time.perf_counter_ns()
    try:
        prompt = torch.tensor([token_ids] * int(binding["scenario"]["batch_size"]), device="cuda:0", dtype=torch.long)
        if prompt.device.type != "cuda":
            raise ContractError("resident frozen prompt did not reach CUDA")
        for index in range(args.warmups):
            torch.cuda.nvtx.range_push(f"C16_SCENARIO::{identity['scenario_id']}::WARMUP::{index}")
            try:
                decode_once(model, prompt, int(binding["scenario"]["decode_tokens"]), torch)
            finally:
                torch.cuda.nvtx.range_pop()
            if budget.expired():
                raise ContractError("C16 resident session budget elapsed during warmup")
        for index in range(args.measures):
            torch.cuda.nvtx.range_push(f"C16_SCENARIO::{identity['scenario_id']}::MEASURE::{index}")
            try:
                results.append(decode_once(model, prompt, int(binding["scenario"]["decode_tokens"]), torch))
            finally:
                torch.cuda.nvtx.range_pop()
            if budget.expired():
                raise ContractError("C16 resident session budget elapsed during measurement")
    finally:
        del prompt
    checksums = {checksum for _duration, checksum in results}
    if len(results) != args.measures or len(checksums) != 1:
        raise ContractError("resident scenario has incomplete or nondeterministic retained measurements")
    elapsed_seconds = (time.perf_counter_ns() - started) / 1e9
    peak_allocated = torch.cuda.max_memory_allocated()
    peak_reserved = torch.cuda.max_memory_reserved()
    apply_reset(torch, reset_policy)
    post_allocated = torch.cuda.memory_allocated()
    post_reserved = torch.cuda.memory_reserved()
    if post_allocated != model_live_allocated:
        atomic_json(Path(row["receipt"] + ".diagnostic.json"), {
            "schema_version": "C16_G_RESIDENT_DIAGNOSTIC_V1",
            "execution_mode": "NATIVE_GPU_DIAGNOSTIC",
            "scientific_eligible": False,
            "identity": identity,
            "resident_session_id": args.session_id,
            "terminal_status": "FAILED_RESIDENT_ISOLATION",
            "reason": "live allocated bytes did not return to model-only envelope",
            "model_resident_allocated_bytes": model_live_allocated,
            "pre_scenario_allocated_bytes": pre_allocated,
            "post_cleanup_allocated_bytes": post_allocated,
            "pre_scenario_reserved_bytes": pre_reserved,
            "post_cleanup_reserved_bytes": post_reserved,
            "reset_policy": reset_policy,
        })
        raise ContractError("resident scenario cleanup did not return to the qualified model-only live allocation envelope")
    durations = [duration for duration, _checksum in results]
    properties = torch.cuda.get_device_properties(0)
    receipt = {
        "schema_version": "C16_G_NATIVE_RECEIPT_V1",
        "stage_id": "C16-2.1",
        "execution_mode": "NATIVE_GPU",
        "scientific_eligible": True,
        "identity": identity,
        "runtime": {
            "device": "cuda:0", "gpu_uuid": smi_row().split(",", 1)[0],
            "driver_version": smi_driver_version(), "cuda_version": torch.version.cuda,
            "torch_version": torch.__version__,
            "attention_backend": f"TRANSFORMERS_CONFIG:{getattr(model.config, '_attn_implementation', 'UNRESOLVED')}",
            "compile_state": "EAGER_UNCOMPILED", "profiler_mode": "UNPROFILED",
        },
        "checks": {
            "execution_budget_ownership": "RESIDENT_SESSION_PARENT",
            "execution_budget_ledger": str(args.budget_ledger),
            "resident_session_id": args.session_id,
            "model_lifetime_mode": "RESIDENT_UNPROFILED_QUALIFICATION",
            "frozen_binding_receipt": row["binding_receipt"],
            "frozen_binding_sha256": sha256_file(Path(row["binding_receipt"])),
            "token_receipt_sha256": binding["input"]["token_receipt_sha256"],
            "package_id": binding["package_id"],
            "package_fixed_commit": binding["package_fixed_commit"],
            "package_manifest_sha256": binding["package_manifest_sha256"],
            "wheelhouse_manifest_sha256": binding["wheelhouse_manifest_sha256"],
            "model_all_cuda": all(parameter.device.type == "cuda" for parameter in model.parameters()),
            "parameter_dtype_set": sorted({str(parameter.dtype).removeprefix("torch.") for parameter in model.parameters()}),
            "warmup_count": args.warmups, "measurement_count": args.measures,
            "output_checksum": next(iter(checksums)),
            "prefix_cache_disabled": True, "past_key_values_retained_across_scenarios": False,
            "scenario_local_references_cleared": True,
            "reset_policy": reset_policy,
            "measurement_active_guard": True,
            "measurement_active_marker": str(args.measurement_active_marker),
            "gpu_telemetry_before": args.telemetry_before,
            "gpu_telemetry_after": smi_row(),
        },
        "artifacts": {
            "duration_ms": durations, "median_duration_ms": statistics.median(durations),
            "min_duration_ms": min(durations), "max_duration_ms": max(durations),
            "cv": statistics.pstdev(durations) / statistics.mean(durations) if len(durations) > 1 else 0.0,
            "peak_allocated_bytes": peak_allocated, "peak_reserved_bytes": peak_reserved,
            "pre_scenario_allocated_bytes": pre_allocated, "pre_scenario_reserved_bytes": pre_reserved,
            "post_cleanup_allocated_bytes": post_allocated, "post_cleanup_reserved_bytes": post_reserved,
            "peak_allocated_delta_bytes": peak_allocated - pre_allocated,
            "terminal_status": "COMPLETE",
        },
    }
    validate_receipt(receipt, require_native=True)
    budget.record_child_operation(identity, operation_kind="NATIVE_RESIDENT_SCENARIO", elapsed_seconds=elapsed_seconds, terminal_status="COMPLETE")
    atomic_json(Path(row["receipt"]), receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resident-plan", type=Path, required=True)
    parser.add_argument("--session-receipt", type=Path, required=True)
    parser.add_argument("--execute-native", action="store_true")
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--implementation-key", required=True)
    parser.add_argument("--dtype", choices=("float16", "bfloat16"), required=True)
    parser.add_argument("--quantization", required=True)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--measures", type=int, default=3)
    parser.add_argument("--budget-ledger", type=Path, required=True)
    args = parser.parse_args()
    if not args.execute_native:
        parser.error("resident runner has no mock mode")
    if args.warmups != 2 or args.measures not in (3, 4, 5):
        parser.error("resident baselines require 2 warmups and 3-5 retained measures")
    adapter = resolve_adapter(args.adapter, args.dtype, args.quantization)
    if adapter.model_loader != "TRANSFORMERS_CAUSAL_LM":
        raise ContractError("resident runner supports only raw Transformers causal-LM adapters")
    plan = load_plan(args.resident_plan)
    rows = plan["scenarios"]
    bindings = [load_binding(Path(row["binding_receipt"]), canary=False) for row in rows]
    if not all(same_model_binding(bindings[0], binding) for binding in bindings[1:]):
        raise ContractError("a resident session may not mix model/package identities")
    args.session_id = plan["session_id"]
    import torch
    from transformers import AutoModelForCausalLM
    if not torch.cuda.is_available():
        raise ContractError("CUDA unavailable; refusing resident CPU fallback")
    session_started = time.perf_counter_ns()
    session_identity_value = session_identity(bindings[0], args, rows[0]["run_id"])
    session_identity_value["run_id"] = plan["session_id"]
    scenario_receipts: list[dict[str, Any]] = []
    with BudgetLease(args.budget_ledger, session_identity_value, "NATIVE_RESIDENT_SESSION", capture=False) as budget:
        try:
            with MeasurementActive(args.budget_ledger, session_identity_value, "NATIVE_RESIDENT_SESSION") as active:
                args.measurement_active_marker = active.path
                args.telemetry_before = smi_row()
                model_load_started = time.perf_counter_ns()
                model = AutoModelForCausalLM.from_pretrained(
                    bindings[0]["model_path"], local_files_only=True, torch_dtype=dtype_for(torch, args.dtype), trust_remote_code=False,
                )
                model.eval().to("cuda:0")
                torch.cuda.synchronize()
                model_load_seconds = (time.perf_counter_ns() - model_load_started) / 1e9
                if {parameter.device.type for parameter in model.parameters()} != {"cuda"}:
                    raise ContractError("resident model parameters are not all CUDA")
                if {str(parameter.dtype).removeprefix("torch.") for parameter in model.parameters()} != {args.dtype}:
                    raise ContractError("resident model dtype differs from bound request")
                if str(getattr(model.config, "_attn_implementation", "UNRESOLVED")) in {"", "UNRESOLVED", "None"}:
                    raise ContractError("resident attention backend is unresolved")
                model_live_allocated = torch.cuda.memory_allocated()
                model_reserved = torch.cuda.memory_reserved()
                torch.cuda.nvtx.range_push(f"C16_RESIDENT_SESSION::{bindings[0]['deployment_id']}")
                try:
                    for binding, row in zip(bindings, rows):
                        scenario_started = time.monotonic()
                        try:
                            scenario_receipts.append(execute_scenario(
                                model, binding, row, args, torch, budget, model_live_allocated, plan["reset_policy"],
                            ))
                        except Exception:
                            budget.record_child_operation(
                                session_identity(binding, args, row["run_id"]),
                                operation_kind="NATIVE_RESIDENT_SCENARIO",
                                elapsed_seconds=time.monotonic() - scenario_started,
                                terminal_status="FAILED_OR_ABORTED",
                                evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC",
                                diagnostic_reason="RESIDENT_SCENARIO_FAILED_OR_ABORTED",
                            )
                            raise
                finally:
                    torch.cuda.nvtx.range_pop()
                session_elapsed = (time.perf_counter_ns() - session_started) / 1e9
                budget.finish(elapsed_seconds=0.0, raw_bytes=0, terminal_status="COMPLETE", evidence_classification="ACCOUNTING_ONLY")
        except Exception:
            if not budget._finished:
                budget.finish(
                    elapsed_seconds=0.0,
                    raw_bytes=0,
                    terminal_status="FAILED_OR_ABORTED",
                    evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC",
                    diagnostic_reason="RESIDENT_SESSION_FAILED_OR_ABORTED",
                )
            raise
    atomic_json(args.session_receipt, {
        "schema_version": "C16_G_RESIDENT_SESSION_RECEIPT_V1",
        "execution_mode": "NATIVE_GPU", "scientific_eligible": True,
        "session_id": plan["session_id"], "code_commit": git_head(),
        "identity_anchor": session_identity_value,
        "runtime": {
            "device": "cuda:0", "gpu_uuid": smi_row().split(",", 1)[0],
            "driver_version": smi_driver_version(), "cuda_version": torch.version.cuda,
            "torch_version": torch.__version__,
            "attention_backend": f"TRANSFORMERS_CONFIG:{getattr(model.config, '_attn_implementation', 'UNRESOLVED')}",
            "compile_state": "EAGER_UNCOMPILED", "profiler_mode": "UNPROFILED",
        },
        "model_resident_allocated_bytes": model_live_allocated,
        "model_resident_reserved_bytes": model_reserved,
        "model_load_seconds": model_load_seconds,
        "session_elapsed_seconds": session_elapsed,
        "reset_policy": plan["reset_policy"],
        "scenario_order": [{"scenario_id": receipt["identity"]["scenario_id"], "run_id": receipt["identity"]["run_id"], "receipt": row["receipt"]} for receipt, row in zip(scenario_receipts, rows)],
        "standalone_path_unchanged": True,
        "resident_profiler_enabled": False,
        "terminal_status": "COMPLETE",
    })
    print(f"PASS C16 resident unprofiled session: {args.session_receipt}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 resident runner: {exc}", file=sys.stderr)
        raise SystemExit(2)
