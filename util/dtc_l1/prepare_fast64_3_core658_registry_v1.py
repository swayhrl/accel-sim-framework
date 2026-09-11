#!/usr/bin/env python3
"""Prepare the isolated final FAST64.3 Base candidate registry.

This future-only, fail-closed tool has no simulator or controller authority.
It leaves the historical V2 registry untouched and can publish a V4 candidate
only after the Core-658 2DConvolution Base summary and its structural companion
have both passed strict collection.  It also selects the already strict,
triplet-compatible Core-95 GESUMMV Base candidate instead of the historical
bbcbb source-inert Base record.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "docs/dtc_l1/fast64/generated"
REGISTRY = GENERATED / "FAST64_3_BASE_SOURCE_REGISTRY_V2.tsv"
OUTPUT = GENERATED / "FAST64_3_BASE_SOURCE_REGISTRY_V4_CORE658.tsv"
FRAMEWORK = "037f008b330eb230353b60edf126d6be9f45afdc"
OBSERVER = "2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e"
CONFIG = "1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde"
HEADINGS = ("workload", "source_class", "summary", "structural", "core_sha", "runtime_sha256")

REPLACEMENTS = {
    "GESUMMV": {
        "expected_source_class": "REUSABLE_SOURCE_INERT_BASE",
        "summary": "fast64_repaired_ramp2_v1/fast64_gesummv_base_core95ccdb7a_a1_r1.json",
        "structural": "fast64_repaired_ramp2_v1/FAST64_3_GESUMMV_REPAIRED_BASE_STRUCTURAL_METRICS_V1.json",
        "core_sha": "95ccdb7a056f2d53f740d90869785cac6d4ee0f5",
        "runtime_sha256": "462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9",
    },
    "2DConvolution": {
        "expected_source_class": "INVALID_HISTORICAL_BASE_PENDING_REPAIR",
        "summary": "fast64_3_tag_identity_repair_v2/fast64_3_2DConvolution_base_core6587238c_a1_v1.json",
        "structural": "fast64_3_tag_identity_repair_v2/FAST64_3_2DCONVOLUTION_BASE_STRUCTURAL_METRICS_V2.json",
        "core_sha": "6587238c60214d99491f4048e28ce8a3458c1509",
        "runtime_sha256": "29a3dd9f57a5accb89822ca3fcf06b11c437bfe864ee43d2ff5f26c8c056f3c1",
    },
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_registry(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    if not rows or tuple(rows[0]) != HEADINGS or any(tuple(row) != HEADINGS for row in rows):
        raise RuntimeError("INVALID_FAST64_3_V2_REGISTRY_SCHEMA")
    for workload, replacement in REPLACEMENTS.items():
        matching = [row for row in rows if row["workload"] == workload]
        if len(matching) != 1 or matching[0]["source_class"] != replacement["expected_source_class"]:
            raise RuntimeError(f"EXPECTED_LITERAL_{workload}_V2_ROW")
    return rows


def require_evidence(workload: str, replacement: dict[str, str]) -> None:
    summary = GENERATED / replacement["summary"]
    structural = GENERATED / replacement["structural"]
    if not summary.is_file() or not structural.is_file():
        raise RuntimeError(f"{workload}: STRICT_SUMMARY_OR_STRUCTURAL_COMPANION_MISSING")
    record = json.loads(summary.read_text(encoding="utf-8"))
    provenance, metrics = record.get("provenance", {}), record.get("metrics", {})
    expected = {
        "workload_id": workload,
        "config_id": "FAST64_BASE_A1",
        "core_sha": replacement["core_sha"],
        "runtime_binary_sha256": replacement["runtime_sha256"],
        "framework_sha": FRAMEWORK,
        "observer_overlay_sha256": OBSERVER,
        "config_sha256": CONFIG,
        "result_classification": "PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE",
    }
    if record.get("schema") != "dtc_l1_summary_v1" or any(provenance.get(k) != v for k, v in expected.items()):
        raise RuntimeError(f"{workload}: STRICT_SUMMARY_IDENTITY_MISMATCH")
    attempt = record.get("immutable_attempt", {})
    if any(not attempt.get(key) for key in ("attempt_uuid", "runner_sha256", "start_receipt_sha256", "terminal_receipt_sha256")):
        raise RuntimeError(f"{workload}: IMMUTABLE_RECEIPT_MISSING")
    required_metrics = (
        "gpu_tot_sim_cycle", "gpu_tot_sim_insn", "DTC_L1_pib_admits", "DTC_L1_pib_retires",
        "DTC_L1_pib_occupancy", "DTC_L1_lower_requests_acquired",
        "DTC_L1_lower_requests_released", "DTC_L1_lower_outstanding",
        "DTC_L1_lower_cap_full_events",
    )
    if any(key not in metrics for key in required_metrics) or metrics["gpu_tot_sim_cycle"] <= 0 or metrics["gpu_tot_sim_insn"] <= 0:
        raise RuntimeError(f"{workload}: REQUIRED_BASE_METRIC_MISSING")
    companion = json.loads(structural.read_text(encoding="utf-8"))
    fields = (
        "cacheline_all_lines_reserved_events", "tag_bank_conflicts", "mshr_entry_full_events",
        "mshr_merge_full_events", "miss_queue_downstream_full_events",
        "live_miss_lower_acquired", "live_miss_lower_released",
        "terminal_lower_outstanding", "terminal_pib_occupancy",
    )
    canonical_summary_refs = {str(summary), str(summary.relative_to(ROOT))}
    if (companion.get("schema") != "FAST64_3_BASE_STRUCTURAL_METRICS_V1"
            or companion.get("source_summary") not in canonical_summary_refs
            or companion.get("source_summary_sha256") != digest(summary)
            or any(key not in companion.get("metrics", {}) for key in fields)):
        raise RuntimeError(f"{workload}: STRUCTURAL_COMPANION_MISMATCH")


def replacement_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    result = [dict(row) for row in rows]
    for row in result:
        replacement = REPLACEMENTS.get(row["workload"])
        if replacement:
            row.update({
                "source_class": "REPAIRED_CORE_FRESH",
                "summary": replacement["summary"],
                "structural": replacement["structural"],
                "core_sha": replacement["core_sha"],
                "runtime_sha256": replacement["runtime_sha256"],
            })
    return result


def validate_full_candidate(rows: list[dict[str, str]]) -> None:
    module_path = ROOT / "util/dtc_l1/collect_fast64_3_base_matrix_v2.py"
    spec = importlib.util.spec_from_file_location("fast64_3_base_matrix_v2", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("CANNOT_LOAD_FAST64_3_MATRIX_VALIDATOR")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", suffix=".tsv", delete=False) as stream:
        temporary = Path(stream.name)
        writer = csv.DictWriter(stream, fieldnames=HEADINGS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    try:
        for row in module.load_registry(temporary):
            module.validate(row)
    finally:
        temporary.unlink(missing_ok=True)


def write_registry(path: Path, rows: list[dict[str, str]]) -> None:
    if path.exists():
        raise RuntimeError("CANDIDATE_REGISTRY_ALREADY_EXISTS")
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=path.parent, text=True)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=HEADINGS, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        os.chmod(temporary, 0o444)
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    rows = read_registry(args.registry)
    for workload, replacement in REPLACEMENTS.items():
        require_evidence(workload, replacement)
    candidate = replacement_rows(rows)
    validate_full_candidate(candidate)
    if args.dry_run:
        print("FAST64_3_CORE658_REGISTRY_V1_DRY_RUN_PASS rows=" + str(len(candidate)))
    else:
        write_registry(args.output, candidate)
        print("FAST64_3_CORE658_REGISTRY_V1_PREPARED output=" + str(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
