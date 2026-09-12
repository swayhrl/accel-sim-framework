#!/usr/bin/env python3
"""Unified C16 native runner. Offline modes are intentionally non-scientific."""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, SCHEMA_VERSION, atomic_json, repo_root
from execution_budget import BudgetLease
from model_adapters import resolve_adapter
from run_schema import validate_receipt


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "-C", str(repo_root()), "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNRESOLVED_CODE_COMMIT"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("canary", "baseline", "census"), required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--mock", action="store_true", help="write a non-scientific fixture receipt; never imports torch")
    parser.add_argument("--execute-native", action="store_true", help="allow real local-files-only CUDA inference")
    parser.add_argument("--adapter", default="qwen25_05b")
    parser.add_argument("--model-id", default="fixture/mock-model")
    parser.add_argument("--model-revision", default="fixture-immutable-revision")
    parser.add_argument("--tokenizer-revision", default="fixture-immutable-tokenizer")
    parser.add_argument("--deployment-id", default="C16_MOCK_DEPLOYMENT")
    parser.add_argument("--implementation-key", default="MOCK_IMPLEMENTATION")
    parser.add_argument("--dtype", choices=("float16", "bfloat16"), default="float16")
    parser.add_argument("--quantization", default="NONE")
    parser.add_argument("--scenario-id", default="S0")
    parser.add_argument("--input-hash", default="0" * 64)
    parser.add_argument("--run-id", default="C16_G_MOCK_RUN")
    parser.add_argument("--model-path", type=Path)
    parser.add_argument("--input-token-ids", type=Path)
    parser.add_argument("--attention-backend", default="MOCK_NO_GPU")
    parser.add_argument("--compile-state", default="EAGER_UNCOMPILED")
    parser.add_argument("--decode-tokens", type=int, default=4)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--measures", type=int, default=3)
    parser.add_argument("--budget-ledger", type=Path)
    args = parser.parse_args()
    if args.mock == args.execute_native:
        parser.error("choose exactly one of --mock or --execute-native")
    if args.decode_tokens < 1 or args.warmups < 0 or args.measures < 1:
        parser.error("decode-tokens/measures must be positive and warmups non-negative")
    if args.execute_native and (args.model_path is None or args.input_token_ids is None):
        parser.error("--execute-native requires --model-path and --input-token-ids")
    if args.execute_native and args.attention_backend in {"", "MOCK_NO_GPU", "UNRESOLVED"}:
        parser.error("--execute-native requires direct --attention-backend evidence")
    if args.execute_native and args.budget_ledger is None:
        parser.error("--execute-native requires the shared C16 --budget-ledger")
    if args.mode == "baseline" and args.execute_native and (args.warmups != 2 or args.measures not in (3, 4, 5)):
        parser.error("native baseline requires 2 warmups and 3-5 retained measures")
    return args


def identity(args: argparse.Namespace) -> dict[str, str]:
    return {
        "model_id": args.model_id,
        "model_revision": args.model_revision,
        "tokenizer_revision": args.tokenizer_revision,
        "deployment_id": args.deployment_id,
        "implementation_key": args.implementation_key,
        "dtype": args.dtype,
        "quantization": args.quantization,
        "scenario_id": args.scenario_id,
        "input_hash": args.input_hash,
        "run_id": args.run_id,
        "code_commit": git_head(),
    }


def mock_receipt(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "stage_id": "C16-0.4",
        "execution_mode": "MOCK",
        "scientific_eligible": False,
        "identity": identity(args),
        "runtime": {"device": "MOCK_NO_GPU", "profiler_mode": "MOCK_NO_GPU"},
        "checks": {
            "no_gpu_operation": True,
            "no_model_load": True,
            "placeholder_output_checksum": hashlib.sha256(args.run_id.encode()).hexdigest(),
        },
        "artifacts": {"kind": "OFFLINE_FIXTURE_ONLY", "catalog_import_forbidden": True},
    }


def load_token_ids(path: Path) -> list[int]:
    try:
        values = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read frozen input token IDs: {path}: {exc}") from exc
    if not isinstance(values, list) or not values or any(not isinstance(value, int) or value < 0 for value in values):
        raise ContractError("input token receipt must be a non-empty JSON list of non-negative IDs")
    return values


def torch_dtype(torch: Any, name: str) -> Any:
    return {"float16": torch.float16, "bfloat16": torch.bfloat16}[name]


def checksum_tensor(tensor: Any) -> str:
    values = tensor.detach().to("cpu").contiguous().numpy().tobytes()
    return hashlib.sha256(values).hexdigest()


def nvidia_smi_uuid() -> str:
    try:
        value = subprocess.check_output(["nvidia-smi", "--query-gpu=uuid", "--format=csv,noheader"], text=True).splitlines()[0].strip()
    except (OSError, subprocess.CalledProcessError, IndexError) as exc:
        raise ContractError("cannot record GPU UUID via nvidia-smi") from exc
    if not value or value == "N/A":
        raise ContractError("nvidia-smi returned no GPU UUID")
    return value


def run_once(model: Any, input_ids: Any, decode_tokens: int, torch: Any) -> tuple[float, str]:
    torch.cuda.synchronize()
    started = time.perf_counter_ns()
    with torch.inference_mode():
        current = input_ids
        output = None
        torch.cuda.nvtx.range_push("C16_NATIVE_FORWARD")
        try:
            for _step in range(decode_tokens):
                output = model(input_ids=current, use_cache=True)
                token = output.logits[:, -1, :].argmax(dim=-1, keepdim=True)
                current = token
        finally:
            torch.cuda.nvtx.range_pop()
    torch.cuda.synchronize()
    assert output is not None
    return (time.perf_counter_ns() - started) / 1e6, checksum_tensor(output.logits[:, -1, :])


