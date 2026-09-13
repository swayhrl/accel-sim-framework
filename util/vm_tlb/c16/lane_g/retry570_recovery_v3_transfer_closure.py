#!/usr/bin/env python3
"""Close a copied Recovery-V3 model asset across local and remote endpoints.

The transport itself is intentionally outside this verifier.  Each endpoint
must independently enumerate a file name, size, and SHA256; this program only
accepts a one-to-one exact match and records the retained transfer evidence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file, valid_sha256


SCHEMA = "C16_G_RETRY570_RECOVERY_V3_DUAL_ENDPOINT_TRANSFER_V1"


def read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read endpoint transfer evidence: {path}") from exc
    if not isinstance(value, dict):
        raise ContractError("endpoint transfer evidence must be an object")
    return value


def rows(value: dict[str, Any], label: str) -> dict[str, tuple[int, str]]:
    result: dict[str, tuple[int, str]] = {}
    for row in value.get("payloads", []):
        try:
            name = Path(str(row.get("filename", Path(str(row["path"])).name))).name
            size, digest = int(row["size_bytes"]), str(row["sha256"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ContractError(f"{label} has malformed payload row") from exc
        if not name or name in result or size < 0 or not valid_sha256(digest):
            raise ContractError(f"{label} payload names/sizes/hashes are not a unique closed set")
        result[name] = (size, digest)
    if not result:
        raise ContractError(f"{label} contains no closed payloads")
    return result


def compare(source: dict[str, tuple[int, str]], remote: dict[str, tuple[int, str]]) -> None:
    if source.keys() != remote.keys():
        raise ContractError("remote payload set differs from local immutable payload set")
    for name, value in source.items():
        if remote[name] != value:
            raise ContractError(f"remote payload differs after transport: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--remote-manifest", type=Path, required=True)
    parser.add_argument("--remote-host", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ContractError("transfer closure refuses to overwrite a retained receipt")
    source, remote = read(args.source_receipt), read(args.remote_manifest)
    if source.get("all_payloads_size_sha256_closed") is not True:
        raise ContractError("source package did not close its payloads")
    source_rows, remote_rows = rows(source, "source"), rows(remote, "remote")
    compare(source_rows, remote_rows)
    atomic_json(args.output, {"schema_version": SCHEMA, "status": "DUAL_ENDPOINT_SIZE_SHA256_CLOSED",
                              "scientific_eligible": False, "remote_host": args.remote_host,
                              "source_receipt": {"path": str(args.source_receipt), "sha256": sha256_file(args.source_receipt)},
                              "remote_manifest": {"path": str(args.remote_manifest), "sha256": sha256_file(args.remote_manifest)},
                              "payload_count": len(source_rows), "payload_bytes": sum(size for size, _ in source_rows.values()),
                              "all_payloads_size_sha256_identical": True})
    print("PASS DUAL_ENDPOINT_SIZE_SHA256_CLOSED")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Recovery-V3 transfer closure: {exc}")
