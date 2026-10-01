#!/usr/bin/env python3
"""Correlation-authoritative B0/B2 FFN timeline and backend audit."""

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from nsys_tools import connect, kernel_rows, nvtx_ranges, runtime_by_correlation


B0_PROJ = re.compile(r"^C16_E1_OPF_CONTROL_GUD84_L(\d+)_(GATE_PROJ|UP_PROJ|DOWN_PROJ)_D(\d+)$")
B0_EXTRA = re.compile(r"^C16_FFN_TIMELINE_L(\d+)_D(\d+)_(ACTIVATION|MULTIPLY)$")
B0_FFN = re.compile(r"^C16_MERGED_BASELINE_B0_L(\d+)_D(\d+)_FFN$")
B2_ROLE = re.compile(r"^C16_MERGED_BASELINE_B2_L(\d+)_D(\d+)_(GATE_UP|SILU_AND_MUL|DOWN)$")
B2_FFN = re.compile(r"^C16_MERGED_BASELINE_B2_L(\d+)_D(\d+)_FFN$")
WALLS = {"B0": "C16_FFN_TIMELINE_DECODE_D0_D3", "B2": "C16_MERGED_BASELINE_B2_DECODE_D0_D3"}


def parse(arm, label):
    if arm == "B0":
        if match := B0_PROJ.fullmatch(label):
            return int(match.group(1)), int(match.group(3)), match.group(2).lower(), False
        if match := B0_EXTRA.fullmatch(label):
            return int(match.group(1)), int(match.group(2)), match.group(3).lower(), False
        if match := B0_FFN.fullmatch(label):
            return int(match.group(1)), int(match.group(2)), "ffn", True
    else:
        if match := B2_ROLE.fullmatch(label):
            return int(match.group(1)), int(match.group(2)), match.group(3).lower(), False
        if match := B2_FFN.fullmatch(label):
            return int(match.group(1)), int(match.group(2)), "ffn", True
    return None


