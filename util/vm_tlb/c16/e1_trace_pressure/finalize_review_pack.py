#!/usr/bin/env python3
"""Fail-closed finalizer for the C16 E1 trace-pressure review pack.

This reads only compact analysis outputs. It never opens traceg inputs, and it
never overwrites an existing generated review-pack artifact.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any


EXPECTED_CORE = "a2322069b9701597db7019080b5b54d29518e3a2"
EXPECTED_CONFIG = "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8"
EXPECTED_SIDECAR = "6c60839714d136b9f6f596218588e658e245e0b7cc6f8e8550cce8d683ce13c6"

SMALL_RESULTS = (
    "AGGREGATION_PROVENANCE.json",
    "D1_D2_D2_D3_STABILITY.json",
    "PER_LAYER_REUSE_DISTANCE_MATRIX.json",
    "PER_LAYER_REUSE_DISTANCE_MATRIX.tsv",
    "QUOTA_STATIC_MAPPING.json",
    "SET_CONFLICT_PRESSURE_ANALYSIS.json",
)
GENERATED = SMALL_RESULTS + (
    "QWEIGHT_L2_SET_MAPPING_MANIFEST.json",
    "TRACE_REFERENCE_SUMMARY_MANIFEST.json",
    "VALIDATION_SUMMARY.json",
    "RESULT_SHA256SUMS",
)


class FinalizationError(ValueError):
    pass


def need(value: bool, message: str) -> None:
    if not value:
        raise FinalizationError(message)


def load(path: Path) -> dict[str, Any]:
    need(path.is_file() and path.stat().st_size > 0, f"missing/empty {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise FinalizationError(f"invalid JSON {path}: {error}") from error
    need(isinstance(value, dict), f"JSON root must be object: {path}")
    return value


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def canonical_digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_schema(value: dict, schema: str, label: str,
                   allow_missing_status: bool) -> bool:
    need(value.get("schema") == schema, f"{label}: schema drift")
    status = value.get("status")
    if status is None:
        need(allow_missing_status, f"{label}: missing status")
        return False
    need(status == "PASS", f"{label}: status is not PASS")
    return True


def distribution(values: list[float | int]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "min": None, "median": None, "max": None}
    ordered = sorted(values)
    middle = len(ordered) // 2
    median = ((ordered[middle - 1] + ordered[middle]) / 2
              if len(ordered) % 2 == 0 else ordered[middle])
    return {"count": len(values), "min": ordered[0], "median": median,
            "max": ordered[-1]}


def tree_inventory(root: Path) -> tuple[int, int]:
    files = 0
    size = 0
    for directory, _, names in os.walk(root):
        base = Path(directory)
        for name in names:
            item = base / name
            if item.is_file():
                files += 1
                size += item.stat().st_size
    return files, size


def validate(args: argparse.Namespace) -> tuple[dict, dict, dict, list[dict]]:
    summary_root = args.analysis_root / "TRACE_REFERENCE_SUMMARY"
    results = args.analysis_root / "results"
    artifacts = args.analysis_root / "artifacts"
    summary_path = summary_root / "TRACE_REFERENCE_SUMMARY.json"
    summary_tsv = summary_root / "TRACE_REFERENCE_SUMMARY.tsv"
    static_input = artifacts / "QWEIGHT_L2_SET_MAPPING.mapper.json"
    qweight_path = results / "QWEIGHT_L2_SET_MAPPING.json"

    summary = load(summary_path)
    require_schema(summary, "C16_E1_TRACE_REFERENCE_SUMMARY_INDEX_V1",
                   "trace summary index", False)
    need(summary.get("kernel_count") == args.expected_kernel_count,
         "trace summary kernel count drift")
    need(len(summary.get("kernel_summaries", [])) == args.expected_kernel_count,
         "trace summary path count drift")
    need(summary.get("claim_boundary") ==
         "TRACE_ADDRESS_REFERENCE_AND_128B_LINE_REFERENCE_PROXY_ONLY_NOT_ACTUAL_L2_TRAFFIC",
         "trace summary claim boundary drift")
    need(summary.get("sidecar_sha256") == EXPECTED_SIDECAR,
         "trace summary sidecar SHA drift")
    need(summary.get("qualified_full_sequence_closure", {}).get("status") == "PASS",
         "qualified sequence closure not PASS")
    with summary_tsv.open(newline="", encoding="utf-8") as stream:
        summary_rows = list(csv.DictReader(stream, delimiter="\t"))
    need(len(summary_rows) == args.expected_kernel_count,
         "trace summary TSV row count drift")
    kernel_files = list((summary_root / "kernels").glob("*/summary.json"))
    need(len(kernel_files) == args.expected_kernel_count,
         "durable kernel summary count drift")

    static = load(static_input)
    require_schema(static, "C16_E1_QWEIGHT_L2_SET_MAPPING_MAPPER_V1",
                   "static mapper output", False)
    qweight = load(qweight_path)
    qweight_had_status = require_schema(
        qweight, "C16_E1_QWEIGHT_L2_SET_MAPPING_V1", "qweight result",
        args.allow_missing_derived_status)
    need(qweight.get("claim_boundary") == "STATIC_ACCEPTED_MAPPER_OUTPUT",
         "qweight claim boundary drift")
    need(qweight.get("region_count") == args.expected_layer_count and
         len(qweight.get("regions", [])) == args.expected_layer_count,
         "qweight region count drift")
    need(qweight.get("total_target_lines") ==
         sum(int(row["line_count"]) for row in qweight["regions"]),
         "qweight total line closure failed")
    geometry = qweight.get("geometry", {})
    need(geometry == {"associativity": 16, "l2_bytes": 64 << 20,
                      "line_size_bytes": 128, "sets_per_subpartition": 2048,
                      "subpartition_count": 16}, "L2 geometry drift")
    for layer, row in enumerate(qweight["regions"]):
        need(int(row["layer_index"]) == layer, "qweight layer order drift")
        need(sum(int(item["line_count"]) for item in row["set_line_counts"]) ==
             int(row["line_count"]), f"layer {layer}: set-line closure failed")
        need(sum(int(value) for value in row["subpartition_line_counts"]) ==
             int(row["line_count"]), f"layer {layer}: subpartition closure failed")

    documents: dict[str, dict] = {}
    status_present = {"QWEIGHT_L2_SET_MAPPING.json": qweight_had_status}
    specifications = {
        "AGGREGATION_PROVENANCE.json": "C16_E1_TRACE_PRESSURE_AGGREGATE_V1",
        "D1_D2_D2_D3_STABILITY.json": "C16_E1_D1_D2_D2_D3_STABILITY_V1",
        "PER_LAYER_REUSE_DISTANCE_MATRIX.json": "C16_E1_PER_LAYER_REUSE_DISTANCE_MATRIX_V1",
        "QUOTA_STATIC_MAPPING.json": "C16_E1_QUOTA_STATIC_MAPPING_V1",
        "SET_CONFLICT_PRESSURE_ANALYSIS.json": "C16_E1_SET_CONFLICT_PRESSURE_ANALYSIS_V1",
    }
    for name, schema in specifications.items():
        document = load(results / name)
        status_present[name] = require_schema(
            document, schema, name, args.allow_missing_derived_status)
        documents[name] = document

    reuse = documents["PER_LAYER_REUSE_DISTANCE_MATRIX.json"]
    pressure = documents["SET_CONFLICT_PRESSURE_ANALYSIS.json"]
    stability = documents["D1_D2_D2_D3_STABILITY.json"]
    quota = documents["QUOTA_STATIC_MAPPING.json"]
    provenance = documents["AGGREGATION_PROVENANCE.json"]
    expected_keys = {(layer, transition) for layer in range(args.expected_layer_count)
                     for transition in ("D1_D2", "D2_D3")}
    need(len(reuse.get("rows", [])) == 2 * args.expected_layer_count and
         {(int(row["layer_index"]), row["transition"]) for row in reuse["rows"]} ==
         expected_keys, "reuse transition matrix drift")
    need(reuse.get("claim_boundary") == "128B_LINE_REFERENCE_PROXY",
         "reuse claim boundary drift")
    need(len(pressure.get("rows", [])) == 2 * args.expected_layer_count and
         {(int(row["layer_index"]), row["transition"]) for row in pressure["rows"]} ==
         expected_keys, "pressure transition matrix drift")
    need(pressure.get("claim_boundary") == "SET_CONFLICT_REFERENCE_PRESSURE_PROXY" and
         pressure.get("actual_l2_hit_miss_or_eviction_claimed") is False,
         "pressure claim boundary drift")
    need(stability.get("layer_count") == args.expected_layer_count and
         stability.get("claim_boundary") == "SET_CONFLICT_REFERENCE_PRESSURE_PROXY",
         "stability scope drift")
    need([row.get("budget") for row in quota.get("budgets", [])] ==
         ["B8", "B16", "B24", "BFULL"], "quota budget matrix drift")
    need(quota.get("performance_ranking_claimed") is False,
         "quota output claims performance ranking")
    for budget in quota["budgets"]:
        need(len(budget.get("per_layer_static_admission", [])) == args.expected_layer_count,
             f"{budget['budget']}: per-layer count drift")

    need(provenance.get("kernel_count") == args.expected_kernel_count and
         provenance.get("raw_trace_opened") is False,
         "aggregation provenance scope drift")
    need(provenance.get("summary_index_sha256") == digest(summary_path),
         "aggregation summary-index SHA drift")
    need(provenance.get("static_mapping_sha256") == digest(static_input),
         "aggregation static-mapping SHA drift")
    need(provenance.get("sidecar_sha256") == EXPECTED_SIDECAR,
         "aggregation sidecar SHA drift")
    authority = provenance.get("runtime_mapper_authority", {})
    mapper_provenance = authority.get("provenance", {})
    need(mapper_provenance.get("accepted_core_sha") == EXPECTED_CORE and
         mapper_provenance.get("accepted_config_sha256") == EXPECTED_CONFIG,
         "runtime mapper authority drift")
    need(provenance.get("runtime_mapper_authority_sha256") ==
         canonical_digest(authority), "runtime mapper authority hash drift")
    need(provenance.get("input_mapper_identity_sha256") ==
         canonical_digest(qweight.get("input_provenance", {}).get("mapper")),
         "input mapper identity hash drift")

    source_records = []
    for name in SMALL_RESULTS:
        path = results / name
        need(path.is_file() and path.stat().st_size > 0, f"missing result {name}")
        source_records.append({"name": name, "source_path": str(path.resolve()),
                               "size_bytes": path.stat().st_size,
                               "sha256": digest(path)})
    validation = {
        "schema": "C16_E1_TRACE_PRESSURE_FINALIZATION_VALIDATION_V1",
        "status": "PASS",
        "claim_boundary": "COMPACT_OFFLINE_TRACE_REFERENCE_PROXY_FINALIZATION",
        "raw_trace_opened": False,
        "checks": {
            "trace_summary_schema_status_rows": "PASS",
            "static_mapping_schema_status_geometry": "PASS",
            "derived_result_schemas_rows_claims": "PASS",
            "reuse_transition_matrix_2x_layers": "PASS",
            "mapper_core_config_authority": "PASS",
            "input_sha_closure": "PASS",
        },
        "expected_kernel_count": args.expected_kernel_count,
        "expected_layer_count": args.expected_layer_count,
        "derived_source_status_present": status_present,
        "missing_derived_status_explicitly_allowed": args.allow_missing_derived_status,
        "source_results": source_records,
    }
    return summary, qweight, provenance, [validation]


def manifests(args: argparse.Namespace, summary: dict, qweight: dict,
              provenance: dict) -> tuple[dict, dict]:
    summary_root = args.analysis_root / "TRACE_REFERENCE_SUMMARY"
    qweight_path = args.analysis_root / "results/QWEIGHT_L2_SET_MAPPING.json"
    static_input = args.analysis_root / "artifacts/QWEIGHT_L2_SET_MAPPING.mapper.json"
    file_count, total_bytes = tree_inventory(summary_root)
    compact_regions = [{
        "layer_index": int(row["layer_index"]),
        "target_class": int(row.get("target_class", int(row["layer_index"]) + 1)),
        "begin": int(row["begin"]),
        "end_exclusive": int(row["end_exclusive"]),
        "bytes": int(row["bytes"]),
        "line_count": int(row["line_count"]),
        "subpartition_line_counts": row["subpartition_line_counts"],
        "set_distribution": row["set_distribution"],
    } for row in qweight["regions"]]
    overlaps = qweight.get("region_pair_set_overlap", [])
    qweight_manifest = {
        "schema": "C16_E1_QWEIGHT_L2_SET_MAPPING_MANIFEST_V1",
        "status": "PASS",
        "claim_boundary": qweight["claim_boundary"],
        "durable_artifact": {
            "path": str(qweight_path.resolve()),
            "size_bytes": qweight_path.stat().st_size,
            "sha256": digest(qweight_path),
            "copied_into_review_pack": False,
        },
        "mapper_input_artifact": {
            "path": str(static_input.resolve()),
            "size_bytes": static_input.stat().st_size,
            "sha256": digest(static_input),
        },
        "geometry": qweight["geometry"],
        "region_count": qweight["region_count"],
        "total_target_lines": qweight["total_target_lines"],
        "regions": compact_regions,
        "aggregate_target_set_population": qweight["aggregate_target_set_population"],
        "region_pair_overlap": {
            "pair_count": len(overlaps),
            "set_intersection": distribution([int(row["set_intersection"]) for row in overlaps]),
            "set_jaccard": distribution([float(row["set_jaccard"]) for row in overlaps]),
        },
        "input_provenance": qweight.get("input_provenance"),
    }
    index_path = summary_root / "TRACE_REFERENCE_SUMMARY.json"
    tsv_path = summary_root / "TRACE_REFERENCE_SUMMARY.tsv"
    trace_manifest = {
        "schema": "C16_E1_TRACE_REFERENCE_SUMMARY_MANIFEST_V1",
        "status": "PASS",
        "claim_boundary": summary["claim_boundary"],
        "durable_root": str(summary_root.resolve()),
        "durable_root_file_count": file_count,
        "durable_root_size_bytes": total_bytes,
        "index": {"path": str(index_path.resolve()), "size_bytes": index_path.stat().st_size,
                  "sha256": digest(index_path)},
        "tsv_index": {"path": str(tsv_path.resolve()), "size_bytes": tsv_path.stat().st_size,
                      "sha256": digest(tsv_path)},
        "kernel_count": summary["kernel_count"],
        "kernel_range": [summary["first_kernel_id"], summary["last_kernel_id"]],
        "totals": summary["totals"],
        "qualified_full_sequence_closure": summary["qualified_full_sequence_closure"],
        "sequence_sha256": summary["sequence_sha256"],
        "sidecar_sha256": summary["sidecar_sha256"],
        "scanner_sha256": summary["scanner_sha256"],
        "trace_index_validation": summary["trace_index_validation"],
        "mapper": summary["mapper"],
        "aggregation_provenance_sha256": digest(
            args.analysis_root / "results/AGGREGATION_PROVENANCE.json"),
    }
    return qweight_manifest, trace_manifest


def prepare_destination(args: argparse.Namespace) -> None:
    if args.review_pack.exists():
        need(args.review_pack.is_dir(), "review-pack path is not a directory")
        existing = list(args.review_pack.iterdir())
        need(args.allow_existing_scaffold,
             "review pack exists; pass --allow-existing-scaffold after auditing it")
        for name in GENERATED:
            need(not (args.review_pack / name).exists(),
                 f"refusing to overwrite generated artifact: {name}")
        need(bool(existing), "--allow-existing-scaffold requires a nonempty scaffold")
    else:
        args.review_pack.mkdir(parents=True)


def finalize(args: argparse.Namespace) -> None:
    summary, qweight, provenance, validation_rows = validate(args)
    qweight_manifest, trace_manifest = manifests(args, summary, qweight, provenance)
    prepare_destination(args)
    with tempfile.TemporaryDirectory(prefix=".trace-pressure-finalize-",
                                     dir=args.review_pack.parent) as directory:
        stage = Path(directory)
        results = args.analysis_root / "results"
        for name in SMALL_RESULTS:
            shutil.copyfile(results / name, stage / name)
        dump(stage / "QWEIGHT_L2_SET_MAPPING_MANIFEST.json", qweight_manifest)
        dump(stage / "TRACE_REFERENCE_SUMMARY_MANIFEST.json", trace_manifest)
        dump(stage / "VALIDATION_SUMMARY.json", validation_rows[0])
        checksum_names = sorted(name for name in GENERATED if name != "RESULT_SHA256SUMS")
        sums = "".join(f"{digest(stage / name)}  {name}\n" for name in checksum_names)
        (stage / "RESULT_SHA256SUMS").write_text(sums, encoding="utf-8")
        for name in GENERATED:
            need(not (args.review_pack / name).exists(), f"late destination collision: {name}")
        for name in GENERATED:
            os.replace(stage / name, args.review_pack / name)
    print(json.dumps({"status": "PASS", "review_pack": str(args.review_pack),
                      "generated": list(GENERATED)}, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-root", type=Path, required=True)
    parser.add_argument("--review-pack", type=Path, required=True)
    parser.add_argument("--allow-existing-scaffold", action="store_true")
    parser.add_argument("--allow-missing-derived-status", action="store_true")
    parser.add_argument("--expected-kernel-count", type=int, default=4515)
    parser.add_argument("--expected-layer-count", type=int, default=28)
    args = parser.parse_args()
    need(args.expected_kernel_count > 0 and args.expected_layer_count > 0,
         "expected counts must be positive")
    return args


if __name__ == "__main__":
    try:
        finalize(parse_args())
    except (FinalizationError, OSError) as error:
        print(f"TRACE_PRESSURE_FINALIZATION_FAIL: {error}", file=os.sys.stderr)
        raise SystemExit(1)
