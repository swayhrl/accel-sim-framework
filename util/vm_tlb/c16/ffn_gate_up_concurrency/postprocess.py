#!/usr/bin/env python3
"""Deterministic block-aware analysis for the frozen B0/B1 ABBA campaign."""

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
ORACLE_SAVING_MS = 7.732849


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def quantile(values, q):
    values = sorted(values)
    if not values:
        raise ValueError("empty quantile")
    position = (len(values) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return values[lower]
    return values[lower] * (upper - position) + values[upper] * (position - lower)


def summary(values):
    mean = statistics.fmean(values)
    return {"count": len(values), "median": statistics.median(values),
            "mean": mean, "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
            "cv": statistics.stdev(values) / mean if len(values) > 1 and mean else 0.0,
            "min": min(values), "max": max(values), "q05": quantile(values, 0.05),
            "q95": quantile(values, 0.95)}


def write_tsv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def arm_metrics(rows, field):
    b0 = [row[field] for row in rows if row["arm"] == "B0"]
    b1 = [row[field] for row in rows if row["arm"] == "B1"]
    m0, m1 = statistics.median(b0), statistics.median(b1)
    return m0, m1, m0 - m1, m0 / m1, (m0 - m1) / m0


def bootstrap(rows, field, rng):
    by_block = {block: [row for row in rows if row["block"] == block] for block in range(12)}
    draws = []
    for _ in range(RESAMPLES):
        sampled = []
        for block in (rng.randrange(12) for _ in range(12)):
            sampled.extend(by_block[block])
        b0, b1, saving, speedup, reduction = arm_metrics(sampled, field)
        draws.append({"b0_median_ms": b0, "b1_median_ms": b1, "saving_ms": saving,
                      "speedup": speedup, "time_reduction_fraction": reduction})
    return {key: {"q05": quantile([row[key] for row in draws], 0.05),
                  "q50": quantile([row[key] for row in draws], 0.50),
                  "q95": quantile([row[key] for row in draws], 0.95)}
            for key in draws[0]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    manifest = []
    expected_sequence = ("B0", "B1", "B1", "B0")
    for block in range(12):
        for position, arm in enumerate(expected_sequence):
            path = args.raw / f"formal_block{block:02d}_pos{position}_{arm.lower()}.json"
            data = json.loads(path.read_text())
            expected_flag = "off" if arm == "B0" else "on"
            if data.get("status") != "PASS" or data.get("gate_up_concurrency") != expected_flag:
                raise RuntimeError(f"arm/status mismatch: {path}")
            if data["generated_token_ids_D0_D3"] != [23578, 11, 323, 3950]:
                raise RuntimeError(f"token mismatch: {path}")
            if len(data["occurrences"]) != 336 or len(data["call_order"]) != 420:
                raise RuntimeError(f"identity count mismatch: {path}")
            by_role = {role: [item["target_ms"] for item in data["occurrences"] if item["role"] == role]
                       for role in ("gate_proj", "up_proj", "down_proj")}
            heldout = {role: [item["target_ms"] for item in data["occurrences"]
                              if item["role"] == role and 14 <= item["layer"] <= 27]
                       for role in ("gate_proj", "up_proj")}
            row = {"block": block, "position": position, "arm": arm,
                   "run_index": data["run_index"], "decode_wall_ms": data["decode_wall_ms"],
                   "d3_step_ms": data["decode_step_ms"][3],
                   "gate_occurrence_median_ms": statistics.median(by_role["gate_proj"]),
                   "up_occurrence_median_ms": statistics.median(by_role["up_proj"]),
                   "down_occurrence_median_ms": statistics.median(by_role["down_proj"]),
                   "heldout_l14_27_gate_median_ms": statistics.median(heldout["gate_proj"]),
                   "heldout_l14_27_up_median_ms": statistics.median(heldout["up_proj"]),
                   "json_sha256": sha256(path), "json_path": str(path)}
            rows.append(row)
            manifest.append({"path": str(path), "sha256": row["json_sha256"], "bytes": path.stat().st_size,
                             "block": block, "position": position, "arm": arm})
    write_tsv(args.output_dir / "RAW_TIMING_SAMPLES.tsv", tuple(rows[0]), rows)
    block_rows = []
    for block in range(12):
        subset = [row for row in rows if row["block"] == block]
        b0, b1, saving, speedup, reduction = arm_metrics(subset, "decode_wall_ms")
        block_rows.append({"block": block, "order": "B0,B1,B1,B0", "b0_mean_ms": b0,
                           "b1_mean_ms": b1, "saving_ms": saving, "speedup": speedup,
                           "time_reduction_fraction": reduction})
    write_tsv(args.output_dir / "ABBA_BLOCK_SUMMARY.tsv", tuple(block_rows[0]), block_rows)
    rng = random.Random(SEED)
    primary_boot = bootstrap(rows, "decode_wall_ms", rng)
    b0, b1, saving, speedup, reduction = arm_metrics(rows, "decode_wall_ms")
    primary = {
        "status": "PASS", "metric": "native CUDA-event complete D0-D3 wall time",
        "arm_summaries_ms": {arm: summary([row["decode_wall_ms"] for row in rows if row["arm"] == arm])
                             for arm in ("B0", "B1")},
        "observed": {"b0_median_ms": b0, "b1_median_ms": b1, "saving_ms": saving,
                     "speedup": speedup, "time_reduction_fraction": reduction},
        "bootstrap": {"unit": "complete four-position ABBA block", "blocks": 12,
                      "resamples": RESAMPLES, "seed": SEED, "interval_quantiles": primary_boot},
    }
    (args.output_dir / "PRIMARY_BOOTSTRAP.json").write_text(json.dumps(primary, indent=2, sort_keys=True) + "\n")
    duration_fields = ("gate_occurrence_median_ms", "up_occurrence_median_ms")
    duration = {}
    duration_rows = []
    for field in duration_fields:
        d0, d1, ds, ratio, dr = arm_metrics(rows, field)
        boot = bootstrap(rows, field, rng)
        role = field.split("_")[0]
        duration[role] = {"b0_median_ms": d0, "b1_median_ms": d1, "b1_over_b0": d1 / d0,
                          "b0_over_b1": ratio, "bootstrap": boot}
        duration_rows.append({"role": role, "b0_median_ms": d0, "b1_median_ms": d1,
                              "b1_over_b0": d1 / d0,
                              "b1_over_b0_q05": 1.0 / boot["speedup"]["q95"],
                              "b1_over_b0_q50": 1.0 / boot["speedup"]["q50"],
                              "b1_over_b0_q95": 1.0 / boot["speedup"]["q05"]})
    write_tsv(args.output_dir / "KERNEL_DURATION_RESPONSE.tsv", tuple(duration_rows[0]), duration_rows)
    (args.output_dir / "KERNEL_DURATION_RESPONSE.json").write_text(json.dumps(duration, indent=2, sort_keys=True) + "\n")
    canary = json.loads((args.raw / "B0_B1_TIMELINE_CANARY.json").read_text())
    overlap_positive = canary["b1_positive_overlap_occurrences"] > 0
    material = primary_boot["saving_ms"]["q05"] > 0 and saving / ORACLE_SAVING_MS >= 0.50
    significant_inflation = any(row["b1_over_b0_q05"] > 1.0 for row in duration_rows)
    if material:
        decision = "STRONG_SOFTWARE_CONCURRENCY_REALIZES_ORACLE_MATERIALLY"
    elif overlap_positive and significant_inflation:
        decision = "CONCURRENCY_ACTIVATED_BUT_RESOURCE_CONTENTION_LIMITED"
    elif overlap_positive:
        decision = "ORACLE_GAP_NOT_EXPLAINED_BY_SIMPLE_KERNEL_SLOWDOWN"
    else:
        decision = "TWO_STREAM_BASELINE_NOT_ACTIVATED"
    realization = {
        "lane6_oracle_saving_reference_ms": ORACLE_SAVING_MS,
        "native_observed_saving_ms": saving,
        "oracle_realization_fraction": saving / ORACLE_SAVING_MS,
        "material_gate": {"saving_bootstrap_q05_positive": primary_boot["saving_ms"]["q05"] > 0,
                          "oracle_realization_at_least_50_percent": saving / ORACLE_SAVING_MS >= 0.50,
                          "pass": material},
        "negative_result_preserved": saving < 0,
    }
    (args.output_dir / "ORACLE_REALIZATION.json").write_text(json.dumps(realization, indent=2, sort_keys=True) + "\n")
    d3_b0, d3_b1, d3_saving, d3_speedup, d3_reduction = arm_metrics(rows, "d3_step_ms")
    heldout = {
        "status": "PASS", "uses_formal_samples_only": True, "additional_gpu_runs": False,
        "d3_whole_step": {"b0_median_ms": d3_b0, "b1_median_ms": d3_b1,
                          "saving_ms": d3_saving, "speedup": d3_speedup,
                          "time_reduction_fraction": d3_reduction,
                          "bootstrap": bootstrap(rows, "d3_step_ms", rng)},
        "layers_14_27": {},
        "overlap_evidence_source": "the frozen B1 timeline canary subset; no additional NSYS run",
    }
    for role in ("gate", "up"):
        field = f"heldout_l14_27_{role}_median_ms"
        h0, h1, hs, hspeed, hreduction = arm_metrics(rows, field)
        heldout["layers_14_27"][role] = {"b0_median_ms": h0, "b1_median_ms": h1,
                                                  "b1_over_b0": h1 / h0,
                                                  "bootstrap": bootstrap(rows, field, rng)}
    (args.output_dir / "HELDOUT_VALIDATION.json").write_text(json.dumps(heldout, indent=2, sort_keys=True) + "\n")
    final = {"status": "PASS" if decision != "TWO_STREAM_BASELINE_NOT_ACTIVATED" else decision,
             "decision": decision, "b1_overlap_activated": overlap_positive,
             "significant_kernel_duration_inflation": significant_inflation,
             "primary_saving_ms": saving, "primary_speedup": speedup,
             "oracle_realization_fraction": saving / ORACLE_SAVING_MS,
             "negative_result_preserved": saving < 0,
             "claim_boundary": "local strong-software concurrency diagnostic only; no whole-model or hardware-mechanism claim"}
    (args.output_dir / "FINAL_DECISION.json").write_text(json.dumps(final, indent=2, sort_keys=True) + "\n")
    (args.output_dir / "TIMING_SAMPLE_MANIFEST.json").write_text(json.dumps({"status": "PASS", "files": manifest}, indent=2, sort_keys=True) + "\n")
    print(json.dumps(final, sort_keys=True))
    if decision == "TWO_STREAM_BASELINE_NOT_ACTIVATED":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
