#!/usr/bin/env python3
"""CPU-only effective solver-output variation relative to physical field scales."""

import json
from pathlib import Path

import numpy as np


RAW = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001/raw")
FIELDS = ("qacc", "qfrc_constraint", "efc_force_valid_concat", "efc.Ma")


def stats(reference, candidate):
    a = reference.astype(np.float64).reshape(-1)
    b = candidate.astype(np.float64).reshape(-1)
    delta = np.abs(a - b)
    base_rms = np.sqrt(np.mean(a * a))
    base_max = np.max(np.abs(a))
    denom = max(base_rms, 1e-30)
    return {
        "element_count": len(a),
        "reference_max_abs": float(base_max),
        "reference_rms": float(base_rms),
        "reference_p99_abs": float(np.quantile(np.abs(a), 0.99)),
        "delta_max_abs": float(delta.max()),
        "delta_mean_abs": float(delta.mean()),
        "delta_rms": float(np.sqrt(np.mean(delta * delta))),
        "delta_p99_abs": float(np.quantile(delta, 0.99)),
        "delta_max_over_reference_rms": float(delta.max() / denom),
        "delta_rms_over_reference_rms": float(np.sqrt(np.mean(delta * delta)) / denom),
        "nonzero_delta_elements": int(np.count_nonzero(delta)),
    }


def main():
    g0 = json.loads((RAW / "G0_T128_SOLVER_ENTRY_RECEIPT.json").read_text())
    by_path = {row["field_path"]: row for row in g0["exit_snapshot"]["manifest"]}
    with np.load(g0["exit_snapshot"]["path"], allow_pickle=False) as archive:
        original = {field: archive[by_path[field]["key"]].copy() for field in ("qacc", "qfrc_constraint", "efc.force", "efc.Ma", "nefc")}
    original["efc_force_valid_concat"] = np.concatenate([
        original["efc.force"][world, :int(count)] for world, count in enumerate(original["nefc"])
    ])
    with np.load(RAW / "B0_T128_SOLVER_REPEAT_OUTPUTS.npz", allow_pickle=False) as archive:
        outputs = {key: archive[key] for key in archive.files}
    result = {"fields": {}, "in_situ_vs_isolated_first": {}}
    for field in FIELDS:
        key = field.replace(".", "_")
        baseline = outputs[f"run_0_{key}"]
        result["fields"][field] = {
            "against_first": [
                {"run": run, **stats(baseline, outputs[f"run_{run}_{key}"])} for run in range(1, 6)
            ],
        }
        original_field = original[field] if field != "efc_force_valid_concat" else original["efc_force_valid_concat"]
        result["in_situ_vs_isolated_first"][field] = stats(original_field, baseline)
    (RAW / "B0_LOCAL_NUMERIC_DIAGNOSTIC.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    compact = {
        field: {
            "reference_rms": result["fields"][field]["against_first"][0]["reference_rms"],
            "max_abs_over_six": max(row["delta_max_abs"] for row in result["fields"][field]["against_first"]),
            "max_delta_rms_over_reference_rms": max(row["delta_rms_over_reference_rms"] for row in result["fields"][field]["against_first"]),
            "in_situ_vs_isolated_first_max_abs": result["in_situ_vs_isolated_first"][field]["delta_max_abs"],
        }
        for field in FIELDS
    }
    print(json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    main()
