#!/usr/bin/env python3
"""Bounded, diagnostic-only PyTorch/NVBit first-kernel stage isolator.

The parent owns exactly one non-capture budget lease per independent C0--C4
process.  The child never opens a lease.  No mode writes a trace or represents
a C target, timing result, model result, or a replacement for the already
closed Retry570 diagnostic windows.
"""
from __future__ import annotations

import argparse
import json
import os
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


SCHEMA = "C16_G_RETRY570_PYTORCH_STAGE_DIAGNOSTIC_V1"
WALL_LIMIT_SECONDS = 60
SAMPLE_SECONDS = 5
TESTCASES = (
    "C0_TORCH_CUDA_INIT",
    "C1_GPU_ALLOCATION",
    "C2_TENSOR_FILL_FIRST_KERNEL",
    "C3_ELEMENTWISE_FIRST_KERNEL",
    "C4_SMALL_GEMM_LIBRARY_KERNEL",
)


def _now() -> float:
    return time.monotonic()


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _tail_markers(path: Path) -> list[str]:
    try:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            handle.seek(max(0, handle.tell() - 2 * 1024 * 1024))
            text = handle.read().decode("utf-8", errors="replace")
    except OSError:
        return []
    return [line for line in text.splitlines() if line.startswith("C16_NVBIT_TIMING")]


def _stage(path: Path, started: float, name: str, **extra: Any) -> None:
    payload = {"schema_version": SCHEMA, "stage": name, "elapsed_seconds": _now() - started, **extra}
    atomic_json(path, payload)
    print("C16_STAGE_DIAGNOSTIC " + json.dumps(payload, sort_keys=True), flush=True)


