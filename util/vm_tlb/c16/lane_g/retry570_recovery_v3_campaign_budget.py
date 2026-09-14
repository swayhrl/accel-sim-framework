#!/usr/bin/env python3
"""Fresh, scope-bound capture accounting for C16 Recovery-V3.

This ledger deliberately never opens a historical ledger for write.  It is a
new authorization namespace for new Recovery-V3 target classes, while keeping
the old ledger byte-addressed as provenance only.
"""
from __future__ import annotations

import fcntl
import json
import time
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file


SCHEMA = "C16_G_RECOVERY_V3_CAMPAIGN_BUDGET_V1"
CAMPAIGN_ID = "c16_full_authority_recovery_v3"
MAX_WINDOWS_PER_SCOPE = 8
MAX_WINDOW_SECONDS = 20 * 60
MAX_WINDOW_RAW_BYTES = 4 * 1024 * 1024 * 1024
MAX_CAMPAIGN_RAW_BYTES = 32 * 1024 * 1024 * 1024


def _limits() -> dict[str, int]:
    return {
        "max_capture_windows_per_budget_scope": MAX_WINDOWS_PER_SCOPE,
        "max_window_seconds": MAX_WINDOW_SECONDS,
        "max_window_raw_bytes": MAX_WINDOW_RAW_BYTES,
        "max_campaign_raw_bytes": MAX_CAMPAIGN_RAW_BYTES,
    }


def _scope_for(identity: dict[str, Any], budget_scope: str) -> None:
    deployment = identity.get("deployment_id")
    scenario = identity.get("scenario_id")
    if not isinstance(deployment, str) or not deployment or not isinstance(scenario, str) or not scenario:
        raise ContractError("Recovery-V3 campaign identity lacks deployment/scenario")
    fields = budget_scope.split("/")
    if len(fields) != 3 or fields[0] != deployment or fields[1] != scenario or not fields[2]:
        raise ContractError("Recovery-V3 budget scope must be deployment/scenario/phase-target-class")


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read Recovery-V3 campaign ledger: {path}") from exc
    if not isinstance(value, dict) or value.get("schema_version") != SCHEMA or value.get("campaign_id") != CAMPAIGN_ID:
        raise ContractError("Recovery-V3 campaign ledger schema/campaign differs")
    if value.get("limits") != _limits() or not isinstance(value.get("entries"), list):
        raise ContractError("Recovery-V3 campaign ledger limits/entries are malformed")
    history = value.get("historical_ledger")
    if not isinstance(history, dict) or not isinstance(history.get("path"), str) or not isinstance(history.get("sha256"), str):
        raise ContractError("Recovery-V3 campaign ledger lacks immutable history provenance")
    for entry in value["entries"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("elapsed_seconds"), (int, float)) or not isinstance(entry.get("raw_bytes"), int):
            raise ContractError("Recovery-V3 campaign ledger has malformed entry")
        if entry["elapsed_seconds"] < 0 or entry["raw_bytes"] < 0 or not isinstance(entry.get("budget_scope"), str):
            raise ContractError("Recovery-V3 campaign ledger has invalid entry")
    return value


def initialize(*, ledger_path: Path, historical_ledger: Path, expected_historical_sha256: str,
               identity: dict[str, Any], budget_scope: str) -> dict[str, Any]:
    """Create/reopen the independent campaign ledger without mutating history."""
    _scope_for(identity, budget_scope)
    if not historical_ledger.is_file() or sha256_file(historical_ledger) != expected_historical_sha256:
        raise ContractError("historical ledger does not match the explicitly bound immutable SHA256")
    lock_path = ledger_path.with_name(ledger_path.name + ".lock")
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    before = historical_ledger.read_bytes()
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        if ledger_path.exists():
            value = _read(ledger_path)
            if value["historical_ledger"] != {"path": str(historical_ledger), "sha256": expected_historical_sha256, "rows_preserved": True}:
                raise ContractError("Recovery-V3 campaign ledger binds different historical provenance")
        else:
            value = {
                "schema_version": SCHEMA,
                "campaign_id": CAMPAIGN_ID,
                "authorization": "RECOVERY_V3_GPU_PIPELINE_SCHEDULING_DELTA_V10",
                "historical_ledger": {"path": str(historical_ledger), "sha256": expected_historical_sha256, "rows_preserved": True},
                "limits": _limits(),
                "entries": [],
            }
            atomic_json(ledger_path, value)
        if historical_ledger.read_bytes() != before:
            raise ContractError("historical ledger changed while Recovery-V3 namespace initialized")
    return value


