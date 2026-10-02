#!/usr/bin/env python3
"""Bounded AOT repair-1 probe on identical frozen discovery graph."""

import hashlib
import json
import os
import traceback
from pathlib import Path

import numpy as np


ROOT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
RAW = ROOT / "raw"
PACKAGE = ROOT / "compile/A0_ATOMIC_DISCOVERYDATA.nequip.pt2"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def first_bad(a, b):
    bad = ~np.isfinite(a) | ~np.isclose(a, b, atol=5e-5, rtol=5e-5)
    if not np.any(bad):
        return None
    at = tuple(int(x) for x in np.argwhere(bad)[0])
    return {"index": at, "observed": str(a[at]), "reference": float(b[at]),
            "observed_finite": bool(np.isfinite(a[at])),
            "allowed": float(5e-5+5e-5*abs(b[at]))}


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
    with np.load(RAW / "REFERENCE_CANARY_OUTPUTS.npz", allow_pickle=False) as z:
        ref_e, ref_f = z["energy"].copy(), z["forces"].copy()
    result = {"status": "STARTED", "frame_index": 55,
              "graph_sha256": sha(RAW / "DISCOVERY_NATURAL_GRAPH.npz"),
              "model_package_sha256": sha(ROOT / "model/NequIP-OAM-S-0.1.nequip.zip"),
              "aot_compiled_sha256": sha(PACKAGE),
              "compile_data_path_sha256": sha(ROOT / "compile/DISCOVERY_FROZEN_INPUT.nequip_data.pt"),
              "compile_mode": "official_AOTInductor_ase_TF32_OFF_OEQ_atomic"}
    out = None
    try:
        calc = NequIPCalculator.from_compiled_model(str(PACKAGE), device="cuda", chemical_species_to_atom_type_map=True)
        data = AtomicDataDict.to_(dict(graph), device=torch.device("cuda"))
        out = calc.model(data)
        torch.cuda.synchronize()
        e = out[AtomicDataDict.TOTAL_ENERGY_KEY].detach().cpu().numpy().copy()
        f = out[AtomicDataDict.FORCE_KEY].detach().cpu().numpy().copy()
        np.savez_compressed(RAW / "A0_AOT_DATA_PROBE_OUTPUTS.npz", energy=e, forces=f)
        result.update({"energy": e.tolist(), "forces_shape": list(f.shape),
                       "energy_first_bad": first_bad(e, ref_e), "forces_first_bad": first_bad(f, ref_f),
                       "energy_finite": bool(np.isfinite(e).all()), "forces_finite": bool(np.isfinite(f).all()),
                       "output_sha256": sha(RAW / "A0_AOT_DATA_PROBE_OUTPUTS.npz")})
        result["status"] = "A0_AOT_DATA_PROBE_QUALIFIED" if result["energy_first_bad"] is None and result["forces_first_bad"] is None else "A0_AOT_DATA_PROBE_MISMATCH"
    except Exception as exc:
        result.update({"status": "A0_AOT_DATA_PROBE_FAILED", "error_type": type(exc).__name__,
                       "error": str(exc), "traceback_tail": traceback.format_exc()[-10000:]})
        if out is not None and isinstance(out, dict):
            partial = {k: v.detach().cpu().numpy() for k, v in out.items() if isinstance(v, torch.Tensor)}
            if partial:
                np.savez_compressed(RAW / "A0_AOT_DATA_PROBE_PARTIAL.npz", **partial)
                result["partial_sha256"] = sha(RAW / "A0_AOT_DATA_PROBE_PARTIAL.npz")
    (RAW / "A0_AOT_DATA_PROBE_STATUS.json").write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: result.get(k) for k in ("status", "energy", "energy_first_bad", "forces_first_bad", "error_type", "error")}, default=str), flush=True)
    if result["status"] != "A0_AOT_DATA_PROBE_QUALIFIED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
