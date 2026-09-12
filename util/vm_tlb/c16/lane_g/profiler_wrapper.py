#!/usr/bin/env python3
"""Bounded nsys/NCU/NVBit execution wrapper with an explicit dry-run mode."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, SCHEMA_VERSION, atomic_json, require_exact_keys, sha256_file
from execution_budget import BudgetLease, MAX_NVBIT_WINDOW_BYTES, MAX_NVBIT_WINDOW_SECONDS
from identity_guard import TARGET_FIELDS, read_object
from run_schema import IDENTITY_FIELDS, RUNTIME_FIELDS, validate_receipt


TOOL_EXECUTABLE = {"nsys": "nsys", "ncu": "ncu"}
MAX_NVBIT_BYTES = MAX_NVBIT_WINDOW_BYTES
MAX_NVBIT_SECONDS = MAX_NVBIT_WINDOW_SECONDS


def parse_args(tool: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"C16 bounded {tool} wrapper")
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--target-json", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--metrics-file", type=Path)
    parser.add_argument("--nvbit-tool", type=Path)
    parser.add_argument("--raw-dir", type=Path)
    parser.add_argument("--budget-ledger", type=Path)
    parser.add_argument("--parent-lease-receipt", type=Path)
    parser.add_argument("--profile-overhead-threshold", type=float, default=0.10)
    parser.add_argument("--nsys-capture-range", choices=("nvtx", "none"), default="nvtx")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.dry_run == args.execute:
        parser.error("choose exactly one of --dry-run or --execute")
    if not args.command or args.command[0] != "--" or len(args.command) == 1:
        parser.error("command must follow --")
    args.command = args.command[1:]
    if tool == "ncu" and args.metrics_file is None:
        parser.error("NCU requires a frozen --metrics-file")
    if tool == "nvbit" and (args.nvbit_tool is None or args.raw_dir is None):
        parser.error("NVBit requires --nvbit-tool and --raw-dir")
    if args.execute and args.budget_ledger is None:
        parser.error("real C16 profiler execution requires one shared --budget-ledger")
    if args.execute and tool != "nvbit" and args.parent_lease_receipt is None:
        parser.error("real nsys/ncu execution requires an explicit immutable --parent-lease-receipt for its child runner")
    if tool == "nvbit" and args.parent_lease_receipt is not None:
        parser.error("NVBit has no wrapper-owned child-runner lease contract")
    return args


def target_with_receipt_identity(path: Path) -> dict[str, Any]:
    target = read_object(path)
    require_exact_keys(target, TARGET_FIELDS, "profiler target")
    identity = target.get("identity")
    runtime = target.get("runtime")
    if not isinstance(identity, dict) or not isinstance(runtime, dict):
        raise ContractError("profiler target must carry full run identity and runtime")
    require_exact_keys(identity, IDENTITY_FIELDS, "profiler target identity")
    return target


def metric_names(path: Path) -> list[str]:
    try:
        names = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    except OSError as exc:
        raise ContractError(f"cannot read frozen NCU metric list: {exc}") from exc
    if not names or any("--set" in name or name.lower() == "full" for name in names):
        raise ContractError("NCU metric list must be compact and may not request --set full")
    return names


def plan_command(tool: str, args: argparse.Namespace) -> list[str]:
    output = str(args.output)
    if tool == "nsys":
        command = ["nsys", "profile", "--force-overwrite=true", "--trace=cuda,nvtx,osrt"]
        if args.nsys_capture_range == "nvtx":
            command.extend(("--capture-range=nvtx", "--capture-range-end=stop"))
        return [*command, "-o", output, *args.command]
    if tool == "ncu":
        return ["ncu", "--target-processes", "application", "--replay-mode", "application", "--metrics", ",".join(metric_names(args.metrics_file)), "--export", output, *args.command]
    return list(args.command)


def output_bytes(path: Path) -> int:
    candidates = {path, *path.parent.glob(path.name + "*")}
    total = 0
    for candidate in candidates:
        if candidate.is_file():
            total += candidate.stat().st_size
        elif candidate.is_dir():
            total += sum(item.stat().st_size for item in candidate.rglob("*") if item.is_file())
    return total


def run_nvbit_guarded(command: list[str], raw_dir: Path, nvbit_tool: Path, target_json: Path, *, max_raw_bytes: int, max_seconds: float) -> tuple[int, str, int, float]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    environment = dict(os.environ)
    environment["CUDA_INJECTION64_PATH"] = str(nvbit_tool)
    environment["C16_NVBIT_TARGET_FILTER_JSON"] = str(target_json)
    process = subprocess.Popen(command, env=environment)
    status = "COMPLETE"
    while process.poll() is None:
        elapsed = time.monotonic() - started
        size = output_bytes(raw_dir)
        if size >= max_raw_bytes or elapsed >= max_seconds:
            status = "BOUNDED_PARTIAL"
            process.terminate()
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            break
        time.sleep(1)
    return process.returncode or 0, status, output_bytes(raw_dir), time.monotonic() - started


def run_command_guarded(command: list[str], max_seconds: float, environment: dict[str, str] | None = None) -> tuple[int, str, float]:
    started = time.monotonic()
    process = subprocess.Popen(command, env=environment)
    status = "COMPLETE"
    while process.poll() is None:
        if time.monotonic() - started >= max_seconds:
            status = "BOUNDED_PARTIAL"
            process.terminate()
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            break
        time.sleep(0.25)
    if status == "COMPLETE" and process.returncode not in (0, None):
        status = "FAILED"
    return process.returncode or 0, status, time.monotonic() - started


def write_parent_lease_start(path: Path, target: dict[str, Any], tool: str, budget: BudgetLease) -> tuple[dict[str, Any], str]:
    """Materialize an immutable, token-bound parent lease proof before launch."""
    if path.exists():
        raise ContractError("parent lease start receipt already exists; refusing to overwrite a session proof")
    token = secrets.token_urlsafe(32)
    payload = {
        "schema_version": "C16_G_PARENT_LEASE_V1",
        "state": "ACTIVE_IMMUTABLE_START_RECEIPT",
        "parent_lease_id": str(uuid.uuid4()),
        "lease_token_sha256": hashlib.sha256(token.encode("utf-8")).hexdigest(),
        "ledger_path": str(budget.ledger_path),
        "max_elapsed_seconds": budget.max_elapsed_seconds,
        "valid_until_unix": time.time() + budget.max_elapsed_seconds,
        "identity": target["identity"],
        "operation_kind": tool.upper(),
        "wrapper_pid": os.getpid(),
        "child_must_prove_locked_ledger": True,
    }
    atomic_json(path, payload)
    return payload, token


def write_parent_lease_closeout(start_path: Path, parent: dict[str, Any], *, terminal_status: str, elapsed_seconds: float, returncode: int | None) -> Path:
    """Record completion separately so the child-observed start receipt stays immutable."""
    closeout = start_path.with_name(start_path.name + ".closeout.json")
    if closeout.exists():
        raise ContractError("parent lease closeout already exists; refusing to overwrite session provenance")
    atomic_json(closeout, {
        "schema_version": "C16_G_PARENT_LEASE_CLOSEOUT_V1",
        "parent_lease_id": parent["parent_lease_id"],
        "parent_start_receipt": str(start_path),
        "parent_start_receipt_sha256": sha256_file(start_path),
        "terminal_status": terminal_status,
        "elapsed_seconds": elapsed_seconds,
        "returncode": returncode if returncode is not None else "NA",
    })
    return closeout


def wrapper_receipt(tool: str, args: argparse.Namespace, target: dict[str, Any], command: list[str], *, executed: bool, terminal_status: str, returncode: int | None, elapsed_s: float, bytes_written: int) -> dict[str, Any]:
    native = executed and terminal_status in {"COMPLETE", "BOUNDED_PARTIAL"}
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "stage_id": {"nsys": "C16-1.4", "ncu": "C16-1.5", "nvbit": "C16-1.6"}[tool],
        "execution_mode": "NATIVE_GPU" if native else "DRY_RUN",
        "scientific_eligible": native,
        "identity": target["identity"],
        "runtime": target["runtime"],
        "checks": {
            "target_identity_fields": {field: target[field] for field in TARGET_FIELDS},
            "naked_launch_ordinal_join_forbidden": True,
            "command": command,
            "profile_overhead_threshold": args.profile_overhead_threshold,
            "nsys_capture_range": args.nsys_capture_range if tool == "nsys" else "NA",
            "nvbit_size_limit_bytes": MAX_NVBIT_BYTES if tool == "nvbit" else "NA",
            "nvbit_time_limit_seconds": MAX_NVBIT_SECONDS if tool == "nvbit" else "NA",
            "nvbit_injection_tool": str(args.nvbit_tool) if tool == "nvbit" else "NA",
            "execution_budget_ledger": str(args.budget_ledger) if args.budget_ledger is not None else "NA",
            "parent_lease_start_receipt": str(args.parent_lease_receipt) if args.parent_lease_receipt is not None else "NA",
            "parent_lease_closeout_receipt": str(getattr(args, "parent_lease_closeout", "NA")),
        },
        "artifacts": {
            "tool": tool,
            "terminal_status": terminal_status,
            "returncode": returncode if returncode is not None else "NA",
            "elapsed_seconds": elapsed_s,
            "output_path": str(args.output),
            "output_bytes": bytes_written,
            "output_sha256": sha256_file(args.output) if args.output.is_file() else "NA",
        },
    }
    if native:
        require_exact_keys(receipt["runtime"], RUNTIME_FIELDS, "native profiler runtime")
    validate_receipt(receipt, require_native=native)
    return receipt


def main(tool: str) -> None:
    args = parse_args(tool)
    target = target_with_receipt_identity(args.target_json)
    command = plan_command(tool, args)
    if args.dry_run:
        receipt = wrapper_receipt(tool, args, target, command, executed=False, terminal_status="DRY_RUN_NONSCIENTIFIC", returncode=None, elapsed_s=0.0, bytes_written=0)
        atomic_json(args.receipt, receipt)
        print(f"PASS C16 {tool} offline dry-run: {args.receipt}")
        return
    if tool != "nvbit" and shutil.which(TOOL_EXECUTABLE[tool]) is None:
        raise ContractError(f"required {tool} executable is unavailable")
    if tool == "nvbit" and not args.nvbit_tool.is_file():
        raise ContractError("NVBit injection tool is unavailable")
    parent: dict[str, Any] | None = None
    returncode: int | None = None
    elapsed = 0.0
    try:
        with BudgetLease(args.budget_ledger, target["identity"], tool.upper(), capture=tool == "nvbit") as budget:
            if tool == "nvbit":
                returncode, terminal_status, bytes_written, elapsed = run_nvbit_guarded(
                    command, args.raw_dir, args.nvbit_tool, args.target_json,
                    max_raw_bytes=budget.max_raw_bytes, max_seconds=budget.max_elapsed_seconds,
                )
                budget.finish(elapsed_seconds=elapsed, raw_bytes=bytes_written, terminal_status=terminal_status)
            else:
                parent, token = write_parent_lease_start(args.parent_lease_receipt, target, tool, budget)
                environment = dict(os.environ)
                environment["C16_G_PARENT_LEASE_RECEIPT"] = str(args.parent_lease_receipt)
                environment["C16_G_PARENT_LEASE_TOKEN"] = token
                returncode, terminal_status, elapsed = run_command_guarded(command, budget.max_elapsed_seconds, environment)
                bytes_written = output_bytes(args.output)
                if tool == "nsys" and terminal_status == "COMPLETE" and returncode == 0 and bytes_written == 0:
                    terminal_status = "FAILED_EMPTY_PROFILE"
                scientific = terminal_status in {"COMPLETE", "BOUNDED_PARTIAL"}
                budget.finish(
                    elapsed_seconds=elapsed,
                    raw_bytes=0,
                    terminal_status=terminal_status,
                    evidence_classification="SCIENTIFIC" if scientific else "NON_SCIENTIFIC_DIAGNOSTIC",
                    diagnostic_reason=None if scientific else f"{tool.upper()}_{terminal_status}",
                )
    except Exception:
        if parent is not None:
            args.parent_lease_closeout = write_parent_lease_closeout(
                args.parent_lease_receipt, parent,
                terminal_status="FAILED_OR_ABORTED", elapsed_seconds=elapsed, returncode=returncode,
            )
        raise
    if parent is not None:
        args.parent_lease_closeout = write_parent_lease_closeout(
            args.parent_lease_receipt, parent,
            terminal_status=terminal_status, elapsed_seconds=elapsed, returncode=returncode,
        )
    receipt = wrapper_receipt(tool, args, target, command, executed=True, terminal_status=terminal_status, returncode=returncode, elapsed_s=elapsed, bytes_written=bytes_written)
    atomic_json(args.receipt, receipt)
    if terminal_status not in {"COMPLETE", "BOUNDED_PARTIAL"}:
        raise ContractError(f"{tool} did not produce an accepted bounded result: {terminal_status} (returncode {returncode})")
    print(f"PASS C16 {tool} wrapper: {args.receipt} ({terminal_status})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--tool", choices=("nsys", "ncu", "nvbit"), required=True)
    known, remaining = parser.parse_known_args()
    sys.argv = [sys.argv[0], *remaining]
    try:
        main(known.tool)
    except ContractError as exc:
        print(f"FAIL C16 profiler contract: {exc}", file=sys.stderr)
        raise SystemExit(2)
