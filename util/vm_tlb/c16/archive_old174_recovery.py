#!/usr/bin/env python3
"""Copy-not-move, hash-closed old174 recovery archive builder (CPU/file I/O only)."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


MODELS = {
    "llama-3.2-1b": ("llama_3p2_1b", "4e20de362430cd3b72f300e6b0f18e50e7166e08"),
    "qwen2.5-0.5b-instruct": ("qwen2p5_0p5b_instruct", "7ae557604adf67be50417f59c2c2f167def9a775"),
    "qwen2.5-7b-instruct-raw": ("qwen2p5_7b_instruct_raw", "a09a35458c702b33eeacc393d103063234e8bc28"),
    "qwen2.5-7b-instruct-awq": ("qwen2p5_7b_instruct_awq", "b25037543e9394b818fdfca67ab2a00ecc7dd641"),
    "qwen3-8b": ("qwen3_8b", "b968826d9c46dd6066d109eabc6255188de91218"),
    "deepseek-v2-lite": ("deepseek_v2_lite", "604d5664dddd88a0433dbae533b7fe9472482de0"),
}


class ArchiveError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def regular_inventory(root: Path, exclude_models: bool = False) -> list[dict[str, object]]:
    if not root.is_dir():
        raise ArchiveError(f"missing directory: {root}")
    rows = []
    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        relative_dir = current_path.relative_to(root)
        if exclude_models and relative_dir == Path("."):
            dirs[:] = [item for item in dirs if item != "models"]
        for name in sorted(files):
            path = current_path / name
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            rows.append({"relative_path": relative, "size": path.stat().st_size, "sha256": digest(path)})
    return sorted(rows, key=lambda row: str(row["relative_path"]))


def inventory_hash(rows: list[dict[str, object]]) -> str:
    value = hashlib.sha256()
    for row in rows:
        value.update(f"{row['relative_path']}\t{row['size']}\t{row['sha256']}\n".encode())
    return value.hexdigest()


def total(rows: list[dict[str, object]]) -> int:
    return sum(int(row["size"]) for row in rows)


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def write_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def copy_inventory(source_root: Path, destination_root: Path, rows: list[dict[str, object]]) -> None:
    for row in rows:
        source, destination = source_root / str(row["relative_path"]), destination_root / str(row["relative_path"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination, follow_symlinks=False)


def assert_equal(source: list[dict[str, object]], destination: list[dict[str, object]], label: str) -> None:
    if source != destination:
        source_map = {str(row["relative_path"]): row for row in source}
        destination_map = {str(row["relative_path"]): row for row in destination}
        missing = sorted(set(source_map).difference(destination_map))[:5]
        extra = sorted(set(destination_map).difference(source_map))[:5]
        changed = [key for key in sorted(set(source_map).intersection(destination_map)) if source_map[key] != destination_map[key]][:5]
        raise ArchiveError(f"{label} inventory mismatch: missing={missing}, extra={extra}, changed={changed}")


def archive_model(source_root: Path, destination_root: Path, slug: str, source_name: str, revision: str, authority_commit: str) -> dict[str, object]:
    source = source_root / "models" / source_name / revision
    final = destination_root / "assets" / "models" / slug / revision
    partial = final.with_name(final.name + ".partial")
    if final.exists() or partial.exists():
        raise ArchiveError(f"refusing an existing model destination: {final} or {partial}")
    source_rows = regular_inventory(source)
    partial.mkdir(parents=True)
    copy_inventory(source, partial, source_rows)
    destination_rows = regular_inventory(partial)
    assert_equal(source_rows, destination_rows, f"model {slug}")
    source_inventory = partial / "SOURCE_INVENTORY.tsv"
    destination_inventory = partial / "DESTINATION_INVENTORY.tsv"
    write_tsv(source_inventory, ["relative_path", "size", "sha256"], source_rows)
    write_tsv(destination_inventory, ["relative_path", "size", "sha256"], destination_rows)
    receipt = partial / "MODEL_ARCHIVE_RECEIPT.json"
    write_json(receipt, {
        "schema_version": 1, "archive_class": "CANONICAL_ASSET", "model_slug": slug, "revision": revision,
        "source_path": str(source), "destination_path": str(final), "file_count": len(source_rows), "total_bytes": total(source_rows),
        "source_inventory_sha256": inventory_hash(source_rows), "destination_inventory_sha256": inventory_hash(destination_rows),
        "source_inventory_file_sha256": digest(source_inventory), "destination_inventory_file_sha256": digest(destination_inventory),
        "authority_commit": authority_commit, "copy_semantics": "COPY_NOT_MOVE", "verification": "EXACT_RELATIVE_PATH_SIZE_SHA256_PASS", "created_at_utc": now(),
    })
    final.parent.mkdir(parents=True, exist_ok=True)
    os.replace(partial, final)
    return {"model_slug": slug, "revision": revision, "source_path": str(source), "destination_path": str(final),
            "file_count": len(source_rows), "total_bytes": total(source_rows), "receipt_path": str(final / "MODEL_ARCHIVE_RECEIPT.json"),
            "receipt_sha256": digest(final / "MODEL_ARCHIVE_RECEIPT.json"), "status": "PASS"}


def archive_snapshot(source_root: Path, destination_root: Path, model_results: list[dict[str, object]], authority_commit: str) -> dict[str, object]:
    final = destination_root / "provenance" / "historical_snapshots" / "old174_c16_recovery_v3"
    partial = final.with_name(final.name + ".partial")
    if final.exists() or partial.exists():
        raise ArchiveError(f"refusing an existing snapshot destination: {final} or {partial}")
    source_rows = regular_inventory(source_root, exclude_models=True)
    partial.mkdir(parents=True)
    copy_inventory(source_root, partial, source_rows)
    destination_rows = regular_inventory(partial)
    assert_equal(source_rows, destination_rows, "non-model snapshot")
    manifest_rows = [{"relative_path": row["relative_path"], "size": row["size"], "sha256": row["sha256"],
        "historical_class": "HISTORICAL_SNAPSHOT_ONLY", "source_path": str(source_root / str(row["relative_path"])),
        "destination_path": str(final / str(row["relative_path"]))} for row in source_rows]
    manifest = partial / "SNAPSHOT_MANIFEST.tsv"
    write_tsv(manifest, ["relative_path", "size", "sha256", "historical_class", "source_path", "destination_path"], manifest_rows)
    redirects = partial / "MODEL_CANONICAL_REDIRECTS.tsv"
    redirect_rows = [{"historical_model_source_path": result["source_path"], "canonical_destination_path": result["destination_path"],
        "model_slug": result["model_slug"], "revision": result["revision"], "canonical_receipt_sha256": result["receipt_sha256"],
        "classification": "CANONICAL_ASSET_REDIRECT"} for result in model_results]
    write_tsv(redirects, ["historical_model_source_path", "canonical_destination_path", "model_slug", "revision", "canonical_receipt_sha256", "classification"], redirect_rows)
    summary = partial / "SNAPSHOT_SUMMARY.json"
    write_json(summary, {"schema_version": 1, "source_root": str(source_root), "destination_root": str(final), "file_count": len(source_rows),
        "total_bytes": total(source_rows), "manifest_sha256": digest(manifest), "source_inventory_sha256": inventory_hash(source_rows),
        "created_at_utc": now(), "source_git_authority": authority_commit, "historical_class": "HISTORICAL_SNAPSHOT_ONLY",
        "notes": "Complete non-model regular-file snapshot. Models are excluded and redirected only to independently verified canonical archives."})
    final.parent.mkdir(parents=True, exist_ok=True)
    os.replace(partial, final)
    return {"source_root": str(source_root), "destination_root": str(final), "file_count": len(source_rows), "total_bytes": total(source_rows),
            "manifest_path": str(final / "SNAPSHOT_MANIFEST.tsv"), "manifest_sha256": digest(final / "SNAPSHOT_MANIFEST.tsv"),
            "summary_path": str(final / "SNAPSHOT_SUMMARY.json"), "redirects_path": str(final / "MODEL_CANONICAL_REDIRECTS.tsv"), "status": "PASS"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--destination-root", type=Path, required=True)
    parser.add_argument("--authority-commit", required=True)
    parser.add_argument("--result-json", type=Path, required=True)
    args = parser.parse_args()
    try:
        results = [archive_model(args.source_root, args.destination_root, slug, source_name, revision, args.authority_commit)
                   for slug, (source_name, revision) in MODELS.items()]
        snapshot = archive_snapshot(args.source_root, args.destination_root, results, args.authority_commit)
        write_json(args.result_json, {"schema_version": 1, "status": "PASS", "models": results, "snapshot": snapshot, "created_at_utc": now()})
    except ArchiveError as error:
        parser.exit(2, f"archive failed closed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
