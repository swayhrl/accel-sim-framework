#!/usr/bin/env python3
"""Reuse exact P1 304-worker S1 with independently qualified source-stop gates."""

import argparse
import json
import os
import sys
from pathlib import Path

import mujoco
import numpy as np
import warp as wp


ROOT = Path("/data/c16/awma/r20r3p2_residual_contract_resume_20261001")
RAW = ROOT / "raw"
PARENT = Path("/data/c16/awma/r20_active_world_native_v1")
R1 = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001")
HERE = Path(__file__).resolve()
AWMA = HERE.parents[1]
sys.path.insert(0, str(AWMA / "r20r3p1_profiler"))
sys.path.insert(0, str(HERE.parent))
from r20r3p1_scientific_profile import (EXPECTED_SHA, SCENE, STEPS, check_output,
                                        reference)
from r20r3p2_b0 import source_stop_predicates, summarize_stop
from snapshot_io import enumerate_data_arrays, file_sha, restore_recorded_snapshot, sha_numpy
from state_utils import make_gpu_snapshot, restore_gpu_snapshot
from b0_repeatability_t128 import output_view
from local_contract_validator import MAX_WORLD_NORM, RMS_NORM, RELATION_WORLD_NORM, world_normed


def compare_pair(step, b0, s1, b0_ctx, s1_ctx, b0_grad, s1_grad, b0_impr, s1_impr):
    float_fields = ("qacc", "qfrc_constraint", "efc.Ma", "efc.force")
    floating = {}
    for field in float_fields:
        x = world_normed(b0[field], s1[field], b0["nefc"] if field == "efc.force" else None)
        x["pass"] = x["max_world_normalized"] <= MAX_WORLD_NORM and x["rms_global_normalized"] <= RMS_NORM
        floating[field] = x
    ls_bit = 1 << 10
    ls_a = (b0["overflow"] & ls_bit) != 0
    ls_b = (s1["overflow"] & ls_bit) != 0
    changed_worlds = np.flatnonzero(ls_a != ls_b)
    alpha0 = b0_ctx.alpha.numpy().copy()
    alpha1 = s1_ctx.alpha.numpy().copy()
    improvement0 = b0_ctx.improvement.numpy().copy()
    improvement1 = s1_ctx.improvement.numpy().copy()
    changed = [{"world": int(w), "B0_flag": bool(ls_a[w]), "S1_flag": bool(ls_b[w]),
                "B0_final_alpha": float(alpha0[w]), "S1_final_alpha": float(alpha1[w]),
                "B0_final_improvement": float(improvement0[w]), "S1_final_improvement": float(improvement1[w])}
               for w in changed_worlds]
    discrete = {
        "nefc_exact": bool(np.array_equal(b0["nefc"], s1["nefc"])),
        "outer_niter_exact": bool(np.array_equal(b0["solver_niter"], s1["solver_niter"])),
        "non_LS_overflow_exact": bool(np.array_equal(b0["overflow"] & ~ls_bit, s1["overflow"] & ~ls_bit)),
    }
    residual = {"B0_gradient_max_diagnostic": float(np.max(b0_grad)),
                "S1_gradient_max_diagnostic": float(np.max(s1_grad)),
                "B0_model_improvement_max_diagnostic": float(np.max(b0_impr)),
                "S1_model_improvement_max_diagnostic": float(np.max(s1_impr))}
    finite_ctx = bool(all(np.isfinite(x).all() for x in (alpha0, alpha1, improvement0, improvement1, s1_grad, s1_impr)))
    return {"step": step, "discrete": discrete, "floating": floating, "residual": residual,
            "finite_ctx_alpha_improvement": finite_ctx,
            "LS_ITERATIONS_changed_worlds": changed,
            "pass": (all(discrete.values()) and all(x["pass"] for x in floating.values()) and finite_ctx)}


