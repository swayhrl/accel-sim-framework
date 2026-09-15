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
LOGICAL_TARGET_SCHEMA = "C16_LOGICAL_TARGET_MANIFEST_V1"
V2_SHARD_SCHEMA = "C16_V2_SHARD_BINDING_V1"
COMPACT_BINARY_READY_HOOK = "NODE109_COMPACT_BINARY_FORMAT_SPEC_REQUIRED"
V2_IDENTITY_FIELDS = {"model_id", "input_binding_sha256", "scenario_id", "target_function", "code_object_sha256", "launch_selector", "static_mref_set_sha256"}
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
        "cta": raw.get("cta"),
        "warp": raw.get("warp_id"),
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


def write_receipt(source_id: str, source: Path, outputs: list[Path], receipt_path: Path, parser_commit: str, argv: list[str], parser_config: dict[str, Any] | None = None) -> None:
    dump_json(receipt_path, {
        "schema_version": SCHEMA,
        "source_id": source_id,
        "source_path": str(source),
        "source_sha256": sha256(source),
        "parser_git_commit": parser_commit,
        "parser_argv": argv,
        "parser_config": parser_config or {"raw_schema": "C16_ROUTE_B_LANE_EVENT_V1", "record_kind": "LANE_EVENT", "terminal_required_when_present": "COMPLETE_ZERO_OVERFLOW_ZERO_DROP"},
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


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def decode_compact_binary(source: Path, format_spec: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Explicit fail-closed hook until node109 supplies a hash-bound record layout."""
    del source, format_spec
    raise AnalysisError(COMPACT_BINARY_READY_HOOK)


def _counter_add(destination: Counter, values: dict[str, int]) -> None:
    destination.update({key: int(value) for key, value in values.items()})


def _read_parsed(path: Path) -> list[dict[str, Any]]:
    if not path.is_file() or path.stat().st_size == 0:
        raise AnalysisError("shard parse output missing or empty")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _identity_equal(actual: Any, expected: Any) -> bool:
    return _canonical(actual) == _canonical(expected)


def _v2_child_binding(manifest: dict[str, Any]) -> dict[str, Any]:
    binding = manifest.get("v2_shard_binding")
    if not isinstance(binding, dict) or binding.get("schema_version") != V2_SHARD_SCHEMA:
        raise AnalysisError("child RUN_MANIFEST lacks C16_V2_SHARD_BINDING_V1 metadata")
    if not isinstance(binding.get("target_identity"), dict) or not isinstance(binding.get("selector"), dict):
        raise AnalysisError("child V2 shard binding lacks target_identity or selector")
    return binding


def _per_cta_fingerprints(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if record.get("cta") is None:
            raise AnalysisError("CTA-sharded record lacks CTA identity")
        groups[_canonical(record["cta"])].append(record)
    return {key: fingerprint(value) for key, value in sorted(groups.items())}


def _set_fingerprint(records_by_shard: dict[str, list[dict[str, Any]]], evidence_class: str) -> dict[str, Any]:
    """Compute set/distribution aggregates without constructing a cross-shard order."""
    pages4k, pages64k, lines, vas, static_mrefs = set(), set(), set(), set(), set()
    accesses, widths, objects = Counter(), Counter(), Counter()
    cta_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for records in records_by_shard.values():
        for record in records:
            address, width = record["address"], record["width_bytes"]
            vas.add(address); pages4k.update(_range_buckets(address, width, 4096))
            pages64k.update(_range_buckets(address, width, 65536)); lines.update(_range_buckets(address, width, 128))
            static = record.get("static_instruction_identity")
            if static is not None:
                static_mrefs.add(static)
            accesses["ATOMIC" if record["is_atomic"] else "WRITE" if record["is_store"] else "READ"] += 1
            widths[str(width)] += 1; objects[record.get("object_class", "UNKNOWN_RUNTIME")] += 1
            if evidence_class == "CTA_SHARDED_ALL_MREF":
                if record.get("cta") is None:
                    raise AnalysisError("CTA-sharded record lacks CTA identity")
                cta_records[_canonical(record["cta"])].append(record)
    result = {
        "merge_semantics": "SET_UNION_AND_DISTRIBUTION_ONLY",
        "aggregate_order_label": "CROSS_SHARD_ORDER_PROHIBITED",
        "cross_shard_reuse_distance": "UNSUPPORTED",
        "unique_exact_va": len(vas), "unique_4k_pages": len(pages4k),
        "unique_64k_pages": len(pages64k), "unique_128b_lines": len(lines),
        "access_counts": dict(sorted(accesses.items())),
        "width_bytes_counts": dict(sorted(widths.items(), key=lambda item: int(item[0]))),
        "object_attribution": dict(sorted(objects.items())),
        "observed_static_mref_indices": sorted(static_mrefs),
    }
    if evidence_class == "CTA_SHARDED_ALL_MREF":
        result["per_cta_fingerprints"] = {key: fingerprint(value) for key, value in sorted(cta_records.items())}
        result["spatial_cta_diversity"] = len(cta_records)
    return result


def analyze_logical_target(root: Path, logical_manifest_path: Path, parser_commit: str, argv: list[str]) -> dict[str, Any]:
    """Parse hash-closed V2 child shards and produce only order-safe aggregate facts."""
    if not logical_manifest_path.is_file():
        raise AnalysisError("logical target manifest not found")
    logical = json.loads(logical_manifest_path.read_text(encoding="utf-8"))
    if logical.get("schema_version") != LOGICAL_TARGET_SCHEMA:
        raise AnalysisError("unsupported logical target manifest schema")
    evidence_class = logical.get("formal_evidence_class")
    if evidence_class not in {"CTA_SHARDED_ALL_MREF", "MREF_SHARDED_COMPLETE_SET"}:
        raise AnalysisError("logical target has unsupported formal evidence class")
    logical_id, identity, children = logical.get("logical_target_id"), logical.get("target_identity"), logical.get("child_shards")
    if not isinstance(logical_id, str) or not isinstance(identity, dict) or not isinstance(children, list) or not children:
        raise AnalysisError("logical target requires id, target identity, and child shards")
    if set(identity) != V2_IDENTITY_FIELDS or not isinstance(identity["launch_selector"], dict):
        raise AnalysisError("logical target target_identity is incomplete")
    expected_runs = logical.get("expected_child_run_ids", [child.get("run_id") for child in children])
    if not isinstance(expected_runs, list) or any(not isinstance(value, str) for value in expected_runs) or len(expected_runs) != len(set(expected_runs)):
        raise AnalysisError("expected_child_run_ids must be a unique string list")
    seen_runs, selectors, declared_mrefs = set(), set(), set()
    parsed_by_shard: dict[str, list[dict[str, Any]]] = {}
    child_rows = []
    for child in children:
        if not isinstance(child, dict) or not isinstance(child.get("run_id"), str) or not isinstance(child.get("raw_rel"), str):
            raise AnalysisError("child shard requires run_id and raw_rel")
        run_id = child["run_id"]
        if run_id in seen_runs:
            raise AnalysisError("logical target repeats a child RUN_ID")
        seen_runs.add(run_id)
        entry_path = root / "catalog" / "entries" / f"{run_id}.json"
        if not entry_path.is_file():
            raise AnalysisError(f"catalog entry not found for shard {run_id}")
        entry = json.loads(entry_path.read_text(encoding="utf-8"))
        raw_dir = Path(entry["raw_path"])
        raw_manifest = verify_manifest(raw_dir, entry["raw_manifest_sha256"])
        binding = _v2_child_binding(raw_manifest)
        if binding.get("formal_evidence_class") != evidence_class or not _identity_equal(binding["target_identity"], identity):
            raise AnalysisError(f"shard {run_id} target identity/evidence class mismatch")
        if binding.get("static_mref_set_sha256") != identity.get("static_mref_set_sha256"):
            raise AnalysisError(f"shard {run_id} static MREF-set identity mismatch")
        selector = binding["selector"]
        if evidence_class == "CTA_SHARDED_ALL_MREF":
            ctas = selector.get("cta_ids")
            if not isinstance(ctas, list) or not ctas:
                raise AnalysisError("CTA shard requires non-empty cta_ids")
            overlap = selectors.intersection({_canonical(cta) for cta in ctas})
            if overlap:
                raise AnalysisError("CTA shard selectors overlap")
            selectors.update(_canonical(cta) for cta in ctas)
        else:
            mrefs = selector.get("static_mref_indices")
            if not isinstance(mrefs, list) or not mrefs or any(not isinstance(value, int) for value in mrefs):
                raise AnalysisError("MREF shard requires non-empty integer static_mref_indices")
            overlap = declared_mrefs.intersection(mrefs)
            if overlap:
                raise AnalysisError("MREF shard selectors overlap")
            declared_mrefs.update(mrefs)
        parsed = root / "derived" / "parsed" / run_id / "memory_access.jsonl"
        stats = parse_route_b(raw_dir / child["raw_rel"], run_id, parsed)
        feature = root / "derived" / "features" / run_id / "fingerprint.json"
        dump_json(feature, {**stats, "source_run_id": run_id, "raw_manifest_sha256": entry["raw_manifest_sha256"], "scientific_status": entry["scientific_status"], "logical_target_id": logical_id})
        receipt = root / "derived" / "features" / run_id / "DERIVED_RECEIPT.json"
        write_receipt(run_id, raw_dir / child["raw_rel"], [parsed, feature], receipt, parser_commit, argv)
        records = _read_parsed(parsed); parsed_by_shard[run_id] = records
        if evidence_class == "CTA_SHARDED_ALL_MREF":
            declared_ctas = {_canonical(cta) for cta in selector["cta_ids"]}
            if any(_canonical(record.get("cta")) not in declared_ctas for record in records):
                raise AnalysisError(f"CTA shard {run_id} records fall outside its declared selector")
        elif any(record.get("static_instruction_identity") not in set(selector["static_mref_indices"]) for record in records):
            raise AnalysisError(f"MREF shard {run_id} records fall outside its declared selector")
        child_rows.append({"run_id": run_id, "raw_manifest_sha256": entry["raw_manifest_sha256"],
            "parsed_path": str(parsed), "parsed_sha256": sha256(parsed), "fingerprint_path": str(feature),
            "fingerprint_sha256": sha256(feature), "selector": selector, "lane_events": stats["lane_events"]})
    if evidence_class == "MREF_SHARDED_COMPLETE_SET":
        expected = logical.get("selected_static_mref_indices")
        if not isinstance(expected, list) or set(expected) != declared_mrefs or len(expected) != len(set(expected)):
            raise AnalysisError("MREF shard union does not equal the frozen selected static MREF set")
    unexpected = seen_runs.difference(expected_runs)
    missing = set(expected_runs).difference(seen_runs)
    if unexpected:
        raise AnalysisError("logical target includes a child absent from expected_child_run_ids")
    if missing and evidence_class == "MREF_SHARDED_COMPLETE_SET":
        raise AnalysisError("MREF complete-set target is missing declared child shards")
    shard_status = "PARTIAL_SHARDS_PRESENT" if missing else "COMPLETE_SHARDS_PRESENT"
    aggregate = _set_fingerprint(parsed_by_shard, evidence_class)
    output_dir = root / "derived" / "logical_targets" / logical_id
    output_dir.mkdir(parents=True, exist_ok=True)
    aggregate_path, child_index_path = output_dir / "aggregate_fingerprint.json", output_dir / "SHARD_PARSE_INDEX.tsv"
    dump_json(aggregate_path, {**aggregate, "logical_target_id": logical_id, "formal_evidence_class": evidence_class,
        "child_run_ids": sorted(seen_runs), "expected_child_run_ids": sorted(expected_runs), "shard_status": shard_status, "source_logical_manifest_sha256": sha256(logical_manifest_path),
        "target_identity": identity})
    with child_index_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["run_id", "raw_manifest_sha256", "selector", "parsed_path", "parsed_sha256", "fingerprint_path", "fingerprint_sha256", "lane_events"], delimiter="\t")
        writer.writeheader()
        for row in sorted(child_rows, key=lambda item: item["run_id"]):
            row["selector"] = _canonical(row["selector"]); writer.writerow(row)
    receipt_path = output_dir / "LOGICAL_TARGET_RECEIPT.json"
    dump_json(receipt_path, {"schema_version": SCHEMA, "logical_target_id": logical_id, "formal_evidence_class": evidence_class,
        "source_logical_manifest_path": str(logical_manifest_path), "source_logical_manifest_sha256": sha256(logical_manifest_path),
        "parser_git_commit": parser_commit, "parser_argv": argv, "parser_config": {"formal_evidence_class": evidence_class, "merge_semantics": aggregate["merge_semantics"], "cross_shard_order": "PROHIBITED"}, "created_at_utc": utc_now(),
        "merge_semantics": aggregate["merge_semantics"], "unsupported_claims": ["CROSS_SHARD_ORDER", "CROSS_SHARD_REUSE_DISTANCE", "GLOBAL_HARDWARE_ORDER"],
        "outputs": [{"path": str(path), "size_bytes": path.stat().st_size, "sha256": sha256(path)} for path in [aggregate_path, child_index_path]]})
    rebuild_indexes(root)
    return {"logical_target_id": logical_id, "formal_evidence_class": evidence_class, "shard_status": shard_status, "receipt": str(receipt_path), **aggregate}


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
    logical = commands.add_parser("analyze-logical-target")
    logical.add_argument("--root", type=Path, required=True); logical.add_argument("--logical-manifest", type=Path, required=True); logical.add_argument("--parser-commit", required=True)
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
        elif args.command == "analyze-logical-target":
            print(json.dumps(analyze_logical_target(args.root, args.logical_manifest, args.parser_commit, os.sys.argv), sort_keys=True))
        else:
            print(json.dumps(analyze_catalog_run(args.root, args.run_id, args.raw_rel, args.parser_commit, os.sys.argv), sort_keys=True))
    except AnalysisError as exc:
        parser.exit(2, f"C16 analysis failed closed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
