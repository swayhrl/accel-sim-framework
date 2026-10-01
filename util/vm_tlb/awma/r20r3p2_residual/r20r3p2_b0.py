#!/usr/bin/env python3
"""Fixed 8x4 B0-only source-stop qualification; no S1 is imported or run."""

import json
import os
import sys
from pathlib import Path

import mujoco
import numpy as np
import warp as wp


ROOT = Path("/data/c16/awma/r20r3p2_residual_contract_resume_20261001")
RAW = ROOT / "raw"
R1 = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001")
HERE = Path(__file__).resolve()
AWMA = HERE.parents[1]
sys.path.insert(0, str(AWMA / "r20r3p1_profiler"))
sys.path.insert(0, str(AWMA / "r20r1_solver_entry"))
sys.path.insert(0, str(AWMA / "r20_active_world"))
from r20r3p1_scientific_profile import EXPECTED_SHA, SCENE, STEPS, check_output, reference
from b0_repeatability_t128 import output_view
from snapshot_io import enumerate_data_arrays, file_sha, restore_recorded_snapshot, sha_numpy
from state_utils import make_gpu_snapshot, restore_gpu_snapshot


@wp.kernel
def source_stop_predicates(
    nv: int,
    tolerance_in: wp.array[float],
    meaninertia_in: wp.array[float],
    alpha_in: wp.array[float],
    improvement_in: wp.array[float],
    grad_dot_in: wp.array[float],
    newton_decrement_in: wp.array[float],
    masks_out: wp.array[int],
    values_out: wp.array2d[float],
):
    w = wp.tid()
    tolerance = tolerance_in[w % tolerance_in.shape[0]]
    meaninertia = meaninertia_in[w % meaninertia_in.shape[0]]
    denom = meaninertia * float(nv)
    alpha = alpha_in[w]
    improvement = improvement_in[w] / denom
    gradient = wp.sqrt(grad_dot_in[w]) / denom
    model_improvement = (0.5 * newton_decrement_in[w]) / denom
    mask = int(0)
    if alpha == 0.0:
        mask |= 1
    if improvement > 0.0 and improvement < tolerance:
        mask |= 2
    if gradient < tolerance:
        mask |= 4
    if model_improvement < tolerance:
        mask |= 8
    masks_out[w] = mask
    values_out[w, 0] = alpha
    values_out[w, 1] = improvement
    values_out[w, 2] = gradient
    values_out[w, 3] = model_improvement
    values_out[w, 4] = tolerance
    values_out[w, 5] = grad_dot_in[w]


def summarize_stop(mask, values, niter, entry_overflow, exit_overflow, done, iterations):
    old_iter = (entry_overflow & 512) != 0
    new_iter = ((exit_overflow & ~entry_overflow) & 512) != 0
    exit_iter = (exit_overflow & 512) != 0
    nonlimit = niter < iterations
    limit = niter == iterations
    finite = np.isfinite(values).all(axis=1)
    valid = done & finite & (values[:, 5] >= 0.0) & (niter >= 1) & (niter <= iterations)
    valid &= np.where(nonlimit, (mask != 0) & ~new_iter,
                      np.where(limit, np.where(mask == 0, exit_iter, ~new_iter), False))
    valid &= ~new_iter | (limit & (mask == 0))
    fail_worlds = np.flatnonzero(~valid).astype(int).tolist()
    reasons = {"alpha_zero": int(np.count_nonzero(mask & 1)),
               "positive_improvement_below_tol": int(np.count_nonzero(mask & 2)),
               "gradient_below_tol": int(np.count_nonzero(mask & 4)),
               "model_improvement_below_tol": int(np.count_nonzero(mask & 8)),
               "any_source_predicate": int(np.count_nonzero(mask)),
               "multiple_predicates": int(sum(int(m).bit_count() > 1 for m in mask))}
    return {"pass": not fail_worlds, "fail_worlds": fail_worlds,
            "predicate_counts": reasons,
            "niter_histogram": {str(int(k)): int(v) for k, v in zip(*np.unique(niter, return_counts=True))},
            "new_ITERATIONS_worlds": np.flatnonzero(new_iter).astype(int).tolist(),
            "inherited_ITERATIONS_worlds": np.flatnonzero(old_iter).astype(int).tolist(),
            "exit_ITERATIONS_worlds": np.flatnonzero(exit_iter).astype(int).tolist(),
            "limit_stop_nonpredicate_count": int(np.count_nonzero(limit & (mask == 0))),
            "predicate_done_on_final_iteration_count": int(np.count_nonzero(limit & (mask != 0))),
            "LS_ITERATIONS_exit_worlds": np.flatnonzero((exit_overflow & 1024) != 0).astype(int).tolist(),
            "nonfinite_predicate_worlds": np.flatnonzero(~finite).astype(int).tolist()}


