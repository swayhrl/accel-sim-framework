#!/usr/bin/env python3
"""Derive POST-FAST64 Lane-C duplicate-miss tables from frozen evidence.

This script deliberately reads only the accepted FAST64 primary registry, its
hash-bound compact JSON rows, and the accepted Stage6 physical-cell registry.
It never launches a simulator and never mutates any accepted FAST64 artifact.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
FAST64 = ROOT / "docs/dtc_l1/fast64"
GENERATED = FAST64 / "generated"
OUT = ROOT / "generated/post_fast64"
PRIMARY_REGISTRY = (
    GENERATED
    / "fast64_4_cap_resolved_matrix_v1/fast64_4_primary_accepted_matrix_v1.tsv"
)
STAGE6_CELLS = GENERATED / "fast64_6_sensitivity_v3/fast64_6_cells.tsv"
FAST12_SUMMARY = FAST64 / "review_packs/FAST64_FINAL/FAST12_summary.tsv"
PRIMARY_EVIDENCE_MANIFEST = (
    GENERATED / "fast64_5_measured_features_v3/fast64_5_input_manifest.tsv"
)
FROZEN_FAST64_COMMIT = "18a68dcccd795f1b6cda75504e9450d00c9cee02"
SM_COUNT = 64


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open() as handle:
        return json.load(handle)


def as_int(metrics: dict[str, Any], field: str, label: str) -> int:
    value = metrics.get(field)
    if not isinstance(value, int):
        raise ValueError(f"{label}: required integer metric {field!r} is absent")
    return value


def decimal(value: float | None) -> str:
    return "UNDEFINED_ZERO_DENOMINATOR" if value is None else f"{value:.9f}"


def rate(numerator: int | float, denominator: int | float) -> float | None:
    return None if denominator == 0 else numerator / denominator


def percentage(value: float | None) -> str:
    return "UNDEFINED_ZERO_DENOMINATOR" if value is None else f"{100.0 * value:.9f}"


def denominator_status(denominator: int | float) -> str:
    return "VALID" if denominator else "ZERO_DENOMINATOR_UNDEFINED"


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def accepted_fast12_workloads() -> list[str]:
    rows = read_tsv(FAST12_SUMMARY)
    result = [row["workload"] for row in rows if row["workload"] != "GM-FAST12"]
    if len(result) != 12 or len(set(result)) != 12:
        raise ValueError("FAST12_summary.tsv does not contain exactly 12 unique workloads")
    return result


def expected_primary_evidence_hashes() -> dict[tuple[str, str], str]:
    """Read FAST64's per-row hash binding for the accepted primary matrix."""
    result: dict[tuple[str, str], str] = {}
    for row in read_tsv(PRIMARY_EVIDENCE_MANIFEST):
        key = (row["workload"], row["mode"])
        if key in result:
            raise ValueError(f"duplicate primary evidence manifest key: {key}")
        result[key] = row["evidence_sha256"]
    return result


def metric_bundle(metrics: dict[str, Any], label: str) -> dict[str, int]:
    fields = (
        "gpu_tot_sim_cycle",
        "gpu_tot_sim_insn",
        "DTC_L1_io_lower_created",
        "DTC_L1_io_lower_issued",
        "DTC_L1_io_lower_responses",
        "DTC_L1_io_pending_hits",
        "DTC_L1_io_tag_evictions",
        "DTC_L1_io_duplicate_after_eviction",
        "DTC_L1_io_physical_allocations",
        "L1D_total_cache_accesses",
        "L1D_total_cache_misses",
        "L2_total_cache_accesses",
        "L2_total_cache_misses",
        "L2_total_cache_reservation_fails",
        "gpgpu_n_mem_read_global",
        "gpgpu_n_mem_write_global",
    )
    return {field: as_int(metrics, field, label) for field in fields}


