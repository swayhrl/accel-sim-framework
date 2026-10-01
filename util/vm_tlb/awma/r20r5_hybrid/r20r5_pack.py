#!/usr/bin/env python3
"""CPU-only R20R5 review/raw/hash closeout after formal hard-gate STOP."""

import csv
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve()
WORKTREE = HERE.parents[4]
PACK = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R5_HYBRID_ACTIVE_WORLD_NATIVE_109_V1"
ROOT = Path("/data/c16/awma/r20r5_hybrid_native_20261002")
RAW = ROOT / "raw"
NODE164 = Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r20r5_hybrid_native_109_v1")
R1 = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001/raw")
STEPS = (128, 136, 144, 152)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def jwrite(name, obj):
    (PACK / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def tsv(name, rows):
    with (PACK / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    nested = json.loads((RAW / "NESTED_CONDITIONAL_CANARY.json").read_text())
    branch = json.loads((RAW / "BRANCH_PATH_CANARY.json").read_text())
    baseline = json.loads((RAW / "BASELINE_SUMMARY.json").read_text())
    correctness = json.loads((RAW / "CANDIDATE_CORRECTNESS_SUMMARY.json").read_text())
    stop = json.loads((RAW / "FORMAL_SEMANTIC_STOP.json").read_text())
    if not (nested["nested_capture_replay_qualified"] and branch["all_five_pass"]
            and baseline["all_qualified"] and correctness["all_four_qualified"]):
        raise RuntimeError("Pre-formal hybrid gate identity changed")
    if stop["classification"] != "R20_ACTIVE_WORLD_LINE_CLOSED_HYBRID_NUMERICS_NOT_QUALIFIED" or stop["completed_formal_rows"] != 90:
        raise RuntimeError("Formal STOP identity changed")
    if (PACK / "HYBRID_CONTRACT.md").stat().st_mtime >= (RAW / "HYBRID_CORRECTNESS.stdout.log").stat().st_mtime:
        raise RuntimeError("Hybrid contract not frozen before correctness")
    if (PACK / "TIMING_CONTRACT.md").stat().st_mtime >= (RAW / "DISCOVERY_TIMING.stdout.log").stat().st_mtime:
        raise RuntimeError("Timing contract not frozen before formal samples")
    shutil.copyfile(RAW / "NESTED_CONDITIONAL_CANARY.json", PACK / "NESTED_CONDITIONAL_CANARY.json")
    tsv("BRANCH_PATH_CANARY.tsv", branch["cases"])
    off_rows = []
    corr_rows = []
    for step in STEPS:
        off = json.loads((RAW / f"BASELINE_T{step}_RECEIPT.json").read_text())
        corr = json.loads((RAW / f"CORRECTNESS_T{step}_RECEIPT.json").read_text())
        if not off["qualified"] or not corr["qualified"] or not corr["branch_trace"]["pass"]:
            raise RuntimeError(f"Pre-formal t{step} receipt changed")
        off_rows.append({"step": step, "entry_sha256": off["entry_sha256"], "source_sha256": off["source_sha256"],
                         "nefc_exact": int(off["nefc_exact"]), "outer_niter_exact": int(off["solver_niter_exact"]),
                         "non_LS_status_exact": int(off["non_LS_overflow_exact"]),
                         "floating_contract": int(all(x["pass"] for x in off["floating"].values())),
                         "qfrc_relation": int(off["qfrc_source_relation_pass"]),
                         "LS_ITERATIONS_count": off["LS_ITERATIONS_count"], "qualified": 1})
        pair = corr["pair"]
        trace = corr["branch_trace"]
        corr_rows.append({"step": step, "entry_sha256": off["entry_sha256"],
                          "B0_source_stop": int(corr["source_stop"]["B0"]["pass"]),
                          "H1_source_stop": int(corr["source_stop"]["H1"]["pass"]),
                          "nefc_exact": int(pair["discrete"]["nefc_exact"]),
                          "outer_niter_exact": int(pair["discrete"]["outer_niter_exact"]),
                          "non_LS_status_exact": int(pair["discrete"]["non_LS_overflow_exact"]),
                          "all_four_floating_screens": int(all(x["pass"] for x in pair["floating"].values())),
                          "LS_changed_worlds": len(pair["LS_ITERATIONS_changed_worlds"]),
                          "first_late_outer_iteration": trace["first_late_outer_iteration_zero_based"],
                          "early_invocations": trace["early_invocations"],
                          "late_invocations": trace["late_invocations"],
                          "late_active_counts": json.dumps(trace["late_active_counts"]),
                          "online_branch_trace_exact": int(trace["pass"]),
                          "no_constraint_worlds": corr["no_constraint_world_count"],
                          "outer_limit_worlds": corr["outer_iteration_limit_world_count"],
                          "qualified": 1})
    tsv("OFF_BASELINE_REGRESSION.tsv", off_rows)
    tsv("CANDIDATE_CORRECTNESS.tsv", corr_rows)
    candidate = ROOT / "source_overlay/mujoco_warp/_src/solver.py"
    p1_source = Path("/data/c16/awma/r20r3p1_profiler_repair_resume_20261001/source_overlay/mujoco_warp/_src/solver.py")
    p2_contract = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R3P2_RESIDUAL_CONTRACT_RESUME_109_V1/SOURCE_SEMANTIC_STOP_CONTRACT.md"
    r4_oracle = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R4_HYBRID_HEADROOM_AUDIT_109_V1/PROFILE_DECOMPOSITION_RECEIPT.json"
    if sha(candidate) != "aba0862337371bb1f09b24d2089654b5571b5be59e8f6695e97409c22e1680e8":
        raise RuntimeError("Hybrid source SHA mismatch")
    jwrite("PARENT_AUTHORITY.json", {
        "stage": "AWMA_R20R5_HYBRID_ACTIVE_WORLD_NATIVE_109_V1",
        "starting_commit": "e523466fc897f17f3309bff4ad02017d09ccb618",
        "starting_tree": "4775f8fa363ff8771d2eb5093e0113a488e3b867",
        "scientific_parent": "769ea5f3592976b2035beb76947b0d934d6efabf",
        "pinned_mujoco_warp_commit": "3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5",
        "pinned_solver_blob_git": "090061796792f4d11408eaa69b4ef3c44465c705",
        "accepted_P1_worker_source_sha256": sha(p1_source),
        "isolated_hybrid_source_sha256": sha(candidate),
        "hybrid_diff_sha256": sha(PACK / "HYBRID_SOURCE_DIFF.patch"),
        "accepted_P2_source_semantic_contract_sha256": sha(p2_contract),
        "accepted_R4_oracle_receipt_sha256": sha(r4_oracle),
        "fixed_threshold_and_worker_count": 304,
        "discovery_entry_sha256": {str(s): sha(R1 / f"R2_T{s}_SOLVER_ENTRY_FULL_DATA.npz") for s in STEPS},
        "node164_root": str(NODE164),
    })
    jwrite("RUN_RECEIPTS.json", {
        "classification": stop["classification"],
        "nested_conditional_canary_pass": nested["nested_capture_replay_qualified"],
        "branch_path_all_five_pass": branch["all_five_pass"],
        "OFF_all_four_qualified": baseline["all_qualified"],
        "B0_H1_correctness_all_four": correctness["all_four_qualified"],
        "debug_branch_observer_formal_timing": False,
        "formal_completed_samples": stop["completed_sample_rows_before_stop"],
        "formal_completed_warmups": stop["completed_warmup_rows"],
        "formal_completed_valid_measurements": stop["completed_formal_rows"],
        "formal_failed_sample": stop["failed_sample"],
        "full_120_semantic_sample_gate": False,
        "performance_verdict_permitted": False,
        "holdout_opened": False, "NSYS": 0, "NCU": 0, "NVBit": 0, "SASS": 0,
        "Accel_Sim": 0, "node174_compute": 0,
        "GPU_lock": "/data/c16/locks/c16_gpu_campaign.lock",
    })
    raw_rows = []
    for path in sorted(RAW.iterdir()):
        if path.is_file():
            raw_rows.append({"node164_path": str(NODE164 / "raw" / path.name),
                             "node109_active_path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)})
    tsv("RAW_DATA_INDEX.tsv", raw_rows)
    (ROOT / "RAW_SHA256SUMS").write_text("".join(
        f"{row['sha256']}  raw/{Path(row['node109_active_path']).name}\n" for row in raw_rows))
    remote = subprocess.run(["rsync", "-rcn", "--itemize-changes", str(RAW) + "/", f"hrl174new:{NODE164}/raw/"],
                            capture_output=True, text=True, check=True)
    if remote.stdout.strip():
        raise RuntimeError("node164 raw checksum comparison found differences: " + remote.stdout)
    source_check = subprocess.run(["ssh", "hrl174new", "sha256sum", str(NODE164 / "source_overlay/solver.py")],
                                  capture_output=True, text=True, check=True)
    if source_check.stdout.split()[0] != sha(candidate):
        raise RuntimeError("node164 hybrid source copy SHA mismatch")
    jwrite("PUBLICATION_VERIFICATION.json", {
        "node164_root": str(NODE164), "raw_file_count": len(raw_rows),
        "raw_bytes": sum(x["bytes"] for x in raw_rows),
        "raw_rsync_checksum_dry_run_empty": True,
        "source_overlay_sha256_local_and_node164": sha(candidate),
        "RAW_SHA256SUMS_node164_path": str(NODE164 / "RAW_SHA256SUMS"),
        "node174_role": "existing node164 storage gateway only; no compute",
    })
    pack_files = sorted(x for x in PACK.iterdir() if x.is_file() and x.name != "SHA256SUMS")
    code_files = sorted(x for x in HERE.parent.iterdir() if x.is_file() and x.suffix == ".py")
    (PACK / "SHA256SUMS").write_text("".join(
        f"{sha(path)}  {path.relative_to(WORKTREE)}\n" for path in pack_files + code_files))
    print(json.dumps({"classification": stop["classification"], "raw_files": len(raw_rows),
                      "raw_bytes": sum(x["bytes"] for x in raw_rows), "pack": str(PACK)}, sort_keys=True))


if __name__ == "__main__":
    main()
