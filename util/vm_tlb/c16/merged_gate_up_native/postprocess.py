#!/usr/bin/env python3
"""Deterministic ABBA analysis for the cross-runtime B0/B2 strong baseline."""

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
from pathlib import Path


SEED = 20261001
RESAMPLES = 1000


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def quantile(values, q):
    values = sorted(values)
    pos = (len(values) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return values[lo] if lo == hi else values[lo] * (hi - pos) + values[hi] * (pos - lo)


def summary(values):
    mean = statistics.fmean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    return {"count": len(values), "median": statistics.median(values), "mean": mean,
            "stdev": sd, "cv": sd / mean if mean else 0.0,
            "q05": quantile(values, .05), "q95": quantile(values, .95),
            "min": min(values), "max": max(values)}


def metrics(rows, field):
    b0 = [row[field] for row in rows if row["arm"] == "B0"]
    b2 = [row[field] for row in rows if row["arm"] == "B2"]
    m0, m2 = statistics.median(b0), statistics.median(b2)
    return {"b0_median_ms": m0, "b2_median_ms": m2, "saving_ms": m0 - m2,
            "speedup": m0 / m2, "time_reduction_fraction": 1.0 - m2 / m0}


def bootstrap(rows, field):
    rng = random.Random(SEED)
    by_block = {block: [row for row in rows if row["block"] == block] for block in range(12)}
    draws = []
    for _ in range(RESAMPLES):
        sample = []
        for block in (rng.randrange(12) for _ in range(12)):
            sample.extend(by_block[block])
        draws.append(metrics(sample, field))
    return {key: {"q05": quantile([row[key] for row in draws], .05),
                  "q50": quantile([row[key] for row in draws], .50),
                  "q95": quantile([row[key] for row in draws], .95)} for key in draws[0]}


def write_tsv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    order = ("B0", "B2", "B2", "B0")
    rows = []
    local_rows = []
    for block in range(12):
        for position, arm in enumerate(order):
            path = args.raw / f"formal_block{block:02d}_pos{position}_{arm.lower()}.json"
            data = json.loads(path.read_text())
            if data.get("status") != "PASS" or data["generated_token_ids_D0_D3"] != [23578, 11, 323, 3950]:
                raise RuntimeError(f"formal identity failure: {path}")
            if len(data["ffn_occurrences"]) != 112:
                raise RuntimeError(f"FFN closure failure: {path}")
            ffn_sum = sum(row["target_ms"] for row in data["ffn_occurrences"])
            row = {"block": block, "position": position, "arm": arm,
                   "run_index": data["run_index"], "decode_wall_ms": data["decode_wall_ms"],
                   "d0_ms": data["decode_step_ms"][0], "d1_ms": data["decode_step_ms"][1],
                   "d2_ms": data["decode_step_ms"][2], "d3_ms": data["decode_step_ms"][3],
                   "ffn_sum_ms": ffn_sum, "json_sha256": sha256(path), "json_path": str(path)}
            rows.append(row)
            for item in data["ffn_occurrences"]:
                local_rows.append({"block": block, "position": position, "arm": arm,
                                   "run_index": data["run_index"], "layer": item["layer"],
                                   "decode_index": item["decode_index"], "ffn_ms": item["target_ms"]})
    write_tsv(args.output_dir / "NATIVE_TIMING_RAW.tsv", rows)
    write_tsv(args.output_dir / "FFN_LOCAL_TIMING.tsv", local_rows)
    block_rows = []
    for block in range(12):
        value = metrics([row for row in rows if row["block"] == block], "decode_wall_ms")
        block_rows.append({"block": block, "order": "B0,B2,B2,B0", **value})
    write_tsv(args.output_dir / "ABBA_BLOCK_SUMMARY.tsv", block_rows)
    primary = metrics(rows, "decode_wall_ms")
    primary_boot = bootstrap(rows, "decode_wall_ms")
    ffn = metrics(rows, "ffn_sum_ms")
    ffn_boot = bootstrap(rows, "ffn_sum_ms")
    result = {
        "status": "PASS", "comparison_class": "cross-runtime strong baseline; not merge-only strict A/B",
        "protocol": {"blocks": 12, "order": "B0,B2,B2,B0", "fresh_process": True,
                     "b0_samples": 24, "b2_samples": 24},
        "primary_endpoint": "complete natural D0-D3 CUDA-event wall",
        "arm_summaries_ms": {arm: summary([row["decode_wall_ms"] for row in rows if row["arm"] == arm]) for arm in ("B0", "B2")},
        "observed": primary,
        "bootstrap": {"unit": "complete ABBA block", "resamples": RESAMPLES,
                      "seed": SEED, "interval_quantiles": primary_boot},
    }
    (args.output_dir / "BOOTSTRAP_RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    ffn_result = {
        "status": "PASS", "metric": "sum of per-layer per-decode FFN CUDA-event intervals",
        "arm_summaries_ms": {arm: summary([row["ffn_sum_ms"] for row in rows if row["arm"] == arm]) for arm in ("B0", "B2")},
        "observed": ffn, "bootstrap": {"unit": "complete ABBA block", "resamples": RESAMPLES,
                                         "seed": SEED, "interval_quantiles": ffn_boot},
        "interpretation_boundary": "includes runtime backend, merged projection, reduction path, and SiluAndMul differences",
    }
    (args.output_dir / "FFN_LOCAL_ANALYSIS.json").write_text(json.dumps(ffn_result, indent=2, sort_keys=True) + "\n")
    q05 = primary_boot["saving_ms"]["q05"]
    q95 = primary_boot["saving_ms"]["q95"]
    if q05 > 0:
        decision = "MATURE_MERGED_SOFTWARE_BASELINE_DOMINATES_SEPARATED_RUNTIME"
    elif q95 < 0:
        decision = "MERGED_RUNTIME_SLOWER_NEGATIVE_RESULT"
    else:
        decision = "CROSS_RUNTIME_STRONG_BASELINES_NOT_SEPARATED_BY_BOOTSTRAP_INTERVAL"
    final = {
        "status": "PASS", "decision": decision,
        "whole_decode": primary, "ffn_local": ffn,
        "whole_decode_bootstrap": primary_boot, "ffn_local_bootstrap": ffn_boot,
        "claim_boundary": "B0/B2 delta is not wholly attributable to gate/up merge",
        "plain_concurrency_or_hardware_story": "NOT_ESTABLISHED",
        "automatic_followup": False,
    }
    (args.output_dir / "FINAL_DECISION.json").write_text(json.dumps(final, indent=2, sort_keys=True) + "\n")
    print(json.dumps(final, sort_keys=True))


if __name__ == "__main__":
    main()
