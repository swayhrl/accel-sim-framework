#!/usr/bin/env python3
"""Build lossless direct-semantic mappings from an nsys SQLite export.

The mapper never assigns an operator from a kernel name, duration, historical
catalog, or model-family template.  A mapping is made only when a kernel's
midpoint is temporally contained in one unambiguous NVTX range emitted by a
directly identified runtime module.  All other kernels remain ``UNKNOWN``.
"""
from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from c16_native_common import ContractError, atomic_json, sha256_file
from direct_semantic_runtime import TAG_PREFIX


MAP_FIELDS = (
    "deployment_id", "scenario_id", "run_id", "kernel_rowid", "kernel_name", "device", "context", "stream",
    "correlation_id", "grid", "block", "start_ns", "end_ns", "duration_ns", "phase", "layer_id", "operator",
    "operator_detail", "module_path", "module_class", "evidence_type", "nvtx_evidence_type",
    "module_identity_evidence_type", "evidence_source", "mapping_status", "source_run_receipt_sha256",
    "source_profile_sha256", "source_package_manifest_sha256",
)
COVERAGE_FIELDS = (
    "deployment_id", "scenario_id", "run_id", "phase", "total_kernel_rows", "total_gpu_duration_ns",
    "direct_mapped_kernel_rows", "direct_mapped_gpu_duration_ns", "direct_coverage_fraction",
    "unknown_kernel_rows", "unknown_gpu_duration_ns", "ambiguous_kernel_rows", "status",
)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read semantic input {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"semantic input {path} is not an object")
    return value


def parse_direct_tag(text: str, identity: dict[str, str]) -> dict[str, str] | None:
    if not text.startswith(TAG_PREFIX + "|"):
        return None
    parts = text.split("|")
    fields: dict[str, str] = {}
    for part in parts[1:]:
        if "=" not in part:
            return None
        key, value = part.split("=", 1)
        if not key or not value or key in fields:
            return None
        fields[key] = value
    required = {"run_id", "deployment_id", "scenario_id", "layer_id", "operator", "operator_detail", "module_path", "module_class"}
    if set(fields) != required:
        return None
    if any(fields[field] != identity[field] for field in ("run_id", "deployment_id", "scenario_id")):
        return None
    if fields["operator"] not in {"ATTENTION", "FFN", "NORM", "EMBEDDING_OUTPUT"}:
        return None
    return fields


def phase_at(midpoint: int, phases: list[tuple[int, int, str]]) -> str:
    matches = [phase for start, end, phase in phases if start <= midpoint <= end]
    if len(matches) == 1:
        return matches[0]
    return "UNKNOWN"


def direct_ranges(connection: sqlite3.Connection, identity: dict[str, str]) -> tuple[list[tuple[int, int, dict[str, str]]], list[tuple[int, int, str]]]:
    ranges: list[tuple[int, int, dict[str, str]]] = []
    phases: list[tuple[int, int, str]] = []
    for start, end, text in connection.execute("SELECT start, end, text FROM NVTX_EVENTS WHERE end IS NOT NULL ORDER BY start"):
        if not isinstance(text, str):
            continue
        if text in {"C16_PHASE_PREFILL", "C16_PHASE_DECODE"}:
            phases.append((int(start), int(end), text.removeprefix("C16_PHASE_")))
        parsed = parse_direct_tag(text, identity)
        if parsed is not None:
            if int(end) <= int(start):
                raise ContractError("direct semantic NVTX range has nonpositive extent")
            ranges.append((int(start), int(end), parsed))
    return ranges, phases


def choose_range(midpoint: int, ranges: list[tuple[int, int, dict[str, str]]]) -> tuple[dict[str, str] | None, bool]:
    """Choose the uniquely narrowest directly observed module range.

    Nested module ranges are expected.  The shortest interval is the direct
    runtime attribution; an equal-width conflict is not guessed and remains
    UNKNOWN.
    """
    candidates = [(end - start, fields) for start, end, fields in ranges if start <= midpoint <= end]
    if not candidates:
        return None, False
    candidates.sort(key=lambda item: item[0])
    narrowest = candidates[0][0]
    tied = [fields for width, fields in candidates if width == narrowest]
    labels = {(item["layer_id"], item["operator"], item["operator_detail"], item["module_path"]) for item in tied}
    if len(labels) != 1:
        return None, True
    return tied[0], False


