#!/usr/bin/env python3
"""Parent-owned, phase-separated formal NVBit capture for frozen C16 models.

This runner intentionally supports only the already-frozen Llama S0 contract.
It keeps the model/input/runtime immutable while separating model prewarm from
the profiler-owned capture window.  The parent owns the only budget lease;
the child proves the active parent receipt/token and cannot be called as an
unledgered standalone capture.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import secrets
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, repo_root, sha256_file
from execution_budget import BudgetLease, MeasurementActive
from model_adapters import resolve_adapter
from profiler_wrapper import write_parent_lease_closeout, write_parent_lease_start
from retry570_recovery_budget import RecoveryBudgetLease, initialize as initialize_recovery_budget
from retry570_long_watch import nvdisasm_environment_contract
from runtime_native_runner import (
    assert_cuda_residency,
    load_binding,
    load_runtime_model,
    load_token_ids,
    smi_driver_version,
    wrapper_measurement_marker,
    wrapper_owned_budget,
)

SCHEMA = "C16_G_RETRY570_MULTIMODEL_FORMAL_CAPTURE_V1"
MODES = ("S3_NARROW_PREFILL", "S4_REPRO_PREFILL", "S5_COMPLETE_PREFILL", "S5_COMPLETE_DECODE")
TARGET_ROLES = ("LARGE_INDEX_PREFILL", "DECODE_INDEX_TARGET", "RECOVERY_PREFILL", "RECOVERY_DECODE")
EXPECTED_CHECKSUM = "2c9e006bcd155e56a28d2c9948a31cf2d5bc60e8bb2b5f5af0e1cae35215383f"
TERM_GRACE_S = 5


def git_head() -> str:
    return subprocess.check_output(["git", "-C", str(repo_root()), "rev-parse", "HEAD"], text=True).strip()


def trace_files(root: Path) -> list[Path]:
    return sorted(item for item in root.rglob("*") if item.is_file() and item.name.endswith((".trace", ".trace.xz")))


def write_event(path: Path, event: str, **fields: Any) -> None:
    row = {"schema_version": SCHEMA, "event": event, "ts_ns": time.monotonic_ns(), **fields}
    atomic_json(path, row)
    with path.with_suffix(path.suffix + ".jsonl").open("a", encoding="utf-8") as handle:
        handle.write(canonical_json(row) + "\n")
    print("C16_MULTIMODEL_CAPTURE " + canonical_json(row), flush=True)


def capture_phase(mode: str) -> str:
    return "DECODE" if mode == "S5_COMPLETE_DECODE" else "PREFILL"


def identity(binding: dict[str, Any], args: argparse.Namespace) -> dict[str, str]:
    return {
        "deployment_id": args.recovery_deployment_id or binding["deployment_id"], "model_id": binding["model_id"],
        "model_revision": binding["model_revision"], "tokenizer_revision": binding["tokenizer_revision"],
        "scenario_id": binding["scenario"]["scenario_id"], "input_hash": binding["input"]["raw_input_sha256"],
        "implementation_key": args.implementation_key, "dtype": args.dtype,
        "quantization": args.quantization, "run_id": args.run_id, "code_commit": git_head(),
    }


def require_contract(binding: dict[str, Any], target: dict[str, Any], target_role: str, *, recovery_v3_generic: bool,
                     direct_function_binding: Path | None = None) -> None:
    scenario = binding["scenario"]
    if not recovery_v3_generic and (binding["model_id"], binding["model_revision"], scenario["scenario_id"], scenario["batch_size"], scenario["prefill_tokens"], scenario["decode_tokens"]) != (
        "meta-llama/Llama-3.2-1B", "4e20de362430cd3b72f300e6b0f18e50e7166e08", "S0", 1, 128, 4,
    ):
        raise ContractError("formal capture refuses a non-frozen Llama S0/B1/T128/decode4 contract")
    try:
        instruction = target["target_instruction"]
        function = target["function"]
        index = int(instruction["nvbit_static_index"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ContractError("closed target receipt is malformed") from exc
    if recovery_v3_generic:
        if target_role not in {"RECOVERY_PREFILL", "RECOVERY_DECODE"} or direct_function_binding is None or not direct_function_binding.is_file():
            raise ContractError("Recovery V3 capture requires an exact phase role and direct-function binding receipt")
        direct = json.loads(direct_function_binding.read_text(encoding="utf-8"))
        if direct.get("status") != "DIRECT_FUNCTION_BINDING_READY_FOR_STATIC_MAP":
            raise ContractError("Recovery V3 direct-function binding is not closed for static-map capture")
        phase = "PREFILL" if target_role == "RECOVERY_PREFILL" else "DECODE"
        rows = [row for row in direct.get("bindings", []) if row.get("phase") == phase]
        if len(rows) != 1 or rows[0].get("direct_function_mangled_name") != function.get("mangled_name"):
            raise ContractError("Recovery V3 map target does not exactly match the phase direct-function binding")
        if rows[0].get("deployment_id") != binding["deployment_id"] or rows[0].get("scenario_id") != scenario["scenario_id"]:
            raise ContractError("Recovery V3 direct-function binding identity differs from capture binding")
        if int(instruction.get("nvbit_static_index", -1)) != index or not instruction.get("opcode") or instruction.get("memory_space") != "GLOBAL" or not instruction.get("has_mref"):
            raise ContractError("Recovery V3 target lacks a directly selected GLOBAL memory instruction")
    elif target_role == "LARGE_INDEX_PREFILL":
        if index != 101 or instruction.get("opcode") != "LDG.E.U16" or "indexSelectLargeIndex" not in function.get("mangled_name", ""):
            raise ContractError("formal Llama prefill target differs from the S2 direct NVBit map")
        if 34 not in target.get("excluded_static_indices", []) or index == 34:
            raise ContractError("historical SASS text line 34 must remain excluded from formal static-index capture")
    elif target_role == "DECODE_INDEX_TARGET":
        # This is an independently profiled/map-selected shape-dependent
        # decode target.  It must never silently reuse LargeIndex/[101,102).
        if index != 17 or instruction.get("opcode") != "LDG.E" or "indexSelectSmallIndex" not in function.get("mangled_name", ""):
            raise ContractError("decode target differs from the direct SmallIndex NVBit map")
    else:
        raise ContractError("unknown formal Llama capture target role")


def run_full(model: Any, prompt: Any, torch: Any, *, decode_tokens: int, phase: str, capture: bool, trace_root: Path | None = None) -> tuple[str, int, dict[str, list[str]]]:
    """Execute the frozen complete workload, capturing only one phase.

    Decode capture necessarily computes the causal prefill outside the ROI to
    establish its scenario-local KV state.  It then captures every remaining
    cache-correct decode forward; no scenario state survives this function.
    """
    cudart = torch.cuda.cudart()
    generated: list[int] = []
    phase_files: dict[str, list[str]] = {"PREFILL": [], **{f"DECODE{step}": [] for step in range(1, decode_tokens + 1)}}
    with torch.inference_mode():
        torch.cuda.nvtx.range_push("C16_NATIVE_FULL_FORWARD")
        try:
            torch.cuda.nvtx.range_push("C16_PHASE_PREFILL")
            try:
                if phase == "PREFILL" and capture:
                    before = {str(path) for path in trace_files(trace_root)} if trace_root is not None else set()
                    if cudart.cudaProfilerStart() != 0: raise ContractError("cudaProfilerStart failed for PREFILL")
                output = model(input_ids=prompt, use_cache=True)
                torch.cuda.synchronize()
                if phase == "PREFILL" and capture:
                    if cudart.cudaProfilerStop() != 0: raise ContractError("cudaProfilerStop failed for PREFILL")
                    phase_files["PREFILL"] = [str(path) for path in trace_files(trace_root) if str(path) not in before] if trace_root is not None else []
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
                        if phase == "DECODE" and capture:
                            before = {str(path) for path in trace_files(trace_root)} if trace_root is not None else set()
                            if cudart.cudaProfilerStart() != 0: raise ContractError(f"cudaProfilerStart failed for DECODE{step}")
                        output = model(input_ids=current_ids, past_key_values=past_key_values, use_cache=True)
                        torch.cuda.synchronize()
                        if phase == "DECODE" and capture:
                            if cudart.cudaProfilerStop() != 0: raise ContractError(f"cudaProfilerStop failed for DECODE{step}")
                            # The frozen decode_once contract emits its first
                            # greedy token from PREFILL, then runs three
                            # cache-correct CUDA decode forwards.  Preserve
                            # that workload: logical Decode2..4 map to these
                            # three forwards, while logical Decode1 is the
                            # prefill-derived token and has no separate CUDA
                            # launch window to trace.
                            phase_files[f"DECODE{step + 1}"] = [str(path) for path in trace_files(trace_root) if str(path) not in before] if trace_root is not None else []
                    finally:
                        torch.cuda.nvtx.range_pop()
                    past_key_values = output.past_key_values
                    current_ids = output.logits[:, -1, :].argmax(dim=-1, keepdim=True)
                    generated.extend(current_ids.detach().to("cpu").flatten().tolist())
            finally:
                torch.cuda.nvtx.range_pop()
        finally:
            torch.cuda.nvtx.range_pop()
    if len(generated) != decode_tokens:
        raise ContractError("frozen decode did not execute the required generated-token count")
    return hashlib.sha256(canonical_json(generated).encode("utf-8")).hexdigest(), decode_tokens, phase_files


def parse_traces(root: Path, target: dict[str, Any]) -> list[dict[str, Any]]:
    function = target["function"]["mangled_name"]
    result: list[dict[str, Any]] = []
    for trace in trace_files(root):
        if trace.suffix == ".xz":
            raise ContractError("formal Route-E parser requires uncompressed bounded trace payloads")
        text = trace.read_text(encoding="utf-8", errors="replace")
        headers = {line.split(" = ", 1)[0]: line.split(" = ", 1)[1] for line in text.splitlines() if line.startswith("-") and " = " in line}
        rows = [line for line in text.splitlines() if line and not line.startswith(("-", "#"))]
        if headers.get("-kernel name") != function or not rows or "#traces format" not in text:
            raise ContractError(f"trace schema/function identity does not bind target: {trace}")
        addresses = sum("0x" in row for row in rows)
        if addresses == 0:
            raise ContractError(f"target trace has no address-bearing memory records: {trace}")
        result.append({"path": str(trace), "size_bytes": trace.stat().st_size, "sha256": sha256_file(trace),
                       "kernel_id": int(headers["-kernel id"]), "function": function,
                       "record_count": len(rows), "address_record_count": addresses})
    return result


def child(args: argparse.Namespace) -> int:
    if args.runtime_code_commit != git_head(): raise ContractError("child source commit differs from parent-bound commit")
    if os.environ.get("CUDA_MODULE_LOADING") != "EAGER" or os.environ.get("ACTIVE_FROM_START") != "0":
        raise ContractError("formal capture requires EAGER plus profiler-owned ACTIVE_FROM_START=0")
    binding = load_binding(args.binding, canary=not args.recovery_v3_generic)
    target = json.loads(args.target_receipt.read_text(encoding="utf-8")); require_contract(binding, target, args.target_role, recovery_v3_generic=args.recovery_v3_generic, direct_function_binding=args.direct_function_binding)
    if args.target_role in {"DECODE_INDEX_TARGET", "RECOVERY_DECODE"} and capture_phase(args.mode) != "DECODE":
        raise ContractError("decode-side target may only be captured in the complete decode workload")
    ident = identity(binding, args)
    _budget, parent = wrapper_owned_budget(args, ident)
    write_event(args.stage, "PROCESS_START", identity=ident, parent_lease_id=parent["parent_lease_id"])
    import torch
    if not torch.cuda.is_available(): raise ContractError("CUDA unavailable; refusing CPU fallback")
    torch.cuda.init(); write_event(args.stage, "RUNTIME_INIT_COMPLETE")
    adapter = resolve_adapter(args.adapter, args.dtype, args.quantization)
    required_sequence_length = int(binding["scenario"]["prefill_tokens"]) + int(binding["scenario"]["decode_tokens"])
    model, loader = load_runtime_model(adapter, Path(binding["model_path"]), torch, args.dtype, required_sequence_length=required_sequence_length)
    devices, dtypes = assert_cuda_residency(model, require_raw_dtype=args.dtype)
    attention = str(getattr(model.config, "_attn_implementation", "UNRESOLVED"))
    if attention != args.expected_attention_backend: raise ContractError("attention backend differs from frozen S1/S2 evidence")
    prompt = torch.tensor([load_token_ids(binding)], device="cuda:0", dtype=torch.long)
    torch.cuda.synchronize(); write_event(args.stage, "PREWARM_BEGIN")
    checksum, decode_steps, _prewarm_phase_files = run_full(model, prompt, torch, decode_tokens=int(binding["scenario"]["decode_tokens"]), phase=capture_phase(args.mode), capture=False)
    expected_checksum = args.expected_output_checksum or EXPECTED_CHECKSUM
    if checksum != expected_checksum: raise ContractError("no-trace prewarm checksum differs from frozen runtime binding")
    if trace_files(args.trace_root): raise ContractError("prewarm emitted formal trace before parent arm")
    write_event(args.stage, "LANE_G_RUNTIME_READY", prewarm_trace_count=0, output_checksum=checksum)
    deadline = time.monotonic() + args.arm_wait_seconds
    while not args.arm_path.exists():
        if time.monotonic() >= deadline: raise ContractError("parent did not arm formal capture after READY")
        time.sleep(0.02)
    arm = json.loads(args.arm_path.read_text(encoding="utf-8"))
    if arm.get("run_id") != args.run_id or arm.get("parent_lease_id") != parent["parent_lease_id"] or arm.get("capture_phase") != capture_phase(args.mode):
        raise ContractError("formal capture arm does not bind the active parent session/phase")
    marker = wrapper_measurement_marker(args, ident)
    if trace_files(args.trace_root): raise ContractError("formal trace exists before CAPTURE_BEGIN")
    write_event(args.stage, "CAPTURE_BEGIN", capture_phase=capture_phase(args.mode), marker=str(marker))
    checksum, decode_steps, phase_files = run_full(model, prompt, torch, decode_tokens=int(binding["scenario"]["decode_tokens"]), phase=capture_phase(args.mode), capture=True, trace_root=args.trace_root)
    if checksum != expected_checksum: raise ContractError("captured workload checksum differs from frozen runtime binding")
    write_event(args.stage, "CAPTURE_END", output_checksum=checksum, decode_steps=decode_steps)
    traces = parse_traces(args.trace_root, target)
    by_path = {item["path"]: item for item in traces}
    phase_summary = {name: {"trace_file_count": len(paths), "record_count": sum(by_path[path]["record_count"] for path in paths), "address_record_count": sum(by_path[path]["address_record_count"] for path in paths)} for name, paths in phase_files.items()}
    if len({path for paths in phase_files.values() for path in paths}) != len(traces):
        raise ContractError("formal phase sidecar does not uniquely account for each captured target trace")
    # Decode has an explicit zero-occurrence outcome when the exact target is
    # absent from all four executed decode steps.  Prefill/canary must observe
    # at least one direct address-bearing record.
    if capture_phase(args.mode) == "PREFILL" and not traces:
        raise ContractError("prefill target capture emitted no exact target trace")
    if args.target_role in {"DECODE_INDEX_TARGET", "RECOVERY_DECODE"}:
        if any(phase_summary[f"DECODE{i}"]["record_count"] <= 0 for i in range(2, decode_steps + 1)):
            raise ContractError("decode-side target did not produce records in every actual frozen decode forward")
    atomic_json(args.child_receipt, {"schema_version": SCHEMA, "status": "FORMAL_CAPTURE_COMPLETE", "scientific_eligible": True,
        "identity": ident, "parent_lease": {"start_receipt": str(args.parent_lease_receipt), "sha256": sha256_file(args.parent_lease_receipt), "parent_lease_id": parent["parent_lease_id"], "child_acquired_second_lease": False},
        "binding_sha256": sha256_file(args.binding), "target_receipt": {"path": str(args.target_receipt), "sha256": sha256_file(args.target_receipt), "target_role": args.target_role, "function": target["function"]["mangled_name"], "static_index": target["target_instruction"]["nvbit_static_index"], "opcode": target["target_instruction"]["opcode"]},
        "runtime": {"gpu_name": torch.cuda.get_device_properties(0).name, "gpu_uuid": subprocess.check_output(["nvidia-smi", "--query-gpu=uuid", "--format=csv,noheader"], text=True).strip(), "driver": smi_driver_version(), "torch": torch.__version__, "torch_cuda": torch.version.cuda, "attention_backend": attention, "loader": loader, "all_cuda_devices": sorted(devices), "parameter_dtypes": sorted(dtypes)},
        "capture": {"mode": args.mode, "phase": capture_phase(args.mode), "decode_steps_executed": decode_steps, "logical_decode_coverage": {"DECODE1": "PREFILL_DERIVED_GREEDY_TOKEN_NO_SEPARATE_CUDA_FORWARD", **{f"DECODE{i}": f"C16_DECODE_STEP_{i - 1}" for i in range(2, decode_steps + 1)}}, "prewarm_trace_count": 0, "trace_file_count": len(traces), "traces": traces, "phase_trace_summary": phase_summary, "output_checksum": checksum, "measurement_marker_observed": str(marker), "terminal_status": "COMPLETE"}})
    write_event(args.stage, "TERMINAL_COMPLETE", trace_file_count=len(traces))
    del model, prompt; gc.collect()
    return 0


def kill_group(process: subprocess.Popen[str]) -> dict[str, Any]:
    result = {"required": False, "term_sent": False, "kill_sent": False, "grace_s": TERM_GRACE_S}
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM); result.update(required=True, term_sent=True)
        try: process.wait(timeout=TERM_GRACE_S)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL); result["kill_sent"] = True; process.wait(timeout=TERM_GRACE_S)
    return result


def child_command(args: argparse.Namespace) -> list[str]:
    command = [sys.executable, str(Path(__file__).resolve()), "--child", "--mode", args.mode, "--target-role", args.target_role, "--binding", str(args.binding), "--target-receipt", str(args.target_receipt), "--receipt", str(args.receipt), "--stage", str(args.stage), "--child-receipt", str(args.child_receipt), "--trace-root", str(args.trace_root), "--budget-ledger", str(args.budget_ledger), "--parent-lease-receipt", str(args.parent_lease_receipt), "--arm-path", str(args.arm_path), "--adapter", args.adapter, "--implementation-key", args.implementation_key, "--dtype", args.dtype, "--quantization", args.quantization, "--run-id", args.run_id, "--runtime-code-commit", args.runtime_code_commit, "--expected-attention-backend", args.expected_attention_backend, "--arm-wait-seconds", str(args.arm_wait_seconds)]
    if args.recovery_deployment_id: command.extend(("--recovery-deployment-id", args.recovery_deployment_id))
    if args.expected_output_checksum: command.extend(("--expected-output-checksum", args.expected_output_checksum))
    if args.recovery_v3_generic:
        command.extend(("--recovery-v3-generic", "--direct-function-binding", str(args.direct_function_binding)))
    return command


def parent(args: argparse.Namespace) -> int:
    if args.runtime_code_commit != git_head(): raise ContractError("parent source commit differs from declared capture commit")
    if not 1 <= args.target_cap_seconds <= 1200: raise ContractError("formal capture cap must be within the frozen 20-minute window")
    if any(path.exists() for path in (args.receipt, args.stage, args.child_receipt, args.stdout, args.stderr, args.parent_lease_receipt, args.arm_path)) or args.trace_root.exists():
        raise ContractError("formal capture refuses to overwrite a retained payload")
    if sha256_file(args.tool) != args.tool_sha256 or not args.nvdisasm.is_file(): raise ContractError("formal tool/nvdisasm closure differs")
    binding = load_binding(args.binding, canary=not args.recovery_v3_generic); target = json.loads(args.target_receipt.read_text(encoding="utf-8")); require_contract(binding, target, args.target_role, recovery_v3_generic=args.recovery_v3_generic, direct_function_binding=args.direct_function_binding)
    if args.target_role in {"DECODE_INDEX_TARGET", "RECOVERY_DECODE"} and capture_phase(args.mode) != "DECODE":
        raise ContractError("decode-side target may only be captured in the complete decode workload")
    ident = identity(binding, args); MeasurementActive.assert_available(args.budget_ledger)
    if args.recovery_ledger is not None:
        if args.recovery_ledger != args.budget_ledger or args.recovery_historical_ledger is None or not args.recovery_historical_sha256 or not args.recovery_deployment_id:
            raise ContractError("recovery capture requires one new ledger plus immutable historical-ledger proof")
        initialize_recovery_budget(recovery_ledger=args.recovery_ledger, historical_ledger=args.recovery_historical_ledger,
                                   expected_historical_sha256=args.recovery_historical_sha256, deployment_id=args.recovery_deployment_id)
        Lease: Any = RecoveryBudgetLease
    else:
        Lease = BudgetLease
    for path in (args.receipt, args.stage, args.child_receipt, args.stdout, args.stderr, args.parent_lease_receipt, args.arm_path): path.parent.mkdir(parents=True, exist_ok=True)
    args.trace_root.mkdir(parents=True)
    started = time.monotonic(); process: subprocess.Popen[str] | None = None; parent_receipt: dict[str, Any] | None = None; terminal = "FAILED_OR_ABORTED"; cleanup = {"required": False}; raw_bytes = 0
    with Lease(args.budget_ledger, ident, "NVBIT", capture=True) as lease:
        if lease.max_elapsed_seconds < args.target_cap_seconds: raise ContractError("remaining NVBit budget cannot cover frozen capture cap")
        parent_receipt, token = write_parent_lease_start(args.parent_lease_receipt, {"identity": ident}, "nvbit", lease)
        env = os.environ.copy(); env.pop("LD_PRELOAD", None); env.update(nvdisasm_environment_contract(args.nvdisasm, env.get("PATH", "")))
        target_function = target["function"]["mangled_name"]
        target_index = str(target["target_instruction"]["nvbit_static_index"])
        marker_path = args.budget_ledger.parent.parent / "control" / "MEASUREMENT_ACTIVE"
        env.update({"CUDA_MODULE_LOADING": "EAGER", "CUDA_INJECTION64_PATH": str(args.tool), "C16_NVBIT_LD_PRELOAD_DECLARATION": str(args.tool), "C16_G_PARENT_LEASE_RECEIPT": str(args.parent_lease_receipt), "C16_G_PARENT_LEASE_TOKEN": token, "C16_G_MEASUREMENT_ACTIVE_MARKER": str(marker_path), "USER_DEFINED_FOLDERS": "1", "TRACES_FOLDER": str(args.trace_root.parent), "TOOL_COMPRESS": "0", "TRACE_FILE_COMPRESS": "0", "ACTIVE_FROM_START": "0", "DYNAMIC_KERNEL_RANGE": f"0-@^{target_function}$", "INSTR_BEGIN": target_index, "INSTR_END": str(int(target_index) + 1), "C16_EXACT_ROOT_FUNCTION_ONLY": "1", "C16_USE_NVBIT_STATIC_INDEX": "1"})
        with args.stdout.open("w") as out, args.stderr.open("w") as err:
            process = subprocess.Popen(child_command(args), stdout=out, stderr=err, text=True, env=env, start_new_session=True)
            armed = False
            while process.poll() is None:
                event = json.loads(args.stage.read_text()) if args.stage.is_file() else {}
                if not armed and event.get("event") == "LANE_G_RUNTIME_READY":
                    if trace_files(args.trace_root): raise ContractError("prewarm created trace before parent measurement arm")
                    with MeasurementActive(args.budget_ledger, ident, "NVBIT_MULTIMODEL_CAPTURE") as marker:
                        arm = {"run_id": args.run_id, "parent_lease_id": parent_receipt["parent_lease_id"], "capture_phase": capture_phase(args.mode), "measurement_marker": str(marker.path), "capture_arm_ns": time.monotonic_ns()}
                        atomic_json(args.arm_path, arm); armed = True
                        while process.poll() is None and time.monotonic() - started < args.target_cap_seconds: time.sleep(0.05)
                    break
                if time.monotonic() - started >= args.target_cap_seconds: break
                time.sleep(0.05)
        if process.poll() is None: cleanup = kill_group(process); terminal = "BOUNDED_TIMEOUT"
        elif process.returncode == 0: terminal = "COMPLETE"
        elapsed = time.monotonic() - started
        traces = parse_traces(args.trace_root, target) if terminal == "COMPLETE" else []
        raw_bytes = sum(item["size_bytes"] for item in traces)
        if raw_bytes > lease.max_raw_bytes: raise ContractError("formal trace exceeded hard NVBit raw budget")
        lease.finish(elapsed_seconds=elapsed, raw_bytes=raw_bytes, terminal_status=terminal, evidence_classification="SCIENTIFIC" if terminal == "COMPLETE" else "NON_SCIENTIFIC_DIAGNOSTIC", diagnostic_reason=None if terminal == "COMPLETE" else "MULTIMODEL_FORMAL_CAPTURE_TIMEOUT_OR_FAILURE")
    if parent_receipt is not None:
        closeout = write_parent_lease_closeout(args.parent_lease_receipt, parent_receipt, terminal_status=terminal, elapsed_seconds=time.monotonic() - started, returncode=None if process is None else process.returncode)
    else: closeout = Path("NA")
    child_data = json.loads(args.child_receipt.read_text()) if args.child_receipt.is_file() else None
    atomic_json(args.receipt, {"schema_version": SCHEMA, "status": "FORMAL_CAPTURE_COMPLETE" if terminal == "COMPLETE" else terminal, "scientific_eligible": terminal == "COMPLETE", "identity": ident, "runtime_code_commit": args.runtime_code_commit, "target_wall_s": time.monotonic() - started, "target_cap_s": args.target_cap_seconds, "terminal_status": terminal, "cleanup": cleanup, "tool": {"path": str(args.tool), "sha256": args.tool_sha256}, "target_receipt": {"path": str(args.target_receipt), "sha256": sha256_file(args.target_receipt)}, "parent_lease_start": {"path": str(args.parent_lease_receipt), "sha256": sha256_file(args.parent_lease_receipt)}, "parent_lease_closeout": {"path": str(closeout), "sha256": sha256_file(closeout)}, "child": child_data, "raw_bytes": raw_bytes, "stdout": {"path": str(args.stdout), "sha256": sha256_file(args.stdout)}, "stderr": {"path": str(args.stderr), "sha256": sha256_file(args.stderr)}})
    return 0 if terminal == "COMPLETE" else 2


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--child", action="store_true"); parser.add_argument("--mode", choices=MODES, required=True); parser.add_argument("--target-role", choices=TARGET_ROLES, default="LARGE_INDEX_PREFILL")
    for name in ("binding", "target_receipt", "receipt", "stage", "child_receipt", "trace_root", "budget_ledger", "parent_lease_receipt", "arm_path", "stdout", "stderr", "tool", "nvdisasm"): parser.add_argument("--" + name.replace("_", "-"), type=Path)
    parser.add_argument("--tool-sha256"); parser.add_argument("--adapter", required=True); parser.add_argument("--implementation-key", required=True); parser.add_argument("--dtype", choices=("float16", "bfloat16"), required=True); parser.add_argument("--quantization", required=True); parser.add_argument("--run-id", required=True); parser.add_argument("--runtime-code-commit", required=True); parser.add_argument("--expected-attention-backend", required=True); parser.add_argument("--expected-output-checksum"); parser.add_argument("--recovery-v3-generic", action="store_true"); parser.add_argument("--direct-function-binding", type=Path); parser.add_argument("--arm-wait-seconds", type=int, default=60); parser.add_argument("--target-cap-seconds", type=int, default=600)
    parser.add_argument("--recovery-ledger", type=Path); parser.add_argument("--recovery-historical-ledger", type=Path); parser.add_argument("--recovery-historical-sha256"); parser.add_argument("--recovery-deployment-id")
    args = parser.parse_args()
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id: raise ValueError
    except ValueError: parser.error("--run-id must be canonical UUID")
    required = (args.binding, args.target_receipt, args.receipt, args.stage, args.child_receipt, args.trace_root, args.budget_ledger, args.parent_lease_receipt, args.arm_path)
    if any(value is None for value in required): parser.error("capture paths are required")
    if args.recovery_v3_generic and (args.direct_function_binding is None or not args.expected_output_checksum): parser.error("Recovery V3 capture requires --direct-function-binding and --expected-output-checksum")
    if not args.recovery_v3_generic and args.target_role in {"RECOVERY_PREFILL", "RECOVERY_DECODE"}: parser.error("Recovery target role requires --recovery-v3-generic")
    if args.child: raise SystemExit(child(args))
    if args.stdout is None or args.stderr is None or args.tool is None or args.nvdisasm is None or not args.tool_sha256: parser.error("parent requires tool, nvdisasm, stdout/stderr, and tool SHA")
    raise SystemExit(parent(args))


if __name__ == "__main__":
    try: main()
    except ContractError as exc: raise SystemExit(f"FAIL multi-model formal capture: {exc}")
