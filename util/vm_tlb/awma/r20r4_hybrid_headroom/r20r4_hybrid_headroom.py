#!/usr/bin/env python3
"""CPU-only accepted-profile decomposition and fixed-304 late-region oracles."""

import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve()
WORKTREE = HERE.parents[4]
PACK = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R4_HYBRID_HEADROOM_AUDIT_109_V1"
P1 = Path("/data/c16/awma/r20r3p1_profiler_repair_resume_20261001/raw")
P2 = Path("/data/c16/awma/r20r3p2_residual_contract_resume_20261001/raw")
P2_PACK = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R3P2_RESIDUAL_CONTRACT_RESUME_109_V1"
STEPS = (128, 136, 144, 152)
WORKERS = 304
STAGE = "UPDATE_GRADIENT_INCREMENTAL"
KERNELS = (
    ("_update_gradient_zero_grad_dot", "other"),
    ("_update_gradient_grad", "other"),
    ("_update_gradient_h_incremental_sparse", "H"),
    ("_padding_h", "other"),
    ("_update_gradient_cholesky_blocked_skip_unchanged", "cholesky"),
)
EXPECTED_P1_MANIFEST_SHA = "2d04585791690c9fcb4a1b5b117caaa6f91009b33a03cdca41e5882104de55b8"
EXPECTED_P1_SQLITE_SHA = "364b2a89fbdd409e8a01a05bf52e005d57ae5a0f4f30a2451b3e87e60d3f4269"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_tsv(path):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def write_tsv(path, rows):
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    PACK.mkdir(parents=True, exist_ok=True)
    manifest = P1 / "REPAIRED_PROFILE_ALL_KERNELS.tsv"
    sqlite = P1 / "REPAIRED_B0_FOUR_ENTRY_NSYS.sqlite"
    if sha(manifest) != EXPECTED_P1_MANIFEST_SHA or sha(sqlite) != EXPECTED_P1_SQLITE_SHA:
        raise RuntimeError("Accepted P1 profiler identity changed")
    p1_receipt = json.loads((P1 / "REPAIRED_PROFILE_RECEIPT.json").read_text())
    if p1_receipt["selected_stage"] != STAGE or p1_receipt["kernel_rows"] != 568:
        raise RuntimeError("Accepted selected stage/profile row count changed")
    p1_rows = read_tsv(manifest)
    active_rows = read_tsv(P2_PACK / "ACTIVE_WORK_COUNTS.tsv")
    active_map = {(int(r["step"]), int(r["outer_iteration_zero_based"])): int(r["active_worlds_derived_from_final_niter"])
                  for r in active_rows}
    if len(active_map) != 40:
        raise RuntimeError("Accepted P2 active-count table is incomplete")
    profile_summary = {int(r["step"]): r for r in read_tsv(P1 / "REPAIRED_B0_PROFILE_SUMMARY.tsv")}
    selected = defaultdict(list)
    for r in p1_rows:
        if r["stage"] == STAGE:
            step, iteration = int(r["step"]), int(r["outer_iteration"])
            if step not in STEPS or iteration < 0 or int(r["duration_ns"]) <= 0 or not r["graph_node_id"]:
                raise RuntimeError("Selected-stage row has invalid identity/duration")
            selected[(step, iteration)].append(r)
    per_iteration = []
    for step in STEPS:
        expected_iters = int(profile_summary[step]["outer_iterations_observed"])
        if expected_iters != p1_receipt["iterations_by_step"][str(step)]:
            raise RuntimeError(f"Iteration count authority mismatch at t{step}")
        for iteration in range(expected_iters):
            group = sorted(selected[(step, iteration)], key=lambda r: int(r["row_index"]))
            if len(group) != len(KERNELS):
                raise RuntimeError(f"Expected five selected-stage rows at t{step}/it{iteration}")
            durations = {"H": 0, "cholesky": 0, "other": 0}
            for r, (name_fragment, category) in zip(group, KERNELS):
                if name_fragment not in r["kernel_name"]:
                    raise RuntimeError(f"Kernel source/graph order changed at t{step}/it{iteration}: {r['kernel_name']}")
                durations[category] += int(r["duration_ns"])
            active = active_map[(step, iteration)]
            if not 1 <= active <= 1024:
                raise RuntimeError(f"Active-count identity invalid at t{step}/it{iteration}")
            stage_ns = sum(durations.values())
            per_iteration.append({"step": step, "outer_iter": iteration,
                                  "active_worlds": active, "active_fraction": active/1024,
                                  "region": "LATE_ELIGIBLE_REGION" if active <= WORKERS else "EARLY_BASELINE_REGION",
                                  "H_us": durations["H"]/1000,
                                  "cholesky_us": durations["cholesky"]/1000,
                                  "other_stage_us": durations["other"]/1000,
                                  "stage_total_us": stage_ns/1000,
                                  "source_kernel_rows": len(group)})
    if len(per_iteration) != sum(p1_receipt["iterations_by_step"].values()):
        raise RuntimeError("Not every accepted outer iteration decomposed")
    per_step_closure = []
    for step in STEPS:
        rows = [r for r in per_iteration if r["step"] == step]
        reconstructed = sum(r["stage_total_us"] for r in rows)
        accepted = float(profile_summary[step]["UPDATE_GRADIENT_INCREMENTAL_gpu_us"])
        if not math.isclose(reconstructed, accepted, abs_tol=0.001, rel_tol=0):
            raise RuntimeError(f"t{step} selected-stage GPU time does not close: {reconstructed} vs {accepted}")
        per_step_closure.append({"step": step, "iterations": len(rows), "reconstructed_stage_us": reconstructed,
                                 "accepted_stage_us": accepted, "abs_difference_us": abs(reconstructed-accepted),
                                 "late_iterations": sum(r["region"] == "LATE_ELIGIBLE_REGION" for r in rows)})
    reconstructed_total = sum(r["reconstructed_stage_us"] for r in per_step_closure)
    accepted_total = float(p1_receipt["eligible_stage_cumulative_gpu_us"][STAGE])
    if not math.isclose(reconstructed_total, accepted_total, abs_tol=0.001, rel_tol=0):
        raise RuntimeError("Four-entry stage total does not close")
    write_tsv(PACK / "PER_ITERATION_STAGE_TIME.tsv", per_iteration)

    all_samples = read_tsv(P2 / "DISCOVERY_TIMING_ALL_SAMPLES.tsv")
    compact = read_tsv(P2_PACK / "DISCOVERY_TIMING.tsv")
    for r in compact:
        matching = [x for x in all_samples if x["phase"] == "FORMAL" and x["group"] == r["group"]
                    and x["step"] == r["step"] and x["arm"] == r["arm"]]
        if len(matching) != 5:
            raise RuntimeError("Accepted formal compact/sample count mismatch")
        median = statistics.median(float(x["wall_ms"]) for x in matching)
        if not math.isclose(median, float(r["wall_median_ms"]), abs_tol=1e-9, rel_tol=0):
            raise RuntimeError("Accepted B0 formal median cannot be reconstructed")
    formal_b0_ms = {}
    for step in STEPS:
        values = [float(r["wall_ms"]) for r in all_samples if r["phase"] == "FORMAL" and r["arm"] == "B0" and int(r["step"]) == step]
        if len(values) != 15:
            raise RuntimeError(f"Expected 15 accepted B0 formal samples at t{step}")
        formal_b0_ms[step] = statistics.median(values)
    oracles = []
    for step in STEPS:
        rows = [r for r in per_iteration if r["step"] == step]
        late = [r for r in rows if r["region"] == "LATE_ELIGIBLE_REGION"]
        late_stage_us = sum(r["stage_total_us"] for r in late)
        late_target_us = sum(r["H_us"]+r["cholesky_us"] for r in late)
        total_stage_us = sum(r["stage_total_us"] for r in rows)
        denom_us = formal_b0_ms[step]*1000
        oracles.append({"step": step, "B0_complete_solver_median_us": denom_us,
                        "selected_stage_all_iterations_us": total_stage_us,
                        "late_selected_stage_us": late_stage_us,
                        "late_target_H_plus_cholesky_us": late_target_us,
                        "late_selected_stage_fraction": late_stage_us/total_stage_us,
                        "O1_ideal_complete_solver_us": denom_us-late_stage_us,
                        "O1_ideal_improvement": late_stage_us/denom_us,
                        "O2_ideal_complete_solver_us": denom_us-late_target_us,
                        "O2_ideal_improvement": late_target_us/denom_us,
                        "O3_completed_world_launch_cost": "UNKNOWN_NOT_SEPARABLE_FROM_KERNEL_TIME",
                        "estimate_boundary": "CROSS_RUN_B0_NSYS_VS_FORMAL_MEDIAN_NOT_PAIRED"})
    denom_all = sum(r["B0_complete_solver_median_us"] for r in oracles)
    late_all = sum(r["late_selected_stage_us"] for r in oracles)
    target_all = sum(r["late_target_H_plus_cholesky_us"] for r in oracles)
    oracles.append({"step": "AGGREGATE_4", "B0_complete_solver_median_us": denom_all,
                    "selected_stage_all_iterations_us": reconstructed_total,
                    "late_selected_stage_us": late_all,
                    "late_target_H_plus_cholesky_us": target_all,
                    "late_selected_stage_fraction": late_all/reconstructed_total,
                    "O1_ideal_complete_solver_us": denom_all-late_all,
                    "O1_ideal_improvement": late_all/denom_all,
                    "O2_ideal_complete_solver_us": denom_all-target_all,
                    "O2_ideal_improvement": target_all/denom_all,
                    "O3_completed_world_launch_cost": "UNKNOWN_NOT_SEPARABLE_FROM_KERNEL_TIME",
                    "estimate_boundary": "CROSS_RUN_B0_NSYS_VS_FORMAL_MEDIAN_NOT_PAIRED"})
    write_tsv(PACK / "LATE_PHASE_ORACLE.tsv", oracles)
    receipt = {"classification": "PROFILE_DECOMPOSITION_QUALIFIED",
               "P1_manifest_sha256": sha(manifest), "P1_sqlite_sha256": sha(sqlite),
               "P1_profile_receipt_selected_stage": STAGE,
               "P2_active_counts_sha256": sha(P2_PACK / "ACTIVE_WORK_COUNTS.tsv"),
               "P2_formal_samples_sha256": sha(P2 / "DISCOVERY_TIMING_ALL_SAMPLES.tsv"),
               "worker_threshold": WORKERS, "per_iteration_rows": len(per_iteration),
               "selected_stage_kernel_rows": len(per_iteration)*len(KERNELS),
               "per_step_closure": per_step_closure,
               "four_entry_reconstructed_stage_us": reconstructed_total,
               "four_entry_accepted_stage_us": accepted_total,
               "late_selected_stage_us": late_all, "late_target_H_plus_cholesky_us": target_all,
               "O1_aggregate_improvement": late_all/denom_all,
               "O2_aggregate_improvement": target_all/denom_all,
               "O2_entry_contribution_shares": {str(r["step"]): r["late_target_H_plus_cholesky_us"]/target_all for r in oracles[:-1]},
               "O3": "UNKNOWN_NOT_SOURCE_IDENTIFIABLE",
               "cross_run_estimate_not_paired": True}
    (PACK / "PROFILE_DECOMPOSITION_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
