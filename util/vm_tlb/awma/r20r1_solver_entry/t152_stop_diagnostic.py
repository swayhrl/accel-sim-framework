#!/usr/bin/env python3
"""CPU-only exact failed t152 overflow-bit and inherited/new provenance."""

import json
from pathlib import Path

import numpy as np


RAW = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001/raw")
BITS = {
    1 << 0: "NEFC", 1 << 1: "NJMAX_NNZ", 1 << 2: "BROADPHASE", 1 << 3: "NARROWPHASE",
    1 << 4: "CCD", 1 << 5: "HFIELD", 1 << 6: "CONTACT_MATCH", 1 << 7: "NVMAX",
    1 << 8: "EPA_HORIZON", 1 << 9: "ITERATIONS", 1 << 10: "LS_ITERATIONS", 1 << 11: "TACTILE",
}


def bit_names(value):
    return [name for bit, name in BITS.items() if int(value) & bit]


def main():
    lineage = json.loads((RAW / "R2_DISCOVERY_ENTRY_LINEAGE.json").read_text())
    entry = next(row for row in lineage["entrances"] if row["step"] == 152)["entry_snapshot"]
    by_path = {row["field_path"]: row for row in entry["manifest"]}
    with np.load(entry["path"], allow_pickle=False) as archive:
        before = archive[by_path["overflow"]["key"]].copy()
    with np.load(RAW / "T152_B0_REPEAT_OUTPUTS.npz", allow_pickle=False) as archive:
        outputs = {key: archive[key] for key in archive.files}
    reference = outputs["run_0_overflow"]
    rows = []
    for run in range(1, 5):
        observed = outputs[f"run_{run}_overflow"]
        changed = np.flatnonzero(reference != observed)
        details = []
        for world in changed:
            old = int(reference[world])
            new = int(observed[world])
            inherited = int(before[world])
            details.append({
                "world": int(world),
                "entry": inherited,
                "entry_names": bit_names(inherited),
                "reference_exit": old,
                "reference_exit_names": bit_names(old),
                "observed_exit": new,
                "observed_exit_names": bit_names(new),
                "reference_new_bits": old & ~inherited,
                "observed_new_bits": new & ~inherited,
                "xor_bit_names": bit_names(old ^ new),
                "reference_solver_niter": int(outputs["run_0_solver_niter"][world]),
                "observed_solver_niter": int(outputs[f"run_{run}_solver_niter"][world]),
                "reference_nefc": int(outputs["run_0_nefc"][world]),
                "observed_nefc": int(outputs[f"run_{run}_nefc"][world]),
                "qacc_world_max_abs": float(np.max(np.abs(outputs["run_0_qacc"][world].astype(np.float64) - outputs[f"run_{run}_qacc"][world].astype(np.float64)))),
            })
        rows.append({"run": run, "changed_worlds": len(changed), "details": details})
    result = {
        "stage": "AWMA_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_V1",
        "classification": "FROZEN_T152_B0_STOP_SIGNATURE_FAILURE_NOT_CAPACITY_REPAIR_OR_THRESHOLD_CASE",
        "entry_sha256": entry["sha256"],
        "entry_overflow_or": int(np.bitwise_or.reduce(before.reshape(-1))),
        "reference_exit_overflow_or": int(np.bitwise_or.reduce(reference.reshape(-1))),
        "comparisons": rows,
    }
    (RAW / "T152_STOP_SIGNATURE_DIAGNOSTIC.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
