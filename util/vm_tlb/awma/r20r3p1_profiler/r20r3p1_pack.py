#!/usr/bin/env python3
"""CPU-only R20R3P1 compact review, node164 and SHA closure."""

import csv
import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve()
WORKTREE = HERE.parents[4]
PACK = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R3P1_PROFILER_REPAIR_AND_RESUME_109_V1"
ROOT = Path("/data/c16/awma/r20r3p1_profiler_repair_resume_20261001")
RAW = ROOT / "raw"
NODE164 = Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r20r3p1_profiler_repair_resume_109_v1")
R1 = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001/raw")
STEPS = (128, 136, 144, 152)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def jwrite(name, obj):
    (PACK / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def write_tsv(name, rows):
    with (PACK / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    PACK.mkdir(parents=True, exist_ok=True)
    canary = json.loads((PACK / "NSYS_CANARY_RECEIPT.json").read_text())
    profile = json.loads((PACK / "REPAIRED_PROFILE_RECEIPT.json").read_text())
    baseline = json.loads((RAW / "BASELINE_SUMMARY.json").read_text())
    correctness = json.loads((RAW / "CANDIDATE_CORRECTNESS_SUMMARY.json").read_text())
    failure = json.loads((RAW / "CANDIDATE_T128_RESIDUAL_FAILURE_AUDIT.json").read_text())
    if canary["classification"] != "NSYS_CANARY_QUALIFIED" or profile["classification"] != "REPAIRED_PROFILE_QUALIFIED":
        raise RuntimeError("Profiler admission not closed")
    if profile["selected_stage"] != "UPDATE_GRADIENT_INCREMENTAL":
        raise RuntimeError("Frozen stage selection changed")
    if not baseline["all_qualified"] or correctness["all_four_qualified"] or len(correctness["results"]) != 1:
        raise RuntimeError("Baseline/candidate stop identity differs")
    if failure["violating_world_count"] != 10 or failure["B0_violating_count"] != 11:
        raise RuntimeError("Residual failure audit changed")
    pinned = Path("/data/c16/awma/r20_active_world_native_v1/source/mujoco_warp/mujoco_warp/_src/solver.py")
    candidate = ROOT / "source_overlay/mujoco_warp/_src/solver.py"
    parent_pack = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R3_ACTIVE_WORLD_SOLVER_NATIVE_109_V1"
    jwrite("PARENT_AUTHORITY.json", {
        "stage": "AWMA_R20R3P1_PROFILER_REPAIR_AND_RESUME_109_V1",
        "starting_commit": "bc5af954c62fff92c6c28a56eae74e49eb20ffd1",
        "starting_tree": "f62e82117eda5bbeeaf58a4af431cfb0ecd82215",
        "scientific_parent": "fa292a11dbc196b65ebe1f3a67f39a7837046995",
        "mujoco_warp_commit": "3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5",
        "pinned_solver_blob_git": "090061796792f4d11408eaa69b4ef3c44465c705",
        "pinned_solver_sha256": sha(pinned), "candidate_overlay_solver_sha256": sha(candidate),
        "parent_eligible_stage_audit_sha256": sha(parent_pack / "ELIGIBLE_STAGE_AUDIT.md"),
        "parent_revised_numerical_contract_sha256": sha(parent_pack / "REVISED_NUMERICAL_CONTRACT.md"),
        "parent_R20R3_OFF_B0_source_sha256": "d26300bbe665aa182a0afc30c3d1ee43c38b8b14841e2e61544c92dea97af916",
        "discovery_entry_sha256": {str(s): sha(R1 / f"R2_T{s}_SOLVER_ENTRY_FULL_DATA.npz") for s in STEPS},
        "B": 1024, "scene": "G1 hfield/shuffle_dance accepted R20/R20R1 authority",
        "node164_root": str(NODE164),
    })
    jwrite("RUN_RECEIPTS.json", {
        "classification": "R20R3_CANDIDATE_NUMERICS_NOT_QUALIFIED",
        "canary_attempts": 2, "engineering_canary_qualified": True,
        "scientific_NSYS_jobs": 1, "scientific_profile_qualified": True,
        "profile_report_sha256": profile["report_sha256"],
        "profile_sqlite_sha256": profile["sqlite_sha256"],
        "selected_stage": profile["selected_stage"],
        "selected_stage_cumulative_gpu_us": profile["eligible_stage_cumulative_gpu_us"],
        "worker_count": 304, "SM_count": 76,
        "patched_OFF_all_four_qualified": True,
        "active_list_canaries": correctness["list_canaries"],
        "candidate_entries_attempted": [128], "candidate_t128_qualified": False,
        "t128_S1_final_gradient_violating_worlds": failure["violating_world_count"],
        "t128_B0_final_gradient_violating_worlds": failure["B0_violating_count"],
        "candidate_formal_timing_run": False, "holdout_opened": False,
        "GPU_lock": "/data/c16/locks/c16_gpu_campaign.lock",
        "NCU": 0, "NVBit": 0, "SASS": 0, "Accel_Sim": 0, "node174_compute": 0,
    })
    raw_rows = []
    for path in sorted(RAW.iterdir()):
        if path.is_file():
            raw_rows.append({"node164_path": str(NODE164 / "raw" / path.name),
                             "node109_active_path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)})
    write_tsv("RAW_DATA_INDEX.tsv", raw_rows)
    (ROOT / "RAW_SHA256SUMS").write_text("".join(
        f"{row['sha256']}  raw/{Path(row['node109_active_path']).name}\n" for row in raw_rows))
    remote = subprocess.run(["rsync", "-rcn", "--itemize-changes", str(RAW) + "/", f"hrl174new:{NODE164}/raw/"],
                            capture_output=True, text=True, check=True)
    if remote.stdout.strip():
        raise RuntimeError("node164 raw checksum comparison found differences: " + remote.stdout)
    source_check = subprocess.run(["ssh", "hrl174new", "sha256sum", str(NODE164 / "source_overlay/solver.py")],
                                  capture_output=True, text=True, check=True)
    if source_check.stdout.split()[0] != sha(candidate):
        raise RuntimeError("node164 candidate overlay source hash mismatch")
    jwrite("PUBLICATION_VERIFICATION.json", {
        "node164_root": str(NODE164), "raw_file_count": len(raw_rows),
        "raw_bytes": sum(x["bytes"] for x in raw_rows),
        "raw_rsync_checksum_dry_run_empty": True,
        "source_overlay_sha256_local_and_node164": sha(candidate),
        "RAW_SHA256SUMS_node164_path": str(NODE164 / "RAW_SHA256SUMS"),
        "node174_role": "existing node164 storage gateway only; no compute",
    })
    pack_files = sorted(path for path in PACK.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    code_files = sorted(path for path in HERE.parent.iterdir() if path.is_file() and path.suffix == ".py")
    (PACK / "SHA256SUMS").write_text("".join(
        f"{sha(path)}  {path.relative_to(WORKTREE)}\n" for path in pack_files + code_files))
    print(json.dumps({"classification": "R20R3_CANDIDATE_NUMERICS_NOT_QUALIFIED",
                      "raw_files": len(raw_rows), "raw_bytes": sum(x["bytes"] for x in raw_rows),
                      "pack": str(PACK)}, sort_keys=True))


if __name__ == "__main__":
    main()
