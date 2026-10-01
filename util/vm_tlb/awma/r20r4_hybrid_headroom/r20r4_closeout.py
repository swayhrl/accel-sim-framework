#!/usr/bin/env python3
"""CPU-only accepted-authority and compact review/hash closure."""

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve()
WORKTREE = HERE.parents[4]
PACK = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R4_HYBRID_HEADROOM_AUDIT_109_V1"
P1_RAW = Path("/data/c16/awma/r20r3p1_profiler_repair_resume_20261001/raw")
P2_RAW = Path("/data/c16/awma/r20r3p2_residual_contract_resume_20261001/raw")
P1_PACK = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R3P1_PROFILER_REPAIR_AND_RESUME_109_V1"
P2_PACK = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R3P2_RESIDUAL_CONTRACT_RESUME_109_V1"
NODE164 = Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_tsv(path):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def main():
    PACK.mkdir(parents=True, exist_ok=True)
    receipt = json.loads((PACK / "PROFILE_DECOMPOSITION_RECEIPT.json").read_text())
    if receipt["classification"] != "PROFILE_DECOMPOSITION_QUALIFIED" or receipt["O2_aggregate_improvement"] < 0.05:
        raise RuntimeError("Decomposition/oracle gate changed")
    p1_profile = json.loads((P1_RAW / "REPAIRED_PROFILE_RECEIPT.json").read_text())
    p2_index = {Path(row["node109_active_path"]).name: row for row in read_tsv(P2_PACK / "RAW_DATA_INDEX.tsv")}
    p2_sha_lines = (P2_PACK / "SHA256SUMS").read_text().splitlines()
    p2_pack_hashes = {line.split("  ", 1)[1]: line.split("  ", 1)[0] for line in p2_sha_lines}
    p1_source = Path("/data/c16/awma/r20r3p1_profiler_repair_resume_20261001/source_overlay/mujoco_warp/_src/solver.py")
    sources = [
        ("P1_per_kernel_manifest", P1_RAW / "REPAIRED_PROFILE_ALL_KERNELS.tsv",
         NODE164 / "r20r3p1_profiler_repair_resume_109_v1/raw/REPAIRED_PROFILE_ALL_KERNELS.tsv",
         p1_profile["full_kernel_manifest_sha256"]),
        ("P1_NSYS_SQLite", P1_RAW / "REPAIRED_B0_FOUR_ENTRY_NSYS.sqlite",
         NODE164 / "r20r3p1_profiler_repair_resume_109_v1/raw/REPAIRED_B0_FOUR_ENTRY_NSYS.sqlite",
         p1_profile["sqlite_sha256"]),
        ("P1_profile_summary", P1_RAW / "REPAIRED_B0_PROFILE_SUMMARY.tsv",
         NODE164 / "r20r3p1_profiler_repair_resume_109_v1/raw/REPAIRED_B0_PROFILE_SUMMARY.tsv",
         p1_profile["compact_summary_sha256"]),
        ("P1_candidate_source", p1_source,
         NODE164 / "r20r3p1_profiler_repair_resume_109_v1/source_overlay/solver.py",
         "868cf9b0420d61656b3698ba7ddc93b6aa3d6a031d825c939a9868adf916a8e3"),
        ("P2_formal_samples", P2_RAW / "DISCOVERY_TIMING_ALL_SAMPLES.tsv",
         NODE164 / "r20r3p2_residual_contract_resume_109_v1/raw/DISCOVERY_TIMING_ALL_SAMPLES.tsv",
         p2_index["DISCOVERY_TIMING_ALL_SAMPLES.tsv"]["sha256"]),
        ("P2_active_counts", P2_PACK / "ACTIVE_WORK_COUNTS.tsv",
         None, p2_pack_hashes["docs/vm_tlb/review_packs/AWMA_R20R3P2_RESIDUAL_CONTRACT_RESUME_109_V1/ACTIVE_WORK_COUNTS.tsv"]),
        ("P2_compact_formal", P2_PACK / "DISCOVERY_TIMING.tsv",
         None, p2_pack_hashes["docs/vm_tlb/review_packs/AWMA_R20R3P2_RESIDUAL_CONTRACT_RESUME_109_V1/DISCOVERY_TIMING.tsv"]),
    ]
    rows = []
    for name, path, node164_path, expected in sources:
        observed = sha(path)
        if observed != expected:
            raise RuntimeError(f"Accepted source hash mismatch: {name}")
        rows.append({"authority": name, "node109_or_repo_path": str(path),
                     "accepted_node164_path": str(node164_path) if node164_path else "GIT_COMPACT_AUTHORITY",
                     "bytes": path.stat().st_size, "sha256": observed})
    with (PACK / "RAW_DATA_INDEX.tsv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    authority = {
        "stage": "AWMA_R20R4_HYBRID_HEADROOM_AUDIT_109_V1",
        "starting_commit": "2b76d71bdf8e98041f06301b5e16af3947874482",
        "starting_tree": "866fcc4d4d607ab6c332711bdce42a1bcae3d862",
        "scientific_parent": "3f4e3409ad629d5302a54e9c3a0f356bdc190456",
        "selected_stage": "_update_gradient_incremental", "worker_count_and_switch": 304,
        "accepted_candidate_source_sha256": sha(p1_source),
        "P1_selected_stage_cumulative_us": p1_profile["eligible_stage_cumulative_gpu_us"]["UPDATE_GRADIENT_INCREMENTAL"],
        "P2_formal_B0_input": "15 formal wall samples per entry; no new timing",
        "input_authority_hashes": {r["authority"]: r["sha256"] for r in rows},
        "GPU_work_this_goal": 0, "GPU_lock_acquired_this_goal": False,
    }
    (PACK / "PARENT_AUTHORITY.json").write_text(json.dumps(authority, indent=2, sort_keys=True) + "\n")
    pack_files = sorted(p for p in PACK.iterdir() if p.is_file() and p.name != "SHA256SUMS")
    code_files = sorted(p for p in HERE.parent.iterdir() if p.is_file() and p.suffix == ".py")
    (PACK / "SHA256SUMS").write_text("".join(
        f"{sha(path)}  {path.relative_to(WORKTREE)}\n" for path in pack_files + code_files))
    print(json.dumps({"classification": "R20R4_HYBRID_CANDIDATE_JUSTIFIED_FOR_REVIEW",
                      "accepted_raw_authorities": len(rows), "O1": receipt["O1_aggregate_improvement"],
                      "O2": receipt["O2_aggregate_improvement"]}, sort_keys=True))


if __name__ == "__main__":
    main()