def primary_rows() -> list[dict[str, str]]:
    expected_workloads = accepted_fast12_workloads()
    expected_hashes = expected_primary_evidence_hashes()
    registry = read_tsv(PRIMARY_REGISTRY)
    io = [
        row
        for row in registry
        if row["mode"] == "IO" and row["acceptance_status"] == "STRICT_TERMINAL_ACCEPTED"
    ]
    by_workload = {row["workload"]: row for row in io}
    if len(io) != 12 or set(by_workload) != set(expected_workloads):
        raise ValueError("primary IO registry is not the exact accepted FAST12 set")

    rows: list[dict[str, str]] = []
    for workload in expected_workloads:
        item = by_workload[workload]
        evidence = GENERATED / item["evidence_path"]
        if not evidence.is_file():
            raise ValueError(f"missing accepted primary compact row: {evidence}")
        expected_hash = expected_hashes.get((workload, "IO"))
        actual_hash = sha256(evidence)
        if actual_hash != expected_hash:
            raise ValueError(f"accepted IO compact evidence SHA mismatch: {evidence}")
        record = load_json(evidence)
        metrics = metric_bundle(record["metrics"], workload)
        lower = metrics["DTC_L1_io_lower_created"]
        issued = metrics["DTC_L1_io_lower_issued"]
        responses = metrics["DTC_L1_io_lower_responses"]
        if not (lower == issued == responses):
            raise ValueError(f"{workload}: accepted terminal lower accounting is unequal")
        duplicate = metrics["DTC_L1_io_duplicate_after_eviction"]
        pending = metrics["DTC_L1_io_pending_hits"]
        evictions = metrics["DTC_L1_io_tag_evictions"]
        share = rate(duplicate, lower)
        escape = rate(duplicate, duplicate + pending)
        per_eviction = rate(duplicate, evictions)
        rows.append(
            {
                "workload": workload,
                "accepted_fast64_commit": FROZEN_FAST64_COMMIT,
                "accepted_registry_path": relative(PRIMARY_REGISTRY),
                "accepted_registry_sha256": sha256(PRIMARY_REGISTRY),
                "accepted_evidence_path": relative(evidence),
                "accepted_evidence_sha256": actual_hash,
                "accepted_core_sha": item["core_sha"],
                "accepted_runtime_binary_sha256": item["runtime_binary_sha256"],
                "accepted_framework_sha": item["framework_sha"],
                "acceptance_status": item["acceptance_status"],
                "cycles": str(metrics["gpu_tot_sim_cycle"]),
                "instructions": str(metrics["gpu_tot_sim_insn"]),
                "io_lower_created": str(lower),
                "io_lower_issued": str(issued),
                "io_lower_responses": str(responses),
                "io_pending_hits": str(pending),
                "io_tag_evictions": str(evictions),
                "io_duplicate_after_eviction": str(duplicate),
                "io_physical_allocations": str(metrics["DTC_L1_io_physical_allocations"]),
                "l1_accesses": str(metrics["L1D_total_cache_accesses"]),
                "l1_misses": str(metrics["L1D_total_cache_misses"]),
                "l2_accesses": str(metrics["L2_total_cache_accesses"]),
                "l2_misses": str(metrics["L2_total_cache_misses"]),
                "l2_reservation_fails": str(metrics["L2_total_cache_reservation_fails"]),
                "global_reads": str(metrics["gpgpu_n_mem_read_global"]),
                "global_writes": str(metrics["gpgpu_n_mem_write_global"]),
                "duplicate_share_of_lower": decimal(share),
                "duplicate_share_of_lower_percent": percentage(share),
                "duplicate_share_denominator_status": denominator_status(lower),
                "duplicate_escape_fraction": decimal(escape),
                "duplicate_escape_fraction_percent": percentage(escape),
                "duplicate_escape_denominator_status": denominator_status(duplicate + pending),
                "duplicate_per_tag_eviction": decimal(per_eviction),
                "duplicate_per_tag_eviction_percent": percentage(per_eviction),
                "duplicate_per_tag_eviction_denominator_status": denominator_status(evictions),
                "duplicate_lower_request_payload_bytes": str(duplicate * 128),
                "duplicate_payload_byte_scope": (
                    "SOURCE_PROVEN_128B_REQUEST_PAYLOAD_ONLY_NOT_TOTAL_LINK_TRAFFIC"
                ),
                "ratio_interpretation": "DESCRIPTIVE_EVENT_RATIO_NOT_PROBABILITY",
                "evidence_class": "EXISTING_DATA_DERIVED_ANALYSIS",
            }
        )
    return rows


