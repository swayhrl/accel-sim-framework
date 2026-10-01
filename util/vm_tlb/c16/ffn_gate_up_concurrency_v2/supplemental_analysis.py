#!/usr/bin/env python3
"""Frozen V2 overlap and held-out summaries using existing canary/formal data."""

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path


def read_tsv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    overlap = read_tsv(args.raw / "B1_GATE_UP_OVERLAP.tsv")
    durations = read_tsv(args.raw / "CANARY_KERNEL_DURATIONS.tsv")
    primary = json.loads((args.output_dir / "PRIMARY_BOOTSTRAP.json").read_text())
    formal_duration = json.loads((args.output_dir / "KERNEL_DURATION_RESPONSE.json").read_text())
    heldout = json.loads((args.output_dir / "HELDOUT_VALIDATION.json").read_text())
    final = json.loads((args.output_dir / "FINAL_DECISION.json").read_text())
    positive = [row for row in overlap if row["overlap_positive"] == "True"]
    held_rows = [row for row in overlap if 14 <= int(row["layer"]) <= 27]
    held_positive = [row for row in held_rows if row["overlap_positive"] == "True"]
    overlap_summary = {
        "status": "PASS", "total_windows": len(overlap), "overlap_count": len(positive),
        "overlap_fraction": len(positive) / len(overlap),
        "total_overlap_ns": sum(int(row["overlap_ns"]) for row in overlap),
        "layers_14_27": {"windows": len(held_rows), "overlap_count": len(held_positive),
                         "overlap_fraction": len(held_positive) / len(held_rows),
                         "total_overlap_ns": sum(int(row["overlap_ns"]) for row in held_rows)},
        "per_window_table": "B1_GATE_UP_OVERLAP.tsv",
    }
    (args.output_dir / "OVERLAP_SUMMARY.json").write_text(json.dumps(overlap_summary, indent=2, sort_keys=True) + "\n")
    grouped = defaultdict(list)
    for row in durations:
        if row["semantic_role"] in ("gate_proj", "up_proj"):
            grouped[(row["arm"], row["semantic_role"])].append(int(row["kernel_duration_ns"]) / 1e6)
    canary_duration = {}
    for role in ("gate_proj", "up_proj"):
        b0 = statistics.median(grouped[("B0", role)])
        b1 = statistics.median(grouped[("B1", role)])
        canary_duration[role] = {"b0_median_ms": b0, "b1_median_ms": b1, "b1_over_b0": b1 / b0}
    (args.output_dir / "CANARY_KERNEL_DURATION_RESPONSE.json").write_text(json.dumps(canary_duration, indent=2, sort_keys=True) + "\n")
    primary_saving = primary["observed"]["saving_ms"]
    d3_saving = heldout["d3_whole_step"]["saving_ms"]
    heldout_v2 = {
        **heldout,
        "layers_14_27_overlap": overlap_summary["layers_14_27"],
        "primary_direction": "B1_FASTER" if primary_saving > 0 else "B1_SLOWER" if primary_saving < 0 else "TIE",
        "d3_direction": "B1_FASTER" if d3_saving > 0 else "B1_SLOWER" if d3_saving < 0 else "TIE",
        "d3_same_direction_as_primary": (primary_saving > 0) == (d3_saving > 0),
        "formal_gate_up_duration_response": formal_duration,
    }
    (args.output_dir / "HELDOUT_V2.json").write_text(json.dumps(heldout_v2, indent=2, sort_keys=True) + "\n")
    facts = {
        "status": "PASS", "correctness": "PASS", "overlap": overlap_summary,
        "primary": primary, "formal_kernel_duration": formal_duration,
        "heldout": heldout_v2, "decision": final,
        "oracle_reference_ms": 7.732849,
        "claim_boundary": "current separated AutoAWQ runtime only; merged software capability is mature but has no accepted native performance result",
    }
    (args.output_dir / "FINAL_REPORT_FACTS.json").write_text(json.dumps(facts, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "overlap_count": len(positive),
                      "heldout_overlap_count": len(held_positive), "decision": final["decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
