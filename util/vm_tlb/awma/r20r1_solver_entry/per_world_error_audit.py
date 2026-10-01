#!/usr/bin/env python3
"""CPU-only per-world normalized B0 variation and negative-control scale audit."""

import json
from pathlib import Path

import numpy as np


RAW = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001/raw")


def world_metric(reference, candidate):
    a = reference.astype(np.float64)
    b = candidate.astype(np.float64)
    scale = np.maximum(np.sqrt(np.mean(a * a, axis=1)), 1.0)
    max_delta = np.max(np.abs(b - a), axis=1)
    normalized = max_delta / scale
    return {
        "worlds": len(scale),
        "max_normalized": float(normalized.max()),
        "p99_normalized": float(np.quantile(normalized, 0.99)),
        "median_normalized": float(np.median(normalized)),
        "max_abs": float(max_delta.max()),
        "worlds_above_1e_minus_4": int(np.count_nonzero(normalized > 1e-4)),
        "worlds_above_5e_minus_4": int(np.count_nonzero(normalized > 5e-4)),
        "reference_world_rms_min_max": [float(scale.min()), float(scale.max())],
    }


def main():
    g0 = json.loads((RAW / "G0_T128_SOLVER_ENTRY_RECEIPT.json").read_text())
    with np.load(RAW / "B0_T128_SOLVER_REPEAT_OUTPUTS.npz", allow_pickle=False) as archive:
        outputs = {key: archive[key] for key in archive.files}
    fields = ("qacc", "qfrc_constraint", "efc_Ma", "efc_force")
    result = {"per_field": {}}
    for field in fields:
        baseline = outputs[f"run_0_{field}"]
        rows = []
        for run in range(1, 6):
            candidate = outputs[f"run_{run}_{field}"]
            if field == "efc_force":
                nefc = outputs["run_0_nefc"]
                normalized = []
                absolute = []
                for world, count in enumerate(nefc):
                    count = int(count)
                    if count == 0:
                        continue
                    a = baseline[world, :count].astype(np.float64)
                    b = candidate[world, :count].astype(np.float64)
                    scale = max(float(np.sqrt(np.mean(a * a))), 1.0)
                    diff = float(np.max(np.abs(b - a)))
                    normalized.append(diff / scale)
                    absolute.append(diff)
                row = {
                    "run": run,
                    "active_worlds": len(normalized),
                    "max_normalized": float(np.max(normalized)),
                    "p99_normalized": float(np.quantile(normalized, 0.99)),
                    "max_abs": float(np.max(absolute)),
                    "worlds_above_1e_minus_4": int(np.count_nonzero(np.asarray(normalized) > 1e-4)),
                    "worlds_above_5e_minus_4": int(np.count_nonzero(np.asarray(normalized) > 5e-4)),
                }
            else:
                row = {"run": run, **world_metric(baseline, candidate)}
            rows.append(row)
        result["per_field"][field] = rows
    (RAW / "B0_PER_WORLD_ERROR_AUDIT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({field: {"max_normalized": max(row["max_normalized"] for row in rows),
                              "worlds_above_5e_minus_4_max": max(row["worlds_above_5e_minus_4"] for row in rows)}
                      for field, rows in result["per_field"].items()}, sort_keys=True))


if __name__ == "__main__":
    main()
