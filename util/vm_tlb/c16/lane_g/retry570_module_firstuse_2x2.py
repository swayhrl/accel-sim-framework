#!/usr/bin/env python3
"""Bounded native/NVBit 2x2 for Retry570 CUDA library/module first use.

This program is diagnostic-only.  Its one exact ``torch.index_select``
reproducer is deliberately identical in every case.  The only variables are
the requested CUDA module loading mode and whether the already hash-closed
NVBit callback-census tool is injected.  That tool observes CUDA driver API
callbacks but performs *no* NVBit function/instruction discovery, insertion,
enablement, tracing, or capture.

The child intentionally does not call ``torch.cuda.synchronize``.  A return
from ``torch.index_select`` is therefore an application dispatch boundary,
not a timing or kernel-completion result.
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
from retry570_long_watch import gpu_snapshot, nvdisasm_environment_contract


SCHEMA = "C16_G_RETRY570_MODULE_FIRST_USE_2X2_V1"
WALL_LIMIT_SECONDS = 25
SNAPSHOT_OFFSETS_SECONDS = (2, 5, 10)
EXACT_CANDIDATE = {
    "candidate_id": "R2_D0_I64_A",
    "shape": (64, 32),
    "dim": 0,
    "index_dtype": "int64",
    "index_count": 64,
}
MODES = frozenset({"NATIVE", "NVBIT_CALLBACK_CENSUS_ONLY", "NVBIT_CALLBACK_CENSUS_RAW", "NVBIT_EMPTY_CALLBACK_TOOL"})
LOADING = frozenset({"LAZY", "EAGER"})
ALLOWED_NVBIT_VERSIONS = frozenset({"1.8", "1.7.5", "1.7.7.3"})


def _now_ns() -> int:
    return time.monotonic_ns()


def _app_event(stage_path: Path, event: str, **fields: Any) -> dict[str, Any]:
    row = {"schema_version": SCHEMA, "ts_ns": _now_ns(), "event": event, **fields}
    atomic_json(stage_path, row)
    print("C16_MODULE_FIRST_USE_APP " + " ".join(f"{key}={value}" for key, value in row.items()), flush=True)
    return row


def _allow_gdb_attach() -> int:
    """Permit a sibling batch gdb process to inspect this diagnostic child.

    Containers frequently omit CAP_SYS_PTRACE even for root.  This per-process
    opt-in is narrower than altering system ptrace policy and exists only to
    make the requested diagnostic stack snapshots possible.
    """
    libc = ctypes.CDLL(None, use_errno=True)
    result = int(libc.prctl(0x59616D61, -1, 0, 0, 0))  # PR_SET_PTRACER, ANY
    if result != 0:
        raise ContractError(f"PR_SET_PTRACER_ANY failed errno={ctypes.get_errno()}")
    return result


def _module_loading_mode() -> dict[str, Any]:
    try:
        driver = ctypes.CDLL("libcuda.so.1")
        function = driver.cuModuleGetLoadingMode
        function.argtypes = [ctypes.POINTER(ctypes.c_int)]
        function.restype = ctypes.c_int
        mode = ctypes.c_int(-1)
        result = int(function(ctypes.byref(mode)))
        return {
            "cu_result": result,
            "mode_value": mode.value,
            "mode_name": {1: "CU_MODULE_EAGER_LOADING", 2: "CU_MODULE_LAZY_LOADING"}.get(mode.value, "UNKNOWN"),
        }
    except (AttributeError, OSError) as exc:
        return {"query_error": f"{type(exc).__name__}: {exc}"}


def _one_exact_operation(torch: Any, stage_path: Path) -> None:
    """Emit the immutable R2_D0_I64_A preparation/operation boundaries.

    No call in this function synchronizes CUDA or consumes output values on
    the host.  The exact-operation return marker is intentionally only a
    Python/ATen dispatch-return observation.
    """
    _app_event(stage_path, "BEFORE_TORCH_MANUAL_SEED")
    torch.manual_seed(570)
    _app_event(stage_path, "AFTER_TORCH_MANUAL_SEED")
    _app_event(stage_path, "BEFORE_TORCH_ARANGE_INDEX")
    indices = (torch.arange(EXACT_CANDIDATE["index_count"], device="cuda:0", dtype=torch.int64) * 17) % EXACT_CANDIDATE["shape"][0]
    _app_event(stage_path, "AFTER_TORCH_ARANGE_INDEX")
    _app_event(stage_path, "BEFORE_TORCH_RANDN_SOURCE")
    source = torch.randn(EXACT_CANDIDATE["shape"], device="cuda:0", dtype=torch.float16)
    _app_event(stage_path, "AFTER_TORCH_RANDN_SOURCE")
    _app_event(stage_path, "BEFORE_EXACT_OPERATION")
    _app_event(stage_path, "EXACT_TARGET_SUBMISSION_BEGIN")
    output = torch.index_select(source, int(EXACT_CANDIDATE["dim"]), indices)
    if output.device.type != "cuda" or list(output.shape) != [64, 32]:
        raise ContractError("exact index_select candidate produced an unexpected output shape/device")
    _app_event(stage_path, "EXACT_OPERATION_RETURN")
    # Deliberately no synchronize, .item(), checksum, trace, or capture.
    del output, source, indices


def child_main(args: argparse.Namespace) -> int:
    try:
        _app_event(args.stage_path, "PROCESS_START", mode=args.mode, cuda_module_loading=args.cuda_module_loading)
        _allow_gdb_attach()
        _app_event(args.stage_path, "PTRACE_ATTACH_AUTHORIZED")
        _app_event(args.stage_path, "TORCH_IMPORT_BEGIN")
        torch, identity = assert_runtime_identity(args)
        _app_event(args.stage_path, "RUNTIME_IDENTITY_CLOSED", runtime_identity=identity)
        if not torch.cuda.is_available():
            raise ContractError("CUDA unavailable; refusing CPU fallback")
        _app_event(args.stage_path, "CUDA_INIT_BEGIN")
        torch.cuda.init()
        _app_event(args.stage_path, "CUDA_INIT_COMPLETE")
        _app_event(args.stage_path, "MODULE_LOADING_MODE_QUERY", **_module_loading_mode())
        _one_exact_operation(torch, args.stage_path)
        atomic_json(args.child_receipt, {
            "schema_version": SCHEMA,
            "status": "CHILD_COMPLETE_NO_SYNCHRONIZE",
            "terminal_status": "COMPLETE",
            "scientific_eligible": False,
            "diagnostic_only": True,
            "runtime_identity": identity,
            "mode": args.mode,
            "cuda_module_loading": args.cuda_module_loading,
            "exact_candidate": EXACT_CANDIDATE,
        })
        _app_event(args.stage_path, "CHILD_COMPLETE")
        return 0
    except Exception as exc:
        atomic_json(args.child_receipt, {
            "schema_version": SCHEMA,
            "status": "CHILD_FAILED",
            "terminal_status": "FAILED_OR_ABORTED",
            "scientific_eligible": False,
            "message": str(exc),
        })
        _app_event(args.stage_path, "CHILD_FAILED", message=str(exc))
        print(f"FAIL Retry570 module-first-use child: {exc}", file=sys.stderr, flush=True)
        return 2


def _run_text_safe(command: list[str], timeout_seconds: int = 6) -> dict[str, Any]:
    try:
        completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout_seconds, check=False)
        return {"command": command, "returncode": completed.returncode, "output": completed.stdout}
    except subprocess.TimeoutExpired as exc:
        return {"command": command, "returncode": "TIMEOUT", "output": (exc.stdout or "") + (exc.stderr or "")}
    except OSError as exc:
        return {"command": command, "returncode": "UNAVAILABLE", "output": f"{type(exc).__name__}: {exc}"}


def _snapshot(pid: int, ordinal: int, output: Path, anchor_event: str, anchor_elapsed_seconds: float, with_gdb: bool, map_inspection: bool) -> dict[str, Any]:
    commands = {
        "threads": _run_text_safe(["ps", "-L", "-p", str(pid), "-o", "pid,tid,stat,pcpu,etime,wchan:32,comm"]),
        "pstree": _run_text_safe(["pstree", "-ap", str(pid)]),
        "processes": _run_text_safe(["ps", "-eo", "pid,ppid,stat,pcpu,etime,wchan:32,args"]),
        "maps": _run_text_safe(["cat", f"/proc/{pid}/maps"]),
    }
    commands["processes"]["output"] = "\n".join(
        line for line in str(commands["processes"]["output"]).splitlines()
        if any(token in line for token in ("python", "nvbit", "nvdisasm"))
    )
    record: dict[str, Any] = {
        "schema_version": SCHEMA,
        "ordinal": ordinal,
        "pid": pid,
        "anchor_event": anchor_event,
        "anchor_elapsed_seconds": anchor_elapsed_seconds,
        "commands": commands,
        **gpu_snapshot(pid),
    }
    if with_gdb:
        # Attach before queuing expressions: gdb otherwise accepts the
        # commands but evaluates them before an inferior is selected.
        command = ["gdb", "-q", "-batch", "-p", str(pid), "-ex", "set pagination off", "-ex", "set print elements 2"]
        if map_inspection:
            # The debug census tool only declares this external vendor-core
            # object so gdb has its true C++ type.  No inferior expression is
            # evaluated by the callback itself.
            command.extend((
                "-ex", "thread apply all bt full", "-ex", "info sharedlibrary",
                # `elfModuleHashMap` is a vendor object with no vendor DWARF.
                # The null, static type anchor supplies only a type for this
                # address cast; it is never evaluated by the callback.
                "-ex", "set $c16_elf_module_map = (NvbitElfModuleMap*) &elfModuleHashMap",
                "-ex", "p $c16_elf_module_map->_M_h._M_element_count",
                "-ex", "p $c16_elf_module_map->_M_h._M_bucket_count",
                "-ex", "p $c16_elf_module_map->_M_h._M_rehash_policy._M_max_load_factor",
                "-ex", "p $c16_elf_module_map->_M_h._M_before_begin._M_nxt->_M_v.first",
                "-ex", "p $c16_elf_module_map->_M_h._M_before_begin._M_nxt->_M_v.first.size()",
                "-ex", "p $c16_elf_module_map->_M_h._M_before_begin._M_nxt->_M_v.second._M_impl._M_finish - $c16_elf_module_map->_M_h._M_before_begin._M_nxt->_M_v.second._M_impl._M_start",
                # The vendor core lacks argument DWARF.  At frame 1 (the
                # observed `operator[]` caller of `_Hash_bytes`) rsi is its
                # const std::string& key under the matched legacy ABI.  These
                # commands only read stopped-process memory.
                "-ex", "frame 1", "-ex", "info registers rdi rsi",
                "-ex", "x/s *((char**)$rsi)",
                "-ex", "p *(unsigned long long*)(*((char**)$rsi) - 24)",
            ))
        else:
            command.extend(("-ex", "thread apply all bt"))
        record["native_backtrace"] = _run_text_safe(command)
        record["native_backtrace"]["diagnostic_perturbation"] = True
    path = output / f"snapshot_{ordinal:02d}.json"
    atomic_json(path, record)
    return {"path": str(path), "sha256": sha256_file(path), "anchor_event": anchor_event, "anchor_elapsed_seconds": anchor_elapsed_seconds}


def _kill_process_group(process: subprocess.Popen[str]) -> dict[str, Any]:
    """External supervisor cleanup for the dedicated child process group."""
    result: dict[str, Any] = {"required": False, "term_sent": False, "kill_sent": False, "grace_seconds": 2}
    if process.poll() is not None:
        return result
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return result
    result["required"] = True
    result["term_sent"] = True
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        result["kill_sent"] = True
        process.wait(timeout=2)
    return result


def _read_stage(path: Path) -> dict[str, Any] | None:
    try:
        item = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return item if isinstance(item, dict) else None


def _parse_app(line: str) -> dict[str, Any] | None:
    if not line.startswith("C16_MODULE_FIRST_USE_APP "):
        return None
    values = dict(re.findall(r"(\w+)=([^ ]+)", line))
    try:
        return {"ts_ns": int(values["ts_ns"]), "event": values["event"]}
    except (KeyError, ValueError) as exc:
        raise ContractError("module-first-use application row is malformed") from exc


def _parse_callback(line: str) -> dict[str, Any] | None:
    if not line.startswith("C16_CALLBACK_CENSUS ts_ns="):
        return None
    values = dict(re.findall(r"(\w+)=([^ ]+)", line))
    try:
        return {
            "ts_ns": int(values["ts_ns"]), "seq": int(values["seq"]), "is_exit": int(values["is_exit"]),
            "cbid": int(values["cbid"]), "callback": values["callback"],
        }
    except (KeyError, ValueError) as exc:
        raise ContractError("module-first-use callback row is malformed") from exc


def _intervals(rows: list[dict[str, Any]], callback: str) -> list[dict[str, Any]]:
    pending: list[dict[str, Any]] = []
    result: list[dict[str, Any]] = []
    for row in (value for value in rows if value["callback"] == callback):
        if row["is_exit"] == 0:
            pending.append(row)
        elif pending:
            entered = pending.pop()
            result.append({"entry_ts_ns": entered["ts_ns"], "exit_ts_ns": row["ts_ns"], "elapsed_ns": row["ts_ns"] - entered["ts_ns"], "cbid": row["cbid"]})
    result.extend({"entry_ts_ns": item["ts_ns"], "exit_ts_ns": None, "elapsed_ns": None, "cbid": item["cbid"]} for item in pending)
    return result


def analyze(stdout_path: Path, mode: str) -> dict[str, Any]:
    app, callbacks = [], []
    text = stdout_path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        item = _parse_app(line)
        if item is not None:
            app.append(item)
        item = _parse_callback(line)
        if item is not None:
            callbacks.append(item)
    app_by_name = {item["event"]: item["ts_ns"] for item in app}
    submission = app_by_name.get("EXACT_TARGET_SUBMISSION_BEGIN")
    post = [item for item in callbacks if submission is not None and item["ts_ns"] >= submission]
    launches = [item for item in post if item["is_exit"] == 0 and (item["callback"].startswith("cuLaunch") or item["callback"].startswith("cuGraphLaunch"))]
    return {
        "mode": mode,
        "tool_ready": any(marker in text for marker in (
            "C16_CALLBACK_CENSUS_TOOL_READY mode=CALLBACK_CENSUS_ONLY",
            "C16_CALLBACK_CENSUS_RAW_TOOL_READY", "C16_EMPTY_CALLBACK_TOOL_READY",
        )),
        "app_events": app,
        "callback_count": len(callbacks),
        "post_submission_callbacks": post,
        "timeline": {
            "PROCESS_START": app_by_name.get("PROCESS_START"),
            "BEFORE_TORCH_ARANGE_INDEX": app_by_name.get("BEFORE_TORCH_ARANGE_INDEX"),
            "EXACT_TARGET_SUBMISSION_BEGIN": submission,
            "cuLibraryLoadData": _intervals(post, "cuLibraryLoadData") if mode != "NATIVE" else "NOT_OBSERVABLE_WITHOUT_NVBIT_CALLBACK_STREAM",
            "cuLibraryGetModule": _intervals(post, "cuLibraryGetModule") if mode != "NATIVE" else "NOT_OBSERVABLE_WITHOUT_NVBIT_CALLBACK_STREAM",
            "first_launch_api": launches[0] if launches else None,
            "EXACT_OPERATION_RETURN": app_by_name.get("EXACT_OPERATION_RETURN"),
        },
    }


def _child_command(args: argparse.Namespace) -> list[str]:
    result = [
        sys.executable, str(Path(__file__).resolve()), "--child", "--stage-path", str(args.stage_path),
        "--child-receipt", str(args.child_receipt), "--mode", args.mode, "--cuda-module-loading", args.cuda_module_loading,
        "--expected-torch-version", args.expected_torch_version, "--expected-torch-cuda", args.expected_torch_cuda,
        "--expected-libtorch-cuda-sha256", args.expected_libtorch_cuda_sha256, "--expected-gpu-name", args.expected_gpu_name,
        "--expected-driver", args.expected_driver,
    ]
    if args.expected_gpu_uuid:
        result.extend(("--expected-gpu-uuid", args.expected_gpu_uuid))
    return result


def _validate(args: argparse.Namespace) -> None:
    if args.runtime_code_commit != git_head():
        raise ContractError("declared runtime code commit differs from this checkout")
    if args.mode not in MODES or args.cuda_module_loading not in LOADING or args.wall_limit_seconds != WALL_LIMIT_SECONDS:
        raise ContractError("2x2 requires fixed native/callback-only mode, LAZY/EAGER, and 25-second cap")
    if args.nvbit_version not in ALLOWED_NVBIT_VERSIONS:
        raise ContractError("NVBit version is outside the frozen version-differential matrix")
    if args.mode != "NATIVE":
        if args.tool_path is None or not args.tool_path.is_file() or not valid_sha256(args.tool_sha256 or "") or sha256_file(args.tool_path) != args.tool_sha256:
            raise ContractError("injected callback mode requires a materialized hash-closed tool")
    if args.mode == "NVBIT_CALLBACK_CENSUS_RAW":
        if args.raw_event_path is None:
            raise ContractError("raw callback census requires a fixed event-buffer path")
        if args.raw_event_path.exists():
            raise ContractError("raw callback census refuses to overwrite its event buffer")
        args.raw_event_path.parent.mkdir(parents=True, exist_ok=True)
    if not valid_sha256(args.expected_libtorch_cuda_sha256) or not args.nvdisasm:
        raise ContractError("2x2 lacks runtime identity or nvdisasm environment contract")
    for path in (args.receipt, args.stdout_path, args.stderr_path, args.stage_path, args.child_receipt, args.analysis_path, args.snapshot_dir):
        if path.exists():
            raise ContractError(f"2x2 refuses to overwrite payload: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id:
            raise ValueError
    except ValueError as exc:
        raise ContractError("2x2 run ID must be canonical UUID") from exc


def parent_main(args: argparse.Namespace) -> int:
    _validate(args)
    identity = {
        "deployment_id": "c16_retry570_exact_indexselect_module_first_use_2x2",
        "scenario_id": "R2_D0_I64_A_DIAGNOSTIC_ONLY",
        "run_id": args.run_id,
        "implementation_key": args.mode,
    }
    MeasurementActive.assert_available(args.budget_ledger)
    started, timed_out, snapshots, process = time.monotonic(), False, [], None
    cleanup: dict[str, Any] = {"required": False, "term_sent": False, "kill_sent": False, "grace_seconds": 2}
    try:
        with BudgetLease(args.budget_ledger, identity, "NVBIT_MODULE_FIRST_USE_2X2_DIAGNOSTIC", capture=False) as lease:
            with MeasurementActive(args.budget_ledger, identity, "NVBIT_MODULE_FIRST_USE_2X2_DIAGNOSTIC"):
                environment = os.environ.copy()
                environment.pop("LD_PRELOAD", None)
                environment.pop("CUDA_INJECTION64_PATH", None)
                for key in tuple(environment):
                    if key.startswith("C16_NVBIT_"):
                        environment.pop(key)
                environment.update(nvdisasm_environment_contract(Path(args.nvdisasm), environment.get("PATH", "")))
                environment["CUDA_MODULE_LOADING"] = args.cuda_module_loading
                if args.mode != "NATIVE":
                    environment.update({
                        "CUDA_INJECTION64_PATH": str(args.tool_path),
                        "C16_NVBIT_LD_PRELOAD_DECLARATION": str(args.tool_path),
                    })
                if args.mode == "NVBIT_CALLBACK_CENSUS_ONLY":
                    environment["CALLBACK_CENSUS_ONLY"] = "1"
                elif args.mode == "NVBIT_CALLBACK_CENSUS_RAW":
                    environment["C16_CALLBACK_CENSUS_RAW_PATH"] = str(args.raw_event_path)
                args.snapshot_dir.mkdir(parents=True)
                with args.stdout_path.open("w", encoding="utf-8") as stdout, args.stderr_path.open("w", encoding="utf-8") as stderr:
                    process = subprocess.Popen(_child_command(args), stdout=stdout, stderr=stderr, text=True, env=environment, start_new_session=True)
                    anchor_seen_at: float | None = None
                    anchor_event = "NO_APP_ANCHOR"
                    remaining = list(SNAPSHOT_OFFSETS_SECONDS)
                    while process.poll() is None:
                        stage = _read_stage(args.stage_path)
                        if stage and stage.get("event") == "EXACT_TARGET_SUBMISSION_BEGIN" and anchor_event != "EXACT_TARGET_SUBMISSION_BEGIN":
                            # stage.json is intentionally the latest marker.  Once the
                            # exact boundary is observed, do not reset its clock on
                            # every polling iteration or snapshots never become due.
                            anchor_seen_at, anchor_event = time.monotonic(), "EXACT_TARGET_SUBMISSION_BEGIN"
                        elif stage and stage.get("event") == "BEFORE_TORCH_ARANGE_INDEX" and anchor_seen_at is None:
                            anchor_seen_at, anchor_event = time.monotonic(), "BEFORE_TORCH_ARANGE_INDEX"
                        if anchor_seen_at is not None and remaining and time.monotonic() - anchor_seen_at >= remaining[0]:
                            ordinal = remaining.pop(0)
                            snapshots.append(_snapshot(process.pid, ordinal, args.snapshot_dir, anchor_event, time.monotonic() - anchor_seen_at, args.gdb_snapshots, args.gdb_map_inspection))
                        if time.monotonic() - started >= args.wall_limit_seconds:
                            timed_out = True
                            cleanup = _kill_process_group(process)
                            break
                        time.sleep(0.05)
                    if process.poll() is None:
                        cleanup = _kill_process_group(process)
            elapsed = time.monotonic() - started
            child_exit = process.returncode if process is not None else None
            analysis = analyze(args.stdout_path, args.mode)
            atomic_json(args.analysis_path, analysis)
            terminal = "BOUNDED_TIMEOUT" if timed_out else "COMPLETE" if child_exit == 0 else "FAILED_OR_ABORTED"
            lease.finish(
                elapsed_seconds=elapsed,
                raw_bytes=0,
                terminal_status=terminal,
                evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC",
                diagnostic_reason="EXACT_REPRODUCER_NATIVE_NVBIT_2X2_NO_DISCOVERY_NO_INSERTION_NO_ENABLE_NO_SYNCHRONIZE_NO_TRACE_NO_CAPTURE",
            )
        atomic_json(args.receipt, {
            "schema_version": SCHEMA,
            "status": "MODULE_FIRST_USE_2X2_" + terminal,
            "terminal_status": terminal,
            "scientific_eligible": False,
            "diagnostic_only": True,
            "not_for_trace": True,
            "not_for_scientific_capture": True,
            "not_for_c_target": True,
            "not_for_native_timing": True,
            "runtime_code_commit": args.runtime_code_commit,
            "nvbit_version": args.nvbit_version,
            "run_id": args.run_id,
            "mode": args.mode,
            "cuda_module_loading_requested": args.cuda_module_loading,
            "target_hard_budget_s": args.wall_limit_seconds,
            "target_wall_s": elapsed,
            "target_group_cleanup": cleanup,
            "wall_limit_seconds": args.wall_limit_seconds,
            "exact_candidate": EXACT_CANDIDATE,
            "tool": {"path": str(args.tool_path), "sha256": args.tool_sha256} if args.mode != "NATIVE" else "NOT_INJECTED",
            "elapsed_seconds": elapsed,
            "child_exit_code": child_exit,
            "analysis": {"path": str(args.analysis_path), "sha256": sha256_file(args.analysis_path)},
            "snapshots": snapshots,
            "stdout": {"path": str(args.stdout_path), "sha256": sha256_file(args.stdout_path)},
            "stderr": {"path": str(args.stderr_path), "sha256": sha256_file(args.stderr_path)},
            "raw_trace_bytes": 0,
            "trace_generated": False,
            "raw_callback_event_buffer": (
                {"path": str(args.raw_event_path), "bytes": args.raw_event_path.stat().st_size, "sha256": sha256_file(args.raw_event_path)}
                if args.raw_event_path is not None and args.raw_event_path.is_file() else "NOT_MATERIALIZED"
            ),
        })
        return 0 if terminal == "COMPLETE" else 2
    except Exception:
        if process is not None:
            _kill_process_group(process)
        raise


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--child", action="store_true")
    result.add_argument("--receipt", type=Path)
    result.add_argument("--stdout-path", type=Path)
    result.add_argument("--stderr-path", type=Path)
    result.add_argument("--stage-path", type=Path, required=True)
    result.add_argument("--child-receipt", type=Path, required=True)
    result.add_argument("--analysis-path", type=Path)
    result.add_argument("--snapshot-dir", type=Path)
    result.add_argument("--budget-ledger", type=Path)
    result.add_argument("--mode", required=True)
    result.add_argument("--cuda-module-loading", required=True)
    result.add_argument("--gdb-snapshots", action="store_true")
    result.add_argument("--gdb-map-inspection", action="store_true")
    result.add_argument("--wall-limit-seconds", type=int, default=WALL_LIMIT_SECONDS)
    result.add_argument("--tool-path", type=Path)
    result.add_argument("--tool-sha256")
    result.add_argument("--raw-event-path", type=Path)
    result.add_argument("--nvdisasm")
    result.add_argument("--expected-torch-version", required=True)
    result.add_argument("--expected-torch-cuda", required=True)
    result.add_argument("--expected-libtorch-cuda-sha256", required=True)
    result.add_argument("--expected-gpu-name", default="NVIDIA GeForce RTX 3090")
    result.add_argument("--expected-driver", default="570.124.04")
    result.add_argument("--expected-gpu-uuid")
    result.add_argument("--runtime-code-commit")
    result.add_argument("--run-id")
    result.add_argument("--nvbit-version", default="1.8")
    return result


def main() -> None:
    args = parser().parse_args()
    if args.child:
        raise SystemExit(child_main(args))
    required = (args.receipt, args.stdout_path, args.stderr_path, args.analysis_path, args.snapshot_dir, args.budget_ledger, args.runtime_code_commit, args.run_id)
    if any(value is None for value in required):
        raise ContractError("2x2 parent requires output paths, ledger, source commit, and run ID")
    raise SystemExit(parent_main(args))


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL Retry570 module-first-use 2x2: {exc}", file=sys.stderr)
        raise SystemExit(2)
