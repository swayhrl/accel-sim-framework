#!/usr/bin/env python3
"""CPU-only compact review generation and SHA index; no science reruns."""

import csv
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve()
WORKTREE = HERE.parents[4]
PACK = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R2_LINESEARCH_SEMANTIC_MATERIALITY_109_V1"
ROOT = Path("/data/c16/awma/r20r2_linesearch_semantic_materiality_20261001")
RAW = ROOT / "raw"
NODE164 = Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r20r2_linesearch_semantic_materiality_109_v1")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_json(name, obj):
    (PACK / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def main():
    PACK.mkdir(parents=True, exist_ok=True)
    off = [json.loads(p.read_text()) for p in sorted(RAW.glob("OFF_[0-9][0-9]_RECEIPT.json"))]
    on = [json.loads(p.read_text()) for p in sorted(RAW.glob("ON_[0-9][0-9]_RECEIPT.json"))]
    analysis = json.loads((RAW / "CHRONOLOGICAL_FIRST_FLAG_PAIR_ANALYSIS.json").read_text())
    assert len(off) == 5 and len(on) == 31
    assert all(x["qualified"] for x in off + on)
    assert analysis["set_count"] == 1 and analysis["clear_count"] == 30
    for name, source in (("WORLD413_LINESEARCH_TRACES.json", RAW / "CHRONOLOGICAL_FIRST_FLAG_PAIR_TRACES.json"),
                         ("WORLD413_FLAG_PAIR_ANALYSIS.json", RAW / "CHRONOLOGICAL_FIRST_FLAG_PAIR_ANALYSIS.json")):
        shutil.copyfile(source, PACK / name)
    source_pinned = Path("/data/c16/awma/r20_active_world_native_v1/source/mujoco_warp/mujoco_warp/_src/solver.py")
    source_overlay = ROOT / "source_overlay/mujoco_warp/_src/solver.py"
    parent_contract = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_V1/LOCAL_NUMERICAL_CONTRACT.md"
    parent_authority = {
        "stage": "AWMA_R20R2_LINESEARCH_SEMANTIC_MATERIALITY_109_V1",
        "scientific_parent_commit": "8a1a8baf6ac5b6eff0c32f04b572eb1d34873d24",
        "mujoco_warp_commit": "3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5",
        "pinned_solver_blob_git": "090061796792f4d11408eaa69b4ef3c44465c705",
        "pinned_solver_sha256": sha(source_pinned),
        "observer_overlay_solver_sha256": sha(source_overlay),
        "t152_entry_sha256": "42e23fbdbb9aaae0dcbeacaa0e7ae278c1728bd9ff3a2881c8410e4f81f98e87",
        "parent_local_numerical_contract_sha256": sha(parent_contract),
        "model_scene": "benchmarks/unitree_g1/scene_hfield.xml; frozen scene/trajectory authority inherited from R20/R20R1",
        "B": 1024, "world": 413, "nefc": 46, "solver_niter": 8,
        "raw_node164_root": str(NODE164),
        "observer_default": "OFF: original pinned source; ON: isolated overlay source",
    }
    write_json("PARENT_AUTHORITY.json", parent_authority)
    off_summary = {
        "repeats": len(off), "all_parent_B0_validator_pass": all(r["qualified"] for r in off),
        "all_frozen_input_hashes_checked_each_run": True,
        "nefc_and_solver_niter_exact_each_run": all(r["nefc_exact"] and r["niter_exact"] for r in off),
        "no_novel_overflow_bits": all(r["overflow_excluding_LS_exact"] and r["no_new_capacity"] for r in off),
        "world413_LS_outcomes": sorted({r["world413_LS_ITERATIONS"] for r in off}),
        "max_perworld_qacc_normalized": max(r["floating"]["qacc"]["max_world_normalized"] for r in off),
        "source_sha256": off[0]["source_sha256"],
        "parent_B0_only_validator_rule": "floating, nefc/niter, non-LS overflow, finite, done and qfrc source relation; no candidate is run",
        "engineering_precheck_note": "An initial one-run OFF precheck incorrectly imposed a candidate-only residual ceiling on a new B0 repeat; preserved as OFF_PRE_GATE_FIX raw. The parent B0-only validator does not use that ceiling. It was corrected before the successful five-run OFF regression or any ON run.",
    }
    write_json("OBSERVER_OFF_REGRESSION.json", off_summary)
    rows = []
    for r in off + on:
        rows.append({"mode": r["mode"], "repeat": r["repeat"], "entry_sha256": r["entry_sha256"],
                     "source_sha256": r["source_sha256"], "nefc413": r["world413_nefc"],
                     "solver_niter413": r["world413_solver_niter"], "LS_ITERATIONS413": int(r["world413_LS_ITERATIONS"]),
                     "nefc_exact": int(r["nefc_exact"]), "niter_exact": int(r["niter_exact"]),
                     "other_overflow_exact": int(r["overflow_excluding_LS_exact"]),
                     "floating_contract_pass": int(all(x["contract_pass"] for x in r["floating"].values())),
                     "finite": int(r["finite"]), "capacity_clear": int(r["no_new_capacity"]),
                     "context_source_relation_pass": int(r["ctx_source_relation_pass"]),
                     "qualified": int(r["qualified"]), "raw_sha256": r["raw_sha256"]})
    with (PACK / "T152_REPEAT_SUMMARY.tsv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    write_json("RUN_RECEIPTS.json", {
        "OFF": json.loads((RAW / "OFF_SUMMARY.json").read_text()),
        "ON": json.loads((RAW / "ON_SUMMARY.json").read_text()),
        "observer_source_diff_sha256": sha(PACK / "OBSERVER_SOURCE_DIFF.patch"),
        "observer_launcher_sha256": sha(HERE.with_name("r20r2_observe.py")),
        "offline_analyzer_sha256": sha(HERE.with_name("r20r2_analyze.py")),
        "all_CUDA_operations_under_gpu_campaign_lock": True,
        "fresh_capture_needed": False,
        "S1_executed": False, "formal_timing_executed": False,
        "NSYS": 0, "NCU": 0, "NVBit": 0, "Accel_Sim": 0,
    })
    raw_rows = []
    for path in sorted(RAW.iterdir()):
        if path.is_file():
            raw_rows.append({"node164_path": str(NODE164 / "raw" / path.name), "bytes": path.stat().st_size,
                             "sha256": sha(path), "node109_active_path": str(path)})
    with (PACK / "RAW_DATA_INDEX.tsv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(raw_rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(raw_rows)
    (ROOT / "RAW_SHA256SUMS").write_text("".join(
        f"{row['sha256']}  raw/{Path(row['node109_active_path']).name}\n" for row in raw_rows))
    check = subprocess.run(
        ["rsync", "-rcn", "--itemize-changes", str(RAW) + "/", f"hrl174new:{NODE164}/raw/"],
        capture_output=True, text=True, check=True)
    if check.stdout.strip():
        raise RuntimeError("node164 raw checksum comparison found differences: " + check.stdout)
    remote_source = subprocess.run(
        ["ssh", "hrl174new", "sha256sum", str(NODE164 / "source_overlay/solver.py")],
        capture_output=True, text=True, check=True)
    if remote_source.stdout.split()[0] != sha(source_overlay):
        raise RuntimeError("node164 overlay source SHA mismatch")
    write_json("PUBLICATION_VERIFICATION.json", {
        "node164_root": str(NODE164), "raw_file_count": len(raw_rows),
        "raw_bytes": sum(x["bytes"] for x in raw_rows),
        "raw_rsync_checksum_dry_run_empty": True,
        "overlay_source_sha256_local_and_node164": sha(source_overlay),
        "raw_sha256sums_path_node164": str(NODE164 / "RAW_SHA256SUMS"),
        "node174_role": "Existing node164 storage gateway only; no compute",
    })
    pack_files = sorted(path for path in PACK.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    code_files = sorted(path for path in HERE.parent.iterdir() if path.is_file() and path.suffix == ".py")
    (PACK / "SHA256SUMS").write_text("".join(
        f"{sha(path)}  {path.relative_to(WORKTREE)}\n" for path in pack_files + code_files))
    print(json.dumps({"review_pack": str(PACK), "raw_files": len(raw_rows), "raw_bytes": sum(x["bytes"] for x in raw_rows),
                      "off": len(off), "on": len(on), "flag_pair": analysis["set_count"] == 1}, sort_keys=True))


if __name__ == "__main__":
    main()
