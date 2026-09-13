#!/usr/bin/env python3
"""Enumerate one exact Recovery-V3 model directory for endpoint SHA closure.

This is deliberately transport-agnostic and never copies, moves, downloads,
or deletes an asset.  It emits the compact ``filename/size_bytes/sha256``
schema accepted by ``retry570_recovery_v3_transfer_closure.py``.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from c16_native_common import ContractError, atomic_json, sha256_file


SCHEMA = "C16_G_RETRY570_RECOVERY_V3_ASSET_ENDPOINT_MANIFEST_V1"


def rows(root: Path, output: Path) -> list[dict[str, object]]:
    if not root.is_dir():
        raise ContractError("asset root is absent")
    result: list[dict[str, object]] = []
    for path in sorted(item for item in root.iterdir() if item.is_file() and item.resolve() != output.resolve()):
        result.append({"filename": path.name, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    if not result or len({str(row["filename"]) for row in result}) != len(result):
        raise ContractError("asset root has no unique regular-file payload set")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--endpoint", required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ContractError("asset endpoint manifest refuses to overwrite retained evidence")
    payloads = rows(args.root, args.output)
    atomic_json(args.output, {
        "schema_version": SCHEMA,
        "status": "ASSET_ENDPOINT_SIZE_SHA256_CLOSED",
        "scientific_eligible": False,
        "endpoint": args.endpoint,
        "root": str(args.root),
        "payloads": payloads,
        "payload_count": len(payloads),
        "payload_bytes": sum(int(row["size_bytes"]) for row in payloads),
    })
    print("PASS ASSET_ENDPOINT_SIZE_SHA256_CLOSED")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Recovery-V3 asset endpoint manifest: {exc}")
