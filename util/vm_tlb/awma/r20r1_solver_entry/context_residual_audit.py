#!/usr/bin/env python3
"""One bounded source-aligned SolverContext residual/read-after-replay audit."""

import json
import os
from pathlib import Path

import mujoco
import numpy as np
import warp as wp

from snapshot_io import enumerate_data_arrays, file_sha, restore_recorded_snapshot, sha_numpy


PARENT = Path("/data/c16/awma/r20_active_world_native_v1")
ROOT = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001")
RAW = ROOT / "raw"
SCENE = PARENT / "scene/unitree_g1_hfield"


def main():
    assert os.environ.get("R20R1_GPU_LOCK_HELD") == "1"
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    import mujoco_warp as mjw
    from mujoco_warp._src import solver
    from mujoco_warp._src.io import load_trajectory, override_model
    from mujoco_warp._src.types import OverflowType

    g0 = json.loads((RAW / "G0_T128_SOLVER_ENTRY_RECEIPT.json").read_text())
    device = wp.get_device("cuda:0")
    mjm = mujoco.MjSpec.from_file(str(SCENE / "scene_hfield.xml")).compile()
    mjd = mujoco.MjData(mjm)
    assert len(load_trajectory(str(SCENE / "shuffle_dance.npz"), mjm, mjd)) == 1000
    with wp.ScopedDevice(device):
        model = mjw.put_model(mjm)
        override_model(model, ["opt.warn_overflow=~ITERATIONS|~LS_ITERATIONS"])
        data = mjw.put_data(mjm, mjd, nworld=1024, nconmax=48, njmax=192)
        original = solver._create_solver_context
        contexts = []

        def witness(m, d):
            ctx = original(m, d)
            contexts.append(ctx)
            return ctx

        solver._create_solver_context = witness
        try:
            with wp.ScopedCapture() as graph:
                solver.solve(model, data)
        finally:
            solver._create_solver_context = original
        assert len(contexts) == 1
        ctx = contexts[0]
        restore_recorded_snapshot(data, g0["entry_snapshot"])
        print("R20R1_RESIDUAL_AUDIT_CAPTURE_AND_RESTORE_OK", flush=True)
        results = []
        saved = {name: [] for name in (
            "grad_dot", "newton_decrement", "alpha", "improvement", "done", "grad_scale",
            "grad", "niter", "overflow", "qfrc_smooth", "efc_Ma", "qfrc_constraint",
        )}
        for repeat in range(3):
            restore_recorded_snapshot(data, g0["entry_snapshot"])
            wp.capture_launch(graph.graph)
            wp.synchronize()
            print(f"R20R1_RESIDUAL_AUDIT_REPLAY_{repeat}_OK", flush=True)
            grad_dot = ctx.grad_dot.numpy().copy()
            newton_decrement = ctx.newton_decrement.numpy().copy()
            alpha = ctx.alpha.numpy().copy()
            improvement_raw = ctx.improvement.numpy().copy()
            done = ctx.done.numpy().copy()
            grad_scale = ctx.grad_scale.numpy().copy()
            grad = ctx.grad.numpy().copy()
            niter = data.solver_niter.numpy().copy()
            overflow = data.overflow.numpy().copy()
            qfrc_smooth = data.qfrc_smooth.numpy().copy()
            efc_Ma = data.efc.Ma.numpy().copy()
            qfrc_constraint = data.qfrc_constraint.numpy().copy()
            for name, value in (
                ("grad_dot", grad_dot), ("newton_decrement", newton_decrement),
                ("alpha", alpha), ("improvement", improvement_raw), ("done", done),
                ("grad_scale", grad_scale), ("grad", grad), ("niter", niter),
                ("overflow", overflow), ("qfrc_smooth", qfrc_smooth),
                ("efc_Ma", efc_Ma), ("qfrc_constraint", qfrc_constraint),
            ):
                saved[name].append(value)
            meaninertia = float(model.stat.meaninertia.numpy().reshape(-1)[0])
            tolerance = float(model.opt.tolerance.numpy().reshape(-1)[0])
            divisor = meaninertia * model.nv
            gradient = np.sqrt(np.maximum(grad_dot.astype(np.float64), 0.0)) / divisor
            model_improvement = 0.5 * newton_decrement.astype(np.float64) / divisor
            improvement = improvement_raw.astype(np.float64) / divisor
            predicates = {
                "alpha_zero": alpha == 0,
                "positive_small_improvement": (improvement > 0) & (improvement < tolerance),
                "small_gradient": gradient < tolerance,
                "small_model_improvement": model_improvement < tolerance,
                "iteration_limit": (overflow & int(OverflowType.ITERATIONS)) != 0,
            }
            if not all(np.isfinite(value).all() for value in (grad_dot, newton_decrement, alpha, improvement_raw, gradient, model_improvement)):
                raise RuntimeError("Nonfinite effective SolverContext residual field")
            qfrc_relation = efc_Ma.astype(np.float64) - qfrc_smooth.astype(np.float64) - grad_scale[:, None].astype(np.float64) * grad[:, :model.nv].astype(np.float64)
            relation_error = np.abs(qfrc_relation - qfrc_constraint.astype(np.float64))
            results.append({
                "repeat": repeat,
                "solver_niter_sha256": sha_numpy(niter),
                "overflow_sha256": sha_numpy(overflow),
                "context_done_all": bool(np.all(done)),
                "meaninertia": meaninertia,
                "nv": model.nv,
                "tolerance": tolerance,
                "predicate_world_counts": {name: int(np.count_nonzero(value)) for name, value in predicates.items()},
                "gradient_max": float(gradient.max()),
                "gradient_p99": float(np.quantile(gradient, 0.99)),
                "gradient_median": float(np.median(gradient)),
                "model_improvement_max": float(model_improvement.max()),
                "model_improvement_p99": float(np.quantile(model_improvement, 0.99)),
                "grad_dot_sha256": sha_numpy(grad_dot),
                "newton_decrement_sha256": sha_numpy(newton_decrement),
                "alpha_sha256": sha_numpy(alpha),
                "improvement_sha256": sha_numpy(improvement_raw),
                "done_sha256": sha_numpy(done),
                "qfrc_source_relation_max_abs_in_fp64_recompute": float(relation_error.max()),
                "qfrc_source_relation_rms_in_fp64_recompute": float(np.sqrt(np.mean(relation_error * relation_error))),
            })
        array_path = RAW / "SOLVER_CONTEXT_RESIDUAL_ARRAYS.npz"
        np.savez_compressed(array_path, **{key: np.stack(values) for key, values in saved.items()})
        receipt = {
            "stage": "AWMA_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_V1",
            "classification": "BOUNDED_SOLVER_CONTEXT_RESIDUAL_AUDIT_NO_TIMING",
            "source_stop_predicates": "solver.py::_solve_done: alpha==0 or positive improvement<tolerance or gradient<tolerance or model_improvement<tolerance; separate ITERATIONS bit",
            "solver_entry_sha256": g0["entry_snapshot"]["sha256"],
            "context_nonempty_fields": len(enumerate_data_arrays(ctx)),
            "residual_arrays_path": str(array_path),
            "residual_arrays_sha256": file_sha(array_path),
            "results": results,
        }
        (RAW / "SOLVER_CONTEXT_RESIDUAL_AUDIT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"results": results}, sort_keys=True))


if __name__ == "__main__":
    main()
