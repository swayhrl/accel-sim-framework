#!/usr/bin/env python3
"""CPU-only preregistered-source-scale local B0 numeric and negative controls."""

import json
from pathlib import Path

import numpy as np


RAW = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001/raw")
EPS32 = float(np.finfo(np.float32).eps)
SPARSE_NNZ_CAP = 4445
MAX_WORLD_NORM = (SPARSE_NNZ_CAP * EPS32) / (1.0 - SPARSE_NNZ_CAP * EPS32)
RMS_NORM = 100.0 * EPS32
RELATION_WORLD_NORM = 100.0 * EPS32


def world_normed(reference, candidate, nefc=None):
    reference = reference.astype(np.float64)
    candidate = candidate.astype(np.float64)
    if nefc is None:
        scale = np.maximum(np.sqrt(np.mean(reference * reference, axis=1)), 1.0)
        max_delta = np.max(np.abs(candidate - reference), axis=1)
        delta_rms_over_global_rms = float(np.sqrt(np.mean((candidate - reference) ** 2)) / max(np.sqrt(np.mean(reference * reference)), 1.0))
        return {"max_world_normalized": float(np.max(max_delta / scale)), "rms_global_normalized": delta_rms_over_global_rms}
    normalized = []
    used_ref = []
    used_delta = []
    for world, count in enumerate(nefc):
        count = int(count)
        if count == 0:
            continue
        a = reference[world, :count]
        b = candidate[world, :count]
        scale = max(float(np.sqrt(np.mean(a * a))), 1.0)
        normalized.append(float(np.max(np.abs(a - b))) / scale)
        used_ref.append(a)
        used_delta.append(b - a)
    a = np.concatenate(used_ref)
    delta = np.concatenate(used_delta)
    return {
        "max_world_normalized": float(max(normalized)),
        "rms_global_normalized": float(np.sqrt(np.mean(delta * delta)) / max(np.sqrt(np.mean(a * a)), 1.0)),
    }


