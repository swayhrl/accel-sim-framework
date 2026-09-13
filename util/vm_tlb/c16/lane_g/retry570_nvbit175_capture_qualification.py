#!/usr/bin/env python3
"""Q0/Q1 bounded NVBit 1.7.5 lifecycle qualification; never a model run."""
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
from retry570_long_watch import nvdisasm_environment_contract

SCHEMA = "C16_G_RETRY570_NVBIT175_CAPTURE_QUALIFICATION_V1"
TARGET_CAP_S, TERM_GRACE_S = 30, 2
EXACT = {"candidate_id": "R2_D0_I64_A", "shape": [64, 32], "dim": 0, "index_dtype": "int64", "index_count": 64}


def event(path: Path, name: str, **fields: Any) -> None:
    row = {"schema_version": SCHEMA, "ts_ns": time.monotonic_ns(), "event": name, **fields}
    atomic_json(path, row)
    print("C16_NVBIT175_CAPTURE " + json.dumps(row, sort_keys=True), flush=True)


def trace_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and (path.name.endswith(".trace") or path.name.endswith(".trace.xz")))


def target_inputs(torch: Any) -> tuple[Any, Any]:
    indices = (torch.arange(64, device="cuda:0", dtype=torch.int64) * 17) % 64
    source = torch.arange(64 * 32, device="cuda:0", dtype=torch.float32).reshape(64, 32).to(dtype=torch.float16)
    return source, indices


