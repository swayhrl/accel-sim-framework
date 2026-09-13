#!/usr/bin/env python3
"""Build and verify a SHA-closed Recovery V3 raw-tree copyback receipt.

``manifest`` runs at either endpoint and enumerates a retained tree without
changing payloads.  ``close`` runs on the local/control host after transport,
checks every named payload independently, and records that no required raw is
remote-only.  It intentionally does not delete the remote source.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, canonical_json, sha256_file


SCHEMA = "C16_G_RECOVERY_V3_TREE_TRANSFER_V1"


def payload_rows(root: Path, *, exclude: Path | None = None) -> list[dict[str, Any]]:
    if not root.is_dir():
        raise ContractError("tree root is absent")
    excluded = exclude.resolve() if exclude is not None else None
    rows = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if excluded is not None and path.resolve() == excluded:
            continue
        rows.append({"relative_path": str(path.relative_to(root)), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    if not rows:
        raise ContractError("retained tree has no payload files")
    return rows


def tree_sha(rows: list[dict[str, Any]]) -> str:
    import hashlib
    return hashlib.sha256(canonical_json(rows).encode("utf-8")).hexdigest()


def read_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError("cannot read tree transfer manifest") from exc
    if not isinstance(value, dict) or value.get("schema_version") != SCHEMA:
        raise ContractError("tree transfer manifest schema differs")
    rows = value.get("payloads")
    if not isinstance(rows, list) or not rows or value.get("payload_tree_sha256") != tree_sha(rows):
        raise ContractError("tree transfer manifest payload rows/hash differ")
    seen: set[str] = set()
    for row in rows:
        name, size, digest = row.get("relative_path"), row.get("size_bytes"), row.get("sha256")
        if (not isinstance(name, str) or not name or Path(name).is_absolute() or ".." in Path(name).parts
                or name in seen or not isinstance(size, int) or size < 0
                or not isinstance(digest, str) or len(digest) != 64):
            raise ContractError("tree transfer manifest row is malformed")
        seen.add(name)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("manifest")
    make.add_argument("--root", type=Path, required=True)
    make.add_argument("--output", type=Path, required=True)
    make.add_argument("--endpoint", required=True)
    close = sub.add_parser("close")
    close.add_argument("--remote-manifest", type=Path, required=True)
    close.add_argument("--local-root", type=Path, required=True)
    close.add_argument("--local-bulk-root", type=Path, required=True)
    close.add_argument("--remote-host", required=True)
    close.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "manifest":
        if args.output.exists():
            raise ContractError("tree manifest refuses to overwrite retained evidence")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        rows = payload_rows(args.root, exclude=args.output)
        atomic_json(args.output, {
            "schema_version": SCHEMA, "status": "ENDPOINT_TREE_SHA256_CLOSED",
            "endpoint": args.endpoint, "root": str(args.root), "payloads": rows,
            "payload_count": len(rows), "payload_bytes": sum(row["size_bytes"] for row in rows),
            "payload_tree_sha256": tree_sha(rows),
        })
        print("PASS ENDPOINT_TREE_SHA256_CLOSED")
        return
    if args.output.exists():
        raise ContractError("tree transfer receipt refuses to overwrite retained evidence")
    remote = read_manifest(args.remote_manifest)
    try:
        args.local_root.resolve().relative_to(args.local_bulk_root.resolve())
    except ValueError as exc:
        raise ContractError("local raw root is outside the required bulk root") from exc
    verified = []
    for row in remote["payloads"]:
        local = args.local_root / row["relative_path"]
        if not local.is_file() or local.stat().st_size != row["size_bytes"] or sha256_file(local) != row["sha256"]:
            raise ContractError(f"local copied payload differs: {row['relative_path']}")
        verified.append({"relative_path": row["relative_path"], "size_bytes": row["size_bytes"], "sha256": row["sha256"], "local_path": str(local)})
    atomic_json(args.output, {
        "schema_version": SCHEMA, "status": "REMOTE_LOCAL_TREE_SIZE_SHA256_CLOSED",
        "scientific_eligible": False, "remote_host": args.remote_host,
        "remote_manifest": {"path": str(args.remote_manifest), "sha256": sha256_file(args.remote_manifest)},
        "remote_root": remote["root"], "local_root": str(args.local_root),
        "local_bulk_root": str(args.local_bulk_root), "payloads": verified,
        "payload_count": len(verified), "payload_bytes": sum(row["size_bytes"] for row in verified),
        "payload_tree_sha256": remote["payload_tree_sha256"],
        "all_payloads_size_sha256_identical": True,
        "remote_only_required_artifact_count_after_closure": 0,
        "raw_payloads_committed": False,
    })
    print("PASS REMOTE_LOCAL_TREE_SIZE_SHA256_CLOSED")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Recovery-V3 tree transfer: {exc}")
