#!/usr/bin/env python3
"""Regression checks for the POST-FAST64 Lane-C derived-data generator."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "util/dtc_l1/generate_post_fast64_duplicate_miss.py"
SPEC = importlib.util.spec_from_file_location("duplicate_miss", MODULE_PATH)
assert SPEC and SPEC.loader
duplicate_miss = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(duplicate_miss)


def main() -> None:
    primary = duplicate_miss.primary_rows()
    assert len(primary) == 12
    by_workload = {row["workload"]: row for row in primary}
    assert set(by_workload) == {
        "ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree",
        "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q",
    }
    for row in primary:
        assert row["io_lower_created"] == row["io_lower_issued"]
        assert row["io_lower_created"] == row["io_lower_responses"]
        assert int(row["duplicate_lower_request_payload_bytes"]) == (
            128 * int(row["io_duplicate_after_eviction"])
        )
        assert row["ratio_interpretation"] == "DESCRIPTIVE_EVENT_RATIO_NOT_PROBABILITY"
    assert by_workload["2DConvolution"]["io_duplicate_after_eviction"] == "1425269"
    assert by_workload["Gaussian"]["duplicate_share_of_lower_percent"] == "50.199679669"
    assert by_workload["NN"]["duplicate_per_tag_eviction"] == "UNDEFINED_ZERO_DENOMINATOR"
    assert by_workload["MRI-Q"]["duplicate_escape_fraction"] == "UNDEFINED_ZERO_DENOMINATOR"
    duplicates = sum(int(row["io_duplicate_after_eviction"]) for row in primary)
    lower_created = sum(int(row["io_lower_created"]) for row in primary)
    assert duplicates == 3_858_174
    assert lower_created == 80_920_595
    assert round(100 * duplicates / lower_created, 9) == 4.767851744
    shares = [float(row["duplicate_share_of_lower_percent"]) for row in primary]
    assert sum(value < 0.1 for value in shares) == 3
    assert sum(0.1 <= value < 1.0 for value in shares) == 1
    assert sum(1.0 <= value <= 5.0 for value in shares) == 4
    assert sum(value > 5.0 for value in shares) == 4

    physical = duplicate_miss.physical_rows()
    assert len(physical) == 13
    physical_by_key = {(row["workload"], row["physical_pool_kib"]): row for row in physical}
    assert physical_by_key[("BICG", "40")]["io_duplicate_after_eviction"] == "388275"
    assert physical_by_key[("GESUMMV", "48")]["duplicate_share_of_lower_percent"] == "1.823452784"
    assert physical_by_key[("Btree", "16.5")]["io_duplicate_after_eviction"] == "1"

    correlations = duplicate_miss.correlation_rows(physical)
    assert len(correlations) == 35
    pooled = {
        row["predictor"]: row["pearson_r"]
        for row in correlations
        if row["scope"] == "POOLED_13_POINTS"
    }
    assert pooled["l2_misses_per_lower_request"] == "0.906674910"
    assert pooled["pending_hits_per_lower_request"] == "-0.814546309"
    assert all(
        row["interpretation"] == "DESCRIPTIVE_ASSOCIATION_ONLY_NOT_CAUSAL_AND_SMALL_N"
        for row in correlations
    )

    oo_gap = duplicate_miss.oo_semantic_gap_rows()
    assert len(oo_gap) == 12
    assert all(row["exact_oo_counter_in_accepted_compact_row"] == "ABSENT" for row in oo_gap)
    assert all(row["proxy_disposition"] == "NOT_EQUIVALENT_DO_NOT_INFER_DUPLICATES" for row in oo_gap)

    manifest = duplicate_miss.input_manifest()
    assert len(manifest) == 4
    assert all(row["evidence_class"] == "ACCEPTED_FAST64_EVIDENCE" for row in manifest)


if __name__ == "__main__":
    main()