def main():
    g0 = json.loads((RAW / "G0_T128_SOLVER_ENTRY_RECEIPT.json").read_text())
    entry_rows = {row["field_path"]: row for row in g0["entry_snapshot"]["manifest"]}
    with np.load(g0["entry_snapshot"]["path"], allow_pickle=False) as archive:
        entry_qacc = archive[entry_rows["qacc"]["key"]].copy()
    exit_rows = {row["field_path"]: row for row in g0["exit_snapshot"]["manifest"]}
    with np.load(g0["exit_snapshot"]["path"], allow_pickle=False) as archive:
        in_situ = {field: archive[exit_rows[field]["key"]].copy()
                   for field in ("qacc", "qfrc_constraint", "efc.Ma", "efc.force", "nefc", "solver_niter", "overflow")}
    with np.load(RAW / "B0_T128_SOLVER_REPEAT_OUTPUTS.npz", allow_pickle=False) as archive:
        outputs = {key: archive[key] for key in archive.files}
    nefc = outputs["run_0_nefc"]
    fields = ("qacc", "qfrc_constraint", "efc_Ma", "efc_force")
    observed = {}
    in_situ_observed = {}
    baseline_all_pass = True
    for field in fields:
        baseline = outputs[f"run_0_{field}"]
        rows = []
        for run in range(1, 6):
            measured = world_normed(baseline, outputs[f"run_{run}_{field}"], nefc if field == "efc_force" else None)
            measured["run"] = run
            measured["max_world_pass"] = measured["max_world_normalized"] <= MAX_WORLD_NORM
            measured["rms_global_pass"] = measured["rms_global_normalized"] <= RMS_NORM
            baseline_all_pass = baseline_all_pass and measured["max_world_pass"] and measured["rms_global_pass"]
            rows.append(measured)
        observed[field] = rows
        source_field = {"efc_force": "efc.force", "efc_Ma": "efc.Ma"}.get(field, field)
        in_situ_row = world_normed(baseline, in_situ[source_field], nefc if field == "efc_force" else None)
        in_situ_row["max_world_pass"] = in_situ_row["max_world_normalized"] <= MAX_WORLD_NORM
        in_situ_row["rms_global_pass"] = in_situ_row["rms_global_normalized"] <= RMS_NORM
        baseline_all_pass = baseline_all_pass and in_situ_row["max_world_pass"] and in_situ_row["rms_global_pass"]
        in_situ_observed[field] = in_situ_row
    in_situ_discrete_exact = all(np.array_equal(outputs[f"run_0_{field}"], in_situ[field])
                                 for field in ("nefc", "solver_niter", "overflow"))
    baseline_all_pass = baseline_all_pass and in_situ_discrete_exact

    with np.load(RAW / "SOLVER_CONTEXT_RESIDUAL_ARRAYS.npz", allow_pickle=False) as archive:
        ctx = {name: archive[name] for name in archive.files}
    meaninertia = float(json.loads((RAW / "SOLVER_CONTEXT_RESIDUAL_AUDIT.json").read_text())["results"][0]["meaninertia"])
    nv = 35
    tol = 1e-6
    gradient = np.sqrt(np.maximum(ctx["grad_dot"].astype(np.float64), 0)) / (meaninertia * nv)
    model_improvement = 0.5 * ctx["newton_decrement"].astype(np.float64) / (meaninertia * nv)
    grad_ceiling_per_world = np.max(gradient, axis=0) + tol
    model_improvement_ceiling_per_world = np.max(model_improvement, axis=0) + tol
    relation = []
    for repeat in range(3):
        predicted = (ctx["efc_Ma"][repeat].astype(np.float64) - ctx["qfrc_smooth"][repeat].astype(np.float64)
                     - ctx["grad_scale"][repeat, :, None].astype(np.float64) * ctx["grad"][repeat, :, :nv].astype(np.float64))
        reference = ctx["qfrc_constraint"][repeat].astype(np.float64)
        scale = np.maximum(np.sqrt(np.mean(reference * reference, axis=1)), 1.0)
        relative = np.max(np.abs(predicted - reference), axis=1) / scale
        relation.append({"repeat": repeat, "max_world_normalized": float(relative.max()),
                         "pass": bool(np.all(relative <= RELATION_WORLD_NORM))})
    relation_pass = all(row["pass"] for row in relation)
    baseline_all_pass = baseline_all_pass and relation_pass

    ref_qacc = outputs["run_0_qacc"]
    ref_qfrc = outputs["run_0_qfrc_constraint"]
    ref_force = outputs["run_0_efc_force"]
    negative = {}
    stale = world_normed(ref_qacc, entry_qacc)
    negative["stale_entry_qacc_rejected"] = stale["max_world_normalized"] > MAX_WORLD_NORM or stale["rms_global_normalized"] > RMS_NORM
    zero_qacc = world_normed(ref_qacc, np.zeros_like(ref_qacc))
    negative["missing_qacc_worlds_rejected"] = zero_qacc["max_world_normalized"] > MAX_WORLD_NORM
    zero_qfrc = world_normed(ref_qfrc, np.zeros_like(ref_qfrc))
    negative["missing_qfrc_worlds_rejected"] = zero_qfrc["max_world_normalized"] > MAX_WORLD_NORM
    zero_force = world_normed(ref_force, np.zeros_like(ref_force), nefc)
    negative["dropped_valid_constraint_forces_rejected"] = zero_force["max_world_normalized"] > MAX_WORLD_NORM
    negative["early_stop_one_world_rejected_by_exact_niter"] = not np.array_equal(outputs["run_0_solver_niter"], np.where(np.arange(1024) == 0, outputs["run_0_solver_niter"] - 1, outputs["run_0_solver_niter"]))
    negative["missing_one_constraint_rejected_by_exact_nefc"] = not np.array_equal(nefc, np.where(np.arange(1024) == int(np.argmax(nefc)), nefc - 1, nefc))
    negative_all = all(negative.values())
    result = {
        "stage": "AWMA_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_V1",
        "classification": "B0_ONLY_CONTRACT_QUALIFICATION_AND_OFFLINE_NEGATIVE_CONTROLS_BEFORE_CANDIDATE",
        "source": "solver.py::_solve_done and _qfrc_constraint_from_grad; solver_test.py source tests are looser cross-implementation checks, not copied tolerance",
        "solver_entry_sha256": g0["entry_snapshot"]["sha256"],
        "float32_eps": EPS32,
        "sparse_nnz_capacity": SPARSE_NNZ_CAP,
        "max_world_norm_bound_gamma_eps_nnz": MAX_WORLD_NORM,
        "rms_global_norm_bound_100eps": RMS_NORM,
        "qfrc_source_relation_norm_bound_100eps": RELATION_WORLD_NORM,
        "source_solver_tolerance": tol,
        "baseline_effective_output_results": observed,
        "in_situ_vs_isolated_first_effective_output_results": in_situ_observed,
        "in_situ_vs_isolated_discrete_signatures_exact": in_situ_discrete_exact,
        "baseline_gradient_max_per_world_plus_tolerance": grad_ceiling_per_world.tolist(),
        "baseline_model_improvement_max_per_world_plus_tolerance": model_improvement_ceiling_per_world.tolist(),
        "qfrc_source_relation_results": relation,
        "baseline_all_pass": baseline_all_pass,
        "negative_controls": negative,
        "negative_controls_all_rejected": negative_all,
        "negative_control_scales": {"stale_qacc": stale, "zero_qacc": zero_qacc, "zero_qfrc": zero_qfrc, "zero_valid_efc_force": zero_force},
    }
    (RAW / "LOCAL_CONTRACT_B0_VALIDATOR.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"baseline_all_pass": baseline_all_pass, "negative_controls_all_rejected": negative_all,
                      "max_world_norm_bound": MAX_WORLD_NORM, "rms_norm_bound": RMS_NORM,
                      "qfrc_relation": relation}, sort_keys=True))
    if not baseline_all_pass or not negative_all:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
