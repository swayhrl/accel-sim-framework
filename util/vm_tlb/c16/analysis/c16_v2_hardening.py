#!/usr/bin/env python3
"""CPU-only semantic hardening for the accepted C16 V2 MREF shard evidence.

This tool reads hash-closed raw containers and creates a *new* compact review
pack.  It neither changes raw evidence nor rewrites the accepted ingest pack.
In particular, a MREF shard is an independent replay: aggregate absolute VA
sets are emitted only as diagnostics unless a shared address space is proven.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c16_warp_container import (  # noqa: E402
    WarpError,
    decode_c16warp1,
    sha256,
    static_access_kind,
    terminal_proof,
    validated_static_width_bytes,
)


RAW_ROOT = Path("/root/share/mnt164/huangrulin/c16_ai_workload")
ACCEPTED_PACK = Path("docs/vm_tlb/review_packs/C16_FIRST_V2_FORMAL_INGEST_174NEW_V1")
TARGETS = {
    "Q05_ATTN": "C16R_qwen25-05b_s2-text_prefill_nvbit-warp-mref-shard_attention-core-v2_20260915T013537Z_820eda91c057",
    "Q05_GEMM": "C16R_qwen25-05b_s2-text_prefill_nvbit-warp-mref-shard_gemm-heavy-v2_20260915T015202Z_1bf75d41aa29",
}


class HardeningError(RuntimeError):
    pass


def source_sha(path: Path) -> str:
    return sha256(path)


def json_sha_row(row: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(row, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def tsv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def load_accepted() -> dict[str, dict[str, str]]:
    table = ACCEPTED_PACK / "RUN_VERIFICATION.tsv"
    if not table.is_file():
        raise HardeningError("accepted run-verification table is missing")
    rows = list(csv.DictReader(table.open(encoding="utf-8"), delimiter="\t"))
    by_target = {row["target"]: row for row in rows}
    if set(by_target) != set(TARGETS) or any(row["result"] != "PASS" for row in rows):
        raise HardeningError("accepted V2 input table is not exactly the two PASS targets")
    return by_target


def load_prior_access_counts() -> dict[str, dict[str, int]]:
    table = ACCEPTED_PACK / "LOGICAL_TARGET_FINGERPRINT.tsv"
    rows = list(csv.DictReader(table.open(encoding="utf-8"), delimiter="\t"))
    by_target = {row["target"]: json.loads(row["access_counts"]) for row in rows}
    if set(by_target) != set(TARGETS):
        raise HardeningError("accepted logical-fingerprint table lacks a target")
    return by_target


def verified_raw_dir(run_id: str, accepted: dict[str, str]) -> tuple[Path, dict[str, Any], set[str]]:
    entry_path = RAW_ROOT / "catalog" / "entries" / f"{run_id}.json"
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    raw_dir = Path(entry["raw_path"])
    if entry.get("raw_manifest_sha256") != accepted["catalog_raw_manifest_sha256"]:
        raise HardeningError(f"catalog manifest authority mismatch: {run_id}")
    manifest_path = raw_dir / "RUN_MANIFEST.json"
    if sha256(manifest_path) != accepted["catalog_raw_manifest_sha256"]:
        raise HardeningError(f"manifest rehash mismatch: {run_id}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    declared: set[str] = set()
    for item in manifest.get("artifacts", []):
        rel = item["relative_path"]
        candidate = raw_dir / rel
        if not candidate.is_file() or candidate.stat().st_size != item["size_bytes"] or sha256(candidate) != item["sha256"]:
            raise HardeningError(f"raw artifact closure mismatch: {run_id}:{rel}")
        declared.add(rel)
    return raw_dir, manifest, declared


def static_rows(raw_dir: Path, shards: list[dict[str, Any]]) -> dict[int, dict[str, str]]:
    path = raw_dir / "STATIC_MREF_MAP.tsv"
    required = {"nvbit_static_index", "opcode", "is_load", "is_store", "has_mref", "sass", "memory_space"}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise HardeningError("static map lacks required hash-bound columns")
        rows = {int(row["nvbit_static_index"]): row for row in reader}
    selected = {int(item["static_index"]) for item in shards}
    if not selected.issubset(rows):
        raise HardeningError("selected static MREF is absent from static map")
    for index in selected:
        if rows[index]["has_mref"] != "1" or rows[index]["memory_space"] != "GLOBAL":
            raise HardeningError(f"selected MREF is not a direct global static row: {index}")
    return rows


def bucket_summary(addresses: list[int], width: int | None) -> dict[str, int]:
    """Return buckets for starting addresses, or exact touched buckets if known."""
    if width is None:
        return {"unique_exact_va": len(set(addresses)), "unique_4k_pages": len({value >> 12 for value in addresses}), "unique_128b_lines": len({value >> 7 for value in addresses})}
    pages, lines = set(), set()
    for address in addresses:
        pages.update(range(address >> 12, ((address + width - 1) >> 12) + 1))
        lines.update(range(address >> 7, ((address + width - 1) >> 7) + 1))
    return {"unique_exact_va": len(set(addresses)), "unique_4k_pages": len(pages), "unique_128b_lines": len(lines)}


def address_space_result(raw_dir: Path, shards: list[dict[str, Any]]) -> dict[str, str]:
    # The v2 NVBit tool consumes one immutable C16_WARP_STATIC selection and
    # emits one terminal container before `done=true`; a different static index
    # consequently entails a different formal_runtime process/replay.  Raw
    # evidence has one object map, no per-shard process/address-space identity,
    # and no object-relative normalization or repeatability contract.
    return {
        "address_space_status": "SEPARATE_REPLAY_ADDRESS_SPACE",
        "shard_count": str(len(shards)),
        "distinct_static_indices": str(len({item["static_index"] for item in shards})),
        "shared_cuda_address_space_proven": "NO",
        "per_shard_same_process_object_map": "NO",
        "normalizable_object_relative_identity": "NO",
        "evidence": "one C16_WARP_STATIC selection per C16WARP1 terminal replay; single container OBJECT_MAP.json has no per-shard process/address-space binding",
        "object_attribution_policy": "UNKNOWN_RUNTIME_ONLY_NO_CROSS_PROCESS_ABSOLUTE_VA_JOIN",
        "cross_shard_absolute_va_union": "REPLAY_UNION_DIAGNOSTIC",
        "raw_object_map_sha256": sha256(raw_dir / "OBJECT_MAP.json"),
    }


def audit_target(target: str, run_id: str, accepted: dict[str, str]) -> dict[str, Any]:
    raw_dir, manifest, declared = verified_raw_dir(run_id, accepted)
    logical = json.loads((raw_dir / "WARP_SHARD_MANIFEST.json").read_text(encoding="utf-8"))
    shards = logical.get("shards")
    selected = logical.get("static_global_mref_set")
    if logical.get("schema_version") != "C16_V2_MREF_SHARDED_COMPLETE_SET_V1" or not isinstance(shards, list) or not isinstance(selected, list):
        raise HardeningError(f"unexpected V2 shard schema: {run_id}")
    selected_sha = hashlib.sha256(json.dumps(selected, separators=(",", ":")).encode()).hexdigest()
    if selected_sha != accepted["static_set_sha256"] or len(selected) != int(accepted["static_count"]):
        raise HardeningError(f"static set closure mismatch: {run_id}")
    if {item.get("static_index") for item in shards} != set(selected) or len(shards) != len(selected):
        raise HardeningError(f"static-set shard coverage mismatch: {run_id}")
    maps = static_rows(raw_dir, shards)
    address_space = address_space_result(raw_dir, shards)
    static_map_sha = sha256(raw_dir / "STATIC_MREF_MAP.tsv")
    access_rows: list[dict[str, Any]] = []
    width_rows: list[dict[str, Any]] = []
    fingerprint_rows: list[dict[str, Any]] = []
    all_addresses: list[int] = []
    access_events: Counter[str] = Counter()
    exact_events = unknown_events = 0
    exact_touched_pages: set[int] = set()
    exact_touched_lines: set[int] = set()
    direct_object_map_matches = 0
    ranges = json.loads((raw_dir / "OBJECT_MAP.json").read_text(encoding="utf-8")).get("ranges", [])
    parsed_ranges = [(int(item["address_start_hex"], 16), int(item["address_end_hex"], 16)) for item in ranges]
    executed = zero = 0
    for shard in sorted(shards, key=lambda item: int(item["static_index"])):
        index, occurrence, record_count, overflow = (int(shard["static_index"]), int(shard["occurrence"]), int(shard["records"]), int(shard["overflow"]))
        binary = raw_dir / "raw_shards" / shard["file"]
        log = binary.with_suffix(".stdout.log")
        if f"raw_shards/{binary.name}" not in declared or f"raw_shards/{log.name}" not in declared:
            raise HardeningError(f"undeclared shard evidence: {run_id}:{index}")
        if binary.stat().st_size != int(shard["bytes"]) or sha256(binary) != shard["sha256"]:
            raise HardeningError(f"shard hash/size mismatch: {run_id}:{index}")
        try:
            decoded, events = decode_c16warp1(binary, index, occurrence)
        except WarpError as error:
            raise HardeningError(f"C16WARP1 decoder rejection: {run_id}:{index}: {error}") from error
        if decoded["records_written"] != record_count or decoded["overflow"] != overflow or not terminal_proof(log, index, occurrence, record_count, overflow):
            raise HardeningError(f"terminal closure mismatch: {run_id}:{index}")
        row = maps[index]
        kind = static_access_kind(row)
        width = validated_static_width_bytes(row)
        width_status = "WIDTH_EXACT_FROM_VALIDATED_STATIC_DECODER" if width is not None else "WIDTH_UNKNOWN"
        status = "EXECUTED_SHARD" if record_count else "ZERO_EXECUTION_PROVEN"
        executed += int(bool(record_count)); zero += int(not record_count)
        addresses = [int(event["address"]) for event in events]
        all_addresses.extend(addresses)
        access_events[kind] += len(addresses)
        starts = bucket_summary(addresses, None)
        exact = bucket_summary(addresses, width) if width is not None else {"unique_4k_pages": 0, "unique_128b_lines": 0}
        if width is None:
            unknown_events += len(addresses)
        else:
            exact_events += len(addresses)
            for address in addresses:
                exact_touched_pages.update(range(address >> 12, ((address + width - 1) >> 12) + 1))
                exact_touched_lines.update(range(address >> 7, ((address + width - 1) >> 7) + 1))
        direct_object_map_matches += sum(any(start <= address < end for start, end in parsed_ranges) for address in addresses)
        static_row_sha = json_sha_row(row)
        access_rows.append({"target": target, "run_id": run_id, "static_index": index, "execution_status": status, "active_lane_address_events": len(addresses), "static_map_sha256": static_map_sha, "static_row_sha256": static_row_sha, "opcode": row["opcode"], "is_load": row["is_load"], "is_store": row["is_store"], "derived_access_kind": kind, "evidence": "NVBIT_STATIC_INSTRUCTION_ISLOAD_ISSTORE_EXACT_ROW"})
        width_rows.append({"target": target, "run_id": run_id, "static_index": index, "execution_status": status, "active_lane_address_events": len(addresses), "static_map_sha256": static_map_sha, "static_row_sha256": static_row_sha, "opcode": row["opcode"], "sass": row["sass"], "width_classification": width_status, "width_bytes": "" if width is None else width, "evidence": "EXACT_SASS_MNEMONIC_EQUALS_STATIC_OPCODE" if width is not None else "C16WARP1_HAS_NO_WIDTH_AND_STATIC_SASS_HAS_NO_VALIDATED_EXPLICIT_WIDTH"})
        fingerprint_rows.append({"target": target, "run_id": run_id, "static_index": index, "occurrence": occurrence, "execution_status": status, "warp_records": record_count, "active_lane_address_events": len(addresses), "access_kind": kind, "width_classification": width_status, "start_unique_exact_va": starts["unique_exact_va"], "start_unique_4k_pages": starts["unique_4k_pages"], "start_unique_128b_lines": starts["unique_128b_lines"], "width_exact_event_count": len(addresses) if width is not None else 0, "width_unknown_event_count": len(addresses) if width is None else 0, "exact_width_subset_touched_4k_pages": exact["unique_4k_pages"], "exact_width_subset_touched_128b_lines": exact["unique_128b_lines"], "object_attribution": "UNKNOWN_RUNTIME", "footprint_semantics": "FORMAL_PER_SHARD_START_ADDRESS_BUCKETS;EXACT_WIDTH_SUBSET_TOUCHED_BUCKETS_ONLY"})
    starts_union = bucket_summary(all_addresses, None)
    aggregate = {"target": target, "run_id": run_id, "executed_shards": executed, "zero_execution_proven_shards": zero, "active_lane_address_events": len(all_addresses), "access_counts": json.dumps(dict(sorted(access_events.items())), sort_keys=True), "width_exact_event_count": exact_events, "width_unknown_event_count": unknown_events, "per_shard_start_address_footprint": "FORMAL", "per_shard_crossing_footprint": "EXACT_WIDTH_SUBSET_ONLY" if unknown_events else "FORMAL_ALL_EVENTS_WIDTH_EXACT", "replay_union_absolute_va_count": starts_union["unique_exact_va"], "replay_union_start_4k_page_count": starts_union["unique_4k_pages"], "replay_union_start_128b_line_count": starts_union["unique_128b_lines"], "replay_union_exact_width_subset_touched_4k_pages": len(exact_touched_pages), "replay_union_exact_width_subset_touched_128b_lines": len(exact_touched_lines), "cross_shard_absolute_va_semantics": "REPLAY_UNION_DIAGNOSTIC", "physical_whole_launch_footprint": "UNSUPPORTED_NO_SHARED_ADDRESS_SPACE_PROOF", "normalized_object_relative_union": "UNSUPPORTED", "cross_shard_order": "PROHIBITED", "cross_shard_reuse_distance": "UNSUPPORTED"}
    object_row = {"target": target, "run_id": run_id, "address_space_status": address_space["address_space_status"], "active_lane_address_events": len(all_addresses), "direct_absolute_va_matches_against_single_container_object_map": direct_object_map_matches, "assigned_object_attribution": "UNKNOWN_RUNTIME", "policy": address_space["object_attribution_policy"], "result": "PASS_CONSERVATIVE_UNKNOWN_RUNTIME"}
    return {"access": access_rows, "width": width_rows, "fingerprints": fingerprint_rows, "aggregate": aggregate, "address_space": {"target": target, "run_id": run_id, **address_space}, "object": object_row, "raw": raw_dir, "manifest": manifest, "static_map_sha": static_map_sha}


def q2_regressions() -> list[dict[str, Any]]:
    # The legacy corpus is only read and parsed into a temporary directory.
    expected = {
        "RTX3090_Q2_PREFILL": {"file": "q2_prefill_raw.jsonl", "lane_events": 786432, "READ": 524288, "WRITE": 262144, "unique_exact_va": 333952, "unique_128b_lines": 5224, "unique_4k_pages": 164, "unique_2m_pages": 20},
        "RTX3090_Q2_DECODE": {"file": "q2_decode_raw.jsonl", "lane_events": 18432, "READ": 12288, "WRITE": 6144, "unique_exact_va": 12291, "unique_128b_lines": 195, "unique_4k_pages": 9, "unique_2m_pages": 7},
    }
    from c16_analysis import parse_route_b  # noqa: E402
    rows = []
    fixture_root = RAW_ROOT / "legacy" / "rtx3090_minimal_compare"
    for name, wanted in expected.items():
        source = fixture_root / wanted["file"]
        with tempfile.TemporaryDirectory() as directory:
            parsed = Path(directory) / "parsed.jsonl"
            stats = parse_route_b(source, name, parsed)
        observed = {"lane_events": stats["lane_events"], "READ": stats["access_counts"].get("READ", 0), "WRITE": stats["access_counts"].get("WRITE", 0), "unique_exact_va": stats["unique_exact_va"], "unique_128b_lines": stats["unique_128b_lines"], "unique_4k_pages": stats["unique_4k_pages"], "unique_2m_pages": stats["unique_2m_pages"]}
        for metric, value in wanted.items():
            if metric == "file":
                continue
            rows.append({"test_id": name, "coverage": metric, "expected": value, "observed": observed[metric], "result": "PASS" if observed[metric] == value else "FAIL", "source_sha256": sha256(source)})
    return rows


def run(output: Path, parser_commit: str) -> None:
    if output.exists():
        raise HardeningError(f"output already exists: {output}")
    accepted = load_accepted()
    prior_access = load_prior_access_counts()
    result = {target: audit_target(target, run_id, accepted[target]) for target, run_id in TARGETS.items()}
    for target in TARGETS:
        observed = json.loads(result[target]["aggregate"]["access_counts"])
        prior = prior_access[target]
        if observed != prior:
            raise HardeningError(f"static access join changes accepted access counts: {target}")
        result[target]["aggregate"]["accepted_prior_access_counts"] = json.dumps(prior, sort_keys=True)
        result[target]["aggregate"]["access_count_comparison"] = "MATCH_ACCEPTED_DERIVED_ACCESS_COUNTS"
    q2_rows = q2_regressions()
    if any(row["result"] != "PASS" for row in q2_rows):
        raise HardeningError("RTX3090 Q2 exact regression failed")
    output.mkdir(parents=True)
    access = [row for target in TARGETS for row in result[target]["access"]]
    widths = [row for target in TARGETS for row in result[target]["width"]]
    fingerprints = [row for target in TARGETS for row in result[target]["fingerprints"]]
    addresses = [result[target]["address_space"] for target in TARGETS]
    objects = [result[target]["object"] for target in TARGETS]
    aggregates = [result[target]["aggregate"] for target in TARGETS]
    tsv(output / "ACCESS_KIND_AUDIT.tsv", list(access[0]), access)
    tsv(output / "WIDTH_AUDIT.tsv", list(widths[0]), widths)
    tsv(output / "PER_SHARD_FINGERPRINT.tsv", list(fingerprints[0]), fingerprints)
    tsv(output / "ADDRESS_SPACE_AUDIT.tsv", list(addresses[0]), addresses)
    tsv(output / "OBJECT_ATTRIBUTION_AUDIT.tsv", list(objects[0]), objects)
    tsv(output / "AGGREGATE_SEMANTICS.tsv", list(aggregates[0]), aggregates)
    tsv(output / "REGRESSION_RESULTS.tsv", list(q2_rows[0]), q2_rows)
    accepted_rows = [{"target": target, "run_id": TARGETS[target], "accepted_run_manifest_sha256": accepted[target]["catalog_raw_manifest_sha256"], "accepted_static_set_sha256": accepted[target]["static_set_sha256"], "accepted_static_count": accepted[target]["static_count"], "rehash_result": "PASS", "raw_static_map_sha256": result[target]["static_map_sha"]} for target in TARGETS]
    tsv(output / "ACCEPTED_INPUTS.tsv", list(accepted_rows[0]), accepted_rows)
    source = Path(__file__).resolve()
    receipt = {"schema_version": 1, "mode": "CPU_ONLY", "raw_mutation": False, "accepted_ingest_review_pack": str(ACCEPTED_PACK), "accepted_producer_commit": "fd2cb24a73d5bb0d5bfadde19438db9ebc2552df", "parser_commit": parser_commit, "parser_source": str(source), "parser_source_sha256": source_sha(source), "c16warp_container_source_sha256": source_sha(source.parent / "c16_warp_container.py"), "raw_root": str(RAW_ROOT), "raw_run_manifest_closure": "PASS", "c16warp1_decoder_integrity": "PASS", "mref_executed_zero_closure": "PASS_170_STATIC_ROWS", "rtx3090_q2_exact_regression": "PASS", "outputs": ["ACCESS_KIND_AUDIT.tsv", "WIDTH_AUDIT.tsv", "ADDRESS_SPACE_AUDIT.tsv", "PER_SHARD_FINGERPRINT.tsv", "AGGREGATE_SEMANTICS.tsv", "OBJECT_ATTRIBUTION_AUDIT.tsv", "REGRESSION_RESULTS.tsv"]}
    (output / "DERIVED_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    decision = {"schema_version": 1, "decision": "C16_V2_ANALYSIS_HARDENING_PASS", "accepted_transport_and_closure_evidence": "PRESERVED", "access_kind_audit": "PASS_STATIC_EXACT_JOIN", "width_audit": "PASS_EXPLICIT_STATIC_SASS_ONLY_UNKNOWN_PRESERVED", "address_space_audit": "PASS_SEPARATE_REPLAY_ADDRESS_SPACE", "object_attribution": "PASS_UNKNOWN_RUNTIME_RETAINED", "cross_shard_absolute_va": "REPLAY_UNION_DIAGNOSTIC_NOT_PHYSICAL_WHOLE_LAUNCH", "unsupported_claims": ["CROSS_SHARD_ORDER", "CROSS_SHARD_REUSE_DISTANCE", "GLOBAL_HARDWARE_ORDER", "CROSS_SHARD_OBJECT_UNION", "PHYSICAL_WHOLE_LAUNCH_ABSOLUTE_VA_FOOTPRINT"], "raw_mutation": False, "gpu_workload": "NOT_RUN"}
    (output / "FINAL_DECISION.json").write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "OPEN_ISSUES.md").write_text("""# Open semantic boundaries

