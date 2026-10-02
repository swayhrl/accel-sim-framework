#!/usr/bin/env python3
"""Create the R25 implementation freeze after both points qualify."""

import argparse
import hashlib
import json
from pathlib import Path


STAGE = "AWMA_R25_TIED_WEIGHT_BROADER_SOFTWARE_VALIDATION_109_V1"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--runner", required=True)
    p.add_argument("--base", required=True)
    p.add_argument("--cce-root", required=True)
    args = p.parse_args()
    root = Path(args.root)
    d0q = load(root / "raw/D0/QUALIFICATION_STATUS.json")
    h0q = load(root / "raw/H0/QUALIFICATION_STATUS.json")
    if not d0q["qualified"] or not h0q["qualified"]:
        raise SystemExit("two-point qualification is not closed")
    if h0q["h0_performance_inspected"] is not False:
        raise SystemExit("H0 holdout discipline is not attested")
    d0 = load(root / "raw/D0/RUNTIME_POINT_AUTHORITY.json")
    h0 = load(root / "raw/H0/RUNTIME_POINT_AUTHORITY.json")
    files = [
        Path(args.runner),
        Path(args.base),
        Path(args.cce_root) / "cut_cross_entropy/cce_backward.py",
        Path(args.cce_root) / "cut_cross_entropy/tl_utils.py",
        Path(args.cce_root) / "cut_cross_entropy/tl_autotune.py",
    ]
    frozen = {
        "stage": STAGE,
        "status": "IMPLEMENTATION_FROZEN_AFTER_TWO_POINT_QUALIFICATION",
        "D0_qualified": True,
        "H0_qualified": True,
        "H0_performance_inspected_before_freeze": False,
        "files": [{"path": str(f), "sha256": sha(f)} for f in files],
        "arms": ["B0_DENSE_STRONG", "C1_COMPACT_FULL", "S2_TILED"],
        "candidate_behavior_after_freeze_mutable": False,
        "compact_accumulator": "sorted unique IDs remapped to compact domain; aten.embedding_dense_backward; no VxH lookup grad",
        "optimizer": {
            "name": "explicit AdamW reference",
            "lr": 0.001,
            "betas": [0.9, 0.999],
            "eps": 1e-8,
            "weight_decay": 0.01,
            "W_dtype": "torch.bfloat16",
            "m_v_dtype": "torch.float32",
            "same_tilewise_consumer_all_arms_points": True,
        },
        "tile_policy": "largest positive BLOCK_V multiple under 32MiB FP32 gradient budget",
        "points": {
            "D0": {
                "weight_shape": d0["weight_shape"],
                "token_count": d0["token_count"],
                "fixed_cce_meta": d0["fixed_cce_meta"],
                "rows_per_tile": d0["rows_per_tile"],
                "tile_count": d0["tile_count"],
                "tile_fp32_budget_bytes": d0["tile_fp32_budget_bytes"],
            },
            "H0": {
                "weight_shape": h0["weight_shape"],
                "token_count": h0["token_count"],
                "fixed_cce_meta": h0["fixed_cce_meta"],
                "rows_per_tile": h0["rows_per_tile"],
                "tile_count": h0["tile_count"],
                "tile_fp32_budget_bytes": h0["tile_fp32_budget_bytes"],
            },
        },
        "formal_protocol": {
            "groups": 3,
            "warmups_per_arm_group": 2,
            "formal_samples_per_arm_group": 5,
            "orders": [
                ["B0_DENSE_STRONG", "C1_COMPACT_FULL", "S2_TILED"],
                ["C1_COMPACT_FULL", "S2_TILED", "B0_DENSE_STRONG"],
                ["S2_TILED", "B0_DENSE_STRONG", "C1_COMPACT_FULL"],
            ],
        },
    }
    out = root / "raw/IMPLEMENTATION_FREEZE.json"
    dump(out, frozen)
    print(out)
    print(sha(out))


if __name__ == "__main__":
    main()
