#!/usr/bin/env python3
"""Target-agnostic deterministic timing statistics for B0/O1/O2 samples."""

import argparse
import csv
import json
from pathlib import Path
import random
import statistics


def percentile(values, p):
    x = sorted(values)
    pos = (len(x) - 1) * p
    lo, hi = int(pos), min(int(pos) + 1, len(x) - 1)
    frac = pos - lo
    return x[lo] * (1 - frac) + x[hi] * frac


def bootstrap_median(values, rng, n=10000):
    medians = []
    for _ in range(n):
        medians.append(statistics.median(values[rng.randrange(len(values))] for _ in values))
    return percentile(medians, 0.025), percentile(medians, 0.975)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--samples", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    cells = {}
    with args.samples.open(newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            cells.setdefault((row["target"], row["condition"]), []).append(float(row["ms"]))
    rng = random.Random(20260930)
    result = {}
    for (target, condition), values in sorted(cells.items()):
        ci = bootstrap_median(values, rng)
        result[f"{target}:{condition}"] = {"n": len(values), "median_ms": statistics.median(values),
            "mean_ms": statistics.mean(values), "cv": statistics.pstdev(values) / statistics.mean(values),
            "q05_ms": percentile(values, 0.05), "q95_ms": percentile(values, 0.95),
            "bootstrap_median_ci95": list(ci), "min_ms": min(values), "max_ms": max(values)}
    args.output.write_text(json.dumps({"status": "PASS", "cells": result}, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
