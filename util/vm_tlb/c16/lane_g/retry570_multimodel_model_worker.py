#!/usr/bin/env python3
"""One frozen full-model C16 workload worker, initially for S1 no-trace gate."""
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
from execution_budget import BudgetLease, MeasurementActive
from runtime_native_runner import assert_cuda_residency, decode_once, load_binding, load_runtime_model, smi_driver_version
from model_adapters import resolve_adapter

SCHEMA = "C16_G_RETRY570_MULTIMODEL_MODEL_WORKER_V1"
NO_TRACE_RANGE = "999999-999999@^$"


def git_head() -> str:
    return subprocess.check_output(["git", "-C", str(repo_root()), "rev-parse", "HEAD"], text=True).strip()


def trace_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and path.name.endswith((".trace", ".trace.xz")))


def stage(path: Path, event: str, **fields: Any) -> None:
    value = {"schema_version": SCHEMA, "event": event, "ts_ns": time.monotonic_ns(), **fields}
    atomic_json(path, value); print("C16_MULTIMODEL_MODEL " + json.dumps(value, sort_keys=True), flush=True)


def identity(binding: dict[str, Any], args: argparse.Namespace) -> dict[str, str]:
    return {"deployment_id": binding["deployment_id"], "model_id": binding["model_id"], "model_revision": binding["model_revision"],
            "tokenizer_revision": binding["tokenizer_revision"], "scenario_id": binding["scenario"]["scenario_id"],
            "input_hash": binding["input"]["raw_input_sha256"], "implementation_key": args.implementation_key,
            "dtype": args.dtype, "quantization": args.quantization, "run_id": args.run_id, "code_commit": git_head()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binding", type=Path, required=True); parser.add_argument("--receipt", type=Path, required=True); parser.add_argument("--stage", type=Path, required=True); parser.add_argument("--trace-root", type=Path, required=True); parser.add_argument("--budget-ledger", type=Path, required=True)
    parser.add_argument("--adapter", required=True); parser.add_argument("--implementation-key", required=True); parser.add_argument("--dtype", choices=("float16", "bfloat16"), required=True); parser.add_argument("--quantization", required=True); parser.add_argument("--run-id", required=True); parser.add_argument("--runtime-code-commit", required=True); parser.add_argument("--expected-attention-backend")
    args = parser.parse_args()
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id: raise ValueError
    except ValueError: parser.error("--run-id must be canonical UUID")
    if args.runtime_code_commit != git_head(): raise ContractError("runtime source commit differs from checkout")
    if os.environ.get("CUDA_MODULE_LOADING") != "EAGER" or os.environ.get("DYNAMIC_KERNEL_RANGE") != NO_TRACE_RANGE:
        raise ContractError("S1 requires EAGER and the frozen impossible no-trace range")
    if args.trace_root.exists() or args.receipt.exists() or args.stage.exists(): raise ContractError("S1 refuses to overwrite a prior payload")
    if not args.binding.is_file(): raise ContractError("frozen binding receipt absent")
    binding = load_binding(args.binding, canary=True)
    if (binding["scenario"]["scenario_id"], binding["scenario"]["batch_size"], binding["scenario"]["prefill_tokens"], binding["scenario"]["decode_tokens"]) != ("S0", 1, 128, 4):
        raise ContractError("campaign S1 requires frozen Llama S0/B1/T128/decode4")
    if binding["model_id"] != "meta-llama/Llama-3.2-1B" or binding["model_revision"] != "4e20de362430cd3b72f300e6b0f18e50e7166e08":
        raise ContractError("campaign S1 only accepts the C0-frozen Llama identity")
    args.trace_root.mkdir(parents=True)
    MeasurementActive.assert_available(args.budget_ledger)
    ident = identity(binding, args)
    with BudgetLease(args.budget_ledger, ident, "MULTIMODEL_S1_FULL_MODEL_NO_TRACE", capture=False) as lease:
        stage(args.stage, "PROCESS_START", identity=ident)
        try:
            import torch
            if not torch.cuda.is_available(): raise ContractError("CUDA unavailable; refusing CPU fallback")
            stage(args.stage, "RUNTIME_INIT_BEGIN"); torch.cuda.init(); stage(args.stage, "RUNTIME_INIT_END")
            adapter = resolve_adapter(args.adapter, args.dtype, args.quantization)
            stage(args.stage, "MODEL_LOAD_BEGIN")
            model, loader = load_runtime_model(adapter, Path(binding["model_path"]), torch, args.dtype, required_sequence_length=132)
            devices, dtypes = assert_cuda_residency(model, require_raw_dtype=args.dtype)
            attention = str(getattr(model.config, "_attn_implementation", "UNRESOLVED"))
            if attention in {"", "UNRESOLVED", "None"} or (args.expected_attention_backend and attention != args.expected_attention_backend):
                raise ContractError("attention backend is unresolved or differs from frozen contract")
            stage(args.stage, "MODEL_LOAD_END", attention_backend=attention)
            token_ids = json.loads(Path(binding["input"]["derived_token_ids_path"]).read_text(encoding="utf-8"))
            prompt = torch.tensor([token_ids], dtype=torch.long, device="cuda:0")
            torch.cuda.synchronize(); stage(args.stage, "FULL_WORKLOAD_BEGIN")
            duration_ms, checksum = decode_once(model, prompt, 4, torch)
            stage(args.stage, "FULL_WORKLOAD_END", output_checksum=checksum)
            traces = trace_files(args.trace_root)
            if traces: raise ContractError("S1 no-trace workload emitted a trace")
            receipt = {"schema_version": SCHEMA, "status": "S1_FULL_MODEL_NO_TRACE_PASS", "scientific_eligible": False, "identity": ident,
                       "binding_sha256": sha256_file(args.binding), "runtime": {"gpu_name": torch.cuda.get_device_properties(0).name, "gpu_uuid": subprocess.check_output(["nvidia-smi", "--query-gpu=uuid", "--format=csv,noheader"], text=True).strip(), "driver": smi_driver_version(), "torch": torch.__version__, "torch_cuda": torch.version.cuda, "attention_backend": attention, "loader": loader},
                       "workload": {"prefill_tokens": 128, "decode_steps": 4, "output_checksum": checksum, "duration_ms": duration_ms, "all_cuda_devices": sorted(devices), "parameter_dtypes": sorted(dtypes)},
                       "prewarm_trace_count": 0, "trace_file_count": 0, "measurement_active_created": False, "terminal_status": "COMPLETE"}
            lease.finish(elapsed_seconds=lease.elapsed_seconds(), raw_bytes=0, terminal_status="COMPLETE", evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC", diagnostic_reason="MULTIMODEL_S1_FULL_MODEL_NO_TRACE_RUNTIME_PREWARM")
            atomic_json(args.receipt, receipt); stage(args.stage, "TERMINAL_COMPLETE")
        except Exception:
            lease.finish(elapsed_seconds=lease.elapsed_seconds(), raw_bytes=0, terminal_status="FAILED_OR_ABORTED", evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC", diagnostic_reason="MULTIMODEL_S1_FULL_MODEL_NO_TRACE_FAILURE")
            raise
        finally:
            try:
                del model, prompt
            except UnboundLocalError:
                pass
            gc.collect()


if __name__ == "__main__":
    try: main()
    except ContractError as exc: raise SystemExit(f"FAIL multi-model S1 worker: {exc}")
