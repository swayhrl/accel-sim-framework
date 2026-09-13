#!/usr/bin/env python3
"""Materialize only immutable non-model package inputs for Recovery-V3.

Large model weights are deliberately not duplicated into a staging package:
they remain in their independently hash-closed bulk-root model directory.  A
fixed A-package supplies the accompanying exact input/scenario receipts and
is closed here at its declared commit and manifest SHA256.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file
from runtime_package_transfer import atomic_bytes, payload_bytes, validate_metadata, validate_payload


SCHEMA = "C16_G_RETRY570_RECOVERY_V3_PACKAGE_INPUTS_V1"


def read(path: Path) -> dict[str, Any]:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: raise ContractError(f"cannot read JSON receipt: {path}") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-commit", required=True); parser.add_argument("--package-dir", required=True)
    parser.add_argument("--package-manifest-sha256", required=True); parser.add_argument("--model-asset-receipt", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True); parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.output_root.exists() or args.receipt.exists():
        raise ContractError("package input materialization refuses to overwrite retained inputs or receipt")
    model = read(args.model_asset_receipt)
    if model.get("all_payloads_size_sha256_closed") is not True:
        raise ContractError("separate model asset has not completed immutable SHA256 closure")
    identity, metadata, package_rows = validate_metadata(args.package_commit, args.package_dir, args.package_manifest_sha256)
    model_identity = model.get("identity", {})
    if model_identity.get("revision") != identity.get("model_revision"):
        raise ContractError("asset receipt revision differs from fixed package identity")
    args.output_root.mkdir(parents=True)
    materialized: list[dict[str, Any]] = []
    for row in package_rows:
        if row["kind"] == "MODEL_ASSET":
            continue
        destination = args.output_root / row["destination_relpath"]
        atomic_bytes(destination, payload_bytes(row, args.package_commit))
        materialized.append(validate_payload(row, destination))
    metadata_root = args.output_root / "package_metadata"
    for name, data in metadata.items(): atomic_bytes(metadata_root / name, data)
    atomic_json(args.receipt, {"schema_version": SCHEMA, "status": "MODEL_AND_INPUT_CONTRACT_HASH_CLOSED",
                               "scientific_eligible": False, "package": {"id": identity["package_id"], "commit": args.package_commit,
                               "manifest_sha256": args.package_manifest_sha256, "package_dir": args.package_dir},
                               "model_asset_receipt": {"path": str(args.model_asset_receipt), "sha256": sha256_file(args.model_asset_receipt)},
                               "model_identity": model_identity, "input_root": str(args.output_root),
                               "non_model_payload_count": len(materialized), "non_model_payloads": materialized,
                               "model_weights_not_duplicated": True,
                               "all_model_and_non_model_inputs_hash_closed": True})
    print("PASS MODEL_AND_INPUT_CONTRACT_HASH_CLOSED")


if __name__ == "__main__":
    try: main()
    except ContractError as exc: raise SystemExit(f"FAIL Recovery-V3 package inputs: {exc}")
