#!/usr/bin/env python3
"""Materialize a one-artifact Recovery-V3 remote/local SHA closure receipt.

Transport is deliberately out of scope for this helper.  The GPU endpoint
first writes a compact manifest after hashing its retained artifact; the
control host then copies the artifact and this helper independently verifies
the local size/SHA before recording the closed pair.  It never treats a local
file alone as proof of remote closure.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file, valid_sha256


SCHEMA = "C16_G_RECOVERY_V3_RAW_TRANSFER_RECEIPT_V1"


def read_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read remote artifact manifest: {path}") from exc
    if not isinstance(value, dict):
        raise ContractError("remote artifact manifest must be a JSON object")
    return value


def closed_remote_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    payload = manifest.get("payload")
    if not isinstance(payload, dict):
        raise ContractError("remote artifact manifest lacks one payload object")
    logical_path, size, digest = payload.get("logical_path"), payload.get("size_bytes"), payload.get("sha256")
    if not isinstance(logical_path, str) or not logical_path or not isinstance(size, int) or size < 0:
        raise ContractError("remote artifact payload path/size is malformed")
    if not isinstance(digest, str) or not valid_sha256(digest):
        raise ContractError("remote artifact payload SHA256 is malformed")
    return {"logical_path": logical_path, "size_bytes": size, "sha256": digest}


def close(remote: dict[str, Any], local_path: Path) -> dict[str, Any]:
    if not local_path.is_file():
        raise ContractError(f"local copied artifact is absent: {local_path}")
    local = {"path": str(local_path), "size_bytes": local_path.stat().st_size, "sha256": sha256_file(local_path)}
    if local["size_bytes"] != remote["size_bytes"] or local["sha256"] != remote["sha256"]:
        raise ContractError("remote/local artifact size or SHA256 differs")
    return local


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote-manifest", type=Path, required=True)
    parser.add_argument("--local-path", type=Path, required=True)
    parser.add_argument("--remote-host", required=True)
    parser.add_argument("--artifact-kind", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ContractError("raw transfer receipt refuses to overwrite retained evidence")
    remote_manifest = read_manifest(args.remote_manifest)
    remote = closed_remote_payload(remote_manifest)
    local = close(remote, args.local_path)
    atomic_json(args.output, {
        "schema_version": SCHEMA,
        "status": "REMOTE_LOCAL_SIZE_SHA256_CLOSED",
        "scientific_eligible": False,
        "artifact_kind": args.artifact_kind,
        "remote": {"host": args.remote_host, **remote, "manifest_path": str(args.remote_manifest), "manifest_sha256": sha256_file(args.remote_manifest)},
        "local": local,
        "size_sha256_identical": True,
        "remote_only_required_artifact_count_after_closure": 0,
        "transport_scope": "COPYBACK_EVIDENCE_ONLY_NO_MODEL_OR_GPU_EXECUTION",
    })
    print("PASS REMOTE_LOCAL_SIZE_SHA256_CLOSED")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Recovery-V3 raw transfer closure: {exc}")
