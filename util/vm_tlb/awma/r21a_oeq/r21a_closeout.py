#!/usr/bin/env python3
"""CPU-only R21A node164/source/compact review/hash closure."""

import csv
import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve()
WORKTREE = HERE.parents[4]
PACK = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R21A_OEQ_GRAPH_READINESS_109_V1"
ROOT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
RAW = ROOT / "raw"
NODE164 = Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r21a_oeq_graph_readiness_109_v1")
DATA = ROOT / "source/nequip-tutorial/sitraj.xyz"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def jwrite(name, value):
    (PACK / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    input_auth = json.loads((PACK / "INPUT_AUTHORITY.json").read_text())
    model_auth = json.loads((PACK / "MODEL_AUTHORITY.json").read_text())
    graph = json.loads((PACK / "DISCOVERY_GRAPH_AUTHORITY.json").read_text())
    a0 = json.loads((RAW / "A0_DATA_QUALIFICATION_STATUS.json").read_text())
    dready = json.loads((RAW / "DREADY_CORRECTNESS_STATUS.json").read_text())
    timing = json.loads((RAW / "DREADY_TIMING_STATUS.json").read_text())
    if input_auth["frame_count"] != 110 or model_auth["requested_id"] != "nequip.net:mir-group/NequIP-OAM-S:0.1":
        raise RuntimeError("Input/model identity changed")
    if not model_auth["loaded_runtime_object_verified"] or graph["edge_count"] != 1394:
        raise RuntimeError("Runtime model or graph not qualified")
    if a0["status"] != "A0_ATOMIC_BASELINE_QUALIFIED" or dready["status"] != "DREADY_NUMERICS_QUALIFIED":
        raise RuntimeError("Numerical authority absent")
    if timing["status"] != "DREADY_TIMING_COMPLETE" or timing["formal_sample_count"] != 30:
        raise RuntimeError("Formal first gate incomplete")
    if timing["Dready_MATERIAL"] or timing["classification_if_stop"] != "R21A_RESULT_MIXED_NEEDS_REVIEW":
        raise RuntimeError("Unexpected material/STOP identity")
    if (PACK / "DREADY_TIMING_CONTRACT.md").stat().st_mtime >= (RAW / "DREADY_TIMING.stdout.log").stat().st_mtime:
        raise RuntimeError("Timing contract not frozen before samples")
    source_commits = {"nequip": "27d9d2182da918ab7be0017d8300e53278f5e00e",
                      "OpenEquivariance": "dc9979099c65113adcc016977c5c60974f9ddafb",
                      "nequip-tutorial": "8f90935ba42fd9e03df323cf03428c456d87b881"}
    for repo, expected in source_commits.items():
        actual = subprocess.check_output(["git", "-C", str(ROOT / "source" / repo), "rev-parse", "HEAD"], text=True).strip()
        if actual != expected:
            raise RuntimeError(f"Source commit changed: {repo}")
    files = []
    for relative, path in (
        *((f"raw/{p.name}", p) for p in sorted(RAW.iterdir()) if p.is_file()),
        *((f"model/{p.name}", p) for p in sorted((ROOT / "model").iterdir()) if p.is_file()),
        *((f"compile/{p.name}", p) for p in sorted((ROOT / "compile").iterdir()) if p.is_file()),
        ("input/sitraj.xyz", DATA),
    ):
        files.append({"node164_path": str(NODE164 / relative), "node109_active_path": str(path),
                      "relative_path": relative, "bytes": path.stat().st_size, "sha256": sha(path)})
    with (PACK / "RAW_DATA_INDEX.tsv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(files[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(files)
    (ROOT / "NODE164_SHA256SUMS").write_text("".join(f"{f['sha256']}  {f['relative_path']}\n" for f in files))
    for subdir, src in (("raw", RAW), ("model", ROOT / "model"), ("compile", ROOT / "compile")):
        check = subprocess.run(["rsync", "-rcn", "--itemize-changes", str(src) + "/", f"hrl174new:{NODE164}/{subdir}/"],
                               capture_output=True, text=True, check=True)
        if check.stdout.strip():
            raise RuntimeError(f"node164 checksum difference in {subdir}: {check.stdout}")
    check_input = subprocess.run(["rsync", "-rcn", "--itemize-changes", str(DATA), f"hrl174new:{NODE164}/input/sitraj.xyz"],
                                 capture_output=True, text=True, check=True)
    if check_input.stdout.strip():
        raise RuntimeError("node164 exact input checksum difference")
    jwrite("PUBLICATION_VERIFICATION.json", {"node164_root": str(NODE164),
            "file_count": len(files), "bytes": sum(x["bytes"] for x in files),
            "checksum_dry_run_empty_all_subdirs": True,
            "NODE164_SHA256SUMS_path": str(NODE164 / "NODE164_SHA256SUMS"),
            "node174_role": "existing node164 storage gateway only; no local staging/compute"})
    jwrite("RUN_RECEIPTS.json", {
        "classification": "R21A_RESULT_MIXED_NEEDS_REVIEW",
        "source_commits": source_commits,
        "model_package_sha256": model_auth["sha256"], "input_sha256": input_auth["sha256"],
        "discovery_frame": 55, "holdout_frame_indices_frozen_but_unopened": [18, 36, 73, 91],
        "natural_receiver_nondecreasing": graph["natural_receiver_major"],
        "natural_sender_within_receiver_monotonic": graph["natural_sender_within_receiver_monotonic"],
        "A0_status": a0["status"], "A0_max_abs_energy_diff_mean": a0["max_abs_energy_diff_mean"],
        "A0_max_abs_force_diff_mean": a0["max_abs_force_diff_mean"],
        "Dready_status": dready["status"],
        "Dready_groups": timing["groups"],
        "Dready_median_relative_improvement": timing["median_relative_improvement"],
        "Dready_MATERIAL": False, "Donline_executed": False, "holdout_executed": False,
        "initial_AOT_example_data_failure_preserved": (RAW / "A0_COMPILED_FIRST_FAILURE_AUDIT.json").is_file(),
        "initial_unsorted_deterministic_failure_preserved": (RAW / "DETERMINISTIC_EAGER_PROBE_OUTPUTS.npz").is_file(),
        "compilation_repairs": ["exact frozen discovery-shaped --data-path for A0 and Dready",
                                "source key_registry registration for one edge-aligned int64 permutation input"],
        "deterministic_graph_repair": "one source-backed composite receiver+sender sort required for correct forces",
        "GPU_lock": "/data/c16/locks/c16_gpu_campaign.lock",
        "NSYS": 0, "NCU": 0, "NVBit": 0, "SASS": 0, "Accel_Sim": 0, "node174_compute": 0,
        "R20_reopened": False})
    pack_files = sorted(p for p in PACK.iterdir() if p.is_file() and p.name != "SHA256SUMS")
    code_files = sorted(p for p in HERE.parent.iterdir() if p.is_file() and p.suffix == ".py")
    (PACK / "SHA256SUMS").write_text("".join(
        f"{sha(p)}  {p.relative_to(WORKTREE)}\n" for p in pack_files + code_files))
    print(json.dumps({"classification": "R21A_RESULT_MIXED_NEEDS_REVIEW", "indexed_files": len(files),
                      "indexed_bytes": sum(x["bytes"] for x in files), "pack": str(PACK)}, sort_keys=True))


if __name__ == "__main__":
    main()