def list_canaries(solver, device):
    nworld = 1024
    ids = wp.empty(nworld, dtype=int, device=device)
    count = wp.empty(1, dtype=int, device=device)
    patterns = {
        "all_active": np.zeros(nworld, dtype=np.bool_),
        "some_done": (np.arange(nworld) % 3 == 0),
        "zero_active": np.ones(nworld, dtype=np.bool_),
    }
    receipts = []
    for name, done_host in patterns.items():
        done = wp.array(done_host, dtype=wp.bool, device=device)
        wp.launch(solver._r20r3p1_build_active_ids, dim=1, inputs=[done, nworld], outputs=[ids, count])
        wp.synchronize()
        actual = int(count.numpy()[0])
        expected = np.flatnonzero(~done_host)
        ok = actual == len(expected) and np.array_equal(ids.numpy()[:actual], expected)
        receipts.append({"name": name, "expected": len(expected), "observed": actual,
                         "ascending_exact": bool(ok)})
        if not ok:
            raise RuntimeError(f"Active-list canary failed: {name}")
    return receipts


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--canary-only", action="store_true")
    args = p.parse_args()
    if os.environ.get("R20R3P2_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU campaign lock receipt absent")
    if Path(os.environ.get("PYTHONPATH", "").split(os.pathsep)[0]).resolve() != ROOT / "source_overlay":
        raise RuntimeError("Isolated source overlay not selected")
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    import mujoco_warp as mjw
    from mujoco_warp._src import solver
    from mujoco_warp._src.io import load_trajectory, override_model
    if Path(solver.__file__).resolve() != ROOT / "source_overlay/mujoco_warp/_src/solver.py":
        raise RuntimeError("Candidate source path mismatch")
    if file_sha(Path(solver.__file__)) != "868cf9b0420d61656b3698ba7ddc93b6aa3d6a031d825c939a9868adf916a8e3":
        raise RuntimeError("Accepted P1 candidate source SHA mismatch")
    device = wp.get_device("cuda:0")
    if device.sm_count != 76:
        raise RuntimeError("Fixed SM-count authority changed")
    with wp.ScopedDevice(device):
        canaries = list_canaries(solver, device)
        (RAW / "ACTIVE_LIST_CANARIES.json").write_text(json.dumps(canaries, indent=2, sort_keys=True) + "\n")
        if args.canary_only:
            print(json.dumps({"list_canaries": canaries, "result": "PASS"}), flush=True)
            return
        for step in STEPS:
            if file_sha(R1 / f"raw/R2_T{step}_SOLVER_ENTRY_FULL_DATA.npz") != EXPECTED_SHA[step]:
                raise RuntimeError(f"Frozen step {step} input SHA mismatch")
        lineage = json.loads((R1 / "raw/R2_DISCOVERY_ENTRY_LINEAGE.json").read_text())
        entries = {x["step"]: x["entry_snapshot"] for x in lineage["entrances"]}
        mjm = mujoco.MjSpec.from_file(str(SCENE / "scene_hfield.xml")).compile()
        mjd = mujoco.MjData(mjm)
        if len(load_trajectory(str(SCENE / "shuffle_dance.npz"), mjm, mjd)) != 1000:
            raise RuntimeError("Control trajectory mismatch")
        model = mjw.put_model(mjm)
        override_model(model, ["opt.warn_overflow=~ITERATIONS|~LS_ITERATIONS"])
        if not (model.opt.graph_conditional and model.is_sparse and int(model.opt.iterations) == 10
                and int(model.opt.ls_iterations) == 20):
            raise RuntimeError("Frozen solver options changed")
        expected_model = {x["path"]: x["sha256"] for x in json.loads((R1 / "raw/G0_MODEL_ARRAY_MANIFEST.json").read_text())}
        model_arrays = enumerate_data_arrays(model)
        if set(model_arrays) != set(expected_model) or any(sha_numpy(v.numpy()) != expected_model[k] for k, v in model_arrays.items()):
            raise RuntimeError("Frozen Model array identity mismatch")
        data = mjw.put_data(mjm, mjd, nworld=1024, nconmax=48, njmax=192)
        contexts = []
        original_factory = solver._create_solver_context

        def witness(m, d):
            ctx = original_factory(m, d)
            contexts.append(ctx)
            return ctx

        solver._create_solver_context = witness
        try:
            solver._R20R3P1_ACTIVE = False
            with wp.ScopedCapture() as b0_graph:
                solver.solve(model, data)
            solver._R20R3P1_ACTIVE_IDS = wp.empty(1024, dtype=int, device=device)
            solver._R20R3P1_ACTIVE_COUNT = wp.empty(1, dtype=int, device=device)
            solver._R20R3P1_WORKERS = 304
            solver._R20R3P1_ACTIVE = True
            with wp.ScopedCapture() as s1_graph:
                solver.solve(model, data)
        finally:
            solver._R20R3P1_ACTIVE = False
            solver._create_solver_context = original_factory
        if len(contexts) != 2:
            raise RuntimeError("B0/S1 context capture count differs")
        b0_ctx, s1_ctx = contexts
        masks = wp.empty(1024, dtype=int, device=device)
        values = wp.empty((1024, 6), dtype=float, device=device)
        results = []
        for step in STEPS:
            entry = entries[step]
            if entry["sha256"] != EXPECTED_SHA[step]:
                raise RuntimeError(f"Lineage SHA mismatch t{step}")
            restore_recorded_snapshot(data, entry)
            frozen = make_gpu_snapshot(data)
            outputs = {}
            statuses = {}
            residuals = {}
            stop_checks = {}
            for arm, graph, ctx in (("B0", b0_graph, b0_ctx), ("S1", s1_graph, s1_ctx)):
                restore_gpu_snapshot(data, frozen)
                arrays = enumerate_data_arrays(data)
                for item in entry["manifest"]:
                    if sha_numpy(arrays[item["field_path"]].numpy()) != item["sha256"]:
                        raise RuntimeError(f"Input Data differs at t{step}:{item['field_path']}")
                wp.capture_launch(graph.graph)
                wp.synchronize()
                out = output_view(data)
                status, gradient, model_improvement = check_output(step, reference(step), out, data, ctx, model,
                                                                   frozen["overflow"].numpy())
                wp.launch(source_stop_predicates, dim=1024,
                          inputs=[model.nv, model.opt.tolerance, model.stat.meaninertia, ctx.alpha,
                                  ctx.improvement, ctx.grad_dot, ctx.newton_decrement],
                          outputs=[masks, values])
                wp.synchronize()
                mask_host = masks.numpy().copy()
                values_host = values.numpy().copy()
                stop = summarize_stop(mask_host, values_host, out["solver_niter"],
                                      frozen["overflow"].numpy(), out["overflow"], ctx.done.numpy().copy(),
                                      int(model.opt.iterations))
                outputs[arm], statuses[arm] = out, status
                residuals[arm] = (gradient, model_improvement)
                stop_checks[arm] = stop
                np.savez_compressed(RAW / f"CORRECTNESS_T{step}_{arm}.npz",
                                    **{k.replace('.', '_'): v for k, v in out.items()},
                                    gradient=gradient, model_improvement=model_improvement,
                                    alpha=ctx.alpha.numpy().copy(), improvement=ctx.improvement.numpy().copy(),
                                    stop_mask=mask_host, stop_values=values_host)
                if not status["qualified"] or not stop["pass"]:
                    print(json.dumps({"step": step, "arm": arm, "reference_qualified": status["qualified"],
                                      "source_stop_pass": stop["pass"]}), flush=True)
                    break
            if len(statuses) != 2 or not all(x["qualified"] for x in statuses.values()) or not all(x["pass"] for x in stop_checks.values()):
                result = {"step": step, "qualified": False, "reason": "B0_OR_S1_SEMANTIC_OR_REFERENCE_GATE_FAIL",
                          "arms": statuses, "source_stop": stop_checks}
            else:
                pair = compare_pair(step, outputs["B0"], outputs["S1"], b0_ctx, s1_ctx,
                                    residuals["B0"][0], residuals["S1"][0],
                                    residuals["B0"][1], residuals["S1"][1])
                result = {"step": step, "qualified": pair["pass"], "pair": pair, "arms": statuses,
                          "source_stop": stop_checks,
                          "no_constraint_world_count": int(np.count_nonzero(outputs["B0"]["nefc"] == 0)),
                          "outer_iteration_limit_world_count": statuses["B0"]["ITERATIONS_count"],
                          "S1_final_active_count": int(solver._R20R3P1_ACTIVE_COUNT.numpy()[0]),
                          "worker_count": 304}
            (RAW / f"CORRECTNESS_T{step}_RECEIPT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            results.append({"step": step, "qualified": result["qualified"], "reason": result.get("reason", "PAIR_CHECK")})
            print(json.dumps(results[-1], sort_keys=True), flush=True)
            if not result["qualified"]:
                break
        summary = {"stage": "AWMA_R20R3P2_RESIDUAL_CONTRACT_REQUALIFICATION_AND_RESUME_109_V1",
                   "all_four_qualified": len(results) == 4 and all(x["qualified"] for x in results),
                   "worker_count": 304, "list_canaries": canaries, "results": results}
        (RAW / "CANDIDATE_CORRECTNESS_SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        print(json.dumps(summary, sort_keys=True), flush=True)
        if not summary["all_four_qualified"]:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
