#!/usr/bin/env python3
"""Run one <=30s no-op NVBit CUDA-driver callback census on exact index_select.

This diagnostic does not inspect CUfunctions, discover instructions, insert
instrumentation, enable instrumentation, capture a trace, or use a model.  It
exists only to expose where an application-side ``torch.index_select`` call
does or does not enter NVBit's CUDA-driver callback stream.
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import re
import shutil
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
from retry570_long_watch import _run_text, gpu_snapshot, nvdisasm_environment_contract


SCHEMA = "C16_G_RETRY570_CALLBACK_CENSUS_DIAGNOSTIC_V1"
# Keep a five-second teardown margin below the 30-second diagnostic ceiling so
# the parent can terminate, hash its compact receipt, and release its budget
# lease even when the external launcher has a 30-second response limit.
WALL_LIMIT_SECONDS = 25
SNAPSHOT_OFFSETS_SECONDS = (2, 5, 10)
EXACT_CANDIDATE = {"candidate_id": "R2_D0_I64_A", "shape": (64, 32), "dim": 0, "index_dtype": "int64", "index_count": 64}
CURRENT_MATCHER_LAUNCH_APIS = frozenset({
    "cuLaunch", "cuLaunchGrid", "cuLaunchKernel", "cuLaunchKernel_ptsz",
    "cuLaunchCooperativeKernel", "cuLaunchCooperativeKernel_ptsz",
    "cuLaunchKernelEx", "cuLaunchKernelEx_ptsz",
})


def _now_ns() -> int:
    return time.monotonic_ns()


def _app_event(stage_path: Path, event: str, **fields: Any) -> dict[str, Any]:
    row = {"schema_version": SCHEMA, "ts_ns": _now_ns(), "event": event, **fields}
    atomic_json(stage_path, row)
    print("C16_CALLBACK_CENSUS_APP " + " ".join(f"{key}={value}" for key, value in row.items()), flush=True)
    return row


def _module_loading_mode() -> dict[str, Any]:
    try:
        driver = ctypes.CDLL("libcuda.so.1")
        function = driver.cuModuleGetLoadingMode
        function.argtypes = [ctypes.POINTER(ctypes.c_int)]
        function.restype = ctypes.c_int
        mode = ctypes.c_int(-1)
        result = int(function(ctypes.byref(mode)))
        names = {1: "CU_MODULE_EAGER_LOADING", 2: "CU_MODULE_LAZY_LOADING"}
        return {"cu_result": result, "mode_value": mode.value, "mode_name": names.get(mode.value, "UNKNOWN")}
    except (AttributeError, OSError) as exc:
        return {"query_error": f"{type(exc).__name__}: {exc}"}


def _one_operation(torch: Any, stage_path: Path, round_id: int) -> str:
    _app_event(stage_path, "ROUND_BEGIN", round_id=round_id, candidate=EXACT_CANDIDATE)
    _app_event(stage_path, "BEFORE_TORCH_MANUAL_SEED", round_id=round_id)
    torch.manual_seed(570)
    _app_event(stage_path, "AFTER_TORCH_MANUAL_SEED", round_id=round_id)
    shape = EXACT_CANDIDATE["shape"]
    _app_event(stage_path, "BEFORE_TORCH_ARANGE_INDEX", round_id=round_id)
    indices = (torch.arange(EXACT_CANDIDATE["index_count"], device="cuda:0", dtype=torch.int64) * 17) % shape[0]
    _app_event(stage_path, "AFTER_TORCH_ARANGE_INDEX", round_id=round_id)
    _app_event(stage_path, "BEFORE_TORCH_RANDN_SOURCE", round_id=round_id)
    source = torch.randn(shape, device="cuda:0", dtype=torch.float16)
    _app_event(stage_path, "AFTER_TORCH_RANDN_SOURCE", round_id=round_id)
    _app_event(stage_path, "BEFORE_EXACT_OPERATION", round_id=round_id)
    # This marker is directly before Python's torch.index_select call.  It is
    # deliberately an application-operation boundary, not a CUDA launch proof.
    _app_event(stage_path, "EXACT_TARGET_SUBMISSION_BEGIN", round_id=round_id)
    output = torch.index_select(source, int(EXACT_CANDIDATE["dim"]), indices)
    _app_event(stage_path, "EXACT_OPERATION_RETURN", round_id=round_id)
    _app_event(stage_path, "BEFORE_SYNC", round_id=round_id)
    torch.cuda.synchronize()
    _app_event(stage_path, "AFTER_SYNC", round_id=round_id)
    if output.device.type != "cuda" or list(output.shape) != [64, 32]:
        raise ContractError("exact index_select candidate produced an unexpected output")
    checksum = str(int(output.float().sum().item() * 1_000_000))
    _app_event(stage_path, "ROUND_END", round_id=round_id, output_checksum_scaled=checksum)
    del output, source, indices
    return checksum


def child_main(args: argparse.Namespace) -> int:
    try:
        _app_event(args.stage_path, "PROCESS_START", cuda_module_loading=args.cuda_module_loading)
        _app_event(args.stage_path, "TORCH_IMPORT_BEGIN")
        torch, identity = assert_runtime_identity(args)
        _app_event(args.stage_path, "RUNTIME_IDENTITY_CLOSED", runtime_identity=identity)
        if not torch.cuda.is_available():
            raise ContractError("CUDA is unavailable; CPU fallback is forbidden")
        _app_event(args.stage_path, "CUDA_INIT_BEGIN")
        torch.cuda.init()
        _app_event(args.stage_path, "CUDA_INIT_COMPLETE")
        _app_event(args.stage_path, "MODULE_LOADING_MODE_QUERY", **_module_loading_mode())
        first = _one_operation(torch, args.stage_path, 1)
        second = _one_operation(torch, args.stage_path, 2)
        if first != second:
            raise ContractError("identical second index_select did not preserve checksum")
        receipt = {"schema_version": SCHEMA, "status": "CHILD_COMPLETE", "terminal_status": "COMPLETE", "scientific_eligible": False, "runtime_identity": identity, "cuda_module_loading": args.cuda_module_loading, "rounds": 2, "checksum_scaled": first}
        atomic_json(args.child_receipt, receipt)
        _app_event(args.stage_path, "CHILD_COMPLETE")
        return 0
    except Exception as exc:
        atomic_json(args.child_receipt, {"schema_version": SCHEMA, "status": "CHILD_FAILED", "terminal_status": "FAILED_OR_ABORTED", "scientific_eligible": False, "message": str(exc)})
        _app_event(args.stage_path, "CHILD_FAILED", message=str(exc))
        print(f"FAIL Retry570 callback census child: {exc}", file=sys.stderr, flush=True)
        return 2


def _run_text_safe(command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=6, check=False)
        return {"command": command, "returncode": completed.returncode, "output": completed.stdout}
    except subprocess.TimeoutExpired as exc:
        return {"command": command, "returncode": "TIMEOUT", "output": (exc.stdout or "") + (exc.stderr or "")}
    except OSError as exc:
        return {"command": command, "returncode": "UNAVAILABLE", "output": f"{type(exc).__name__}: {exc}"}


def _process_snapshot(pid: int, ordinal: int, output: Path, operation_anchor_event: str, operation_anchor_elapsed_seconds: float) -> dict[str, Any]:
    tools = {
        "threads": ["ps", "-L", "-p", str(pid), "-o", "pid,tid,stat,pcpu,etime,wchan:32,comm"],
        "pstree": ["pstree", "-ap", str(pid)],
        "nvdisasm": ["pgrep", "-af", "nvdisasm"],
        "process_filter": ["ps", "-eo", "pid,ppid,stat,pcpu,etime,wchan:32,args"],
    }
    record = {"schema_version": SCHEMA, "ordinal": ordinal, "operation_anchor_event": operation_anchor_event, "operation_anchor_elapsed_seconds": operation_anchor_elapsed_seconds, "pid": pid, "commands": {key: _run_text_safe(command) for key, command in tools.items()}, **gpu_snapshot(pid)}
    record["commands"]["process_filter"]["output"] = "\n".join(line for line in str(record["commands"]["process_filter"]["output"]).splitlines() if any(token in line for token in ("nvdisasm", "python", "nvbit")))
    if ordinal == 5:
        if shutil.which("gdb"):
            record["native_backtrace"] = _run_text_safe(["gdb", "-q", "-batch", "-ex", "set pagination off", "-ex", "thread apply all bt", "-p", str(pid)])
            record["native_backtrace"]["diagnostic_perturbation"] = True
        else:
            record["native_backtrace"] = {"status": "UNAVAILABLE_GDB_NOT_INSTALLED", "diagnostic_perturbation": False}
    path = output / f"snapshot_{ordinal:02d}.json"
    atomic_json(path, record)
    return {"path": str(path), "sha256": sha256_file(path), "operation_anchor_event": operation_anchor_event, "operation_anchor_elapsed_seconds": operation_anchor_elapsed_seconds}


def _kill_process_group(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=5)


def _read_stage(path: Path) -> dict[str, Any] | None:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return result if isinstance(result, dict) else None


def _child_command(args: argparse.Namespace) -> list[str]:
    value = [sys.executable, str(Path(__file__).resolve()), "--child", "--stage-path", str(args.stage_path), "--child-receipt", str(args.child_receipt), "--cuda-module-loading", args.cuda_module_loading, "--expected-torch-version", args.expected_torch_version, "--expected-torch-cuda", args.expected_torch_cuda, "--expected-libtorch-cuda-sha256", args.expected_libtorch_cuda_sha256, "--expected-gpu-name", args.expected_gpu_name, "--expected-driver", args.expected_driver]
    if args.expected_gpu_uuid:
        value.extend(("--expected-gpu-uuid", args.expected_gpu_uuid))
    return value


def _parse_callback(line: str) -> dict[str, Any] | None:
    if not line.startswith("C16_CALLBACK_CENSUS ts_ns="):
        return None
    values = dict(re.findall(r"(\w+)=([^ ]+)", line))
    try:
        return {"ts_ns": int(values["ts_ns"]), "seq": int(values["seq"]), "pid": int(values["pid"]), "tid": int(values["tid"]), "is_exit": int(values["is_exit"]), "cbid": int(values["cbid"]), "callback": values["callback"]}
    except (KeyError, ValueError) as exc:
        raise ContractError("callback census row is malformed") from exc


def _parse_app(line: str) -> dict[str, Any] | None:
    if not line.startswith("C16_CALLBACK_CENSUS_APP "):
        return None
    values = dict(re.findall(r"(\w+)=([^ ]+)", line))
    try:
        return {"ts_ns": int(values["ts_ns"]), "event": values["event"]}
    except (KeyError, ValueError) as exc:
        raise ContractError("application census row is malformed") from exc


def analyze(stdout: Path) -> dict[str, Any]:
    text = stdout.read_text(encoding="utf-8", errors="replace")
    callbacks, app = [], []
    for line in text.splitlines():
        callback, application = _parse_callback(line), _parse_app(line)
        if callback is not None:
            callbacks.append(callback)
        if application is not None:
            app.append(application)
    submission = next((row for row in app if row["event"] == "EXACT_TARGET_SUBMISSION_BEGIN"), None)
    post = [row for row in callbacks if submission is not None and row["ts_ns"] >= submission["ts_ns"]]
    pending: dict[tuple[int, str], list[dict[str, Any]]] = {}
    completed: list[dict[str, Any]] = []
    for row in post:
        key = (row["cbid"], row["callback"])
        if row["is_exit"] == 0:
            pending.setdefault(key, []).append(row)
        elif pending.get(key):
            enter = pending[key].pop()
            completed.append({"enter": enter, "exit": row, "elapsed_ns": row["ts_ns"] - enter["ts_ns"]})
    unmatched = [row for values in pending.values() for row in values]
    launches = [row for row in post if row["is_exit"] == 0 and (row["callback"].startswith("cuLaunch") or row["callback"].startswith("cuGraphLaunch"))]
    unhandled_launches = sorted({row["callback"] for row in launches if row["callback"] not in CURRENT_MATCHER_LAUNCH_APIS})
    tool_ready = "C16_CALLBACK_CENSUS_TOOL_READY mode=CALLBACK_CENSUS_ONLY" in text
    if submission is None:
        classification = "PRE_SUBMISSION_HOST_OPERATION_STALL_AFTER:" + (app[-1]["event"] if app else "NO_APP_EVENT")
    elif not tool_ready:
        classification = "HARNESS_FAIL_CLOSED_NVBIT_TOOL_NOT_LOADED"
    elif unmatched:
        classification = f"CUDA_DRIVER_API_STALL_IDENTIFIED:{unmatched[-1]['callback']}"
    elif not post:
        classification = "HOST_SIDE_OR_NVBIT_PRE_CALLBACK_INTERNAL_STALL"
    elif unhandled_launches:
        classification = "CALLBACK_MATCHER_GAP_CANDIDATE:" + ",".join(unhandled_launches)
    elif launches:
        classification = "LAUNCH_CALLBACK_VISIBLE_NO_FUNCTION_IDENTITY_IN_CENSUS"
    else:
        classification = "HOST_SIDE_CALLBACK_ACTIVITY_WITHOUT_POST_SUBMISSION_LAUNCH"
    return {"tool_ready": tool_ready, "application_events": app, "submission_ts_ns": submission["ts_ns"] if submission is not None else None, "callback_count_total": len(callbacks), "post_submission_callbacks": post, "post_submission_launch_entries": launches, "unmatched_driver_entries": unmatched, "completed_driver_calls": completed, "current_matcher_launch_apis": sorted(CURRENT_MATCHER_LAUNCH_APIS), "unhandled_launch_api_names": unhandled_launches, "classification": classification}


def _validate(args: argparse.Namespace) -> None:
    if args.runtime_code_commit != git_head():
        raise ContractError("declared runtime code commit differs from this checkout")
    if args.wall_limit_seconds != WALL_LIMIT_SECONDS or args.cuda_module_loading not in {"LAZY", "EAGER", "UNSET"}:
        raise ContractError("callback census requires a fixed <=30s cap and LAZY/EAGER/UNSET mode")
    if args.tool_path is None or not args.tool_path.is_file() or not valid_sha256(args.tool_sha256 or "") or sha256_file(args.tool_path) != args.tool_sha256:
        raise ContractError("callback census requires a materialized hash-closed tool")
    if not valid_sha256(args.expected_libtorch_cuda_sha256) or not args.nvdisasm:
        raise ContractError("callback census lacks runtime identity or nvdisasm contract")
    for path in (args.receipt, args.stdout_path, args.stderr_path, args.stage_path, args.child_receipt, args.snapshot_dir, args.analysis_path):
        if path.exists():
            raise ContractError(f"callback census refuses to overwrite payload: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id:
            raise ValueError
    except ValueError as exc:
        raise ContractError("callback census run ID must be canonical UUID") from exc


def parent_main(args: argparse.Namespace) -> int:
    _validate(args)
    identity = {"deployment_id": "c16_retry570_exact_indexselect_callback_census", "scenario_id": "R2_D0_I64_A_CALLBACK_CENSUS_ONLY", "run_id": args.run_id, "implementation_key": "NVBIT_CALLBACK_CENSUS_ONLY_NO_INTROSPECTION"}
    MeasurementActive.assert_available(args.budget_ledger)
    started, timed_out, snapshots, process = time.monotonic(), False, [], None
    try:
        with BudgetLease(args.budget_ledger, identity, "NVBIT_CALLBACK_CENSUS_ONLY_DIAGNOSTIC", capture=False) as lease:
            with MeasurementActive(args.budget_ledger, identity, "NVBIT_CALLBACK_CENSUS_ONLY_DIAGNOSTIC"):
                environment = os.environ.copy()
                environment.pop("LD_PRELOAD", None)
                environment.pop("CUDA_INJECTION64_PATH", None)
                for key in tuple(environment):
                    if key.startswith("C16_NVBIT_"):
                        environment.pop(key)
                environment.update(nvdisasm_environment_contract(Path(args.nvdisasm), environment.get("PATH", "")))
                if args.cuda_module_loading == "UNSET":
                    environment.pop("CUDA_MODULE_LOADING", None)
                else:
                    environment["CUDA_MODULE_LOADING"] = args.cuda_module_loading
                environment.update({"CUDA_INJECTION64_PATH": str(args.tool_path), "C16_NVBIT_LD_PRELOAD_DECLARATION": str(args.tool_path), "CALLBACK_CENSUS_ONLY": "1"})
                args.snapshot_dir.mkdir(parents=True)
                with args.stdout_path.open("w", encoding="utf-8") as stdout, args.stderr_path.open("w", encoding="utf-8") as stderr:
                    process = subprocess.Popen(_child_command(args), stdout=stdout, stderr=stderr, text=True, env=environment, start_new_session=True)
                    operation_anchor_seen_at: float | None = None
                    operation_anchor_event: str | None = None
                    remaining = list(SNAPSHOT_OFFSETS_SECONDS)
                    while process.poll() is None:
                        stage = _read_stage(args.stage_path)
                        if stage and stage.get("event") == "EXACT_TARGET_SUBMISSION_BEGIN":
                            operation_anchor_seen_at, operation_anchor_event = time.monotonic(), "EXACT_TARGET_SUBMISSION_BEGIN"
                        elif operation_anchor_seen_at is None and stage and stage.get("event") == "ROUND_BEGIN":
                            operation_anchor_seen_at, operation_anchor_event = time.monotonic(), "ROUND_BEGIN_PRE_SUBMISSION"
                        if operation_anchor_seen_at is not None and remaining and time.monotonic() - operation_anchor_seen_at >= remaining[0]:
                            offset = remaining.pop(0)
                            snapshots.append(_process_snapshot(process.pid, offset, args.snapshot_dir, str(operation_anchor_event), time.monotonic() - operation_anchor_seen_at))
                        if time.monotonic() - started >= args.wall_limit_seconds:
                            timed_out = True
                            _kill_process_group(process)
                            break
                        time.sleep(0.05)
                    if process.poll() is None:
                        _kill_process_group(process)
            elapsed = time.monotonic() - started
            child_exit = process.returncode if process is not None else None
            analysis = analyze(args.stdout_path)
            atomic_json(args.analysis_path, analysis)
            terminal = "BOUNDED_TIMEOUT" if timed_out else "COMPLETE" if child_exit == 0 else "FAILED_OR_ABORTED"
            status = "CALLBACK_CENSUS_" + terminal
            lease.finish(elapsed_seconds=elapsed, raw_bytes=0, terminal_status=terminal, evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC", diagnostic_reason="CALLBACK_CENSUS_ONLY_ALL_DRIVER_CALLBACKS_NO_INTROSPECTION_INSTRUMENTATION_TRACE_OR_SCIENTIFIC_CAPTURE")
        atomic_json(args.receipt, {"schema_version": SCHEMA, "status": status, "terminal_status": terminal, "scientific_eligible": False, "diagnostic_only": True, "not_for_trace": True, "not_for_scientific_capture": True, "not_for_c_target": True, "not_for_native_timing": True, "runtime_code_commit": args.runtime_code_commit, "run_id": args.run_id, "cuda_module_loading_requested": args.cuda_module_loading, "wall_limit_seconds": args.wall_limit_seconds, "tool": {"path": str(args.tool_path), "sha256": args.tool_sha256}, "elapsed_seconds": elapsed, "child_exit_code": child_exit, "analysis": {"path": str(args.analysis_path), "sha256": sha256_file(args.analysis_path), "classification": analysis["classification"]}, "snapshots": snapshots, "stdout": {"path": str(args.stdout_path), "sha256": sha256_file(args.stdout_path)}, "stderr": {"path": str(args.stderr_path), "sha256": sha256_file(args.stderr_path)}, "trace_generated": False, "raw_trace_bytes": 0})
        return 0 if terminal == "COMPLETE" else 2
    except Exception:
        if process is not None:
            _kill_process_group(process)
        raise


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--child", action="store_true")
    value.add_argument("--receipt", type=Path)
    value.add_argument("--stdout-path", type=Path)
    value.add_argument("--stderr-path", type=Path)
    value.add_argument("--stage-path", type=Path, required=True)
    value.add_argument("--child-receipt", type=Path, required=True)
    value.add_argument("--analysis-path", type=Path)
    value.add_argument("--snapshot-dir", type=Path)
    value.add_argument("--budget-ledger", type=Path)
    value.add_argument("--wall-limit-seconds", type=int, default=WALL_LIMIT_SECONDS)
    value.add_argument("--cuda-module-loading", default="UNSET")
    value.add_argument("--tool-path", type=Path)
    value.add_argument("--tool-sha256")
    value.add_argument("--nvdisasm")
    value.add_argument("--expected-torch-version", required=True)
    value.add_argument("--expected-torch-cuda", required=True)
    value.add_argument("--expected-libtorch-cuda-sha256", required=True)
    value.add_argument("--expected-gpu-name", default="NVIDIA GeForce RTX 3090")
    value.add_argument("--expected-driver", default="570.124.04")
    value.add_argument("--expected-gpu-uuid")
    value.add_argument("--runtime-code-commit")
    value.add_argument("--run-id")
    return value


def main() -> None:
    args = parser().parse_args()
    if args.child:
        raise SystemExit(child_main(args))
    needed = (args.receipt, args.stdout_path, args.stderr_path, args.analysis_path, args.snapshot_dir, args.budget_ledger, args.runtime_code_commit, args.run_id)
    if any(item is None for item in needed):
        raise ContractError("callback census parent requires receipt, logs, analysis, snapshots, ledger, source commit, and run ID")
    raise SystemExit(parent_main(args))


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL Retry570 callback census: {exc}", file=sys.stderr)
        raise SystemExit(2)
