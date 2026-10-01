#!/usr/bin/env python3
"""CPU-only exact residual-envelope diagnostic; never modifies the frozen gate."""

import json
from pathlib import Path

import numpy as np


RAW = Path("/data/c16/awma/r20r3p1_profiler_repair_resume_20261001/raw")
R1 = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001/raw")
step = 128
with np.load(R1 / f"T{step}_B0_RESIDUAL_ARRAYS.npz", allow_pickle=False) as p:
    parent = np.max(p["gradient"].astype(np.float64), axis=0)
with np.load(RAW / f"BASELINE_T{step}_OUTPUTS.npz", allow_pickle=False) as p:
    off = p["gradient"].astype(np.float64)
with np.load(RAW / f"CORRECTNESS_T{step}_B0.npz", allow_pickle=False) as p:
    b0 = p["gradient"].astype(np.float64)
    b0_niter = p["solver_niter"].copy()
    b0_nefc = p["nefc"].copy()
with np.load(RAW / f"CORRECTNESS_T{step}_S1.npz", allow_pickle=False) as p:
    s1 = p["gradient"].astype(np.float64)
    s1_niter = p["solver_niter"].copy()
    s1_nefc = p["nefc"].copy()
ceiling = np.maximum(parent, off) + 1e-6
violating = np.flatnonzero(s1 > ceiling)
rows = []
for w in violating:
    rows.append({"world": int(w), "parent_B0_max": float(parent[w]), "patched_OFF_B0": float(off[w]),
                 "frozen_ceiling": float(ceiling[w]), "current_B0": float(b0[w]), "S1": float(s1[w]),
                 "S1_minus_ceiling": float(s1[w]-ceiling[w]), "S1_minus_current_B0": float(s1[w]-b0[w]),
                 "nefc_B0_S1": [int(b0_nefc[w]), int(s1_nefc[w])],
                 "outer_niter_B0_S1": [int(b0_niter[w]), int(s1_niter[w])],
                 "current_B0_itself_above_ceiling": bool(b0[w] > ceiling[w])})
result = {"step": step, "frozen_rule": "max(parent 5 B0 residuals, patched OFF B0 residual) + unchanged source tolerance 1e-6",
          "violating_world_count": len(rows), "violations": rows,
          "max_S1_minus_ceiling": float(np.max(s1-ceiling)),
          "max_abs_S1_minus_current_B0": float(np.max(np.abs(s1-b0))),
          "B0_violating_count": int(np.count_nonzero(b0>ceiling)),
          "candidate_gate_pass": len(rows) == 0}
(RAW / "CANDIDATE_T128_RESIDUAL_FAILURE_AUDIT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, indent=2, sort_keys=True))
