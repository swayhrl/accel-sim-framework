#!/usr/bin/env python3
"""One non-timed deterministic OEQ graph/permutation and output canary."""

import argparse
import hashlib
import json
import os
import traceback
from pathlib import Path

import numpy as np

from deterministic_patch import enable_deterministic_oeq_for_packaged_oam_s


ROOT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
RAW = ROOT / "raw"
MODEL = ROOT / "model/NequIP-OAM-S-0.1.nequip.zip"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def first_bad(ref, observed):
    bad = ~np.isfinite(observed) | ~np.isclose(ref, observed, atol=5e-5, rtol=5e-5)
    if not np.any(bad):
        return None
    at = tuple(int(x) for x in np.argwhere(bad)[0])
    return {"index": at, "reference": float(ref[at]), "observed": str(observed[at]),
            "allowed": float(5e-5+5e-5*abs(ref[at]))}


def main():
    if os.environ.get("R21A_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU lock receipt absent")
    import torch
    import openequivariance
    from nequip.data import AtomicDataDict
    from nequip.model import ModelFromPackage, modify

    torch.set_default_dtype(torch.float32)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_float32_matmul_precision("highest")
    parser = argparse.ArgumentParser()
    parser.add_argument("--fullsort", action="store_true")
    args = parser.parse_args()
    suffix = "FULLSORT_" if args.fullsort else ""
    graph = json.loads((RAW / "DISCOVERY_GRAPH_AUTHORITY.json").read_text())
    if not graph["natural_receiver_major"]:
        raise RuntimeError("Natural graph receiver-major authority changed")
    with np.load(RAW / "DISCOVERY_NATURAL_GRAPH.npz", allow_pickle=False) as z:
        natural_cpu = {k: torch.from_numpy(z[k].copy()) for k in z.files}
    with np.load(RAW / "REFERENCE_DATA_RUN_0.npz", allow_pickle=False) as z:
        ref_e, ref_f = z["energy"].copy(), z["forces"].copy()
    status = {"status": "STARTED", "arm": f"DETERMINISTIC_{suffix}EAGER_ENGINEERING_PROBE",
              "frame_index": 55, "frame_raw_sha256": graph["frame_raw_sha256"],
              "graph_npz_sha256": graph["graph_npz_sha256"],
              "directed_edge_shift_multiset_sha256": graph["directed_edge_shift_multiset_sha256"],
              "model_package_sha256": sha(MODEL),
              "deterministic_patch_sha256": sha(Path(__file__).with_name("deterministic_patch.py")),
              "receiver_sort_executed": bool(args.fullsort), "energy": "NOT_PRODUCED", "forces": "NOT_PRODUCED"}
    out = None
    try:
        data = AtomicDataDict.to_(dict(natural_cpu), device=torch.device("cuda"))
        edge = data[AtomicDataDict.EDGE_INDEX_KEY]
        if not torch.all(edge[0, 1:] >= edge[0, :-1]).item():
            raise RuntimeError("Natural graph not receiver-major after GPU transfer")
        nnode, nedge = int(data[AtomicDataDict.POSITIONS_KEY].shape[0]), int(edge.shape[1])
        if args.fullsort:
            if graph["natural_sender_within_receiver_monotonic"]:
                raise RuntimeError("Full row-major sort not source-required on already lexicographic graph")
            receiver_perm = torch.argsort(edge[0] * nnode + edge[1])
            data[AtomicDataDict.EDGE_INDEX_KEY] = edge[:, receiver_perm]
            data[AtomicDataDict.EDGE_CELL_SHIFT_KEY] = data[AtomicDataDict.EDGE_CELL_SHIFT_KEY][receiver_perm]
            edge = data[AtomicDataDict.EDGE_INDEX_KEY]
            status["receiver_reorder_permutation_sha256"] = hashlib.sha256(receiver_perm.detach().cpu().numpy().tobytes()).hexdigest()
        perm = torch.argsort(edge[1] * nnode + edge[0])
        if not torch.equal(torch.sort(perm).values, torch.arange(nedge, device=perm.device)):
            raise RuntimeError("Sender transpose permutation not bijective")
        if not torch.all((edge[1] * nnode + edge[0])[perm][1:] >= (edge[1] * nnode + edge[0])[perm][:-1]).item():
            raise RuntimeError("Sender transpose order not monotonic")
        data[AtomicDataDict.EDGE_TRANSPOSE_PERM_KEY] = perm
        torch.cuda.synchronize()
        perm_cpu = perm.detach().cpu().numpy().copy()
        prepared_path = RAW / f"DISCOVERY_DETERMINISTIC_{suffix}GRAPH_READY.npz"
        np.savez_compressed(prepared_path,
                            **{k: v.detach().cpu().numpy() for k, v in data.items() if isinstance(v, torch.Tensor)})
        status.update({"edge_count": nedge, "node_count": nnode,
                       "sender_perm_sha256": hashlib.sha256(perm_cpu.tobytes()).hexdigest(),
                       "prepared_graph_sha256": sha(prepared_path),
                       "same_natural_edge_index_sha256": hashlib.sha256(edge.detach().cpu().numpy().tobytes()).hexdigest()
                              == graph["graph_fields"][AtomicDataDict.EDGE_INDEX_KEY]["sha256"],
                       "same_natural_edge_shift_sha256": hashlib.sha256(data[AtomicDataDict.EDGE_CELL_SHIFT_KEY].detach().cpu().numpy().tobytes()).hexdigest()
                              == graph["graph_fields"][AtomicDataDict.EDGE_CELL_SHIFT_KEY]["sha256"]})
        if args.fullsort:
            natural_edge = natural_cpu[AtomicDataDict.EDGE_INDEX_KEY].numpy()
            natural_shift = natural_cpu[AtomicDataDict.EDGE_CELL_SHIFT_KEY].numpy()
            prepared_edge = edge.detach().cpu().numpy()
            prepared_shift = data[AtomicDataDict.EDGE_CELL_SHIFT_KEY].detach().cpu().numpy()
            original_tuples = sorted(tuple(int(v) for v in (natural_edge[0, i], natural_edge[1, i], *natural_shift[i])) for i in range(nedge))
            prepared_tuples = sorted(tuple(int(v) for v in (prepared_edge[0, i], prepared_edge[1, i], *prepared_shift[i])) for i in range(nedge))
            status["edge_shift_multiset_exact"] = original_tuples == prepared_tuples
            if not status["edge_shift_multiset_exact"]:
                raise RuntimeError("Fullsort changed directed edge/periodic-image multiset")
        elif not status["same_natural_edge_index_sha256"] or not status["same_natural_edge_shift_sha256"]:
            raise RuntimeError("Deterministic prep altered natural graph topology/periodic shifts")
        status_path = RAW / f"DETERMINISTIC_{suffix}EAGER_PROBE_STATUS.json"
        status_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
        package = ModelFromPackage(str(MODEL), compile_mode="eager")
        modified = modify(package, modifiers=[{"modifier": "enable_OpenEquivariance"}])
        model = modified["sole_model"].eval()
        status["patch_modules"] = enable_deterministic_oeq_for_packaged_oam_s(model)
        for p in model.parameters():
            p.requires_grad_(False)
        model = model.to("cuda")
        out = model(data)
        torch.cuda.synchronize()
        e = out[AtomicDataDict.TOTAL_ENERGY_KEY].detach().cpu().numpy().copy()
        f = out[AtomicDataDict.FORCE_KEY].detach().cpu().numpy().copy()
        output_path = RAW / f"DETERMINISTIC_{suffix}EAGER_PROBE_OUTPUTS.npz"
        np.savez_compressed(output_path, energy=e, forces=f)
        status.update({"energy": e.tolist(), "forces_shape": list(f.shape),
                       "energy_first_bad": first_bad(ref_e, e), "forces_first_bad": first_bad(ref_f, f),
                       "energy_finite": bool(np.isfinite(e).all()), "forces_finite": bool(np.isfinite(f).all()),
                       "output_sha256": sha(output_path)})
        status["status"] = "DETERMINISTIC_EAGER_PROBE_QUALIFIED" if status["energy_first_bad"] is None and status["forces_first_bad"] is None else "DETERMINISTIC_EAGER_PROBE_MISMATCH"
    except Exception as exc:
        status.update({"status": "DETERMINISTIC_EAGER_PROBE_FAILED", "error_type": type(exc).__name__,
                       "error": str(exc), "traceback_tail": traceback.format_exc()[-12000:]})
        if out is not None and isinstance(out, dict):
            partial = {k: v.detach().cpu().numpy() for k, v in out.items() if isinstance(v, torch.Tensor)}
            if partial:
                partial_path = RAW / f"DETERMINISTIC_{suffix}EAGER_PROBE_PARTIAL.npz"
                np.savez_compressed(partial_path, **partial)
                status["partial_sha256"] = sha(partial_path)
    (RAW / f"DETERMINISTIC_{suffix}EAGER_PROBE_STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: status.get(k) for k in ("status", "receiver_sort_executed", "edge_count", "patch_modules", "energy", "energy_first_bad", "forces_first_bad", "error_type", "error")}, default=str), flush=True)
    if status["status"] != "DETERMINISTIC_EAGER_PROBE_QUALIFIED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
