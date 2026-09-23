#!/usr/bin/env python3
"""Validate and summarize the V1 structural-signature catalog without recapture."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--v2-inventory", type=Path, required=True)
    parser.add_argument("--lane-c-inventory", type=Path, required=True)
    args = parser.parse_args()
    assert sha256(args.v2_inventory) == "222d5dfeeb1e7aaae3423f13873053c37c27f5c6290d8a58bd3186a0803ca77a"
    assert sha256(args.lane_c_inventory) == "7041c0aedc6e5c066530f4a412192fee9011c69301018b15e4e829c963cdeed0"
    catalog = read(args.catalog)
    structural = [row for row in catalog if row["catalog_row_type"] == "STRUCTURAL_STRATUM"]
    native = [row for row in catalog if row["catalog_row_type"] == "LANE_C_UNMAPPED_NATIVE_ONLY"]
    assert len(catalog) == 109 and len(structural) == 100 and len(native) == 9
    assert sum(int(row["stratum_launch_count_s2"]) for row in structural) == 34677
    assert sum(int(row["stratum_accumulated_gpu_duration_ns"]) for row in structural) == 154876910
    assert all(row["cross_context_label"] == "UNTESTED_ACROSS_CONTEXT" for row in structural)
    assert all(row["performance_weight_label"] == "SCENARIO_SPECIFIC" for row in structural)
    assert all(row["lane_c_asset_status"] in {"REUSABLE_NOW", "REQUIRES_REQUALIFICATION", "MISSING_SIM_TRACE"} for row in structural)
    assert all(row["lane_c_asset_status"] == "NATIVE_ONLY" for row in native)
    phase = {}
    for row in structural:
        phase[row["phase"]] = (int(row["phase_accumulated_gpu_duration_ns"]), float(row["phase_gpu_time_share_full_s2"]))
    families: dict[tuple[str, str], tuple[int, float, float]] = {}
    for row in structural:
        families[(row["phase"], row["normalized_kernel_family"])] = (
            int(row["family_accumulated_gpu_duration_ns"]),
            float(row["family_gpu_time_share_full_s2"]),
            float(row["family_gpu_time_share_within_phase"]),
        )
    recurrence = defaultdict(lambda: Counter())
    for row in read(args.v2_inventory):
        if row["phase"] == "DECODE":
            recurrence[(row["normalized_kernel_family"], row["grid"], row["block"])][row["decode_step"]] += 1
    wanted = []
    for key, counts in recurrence.items():
        if key[0] in {"CUBLAS_GEMV", "PYTORCH_FLASH_FWD"}:
            values = [counts[str(step)] for step in range(1, 33)]
            wanted.append({"family": key[0], "grid": key[1], "block": key[2], "mean": sum(values) / 32, "min": min(values), "max": max(values), "stable": min(values) == max(values)})
    wanted.sort(key=lambda item: (item["family"], item["grid"], item["block"]))
    status_counts = Counter(row["lane_c_asset_status"] for row in structural)
    print(json.dumps({"phase": phase, "families": {f"{key[0]}::{key[1]}": value for key, value in sorted(families.items())}, "decode_gemv_flash_shape_recurrence": wanted, "asset_status_counts_structural": dict(status_counts)}, sort_keys=True))
    print("STRUCTURAL_SIGNATURE_VALIDATION_PASS")


if __name__ == "__main__":
    main()
