#!/usr/bin/env python3
"""Independent, CPU-only ingest for hash-closed C16WARP1 MREF-shard containers."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HEADER = struct.Struct("<8sIIQQQ")
RECORD = struct.Struct("<6I32Q")
MAGIC = b"C16WARP1"
FORMAT_SPEC = "C16WARP1:<8sIIQQQ|<6I32Q"
TERMINAL = re.compile(r"C16_WARP_TERMINAL static=(\d+) occurrence=(\d+) records=(\d+) overflow=(\d+)")
SASS_MNEMONIC = re.compile(r"^\s*(?:@!?P\d+\s+)?([A-Z][A-Z0-9]*(?:\.[A-Z0-9_]+)*)\s+")
WIDTH_OPCODE = re.compile(r"^(?:LDG|STG|ATOM)(?:\.[A-Z0-9_]+)*\.(8|16|32|64|128)$")


class WarpError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for part in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_container(raw_dir: Path, expected_manifest_sha: str) -> dict[str, Any]:
    manifest_path = raw_dir / "RUN_MANIFEST.json"
    if not manifest_path.is_file() or sha256(manifest_path) != expected_manifest_sha:
        raise WarpError("container RUN_MANIFEST SHA mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    declared = set()
    for artifact in manifest.get("artifacts", []):
        path = raw_dir / artifact["relative_path"]
        if not path.is_file() or path.stat().st_size != artifact["size_bytes"] or sha256(path) != artifact["sha256"]:
            raise WarpError(f"container artifact hash/size mismatch: {artifact.get('relative_path')}")
        declared.add(artifact["relative_path"])
    return {"manifest": manifest, "declared": declared}


def decode_c16warp1(path: Path, expected_static: int, expected_occurrence: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    raw = path.read_bytes()
    if len(raw) < HEADER.size:
        raise WarpError("C16WARP1 truncated header")
    magic, static_index, occurrence, callback_records, overflow, records_written = HEADER.unpack_from(raw)
    if magic != MAGIC:
        raise WarpError("C16WARP1 magic/version mismatch")
    if static_index != expected_static or occurrence != expected_occurrence:
        raise WarpError("C16WARP1 static index/occurrence mismatch")
    expected_size = HEADER.size + records_written * RECORD.size
    if len(raw) != expected_size:
        raise WarpError("C16WARP1 truncated or trailing bytes")
    if overflow != 0 or callback_records != records_written:
        raise WarpError("C16WARP1 overflow or callback/record count mismatch")
    events = []
    for offset in range(HEADER.size, len(raw), RECORD.size):
        record_static, mask, cta_x, cta_y, cta_z, warp, *addresses = RECORD.unpack_from(raw, offset)
        if record_static != static_index:
            raise WarpError("C16WARP1 record static index mismatch")
        for lane, address in enumerate(addresses):
            if (mask >> lane) & 1:
                events.append({"static_index": static_index, "occurrence": occurrence, "cta": [cta_x, cta_y, cta_z], "warp": warp, "lane": lane, "active_mask": mask, "address": address})
    return ({"format": "C16WARP1", "format_spec": FORMAT_SPEC, "static_index": static_index, "occurrence": occurrence,
             "callback_warp_records": callback_records, "overflow": overflow, "records_written": records_written,
             "active_lane_address_events": len(events), "sha256": sha256(path)}, events)


def terminal_proof(path: Path, static_index: int, occurrence: int, records: int, overflow: int) -> bool:
    matches = TERMINAL.findall(path.read_text(encoding="utf-8", errors="strict"))
    return len(matches) == 1 and tuple(map(int, matches[0])) == (static_index, occurrence, records, overflow)


def static_map(path: Path, selected: set[int]) -> dict[int, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = {int(row["nvbit_static_index"]): row for row in csv.DictReader(handle, delimiter="\t")}
    if not selected.issubset(rows):
        raise WarpError("frozen selected MREF set absent from static map")
    for index in selected:
        if rows[index].get("has_mref") != "1":
            raise WarpError("selected static index is not a static memory reference")
    return rows


def static_access_kind(row: dict[str, str]) -> str:
    """Return an access kind only when the hash-bound static row proves it.

    ``is_load``/``is_store`` are emitted from NVBit's instruction metadata.  A
    static map can also contain an atomic instruction, for which neither a
    load nor a store classification is an adequate replacement.  Any malformed
    or contradictory row remains unknown rather than inheriting a default.
    """
    load, store, opcode = row.get("is_load"), row.get("is_store"), row.get("opcode", "")
    if load not in {"0", "1"} or store not in {"0", "1"}:
        return "UNKNOWN_ACCESS_KIND"
    if opcode.startswith("ATOM"):
        return "ATOMIC"
    if (load, store) == ("1", "0"):
        return "READ"
    if (load, store) == ("0", "1"):
        return "WRITE"
    return "UNKNOWN_ACCESS_KIND"


def validated_static_width_bytes(row: dict[str, str]) -> int | None:
    """Decode an explicit SASS width only after cross-checking the static row.

    C16WARP1 has no width field.  This deliberately narrow decoder accepts
    only the exact width-bearing LDG/STG/ATOM mnemonic from the static map and
    requires that it is the actual SASS mnemonic (after an optional predicate).
    A bare opcode such as ``STG.E`` is not assigned an architecture-default
    width, and a friendly but mismatched opcode spelling is rejected.
    """
    opcode = row.get("opcode", "")
    match = WIDTH_OPCODE.fullmatch(opcode)
    sass_match = SASS_MNEMONIC.match(row.get("sass", ""))
    if not match or not sass_match or sass_match.group(1) != opcode:
        return None
    return int(match.group(1)) // 8


def object_ranges(path: Path) -> list[tuple[int, int, str]]:
    data = json.loads(path.read_text(encoding="utf-8")); ranges = []
    for item in data.get("ranges", []):
        start, end, cls = int(item["address_start_hex"], 16), int(item["address_end_hex"], 16), item.get("class")
        if end <= start or cls not in {"WEIGHT", "QUANT_METADATA", "KV_CACHE", "ACTIVATION"}:
            raise WarpError("invalid object map range/class")
        ranges.append((start, end, cls))
    return sorted(ranges)


def classify(address: int, ranges: list[tuple[int, int, str]]) -> str:
    matches = [cls for start, end, cls in ranges if start <= address < end]
    return matches[0] if len(matches) == 1 else "UNKNOWN_RUNTIME"


def ingest_container(root: Path, run_id: str, expected_manifest_sha: str, expected_static_set_sha: str, expected_count: int, parser_commit: str, producer_commit: str, parser_argv: list[str] | None = None) -> dict[str, Any]:
    entry_path = root / "catalog" / "entries" / f"{run_id}.json"
    if not entry_path.is_file():
        raise WarpError("catalog entry absent")
    entry = json.loads(entry_path.read_text(encoding="utf-8")); raw_dir = Path(entry["raw_path"])
    if entry.get("raw_manifest_sha256") != expected_manifest_sha:
        raise WarpError("catalog and accepted manifest authority mismatch")
    closure = verify_container(raw_dir, expected_manifest_sha)
    logical = json.loads((raw_dir / "WARP_SHARD_MANIFEST.json").read_text(encoding="utf-8"))
    if logical.get("schema_version") != "C16_V2_MREF_SHARDED_COMPLETE_SET_V1":
        raise WarpError("unexpected logical shard manifest schema")
    selected = logical.get("static_global_mref_set")
    if not isinstance(selected, list) or len(selected) != expected_count or len(selected) != len(set(selected)):
        raise WarpError("frozen static MREF set count/uniqueness mismatch")
    shards = logical.get("shards")
    if not isinstance(shards, list) or {item.get("static_index") for item in shards} != set(selected) or len(shards) != len(selected):
        raise WarpError("shard declarations do not exactly cover frozen static MREF set")
    computed_static_set_sha = hashlib.sha256(json.dumps(selected, separators=(",", ":")).encode("utf-8")).hexdigest()
    if computed_static_set_sha != expected_static_set_sha:
        raise WarpError("frozen static MREF-set SHA mismatch")
    maps = static_map(raw_dir / "STATIC_MREF_MAP.tsv", set(selected)); ranges = object_ranges(raw_dir / "OBJECT_MAP.json")
    executed, zero, per_shard, all_events = set(), set(), [], []
    for shard in sorted(shards, key=lambda item: item["static_index"]):
        index, occurrence, count, overflow = shard["static_index"], shard["occurrence"], shard["records"], shard["overflow"]
        binary = raw_dir / "raw_shards" / shard["file"]; log = binary.with_suffix(".stdout.log")
        if f"raw_shards/{shard['file']}" not in closure["declared"] or f"raw_shards/{log.name}" not in closure["declared"]:
            raise WarpError("binary or terminal evidence absent from raw container manifest")
        if binary.stat().st_size != shard["bytes"] or sha256(binary) != shard["sha256"]:
            raise WarpError("shard binary does not match logical manifest")
        decoded, events = decode_c16warp1(binary, index, occurrence)
        if decoded["records_written"] != count or decoded["overflow"] != overflow or not terminal_proof(log, index, occurrence, count, overflow):
            raise WarpError("binary/log terminal evidence inconsistent")
        if count == 0:
            zero.add(index); status = "ZERO_EXECUTION_PROVEN"
        else:
            executed.add(index); status = "EXECUTED_SHARD"; all_events.extend(events)
        for event in events:
            event["object_class"] = classify(event["address"], ranges)
            event["access_kind"] = static_access_kind(maps[index])
            event["opcode"] = maps[index]["opcode"]
            event["width_bytes"] = validated_static_width_bytes(maps[index])
        per_shard.append({**decoded, "classification": status, "terminal_log_sha256": sha256(log), "object_attribution": dict(Counter(event.get("object_class", "UNKNOWN_RUNTIME") for event in events))})
    if executed | zero != set(selected) or executed & zero:
        raise WarpError("executed/zero classification is not exact static-set coverage")
    addresses = {event["address"] for event in all_events}; pages4k = {value >> 12 for value in addresses}; pages64k = {value >> 16 for value in addresses}; pages2m = {value >> 21 for value in addresses}; lines = {value >> 7 for value in addresses}
    access = Counter(event["access_kind"] for event in all_events)
    objects = Counter(event["object_class"] for event in all_events)
    parsed = root / "derived" / "parsed" / run_id / "c16warp1_active_lane_events.jsonl"; parsed.parent.mkdir(parents=True, exist_ok=True)
    with parsed.open("w", encoding="utf-8") as handle:
        for event in all_events: handle.write(json.dumps(event, sort_keys=True) + "\n")
    fingerprint = {"source_run_id": run_id, "source_raw_manifest_sha256": expected_manifest_sha, "static_mref_set_sha256": expected_static_set_sha, "computed_static_mref_set_sha256": computed_static_set_sha, "frozen_static_mref_count": expected_count,
        "executed_shards": len(executed), "zero_execution_proven_shards": len(zero), "total_warp_records": sum(item["records_written"] for item in per_shard), "overflow_total": sum(item["overflow"] for item in per_shard),
        "active_lane_address_events": len(all_events), "unique_exact_va": len(addresses), "unique_4k_pages": len(pages4k), "unique_64k_pages": len(pages64k), "unique_2m_pages": len(pages2m), "unique_128b_lines": len(lines),
        "access_counts": dict(access), "width_bytes_status": "STATIC_SASS_VALIDATED_WHERE_EXPLICIT_ELSE_UNKNOWN", "object_attribution": dict(objects), "per_mref": per_shard,
        "aggregate_order_label": "CROSS_SHARD_ORDER_PROHIBITED", "cross_shard_reuse_distance": "UNSUPPORTED", "global_hardware_order": "UNSUPPORTED"}
    feature = root / "derived" / "features" / run_id / "c16warp1_logical_fingerprint.json"; dump(feature, fingerprint)
    receipt = feature.parent / "C16WARP1_DERIVED_RECEIPT.json"; dump(receipt, {"source_run_id": run_id, "source_raw_manifest_sha256": expected_manifest_sha, "producer_commit": producer_commit, "parser_commit": parser_commit,
        "parser_argv": parser_argv or [], "parser_config": {"container_mode": "SINGLE_CONTAINER_RUN", "decoder_format_spec": FORMAT_SPEC, "active_mask": "SET_BITS_ONLY_INACTIVE_LANES_NOT_EMITTED", "static_set_coverage": "EXACT_EXECUTED_OR_ZERO_EXECUTION_PROVEN", "aggregate_order_label": "CROSS_SHARD_ORDER_PROHIBITED"},
        "decoder_format_spec": FORMAT_SPEC, "decoder_source_sha256": sha256(Path(__file__)), "outputs": [{"path": str(path), "size_bytes": path.stat().st_size, "sha256": sha256(path)} for path in [parsed, feature]]})
    return {"fingerprint": fingerprint, "receipt": str(receipt), "parsed": str(parsed)}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--root", type=Path, required=True); parser.add_argument("--run-id", required=True); parser.add_argument("--manifest-sha", required=True); parser.add_argument("--static-set-sha", required=True); parser.add_argument("--static-count", type=int, required=True); parser.add_argument("--parser-commit", required=True); parser.add_argument("--producer-commit", required=True)
    args = parser.parse_args()
    try: print(json.dumps(ingest_container(args.root, args.run_id, args.manifest_sha, args.static_set_sha, args.static_count, args.parser_commit, args.producer_commit, sys.argv[1:]), sort_keys=True))
    except WarpError as error: parser.exit(2, f"C16WARP1 ingest failed closed: {error}\n")
    return 0


if __name__ == "__main__": raise SystemExit(main())
