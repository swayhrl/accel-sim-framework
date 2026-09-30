#!/usr/bin/env python3
"""Strict OFF/ON or ON/formal semantic and CUDA-kernel neutrality comparison."""

import argparse
import hashlib
import json
from pathlib import Path

from nsys_tools import (DECODE_WALL, EXTRA_RE, PROJ_RE, canonical_occurrences,
                        connect, kernel_signature, nvtx_ranges, read_json,
                        semantic_policy)


def module_classes(run):
    return [(r["layer"], r["role"], r["module_class"], r["supported_qweight_family"])
            for r in run["module_census"]]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def ranges(sqlite_path):
    conn = connect(sqlite_path)
    try:
        labels = [r["label"] for r in nvtx_ranges(conn)]
    finally:
        conn.close()
    return {"projection": sum(PROJ_RE.fullmatch(x) is not None for x in labels),
            "activation": sum(EXTRA_RE.fullmatch(x) is not None and x.endswith("_ACTIVATION") for x in labels),
            "multiply": sum(EXTRA_RE.fullmatch(x) is not None and x.endswith("_MULTIPLY") for x in labels),
            "decode_wall": labels.count(DECODE_WALL)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--left-json", type=Path, required=True)
    p.add_argument("--right-json", type=Path, required=True)
    p.add_argument("--left-sqlite", type=Path, required=True)
    p.add_argument("--right-sqlite", type=Path, required=True)
    p.add_argument("--mode", choices=("OFF_ON", "ON_FORMAL"), required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    left, right = read_json(args.left_json), read_json(args.right_json)
    left_k, right_k = kernel_signature(args.left_sqlite), kernel_signature(args.right_sqlite)
    checks = {
        "status_pass": left.get("status") == right.get("status") == "PASS",
        "generated_tokens_equal": left["generated_token_ids_D0_D3"] == right["generated_token_ids_D0_D3"] == [23578,11,323,3950],
        "call_order_420_equal": len(left["call_order"]) == len(right["call_order"]) == 420 and left["call_order"] == right["call_order"],
        "occurrence_336_identity_equal": len(left["occurrences"]) == len(right["occurrences"]) == 336 and canonical_occurrences(left) == canonical_occurrences(right),
        "module_classes_equal": module_classes(left) == module_classes(right),
        "policy_semantics_equal": semantic_policy(left) == semantic_policy(right),
        "kernel_name_count_order_equal": [x[0] for x in left_k] == [x[0] for x in right_k],
        "kernel_grid_block_order_equal": left_k == right_k,
    }
    right_ranges = ranges(args.right_sqlite)
    if args.mode == "OFF_ON":
        left_ranges = ranges(args.left_sqlite)
        checks.update({"off_has_no_new_timeline_ranges": left_ranges["activation"] == 0 and left_ranges["multiply"] == 0 and left_ranges["decode_wall"] == 0,
                       "on_projection_ranges_336": right_ranges["projection"] == 336,
                       "on_activation_ranges_112": right_ranges["activation"] == 112,
                       "on_multiply_ranges_112": right_ranges["multiply"] == 112,
                       "on_decode_wall_one": right_ranges["decode_wall"] == 1})
    else:
        checks.update({"formal_projection_ranges_336": right_ranges["projection"] == 336,
                       "formal_activation_ranges_112": right_ranges["activation"] == 112,
                       "formal_multiply_ranges_112": right_ranges["multiply"] == 112,
                       "formal_decode_wall_one": right_ranges["decode_wall"] == 1})
    passed = all(checks.values())
    result = {"status": "PASS" if passed else "INSTRUMENTATION_NOT_NEUTRAL",
              "mode": args.mode, "checks": checks, "left_kernel_count": len(left_k),
              "right_kernel_count": len(right_k), "left_kernel_sequence_sha256": digest(left_k),
              "right_kernel_sequence_sha256": digest(right_k),
              "call_order_sha256": digest(left["call_order"]),
              "occurrence_identity_sha256": digest(canonical_occurrences(left)),
              "right_range_counts": right_ranges}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