def extract(arm, sqlite_path):
    conn = connect(sqlite_path)
    try:
        kernels = kernel_rows(conn)
        runtimes = runtime_by_correlation(conn)
        ranges = nvtx_ranges(conn)
    finally:
        conn.close()
    walls = [row for row in ranges if row["label"] == WALLS[arm]]
    if len(walls) != 1:
        raise RuntimeError(f"{arm} wall count {len(walls)}")
    wall = walls[0]
    semantic = []
    ffn = []
    for row in ranges:
        parsed = parse(arm, row["label"])
        if parsed:
            layer, decode, role, is_ffn = parsed
            value = {**row, "layer": layer, "decode": decode, "role": role}
            (ffn if is_ffn else semantic).append(value)
    expected_semantic = 560 if arm == "B0" else 336
    if len(semantic) != expected_semantic or len(ffn) != 112:
        raise RuntimeError(f"{arm} range closure semantic={len(semantic)} ffn={len(ffn)}")
    by_key = defaultdict(list)
    wall_kernels = []
    for kernel in kernels:
        runtime = runtimes.get(kernel["correlation_id"])
        if runtime is None or runtime["global_tid"] != wall["global_tid"]:
            continue
        if not (wall["start"] <= runtime["start"] and runtime["end"] <= wall["end"]):
            continue
        wall_kernels.append(kernel)
        candidates = [row for row in semantic if row["global_tid"] == runtime["global_tid"] and row["start"] <= runtime["start"] and runtime["end"] <= row["end"]]
        candidates.sort(key=lambda row: row["end"] - row["start"])
        if candidates:
            row = candidates[0]
            by_key[(row["layer"], row["decode"], row["role"])].append(kernel)
    return by_key, wall_kernels, semantic, ffn


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--b0-sqlite", type=Path, required=True)
    parser.add_argument("--b2-sqlite", type=Path, required=True)
    parser.add_argument("--b2-json", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    b2_json = json.loads(args.b2_json.read_text())
    extracted = {"B0": extract("B0", args.b0_sqlite), "B2": extract("B2", args.b2_sqlite)}
    inventory_rows = []
    timing_rows = []
    role_counts = {}
    reduction_counts = {}
    for arm, (by_key, wall_kernels, semantic, ffn) in extracted.items():
        role_counts[arm] = Counter()
        reduction_counts[arm] = 0
        for (layer, decode, role), rows in sorted(by_key.items()):
            duration = sum(row["end"] - row["start"] for row in rows)
            role_counts[arm][role] += len(rows)
            reduction_counts[arm] += sum(bool(re.search(r"reduce|reduction|splitk", row["kernel_name"], re.I)) for row in rows)
            timing_rows.append({"arm": arm, "layer": layer, "decode_index": decode, "role": role,
                                "kernel_count": len(rows), "kernel_duration_ns": duration})
            counts = Counter((row["kernel_name"], row["grid"], row["block"]) for row in rows)
            for (name, grid, block), count in sorted(counts.items()):
                inventory_rows.append({"arm": arm, "layer": layer, "decode_index": decode, "role": role,
                                       "kernel_name": name, "grid": grid, "block": block, "count": count})
    with (args.output_dir / "FFN_KERNEL_INVENTORY.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(inventory_rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(inventory_rows)
    with (args.output_dir / "FFN_SEMANTIC_TIMING.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(timing_rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(timing_rows)
    b2_by = extracted["B2"][0]
    checks = {
        "b0_all_projection_ranges_have_gpu_activity": all(b0_key in extracted["B0"][0] for b0_key in [(l, d, r) for l in range(28) for d in range(4) for r in ("gate_proj", "up_proj", "down_proj")]),
        "b2_gate_up_112_have_gpu_activity": sum((l, d, "gate_up") in b2_by for l in range(28) for d in range(4)) == 112,
        "b2_silu_and_mul_112_have_gpu_activity": sum((l, d, "silu_and_mul") in b2_by for l in range(28) for d in range(4)) == 112,
        "b2_down_112_have_gpu_activity": sum((l, d, "down") in b2_by for l in range(28) for d in range(4)) == 112,
        "b2_backend_recorded": all(row["kernel_backend_class"] for row in b2_json["module_census"]),
        "b2_single_backend": len({row["kernel_backend_class"] for row in b2_json["module_census"]}) == 1,
    }
    merged_names = sorted({row["kernel_name"] for row in inventory_rows if row["arm"] == "B2" and row["role"] == "gate_up"})
    silu_names = sorted({row["kernel_name"] for row in inventory_rows if row["arm"] == "B2" and row["role"] == "silu_and_mul"})
    result = {
        "status": "PASS" if all(checks.values()) else "TIMELINE_OR_BACKEND_FAILED",
        "checks": checks,
        "b0_decode_kernel_count": len(extracted["B0"][1]),
        "b2_decode_kernel_count": len(extracted["B2"][1]),
        "b0_role_kernel_counts": dict(role_counts["B0"]),
        "b2_role_kernel_counts": dict(role_counts["B2"]),
        "b0_reduction_name_classified_count": reduction_counts["B0"],
        "b2_reduction_name_classified_count": reduction_counts["B2"],
        "b2_merged_gate_up_kernel_names": merged_names,
        "b2_silu_and_mul_kernel_names": silu_names,
        "b2_selected_quant_method": sorted({row["quant_method_class"] for row in b2_json["module_census"]}),
        "b2_selected_kernel_backend": sorted({row["kernel_backend_class"] for row in b2_json["module_census"]}),
        "b2_gate_up_parameter_layout": b2_json["module_census"][0]["gate_up_parameters"],
        "b2_kernel_state": b2_json["module_census"][0]["kernel_state"],
        "kernel_attribution": "NVTX CPU launch scope plus CUDA runtime correlationId to GPU kernel",
        "reduction_count_boundary": "name-classified only; exact per-semantic kernel inventory is authoritative",
    }
    (args.output_dir / "TIMELINE_CANARY_SUMMARY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
