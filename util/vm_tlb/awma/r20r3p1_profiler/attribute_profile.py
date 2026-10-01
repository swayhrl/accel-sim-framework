#!/usr/bin/env python3
"""CPU-only exact node-pattern attribution for one repaired four-entry NSYS profile."""

import csv
import hashlib
import json
import sqlite3
from pathlib import Path


ROOT = Path("/data/c16/awma/r20r3p1_profiler_repair_resume_20261001")
RAW = ROOT / "raw"
REPORT = RAW / "REPAIRED_B0_FOUR_ENTRY_NSYS.nsys-rep"
SQLITE = RAW / "REPAIRED_B0_FOUR_ENTRY_NSYS.sqlite"
STEPS = (128, 136, 144, 152)
PATTERN = (
    ("mul_m_kernel", "LINESEARCH"),
    ("_linesearch_jv_fused_kernel", "LINESEARCH"),
    ("_linesearch_iterative_kernel", "LINESEARCH"),
    ("_zero_change_counters", "COUNTER_RESET"),
    ("_update_constraint_efc", "UPDATE_CONSTRAINT"),
    ("_zero_qfrc_constraint_sparse", "UPDATE_CONSTRAINT"),
    ("_update_constraint_init_qfrc_constraint_sparse", "UPDATE_CONSTRAINT"),
    ("_update_gradient_zero_grad_dot", "UPDATE_GRADIENT_INCREMENTAL"),
    ("_update_gradient_grad", "UPDATE_GRADIENT_INCREMENTAL"),
    ("_update_gradient_h_incremental_sparse", "UPDATE_GRADIENT_INCREMENTAL"),
    ("_padding_h", "UPDATE_GRADIENT_INCREMENTAL"),
    ("_update_gradient_cholesky_blocked_skip_unchanged", "UPDATE_GRADIENT_INCREMENTAL"),
    ("_solve_done", "SOLVE_DONE"),
    ("set_conditional_if_handle_kernel", "GRAPH_CONTROL"),
)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    if not REPORT.is_file() or REPORT.stat().st_size == 0 or not SQLITE.is_file() or SQLITE.stat().st_size == 0:
        raise RuntimeError("Repaired report or SQLite missing")
    profile = json.loads((RAW / "PROFILE_SUMMARY.json").read_text())
    if not profile["all_qualified"] or profile["entry_order"] != list(STEPS):
        raise RuntimeError("Scientific workload numeric/order gate failed")
    db = sqlite3.connect(SQLITE)
    ranges = db.execute("SELECT text,start,end FROM NVTX_EVENTS ORDER BY start").fetchall()
    expected_ranges = {"R20R3_PROFILE", *(f"R20R3_T{s}_OFF_B0" for s in STEPS)}
    if {x[0] for x in ranges} != expected_ranges:
        raise RuntimeError("Exact NVTX range set mismatch")
    all_rows = []
    summary = []
    for step in STEPS:
        label = f"R20R3_T{step}_OFF_B0"
        begin, end = next((a, b) for name, a, b in ranges if name == label)
        rows = db.execute(
            "SELECT k.start,k.end,s.value,k.graphNodeId,k.gridX,k.gridY,k.gridZ,k.blockX,k.blockY,k.blockZ "
            "FROM CUPTI_ACTIVITY_KIND_KERNEL k LEFT JOIN StringIds s ON s.id=k.demangledName "
            "WHERE k.start>=? AND k.end<=? ORDER BY k.start", (begin, end)).fetchall()
        if len(rows) < 16 or (len(rows)-16) % len(PATTERN):
            raise RuntimeError(f"t{step} graph child sequence length is not init15 + repeated14 + recovery1: {len(rows)}")
        iterations = (len(rows)-16) // len(PATTERN)
        if not 1 <= iterations <= 10:
            raise RuntimeError(f"t{step} repeated iteration count invalid: {iterations}")
        if "set_conditional_if_handle_kernel" not in rows[14][2] or "_qfrc_constraint_from_grad" not in rows[-1][2]:
            raise RuntimeError(f"t{step} initial/recovery anchors missing")
        totals = {stage: 0 for _, stage in PATTERN}
        totals["INIT"] = 0
        totals["FINAL_RECOVERY"] = 0
        for index, (start, stop, name, node, gx, gy, gz, bx, by, bz) in enumerate(rows):
            if name is None or node is None or stop <= start:
                raise RuntimeError(f"t{step} unbound graph child kernel at row {index}")
            if index < 15:
                stage = "INIT"
                iteration = -1
            elif index == len(rows)-1:
                stage = "FINAL_RECOVERY"
                iteration = iterations
            else:
                offset = index - 15
                iteration = offset // len(PATTERN)
                slot = offset % len(PATTERN)
                required, stage = PATTERN[slot]
                if required not in name:
                    raise RuntimeError(f"t{step} iteration {iteration} slot {slot}: expected {required}, observed {name}")
            duration = stop-start
            totals[stage] += duration
            all_rows.append({"step": step, "row_index": index, "outer_iteration": iteration, "stage": stage,
                             "kernel_name": name, "graph_node_id": node, "start_ns": start, "end_ns": stop,
                             "duration_ns": duration, "grid": f"{gx},{gy},{gz}", "block": f"{bx},{by},{bz}"})
        summary.append({"step": step, "graph_child_kernel_rows": len(rows), "outer_iterations_observed": iterations,
                        "LINESEARCH_gpu_us": totals["LINESEARCH"]/1000,
                        "UPDATE_CONSTRAINT_gpu_us": totals["UPDATE_CONSTRAINT"]/1000,
                        "UPDATE_GRADIENT_INCREMENTAL_gpu_us": totals["UPDATE_GRADIENT_INCREMENTAL"]/1000,
                        "INIT_gpu_us": totals["INIT"]/1000,
                        "OTHER_REPEATED_gpu_us": sum(totals[s] for s in ("COUNTER_RESET", "SOLVE_DONE", "GRAPH_CONTROL"))/1000,
                        "FINAL_RECOVERY_gpu_us": totals["FINAL_RECOVERY"]/1000,
                        "all_kernel_gpu_us": sum(totals.values())/1000})
    if len(all_rows) != db.execute("SELECT COUNT(*) FROM CUPTI_ACTIVITY_KIND_KERNEL").fetchone()[0]:
        raise RuntimeError("Some kernel rows were not assigned to the four exact NVTX ranges")
    with (RAW / "REPAIRED_PROFILE_ALL_KERNELS.tsv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(all_rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(all_rows)
    with (RAW / "REPAIRED_B0_PROFILE_SUMMARY.tsv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary)
    eligible = {stage: sum(row[f"{stage}_gpu_us"] for row in summary)
                for stage in ("LINESEARCH", "UPDATE_CONSTRAINT", "UPDATE_GRADIENT_INCREMENTAL")}
    ranked = sorted(eligible.items(), key=lambda item: item[1], reverse=True)
    top, second = ranked[0], ranked[1]
    selected = top[0]
    tie_within_5pct = (top[1] - second[1]) / top[1] <= 0.05
    if tie_within_5pct:
        modifications = {"LINESEARCH": 3, "UPDATE_CONSTRAINT": 3, "UPDATE_GRADIENT_INCREMENTAL": 5}
        selected = min((top[0], second[0]), key=lambda x: (modifications[x], x))
    receipt = {"classification": "REPAIRED_PROFILE_QUALIFIED", "report_sha256": sha(REPORT),
               "sqlite_sha256": sha(SQLITE), "report_bytes": REPORT.stat().st_size,
               "sqlite_bytes": SQLITE.stat().st_size, "entry_order": list(STEPS),
               "NVTX_range_count": len(ranges), "kernel_rows": len(all_rows),
               "all_graph_node_ids_bound": True, "iterations_by_step": {str(x["step"]): x["outer_iterations_observed"] for x in summary},
               "eligible_stage_cumulative_gpu_us": eligible, "ranked_stages": ranked,
               "tie_within_5pct": tie_within_5pct, "selected_stage": selected,
               "full_kernel_manifest_sha256": sha(RAW / "REPAIRED_PROFILE_ALL_KERNELS.tsv"),
               "compact_summary_sha256": sha(RAW / "REPAIRED_B0_PROFILE_SUMMARY.tsv")}
    (RAW / "REPAIRED_PROFILE_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
