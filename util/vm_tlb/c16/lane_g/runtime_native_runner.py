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
import fcntl
import hashlib
import json
import os
import statistics
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, repo_root, sha256_file
from execution_budget import BudgetLease, MEASUREMENT_ACTIVE_SCHEMA, MeasurementActive
from model_adapters import resolve_adapter
from run_schema import validate_receipt


class WrapperOwnedBudget:
    """Bound a runner launched inside an already-ledgered profiler wrapper.

    The profiler wrapper holds the sole `BudgetLease` for the child process
    and records the operation.  Acquiring it again in the child would create
    a deliberate nonblocking-lock failure.  This object preserves the
    wrapper's remaining wall-time ceiling for warmup/measure checks without
    creating a second ledger entry.
    """

    def __init__(self, max_elapsed_seconds: float) -> None:
        if max_elapsed_seconds <= 0:
            raise ContractError("wrapper-supplied C16 budget ceiling is invalid")
        self.max_elapsed_seconds = max_elapsed_seconds
        self._started = time.monotonic()

    def expired(self) -> bool:
        return time.monotonic() - self._started >= self.max_elapsed_seconds


PARENT_LEASE_FIELDS = (
    "schema_version", "state", "parent_lease_id", "lease_token_sha256", "ledger_path",
    "max_elapsed_seconds", "valid_until_unix", "identity", "operation_kind", "wrapper_pid",
)


