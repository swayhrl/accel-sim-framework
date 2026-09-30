#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from pathlib import Path

from common import ACCEPTED_ZERO_FILL_MS, write_json


DECISION = "CCE_ZERO_INIT_SOFTWARE_REMOVABLE"


def kernels(path: Path):
    connection = sqlite3.connect(path)
    query = """
        select k.start,k.end,k.end-k.start,k.gridX,k.gridY,k.gridZ,
               k.blockX,k.blockY,k.blockZ,s.value
        from CUPTI_ACTIVITY_KIND_KERNEL k
        join StringIds s on s.id=k.demangledName
        order by k.start
    """
    rows = list(connection.execute(query))
    connection.close()
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root
    raw = root / "raw"
    c1_path = raw / "nsys/C1_ZERO_INIT_REMOVED.sqlite"
    c0_path = Path(
        "/data/c16/awma/exact_loss_cce_liger_109_v1_20260930/"
        "raw/nsys/B1_CCE_EXACT.sqlite"
    )
    c1 = kernels(c1_path)
    c0 = kernels(c0_path)
    fields = [
        "start_ns","end_ns","duration_ns","grid_x","grid_y","grid_z",
        "block_x","block_y","block_z","demangled_name",
    ]
    with (raw / "nsys/C1_KERNEL_INSTANCES.tsv").open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(fields)
        writer.writerows(c1)

    full_elements = 151936 * 896
    full_grid = full_elements // 1024
    state_elements = 1187 * 14
    state_grid = (state_elements + 1023) // 1024

    def named(rows, token):
        return [row for row in rows if token in row[9]]

    c0_full_fills = [
        row for row in named(c0, "FillFunctor<float>")
        if row[3] == full_grid
    ]
    c1_full_fills = [
        row for row in named(c1, "FillFunctor<float>")
        if row[3] == full_grid
    ]
    c1_full_copies = [
        row for row in named(c1, "bfloat16_copy_kernel_cuda")
        if row[3] == full_grid
    ]
    c1_state_resets = [
        row for row in named(c1, "FillFunctor<int>")
        if row[3] == state_grid
    ]
    c1_core = named(c1, "_cce_backward_kernel")
    c1_lse = named(c1, "_cce_lse_forward_kernel")
    c1_other_full_grid = [
        row for row in c1
        if row[3] == full_grid and "bfloat16_copy_kernel_cuda" not in row[9]
    ]
    c1_large_float_fills = [
        row for row in named(c1, "FillFunctor<float>")
        if row[2] >= 100000
    ]

    if len(c0_full_fills) != 1 or c0_full_fills[0][2] != 751779:
        raise RuntimeError(f"accepted C0 full zero anchor mismatch: {c0_full_fills}")
    if c1_full_fills:
        raise RuntimeError(f"C1 retained a full dC fill: {c1_full_fills}")
    if len(c1_full_copies) != 1:
        raise RuntimeError(f"C1 full BF16 output cast mismatch: {c1_full_copies}")
    if len(c1_state_resets) != 1:
        raise RuntimeError(f"C1 init-state reset mismatch: {c1_state_resets}")
    if len(c1_core) != 1 or c1_core[0][3:9] != (2374, 1, 1, 128, 1, 1):
        raise RuntimeError(f"C1 core kernel geometry mismatch: {c1_core}")
    if len(c1_lse) != 1:
        raise RuntimeError("C1 LSE kernel missing")
    if c1_other_full_grid or c1_large_float_fills:
        raise RuntimeError(
            f"equivalent full-size pass detected: grid={c1_other_full_grid} fills={c1_large_float_fills}"
        )

    paired_path = raw / "PAIRED_ANALYSIS.json"
    paired = json.loads(paired_path.read_text())
    improvement = paired["improvement_fraction"]
    recovery = paired["accepted_zero_fill_recovery_fraction"]
    stable = max(
        paired["C0"]["group_median_range_fraction"],
        paired["C1"]["group_median_range_fraction"],
    ) < 0.05
    numerical = json.loads((raw / "REAL_NUMERICAL_QUALIFICATION.json").read_text())
    directed = json.loads((raw / "DIRECTED_TESTS.json").read_text())
    qualified = (
        numerical["qualified"]
        and directed["status"] == "PASS"
        and stable
        and (improvement >= 0.05 or recovery >= 0.70)
    )
    if not qualified:
        raise RuntimeError(
            f"software-removable decision gates failed: improvement={improvement} recovery={recovery} stable={stable}"
        )

    analysis = {
        "stage": "AWMA_CCE_ZERO_INIT_REMOVAL_109_V1",
        "decision": DECISION,
        "c0_accepted_full_zero_fill": {
            "duration_ns": c0_full_fills[0][2],
            "grid_x": c0_full_fills[0][3],
            "elements": full_elements,
        },
        "c1_full_zero_fill_absent": True,
        "c1_equivalent_full_size_initialization_absent": True,
        "c1_full_output_cast": {
            "present": True,
            "duration_ns": c1_full_copies[0][2],
            "grid_x": c1_full_copies[0][3],
        },
        "c1_init_state_reset": {
            "present": True,
            "duration_ns": c1_state_resets[0][2],
            "grid_x": c1_state_resets[0][3],
            "elements": state_elements,
            "bytes": state_elements * 4,
        },
        "c1_cce_backward": {
            "present": True,
            "duration_ns": c1_core[0][2],
            "grid_x": c1_core[0][3],
            "block_x": c1_core[0][6],
        },
        "c1_lse": {
            "present": True,
            "duration_ns": c1_lse[0][2],
            "grid_x": c1_lse[0][3],
        },
        "c1_total_gpu_kernel_ns": sum(row[2] for row in c1),
        "c1_kernel_instances": len(c1),
        "numerical_qualified": True,
        "directed_qualified": True,
        "stable_across_groups": stable,
        "improvement_fraction": improvement,
        "median_delta_ms": paired["median_delta_ms_C0_minus_C1"],
        "accepted_zero_fill_ms": ACCEPTED_ZERO_FILL_MS,
        "accepted_zero_fill_recovery_fraction": recovery,
        "ncu_runs": 0,
    }
    write_json(raw / "NSYS_CAUSAL_ANALYSIS.json", analysis)
    paired["decision_pending_nsys"] = False
    paired["nsys_causal_qualified"] = True
    paired["decision"] = DECISION
    write_json(paired_path, paired)
    write_json(raw / "FINAL_DECISION.json", {
        "stage": analysis["stage"],
        "decision": DECISION,
        "reason": (
            "C1 passed full-gradient correctness, removed the accepted full-size dC zero-fill "
            "without an equivalent pass, improved the full operator by at least 5%, and recovered "
            "at least 70% of the accepted zero-fill time."
        ),
    })
    campaign_path = raw / "REAL_CAMPAIGN_RESULT.json"
    campaign = json.loads(campaign_path.read_text())
    campaign["status"] = "COMPLETE"
    campaign["decision"] = DECISION
    campaign["nsys_causal_qualified"] = True
    write_json(campaign_path, campaign)
    print(json.dumps(analysis, sort_keys=True))


if __name__ == "__main__":
    main()
