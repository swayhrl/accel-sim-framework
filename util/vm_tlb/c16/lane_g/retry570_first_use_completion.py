#!/usr/bin/env python3
"""Bound NVBit EMPTY/EAGER first-use completion and same-process reuse."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file, valid_sha256
from execution_budget import BudgetLease, MeasurementActive
from nvbit_indexselect_microreproducer import assert_runtime_identity, git_head
from retry570_long_watch import gpu_snapshot, nvdisasm_environment_contract

SCHEMA = "C16_G_RETRY570_FIRST_USE_COMPLETION_V1"
TARGET_HARD_BUDGET_S = 60
TERM_GRACE_S = 2
EXACT_CANDIDATE = {"candidate_id": "R2_D0_I64_A", "shape": [64, 32], "dim": 0,
                   "index_dtype": "int64", "index_count": 64}


def event(stage: Path, name: str, **fields: Any) -> None:
    row = {"schema_version": SCHEMA, "ts_ns": time.monotonic_ns(), "event": name, **fields}
    atomic_json(stage, row)
    print("C16_FIRST_USE " + " ".join(f"{key}={value}" for key, value in row.items()), flush=True)


def child_main(args: argparse.Namespace) -> int:
    event(args.stage_path, "PROCESS_START")
    torch, identity = assert_runtime_identity(args)
    event(args.stage_path, "RUNTIME_IDENTITY_CLOSED", identity=identity)
    if not torch.cuda.is_available():
        raise ContractError("CUDA unavailable; CPU fallback forbidden")
    event(args.stage_path, "CUDA_INIT_BEGIN")
    torch.cuda.init()
    event(args.stage_path, "CUDA_INIT_END")
    torch.manual_seed(570)
    event(args.stage_path, "INPUT_PREPARATION_BEGIN")
    indices = (torch.arange(64, device="cuda:0", dtype=torch.int64) * 17) % 64
    source = torch.randn((64, 32), device="cuda:0", dtype=torch.float16)
    torch.cuda.synchronize()
    event(args.stage_path, "READY", measurement_active=False)
    checksums: list[str] = []
    round_receipts: list[dict[str, Any]] = []
    outputs = []
    for ordinal in (1, 2):
        begin = time.monotonic_ns()
        event(args.stage_path, f"ROUND{ordinal}_BEGIN")
        output = torch.index_select(source, 0, indices)
        dispatch = time.monotonic_ns()
        event(args.stage_path, f"ROUND{ordinal}_DISPATCH_RETURN")
        torch.cuda.synchronize()
        end = time.monotonic_ns()
        event(args.stage_path, f"ROUND{ordinal}_END")
        if output.device.type != "cuda" or list(output.shape) != [64, 32]:
            raise ContractError("exact operation changed output shape/device")
        outputs.append(output)
        round_receipts.append({"round": ordinal, "dispatch_latency_s": (dispatch - begin) / 1e9,
                               "synchronized_latency_s": (end - begin) / 1e9})
    for output in outputs:
        checksums.append(hashlib.sha256(output.detach().cpu().contiguous().numpy().tobytes()).hexdigest())
    if len(set(checksums)) != 1:
        raise ContractError("identical exact operations produced different outputs")
    event(args.stage_path, "QUALIFICATION_COMPLETE")
    atomic_json(args.child_receipt, {"schema_version": SCHEMA, "status": "COMPLETE", "scientific_eligible": False,
                                     "runtime_identity": identity, "exact_candidate": EXACT_CANDIDATE,
                                     "rounds": round_receipts, "output_sha256": checksums[0],
                                     "cuda_module_loading": "EAGER", "measurement_active_created": False,
                                     "trace_generated": False, "raw_bytes": 0})
    return 0


def run_text(command: list[str], timeout: int = 2) -> dict[str, Any]:
    try:
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                timeout=timeout, check=False)
        return {"command": command, "returncode": result.returncode, "output": result.stdout}
    except subprocess.TimeoutExpired as exc:
        return {"command": command, "returncode": "TIMEOUT", "output": (exc.stdout or "") + (exc.stderr or "")}
    except OSError as exc:
        return {"command": command, "returncode": "UNAVAILABLE", "output": f"{type(exc).__name__}: {exc}"}


def final_state(pid: int, output: Path) -> dict[str, Any]:
    record = {"schema_version": SCHEMA, "pid": pid, "captured_at_ns": time.monotonic_ns(),
              "threads": run_text(["ps", "-L", "-p", str(pid), "-o", "pid,tid,stat,pcpu,etime,wchan:32,comm"]),
              "wchan": run_text(["cat", f"/proc/{pid}/wchan"]),
              "syscall": run_text(["cat", f"/proc/{pid}/syscall"]),
              "native_stack": run_text(["cat", f"/proc/{pid}/stack"]), **gpu_snapshot(pid)}
    atomic_json(output, record)
    return {"path": str(output), "sha256": sha256_file(output)}


def stop_group(process: subprocess.Popen[str]) -> dict[str, Any]:
    result = {"required": False, "term_sent": False, "kill_sent": False, "grace_s": TERM_GRACE_S}
    if process.poll() is not None:
        return result
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return result
    result.update(required=True, term_sent=True)
    try:
        process.wait(timeout=TERM_GRACE_S)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        result["kill_sent"] = True
        process.wait(timeout=TERM_GRACE_S)
    return result


def parsed_events(stdout_path: Path) -> dict[str, int]:
    result: dict[str, int] = {}
    for line in stdout_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("C16_FIRST_USE "):
            continue
        fields = dict(re.findall(r"(\w+)=([^ ]+)", line))
        if "event" in fields and "ts_ns" in fields:
            result[fields["event"]] = int(fields["ts_ns"])
    return result


def child_command(args: argparse.Namespace) -> list[str]:
    command = [sys.executable, str(Path(__file__).resolve()), "--child", "--stage-path", str(args.stage_path),
               "--child-receipt", str(args.child_receipt), "--expected-torch-version", args.expected_torch_version,
               "--expected-torch-cuda", args.expected_torch_cuda, "--expected-libtorch-cuda-sha256", args.expected_libtorch_cuda_sha256,
               "--expected-gpu-name", args.expected_gpu_name, "--expected-driver", args.expected_driver]
    if args.expected_gpu_uuid:
        command.extend(("--expected-gpu-uuid", args.expected_gpu_uuid))
    return command


def validate_args(args: argparse.Namespace) -> None:
    if args.runtime_code_commit != git_head() or args.wall_limit_seconds != TARGET_HARD_BUDGET_S:
        raise ContractError("first-use runtime commit or fixed 60-second budget differs")
    if not args.tool_path.is_file() or not valid_sha256(args.tool_sha256) or sha256_file(args.tool_path) != args.tool_sha256:
        raise ContractError("EMPTY tool is not materialized/hash-closed")
    if not valid_sha256(args.expected_libtorch_cuda_sha256) or not args.nvdisasm:
        raise ContractError("runtime/nvdisasm identity incomplete")
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id:
            raise ValueError
    except ValueError as exc:
        raise ContractError("run ID must be canonical UUID") from exc
    for path in (args.receipt, args.stdout_path, args.stderr_path, args.stage_path,
                 args.child_receipt, args.final_state_path):
        if path.exists():
            raise ContractError(f"refusing to overwrite diagnostic payload: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)


def parent_main(args: argparse.Namespace) -> int:
    validate_args(args)
    identity = {"deployment_id": "c16_retry570_exact_indexselect_first_use_completion",
                "scenario_id": "R2_D0_I64_A_EAGER_EMPTY_DIAGNOSTIC", "run_id": args.run_id,
                "implementation_key": "NVBIT_1_8_EMPTY_EAGER"}
    MeasurementActive.assert_available(args.budget_ledger)
    started = time.monotonic()
    timed_out = False
    snapshot: dict[str, Any] | str = "NOT_REQUIRED_COMPLETED"
    cleanup = {"required": False, "term_sent": False, "kill_sent": False, "grace_s": TERM_GRACE_S}
    process: subprocess.Popen[str] | None = None
    with BudgetLease(args.budget_ledger, identity, "NVBIT_FIRST_USE_COMPLETION_QUALIFICATION", capture=False) as lease:
        environment = os.environ.copy()
        environment.pop("LD_PRELOAD", None)
        environment.pop("CUDA_INJECTION64_PATH", None)
        environment.update(nvdisasm_environment_contract(Path(args.nvdisasm), environment.get("PATH", "")))
        environment.update({"CUDA_MODULE_LOADING": "EAGER", "CUDA_INJECTION64_PATH": str(args.tool_path),
                            "C16_NVBIT_LD_PRELOAD_DECLARATION": str(args.tool_path)})
        with args.stdout_path.open("w", encoding="utf-8") as stdout, args.stderr_path.open("w", encoding="utf-8") as stderr:
            process = subprocess.Popen(child_command(args), stdout=stdout, stderr=stderr, text=True,
                                       env=environment, start_new_session=True)
            while process.poll() is None:
                if time.monotonic() - started >= TARGET_HARD_BUDGET_S:
                    timed_out = True
                    snapshot = final_state(process.pid, args.final_state_path)
                    cleanup = stop_group(process)
                    break
                time.sleep(0.05)
        if process.poll() is None:
            cleanup = stop_group(process)
        elapsed = time.monotonic() - started
        terminal = "BOUNDED_TIMEOUT" if timed_out else "COMPLETE" if process.returncode == 0 else "FAILED_OR_ABORTED"
        lease.finish(elapsed_seconds=elapsed, raw_bytes=0, terminal_status=terminal,
                     evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC",
                     diagnostic_reason="NVBIT_1_8_EMPTY_EAGER_FIRST_USE_AND_TWO_IDENTICAL_EXACT_OPERATIONS")
    events = parsed_events(args.stdout_path)
    child = json.loads(args.child_receipt.read_text(encoding="utf-8")) if args.child_receipt.is_file() else None
    process_to_ready = ((events["READY"] - events["PROCESS_START"]) / 1e9
                        if "READY" in events and "PROCESS_START" in events else None)
    atomic_json(args.receipt, {"schema_version": SCHEMA, "status": "FIRST_USE_COMPLETION_" + terminal,
                               "terminal_status": terminal, "scientific_eligible": False,
                               "runtime_code_commit": args.runtime_code_commit, "run_id": args.run_id,
                               "mode": "NVBIT_1_8_EMPTY_CALLBACK_EAGER", "exact_candidate": EXACT_CANDIDATE,
                               "target_hard_budget_s": TARGET_HARD_BUDGET_S, "target_wall_s": elapsed,
                               "target_group_cleanup": cleanup, "process_to_ready_s": process_to_ready,
                               "round1": child["rounds"][0] if child else None,
                               "round2": child["rounds"][1] if child else None,
                               "output_sha256": child.get("output_sha256") if child else None,
                               "final_process_state": snapshot, "tool": {"path": str(args.tool_path), "sha256": args.tool_sha256},
                               "measurement_active_created": False, "trace_generated": False, "raw_bytes": 0,
                               "stdout": {"path": str(args.stdout_path), "sha256": sha256_file(args.stdout_path)},
                               "stderr": {"path": str(args.stderr_path), "sha256": sha256_file(args.stderr_path)}})
    return 0 if terminal == "COMPLETE" else 2


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--child", action="store_true")
    result.add_argument("--receipt", type=Path)
    result.add_argument("--stdout-path", type=Path)
    result.add_argument("--stderr-path", type=Path)
    result.add_argument("--stage-path", type=Path, required=True)
    result.add_argument("--child-receipt", type=Path, required=True)
    result.add_argument("--final-state-path", type=Path)
    result.add_argument("--budget-ledger", type=Path)
    result.add_argument("--wall-limit-seconds", type=int, default=TARGET_HARD_BUDGET_S)
    result.add_argument("--tool-path", type=Path)
    result.add_argument("--tool-sha256")
    result.add_argument("--nvdisasm")
    result.add_argument("--expected-torch-version", required=True)
    result.add_argument("--expected-torch-cuda", required=True)
    result.add_argument("--expected-libtorch-cuda-sha256", required=True)
    result.add_argument("--expected-gpu-name", default="NVIDIA GeForce RTX 3090")
    result.add_argument("--expected-driver", default="570.124.04")
    result.add_argument("--expected-gpu-uuid")
    result.add_argument("--runtime-code-commit")
    result.add_argument("--run-id")
    return result


def main() -> None:
    args = parser().parse_args()
    if args.child:
        raise SystemExit(child_main(args))
    required = (args.receipt, args.stdout_path, args.stderr_path, args.final_state_path,
                args.budget_ledger, args.tool_path, args.tool_sha256, args.runtime_code_commit, args.run_id)
    if any(value is None for value in required):
        raise ContractError("parent requires outputs, ledger, EMPTY tool, source commit, and run ID")
    raise SystemExit(parent_main(args))


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Retry570 first-use completion qualification: {exc}")
