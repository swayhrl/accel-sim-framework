#!/usr/bin/env python3
"""CPU-only pinpoint of frozen B0 full-Data restore divergence."""

import json
from pathlib import Path

import numpy as np


RAW = Path("/data/c16/awma/r20_active_world_native_v1/raw")


def main():
    with np.load(RAW / "BASELINE_DISCOVERY_REPEATS.npz", allow_pickle=False) as archive:
        arrays = {key: archive[key] for key in archive.files}
    fields = sorted(arrays)
    result = {"shape": {key: list(arrays[key].shape) for key in fields}, "per_step": []}
    for offset in range(arrays["niter"].shape[1]):
        row = {"absolute_step": 128 + offset}
        for key in fields:
            baseline = arrays[key][0, offset]
            peers = arrays[key][1:, offset]
            different = peers != baseline
            row[key + "_any_different"] = bool(np.any(different))
            row[key + "_different_worlds_max"] = int(max(
                np.count_nonzero(np.any(delta, axis=tuple(range(1, delta.ndim))))
                if delta.ndim > 1 else np.count_nonzero(delta)
                for delta in different
            ))
            if key in ("qpos", "qvel", "qacc_warmstart", "ctrl"):
                row[key + "_max_abs"] = float(np.max(np.abs(peers.astype(np.float64) - baseline.astype(np.float64))))
        result["per_step"].append(row)
    result["first_divergence_by_field"] = {
        key: next((row["absolute_step"] for row in result["per_step"] if row[key + "_any_different"]), None)
        for key in fields
    }
    (RAW / "BASELINE_DIVERGENCE_ANALYSIS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"first_divergence_by_field": result["first_divergence_by_field"], "first_3_steps": result["per_step"][:3]}, sort_keys=True))


if __name__ == "__main__":
    main()
