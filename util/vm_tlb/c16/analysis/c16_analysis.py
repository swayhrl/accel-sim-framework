#!/usr/bin/env python3
"""Hash-bound, CPU-only parser and fingerprint workflow for C16 artifacts.

The module deliberately uses JSONL/JSON/TSV and the standard library.  It has no
CUDA, NVBit, NCU, tokenizer, or model-runtime dependency.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "C16_ANALYSIS_V1"
OBJECT_CLASSES = {"WEIGHT", "QUANT_METADATA", "KV_CACHE", "ACTIVATION", "UNKNOWN_RUNTIME"}
OBJECT_PRIORITY = {"WEIGHT": 0, "QUANT_METADATA": 1, "KV_CACHE": 2, "ACTIVATION": 3}


class AnalysisError(RuntimeError):
    """A source is incomplete, malformed, or unsupported; callers must fail closed."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def mask_lane_count(mask: Any) -> int | None:
    if mask is None:
        return None
    if not isinstance(mask, int) or mask < 0:
        raise AnalysisError("active_mask must be a non-negative integer or null")
    return mask.bit_count()


def _range_buckets(address: int, width: int, bucket: int) -> range:
    if address < 0 or width <= 0:
        raise AnalysisError("gpu_va must be non-negative and width_bytes positive")
    return range(address // bucket, (address + width - 1) // bucket + 1)


def normalize_record(raw: dict[str, Any], source_id: str) -> dict[str, Any]:
    if raw.get("record_kind") != "LANE_EVENT":
        raise AnalysisError("only LANE_EVENT records are accepted by Route-B parser")
    if raw.get("raw_schema") != "C16_ROUTE_B_LANE_EVENT_V1":
        raise AnalysisError("unsupported or absent Route-B raw_schema")
    access_kind = raw.get("access_kind")
    if access_kind not in {"READ", "WRITE", "ATOMIC"}:
        raise AnalysisError(f"unsupported access_kind: {access_kind!r}")
    address, width = raw.get("gpu_va"), raw.get("width_bytes")
    if not isinstance(address, int) or not isinstance(width, int):
        raise AnalysisError("gpu_va and width_bytes must be integers")
    _range_buckets(address, width, 128)
    return {
        "source_id": source_id,
        "launch_id": raw.get("kernel_launch_id"),
        "phase": raw.get("phase"),
        "decode_step": raw.get("decode_step"),
        "function": raw.get("function_mangled_name"),
        "static_instruction_identity": raw.get("static_index"),
        "pc_offset": raw.get("instruction_offset"),
        "opcode": raw.get("opcode"),
        "memory_space": raw.get("memory_space"),
        "is_load": access_kind == "READ",
        "is_store": access_kind == "WRITE",
        "is_atomic": access_kind == "ATOMIC",
        "width_bytes": width,
        "active_mask": raw.get("active_mask"),
        "active_lane_count": mask_lane_count(raw.get("active_mask")),
        "lane": raw.get("lane_id"),
        "address": address,
        "object_class": "UNKNOWN_RUNTIME",
        "observed_event_sequence": raw.get("observed_event_sequence"),
        "sequence_label": raw.get("sequence_label"),
    }


def object_join(record: dict[str, Any], ranges: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Attribute a record by range, with explicit deterministic alias priority."""
    address = record["address"]
    matches = []
    for item in ranges:
        cls = item.get("object_class")
        if cls not in OBJECT_CLASSES or cls == "UNKNOWN_RUNTIME":
            raise AnalysisError("object range must use a evidenced non-UNKNOWN object class")
        start, end = item.get("start"), item.get("end")
        if not isinstance(start, int) or not isinstance(end, int) or end <= start:
            raise AnalysisError("object range requires integer half-open start/end")
        if start <= address < end:
            matches.append(item)
    if not matches:
        return {**record, "object_class": "UNKNOWN_RUNTIME", "object_id": None}
    chosen = sorted(matches, key=lambda x: (x.get("priority", OBJECT_PRIORITY[x["object_class"]]), x.get("object_id", "")))[0]
    return {**record, "object_class": chosen["object_class"], "object_id": chosen.get("object_id")}


def fingerprint(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    pages4k, pages64k, lines, vas = set(), set(), set(), set()
    widths, accesses, active_lanes, objects = Counter(), Counter(), Counter(), Counter()
    launches: dict[str, int] = defaultdict(int)
    lane_events = 0
    for record in records:
        lane_events += 1
        address, width = record["address"], record["width_bytes"]
        vas.add(address)
        pages4k.update(_range_buckets(address, width, 4096))
        pages64k.update(_range_buckets(address, width, 65536))
        lines.update(_range_buckets(address, width, 128))
        widths[str(width)] += 1
        accesses["ATOMIC" if record["is_atomic"] else "WRITE" if record["is_store"] else "READ"] += 1
        objects[record.get("object_class", "UNKNOWN_RUNTIME")] += 1
        if record.get("active_lane_count") is not None:
            active_lanes[str(record["active_lane_count"])] += 1
        launches[str(record.get("launch_id"))] += 1
    if not lane_events:
        raise AnalysisError("empty input is not analyzable")
    return {
        "schema_version": SCHEMA,
        "lane_events": lane_events,
        "access_counts": dict(sorted(accesses.items())),
        "width_bytes_counts": dict(sorted(widths.items(), key=lambda x: int(x[0]))),
        "unique_exact_va": len(vas),
        "unique_128b_lines": len(lines),
        "unique_4k_pages": len(pages4k),
        "unique_64k_pages": len(pages64k),
        "unique_2m_pages": len({address // (2 * 1024 * 1024) for address in vas}),
        "active_lane_distribution": dict(sorted(active_lanes.items(), key=lambda x: int(x[0]))),
        "object_attribution": dict(sorted(objects.items())),
        "per_launch_footprint": dict(sorted(launches.items())),
        "reuse_order_label": "OBSERVED_CALLBACK_ORDER_ONLY",
    }


def parse_route_b(source: Path, source_id: str, parsed_path: Path) -> dict[str, Any]:
    """Stream raw JSONL to normalized JSONL and return its exact fingerprint."""
    if not source.is_file() or source.stat().st_size == 0:
        raise AnalysisError("input is missing, empty, or not a regular file")
    parsed_path.parent.mkdir(parents=True, exist_ok=True)
    def records() -> Iterable[dict[str, Any]]:
        lane_events = 0
        terminal_seen = False
        with source.open("r", encoding="utf-8") as input_handle, parsed_path.open("w", encoding="utf-8") as output_handle:
            for line_number, line in enumerate(input_handle, 1):
                if not line.strip():
                    raise AnalysisError(f"partial/blank JSONL record at line {line_number}")
                try:
                    raw = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise AnalysisError(f"invalid JSON at line {line_number}") from exc
                if not isinstance(raw, dict):
                    raise AnalysisError(f"JSON record {line_number} is not an object")
                if raw.get("record_kind") == "TERMINAL":
                    if terminal_seen or raw.get("terminal_status") != "COMPLETE":
                        raise AnalysisError("invalid Route-B terminal record")
                    if raw.get("event_count") != lane_events or raw.get("overflow_count") != 0 or raw.get("drop_count") != 0:
                        raise AnalysisError("Route-B terminal does not close the parsed event stream")
                    terminal_seen = True
                    continue
                if terminal_seen:
                    raise AnalysisError("data record found after Route-B terminal")
                normalized = normalize_record(raw, source_id)
                output_handle.write(json.dumps(normalized, sort_keys=True, separators=(",", ":")) + "\n")
                lane_events += 1
                yield normalized
    return fingerprint(records())


def write_receipt(source_id: str, source: Path, outputs: list[Path], receipt_path: Path, parser_commit: str, argv: list[str]) -> None:
    dump_json(receipt_path, {
        "schema_version": SCHEMA,
        "source_id": source_id,
        "source_path": str(source),
        "source_sha256": sha256(source),
        "parser_git_commit": parser_commit,
        "parser_argv": argv,
        "created_at_utc": utc_now(),
        "outputs": [{"path": str(p), "size_bytes": p.stat().st_size, "sha256": sha256(p)} for p in outputs],
    })


def normalize_ncu_csv(source: Path, source_id: str, output: Path, classification: str, ncu_version: str) -> int:
    if classification not in {"N1_QUALIFICATION", "RTX4080_R5"}:
        raise AnalysisError("NCU classification must be N1_QUALIFICATION or RTX4080_R5")
    if not source.is_file() or source.stat().st_size == 0:
        raise AnalysisError("NCU CSV is missing or empty")
    output.parent.mkdir(parents=True, exist_ok=True)
    with source.open("r", encoding="utf-8-sig", newline="") as input_handle:
        rows = list(csv.DictReader(input_handle))
    if not rows:
        raise AnalysisError("NCU CSV has no data rows")
    forbidden = {"report", "source"}
    with output.open("w", encoding="utf-8") as handle:
        for row_index, row in enumerate(rows):
            kernel = row.get("Kernel Name") or row.get("launch__kernel_name") or "UNKNOWN"
            for metric, value in sorted(row.items()):
                if metric in forbidden or value in (None, "") or metric in {"ID", "Kernel Name", "launch__kernel_name"}:
                    continue
                handle.write(json.dumps({"source_id": source_id, "classification": classification,
                    "ncu_version": ncu_version, "raw_report_sha256": sha256(source), "kernel_identity": kernel,
                    "metric_name": metric, "value": value, "unit": None, "row": row_index}, sort_keys=True) + "\n")
    return len(rows)


def verify_manifest(raw_dir: Path, manifest_sha: str) -> dict[str, Any]:
    manifest = raw_dir / "RUN_MANIFEST.json"
    if not manifest.is_file() or sha256(manifest) != manifest_sha:
        raise AnalysisError("RUN_MANIFEST hash mismatch")
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    for artifact in payload.get("artifacts", []):
        path = raw_dir / artifact["relative_path"]
        if not path.is_file() or path.stat().st_size != artifact["size_bytes"] or sha256(path) != artifact["sha256"]:
            raise AnalysisError(f"raw artifact verification failed: {artifact.get('relative_path')}")
    return payload


def rebuild_indexes(root: Path) -> dict[str, Path]:
    """Deterministically rebuild small discovery indexes from hash-closed receipts."""
    feature_root = root / "derived" / "features"
    rows = []
    for receipt_path in sorted(feature_root.glob("*/DERIVED_RECEIPT.json")):
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        outputs = {Path(item["path"]).name: item for item in receipt["outputs"]}
        rows.append({"source_id": receipt["source_id"], "source_sha256": receipt["source_sha256"],
            "parser_git_commit": receipt["parser_git_commit"], "receipt_path": str(receipt_path),
            "receipt_sha256": sha256(receipt_path), "parsed_path": outputs.get("memory_access.jsonl", {}).get("path", ""),
            "parsed_sha256": outputs.get("memory_access.jsonl", {}).get("sha256", ""),
            "feature_path": outputs.get("fingerprint.json", {}).get("path", ""),
            "feature_sha256": outputs.get("fingerprint.json", {}).get("sha256", "")})
    parse_index, feature_index = root / "derived" / "PARSE_INDEX.tsv", root / "derived" / "FEATURE_INDEX.tsv"
    parse_index.parent.mkdir(parents=True, exist_ok=True)
    with parse_index.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source_id", "source_sha256", "parser_git_commit", "parsed_path", "parsed_sha256", "receipt_path", "receipt_sha256"], delimiter="\t")
        writer.writeheader(); writer.writerows([{key: row[key] for key in writer.fieldnames} for row in rows])
    with feature_index.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source_id", "source_sha256", "feature_path", "feature_sha256", "receipt_path", "receipt_sha256"], delimiter="\t")
        writer.writeheader(); writer.writerows([{key: row[key] for key in writer.fieldnames} for row in rows])
    return {"parse_index": parse_index, "feature_index": feature_index}


def analyze_catalog_run(root: Path, run_id: str, raw_rel: str, parser_commit: str, argv: list[str]) -> dict[str, Any]:
    entry_path = root / "catalog" / "entries" / f"{run_id}.json"
    if not entry_path.is_file():
        raise AnalysisError("catalog entry not found")
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    raw_dir = Path(entry["raw_path"])
    manifest = verify_manifest(raw_dir, entry["raw_manifest_sha256"])
    raw = raw_dir / raw_rel
    out_base = root / "derived"
    parsed = out_base / "parsed" / run_id / "memory_access.jsonl"
    features = out_base / "features" / run_id / "fingerprint.json"
    stats = parse_route_b(raw, run_id, parsed)
    dump_json(features, {**stats, "source_run_id": run_id, "raw_manifest_sha256": entry["raw_manifest_sha256"], "scientific_status": entry["scientific_status"]})
    receipt = out_base / "features" / run_id / "DERIVED_RECEIPT.json"
    write_receipt(run_id, raw, [parsed, features], receipt, parser_commit, argv)
    indexes = rebuild_indexes(root)
    return {"run_id": run_id, "manifest_schema": manifest.get("schema_version"), "receipt": str(receipt), "indexes": {key: str(value) for key, value in indexes.items()}, **stats}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    route = commands.add_parser("route-b")
    route.add_argument("--input", type=Path, required=True); route.add_argument("--source-id", required=True)
    route.add_argument("--root", type=Path, required=True); route.add_argument("--parser-commit", required=True)
    ncu = commands.add_parser("ncu-csv")
    ncu.add_argument("--input", type=Path, required=True); ncu.add_argument("--source-id", required=True)
    ncu.add_argument("--output", type=Path, required=True); ncu.add_argument("--classification", required=True); ncu.add_argument("--ncu-version", required=True)
    index = commands.add_parser("rebuild-index")
    index.add_argument("--root", type=Path, required=True)
    run = commands.add_parser("analyze-run")
    run.add_argument("--root", type=Path, required=True); run.add_argument("--run-id", required=True); run.add_argument("--raw-rel", required=True); run.add_argument("--parser-commit", required=True)
    args = parser.parse_args()
    try:
        if args.command == "route-b":
            parsed = args.root / "derived" / "parsed" / args.source_id / "memory_access.jsonl"
            features = args.root / "derived" / "features" / args.source_id / "fingerprint.json"
            stats = parse_route_b(args.input, args.source_id, parsed)
            dump_json(features, stats)
            receipt = args.root / "derived" / "features" / args.source_id / "DERIVED_RECEIPT.json"
            write_receipt(args.source_id, args.input, [parsed, features], receipt, args.parser_commit, os.sys.argv)
            indexes = rebuild_indexes(args.root)
            print(json.dumps({"receipt": str(receipt), "indexes": {key: str(value) for key, value in indexes.items()}, **stats}, sort_keys=True))
        elif args.command == "ncu-csv":
            print(json.dumps({"rows": normalize_ncu_csv(args.input, args.source_id, args.output, args.classification, args.ncu_version)}))
        elif args.command == "rebuild-index":
            print(json.dumps({key: str(value) for key, value in rebuild_indexes(args.root).items()}, sort_keys=True))
        else:
            print(json.dumps(analyze_catalog_run(args.root, args.run_id, args.raw_rel, args.parser_commit, os.sys.argv), sort_keys=True))
    except AnalysisError as exc:
        parser.exit(2, f"C16 analysis failed closed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
