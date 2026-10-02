#!/usr/bin/env python3
"""Pinned discovery frame graph authority and first real e3nn reference output."""

import hashlib
import json
import os
import traceback
from pathlib import Path

import numpy as np


ROOT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
RAW = ROOT / "raw"
SOURCE = ROOT / "source/nequip-tutorial/sitraj.xyz"
MODEL = ROOT / "model/NequIP-OAM-S-0.1.nequip.zip"
FRAME = 55


def h(blob):
    return hashlib.sha256(blob).hexdigest()


def tensor_receipt(t):
    a = t.detach().cpu().contiguous().numpy()
    return {"dtype": str(a.dtype), "shape": list(a.shape), "sha256": h(a.tobytes())}, a


def main():
    if os.environ.get("R21A_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU lock receipt absent")
    import ase.io
    import torch
    from nequip.data import AtomicDataDict, from_ase
    from nequip.data._nl import DEFAULT_NEIGHBORLIST_BACKEND
    from nequip.integrations.utils import basic_transforms
    from nequip.model import ModelFromPackage

    torch.set_default_dtype(torch.float32)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_float32_matmul_precision("highest")
    frame_authority = json.loads((Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r21a-oeq-graph-readiness-109-v1")
                                   / "docs/vm_tlb/review_packs/AWMA_R21A_OEQ_GRAPH_READINESS_109_V1/INPUT_AUTHORITY.json").read_text())
    selected = next(row for row in frame_authority["selected"] if row["role"] == "DISCOVERY")
    if selected["index"] != FRAME:
        raise RuntimeError("Frozen discovery index differs")
    status = {"frame_index": FRAME, "frame_raw_sha256": selected["raw_frame_sha256"],
              "input_file_sha256": frame_authority["sha256"],
              "model_package_sha256": h(MODEL.read_bytes()),
              "source_nequip_commit": "27d9d2182da918ab7be0017d8300e53278f5e00e",
              "source_oeq_commit": "dc9979099c65113adcc016977c5c60974f9ddafb",
              "TF32": "OFF", "first_mismatch": "NOT_APPLICABLE_REFERENCE_ONLY",
              "energy": "NOT_PRODUCED", "forces": "NOT_PRODUCED", "status": "STARTED"}
    out = None
    try:
        atoms = ase.io.read(str(SOURCE), index=FRAME, format="extxyz")
        if len(atoms) != 64 or set(atoms.get_chemical_symbols()) != {"Si"} or not np.all(atoms.pbc):
            raise RuntimeError("Discovery ASE frame identity invalid")
        package = ModelFromPackage(str(MODEL), compile_mode="eager")
        model = package["sole_model"].eval()
        metadata = dict(model.metadata)
        r_max = float(metadata["r_max"])
        type_names = metadata["type_names"].split()
        if r_max != 4.5 or "Si" not in type_names:
            raise RuntimeError("Actual loaded model cutoff/type identity mismatch")
        transforms = basic_transforms(metadata, r_max, type_names, {x: x for x in type_names},
                                      neighborlist_backend=DEFAULT_NEIGHBORLIST_BACKEND)
        data = from_ase(atoms)
        # DFT labels remain source provenance, never model inputs or implementation reference.
        for key in (AtomicDataDict.TOTAL_ENERGY_KEY, AtomicDataDict.PER_ATOM_ENERGY_KEY,
                    AtomicDataDict.FORCE_KEY, AtomicDataDict.STRESS_KEY):
            data.pop(key, None)
        data.pop("free_energy", None)
        for transform in transforms:
            data = transform(data)
        edge_index = data[AtomicDataDict.EDGE_INDEX_KEY].detach().cpu().numpy()
        shift_key = AtomicDataDict.EDGE_CELL_SHIFT_KEY
        shifts = data[shift_key].detach().cpu().numpy() if shift_key in data else None
        if edge_index.ndim != 2 or edge_index.shape[0] != 2 or edge_index.shape[1] == 0 or shifts is None:
            raise RuntimeError("Natural periodic graph missing directed edge/shift authority")
        if shifts.shape != (edge_index.shape[1], 3):
            raise RuntimeError("Edge/cell-shift alignment shape mismatch")
        if not np.isfinite(shifts).all() or not np.array_equal(shifts, np.rint(shifts)):
            raise RuntimeError("Periodic cell shifts are not finite integer images")
        sorted_receiver = bool(np.all(edge_index[0, 1:] >= edge_index[0, :-1]))
        tuples = [tuple(int(v) for v in (edge_index[0, i], edge_index[1, i], *shifts[i]))
                  for i in range(edge_index.shape[1])]
        multiset = sorted(tuples)
        graph_payload = {}
        graph_fields = {}
        for key, value in data.items():
            if isinstance(value, torch.Tensor):
                graph_fields[key], graph_payload[key.replace("/", "_")] = tensor_receipt(value)
        np.savez_compressed(RAW / "DISCOVERY_NATURAL_GRAPH.npz", **graph_payload)
        graph = {"frame_index": FRAME, "frame_raw_sha256": selected["raw_frame_sha256"],
                 "model_r_max_A": r_max, "type_names_count": len(type_names), "Si_type_index": type_names.index("Si"),
                 "neighborlist_backend": DEFAULT_NEIGHBORLIST_BACKEND,
                 "edge_count": int(edge_index.shape[1]), "directed_edge_shift_multiset_sha256": h(json.dumps(multiset, separators=(",", ":")).encode()),
                 "natural_receiver_major": sorted_receiver,
                 "natural_sender_within_receiver_monotonic": bool(all(edge_index[1, i] <= edge_index[1, i+1]
                       for i in range(edge_index.shape[1]-1) if edge_index[0, i] == edge_index[0, i+1])),
                 "edge_index_orientation": "row0=receiver/dst; row1=sender/src (pinned InteractionBlock source)",
                 "graph_fields": graph_fields,
                 "graph_npz_sha256": h((RAW / "DISCOVERY_NATURAL_GRAPH.npz").read_bytes()),
                 "provided_DFT_labels_used_as_reference": False}
        (RAW / "DISCOVERY_GRAPH_AUTHORITY.json").write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n")
        status["graph_authority_sha256"] = h((RAW / "DISCOVERY_GRAPH_AUTHORITY.json").read_bytes())
        status["graph_npz_sha256"] = graph["graph_npz_sha256"]
        status["edge_count"] = graph["edge_count"]
        status["natural_receiver_major"] = sorted_receiver
        status["model_metadata"] = metadata
        status["model_module_count"] = len(list(model.named_modules()))
        status["interaction_layer_names"] = [n for n, m in model.named_modules() if type(m).__name__ == "InteractionBlock"]
        (RAW / "REFERENCE_CANARY_STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
        for p in model.parameters():
            p.requires_grad_(False)
        model = model.to("cuda")
        data_cuda = AtomicDataDict.to_(dict(data), device=torch.device("cuda"))
        out = model(data_cuda)
        torch.cuda.synchronize()
        energy = out[AtomicDataDict.TOTAL_ENERGY_KEY].detach().cpu().numpy().copy()
        forces = out[AtomicDataDict.FORCE_KEY].detach().cpu().numpy().copy()
        np.savez_compressed(RAW / "REFERENCE_CANARY_OUTPUTS.npz", energy=energy, forces=forces)
        status["energy"] = energy.tolist()
        status["forces_shape"] = list(forces.shape)
        status["forces_sha256"] = h(forces.tobytes())
        status["force_finite"] = bool(np.isfinite(forces).all())
        status["energy_finite"] = bool(np.isfinite(energy).all())
        status["output_payload_sha256"] = h((RAW / "REFERENCE_CANARY_OUTPUTS.npz").read_bytes())
        status["status"] = "REFERENCE_CANARY_QUALIFIED" if status["force_finite"] and status["energy_finite"] else "REFERENCE_CANARY_NONFINITE"
    except Exception as exc:
        status["status"] = "REFERENCE_CANARY_FAILED"
        status["error_type"] = type(exc).__name__
        status["error"] = str(exc)
        status["traceback_tail"] = traceback.format_exc()[-10000:]
        if out is not None:
            status["output_keys"] = list(out.keys()) if isinstance(out, dict) else str(type(out))
            # Preserve every available detached tensor before scientific STOP.
            tensors = {k: v.detach().cpu().numpy() for k, v in out.items() if isinstance(v, torch.Tensor)} if isinstance(out, dict) else {}
            if tensors:
                np.savez_compressed(RAW / "REFERENCE_CANARY_PARTIAL_OUTPUTS.npz", **tensors)
                status["partial_output_payload_sha256"] = h((RAW / "REFERENCE_CANARY_PARTIAL_OUTPUTS.npz").read_bytes())
    (RAW / "REFERENCE_CANARY_STATUS.json").write_text(json.dumps(status, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: status.get(k) for k in ("status", "edge_count", "natural_receiver_major", "interaction_layer_names", "energy", "forces_shape", "error_type", "error")}, sort_keys=True, default=str), flush=True)
    if status["status"] != "REFERENCE_CANARY_QUALIFIED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
