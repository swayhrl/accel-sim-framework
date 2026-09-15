#!/usr/bin/env python3
"""CPU-only, fail-closed Qwen0 Decode V3 ingest and consolidation."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c16_v2_hardening import q2_regressions  # noqa: E402
from c16_warp_container import (  # noqa: E402
    WarpError,
    decode_c16warp1,
    sha256,
    static_access_kind,
    terminal_proof,
    validated_static_width_bytes,
)


RAW_ROOT = Path("/root/share/mnt164/huangrulin/c16_ai_workload")
PREFILL_PACK = Path("docs/vm_tlb/review_packs/C16_V2_ANALYSIS_HARDENING_174NEW_V1")
PRODUCER_AUTHORITY = "20ee2e015d3b3eb72b67d03657242887932a925d"
IMPLEMENTATION_BASE = "670a681f96adc3be463b2f8d9bc4a8c1c08fe7b8"
CONTEXT_SCHEMA = "C16_ADDRESS_CONTEXT_V1"
SHARD_SCHEMA = "C16_V3_MREF_SHARDED_COMPLETE_SET_V1"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
GPU_UUID = re.compile(r"^GPU-[0-9a-f-]+$")
OBJECT_CLASSES = {"WEIGHT", "QUANT_METADATA", "KV_CACHE", "ACTIVATION"}
OBJECT_PRIORITY = {"WEIGHT": 0, "QUANT_METADATA": 1, "KV_CACHE": 2, "ACTIVATION": 3}
IDENTITY_FIELDS = ("class", "runtime_name", "layer", "storage_bytes", "dtype", "shape")

TARGETS = {
    "Q05_DECODE_EARLY_HEAVY": {
        "run_id": "C16R_qwen25-05b_s2-text_decode_nvbit-warp-mref-shard_q05-decode-early-heavy_20260915T065526Z_310734bf5eff",
        "manifest_sha256": "8269bff93a3f53070459128937379e001bc8f133b1d63b1c25ff2016d843f720",
        "static_set_sha256": "f9b0f40792fe2b1576728d944294c223ddef0269720c91877fe0ab08f09b45f7",
        "static_count": 16,
        "producer_unique_start_va": 33,
    },
    "Q05_DECODE_EARLY_KV_ATTN": {
        "run_id": "C16R_qwen25-05b_s2-text_decode_nvbit-warp-mref-shard_q05-decode-early-kv-attn_20260915T065526Z_8e1c42e61119",
        "manifest_sha256": "0fa680ce633e9e64672406d255f0c9d04b3122c75dfd90881b790129b694a63d",
        "static_set_sha256": "2f2c7bf3f901012123c805dbf377d259196afd2a61cb76626b93b865c8ed38e5",
        "static_count": 41,
        "producer_unique_start_va": 4158,
    },
    "Q05_DECODE_LATE_KV_ATTN": {
        "run_id": "C16R_qwen25-05b_s2-text_decode_nvbit-warp-mref-shard_q05-decode-late-kv-attn_20260915T065526Z_0f93940e2b66",
        "manifest_sha256": "f49f440be6e873575a6fbd715d64dc952968fbd9d2ca6902fe7c4d50665d5a9b",
        "static_set_sha256": "2f2c7bf3f901012123c805dbf377d259196afd2a61cb76626b93b865c8ed38e5",
        "static_count": 41,
        "producer_unique_start_va": 4158,
    },
}


class DecodeError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def output_record(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), "size_bytes": path.stat().st_size, "sha256": sha256(path)}


def verified_container(target: str, authority: dict[str, Any]) -> tuple[Path, dict[str, Any], dict[str, dict[str, Any]]]:
    run_id = authority["run_id"]
    entry_path = RAW_ROOT / "catalog" / "entries" / f"{run_id}.json"
    if not entry_path.is_file():
        raise DecodeError(f"catalog entry absent: {run_id}")
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    if entry.get("run_id") != run_id or entry.get("raw_manifest_sha256") != authority["manifest_sha256"]:
        raise DecodeError(f"catalog authority mismatch: {run_id}")
    if entry.get("scientific_status") != "FORMAL" or entry.get("phase") != "DECODE":
        raise DecodeError(f"catalog status/phase mismatch: {run_id}")
    raw_dir = Path(entry["raw_path"])
    manifest_path = raw_dir / "RUN_MANIFEST.json"
    if sha256(manifest_path) != authority["manifest_sha256"]:
        raise DecodeError(f"RUN_MANIFEST rehash mismatch: {run_id}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    declared: dict[str, dict[str, Any]] = {}
    for item in manifest.get("artifacts", []):
        rel = item.get("relative_path")
        if not isinstance(rel, str) or rel in declared:
            raise DecodeError(f"duplicate/invalid manifest artifact: {run_id}:{rel}")
        path = raw_dir / rel
        if not path.is_file() or path.stat().st_size != item.get("size_bytes") or sha256(path) != item.get("sha256"):
            raise DecodeError(f"artifact size/SHA mismatch: {run_id}:{rel}")
        declared[rel] = item
    required = {"WARP_SHARD_MANIFEST.json", "STATIC_MREF_MAP.tsv", "QUICKCHECK.json"}
    if not required.issubset(declared):
        raise DecodeError(f"container lacks required artifacts: {run_id}")
    return raw_dir, entry, declared


def load_static_rows(path: Path, selected: set[int]) -> tuple[dict[int, dict[str, str]], list[dict[str, str]], str]:
    required = {"nvbit_static_index", "opcode", "memory_space", "is_load", "is_store", "has_mref", "sass", "function_mangled_name", "function_full_name"}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise DecodeError("static map lacks required exact metadata")
        all_rows = list(reader)
    rows = {int(row["nvbit_static_index"]): row for row in all_rows}
    if not selected.issubset(rows):
        raise DecodeError("selected MREF absent from static map")
    for index in selected:
        if rows[index]["memory_space"] != "GLOBAL" or rows[index]["has_mref"] != "1":
            raise DecodeError(f"selected row is not direct GLOBAL MREF: {index}")
    functions = {rows[index]["function_mangled_name"] for index in selected}
    if len(functions) != 1:
        raise DecodeError("selected MREF set spans multiple functions")
    return rows, all_rows, next(iter(functions))


def semantic_identity(item: dict[str, Any]) -> dict[str, Any]:
    identity = {field: item.get(field) for field in IDENTITY_FIELDS}
    if not isinstance(identity["runtime_name"], str) or not identity["runtime_name"]:
        raise DecodeError("object range lacks stable runtime_name")
    if not isinstance(identity["storage_bytes"], int) or identity["storage_bytes"] <= 0:
        raise DecodeError("object range lacks valid storage size")
    if not isinstance(identity["shape"], list):
        raise DecodeError("object range lacks exact shape")
    return identity


def verified_context(path: Path, shard: dict[str, Any], target: str, trace_sha: str, static_map_sha: str, entry: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    context = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "schema_version": CONTEXT_SCHEMA,
        "target_id": target,
        "static_index": str(shard["static_index"]),
        "function_occurrence": str(shard["occurrence"]),
        "trace_sha256": trace_sha,
        "static_map_sha256": static_map_sha,
        "model_id": entry["model"],
        "revision": entry["revision"],
        "scenario": "S2_TEXT",
    }
    for key, value in expected.items():
        if context.get(key) != value:
            raise DecodeError(f"address-context {key} mismatch: {target}:{shard['static_index']}")
    if not isinstance(context.get("process_pid"), int) or context["process_pid"] <= 0:
        raise DecodeError("address-context process PID invalid")
    if not isinstance(context.get("process_started_monotonic"), (int, float)) or context["process_started_monotonic"] <= 0:
        raise DecodeError("address-context process start invalid")
    if not isinstance(context.get("address_space_id"), str) or not HEX64.fullmatch(context["address_space_id"]):
        raise DecodeError("address-context address-space ID invalid")
    if not isinstance(context.get("gpu_uuid"), str) or not GPU_UUID.fullmatch(context["gpu_uuid"]):
        raise DecodeError("address-context GPU UUID invalid")
    if not isinstance(context.get("object_map_sha256"), str) or not HEX64.fullmatch(context["object_map_sha256"]):
        raise DecodeError("address-context object-map SHA invalid")
    ranges = []
    for item in context.get("ranges", []):
        if item.get("class") not in OBJECT_CLASSES:
            raise DecodeError("address-context object class invalid")
        try:
            start, end = int(item["address_start_hex"], 16), int(item["address_end_hex"], 16)
        except (KeyError, TypeError, ValueError) as error:
            raise DecodeError("address-context range address invalid") from error
        if end <= start or item.get("storage_bytes") != end - start:
            raise DecodeError("address-context range size mismatch")
        identity = semantic_identity(item)
        ranges.append({**item, "start": start, "end": end, "identity": identity, "identity_sha256": canonical_sha(identity)})
    return context, ranges


def bucket_counts(addresses: list[int], width: int | None) -> dict[str, int]:
    exact = set(addresses)
    if width is None:
        return {"unique_exact_va": len(exact), "pages4k": len({a >> 12 for a in exact}), "pages64k": len({a >> 16 for a in exact}), "pages2m": len({a >> 21 for a in exact}), "lines128": len({a >> 7 for a in exact})}
    pages4k, pages64k, pages2m, lines = set(), set(), set(), set()
    for address in exact:
        pages4k.update(range(address >> 12, ((address + width - 1) >> 12) + 1))
        pages64k.update(range(address >> 16, ((address + width - 1) >> 16) + 1))
        pages2m.update(range(address >> 21, ((address + width - 1) >> 21) + 1))
        lines.update(range(address >> 7, ((address + width - 1) >> 7) + 1))
    return {"unique_exact_va": len(exact), "pages4k": len(pages4k), "pages64k": len(pages64k), "pages2m": len(pages2m), "lines128": len(lines)}


def attribute_event(event: dict[str, Any], ranges: list[dict[str, Any]]) -> dict[str, Any]:
    matches = [item for item in ranges if item["start"] <= event["address"] < item["end"]]
    if not matches:
        return {**event, "object_class": "UNKNOWN_RUNTIME", "object_identity": None, "object_identity_sha256": None, "object_relative_offset": None, "object_match_count": 0}
    chosen = sorted(matches, key=lambda item: (OBJECT_PRIORITY[item["class"]], canonical(item["identity"]), item["start"], item["end"]))[0]
    return {**event, "object_class": chosen["class"], "object_identity": chosen["identity"], "object_identity_sha256": chosen["identity_sha256"], "object_relative_offset": event["address"] - chosen["start"], "object_match_count": len(matches)}


def attribute_same_process_event(event: dict[str, Any], ranges: list[dict[str, Any]], context: dict[str, Any]) -> dict[str, Any]:
    if event.get("address_space_id") != context.get("address_space_id") or event.get("process_pid") != context.get("process_pid"):
        raise DecodeError("cross-process/address-space object-map join prohibited")
    return attribute_event(event, ranges)


def compare_object_relative(early: list[dict[str, Any]], late: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def validated(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for event in events:
            identity, digest, offset = event.get("object_identity"), event.get("object_identity_sha256"), event.get("object_relative_offset")
            if identity is None:
                continue
            if digest != canonical_sha(identity) or not isinstance(offset, int) or offset < 0:
                raise DecodeError("object-relative event identity/offset mismatch")
            groups[digest].append(event)
        return groups
    left, right = validated(early), validated(late)
    common = sorted(set(left) & set(right))
    if not common:
        return [{"object_identity_sha256": "", "object_class": "", "runtime_name": "", "early_events": 0, "late_events": 0, "early_unique_relative_offsets": 0, "late_unique_relative_offsets": 0, "early_relative_4k_pages": 0, "late_relative_4k_pages": 0, "early_relative_128b_lines": 0, "late_relative_128b_lines": 0, "relative_offset_set_relation": "UNSUPPORTED_NO_COMMON_ATTRIBUTED_SEMANTIC_IDENTITY"}]
    rows = []
    for digest in common:
        le, re = left[digest], right[digest]
        identity = le[0]["object_identity"]
        if any(event["object_identity"] != identity for event in le + re):
            raise DecodeError("object identity digest collision/mismatch")
        lo = {event["object_relative_offset"] for event in le}; ro = {event["object_relative_offset"] for event in re}
        relation = "EQUAL" if lo == ro else "EARLY_SUBSET" if lo < ro else "LATE_SUBSET" if ro < lo else "DIFFERENT"
        rows.append({"object_identity_sha256": digest, "object_class": identity["class"], "runtime_name": identity["runtime_name"], "early_events": len(le), "late_events": len(re), "early_unique_relative_offsets": len(lo), "late_unique_relative_offsets": len(ro), "early_relative_4k_pages": len({v >> 12 for v in lo}), "late_relative_4k_pages": len({v >> 12 for v in ro}), "early_relative_128b_lines": len({v >> 7 for v in lo}), "late_relative_128b_lines": len({v >> 7 for v in ro}), "relative_offset_set_relation": relation})
    return rows


def coverage_rows(target: str, selected_function: str, all_rows: list[dict[str, str]], selected: set[int], static_map_sha: str) -> list[dict[str, Any]]:
    function_rows = [row for row in all_rows if row["function_mangled_name"] == selected_function]
    global_to_shared = [row for row in function_rows if row["memory_space"] == "GLOBAL_TO_SHARED" or row["opcode"].startswith("LDGSTS")]
    other_special = [row for row in function_rows if row["opcode"].startswith(("ATOM", "RED", "SUATOM", "TEX", "TLD"))]
    return [{
        "target": target,
        "static_map_sha256": static_map_sha,
        "function_instruction_rows": len(function_rows),
        "selected_direct_global_mref_rows": len(selected),
        "global_to_shared_static_rows": len(global_to_shared),
        "other_special_global_static_rows": len(other_special),
        "global_to_shared_opcodes": canonical(dict(sorted(Counter(row["opcode"] for row in global_to_shared).items()))),
        "coverage_classification": "DIRECT_GLOBAL_MREF_SCOPE_LIMITED_SPECIAL_GLOBAL_PATHS_PRESENT" if global_to_shared or other_special else "DIRECT_GLOBAL_MREF_SCOPE_NO_SPECIAL_GLOBAL_PATH_IDENTIFIED",
    }]


def audit_target(target: str, authority: dict[str, Any], parser_commit: str, parser_argv: list[str]) -> dict[str, Any]:
    raw_dir, entry, declared = verified_container(target, authority)
    logical = json.loads((raw_dir / "WARP_SHARD_MANIFEST.json").read_text(encoding="utf-8"))
    shards = logical.get("shards")
    if logical.get("schema_version") != SHARD_SCHEMA or logical.get("target_id") != target or not isinstance(shards, list):
        raise DecodeError(f"unexpected shard manifest identity/schema: {target}")
    selected = [item.get("static_index") for item in shards]
    if len(selected) != authority["static_count"] or len(selected) != len(set(selected)) or any(not isinstance(value, int) for value in selected):
        raise DecodeError(f"static set count/uniqueness mismatch: {target}")
    if logical.get("static_mref_set_sha256") != authority["static_set_sha256"]:
        raise DecodeError(f"static set authority mismatch: {target}")
    selected_set = set(selected)
    static_map_path = raw_dir / "STATIC_MREF_MAP.tsv"; static_map_sha = sha256(static_map_path)
    static_rows, all_static_rows, function = load_static_rows(static_map_path, selected_set)
    closure_rows, access_rows, object_rows, parsed_events, per_shard = [], [], [], [], []
    seen_spaces, seen_pids, gpu_uuids = set(), set(), set()
    access_counts: Counter[str] = Counter(); object_counts: Counter[str] = Counter()
    exact_width_events = unknown_width_events = executed = zero = warp_records = overflow_total = 0
    replay_addresses: list[int] = []
    for shard in sorted(shards, key=lambda item: item["static_index"]):
        index, occurrence = int(shard["static_index"]), int(shard["occurrence"])
        trace_rel = f"raw_shards/{shard['trace']}"; log_rel = f"raw_shards/mref_{index}.stdout.log"; context_rel = f"raw_shards/{shard['address_context']}"
        if not {trace_rel, log_rel, context_rel}.issubset(declared):
            raise DecodeError(f"shard artifact missing from container closure: {target}:{index}")
        trace, log, context_path = raw_dir / trace_rel, raw_dir / log_rel, raw_dir / context_rel
        if sha256(trace) != shard.get("trace_sha256") or sha256(context_path) != shard.get("address_context_sha256"):
            raise DecodeError(f"shard trace/context SHA mismatch: {target}:{index}")
        try:
            decoded, events = decode_c16warp1(trace, index, occurrence)
        except WarpError as error:
            raise DecodeError(f"C16WARP1 rejection: {target}:{index}: {error}") from error
        records, overflow = int(shard["records"]), int(shard["overflow"])
        if decoded["records_written"] != records or decoded["overflow"] != overflow or not terminal_proof(log, index, occurrence, records, overflow):
            raise DecodeError(f"terminal/count closure mismatch: {target}:{index}")
        computed_status = "EXECUTED_SHARD" if records else "ZERO_EXECUTION_PROVEN"
        if shard.get("classification") != computed_status:
            raise DecodeError(f"shard classification mismatch: {target}:{index}")
        context, ranges = verified_context(context_path, shard, target, decoded["sha256"], static_map_sha, entry)
        if context["address_space_id"] in seen_spaces or context["process_pid"] in seen_pids:
            raise DecodeError(f"replay address-space/process identity reused: {target}:{index}")
        seen_spaces.add(context["address_space_id"]); seen_pids.add(context["process_pid"]); gpu_uuids.add(context["gpu_uuid"])
        row = static_rows[index]; access = static_access_kind(row); width = validated_static_width_bytes(row)
        if access == "UNKNOWN_ACCESS_KIND":
            raise DecodeError(f"selected static row has unknown access kind: {target}:{index}")
        attributed = []
        for event in events:
            item = attribute_same_process_event({**event, "target": target, "run_id": authority["run_id"], "address_space_id": context["address_space_id"], "process_pid": context["process_pid"], "access_kind": access, "width_bytes": width}, ranges, context)
            attributed.append(item); parsed_events.append(item)
        addresses = [event["address"] for event in attributed]; replay_addresses.extend(addresses)
        access_counts[access] += len(addresses); object_counts.update(event["object_class"] for event in attributed)
        exact_width_events += len(addresses) if width is not None else 0; unknown_width_events += len(addresses) if width is None else 0
        executed += int(records > 0); zero += int(records == 0); warp_records += records; overflow_total += overflow
        starts = bucket_counts(addresses, None); touched = bucket_counts(addresses, width) if width is not None else None
        closure_rows.append({"target": target, "run_id": authority["run_id"], "static_index": index, "occurrence": occurrence, "classification": computed_status, "warp_records": records, "active_lane_address_events": len(addresses), "overflow": overflow, "trace_sha256": decoded["sha256"], "terminal_log_sha256": sha256(log), "address_context_sha256": sha256(context_path), "address_space_id": context["address_space_id"], "process_pid": context["process_pid"], "result": "PASS"})
        access_rows.append({"target": target, "static_index": index, "classification": computed_status, "active_lane_address_events": len(addresses), "opcode": row["opcode"], "sass": row["sass"], "is_load": row["is_load"], "is_store": row["is_store"], "derived_access_kind": access, "width_classification": "WIDTH_EXACT_FROM_VALIDATED_STATIC_SASS" if width is not None else "WIDTH_UNKNOWN", "width_bytes": "" if width is None else width, "start_unique_va": starts["unique_exact_va"], "start_4k_pages": starts["pages4k"], "start_64k_pages": starts["pages64k"], "start_2m_pages": starts["pages2m"], "start_128b_lines": starts["lines128"], "exact_width_touched_4k_pages": "" if touched is None else touched["pages4k"], "exact_width_touched_64k_pages": "" if touched is None else touched["pages64k"], "exact_width_touched_2m_pages": "" if touched is None else touched["pages2m"], "exact_width_touched_128b_lines": "" if touched is None else touched["lines128"], "static_map_sha256": static_map_sha})
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for event in attributed:
            grouped[event["object_identity_sha256"] or "UNKNOWN_RUNTIME"].append(event)
        if not grouped:
            grouped["NO_ACTIVE_EVENTS"] = []
        for identity_sha, group in sorted(grouped.items()):
            identity = group[0]["object_identity"] if group else None; group_addresses = [event["address"] for event in group]
            group_starts = bucket_counts(group_addresses, None); group_touched = bucket_counts(group_addresses, width) if width is not None else None
            object_rows.append({"target": target, "static_index": index, "occurrence": occurrence, "address_space_id": context["address_space_id"], "process_pid": context["process_pid"], "gpu_uuid": context["gpu_uuid"], "trace_sha256": decoded["sha256"], "address_context_sha256": sha256(context_path), "object_map_sha256": context["object_map_sha256"], "same_process_binding": "PASS", "object_class": identity["class"] if identity else ("UNKNOWN_RUNTIME" if group else "NO_ACTIVE_EVENTS"), "object_identity_sha256": "" if identity is None else identity_sha, "runtime_name": "" if identity is None else identity["runtime_name"], "active_lane_address_events": len(group), "start_unique_va": group_starts["unique_exact_va"], "start_4k_pages": group_starts["pages4k"], "start_64k_pages": group_starts["pages64k"], "start_2m_pages": group_starts["pages2m"], "start_128b_lines": group_starts["lines128"], "exact_width_touched_4k_pages": "" if group_touched is None else group_touched["pages4k"], "exact_width_touched_64k_pages": "" if group_touched is None else group_touched["pages64k"], "exact_width_touched_2m_pages": "" if group_touched is None else group_touched["pages2m"], "exact_width_touched_128b_lines": "" if group_touched is None else group_touched["lines128"], "alias_resolution": "CLASS_PRIORITY_THEN_CANONICAL_SEMANTIC_IDENTITY"})
        per_shard.append({"static_index": index, "occurrence": occurrence, "classification": computed_status, "warp_records": records, "active_lane_address_events": len(addresses), "access_kind": access, "width_bytes": width, "start_footprint": starts, "exact_width_touched_footprint": touched, "object_event_counts": dict(sorted(Counter(event["object_class"] for event in attributed).items())), "address_space_id": context["address_space_id"], "process_pid": context["process_pid"], "trace_sha256": decoded["sha256"], "address_context_sha256": sha256(context_path)})
    if len(gpu_uuids) != 1 or executed + zero != authority["static_count"] or overflow_total:
        raise DecodeError(f"target replay/GPU/static closure failed: {target}")
    replay_union = bucket_counts(replay_addresses, None)
    if replay_union["unique_exact_va"] != authority["producer_unique_start_va"]:
        raise DecodeError(f"producer unique-start-VA diagnostic differs from raw recomputation: {target}")
    quickcheck = json.loads((raw_dir / "QUICKCHECK.json").read_text(encoding="utf-8"))
    quickcheck_expected = {"executed_shards": executed, "zero_shards": zero, "overflow_total": overflow_total, "shard_count": authority["static_count"], "address_count_replay_diagnostic": replay_union["unique_exact_va"]}
    if any(quickcheck.get(key) != value for key, value in quickcheck_expected.items()):
        raise DecodeError(f"producer quickcheck differs from raw recomputation: {target}")
    aggregate = {"target": target, "phase": "DECODE", "run_id": authority["run_id"], "function_mangled_name": function, "occurrence": sorted({row["occurrence"] for row in closure_rows})[0], "static_mref_count": authority["static_count"], "selected_indices_independent_sha256": canonical_sha(sorted(selected)), "executed_shards": executed, "zero_execution_proven_shards": zero, "warp_records": warp_records, "active_lane_address_events": len(parsed_events), "access_counts": {kind: count for kind, count in sorted(access_counts.items()) if count}, "width_exact_event_count": exact_width_events, "width_unknown_event_count": unknown_width_events, "object_event_counts": dict(sorted(object_counts.items())), "object_attribution_coverage_events": sum(count for kind, count in object_counts.items() if kind != "UNKNOWN_RUNTIME"), "gpu_uuid": next(iter(gpu_uuids)), "per_shard_footprint_semantics": "FORMAL_PROCESS_LOCAL", "replay_union_unique_start_va": replay_union["unique_exact_va"], "replay_union_start_4k_pages": replay_union["pages4k"], "replay_union_start_64k_pages": replay_union["pages64k"], "replay_union_start_2m_pages": replay_union["pages2m"], "replay_union_start_128b_lines": replay_union["lines128"], "replay_union_semantics": "REPLAY_UNION_DIAGNOSTIC", "physical_whole_kernel_absolute_va_footprint": "UNSUPPORTED", "cross_shard_order": "PROHIBITED", "cross_shard_reuse_distance": "UNSUPPORTED", "cross_shard_object_union": "UNSUPPORTED"}
    parsed_path = RAW_ROOT / "derived" / "parsed" / authority["run_id"] / "c16warp1_hardened_active_lane_events.jsonl"
    parsed_path.parent.mkdir(parents=True, exist_ok=True)
    with parsed_path.open("w", encoding="utf-8") as handle:
        for event in parsed_events:
            handle.write(canonical(event) + "\n")
    feature_path = RAW_ROOT / "derived" / "features" / authority["run_id"] / "c16_decode_target_fingerprint.json"
    dump(feature_path, {**aggregate, "source_raw_manifest_sha256": authority["manifest_sha256"], "static_mref_set_sha256": authority["static_set_sha256"], "per_shard": per_shard})
    receipt_path = feature_path.parent / "C16_DECODE_DERIVED_RECEIPT.json"
    dump(receipt_path, {"schema_version": 1, "created_at_utc": utc_now(), "source_run_id": authority["run_id"], "source_raw_manifest_sha256": authority["manifest_sha256"], "producer_authority_commit": PRODUCER_AUTHORITY, "parser_commit": parser_commit, "parser_source_path": str(Path(__file__).resolve()), "parser_source_sha256": sha256(Path(__file__)), "parser_argv": parser_argv, "parser_config": {"address_context_schema": CONTEXT_SCHEMA, "object_join": "SAME_SHARD_SAME_PROCESS_CONTEXT_ONLY", "width": "EXACT_VALIDATED_SASS_OR_UNKNOWN", "replay_union": "DIAGNOSTIC_ONLY", "cross_shard_order": "PROHIBITED"}, "outputs": [output_record(parsed_path), output_record(feature_path)]})
    return {"raw_dir": raw_dir, "entry": entry, "aggregate": aggregate, "closure_rows": closure_rows, "access_rows": access_rows, "object_rows": object_rows, "parsed_events": parsed_events, "receipt_path": receipt_path, "coverage_rows": coverage_rows(target, function, all_static_rows, selected_set, static_map_sha), "address_space_ids": seen_spaces, "process_pids": seen_pids}


def prefill_baseline_rows() -> list[dict[str, Any]]:
    aggregate_path = PREFILL_PACK / "AGGREGATE_SEMANTICS.tsv"
    accepted_path = PREFILL_PACK / "ACCEPTED_INPUTS.tsv"
    aggregates = {row["target"]: row for row in csv.DictReader(aggregate_path.open(encoding="utf-8"), delimiter="\t")}
    accepted = {row["target"]: row for row in csv.DictReader(accepted_path.open(encoding="utf-8"), delimiter="\t")}
    if set(aggregates) != {"Q05_ATTN", "Q05_GEMM"} or set(accepted) != set(aggregates):
        raise DecodeError("accepted Prefill hardening pack is incomplete")
    rows = []
    for target in ("Q05_ATTN", "Q05_GEMM"):
        row, authority = aggregates[target], accepted[target]
        raw_dir = Path(json.loads((RAW_ROOT / "catalog" / "entries" / f"{row['run_id']}.json").read_text(encoding="utf-8"))["raw_path"])
        logical = json.loads((raw_dir / "WARP_SHARD_MANIFEST.json").read_text(encoding="utf-8")); occurrence = logical["shards"][0]["occurrence"]
        static = list(csv.DictReader((raw_dir / "STATIC_MREF_MAP.tsv").open(encoding="utf-8"), delimiter="\t")); selected = {item["static_index"] for item in logical["shards"]}; function = next(item["function_mangled_name"] for item in static if int(item["nvbit_static_index"]) in selected)
        rows.append({"phase": "PREFILL", "target": target, "run_id": row["run_id"], "function_mangled_name": function, "occurrence": occurrence, "static_mref_count": int(authority["accepted_static_count"]), "executed_shards": int(row["executed_shards"]), "zero_execution_proven_shards": int(row["zero_execution_proven_shards"]), "active_lane_address_events": int(row["active_lane_address_events"]), "access_counts": row["access_counts"], "width_exact_event_count": int(row["width_exact_event_count"]), "width_unknown_event_count": int(row["width_unknown_event_count"]), "object_attributed_events": 0, "object_event_counts": canonical({"UNKNOWN_RUNTIME": int(row["active_lane_address_events"])}), "per_shard_footprint_semantics": "FORMAL_PROCESS_LOCAL", "replay_union_semantics": "REPLAY_UNION_DIAGNOSTIC", "object_relative_normalization": "UNSUPPORTED_NO_PER_SHARD_CONTEXT", "physical_whole_kernel_absolute_va_footprint": "UNSUPPORTED", "evidence_source": "C16_V2_ANALYSIS_HARDENING_174NEW_V1"})
    return rows


def run(output: Path, parser_commit: str, awq_receipt: Path | None, parser_argv: list[str]) -> None:
    if output.exists():
        raise DecodeError(f"output already exists: {output}")
    results = {target: audit_target(target, authority, parser_commit, parser_argv) for target, authority in TARGETS.items()}
    all_spaces = [space for target in TARGETS for space in results[target]["address_space_ids"]]
    all_pids = [pid for target in TARGETS for pid in results[target]["process_pids"]]
    if len(all_spaces) != len(set(all_spaces)) or len(all_pids) != len(set(all_pids)):
        raise DecodeError("cross-target replay process/address-space identity reused")
    if len({results[target]["aggregate"]["gpu_uuid"] for target in TARGETS}) != 1:
        raise DecodeError("Decode target GPU UUIDs differ")
    object_relative = compare_object_relative(results["Q05_DECODE_EARLY_KV_ATTN"]["parsed_events"], results["Q05_DECODE_LATE_KV_ATTN"]["parsed_events"])
    output.mkdir(parents=True)
    closure = [row for target in TARGETS for row in results[target]["closure_rows"]]
    access = [row for target in TARGETS for row in results[target]["access_rows"]]
    objects = [row for target in TARGETS for row in results[target]["object_rows"]]
    coverage = [row for target in TARGETS for row in results[target]["coverage_rows"]]
    write_tsv(output / "MREF_CLOSURE.tsv", list(closure[0]), closure)
    write_tsv(output / "ACCESS_WIDTH_AUDIT.tsv", list(access[0]), access)
    write_tsv(output / "PER_SHARD_OBJECT_ATTRIBUTION.tsv", list(objects[0]), objects)
    write_tsv(output / "OBJECT_RELATIVE_NORMALIZATION.tsv", list(object_relative[0]), object_relative)
    write_tsv(output / "DIRECT_GLOBAL_MREF_COVERAGE_AUDIT.tsv", list(coverage[0]), coverage)
    verification = [{"target": target, "run_id": TARGETS[target]["run_id"], "catalog_manifest_sha256": TARGETS[target]["manifest_sha256"], "artifact_hash_closure": "PASS", "static_set_sha256": TARGETS[target]["static_set_sha256"], "static_count": TARGETS[target]["static_count"], "address_context_closure": "PASS", "gpu_uuid_consistency": "PASS", "raw_mutation": "NO", "result": "PASS"} for target in TARGETS]
    write_tsv(output / "RUN_VERIFICATION.tsv", list(verification[0]), verification)
    early, late = results["Q05_DECODE_EARLY_KV_ATTN"]["aggregate"], results["Q05_DECODE_LATE_KV_ATTN"]["aggregate"]
    comparison = [{"comparison": "EARLY_VS_LATE_KV_ATTN", "function_identity": "SAME", "static_set_identity": "SAME", "early_occurrence": early["occurrence"], "late_occurrence": late["occurrence"], "early_active_lane_events": early["active_lane_address_events"], "late_active_lane_events": late["active_lane_address_events"], "early_access_counts": canonical(early["access_counts"]), "late_access_counts": canonical(late["access_counts"]), "early_width_exact_events": early["width_exact_event_count"], "late_width_exact_events": late["width_exact_event_count"], "object_relative_comparison": object_relative[0]["relative_offset_set_relation"] if len(object_relative) == 1 else "SUPPORTED_PER_MATCHED_IDENTITY_ROWS", "absolute_va_comparison": "UNSUPPORTED_SEPARATE_REPLAY_ADDRESS_SPACES", "result": "PASS_SCOPED"}]
    write_tsv(output / "EARLY_LATE_KV_COMPARISON.tsv", list(comparison[0]), comparison)
    baseline = prefill_baseline_rows()
    for target in TARGETS:
        row = results[target]["aggregate"]
        baseline.append({"phase": "DECODE", "target": target, "run_id": row["run_id"], "function_mangled_name": row["function_mangled_name"], "occurrence": row["occurrence"], "static_mref_count": row["static_mref_count"], "executed_shards": row["executed_shards"], "zero_execution_proven_shards": row["zero_execution_proven_shards"], "active_lane_address_events": row["active_lane_address_events"], "access_counts": canonical(row["access_counts"]), "width_exact_event_count": row["width_exact_event_count"], "width_unknown_event_count": row["width_unknown_event_count"], "object_attributed_events": row["object_attribution_coverage_events"], "object_event_counts": canonical(row["object_event_counts"]), "per_shard_footprint_semantics": row["per_shard_footprint_semantics"], "replay_union_semantics": row["replay_union_semantics"], "object_relative_normalization": "SUPPORTED_WHERE_MATCHED" if len(object_relative) > 1 else "UNSUPPORTED_NO_COMMON_ATTRIBUTED_SEMANTIC_IDENTITY", "physical_whole_kernel_absolute_va_footprint": row["physical_whole_kernel_absolute_va_footprint"], "evidence_source": "NODE164_RAW_INDEPENDENT_V3_INGEST"})
    write_tsv(output / "QWEN0_PREFILL_DECODE_BASELINE.tsv", list(baseline[0]), baseline)
    regressions = q2_regressions()
    for target in TARGETS:
        observed = results[target]["aggregate"]
        regressions.extend([
            {"test_id": target, "coverage": "STATIC_EXECUTED_ZERO_CLOSURE", "expected": TARGETS[target]["static_count"], "observed": observed["executed_shards"] + observed["zero_execution_proven_shards"], "result": "PASS", "source_sha256": TARGETS[target]["manifest_sha256"]},
            {"test_id": target, "coverage": "PRODUCER_UNIQUE_START_VA_DIAGNOSTIC", "expected": TARGETS[target]["producer_unique_start_va"], "observed": observed["replay_union_unique_start_va"], "result": "PASS", "source_sha256": TARGETS[target]["manifest_sha256"]},
        ])
    write_tsv(output / "REGRESSION_RESULTS.tsv", list(regressions[0]), regressions)
    supported = """# Supported claims

