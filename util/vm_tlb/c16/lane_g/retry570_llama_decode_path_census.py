#!/usr/bin/env python3
"""Diagnostic-only, phase-separated kernel census for frozen Llama decode.

This is deliberately not an NVBit capture.  It records the CUDA kernel names
observed by PyTorch's profiler for the frozen S0 prefill and each actual
cache-correct one-token decode forward.  The first logical output token is
derived from prefill by the immutable workload and therefore has no separate
CUDA decode forward to census.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, repo_root, sha256_file
from model_adapters import resolve_adapter
from runtime_native_runner import assert_cuda_residency, load_binding, load_runtime_model, load_token_ids, smi_driver_version


SCHEMA = "C16_G_NVBIT175_LLAMA_DECODE_PATH_CENSUS_V1"
EXPECTED_CHECKSUM = "2c9e006bcd155e56a28d2c9948a31cf2d5bc60e8bb2b5f5af0e1cae35215383f"


def git_head() -> str:
    return subprocess.check_output(["git", "-C", str(repo_root()), "rev-parse", "HEAD"], text=True).strip()


def require_frozen_binding(binding: dict[str, Any]) -> None:
    scenario = binding.get("scenario", {})
    if (binding.get("model_id"), binding.get("model_revision"), scenario.get("scenario_id"), scenario.get("batch_size"), scenario.get("prefill_tokens"), scenario.get("decode_tokens")) != (
        "meta-llama/Llama-3.2-1B", "4e20de362430cd3b72f300e6b0f18e50e7166e08", "S0", 1, 128, 4,
    ):
        raise ContractError("decode census accepts only the frozen Llama S0/B1/T128/decode4 binding")


def cuda_kernel_names(profile: Any, torch: Any) -> dict[str, int]:
    """Return only CUDA activity names; PyTorch profiler owns no NVBit trace."""
    cuda_type = torch.autograd.DeviceType.CUDA
    names: dict[str, int] = {}
    for event in profile.events():
        if getattr(event, "device_type", None) != cuda_type:
            continue
        name = str(getattr(event, "name", ""))
        if name:
            names[name] = names.get(name, 0) + 1
    return dict(sorted(names.items()))


def index_select_rows(names: dict[str, int]) -> list[dict[str, Any]]:
    return [{"kernel_name": name, "launch_count": count} for name, count in names.items() if "indexSelect" in name]


def profile_forward(model: Any, kwargs: dict[str, Any], torch: Any) -> tuple[Any, dict[str, int]]:
    with torch.inference_mode(), torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CUDA]) as profile:
        output = model(**kwargs)
        torch.cuda.synchronize()
    return output, cuda_kernel_names(profile, torch)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binding", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--adapter", default="llama32_1b")
    parser.add_argument("--implementation-key", default="TRANSFORMERS_CAUSAL_LM")
    parser.add_argument("--dtype", default="float16", choices=("float16", "bfloat16"))
    parser.add_argument("--quantization", default="NONE")
    parser.add_argument("--runtime-code-commit", required=True)
    parser.add_argument("--measurement-marker", type=Path, required=True)
    args = parser.parse_args()
    if args.runtime_code_commit != git_head():
        raise ContractError("decode census source commit differs from its declared commit")
    if args.receipt.exists():
        raise ContractError("decode census refuses to overwrite retained evidence")
    if args.measurement_marker.exists():
        raise ContractError("decode census refuses to overlap MEASUREMENT_ACTIVE")
    if os.environ.get("CUDA_INJECTION64_PATH") or os.environ.get("ACTIVE_FROM_START") not in {None, "0"}:
        raise ContractError("decode census forbids NVBit injection/capture environment")
    binding = load_binding(args.binding, canary=True)
    require_frozen_binding(binding)
    try:
        import torch
        if not torch.cuda.is_available():
            raise ContractError("CUDA unavailable; refusing CPU fallback")
        started_ns = time.monotonic_ns()
        torch.cuda.init()
        adapter = resolve_adapter(args.adapter, args.dtype, args.quantization)
        model, loader = load_runtime_model(adapter, Path(binding["model_path"]), torch, args.dtype, required_sequence_length=132)
        devices, dtypes = assert_cuda_residency(model, require_raw_dtype=args.dtype)
        attention = str(getattr(model.config, "_attn_implementation", "UNRESOLVED"))
        if attention != "sdpa":
            raise ContractError("decode census attention backend differs from frozen Llama contract")
        prompt = torch.tensor([load_token_ids(binding)], device="cuda:0", dtype=torch.long)
        output, prefill = profile_forward(model, {"input_ids": prompt, "use_cache": True}, torch)
        past = output.past_key_values
        current = output.logits[:, -1, :].argmax(dim=-1, keepdim=True)
        generated = current.detach().to("cpu").flatten().tolist()
        actual_decode: dict[str, dict[str, int]] = {}
        for step in range(1, 4):
            output, names = profile_forward(model, {"input_ids": current, "past_key_values": past, "use_cache": True}, torch)
            actual_decode[f"C16_DECODE_STEP_{step}"] = names
            past = output.past_key_values
            current = output.logits[:, -1, :].argmax(dim=-1, keepdim=True)
            generated.extend(current.detach().to("cpu").flatten().tolist())
        checksum = hashlib.sha256(canonical_json(generated).encode("utf-8")).hexdigest()
        if checksum != EXPECTED_CHECKSUM or len(generated) != 4:
            raise ContractError("decode census output differs from the frozen Llama workload")
        phases: dict[str, Any] = {
            "PREFILL": {"cuda_kernel_count": sum(prefill.values()), "index_select_kernels": index_select_rows(prefill)},
            "DECODE1": {"logical_coverage": "PREFILL_DERIVED_GREEDY_TOKEN_NO_SEPARATE_CUDA_FORWARD", "cuda_kernel_count": 0, "index_select_kernels": []},
        }
        for actual in range(1, 4):
            logical = f"DECODE{actual + 1}"
            names = actual_decode[f"C16_DECODE_STEP_{actual}"]
            phases[logical] = {"logical_coverage": f"C16_DECODE_STEP_{actual}", "cuda_kernel_count": sum(names.values()), "index_select_kernels": index_select_rows(names)}
        actual_rows = [row for phase in ("DECODE2", "DECODE3", "DECODE4") for row in phases[phase]["index_select_kernels"]]
        classifications = sorted({"LargeIndex" if "indexSelectLargeIndex" in row["kernel_name"] else "SmallIndex" if "indexSelectSmallIndex" in row["kernel_name"] else "OTHER_INDEXSELECT" for row in actual_rows})
        status = "DECODE_INDEXSELECT_CANDIDATE_OBSERVED" if actual_rows else "STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED_NO_DECODE_INDEXSELECT_OBSERVED"
        receipt = {
            "schema_version": SCHEMA, "status": status, "scientific_eligible_for_timing": False,
            "diagnostic_only": True, "no_nvbit_trace_or_instrumentation": True,
            "identity": {"deployment_id": binding["deployment_id"], "model_id": binding["model_id"], "model_revision": binding["model_revision"], "scenario_id": binding["scenario"]["scenario_id"], "input_hash": binding["input"]["raw_input_sha256"], "runtime_code_commit": git_head(), "implementation_key": args.implementation_key, "dtype": args.dtype, "quantization": args.quantization},
            "runtime": {"gpu_name": torch.cuda.get_device_properties(0).name, "gpu_uuid": subprocess.check_output(["nvidia-smi", "--query-gpu=uuid", "--format=csv,noheader"], text=True).strip(), "driver": smi_driver_version(), "torch": torch.__version__, "torch_cuda": torch.version.cuda, "attention_backend": attention, "loader": loader, "all_cuda_devices": sorted(devices), "parameter_dtypes": sorted(dtypes)},
            "binding_sha256": sha256_file(args.binding), "output_checksum": checksum,
            "large_index_prefill_target": {"function_class": "LARGE_INDEX_PREFILL_TARGET", "static_range": [101, 102], "decode_structural_zero": "STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED"},
            "phases": phases, "actual_decode_indexselect_classes": classifications,
            "requires_independent_nvbit_static_map_before_decode_capture": bool(actual_rows),
            "elapsed_seconds": (time.monotonic_ns() - started_ns) / 1_000_000_000,
            "terminal_status": "COMPLETE",
        }
        atomic_json(args.receipt, receipt)
        print("PASS " + status)
    finally:
        try:
            del model, prompt, output, past, current
        except UnboundLocalError:
            pass
        gc.collect()


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Llama decode path census: {exc}")