def main():
    if os.environ.get("R20R3P2_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU campaign lock receipt absent")
    overlay = ROOT / "source_overlay"
    if Path(os.environ.get("PYTHONPATH", "").split(os.pathsep)[0]).resolve() != overlay:
        raise RuntimeError("Candidate-capable source overlay not selected")
    for step in STEPS:
        if file_sha(R1 / f"raw/R2_T{step}_SOLVER_ENTRY_FULL_DATA.npz") != EXPECTED_SHA[step]:
            raise RuntimeError(f"Frozen input t{step} SHA mismatch")
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    import mujoco_warp as mjw
    from mujoco_warp._src import solver
    from mujoco_warp._src.io import load_trajectory, override_model
    if Path(solver.__file__).resolve() != overlay / "mujoco_warp/_src/solver.py":
        raise RuntimeError("Unexpected solver source path")
    if file_sha(Path(solver.__file__)) != "868cf9b0420d61656b3698ba7ddc93b6aa3d6a031d825c939a9868adf916a8e3":
        raise RuntimeError("Parent candidate source SHA mismatch")
    solver._R20R3P1_ACTIVE = False
    lineage = json.loads((R1 / "raw/R2_DISCOVERY_ENTRY_LINEAGE.json").read_text())
    entries = {row["step"]: row["entry_snapshot"] for row in lineage["entrances"]}
    mjm = mujoco.MjSpec.from_file(str(SCENE / "scene_hfield.xml")).compile()
    mjd = mujoco.MjData(mjm)
    if len(load_trajectory(str(SCENE / "shuffle_dance.npz"), mjm, mjd)) != 1000:
        raise RuntimeError("Frozen control identity changed")
    device = wp.get_device("cuda:0")
    results = []
    with wp.ScopedDevice(device):
        model = mjw.put_model(mjm)
        override_model(model, ["opt.warn_overflow=~ITERATIONS|~LS_ITERATIONS"])
        if not (model.opt.graph_conditional and model.is_sparse and int(model.opt.iterations) == 10
                and int(model.opt.ls_iterations) == 20):
            raise RuntimeError("Frozen solver options changed")
        expected_model = {x["path"]: x["sha256"] for x in json.loads((R1 / "raw/G0_MODEL_ARRAY_MANIFEST.json").read_text())}
        actual_model = enumerate_data_arrays(model)
        if set(actual_model) != set(expected_model) or any(sha_numpy(v.numpy()) != expected_model[k] for k, v in actual_model.items()):
            raise RuntimeError("Frozen Model array identity changed")
        data = mjw.put_data(mjm, mjd, nworld=1024, nconmax=48, njmax=192)
        original_factory = solver._create_solver_context
        contexts = []

        def witness(m, d):
            ctx = original_factory(m, d)
            contexts.append(ctx)
            return ctx

        solver._create_solver_context = witness
        try:
            with wp.ScopedCapture() as graph:
                solver.solve(model, data)
        finally:
            solver._create_solver_context = original_factory
        if len(contexts) != 1:
            raise RuntimeError("Expected exactly one B0 captured SolverContext")
        ctx = contexts[0]
        masks = wp.empty(1024, dtype=int, device=device)
        values = wp.empty((1024, 6), dtype=float, device=device)
        for step in STEPS:
            entry = entries[step]
            if entry["sha256"] != EXPECTED_SHA[step]:
                raise RuntimeError(f"Lineage SHA mismatch t{step}")
            restore_recorded_snapshot(data, entry)
            frozen = make_gpu_snapshot(data)
            for repeat in range(8):
                restore_gpu_snapshot(data, frozen)
                current = enumerate_data_arrays(data)
                for row in entry["manifest"]:
                    if sha_numpy(current[row["field_path"]].numpy()) != row["sha256"]:
                        raise RuntimeError(f"Frozen Data changed t{step} repeat{repeat}: {row['field_path']}")
                wp.capture_launch(graph.graph)
                wp.synchronize()
                out = output_view(data)
                original_status, _, _ = check_output(step, reference(step), out, data, ctx, model,
                                                     frozen["overflow"].numpy())
                wp.launch(source_stop_predicates, dim=1024,
                          inputs=[model.nv, model.opt.tolerance, model.stat.meaninertia, ctx.alpha,
                                  ctx.improvement, ctx.grad_dot, ctx.newton_decrement],
                          outputs=[masks, values])
                wp.synchronize()
                mask_host = masks.numpy().copy()
                values_host = values.numpy().copy()
                done_host = ctx.done.numpy().copy()
                stop = summarize_stop(mask_host, values_host, out["solver_niter"],
                                      frozen["overflow"].numpy(), out["overflow"], done_host,
                                      int(model.opt.iterations))
                receipt = {"step": step, "repeat": repeat, "entry_sha256": EXPECTED_SHA[step],
                           "source_sha256": file_sha(Path(solver.__file__)),
                           "input_138_fields_exact": True, "model_266_fields_exact": True,
                           "original_hard_gates": original_status, "source_stop": stop,
                           "qualified": bool(original_status["qualified"] and stop["pass"])}
                payload = RAW / f"B0_T{step}_R{repeat:02d}_OUTPUT_AND_STOP.npz"
                np.savez_compressed(payload, **{key.replace('.', '_'): value for key, value in out.items()},
                                    stop_mask=mask_host, stop_values=values_host, done=done_host)
                receipt["payload_sha256"] = file_sha(payload)
                (RAW / f"B0_T{step}_R{repeat:02d}_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
                results.append({"step": step, "repeat": repeat, "qualified": receipt["qualified"],
                                "source_stop_pass": stop["pass"], "fail_world_count": len(stop["fail_worlds"]),
                                "new_ITERATIONS_count": len(stop["new_ITERATIONS_worlds"]),
                                "LS_ITERATIONS_count": len(stop["LS_ITERATIONS_exit_worlds"])})
                print(json.dumps(results[-1], sort_keys=True), flush=True)
                if not receipt["qualified"]:
                    break
            if len(results) != (STEPS.index(step)+1)*8 or not all(x["qualified"] for x in results):
                break
        summary = {"stage": "AWMA_R20R3P2_RESIDUAL_CONTRACT_REQUALIFICATION_AND_RESUME_109_V1",
                   "predeclared_repeats_per_step": 8, "completed_replays": len(results),
                   "all_32_qualified": len(results) == 32 and all(x["qualified"] for x in results),
                   "candidate_executed": False, "results": results}
        (RAW / "B0_ONLY_QUALIFICATION_SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"completed_replays": len(results), "all_32_qualified": summary["all_32_qualified"]}, sort_keys=True), flush=True)
        if not summary["all_32_qualified"]:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
