#!/usr/bin/env python3
"""Fail-closed accounting and leases for bounded C16 native operations.

The ledger is intentionally local to the AutoDL work root.  It contains only
small receipts and is neither a trace nor a scientific measurement artifact.
"""
from __future__ import annotations

import fcntl
import json
import time
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, PLANNING_SHA, atomic_json


SCHEMA_VERSION = "C16_G_EXECUTION_BUDGET_V1"
MAX_GPU_ACTIVE_SECONDS = 24 * 60 * 60
MAX_NVBIT_TOTAL_RAW_BYTES = 64 * 1024 * 1024 * 1024
MAX_NVBIT_WINDOW_BYTES = 4 * 1024 * 1024 * 1024
MAX_NVBIT_WINDOW_SECONDS = 20 * 60
MAX_NVBIT_WINDOWS_PER_DEPLOYMENT = 6


def _new_ledger() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "planning_sha": PLANNING_SHA,
        "limits": {
            "gpu_active_seconds": MAX_GPU_ACTIVE_SECONDS,
            "nvbit_total_raw_bytes": MAX_NVBIT_TOTAL_RAW_BYTES,
            "nvbit_window_raw_bytes": MAX_NVBIT_WINDOW_BYTES,
            "nvbit_window_seconds": MAX_NVBIT_WINDOW_SECONDS,
            "nvbit_windows_per_deployment": MAX_NVBIT_WINDOWS_PER_DEPLOYMENT,
        },
        "entries": [],
    }


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return _new_ledger()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read execution-budget ledger: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
        raise ContractError("execution-budget ledger has an unknown schema")
    if payload.get("planning_sha") != PLANNING_SHA or payload.get("limits") != _new_ledger()["limits"]:
        raise ContractError("execution-budget ledger planning authority or hard limits differ")
    if not isinstance(payload.get("entries"), list):
        raise ContractError("execution-budget ledger has no entry list")
    for entry in payload["entries"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("elapsed_seconds"), (int, float)) or not isinstance(entry.get("raw_bytes"), int):
            raise ContractError("execution-budget ledger has a malformed entry")
        if entry["elapsed_seconds"] < 0 or entry["raw_bytes"] < 0:
            raise ContractError("execution-budget ledger has a negative accounting value")
    return payload


def _totals(payload: dict[str, Any]) -> tuple[float, int]:
    return (
        sum(float(entry["elapsed_seconds"]) for entry in payload["entries"]),
        sum(int(entry["raw_bytes"]) for entry in payload["entries"]),
    )


class BudgetLease:
    """One fail-closed operation lease, serialized by a sidecar file lock."""

    def __init__(self, ledger_path: Path, identity: dict[str, Any], operation_kind: str, *, capture: bool) -> None:
        self.ledger_path = ledger_path
        self.identity = identity
        self.operation_kind = operation_kind
        self.capture = capture
        self._lock_handle: Any | None = None
        self._ledger: dict[str, Any] | None = None
        self._started = 0.0
        self._finished = False
        self.max_elapsed_seconds = 0.0
        self.max_raw_bytes = 0

    def _release(self) -> None:
        if self._lock_handle is not None:
            fcntl.flock(self._lock_handle.fileno(), fcntl.LOCK_UN)
            self._lock_handle.close()
            self._lock_handle = None

    def __enter__(self) -> "BudgetLease":
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path = self.ledger_path.with_name(self.ledger_path.name + ".lock")
        self._lock_handle = lock_path.open("a+", encoding="utf-8")
        try:
            fcntl.flock(self._lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            self._release()
            raise ContractError("another C16 GPU operation holds the shared execution-budget ledger") from exc
        try:
            self._ledger = _load(self.ledger_path)
            elapsed_used, raw_used = _totals(self._ledger)
            active_remaining = MAX_GPU_ACTIVE_SECONDS - elapsed_used
            if active_remaining <= 0:
                raise ContractError("C16 GPU-active-hour budget is exhausted")
            self.max_elapsed_seconds = min(MAX_NVBIT_WINDOW_SECONDS, active_remaining) if self.capture else active_remaining
            if self.capture:
                deployment = self.identity.get("deployment_id")
                windows = sum(
                    entry.get("operation_kind") == "NVBIT" and entry.get("deployment_id") == deployment
                    for entry in self._ledger["entries"]
                )
                if windows >= MAX_NVBIT_WINDOWS_PER_DEPLOYMENT:
                    raise ContractError("first-wave NVBit window budget is exhausted for this deployment")
                raw_remaining = MAX_NVBIT_TOTAL_RAW_BYTES - raw_used
                if raw_remaining <= 0:
                    raise ContractError("C16 first-wave NVBit raw-budget is exhausted")
                self.max_raw_bytes = min(MAX_NVBIT_WINDOW_BYTES, raw_remaining)
            self._started = time.monotonic()
            return self
        except Exception:
            self._release()
            raise

    def elapsed_seconds(self) -> float:
        return time.monotonic() - self._started

    def expired(self) -> bool:
        return self.elapsed_seconds() >= self.max_elapsed_seconds

    def finish(self, *, elapsed_seconds: float, raw_bytes: int, terminal_status: str) -> None:
        if self._ledger is None:
            raise ContractError("execution-budget lease was not acquired")
        if self._finished:
            raise ContractError("execution-budget lease was already finalized")
        if elapsed_seconds < 0 or raw_bytes < 0:
            raise ContractError("cannot record negative execution-budget usage")
        if not isinstance(self.identity.get("deployment_id"), str) or not isinstance(self.identity.get("run_id"), str):
            raise ContractError("execution-budget entry lacks deployment/run identity")
        self._ledger["entries"].append({
            "operation_kind": self.operation_kind,
            "deployment_id": self.identity["deployment_id"],
            "run_id": self.identity["run_id"],
            "elapsed_seconds": elapsed_seconds,
            "raw_bytes": raw_bytes,
            "terminal_status": terminal_status,
            "max_elapsed_seconds_at_start": self.max_elapsed_seconds,
            "max_raw_bytes_at_start": self.max_raw_bytes if self.capture else 0,
        })
        atomic_json(self.ledger_path, self._ledger)
        self._finished = True

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        try:
            if not self._finished and self._ledger is not None:
                self.finish(
                    elapsed_seconds=self.elapsed_seconds(),
                    raw_bytes=0,
                    terminal_status="FAILED_OR_ABORTED" if exc_type is not None else "UNRECORDED_ABORT",
                )
        finally:
            self._release()
        return False


def ledger_markdown() -> str:
    return """# C16 Lane G execution-budget guard

Real C16 native operations require one shared `--budget-ledger` in the AutoDL work root. The guard serializes C16 GPU operations with a nonblocking lock and records native/profile elapsed time separately from NVBit raw bytes. It refuses a new operation after 24 GPU-active hours, and for NVBit it additionally refuses concurrent use, a seventh first-wave window for one deployment, or a window whose available raw allowance is exhausted.

NVBit's effective runtime/raw ceiling is the smaller of the per-window 20-minute/4-GiB limit and the remaining global 24-hour/64-GiB budget. A terminal `BOUNDED_PARTIAL` is preserved rather than extended. The ledger is accounting provenance only: it never turns a dry-run into native evidence and it never contains profiler raw output.
"""
