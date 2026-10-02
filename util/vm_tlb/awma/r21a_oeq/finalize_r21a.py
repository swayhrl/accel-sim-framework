#!/usr/bin/env python3
"""CPU-only closeout of the already-stopped R21A Dready campaign."""

import csv
import difflib
import hashlib
import json
import math
import shutil
import subprocess
from pathlib import Path

import numpy as np


ROOT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
RAW = ROOT / "raw"
WT = Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r21a-oeq-graph-readiness-109-v1")
PACK = WT / "docs/vm_tlb/review_packs/AWMA_R21A_OEQ_GRAPH_READINESS_109_V1"
RUN_ID = "AWMA_R21A_OEQ_GRAPH_READINESS_109_V1_20261002"
REMOTE_HOST = "hrl174new"
REMOTE_ROOT = Path("/root/share/mnt164/huangrulin/awma/r21a_oeq_graph_readiness_109_v1")
REMOTE_PATH = REMOTE_ROOT / RUN_ID
COPYBACK = ROOT / "copyback_verify" / RUN_ID


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tensor_sha(value):
    array = np.ascontiguousarray(value)
    return hashlib.sha256(memoryview(array.view(np.uint8))).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_tsv(path, rows, fields):
    with Path(path).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def mismatch(ref, observed):
    bad = ~np.isfinite(observed) | ~np.isclose(ref, observed, atol=5e-5, rtol=5e-5)
    if not np.any(bad):
        return None
    index = tuple(int(item) for item in np.argwhere(bad)[0])
    return {"index": index, "reference": float(ref[index]), "observed": float(observed[index])}


def git_head(path):
    return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()


