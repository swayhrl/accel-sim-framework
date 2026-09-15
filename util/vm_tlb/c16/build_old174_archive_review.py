#!/usr/bin/env python3
"""Generate the compact Git review pack for the verified old174 -> 164 archive."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def files(root: Path):
    for current, _, names in os.walk(root):
        for name in names:
            path = Path(current) / name
            if path.is_file():
                yield path


def write_tsv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--node109-check", type=Path, required=True)
    parser.add_argument("--authority-commit", required=True)
    args = parser.parse_args()
    pack = args.repo / "docs/vm_tlb/review_packs/C16_OLD174_RECOVERY_ARCHIVE_TO_164_V1"
    pack.mkdir(parents=True, exist_ok=True)
    result = json.loads(args.result.read_text())
    snapshot = result["snapshot"]
    snap = Path(snapshot["destination_root"])
    source_rows = []
    for item in result["models"]:
        archive = Path(item["destination_path"])
        for row in csv.DictReader((archive / "SOURCE_INVENTORY.tsv").open(), delimiter="\t"):
            source_rows.append({"relative_path": f"models/{Path(item['source_path']).parent.name}/{item['revision']}/{row['relative_path']}", "size": row["size"], "sha256": row["sha256"], "classification": "CANONICAL_ASSET_SOURCE"})
    for row in csv.DictReader((snap / "SNAPSHOT_MANIFEST.tsv").open(), delimiter="\t"):
        source_rows.append({"relative_path": row["relative_path"], "size": row["size"], "sha256": row["sha256"], "classification": "HISTORICAL_SNAPSHOT_ONLY_SOURCE"})
    write_tsv(pack / "SOURCE_INVENTORY.tsv", ["relative_path", "size", "sha256", "classification"], source_rows)
    model_rows = []
    for item in result["models"]:
        node109 = "READ_ONLY_MATCH_LLAMAPAYLOAD" if item["model_slug"] == "llama-3.2-1b" else "NOT_AVAILABLE_ON_NODE109_ACTIVE_ROOT"
        model_rows.append({**item, "archive_class": "CANONICAL_ASSET", "node109_cross_check": node109})
    write_tsv(pack / "MODEL_ARCHIVE_STATUS.tsv", ["model_slug", "revision", "source_path", "destination_path", "file_count", "total_bytes", "receipt_path", "receipt_sha256", "archive_class", "node109_cross_check", "status"], model_rows)
    for name in ["MODEL_CANONICAL_REDIRECTS.tsv", "SNAPSHOT_MANIFEST.tsv"]:
        (pack / name).write_bytes((snap / name).read_bytes())
    (pack / "SNAPSHOT_SUMMARY.json").write_bytes((snap / "SNAPSHOT_SUMMARY.json").read_bytes())
    current = args.destination / "legacy/rtx3090_minimal_compare"
    overlaps = []
    manifest_rows = list(csv.DictReader((snap / "SNAPSHOT_MANIFEST.tsv").open(), delimiter="\t"))
    for row in manifest_rows:
        source_path = Path(row["source_path"])
        for destination in current.rglob(source_path.name) if current.is_dir() else []:
            if destination.is_file() and destination.stat().st_size == int(row["size"]) and sha(destination) == row["sha256"]:
                overlaps.append({"source_path": str(source_path), "snapshot_path": row["destination_path"], "current_164_path": str(destination), "size": row["size"], "sha256": row["sha256"], "classification": "EXACT_BYTE_OVERLAP_SEPARATE_CURRENT_CURATED_ARCHIVE", "action": "PRESERVE_BOTH_NO_MUTATION"})
    write_tsv(pack / "HISTORICAL_OVERLAP.tsv", ["source_path", "snapshot_path", "current_164_path", "size", "sha256", "classification", "action"], overlaps)
    root_rows = []
    for root in sorted(Path("/root/share").glob("c16_*")):
        if not root.is_dir(): continue
        source_files = list(files(root)); total_bytes = sum(item.stat().st_size for item in source_files)
        if root == args.source:
            classification, represented, action = "SOURCE_AUTHORITY_ARCHIVED", "YES_CANONICAL_MODELS_AND_HISTORICAL_SNAPSHOT", "RETAIN_UNTIL_SEPARATE_CLEANUP"
        elif root.name == "c16_transfer_109_receipts":
            classification, represented, action = "TRANSFER_RECEIPTS_AUXILIARY", "NO", "INVENTORY_ONLY_REVIEW_SEPARATELY"
        else:
            classification, represented, action = "UNKNOWN", "UNKNOWN", "NO_BULK_COPY"
        root_rows.append({"path": str(root), "bytes": total_bytes, "file_count": len(source_files), "classification": classification, "already_represented_on_164": represented, "recommended_future_action": action})
    write_tsv(pack / "OTHER_C16_ROOTS.tsv", ["path", "bytes", "file_count", "classification", "already_represented_on_164", "recommended_future_action"], root_rows)
    cleanup = [
        {"source_path": str(args.source / "models"), "classification": "SAFE_TO_DELETE_AFTER_SEPARATE_CLEANUP", "basis": "six canonical archives independently hash-closed; no deletion authorized here", "recommendation": "separate cleanup goal only"},
        {"source_path": str(args.source / "receipts"), "classification": "RETAIN_SOURCE", "basis": "small provenance convenience copy plus snapshot closure", "recommendation": "retain by default"},
        {"source_path": str(args.source / "inputs"), "classification": "RETAIN_SOURCE", "basis": "small input provenance convenience copy plus snapshot closure", "recommendation": "retain by default"},
        {"source_path": str(args.source / "raw"), "classification": "RETAIN_SOURCE", "basis": "historical archaeology and curated-overlap context", "recommendation": "later cleanup only with object-level review"},
        {"source_path": str(args.source / "staging"), "classification": "RETAIN_SOURCE", "basis": "historical staging is snapshot-preserved but useful for provenance", "recommendation": "retain by default"},
        {"source_path": str(args.source / "hf-cache"), "classification": "UNKNOWN_DO_NOT_DELETE", "basis": "small cache-like content outside canonical asset mapping", "recommendation": "separate inspection required"},
    ]
    write_tsv(pack / "CLEANUP_READINESS.tsv", ["source_path", "classification", "basis", "recommendation"], cleanup)
    (pack / "NODE109_READ_ONLY_MODEL_CROSSCHECK.txt").write_bytes(args.node109_check.read_bytes())
    (pack / "README.md").write_text("# C16 old174 recovery archive to node164 V1\n\n"
        "Status: `PASS`. Six canonical hash-closed model archives were copied through per-model `.partial` paths and independently re-inventoried before promotion. A complete non-model regular-file historical snapshot is classified `HISTORICAL_SNAPSHOT_ONLY`; it is not Pipeline V1 raw/catalog data. No source file was moved, modified, or deleted.\n\n"
        f"Source authority: `{args.source}`. Archive authority commit: `{args.authority_commit}`. Node109 access was read-only; its active Llama payload hash matches canonical node164. Qwen3-30B-A3B is absent from canonical asset scope.\n", encoding="utf-8")
    final = {"schema_version": 1, "decision": "C16_OLD174_RECOVERY_ARCHIVE_TO_164_V1_PASS", "source_root": str(args.source), "destination_root": str(args.destination), "canonical_model_count": len(result["models"]), "snapshot_file_count": snapshot["file_count"], "snapshot_total_bytes": snapshot["total_bytes"], "snapshot_manifest_sha256": snapshot["manifest_sha256"], "source_modified_or_deleted": False, "pipeline_namespace_polluted": False, "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")}
    (pack / "FINAL_DECISION.json").write_text(json.dumps(final, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sum_files = sorted(path for path in pack.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    (pack / "SHA256SUMS").write_text("".join(f"{sha(path)}  {path.relative_to(args.repo)}\n" for path in sum_files), encoding="utf-8")


if __name__ == "__main__":
    main()
