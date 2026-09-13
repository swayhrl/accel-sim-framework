"""Immutable-history budget namespace for C16 NVBit recovery campaign v2.

The historical C16 ledger is deliberately *not* imported, rewritten, or
reclassified.  Recovery captures receive a new ledger file and deployment
namespace with a separately authorized eight-window maximum per model.
"""
from __future__ import annotations

import fcntl
import json
import time
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file


SCHEMA = "C16_G_NVBIT175_RECOVERY_BUDGET_V2"
CAMPAIGN_ID = "c16_nvbit175_multimodel_recovery_v2"
MAX_WINDOWS_PER_DEPLOYMENT = 8
MAX_WINDOW_SECONDS = 20 * 60
MAX_WINDOW_RAW_BYTES = 4 * 1024 * 1024 * 1024
MAX_TOTAL_RAW_BYTES = 32 * 1024 * 1024 * 1024


def _read(path: Path) -> dict[str, Any]:
    try: value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: raise ContractError(f"cannot read recovery ledger: {path}") from exc
    if not isinstance(value, dict) or value.get("schema_version") != SCHEMA or value.get("campaign_id") != CAMPAIGN_ID:
        raise ContractError("recovery ledger schema/campaign differs")
    if value.get("limits") != {"max_nvbit_capture_windows_per_deployment": MAX_WINDOWS_PER_DEPLOYMENT, "max_window_seconds": MAX_WINDOW_SECONDS, "max_window_raw_bytes": MAX_WINDOW_RAW_BYTES, "max_total_raw_bytes": MAX_TOTAL_RAW_BYTES}:
        raise ContractError("recovery ledger limits differ from user authorization")
    if not isinstance(value.get("entries"), list) or not isinstance(value.get("historical_ledger"), dict): raise ContractError("recovery ledger is malformed")
    return value


