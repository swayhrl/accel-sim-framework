#!/usr/bin/env python3
"""Fail-closed accounting and leases for bounded C16 native operations.

The ledger is intentionally local to the AutoDL work root.  It contains only
small receipts and is neither a trace nor a scientific measurement artifact.
"""
from __future__ import annotations

import fcntl
import json
import os
import time
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, PLANNING_SHA, atomic_json


SCHEMA_VERSION = "C16_G_EXECUTION_BUDGET_V1"
MAX_GPU_INSTANCE_WALL_SECONDS = 24 * 60 * 60
MAX_NVBIT_TOTAL_RAW_BYTES = 64 * 1024 * 1024 * 1024
MAX_NVBIT_WINDOW_BYTES = 4 * 1024 * 1024 * 1024
MAX_NVBIT_WINDOW_SECONDS = 20 * 60
MAX_NVBIT_WINDOWS_PER_DEPLOYMENT = 6
EVIDENCE_CLASSIFICATIONS = {"SCIENTIFIC", "NON_SCIENTIFIC_DIAGNOSTIC", "ACCOUNTING_ONLY"}
MEASUREMENT_ACTIVE_SCHEMA = "C16_G_MEASUREMENT_ACTIVE_V1"


def _new_ledger() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "planning_sha": PLANNING_SHA,
        "limits": {
            "gpu_instance_wall_seconds": MAX_GPU_INSTANCE_WALL_SECONDS,
            "nvbit_total_raw_bytes": MAX_NVBIT_TOTAL_RAW_BYTES,
            "nvbit_window_raw_bytes": MAX_NVBIT_WINDOW_BYTES,
            "nvbit_window_seconds": MAX_NVBIT_WINDOW_SECONDS,
            "nvbit_windows_per_deployment": MAX_NVBIT_WINDOWS_PER_DEPLOYMENT,
        },
        "instance": {
            "start_unix": None,
            "start_source": "UNINITIALIZED",
            "instance_receipt_path": "NA",
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
    instance = payload.get("instance")
    if not isinstance(instance, dict) or not isinstance(instance.get("start_source"), str) or not isinstance(instance.get("instance_receipt_path"), str):
        raise ContractError("execution-budget ledger has malformed instance provenance")
    if instance.get("start_unix") is not None and (not isinstance(instance["start_unix"], (int, float)) or instance["start_unix"] <= 0):
        raise ContractError("execution-budget ledger has an invalid instance start time")
    if not isinstance(payload.get("entries"), list):
        raise ContractError("execution-budget ledger has no entry list")
    for entry in payload["entries"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("elapsed_seconds"), (int, float)) or not isinstance(entry.get("raw_bytes"), int):
            raise ContractError("execution-budget ledger has a malformed entry")
        if entry["elapsed_seconds"] < 0 or entry["raw_bytes"] < 0:
            raise ContractError("execution-budget ledger has a negative accounting value")
        classification = entry.get("evidence_classification")
        if classification is not None and classification not in EVIDENCE_CLASSIFICATIONS:
            raise ContractError("execution-budget ledger has an unknown evidence classification")
    return payload


def _totals(payload: dict[str, Any]) -> tuple[float, int]:
    return (
        sum(float(entry["elapsed_seconds"]) for entry in payload["entries"]),
        sum(int(entry["raw_bytes"]) for entry in payload["entries"]),
    )


def initialize_ledger(ledger_path: Path, *, instance_start_unix: float, start_source: str, instance_receipt_path: Path) -> dict[str, Any]:
    """Initialize the one ledger from a C16-1.1 receipt without guessing start time."""
    if instance_start_unix <= 0 or instance_start_unix > time.time() or not start_source:
        raise ContractError("execution-budget ledger requires an observed, non-future instance start time")
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = ledger_path.with_name(ledger_path.name + ".lock")
    with lock_path.open("a+", encoding="utf-8") as lock_handle:
        try:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ContractError("another C16 GPU operation holds the shared execution-budget ledger") from exc
        try:
            ledger = _load(ledger_path)
            instance = ledger["instance"]
            expected = {
                "start_unix": instance_start_unix,
                "start_source": start_source,
                "instance_receipt_path": str(instance_receipt_path),
            }
            if instance["start_unix"] is None:
                ledger["instance"] = expected
                atomic_json(ledger_path, ledger)
            elif instance != expected:
                raise ContractError("execution-budget ledger is already initialized with different instance provenance")
            return ledger
        finally:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)


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
            _active_elapsed_used, raw_used = _totals(self._ledger)
            instance = self._ledger["instance"]
            start_unix = instance["start_unix"]
            if start_unix is None:
                raise ContractError("execution-budget ledger is uninitialized; complete C16-1.1 first")
            wall_remaining = MAX_GPU_INSTANCE_WALL_SECONDS - (time.time() - float(start_unix))
            if wall_remaining <= 0:
                raise ContractError("C16 GPU-instance wall-time budget is exhausted")
            self.max_elapsed_seconds = min(MAX_NVBIT_WINDOW_SECONDS, wall_remaining) if self.capture else wall_remaining
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

    def finish(
        self,
        *,
        elapsed_seconds: float,
        raw_bytes: int,
        terminal_status: str,
        evidence_classification: str = "SCIENTIFIC",
        diagnostic_reason: str | None = None,
    ) -> None:
        if self._ledger is None:
            raise ContractError("execution-budget lease was not acquired")
        if self._finished:
            raise ContractError("execution-budget lease was already finalized")
        if elapsed_seconds < 0 or raw_bytes < 0:
            raise ContractError("cannot record negative execution-budget usage")
        if evidence_classification not in EVIDENCE_CLASSIFICATIONS:
            raise ContractError("execution-budget entry has an unknown evidence classification")
        if diagnostic_reason is not None and (not isinstance(diagnostic_reason, str) or not diagnostic_reason):
            raise ContractError("execution-budget diagnostic reason is malformed")
        if not isinstance(self.identity.get("deployment_id"), str) or not isinstance(self.identity.get("run_id"), str):
            raise ContractError("execution-budget entry lacks deployment/run identity")
        entry = {
            "operation_kind": self.operation_kind,
            "deployment_id": self.identity["deployment_id"],
            "run_id": self.identity["run_id"],
            "elapsed_seconds": elapsed_seconds,
            "raw_bytes": raw_bytes,
            "terminal_status": terminal_status,
            "max_elapsed_seconds_at_start": self.max_elapsed_seconds,
            "max_raw_bytes_at_start": self.max_raw_bytes if self.capture else 0,
            "evidence_classification": evidence_classification,
        }
        if diagnostic_reason is not None:
            entry["diagnostic_reason"] = diagnostic_reason
        self._ledger["entries"].append(entry)
        atomic_json(self.ledger_path, self._ledger)
        self._finished = True

    def record_child_operation(
        self,
        identity: dict[str, Any],
        *,
        operation_kind: str,
        elapsed_seconds: float,
        terminal_status: str,
        evidence_classification: str = "SCIENTIFIC",
        diagnostic_reason: str | None = None,
    ) -> None:
        """Account a resident-session child without taking a second lease.

        A resident process holds this parent lease for its full model lifetime.
        Each frozen scenario is nevertheless an independently identified GPU
        operation, so it receives its own ledger row.  The parent is later
        closed with zero elapsed/raw accounting to avoid double-counting the
        child elapsed time.
        """
        if self._ledger is None or self._finished:
            raise ContractError("resident child accounting requires an active parent budget lease")
        if elapsed_seconds < 0 or evidence_classification not in EVIDENCE_CLASSIFICATIONS:
            raise ContractError("resident child accounting is malformed")
        if not isinstance(identity.get("deployment_id"), str) or not isinstance(identity.get("run_id"), str):
            raise ContractError("resident child accounting lacks deployment/run identity")
        entry = {
            "operation_kind": operation_kind,
            "deployment_id": identity["deployment_id"],
            "run_id": identity["run_id"],
            "elapsed_seconds": elapsed_seconds,
            "raw_bytes": 0,
            "terminal_status": terminal_status,
            "max_elapsed_seconds_at_start": self.max_elapsed_seconds,
            "max_raw_bytes_at_start": 0,
            "evidence_classification": evidence_classification,
            "parent_operation_kind": self.operation_kind,
            "parent_run_id": self.identity.get("run_id", "NA"),
        }
        if diagnostic_reason is not None:
            entry["diagnostic_reason"] = diagnostic_reason
        self._ledger["entries"].append(entry)
        atomic_json(self.ledger_path, self._ledger)

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        try:
            if not self._finished and self._ledger is not None:
                self.finish(
                    elapsed_seconds=self.elapsed_seconds(),
                    raw_bytes=0,
                    terminal_status="FAILED_OR_ABORTED" if exc_type is not None else "UNRECORDED_ABORT",
                    evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC",
                    diagnostic_reason="UNHANDLED_OPERATION_EXIT",
                )
        finally:
            self._release()
        return False