def _kill_process_group(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            return
        process.wait(timeout=10)


def _proc_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError as exc:
        return f"UNAVAILABLE: {type(exc).__name__}: {exc}"


def stack_snapshot(pid: int, directory: Path, ordinal: int, elapsed_seconds: float) -> Path:
    """Capture Linux-native, read-only thread state without debugger attach."""
    directory.mkdir(parents=True, exist_ok=True)
    rows = [
        f"schema_version={SCHEMA}",
        f"sample_ordinal={ordinal}",
        f"sample_elapsed_seconds={elapsed_seconds:.6f}",
        f"pid={pid}",
    ]
    task_root = Path("/proc") / str(pid) / "task"
    try:
        tids = sorted(item.name for item in task_root.iterdir() if item.name.isdigit())
    except OSError as exc:
        tids = []
        rows.append(f"task_enumeration=UNAVAILABLE: {type(exc).__name__}: {exc}")
    for tid in tids:
        base = task_root / tid
        rows.extend((
            f"\n=== tid={tid} status ===\n{_proc_text(base / 'status')}",
            f"\n=== tid={tid} wchan ===\n{_proc_text(base / 'wchan')}",
            f"\n=== tid={tid} syscall ===\n{_proc_text(base / 'syscall')}",
            f"\n=== tid={tid} kernel_stack ===\n{_proc_text(base / 'stack')}",
        ))
    path = directory / f"stack_snapshot_{ordinal:03d}.txt"
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return path


def _timestamp_stage(started: float) -> dict[str, Any]:
    return {"monotonic_seconds": _now(), "elapsed_seconds": _now() - started}


def child_main(args: argparse.Namespace) -> int:
    started = _now()
    try:
        _stage(args.stage_path, started, "PROCESS_START", testcase=args.testcase)
        _stage(args.stage_path, started, "TORCH_IMPORT_BEGIN")
        import torch

        _stage(args.stage_path, started, "TORCH_IMPORT_COMPLETE", torch_version=torch.__version__, torch_cuda=torch.version.cuda)
        if not torch.cuda.is_available():
            raise ContractError("CUDA is unavailable; CPU fallback is forbidden")
        _stage(args.stage_path, started, "CUDA_INIT_BEGIN")
        torch.cuda.init()
        _stage(args.stage_path, started, "CUDA_INIT_COMPLETE")
        # This routine validates torch/CUDA/libtorch/GPU/driver after the
        # explicit C0 initialization boundary. It does not allocate tensors
        # or submit a voluntary CUDA workload.
        checked_torch, identity = assert_runtime_identity(args)
        if checked_torch.__version__ != torch.__version__:
            raise ContractError("runtime identity imported a different torch module")
        _stage(args.stage_path, started, "RUNTIME_IDENTITY_CLOSED", runtime_identity=identity)
        if args.testcase == "C0_TORCH_CUDA_INIT":
            pass
        elif args.testcase == "C1_GPU_ALLOCATION":
            _stage(args.stage_path, started, "GPU_ALLOCATION_BEGIN")
            value = torch.empty((1,), dtype=torch.float32, device="cuda:0")
            torch.cuda.synchronize()
            del value
            _stage(args.stage_path, started, "GPU_ALLOCATION_COMPLETE")
        elif args.testcase == "C2_TENSOR_FILL_FIRST_KERNEL":
            value = torch.empty((256,), dtype=torch.float32, device="cuda:0")
            _stage(args.stage_path, started, "FIRST_CUDA_KERNEL_SUBMISSION_BEGIN", operation="tensor_fill")
            value.fill_(1.0)
            torch.cuda.synchronize()
            _stage(args.stage_path, started, "FIRST_CUDA_KERNEL_COMPLETED", operation="tensor_fill")
            del value
        elif args.testcase == "C3_ELEMENTWISE_FIRST_KERNEL":
            value = torch.empty((256,), dtype=torch.float32, device="cuda:0")
            _stage(args.stage_path, started, "FIRST_CUDA_KERNEL_SUBMISSION_BEGIN", operation="torch_add")
            result = torch.add(value, 1.0)
            torch.cuda.synchronize()
            _stage(args.stage_path, started, "FIRST_CUDA_KERNEL_COMPLETED", operation="torch_add")
            del result, value
        elif args.testcase == "C4_SMALL_GEMM_LIBRARY_KERNEL":
            left = torch.empty((32, 32), dtype=torch.float16, device="cuda:0")
            right = torch.empty((32, 32), dtype=torch.float16, device="cuda:0")
            _stage(args.stage_path, started, "FIRST_CUDA_KERNEL_SUBMISSION_BEGIN", operation="torch_mm")
            result = torch.mm(left, right)
            torch.cuda.synchronize()
            _stage(args.stage_path, started, "FIRST_CUDA_KERNEL_COMPLETED", operation="torch_mm")
            del result, left, right
        else:  # argparse prevents this; retain a fail-closed internal guard.
            raise ContractError(f"unsupported testcase: {args.testcase}")
        terminal = {
            "schema_version": SCHEMA,
            "status": "CHILD_COMPLETE",
            "testcase": args.testcase,
            "runtime_identity": identity,
            "elapsed_seconds": _now() - started,
            "terminal_status": "COMPLETE",
            "scientific_eligible": False,
        }
        atomic_json(args.child_receipt, terminal)
        _stage(args.stage_path, started, "CHILD_COMPLETE")
        return 0
    except Exception as exc:
        failure = {
            "schema_version": SCHEMA,
            "status": "CHILD_FAILED",
            "testcase": args.testcase,
            "message": str(exc),
            "elapsed_seconds": _now() - started,
            "terminal_status": "FAILED_OR_ABORTED",
            "scientific_eligible": False,
        }
        atomic_json(args.child_receipt, failure)
        _stage(args.stage_path, started, "CHILD_FAILED", message=str(exc))
        print(f"FAIL Retry570 stage child: {exc}", file=sys.stderr, flush=True)
        return 2


def _child_command(args: argparse.Namespace) -> list[str]:
    command = [
        sys.executable, str(Path(__file__).resolve()), "--child", "--testcase", args.testcase,
        "--stage-path", str(args.stage_path), "--child-receipt", str(args.child_receipt),
        "--expected-torch-version", args.expected_torch_version,
        "--expected-torch-cuda", args.expected_torch_cuda,
        "--expected-libtorch-cuda-sha256", args.expected_libtorch_cuda_sha256,
        "--expected-gpu-name", args.expected_gpu_name,
        "--expected-driver", args.expected_driver,
    ]
    if args.expected_gpu_uuid:
        command.extend(("--expected-gpu-uuid", args.expected_gpu_uuid))
    return command


def _validate_parent(args: argparse.Namespace) -> None:
    if args.runtime_code_commit != git_head():
        raise ContractError("declared runtime code commit differs from this source checkout")
    if args.wall_limit_seconds != WALL_LIMIT_SECONDS or args.sample_seconds != SAMPLE_SECONDS:
        raise ContractError("stage diagnostic requires a 60-second limit and 5-second sampling")
    if not valid_sha256(args.expected_libtorch_cuda_sha256):
        raise ContractError("expected libtorch CUDA SHA must be lowercase SHA256")
    if args.mode == "NVBIT":
        if args.tool_path is None or not args.tool_path.is_file() or args.tool_sha256 is None:
            raise ContractError("NVBit stage diagnostic needs a materialized timing-probe tool")
        if not valid_sha256(args.tool_sha256) or sha256_file(args.tool_path) != args.tool_sha256:
            raise ContractError("NVBit stage diagnostic tool path/SHA is not closed")
        if not args.nvdisasm:
            raise ContractError("NVBit stage diagnostic lacks an nvdisasm contract")
    elif args.tool_path is not None or args.tool_sha256 is not None or args.nvdisasm:
        raise ContractError("native stage diagnostic must not declare an NVBit tool")
    for path in (args.receipt, args.samples_path, args.stage_path, args.child_receipt, args.stdout_path, args.stderr_path, args.stack_dir):
        if path.exists():
            raise ContractError(f"stage diagnostic refuses to overwrite payload: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id:
            raise ValueError
    except ValueError as exc:
        raise ContractError("stage diagnostic run ID must be a canonical UUID") from exc


def parent_main(args: argparse.Namespace) -> int:
    _validate_parent(args)
    identity = {
        "deployment_id": "c16_retry570_pytorch_first_kernel_stage_diagnostic",
        "scenario_id": args.testcase,
        "run_id": args.run_id,
        "implementation_key": "PYTORCH_C0_C4_INDEPENDENT_PROCESS_NVBIT_TIMING_PROBE" if args.mode == "NVBIT" else "PYTORCH_C0_C4_INDEPENDENT_PROCESS_NATIVE",
    }
    MeasurementActive.assert_available(args.budget_ledger)
    process: subprocess.Popen[str] | None = None
    started = _now()
    samples: list[dict[str, Any]] = []
    stack_paths: list[Path] = []
    timed_out = False
    nvdisasm_contract: dict[str, str] | None = None
    try:
        with BudgetLease(args.budget_ledger, identity, f"PYTORCH_STAGE_{args.mode}_DIAGNOSTIC", capture=False) as lease:
            with MeasurementActive(args.budget_ledger, identity, f"PYTORCH_STAGE_{args.mode}_DIAGNOSTIC"):
                environment = os.environ.copy()
                environment.pop("LD_PRELOAD", None)
                environment.pop("CUDA_INJECTION64_PATH", None)
                for name in tuple(environment):
                    if name.startswith("C16_NVBIT_"):
                        environment.pop(name)
                if args.mode == "NVBIT":
                    assert args.tool_path is not None and args.nvdisasm is not None
                    nvdisasm_contract = nvdisasm_environment_contract(Path(args.nvdisasm), environment.get("PATH", ""))
                    environment.update(nvdisasm_contract)
                    environment["CUDA_INJECTION64_PATH"] = str(args.tool_path)
                    environment["C16_NVBIT_LD_PRELOAD_DECLARATION"] = str(args.tool_path)
                with args.stdout_path.open("w", encoding="utf-8") as stdout, args.stderr_path.open("w", encoding="utf-8") as stderr:
                    process = subprocess.Popen(_child_command(args), stdout=stdout, stderr=stderr, text=True, env=environment, start_new_session=True)
                    next_sample = started
                    ordinal = 0
                    while process.poll() is None:
                        now = _now()
                        if now >= next_sample:
                            stage = _read_json(args.stage_path)
                            markers = _tail_markers(args.stdout_path) if args.mode == "NVBIT" else []
                            sample = {
                                "schema_version": SCHEMA,
                                "sample_elapsed_seconds": now - started,
                                "stage": stage,
                                "nvbit_timing_markers": markers[-32:],
                                **gpu_snapshot(process.pid),
                            }
                            # Stack snapshots are deliberately only taken when
                            # the process is still live. They are /proc reads,
                            # not debugger attachment or process modification.
                            snapshot = stack_snapshot(process.pid, args.stack_dir, ordinal, now - started)
                            stack_paths.append(snapshot)
                            sample["stack_snapshot"] = {"path": str(snapshot), "sha256": sha256_file(snapshot)}
                            samples.append(sample)
                            with args.samples_path.open("a", encoding="utf-8") as handle:
                                handle.write(json.dumps(sample, sort_keys=True) + "\n")
                            ordinal += 1
                            next_sample += args.sample_seconds
                        if now - started >= args.wall_limit_seconds:
                            timed_out = True
                            _kill_process_group(process)
                            break
                        time.sleep(min(0.25, max(0.01, next_sample - _now())))
                    if process.poll() is None:
                        _kill_process_group(process)
            elapsed = _now() - started
            child_exit_code = process.returncode if process is not None else None
            final_stage = _read_json(args.stage_path)
            markers = _tail_markers(args.stdout_path) if args.mode == "NVBIT" else []
            first_submission = None
            first_completed = None
            if final_stage is not None:
                if final_stage.get("stage") == "FIRST_CUDA_KERNEL_SUBMISSION_BEGIN":
                    first_submission = final_stage.get("elapsed_seconds")
                if final_stage.get("stage") == "FIRST_CUDA_KERNEL_COMPLETED":
                    first_completed = final_stage.get("elapsed_seconds")
            # The stage file is last-write-only, so find timing from the stdout
            # child protocol as an intentionally conservative fallback.
            try:
                child_text = args.stdout_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                child_text = ""
            stage_lines = [line for line in child_text.splitlines() if line.startswith("C16_STAGE_DIAGNOSTIC ")]
            for line in stage_lines:
                try:
                    stage_payload = json.loads(line.split(" ", 1)[1])
                except (IndexError, json.JSONDecodeError):
                    continue
                if stage_payload.get("stage") == "FIRST_CUDA_KERNEL_SUBMISSION_BEGIN":
                    first_submission = stage_payload.get("elapsed_seconds")
                elif stage_payload.get("stage") == "FIRST_CUDA_KERNEL_COMPLETED":
                    first_completed = stage_payload.get("elapsed_seconds")
            if timed_out:
                status = "BOUNDED_TIMEOUT"
                terminal_status = "BOUNDED_TIMEOUT"
            elif child_exit_code == 0:
                status = "COMPLETE"
                terminal_status = "COMPLETE"
            else:
                status = "CHILD_FAILED_OR_ABORTED"
                terminal_status = "FAILED_OR_ABORTED"
            lease.finish(
                elapsed_seconds=elapsed,
                raw_bytes=0,
                terminal_status=terminal_status,
                evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC",
                diagnostic_reason="PYTORCH_FIRST_KERNEL_STAGE_ISOLATION_NO_TRACE_NO_SCIENTIFIC_CAPTURE",
            )
        receipt = {
            "schema_version": SCHEMA,
            "status": status,
            "terminal_status": terminal_status,
            "scientific_eligible": False,
            "diagnostic_only": True,
            "not_for_trace": True,
            "not_for_c_target": True,
            "not_for_native_timing": True,
            "run_id": args.run_id,
            "testcase": args.testcase,
            "mode": args.mode,
            "runtime_code_commit": args.runtime_code_commit,
            "wall_limit_seconds": args.wall_limit_seconds,
            "sample_seconds": args.sample_seconds,
            "first_cuda_submission_elapsed_seconds": first_submission,
            "first_cuda_completion_elapsed_seconds": first_completed,
            "child_exit_code": child_exit_code,
            "nvbit_tool": None if args.mode == "NATIVE" else {"path": str(args.tool_path), "sha256": args.tool_sha256},
            "nvdisasm_environment_contract": nvdisasm_contract,
            "nvbit_stage_markers": markers,
            "samples": {"path": str(args.samples_path), "sha256": sha256_file(args.samples_path), "count": len(samples)},
            "stack_snapshots": [{"path": str(path), "sha256": sha256_file(path)} for path in stack_paths],
            "stage_path": {"path": str(args.stage_path), "sha256": sha256_file(args.stage_path)} if args.stage_path.is_file() else None,
            "child_receipt": {"path": str(args.child_receipt), "sha256": sha256_file(args.child_receipt)} if args.child_receipt.is_file() else None,
            "stdout": {"path": str(args.stdout_path), "sha256": sha256_file(args.stdout_path)},
            "stderr": {"path": str(args.stderr_path), "sha256": sha256_file(args.stderr_path)},
            "elapsed_seconds": elapsed,
            "raw_trace_bytes": 0,
            "trace_generated": False,
        }
        atomic_json(args.receipt, receipt)
        return 0 if terminal_status == "COMPLETE" else 2
    except Exception as exc:
        if process is not None:
            _kill_process_group(process)
        atomic_json(args.receipt, {
            "schema_version": SCHEMA,
            "status": "HARNESS_FAIL_CLOSED",
            "scientific_eligible": False,
            "message": str(exc),
            "testcase": args.testcase,
            "mode": args.mode,
            "run_id": args.run_id,
        })
        raise


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--child", action="store_true")
    result.add_argument("--testcase", choices=TESTCASES, required=True)
    result.add_argument("--mode", choices=("NATIVE", "NVBIT"))
    result.add_argument("--receipt", type=Path)
    result.add_argument("--samples-path", type=Path)
    result.add_argument("--stage-path", type=Path, required=True)
    result.add_argument("--child-receipt", type=Path, required=True)
    result.add_argument("--stdout-path", type=Path)
    result.add_argument("--stderr-path", type=Path)
    result.add_argument("--stack-dir", type=Path)
    result.add_argument("--budget-ledger", type=Path)
    result.add_argument("--wall-limit-seconds", type=int, default=WALL_LIMIT_SECONDS)
    result.add_argument("--sample-seconds", type=int, default=SAMPLE_SECONDS)
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
    required = (args.mode, args.receipt, args.samples_path, args.stdout_path, args.stderr_path, args.stack_dir, args.budget_ledger, args.runtime_code_commit, args.run_id)
    if any(value is None for value in required):
        raise ContractError("parent stage diagnostic requires mode, paths, ledger, source commit, and run ID")
    raise SystemExit(parent_main(args))


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL Retry570 stage diagnostic: {exc}", file=sys.stderr)
        raise SystemExit(2)