def target_operation(torch: Any, source: Any, indices: Any) -> str:
    output = torch.index_select(source, 0, indices)
    torch.cuda.synchronize()
    if output.device.type != "cuda" or list(output.shape) != [64, 32]:
        raise ContractError("exact index_select output differs")
    return hashlib.sha256(output.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def parse_stats(trace_root: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for stats in trace_root.glob("stats_ctx_*"):
        for line in stats.read_text(encoding="utf-8", errors="replace").splitlines():
            parts = [part.strip() for part in line.split(",")]
            match = re.match(r"kernel-(\d+)-ctx_0x[0-9a-f]+\.trace", parts[0] if parts else "")
            if match and len(parts) >= 2:
                rows.append({"kernel_id": int(match.group(1)), "function": parts[1]})
    matches = [row for row in rows if "indexSelectLargeIndex" in row["function"]]
    if len(matches) != 1:
        raise ContractError(f"Q0 requires exactly one directly observed indexSelectLargeIndex row; observed={len(matches)}")
    return {"all_kernel_rows": rows, "target": matches[0]}


def child(args: argparse.Namespace) -> int:
    event(args.stage, "PROCESS_START", mode=args.mode)
    torch, identity = assert_runtime_identity(args)
    event(args.stage, "RUNTIME_IDENTITY_CLOSED", identity=identity)
    if not torch.cuda.is_available():
        raise ContractError("CUDA unavailable; no CPU fallback")
    event(args.stage, "EAGER_NVBIT_INIT_BEGIN")
    torch.cuda.init()
    event(args.stage, "EAGER_NVBIT_INIT_END")
    event(args.stage, "PREWARM_BEGIN")
    source, indices = target_inputs(torch)
    torch.cuda.synchronize()
    event(args.stage, "PREWARM_END")
    before = len(trace_files(args.trace_root))
    if before != 0:
        raise ContractError("prewarm emitted a trace before capture arm")
    event(args.stage, "LANE_G_RUNTIME_READY", prewarm_trace_count=before)
    if args.mode == "Q0":
        event(args.stage, "Q0_TARGET_EXECUTE_BEGIN")
        checksum = target_operation(torch, source, indices)
        event(args.stage, "Q0_TARGET_EXECUTE_END")
        if trace_files(args.trace_root):
            raise ContractError("Q0 no-trace runtime/prewarm gate emitted trace")
        atomic_json(args.child_receipt, {"schema_version": SCHEMA, "status": "LANE_G_RUNTIME_READY", "scientific_eligible": False,
            "runtime_identity": identity, "exact_target": EXACT, "output_sha256": checksum, "prewarm_trace_count": 0,
            "measurement_active_created": False, "trace_generated": False})
        return 0
    deadline = time.monotonic() + args.arm_wait_seconds
    while not args.arm_path.exists():
        if time.monotonic() >= deadline:
            raise ContractError("Q1 did not receive parent arm after READY")
        time.sleep(0.02)
    arm = json.loads(args.arm_path.read_text(encoding="utf-8"))
    if arm.get("run_id") != args.run_id or arm.get("target") != args.target:
        raise ContractError("Q1 arm identity/target differs")
    event(args.stage, "CAPTURE_BEGIN", target=args.target)
    checksum = target_operation(torch, source, indices)
    event(args.stage, "CAPTURE_END", output_sha256=checksum)
    atomic_json(args.child_receipt, {"schema_version": SCHEMA, "status": "CAPTURE_COMPLETE", "scientific_eligible": False,
        "runtime_identity": identity, "exact_target": EXACT, "target": args.target, "output_sha256": checksum,
        "prewarm_trace_count": before, "capture_trace_count": len(trace_files(args.trace_root)), "trace_generated": True})
    return 0


def kill_group(process: subprocess.Popen[str]) -> dict[str, Any]:
    result = {"required": False, "term_sent": False, "kill_sent": False, "grace_s": TERM_GRACE_S}
    if process.poll() is not None:
        return result
    os.killpg(process.pid, signal.SIGTERM); result.update(required=True, term_sent=True)
    try:
        process.wait(timeout=TERM_GRACE_S)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL); result["kill_sent"] = True; process.wait(timeout=TERM_GRACE_S)
    return result


def parse_trace(path: Path) -> dict[str, Any]:
    if path.suffix == ".xz":
        raise ContractError("Q1 requires uncompressed trace for direct bounded parser validation")
    text = path.read_text(encoding="utf-8", errors="replace")
    headers = {line.split(" = ", 1)[0]: line.split(" = ", 1)[1] for line in text.splitlines() if line.startswith("-") and " = " in line}
    rows = [line for line in text.splitlines() if line and not line.startswith("-") and not line.startswith("#")]
    required = ("-kernel name", "-kernel id", "-nvbit version", "-accelsim tracer version")
    if "#traces format" not in text or any(key not in headers for key in required) or not rows or any(len(row.split()) < 6 for row in rows):
        raise ContractError(f"invalid or truncated C16 trace schema: {path}")
    return {"path": str(path), "size_bytes": path.stat().st_size, "sha256": sha256_file(path),
            "kernel_name": headers["-kernel name"], "kernel_id": int(headers["-kernel id"]), "record_count": len(rows),
            "required_memory_instruction_fields": "TRACE_FORMAT_COLUMNS_PRESENT"}


def child_command(args: argparse.Namespace) -> list[str]:
    result = [sys.executable, str(Path(__file__).resolve()), "--child", "--mode", args.mode, "--stage", str(args.stage),
              "--child-receipt", str(args.child_receipt), "--trace-root", str(args.trace_root), "--run-id", args.run_id,
              "--expected-torch-version", args.expected_torch_version, "--expected-torch-cuda", args.expected_torch_cuda,
              "--expected-libtorch-cuda-sha256", args.expected_libtorch_cuda_sha256, "--expected-gpu-name", args.expected_gpu_name,
              "--expected-driver", args.expected_driver]
    if args.expected_gpu_uuid: result.extend(("--expected-gpu-uuid", args.expected_gpu_uuid))
    if args.mode == "Q1":
        result.extend(("--arm-path", str(args.arm_path), "--arm-wait-seconds", str(args.arm_wait_seconds), "--target",
                       json.dumps(args.target, sort_keys=True, separators=(",", ":"))))
    return result


def parent(args: argparse.Namespace) -> int:
    if args.runtime_code_commit != git_head() or args.target_cap_seconds != TARGET_CAP_S:
        raise ContractError("runtime source commit or fixed Q0/Q1 target cap differs")
    if not args.preflight.is_file() or json.loads(args.preflight.read_text()).get("CAPTURE_ALLOWED") != "YES":
        raise ContractError("Q0/Q1 requires hash-closed CAPTURE_ALLOWED preflight")
    if not args.tool.is_file() or sha256_file(args.tool) != args.tool_sha256 or not args.nvdisasm.is_file():
        raise ContractError("tool/nvdisasm closure differs")
    if args.mode == "Q1" and (not args.q0_receipt.is_file() or not args.target_plan.is_file()):
        raise ContractError("Q1 requires Q0 runtime-ready receipt and frozen target plan")
    if args.mode == "Q1" and (not isinstance(args.target, dict) or not isinstance(args.target.get("kernel_id"), int) or not isinstance(args.target.get("function"), str)):
        raise ContractError("Q1 requires an exact Q0 target object")
    if args.mode == "Q1":
        q0 = json.loads(args.q0_receipt.read_text(encoding="utf-8"))
        plan = json.loads(args.target_plan.read_text(encoding="utf-8"))
        if q0.get("status") != "LANE_G_RUNTIME_READY" or q0.get("scientific_eligible") is not False:
            raise ContractError("Q1 requires a non-scientific LANE_G_RUNTIME_READY Q0 receipt")
        if q0.get("prewarm_trace_count") != 0 or q0.get("measurement_active_created") is not False:
            raise ContractError("Q1 rejects a Q0 receipt with prewarm trace or measurement activity")
        if plan.get("status") != "Q0_FROZEN_EXACT_TARGET_PLAN" or plan.get("scientific_eligible") is not False or plan.get("target") != args.target:
            raise ContractError("Q1 target must exactly equal the frozen non-scientific Q0 plan")
        if args.arm_path.exists():
            raise ContractError("Q1 arm path must be absent before parent creates it")
    for path in (args.receipt, args.stage, args.child_receipt, args.stdout, args.stderr):
        if path.exists(): raise ContractError(f"refusing to overwrite payload: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
    if args.trace_root.exists(): raise ContractError("trace root must be fresh")
    args.trace_root.mkdir(parents=True)
    MeasurementActive.assert_available(args.budget_ledger)
    identity = {"deployment_id": "c16_retry570_nvbit175_capture_qualification", "scenario_id": args.mode,
                "run_id": args.run_id, "implementation_key": "NVBIT_1_7_5_ORIGINAL_LANE_G_TRACER"}
    started, timed_out, cleanup = time.monotonic(), False, {"required": False, "term_sent": False, "kill_sent": False, "grace_s": TERM_GRACE_S}
    process: subprocess.Popen[str] | None = None
    with BudgetLease(args.budget_ledger, identity, "NVBIT_175_CAPTURE_QUALIFICATION", capture=args.mode == "Q1") as lease:
        env = os.environ.copy(); env.pop("LD_PRELOAD", None); env.pop("CUDA_INJECTION64_PATH", None)
        env.update(nvdisasm_environment_contract(args.nvdisasm, env.get("PATH", "")))
        env.update({"CUDA_MODULE_LOADING": "EAGER", "CUDA_INJECTION64_PATH": str(args.tool), "C16_NVBIT_LD_PRELOAD_DECLARATION": str(args.tool),
                    "USER_DEFINED_FOLDERS": "1", "TRACES_FOLDER": str(args.trace_root.parent), "TOOL_COMPRESS": "0", "TRACE_FILE_COMPRESS": "0",
                    "ACTIVE_FROM_START": "1", "DYNAMIC_KERNEL_RANGE": "999999-999999@^$" if args.mode == "Q0" else f"{args.target['kernel_id']}-{args.target['kernel_id']}@.*"})
        with args.stdout.open("w") as out, args.stderr.open("w") as err:
            process = subprocess.Popen(child_command(args), stdout=out, stderr=err, text=True, env=env, start_new_session=True)
            armed = False
            while process.poll() is None:
                stage = json.loads(args.stage.read_text()) if args.stage.is_file() else {}
                if args.mode == "Q1" and not armed and stage.get("event") == "LANE_G_RUNTIME_READY":
                    if trace_files(args.trace_root): raise ContractError("trace exists before Q1 capture arm")
                    with MeasurementActive(args.budget_ledger, identity, "NVBIT_175_Q1_CAPTURE"):
                        atomic_json(args.arm_path, {"run_id": args.run_id, "target": args.target, "capture_begin_armed_ns": time.monotonic_ns()})
                        armed = True
                        while process.poll() is None and time.monotonic() - started < TARGET_CAP_S: time.sleep(0.02)
                        if process.poll() is None:
                            timed_out = True
                    break
                if time.monotonic() - started >= TARGET_CAP_S: timed_out = True; cleanup = kill_group(process); break
                time.sleep(0.02)
        if process.poll() is None: cleanup = kill_group(process)
        elapsed = time.monotonic() - started
        terminal = "BOUNDED_TIMEOUT" if timed_out else "COMPLETE" if process.returncode == 0 else "FAILED_OR_ABORTED"
        traces = [parse_trace(path) for path in trace_files(args.trace_root)] if terminal == "COMPLETE" and args.mode == "Q1" else []
        if args.mode == "Q0":
            plan = parse_stats(args.trace_root)
            atomic_json(args.target_plan, {"schema_version": SCHEMA, "status": "Q0_FROZEN_EXACT_TARGET_PLAN", "target": plan["target"], "all_kernel_rows": plan["all_kernel_rows"], "scientific_eligible": False})
        elif len(traces) != 1 or traces[0]["kernel_id"] != args.target["kernel_id"] or traces[0]["kernel_name"] != args.target["function"]:
            raise ContractError("Q1 trace does not uniquely bind the Q0 frozen target identity")
        raw = sum(item["size_bytes"] for item in traces)
        lease.finish(elapsed_seconds=elapsed, raw_bytes=raw, terminal_status=terminal, evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC",
                     diagnostic_reason="NVBIT175_Q0_PREWARM_OR_Q1_TINY_CAPTURE_QUALIFICATION_NOT_NATIVE_TIMING")
    child_data = json.loads(args.child_receipt.read_text()) if args.child_receipt.is_file() else None
    atomic_json(args.receipt, {"schema_version": SCHEMA, "status": "LANE_G_RUNTIME_READY" if args.mode == "Q0" and terminal == "COMPLETE" else "Q1_CAPTURE_COMPLETE" if terminal == "COMPLETE" else terminal,
        "scientific_eligible": False, "mode": args.mode, "run_id": args.run_id, "runtime_code_commit": args.runtime_code_commit,
        "target_wall_s": elapsed, "target_cap_s": TARGET_CAP_S, "target_group_cleanup": cleanup, "terminal_status": terminal,
        "preflight": {"path": str(args.preflight), "sha256": sha256_file(args.preflight)}, "tool": {"path": str(args.tool), "sha256": args.tool_sha256},
        "nvdisasm": str(args.nvdisasm), "child_environment": {"CUDA_MODULE_LOADING": "EAGER", "DYNAMIC_KERNEL_RANGE": env["DYNAMIC_KERNEL_RANGE"], "PATH": env["PATH"], "NVDISASM": env["NVDISASM"]},
        "prewarm_trace_count": 0, "measurement_active_created": args.mode == "Q1", "capture_traces": traces, "raw_bytes": raw,
        "child_receipt": child_data, "stdout": {"path": str(args.stdout), "sha256": sha256_file(args.stdout)}, "stderr": {"path": str(args.stderr), "sha256": sha256_file(args.stderr)}})
    return 0 if terminal == "COMPLETE" else 2


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--child", action="store_true"); p.add_argument("--mode", choices=("Q0", "Q1"), required=True)
    p.add_argument("--receipt", type=Path); p.add_argument("--stage", type=Path, required=True); p.add_argument("--child-receipt", type=Path, required=True); p.add_argument("--stdout", type=Path); p.add_argument("--stderr", type=Path); p.add_argument("--trace-root", type=Path, required=True); p.add_argument("--target-plan", type=Path); p.add_argument("--q0-receipt", type=Path); p.add_argument("--arm-path", type=Path); p.add_argument("--arm-wait-seconds", type=int, default=10); p.add_argument("--target", type=json.loads)
    p.add_argument("--preflight", type=Path); p.add_argument("--budget-ledger", type=Path); p.add_argument("--tool", type=Path); p.add_argument("--tool-sha256"); p.add_argument("--nvdisasm", type=Path); p.add_argument("--target-cap-seconds", type=int, default=TARGET_CAP_S); p.add_argument("--expected-torch-version", required=True); p.add_argument("--expected-torch-cuda", required=True); p.add_argument("--expected-libtorch-cuda-sha256", required=True); p.add_argument("--expected-gpu-name", default="NVIDIA GeForce RTX 3090"); p.add_argument("--expected-driver", default="570.124.04"); p.add_argument("--expected-gpu-uuid"); p.add_argument("--runtime-code-commit"); p.add_argument("--run-id")
    args = p.parse_args()
    if args.child: raise SystemExit(child(args))
    required = (args.receipt, args.stdout, args.stderr, args.preflight, args.budget_ledger, args.tool, args.tool_sha256, args.nvdisasm, args.runtime_code_commit, args.run_id, args.target_plan)
    if any(value is None for value in required) or not valid_sha256(args.tool_sha256) or not valid_sha256(args.expected_libtorch_cuda_sha256): raise ContractError("parent lacks closed identity/paths")
    if args.mode == "Q1" and (args.q0_receipt is None or args.arm_path is None or args.target is None): raise ContractError("Q1 lacks Q0/arm paths")
    raise SystemExit(parent(args))


if __name__ == "__main__":
    try: main()
    except ContractError as exc: raise SystemExit(f"FAIL Retry570 NVBit175 capture qualification: {exc}")
