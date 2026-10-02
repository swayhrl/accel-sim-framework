#!/usr/bin/env python3
"""CPU-only R21A compact numerical/profile-free decision tables."""

import csv
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
RAW = ROOT / "raw"
WORKTREE = Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r21a-oeq-graph-readiness-109-v1")
PACK = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R21A_OEQ_GRAPH_READINESS_109_V1"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def tsv(name, rows):
    with (PACK / name).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    PACK.mkdir(parents=True, exist_ok=True)
    input_auth = json.loads((PACK / "INPUT_AUTHORITY.json").read_text())
    model_auth = json.loads((PACK / "MODEL_AUTHORITY.json").read_text())
    runtime = json.loads((RAW / "RUNTIME_ADMISSION.json").read_text())
    graph = json.loads((RAW / "DISCOVERY_GRAPH_AUTHORITY.json").read_text())
    atomic = json.loads((RAW / "A0_DATA_QUALIFICATION_STATUS.json").read_text())
    deterministic = json.loads((RAW / "DREADY_CORRECTNESS_STATUS.json").read_text())
    timing = json.loads((RAW / "DREADY_TIMING_STATUS.json").read_text())
    if input_auth["frame_count"] != 110 or runtime["status"] != "MODEL_RUNTIME_LOADED":
        raise RuntimeError("Source/model input authority changed")
    if atomic["status"] != "A0_ATOMIC_BASELINE_QUALIFIED" or deterministic["status"] != "DREADY_NUMERICS_QUALIFIED":
        raise RuntimeError("Numerical qualification not closed")
    if timing["status"] != "DREADY_TIMING_COMPLETE" or timing["Dready_MATERIAL"] or timing["classification_if_stop"] != "R21A_RESULT_MIXED_NEEDS_REVIEW":
        raise RuntimeError("Dready decision identity changed")
    if (PACK / "DREADY_TIMING_CONTRACT.md").stat().st_mtime >= (RAW / "DREADY_TIMING.stdout.log").stat().st_mtime:
        raise RuntimeError("Timing contract was not frozen before formal timing")
    shutil.copyfile(RAW / "DISCOVERY_GRAPH_AUTHORITY.json", PACK / "DISCOVERY_GRAPH_AUTHORITY.json")
    model_auth.update({"loaded_runtime_object_verified": runtime["actual_OAM_S_package_loaded"],
                       "loaded_model_class": runtime["loaded_model_class"],
                       "loaded_parameter_count": runtime["loaded_parameter_count"],
                       "loaded_parameter_dtypes": runtime["loaded_parameter_dtypes"],
                       "runtime_discovery_model_metadata": json.loads((RAW / "REFERENCE_CANARY_STATUS.json").read_text())["model_metadata"],
                       "runtime_discovery_interaction_layers": json.loads((RAW / "REFERENCE_CANARY_STATUS.json").read_text())["interaction_layer_names"]})
    (PACK / "MODEL_AUTHORITY.json").write_text(json.dumps(model_auth, indent=2, sort_keys=True) + "\n")
    platform = {"stage": "AWMA_R21A_OEQ_GRAPH_READINESS_109_V1",
                "GPU_name": runtime["GPU_name"], "GPU_capability": runtime["GPU_capability"],
                "driver": runtime["driver_line"], "python": runtime["python"],
                "torch_cuda_runtime": runtime["torch_cuda_runtime"], "packages": runtime["packages"],
                "isolated_env": str(ROOT / "env"),
                "read_only_dependency_base": "/data/c16/awma/vla_rtc_vjp_boundary_20260930/env/lib/python3.12/site-packages",
                "accepted_envs_or_driver_modified": False,
                "TF32": "OFF", "source_NequIP_commit": "27d9d2182da918ab7be0017d8300e53278f5e00e",
                "source_OEQ_commit": "dc9979099c65113adcc016977c5c60974f9ddafb"}
    (PACK / "PLATFORM_RECEIPT.json").write_text(json.dumps(platform, indent=2, sort_keys=True) + "\n")
    sources = {"nequip_repo": "mir-group/nequip", "nequip_commit": platform["source_NequIP_commit"],
               "oeq_repo": "PASSIONLab/OpenEquivariance", "oeq_commit": platform["source_OEQ_commit"],
               "input_repo": "mir-group/nequip-tutorial", "input_commit": input_auth["commit"],
               "input_blob": input_auth["git_blob"], "input_sha256": input_auth["sha256"],
               "model_id": model_auth["requested_id"], "model_package_sha256": model_auth["sha256"],
               "model_zenodo_md5": model_auth["zenodo_declared_md5"],
               "source_backed_atomic": "pinned _tp_scatter_oeq.py TensorProductConv(... deterministic=False)",
               "source_backed_deterministic": "pinned OEQ TensorProductConv(... deterministic=True) requires receiver-row order and sender_perm",
               "source_backed_preparation": "pinned NequIP SortedNeighborListTransform composite receiver*N+sender reorder, aligned cell shifts, argsort(sender*N+receiver)",
               "official_AOT_mode": "nequip-compile --mode aotinductor --device cuda --target ase --no-tf32, exact discovery-shaped --data-path",
               "original_example_AOT_failure_retained": True,
               "research_patch_sha256": sha(WORKTREE / "util/vm_tlb/awma/r21a_oeq/deterministic_patch.py")}
    (PACK / "SOURCE_BINDINGS.json").write_text(json.dumps(sources, indent=2, sort_keys=True) + "\n")
    ref_rows = []
    for row in atomic["reference_runs"]:
        ref_rows.append({"repeat": row["repeat"], "energy": row["energy"],
                         "energy_finite": int(row["energy_finite"]), "forces_finite": int(row["forces_finite"]),
                         "first_energy_mismatch_vs_reference_mean": str(row["energy_first_mismatch_vs_reference_mean"]),
                         "first_force_mismatch_vs_reference_mean": str(row["forces_first_mismatch_vs_reference_mean"]),
                         "output_payload_sha256": row["payload_sha256"]})
    tsv("REFERENCE_NUMERICS.tsv", ref_rows)
    a0_rows = []
    for row in atomic["A0_runs"]:
        a0_rows.append({"repeat": row["repeat"], "energy": row["energy"],
                        "energy_finite": int(row["energy_finite"]), "forces_finite": int(row["forces_finite"]),
                        "first_energy_mismatch_vs_reference_mean": str(row["energy_first_mismatch_vs_reference_mean"]),
                        "first_force_mismatch_vs_reference_mean": str(row["forces_first_mismatch_vs_reference_mean"]),
                        "output_payload_sha256": row["payload_sha256"]})
    tsv("A0_ATOMIC_QUALIFICATION.tsv", a0_rows)
    d_rows = []
    for row in deterministic["runs"]:
        d_rows.append({"repeat": row["repeat"], "energy": row["energy"],
                       "energy_finite": int(row["energy_finite"]), "forces_finite": int(row["forces_finite"]),
                       "first_energy_mismatch": str(row["energy_first_mismatch"]),
                       "first_force_mismatch": str(row["forces_first_mismatch"]),
                       "output_payload_sha256": row["output_sha256"]})
    tsv("DREADY_CORRECTNESS.tsv", d_rows)
    time_rows = []
    for group in timing["groups"]:
        for arm in ("A0", "Dready"):
            row = group[arm]
            time_rows.append({"group": group["group"], "arm": arm, "formal_samples": 5, "warmups": 2,
                              "wall_median_ms": row["wall_median_ms"], "wall_MAD_ms": row["wall_MAD_ms"],
                              "event_median_ms": row["event_median_ms"], "event_MAD_ms": row["event_MAD_ms"],
                              "group_Dready_relative_improvement": group["relative_improvement"],
                              "group_gap_gt_3x_larger_MAD": int(group["gap_gt_3x_larger_MAD"]),
                              "all_formal_numeric_pass": int(timing["all_30_formal_numeric_pass"])})
    tsv("DREADY_TIMING.tsv", time_rows)
    print(json.dumps({"classification": timing["classification_if_stop"],
                      "N": input_auth["frame_count"], "discovery": 55,
                      "edge_count": graph["edge_count"], "natural_receiver_major": graph["natural_receiver_major"],
                      "median_Dready_improvement": timing["median_relative_improvement"]}, sort_keys=True))


if __name__ == "__main__":
    main()
