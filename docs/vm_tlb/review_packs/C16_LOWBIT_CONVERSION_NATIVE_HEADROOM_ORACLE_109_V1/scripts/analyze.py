#!/usr/bin/env python3
"""Deterministic CPU analysis for A/B/C timing and headroom gate."""

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
    out = []
    for _ in range(n):
        sample = [values[rng.randrange(len(values))] for _ in values]
        out.append(statistics.median(sample))
    return percentile(out, 0.025), percentile(out, 0.975)


def bootstrap_ratio(a, b, rng, n=10000):
    out = []
    for _ in range(n):
        sa = [a[rng.randrange(len(a))] for _ in a]
        sb = [b[rng.randrange(len(b))] for _ in b]
        out.append(statistics.median(sa) / statistics.median(sb))
    return percentile(out, 0.025), percentile(out, 0.975)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    values = {}
    with (args.raw / "TIMING_SAMPLES.tsv").open(newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            values.setdefault((row["target"], row["condition"]), []).append(float(row["ms"]))
    rng = random.Random(20260929)
    stats = {}
    rows = []
    for key in sorted(values):
        vals = values[key]
        ci = bootstrap_median(vals, rng)
        item = {"n": len(vals), "median_ms": statistics.median(vals), "mean_ms": statistics.mean(vals),
                "cv": statistics.pstdev(vals) / statistics.mean(vals),
                "sample_p2_5_ms": percentile(vals, 0.025), "sample_p97_5_ms": percentile(vals, 0.975),
                "bootstrap_median_ci95_low_ms": ci[0], "bootstrap_median_ci95_high_ms": ci[1],
                "min_ms": min(vals), "max_ms": max(vals)}
        stats[f"{key[0]}:{key[1]}"] = item
        rows.append((key[0], key[1], *item.values()))
    a, b, c = (values[("discovery", x)] for x in ("A", "B", "C"))
    oracle_ci = bootstrap_ratio(a, b, rng)
    predecoded_ci = bootstrap_ratio(a, c, rng)
    gate = json.loads((args.raw / "DISCOVERY_GATE.json").read_text())
    correctness = list(csv.DictReader((args.raw / "CORRECTNESS.tsv").open(newline=""), delimiter="\t"))[0]
    result = {
        "status": "NO_LOCAL_ORACLE_HEADROOM_STOP_VALIDATION",
        "validation_executed": False,
        "discovery_gate": gate,
        "statistics": stats,
        "local_oracle_speedup": statistics.median(a) / statistics.median(b),
        "local_oracle_speedup_bootstrap_ci95": list(oracle_ci),
        "predecoded_speedup_vs_baseline": statistics.median(a) / statistics.median(c),
        "predecoded_speedup_bootstrap_ci95": list(predecoded_ci),
        "expanded_weight_bytes": int(correctness["expanded_weight_bytes"]),
        "compressed_weight_bytes": int(correctness["compressed_weight_bytes"]),
        "expansion_ratio": int(correctness["expanded_weight_bytes"]) / int(correctness["compressed_weight_bytes"]),
        "correctness": {"baseline_authority_pass": correctness["baseline_authority_pass"] == "True",
                        "predecoded_correct": correctness["predecoded_correct"] == "True",
                        "predecoded_max_abs": float(correctness["predecoded_max_abs"]),
                        "oracle_status": correctness["oracle_status"]},
        "interpretation": "Conversion half-ops are not exposed as positive local headroom under this isolated oracle; the oracle dependency path is slower. Correct predecode is only a separate representation/kernel diagnostic.",
    }
    with (args.out / "MEASUREMENT_STATISTICS.tsv").open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(("target", "condition", "n", "median_ms", "mean_ms", "cv", "sample_p2_5_ms", "sample_p97_5_ms", "bootstrap_median_ci95_low_ms", "bootstrap_median_ci95_high_ms", "min_ms", "max_ms"))
        for target, condition, *vals in rows:
            w.writerow((target, condition, *vals))
    (args.out / "HEADROOM_SUMMARY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "oracle_speedup": result["local_oracle_speedup"],
                      "oracle_ci95": oracle_ci, "predecoded_speedup": result["predecoded_speedup_vs_baseline"],
                      "predecoded_ci95": predecoded_ci}, sort_keys=True))


if __name__ == "__main__":
    main()
