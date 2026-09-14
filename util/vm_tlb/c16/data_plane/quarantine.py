#!/usr/bin/env python3
"""Fail-closed destination quarantine for unadmitted Pipeline V1 bundles."""
from __future__ import annotations

from pathlib import Path

try:
    from .receiver_common import AdmissionError, rename_noreplace, utc_now, write_json_new
except ImportError:
    from receiver_common import AdmissionError, rename_noreplace, utc_now, write_json_new


def quarantine_bundle(root: Path, bundle: Path, run_id: str, reason: str) -> Path:
    """Move a never-admitted bundle to a unique quarantine path; never overwrite."""
    if not bundle.exists() or bundle.is_symlink():
        raise AdmissionError(f"cannot quarantine absent/invalid bundle: {bundle}")
    destination = root / "quarantine" / f"{run_id}.{utc_now().replace(':', '').replace('-', '')}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    rename_noreplace(bundle, destination)
    write_json_new(destination / "QUARANTINE_RECEIPT.json", {
        "schema_version": 1,
        "run_id": run_id,
        "quarantined_at_utc": utc_now(),
        "reason": reason,
        "original_inbox_path": str(bundle),
        "quarantine_path": str(destination),
        "admitted": False,
    })
    return destination