def wrapper_owned_budget(args: argparse.Namespace, identity: dict[str, str]) -> tuple[WrapperOwnedBudget, dict[str, Any]]:
    """Prove the child is inside the live, single wrapper-owned budget lease.

    Environment variables alone are not an authority: the immutable start
    receipt must bind a secret token, exact run identity and ledger path, and
    the ledger's advisory lock must be held by another process while the child
    starts.  A standalone child therefore either obtains its own lease or
    fails closed; it cannot select wrapper mode as a budget bypass.
    """
    if args.parent_lease_receipt is None:
        raise ContractError("wrapper-owned budget mode requires an explicit parent lease receipt")
    environment_receipt = os.environ.get("C16_G_PARENT_LEASE_RECEIPT")
    token = os.environ.get("C16_G_PARENT_LEASE_TOKEN")
    if environment_receipt != str(args.parent_lease_receipt) or not token:
        raise ContractError("wrapper-owned budget mode lacks the active parent receipt/token environment")
    try:
        parent = json.loads(args.parent_lease_receipt.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read parent lease receipt: {exc}") from exc
    if not isinstance(parent, dict) or any(field not in parent for field in PARENT_LEASE_FIELDS):
        raise ContractError("parent lease receipt is incomplete")
    if parent["schema_version"] != "C16_G_PARENT_LEASE_V1" or parent["state"] != "ACTIVE_IMMUTABLE_START_RECEIPT":
        raise ContractError("parent lease receipt is not an active C16 wrapper session")
    if parent["ledger_path"] != str(args.budget_ledger) or parent["identity"] != identity:
        raise ContractError("parent lease receipt does not bind this exact child ledger/identity")
    if not isinstance(parent["max_elapsed_seconds"], (int, float)) or float(parent["max_elapsed_seconds"]) <= 0:
        raise ContractError("parent lease receipt has an invalid elapsed-time ceiling")
    if not isinstance(parent["valid_until_unix"], (int, float)) or time.time() > float(parent["valid_until_unix"]):
        raise ContractError("parent lease receipt has expired")
    if hashlib.sha256(token.encode("utf-8")).hexdigest() != parent["lease_token_sha256"]:
        raise ContractError("parent lease token does not match its immutable receipt")
    lock_path = args.budget_ledger.with_name(args.budget_ledger.name + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as lock_handle:
        try:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            pass
        else:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
            raise ContractError("parent lease receipt exists but the shared budget ledger is not locked")
    return WrapperOwnedBudget(float(parent["max_elapsed_seconds"])), parent


def wrapper_measurement_marker(args: argparse.Namespace, identity: dict[str, str]) -> Path:
    """Require a child runner to observe the live marker owned by its wrapper."""
    marker_text = os.environ.get("C16_G_MEASUREMENT_ACTIVE_MARKER")
    expected = args.budget_ledger.parent.parent / "control" / "MEASUREMENT_ACTIVE"
    if marker_text != str(expected):
        raise ContractError("wrapper-owned budget mode lacks its expected active measurement marker")
    try:
        marker = json.loads(expected.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read active wrapper measurement marker: {exc}") from exc
    if (
        marker.get("schema_version") != MEASUREMENT_ACTIVE_SCHEMA
        or marker.get("ledger_path") != str(args.budget_ledger)
        or marker.get("deployment_id") != identity.get("deployment_id")
        or marker.get("run_id") != identity.get("run_id")
    ):
        raise ContractError("active measurement marker does not bind this wrapper-owned child")
    return expected


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


def load_runtime_model(adapter: Any, model_path: Path, torch: Any, dtype: str, *, required_sequence_length: int) -> tuple[Any, dict[str, Any]]:
    """Load only the adapter explicitly named by the frozen deployment.

    AWQ is intentionally not substituted with a raw Transformers load.  Its
    packed parameter dtypes are implementation data rather than the requested
    floating-point compute dtype, so that branch reports the exact AutoAWQ load
    contract instead of applying the raw-model dtype assertion to packed weights.
    """
    if required_sequence_length <= 0:
        raise ContractError("frozen scenario has an invalid required sequence length")
    if adapter.model_loader == "TRANSFORMERS_CAUSAL_LM":
        try:
            from transformers import AutoModelForCausalLM
        except ImportError as exc:
            raise ContractError("hash-closed transformers environment is unavailable") from exc
        model = AutoModelForCausalLM.from_pretrained(
            str(model_path), local_files_only=True, torch_dtype=dtype_for(torch, dtype), trust_remote_code=False,
        )
        model.eval().to("cuda:0")
        return model, {
            "adapter_loader": adapter.model_loader,
            "quantization_implementation": "NONE_TRANSFORMERS_LOCAL_FILES_ONLY",
            "requested_dtype": dtype,
            "required_sequence_length": required_sequence_length,
            "cpu_offload_forbidden": True,
        }
    if adapter.model_loader == "AUTOAWQ_CAUSAL_LM":
        try:
            from awq import AutoAWQForCausalLM
        except ImportError as exc:
            raise ContractError("AutoAWQ is absent; AWQ is not silently substituted with a raw adapter") from exc
        # ``fuse_layers=False`` keeps the qualified standalone model structure;
        # device_map is deliberately a single CUDA device with no offload folder.
        awq = AutoAWQForCausalLM.from_quantized(
            str(model_path), max_seq_len=required_sequence_length, fuse_layers=False,
            trust_remote_code=False, safetensors=True, device_map="cuda:0",
        )
        model = getattr(awq, "model", None)
        if model is None:
            raise ContractError("AutoAWQ quantized load did not expose its CUDA causal-LM model")
        model.eval()
        return model, {
            "adapter_loader": adapter.model_loader,
            "quantization_implementation": "AUTOAWQ_FROM_QUANTIZED_FUSE_FALSE",
            "requested_dtype": dtype,
            "required_sequence_length": required_sequence_length,
            "device_map": "cuda:0",
            "cpu_offload_forbidden": True,
        }
    raise ContractError(f"unsupported runtime-native adapter loader: {adapter.model_loader}")


def assert_cuda_residency(model: Any, *, require_raw_dtype: str | None) -> tuple[set[str], set[str]]:
    """Reject CPU/meta/offloaded parameters or material buffers before inference."""
    parameter_devices = {parameter.device.type for parameter in model.parameters()}
    parameter_dtypes = {str(parameter.dtype).removeprefix("torch.") for parameter in model.parameters()}
    if parameter_devices != {"cuda"}:
        raise ContractError("model parameters are not all CUDA; refusing CPU/offload fallback")
    buffer_devices = {buffer.device.type for _name, buffer in model.named_buffers() if buffer.numel()}
    if buffer_devices and buffer_devices != {"cuda"}:
        raise ContractError("model buffers are not all CUDA; refusing CPU/offload fallback")
    device_map = getattr(model, "hf_device_map", None)
    if device_map is not None:
        if not isinstance(device_map, dict) or any(str(device) not in {"cuda:0", "0"} for device in device_map.values()):
            raise ContractError("model device map is not an all-cuda:0 deployment")
    if require_raw_dtype is not None and parameter_dtypes != {require_raw_dtype}:
        raise ContractError(f"model parameter dtype differs from bound request: {parameter_dtypes}")
    return parameter_devices, parameter_dtypes


def is_cuda_oom(error: BaseException) -> bool:
    """Recognize only CUDA allocator failures for explicit resource admission."""
    return error.__class__.__name__ == "OutOfMemoryError" or "CUDA out of memory" in str(error)


def resource_admission_receipt(identity: dict[str, str], args: argparse.Namespace, error: BaseException) -> dict[str, Any]:
    """Record an OOM as an explicit no-substitution resource result, not timing."""
    return {
        "schema_version": "C16_G_RESOURCE_ADMISSION_V1",
        "stage_id": "C16-2.1",
        "status": "SKIPPED_RESOURCE",
        "scientific_eligible": False,
        "identity": identity,
        "reason": "CUDA_OOM_RESOURCE_ADMISSION_NO_CPU_OFFLOAD_OR_SHAPE_SUBSTITUTION",
        "error_class": error.__class__.__name__,
        "constraints": {
            "cpu_offload_forbidden": True,
            "frozen_context_batch_decode_unchanged": True,
            "timing_result_emitted": False,
        },
    }


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
    except ImportError as exc:
        raise ContractError("hash-closed torch environment is unavailable") from exc
    if not torch.cuda.is_available():
        raise ContractError("CUDA unavailable; refusing CPU fallback")
    adapter = resolve_adapter(args.adapter, args.dtype, args.quantization)
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
        "checks": {
            "identity_persisted_before_gpu_operation": True,
            "cache_correct_decode_required": True,
            "measurement_active_guard": getattr(args, "measurement_active_guard", False),
            "measurement_active_marker": str(getattr(args, "measurement_active_marker", "NA")),
        },
        "artifacts": {"terminal_status": "PENDING"},
    })
    torch.cuda.reset_peak_memory_stats()
    telemetry_before = smi_row()
    required_sequence_length = int(binding["scenario"]["prefill_tokens"]) + int(binding["scenario"]["decode_tokens"])
    model, loader_evidence = load_runtime_model(
        adapter, model_path, torch, args.dtype, required_sequence_length=required_sequence_length,
    )
    _parameter_devices, parameter_dtypes = assert_cuda_residency(
        model,
        require_raw_dtype=args.dtype if adapter.model_loader == "TRANSFORMERS_CAUSAL_LM" else None,
    )
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
            "adapter_load_evidence": loader_evidence,
            "output_checksum": next(iter(checksums)),
            "warmup_count": args.warmups,
            "measurement_count": args.measures,
            "cache_correct_decode": True,
            "execution_budget_ledger": str(args.budget_ledger),
            "execution_budget_max_elapsed_seconds": budget.max_elapsed_seconds,
            "execution_budget_ownership": "PROFILER_WRAPPER" if args.budget_owned_by_wrapper else "RUNNER",
            "measurement_active_guard": getattr(args, "measurement_active_guard", False),
            "measurement_active_marker": str(getattr(args, "measurement_active_marker", "NA")),
            "parent_lease_receipt": str(args.parent_lease_receipt) if args.budget_owned_by_wrapper else "NA",
            "parent_lease_receipt_sha256": sha256_file(args.parent_lease_receipt) if args.budget_owned_by_wrapper else "NA",
            "parent_lease_id": args.parent_lease["parent_lease_id"] if args.budget_owned_by_wrapper else "NA",
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
    parser.add_argument("--budget-owned-by-wrapper", action="store_true")
    parser.add_argument("--parent-lease-receipt", type=Path)
    args = parser.parse_args()
    if not args.execute_native:
        parser.error("runtime-native runner has no mock mode; use the fixed offline runner for non-scientific fixtures")
    if args.warmups != 2 or args.measures not in (3, 4, 5):
        parser.error("C16 native baselines require 2 warmups and 3-5 retained measures")
    if args.budget_owned_by_wrapper != (args.parent_lease_receipt is not None):
        parser.error("wrapper-owned budget mode requires --parent-lease-receipt, and vice versa")
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id:
            raise ValueError
    except ValueError:
        parser.error("--run-id must be a canonical UUID")
    binding = load_binding(args.binding_receipt, canary=args.mode == "canary")
    if args.budget_owned_by_wrapper:
        budget, args.parent_lease = wrapper_owned_budget(args, runtime_identity(binding, args))
        args.measurement_active_marker = wrapper_measurement_marker(args, runtime_identity(binding, args))
        args.measurement_active_guard = True
        try:
            receipt = execute(binding, args, budget)
        except Exception as exc:
            if not is_cuda_oom(exc):
                raise
            raise ContractError("wrapper-owned native runner hit CUDA OOM; wrapper must preserve its terminal resource result") from exc
    else:
        with BudgetLease(args.budget_ledger, runtime_identity(binding, args), f"NATIVE_{args.mode.upper()}", capture=False) as budget:
            with MeasurementActive(args.budget_ledger, runtime_identity(binding, args), f"NATIVE_{args.mode.upper()}") as active:
                args.measurement_active_marker = active.path
                args.measurement_active_guard = True
                try:
                    receipt = execute(binding, args, budget)
                except Exception as exc:
                    if not is_cuda_oom(exc):
                        raise
                    identity = runtime_identity(binding, args)
                    budget.finish(
                        elapsed_seconds=budget.elapsed_seconds(), raw_bytes=0,
                        terminal_status="SKIPPED_RESOURCE",
                        evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC",
                        diagnostic_reason="CUDA_OOM_RESOURCE_ADMISSION_NO_CPU_OFFLOAD",
                    )
                    skip = resource_admission_receipt(identity, args, exc)
                    skip_path = args.receipt.with_name(args.receipt.name + ".resource_admission.json")
                    atomic_json(skip_path, skip)
                    print(f"SKIPPED_RESOURCE C16 cache-correct native runner: {skip_path}")
                    return
                budget.finish(elapsed_seconds=budget.elapsed_seconds(), raw_bytes=0, terminal_status="COMPLETE")
    atomic_json(args.receipt, receipt)
    print(f"PASS C16 cache-correct native runner: {args.receipt}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 cache-correct native runner: {exc}", file=sys.stderr)
        raise SystemExit(2)
