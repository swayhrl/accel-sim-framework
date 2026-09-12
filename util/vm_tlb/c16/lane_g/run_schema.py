#!/usr/bin/env python3
"""Validation for G receipts before they can enter a scientific catalog."""
from __future__ import annotations

from typing import Any

from c16_native_common import ContractError, SCHEMA_VERSION, require_exact_keys


IDENTITY_FIELDS = (
    "model_id", "model_revision", "tokenizer_revision", "deployment_id",
    "implementation_key", "dtype", "quantization", "scenario_id", "input_hash",
    "run_id", "code_commit",
)
RUNTIME_FIELDS = (
    "device", "gpu_uuid", "driver_version", "cuda_version", "torch_version",
    "attention_backend", "compile_state", "profiler_mode",
)
RECEIPT_FIELDS = (
    "schema_version", "stage_id", "execution_mode", "scientific_eligible", "identity",
    "runtime", "checks", "artifacts",
)


def validate_receipt(receipt: dict[str, Any], *, require_native: bool = False) -> None:
    require_exact_keys(receipt, RECEIPT_FIELDS, "receipt")
    if receipt["schema_version"] != SCHEMA_VERSION:
        raise ContractError("unexpected receipt schema version")
    if not isinstance(receipt["identity"], dict) or not isinstance(receipt["runtime"], dict):
        raise ContractError("receipt identity/runtime must be objects")
    require_exact_keys(receipt["identity"], IDENTITY_FIELDS, "identity")
    if require_native:
        if receipt["execution_mode"] != "NATIVE_GPU" or receipt["scientific_eligible"] is not True:
            raise ContractError("native receipt is not scientifically eligible")
        require_exact_keys(receipt["runtime"], RUNTIME_FIELDS, "runtime")
        if not str(receipt["runtime"]["device"]).startswith("cuda"):
            raise ContractError("native receipt reports a non-CUDA device")
        if receipt["runtime"]["profiler_mode"] == "CPU_FALLBACK":
            raise ContractError("CPU fallback is forbidden for native C16 results")
    else:
        if receipt["execution_mode"] not in {"DRY_RUN", "MOCK"}:
            raise ContractError("offline receipt must explicitly be DRY_RUN or MOCK")
        if receipt["scientific_eligible"] is not False:
            raise ContractError("offline receipt cannot be scientific evidence")


def schema_markdown() -> str:
    return """# C16 Lane G run / receipt schema

Every runner, profiler, and capture receipt uses `C16_G_NATIVE_RECEIPT_V1`. Before any GPU operation, `identity` must close `model_id`, immutable model/tokenizer revisions, deployment/implementation, dtype/quantization, scenario/input hash, run ID, and code commit. Native receipts additionally record CUDA device/UUID, driver, CUDA/PyTorch, attention backend, compile state, and profiler mode.

`NATIVE_GPU` with `scientific_eligible=true` is the only scientific native mode. `DRY_RUN` and `MOCK` receipts are deliberately `scientific_eligible=false`; their placeholder output must never be imported into a native catalog. A CPU fallback, dtype change, backend change, or incomplete identity invalidates the run rather than silently creating a result.

Kernel/counter/trace target receipts additionally bind phase, decode-step bin, device/context/stream/correlation, kernel name, implementation, grid/block, semantic evidence, and the revalidated run ID. A naked launch ordinal is never a capture key.
"""
