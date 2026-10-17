#!/usr/bin/env python3
"""Fail-closed registry preparer for the Core41 2DConvolution Base repair.

This tool has no simulator or controller authority.  It only turns the
already-published Core41 strict summary plus structural companion into a
candidate FAST64.3 registry after independently validating the complete
12-row Base matrix.  The retained V2 registry is never edited in place.
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
OUTPUT = GENERATED / "FAST64_3_BASE_SOURCE_REGISTRY_V3_CORE41.tsv"
SUMMARY = GENERATED / "fast64_3_repair_v1/fast64_3_2DConvolution_base_core41d740e8_a1_v1.json"
STRUCTURAL = GENERATED / "fast64_3_repair_v1/FAST64_3_2DCONVOLUTION_BASE_STRUCTURAL_METRICS_V1.json"
CORE = "41d740e862a6ad89ab0fc32b7b927ec787752862"
RUNTIME = "6e72d36665cde18e2845914ee9c2a9f2e65b37b7b3c216edf4b676ad17e2c21c"
FRAMEWORK = "037f008b330eb230353b60edf126d6be9f45afdc"
OBSERVER = "2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e"
CONFIG = "1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde"
HEADINGS = ("workload", "source_class", "summary", "structural", "core_sha", "runtime_sha256")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_registry(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    if not rows or tuple(rows[0]) != HEADINGS or any(tuple(row) != HEADINGS for row in rows):
        raise RuntimeError("INVALID_FAST64_3_V2_REGISTRY_SCHEMA")
    matches = [row for row in rows if row["workload"] == "2DConvolution"]
    if len(matches) != 1 or matches[0]["source_class"] != "INVALID_HISTORICAL_BASE_PENDING_REPAIR":
        raise RuntimeError("EXPECTED_LITERAL_2D_INVALID_HISTORY_ROW")
    return rows


def replacement(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    result = [dict(row) for row in rows]
    for row in result:
        if row["workload"] == "2DConvolution":
            row.update({
                "source_class": "REPAIRED_CORE_FRESH",
                "summary": "fast64_3_repair_v1/fast64_3_2DConvolution_base_core41d740e8_a1_v1.json",
                "structural": "fast64_3_repair_v1/FAST64_3_2DCONVOLUTION_BASE_STRUCTURAL_METRICS_V1.json",
                "core_sha": CORE,
                "runtime_sha256": RUNTIME,
            })
    return result


def require_2d_evidence() -> None:
    if not SUMMARY.is_file():
        raise RuntimeError("MISSING_2D_STRICT_SUMMARY")
    if not STRUCTURAL.is_file():
        raise RuntimeError("MISSING_2D_STRUCTURAL_COMPANION")
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    provenance, metrics = summary.get("provenance", {}), summary.get("metrics", {})
    expected = {
        "workload_id": "2DConvolution", "config_id": "FAST64_BASE_A1",
        "core_sha": CORE, "runtime_binary_sha256": RUNTIME,
        "framework_sha": FRAMEWORK, "observer_overlay_sha256": OBSERVER,
        "config_sha256": CONFIG,
        "result_classification": "PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE",
    }
    if summary.get("schema") != "dtc_l1_summary_v1" or any(provenance.get(k) != v for k, v in expected.items()):
        raise RuntimeError("2D_STRICT_SUMMARY_IDENTITY_MISMATCH")
    if any(not summary.get("immutable_attempt", {}).get(key) for key in ("attempt_uuid", "runner_sha256", "start_receipt_sha256", "terminal_receipt_sha256")):
        raise RuntimeError("2D_STRICT_SUMMARY_IMMUTABLE_RECEIPT_MISSING")
    needed = ("gpu_tot_sim_cycle", "gpu_tot_sim_insn", "DTC_L1_pib_admits", "DTC_L1_pib_retires",
              "DTC_L1_pib_occupancy", "DTC_L1_lower_requests_acquired", "DTC_L1_lower_requests_released",
              "DTC_L1_lower_outstanding", "DTC_L1_lower_cap_full_events")
    if any(key not in metrics for key in needed) or metrics["gpu_tot_sim_cycle"] <= 0 or metrics["gpu_tot_sim_insn"] <= 0:
        raise RuntimeError("2D_STRICT_SUMMARY_METRIC_MISSING")
    companion = json.loads(STRUCTURAL.read_text(encoding="utf-8"))
    cm = companion.get("metrics", {})
    required = ("cacheline_all_lines_reserved_events", "tag_bank_conflicts", "mshr_entry_full_events",
                "mshr_merge_full_events", "miss_queue_downstream_full_events", "live_miss_lower_acquired",
                "live_miss_lower_released", "terminal_lower_outstanding", "terminal_pib_occupancy")
    if companion.get("schema") != "FAST64_3_BASE_STRUCTURAL_METRICS_V1" or companion.get("source_summary") != str(SUMMARY) or companion.get("source_summary_sha256") != digest(SUMMARY) or any(key not in cm for key in required):
        raise RuntimeError("2D_STRUCTURAL_COMPANION_MISMATCH")


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
        writer.writeheader(); writer.writerows(rows)
    try:
        loaded = module.load_registry(temporary)
        for row in loaded:
            module.validate(row)
    finally:
        temporary.unlink(missing_ok=True)


def write_registry(path: Path, rows: list[dict[str, str]]) -> None:
    if path.exists():
        raise RuntimeError("CANDIDATE_REGISTRY_ALREADY_EXISTS")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=path.parent, text=True)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=HEADINGS, delimiter="\t", lineterminator="\n")
            writer.writeheader(); writer.writerows(rows)
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
    rows = replacement(read_registry(args.registry))
    require_2d_evidence()
    validate_full_candidate(rows)
    if args.dry_run:
        print("FAST64_3_CORE41_REGISTRY_V1_DRY_RUN_PASS rows=" + str(len(rows)))
    else:
        write_registry(args.output, rows)
        print("FAST64_3_CORE41_REGISTRY_V1_PREPARED output=" + str(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
