#!/usr/bin/env python3
"""Deterministic, source-field-only AWMA representative-suite selector."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

STATUS = "PROVISIONAL_PRE_GATE"
SEED = "AWMA_REPRESENTATIVE_SUITE_SELECTOR_V1_HOLDOUT_SPLIT"
REQUIRED = {"global_launch_index", "phase", "decode_step", "duration_ns", "grid", "block", "exact_kernel_name", "demangled_kernel_name", "normalized_kernel_family", "semantic_category"}

def clean(value):
    return (value or "").strip() or "UNKNOWN"

def read_inventory(path):
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    missing = REQUIRED - set(rows[0] if rows else [])
    if missing:
        raise ValueError("missing required inventory fields: " + ", ".join(sorted(missing)))
    for row in rows:
        for field in REQUIRED - {"duration_ns"}:
            row[field] = clean(row[field])
        row["phase"] = row["phase"].upper()
        row["duration_ns"] = int(row["duration_ns"])
        row["implementation"] = row["demangled_kernel_name"] if row["demangled_kernel_name"] != "UNKNOWN" else row["exact_kernel_name"]
    return rows

def stratum_key(row):
    return tuple(row[name] for name in ("phase", "normalized_kernel_family", "implementation", "grid", "block"))

def split_partition(row, fraction):
    identity = "|".join((SEED, row["global_launch_index"], *stratum_key(row)))
    value = int(hashlib.sha256(identity.encode()).hexdigest()[:16], 16) / 2**64
    return "HOLDOUT" if value < fraction else "SELECTION"

def med(values):
    return statistics.median(values) if values else 0

def step_behavior(rows):
    if not rows or rows[0]["phase"] != "DECODE":
        return "NOT_APPLICABLE"
    per_step = defaultdict(list)
    for row in rows:
        if row["decode_step"].isdigit():
            per_step[int(row["decode_step"])].append(row["duration_ns"])
    if not per_step:
        return "DECODE_STEP_UNKNOWN"
    steps = sorted(per_step)
    values = [statistics.fmean(per_step[step]) for step in steps]
    n = max(1, len(steps) // 3)
    early, late = statistics.fmean(values[:n]), statistics.fmean(values[-n:])
    complete = "ALL_STEPS" if len(steps) / (steps[-1] - steps[0] + 1) >= .90 else "PARTIAL_STEPS"
    trend = "STABLE" if max(early, late) / max(1, min(early, late)) < 1.10 else ("EARLY_HEAVIER" if early > late else "LATE_HEAVIER")
    return "DECODE_%s_%s" % (complete, trend)

def candidates(rows):
    grouped, family_values = defaultdict(list), defaultdict(list)
    for row in rows:
        grouped[stratum_key(row)].append(row)
        family_values[(row["phase"], row["normalized_kernel_family"])].append(row["duration_ns"])
    family_median = {key: med(values) for key, values in family_values.items()}
    result = []
    for key, group in grouped.items():
        duration_median = med([row["duration_ns"] for row in group])
        rep = min(group, key=lambda row: (abs(row["duration_ns"] - duration_median), int(row["global_launch_index"])))
        phase, family, implementation, grid, block = key
        tags = []
        if phase == "PREFILL" and family == "CUBLAS_GEMM":
            tags.append("PREFILL_GEMM_VARIANT")
        if family == "PYTORCH_FLASH_FWD":
            tags.append("PREFILL_FLASH" if phase == "PREFILL" else "DECODE_FLASH_UNRESOLVED_VARIANT")
        if phase == "DECODE" and family == "CUBLAS_GEMV":
            tags.append("LONG_DECODE_GEMV_OBSERVED" if duration_median >= 2 * family_median[(phase, family)] else "ORDINARY_DECODE_GEMV_OBSERVED")
        result.append({"phase": phase, "family": family, "implementation": implementation, "grid": grid, "block": block, "semantic_category": rep["semantic_category"], "decode_behavior": step_behavior(group), "launch_count": len(group), "duration_ns": sum(row["duration_ns"] for row in group), "median_duration_ns": duration_median, "representative": rep, "tags": tags})
    return result

def candidate_key(candidate):
    return tuple(candidate[name] for name in ("phase", "family", "implementation", "grid", "block"))

def choose(candidates, budget):
    total = sum(item["duration_ns"] for item in candidates)
    family_mass = defaultdict(int)
    for item in candidates:
        family_mass[(item["phase"], item["family"])] += item["duration_ns"]
    forced = defaultdict(list)
    for phase_family, mass in family_mass.items():
        if mass / total >= .002:
            item = max((x for x in candidates if (x["phase"], x["family"]) == phase_family), key=lambda x: (x["duration_ns"], candidate_key(x)))
            forced[candidate_key(item)].append("HIGH_TIME_PHASE_FAMILY")
    for tag in ("LONG_DECODE_GEMV_OBSERVED", "ORDINARY_DECODE_GEMV_OBSERVED", "PREFILL_FLASH", "DECODE_FLASH_UNRESOLVED_VARIANT", "PREFILL_GEMM_VARIANT"):
        tagged = [item for item in candidates if tag in item["tags"]]
        if tagged:
            forced[candidate_key(max(tagged, key=lambda x: (x["duration_ns"], candidate_key(x))))].append(tag)
    for item in candidates:
        mass = family_mass[(item["phase"], item["family"])]
        if mass / total >= .002 and item["duration_ns"] / mass <= .02 and item["duration_ns"] / total >= .0005:
            forced[candidate_key(item)].append("RARE_STRUCTURALLY_DISTINCT")
    selected, selected_keys = [], set()
    for item in sorted(candidates, key=candidate_key):
        if candidate_key(item) in forced:
            item["selection_reason"] = ";".join(sorted(set(forced[candidate_key(item)])))
            selected.append(item)
            selected_keys.add(candidate_key(item))
    while len(selected) < budget:
        choices = [item for item in candidates if candidate_key(item) not in selected_keys]
        if not choices:
            break
        families = {(item["phase"], item["family"]) for item in selected}
        behaviors = {(item["phase"], item["family"], item["decode_behavior"]) for item in selected}
        def score(item):
            value = item["duration_ns"] / total
            value += .05 if (item["phase"], item["family"]) not in families else 0
            value += .01 if (item["phase"], item["family"], item["decode_behavior"]) not in behaviors else 0
            return value, candidate_key(item)
        item = max(choices, key=score)
        item["selection_reason"] = "GREEDY_NATIVE_TIME_AND_DIVERSITY"
        selected.append(item)
        selected_keys.add(candidate_key(item))
    return sorted(selected, key=candidate_key)

def write_tsv(path, rows):
    rows = list(rows)
    columns = list(rows[0]) if rows else ["status"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--budget", type=int, default=24)
    parser.add_argument("--holdout-fraction", type=float, default=.20)
    parser.add_argument("--input-label", default="UNSPECIFIED")
    args = parser.parse_args()
    if not 0 < args.holdout_fraction < .5:
        raise ValueError("holdout fraction must be in (0, .5)")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_inventory(args.inventory)
    for row in rows:
        row["partition"] = split_partition(row, args.holdout_fraction)
    selection_rows = [row for row in rows if row["partition"] == "SELECTION"]
    holdout_rows = [row for row in rows if row["partition"] == "HOLDOUT"]
    all_candidates = candidates(selection_rows)
    selected = choose(all_candidates, args.budget)
    selected_keys = {candidate_key(item) for item in selected}
    suite = []
    for ordinal, item in enumerate(selected, 1):
        row = item["representative"]
        suite.append({"suite_id": "R%02d" % ordinal, "status": STATUS, "global_launch_index": row["global_launch_index"], "phase": item["phase"], "decode_step": row["decode_step"], "normalized_kernel_family": item["family"], "semantic_category": item["semantic_category"], "exact_implementation": item["implementation"], "grid": item["grid"], "block": item["block"], "decode_behavior": item["decode_behavior"], "representative_duration_ns": row["duration_ns"], "stratum_launch_count_selection_pool": item["launch_count"], "stratum_gpu_duration_ns_selection_pool": item["duration_ns"], "observed_tags": ";".join(item["tags"]) or "NONE", "selection_reason": item["selection_reason"]})
    write_tsv(args.output_dir / "SELECTED_SUITE.tsv", suite)
    total = sum(row["duration_ns"] for row in selection_rows)
    coverage = []
    for phase in sorted({row["phase"] for row in selection_rows} | {"ALL_SELECTION_POOL"}):
        phase_rows = selection_rows if phase == "ALL_SELECTION_POOL" else [row for row in selection_rows if row["phase"] == phase]
        covered = [row for row in phase_rows if stratum_key(row) in selected_keys]
        coverage.append({"scope": phase, "selection_pool_duration_ns": sum(row["duration_ns"] for row in phase_rows), "covered_duration_ns": sum(row["duration_ns"] for row in covered), "coverage_share": sum(row["duration_ns"] for row in covered) / sum(row["duration_ns"] for row in phase_rows), "whole_selection_pool_share": sum(row["duration_ns"] for row in phase_rows) / total})
    write_tsv(args.output_dir / "PROVISIONAL_COVERAGE.tsv", coverage)
    holdouts = [{"status": STATUS, "global_launch_index": row["global_launch_index"], "phase": row["phase"], "decode_step": row["decode_step"], "normalized_kernel_family": row["normalized_kernel_family"], "semantic_category": row["semantic_category"], "exact_implementation": row["implementation"], "grid": row["grid"], "block": row["block"], "duration_ns": row["duration_ns"], "validation_rule": "HASH_HOLDOUT_NOT_USED_FOR_SELECTION_OR_TUNING"} for row in holdout_rows]
    write_tsv(args.output_dir / "PROPOSED_HOLDOUTS.tsv", holdouts)
    uncovered = []
    for item in all_candidates:
        if candidate_key(item) not in selected_keys:
            uncovered.append({"status": STATUS, "phase": item["phase"], "normalized_kernel_family": item["family"], "semantic_category": item["semantic_category"], "exact_implementation": item["implementation"], "grid": item["grid"], "block": item["block"], "decode_behavior": item["decode_behavior"], "selection_pool_duration_ns": item["duration_ns"], "confidence": "LOW" if item["semantic_category"] == "UNKNOWN" else "MEDIUM", "reason": "NOT_SELECTED_WITHIN_PROVISIONAL_BUDGET"})
    for reason in ("SPLITKV_TAG_NOT_SOURCE_SUPPORTED_BY_V1_INPUT", "COMBINE_TAG_NOT_SOURCE_SUPPORTED_BY_V1_INPUT"):
        uncovered.append({"status": STATUS, "phase": "DECODE", "normalized_kernel_family": "PYTORCH_FLASH_FWD", "semantic_category": "ATTENTION_CORE", "exact_implementation": "UNKNOWN", "grid": "UNKNOWN", "block": "UNKNOWN", "decode_behavior": "UNKNOWN", "selection_pool_duration_ns": 0, "confidence": "LOW", "reason": reason})
    write_tsv(args.output_dir / "UNCOVERED_LOW_CONFIDENCE_STRATA.tsv", uncovered)
    receipt = {"status": STATUS, "selector": "AWMA_REPRESENTATIVE_SUITE_SELECTOR_V1", "input_label": args.input_label, "inventory": str(args.inventory), "inventory_sha256": sha256(args.inventory), "input_rows": len(rows), "selection_pool_rows": len(selection_rows), "holdout_rows": len(holdout_rows), "budget": args.budget, "selected_count": len(selected), "holdout_fraction": args.holdout_fraction, "holdout_seed": SEED, "selection_uses_holdout_duration": False, "v1_limitations": ["V1 phase attribution awaits Window A corrected launch-context census.", "V1 has no source-supported splitkv/combine tag; no name-based inference was made.", "Simulator-native trace mapping awaits Window C coverage audit."], "v2_replacement_fields": sorted(REQUIRED | {"launch_context_phase", "launch_context_confidence", "trace_correlation_id"})}
    (args.output_dir / "RUN_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
if __name__ == "__main__":
    main()

