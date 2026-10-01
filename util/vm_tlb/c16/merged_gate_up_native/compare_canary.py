#!/usr/bin/env python3
"""Cross-runtime correctness gate for the B0/B2 timeline canaries."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import torch


EXPECTED = [23578, 11, 323, 3950]
ATOL = 0.05
RTOL = 0.01


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--b0-json", type=Path, required=True)
    parser.add_argument("--b2-json", type=Path, required=True)
    parser.add_argument("--b0-tensors", type=Path, required=True)
    parser.add_argument("--b2-tensors", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    b0 = json.loads(args.b0_json.read_text())
    b2 = json.loads(args.b2_json.read_text())
    p0 = torch.load(args.b0_tensors, map_location="cpu", weights_only=False)
    p2 = torch.load(args.b2_tensors, map_location="cpu", weights_only=False)
    rows = []
    exact_shape = True
    all_finite = True
    all_within = True
    for layer in range(28):
        for decode in range(4):
            comparisons = [
                ("hidden_input", f"L{layer}.D{decode}.gate_proj.input", f"L{layer}.D{decode}.gate_up.input"),
                ("gate_proj", f"L{layer}.D{decode}.gate_proj.output", f"L{layer}.D{decode}.gate_proj.output"),
                ("up_proj", f"L{layer}.D{decode}.up_proj.output", f"L{layer}.D{decode}.up_proj.output"),
                ("down_proj", f"L{layer}.D{decode}.down_proj.output", f"L{layer}.D{decode}.down_proj.output"),
                ("ffn_output", f"L{layer}.D{decode}.ffn.output", f"L{layer}.D{decode}.ffn.output"),
            ]
            for role, k0, k2 in comparisons:
                left, right = p0["tensors"][k0], p2["tensors"][k2]
                same_shape = tuple(left.shape) == tuple(right.shape)
                finite = bool(torch.isfinite(left).all() and torch.isfinite(right).all())
                if same_shape:
                    delta = left.float() - right.float()
                    max_abs = float(delta.abs().max())
                    mean_abs = float(delta.abs().mean())
                    relative_l2 = float(torch.linalg.vector_norm(delta) / torch.linalg.vector_norm(left.float()).clamp_min(1e-12))
                    within = bool(torch.allclose(left.float(), right.float(), atol=ATOL, rtol=RTOL))
                else:
                    max_abs = mean_abs = relative_l2 = math.inf
                    within = False
                exact_shape &= same_shape
                all_finite &= finite
                all_within &= within
                rows.append({"layer": layer, "decode_index": decode, "role": role,
                             "b0_shape": json.dumps(list(left.shape)), "b2_shape": json.dumps(list(right.shape)),
                             "shape_equal": same_shape, "all_finite": finite,
                             "max_abs": max_abs, "mean_abs": mean_abs,
                             "relative_l2": relative_l2, "atol": ATOL, "rtol": RTOL,
                             "within_tolerance": within})
    with (args.output_dir / "FP16_COMPARISON.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    checks = {
        "b0_status": b0.get("status") == "PASS",
        "b2_status": b2.get("status") == "PASS",
        "tokens_exact": b0["generated_token_ids_D0_D3"] == b2["generated_token_ids_D0_D3"] == EXPECTED,
        "b0_call_order_420": len(b0["call_order"]) == 420,
        "b0_projection_occurrences_336": len(b0["occurrences"]) == 336,
        "b0_ffn_occurrences_112": len(b0["ffn_occurrences"]) == 112,
        "b2_semantic_occurrences_336": len(b2["occurrences"]) == 336,
        "b2_ffn_occurrences_112": len(b2["ffn_occurrences"]) == 112,
        "all_shapes_equal": exact_shape,
        "all_outputs_finite": all_finite,
        "all_fp16_comparisons_within_frozen_tolerance": all_within,
        "b2_tensor_dump_all_finite": b2["tensor_dump"]["all_finite"] is True,
        "b2_28_merged_modules": len(b2["module_census"]) == 28,
        "b2_single_backend_identity": len({row["kernel_backend_class"] for row in b2["module_census"]}) == 1,
    }
    result = {
        "status": "PASS" if all(checks.values()) else "CORRECTNESS_OR_IDENTITY_FAILED",
        "checks": checks, "expected_tokens": EXPECTED,
        "b0_tokens": b0["generated_token_ids_D0_D3"],
        "b2_tokens": b2["generated_token_ids_D0_D3"],
        "comparison_rows": len(rows), "atol": ATOL, "rtol": RTOL,
        "max_abs_overall": max(row["max_abs"] for row in rows),
        "mean_abs_overall": sum(row["mean_abs"] for row in rows) / len(rows),
        "max_relative_l2": max(row["relative_l2"] for row in rows),
        "b0_json_sha256": sha256(args.b0_json), "b2_json_sha256": sha256(args.b2_json),
        "b0_tensor_sha256": sha256(args.b0_tensors), "b2_tensor_sha256": sha256(args.b2_tensors),
        "comparison_class": "same checkpoint and logical AWQ semantics; cross-runtime strong baseline; not merge-only A/B",
    }
    (args.output_dir / "CROSS_RUNTIME_CORRECTNESS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
