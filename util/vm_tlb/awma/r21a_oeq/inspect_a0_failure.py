#!/usr/bin/env python3
"""CPU-only first compiled-A0 nonfinite/mismatch persistence audit."""

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
RAW = ROOT / "raw"
with np.load(RAW / "A0_RUN_0.npz", allow_pickle=False) as z:
    energy = z["energy"].copy()
    forces = z["forces"].copy()
with np.load(RAW / "REFERENCE_RUN_0.npz", allow_pickle=False) as z:
    ref_e = z["energy"].copy()
    ref_f = z["forces"].copy()


def first_bad(a, b):
    bad = ~np.isfinite(a) | ~np.isclose(a, b, atol=5e-5, rtol=5e-5)
    if not np.any(bad):
        return None
    idx = tuple(int(x) for x in np.argwhere(bad)[0])
    return {"index": idx, "compiled_value": float(a[idx]), "reference_value": float(b[idx]),
            "compiled_finite": bool(np.isfinite(a[idx])),
            "absolute_difference": float(abs(a[idx]-b[idx])),
            "allowed_atol_plus_rtol_abs_ref": float(5e-5+5e-5*abs(b[idx]))}


result = {"status": "FIRST_COMPILED_A0_OUTPUT_PRESERVED",
          "frame_index": 55,
          "graph_authority_sha256": hashlib.sha256((RAW / "DISCOVERY_GRAPH_AUTHORITY.json").read_bytes()).hexdigest(),
          "compiled_A0_payload_sha256": hashlib.sha256((RAW / "A0_RUN_0.npz").read_bytes()).hexdigest(),
          "reference_payload_sha256": hashlib.sha256((RAW / "REFERENCE_RUN_0.npz").read_bytes()).hexdigest(),
          "energy_first_bad": first_bad(energy, ref_e),
          "force_first_bad": first_bad(forces, ref_f),
          "nonfinite_energy_count": int(np.count_nonzero(~np.isfinite(energy))),
          "nonfinite_force_count": int(np.count_nonzero(~np.isfinite(forces))),
          "force_shape": list(forces.shape)}
(RAW / "A0_COMPILED_FIRST_FAILURE_AUDIT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, indent=2, sort_keys=True))
