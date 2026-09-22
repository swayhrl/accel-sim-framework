#!/usr/bin/env python3
"""Immutable per-run catalog entry support for C16 Pipeline V1."""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from .receiver_common import AdmissionError, sha256_file, write_json_new
except ImportError:
    from receiver_common import AdmissionError, sha256_file, write_json_new


def catalog_entry_from_manifest(manifest: dict[str, Any], raw_path: Path, manifest_sha256: str) -> dict[str, Any]:
    scenario = manifest["scenario"]
    capture = manifest["capture"]
    return {
        "schema_version": 1,
        "run_id": manifest["run_id"],
        "model": manifest["model"]["model_id"],
        "revision": manifest["model"]["revision"],
        "scenario": scenario["input_class"],
        "phase": scenario["phase"],
        "instrument": capture["instrument"],
        "target": capture["target"],
        "producer_host": manifest["producer"]["hostname"],
        "producer_commit": manifest["git"]["commit"],
        "model_binding": {"asset_receipt_sha256": manifest["model"]["asset_receipt_sha256"]},
        "input_binding": {
            "binding_id": manifest["input"]["binding_id"],
            "authority_status": manifest["input"]["authority_status"],
            "receipt_sha256": manifest["input"]["receipt_sha256"],
            "token_ids_sha256_or_semantic_hash": manifest["input"]["token_ids_sha256_or_semantic_hash"],
        },
        "raw_path": str(raw_path),
        "raw_bytes": sum(item["size_bytes"] for item in manifest["artifacts"]),
        "raw_manifest_sha256": manifest_sha256,
        "transfer_status": "TRANSFER_ACKED",
        "parse_status": "NOT_STARTED",
        "feature_status": "NOT_STARTED",
        "scientific_status": manifest["scientific_status"],
        "legacy": False,
    }


def write_catalog_entry(root: Path, entry: dict[str, Any], *, catalog_root: Path | None = None) -> tuple[Path, str]:
    path = (catalog_root if catalog_root is not None else root / "catalog") / "entries" / f"{entry['run_id']}.json"
    if path.exists():
        raise AdmissionError(f"immutable catalog entry already exists: {path}")
    write_json_new(path, entry)
    return path, sha256_file(path)