class MeasurementActive:
    """Fail closed when another operation or host task owns the formal window.

    The ledger lock serializes GPU science.  This separate, small marker lets
    remote transfer/export helpers observe that they must not share the host
    with a formal measurement.  It is created only while the caller owns a
    ledger lease.  A stale marker is intentionally not overwritten.
    """

    def __init__(self, ledger_path: Path, identity: dict[str, Any], operation_kind: str) -> None:
        self.ledger_path = ledger_path
        self.identity = identity
        self.operation_kind = operation_kind
        self.path = ledger_path.parent.parent / "control" / "MEASUREMENT_ACTIVE"
        self.marker_id = ""

    def __enter__(self) -> "MeasurementActive":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            raise ContractError(f"formal GPU operation is blocked by an existing measurement marker: {self.path}")
        self.marker_id = f"{self.operation_kind}-{time.time_ns()}"
        atomic_json(self.path, {
            "schema_version": MEASUREMENT_ACTIVE_SCHEMA,
            "marker_id": self.marker_id,
            "operation_kind": self.operation_kind,
            "ledger_path": str(self.ledger_path),
            "deployment_id": self.identity.get("deployment_id"),
            "run_id": self.identity.get("run_id"),
            "pid": os.getpid(),
            "started_unix": time.time(),
        })
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        try:
            marker = json.loads(self.path.read_text(encoding="utf-8"))
            if marker.get("schema_version") != MEASUREMENT_ACTIVE_SCHEMA or marker.get("marker_id") != self.marker_id:
                raise ContractError("measurement marker changed ownership during a formal GPU operation")
            self.path.unlink()
        except FileNotFoundError as error:
            raise ContractError("measurement marker disappeared during a formal GPU operation") from error
        except json.JSONDecodeError as error:
            raise ContractError("measurement marker is unreadable during formal GPU cleanup") from error
        return False


