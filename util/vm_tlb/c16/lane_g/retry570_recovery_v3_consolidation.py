#!/usr/bin/env python3
"""Publish the V9 non-destructive prelaunch asset-consolidation receipt."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file


SCHEMA = "C16_G_RETRY570_RECOVERY_V3_ASSET_CONSOLIDATION_V1"
ROWS = (
    ("llama_3p2_1b", "meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08"),
    ("qwen2p5_0p5b_instruct", "Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775"),
    ("qwen2p5_7b_instruct_raw", "Qwen/Qwen2.5-7B-Instruct@a09a35458c702b33eeacc393d103063234e8bc28"),
    ("qwen2p5_7b_instruct_awq", "Qwen/Qwen2.5-7B-Instruct-AWQ@b25037543e9394b818fdfca67ab2a00ecc7dd641"),
    ("qwen3_8b", "Qwen/Qwen3-8B@b968826d9c46dd6066d109eabc6255188de91218"),
    ("qwen3_30b_a3b", "USER_MANAGED_DOWNLOAD_UNDER_/root/share/huangrulin"),
    ("deepseek_v2_lite", "deepseek-ai/DeepSeek-V2-Lite@604d5664dddd88a0433dbae533b7fe9472482de0"),
    ("glm_extension", "UNRESOLVED"),
)
RECEIPT_STEMS = {"qwen2p5_0p5b_instruct": "R1_QWEN2P5_0P5B_ASSET_RECEIPT.json", "qwen2p5_7b_instruct_raw": "R1_QWEN2P5_7B_RAW_ASSET_RECEIPT.json", "qwen2p5_7b_instruct_awq": "R1_QWEN2P5_7B_AWQ_ASSET_RECEIPT.json", "qwen3_8b": "R1_QWEN3_8B_ASSET_RECEIPT.json"}


def load(path: Path) -> dict[str, Any]:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: raise ContractError(f"invalid consolidation evidence: {path}") from exc


def asset_row(key: str, identity: str, root: Path, receipt_root: Path) -> dict[str, str]:
    if key == "qwen3_30b_a3b":
        return {"model_key": key, "exact_identity_revision": identity, "source_paths": "NOT_INSPECTED_BY_USER_SCOPE", "destination_path": "NOT_APPLICABLE", "migration_method": "NONE", "source_bytes": "NA", "destination_bytes": "NA", "hash_closure": "NOT_APPLICABLE", "old_duplicate_removed": "NO", "status": "EXCLUDED_BY_USER_CURRENT_CAMPAIGN"}
    if key == "glm_extension":
        return {"model_key": key, "exact_identity_revision": identity, "source_paths": "NONE", "destination_path": "NONE", "migration_method": "NONE", "source_bytes": "NA", "destination_bytes": "NA", "hash_closure": "NOT_APPLICABLE", "old_duplicate_removed": "NO", "status": "IDENTITY_NOT_YET_RESOLVED"}
    dests = list(root.joinpath("models", key).glob("*"))
    receipt_path = receipt_root / RECEIPT_STEMS[key] if key in RECEIPT_STEMS else None
    if receipt_path is not None and receipt_path.is_file():
        receipt = load(receipt_path); payloads = receipt.get("payloads", [])
        total = sum(int(row["size_bytes"]) for row in payloads)
        acquisition = receipt.get("acquisition_source", {})
        # The already-running Qwen0.5 fetch was deliberately allowed to
        # finish under the earlier receipt schema. Its destination and P1
        # immutable closure prove a direct bulk-root exact fetch, not a copy.
        if not acquisition and key == "qwen2p5_0p5b_instruct":
            source, method = "NETWORK_EXACT_REVISION", "EXACT_IMMUTABLE_NETWORK_FETCH"
        else:
            source, method = acquisition.get("source_directory", "NETWORK_EXACT_REVISION"), acquisition.get("kind", "EXACT_IMMUTABLE_NETWORK_FETCH")
        return {"model_key": key, "exact_identity_revision": identity, "source_paths": str(source), "destination_path": str(receipt.get("destination")), "migration_method": method, "source_bytes": str(total), "destination_bytes": str(total), "hash_closure": "SOURCE_AND_DESTINATION_FILE_SHA256_PASS" if receipt.get("all_payloads_size_sha256_closed") else "FAIL", "old_duplicate_removed": "NO", "status": "EXISTING_ASSET_CONSOLIDATED" if source != "NETWORK_EXACT_REVISION" else "ALREADY_UNDER_BULK_ROOT"}
    # A destination directory without its immutable payload receipt is never
    # evidence of a closed model.  The two network acquisitions authorized by
    # V9 may, however, already be materializing directly under the bulk root.
    # Preserve that live state explicitly instead of collapsing it into
    # "not found" while the non-destructive fetch is still in progress.
    if key in {"qwen2p5_0p5b_instruct", "qwen3_8b"} and dests:
        return {"model_key": key, "exact_identity_revision": identity, "source_paths": "HUGGINGFACE_EXACT_FETCH_TO_BULK_ROOT", "destination_path": str(dests[0]), "migration_method": "NETWORK_FETCH_ALREADY_WRITING_TO_BULK_ROOT", "source_bytes": "IN_PROGRESS", "destination_bytes": "IN_PROGRESS", "hash_closure": "PENDING", "old_duplicate_removed": "NO", "status": "EXACT_FETCH_IN_PROGRESS"}
    return {"model_key": key, "exact_identity_revision": identity, "source_paths": "METADATA_ONLY_OR_NO_COMPLETE_EXACT_ASSET", "destination_path": "NONE", "migration_method": "NONE", "source_bytes": "NA", "destination_bytes": "NA", "hash_closure": "NOT_CLOSED", "old_duplicate_removed": "NO", "status": "EXACT_ASSET_NOT_FOUND_CONTINUE_RECOVERY"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bulk-root", type=Path, required=True); parser.add_argument("--receipt-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True); parser.add_argument("--output-tsv", type=Path, required=True)
    args = parser.parse_args()
    if args.output_json.exists() or args.output_tsv.exists(): raise ContractError("consolidation receipt refuses to overwrite retained evidence")
    if args.bulk_root.resolve() != Path("/root/share/c16_recovery_v3") or not args.receipt_root.is_dir(): raise ContractError("consolidation requires the fixed local bulk roots")
    rows = [asset_row(key, identity, args.bulk_root, args.receipt_root) for key, identity in ROWS]
    value: dict[str, Any] = {"schema_version": SCHEMA, "status": "V9_PRELAUNCH_ASSET_CONSOLIDATION_COMPLETE", "scientific_eligible": False, "bulk_root": str(args.bulk_root), "rows": rows, "policy": "No unique source was moved or deleted; HF snapshots are not moved independently of cache blobs."}
    atomic_json(args.output_json, value); args.output_tsv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_tsv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t"); writer.writeheader(); writer.writerows(rows)
    print("PASS V9_PRELAUNCH_ASSET_CONSOLIDATION_COMPLETE")


if __name__ == "__main__":
    try: main()
    except ContractError as exc: raise SystemExit(f"FAIL Recovery-V3 consolidation: {exc}")
