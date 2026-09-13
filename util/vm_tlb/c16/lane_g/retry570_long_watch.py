#!/usr/bin/env python3
"""One-shot, non-capture Retry570 NVBit/PyTorch long-watch diagnostic.

This program is intentionally narrower than the six-plus-six bounded NVBit
windows it follows.  Its child executes the unchanged finite index_select
microreproducer candidate set, while the parent owns one *non-capture* budget
lease and samples the child every five seconds.  The long-watch mode uses the
map-only tool; the distinct path-smoke mode permits only a compact official
instruction-count tool.  Neither produces a trace or scientific capture. The
PyTorch workload necessarily allocates its tiny tensors; that is the
first-CUDA-kernel boundary the experiment is designed to observe.

It is not a trace capture, C target, timing result, or static-map authority.
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
from nvbit_indexselect_microreproducer import (
    CANDIDATES,
    DIAGNOSTIC_DEPLOYMENT,
    assert_runtime_identity,
    git_head,
)


SCHEMA = "C16_G_RETRY570_NVBIT_LONG_WATCH_V1"
LONG_WATCH_SECONDS = 300
SAMPLE_SECONDS = 5
BASELINE_SECONDS = 60
PATH_SMOKE_SECONDS = 60
DIAGNOSTIC_DEPLOYMENT = "c16_retry570_indexselect_microreproducer_long_watch"
STAGE_CUDA_READY = "CUDA_AVAILABLE_CONFIRMED"
STAGE_FIRST_KERNEL_COMPLETED = "FIRST_CUDA_KERNEL_COMPLETED"


def _now() -> float:
    return time.monotonic()


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _tail_contains(path: Path, markers: tuple[str, ...]) -> list[str]:
    try:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            handle.seek(max(0, handle.tell() - 1_048_576))
            text = handle.read().decode("utf-8", errors="replace")
    except OSError:
        return []
    return [marker for marker in markers if marker in text]


def _command_text(command: list[str]) -> str:
    return " ".join(command)


def _run_text(command: list[str]) -> tuple[int, str]:
    try:
        completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    except OSError as exc:
        return 127, str(exc)
    return completed.returncode, completed.stdout.strip()


def gpu_snapshot(pid: int) -> dict[str, Any]:
    gpu_rc, gpu_text = _run_text([
        "nvidia-smi", "--query-gpu=utilization.gpu,memory.used", "--format=csv,noheader,nounits",
    ])
    apps_rc, apps_text = _run_text([
        "nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader,nounits",
    ])
    ps_rc, ps_text = _run_text(["ps", "-p", str(pid), "-o", "etimes=,pcpu=,stat=,wchan="])
    apps = [line.strip() for line in apps_text.splitlines() if line.strip()]
    return {
        "gpu_query_exit_code": gpu_rc,
        "gpu_utilization_and_memory": gpu_text,
        "gpu_process_query_exit_code": apps_rc,
        "gpu_processes": apps,
        "child_pid_present_in_gpu_processes": any(line.split(",", 1)[0].strip() == str(pid) for line in apps),
        "ps_query_exit_code": ps_rc,
        "process_state_wchan": ps_text,
    }


def nvdisasm_environment_contract(nvdisasm: Path, inherited_path: str) -> dict[str, str]:
    """Close NVBit's documented ``nvdisasm in PATH`` requirement per child.

    NVBit 1.8 resolves the configured ``NVDISASM`` command through PATH.  An
    absolute value in ``NVDISASM`` alone is therefore not a durable contract.
    Keep the verified absolute path as provenance while passing its basename
    only after prefixing the exact parent directory to the child PATH.
    """
    if not nvdisasm.is_absolute() or not nvdisasm.is_file() or not os.access(nvdisasm, os.X_OK):
        raise ContractError("NVBit harness requires an executable absolute --nvdisasm path")
    tool_directory = str(nvdisasm.parent)
    components = [item for item in inherited_path.split(os.pathsep) if item and item != tool_directory]
    return {
        "NVDISASM": nvdisasm.name,
        "PATH": os.pathsep.join([tool_directory, *components]),
        "C16_NVBIT_NVDISASM_ABSOLUTE_PATH": str(nvdisasm),
        "C16_NVBIT_NVDISASM_PATH_PREFIX": tool_directory,
    }


def validate_mode(mode: str, wall_limit_seconds: int, sample_seconds: int, authorization_receipt: Path | None) -> None:
    if sample_seconds != SAMPLE_SECONDS:
        raise ContractError(f"long-watch sampling must be exactly {SAMPLE_SECONDS} seconds")
    if mode == "NVBIT_LONG_WATCH":
        if wall_limit_seconds != LONG_WATCH_SECONDS:
            raise ContractError(f"NVBit long-watch wall limit must be exactly {LONG_WATCH_SECONDS} seconds")
        if authorization_receipt is None:
            raise ContractError("NVBit long-watch requires a durable one-shot authorization receipt")
    elif mode == "BASELINE":
        if wall_limit_seconds != BASELINE_SECONDS:
            raise ContractError(f"baseline wall limit must be exactly {BASELINE_SECONDS} seconds")
        if authorization_receipt is not None:
            raise ContractError("baseline must not create or consume the NVBit one-shot authorization")
    elif mode == "NVBIT_PATH_SMOKE":
        if wall_limit_seconds != PATH_SMOKE_SECONDS:
            raise ContractError(f"NVBit path smoke wall limit must be exactly {PATH_SMOKE_SECONDS} seconds")
        if authorization_receipt is not None:
            raise ContractError("NVBit path smoke must not create or consume the long-watch authorization")
    else:
        raise ContractError("long-watch mode must be BASELINE, NVBIT_LONG_WATCH, or NVBIT_PATH_SMOKE")


def classify_timeout(samples: list[dict[str, Any]], stages: list[dict[str, Any]]) -> str:
    """Use observed progress, not an absence of profiler raw, to name a timeout."""
    stage_values = [str(item.get("stage", "")) for item in stages]
    distinct_stages = len(set(stage_values))
    busy_samples = 0
    for sample in samples:
        state = str(sample.get("process_state_wchan", ""))
        fields = state.split()
        try:
            cpu = float(fields[1]) if len(fields) >= 2 else 0.0
        except ValueError:
            cpu = 0.0
        if cpu >= 25.0:
            busy_samples += 1
    # Either repeatedly advancing child stages or sustained host-side work is
    # evidence of progress.  This deliberately does not claim a CUDA kernel.
    if distinct_stages >= 4 or (len(samples) >= 4 and busy_samples * 2 >= len(samples)):
        return "NVBIT_PYTORCH_EXTREME_STARTUP_OVERHEAD"
    return "NVBIT_PYTORCH_PRE_FIRST_KERNEL_STALL_CONFIRMED"


def reserve_long_watch(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as exc:
        raise ContractError(f"NVBit long-watch was already reserved or completed: {path}") from exc
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def _stage(path: Path, started: float, name: str, **extra: Any) -> None:
    payload = {"schema_version": SCHEMA, "stage": name, "elapsed_seconds": _now() - started, **extra}
    atomic_json(path, payload)
    print("C16_LONG_WATCH_STAGE " + json.dumps(payload, sort_keys=True), flush=True)


def child_main(args: argparse.Namespace) -> int:
    started = _now()
    first_kernel_elapsed: float | None = None
    try:
        _stage(args.stage_path, started, "PROCESS_START")
        _stage(args.stage_path, started, "TORCH_IMPORT_BEGIN")
        torch, identity = assert_runtime_identity(args)
        _stage(args.stage_path, started, "TORCH_IMPORTED_AND_RUNTIME_IDENTITY_CLOSED", runtime_identity=identity)
        _stage(args.stage_path, started, "CUDA_AVAILABLE_CHECK_BEGIN")
        # assert_runtime_identity has already rejected a CPU fallback.  Keep a
        # distinct marker so the parent can separate import/identity from the
        # first actual CUDA workload submission.
        if not torch.cuda.is_available():
            raise ContractError("CUDA disappeared after runtime identity verification")
        _stage(args.stage_path, started, STAGE_CUDA_READY)
        torch.manual_seed(570)
        completed: list[dict[str, Any]] = []
        for position, candidate in enumerate(CANDIDATES):
            shape = tuple(int(value) for value in candidate["shape"])
            dim = int(candidate["dim"])
            index_count = min(4096, shape[dim])
            _stage(
                args.stage_path, started, "FIRST_CUDA_KERNEL_SUBMISSION_BEGIN" if position == 0 else "NEXT_CANDIDATE_BEGIN",
                candidate_id=candidate["candidate_id"], shape=list(shape), dim=dim, index_count=index_count,
            )
            # This is the same finite workload and candidate ordering as the
            # existing microreproducer.  The injected map-only tool itself
            # contains no instrumentation or CUDA allocation.
            indices = (torch.arange(index_count, device="cuda:0", dtype=torch.int64) * 17) % shape[dim]
            source = torch.randn(shape, device="cuda:0", dtype=torch.float16)
            output = torch.index_select(source, dim, indices)
            torch.cuda.synchronize()
            if position == 0:
                first_kernel_elapsed = _now() - started
                _stage(args.stage_path, started, STAGE_FIRST_KERNEL_COMPLETED)
            expected_shape = list(shape)
            expected_shape[dim] = index_count
            if output.device.type != "cuda" or list(output.shape) != expected_shape:
                raise ContractError("index_select produced an invalid long-watch output")
            completed.append({**candidate, "index_count": index_count, "output_shape": list(output.shape)})
            del output, source, indices
        torch.cuda.synchronize()
        final = {
            "schema_version": SCHEMA,
            "status": "CHILD_COMPLETE",
            "runtime_identity": identity,
            "candidate_search": {"same_as_microreproducer": True, "candidates": completed},
            "elapsed_seconds": _now() - started,
            "first_cuda_kernel_completed_elapsed_seconds": first_kernel_elapsed,
            "terminal_status": "COMPLETE",
        }
        atomic_json(args.child_receipt, final)
        _stage(args.stage_path, started, "CHILD_COMPLETE")
        return 0
    except Exception as exc:
        failure = {
            "schema_version": SCHEMA,
            "status": "CHILD_FAILED",
            "scientific_eligible": False,
            "message": str(exc),
            "elapsed_seconds": _now() - started,
            "terminal_status": "FAILED_OR_ABORTED",
        }
        atomic_json(args.child_receipt, failure)
        _stage(args.stage_path, started, "CHILD_FAILED", message=str(exc))
        print(f"FAIL Retry570 long-watch child: {exc}", file=sys.stderr, flush=True)
        return 2


def _child_command(args: argparse.Namespace) -> list[str]:
    command = [
        sys.executable, str(Path(__file__).resolve()), "--child",
        "--stage-path", str(args.stage_path),
        "--child-receipt", str(args.child_receipt),
        "--expected-torch-version", args.expected_torch_version,
        "--expected-torch-cuda", args.expected_torch_cuda,
        "--expected-libtorch-cuda-sha256", args.expected_libtorch_cuda_sha256,
        "--expected-gpu-name", args.expected_gpu_name,
        "--expected-driver", args.expected_driver,
    ]
    if args.expected_gpu_uuid:
        command.extend(["--expected-gpu-uuid", args.expected_gpu_uuid])
    return command


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


def parent_main(args: argparse.Namespace) -> int:
    validate_mode(args.mode, args.wall_limit_seconds, args.sample_seconds, args.authorization_receipt)
    if args.runtime_code_commit != git_head():
        raise ContractError("declared runtime code commit differs from this source checkout")
    if not valid_sha256(args.expected_libtorch_cuda_sha256):
        raise ContractError("expected libtorch CUDA SHA must be lowercase SHA256")
    if args.mode in {"NVBIT_LONG_WATCH", "NVBIT_PATH_SMOKE"}:
        if args.tool_path is None or args.tool_sha256 is None or not args.tool_path.is_file():
            raise ContractError("NVBit operation requires a materialized hash-closed tool")
        if not valid_sha256(args.tool_sha256) or sha256_file(args.tool_path) != args.tool_sha256:
            raise ContractError("NVBit operation tool path/SHA is not closed")
        if not args.nvdisasm:
            raise ContractError("NVBit operation lacks an nvdisasm contract input")
        if args.mode == "NVBIT_LONG_WATCH" and (not args.exact_mangled_function or args.static_map_path is None):
            raise ContractError("NVBit long-watch lacks exact mapper identity/configuration")
        if args.mode == "NVBIT_PATH_SMOKE" and not args.tool_evidence_marker:
            raise ContractError("NVBit path smoke requires an exact official-tool evidence marker")
        if args.mode == "NVBIT_PATH_SMOKE" and args.smoke_tool_kind != "NVBIT_1_8_OFFICIAL_INSTR_COUNT_BB":
            raise ContractError("NVBit path smoke permits only NVBit 1.8 official instr_count_bb")
    elif args.tool_path is not None or args.tool_sha256 is not None:
        raise ContractError("baseline must execute without an NVBit tool declaration")
    for path in (args.receipt, args.samples_path, args.stage_path, args.child_receipt, args.stdout_path, args.stderr_path):
        if path.exists():
            raise ContractError(f"long-watch refuses to overwrite existing diagnostic payload: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id:
            raise ValueError
    except ValueError as exc:
        raise ContractError("long-watch run ID must be a canonical UUID") from exc

    identity = {
        "deployment_id": DIAGNOSTIC_DEPLOYMENT,
        "run_id": args.run_id,
        "scenario_id": "INDEXSELECT_EXACT_FUNCTION_NVBIT_PATH_SMOKE" if args.mode == "NVBIT_PATH_SMOKE" else "INDEXSELECT_EXACT_FUNCTION_LONG_WATCH",
        "implementation_key": "TORCH_INDEX_SELECT_MICROREPRODUCER_OFFICIAL_INSTRUMENTATION_SMOKE" if args.mode == "NVBIT_PATH_SMOKE" else "TORCH_INDEX_SELECT_MICROREPRODUCER_MAP_ONLY",
    }
    MeasurementActive.assert_available(args.budget_ledger)
    authorization: dict[str, Any] | None = None
    if args.mode == "NVBIT_LONG_WATCH":
        assert args.authorization_receipt is not None
        authorization = {
            "schema_version": SCHEMA,
            "status": "RESERVED_NOT_STARTED",
            "mode": args.mode,
            "run_id": args.run_id,
            "runtime_code_commit": args.runtime_code_commit,
            "wall_limit_seconds": LONG_WATCH_SECONDS,
            "sample_seconds": SAMPLE_SECONDS,
            "scientific_eligible": False,
            "created_unix": time.time(),
        }
        reserve_long_watch(args.authorization_receipt, authorization)

    started = _now()
    samples: list[dict[str, Any]] = []
    stages: list[dict[str, Any]] = []
    process: subprocess.Popen[str] | None = None
    timed_out = False
    first_kernel_elapsed: float | None = None
    try:
        operation_kind = "NVBIT_PATH_SMOKE_DIAGNOSTIC" if args.mode == "NVBIT_PATH_SMOKE" else "NVBIT_LONG_WATCH_DIAGNOSTIC"
        with BudgetLease(args.budget_ledger, identity, operation_kind, capture=False) as lease:
            with MeasurementActive(args.budget_ledger, identity, operation_kind):
                environment = os.environ.copy()
                environment.pop("LD_PRELOAD", None)
                environment.pop("CUDA_INJECTION64_PATH", None)
                for name in tuple(environment):
                    if name.startswith("C16_NVBIT_"):
                        environment.pop(name)
                nvdisasm_contract: dict[str, str] | None = None
                if args.mode in {"NVBIT_LONG_WATCH", "NVBIT_PATH_SMOKE"}:
                    assert args.tool_path is not None and args.tool_sha256 is not None
                    assert args.nvdisasm is not None
                    nvdisasm_contract = nvdisasm_environment_contract(Path(args.nvdisasm), environment.get("PATH", ""))
                    environment.update({
                        "CUDA_INJECTION64_PATH": str(args.tool_path),
                        "C16_NVBIT_LD_PRELOAD_DECLARATION": str(args.tool_path),
                    })
                    environment.update(nvdisasm_contract)
                    if args.mode == "NVBIT_LONG_WATCH":
                        assert args.static_map_path is not None
                        environment.update({
                            "C16_NVBIT_TARGET_FUNCTION_MANGLED": args.exact_mangled_function,
                            "C16_NVBIT_STATIC_MAP_PATH": str(args.static_map_path),
                            "C16_NVBIT_CODE_OBJECT_SHA256": args.expected_libtorch_cuda_sha256,
                        })
                with args.stdout_path.open("w", encoding="utf-8") as stdout, args.stderr_path.open("w", encoding="utf-8") as stderr:
                    process = subprocess.Popen(
                        _child_command(args), stdout=stdout, stderr=stderr, text=True, env=environment, start_new_session=True,
                    )
                    next_sample = started
                    while process.poll() is None:
                        now = _now()
                        if now >= next_sample:
                            stage = _read_json(args.stage_path)
                            if stage is not None and (not stages or stage != stages[-1]):
                                stages.append(stage)
                                if stage.get("stage") == STAGE_FIRST_KERNEL_COMPLETED and first_kernel_elapsed is None:
                                    first_kernel_elapsed = float(stage.get("elapsed_seconds", now - started))
                            sample = {
                                "schema_version": SCHEMA,
                                "sample_elapsed_seconds": now - started,
                                "stage": stage,
                                "cuda_initialization_complete": stage is not None and str(stage.get("stage")) in {
                                    STAGE_CUDA_READY, "FIRST_CUDA_KERNEL_SUBMISSION_BEGIN", STAGE_FIRST_KERNEL_COMPLETED, "CHILD_COMPLETE",
                                },
                                "first_cuda_kernel_completed": first_kernel_elapsed is not None,
                                "callback_or_map_markers": _tail_contains(args.stdout_path, tuple(marker for marker in (
                                    "C16_EXACT_MAP_ONLY_TOOL_READY", "C16_EXACT_MAP_ONLY_COMPLETE", "C16_EXACT_MAP_ONLY_TERMINAL", args.tool_evidence_marker,
                                ) if marker)),
                                **gpu_snapshot(process.pid),
                            }
                            samples.append(sample)
                            with args.samples_path.open("a", encoding="utf-8") as handle:
                                handle.write(json.dumps(sample, sort_keys=True) + "\n")
                            next_sample += args.sample_seconds
                        if now - started >= args.wall_limit_seconds:
                            timed_out = True
                            _kill_process_group(process)
                            break
                        time.sleep(min(0.25, max(0.01, next_sample - _now())))
                    if process.poll() is None:
                        _kill_process_group(process)
                    final_stage = _read_json(args.stage_path)
                    if final_stage is not None and (not stages or final_stage != stages[-1]):
                        stages.append(final_stage)
                        if final_stage.get("stage") == STAGE_FIRST_KERNEL_COMPLETED and first_kernel_elapsed is None:
                            first_kernel_elapsed = float(final_stage.get("elapsed_seconds", _now() - started))
            child_payload = _read_json(args.child_receipt)
            if first_kernel_elapsed is None and child_payload is not None:
                child_first_kernel = child_payload.get("first_cuda_kernel_completed_elapsed_seconds")
                if isinstance(child_first_kernel, (int, float)) and child_first_kernel >= 0:
                    first_kernel_elapsed = float(child_first_kernel)
            elapsed = _now() - started
            child_exit_code = process.returncode if process is not None else None
            tool_evidence_seen = bool(args.tool_evidence_marker and _tail_contains(args.stdout_path, (args.tool_evidence_marker,)))
            if timed_out and first_kernel_elapsed is None:
                status = classify_timeout(samples, stages)
                terminal_status = "BOUNDED_TIMEOUT_NO_FIRST_KERNEL"
            elif timed_out:
                status = "NVBIT_LONG_WATCH_FIRST_KERNEL_OBSERVED_BUT_CHILD_DID_NOT_COMPLETE"
                terminal_status = "BOUNDED_TIMEOUT_AFTER_FIRST_KERNEL"
            elif child_exit_code == 0 and first_kernel_elapsed is not None:
                if args.mode == "BASELINE":
                    status = "BASELINE_FIRST_CUDA_KERNEL_OBSERVED"
                    terminal_status = "COMPLETE"
                elif args.mode == "NVBIT_PATH_SMOKE" and tool_evidence_seen:
                    status = "NVBIT_PATH_SMOKE_FIRST_KERNEL_AND_TOOL_EVIDENCE_OBSERVED"
                    terminal_status = "COMPLETE"
                elif args.mode == "NVBIT_PATH_SMOKE":
                    status = "NVBIT_PATH_SMOKE_TOOL_EVIDENCE_NOT_OBSERVED"
                    terminal_status = "FAILED_OR_ABORTED"
                else:
                    status = "NVBIT_LONG_WATCH_FIRST_CUDA_KERNEL_OBSERVED"
                    terminal_status = "COMPLETE"
            else:
                status = (
                    "BASELINE_CHILD_FAILED_BEFORE_FIRST_KERNEL" if args.mode == "BASELINE" else
                    ("NVBIT_PATH_SMOKE_CHILD_FAILED_BEFORE_FIRST_KERNEL" if args.mode == "NVBIT_PATH_SMOKE" else "NVBIT_LONG_WATCH_CHILD_FAILED_BEFORE_FIRST_KERNEL")
                )
                terminal_status = "FAILED_OR_ABORTED"
            lease.finish(
                elapsed_seconds=elapsed,
                raw_bytes=0,
                terminal_status=terminal_status,
                evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC",
                diagnostic_reason=("NVBIT_PATH_PROPAGATION_SMOKE_NO_TRACE_CAPTURE" if args.mode == "NVBIT_PATH_SMOKE" else "ONE_SHOT_300_SECOND_WATCHDOG_DISCRIMINATOR_NO_TRACE_CAPTURE"),
            )
        receipt = {
            "schema_version": SCHEMA,
            "status": status,
            "scientific_eligible": False,
            "diagnostic_only": True,
            "not_for_trace": True,
            "not_for_c_target": True,
            "mode": args.mode,
            "run_id": args.run_id,
            "runtime_code_commit": args.runtime_code_commit,
            "wall_limit_seconds": args.wall_limit_seconds,
            "sample_seconds": args.sample_seconds,
            "same_microreproducer_candidates": list(CANDIDATES),
            "nvbit_tool": None if args.mode == "BASELINE" else {"path": str(args.tool_path), "sha256": args.tool_sha256},
            "nvdisasm_environment_contract": nvdisasm_contract,
            "required_tool_evidence_marker": args.tool_evidence_marker,
            "tool_evidence_marker_observed": tool_evidence_seen if args.mode == "NVBIT_PATH_SMOKE" else None,
            "tool_contract": (
                {"type": "MAP_ONLY_NO_INSTRUMENTATION", "tool_cuda_allocation": False, "tool_context_or_lifecycle_logic": False}
                if args.mode == "NVBIT_LONG_WATCH" else
                ({"type": args.smoke_tool_kind, "trace_generated": False} if args.mode == "NVBIT_PATH_SMOKE" else None)
            ),
            "first_cuda_kernel_completed_elapsed_seconds": first_kernel_elapsed,
            "child_exit_code": child_exit_code,
            "terminal_status": terminal_status,
            "elapsed_seconds": elapsed,
            "samples": {"path": str(args.samples_path), "sha256": sha256_file(args.samples_path), "count": len(samples)},
            "stages": stages,
            "child_receipt": {"path": str(args.child_receipt), "sha256": sha256_file(args.child_receipt)} if args.child_receipt.is_file() else None,
            "stdout": {"path": str(args.stdout_path), "sha256": sha256_file(args.stdout_path)},
            "stderr": {"path": str(args.stderr_path), "sha256": sha256_file(args.stderr_path)},
            "trace_generated": False,
            "raw_trace_bytes": 0,
        }
        atomic_json(args.receipt, receipt)
        if authorization is not None:
            assert args.authorization_receipt is not None
            authorization.update({
                "status": "COMPLETE",
                "completed_unix": time.time(),
                "receipt_path": str(args.receipt),
                "receipt_sha256": sha256_file(args.receipt),
                "terminal_status": terminal_status,
            })
            atomic_json(args.authorization_receipt, authorization)
        return 0 if terminal_status == "COMPLETE" else 2
    except Exception as exc:
        if process is not None:
            _kill_process_group(process)
        failure = {
            "schema_version": SCHEMA,
            "status": "LONG_WATCH_HARNESS_FAIL_CLOSED",
            "scientific_eligible": False,
            "message": str(exc),
            "mode": args.mode,
            "run_id": args.run_id,
        }
        atomic_json(args.receipt, failure)
        if authorization is not None:
            assert args.authorization_receipt is not None
            authorization.update({
                "status": "FAILED_BEFORE_OR_DURING_RUN",
                "completed_unix": time.time(),
                "receipt_path": str(args.receipt),
                "receipt_sha256": sha256_file(args.receipt),
                "message": str(exc),
            })
            atomic_json(args.authorization_receipt, authorization)
        raise


def parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(description=__doc__)
    argument_parser.add_argument("--child", action="store_true")
    argument_parser.add_argument("--mode", choices=("BASELINE", "NVBIT_LONG_WATCH", "NVBIT_PATH_SMOKE"))
    argument_parser.add_argument("--receipt", type=Path)
    argument_parser.add_argument("--samples-path", type=Path)
    argument_parser.add_argument("--stage-path", type=Path, required=True)
    argument_parser.add_argument("--child-receipt", type=Path, required=True)
    argument_parser.add_argument("--stdout-path", type=Path)
    argument_parser.add_argument("--stderr-path", type=Path)
    argument_parser.add_argument("--authorization-receipt", type=Path)
    argument_parser.add_argument("--budget-ledger", type=Path)
    argument_parser.add_argument("--wall-limit-seconds", type=int)
    argument_parser.add_argument("--sample-seconds", type=int, default=SAMPLE_SECONDS)
    argument_parser.add_argument("--tool-path", type=Path)
    argument_parser.add_argument("--tool-sha256")
    argument_parser.add_argument("--exact-mangled-function")
    argument_parser.add_argument("--static-map-path", type=Path)
    argument_parser.add_argument("--nvdisasm")
    argument_parser.add_argument("--tool-evidence-marker")
    argument_parser.add_argument("--smoke-tool-kind")
    argument_parser.add_argument("--expected-torch-version", required=True)
    argument_parser.add_argument("--expected-torch-cuda", required=True)
    argument_parser.add_argument("--expected-libtorch-cuda-sha256", required=True)
    argument_parser.add_argument("--expected-gpu-name", default="NVIDIA GeForce RTX 3090")
    argument_parser.add_argument("--expected-driver", default="570.124.04")
    argument_parser.add_argument("--expected-gpu-uuid")
    argument_parser.add_argument("--runtime-code-commit")
    argument_parser.add_argument("--run-id")
    return argument_parser


def main() -> None:
    args = parser().parse_args()
    if args.child:
        raise SystemExit(child_main(args))
    required = (args.mode, args.receipt, args.samples_path, args.stdout_path, args.stderr_path, args.budget_ledger, args.wall_limit_seconds, args.runtime_code_commit, args.run_id)
    if any(value is None for value in required):
        raise ContractError("parent long-watch requires mode, paths, ledger, wall limit, source commit, and run ID")
    raise SystemExit(parent_main(args))


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL Retry570 long-watch: {exc}", file=sys.stderr)
        raise SystemExit(2)
