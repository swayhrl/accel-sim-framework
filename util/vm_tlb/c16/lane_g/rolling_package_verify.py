#!/usr/bin/env python3
"""Verify an immutable Lane-A P0/P1 rolling package after remote transfer."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file, valid_sha256


FIELDS = (
    "artifact_id", "kind", "requiredness", "source_ref", "local_path", "destination_relpath",
    "size_bytes", "sha256", "verification_status", "transfer_action", "notes",
)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read rolling package manifest: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("rolling package manifest is not an object")
    return value


def load_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if tuple(reader.fieldnames or ()) != FIELDS:
                raise ContractError("rolling package TSV schema differs")
            rows = list(reader)
    except OSError as exc:
        raise ContractError(f"cannot read rolling package TSV: {exc}") from exc
    if not rows or any(not valid_sha256(row["sha256"]) or not row["destination_relpath"] for row in rows):
        raise ContractError("rolling package TSV has an invalid hash or destination")
    return rows


def verify_metadata(package_manifest: dict[str, Any], metadata_dir: Path) -> list[dict[str, Any]]:
    payloads = package_manifest.get("payloads")
    if not isinstance(payloads, list) or not payloads:
        raise ContractError("rolling package publication manifest has no payloads")
    seen: set[str] = set()
    records: list[dict[str, Any]] = []
    for payload in payloads:
        if not isinstance(payload, dict) or set(payload) != {"path", "sha256", "size_bytes"}:
            raise ContractError("rolling package publication payload schema differs")
        path_name = payload["path"]
        if not isinstance(path_name, str) or path_name in seen or Path(path_name).is_absolute() or ".." in Path(path_name).parts:
            raise ContractError("rolling package publication payload path is unsafe or duplicated")
        seen.add(path_name)
        path = metadata_dir / path_name
        if not path.is_file() or path.stat().st_size != payload["size_bytes"] or sha256_file(path) != payload["sha256"]:
            raise ContractError(f"rolling package metadata payload is not hash closed: {path_name}")
        records.append({"path": str(path), "sha256": payload["sha256"], "status": "PASS"})
    return records


def verify_rows(rows: list[dict[str, str]], root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        destination = row["destination_relpath"]
        if destination in seen or Path(destination).is_absolute() or ".." in Path(destination).parts:
            raise ContractError("rolling package destination is unsafe or duplicated")
        seen.add(destination)
        path = root / destination
        if not path.is_file():
            raise ContractError(f"rolling package payload is absent: {destination}")
        if row["size_bytes"] != "NA" and path.stat().st_size != int(row["size_bytes"]):
            raise ContractError(f"rolling package payload size differs: {destination}")
        actual = sha256_file(path)
        if actual != row["sha256"]:
            raise ContractError(f"rolling package payload hash differs: {destination}")
        records.append({"artifact_id": row["artifact_id"], "path": str(path), "sha256": actual, "status": "PASS"})
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--metadata-dir", type=Path, required=True)
    parser.add_argument("--package-manifest", type=Path, required=True)
    parser.add_argument("--expected-package-manifest-sha256", required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if not valid_sha256(args.expected_package_manifest_sha256):
        raise ContractError("expected rolling package manifest hash is invalid")
    if sha256_file(args.package_manifest) != args.expected_package_manifest_sha256:
        raise ContractError("immutable rolling package manifest hash differs")
    package_manifest = load_json(args.package_manifest)
    metadata = verify_metadata(package_manifest, args.metadata_dir)
    rows = verify_rows(load_rows(args.package_manifest.parent / "C16_GPU_PACKAGE_MANIFEST.tsv"), args.package_root)
    atomic_json(args.receipt, {
        "schema_version": "C16_G_ROLLING_PACKAGE_TRANSFER_RECEIPT_V1",
        "execution_mode": "TRANSFER_HASH_VERIFY",
        "scientific_eligible": False,
        "package_id": package_manifest.get("package_id"),
        "package_manifest_sha256": args.expected_package_manifest_sha256,
        "metadata_payloads": metadata,
        "payload_rows": rows,
        "status": "TRANSFER_HASH_CLOSED",
    })
    print(f"PASS C16 rolling package verifier: {args.receipt} ({len(rows)} payloads)")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 rolling package verifier: {exc}", file=sys.stderr)
        raise SystemExit(2)
