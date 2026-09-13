#!/usr/bin/env python3
"""Close a non-destructive Recovery-V3 copy from a retained package receipt."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file, valid_sha256


SCHEMA = "C16_G_RETRY570_RECOVERY_V3_EXISTING_ASSET_COPY_V1"


def read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"invalid retained source receipt: {path}") from exc
    if not isinstance(value, dict):
        raise ContractError("retained source receipt must be a JSON object")
    return value


def expected_model_rows(receipt: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in receipt.get("rows", []):
        artifact = str(row.get("artifact_id", ""))
        if ":" not in artifact or not artifact.split(":", 1)[0].startswith("c16_"):
            continue
        name, size, digest = Path(str(row.get("destination_relpath", ""))).name, row.get("size_bytes"), row.get("sha256")
        if row.get("status") != "PASS" or not name or not isinstance(size, int) or size < 0 or not isinstance(digest, str) or not valid_sha256(digest):
            raise ContractError("source package model row is not SHA closed")
        result.append({"filename": name, "size_bytes": size, "sha256": digest})
    if not result or len({row["filename"] for row in result}) != len(result):
        raise ContractError("source receipt lacks a unique closed model payload set")
    return sorted(result, key=lambda row: row["filename"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-key", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--source-directory", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--bulk-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ContractError("existing-asset receipt refuses to overwrite retained evidence")
    try:
        args.destination.resolve().relative_to(args.bulk_root.resolve() / "models" / args.model_key)
        destination_is_bound = args.destination.resolve().parent.name == args.model_key
    except ValueError:
        destination_is_bound = False
    if len(args.revision) != 40 or not destination_is_bound or args.bulk_root.resolve() != Path("/root/share/c16_recovery_v3"):
        raise ContractError("existing-asset copy must target its fixed Recovery-V3 bulk-root identity directory")
    if not args.destination.is_dir():
        raise ContractError("destination does not exist after non-destructive copy")
    source = read(args.source_receipt)
    rows = expected_model_rows(source)
    closed: list[dict[str, Any]] = []
    for row in rows:
        target = args.destination / row["filename"]
        if not target.is_file() or target.stat().st_size != row["size_bytes"] or sha256_file(target) != row["sha256"]:
            raise ContractError(f"destination size/SHA closure fails: {row['filename']}")
        closed.append({**row, "path": str(target)})
    atomic_json(args.output, {"schema_version": SCHEMA, "status": "EXISTING_ASSET_CONSOLIDATED_AND_HASH_CLOSED",
                              "scientific_eligible": False, "model_key": args.model_key,
                              "identity": {"model_id": args.model_id, "revision": args.revision},
                              "acquisition_source": {"kind": "NONDESTRUCTIVE_REMOTE_COPY", "source_directory": str(args.source_directory),
                                                     "source_receipt": str(args.source_receipt), "source_receipt_sha256": sha256_file(args.source_receipt),
                                                     "source_files_size_sha256_closed": True, "source_moved_or_deleted": False},
                              "destination": str(args.destination), "payloads": closed,
                              "payload_bytes": sum(row["size_bytes"] for row in closed),
                              "all_payloads_size_sha256_closed": True, "old_duplicate_removed": False})
    print("PASS EXISTING_ASSET_CONSOLIDATED_AND_HASH_CLOSED")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Recovery-V3 existing-asset copy: {exc}")
