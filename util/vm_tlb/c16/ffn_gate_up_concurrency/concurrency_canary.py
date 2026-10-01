#!/usr/bin/env python3
"""Validate B0/B1 semantics, kernel identity, and real gate/up overlap."""

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from nsys_tools import (DECODE_WALL, connect, kernel_rows, nvtx_ranges,
                        parse_semantic, read_json, runtime_by_correlation)


def digest(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def write_tsv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def canonical_occurrences(run):
    keys = ("layer", "role", "decode_index", "token_id", "range", "input_sha256",
            "output_sha256", "input_shape", "output_shape", "module_class")
    return [{key: row[key] for key in keys} for row in run["occurrences"]]


def module_identity(run):
    keys = ("layer", "role", "module_class", "supported_qweight_family", "dtype",
            "shape", "numel", "element_size_bytes", "bytes", "storage_offset_elements",
            "storage_offset_bytes", "contiguous", "storage_nbytes")
    return [{key: row[key] for key in keys} for row in run["module_census"]]


def transition_semantics(run):
    omitted = {"stream_value", "base_ptr", "cpu_update_ns"}
    return [{key: value for key, value in row.items() if key not in omitted}
            for row in run["policy_transitions"]]


def policy_semantics(run):
    keys = ("condition", "mode", "set_name", "selected_roles", "selected_module_count",
            "hit_ratio", "target_persisting", "policy_transition_count",
            "all_84_ffn_instrumented", "no_reset_between_transitions",
            "no_inner_loop_synchronize")
    return {key: run[key] for key in keys}


def merge(intervals):
    out = []
    for start, end in sorted(intervals):
        if not out or start > out[-1][1]:
            out.append([start, end])
        else:
            out[-1][1] = max(out[-1][1], end)
    return out


def intersection_ns(left, right):
    a, b = merge(left), merge(right)
    i = j = total = 0
    while i < len(a) and j < len(b):
        total += max(0, min(a[i][1], b[j][1]) - max(a[i][0], b[j][0]))
        if a[i][1] <= b[j][1]:
            i += 1
        else:
            j += 1
    return total


def extract(path):
    conn = connect(path)
    try:
        kernels = kernel_rows(conn)
        runtimes = runtime_by_correlation(conn)
        ranges = nvtx_ranges(conn)
    finally:
        conn.close()
    walls = [row for row in ranges if row["label"] == DECODE_WALL]
    if len(walls) != 1:
        raise RuntimeError(f"decode wall count {len(walls)} != 1 in {path}")
    wall = walls[0]
    semantics = []
    for row in ranges:
        parsed = parse_semantic(row["label"])
        if parsed:
            semantics.append({**row, **parsed})
    expected = {(step, layer, role) for step in range(4) for layer in range(28)
                for role in ("gate_proj", "up_proj", "activation", "multiply", "down_proj")}
    observed = {(row["decode_step"], row["layer"], row["role"]) for row in semantics}
    if len(semantics) != 560 or observed != expected:
        raise RuntimeError(f"semantic closure failed rows={len(semantics)}")
    by_key = defaultdict(list)
    wall_kernels = []
    for kernel in kernels:
        runtime = runtimes.get(kernel["correlation_id"])
        if runtime is None:
            continue
        if not (runtime["global_tid"] == wall["global_tid"] and
                wall["start"] <= runtime["start"] and runtime["end"] <= wall["end"]):
            continue
        wall_kernels.append(kernel)
        candidates = [row for row in semantics
                      if row["global_tid"] == runtime["global_tid"] and
                      row["start"] <= runtime["start"] and runtime["end"] <= row["end"]]
        candidates.sort(key=lambda row: row["end"] - row["start"])
        if candidates:
            row = candidates[0]
            by_key[(row["decode_step"], row["layer"], row["role"])].append(kernel)
    missing = sorted(key for key in expected if key[2].endswith("_proj") and not by_key[key])
    if missing:
        raise RuntimeError(f"projection activity missing: {missing[:5]} count={len(missing)}")
    return by_key, wall_kernels


def inventory(rows):
    return Counter((row["kernel_name"], row["grid"], row["block"]) for row in rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--b0-json", type=Path, required=True)
    parser.add_argument("--b1-json", type=Path, required=True)
    parser.add_argument("--b0-sqlite", type=Path, required=True)
    parser.add_argument("--b1-sqlite", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    b0, b1 = read_json(args.b0_json), read_json(args.b1_json)
    b0_by, b0_wall = extract(args.b0_sqlite)
    b1_by, b1_wall = extract(args.b1_sqlite)
    keys = sorted(set(b0_by) | set(b1_by))
    per_semantic_equal = all(inventory(b0_by[key]) == inventory(b1_by[key]) for key in keys)
    checks = {
        "status_pass": b0.get("status") == b1.get("status") == "PASS",
        "arms_bound": b0.get("gate_up_concurrency") == "off" and b1.get("gate_up_concurrency") == "on",
        "tokens_exact_equal": b0["generated_token_ids_D0_D3"] == b1["generated_token_ids_D0_D3"] == [23578, 11, 323, 3950],
        "call_order_420_exact_equal": len(b0["call_order"]) == len(b1["call_order"]) == 420 and b0["call_order"] == b1["call_order"],
        "occurrence_336_exact_equal": len(b0["occurrences"]) == len(b1["occurrences"]) == 336 and canonical_occurrences(b0) == canonical_occurrences(b1),
        "module_identity_equal": module_identity(b0) == module_identity(b1),
        "policy_summary_equal": policy_semantics(b0) == policy_semantics(b1),
        "policy_transition_semantics_equal_except_stream_pointer_timing": transition_semantics(b0) == transition_semantics(b1),
        "global_kernel_name_grid_block_multiset_equal": inventory(b0_wall) == inventory(b1_wall),
        "global_kernel_count_equal": len(b0_wall) == len(b1_wall),
        "per_semantic_kernel_inventory_equal": per_semantic_equal,
    }
    duration_rows = []
    for arm, data in (("B0", b0_by), ("B1", b1_by)):
        for (step, layer, role), rows in sorted(data.items()):
            duration_rows.append({"arm": arm, "decode_step": step, "layer": layer,
                                  "semantic_role": role, "kernel_count": len(rows),
                                  "kernel_duration_ns": sum(row["end"] - row["start"] for row in rows)})
    overlap_rows = []
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
                                 "overlap_ns": overlap, "overlap_positive": overlap > 0})
    positive = sum(row["overlap_positive"] for row in overlap_rows)
    checks["b1_real_gate_up_gpu_overlap"] = positive > 0
    write_tsv(args.output_dir / "CANARY_KERNEL_DURATIONS.tsv", tuple(duration_rows[0]), duration_rows)
    write_tsv(args.output_dir / "B1_GATE_UP_OVERLAP.tsv", tuple(overlap_rows[0]), overlap_rows)
    result = {
        "status": "PASS" if all(checks.values()) else "TWO_STREAM_CANARY_FAILED",
        "checks": checks,
        "b0_decode_kernel_count": len(b0_wall),
        "b1_decode_kernel_count": len(b1_wall),
        "b0_kernel_inventory_sha256": digest(sorted(inventory(b0_wall).items())),
        "b1_kernel_inventory_sha256": digest(sorted(inventory(b1_wall).items())),
        "semantic_occurrence_count": len(keys),
        "b1_gate_up_occurrences": len(overlap_rows),
        "b1_positive_overlap_occurrences": positive,
        "b1_total_overlap_ns": sum(row["overlap_ns"] for row in overlap_rows),
        "policy_transition_count": len(b0["policy_transitions"]),
        "allowed_difference": "policy transition stream_value may differ; pointer/timing are process-local",
    }
    (args.output_dir / "B0_B1_TIMELINE_CANARY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