def _historical_lineage(*, historical_ledger: Path, expected_historical_sha256: str,
                        historical_archive: Path | None) -> dict[str, Any]:
    """Prove either an exact live historical ledger or an append-only successor.

    Recovery V2 was deliberately created against an immutable historical
    snapshot.  The live legacy ledger can subsequently receive new (and
    independently retained) entries.  A new recovery capture may continue
    only when a byte-exact archive proves the original snapshot and the live
    ledger is demonstrably an append-only successor.  Merely passing a new
    hash, or a lookalike archive, is not an acceptable bridge.
    """
    if not historical_ledger.is_file():
        raise ContractError("historical ledger is absent")
    live_sha = sha256_file(historical_ledger)
    if live_sha == expected_historical_sha256:
        return {
            "mode": "LIVE_HISTORICAL_LEDGER_EXACT",
            "live_path": str(historical_ledger),
            "live_sha256": live_sha,
            "archive_path": None,
            "archive_sha256": None,
        }
    if historical_archive is None or not historical_archive.is_file():
        raise ContractError("historical ledger changed; exact archive is required for append-only recovery proof")
    archive_sha = sha256_file(historical_archive)
    if archive_sha != expected_historical_sha256:
        raise ContractError("historical archive SHA256 differs from the recovery ledger's immutable binding")
    try:
        archived = json.loads(historical_archive.read_text(encoding="utf-8"))
        live = json.loads(historical_ledger.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError("historical archive/live ledger JSON cannot be read") from exc
    if not isinstance(archived, dict) or not isinstance(live, dict):
        raise ContractError("historical archive/live ledger must be JSON objects")
    if archived.get("schema_version") != live.get("schema_version") or archived.get("limits") != live.get("limits"):
        raise ContractError("live legacy ledger differs in schema or limits from the immutable historical snapshot")
    archived_entries, live_entries = archived.get("entries"), live.get("entries")
    if not isinstance(archived_entries, list) or not isinstance(live_entries, list):
        raise ContractError("historical archive/live ledger lacks entry lists")
    if len(live_entries) < len(archived_entries) or live_entries[:len(archived_entries)] != archived_entries:
        raise ContractError("live legacy ledger is not an append-only successor of the immutable historical snapshot")
    return {
        "mode": "ARCHIVE_EXACT_LIVE_APPEND_ONLY",
        "live_path": str(historical_ledger),
        "live_sha256": live_sha,
        "archive_path": str(historical_archive),
        "archive_sha256": archive_sha,
        "archived_entry_count": len(archived_entries),
        "live_entry_count": len(live_entries),
    }


def initialize(*, recovery_ledger: Path, historical_ledger: Path, expected_historical_sha256: str,
               deployment_id: str, historical_archive: Path | None = None) -> dict[str, Any]:
    """Initialize once while proving immutable-history or append-only lineage."""
    if not deployment_id.startswith("c16_nvbit175_recovery_"):
        raise ContractError("recovery deployment must use the new authorized namespace")
    lineage = _historical_lineage(
        historical_ledger=historical_ledger,
        expected_historical_sha256=expected_historical_sha256,
        historical_archive=historical_archive,
    )
    legacy_before = historical_ledger.read_bytes()
    lock_path = recovery_ledger.with_name(recovery_ledger.name + ".lock")
    recovery_ledger.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        if recovery_ledger.exists():
            value = _read(recovery_ledger)
            if value["historical_ledger"] != {"path": str(historical_ledger), "sha256": expected_historical_sha256, "rows_preserved": True}:
                raise ContractError("recovery ledger does not bind the immutable historical ledger")
        else:
            value = {"schema_version": SCHEMA, "campaign_id": CAMPAIGN_ID,
                     "authorization": "USER_APPROVED_RECOVERY_CAPTURE_WINDOWS",
                     "historical_ledger": {"path": str(historical_ledger), "sha256": expected_historical_sha256, "rows_preserved": True},
                     "limits": {"max_nvbit_capture_windows_per_deployment": MAX_WINDOWS_PER_DEPLOYMENT, "max_window_seconds": MAX_WINDOW_SECONDS, "max_window_raw_bytes": MAX_WINDOW_RAW_BYTES, "max_total_raw_bytes": MAX_TOTAL_RAW_BYTES},
                     "authorized_deployments": [deployment_id], "entries": []}
            atomic_json(recovery_ledger, value)
        if historical_ledger.read_bytes() != legacy_before:
            raise ContractError("live historical ledger changed during recovery initialization")
        # Re-run the exact/append-only proof after creating or reopening the
        # recovery ledger so a concurrent rewrite cannot be mistaken for a
        # legitimate history extension.
        _historical_lineage(
            historical_ledger=historical_ledger,
            expected_historical_sha256=expected_historical_sha256,
            historical_archive=historical_archive,
        )
        return value


class RecoveryBudgetLease:
    """Exclusive new-campaign capture lease; it never opens the old ledger for write."""
    def __init__(self, ledger_path: Path, identity: dict[str, Any], operation_kind: str, *, capture: bool) -> None:
        self.ledger_path, self.identity, self.operation_kind, self.capture = ledger_path, identity, operation_kind, capture
        self._handle: Any | None = None; self._ledger: dict[str, Any] | None = None; self._started = 0.0; self._finished = False
        self.max_elapsed_seconds = 0.0; self.max_raw_bytes = 0

    def __enter__(self) -> "RecoveryBudgetLease":
        deployment = self.identity.get("deployment_id")
        if not isinstance(deployment, str) or not deployment.startswith("c16_nvbit175_recovery_"):
            raise ContractError("recovery capture identity lacks an authorized new deployment namespace")
        lock_path = self.ledger_path.with_name(self.ledger_path.name + ".lock")
        self._handle = lock_path.open("a+", encoding="utf-8")
        try:
            fcntl.flock(self._handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            self._handle.close(); self._handle = None; raise ContractError("another recovery capture owns the campaign lease") from exc
        try:
            self._ledger = _read(self.ledger_path)
            if deployment not in self._ledger["authorized_deployments"]:
                self._ledger["authorized_deployments"].append(deployment); atomic_json(self.ledger_path, self._ledger)
            count = sum(entry.get("operation_kind") == "NVBIT" and entry.get("deployment_id") == deployment for entry in self._ledger["entries"])
            if count >= MAX_WINDOWS_PER_DEPLOYMENT: raise ContractError("new recovery deployment reached its authorized eight NVBit windows")
            total_raw = sum(int(entry.get("raw_bytes", 0)) for entry in self._ledger["entries"])
            if total_raw >= MAX_TOTAL_RAW_BYTES: raise ContractError("new recovery campaign reached its raw storage budget")
            self.max_elapsed_seconds = MAX_WINDOW_SECONDS; self.max_raw_bytes = min(MAX_WINDOW_RAW_BYTES, MAX_TOTAL_RAW_BYTES - total_raw); self._started = time.monotonic()
            return self
        except Exception:
            fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN); self._handle.close(); self._handle = None; raise

    def elapsed_seconds(self) -> float: return time.monotonic() - self._started

    def finish(self, *, elapsed_seconds: float, raw_bytes: int, terminal_status: str, evidence_classification: str = "SCIENTIFIC", diagnostic_reason: str | None = None) -> None:
        if self._ledger is None or self._finished: raise ContractError("recovery lease is not active")
        if elapsed_seconds < 0 or raw_bytes < 0 or elapsed_seconds > self.max_elapsed_seconds or raw_bytes > self.max_raw_bytes:
            raise ContractError("recovery capture exceeds its immutable lease ceiling")
        if not isinstance(self.identity.get("run_id"), str): raise ContractError("recovery lease lacks run identity")
        entry = {"operation_kind": self.operation_kind, "deployment_id": self.identity["deployment_id"], "run_id": self.identity["run_id"], "elapsed_seconds": elapsed_seconds, "raw_bytes": raw_bytes, "terminal_status": terminal_status, "evidence_classification": evidence_classification, "max_elapsed_seconds_at_start": self.max_elapsed_seconds, "max_raw_bytes_at_start": self.max_raw_bytes}
        if diagnostic_reason: entry["diagnostic_reason"] = diagnostic_reason
        self._ledger["entries"].append(entry); atomic_json(self.ledger_path, self._ledger); self._finished = True

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        try:
            if not self._finished and self._ledger is not None:
                self.finish(elapsed_seconds=self.elapsed_seconds(), raw_bytes=0, terminal_status="FAILED_OR_ABORTED", evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC", diagnostic_reason="UNHANDLED_RECOVERY_CAPTURE_EXIT")
        finally:
            if self._handle is not None:
                fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN); self._handle.close(); self._handle = None
        return False
