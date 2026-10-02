#!/usr/bin/env python3
"""Diagnostic-only unmodified e3nn AOT output on the identical frozen graph."""

import hashlib
import json
import os
import traceback
from pathlib import Path

import numpy as np


ROOT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
RAW = ROOT / "raw"
PACKAGE = ROOT / "compile/REFERENCE_E3NN_OAM_S.nequip.pt2"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    if os.environ.get("R21A_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU lock receipt absent")
    import torch
    import openequivariance
    from nequip.data import AtomicDataDict
    from nequip.integrations.ase import NequIPCalculator

    torch.set_default_dtype(torch.float32)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_float32_matmul_precision("highest")
    with np.load(RAW / "DISCOVERY_NATURAL_GRAPH.npz", allow_pickle=False) as z:
        graph = {k: torch.from_numpy(z[k].copy()) for k in z.files}
    with np.load(RAW / "REFERENCE_RUN_0.npz", allow_pickle=False) as z:
        ref_e, ref_f = z["energy"].copy(), z["forces"].copy()
    result = {"frame_index": 55, "graph_sha256": sha(RAW / "DISCOVERY_NATURAL_GRAPH.npz"),
              "model_package_sha256": sha(ROOT / "model/NequIP-OAM-S-0.1.nequip.zip"),
              "compiled_e3nn_sha256": sha(PACKAGE), "status": "STARTED", "energy": "NOT_PRODUCED", "forces": "NOT_PRODUCED"}
    out = None
    try:
        calc = NequIPCalculator.from_compiled_model(str(PACKAGE), device="cuda", chemical_species_to_atom_type_map=True)
        data = AtomicDataDict.to_(dict(graph), device=torch.device("cuda"))
        out = calc.model(data)
        torch.cuda.synchronize()
        energy = out[AtomicDataDict.TOTAL_ENERGY_KEY].detach().cpu().numpy().copy()
        forces = out[AtomicDataDict.FORCE_KEY].detach().cpu().numpy().copy()
        np.savez_compressed(RAW / "REFERENCE_AOT_PROBE_OUTPUTS.npz", energy=energy, forces=forces)
        result.update({"energy": energy.tolist(), "forces_shape": list(forces.shape),
                       "energy_finite": bool(np.isfinite(energy).all()), "forces_finite": bool(np.isfinite(forces).all()),
                       "max_abs_energy_diff_from_eager": float(np.max(np.abs(energy-ref_e))),
                       "max_abs_force_diff_from_eager": float(np.max(np.abs(forces-ref_f))),
                       "allclose_eager_atol_rtol_5e-5": bool(np.allclose(energy, ref_e, atol=5e-5, rtol=5e-5)
                                                         and np.allclose(forces, ref_f, atol=5e-5, rtol=5e-5)),
                       "output_sha256": sha(RAW / "REFERENCE_AOT_PROBE_OUTPUTS.npz")})
        result["status"] = "REFERENCE_AOT_QUALIFIED" if result["energy_finite"] and result["forces_finite"] and result["allclose_eager_atol_rtol_5e-5"] else "REFERENCE_AOT_NUMERIC_MISMATCH"
    except Exception as exc:
        result.update({"status": "REFERENCE_AOT_FAILED", "error_type": type(exc).__name__,
                       "error": str(exc), "traceback_tail": traceback.format_exc()[-8000:]})
    (RAW / "REFERENCE_AOT_PROBE_STATUS.json").write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: result.get(k) for k in ("status", "energy", "energy_finite", "forces_finite", "allclose_eager_atol_rtol_5e-5", "error_type", "error")}, default=str), flush=True)


if __name__ == "__main__":
    main()
