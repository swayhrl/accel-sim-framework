#!/usr/bin/env python3
"""One official OEQ atomic eager engineering canary; persists first output/failure."""

import hashlib
import json
import os
import traceback
from pathlib import Path

import numpy as np


ROOT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
RAW = ROOT / "raw"
MODEL = ROOT / "model/NequIP-OAM-S-0.1.nequip.zip"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mismatch(reference, observed):
    mask = ~np.isclose(reference, observed, atol=5e-5, rtol=5e-5)
    if not np.any(mask):
        return None
    loc = tuple(int(x) for x in np.argwhere(mask)[0])
    return {"index": loc, "reference": float(reference[loc]), "observed": float(observed[loc]),
            "abs_diff": float(abs(observed[loc]-reference[loc])),
            "allowed_atol_plus_rtol_abs_ref": float(5e-5+5e-5*abs(reference[loc]))}


def main():
    if os.environ.get("R21A_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU lock receipt absent")
    import torch
    import openequivariance
    from nequip.data import AtomicDataDict
    from nequip.model import ModelFromPackage, modify
    from nequip.model.modify_utils import get_all_modifiers

    torch.set_default_dtype(torch.float32)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_float32_matmul_precision("highest")
    authority = json.loads((RAW / "DISCOVERY_GRAPH_AUTHORITY.json").read_text())
    with np.load(RAW / "DISCOVERY_NATURAL_GRAPH.npz", allow_pickle=False) as z:
        data_cpu = {key: torch.from_numpy(z[key].copy()) for key in z.files}
    if "free_energy" in data_cpu or "forces" in data_cpu or "total_energy" in data_cpu:
        raise RuntimeError("DFT label leaked into scientific graph input")
    with np.load(RAW / "REFERENCE_CANARY_OUTPUTS.npz", allow_pickle=False) as z:
        ref_e, ref_f = z["energy"].copy(), z["forces"].copy()
    status = {"stage": "AWMA_R21A_OEQ_GRAPH_READINESS_109_V1",
              "arm": "A0_OFFICIAL_OEQ_ATOMIC_ENGINEERING_PROBE",
              "compile_mode": "eager_probe_not_performance_baseline",
              "frame_index": 55, "graph_authority_sha256": sha(RAW / "DISCOVERY_GRAPH_AUTHORITY.json"),
              "model_package_sha256": sha(MODEL), "nequip_commit": "27d9d2182da918ab7be0017d8300e53278f5e00e",
              "oeq_commit": "dc9979099c65113adcc016977c5c60974f9ddafb",
              "TF32": "OFF", "energy": "NOT_PRODUCED", "forces": "NOT_PRODUCED", "status": "STARTED"}
    out = None
    try:
        package = ModelFromPackage(str(MODEL), compile_mode="eager")
        package.eval()
        status["available_package_modifiers"] = sorted(get_all_modifiers(package["sole_model"]).keys())
        modified = modify(package, modifiers=[{"modifier": "enable_OpenEquivariance"}])
        model = modified["sole_model"].eval()
        oeq_modules = [(name, module) for name, module in model.named_modules() if "OpenEquivariance" in type(module).__name__]
        status["oeq_module_names"] = [name for name, _ in oeq_modules]
        status["oeq_module_count"] = len(oeq_modules)
        status["oeq_deterministic_flags"] = [bool(module.tp_conv.input_args["deterministic"]) for _, module in oeq_modules]
        if len(oeq_modules) != 2 or any(status["oeq_deterministic_flags"]):
            raise RuntimeError("Official atomic modifier did not replace both OAM-S interaction TP modules")
        for p in model.parameters():
            p.requires_grad_(False)
        model = model.to("cuda")
        data_cuda = AtomicDataDict.to_(dict(data_cpu), device=torch.device("cuda"))
        out = model(data_cuda)
        torch.cuda.synchronize()
        energy = out[AtomicDataDict.TOTAL_ENERGY_KEY].detach().cpu().numpy().copy()
        forces = out[AtomicDataDict.FORCE_KEY].detach().cpu().numpy().copy()
        np.savez_compressed(RAW / "A0_ENGINEERING_PROBE_OUTPUTS.npz", energy=energy, forces=forces)
        status.update({"energy": energy.tolist(), "forces_shape": list(forces.shape),
                       "forces_sha256": hashlib.sha256(forces.tobytes()).hexdigest(),
                       "output_payload_sha256": sha(RAW / "A0_ENGINEERING_PROBE_OUTPUTS.npz"),
                       "energy_finite": bool(np.isfinite(energy).all()), "forces_finite": bool(np.isfinite(forces).all()),
                       "energy_first_mismatch": mismatch(ref_e, energy),
                       "forces_first_mismatch": mismatch(ref_f, forces)})
        status["status"] = ("ATOMIC_EAGER_PROBE_QUALIFIED" if status["energy_finite"] and status["forces_finite"]
                            and status["energy_first_mismatch"] is None and status["forces_first_mismatch"] is None
                            else "ATOMIC_EAGER_PROBE_NUMERIC_MISMATCH")
    except Exception as exc:
        status["status"] = "ATOMIC_EAGER_PROBE_FAILED"
        status["error_type"] = type(exc).__name__
        status["error"] = str(exc)
        status["traceback_tail"] = traceback.format_exc()[-12000:]
        if out is not None and isinstance(out, dict):
            tensors = {k: v.detach().cpu().numpy() for k, v in out.items() if isinstance(v, torch.Tensor)}
            if tensors:
                np.savez_compressed(RAW / "A0_ENGINEERING_PROBE_PARTIAL_OUTPUTS.npz", **tensors)
                status["partial_output_payload_sha256"] = sha(RAW / "A0_ENGINEERING_PROBE_PARTIAL_OUTPUTS.npz")
    (RAW / "A0_ENGINEERING_PROBE_STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: status.get(k) for k in ("status", "oeq_module_count", "oeq_deterministic_flags", "energy", "energy_first_mismatch", "forces_first_mismatch", "error_type", "error")}, default=str), flush=True)
    if status["status"] != "ATOMIC_EAGER_PROBE_QUALIFIED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
