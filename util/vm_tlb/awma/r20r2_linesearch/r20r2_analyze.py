#!/usr/bin/env python3
"""CPU-only, chronological-first flag-pair analysis of the bounded observer run."""

import json
from pathlib import Path

import numpy as np


RAW = Path("/data/c16/awma/r20r2_linesearch_semantic_materiality_20261001/raw")
WORLD = 413
ENTRY_NAMES = ("outer", "nefc", "search_dot", "snorm", "tolerance", "ls_tolerance", "gtol",
               "gtol_accept", "noise_floor", "p0_cost", "p0_derivative", "p0_curvature",
               "lo_alpha_in", "lo_in_cost", "lo_in_derivative", "lo_in_curvature",
               "initial_converged", "search_unchanged")
INNER_NAMES = ("lo_alpha_before", "hi_alpha_before", "lo_next_alpha", "hi_next_alpha", "mid_alpha",
               "lo_next_cost", "lo_next_derivative", "lo_next_curvature",
               "hi_next_cost", "hi_next_derivative", "hi_next_curvature",
               "mid_cost", "mid_derivative", "mid_curvature", "conv_lo", "conv_hi", "conv_mid",
               "swap_lo", "swap_hi", "done_no_swap", "done_lo_signed_gtol", "done_hi_signed_gtol",
               "converged_candidate", "ls_done", "selected_alpha", "improvement",
               "lo_cost_after", "lo_derivative_after", "hi_cost_after", "hi_derivative_after", "break")
EXIT_NAMES = ("ls_converged", "alpha", "improvement", "LS_ITERATIONS_written", "ls_exhausted")


def scalar(value):
    x = float(value)
    return x if np.isfinite(x) else repr(x)


def fields(row, names):
    return {name: scalar(row[index]) for index, name in enumerate(names)}


def decode(trace):
    result = []
    for outer in range(trace.shape[0]):
        if not np.any(trace[outer, 21, :]):
            continue
        inner = []
        for iteration in range(20):
            row = trace[outer, iteration + 1, :]
            if not np.any(row):
                break
            inner.append({"inner_iteration": iteration, **fields(row, INNER_NAMES)})
        result.append({"outer_iteration": outer, "entry": fields(trace[outer, 0, :], ENTRY_NAMES),
                       "inner": inner, "exit": fields(trace[outer, 21, :], EXIT_NAMES)})
    return result


def normed_world(reference, candidate, n=None):
    left = np.asarray(reference, dtype=np.float64)
    right = np.asarray(candidate, dtype=np.float64)
    if n is not None:
        left = left[:n]
        right = right[:n]
    scale = max(float(np.sqrt(np.mean(left * left))), 1.0)
    return {"max_abs": float(np.max(np.abs(right - left))),
            "max_world_normalized": float(np.max(np.abs(right - left)) / scale),
            "rms_world_normalized": float(np.sqrt(np.mean((right - left) ** 2)) / scale),
            "reference_sha256_not_recorded_here": "See full raw NPZ hash index"}


