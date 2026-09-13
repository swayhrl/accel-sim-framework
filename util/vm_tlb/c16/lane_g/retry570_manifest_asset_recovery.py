#!/usr/bin/env python3
"""Recover one exact C16 model package from an immutable A manifest.

The downloader is deliberately manifest-driven: it obtains the expected rows
from the named Git commit, requires the commit's manifest SHA256, downloads
only those exact filenames at the exact revision, and closes every file by
size and SHA256.  It never chooses a model variant or revision itself.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file


SCHEMA = "C16_G_RETRY570_MANIFEST_ASSET_RECOVERY_V1"
IDENTITY = re.compile(r"^(?P<model>[^@;]+)@(?P<revision>[0-9a-f]{40});tokenizer@(?P<tokenizer>[0-9a-f]{40})$")


def git_bytes(commit: str, path: str) -> bytes:
    try:
        return subprocess.check_output(["git", "show", f"{commit}:{path}"])
    except subprocess.CalledProcessError as exc:
        raise ContractError("immutable package manifest is absent from the declared Git commit") from exc


def model_rows(commit: str, package_id: str, expected_manifest_sha256: str) -> tuple[dict[str, str], list[dict[str, Any]], str]:
    root = f"docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_a/packages/{package_id}"
    authority_path = f"{root}/{package_id}_MANIFEST.json"
    authority_bytes = git_bytes(commit, authority_path)
    if hashlib.sha256(authority_bytes).hexdigest() != expected_manifest_sha256:
        raise ContractError("immutable package manifest SHA256 differs from declared authority")
    try:
        authority = json.loads(authority_bytes)
        tsv = next(row for row in authority["payloads"] if row["path"] == "C16_GPU_PACKAGE_MANIFEST.tsv")
    except (KeyError, StopIteration, TypeError, json.JSONDecodeError) as exc:
        raise ContractError("immutable package authority lacks its model-payload TSV") from exc
    path = f"{root}/{tsv['path']}"
    content = git_bytes(commit, path)
    if len(content) != tsv.get("size_bytes") or hashlib.sha256(content).hexdigest() != tsv.get("sha256"):
        raise ContractError("immutable package payload TSV differs from its authority row")
    rows: list[dict[str, Any]] = []
    identities: set[str] = set()
    for line in content.decode("utf-8").splitlines():
        fields = line.split("\t")
        if len(fields) < 8 or fields[1] != "MODEL_ASSET":
            continue
        identities.add(fields[3])
        rows.append({"logical_id": fields[0], "filename": Path(fields[5]).name, "size_bytes": int(fields[6]), "sha256": fields[7]})
    if not rows or len(identities) != 1:
        raise ContractError("manifest has no unique exact model-asset identity")
    match = IDENTITY.fullmatch(next(iter(identities)))
    if match is None or match.group("revision") != match.group("tokenizer"):
        raise ContractError("manifest model/tokenizer identity is incomplete or inconsistent")
    if len({row["filename"] for row in rows}) != len(rows):
        raise ContractError("manifest model payload filenames are not unique")
    return match.groupdict(), rows, authority_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-commit", required=True); parser.add_argument("--package-id", required=True); parser.add_argument("--package-manifest-sha256", required=True)
    parser.add_argument("--destination", type=Path, required=True); parser.add_argument("--receipt", type=Path, required=True); parser.add_argument("--allow-network", action="store_true")
    args = parser.parse_args()
    if not args.allow_network:
        raise ContractError("network retrieval requires explicit --allow-network after identity closure")
    if args.destination.exists() or args.receipt.exists():
        raise ContractError("asset recovery refuses to overwrite a retained package/receipt")
    identity, rows, manifest_path = model_rows(args.package_commit, args.package_id, args.package_manifest_sha256)
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as exc:
        raise ContractError("hash-closed runtime lacks huggingface_hub for authorized asset retrieval") from exc
    args.destination.mkdir(parents=True)
    try:
        for row in rows:
            hf_hub_download(repo_id=identity["model"], filename=row["filename"], revision=identity["revision"], local_dir=str(args.destination), local_dir_use_symlinks=False)
        closed: list[dict[str, Any]] = []
        for row in rows:
            path = args.destination / row["filename"]
            if not path.is_file() or path.stat().st_size != row["size_bytes"] or sha256_file(path) != row["sha256"]:
                raise ContractError(f"downloaded payload fails immutable size/SHA closure: {row['filename']}")
            closed.append({**row, "path": str(path)})
    except Exception:
        # Retain the dedicated partial directory as diagnostic evidence; it is
        # never repurposed as a qualified asset package.
        raise
    atomic_json(args.receipt, {"schema_version": SCHEMA, "status": "HASH_CLOSED_PACKAGE_RECOVERED", "scientific_eligible": False, "network_retrieval_authorized_after_exact_identity_closure": True, "package": {"id": args.package_id, "commit": args.package_commit, "manifest_path": manifest_path, "manifest_sha256": args.package_manifest_sha256}, "identity": identity, "payloads": closed, "destination": str(args.destination), "all_payloads_size_sha256_closed": True})
    print("PASS HASH_CLOSED_PACKAGE_RECOVERED")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL manifest asset recovery: {exc}")