def physical_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    cells = read_tsv(STAGE6_CELLS)
    selected = [
        cell
        for cell in cells
        if cell["dimension"] == "physical" and cell["mode"] == "IO"
    ]
    expected_counts = {"BICG": 4, "GESUMMV": 4, "Btree": 5}
    actual_counts: dict[str, int] = defaultdict(int)
    for cell in selected:
        actual_counts[cell["workload"]] += 1
    if dict(actual_counts) != expected_counts:
        raise ValueError(f"unexpected accepted physical IO matrix: {dict(actual_counts)}")

    for cell in sorted(selected, key=lambda row: (row["workload"], float(row["point"]))):
        evidence = ROOT / cell["evidence_path"]
        if sha256(evidence) != cell["evidence_sha256"]:
            raise ValueError(f"Stage6 evidence SHA mismatch: {evidence}")
        metrics = metric_bundle(load_json(evidence)["metrics"], f"{cell['workload']}@{cell['point']}")
        lower = metrics["DTC_L1_io_lower_created"]
        duplicate = metrics["DTC_L1_io_duplicate_after_eviction"]
        pending = metrics["DTC_L1_io_pending_hits"]
        evictions = metrics["DTC_L1_io_tag_evictions"]
        instructions = metrics["gpu_tot_sim_insn"]
        cycles = metrics["gpu_tot_sim_cycle"]
        share = rate(duplicate, lower)
        rows.append(
            {
                "workload": cell["workload"],
                "physical_pool_kib": cell["point"],
                "modeled_value": cell["modeled_value"],
                "accepted_fast64_commit": FROZEN_FAST64_COMMIT,
                "accepted_stage6_cells_path": relative(STAGE6_CELLS),
                "accepted_stage6_cells_sha256": sha256(STAGE6_CELLS),
                "accepted_evidence_path": cell["evidence_path"],
                "accepted_evidence_sha256": cell["evidence_sha256"],
                "accepted_config_path": cell["config_path"],
                "accepted_config_sha256": cell["config_sha256"],
                "cycles": str(cycles),
                "instructions": str(instructions),
                "cycles_per_instruction": decimal(rate(cycles, instructions)),
                "io_lower_created": str(lower),
                "lower_requests_per_million_instructions": decimal(rate(lower * 1_000_000, instructions)),
                "io_pending_hits": str(pending),
                "pending_hits_per_lower_request": decimal(rate(pending, lower)),
                "io_tag_evictions": str(evictions),
                "tag_evictions_per_lower_request": decimal(rate(evictions, lower)),
                "io_duplicate_after_eviction": str(duplicate),
                "duplicate_share_of_lower": decimal(share),
                "duplicate_share_of_lower_percent": percentage(share),
                "duplicate_escape_fraction": decimal(rate(duplicate, duplicate + pending)),
                "duplicate_per_tag_eviction": decimal(rate(duplicate, evictions)),
                "duplicates_per_million_instructions": decimal(rate(duplicate * 1_000_000, instructions)),
                "l2_misses": str(metrics["L2_total_cache_misses"]),
                "l2_misses_per_lower_request": decimal(rate(metrics["L2_total_cache_misses"], lower)),
                "l2_reservation_fails": str(metrics["L2_total_cache_reservation_fails"]),
                "l2_reservation_fails_per_lower_request": decimal(rate(metrics["L2_total_cache_reservation_fails"], lower)),
                "global_reads": str(metrics["gpgpu_n_mem_read_global"]),
                "global_writes": str(metrics["gpgpu_n_mem_write_global"]),
                "normalization_note": (
                    "All event rates use per-lower-request or per-million-instruction "
                    "exposure; cycles_per_instruction is a time/exposure ratio."
                ),
                "evidence_class": "EXISTING_DATA_DERIVED_ANALYSIS",
            }
        )
    return rows


def oo_semantic_gap_rows() -> list[dict[str, str]]:
    """Fail closed if accepted OO compact rows expose an exact counter.

    `DTC_L1_oo_new_misses` is deliberately recorded as an available but rejected
    proxy: it counts every OO new miss and cannot identify the IO event sequence
    of a pending Tag eviction followed by pre-response same-line reallocation.
    """
    expected_workloads = accepted_fast12_workloads()
    expected_hashes = expected_primary_evidence_hashes()
    registry = read_tsv(PRIMARY_REGISTRY)
    oo = [
        row
        for row in registry
        if row["mode"] == "OO" and row["acceptance_status"] == "STRICT_TERMINAL_ACCEPTED"
    ]
    by_workload = {row["workload"]: row for row in oo}
    if len(oo) != 12 or set(by_workload) != set(expected_workloads):
        raise ValueError("primary OO registry is not the exact accepted FAST12 set")

    output: list[dict[str, str]] = []
    for workload in expected_workloads:
        item = by_workload[workload]
        evidence = GENERATED / item["evidence_path"]
        actual_hash = sha256(evidence)
        if actual_hash != expected_hashes.get((workload, "OO")):
            raise ValueError(f"accepted OO compact evidence SHA mismatch: {evidence}")
        metrics = load_json(evidence)["metrics"]
        exact_counter = "DTC_L1_oo_duplicate_after_eviction"
        if exact_counter in metrics:
            raise ValueError(
                f"{workload}: accepted OO evidence unexpectedly exposes {exact_counter}; "
                "the semantic-gap conclusion must be re-audited"
            )
        output.append(
            {
                "workload": workload,
                "accepted_fast64_commit": FROZEN_FAST64_COMMIT,
                "accepted_registry_path": relative(PRIMARY_REGISTRY),
                "accepted_evidence_path": relative(evidence),
                "accepted_evidence_sha256": actual_hash,
                "accepted_core_sha": item["core_sha"],
                "exact_oo_counter": exact_counter,
                "exact_oo_counter_in_accepted_compact_row": "ABSENT",
                "available_but_rejected_proxy": "DTC_L1_oo_new_misses",
                "proxy_disposition": "NOT_EQUIVALENT_DO_NOT_INFER_DUPLICATES",
                "required_observer_counter": exact_counter,
                "evidence_class": "INSUFFICIENT",
            }
        )
    return output


