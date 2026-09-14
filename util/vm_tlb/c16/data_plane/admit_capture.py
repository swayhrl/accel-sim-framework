#!/usr/bin/env python3
"""Promote a verified partial capture to immutable raw storage and catalog it."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .catalog import catalog_entry_from_manifest, write_catalog_entry
    from .rebuild_catalog_snapshot import rebuild
    from .receiver_common import AdmissionError, load_json, rename_noreplace, sha256_file, utc_now
except ImportError:
    from catalog import catalog_entry_from_manifest, write_catalog_entry
    from rebuild_catalog_snapshot import rebuild
    from receiver_common import AdmissionError, load_json, rename_noreplace, sha256_file, utc_now


def admit(root: Path, verification_receipt: Path) -> dict:
    receipt = load_json(verification_receipt)
    if receipt.get("verification_status") != "PASS":
        raise AdmissionError("PASS verification receipt required")
    run_id = receipt.get("run_id")
    if not isinstance(run_id, str):
        raise AdmissionError("receipt missing RUN_ID")
    partial = root / "inbox" / f"{run_id}.partial"
    raw = root / "raw" / run_id
    manifest_path = partial / "RUN_MANIFEST.json"
    if not partial.is_dir() or raw.exists():
        raise AdmissionError("partial absent or immutable raw destination already exists")
    if sha256_file(manifest_path) != receipt.get("source_manifest_sha256"):
        raise AdmissionError("manifest changed after verification")
    manifest = load_json(manifest_path)
    rename_noreplace(partial, raw)
    try:
        entry = catalog_entry_from_manifest(manifest, raw, receipt["source_manifest_sha256"])
        catalog_path, catalog_sha = write_catalog_entry(root, entry)
        snapshot = rebuild(root)
    except Exception as exc:
        raise AdmissionError(f"raw promoted but catalog closure failed; do not ACK: {exc}") from exc
    return {
        "schema_version": 1,
        "run_id": run_id,
        "admission_status": "PASS",
        "admitted_at_utc": utc_now(),
        "destination_raw_path": str(raw),
        "source_manifest_sha256": receipt["source_manifest_sha256"],
        "file_count": receipt["file_count"],
        "total_bytes": receipt["total_bytes"],
        "catalog_entry_path": str(catalog_path),
        "catalog_entry_sha256": catalog_sha,
        "catalog_snapshot_path": str(snapshot),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--verification-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="new receipt path; never overwritten")
    args = parser.parse_args()
    try:
        result = admit(args.root, args.verification_receipt)
        if args.output.exists():
            raise AdmissionError(f"output exists: {args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"admission_status": "PASS", "output": str(args.output)}, sort_keys=True))
        return 0
    except (AdmissionError, OSError) as exc:
        print(json.dumps({"admission_status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
