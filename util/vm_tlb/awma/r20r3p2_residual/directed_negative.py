#!/usr/bin/env python3
"""CPU-only directed negatives against the source-semantic B0 contract."""

import json
import sys
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve()
AWMA = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(AWMA / "r20r1_solver_entry"))
from r20r3p2_b0 import summarize_stop
from local_contract_validator import MAX_WORLD_NORM, RMS_NORM, world_normed


ROOT = Path("/data/c16/awma/r20r3p2_residual_contract_resume_20261001")
RAW = ROOT / "raw"
R1 = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001/raw")
lineage = json.loads((R1 / "R2_DISCOVERY_ENTRY_LINEAGE.json").read_text())
entry = next(x["entry_snapshot"] for x in lineage["entrances"] if x["step"] == 128)
with np.load(entry["path"], allow_pickle=False) as z:
    by_path = {r["field_path"]: z[r["key"]].copy() for r in entry["manifest"]}
entry_overflow = by_path["overflow"]
with np.load(RAW / "B0_T128_R00_OUTPUT_AND_STOP.npz", allow_pickle=False) as z:
    base = {name: z[name].copy() for name in z.files}


def validate(test):
    stop = summarize_stop(test["stop_mask"], test["stop_values"], test["solver_niter"],
                          entry_overflow, test["overflow"], test["done"], 10)
    discrete = {"niter_exact": bool(np.array_equal(base["solver_niter"], test["solver_niter"])),
                "nefc_exact": bool(np.array_equal(base["nefc"], test["nefc"])),
                "non_LS_overflow_exact": bool(np.array_equal(base["overflow"] & ~1024, test["overflow"] & ~1024))}
    floating = {}
    for field in ("qacc", "qfrc_constraint"):
        metric = world_normed(base[field], test[field])
        floating[field] = metric["max_world_normalized"] <= MAX_WORLD_NORM and metric["rms_global_normalized"] <= RMS_NORM
    return {"accepted": bool(stop["pass"] and all(discrete.values()) and all(floating.values())),
            "stop_pass": stop["pass"], "discrete": discrete, "floating": floating,
            "source_stop_fail_worlds": stop["fail_worlds"]}


def copy():
    return {key: value.copy() for key, value in base.items()}


positive = validate(copy())
if not positive["accepted"]:
    raise RuntimeError("Positive frozen B0 control rejected")
nonlimit = np.flatnonzero(base["solver_niter"] < 10)
if not len(nonlimit):
    raise RuntimeError("No nonlimit world available for directed negatives")
w = int(nonlimit[0])
cases = {}

bad = copy()
bad["stop_mask"][w] = 0
bad["done"][w] = True
cases["false_done_all_four_predicates_false"] = validate(bad)

bad = copy()
bad["solver_niter"][w] -= 1
cases["early_outer_stop_niter_decrement"] = validate(bad)

bad = copy()
bad["nefc"][w] -= 1
cases["missed_constraint_changed_nefc"] = validate(bad)

bad = copy()
bad["qacc"] = by_path["qacc"].copy()
cases["stale_entry_qacc"] = validate(bad)

bad = copy()
bad["qfrc_constraint"] = by_path["qfrc_constraint"].copy()
cases["stale_entry_qfrc"] = validate(bad)

eligible = np.flatnonzero((base["solver_niter"] < 10) & ((entry_overflow & 512) == 0))
if not len(eligible):
    raise RuntimeError("No nonlimit, entry-ITERATIONS-clear world for bit negative")
w_bit = int(eligible[0])
bad = copy()
bad["overflow"][w_bit] |= 512
cases["false_new_ITERATIONS_bit"] = validate(bad)

result = {"stage": "AWMA_R20R3P2_RESIDUAL_CONTRACT_REQUALIFICATION_AND_RESUME_109_V1",
          "positive_B0_accepted": positive["accepted"], "negative_world": w,
          "false_limit_world": w_bit, "cases": cases,
          "all_directed_negatives_rejected": all(not x["accepted"] for x in cases.values()),
          "candidate_executed": False}
(RAW / "DIRECTED_NEGATIVE_VALIDATOR.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps({"positive_B0_accepted": result["positive_B0_accepted"],
                  "all_directed_negatives_rejected": result["all_directed_negatives_rejected"],
                  "case_results": {name: value["accepted"] for name, value in cases.items()}}, sort_keys=True))
if not result["all_directed_negatives_rejected"]:
    raise SystemExit(2)