def main():
    receipts = sorted(RAW.glob("ON_[0-9][0-9]_RECEIPT.json"))
    rows = [json.loads(path.read_text()) for path in receipts]
    clear_row = next(row for row in rows if not row["world413_LS_ITERATIONS"])
    set_row = next(row for row in rows if row["world413_LS_ITERATIONS"])
    chosen = (clear_row, set_row)
    traces = {}
    arrays = {}
    for row in chosen:
        label = "SET" if row["world413_LS_ITERATIONS"] else "CLEAR"
        with np.load(row["raw_path"], allow_pickle=False) as z:
            traces[label] = decode(z["trace"])
            arrays[label] = {name: z[name].copy() for name in z.files if name != "trace"}
    (RAW / "CHRONOLOGICAL_FIRST_FLAG_PAIR_TRACES.json").write_text(
        json.dumps({"choice_rule": "first observed CLEAR and first observed SET in bounded same-graph run",
                    "clear_repeat": clear_row["repeat"], "set_repeat": set_row["repeat"],
                    "CLEAR": traces["CLEAR"], "SET": traces["SET"]}, indent=2, sort_keys=True) + "\n")
    exit_rows = []
    for outer in range(10):
        left = next((x for x in traces["CLEAR"] if x["outer_iteration"] == outer), None)
        right = next((x for x in traces["SET"] if x["outer_iteration"] == outer), None)
        if left is None and right is None:
            continue
        exit_rows.append({"outer_iteration": outer,
                          "clear_inner_count": len(left["inner"]) if left else None,
                          "set_inner_count": len(right["inner"]) if right else None,
                          "clear_exit": left["exit"] if left else None,
                          "set_exit": right["exit"] if right else None})
    coverage = {}
    for name in ("nefc", "solver_niter"):
        a = arrays["CLEAR"][f"output_{name}"]
        b = arrays["SET"][f"output_{name}"]
        coverage[name] = {"global_exact": bool(np.array_equal(a, b)), "world413_clear": int(a[WORLD]),
                          "world413_set": int(b[WORLD])}
    output_diffs = {}
    n = coverage["nefc"]["world413_clear"]
    for name in ("qacc", "qfrc_constraint", "efc_Ma", "efc_force"):
        a = arrays["CLEAR"][f"output_{name}"][WORLD]
        b = arrays["SET"][f"output_{name}"][WORLD]
        output_diffs[name] = normed_world(a, b, n if name == "efc_force" else None)
    aggregate = {"CLEAR": [], "SET": []}
    for row in rows:
        with np.load(row["raw_path"], allow_pickle=False) as z:
            t = z["trace"]
            label = "SET" if row["world413_LS_ITERATIONS"] else "CLEAR"
            aggregate[label].append({"repeat": row["repeat"], "outer2_gtol_accept": scalar(t[2, 0, 7]),
                                     "outer2_hi_next_derivative_inner1": scalar(t[2, 2, 9]),
                                     "outer2_conv_hi_inner1": scalar(t[2, 2, 15]),
                                     "outer2_swap_lo_inner1": scalar(t[2, 2, 17]),
                                     "outer2_alpha": scalar(t[2, 21, 1]),
                                     "outer2_improvement": scalar(t[2, 21, 2])})
    clear_inner = traces["CLEAR"][2]["inner"][1]
    set_inner = traces["SET"][2]["inner"][1]
    decisive = {"outer_iteration": 2, "inner_iteration": 1,
                "predicate": "abs(hi_next.derivative) < gtol_accept && hi_next.cost < 0",
                "clear_gtol_accept": traces["CLEAR"][2]["entry"]["gtol_accept"],
                "set_gtol_accept": traces["SET"][2]["entry"]["gtol_accept"],
                "clear_hi_next_derivative": clear_inner["hi_next_derivative"],
                "set_hi_next_derivative": set_inner["hi_next_derivative"],
                "clear_hi_next_cost": clear_inner["hi_next_cost"],
                "set_hi_next_cost": set_inner["hi_next_cost"],
                "clear_conv_hi": clear_inner["conv_hi"], "set_conv_hi": set_inner["conv_hi"],
                "clear_swap_lo": clear_inner["swap_lo"], "set_swap_lo": set_inner["swap_lo"],
                "clear_ls_done": clear_inner["ls_done"], "set_ls_done": set_inner["ls_done"]}
    aggregate_ranges = {}
    for label, records in aggregate.items():
        aggregate_ranges[label] = {name: [min(r[name] for r in records), max(r[name] for r in records)]
                                   for name in ("outer2_alpha", "outer2_improvement", "outer2_gtol_accept",
                                                "outer2_hi_next_derivative_inner1")}
    summary = {"clear_repeat": clear_row["repeat"], "set_repeat": set_row["repeat"],
               "all_ON_runs_qualified": all(row["qualified"] for row in rows),
               "ON_count": len(rows), "clear_count": sum(not row["world413_LS_ITERATIONS"] for row in rows),
               "set_count": sum(row["world413_LS_ITERATIONS"] for row in rows),
               "exit_by_outer": exit_rows, "coverage": coverage,
               "decisive_predicate": decisive, "all_run_outer2_aggregate": aggregate,
               "outer2_ranges_by_flag": aggregate_ranges,
               "world413_output_differences": output_diffs,
               "reference_contract_gamma": 0.0005301662193351918,
               "reference_contract_rms": 1.1920928955078125e-5}
    (RAW / "CHRONOLOGICAL_FIRST_FLAG_PAIR_ANALYSIS.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