def native_receipt(args: argparse.Namespace, budget: BudgetLease) -> dict[str, Any]:
    try:
        import torch
    except ImportError as exc:
        raise ContractError("PyTorch is absent; import the hash-closed wheelhouse before C16-1") from exc
    if not torch.cuda.is_available():
        raise ContractError("CUDA unavailable; refusing CPU fallback")
    adapter = resolve_adapter(args.adapter, args.dtype, args.quantization)
    if not args.model_path or not args.model_path.is_dir():
        raise ContractError("model path is not an imported local directory")
    token_ids = load_token_ids(args.input_token_ids)
    initial = {
        "schema_version": SCHEMA_VERSION,
        "stage_id": "C16-1.3" if args.mode == "canary" else "C16-2.1",
        "execution_mode": "PENDING_NATIVE_GPU",
        "scientific_eligible": False,
        "identity": identity(args),
        "runtime": {"device": "cuda:0", "profiler_mode": "UNPROFILED"},
        "checks": {"identity_persisted_before_gpu_operation": True},
        "artifacts": {"terminal_status": "PENDING"},
    }
    atomic_json(args.receipt.with_suffix(args.receipt.suffix + ".preflight.json"), initial)
    dtype = torch_dtype(torch, args.dtype)
    torch.cuda.reset_peak_memory_stats()
    if adapter.model_loader == "TRANSFORMERS_CAUSAL_LM":
        try:
            from transformers import AutoModelForCausalLM
        except ImportError as exc:
            raise ContractError("transformers is absent from the hash-closed wheelhouse") from exc
        model = AutoModelForCausalLM.from_pretrained(str(args.model_path), local_files_only=True, torch_dtype=dtype, trust_remote_code=False)
        model.eval().to("cuda:0")
    elif adapter.model_loader == "AUTOAWQ_CAUSAL_LM":
        try:
            from awq import AutoAWQForCausalLM
        except ImportError as exc:
            raise ContractError("AutoAWQ is absent; AWQ is not silently substituted with a raw adapter") from exc
        awq = AutoAWQForCausalLM.from_quantized(str(args.model_path), fuse_layers=False, trust_remote_code=False, safetensors=True, device_map="cuda:0")
        model = awq.model
        model.eval()
    else:
        raise ContractError(f"unsupported adapter loader: {adapter.model_loader}")
    if any(parameter.device.type != "cuda" for parameter in model.parameters()):
        raise ContractError("model has non-CUDA parameters; refusing mixed/CPU fallback")
    input_ids = torch.tensor([token_ids], device="cuda:0", dtype=torch.long)
    if input_ids.device.type != "cuda":
        raise ContractError("input IDs did not reach CUDA")
    for _ in range(args.warmups):
        run_once(model, input_ids, args.decode_tokens, torch)
        if budget.expired():
            raise ContractError("C16 GPU-active budget expired during native warmup")
    measurements = []
    for _ in range(args.measures):
        measurements.append(run_once(model, input_ids, args.decode_tokens, torch))
        if budget.expired():
            raise ContractError("C16 GPU-active budget expired during native measurement")
    durations = [item[0] for item in measurements]
    checksums = {item[1] for item in measurements}
    if len(checksums) != 1:
        raise ContractError("native output checksum is non-deterministic within the frozen run")
    device = torch.cuda.get_device_properties(0)
    runtime = {
        "device": "cuda:0",
        "gpu_name": device.name,
        "gpu_uuid": nvidia_smi_uuid(),
        "driver_version": torch.cuda.driver_version,
        "cuda_version": torch.version.cuda,
        "torch_version": torch.__version__,
        "attention_backend": args.attention_backend,
            "compile_state": args.compile_state,
            "profiler_mode": "UNPROFILED",
            "adapter_loader": adapter.model_loader,
    }
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "stage_id": "C16-1.3" if args.mode == "canary" else "C16-2.1",
        "execution_mode": "NATIVE_GPU",
        "scientific_eligible": True,
        "identity": identity(args),
        "runtime": runtime,
        "checks": {
            "cuda_available": True,
            "model_all_cuda": True,
            "input_all_cuda": True,
            "output_checksum": next(iter(checksums)),
            "warmup_count": args.warmups,
            "measurement_count": args.measures,
            "execution_budget_ledger": str(args.budget_ledger),
            "execution_budget_max_elapsed_seconds": budget.max_elapsed_seconds,
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
    args = parse_args()
    if args.mock:
        receipt = mock_receipt(args)
    else:
        with BudgetLease(args.budget_ledger, identity(args), f"NATIVE_{args.mode.upper()}", capture=False) as budget:
            receipt = native_receipt(args, budget)
            budget.finish(elapsed_seconds=budget.elapsed_seconds(), raw_bytes=0, terminal_status="COMPLETE")
    validate_receipt(receipt, require_native=args.execute_native)
    atomic_json(args.receipt, receipt)
    print(f"PASS C16 Lane G {receipt['execution_mode']} receipt: {args.receipt}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 Lane G contract: {exc}", file=sys.stderr)
        raise SystemExit(2)