`C16WARP1` contains lane starting addresses, not access widths.  The hardening decoder accepts only an explicit width-bearing static opcode when it exactly equals the SASS mnemonic.  Bare `STG.E` remains `WIDTH_UNKNOWN`; its page/line values are explicitly start-address buckets, not touched-range claims.

Every V2 MREF shard is a distinct replay selected by immutable `C16_WARP_STATIC`.  The raw containers carry one object map without a per-shard process/address-space binding, stable object-relative normalization, or repeatability/layout-equivalence proof.  Therefore all active events remain `UNKNOWN_RUNTIME`; object unions are unsupported.

Per-shard starting-address footprints and exact static-MREF executed/zero closure remain FORMAL.  Cross-shard absolute VA/page/line unions are retained only as `REPLAY_UNION_DIAGNOSTIC`; no whole-launch physical footprint, temporal order, reuse distance, or global hardware order is claimed.
""", encoding="utf-8")
    (output / "README.md").write_text("""# C16 V2 analysis hardening — 174-new V1

Status: `C16_V2_ANALYSIS_HARDENING_PASS`.

This is a new CPU-only derived review pack. It preserves the accepted V2 transport, decoder, artifact-SHA, and 170-row executed/zero closure evidence without changing raw data or the accepted ingest review pack.

The static access join confirms that the existing all-WRITE event totals are supported for the currently executed rows, rather than a C16WARP1 access-kind field. The result is bound to the admitted static rows. Width is recovered only for static SASS mnemonics with an explicit, matching width; all other rows remain unknown. Cross-replay absolute-VA unions are diagnostic only because the shards are separate replay address spaces.
""", encoding="utf-8")
    sums = []
    for path in sorted(output.iterdir()):
        if path.name != "SHA256SUMS" and path.is_file():
            sums.append(f"{sha256(path)}  {path.name}")
    (output / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--parser-commit", required=True)
    args = parser.parse_args()
    try:
        run(args.output, args.parser_commit)
    except (HardeningError, WarpError, OSError, json.JSONDecodeError) as error:
        parser.exit(2, f"C16 V2 hardening failed closed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
