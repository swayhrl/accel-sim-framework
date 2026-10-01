#!/usr/bin/env python3
"""CPU-only B0 qualification rollup and pre-S1 candidate identity freeze."""

import csv
import hashlib
import json
import shutil
from pathlib import Path


HERE = Path(__file__).resolve()
WORKTREE = HERE.parents[4]
PACK = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R3P2_RESIDUAL_CONTRACT_RESUME_109_V1"
ROOT = Path("/data/c16/awma/r20r3p2_residual_contract_resume_20261001")
RAW = ROOT / "raw"
P1 = Path("/data/c16/awma/r20r3p1_profiler_repair_resume_20261001")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_tsv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    PACK.mkdir(parents=True, exist_ok=True)
    summary = json.loads((RAW / "B0_ONLY_QUALIFICATION_SUMMARY.json").read_text())
    negative = json.loads((RAW / "DIRECTED_NEGATIVE_VALIDATOR.json").read_text())
    if not summary["all_32_qualified"] or summary["completed_replays"] != 32 or not negative["all_directed_negatives_rejected"]:
        raise RuntimeError("B0-only/new-contract gate not qualified")
    rows = []
    predicates = []
    for step in (128, 136, 144, 152):
        aggregate = {key: 0 for key in ("alpha_zero", "positive_improvement_below_tol", "gradient_below_tol",
                                         "model_improvement_below_tol", "any_source_predicate", "multiple_predicates")}
        new_iter = inherited_iter = limit_stops = final_pred = ls_count = 0
        hist = {}
        for repeat in range(8):
            receipt = json.loads((RAW / f"B0_T{step}_R{repeat:02d}_RECEIPT.json").read_text())
            stop, hard = receipt["source_stop"], receipt["original_hard_gates"]
            if not receipt["qualified"]:
                raise RuntimeError(f"Unexpected failed B0 at {step}/{repeat}")
            rows.append({"step": step, "repeat": repeat, "entry_sha256": receipt["entry_sha256"],
                         "all_hard_gates": int(hard["qualified"]), "source_stop_consistent": int(stop["pass"]),
                         "nefc_exact": int(hard["nefc_exact"]), "outer_niter_exact": int(hard["solver_niter_exact"]),
                         "non_LS_status_exact": int(hard["non_LS_overflow_exact"]),
                         "capacity_clear": int(hard["no_new_capacity_overflow"]),
                         "finite": int(hard["finite"]), "done": int(hard["ctx_done_all"]),
                         "qfrc_relation": int(hard["qfrc_source_relation_pass"]),
                         "new_ITERATIONS_count": len(stop["new_ITERATIONS_worlds"]),
                         "limit_stop_count": stop["limit_stop_nonpredicate_count"],
                         "LS_ITERATIONS_count": len(stop["LS_ITERATIONS_exit_worlds"]),
                         "qacc_max_world_norm": hard["floating"]["qacc"]["max_world_normalized"],
                         "qfrc_max_world_norm": hard["floating"]["qfrc_constraint"]["max_world_normalized"],
                         "payload_sha256": receipt["payload_sha256"]})
            for name, count in stop["predicate_counts"].items():
                aggregate[name] += count
            for niter, count in stop["niter_histogram"].items():
                hist[niter] = hist.get(niter, 0) + count
            new_iter += len(stop["new_ITERATIONS_worlds"])
            inherited_iter += len(stop["inherited_ITERATIONS_worlds"])
            limit_stops += stop["limit_stop_nonpredicate_count"]
            final_pred += stop["predicate_done_on_final_iteration_count"]
            ls_count += len(stop["LS_ITERATIONS_exit_worlds"])
        predicates.append({"step": step, "B0_repeats": 8,
                           "niter_histogram_across_repeats": json.dumps(hist, sort_keys=True),
                           **aggregate, "new_ITERATIONS_count": new_iter,
                           "inherited_ITERATIONS_count": inherited_iter,
                           "limit_stop_nonpredicate_count": limit_stops,
                           "predicate_done_on_final_iteration_count": final_pred,
                           "LS_ITERATIONS_exit_count": ls_count})
    write_tsv(PACK / "B0_ONLY_RESIDUAL_QUALIFICATION.tsv", rows)
    write_tsv(PACK / "B0_STOP_PREDICATE_SUMMARY.tsv", predicates)
    shutil.copyfile(RAW / "DIRECTED_NEGATIVE_VALIDATOR.json", PACK / "DIRECTED_NEGATIVE_VALIDATOR.json")
    p2_source = ROOT / "source_overlay/mujoco_warp/_src/solver.py"
    p1_source = P1 / "source_overlay/mujoco_warp/_src/solver.py"
    p1_diff = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R3P1_PROFILER_REPAIR_AND_RESUME_109_V1/CANDIDATE_SOURCE_DIFF.patch"
    if sha(p2_source) != sha(p1_source) or sha(p2_source) != "868cf9b0420d61656b3698ba7ddc93b6aa3d6a031d825c939a9868adf916a8e3":
        raise RuntimeError("Parent selected candidate source identity mismatch")
    candidate = {"selected_stage": "_update_gradient_incremental", "worker_count": 304,
                 "P1_candidate_source_sha256": sha(p1_source), "P2_copied_source_sha256": sha(p2_source),
                 "parent_CANDIDATE_SOURCE_DIFF_sha256": sha(p1_diff),
                 "candidate_source_changed_in_P2": False,
                 "B0_all_32_qualified_before_S1": True,
                 "directed_negatives_all_rejected_before_S1": True}
    (PACK / "CANDIDATE_IDENTITY.json").write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"B0_all_32_qualified": True, "directed_negatives_all_rejected": True,
                      "candidate_source_sha256": candidate["P2_copied_source_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
