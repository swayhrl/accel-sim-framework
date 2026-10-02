#!/usr/bin/env python3
"""Five reference and five official compiled atomic OEQ evaluations on frozen graph."""

import hashlib
import json
import os
import traceback
from pathlib import Path

import numpy as np


ROOT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
RAW = ROOT / "raw"
MODEL = ROOT / "model/NequIP-OAM-S-0.1.nequip.zip"
COMPILED = ROOT / "compile/A0_ATOMIC_DISCOVERYDATA.nequip.pt2"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def first_mismatch(ref, other):
    mask = ~np.isclose(ref, other, atol=5e-5, rtol=5e-5)
    if not np.any(mask):
        return None
    at = tuple(int(x) for x in np.argwhere(mask)[0])
    return {"index": at, "reference": float(ref[at]), "observed": float(other[at]),
            "abs_diff": float(abs(other[at]-ref[at])),
            "allowed_atol_plus_rtol_abs_ref": float(5e-5+5e-5*abs(ref[at]))}


def main():
    if os.environ.get("R21A_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU lock receipt absent")
    import torch
    import openequivariance
    from nequip.data import AtomicDataDict
    from nequip.integrations.ase import NequIPCalculator
    from nequip.model import ModelFromPackage

    torch.set_default_dtype(torch.float32)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_float32_matmul_precision("highest")
    graph = json.loads((RAW / "DISCOVERY_GRAPH_AUTHORITY.json").read_text())
    with np.load(RAW / "DISCOVERY_NATURAL_GRAPH.npz", allow_pickle=False) as z:
        natural_cpu = {key: torch.from_numpy(z[key].copy()) for key in z.files}
    if sha(RAW / "DISCOVERY_NATURAL_GRAPH.npz") != graph["graph_npz_sha256"]:
        raise RuntimeError("Frozen graph payload SHA changed")
    status = {"stage": "AWMA_R21A_OEQ_GRAPH_READINESS_109_V1", "frame_index": 55,
              "frame_raw_sha256": graph["frame_raw_sha256"],
              "graph_sha256": sha(RAW / "DISCOVERY_GRAPH_AUTHORITY.json"),
              "graph_payload_sha256": graph["graph_npz_sha256"],
              "directed_edge_shift_multiset_sha256": graph["directed_edge_shift_multiset_sha256"],
              "model_package_sha256": sha(MODEL), "compiled_atomic_sha256": sha(COMPILED),
              "compile_data_path_sha256": sha(ROOT / "compile/DISCOVERY_FROZEN_INPUT.nequip_data.pt"),
              "A0_compile_mode": "official_nequip_AOTInductor_ase_enable_OpenEquivariance_TF32_OFF_exact_frozen_data_path",
              "reference_mode": "unmodified_packaged_e3nn_eager_correctness_only",
              "atol": 5e-5, "rtol": 5e-5,
              "reference_runs": [], "A0_runs": [], "first_mismatch": "NOT_YET_COMPARED",
              "status": "STARTED"}
    (RAW / "A0_DATA_QUALIFICATION_STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    try:
        reference = ModelFromPackage(str(MODEL), compile_mode="eager")["sole_model"].eval()
        for p in reference.parameters():
            p.requires_grad_(False)
        reference = reference.to("cuda")
        calc = NequIPCalculator.from_compiled_model(str(COMPILED), device="cuda", chemical_species_to_atom_type_map=True)
        atomic = calc.model.eval()
        # Both arms consume the same frozen natural graph; no labels or neighbor rebuild in the call.
        data_cuda = AtomicDataDict.to_(dict(natural_cpu), device=torch.device("cuda"))
        outputs = {"reference": [], "A0": []}
        for arm, model in (("reference", reference), ("A0", atomic)):
            for repeat in range(5):
                out = None
                try:
                    out = model(dict(data_cuda))
                    torch.cuda.synchronize()
                    energy = out[AtomicDataDict.TOTAL_ENERGY_KEY].detach().cpu().numpy().copy()
                    forces = out[AtomicDataDict.FORCE_KEY].detach().cpu().numpy().copy()
                    path = RAW / f"{arm.upper()}_DATA_RUN_{repeat}.npz"
                    np.savez_compressed(path, energy=energy, forces=forces)
                    row = {"repeat": repeat, "energy": energy.tolist(), "forces_shape": list(forces.shape),
                           "energy_finite": bool(np.isfinite(energy).all()), "forces_finite": bool(np.isfinite(forces).all()),
                           "payload_path": str(path), "payload_sha256": sha(path)}
                    status[f"{arm}_runs"].append(row)
                    outputs[arm].append((energy, forces))
                    (RAW / "A0_DATA_QUALIFICATION_STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
                    if not (row["energy_finite"] and row["forces_finite"]):
                        raise RuntimeError(f"Nonfinite {arm} output repeat {repeat}")
                except Exception:
                    if out is not None and isinstance(out, dict):
                        partial = {key: value.detach().cpu().numpy() for key, value in out.items() if isinstance(value, torch.Tensor)}
                        if partial:
                            path = RAW / f"{arm.upper()}_DATA_RUN_{repeat}_PARTIAL.npz"
                            np.savez_compressed(path, **partial)
                            status["partial_payload_sha256"] = sha(path)
                    raise
        ref_e = np.mean(np.stack([x[0] for x in outputs["reference"]]), axis=0)
        ref_f = np.mean(np.stack([x[1] for x in outputs["reference"]]), axis=0)
        a0_e = np.mean(np.stack([x[0] for x in outputs["A0"]]), axis=0)
        a0_f = np.mean(np.stack([x[1] for x in outputs["A0"]]), axis=0)
        status["reference_mean_energy"] = ref_e.tolist()
        status["A0_mean_energy"] = a0_e.tolist()
        status["mean_energy_first_mismatch"] = first_mismatch(ref_e, a0_e)
        status["mean_forces_first_mismatch"] = first_mismatch(ref_f, a0_f)
        for row, (energy, forces) in zip(status["A0_runs"], outputs["A0"]):
            row["energy_first_mismatch_vs_reference_mean"] = first_mismatch(ref_e, energy)
            row["forces_first_mismatch_vs_reference_mean"] = first_mismatch(ref_f, forces)
        for row, (energy, forces) in zip(status["reference_runs"], outputs["reference"]):
            row["energy_first_mismatch_vs_reference_mean"] = first_mismatch(ref_e, energy)
            row["forces_first_mismatch_vs_reference_mean"] = first_mismatch(ref_f, forces)
        status["max_abs_energy_diff_mean"] = float(np.max(np.abs(a0_e-ref_e)))
        status["max_abs_force_diff_mean"] = float(np.max(np.abs(a0_f-ref_f)))
        status["force_rms_diff_mean"] = float(np.sqrt(np.mean((a0_f-ref_f)**2)))
        status["output_shape_match"] = ref_e.shape == a0_e.shape and ref_f.shape == a0_f.shape == (64, 3)
        status["exact_graph_input_shared"] = True
        status["all_ten_individual_checks_pass"] = all(
            row["energy_first_mismatch_vs_reference_mean"] is None and row["forces_first_mismatch_vs_reference_mean"] is None
            for row in status["reference_runs"] + status["A0_runs"])
        status["status"] = ("A0_ATOMIC_BASELINE_QUALIFIED" if status["output_shape_match"] and status["all_ten_individual_checks_pass"]
                            and status["mean_energy_first_mismatch"] is None and status["mean_forces_first_mismatch"] is None
                            else "A0_ATOMIC_NUMERIC_MISMATCH")
        status["first_mismatch"] = status["mean_energy_first_mismatch"] or status["mean_forces_first_mismatch"]
    except Exception as exc:
        status["status"] = "A0_ATOMIC_EXECUTION_FAILED"
        status["error_type"] = type(exc).__name__
        status["error"] = str(exc)
        status["traceback_tail"] = traceback.format_exc()[-12000:]
    (RAW / "A0_DATA_QUALIFICATION_STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: status.get(k) for k in ("status", "max_abs_energy_diff_mean", "max_abs_force_diff_mean", "force_rms_diff_mean", "output_shape_match", "all_ten_individual_checks_pass", "first_mismatch", "error_type", "error")}, sort_keys=True, default=str), flush=True)
    if status["status"] != "A0_ATOMIC_BASELINE_QUALIFIED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
