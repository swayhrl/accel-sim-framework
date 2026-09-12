#!/usr/bin/env python3
"""Emit direct module-identity NVTX ranges for a non-timing C16 semantic pass.

This runner is intentionally separate from ``runtime_native_runner.py``.  It
loads a bound model once, executes exactly one warmup and one captured
cache-correct decode, and never records timing samples.  Its output is a
diagnostic receipt, not a baseline or a census performance receipt.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import re
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, sha256_file
from execution_budget import BudgetLease, MeasurementActive
from model_adapters import resolve_adapter
from runtime_native_runner import (
    assert_cuda_residency, git_head, load_binding, load_runtime_model, load_token_ids,
    runtime_identity, smi_driver_version, smi_row, wrapper_measurement_marker,
    wrapper_owned_budget,
)


LAYER_PATTERN = re.compile(r"(?:^|\.)layers\.(\d+)(?:\.|$)")
TAG_PREFIX = "C16_DIRECT_SEMANTIC_V1"


@dataclass(frozen=True)
class ModuleSemantic:
    module_path: str
    module_class: str
    layer_id: str
    operator: str
    operator_detail: str

    def tag(self, identity: dict[str, str]) -> str:
        fields = (
            ("run_id", identity["run_id"]),
            ("deployment_id", identity["deployment_id"]),
            ("scenario_id", identity["scenario_id"]),
            ("layer_id", self.layer_id),
            ("operator", self.operator),
            ("operator_detail", self.operator_detail),
            ("module_path", self.module_path),
            ("module_class", self.module_class),
        )
        if any("|" in value or "=" in value for _, value in fields):
            raise ContractError("direct semantic module identity has an unsafe NVTX delimiter")
        return "|".join([TAG_PREFIX, *(f"{key}={value}" for key, value in fields)])


def direct_module_semantic(module_path: str, module_class: str) -> ModuleSemantic | None:
    """Classify only a direct runtime module identity, never a CUDA kernel name."""
    if not module_path:
        return None
    lower = module_path.lower()
    class_lower = module_class.lower()
    layer = LAYER_PATTERN.search(module_path)
    layer_id = layer.group(1) if layer else "OUTPUT"
    tail = lower.rsplit(".", 1)[-1]
    if tail in {"embed_tokens", "embed_in"} or class_lower.endswith("embedding"):
        return ModuleSemantic(module_path, module_class, "EMBEDDING_OUTPUT", "EMBEDDING_OUTPUT", "NONE")
    if "self_attn" in lower or ".attention" in lower:
        detail = {
            "q_proj": "Q_PROJ", "k_proj": "K_PROJ", "v_proj": "V_PROJ", "o_proj": "O_PROJ",
        }.get(tail, "ATTENTION_CORE")
        return ModuleSemantic(module_path, module_class, layer_id, "ATTENTION", detail)
    if ".mlp" in lower or ".feed_forward" in lower:
        detail = {
            "gate_proj": "GATE", "up_proj": "UP", "down_proj": "DOWN",
        }.get(tail, "FFN_CORE")
        return ModuleSemantic(module_path, module_class, layer_id, "FFN", detail)
    if "norm" in lower or "norm" in class_lower:
        return ModuleSemantic(module_path, module_class, layer_id, "NORM", "NONE")
    return None


def attach_direct_module_ranges(model: Any, torch: Any, identity: dict[str, str]) -> tuple[list[Any], list[ModuleSemantic]]:
    """Attach paired hooks to direct module objects; unrecognized modules remain absent."""
    hooks: list[Any] = []
    semantics: list[ModuleSemantic] = []
    for module_path, module in model.named_modules():
        semantic = direct_module_semantic(module_path, module.__class__.__name__)
        if semantic is None:
            continue
        tag = semantic.tag(identity)
        # PyTorch treats a non-None hook result as a replacement input/output.
        # NVTX returns an implementation value, so the hook must explicitly
        # discard it instead of changing model semantics.
        def push_range(_module: Any, _inputs: Any, *, tag: str = tag) -> None:
            torch.cuda.nvtx.range_push(tag)
            return None

        def pop_range(_module: Any, _inputs: Any, _output: Any) -> None:
            torch.cuda.nvtx.range_pop()
            return None

        hooks.append(module.register_forward_pre_hook(push_range))
        hooks.append(module.register_forward_hook(pop_range))
        semantics.append(semantic)
    if not semantics:
        raise ContractError("no direct module identities were eligible for semantic NVTX instrumentation")
    return hooks, semantics


def semantic_decode(model: Any, prompt_ids: Any, decode_tokens: int, torch: Any) -> str:
    """One cache-correct decode without a timer or retained timing samples."""
    generated: list[int] = []
    with torch.inference_mode():
        torch.cuda.nvtx.range_push("C16_DIRECT_SEMANTIC_CAPTURE")
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
    if len(generated) != decode_tokens * int(prompt_ids.shape[0]):
        raise ContractError("semantic diagnostic did not produce the bound decode length")
    return hashlib.sha256(canonical_json(generated).encode("utf-8")).hexdigest()


def execute(binding: dict[str, Any], args: argparse.Namespace, budget: Any) -> dict[str, Any]:
    try:
        import torch
    except ImportError as exc:
        raise ContractError("hash-closed torch environment is unavailable") from exc
    if not torch.cuda.is_available():
        raise ContractError("CUDA unavailable; refusing CPU fallback")
    adapter = resolve_adapter(args.adapter, args.dtype, args.quantization)
    identity = runtime_identity(binding, args)
    if identity["code_commit"] != git_head():
        raise ContractError("semantic runner source commit is not hash-addressable")
    token_ids = load_token_ids(binding)
    model_path = Path(binding["model_path"])
    if not model_path.is_dir():
        raise ContractError("bound local model path is absent")
    atomic_json(args.receipt.with_suffix(args.receipt.suffix + ".preflight.json"), {
        "schema_version": "C16_G_DIRECT_SEMANTIC_RECEIPT_V1",
        "status": "SEMANTIC_DIAGNOSTIC_PENDING",
        "scientific_eligible": False,
        "scientific_eligible_for_timing": False,
        "identity": identity,
    })
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
    observed_attention = str(getattr(model.config, "_attn_implementation", "UNRESOLVED"))
    if prompt.device.type != "cuda" or observed_attention in {"", "UNRESOLVED", "None"}:
        raise ContractError("semantic runner has unresolved CUDA input or attention backend")
    # Warmup occurs before hooks and has no timing output.  It is deliberately not semantic evidence.
    warmup_checksum = semantic_decode(model, prompt, int(binding["scenario"]["decode_tokens"]), torch)
    hooks, semantics = attach_direct_module_ranges(model, torch, identity)
    try:
        torch.cuda.synchronize()
        evidence_checksum = semantic_decode(model, prompt, int(binding["scenario"]["decode_tokens"]), torch)
        torch.cuda.synchronize()
    finally:
        for hook in reversed(hooks):
            hook.remove()
    if warmup_checksum != evidence_checksum:
        raise ContractError("semantic diagnostic output checksum differs from its pre-hook warmup")
    properties = torch.cuda.get_device_properties(0)
    telemetry_after = smi_row()
    del prompt, model
    gc.collect()
    torch.cuda.synchronize()
    return {
        "schema_version": "C16_G_DIRECT_SEMANTIC_RECEIPT_V1",
        "stage_id": "C16-SEMANTIC-1",
        "status": "SEMANTIC_DIAGNOSTIC_ONLY_COMPLETE",
        "scientific_eligible": False,
        "scientific_eligible_for_timing": False,
        "identity": identity,
        "runtime": {
            "device": "cuda:0", "gpu_name": properties.name, "gpu_uuid": smi_row().split(",", 1)[0],
            "driver_version": smi_driver_version(), "cuda_version": torch.version.cuda,
            "torch_version": torch.__version__, "attention_backend": f"TRANSFORMERS_CONFIG:{observed_attention}",
            "compile_state": "EAGER_UNCOMPILED", "profiler_mode": "NSYS_DIRECT_SEMANTIC_DIAGNOSTIC",
        },
        "checks": {
            "semantic_pass_classification": "SEMANTIC_DIAGNOSTIC_ONLY",
            "not_for_native_timing": True,
            "timing_samples_recorded": False,
            "direct_module_identity_only": True,
            "kernel_name_heuristic_forbidden": True,
            "duration_semantic_guessing_forbidden": True,
            "historical_operator_backfill_forbidden": True,
            "module_range_schema": TAG_PREFIX,
            "direct_module_hook_count": len(semantics),
            "direct_module_categories": sorted({f"{item.operator}:{item.operator_detail}" for item in semantics}),
            "output_checksum": evidence_checksum,
            "cache_correct_decode": True,
            "model_all_cuda": True,
            "input_all_cuda": True,
            "parameter_dtype_set": sorted(parameter_dtypes),
            "adapter_load_evidence": loader_evidence,
            "frozen_binding_receipt": str(args.binding_receipt),
            "frozen_binding_sha256": sha256_file(args.binding_receipt),
            "package_id": binding["package_id"],
            "package_fixed_commit": binding["package_fixed_commit"],
            "package_manifest_sha256": binding["package_manifest_sha256"],
            "parent_lease_receipt": str(args.parent_lease_receipt) if args.budget_owned_by_wrapper else "NA",
            "parent_lease_receipt_sha256": sha256_file(args.parent_lease_receipt) if args.budget_owned_by_wrapper else "NA",
            "parent_lease_id": args.parent_lease["parent_lease_id"] if args.budget_owned_by_wrapper else "NA",
            "measurement_active_guard": getattr(args, "measurement_active_guard", False),
            "measurement_active_marker": str(getattr(args, "measurement_active_marker", "NA")),
            "gpu_telemetry_before": telemetry_before,
            "gpu_telemetry_after": telemetry_after,
        },
        "artifacts": {"terminal_status": "COMPLETE", "semantic_decode_count": 1, "warmup_decode_count": 1},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--binding-receipt", type=Path, required=True)
    parser.add_argument("--execute-semantic", action="store_true")
    parser.add_argument("--adapter", required=True)
    parser.add_argument("--implementation-key", required=True)
    parser.add_argument("--dtype", choices=("float16", "bfloat16"), required=True)
    parser.add_argument("--quantization", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--budget-ledger", type=Path, required=True)
    parser.add_argument("--budget-owned-by-wrapper", action="store_true")
    parser.add_argument("--parent-lease-receipt", type=Path)
    args = parser.parse_args()
    if not args.execute_semantic:
        parser.error("direct semantic runner has no mock/native-timing mode; use --execute-semantic")
    if args.budget_owned_by_wrapper != (args.parent_lease_receipt is not None):
        parser.error("wrapper-owned semantic mode requires --parent-lease-receipt, and vice versa")
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id:
            raise ValueError
    except ValueError:
        parser.error("--run-id must be a canonical UUID")
    binding = load_binding(args.binding_receipt, canary=False)
    identity = runtime_identity(binding, args)
    if args.budget_owned_by_wrapper:
        budget, args.parent_lease = wrapper_owned_budget(args, identity)
        args.measurement_active_marker = wrapper_measurement_marker(args, identity)
        args.measurement_active_guard = True
        receipt = execute(binding, args, budget)
    else:
        with BudgetLease(args.budget_ledger, identity, "NSYS_DIRECT_SEMANTIC", capture=False) as budget:
            with MeasurementActive(args.budget_ledger, identity, "NSYS_DIRECT_SEMANTIC") as active:
                args.measurement_active_marker = active.path
                args.measurement_active_guard = True
                receipt = execute(binding, args, budget)
                budget.finish(
                    elapsed_seconds=budget.elapsed_seconds(), raw_bytes=0, terminal_status="COMPLETE",
                    evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC", diagnostic_reason="SEMANTIC_DIAGNOSTIC_ONLY",
                )
    atomic_json(args.receipt, receipt)
    print(f"PASS C16 direct semantic diagnostic: {args.receipt}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 direct semantic diagnostic: {exc}", file=sys.stderr)
        raise SystemExit(2)