def mark_existing_entry_diagnostic(ledger_path: Path, *, run_id: str, reason: str) -> dict[str, Any]:
    """Annotate an already-accounted run without changing elapsed/raw usage.

    This is for historical pre-gate attempts.  It never deletes an entry or
    rewrites its resource accounting, and refuses to relabel a previously
    explicit scientific entry.
    """
    if not run_id or not reason:
        raise ContractError("diagnostic annotation requires run ID and reason")
    lock_path = ledger_path.with_name(ledger_path.name + ".lock")
    with lock_path.open("a+", encoding="utf-8") as lock_handle:
        try:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ContractError("cannot annotate a ledger while a C16 operation is active") from exc
        try:
            ledger = _load(ledger_path)
            matches = [entry for entry in ledger["entries"] if entry.get("run_id") == run_id]
            if len(matches) != 1:
                raise ContractError("diagnostic annotation requires exactly one existing ledger entry")
            entry = matches[0]
            existing = entry.get("evidence_classification")
            if existing not in (None, "NON_SCIENTIFIC_DIAGNOSTIC"):
                raise ContractError("refusing to relabel an explicit scientific ledger entry")
            entry["evidence_classification"] = "NON_SCIENTIFIC_DIAGNOSTIC"
            entry["diagnostic_reason"] = reason
            atomic_json(ledger_path, ledger)
            return entry
        finally:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)


def ledger_markdown() -> str:
    return """# C16 Lane G execution-budget guard

Real C16 native operations require one shared `--budget-ledger` in the AutoDL work root. C16-1.1 initializes it from an explicit provider/AutoDL instance-start timestamp and the instance receipt path; a real operation cannot create or use an uninitialized ledger. The guard serializes C16 GPU operations with a nonblocking lock, enforces the 24 GPU-instance-hour wall-clock envelope, and records GPU-active operation elapsed time separately from rental wall time and NVBit raw bytes. For NVBit it additionally refuses concurrent use, a seventh first-wave window for one deployment, or a window whose available raw allowance is exhausted.

NVBit's effective runtime/raw ceiling is the smaller of the per-window 20-minute/4-GiB limit and the remaining instance wall-time/64-GiB budget. A terminal `BOUNDED_PARTIAL` is preserved rather than extended. The ledger is accounting provenance only: it never turns a dry-run into native evidence and it never contains profiler raw output.
"""
