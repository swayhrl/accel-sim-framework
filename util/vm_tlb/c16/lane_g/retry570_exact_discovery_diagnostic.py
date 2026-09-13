#!/usr/bin/env python3
"""One bounded, non-capture discovery-only replay of Retry570's exact target.

The child reproduces only historic candidate R2_D0_I64_A (shape 64x32,
dimension 0, int64, 64 indices) twice in the same process.  The first target
launch permits NVBit discovery only; the second is a cache/reuse observation.
No instruction is inserted, enabled, traced, or interpreted as performance.
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
from retry570_pytorch_stage_diagnostic import stack_snapshot


SCHEMA = "C16_G_RETRY570_EXACT_DISCOVERY_DIAGNOSTIC_V1"
WALL_LIMIT_SECONDS = 60
SAMPLE_SECONDS = 5
EXACT_TARGET_MANGLED = (
    "_ZN2at6native44_GLOBAL__N__50c743a2_11_Indexing_cu_89862edb21"
    "indexSelectLargeIndexIN3c104HalfEljLi2ELi2ELin2ELb1EEEvNS_4cuda6detail10"
    "TensorInfoIT_T1_EENS7_IKS8_S9_EENS7_IKT0_S9_EEiiS9_S9_l"
)
EXACT_CANDIDATE = {"candidate_id": "R2_D0_I64_A", "shape": (64, 32), "dim": 0, "index_dtype": "int64", "index_count": 64}


def _now() -> float:
    return time.monotonic()


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _stage(path: Path, started: float, name: str, **extra: Any) -> None:
    payload = {"schema_version": SCHEMA, "stage": name, "elapsed_seconds": _now() - started, **extra}
    atomic_json(path, payload)
    print("C16_EXACT_DISCOVERY_CHILD_STAGE " + json.dumps(payload, sort_keys=True), flush=True)


def _tail_discovery(path: Path) -> list[str]:
    try:
        with path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            handle.seek(max(0, handle.tell() - 2 * 1024 * 1024))
            lines = handle.read().decode("utf-8", errors="replace").splitlines()
    except OSError:
        return []
    return [line for line in lines if line.startswith("C16_EXACT_DISCOVERY")][-128:]


def _process_tree(pid: int) -> list[dict[str, str]]:
    code, output = _run_text(["ps", "-eo", "pid=,ppid=,pcpu=,stat=,wchan=,comm=,args="])
    if code != 0:
        return [{"error": output}]
    rows: dict[int, dict[str, str]] = {}
    for line in output.splitlines():
        fields = line.split(None, 6)
        if len(fields) < 6:
            continue
        try:
            current, parent = int(fields[0]), int(fields[1])
        except ValueError:
            continue
        rows[current] = {"pid": fields[0], "ppid": fields[1], "cpu_percent": fields[2], "state": fields[3], "wchan": fields[4], "command": " ".join(fields[5:])}
    descendants = {pid}
    changed = True
    while changed:
        changed = False
        for current, row in rows.items():
            if int(row["ppid"]) in descendants and current not in descendants:
                descendants.add(current)
                changed = True
    return [rows[current] for current in sorted(descendants) if current in rows]


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


def _one_exact_operation(torch: Any, stage_path: Path, started: float, ordinal: int) -> str:
    """Preserve the historic small R2_D0_I64_A construction and operation."""
    _stage(stage_path, started, "EXACT_OPERATION_BEGIN", operation_ordinal=ordinal, candidate=EXACT_CANDIDATE)
    torch.manual_seed(570)
    shape = EXACT_CANDIDATE["shape"]
    indices = (torch.arange(EXACT_CANDIDATE["index_count"], device="cuda:0", dtype=torch.int64) * 17) % shape[0]
    source = torch.randn(shape, device="cuda:0", dtype=torch.float16)
    _stage(stage_path, started, "EXACT_TARGET_SUBMISSION_BEGIN", operation_ordinal=ordinal, candidate=EXACT_CANDIDATE)
    output = torch.index_select(source, int(EXACT_CANDIDATE["dim"]), indices)
    torch.cuda.synchronize()
    if output.device.type != "cuda" or list(output.shape) != [64, 32]:
        raise ContractError("exact index_select candidate produced an unexpected output")
    checksum = int(output.float().sum().item() * 1_000_000)
    _stage(stage_path, started, "EXACT_TARGET_COMPLETED", operation_ordinal=ordinal, output_checksum_scaled=checksum)
    del output, source, indices
    return str(checksum)


def child_main(args: argparse.Namespace) -> int:
    started = _now()
    try:
        _stage(args.stage_path, started, "PROCESS_START", exact_target_mangled=EXACT_TARGET_MANGLED)
        _stage(args.stage_path, started, "TORCH_IMPORT_BEGIN")
        torch, identity = assert_runtime_identity(args)
        _stage(args.stage_path, started, "RUNTIME_IDENTITY_CLOSED", runtime_identity=identity)
        if not torch.cuda.is_available():
            raise ContractError("CUDA is unavailable; CPU fallback is forbidden")
        _stage(args.stage_path, started, "CUDA_INIT_BEGIN")
        torch.cuda.init()
        _stage(args.stage_path, started, "CUDA_INIT_COMPLETE")
        first_checksum = _one_exact_operation(torch, args.stage_path, started, 0)
        second_checksum = _one_exact_operation(torch, args.stage_path, started, 1)
        if first_checksum != second_checksum:
            raise ContractError("same-process exact target reuse inputs did not preserve output checksum")
        receipt = {"schema_version": SCHEMA, "status": "CHILD_COMPLETE", "scientific_eligible": False, "runtime_identity": identity, "exact_target_mangled": EXACT_TARGET_MANGLED, "candidate": EXACT_CANDIDATE, "operation_count": 2, "same_process_output_checksum_scaled": first_checksum, "elapsed_seconds": _now() - started, "terminal_status": "COMPLETE"}
        atomic_json(args.child_receipt, receipt)
        _stage(args.stage_path, started, "CHILD_COMPLETE")
        return 0
    except Exception as exc:
        atomic_json(args.child_receipt, {"schema_version": SCHEMA, "status": "CHILD_FAILED", "scientific_eligible": False, "message": str(exc), "elapsed_seconds": _now() - started, "terminal_status": "FAILED_OR_ABORTED"})
        _stage(args.stage_path, started, "CHILD_FAILED", message=str(exc))
        print(f"FAIL Retry570 exact discovery child: {exc}", file=sys.stderr, flush=True)
        return 2


def _child_command(args: argparse.Namespace) -> list[str]:
    command = [sys.executable, str(Path(__file__).resolve()), "--child", "--stage-path", str(args.stage_path), "--child-receipt", str(args.child_receipt), "--expected-torch-version", args.expected_torch_version, "--expected-torch-cuda", args.expected_torch_cuda, "--expected-libtorch-cuda-sha256", args.expected_libtorch_cuda_sha256, "--expected-gpu-name", args.expected_gpu_name, "--expected-driver", args.expected_driver]
    if args.expected_gpu_uuid:
        command.extend(("--expected-gpu-uuid", args.expected_gpu_uuid))
    return command


def _validate(args: argparse.Namespace) -> None:
    if args.runtime_code_commit != git_head():
        raise ContractError("declared runtime code commit differs from this checkout")
    if args.wall_limit_seconds != WALL_LIMIT_SECONDS or args.sample_seconds != SAMPLE_SECONDS:
        raise ContractError("exact discovery has a fixed 60-second wall cap and 5-second samples")
    if args.tool_path is None or not args.tool_path.is_file() or not args.tool_sha256 or not valid_sha256(args.tool_sha256) or sha256_file(args.tool_path) != args.tool_sha256:
        raise ContractError("exact discovery requires a materialized, hash-closed tool")
    if not valid_sha256(args.expected_libtorch_cuda_sha256) or not args.nvdisasm:
        raise ContractError("exact discovery lacks libtorch or nvdisasm closure")
    for path in (args.receipt, args.samples_path, args.stage_path, args.child_receipt, args.stdout_path, args.stderr_path, args.stack_dir):
        if path.exists():
            raise ContractError(f"exact discovery refuses to overwrite payload: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if str(uuid.UUID(args.run_id)) != args.run_id:
            raise ValueError
    except ValueError as exc:
        raise ContractError("exact discovery run ID must be a canonical UUID") from exc


def parent_main(args: argparse.Namespace) -> int:
    _validate(args)
    identity = {"deployment_id": "c16_retry570_exact_indexselect_discovery", "scenario_id": "R2_D0_I64_A_EXACT_TARGET_TWO_IDENTICAL_LAUNCHES", "run_id": args.run_id, "implementation_key": "NVBIT_EXACT_TARGET_DISCOVERY_ONLY_NO_INSERTION_NO_ENABLE"}
    MeasurementActive.assert_available(args.budget_ledger)
    started, samples, snapshots = _now(), [], []
    process: subprocess.Popen[str] | None = None
    timed_out = False
    contract: dict[str, str] | None = None
    try:
        with BudgetLease(args.budget_ledger, identity, "NVBIT_EXACT_DISCOVERY_ONLY_DIAGNOSTIC", capture=False) as lease:
            with MeasurementActive(args.budget_ledger, identity, "NVBIT_EXACT_DISCOVERY_ONLY_DIAGNOSTIC"):
                environment = os.environ.copy()
                environment.pop("LD_PRELOAD", None)
                environment.pop("CUDA_INJECTION64_PATH", None)
                for name in tuple(environment):
                    if name.startswith("C16_NVBIT_"):
                        environment.pop(name)
                contract = nvdisasm_environment_contract(Path(args.nvdisasm), environment.get("PATH", ""))
                environment.update(contract)
                environment.update({"CUDA_INJECTION64_PATH": str(args.tool_path), "C16_NVBIT_LD_PRELOAD_DECLARATION": str(args.tool_path), "C16_NVBIT_TARGET_FUNCTION_MANGLED": EXACT_TARGET_MANGLED})
                with args.stdout_path.open("w", encoding="utf-8") as stdout, args.stderr_path.open("w", encoding="utf-8") as stderr:
                    process = subprocess.Popen(_child_command(args), stdout=stdout, stderr=stderr, text=True, env=environment, start_new_session=True)
                    ordinal, next_sample = 0, started
                    while process.poll() is None:
                        now = _now()
                        if now >= next_sample:
                            markers = _tail_discovery(args.stdout_path)
                            tree = _process_tree(process.pid)
                            sample = {"schema_version": SCHEMA, "sample_elapsed_seconds": now - started, "stage": _read_json(args.stage_path), "last_discovery_markers": markers[-32:], "process_tree": tree, **gpu_snapshot(process.pid)}
                            # The root plus any live nvdisasm subprocess is
                            # captured non-destructively. This is evidence for
                            # a FUNCTION_BEGIN-without-END branch, not a
                            # debugger attach and not a process modification.
                            snap_root = stack_snapshot(process.pid, args.stack_dir / f"root_{process.pid}", ordinal, now - started)
                            snapshot_rows = [{"pid": process.pid, "path": str(snap_root), "sha256": sha256_file(snap_root)}]
                            for row in tree:
                                try:
                                    child_pid = int(row.get("pid", "-1"))
                                except ValueError:
                                    continue
                                if child_pid == process.pid:
                                    continue
                                snap_child = stack_snapshot(child_pid, args.stack_dir / f"child_{child_pid}", ordinal, now - started)
                                snapshot_rows.append({"pid": child_pid, "path": str(snap_child), "sha256": sha256_file(snap_child)})
                            sample["stack_snapshots"] = snapshot_rows
                            snapshots.extend(snapshot_rows)
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
            child_exit = process.returncode if process is not None else None
            markers = _tail_discovery(args.stdout_path)
            summary = next((line for line in reversed(markers) if line.startswith("C16_EXACT_DISCOVERY_SUMMARY")), None)
            reuse = any("stage=TARGET_REUSE_CALLBACK" in line for line in markers)
            if timed_out:
                status, terminal = "BOUNDED_TIMEOUT_DISCOVERY_LAST_MARKER_RETAINED", "BOUNDED_TIMEOUT"
            elif child_exit == 0 and summary is not None and reuse:
                status, terminal = "EXACT_TARGET_DISCOVERY_COMPLETE_WITH_SAME_PROCESS_REUSE", "COMPLETE"
            else:
                status, terminal = "EXACT_TARGET_DISCOVERY_INCOMPLETE_OR_TARGET_NOT_OBSERVED", "FAILED_OR_ABORTED"
            lease.finish(elapsed_seconds=elapsed, raw_bytes=0, terminal_status=terminal, evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC", diagnostic_reason="EXACT_INDEXSELECT_RELATED_FUNCTION_DISCOVERY_ONLY_NO_INSERTION_ENABLE_TRACE_OR_SCIENTIFIC_CAPTURE")
        receipt = {"schema_version": SCHEMA, "status": status, "terminal_status": terminal, "scientific_eligible": False, "diagnostic_only": True, "not_for_trace": True, "not_for_scientific_capture": True, "not_for_c_target": True, "not_for_native_timing": True, "runtime_code_commit": args.runtime_code_commit, "run_id": args.run_id, "wall_limit_seconds": args.wall_limit_seconds, "sample_seconds": args.sample_seconds, "exact_target_mangled": EXACT_TARGET_MANGLED, "exact_candidate": EXACT_CANDIDATE, "same_process_identical_operation_count": 2, "tool": {"path": str(args.tool_path), "sha256": args.tool_sha256}, "nvdisasm_environment_contract": contract, "child_exit_code": child_exit, "elapsed_seconds": elapsed, "discovery_summary_line": summary, "target_reuse_callback_observed": reuse, "samples": {"path": str(args.samples_path), "sha256": sha256_file(args.samples_path), "count": len(samples)}, "stack_snapshots": snapshots, "stage": {"path": str(args.stage_path), "sha256": sha256_file(args.stage_path)} if args.stage_path.is_file() else None, "child_receipt": {"path": str(args.child_receipt), "sha256": sha256_file(args.child_receipt)} if args.child_receipt.is_file() else None, "stdout": {"path": str(args.stdout_path), "sha256": sha256_file(args.stdout_path)}, "stderr": {"path": str(args.stderr_path), "sha256": sha256_file(args.stderr_path)}, "trace_generated": False, "raw_trace_bytes": 0}
        atomic_json(args.receipt, receipt)
        return 0 if terminal == "COMPLETE" else 2
    except Exception as exc:
        if process is not None:
            _kill_process_group(process)
        atomic_json(args.receipt, {"schema_version": SCHEMA, "status": "HARNESS_FAIL_CLOSED", "scientific_eligible": False, "message": str(exc), "run_id": args.run_id})
        raise


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--child", action="store_true")
    value.add_argument("--receipt", type=Path)
    value.add_argument("--samples-path", type=Path)
    value.add_argument("--stage-path", type=Path, required=True)
    value.add_argument("--child-receipt", type=Path, required=True)
    value.add_argument("--stdout-path", type=Path)
    value.add_argument("--stderr-path", type=Path)
    value.add_argument("--stack-dir", type=Path)
    value.add_argument("--budget-ledger", type=Path)
    value.add_argument("--wall-limit-seconds", type=int, default=WALL_LIMIT_SECONDS)
    value.add_argument("--sample-seconds", type=int, default=SAMPLE_SECONDS)
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
    required = (args.receipt, args.samples_path, args.stdout_path, args.stderr_path, args.stack_dir, args.budget_ledger, args.runtime_code_commit, args.run_id)
    if any(item is None for item in required):
        raise ContractError("exact discovery parent requires all payload paths, ledger, source commit, and run ID")
    raise SystemExit(parent_main(args))


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL Retry570 exact discovery: {exc}", file=sys.stderr)
        raise SystemExit(2)
