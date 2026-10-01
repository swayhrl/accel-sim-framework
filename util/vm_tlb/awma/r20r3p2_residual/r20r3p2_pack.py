#!/usr/bin/env python3
"""CPU-only R20R3P2 node164 and compact review/hash closure."""

import csv
import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve()
WORKTREE = HERE.parents[4]
PACK = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R3P2_RESIDUAL_CONTRACT_RESUME_109_V1"
ROOT = Path("/data/c16/awma/r20r3p2_residual_contract_resume_20261001")
RAW = ROOT / "raw"
NODE164 = Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r20r3p2_residual_contract_resume_109_v1")
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
    b0 = json.loads((RAW / "B0_ONLY_QUALIFICATION_SUMMARY.json").read_text())
    negative = json.loads((RAW / "DIRECTED_NEGATIVE_VALIDATOR.json").read_text())
    correct = json.loads((RAW / "CANDIDATE_CORRECTNESS_SUMMARY.json").read_text())
    timing = json.loads((RAW / "DISCOVERY_TIMING_DECISION.json").read_text())
    if not (b0["all_32_qualified"] and negative["all_directed_negatives_rejected"] and correct["all_four_qualified"]):
        raise RuntimeError("Science gates before timing not closed")
    if timing["discovery_MATERIAL"] or timing["classification_if_stop"] != "R20R3_ACTIVE_WORLD_NO_MATERIAL_GAIN":
        raise RuntimeError("Discovery terminal identity changed")
    if not timing["all_formal_samples_semantically_qualified"] or timing["formal_count"] != 120 or timing["warmup_count"] != 48:
        raise RuntimeError("Formal sample/semantic identity changed")
    if (PACK / "CONTRACT_DECISION.md").stat().st_mtime >= (RAW / "CANDIDATE_CORRECTNESS.stdout.log").stat().st_mtime:
        raise RuntimeError("Contract decision was not frozen before new candidate run")
    if (PACK / "TIMING_CONTRACT.md").stat().st_mtime >= (RAW / "DISCOVERY_TIMING.stdout.log").stat().st_mtime:
        raise RuntimeError("Timing contract was not frozen before formal samples")
    p1_pack = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R3P1_PROFILER_REPAIR_AND_RESUME_109_V1"
    candidate = ROOT / "source_overlay/mujoco_warp/_src/solver.py"
    p1_candidate = Path("/data/c16/awma/r20r3p1_profiler_repair_resume_20261001/source_overlay/mujoco_warp/_src/solver.py")
    if sha(candidate) != sha(p1_candidate) or sha(candidate) != "868cf9b0420d61656b3698ba7ddc93b6aa3d6a031d825c939a9868adf916a8e3":
        raise RuntimeError("Candidate source identity changed")
    jwrite("PARENT_AUTHORITY.json", {
        "stage": "AWMA_R20R3P2_RESIDUAL_CONTRACT_REQUALIFICATION_AND_RESUME_109_V1",
        "starting_commit": "36be18b1318dc68af2e65d10803f3f9120d3fdc5",
        "starting_tree": "f989412b2fab6e2d970ea1ad115cda4135e5d2f5",
        "scientific_parent": "53837e8366f0d96a636c89365b782aa411e7bc63",
        "old_parent_status_preserved": "R20R3_CANDIDATE_NUMERICS_NOT_QUALIFIED",
        "mujoco_warp_commit": "3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5",
        "pinned_solver_blob_git": "090061796792f4d11408eaa69b4ef3c44465c705",
        "P1_selected_candidate_source_sha256": sha(p1_candidate),
        "P2_same_candidate_source_sha256": sha(candidate),
        "P1_candidate_source_diff_sha256": sha(p1_pack / "CANDIDATE_SOURCE_DIFF.patch"),
        "selected_stage": "_update_gradient_incremental", "worker_count": 304,
        "discovery_entry_sha256": {str(step): sha(R1 / f"R2_T{step}_SOLVER_ENTRY_FULL_DATA.npz") for step in STEPS},
        "model_scene": "accepted G1 hfield / shuffle_dance, B1024 sparse Newton pyramidal conditional graph",
        "node164_root": str(NODE164),
    })
    jwrite("RUN_RECEIPTS.json", {
        "final_classification": "R20R3_ACTIVE_WORLD_NO_MATERIAL_GAIN",
        "source_semantic_contract_B0_replays": b0["completed_replays"],
        "all_B0_only_qualified": b0["all_32_qualified"],
        "directed_negatives_all_rejected": negative["all_directed_negatives_rejected"],
        "candidate_source_sha256": sha(candidate),
        "candidate_correctness_all_four": correct["all_four_qualified"],
        "candidate_worker_count": correct["worker_count"],
        "formal_warmup_samples": timing["warmup_count"],
        "formal_measurement_samples": timing["formal_count"],
        "all_formal_samples_semantically_qualified": timing["all_formal_samples_semantically_qualified"],
        "aggregate_groups": timing["groups"],
        "median_aggregate_relative_improvement": timing["median_aggregate_relative_improvement"],
        "discovery_MATERIAL": timing["discovery_MATERIAL"],
        "holdout_opened": False, "NSYS": 0, "NCU": 0, "NVBit": 0, "SASS": 0,
        "Accel_Sim": 0, "node174_compute": 0,
        "GPU_lock": "/data/c16/locks/c16_gpu_campaign.lock",
    })
    raw_rows = []
    for path in sorted(RAW.iterdir()):
        if path.is_file():
            raw_rows.append({"node164_path": str(NODE164 / "raw" / path.name),
                             "node109_active_path": str(path), "bytes": path.stat().st_size,
                             "sha256": sha(path)})
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
        raise RuntimeError("node164 source copy SHA mismatch")
    jwrite("PUBLICATION_VERIFICATION.json", {
        "node164_root": str(NODE164), "raw_file_count": len(raw_rows),
        "raw_bytes": sum(x["bytes"] for x in raw_rows),
        "raw_rsync_checksum_dry_run_empty": True,
        "source_sha256_local_and_node164": sha(candidate),
        "RAW_SHA256SUMS_node164_path": str(NODE164 / "RAW_SHA256SUMS"),
        "node174_role": "storage gateway only, no compute",
    })
    pack_files = sorted(x for x in PACK.iterdir() if x.is_file() and x.name != "SHA256SUMS")
    code_files = sorted(x for x in HERE.parent.iterdir() if x.is_file() and x.suffix == ".py")
    (PACK / "SHA256SUMS").write_text("".join(
        f"{sha(path)}  {path.relative_to(WORKTREE)}\n" for path in pack_files + code_files))
    print(json.dumps({"classification": "R20R3_ACTIVE_WORLD_NO_MATERIAL_GAIN",
                      "raw_files": len(raw_rows), "raw_bytes": sum(x["bytes"] for x in raw_rows),
                      "pack": str(PACK)}, sort_keys=True))


if __name__ == "__main__":
    main()
