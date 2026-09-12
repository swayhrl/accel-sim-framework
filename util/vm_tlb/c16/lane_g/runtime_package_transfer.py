#!/usr/bin/env python3
"""Materialize and re-verify an immutable C16 rolling package.

The tool is deliberately transport-agnostic: local materialization reads each
payload only from the package's fixed Git commit or declared absolute local
asset path, and the same manifest is then rechecked at the remote destination
after rsync.  It never downloads a model revision or repairs a mismatched
payload in place.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file


PACKAGE_FIELDS = (
    "artifact_id", "kind", "requiredness", "source_ref", "local_path",
    "destination_relpath", "size_bytes", "sha256", "verification_status",
    "transfer_action", "notes",
)
METADATA_NAMES = (
    "C16_GPU_PACKAGE_MANIFEST.tsv", "EXPECTED_HASHES.tsv", "TRANSFER_PLAN.md",
    "PACKAGE_IDENTITY.json",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def git_blob(commit: str, path: str) -> bytes:
    try:
        return subprocess.check_output(["git", "-C", str(repo_root()), "show", f"{commit}:{path}"])
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContractError(f"fixed Git payload unavailable: {commit}:{path}") from exc


def parse_rows(text: str, label: str) -> list[dict[str, str]]:
    reader = csv.DictReader(text.splitlines(), delimiter="\t")
    if tuple(reader.fieldnames or ()) != PACKAGE_FIELDS:
        raise ContractError(f"{label} does not use the immutable rolling-package schema")
    rows = list(reader)
    if not rows:
        raise ContractError(f"{label} has no payload rows")
    seen: set[str] = set()
    for row in rows:
        destination = row["destination_relpath"]
        if not destination or destination in seen or Path(destination).is_absolute() or ".." in Path(destination).parts:
            raise ContractError(f"{label} has an unsafe or duplicate destination: {destination!r}")
        seen.add(destination)
        if not row["sha256"] or len(row["sha256"]) != 64 or any(char not in "0123456789abcdef" for char in row["sha256"]):
            raise ContractError(f"{label} has an invalid SHA256 for {row['artifact_id']}")
        if row["size_bytes"] != "NA":
            try:
                if int(row["size_bytes"]) < 0:
                    raise ValueError
            except ValueError as exc:
                raise ContractError(f"{label} has invalid size for {row['artifact_id']}") from exc
    return rows


def atomic_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def payload_bytes(row: dict[str, str], package_commit: str) -> bytes:
    source_ref = row["source_ref"]
    local_path = row["local_path"]
    if source_ref.startswith("git:"):
        prefix, separator, path = source_ref[4:].partition(":")
        if not separator or not prefix or not path:
            raise ContractError(f"malformed Git source ref for {row['artifact_id']}")
        return git_blob(prefix, path)
    path = Path(local_path)
    if path.is_absolute():
        if not path.is_file():
            raise ContractError(f"declared local package payload is absent: {path}")
        return path.read_bytes()
    if not local_path or local_path == "NA":
        raise ContractError(f"package row has no materializable source: {row['artifact_id']}")
    return git_blob(package_commit, local_path)


def validate_payload(row: dict[str, str], path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ContractError(f"required package payload is absent: {path}")
    actual_size = path.stat().st_size
    actual_sha = sha256_file(path)
    expected_size = row["size_bytes"]
    if (expected_size != "NA" and actual_size != int(expected_size)) or actual_sha != row["sha256"]:
        raise ContractError(f"payload size/hash mismatch for {row['artifact_id']}")
    return {
        "artifact_id": row["artifact_id"],
        "destination_relpath": row["destination_relpath"],
        "size_bytes": actual_size,
        "sha256": actual_sha,
        "status": "PASS",
    }


def package_paths(package_dir: str) -> tuple[str, str]:
    base = package_dir.rstrip("/")
    return f"{base}/C16_GPU_PACKAGE_MANIFEST.tsv", f"{base}/PACKAGE_IDENTITY.json"


def validate_metadata(package_commit: str, package_dir: str, expected_manifest_sha: str) -> tuple[dict[str, Any], dict[str, bytes], list[dict[str, str]]]:
    manifest_path, identity_path = package_paths(package_dir)
    manifest_bytes = git_blob(package_commit, manifest_path)
    identity_bytes = git_blob(package_commit, identity_path)
    try:
        identity = json.loads(identity_bytes)
    except json.JSONDecodeError as exc:
        raise ContractError("rolling package identity JSON is invalid") from exc
    if hashlib.sha256(git_blob(package_commit, f"{package_dir}/C16_GPU_PACKAGE_{identity.get('package_id', '').removeprefix('C16_GPU_PACKAGE_')}_MANIFEST.json")).hexdigest() != expected_manifest_sha:
        raise ContractError("user-bound rolling package manifest SHA256 differs")
    if identity.get("package_manifest_sha256") != expected_manifest_sha:
        raise ContractError("package identity does not bind the expected manifest SHA256")
    rows = parse_rows(manifest_bytes.decode("utf-8"), "package manifest")
    metadata = {name: git_blob(package_commit, f"{package_dir}/{name}") for name in METADATA_NAMES}
    package_json_name = identity.get("package_manifest")
    if not isinstance(package_json_name, str) or not package_json_name:
        raise ContractError("package identity lacks package manifest name")
    package_json = json.loads(git_blob(package_commit, f"{package_dir}/{package_json_name}"))
    for item in package_json.get("payloads", []):
        name = item.get("path") if isinstance(item, dict) else None
        if not isinstance(name, str) or name not in metadata:
            raise ContractError("package JSON references unknown metadata payload")
        data = metadata[name]
        if item.get("size_bytes") != len(data) or item.get("sha256") != hashlib.sha256(data).hexdigest():
            raise ContractError(f"package metadata hash mismatch: {name}")
    return identity, metadata, rows


def materialize(args: argparse.Namespace) -> dict[str, Any]:
    identity, metadata, rows = validate_metadata(args.package_commit, args.package_dir, args.expected_package_manifest_sha256)
    for row in rows:
        destination = args.transfer_root / row["destination_relpath"]
        atomic_bytes(destination, payload_bytes(row, args.package_commit))
        validate_payload(row, destination)
    metadata_root = args.transfer_root / "package_metadata"
    for name, data in metadata.items():
        atomic_bytes(metadata_root / name, data)
    package_json_name = identity["package_manifest"]
    atomic_bytes(metadata_root / package_json_name, git_blob(args.package_commit, f"{args.package_dir}/{package_json_name}"))
    return {
        "schema_version": "C16_G_RUNTIME_PACKAGE_TRANSFER_V1",
        "stage_id": "C16-1.2",
        "execution_mode": "LOCAL_IMMUTABLE_PACKAGE_MATERIALIZATION",
        "scientific_eligible": False,
        "package_commit": args.package_commit,
        "package_id": identity["package_id"],
        "package_manifest_sha256": args.expected_package_manifest_sha256,
        "transfer_root": str(args.transfer_root),
        "rows": [validate_payload(row, args.transfer_root / row["destination_relpath"]) for row in rows],
        "status": "LOCAL_HASH_CLOSED_READY_FOR_RSYNC",
    }


def verify(args: argparse.Namespace) -> dict[str, Any]:
    manifest_path = args.transfer_root / "package_metadata" / "C16_GPU_PACKAGE_MANIFEST.tsv"
    identity_path = args.transfer_root / "package_metadata" / "PACKAGE_IDENTITY.json"
    package_json_paths = list((args.transfer_root / "package_metadata").glob("C16_GPU_PACKAGE_*_MANIFEST.json"))
    if len(package_json_paths) != 1 or not manifest_path.is_file() or not identity_path.is_file():
        raise ContractError("transferred rolling package metadata is incomplete")
    if sha256_file(package_json_paths[0]) != args.expected_package_manifest_sha256:
        raise ContractError("transferred rolling package manifest SHA256 differs")
    identity = json.loads(identity_path.read_text(encoding="utf-8"))
    if identity.get("package_manifest_sha256") != args.expected_package_manifest_sha256:
        raise ContractError("transferred package identity differs")
    rows = parse_rows(manifest_path.read_text(encoding="utf-8"), "transferred package manifest")
    return {
        "schema_version": "C16_G_RUNTIME_PACKAGE_TRANSFER_V1",
        "stage_id": "C16-1.2",
        "execution_mode": "REMOTE_TRANSFER_HASH_VERIFY",
        "scientific_eligible": False,
        "package_id": identity.get("package_id", "UNRESOLVED"),
        "package_manifest_sha256": args.expected_package_manifest_sha256,
        "transfer_root": str(args.transfer_root),
        "rows": [validate_payload(row, args.transfer_root / row["destination_relpath"]) for row in rows],
        "status": "TRANSFER_HASH_CLOSED",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transfer-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--expected-package-manifest-sha256", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--materialize", action="store_true")
    group.add_argument("--verify", action="store_true")
    parser.add_argument("--package-commit")
    parser.add_argument("--package-dir")
    args = parser.parse_args()
    if len(args.expected_package_manifest_sha256) != 64 or any(char not in "0123456789abcdef" for char in args.expected_package_manifest_sha256):
        parser.error("expected package manifest SHA256 must be lowercase hexadecimal")
    if args.materialize and (not args.package_commit or not args.package_dir):
        parser.error("--materialize requires --package-commit and --package-dir")
    receipt = materialize(args) if args.materialize else verify(args)
    atomic_json(args.receipt, receipt)
    print(f"PASS C16 immutable package {receipt['execution_mode']}: {receipt['package_id']} ({len(receipt['rows'])} rows)")


if __name__ == "__main__":
    try:
        main()
    except (ContractError, json.JSONDecodeError) as exc:
        print(f"FAIL C16 immutable package transfer: {exc}", file=sys.stderr)
        raise SystemExit(2)
