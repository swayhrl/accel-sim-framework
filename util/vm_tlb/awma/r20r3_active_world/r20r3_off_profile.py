#!/usr/bin/env python3
"""R20R3 exact-entry OFF qualification and the one four-entry B0 NSYS workload."""

import argparse
import ctypes
import json
import os
import sys
from pathlib import Path

import mujoco
import numpy as np
import warp as wp


ROOT = Path("/data/c16/awma/r20r3_active_world_solver_native_20261001")
PARENT = Path("/data/c16/awma/r20_active_world_native_v1")
R1 = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001")
SCENE = PARENT / "scene/unitree_g1_hfield"
RAW = ROOT / "raw"
STEPS = (128, 136, 144, 152)
EXPECTED_SHA = {128: "8f3d7015979e959625f3b1d1cd1efb3fb2dea65b4e07bc9c9f1795b30dccd85d",
                136: "07c012c0d17eaba3522bcc35016eff581612c138b7c876dff64455788344e883",
                144: "4177e0a8a509608651f85f055877576cd71d3f25a40ab2451f276c9b08cdfda6",
                152: "42e23fbdbb9aaae0dcbeacaa0e7ae278c1728bd9ff3a2881c8410e4f81f98e87"}
CONTRACT_SHA = "456ca1fa3cbca9aa8d4a6c1cae14ea85a176f23660c9d0c8754a141eb70af66d"
HERE = Path(__file__).resolve()
WORKTREE = HERE.parents[4]
sys.path.insert(0, str(HERE.parents[1] / "r20r1_solver_entry"))
sys.path.insert(0, str(HERE.parents[1] / "r20_active_world"))
from b0_repeatability_t128 import output_view
from local_contract_validator import MAX_WORLD_NORM, RMS_NORM, RELATION_WORLD_NORM, world_normed
from snapshot_io import enumerate_data_arrays, file_sha, restore_recorded_snapshot, sha_numpy
from state_utils import make_gpu_snapshot, restore_gpu_snapshot


def reference(step):
    with np.load(R1 / f"raw/T{step}_B0_REPEAT_OUTPUTS.npz", allow_pickle=False) as z:
        return {field: z[f"run_0_{field.replace('.', '_') }"].copy()
                for field in ("qacc", "qfrc_constraint", "solver_niter", "overflow", "efc.force", "efc.Ma", "nefc",
                              "efc.force_valid_concat")}