def kernel_rows(connection: sqlite3.Connection, identity: dict[str, str], *, source_run_sha: str, source_profile_sha: str, source_manifest_sha: str) -> tuple[list[dict[str, Any]], int, int]:
    ranges, phases = direct_ranges(connection, identity)
    if not ranges:
        raise ContractError("semantic profile has no parseable direct module NVTX range")
    query = """
        SELECT k.rowid, k.start, k.end, k.deviceId, k.contextId, k.streamId, k.correlationId,
               k.gridX, k.gridY, k.gridZ, k.blockX, k.blockY, k.blockZ, s.value
        FROM CUPTI_ACTIVITY_KIND_KERNEL k
        LEFT JOIN StringIds s ON s.id = k.demangledName
        ORDER BY k.start, k.rowid
    """
    rows: list[dict[str, Any]] = []
    ambiguity_count = 0
    for rowid, start, end, device, context, stream, correlation, gx, gy, gz, bx, by, bz, name in connection.execute(query):
        start_i, end_i = int(start), int(end)
        midpoint = (start_i + end_i) // 2
        semantic, ambiguous = choose_range(midpoint, ranges)
        if ambiguous:
            ambiguity_count += 1
        common = {
            "deployment_id": identity["deployment_id"], "scenario_id": identity["scenario_id"], "run_id": identity["run_id"],
            "kernel_rowid": rowid, "kernel_name": name if isinstance(name, str) and name else "[UNRESOLVED_KERNEL_NAME]",
            "device": f"cuda:{device}", "context": f"CUDA_CONTEXT_{context}", "stream": f"CUDA_STREAM_{stream}",
            "correlation_id": f"CUDA_CORRELATION_{correlation}", "grid": f"{gx}x{gy}x{gz}", "block": f"{bx}x{by}x{bz}",
            "start_ns": start_i, "end_ns": end_i, "duration_ns": end_i - start_i, "phase": phase_at(midpoint, phases),
            "source_run_receipt_sha256": source_run_sha, "source_profile_sha256": source_profile_sha,
            "source_package_manifest_sha256": source_manifest_sha,
        }
        if semantic is None:
            rows.append({**common, "layer_id": "UNKNOWN", "operator": "UNKNOWN", "operator_detail": "UNKNOWN",
                         "module_path": "UNKNOWN", "module_class": "UNKNOWN", "evidence_type": "UNKNOWN",
                         "nvtx_evidence_type": "UNKNOWN", "module_identity_evidence_type": "UNKNOWN",
                         "evidence_source": "NO_UNAMBIGUOUS_DIRECT_RUNTIME_NVTX_CONTAINMENT",
                         "mapping_status": "UNKNOWN_CONSERVATIVE" if not ambiguous else "UNKNOWN_AMBIGUOUS_DIRECT_RANGE"})
        else:
            rows.append({**common, "layer_id": semantic["layer_id"], "operator": semantic["operator"],
                         "operator_detail": semantic["operator_detail"], "module_path": semantic["module_path"],
                         "module_class": semantic["module_class"], "evidence_type": "DIRECT_MODULE_ID",
                         "nvtx_evidence_type": "DIRECT_RUNTIME_NVTX", "module_identity_evidence_type": "DIRECT_MODULE_ID",
                         "evidence_source": "DIRECT_RUNTIME_NVTX_TEMPORAL_CONTAINMENT",
                         "mapping_status": "DIRECT_UNAMBIGUOUS"})
    if not rows:
        raise ContractError("semantic profile has no CUDA kernel rows")
    return rows, len(ranges), ambiguity_count


def coverage(rows: Iterable[dict[str, Any]], ambiguity_count: int) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["phase"]].append(row)
    result = []
    for phase, values in sorted(grouped.items()):
        total = sum(int(row["duration_ns"]) for row in values)
        mapped = [row for row in values if row["mapping_status"] == "DIRECT_UNAMBIGUOUS"]
        mapped_time = sum(int(row["duration_ns"]) for row in mapped)
        unknown = [row for row in values if row["mapping_status"] != "DIRECT_UNAMBIGUOUS"]
        result.append({
            "deployment_id": values[0]["deployment_id"], "scenario_id": values[0]["scenario_id"], "run_id": values[0]["run_id"],
            "phase": phase, "total_kernel_rows": len(values), "total_gpu_duration_ns": total,
            "direct_mapped_kernel_rows": len(mapped), "direct_mapped_gpu_duration_ns": mapped_time,
            "direct_coverage_fraction": mapped_time / total if total else 0.0,
            "unknown_kernel_rows": len(unknown), "unknown_gpu_duration_ns": sum(int(row["duration_ns"]) for row in unknown),
            "ambiguous_kernel_rows": sum(row["mapping_status"] == "UNKNOWN_AMBIGUOUS_DIRECT_RANGE" for row in values),
            "status": "DIRECT_SEMANTIC_DIAGNOSTIC_ONLY",
        })
    return result