class RecoveryV3CampaignLease:
    """One exclusive capture lease in the fresh campaign/scenario namespace."""
    def __init__(self, ledger_path: Path, identity: dict[str, Any], operation_kind: str, *, capture: bool,
                 budget_scope: str) -> None:
        if not capture or operation_kind != "NVBIT":
            raise ContractError("Recovery-V3 campaign namespace permits bounded NVBIT capture only")
        _scope_for(identity, budget_scope)
        self.ledger_path = ledger_path
        self.identity = identity
        self.operation_kind = operation_kind
        self.budget_scope = budget_scope
        self.capture = capture
        self._handle: Any | None = None
        self._ledger: dict[str, Any] | None = None
        self._started = 0.0
        self._finished = False
        self.max_elapsed_seconds = 0.0
        self.max_raw_bytes = 0

    def __enter__(self) -> "RecoveryV3CampaignLease":
        lock_path = self.ledger_path.with_name(self.ledger_path.name + ".lock")
        self._handle = lock_path.open("a+", encoding="utf-8")
        try:
            fcntl.flock(self._handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            self._handle.close(); self._handle = None
            raise ContractError("another Recovery-V3 capture owns the campaign lease") from exc
        try:
            self._ledger = _read(self.ledger_path)
            windows = sum(entry.get("budget_scope") == self.budget_scope for entry in self._ledger["entries"])
            if windows >= MAX_WINDOWS_PER_SCOPE:
                raise ContractError("Recovery-V3 budget scope reached its authorized eight capture windows")
            raw_used = sum(int(entry["raw_bytes"]) for entry in self._ledger["entries"])
            if raw_used >= MAX_CAMPAIGN_RAW_BYTES:
                raise ContractError("Recovery-V3 campaign raw budget is exhausted")
            self.max_elapsed_seconds = MAX_WINDOW_SECONDS
            self.max_raw_bytes = min(MAX_WINDOW_RAW_BYTES, MAX_CAMPAIGN_RAW_BYTES - raw_used)
            self._started = time.monotonic()
            return self
        except Exception:
            fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN); self._handle.close(); self._handle = None
            raise

    def elapsed_seconds(self) -> float:
        return time.monotonic() - self._started

    def finish(self, *, elapsed_seconds: float, raw_bytes: int, terminal_status: str,
               evidence_classification: str = "SCIENTIFIC", diagnostic_reason: str | None = None) -> None:
        if self._ledger is None or self._finished:
            raise ContractError("Recovery-V3 campaign lease is not active")
        if elapsed_seconds < 0 or raw_bytes < 0 or elapsed_seconds > self.max_elapsed_seconds or raw_bytes > self.max_raw_bytes:
            raise ContractError("Recovery-V3 campaign capture exceeds hard lease bounds")
        entry = {
            "operation_kind": self.operation_kind,
            "campaign_id": CAMPAIGN_ID,
            "budget_scope": self.budget_scope,
            "deployment_id": self.identity["deployment_id"],
            "scenario_id": self.identity["scenario_id"],
            "run_id": self.identity["run_id"],
            "elapsed_seconds": elapsed_seconds,
            "raw_bytes": raw_bytes,
            "terminal_status": terminal_status,
            "evidence_classification": evidence_classification,
            "max_elapsed_seconds_at_start": self.max_elapsed_seconds,
            "max_raw_bytes_at_start": self.max_raw_bytes,
        }
        if diagnostic_reason:
            entry["diagnostic_reason"] = diagnostic_reason
        self._ledger["entries"].append(entry)
        atomic_json(self.ledger_path, self._ledger)
        self._finished = True

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        try:
            if not self._finished and self._ledger is not None:
                self.finish(elapsed_seconds=self.elapsed_seconds(), raw_bytes=0,
                            terminal_status="FAILED_OR_ABORTED", evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC",
                            diagnostic_reason="UNHANDLED_RECOVERY_V3_CAMPAIGN_CAPTURE_EXIT")
        finally:
            if self._handle is not None:
                fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
                self._handle.close(); self._handle = None
        return False
