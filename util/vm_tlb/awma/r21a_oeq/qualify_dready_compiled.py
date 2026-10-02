#!/usr/bin/env python3
"""Five Dready full-model AOT energy+force correctness evaluations."""

import hashlib
import json
import os
import traceback
from pathlib import Path

import numpy as np


ROOT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
RAW = ROOT / "raw"
MODEL = ROOT / "model/NequIP-OAM-S-0.1.nequip.zip"
COMPILED = ROOT / "compile/DREADY_OAM_S.nequip.pt2"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def first_bad(ref, obs):
    bad = ~np.isfinite(obs) | ~np.isclose(ref, obs, atol=5e-5, rtol=5e-5)
    if not np.any(bad):
        return None
    at = tuple(int(x) for x in np.argwhere(bad)[0])
    return {"index": at, "reference": float(ref[at]), "observed": str(obs[at]),
            "allowed_atol_plus_rtol_abs_ref": float(5e-5+5e-5*abs(ref[at]))}


def main():
    if os.environ.get("R21A_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU lock receipt absent")
    import torch
    import openequivariance
    from nequip.data import AtomicDataDict
    from nequip.model.inference_models import load_compiled_model

    torch.set_default_dtype(torch.float32)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_float32_matmul_precision("highest")
    if not json.loads((RAW / "A0_DATA_QUALIFICATION_STATUS.json").read_text())["status"] == "A0_ATOMIC_BASELINE_QUALIFIED":
        raise RuntimeError("Compiled A0 strong baseline not qualified")
    prep = json.loads((RAW / "DETERMINISTIC_FULLSORT_EAGER_PROBE_STATUS.json").read_text())
    with np.load(RAW / "DISCOVERY_DETERMINISTIC_FULLSORT_GRAPH_READY.npz", allow_pickle=False) as z:
        prepared = {k: torch.from_numpy(z[k].copy()) for k in z.files}
    if sha(RAW / "DISCOVERY_DETERMINISTIC_FULLSORT_GRAPH_READY.npz") != prep["prepared_graph_sha256"]:
        raise RuntimeError("Prepared graph hash changed")
    reference = []
    for i in range(5):
        with np.load(RAW / f"REFERENCE_DATA_RUN_{i}.npz", allow_pickle=False) as z:
            reference.append((z["energy"].copy(), z["forces"].copy()))
    ref_e = np.mean(np.stack([x[0] for x in reference]), axis=0)
    ref_f = np.mean(np.stack([x[1] for x in reference]), axis=0)
    status = {"status": "STARTED", "frame_index": 55, "frame_raw_sha256": prep["frame_raw_sha256"],
              "natural_graph_multiset_sha256": prep["directed_edge_shift_multiset_sha256"],
              "prepared_graph_sha256": prep["prepared_graph_sha256"],
              "sender_perm_sha256": prep["sender_perm_sha256"],
              "model_package_sha256": sha(MODEL), "compiled_dready_sha256": sha(COMPILED),
              "compiled_A0_sha256": sha(ROOT / "compile/A0_ATOMIC_DISCOVERYDATA.nequip.pt2"),
              "compile_mode": "same_NequIP_AOTInductor_ase_cuda_TF32_OFF_exact_discovery_data_path_method",
              "receiver_sort_performed_once_outside_timing": True,
              "runs": [], "first_mismatch": "NOT_YET_COMPARED", "atol": 5e-5, "rtol": 5e-5}
    (RAW / "DREADY_CORRECTNESS_STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    out = None
    try:
        compiled, metadata = load_compiled_model(str(COMPILED), device="cuda")
        status["compiled_input_keys"] = compiled.input_keys
        status["compiled_output_keys"] = compiled.output_keys
        if AtomicDataDict.EDGE_TRANSPOSE_PERM_KEY not in compiled.input_keys:
            raise RuntimeError("Deterministic AOT artifact lacks permutation input")
        data = AtomicDataDict.to_(dict(prepared), device=torch.device("cuda"))
        for i in range(5):
            out = None
            try:
                out = compiled(dict(data))
                torch.cuda.synchronize()
                e = out[AtomicDataDict.TOTAL_ENERGY_KEY].detach().cpu().numpy().copy()
                f = out[AtomicDataDict.FORCE_KEY].detach().cpu().numpy().copy()
                path = RAW / f"DREADY_RUN_{i}.npz"
                np.savez_compressed(path, energy=e, forces=f)
                row = {"repeat": i, "energy": e.tolist(), "forces_shape": list(f.shape),
                       "energy_finite": bool(np.isfinite(e).all()), "forces_finite": bool(np.isfinite(f).all()),
                       "energy_first_mismatch": first_bad(ref_e, e), "forces_first_mismatch": first_bad(ref_f, f),
                       "output_sha256": sha(path)}
                status["runs"].append(row)
                (RAW / "DREADY_CORRECTNESS_STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True, default=str) + "\n")
                if not row["energy_finite"] or not row["forces_finite"]:
                    raise RuntimeError(f"Dready nonfinite repeat {i}")
            except Exception:
                if out is not None and isinstance(out, dict):
                    partial = {k: v.detach().cpu().numpy() for k, v in out.items() if isinstance(v, torch.Tensor)}
                    if partial:
                        path = RAW / f"DREADY_RUN_{i}_PARTIAL.npz"
                        np.savez_compressed(path, **partial)
                        status["partial_sha256"] = sha(path)
                raise
        status["all_five_pass"] = len(status["runs"]) == 5 and all(
            r["energy_finite"] and r["forces_finite"] and r["energy_first_mismatch"] is None and r["forces_first_mismatch"] is None
            and r["forces_shape"] == [64, 3] for r in status["runs"])
        status["first_mismatch"] = next((r["energy_first_mismatch"] or r["forces_first_mismatch"] for r in status["runs"]
                                         if r["energy_first_mismatch"] or r["forces_first_mismatch"]), None)
        status["status"] = "DREADY_NUMERICS_QUALIFIED" if status["all_five_pass"] else "DREADY_NUMERIC_MISMATCH"
    except Exception as exc:
        status.update({"status": "DREADY_EXECUTION_FAILED", "error_type": type(exc).__name__,
                       "error": str(exc), "traceback_tail": traceback.format_exc()[-12000:]})
    (RAW / "DREADY_CORRECTNESS_STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: status.get(k) for k in ("status", "all_five_pass", "first_mismatch", "compiled_input_keys", "error_type", "error")}, default=str), flush=True)
    if status["status"] != "DREADY_NUMERICS_QUALIFIED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