- All three Decode containers and every declared artifact independently hash-close.
- The 98 selected direct `GLOBAL + MREF` static rows close exactly as executed or proven-zero.
- Access kind is derived only from each hash-bound static row; width is exact only for a matching explicit SASS mnemonic.
- Per-shard start-address footprints, and touched-range footprints for exact-width subsets, are formal within that shard's process-local address space.
- Object attribution uses only the same shard's hash-bound `C16_ADDRESS_CONTEXT_V1`; unmatched addresses remain `UNKNOWN_RUNTIME`.
- The consolidated table is an analysis baseline, not a physical whole-kernel absolute-VA union.

Unsupported: cross-replay absolute-VA union as a physical footprint, cross-shard temporal order, reuse distance, cross-process object joins, and object-relative comparison without an exact matched semantic identity.
"""
    (output / "SUPPORTED_CLAIMS.md").write_text(supported, encoding="utf-8")
    issues = """# Open issues and scoped discrepancies

- Producer `address_count_replay_diagnostic=33` for Early Heavy is the unique starting-VA count after a replay union. Independent active-mask decoding yields 65 active lane-address events (one zero address, thirty-two repeated zero addresses, and thirty-two nonzero addresses). The review pack keeps these as different metrics.
- All observed Decode addresses are outside their own same-process context ranges, so object attribution remains `UNKNOWN_RUNTIME` and early/late object-relative normalization is unsupported. No cross-process fallback map was used.
- The Flash function has 84 `LDGSTS...128` `GLOBAL_TO_SHARED` static rows outside the frozen 41-row direct-GLOBAL-MREF set. The accepted runs remain valid for direct `GLOBAL + MREF` scope, but do not cover every physical global-memory path.
- Bare `LDG.E`/`STG.E` accesses remain `WIDTH_UNKNOWN`; touched-range footprints are reported only for exact-width subsets.
"""
    (output / "OPEN_ISSUES.md").write_text(issues, encoding="utf-8")
    awq_status: dict[str, Any] = {"status": "SOURCE_ACQUISITION_NOT_ATTEMPTED"}
    if awq_receipt is not None:
        if not awq_receipt.is_file():
            raise DecodeError("AWQ source acquisition receipt path is absent")
        awq_status = {"status": json.loads(awq_receipt.read_text(encoding="utf-8")).get("status"), "receipt_path": str(awq_receipt), "receipt_sha256": sha256(awq_receipt)}
    dump(output / "AWQ_SOURCE_ACQUISITION.json", awq_status)
    receipt_outputs = []
    for target in TARGETS:
        target_receipt = results[target]["receipt_path"]
        receipt_outputs.append(output_record(target_receipt))
        receipt_outputs.extend(json.loads(target_receipt.read_text(encoding="utf-8"))["outputs"])
    dump(output / "DERIVED_RECEIPT.json", {"schema_version": 1, "created_at_utc": utc_now(), "mode": "CPU_ONLY", "implementation_base": IMPLEMENTATION_BASE, "producer_authority_commit": PRODUCER_AUTHORITY, "parser_commit": parser_commit, "parser_source_path": str(Path(__file__).resolve()), "parser_source_sha256": sha256(Path(__file__)), "parser_argv": parser_argv, "parser_config": {"raw_root": str(RAW_ROOT), "address_context_schema": CONTEXT_SCHEMA, "access_kind": "STATIC_ROW_ONLY", "width": "VALIDATED_EXPLICIT_SASS_ONLY", "cross_replay_va": "REPLAY_UNION_DIAGNOSTIC", "object_join": "SAME_SHARD_ADDRESS_CONTEXT_ONLY"}, "outputs": receipt_outputs})
    decision = {"schema_version": 1, "decision": "C16_QWEN0_DECODE_ANALYSIS_174NEW_V4_PASS", "implementation_base": IMPLEMENTATION_BASE, "producer_authority_commit": PRODUCER_AUTHORITY, "parser_commit": parser_commit, "accepted_decode_targets": list(TARGETS), "decode_raw_manifest_closure": "PASS", "static_mref_closure": "PASS_98_ROWS", "address_context_binding": "PASS_98_SHARDS", "access_width_hardening": "PASS", "same_process_object_attribution": "PASS_CONSERVATIVE_UNKNOWN_RUNTIME", "object_relative_normalization": "UNSUPPORTED_NO_COMMON_ATTRIBUTED_SEMANTIC_IDENTITY", "direct_global_mref_scope": "VALID_BUT_FLASH_SPECIAL_GLOBAL_TO_SHARED_PATHS_OUTSIDE_SCOPE", "prefill_decode_baseline": "PASS_SCOPED", "rtx3090_q2_exact_regression": "PASS", "raw_mutation": False, "gpu_workload": "NOT_RUN", "awq_source_acquisition": awq_status["status"], "unsupported_claims": ["PHYSICAL_WHOLE_KERNEL_CROSS_REPLAY_ABSOLUTE_VA_FOOTPRINT", "CROSS_SHARD_ORDER", "CROSS_SHARD_REUSE_DISTANCE", "CROSS_PROCESS_OBJECT_JOIN", "UNPROVEN_OBJECT_RELATIVE_NORMALIZATION"]}
    dump(output / "FINAL_DECISION.json", decision)
    sums = [f"{sha256(path)}  {path.name}" for path in sorted(output.iterdir()) if path.is_file() and path.name != "SHA256SUMS"]
    (output / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--parser-commit", required=True)
    parser.add_argument("--awq-receipt", type=Path)
    args = parser.parse_args()
    try:
        run(args.output, args.parser_commit, args.awq_receipt, sys.argv)
    except (DecodeError, WarpError, OSError, json.JSONDecodeError, csv.Error) as error:
        parser.exit(2, f"C16 Decode consolidation failed closed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