def check_output(step, ref, out, data, ctx, model, entry_overflow):
    ls_bit = 1 << 10
    iterations_bit = 1 << 9
    nefc_exact = bool(np.array_equal(ref["nefc"], out["nefc"]))
    niter_exact = bool(np.array_equal(ref["solver_niter"], out["solver_niter"]))
    other_status_exact = bool(np.array_equal(ref["overflow"] & ~ls_bit, out["overflow"] & ~ls_bit))
    capacity_mask = (1 << 12) - 1 - iterations_bit - ls_bit
    no_new_capacity = not np.count_nonzero((out["overflow"] & ~entry_overflow) & capacity_mask)
    floating = {}
    for field in ("qacc", "qfrc_constraint", "efc.Ma", "efc.force"):
        x = world_normed(ref[field], out[field], ref["nefc"] if field == "efc.force" else None)
        x["pass"] = x["max_world_normalized"] <= MAX_WORLD_NORM and x["rms_global_normalized"] <= RMS_NORM
        floating[field] = x
    finite = all(np.isfinite(out[field]).all() for field in ("qacc", "qfrc_constraint", "efc.Ma", "efc.force_valid_concat"))
    grad = ctx.grad.numpy().copy()
    grad_scale = ctx.grad_scale.numpy().copy()
    grad_dot = ctx.grad_dot.numpy().copy()
    decrement = ctx.newton_decrement.numpy().copy()
    done = ctx.done.numpy().copy()
    smooth = data.qfrc_smooth.numpy().copy()
    qfrc = out["qfrc_constraint"]
    prediction = out["efc.Ma"].astype(np.float64) - smooth.astype(np.float64) - grad_scale[:, None].astype(np.float64) * grad[:, :model.nv].astype(np.float64)
    scale = np.maximum(np.sqrt(np.mean(qfrc.astype(np.float64) ** 2, axis=1)), 1.0)
    relation = np.max(np.abs(prediction - qfrc.astype(np.float64)), axis=1) / scale
    meaninertia = float(model.stat.meaninertia.numpy().reshape(-1)[0])
    gradient = np.sqrt(np.maximum(grad_dot.astype(np.float64), 0)) / (meaninertia * model.nv)
    model_improvement = 0.5 * decrement.astype(np.float64) / (meaninertia * model.nv)
    ctx_finite = all(np.isfinite(x).all() for x in (grad, grad_scale, grad_dot, decrement, gradient, model_improvement))
    ctx_pass = bool(np.all(done) and ctx_finite and np.all(relation <= RELATION_WORLD_NORM))
    status = {
        "step": step, "entry_sha256": EXPECTED_SHA[step], "nefc_exact": nefc_exact,
        "solver_niter_exact": niter_exact, "non_LS_overflow_exact": other_status_exact,
        "no_new_capacity_overflow": bool(no_new_capacity), "floating": floating, "finite": finite,
        "ctx_done_all": bool(np.all(done)), "ctx_finite": ctx_finite,
        "qfrc_source_relation_max_normalized": float(relation.max()), "qfrc_source_relation_pass": ctx_pass,
        "LS_ITERATIONS_worlds": np.flatnonzero((out["overflow"] & ls_bit) != 0).astype(int).tolist(),
        "LS_ITERATIONS_count": int(np.count_nonzero((out["overflow"] & ls_bit) != 0)),
        "ITERATIONS_count": int(np.count_nonzero((out["overflow"] & iterations_bit) != 0)),
        "gradient_max": float(np.max(gradient)), "model_improvement_max": float(np.max(model_improvement)),
        "qualified": (nefc_exact and niter_exact and other_status_exact and bool(no_new_capacity) and finite
                      and ctx_pass and all(x["pass"] for x in floating.values())),
    }
    return status, gradient, model_improvement