def kernel_catalog_join_audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Prove that every semantic row retains a stable catalog join identity.

    ``kernel_rowid`` is a SQLite-local identity while correlation/stream/time
    are portable observables.  Keeping both prevents a naked launch ordinal
    or a kernel-name guess from becoming the join mechanism.
    """
    fields = ("run_id", "kernel_rowid", "correlation_id", "stream", "start_ns", "end_ns")
    keys = [tuple(str(row[field]) for field in fields) for row in rows]
    if len(keys) != len(set(keys)):
        raise ContractError("direct semantic rows do not have unique stable kernel-catalog join keys")
    return {
        "kernel_catalog_join_key_fields": list(fields),
        "kernel_catalog_join_row_count": len(keys),
        "kernel_catalog_join_unique_row_count": len(set(keys)),
        "kernel_catalog_full_population_preserved": True,
        "naked_launch_ordinal_join_forbidden": True,
    }


def write_tsv(path: Path, fields: tuple[str, ...], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sqlite", type=Path, required=True)
    parser.add_argument("--raw-profile", type=Path, required=True)
    parser.add_argument("--semantic-receipt", type=Path, required=True)
    parser.add_argument("--nsys-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    semantic, nsys = read_json(args.semantic_receipt), read_json(args.nsys_receipt)
    if semantic.get("status") != "SEMANTIC_DIAGNOSTIC_ONLY_COMPLETE" or semantic.get("scientific_eligible") is not False or semantic.get("scientific_eligible_for_timing") is not False:
        raise ContractError("semantic receipt is not an explicitly non-timing diagnostic")
    if nsys.get("execution_mode") != "NATIVE_GPU" or nsys.get("scientific_eligible") is not False or not nsys.get("checks", {}).get("semantic_diagnostic_only"):
        raise ContractError("nsys receipt is not an explicitly diagnostic native semantic capture")
    identity = semantic.get("identity")
    if not isinstance(identity, dict) or nsys.get("identity") != identity:
        raise ContractError("semantic and nsys receipt identity mismatch")
    required_identity = ("run_id", "deployment_id", "scenario_id")
    if any(not isinstance(identity.get(key), str) or not identity[key] for key in required_identity):
        raise ContractError("semantic receipt identity is incomplete")
    if semantic.get("checks", {}).get("package_manifest_sha256") in (None, "", "NA"):
        raise ContractError("semantic receipt lacks its source package manifest SHA")
    if not args.sqlite.is_file() or not args.raw_profile.is_file():
        raise ContractError("semantic mapper requires local SQLite and raw nsys profile inputs")
    connection = sqlite3.connect(args.sqlite)
    try:
        rows, range_count, ambiguity_count = kernel_rows(
            connection, identity, source_run_sha=sha256_file(args.semantic_receipt),
            source_profile_sha=sha256_file(args.raw_profile),
            source_manifest_sha=semantic["checks"]["package_manifest_sha256"],
        )
    finally:
        connection.close()
    coverage_rows = coverage(rows, ambiguity_count)
    join_audit = kernel_catalog_join_audit(rows)
    mapped_rows = sum(row["mapping_status"] == "DIRECT_UNAMBIGUOUS" for row in rows)
    qualified = range_count > 0 and mapped_rows > 0 and ambiguity_count == 0
    write_tsv(args.output_dir / "DIRECT_SEMANTIC_MAP.tsv", MAP_FIELDS, rows)
    write_tsv(args.output_dir / "SEMANTIC_COVERAGE.tsv", COVERAGE_FIELDS, coverage_rows)
    receipt = {
        "schema_version": "C16_G_DIRECT_SEMANTIC_MAP_V1", "stage_id": "C16-SEMANTIC-2",
        "status": "DIRECT_SEMANTIC_QUALIFICATION_PASS" if qualified else "DIRECT_SEMANTIC_QUALIFICATION_NO_GO",
        "scientific_eligible": False, "scientific_eligible_for_timing": False,
        "identity": identity,
        "sources": {
            "semantic_receipt": {"path": str(args.semantic_receipt), "sha256": sha256_file(args.semantic_receipt)},
            "nsys_receipt": {"path": str(args.nsys_receipt), "sha256": sha256_file(args.nsys_receipt)},
            "raw_profile": {"path": str(args.raw_profile), "sha256": sha256_file(args.raw_profile)},
            "sqlite": {"path": str(args.sqlite), "sha256": sha256_file(args.sqlite)},
        },
        "checks": {
            "kernel_name_heuristic_forbidden": True, "duration_semantic_guessing_forbidden": True,
            "historical_operator_backfill_forbidden": True, "direct_runtime_range_count": range_count,
            "direct_unambiguous_kernel_rows": mapped_rows, "ambiguous_kernel_rows": ambiguity_count,
            "unknown_rows_preserved": sum(row["mapping_status"] != "DIRECT_UNAMBIGUOUS" for row in rows),
            "kernel_correlation_stream_identity_preserved": True,
            **join_audit,
        },
        "outputs": {
            "direct_semantic_map": {"path": "DIRECT_SEMANTIC_MAP.tsv", "sha256": sha256_file(args.output_dir / "DIRECT_SEMANTIC_MAP.tsv")},
            "semantic_coverage": {"path": "SEMANTIC_COVERAGE.tsv", "sha256": sha256_file(args.output_dir / "SEMANTIC_COVERAGE.tsv")},
        },
    }
    atomic_json(args.output_dir / "SEMANTIC_EVIDENCE_RECEIPT.json", receipt)
    print(f"PASS C16 direct semantic map: {receipt['status']}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 direct semantic map: {exc}", file=sys.stderr)
        raise SystemExit(2)
