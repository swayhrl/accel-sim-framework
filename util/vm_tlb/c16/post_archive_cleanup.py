#!/usr/bin/env python3
"""Fail-closed archival and deletion guards for C16 old174 model cleanup."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path


class CleanupError(RuntimeError):
    pass


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def inventory(root: Path) -> list[dict[str, object]]:
    if not root.is_dir(): raise CleanupError(f"missing root: {root}")
    rows = []
    for current, _, names in os.walk(root):
        for name in sorted(names):
            path = Path(current) / name
            if path.is_file(): rows.append({"relative_path": path.relative_to(root).as_posix(), "size": path.stat().st_size, "sha256": sha(path)})
    return sorted(rows, key=lambda row: str(row["relative_path"]))


def write_tsv(path: Path, fields, rows) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def receipts_archive(source: Path, destination: Path) -> dict[str, object]:
    final, partial = destination, destination.with_name(destination.name + ".partial")
    if final.exists() or partial.exists(): raise CleanupError("receipt archive destination or .partial already exists")
    source_rows = inventory(source); partial.mkdir(parents=True)
    for row in source_rows:
        origin, target = source / str(row["relative_path"]), partial / str(row["relative_path"])
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(origin, target, follow_symlinks=False)
    destination_rows = inventory(partial)
    if source_rows != destination_rows: raise CleanupError("receipt archive inventory mismatch")
    manifest = partial / "TRANSFER_RECEIPTS_ARCHIVE_MANIFEST.tsv"
    write_tsv(manifest, ["relative_path", "size", "sha256", "classification", "source_path", "destination_path"], [{**row, "classification": "HISTORICAL_SNAPSHOT_ONLY_NOT_PIPELINE_RUN", "source_path": str(source / str(row["relative_path"])), "destination_path": str(final / str(row["relative_path"]))} for row in source_rows])
    receipt = partial / "TRANSFER_RECEIPTS_ARCHIVE_RECEIPT.json"
    receipt.write_text(json.dumps({"schema_version": 1, "source_root": str(source), "destination_root": str(final), "file_count": len(source_rows), "total_bytes": sum(int(row["size"]) for row in source_rows), "manifest_sha256": sha(manifest), "source_inventory_sha256": hashlib.sha256(json.dumps(source_rows, sort_keys=True).encode()).hexdigest(), "destination_inventory_sha256": hashlib.sha256(json.dumps(destination_rows, sort_keys=True).encode()).hexdigest(), "classification": "HISTORICAL_SNAPSHOT_ONLY_NOT_PIPELINE_RUN", "copy_semantics": "COPY_NOT_MOVE", "verification": "EXACT_REGULAR_FILE_SET_SIZE_SHA256_PASS", "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    final.parent.mkdir(parents=True, exist_ok=True); os.replace(partial, final)
    return {"destination": str(final), "manifest": str(final / manifest.name), "receipt": str(final / receipt.name), "file_count": len(source_rows), "total_bytes": sum(int(row["size"]) for row in source_rows)}


def predelete_recheck(status_tsv: Path) -> list[dict[str, str]]:
    rows = list(csv.DictReader(status_tsv.open(), delimiter="\t"))
    if len(rows) != 6 or any(row["status"] != "PASS" for row in rows): raise CleanupError("archive status table is not six PASS rows")
    for row in rows:
        directory, receipt = Path(row["destination_path"]), Path(row["receipt_path"])
        if not directory.is_dir() or not receipt.is_file() or sha(receipt) != row["receipt_sha256"]: raise CleanupError(f"receipt/path recheck failed: {row['model_slug']}")
        if directory.with_name(directory.name + ".partial").exists(): raise CleanupError(f"canonical .partial remains: {row['model_slug']}")
        expected = [{"relative_path": item["relative_path"], "size": int(item["size"]), "sha256": item["sha256"]}
                    for item in csv.DictReader((directory / "DESTINATION_INVENTORY.tsv").open(), delimiter="\t")]
        actual = inventory(directory)
        actual_payload = [row for row in actual if row["relative_path"] not in {"SOURCE_INVENTORY.tsv", "DESTINATION_INVENTORY.tsv", "MODEL_ARCHIVE_RECEIPT.json"}]
        if expected != actual_payload: raise CleanupError(f"canonical content rehash mismatch: {row['model_slug']}")
    snapshot = Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/historical_snapshots/old174_c16_recovery_v3")
    if not snapshot.is_dir() or not (snapshot / "SNAPSHOT_MANIFEST.tsv").is_file() or not (snapshot / "SNAPSHOT_SUMMARY.json").is_file(): raise CleanupError("historical non-model snapshot missing")
    return rows


def delete_authorized(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    results = []
    allowed_prefix = Path("/root/share/c16_recovery_v3/models")
    for row in rows:
        source = Path(row["source_path"])
        if source.parent.parent != allowed_prefix or not source.is_dir(): raise CleanupError(f"unauthorized/missing deletion target: {source}")
        bytes_before = sum(path.stat().st_size for current, _, names in os.walk(source) for path in (Path(current) / name for name in names) if path.is_file())
        shutil.rmtree(source)
        if source.exists(): raise CleanupError(f"deletion did not remove target: {source}")
        results.append({"model_slug": row["model_slug"], "source_path": str(source), "bytes_freed": bytes_before, "status": "DELETED_AFTER_CANONICAL_RECHECK_PASS"})
    return results