class Nvtx:
    def __init__(self):
        self.lib = ctypes.CDLL("libnvToolsExt.so.1")
        self.lib.nvtxRangePushA.argtypes = [ctypes.c_char_p]
        self.lib.nvtxRangePushA.restype = ctypes.c_int
        self.lib.nvtxRangePop.argtypes = []
        self.lib.nvtxRangePop.restype = ctypes.c_int

    def push(self, name):
        self.lib.nvtxRangePushA(name.encode("ascii"))

    def pop(self):
        self.lib.nvtxRangePop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("baseline", "profile"), required=True)
    args = parser.parse_args()
    if os.environ.get("R20R3_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU campaign lock receipt absent")
    overlay = ROOT / "source_overlay"
    if Path(os.environ.get("PYTHONPATH", "").split(os.pathsep)[0]).resolve() != overlay:
        raise RuntimeError("OFF source overlay not selected")
    for step in STEPS:
        if file_sha(R1 / f"raw/R2_T{step}_SOLVER_ENTRY_FULL_DATA.npz") != EXPECTED_SHA[step]:
            raise RuntimeError(f"Frozen step {step} input SHA mismatch")
    contract = WORKTREE / "docs/vm_tlb/review_packs/AWMA_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_V1/LOCAL_NUMERICAL_CONTRACT.md"
    if file_sha(contract) != CONTRACT_SHA:
        raise RuntimeError("Parent local numerical contract changed")
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    import mujoco_warp as mjw
    from mujoco_warp._src import solver
    from mujoco_warp._src.io import load_trajectory, override_model
    if Path(solver.__file__).resolve() != overlay / "mujoco_warp/_src/solver.py":
        raise RuntimeError("Imported source path mismatch")
    lineage = json.loads((R1 / "raw/R2_DISCOVERY_ENTRY_LINEAGE.json").read_text())
    entries = {row["step"]: row["entry_snapshot"] for row in lineage["entrances"]}
    if set(entries) != set(STEPS):
        raise RuntimeError("Lineage step set mismatch")
    mjm = mujoco.MjSpec.from_file(str(SCENE / "scene_hfield.xml")).compile()
    mjd = mujoco.MjData(mjm)
    if len(load_trajectory(str(SCENE / "shuffle_dance.npz"), mjm, mjd)) != 1000:
        raise RuntimeError("Control trajectory authority mismatch")
    results = []
    device = wp.get_device("cuda:0")
    with wp.ScopedDevice(device):
        model = mjw.put_model(mjm)
        override_model(model, ["opt.warn_overflow=~ITERATIONS|~LS_ITERATIONS"])
        if not (model.opt.graph_conditional and model.is_sparse and int(model.opt.iterations) == 10
                and int(model.opt.ls_iterations) == 20):
            raise RuntimeError("Solver options changed")
        expected_model = {x["path"]: x["sha256"] for x in json.loads((R1 / "raw/G0_MODEL_ARRAY_MANIFEST.json").read_text())}
        actual_model = enumerate_data_arrays(model)
        if set(actual_model) != set(expected_model):
            raise RuntimeError("Model array field set changed")
        for path, array in actual_model.items():
            if sha_numpy(array.numpy()) != expected_model[path]:
                raise RuntimeError(f"Model array changed at {path}")
        data = mjw.put_data(mjm, mjd, nworld=1024, nconmax=48, njmax=192)
        original_make = solver._create_solver_context
        contexts = []

        def witness(m, d):
            ctx = original_make(m, d)
            contexts.append(ctx)
            return ctx

        solver._create_solver_context = witness
        try:
            with wp.ScopedCapture() as graph:
                solver.solve(model, data)
        finally:
            solver._create_solver_context = original_make
        if len(contexts) != 1:
            raise RuntimeError("Expected one complete-solver context in graph")
        ctx = contexts[0]
        frozen = {}
        for step in STEPS:
            entry = entries[step]
            if entry["sha256"] != EXPECTED_SHA[step]:
                raise RuntimeError(f"Lineage SHA mismatch for {step}")
            restore_recorded_snapshot(data, entry)
            frozen[step] = make_gpu_snapshot(data)
        nvtx = Nvtx() if args.mode == "profile" else None
        if nvtx:
            nvtx.push("R20R3_PROFILE")
        try:
            for step in STEPS:
                restore_gpu_snapshot(data, frozen[step])
                arrays = enumerate_data_arrays(data)
                for item in entries[step]["manifest"]:
                    if sha_numpy(arrays[item["field_path"]].numpy()) != item["sha256"]:
                        raise RuntimeError(f"Data input differs at t{step}:{item['field_path']}")
                if nvtx:
                    nvtx.push(f"R20R3_T{step}_OFF_B0")
                wp.capture_launch(graph.graph)
                wp.synchronize()
                if nvtx:
                    nvtx.pop()
                out = output_view(data)
                status, gradient, improvement = check_output(step, reference(step), out, data, ctx, model,
                                                             frozen[step]["overflow"].numpy())
                status.update({"mode": args.mode, "source_sha256": file_sha(Path(solver.__file__)),
                               "input_138_array_hashes_checked": True, "model_266_array_hashes_checked": True})
                prefix = f"{args.mode.upper()}_T{step}"
                np.savez_compressed(RAW / f"{prefix}_OUTPUTS.npz", **{k.replace('.', '_'): v for k, v in out.items()},
                                    gradient=gradient, model_improvement=improvement)
                status["output_payload_sha256"] = file_sha(RAW / f"{prefix}_OUTPUTS.npz")
                (RAW / f"{prefix}_RECEIPT.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
                results.append(status)
                print(json.dumps({"mode": args.mode, "step": step, "qualified": status["qualified"],
                                  "LS_count": status["LS_ITERATIONS_count"]}, sort_keys=True), flush=True)
                if not status["qualified"]:
                    break
        finally:
            if nvtx:
                nvtx.pop()
        summary = {"mode": args.mode, "entry_order": [x["step"] for x in results],
                   "all_qualified": len(results) == len(STEPS) and all(x["qualified"] for x in results),
                   "source_sha256": file_sha(Path(solver.__file__)),
                   "contract_sha256": CONTRACT_SHA,
                   "results": [{"step": x["step"], "qualified": x["qualified"],
                                "LS_ITERATIONS_count": x["LS_ITERATIONS_count"]} for x in results]}
        (RAW / f"{args.mode.upper()}_SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        print(json.dumps(summary, sort_keys=True), flush=True)
        if not summary["all_qualified"]:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
