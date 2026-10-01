#!/usr/bin/env python3
"""CPU-only audit of a stopped B1 canary whose runner rejected correctness."""

import argparse
import csv
import hashlib
import json
import re
import statistics
from pathlib import Path

from concurrency_canary import extract, intersection_ns, inventory


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_tsv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    b0_json_path = args.raw / "canary_b0.json"
    b0 = json.loads(b0_json_path.read_text())
    stderr = (args.raw / "canary_b1.stderr.log").read_text(errors="replace")
    matches = re.findall(r"token drift \[([^]]+)\]", stderr)
    if len(matches) != 1:
        raise RuntimeError("cannot establish unique B1 token drift")
    observed = [int(value.strip()) for value in matches[0].split(",")]
    expected = [23578, 11, 323, 3950]
    b0_by, b0_wall = extract(args.raw / "canary_b0.sqlite")
    b1_by, b1_wall = extract(args.raw / "canary_b1.sqlite")
    keys = sorted(set(b0_by) | set(b1_by))
    per_semantic = all(inventory(b0_by[key]) == inventory(b1_by[key]) for key in keys)
    global_inventory = inventory(b0_wall) == inventory(b1_wall)
    overlap_rows = []
    response_rows = []
    for step in range(4):
        for layer in range(28):
            gate = b1_by[(step, layer, "gate_proj")]
            up = b1_by[(step, layer, "up_proj")]
            gate_intervals = [(row["start"], row["end"]) for row in gate]
            up_intervals = [(row["start"], row["end"]) for row in up]
            overlap = intersection_ns(gate_intervals, up_intervals)
            overlap_rows.append({"decode_step": step, "layer": layer,
                                 "gate_kernel_count": len(gate), "up_kernel_count": len(up),
                                 "gate_start": min(x[0] for x in gate_intervals),
                                 "gate_end": max(x[1] for x in gate_intervals),
                                 "up_start": min(x[0] for x in up_intervals),
                                 "up_end": max(x[1] for x in up_intervals),
                                 "overlap_ns": overlap, "overlap_positive": overlap > 0,
                                 "scientific_status": "QUARANTINED_CORRECTNESS_FAILURE"})
            for role in ("gate_proj", "up_proj"):
                b0_ns = sum(row["end"] - row["start"] for row in b0_by[(step, layer, role)])
                b1_ns = sum(row["end"] - row["start"] for row in b1_by[(step, layer, role)])
                response_rows.append({"decode_step": step, "layer": layer, "role": role,
                                      "b0_kernel_duration_ns": b0_ns,
                                      "b1_kernel_duration_ns": b1_ns,
                                      "b1_over_b0": b1_ns / b0_ns,
                                      "scientific_status": "QUARANTINED_CORRECTNESS_FAILURE"})
    write_tsv(args.output_dir / "GATE_UP_OVERLAP.tsv", tuple(overlap_rows[0]), overlap_rows)
    write_tsv(args.output_dir / "KERNEL_DURATION_RESPONSE.tsv", tuple(response_rows[0]), response_rows)
    b0_summary = {
        "status": "PASS", "arm": "B0", "gate_up_concurrency": "off",
        "generated_tokens": b0["generated_token_ids_D0_D3"],
        "call_order_count": len(b0["call_order"]), "projection_occurrence_count": len(b0["occurrences"]),
        "decode_kernel_count": len(b0_wall), "runner_json_sha256": sha256(b0_json_path),
        "nsys_rep_sha256": sha256(args.raw / "canary_b0.nsys-rep"),
        "sqlite_sha256": sha256(args.raw / "canary_b0.sqlite"),
    }
    b1_summary = {
        "status": "CORRECTNESS_MISMATCH_STOP", "arm": "B1", "gate_up_concurrency": "on",
        "expected_tokens": expected, "observed_tokens": observed,
        "runner_json_written": False, "call_order_identity": "NOT_ESTABLISHED_DUE_RUNNER_STOP",
        "projection_hash_shape_identity": "NOT_ESTABLISHED_DUE_RUNNER_STOP",
        "decode_kernel_count": len(b1_wall),
        "nsys_rep_sha256": sha256(args.raw / "canary_b1.nsys-rep"),
        "sqlite_sha256": sha256(args.raw / "canary_b1.sqlite"),
        "stderr_sha256": sha256(args.raw / "canary_b1.stderr.log"),
    }
    (args.output_dir / "TIMELINE_CANARY_B0.json").write_text(json.dumps(b0_summary, indent=2, sort_keys=True) + "\n")
    (args.output_dir / "TIMELINE_CANARY_B1.json").write_text(json.dumps(b1_summary, indent=2, sort_keys=True) + "\n")
    ratios = [row["b1_over_b0"] for row in response_rows]
    result = {
        "status": "CORRECTNESS_MISMATCH_STOP",
        "formal_timing_started": False,
        "expected_tokens": expected,
        "b0_tokens": b0["generated_token_ids_D0_D3"],
        "b1_tokens": observed,
        "b0_decode_kernel_count": len(b0_wall),
        "b1_decode_kernel_count": len(b1_wall),
        "global_kernel_name_grid_block_multiset_equal": global_inventory,
        "per_semantic_kernel_inventory_equal": per_semantic,
        "b1_overlap_count": sum(row["overlap_positive"] for row in overlap_rows),
        "b1_overlap_fraction": sum(row["overlap_positive"] for row in overlap_rows) / len(overlap_rows),
        "b1_total_overlap_ns": sum(row["overlap_ns"] for row in overlap_rows),
        "quarantined_duration_ratio_median": statistics.median(ratios),
        "scientific_use": "NONE; trace-only structural evidence is quarantined by correctness failure",
        "stop_rule": "any identity/hash/shape/token mismatch",
    }
    (args.output_dir / "FAILED_CANARY_AUDIT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
