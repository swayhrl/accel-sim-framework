#!/usr/bin/env python3
"""CPU-only compact correctness/timing and derived active-work accounting."""

import csv
import json
import statistics
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve()
WORKTREE = HERE.parents[4]
PACK = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R3P2_RESIDUAL_CONTRACT_RESUME_109_V1"
RAW = Path("/data/c16/awma/r20r3p2_residual_contract_resume_20261001/raw")
STEPS = (128, 136, 144, 152)


def tsv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def median_mad(values):
    center = statistics.median(values)
    return center, statistics.median(abs(x-center) for x in values)


def main():
    correctness = json.loads((RAW / "CANDIDATE_CORRECTNESS_SUMMARY.json").read_text())
    timing = json.loads((RAW / "DISCOVERY_TIMING_DECISION.json").read_text())
    if not correctness["all_four_qualified"] or timing["discovery_MATERIAL"] or timing["classification_if_stop"] != "R20R3_ACTIVE_WORLD_NO_MATERIAL_GAIN":
        raise RuntimeError("Discovery stop identity changed")
    correct_rows = []
    for step in STEPS:
        r = json.loads((RAW / f"CORRECTNESS_T{step}_RECEIPT.json").read_text())
        if not r["qualified"]:
            raise RuntimeError(f"Candidate t{step} correctness changed")
        pair = r["pair"]
        correct_rows.append({"step": step, "entry_sha256": r["arms"]["B0"]["entry_sha256"],
                             "B0_source_stop": int(r["source_stop"]["B0"]["pass"]),
                             "S1_source_stop": int(r["source_stop"]["S1"]["pass"]),
                             "nefc_exact": int(pair["discrete"]["nefc_exact"]),
                             "outer_niter_exact": int(pair["discrete"]["outer_niter_exact"]),
                             "non_LS_status_exact": int(pair["discrete"]["non_LS_overflow_exact"]),
                             "qacc_max_world_norm": pair["floating"]["qacc"]["max_world_normalized"],
                             "qfrc_max_world_norm": pair["floating"]["qfrc_constraint"]["max_world_normalized"],
                             "Ma_max_world_norm": pair["floating"]["efc.Ma"]["max_world_normalized"],
                             "valid_force_max_world_norm": pair["floating"]["efc.force"]["max_world_normalized"],
                             "LS_flag_changed_worlds": len(pair["LS_ITERATIONS_changed_worlds"]),
                             "no_constraint_worlds": r["no_constraint_world_count"],
                             "outer_limit_worlds": r["outer_iteration_limit_world_count"],
                             "worker_count": r["worker_count"], "qualified": 1})
    tsv(PACK / "CANDIDATE_CORRECTNESS.tsv", correct_rows)
    with (RAW / "DISCOVERY_TIMING_ALL_SAMPLES.tsv").open(newline="") as stream:
        samples = list(csv.DictReader(stream, delimiter="\t"))
    if len(samples) != 168:
        raise RuntimeError("Unexpected timing sample count")
    timing_rows = []
    for group in range(3):
        for step in STEPS:
            for arm in ("B0", "S1"):
                subset = [r for r in samples if int(r["group"]) == group and int(r["step"]) == step
                          and r["arm"] == arm and r["phase"] == "FORMAL"]
                if len(subset) != 5 or not all(r["sample_semantic_pass"] == "True" for r in subset):
                    raise RuntimeError("Formal sample semantic/count mismatch")
                wall, wall_mad = median_mad([float(r["wall_ms"]) for r in subset])
                event, event_mad = median_mad([float(r["cuda_event_ms"]) for r in subset])
                timing_rows.append({"group": group, "step": step, "arm": arm,
                                    "formal_samples": 5, "warmups": 2,
                                    "wall_median_ms": wall, "wall_MAD_ms": wall_mad,
                                    "event_median_ms": event, "event_MAD_ms": event_mad,
                                    "all_semantic_gates": 1})
    tsv(PACK / "DISCOVERY_TIMING.tsv", timing_rows)
    active_rows = []
    for step in STEPS:
        with np.load(RAW / f"B0_T{step}_R00_OUTPUT_AND_STOP.npz", allow_pickle=False) as z:
            niter = z["solver_niter"].copy()
        for iteration in range(10):
            active = int(np.count_nonzero(niter > iteration))
            active_rows.append({"step": step, "outer_iteration_zero_based": iteration,
                                "active_worlds_derived_from_final_niter": active,
                                "baseline_H_and_Cholesky_world_grid": 1024,
                                "S1_fixed_worker_world_grid": 304,
                                "S1_active_ID_count_derived": active,
                                "derivation": "post-run niter histogram; not an input to candidate; H may have zero changed rows and Cholesky may no-flip skip"})
    tsv(PACK / "ACTIVE_WORK_COUNTS.tsv", active_rows)
    print(json.dumps({"correctness_rows": len(correct_rows), "timing_rows": len(timing_rows),
                      "active_work_rows": len(active_rows), "classification": timing["classification_if_stop"]}, sort_keys=True))


if __name__ == "__main__":
    main()
