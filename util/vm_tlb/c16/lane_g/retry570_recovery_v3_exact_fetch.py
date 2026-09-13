#!/usr/bin/env python3
"""Fetch one immutable Recovery-V3 model into the local bulk root.

This is deliberately a small asset-acquisition primitive, rather than a
runtime launcher.  It asks Hugging Face for the declared immutable revision,
requires the returned commit to be identical, materializes that exact tree
under the caller supplied bulk-root destination, and closes every published
file by size and SHA256 (including the API-provided LFS SHA256 where present).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file, valid_sha256


SCHEMA = "C16_G_RETRY570_RECOVERY_V3_EXACT_FETCH_V1"


def inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def expected_siblings(model_id: str, revision: str) -> tuple[str, list[dict[str, Any]]]:
    try:
        from huggingface_hub import HfApi
    except ImportError as exc:
        raise ContractError("huggingface_hub is required for an authorized exact fetch") from exc
    info = HfApi().model_info(model_id, revision=revision, files_metadata=True)
    if info.sha != revision:
        raise ContractError(f"Hub returned non-identical revision {info.sha!r}")
    files: list[dict[str, Any]] = []
    for sibling in info.siblings:
        if not sibling.rfilename or sibling.rfilename.endswith("/"):
            continue
        lfs = getattr(sibling, "lfs", None)
        lfs_sha = getattr(lfs, "sha256", None) if lfs is not None else None
        files.append({"filename": sibling.rfilename, "size_bytes": sibling.size,
                      "hub_lfs_sha256": lfs_sha})
    if not files:
        raise ContractError("immutable revision exposes no files")
    return info.sha, sorted(files, key=lambda row: row["filename"])


def close(destination: Path, files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    closed: list[dict[str, Any]] = []
    for row in files:
        path = destination / row["filename"]
        if not path.is_file():
            raise ContractError(f"immutable payload was not materialized: {row['filename']}")
        actual_size = path.stat().st_size
        if row["size_bytes"] is not None and actual_size != row["size_bytes"]:
            raise ContractError(f"immutable payload size differs: {row['filename']}")
        actual_sha = sha256_file(path)
        if row["hub_lfs_sha256"] is not None and actual_sha != row["hub_lfs_sha256"]:
            raise ContractError(f"immutable LFS SHA256 differs: {row['filename']}")
        closed.append({**row, "path": str(path), "sha256": actual_sha,
                       "size_bytes": actual_size})
    return closed


def fetch(model_id: str, revision: str, expected_config_sha256: str, destination: Path) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    returned_revision, files = expected_siblings(model_id, revision)
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise ContractError("huggingface_hub is required for an authorized exact fetch") from exc
    snapshot_download(repo_id=model_id, revision=revision, local_dir=str(destination))
    config = destination / "config.json"
    if not config.is_file() or sha256_file(config) != expected_config_sha256:
        raise ContractError("materialized exact revision does not have the declared config SHA256")
    return returned_revision, files, close(destination, files)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deployment", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--expected-config-sha256", required=True)
    parser.add_argument("--bulk-root", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--allow-network", action="store_true", required=True)
    args = parser.parse_args()
    if not valid_sha256(args.expected_config_sha256) or len(args.revision) != 40:
        raise ContractError("exact fetch requires SHA256 config and 40-hex immutable revision")
    if args.destination.exists() or args.receipt.exists():
        raise ContractError("exact fetch refuses to overwrite retained destination or receipt")
    if not inside(args.destination, args.bulk_root) or not inside(args.receipt, args.bulk_root):
        raise ContractError("Recovery-V3 asset payloads and receipts must be below the declared bulk root")
    args.destination.mkdir(parents=True)
    returned_revision, expected, closed = fetch(args.model_id, args.revision, args.expected_config_sha256, args.destination)
    receipt = {
        "schema_version": SCHEMA,
        "status": "EXACT_ASSET_FETCHED_AND_HASH_CLOSED",
        "scientific_eligible": False,
        "deployment": args.deployment,
        "identity": {"model_id": args.model_id, "requested_revision": args.revision,
                     "returned_revision": returned_revision,
                     "expected_config_sha256": args.expected_config_sha256},
        "acquisition_source": {"kind": "EXACT_IMMUTABLE_NETWORK_FETCH",
                                "authorized_after_no_local_exact_asset_receipt": True,
                                "hf_home": os.environ.get("HF_HOME", "UNSPECIFIED")},
        "destination": str(args.destination),
        "expected_payload_count": len(expected), "payloads": closed,
        "payload_bytes": sum(row["size_bytes"] for row in closed),
        "all_payloads_size_sha256_closed": True,
    }
    atomic_json(args.receipt, receipt)
    print("PASS EXACT_ASSET_FETCHED_AND_HASH_CLOSED")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL exact asset fetch: {exc}")
