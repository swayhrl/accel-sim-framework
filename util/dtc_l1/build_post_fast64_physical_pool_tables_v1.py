#!/usr/bin/env python3
"""Build Lane-B physical-pool tables from hash-bound accepted FAST64.6 inputs.

This program is deliberately analysis-only: it reads compact Stage6 summaries,
checks them against the FAST64_FINAL input manifest, and emits no simulator
inputs or execution artifacts.  A missing mode-specific compact metric is
rendered explicitly instead of being converted to zero.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FAST64_SHA = "18a68dcccd795f1b6cda75504e9450d00c9cee02"
INPUT_MANIFEST = ROOT / "docs/dtc_l1/fast64/review_packs/FAST64_FINAL/FAST64_7_INPUT_MANIFEST.tsv"
NUMERIC_REGISTRY = ROOT / "docs/dtc_l1/fast64/generated/FAST64_6_NUMERIC_REGISTRY_V1.tsv"
CELLS = ROOT / "docs/dtc_l1/fast64/generated/fast64_6_sensitivity_v3/fast64_6_cells.tsv"
DEADLOCKS = ROOT / "docs/dtc_l1/fast64/generated/fast64_6_sensitivity_v3/fast64_6_expected_deadlocks.tsv"
PLATFORM = ROOT / "docs/dtc_l1/fast64/FAST64_PLATFORM_CONTRACT.md"
WORKLOADS = ("BICG", "GESUMMV", "Btree")
SM_COUNT = 64
MISSING = "NA_NOT_REPORTED_IN_ACCEPTED_COMPACT"


@dataclass(frozen=True)
class Counter:
    column: str
    metric_key: str | None
    io_key: str | None = None
    oo_key: str | None = None
    per_lower: bool = True
    rate_eligible: bool = True


# All fields requested for B1 are explicit.  The compact schema has no OO
# peak/minimum-free or OO no-free/allocation-width exports; those cells remain
# explicit NA rather than silently becoming zeros.
COUNTERS = (
    Counter("lower_requests_created", None, "DTC_L1_io_lower_created", "DTC_L1_oo_lower_created", False),
    Counter("lower_requests_issued", None, "DTC_L1_io_lower_issued", "DTC_L1_oo_lower_issued"),
    Counter("lower_responses", None, "DTC_L1_io_lower_responses", "DTC_L1_oo_lower_responses"),
    Counter("l2_accesses", "L2_total_cache_accesses"),
    Counter("l2_misses", "L2_total_cache_misses"),
    Counter("l2_reservation_fails", "L2_total_cache_reservation_fails"),
    Counter("global_reads", "gpgpu_n_mem_read_global"),
    Counter("global_writes", "gpgpu_n_mem_write_global"),
    Counter("valid_hits", None, "DTC_L1_io_valid_hits", "DTC_L1_oo_valid_hits"),
    Counter("pending_hits", None, "DTC_L1_io_pending_hits", "DTC_L1_oo_pending_hits"),
    Counter("tag_evictions", None, "DTC_L1_io_tag_evictions", "DTC_L1_oo_tag_evictions"),
    Counter("io_duplicate_after_eviction", "DTC_L1_io_duplicate_after_eviction", per_lower=True),
    Counter("io_no_free_physical_events", "DTC_L1_io_no_free_physical_events", per_lower=True),
    Counter("io_partial_allocation_events", "DTC_L1_io_partial_allocation_events", per_lower=True),
    Counter("io_allocation_width_limited_events", "DTC_L1_io_allocation_width_limited_events", per_lower=True),
    Counter("physical_allocations", None, "DTC_L1_io_physical_allocations", "DTC_L1_oo_new_misses", False),
    Counter("physical_releases", "DTC_L1_io_physical_releases", per_lower=True),
    Counter("physical_allocated_terminal", None, "DTC_L1_io_physical_allocated_current", "DTC_L1_oo_physical_allocated", False, False),
    Counter("physical_allocated_peak_per_sm", "DTC_L1_io_physical_allocated_peak_per_sm", per_lower=False, rate_eligible=False),
    Counter("physical_free_minimum_per_sm_reported", "DTC_L1_io_physical_free_minimum_per_sm", per_lower=False, rate_eligible=False),
    Counter("oo_out_of_order_retires", "DTC_L1_oo_out_of_order_retires", per_lower=True),
    Counter("oo_immediate_reclaims", "DTC_L1_oo_immediate_reclaims", per_lower=True),
    Counter("oo_deferred_reclaims", "DTC_L1_oo_deferred_reclaims", per_lower=True),
    Counter("oo_final_ref_reclaims", "DTC_L1_oo_final_ref_reclaims", per_lower=True),
    Counter("oo_wakeups", "DTC_L1_oo_wakeups", per_lower=True),
)


def fail(message: str) -> None:
    raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def write_tsv(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=header, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def point_sort(value: str) -> float:
    return float(value)


def metric_for(counter: Counter, mode: str, metrics: dict[str, int]) -> str:
    key = counter.metric_key
    if key is None:
        key = counter.io_key if mode == "IO" else counter.oo_key
    if key is None or key not in metrics:
        return MISSING
    return str(metrics[key])


def ratio(value: str, denominator: int, scale: int = 1) -> str:
    if value == MISSING:
        return MISSING
    return f"{int(value) * scale / denominator:.9f}"


def manifest_hash(path_string: str) -> str:
    for row in read_tsv(INPUT_MANIFEST):
        if row["input_path"] == path_string:
            return row["sha256"]
    fail(f"FAST64_FINAL_INPUT_MISSING:{path_string}")


def validate_authority() -> None:
    if not all(path.is_file() for path in (INPUT_MANIFEST, NUMERIC_REGISTRY, CELLS, DEADLOCKS, PLATFORM)):
        fail("FAST64_ACCEPTED_INPUT_MISSING")
    relative_cells = CELLS.relative_to(ROOT).as_posix()
    if sha256(CELLS) != manifest_hash(relative_cells):
        fail("FAST64_STAGE6_CELLS_SHA_MISMATCH")
    deadlock_rows = read_tsv(DEADLOCKS)
    expected = {("BICG", "16.5", mode) for mode in ("IO", "OO")} | {("GESUMMV", "16.5", mode) for mode in ("IO", "OO")}
    observed = {(r["workload"], r["point"], r["mode"]) for r in deadlock_rows}
    if observed != expected:
        fail("FAST64_EXPECTED_DEADLOCK_BOUNDARY_MISMATCH")


def build_rows() -> list[dict[str, str]]:
    validate_authority()
    cells = {(r["workload"], r["dimension"], r["point"], r["mode"]): r for r in read_tsv(CELLS)}
    output: list[dict[str, str]] = []
    for registry in read_tsv(NUMERIC_REGISTRY):
        if registry["dimension"] != "physical" or registry["workload"] not in WORKLOADS:
            continue
        key = (registry["workload"], registry["dimension"], registry["point"], registry["mode"])
        if key not in cells:
            fail(f"FAST64_STAGE6_CELL_MISSING:{key}")
        cell = cells[key]
        if cell["evidence_path"] != registry["summary"]:
            fail(f"FAST64_STAGE6_SUMMARY_PATH_MISMATCH:{key}")
        compact = ROOT / registry["summary"]
        if not compact.is_file() or sha256(compact) != cell["evidence_sha256"]:
            fail(f"FAST64_STAGE6_COMPACT_SHA_MISMATCH:{key}")
        with compact.open(encoding="utf-8") as stream:
            record = json.load(stream)
        metrics = record.get("metrics")
        if not isinstance(metrics, dict):
            fail(f"FAST64_STAGE6_METRICS_MISSING:{key}")
        cycles = metrics.get("gpu_tot_sim_cycle")
        instructions = metrics.get("gpu_tot_sim_insn")
        if not isinstance(cycles, int) or cycles <= 0 or not isinstance(instructions, int) or instructions <= 0:
            fail(f"FAST64_STAGE6_INVALID_EXPOSURE:{key}")
        row = {
            "evidence_class": "ACCEPTED_FAST64_EVIDENCE",
            "frozen_fast64_framework_sha": FAST64_SHA,
            "workload": registry["workload"],
            "dimension": registry["dimension"],
            "physical_point_kib": registry["point"],
            "mode": registry["mode"],
            "modeled_pool": cell["modeled_value"],
            "row_disposition": registry["origin"],
            "compact_evidence_path": registry["summary"],
            "compact_evidence_sha256": cell["evidence_sha256"],
            "stage6_cells_path": CELLS.relative_to(ROOT).as_posix(),
            "stage6_cells_sha256": sha256(CELLS),
            "cycles": str(cycles),
            "instructions": str(instructions),
        }
        for counter in COUNTERS:
            row[counter.column] = metric_for(counter, registry["mode"], metrics)
        output.append(row)
    output.sort(key=lambda r: (WORKLOADS.index(r["workload"]), point_sort(r["physical_point_kib"]), r["mode"]))
    if len(output) != 26:
        fail(f"FAST64_LANE_B_NUMERIC_ROW_COUNT_NOT_26:{len(output)}")
    if any(r["physical_point_kib"] == "16.5" and r["workload"] != "Btree" for r in output):
        fail("EXPECTED_DEADLOCK_MISCLASSIFIED_AS_NUMERIC")
    return output


def normalized_rows(raw_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    field_by_name = {counter.column: counter for counter in COUNTERS}
    for raw in raw_rows:
        cycles = int(raw["cycles"])
        instructions = int(raw["instructions"])
        lower = raw["lower_requests_created"]
        common = {key: raw[key] for key in (
            "evidence_class", "frozen_fast64_framework_sha", "workload", "dimension",
            "physical_point_kib", "mode", "modeled_pool", "row_disposition",
            "compact_evidence_path", "compact_evidence_sha256",
        )}
        for metric in ("cycles", *field_by_name):
            raw_value = raw[metric]
            if metric == "cycles":
                normalizations = (("per_1m_instructions", instructions, 1_000_000, "cycles / instruction * 1e6", "cycles per 1M instructions"),)
            else:
                counter = field_by_name[metric]
                if not counter.rate_eligible:
                    continue
                normalizations = [
                    ("per_1m_instructions", instructions, 1_000_000, f"{metric} / instructions * 1e6", f"{metric} events per 1M instructions"),
                    ("per_simulated_cycle", cycles, 1, f"{metric} / cycles", f"{metric} events per simulated cycle"),
                    ("per_sm_cycle", cycles * SM_COUNT, 1, f"{metric} / ({SM_COUNT} * cycles)", f"{metric} events per SM-cycle"),
                ]
                if counter.per_lower and lower != MISSING and metric != "lower_requests_created":
                    normalizations.append(("per_1m_lower_requests", int(lower), 1_000_000, f"{metric} / lower_requests_created * 1e6", f"{metric} events per 1M lower requests"))
            for normalization, denominator, scale, formula, unit in normalizations:
                rows.append(common | {
                    "raw_metric": metric,
                    "raw_value": raw_value,
                    "normalization": normalization,
                    "denominator": str(denominator),
                    "normalized_value": ratio(raw_value, denominator, scale),
                    "unit": unit,
                    "formula": formula,
                    "provenance": "EXISTING_DATA_DERIVED_ANALYSIS; raw_metric from compact_evidence_path/SHA in this row; SM_COUNT=64 from FAST64_PLATFORM_CONTRACT.md",
                })
    reference = {(r["workload"], r["mode"]): r for r in raw_rows if r["physical_point_kib"] == "32"}
    if len(reference) != len(WORKLOADS) * 2:
        fail("FAST64_LANE_B_32K_REFERENCE_INCOMPLETE")
    for raw in raw_rows:
        ref = reference[(raw["workload"], raw["mode"])]
        point_cycles = int(raw["cycles"])
        ref_cycles = int(ref["cycles"])
        common = {key: raw[key] for key in (
            "evidence_class", "frozen_fast64_framework_sha", "workload", "dimension",
            "physical_point_kib", "mode", "modeled_pool", "row_disposition",
            "compact_evidence_path", "compact_evidence_sha256",
        )}
        rows.append(common | {
            "raw_metric": "cycles",
            "raw_value": raw["cycles"],
            "normalization": "same_mode_cycles_relative_to_32k",
            "denominator": str(ref_cycles),
            "normalized_value": f"{point_cycles / ref_cycles:.9f}",
            "unit": "ratio (32 KiB same workload/mode = 1.0)",
            "formula": "cycles(point, workload, mode) / cycles(32KiB, same workload, same mode)",
            "provenance": "EXISTING_DATA_DERIVED_ANALYSIS; 32 KiB reference row is an accepted compact row in this table",
        })
        rows.append(common | {
            "raw_metric": "cycles",
            "raw_value": raw["cycles"],
            "normalization": "same_mode_speedup_vs_32k",
            "denominator": str(ref_cycles),
            "normalized_value": f"{ref_cycles / point_cycles:.9f}",
            "unit": "speedup (higher is faster; 32 KiB same workload/mode = 1.0)",
            "formula": "cycles(32KiB, same workload, same mode) / cycles(point, workload, mode)",
            "provenance": "EXISTING_DATA_DERIVED_ANALYSIS; 32 KiB reference row is an accepted compact row in this table",
        })
    return rows


def dictionary_rows() -> list[dict[str, str]]:
    rows = [
        {
            "field": "physical_free_minimum_per_sm_reported",
            "kind": "raw",
            "formula_or_semantics": "Accepted compact DTC_L1_io_physical_free_minimum_per_sm; source aggregation takes the minimum only among nonzero per-SM values.",
            "unit": "lines",
            "provenance": "Core95 src/gpgpu-sim/dtc-l1-common.h:1495-1499; accepted compact path/SHA per raw row",
        },
        {
            "field": "physical_allocated_peak_per_sm",
            "kind": "raw",
            "formula_or_semantics": "Accepted compact DTC_L1_io_physical_allocated_peak_per_sm; source aggregation is max across SM-local peaks.",
            "unit": "lines",
            "provenance": "Core95 src/gpgpu-sim/dtc-l1-common.h:1492-1494; accepted compact path/SHA per raw row",
        },
    ]
    for counter in COUNTERS:
        rows.append({
            "field": counter.column,
            "kind": "raw",
            "formula_or_semantics": "Exact compact counter value; mode-inapplicable or unexported accepted fields are NA_NOT_REPORTED_IN_ACCEPTED_COMPACT.",
            "unit": "events/count unless field name states otherwise",
            "provenance": "Accepted Stage6 compact evidence path/SHA in each raw-table row",
        })
    rows.extend([
        {
            "field": "per_1m_instructions",
            "kind": "derived",
            "formula_or_semantics": "raw_metric / instructions * 1,000,000",
            "unit": "raw-metric units per 1M instructions",
            "provenance": "EXISTING_DATA_DERIVED_ANALYSIS from accepted raw table",
        },
        {
            "field": "per_1m_lower_requests",
            "kind": "derived",
            "formula_or_semantics": "raw_metric / lower_requests_created * 1,000,000; emitted only for event counters where lower-request exposure is meaningful",
            "unit": "raw-metric events per 1M lower requests",
            "provenance": "EXISTING_DATA_DERIVED_ANALYSIS from accepted raw table",
        },
        {
            "field": "per_simulated_cycle",
            "kind": "derived",
            "formula_or_semantics": "raw_metric / gpu_tot_sim_cycle",
            "unit": "raw-metric events per simulated cycle",
            "provenance": "EXISTING_DATA_DERIVED_ANALYSIS from accepted raw table",
        },
        {
            "field": "per_sm_cycle",
            "kind": "derived",
            "formula_or_semantics": "raw_metric / (64 * gpu_tot_sim_cycle)",
            "unit": "raw-metric events per SM-cycle",
            "provenance": "EXISTING_DATA_DERIVED_ANALYSIS; 64 endpoints from FAST64_PLATFORM_CONTRACT.md",
        },
        {
            "field": "same_mode_cycles_relative_to_32k",
            "kind": "derived",
            "formula_or_semantics": "cycles(point, workload, mode) / cycles(32KiB, same workload, same mode)",
            "unit": "ratio",
            "provenance": "EXISTING_DATA_DERIVED_ANALYSIS from accepted raw table",
        },
        {
            "field": "same_mode_speedup_vs_32k",
            "kind": "derived",
            "formula_or_semantics": "cycles(32KiB, same workload, same mode) / cycles(point, workload, mode)",
            "unit": "speedup; higher is faster",
            "provenance": "EXISTING_DATA_DERIVED_ANALYSIS from accepted raw table",
        },
    ])
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "generated/post_fast64")
    args = parser.parse_args()
    raw_rows = build_rows()
    normalized = normalized_rows(raw_rows)
    raw_header = list(raw_rows[0])
    normalized_header = list(normalized[0])
    dictionary = dictionary_rows()
    dictionary_header = list(dictionary[0])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".post_fast64_physical.", dir=args.output_dir) as temp:
        staging = Path(temp)
        write_tsv(staging / "physical_pool_mechanism_raw.tsv", raw_header, raw_rows)
        write_tsv(staging / "physical_pool_mechanism_normalized.tsv", normalized_header, normalized)
        write_tsv(staging / "physical_pool_mechanism_normalization_dictionary.tsv", dictionary_header, dictionary)
        for name in ("physical_pool_mechanism_raw.tsv", "physical_pool_mechanism_normalized.tsv", "physical_pool_mechanism_normalization_dictionary.tsv"):
            os.replace(staging / name, args.output_dir / name)
    print(f"POST_FAST64_LANE_B_ANALYSIS_ONLY_PASS rows={len(raw_rows)} output={args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
