#!/usr/bin/env python3
"""CPU-only R20R3 evidence and publication closure."""

import csv
import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve()
WORKTREE = HERE.parents[4]
PACK = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R3_ACTIVE_WORLD_SOLVER_NATIVE_109_V1"
ROOT = Path("/data/c16/awma/r20r3_active_world_solver_native_20261001")
RAW = ROOT / "raw"
NODE164 = Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r20r3_active_world_solver_native_109_v1")
R1 = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001")
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
    PACK.mkdir(parents=True, exist_ok=True)
    baseline = json.loads((RAW / "BASELINE_SUMMARY.json").read_text())
    profile = json.loads((RAW / "PROFILE_SUMMARY.json").read_text())
    if not (baseline["all_qualified"] and profile["all_qualified"]):
        raise RuntimeError("OFF or profile workload numerical gate did not pass")
    if baseline["entry_order"] != list(STEPS) or profile["entry_order"] != list(STEPS):
        raise RuntimeError("Four-entry order changed")
    pinned = Path("/data/c16/awma/r20_active_world_native_v1/source/mujoco_warp/mujoco_warp/_src/solver.py")
    overlay = ROOT / "source_overlay/mujoco_warp/_src/solver.py"
    if sha(pinned) != sha(overlay):
        raise RuntimeError("OFF solver overlay differs from pinned source")
    contract = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_V1/LOCAL_NUMERICAL_CONTRACT.md"
    r2 = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R2_LINESEARCH_SEMANTIC_MATERIALITY_109_V1/FINAL_DECISION.md"
    jwrite("PARENT_AUTHORITY.json", {
        "stage": "AWMA_R20R3_ACTIVE_WORLD_SOLVER_NATIVE_109_V1",
        "starting_commit": "2b9783a4a28691c7c762bcfb7c8c3a8c115cff36",
        "starting_tree": "88987ebdb5c756512ac6a65caa234efbc9420902",
        "scientific_parent": "e645b5e011c18f1e44b7a1509fb55c49486adff5",
        "mujoco_warp_commit": "3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5",
        "solver_blob_git": "090061796792f4d11408eaa69b4ef3c44465c705",
        "solver_sha256_pinned_and_off_overlay": sha(pinned),
        "R20R1_local_numerical_contract_sha256": sha(contract),
        "R20R2_final_decision_sha256": sha(r2),
        "discovery_entry_sha256": {str(step): sha(R1 / f"raw/R2_T{step}_SOLVER_ENTRY_FULL_DATA.npz") for step in STEPS},
        "model_and_scene": "R20/R20R1 accepted G1 hfield/shuffle_dance B1024 sparse Newton pyramidal conditional-graph authority",
        "node164_raw_root": str(NODE164 / "raw"),
    })
    rows = []
    for step in STEPS:
        receipt = json.loads((RAW / f"BASELINE_T{step}_RECEIPT.json").read_text())
        rows.append({"step": step, "entry_sha256": receipt["entry_sha256"],
                     "source_sha256": receipt["source_sha256"], "qualified": int(receipt["qualified"]),
                     "nefc_exact": int(receipt["nefc_exact"]),
                     "outer_niter_exact": int(receipt["solver_niter_exact"]),
                     "other_overflow_exact": int(receipt["non_LS_overflow_exact"]),
                     "capacity_clear": int(receipt["no_new_capacity_overflow"]),
                     "floating_contract_pass": int(all(x["pass"] for x in receipt["floating"].values())),
                     "qfrc_source_relation_pass": int(receipt["qfrc_source_relation_pass"]),
                     "LS_ITERATIONS_count": receipt["LS_ITERATIONS_count"],
                     "output_payload_sha256": receipt["output_payload_sha256"]})
    tsv("OFF_BASELINE_REGRESSION.tsv", rows)
    tsv("B0_PROFILE_SUMMARY.tsv", [
        {"step": step, "workload_qualified": int(json.loads((RAW / f"PROFILE_T{step}_RECEIPT.json").read_text())["qualified"]),
         "nsys_kernel_time": "UNAVAILABLE_NO_REPORT", "eligible_stage_rank": "NOT_COMPUTABLE",
         "cause": "One NSYS job produced no report/SQLite/qdstrm"}
        for step in STEPS])
    audit = PACK / "ELIGIBLE_STAGE_AUDIT.md"
    profile_log = RAW / "NSYS_RUN.stdout.log"
    if audit.stat().st_mtime >= profile_log.stat().st_mtime:
        raise RuntimeError("Eligible-stage audit was not frozen before NSYS output")
    jwrite("RUN_RECEIPTS.json", {
        "OFF_B0_regression": baseline, "NSYS_workload": profile,
        "eligible_stage_audit_sha256": sha(audit),
        "audit_mtime_precedes_nsys_stdout": True,
        "NSYS_jobs_executed": 1, "NSYS_report_count": 0,
        "NSYS_command": "nsys profile --trace=cuda,nvtx --cuda-graph-trace=node --capture-range=nvtx --nvtx-capture=R20R3_PROFILE --capture-range-end=stop --sample=none --cpuctxsw=none --export=sqlite",
        "GPU_lock": "/data/c16/locks/c16_gpu_campaign.lock",
        "S1_constructed": False, "formal_timing_run": False, "holdout_opened": False,
        "NCU": 0, "NVBit": 0, "SASS": 0, "Accel_Sim": 0, "node174_compute": 0,
        "classification": "R20R3_ACTIVE_WORLD_DIAGNOSTIC_NOT_QUALIFIED",
    })
    raw_rows = []
    for path in sorted(RAW.iterdir()):
        if path.is_file():
            raw_rows.append({"node164_path": str(NODE164 / "raw" / path.name),
                             "node109_active_path": str(path), "bytes": path.stat().st_size, "sha256": sha(path)})
    tsv("RAW_DATA_INDEX.tsv", raw_rows)
    (ROOT / "RAW_SHA256SUMS").write_text("".join(
        f"{row['sha256']}  raw/{Path(row['node109_active_path']).name}\n" for row in raw_rows))
    remote = subprocess.run(
        ["rsync", "-rcn", "--itemize-changes", str(RAW) + "/", f"hrl174new:{NODE164}/raw/"],
        capture_output=True, text=True, check=True)
    if remote.stdout.strip():
        raise RuntimeError("node164 raw checksum comparison found differences")
    jwrite("PUBLICATION_VERIFICATION.json", {
        "node164_raw_root": str(NODE164 / "raw"),
        "file_count": len(raw_rows), "raw_bytes": sum(x["bytes"] for x in raw_rows),
        "rsync_checksum_dry_run_empty": True,
        "RAW_SHA256SUMS_node164_path": str(NODE164 / "RAW_SHA256SUMS"),
        "node174_role": "storage gateway only",
    })
    pack_files = sorted(x for x in PACK.iterdir() if x.is_file() and x.name != "SHA256SUMS")
    code_files = sorted(x for x in HERE.parent.iterdir() if x.is_file() and x.suffix == ".py")
    (PACK / "SHA256SUMS").write_text("".join(
        f"{sha(path)}  {path.relative_to(WORKTREE)}\n" for path in pack_files + code_files))
    print(json.dumps({"classification": "R20R3_ACTIVE_WORLD_DIAGNOSTIC_NOT_QUALIFIED",
                      "raw_files": len(raw_rows), "raw_bytes": sum(x["bytes"] for x in raw_rows),
                      "pack": str(PACK)}, sort_keys=True))


if __name__ == "__main__":
    main()
