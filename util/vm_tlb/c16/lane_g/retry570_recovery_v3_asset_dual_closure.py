#!/usr/bin/env python3
"""Close two independently hashed Recovery-V3 model-asset endpoints."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file


SCHEMA = "C16_G_RETRY570_RECOVERY_V3_ASSET_DUAL_CLOSURE_V1"


def read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read endpoint manifest: {path}") from exc
    if not isinstance(value, dict) or value.get("status") != "ASSET_ENDPOINT_SIZE_SHA256_CLOSED":
        raise ContractError("endpoint manifest is not hash-closed")
    return value


def payloads(value: dict[str, Any]) -> dict[str, tuple[int, str]]:
    result: dict[str, tuple[int, str]] = {}
    for row in value.get("payloads", []):
        name, size, digest = row.get("filename"), row.get("size_bytes"), row.get("sha256")
        if not isinstance(name, str) or not name or not isinstance(size, int) or size < 0 or not isinstance(digest, str) or len(digest) != 64 or name in result:
            raise ContractError("endpoint payload set is malformed")
        result[name] = (size, digest)
    if not result:
        raise ContractError("endpoint payload set is empty")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-key", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--destination-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ContractError("asset dual closure refuses to overwrite retained evidence")
    source, destination = payloads(read(args.source_manifest)), payloads(read(args.destination_manifest))
    if source != destination:
        missing = sorted(source.keys() ^ destination.keys())
        raise ContractError(f"asset endpoint payloads differ: {missing[:3]}")
    atomic_json(args.output, {
        "schema_version": SCHEMA, "status": "SOURCE_AND_DESTINATION_FILE_SHA256_PASS",
        "scientific_eligible": False, "model_key": args.model_key,
        "identity": {"model_id": args.model_id, "revision": args.revision},
        "source_manifest": {"path": str(args.source_manifest), "sha256": sha256_file(args.source_manifest)},
        "destination_manifest": {"path": str(args.destination_manifest), "sha256": sha256_file(args.destination_manifest)},
        "payload_count": len(source), "payload_bytes": sum(size for size, _ in source.values()),
        "all_payloads_size_sha256_identical": True, "source_moved_or_deleted": False,
    })
    print("PASS SOURCE_AND_DESTINATION_FILE_SHA256_PASS")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Recovery-V3 asset dual closure: {exc}")
