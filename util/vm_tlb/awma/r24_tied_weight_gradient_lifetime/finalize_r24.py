#!/usr/bin/env python3
"""CPU-only R24 decision finalization from frozen Native formal tables."""

import argparse
import csv
import hashlib
import json
import statistics
from pathlib import Path


ARMS = ("B0_STRONG", "S1_LATE_FULL", "S2_LATE_TILED")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def med(values):
    return statistics.median(values)


def mad(values):
    center = med(values)
    return med([abs(value - center) for value in values])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, required=True)
    args = ap.parse_args()
    timing_path = args.raw / "FORMAL_TARGET_TIMING.tsv"
    memory_path = args.raw / "MEMORY_ACCOUNTING.tsv"
    with timing_path.open() as f:
        timing = list(csv.DictReader(f, delimiter="\t"))
    with memory_path.open() as f:
        memory = {r["arm"]: r for r in csv.DictReader(f, delimiter="\t")}

    def values(group, arm):
        return [
            float(r["target_gpu_ms"])
            for r in timing
            if int(r["group"]) == group and r["arm"] == arm
        ]

    def stable_counts(candidate, baseline):
        benefit = regression = 0
        details = []
        for group in range(3):
            c, b = values(group, candidate), values(group, baseline)
            gap = med(b) - med(c)
            gate = 3 * max(mad(c), mad(b))
            benefit += gap > gate
            regression += -gap > gate
            details.append(
                {
                    "group": group,
                    "baseline_median_ms": med(b),
                    "candidate_median_ms": med(c),
                    "baseline_minus_candidate_ms": gap,
                    "three_x_larger_MAD_ms": gate,
                    "stable_benefit": gap > gate,
                    "stable_regression": -gap > gate,
                }
            )
        return benefit, regression, details

    b0_benefit, b0_regression, b0_details = stable_counts(
        "S2_LATE_TILED", "B0_STRONG"
    )
    s1_benefit, s1_regression, s1_details = stable_counts(
        "S2_LATE_TILED", "S1_LATE_FULL"
    )
    no_full = memory["S2_LATE_TILED"][
        "formal_full_dense_gradient_materialized"
    ] == "False"
    peaks = {
        arm: int(float(memory[arm]["median_target_peak_allocated_bytes"]))
        for arm in ARMS
    }
    memory_reduction = no_full and peaks["S2_LATE_TILED"] < min(
        peaks["B0_STRONG"], peaks["S1_LATE_FULL"]
    )
    if memory_reduction and (b0_regression >= 2 or s1_regression >= 2):
        decision = "R24_CAPACITY_TIME_TRADEOFF"
    elif (
        memory_reduction
        and b0_regression < 2
        and s1_regression < 2
        and (b0_benefit >= 2 or s1_benefit >= 2)
    ):
        decision = "R24_TILED_DELAYED_UPDATE_NET_RESPONSE_PRESENT"
    elif not memory_reduction:
        decision = "R24_TIED_WEIGHT_GRADIENT_PATH_NOT_BENEFICIAL"
    else:
        decision = "R24_TIED_WEIGHT_GRADIENT_PATH_NOT_BENEFICIAL"

    result = {
        "decision": decision,
        "formal_target_timing_sha256": sha(timing_path),
        "memory_accounting_sha256": sha(memory_path),
        "s2_no_full_gradient_all_formal": no_full,
        "s2_memory_reduction": memory_reduction,
        "median_target_peak_allocated_bytes": peaks,
        "s2_stable_benefit_groups_vs_b0": b0_benefit,
        "s2_stable_regression_groups_vs_b0": b0_regression,
        "s2_stable_benefit_groups_vs_s1": s1_benefit,
        "s2_stable_regression_groups_vs_s1": s1_regression,
        "s2_vs_b0_groups": b0_details,
        "s2_vs_s1_groups": s1_details,
        "decision_rule": "capacity tradeoff requires stable regression in at least two groups; net response admits mixed-vs-B0 when S2 has clear memory reduction and stable benefit in at least two groups without two-group regression",
        "gpu_rerun_for_finalization": False,
    }
    (args.raw / "DECISION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