CORRELATION_METRICS = (
    "physical_pool_kib",
    "pending_hits_per_lower_request",
    "tag_evictions_per_lower_request",
    "l2_misses_per_lower_request",
    "l2_reservation_fails_per_lower_request",
    "lower_requests_per_million_instructions",
    "cycles_per_instruction",
)


def numerical(row: dict[str, str], key: str) -> float:
    value = row[key]
    if value == "UNDEFINED_ZERO_DENOMINATOR":
        raise ValueError(f"cannot correlate undefined value {key}")
    return float(value)


def pearson(x: list[float], y: list[float]) -> float | None:
    if len(x) != len(y) or len(x) < 2:
        return None
    mean_x = sum(x) / len(x)
    mean_y = sum(y) / len(y)
    xx = sum((value - mean_x) ** 2 for value in x)
    yy = sum((value - mean_y) ** 2 for value in y)
    if xx == 0.0 or yy == 0.0:
        return None
    return sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y)) / math.sqrt(xx * yy)


def correlation_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    scopes: list[tuple[str, list[dict[str, str]]]] = [("POOLED_13_POINTS", rows)]
    for workload in ("BICG", "GESUMMV", "Btree"):
        scopes.append((f"WITHIN_{workload}", [row for row in rows if row["workload"] == workload]))

    demeaned: list[dict[str, str]] = []
    for workload in ("BICG", "GESUMMV", "Btree"):
        group = [row for row in rows if row["workload"] == workload]
        means = {
            key: sum(numerical(row, key) for row in group) / len(group)
            for key in ("duplicate_share_of_lower",) + CORRELATION_METRICS
        }
        for row in group:
            demeaned.append(
                {
                    key: f"{numerical(row, key) - means[key]:.17g}"
                    for key in ("duplicate_share_of_lower",) + CORRELATION_METRICS
                }
            )
    scopes.append(("WITHIN_WORKLOAD_DEMEANED_13_POINTS", demeaned))

    output: list[dict[str, str]] = []
    for scope, scoped_rows in scopes:
        target = [numerical(row, "duplicate_share_of_lower") for row in scoped_rows]
        for metric in CORRELATION_METRICS:
            coefficient = pearson(target, [numerical(row, metric) for row in scoped_rows])
            output.append(
                {
                    "scope": scope,
                    "n_points": str(len(scoped_rows)),
                    "outcome": "duplicate_share_of_lower",
                    "predictor": metric,
                    "pearson_r": "UNDEFINED_CONSTANT_SERIES" if coefficient is None else f"{coefficient:.9f}",
                    "interpretation": (
                        "DESCRIPTIVE_ASSOCIATION_ONLY_NOT_CAUSAL_AND_SMALL_N"
                    ),
                    "evidence_class": "MEASURED_CORRELATION",
                }
            )
    return output


def input_manifest() -> list[dict[str, str]]:
    inputs = (
        ("accepted_FAST12_membership", FAST12_SUMMARY),
        ("accepted_FAST12_IO_registry", PRIMARY_REGISTRY),
        ("accepted_FAST12_primary_row_hash_bindings", PRIMARY_EVIDENCE_MANIFEST),
        ("accepted_Stage6_physical_IO_registry", STAGE6_CELLS),
    )
    return [
        {
            "accepted_fast64_commit": FROZEN_FAST64_COMMIT,
            "input_role": role,
            "path": relative(path),
            "sha256": sha256(path),
            "evidence_class": "ACCEPTED_FAST64_EVIDENCE",
        }
        for role, path in inputs
    ]


def main() -> None:
    primary = primary_rows()
    physical = physical_rows()
    correlations = correlation_rows(physical)
    oo_gap = oo_semantic_gap_rows()
    write_tsv(OUT / "duplicate_miss_fast12_io.tsv", primary, list(primary[0]))
    write_tsv(
        OUT / "duplicate_miss_stage6_io_physical.tsv", physical, list(physical[0])
    )
    write_tsv(
        OUT / "duplicate_miss_stage6_io_correlations.tsv",
        correlations,
        list(correlations[0]),
    )
    write_tsv(OUT / "duplicate_miss_oo_semantic_gap.tsv", oo_gap, list(oo_gap[0]))
    manifest = input_manifest()
    write_tsv(OUT / "duplicate_miss_input_manifest.tsv", manifest, list(manifest[0]))


if __name__ == "__main__":
    main()
