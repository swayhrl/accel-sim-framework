#!/usr/bin/env python3
"""CPU-only official nequip-compile --data-path from the frozen discovery graph."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch


ROOT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
RAW = ROOT / "raw"


class FrozenInput(torch.nn.Module):
    def __init__(self, tensors):
        super().__init__()
        for name, tensor in tensors.items():
            self.register_buffer(name, tensor)

    def forward(self, pos: torch.Tensor) -> torch.Tensor:
        return pos


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--deterministic", action="store_true")
    args = parser.parse_args()
    graph = RAW / ("DISCOVERY_DETERMINISTIC_FULLSORT_GRAPH_READY.npz" if args.deterministic else "DISCOVERY_NATURAL_GRAPH.npz")
    path = ROOT / "compile" / ("DISCOVERY_DETERMINISTIC_FROZEN_INPUT.nequip_data.pt" if args.deterministic else "DISCOVERY_FROZEN_INPUT.nequip_data.pt")
    receipt_path = RAW / ("DETERMINISTIC_AOT_DATA_PATH_RECEIPT.json" if args.deterministic else "AOT_DATA_PATH_RECEIPT.json")
    authority = json.loads((RAW / "DISCOVERY_GRAPH_AUTHORITY.json").read_text())
    graph_sha = hashlib.sha256(graph.read_bytes()).hexdigest()
    if args.deterministic:
        prepared = json.loads((RAW / "DETERMINISTIC_FULLSORT_EAGER_PROBE_STATUS.json").read_text())
        if graph_sha != prepared["prepared_graph_sha256"] or not prepared["edge_shift_multiset_exact"]:
            raise RuntimeError("Deterministic fullsort graph identity changed")
    elif graph_sha != authority["graph_npz_sha256"]:
        raise RuntimeError("Frozen natural graph identity changed")
    with np.load(graph, allow_pickle=False) as z:
        tensors = {key: torch.from_numpy(z[key].copy()) for key in z.files}
    model = torch.jit.script(FrozenInput(tensors))
    model.save(str(path))
    reloaded = torch.jit.load(str(path))
    actual = reloaded.state_dict()
    if set(actual) != set(tensors) or any(not torch.equal(actual[k], v) for k, v in tensors.items()):
        raise RuntimeError("TorchScript data-path state_dict does not preserve frozen graph")
    receipt = {"status": "FROZEN_AOT_DATA_PATH_QUALIFIED", "path": str(path),
               "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
               "source_graph_npz_sha256": graph_sha,
               "deterministic_ready": args.deterministic,
               "input_fields": {k: {"shape": list(v.shape), "dtype": str(v.dtype)} for k, v in tensors.items()},
               "GPU_used": False, "model_or_graph_changed": False}
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": receipt["status"], "sha256": receipt["sha256"], "field_count": len(tensors)}, sort_keys=True))


if __name__ == "__main__":
    main()
