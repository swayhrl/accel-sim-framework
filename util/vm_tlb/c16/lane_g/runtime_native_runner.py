#!/usr/bin/env python3
"""C16 runtime-native runner with cache-correct greedy decoding.

This is a runtime implementation layer, separate from the immutable C16-0
offline package.  It consumes a previously validated frozen-binding receipt
and keeps ``past_key_values`` across decode steps, rather than timing a set of
unrelated one-token forwards.  It has no download, CPU-offload, or profiler
fallback path.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, repo_root, sha256_file
from execution_budget import BudgetLease
from model_adapters import resolve_adapter
from run_schema import validate_receipt


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "-C", str(repo_root()), "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContractError("runtime runner must execute from a hash-addressable Git checkout") from exc


def smi_row() -> str:
    fields = "uuid,temperature.gpu,pstate,power.draw,power.limit,clocks.current.graphics,clocks.current.memory,clocks_throttle_reasons.active"
    try:
        rows = subprocess.check_output(["nvidia-smi", f"--query-gpu={fields}", "--format=csv,noheader,nounits"], text=True).splitlines()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContractError("cannot record GPU telemetry via nvidia-smi") from exc
    if len(rows) != 1 or not rows[0].strip():
        raise ContractError("C16 runtime runner requires exactly one queryable GPU")
    return rows[0].strip()


def smi_driver_version() -> str:
    """Read the loaded NVIDIA driver version from the same runtime probe.

    ``torch.version.cuda`` describes the wheel build, not the driver.  PyTorch
    does not expose a stable ``torch.cuda.driver_version`` API across the
    pinned builds, so use the already-required local ``nvidia-smi`` query.
    """
    try:
        value = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader,nounits"],
            text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContractError("cannot record NVIDIA driver version via nvidia-smi") from exc
    if not value or "\n" in value:
        raise ContractError("C16 runtime runner requires exactly one driver-version value")
    return value


def load_binding(path: Path, *, canary: bool) -> dict[str, Any]:
    try:
        binding = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read frozen-binding receipt: {exc}") from exc
    required = (
        "schema_version", "scientific_eligible", "status", "deployment_id", "model_id",
        "model_revision", "tokenizer_revision", "scenario", "input", "model_path",
        "package_id", "package_fixed_commit", "package_manifest_sha256",
        "wheelhouse_manifest_sha256", "model_files",
    )
    if not isinstance(binding, dict) or any(key not in binding for key in required):
        raise ContractError("frozen-binding receipt lacks required identity fields")
    if binding["schema_version"] != "C16_G_RUNTIME_FROZEN_BINDING_V1" or binding["scientific_eligible"] is not False or binding["status"] != "FROZEN_RUNTIME_BINDING_READY":
        raise ContractError("frozen-binding receipt has an ineligible schema/state")
    scenario, input_data = binding["scenario"], binding["input"]
    if not isinstance(scenario, dict) or not isinstance(input_data, dict):
        raise ContractError("frozen-binding scenario/input is malformed")
    for key in ("scenario_id", "batch_size", "prefill_tokens", "decode_tokens"):
        if key not in scenario:
            raise ContractError(f"frozen-binding scenario lacks {key}")
    for key in ("raw_input_sha256", "derived_token_ids_path", "derived_token_ids_sha256", "target_token_ids_sha256"):
        if key not in input_data:
            raise ContractError(f"frozen-binding input lacks {key}")
    if canary and (scenario["scenario_id"], scenario["batch_size"], scenario["prefill_tokens"], scenario["decode_tokens"]) != ("S0", 1, 128, 4):
        raise ContractError("G0 canary must use the exact frozen S0/B1/T128/Decode4 binding")
    return binding


def load_token_ids(binding: dict[str, Any]) -> list[int]:
    path = Path(binding["input"]["derived_token_ids_path"])
    try:
        values = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read derived frozen token IDs: {exc}") from exc
    if not isinstance(values, list) or not values or any(not isinstance(value, int) or value < 0 for value in values):
        raise ContractError("derived frozen token IDs are malformed")
    if len(values) != binding["scenario"]["prefill_tokens"]:
        raise ContractError("derived frozen token length differs from scenario binding")
    actual_sha = hashlib.sha256(canonical_json(values).encode("utf-8")).hexdigest()
    if actual_sha != binding["input"]["target_token_ids_sha256"] or sha256_file(path) != binding["input"]["derived_token_ids_sha256"]:
        raise ContractError("derived frozen token IDs differ from the binding receipt")
    return values


def runtime_identity(binding: dict[str, Any], args: argparse.Namespace) -> dict[str, str]:
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
        "code_commit": git_head(),
    }


def dtype_for(torch: Any, name: str) -> Any:
    return {"float16": torch.float16, "bfloat16": torch.bfloat16}[name]


def decode_once(model: Any, prompt_ids: Any, decode_tokens: int, torch: Any) -> tuple[float, str]:
    """Run one complete prefill + cache-correct greedy decode with two syncs only."""
    torch.cuda.synchronize()
    started = time.perf_counter_ns()
    generated: list[int] = []
    with torch.inference_mode():
        torch.cuda.nvtx.range_push("C16_NATIVE_FULL_FORWARD")
        try:
            torch.cuda.nvtx.range_push("C16_PHASE_PREFILL")
            try:
                output = model(input_ids=prompt_ids, use_cache=True)
            finally:
                torch.cuda.nvtx.range_pop()
            past_key_values = output.past_key_values
            current_ids = output.logits[:, -1, :].argmax(dim=-1, keepdim=True)
            generated.extend(current_ids.detach().to("cpu").flatten().tolist())
            torch.cuda.nvtx.range_push("C16_PHASE_DECODE")
            try:
                for step in range(1, decode_tokens):
                    torch.cuda.nvtx.range_push(f"C16_DECODE_STEP_{step}")
                    try:
                        output = model(input_ids=current_ids, past_key_values=past_key_values, use_cache=True)
                    finally:
                        torch.cuda.nvtx.range_pop()
                    past_key_values = output.past_key_values
                    current_ids = output.logits[:, -1, :].argmax(dim=-1, keepdim=True)
                    generated.extend(current_ids.detach().to("cpu").flatten().tolist())
            finally:
                torch.cuda.nvtx.range_pop()
        finally:
            torch.cuda.nvtx.range_pop()
    torch.cuda.synchronize()
    if len(generated) != decode_tokens * int(prompt_ids.shape[0]):
        raise ContractError("native decode did not produce the frozen requested decode length")
    checksum = hashlib.sha256(canonical_json(generated).encode("utf-8")).hexdigest()
    return (time.perf_counter_ns() - started) / 1e6, checksum


def execute(binding: dict[str, Any], args: argparse.Namespace, budget: BudgetLease) -> dict[str, Any]:
    try:
        import torch
        from transformers import AutoModelForCausalLM
    except ImportError as exc:
        raise ContractError("hash-closed torch/transformers environment is unavailable") from exc
    if not torch.cuda.is_available():
        raise ContractError("CUDA unavailable; refusing CPU fallback")
    adapter = resolve_adapter(args.adapter, args.dtype, args.quantization)
    if adapter.model_loader != "TRANSFORMERS_CAUSAL_LM":
        raise ContractError("runtime-native runner only supports the raw Transformers deployment adapters")
    model_path = Path(binding["model_path"])
    if not model_path.is_dir():
        raise ContractError("bound local model path is absent")
    token_ids = load_token_ids(binding)
    identity = runtime_identity(binding, args)
    atomic_json(args.receipt.with_suffix(args.receipt.suffix + ".preflight.json"), {
        "schema_version": "C16_G_NATIVE_RECEIPT_V1",
        "stage_id": "C16-1.3" if args.mode == "canary" else "C16-2.1",
        "execution_mode": "PENDING_NATIVE_GPU",
        "scientific_eligible": False,
        "identity": identity,
        "runtime": {"device": "cuda:0", "profiler_mode": "UNPROFILED"},
        "checks": {"identity_persisted_before_gpu_operation": True, "cache_correct_decode_required": True},
        "artifacts": {"terminal_status": "PENDING"},
    })
    torch.cuda.reset_peak_memory_stats()
    telemetry_before = smi_row()
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path), local_files_only=True, torch_dtype=dtype_for(torch, args.dtype), trust_remote_code=False,
    )
    model.eval().to("cuda:0")
    parameter_devices = {parameter.device.type for parameter in model.parameters()}
    parameter_dtypes = {str(parameter.dtype).removeprefix("torch.") for parameter in model.parameters()}
    if parameter_devices != {"cuda"}:
        raise ContractError("model parameters are not all CUDA; refusing CPU/offload fallback")
    if parameter_dtypes != {args.dtype}:
        raise ContractError(f"model parameter dtype differs from bound request: {parameter_dtypes}")
    prompt = torch.tensor([token_ids] * int(binding["scenario"]["batch_size"]), device="cuda:0", dtype=torch.long)
    if prompt.device.type != "cuda":
        raise ContractError("frozen prompt IDs did not reach CUDA")
    observed_attention = str(getattr(model.config, "_attn_implementation", "UNRESOLVED"))
    if observed_attention in {"", "UNRESOLVED", "None"}:
        raise ContractError("runtime attention backend is unresolved")
    for _ in range(args.warmups):
        decode_once(model, prompt, int(binding["scenario"]["decode_tokens"]), torch)
        if budget.expired():
            raise ContractError("C16 budget elapsed during native warmup")
    results = []
    for _ in range(args.measures):
        results.append(decode_once(model, prompt, int(binding["scenario"]["decode_tokens"]), torch))
        if budget.expired():
            raise ContractError("C16 budget elapsed during native measurement")
    checksums = {checksum for _, checksum in results}
    if len(checksums) != 1:
        raise ContractError("native output checksum is non-deterministic within one frozen run")
    properties = torch.cuda.get_device_properties(0)
    telemetry_after = smi_row()
    durations = [duration for duration, _ in results]
    receipt = {
        "schema_version": "C16_G_NATIVE_RECEIPT_V1",
        "stage_id": "C16-1.3" if args.mode == "canary" else "C16-2.1",
        "execution_mode": "NATIVE_GPU",
        "scientific_eligible": True,
        "identity": identity,
        "runtime": {
            "device": "cuda:0",
            "gpu_name": properties.name,
            "gpu_uuid": smi_row().split(",", 1)[0],
            "driver_version": smi_driver_version(),
            "cuda_version": torch.version.cuda,
            "torch_version": torch.__version__,
            "attention_backend": f"TRANSFORMERS_CONFIG:{observed_attention}",
            "compile_state": "EAGER_UNCOMPILED",
            "profiler_mode": "UNPROFILED",
        },
        "checks": {
            "cuda_available": True,
            "model_all_cuda": True,
            "input_all_cuda": True,
            "parameter_dtype_set": sorted(parameter_dtypes),
            "output_checksum": next(iter(checksums)),
            "warmup_count": args.warmups,
            "measurement_count": args.measures,
            "cache_correct_decode": True,
            "execution_budget_ledger": str(args.budget_ledger),
            "execution_budget_max_elapsed_seconds": budget.max_elapsed_seconds,
            "frozen_binding_receipt": str(args.binding_receipt),
            "frozen_binding_sha256": sha256_file(args.binding_receipt),
            "package_id": binding["package_id"],
            "package_fixed_commit": binding["package_fixed_commit"],
            "package_manifest_sha256": binding["package_manifest_sha256"],
            "wheelhouse_manifest_sha256": binding["wheelhouse_manifest_sha256"],
            "bound_model_files": binding["model_files"],
            "token_receipt_sha256": binding["input"]["token_receipt_sha256"],
            "gpu_telemetry_before": telemetry_before,
            "gpu_telemetry_after": telemetry_after,
        },
        "artifacts": {
            "duration_ms": durations,
            "median_duration_ms": statistics.median(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "cv": statistics.pstdev(durations) / statistics.mean(durations) if len(durations) > 1 else 0.0,
            "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
            "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
            "terminal_status": "COMPLETE",
        },
    }
    validate_receipt(receipt, require_native=True)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("canary", "baseline"), required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--binding-receipt", type=Path, required=True)
    parser.add_argument("--execute-native", action="store_true")
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--implementation-key", required=True)
    parser.add_argument("--dtype", choices=("float16", "bfloat16"), required=True)
    parser.add_argument("--quantization", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--measures", type=int, default=3)
    parser.add_argument("--budget-ledger", type=Path, required=True)
    args = parser.parse_args()
    if not args.execute_native:
        parser.error("runtime-native runner has no mock mode; use the fixed offline runner for non-scientific fixtures")
    if args.warmups != 2 or args.measures not in (3, 4, 5):
        parser.error("C16 native baselines require 2 warmups and 3-5 retained measures")
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id:
            raise ValueError
    except ValueError:
        parser.error("--run-id must be a canonical UUID")
    binding = load_binding(args.binding_receipt, canary=args.mode == "canary")
    with BudgetLease(args.budget_ledger, runtime_identity(binding, args), f"NATIVE_{args.mode.upper()}", capture=False) as budget:
        receipt = execute(binding, args, budget)
        budget.finish(elapsed_seconds=budget.elapsed_seconds(), raw_bytes=0, terminal_status="COMPLETE")
    atomic_json(args.receipt, receipt)
    print(f"PASS C16 cache-correct native runner: {args.receipt}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 cache-correct native runner: {exc}", file=sys.stderr)
        raise SystemExit(2)