def main():
    PACK.mkdir(parents=True, exist_ok=True)
    timing = json.loads((RAW / "DREADY_TIMING_STATUS.json").read_text())
    if timing["status"] != "DREADY_TIMING_COMPLETE" or timing["Dready_MATERIAL"] is not False:
        raise SystemExit("Dready STOP authority is not the frozen mixed result")
    if timing["classification_if_stop"] != "R21A_RESULT_MIXED_NEEDS_REVIEW":
        raise SystemExit("unexpected Dready classification")
    if any(RAW.glob("DONLINE*")) or any(RAW.glob("HOLDOUT*")):
        raise SystemExit("forbidden downstream output exists")

    runtime = json.loads((RAW / "RUNTIME_ADMISSION.json").read_text())
    graph = json.loads((RAW / "DISCOVERY_GRAPH_AUTHORITY.json").read_text())
    a0 = json.loads((RAW / "A0_DATA_QUALIFICATION_STATUS.json").read_text())
    dready = json.loads((RAW / "DREADY_CORRECTNESS_STATUS.json").read_text())
    input_authority = json.loads((PACK / "INPUT_AUTHORITY.json").read_text())
    model_authority = json.loads((PACK / "MODEL_AUTHORITY.json").read_text())

    source = {
        "stage": "AWMA_R21A_OEQ_GRAPH_READINESS_109_V1",
        "literature_authority": {"commit": "18005684c6ca0f0e6804b10ecfb411d80ae83e26",
                                  "file": "docs/vm_tlb/literature_notes/awma/rounds/2026-10-02_ROUND_21A_SOURCE_INPUT_QUALIFICATION.md"},
        "execution_start": {"commit": "bc1be3ec465346d1c9f1159392f1f653f19fd7fe",
                            "tree": "dfdbe4b90aa7f0a00f8980b3f8d7979a083e977d",
                            "scientific_parent": "0c6cda2f680fa93ed5ea7d4b098eef5044a8a0c4"},
        "nequip": {"commit": git_head(ROOT / "source/nequip")},
        "OpenEquivariance": {"commit": git_head(ROOT / "source/OpenEquivariance")},
        "input_repo": {"commit": git_head(ROOT / "source/nequip-tutorial"),
                       "git_blob": subprocess.check_output(["git", "-C", str(ROOT / "source/nequip-tutorial"), "hash-object", "sitraj.xyz"], text=True).strip()},
        "model_package_sha256": sha(ROOT / "model/NequIP-OAM-S-0.1.nequip.zip"),
        "input_sha256": sha(ROOT / "source/nequip-tutorial/sitraj.xyz"),
    }
    source["source_file_sha256"] = {
        "nequip/nequip/nn/_tp_scatter_oeq.py": sha(ROOT / "source/nequip/nequip/nn/_tp_scatter_oeq.py"),
        "nequip/nequip/nn/interaction_block.py": sha(ROOT / "source/nequip/nequip/nn/interaction_block.py"),
        "nequip/nequip/data/transforms/neighborlist.py": sha(ROOT / "source/nequip/nequip/data/transforms/neighborlist.py"),
        "OpenEquivariance/openequivariance/openequivariance/_torch/TensorProductConv.py": sha(ROOT / "source/OpenEquivariance/openequivariance/openequivariance/_torch/TensorProductConv.py"),
        "research_patch/deterministic_patch.py": sha(WT / "util/vm_tlb/awma/r21a_oeq/deterministic_patch.py"),
    }
    if source["nequip"]["commit"] != "27d9d2182da918ab7be0017d8300e53278f5e00e": raise SystemExit("NequIP source drift")
    if source["OpenEquivariance"]["commit"] != "dc9979099c65113adcc016977c5c60974f9ddafb": raise SystemExit("OEQ source drift")
    if source["input_repo"]["commit"] != "8f90935ba42fd9e03df323cf03428c456d87b881": raise SystemExit("input source drift")
    if source["input_repo"]["git_blob"] != "baac4e23364d00d29b2410fa60a92ade0cbf35a3": raise SystemExit("input blob drift")
    write_json(PACK / "SOURCE_BINDINGS.json", source)

    gpu = subprocess.check_output(["nvidia-smi", "--query-gpu=name,uuid,driver_version,compute_cap,memory.total", "--format=csv,noheader"], text=True).strip()
    platform = {"node": "109", "gpu_line": gpu, "TF32": "OFF", "python": runtime["python"],
                "torch_cuda_runtime": runtime["torch_cuda_runtime"], "packages": runtime["packages"],
                "source_commits": runtime["source_commits"], "model_runtime_loaded": runtime["actual_OAM_S_package_loaded"],
                "training": False, "NSYS": 0, "NCU": 0, "NVBit": 0, "SASS": 0, "AccelSim": 0,
                "current_gpu_compute_processes": subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader,nounits"], text=True).strip().splitlines()}
    write_json(PACK / "PLATFORM_RECEIPT.json", platform)
    model_authority.update({"loaded_runtime_object_verified": True,
                            "loaded_parameter_count": runtime["loaded_parameter_count"],
                            "loaded_parameter_dtypes": runtime["loaded_parameter_dtypes"],
                            "runtime_package_versions": runtime["packages"],
                            "runtime_status": runtime["status"]})
    write_json(PACK / "MODEL_AUTHORITY.json", model_authority)
    write_json(PACK / "DISCOVERY_GRAPH_AUTHORITY.json", graph)

    refs = []
    for run in a0["reference_runs"]:
        with np.load(run["payload_path"], allow_pickle=False) as data:
            refs.append((data["energy"].copy(), data["forces"].copy()))
    ref_e = np.mean(np.stack([item[0] for item in refs]), axis=0)
    ref_f = np.mean(np.stack([item[1] for item in refs]), axis=0)
    ref_rows = []
    for run, (energy, forces) in zip(a0["reference_runs"], refs):
        ref_rows.append({"repeat": run["repeat"], "energy": float(energy.reshape(-1)[0]),
                         "forces_shape": json.dumps(list(forces.shape), separators=(",", ":")),
                         "forces_sha256": tensor_sha(forces), "finite": np.isfinite(energy).all() and np.isfinite(forces).all(),
                         "payload_path": run["payload_path"], "payload_sha256": run["payload_sha256"]})
    write_tsv(PACK / "REFERENCE_NUMERICS.tsv", ref_rows,
              ["repeat", "energy", "forces_shape", "forces_sha256", "finite", "payload_path", "payload_sha256"])

    a0_rows = []
    for run in a0["A0_runs"]:
        with np.load(run["payload_path"], allow_pickle=False) as data:
            energy, forces = data["energy"].copy(), data["forces"].copy()
        diff_e, diff_f = np.abs(energy-ref_e), np.abs(forces-ref_f)
        a0_rows.append({"repeat": run["repeat"], "energy": float(energy.reshape(-1)[0]),
                        "max_abs_energy_diff": float(diff_e.max()), "max_abs_force_diff": float(diff_f.max()),
                        "force_rms_diff": float(np.sqrt(np.mean(diff_f**2))), "energy_first_mismatch": json.dumps(mismatch(ref_e, energy)),
                        "forces_first_mismatch": json.dumps(mismatch(ref_f, forces)), "finite": np.isfinite(energy).all() and np.isfinite(forces).all(),
                        "status": "PASS" if mismatch(ref_e, energy) is None and mismatch(ref_f, forces) is None else "FAIL",
                        "payload_path": run["payload_path"], "payload_sha256": run["payload_sha256"]})
    write_tsv(PACK / "A0_ATOMIC_QUALIFICATION.tsv", a0_rows,
              ["repeat", "energy", "max_abs_energy_diff", "max_abs_force_diff", "force_rms_diff", "energy_first_mismatch", "forces_first_mismatch", "finite", "status", "payload_path", "payload_sha256"])

    dready_rows = []
    for run in dready["runs"]:
        path = RAW / f"DREADY_RUN_{run['repeat']}.npz"
        with np.load(path, allow_pickle=False) as data:
            energy, forces = data["energy"].copy(), data["forces"].copy()
        diff_e, diff_f = np.abs(energy-ref_e), np.abs(forces-ref_f)
        dready_rows.append({"repeat": run["repeat"], "energy": float(energy.reshape(-1)[0]),
                            "max_abs_energy_diff": float(diff_e.max()), "max_abs_force_diff": float(diff_f.max()),
                            "force_rms_diff": float(np.sqrt(np.mean(diff_f**2))), "energy_first_mismatch": json.dumps(mismatch(ref_e, energy)),
                            "forces_first_mismatch": json.dumps(mismatch(ref_f, forces)), "finite": np.isfinite(energy).all() and np.isfinite(forces).all(),
                            "status": "PASS" if mismatch(ref_e, energy) is None and mismatch(ref_f, forces) is None else "FAIL",
                            "payload_path": str(path), "payload_sha256": sha(path)})
    write_tsv(PACK / "DREADY_CORRECTNESS.tsv", dready_rows,
              ["repeat", "energy", "max_abs_energy_diff", "max_abs_force_diff", "force_rms_diff", "energy_first_mismatch", "forces_first_mismatch", "finite", "status", "payload_path", "payload_sha256"])
    shutil.copy2(RAW / "DREADY_TIMING_ALL_SAMPLES.tsv", PACK / "DREADY_TIMING.tsv")

    patch_file = WT / "util/vm_tlb/awma/r21a_oeq/deterministic_patch.py"
    patch_lines = list(difflib.unified_diff([], patch_file.read_text().splitlines(True),
                                            fromfile="/dev/null", tofile="b/util/vm_tlb/awma/r21a_oeq/deterministic_patch.py"))
    (PACK / "DETERMINISTIC_SOURCE_DIFF.patch").write_text("".join(patch_lines))

    decision = f"""# Dready decision\n\nStatus: `R21A_RESULT_MIXED_NEEDS_REVIEW`.\n\nAll 30 formal outputs passed energy/force correctness. All three group medians favored Dready, but the median relative wall improvement was `{timing['median_relative_improvement']*100:.4f}%`, below the frozen 5% threshold. Groups 0 and 2 also failed `gap > 3× larger-arm MAD`; only group 1 passed that noise gate. Therefore Dready is not MATERIAL. Donline and holdouts are not authorized and were not run.\n"""
    (PACK / "DREADY_DECISION.md").write_text(decision)
    for name, status, reason in (
        ("DONLINE_CORRECTNESS.tsv", "NOT_RUN", "Dready not MATERIAL"),
        ("DONLINE_TIMING.tsv", "NOT_RUN", "Dready not MATERIAL"),
        ("HOLDOUT_GRAPH_AUTHORITY.tsv", "NOT_RUN", "Donline not admitted"),
        ("HOLDOUT_TIMING.tsv", "NOT_RUN", "Donline not admitted"),
    ):
        write_tsv(PACK / name, [{"status": status, "reason": reason}], ["status", "reason"])
    (PACK / "DONLINE_DECISION.md").write_text("# Donline decision\n\n`NOT_RUN`: Dready did not satisfy the MATERIAL gate.\n")

    repair = """# Engineering repair ledger\n\n- The first generic compiled A0 package produced nonfinite output; its partial output is preserved as `A0_RUN_0_PARTIAL.npz` and `A0_COMPILED_FIRST_FAILURE_AUDIT.json`. The bounded repair used NequIP's exact discovery-shaped `--data-path` AOT interface; five reference and five A0 outputs then qualified.\n- The first deterministic natural-order eager probe preserved receiver-major order but produced a force mismatch at `[0,0]` (reference about -0.144125, observed about -0.228056); the output is preserved. The source-backed `SortedNeighborListTransform` composite receiver/sender order plus its transpose permutation was required for correct deterministic forces. Edge/periodic-shift multiset remained exact and preparation occurs once per rebuilt graph, shared by both layers.\n- The first AOT candidate compile failed because `edge_transpose_perm` was not registered. The bounded repair registered it as an edge-aligned int64 field before compile.\n"""
    (PACK / "ENGINEERING_REPAIR_LEDGER.md").write_text(repair)

    final_text = f"""# Final decision — AWMA R21A OEQ graph readiness\n\n`R21A_RESULT_MIXED_NEEDS_REVIEW`\n\nThe official compiled atomic A0 and compiled deterministic-ready candidate both qualified numerically on real OAM-S frame 55. Free readiness produced a median `{timing['median_relative_improvement']*100:.4f}%` complete energy+force wall improvement, below 5%, with two of three groups failing the frozen 3×MAD gate. This is not a MATERIAL response. Donline and holdout validation were not run. No hardware, node174 compute, or Accel-Sim continuation is authorized.\n"""
    (PACK / "FINAL_DECISION.md").write_text(final_text)
    readme = f"""# AWMA R21A OEQ graph-readiness Native screen\n\nTrained model: `nequip.net:mir-group/NequIP-OAM-S:0.1`, package SHA256 `{source['model_package_sha256']}`. Real discovery geometry: pinned `sitraj.xyz` frame 55 of 110; the file is a collection of real periodic Si frames and is not interpreted as a time sequence.\n\nThe natural graph has 1,394 directed periodic edges and is receiver-major, but not sender-monotonic within receiver rows. The natural-order transpose-only deterministic probe failed forces; NequIP's source-backed composite receiver/sender ordering and one sender transpose permutation were needed. That prepared representation is shared across both interaction layers.\n\nA0 and Dready use the same official NequIP AOTInductor ASE CUDA path, float32 and TF32 OFF. A0 and Dready each passed five energy/force evaluations at `atol=rtol=5e-5`.\n\nDready did not pass the MATERIAL timing gate: median wall improvement `{timing['median_relative_improvement']*100:.4f}%`, below 5%, and only one of three groups passed 3×MAD. Final status is `R21A_RESULT_MIXED_NEEDS_REVIEW`; Donline and holdouts are NOT_RUN. This supports only a bounded Native diagnostic and no deployment, rebuild-frequency, temporal-MD, hardware, or cross-model claim.\n"""
    (PACK / "README.md").write_text(readme)

    # Assemble durable payload before writing the final index/receipt.
    payload = ROOT / "publish_payload" / RUN_ID
    if payload.exists():
        raise SystemExit(f"payload already exists: {payload}")
    (payload / "raw").mkdir(parents=True)
    (payload / "compile").mkdir()
    (payload / "model").mkdir()
    (payload / "input").mkdir()
    for path in RAW.iterdir():
        if path.is_file(): shutil.copy2(path, payload / "raw" / path.name)
    for path in (ROOT / "compile").iterdir():
        if path.is_file(): shutil.copy2(path, payload / "compile" / path.name)
    shutil.copy2(ROOT / "model/NequIP-OAM-S-0.1.nequip.zip", payload / "model")
    shutil.copy2(ROOT / "source/nequip-tutorial/sitraj.xyz", payload / "input")
    files = sorted(path for path in payload.rglob("*") if path.is_file())
    with (payload / "RAW_SHA256SUMS").open("w") as stream:
        for path in files: stream.write(f"{sha(path)}  {path.relative_to(payload).as_posix()}\n")
    if subprocess.run(["ssh", REMOTE_HOST, "test", "-e", str(REMOTE_PATH)]).returncode == 0:
        raise SystemExit(f"remote target exists: {REMOTE_PATH}")
    subprocess.run(["ssh", REMOTE_HOST, "mkdir", "-p", str(REMOTE_ROOT)], check=True)
    subprocess.run(["rsync", "-rt", "--no-owner", "--no-group", "--no-perms", f"{payload}/", f"{REMOTE_HOST}:{REMOTE_PATH}/"], check=True)
    remote_verify = subprocess.run(["ssh", REMOTE_HOST, f"cd {REMOTE_PATH} && sha256sum -c RAW_SHA256SUMS"], check=True, text=True, stdout=subprocess.PIPE).stdout
    if COPYBACK.exists(): raise SystemExit(f"copyback exists: {COPYBACK}")
    COPYBACK.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["rsync", "-rt", "--no-owner", "--no-group", "--no-perms", f"{REMOTE_HOST}:{REMOTE_PATH}/", f"{COPYBACK}/"], check=True)
    for path in files + [payload / "RAW_SHA256SUMS"]:
        other = COPYBACK / path.relative_to(payload)
        if not other.is_file() or other.stat().st_size != path.stat().st_size or sha(other) != sha(path):
            raise SystemExit(f"copyback mismatch: {path}")
    index_rows = []
    for path in files:
        relative = path.relative_to(payload).as_posix()
        index_rows.append({"artifact": relative, "node109_path": str(path), "bytes": path.stat().st_size,
                           "sha256": sha(path), "node164_path": str(REMOTE_PATH / relative)})
    write_tsv(PACK / "RAW_DATA_INDEX.tsv", index_rows, ["artifact", "node109_path", "bytes", "sha256", "node164_path"])
    run_receipt = {
        "status": "R21A_RESULT_MIXED_NEEDS_REVIEW", "run_id": RUN_ID,
        "gpu_lock_path": "/data/c16/locks/c16_gpu_campaign.lock",
        "scripts_require_R21A_GPU_LOCK_HELD": True,
        "durable_per_execution_lock_timestamp_receipt_present": False,
        "current_gpu_lock_held": False, "current_gpu_processes": platform["current_gpu_compute_processes"],
        "donline_run": False, "holdout_run": False, "node174_compute": False,
        "remote_path": str(REMOTE_PATH), "remote_verify": "PASS", "remote_verify_lines": len(remote_verify.splitlines()),
        "copyback_path": str(COPYBACK), "copyback_verify": "PASS",
        "raw_manifest_sha256": sha(payload / "RAW_SHA256SUMS"),
    }
    write_json(PACK / "RUN_RECEIPTS.json", run_receipt)
    pack_files = sorted(path for path in PACK.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    (PACK / "SHA256SUMS").write_text("".join(f"{sha(path)}  {path.name}\n" for path in pack_files))
    print(json.dumps({"status": run_receipt["status"], "remote": str(REMOTE_PATH),
                      "median_gain": timing["median_relative_improvement"], "pack_files": len(pack_files)}, sort_keys=True))


if __name__ == "__main__":
    main()
