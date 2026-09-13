#!/usr/bin/env python3
"""Emit one NVBit-native map for the observed Llama decode-side function.

The caller provides the exact full mangled name recovered by the no-NVBit
decode census.  This map-only diagnostic does not arm a measurement marker,
does not insert an instruction callback, and does not produce a memory trace.
It uses the separate recovery ledger and leaves the historical ledger intact.
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, repo_root, sha256_file
from model_adapters import resolve_adapter
from retry570_recovery_budget import RecoveryBudgetLease, initialize
from retry570_multimodel_capture import EXPECTED_CHECKSUM, run_full
from runtime_native_runner import assert_cuda_residency, load_binding, load_runtime_model, load_token_ids, smi_driver_version


SCHEMA = "C16_G_NVBIT175_LLAMA_DECODE_STATIC_MAP_V1"
DEPLOYMENT = "c16_nvbit175_recovery_llama32_1b_v1"


def git_head() -> str:
    return subprocess.check_output(["git", "-C", str(repo_root()), "rev-parse", "HEAD"], text=True).strip()


def require_frozen(binding: dict[str, Any]) -> None:
    scenario = binding.get("scenario", {})
    if (binding.get("model_id"), binding.get("model_revision"), scenario.get("scenario_id"), scenario.get("batch_size"), scenario.get("prefill_tokens"), scenario.get("decode_tokens")) != (
        "meta-llama/Llama-3.2-1B", "4e20de362430cd3b72f300e6b0f18e50e7166e08", "S0", 1, 128, 4,
    ):
        raise ContractError("decode static mapper accepts only frozen Llama S0/B1/T128/decode4")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binding", type=Path, required=True); parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--static-map", type=Path, required=True); parser.add_argument("--target-function", required=True)
    parser.add_argument("--recovery-ledger", type=Path, required=True); parser.add_argument("--historical-ledger", type=Path, required=True); parser.add_argument("--historical-ledger-sha256", required=True)
    parser.add_argument("--measurement-marker", type=Path, required=True); parser.add_argument("--run-id", required=True); parser.add_argument("--runtime-code-commit", required=True)
    parser.add_argument("--adapter", default="llama32_1b"); parser.add_argument("--implementation-key", default="TRANSFORMERS_CAUSAL_LM"); parser.add_argument("--dtype", default="float16", choices=("float16", "bfloat16")); parser.add_argument("--quantization", default="NONE")
    args = parser.parse_args()
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id: raise ValueError
    except ValueError:
        parser.error("--run-id must be canonical UUID")
    if args.runtime_code_commit != git_head(): raise ContractError("decode static-map source commit differs from declared commit")
    if args.receipt.exists() or args.static_map.exists(): raise ContractError("decode static map refuses to overwrite retained payload")
    if args.measurement_marker.exists(): raise ContractError("decode static map must not overlap MEASUREMENT_ACTIVE")
    if os.environ.get("CUDA_MODULE_LOADING") != "EAGER" or os.environ.get("ACTIVE_FROM_START") != "0": raise ContractError("decode static map requires EAGER and profiler-disabled tool state")
    if os.environ.get("C16_NVBIT_TARGET_FUNCTION_MANGLED") != args.target_function or os.environ.get("C16_NVBIT_STATIC_MAP_PATH") != str(args.static_map): raise ContractError("injected mapper does not bind exact decode function/map path")
    if os.environ.get("C16_NVBIT_TARGET_INSTR_INDEX") not in {None, ""}: raise ContractError("decode static map forbids instruction instrumentation")
    if not os.environ.get("CUDA_INJECTION64_PATH"): raise ContractError("decode static map requires the exact injected mapper")
    binding = load_binding(args.binding, canary=True); require_frozen(binding)
    initialize(recovery_ledger=args.recovery_ledger, historical_ledger=args.historical_ledger, expected_historical_sha256=args.historical_ledger_sha256, deployment_id=DEPLOYMENT)
    identity = {"deployment_id": DEPLOYMENT, "model_id": binding["model_id"], "model_revision": binding["model_revision"], "scenario_id": binding["scenario"]["scenario_id"], "input_hash": binding["input"]["raw_input_sha256"], "implementation_key": args.implementation_key, "dtype": args.dtype, "quantization": args.quantization, "run_id": args.run_id, "code_commit": git_head()}
    started = time.monotonic()
    with RecoveryBudgetLease(args.recovery_ledger, identity, "NVBIT", capture=False) as lease:
        try:
            import torch
            if not torch.cuda.is_available(): raise ContractError("CUDA unavailable; refusing CPU fallback")
            torch.cuda.init(); adapter = resolve_adapter(args.adapter, args.dtype, args.quantization)
            model, loader = load_runtime_model(adapter, Path(binding["model_path"]), torch, args.dtype, required_sequence_length=132)
            devices, dtypes = assert_cuda_residency(model, require_raw_dtype=args.dtype)
            attention = str(getattr(model.config, "_attn_implementation", "UNRESOLVED"))
            if attention != "sdpa": raise ContractError("decode static-map attention backend differs from frozen Llama contract")
            prompt = torch.tensor([load_token_ids(binding)], device="cuda:0", dtype=torch.long)
            checksum, decode_steps, _ = run_full(model, prompt, torch, phase="DECODE", capture=False)
            if checksum != EXPECTED_CHECKSUM or decode_steps != 4: raise ContractError("decode static map workload differs from frozen Llama contract")
            if not args.static_map.is_file() or args.static_map.stat().st_size == 0: raise ContractError("exact decode function did not emit an NVBit-native static map")
            receipt = {"schema_version": SCHEMA, "status": "DECODE_NVBIT_STATIC_MAP_PASS", "scientific_eligible_for_timing": False, "diagnostic_only": True,
                       "identity": identity, "binding_sha256": sha256_file(args.binding), "target_function_mangled": args.target_function,
                       "static_map": {"path": str(args.static_map), "size_bytes": args.static_map.stat().st_size, "sha256": sha256_file(args.static_map)},
                       "runtime": {"gpu_name": torch.cuda.get_device_properties(0).name, "gpu_uuid": subprocess.check_output(["nvidia-smi", "--query-gpu=uuid", "--format=csv,noheader"], text=True).strip(), "driver": smi_driver_version(), "torch": torch.__version__, "torch_cuda": torch.version.cuda, "attention_backend": attention, "loader": loader, "all_cuda_devices": sorted(devices), "parameter_dtypes": sorted(dtypes)},
                       "output_checksum": checksum, "decode_steps_executed": decode_steps, "measurement_active_created": False, "instruction_instrumentation": False, "trace_emission": False, "terminal_status": "COMPLETE"}
            atomic_json(args.receipt, receipt)
            lease.finish(elapsed_seconds=lease.elapsed_seconds(), raw_bytes=0, terminal_status="COMPLETE", evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC", diagnostic_reason="DECODE_SIDE_EXACT_FUNCTION_NVBIT_NATIVE_STATIC_MAP")
            print("PASS DECODE_NVBIT_STATIC_MAP_PASS")
        except Exception:
            lease.finish(elapsed_seconds=lease.elapsed_seconds(), raw_bytes=0, terminal_status="FAILED_OR_ABORTED", evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC", diagnostic_reason="DECODE_SIDE_EXACT_FUNCTION_NVBIT_NATIVE_STATIC_MAP_FAILURE")
            raise
        finally:
            try: del model, prompt
            except UnboundLocalError: pass
            gc.collect()


if __name__ == "__main__":
    try: main()
    except ContractError as exc: raise SystemExit(f"FAIL Llama decode static map: {exc}")
