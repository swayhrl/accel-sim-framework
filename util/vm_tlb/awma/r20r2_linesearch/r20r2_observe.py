#!/usr/bin/env python3
"""Frozen t152 complete-solver LS observer; correctness only, never timing."""

import argparse
import json
import os
import sys
from pathlib import Path

import mujoco
import numpy as np
import warp as wp


PARENT = Path("/data/c16/awma/r20_active_world_native_v1")
R1 = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001")
ROOT = Path("/data/c16/awma/r20r2_linesearch_semantic_materiality_20261001")
RAW = ROOT / "raw"
SCENE = PARENT / "scene/unitree_g1_hfield"
PINNED = PARENT / "source/mujoco_warp"
OVERLAY = ROOT / "source_overlay"
ENTRY_SHA = "42e23fbdbb9aaae0dcbeacaa0e7ae278c1728bd9ff3a2881c8410e4f81f98e87"
CONTRACT_SHA = "456ca1fa3cbca9aa8d4a6c1cae14ea85a176f23660c9d0c8754a141eb70af66d"
WORLD = 413

HERE = Path(__file__).resolve()
AWMA = HERE.parents[1]
sys.path.insert(0, str(AWMA / "r20r1_solver_entry"))
sys.path.insert(0, str(AWMA / "r20_active_world"))
from b0_repeatability_t128 import output_view
from local_contract_validator import MAX_WORLD_NORM, RMS_NORM, RELATION_WORLD_NORM, world_normed
from snapshot_io import enumerate_data_arrays, file_sha, restore_recorded_snapshot, sha_numpy
from state_utils import make_gpu_snapshot, restore_gpu_snapshot


def reference_outputs():
    path = R1 / "raw/T152_B0_REPEAT_OUTPUTS.npz"
    with np.load(path, allow_pickle=False) as z:
        return {
            "qacc": z["run_0_qacc"].copy(),
            "qfrc_constraint": z["run_0_qfrc_constraint"].copy(),
            "solver_niter": z["run_0_solver_niter"].copy(),
            "overflow": z["run_0_overflow"].copy(),
            "efc.force": z["run_0_efc_force"].copy(),
            "efc.Ma": z["run_0_efc_Ma"].copy(),
            "nefc": z["run_0_nefc"].copy(),
            "efc.force_valid_concat": z["run_0_efc_force_valid_concat"].copy(),
        }


def compare(reference, observed, entry_overflow, ctx, model, data, residual_envelope):
    nefc_equal = bool(np.array_equal(reference["nefc"], observed["nefc"]))
    niter_equal = bool(np.array_equal(reference["solver_niter"], observed["solver_niter"]))
    ls = 1 << 10
    overflow_nonls_equal = bool(np.array_equal(reference["overflow"] & ~ls, observed["overflow"] & ~ls))
    float_fields = ("qacc", "qfrc_constraint", "efc.Ma", "efc.force")
    floating = {}
    for field in float_fields:
        metric = world_normed(reference[field], observed[field], reference["nefc"] if field == "efc.force" else None)
        metric["contract_pass"] = metric["max_world_normalized"] <= MAX_WORLD_NORM and metric["rms_global_normalized"] <= RMS_NORM
        floating[field] = metric
    new_bits = observed["overflow"] & ~entry_overflow
    capacity_mask = (1 << 12) - 1 - (1 << 9) - ls
    no_capacity = not np.count_nonzero(new_bits & capacity_mask)
    finite = all(np.isfinite(observed[field]).all() for field in float_fields + ("efc.force_valid_concat",))
    meaninertia = float(model.stat.meaninertia.numpy().reshape(-1)[0])
    nv = model.nv
    grad_dot = ctx.grad_dot.numpy().copy()
    decrement = ctx.newton_decrement.numpy().copy()
    grad = ctx.grad.numpy().copy()
    grad_scale = ctx.grad_scale.numpy().copy()
    done = ctx.done.numpy().copy()
    Ma = observed["efc.Ma"]
    smooth = data.qfrc_smooth.numpy().copy()
    qfrc = observed["qfrc_constraint"]
    predicted = Ma.astype(np.float64) - smooth.astype(np.float64) - grad_scale[:, None].astype(np.float64) * grad[:, :nv].astype(np.float64)
    scale = np.maximum(np.sqrt(np.mean(qfrc.astype(np.float64) ** 2, axis=1)), 1.0)
    relation = np.max(np.abs(predicted - qfrc.astype(np.float64)), axis=1) / scale
    gradient = np.sqrt(np.maximum(grad_dot.astype(np.float64), 0)) / (meaninertia * nv)
    model_improvement = 0.5 * decrement.astype(np.float64) / (meaninertia * nv)
    context_finite = all(np.isfinite(x).all() for x in (grad_dot, decrement, grad, grad_scale, gradient, model_improvement))
    gradient_envelope_pass = bool(np.all(gradient <= residual_envelope["gradient"] + 1e-6))
    improvement_envelope_pass = bool(np.all(model_improvement <= residual_envelope["model_improvement"] + 1e-6))
    # The parent B0-only validator gates source relation/done/finite. Its
    # candidate-only residual ceilings are reported here, not retroactively
    # imposed on another B0 repeat (there is no candidate in R20R2).
    context_pass = bool(np.all(done) and context_finite and np.all(relation <= RELATION_WORLD_NORM))
    return {
        "nefc_exact": nefc_equal,
        "niter_exact": niter_equal,
        "overflow_excluding_LS_exact": overflow_nonls_equal,
        "floating": floating,
        "finite": finite,
        "no_new_capacity": no_capacity,
        "ctx_done_all": bool(np.all(done)),
        "ctx_finite": context_finite,
        "ctx_source_relation_max": float(relation.max()),
        "ctx_source_relation_pass": bool(np.all(relation <= RELATION_WORLD_NORM)),
        "ctx_gradient_envelope_pass": gradient_envelope_pass,
        "ctx_model_improvement_envelope_pass": improvement_envelope_pass,
        "world413_nefc": int(observed["nefc"][WORLD]),
        "world413_solver_niter": int(observed["solver_niter"][WORLD]),
        "world413_LS_ITERATIONS": bool(observed["overflow"][WORLD] & ls),
        "world413_overflow": int(observed["overflow"][WORLD]),
        "world413_gradient": float(gradient[WORLD]),
        "world413_model_improvement": float(model_improvement[WORLD]),
        "qualified": (nefc_equal and niter_equal and overflow_nonls_equal and finite and no_capacity and context_pass
                      and all(v["contract_pass"] for v in floating.values())
                      and int(observed["nefc"][WORLD]) == 46 and int(observed["solver_niter"][WORLD]) == 8),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=("off", "on", "fresh"), required=True)
    p.add_argument("--max-repeats", type=int, required=True)
    args = p.parse_args()
    if os.environ.get("R20R2_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU campaign lock receipt absent")
    if args.mode == "off" and args.max_repeats != 5:
        raise RuntimeError("OFF regression is frozen to 5 repeats")
    if args.mode == "on" and args.max_repeats != 32:
        raise RuntimeError("ON bound is frozen to 32 repeats")
    if args.mode == "fresh" and args.max_repeats != 4:
        raise RuntimeError("fresh graph bound is frozen to 4 repeats")
    expected_source = PINNED if args.mode == "off" else OVERLAY
    if Path(os.environ.get("PYTHONPATH", "").split(os.pathsep)[0]).resolve() != expected_source:
        raise RuntimeError("Wrong source root selected")
    if file_sha(R1 / "raw/R2_T152_SOLVER_ENTRY_FULL_DATA.npz") != ENTRY_SHA:
        raise RuntimeError("Frozen input SHA mismatch")
    contract = HERE.parents[4] / "docs/vm_tlb/review_packs/AWMA_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_V1/LOCAL_NUMERICAL_CONTRACT.md"
    if file_sha(contract) != CONTRACT_SHA:
        raise RuntimeError("Frozen local numerical contract SHA mismatch")
    wp.config.kernel_cache_dir = str(ROOT / "cache" / args.mode / "warp")
    wp.init()
    import mujoco_warp as mjw
    from mujoco_warp._src import solver
    from mujoco_warp._src.io import load_trajectory, override_model
    print(json.dumps({"mode": args.mode, "solver_source": str(Path(solver.__file__).resolve()),
                      "solver_source_sha256": file_sha(Path(solver.__file__)), "input_sha256": ENTRY_SHA}), flush=True)
    if Path(solver.__file__).resolve() != expected_source / "mujoco_warp/_src/solver.py":
        raise RuntimeError("Imported solver source did not match selected root")
    lineage = json.loads((R1 / "raw/R2_DISCOVERY_ENTRY_LINEAGE.json").read_text())
    row = next(x for x in lineage["entrances"] if x["step"] == 152)
    entry = row["entry_snapshot"]
    if entry["sha256"] != ENTRY_SHA:
        raise RuntimeError("Lineage input SHA mismatch")
    reference = reference_outputs()
    with np.load(R1 / "raw/T152_B0_RESIDUAL_ARRAYS.npz", allow_pickle=False) as z:
        residual_envelope = {key: np.max(z[key].astype(np.float64), axis=0) for key in ("gradient", "model_improvement")}
    mjm = mujoco.MjSpec.from_file(str(SCENE / "scene_hfield.xml")).compile()
    mjd = mujoco.MjData(mjm)
    if len(load_trajectory(str(SCENE / "shuffle_dance.npz"), mjm, mjd)) != 1000:
        raise RuntimeError("Frozen control trajectory mismatch")
    device = wp.get_device("cuda:0")
    records = []
    with wp.ScopedDevice(device):
        model = mjw.put_model(mjm)
        override_model(model, ["opt.warn_overflow=~ITERATIONS|~LS_ITERATIONS"])
        if not (model.opt.graph_conditional and model.is_sparse and int(model.opt.iterations) == 10 and int(model.opt.ls_iterations) == 20):
            raise RuntimeError("Frozen solver configuration changed")
        expected_model = {x["path"]: x["sha256"] for x in json.loads((R1 / "raw/G0_MODEL_ARRAY_MANIFEST.json").read_text())}
        actual_model = enumerate_data_arrays(model)
        if set(actual_model) != set(expected_model):
            raise RuntimeError("Model field set changed")
        for path, array in actual_model.items():
            if sha_numpy(array.numpy()) != expected_model[path]:
                raise RuntimeError(f"Model array changed: {path}")
        data = mjw.put_data(mjm, mjd, nworld=1024, nconmax=48, njmax=192)
        ctx_witness = []
        original_make_ctx = solver._create_solver_context

        def witness(m, d):
            ctx = original_make_ctx(m, d)
            ctx_witness.append(ctx)
            return ctx

        solver._create_solver_context = witness
        if args.mode != "off":
            trace = wp.zeros((10, 22, 40), dtype=wp.float32, device=device)
            solver._R20R2_TRACE = trace
        else:
            trace = None
        try:
            if args.mode != "fresh":
                with wp.ScopedCapture() as graph:
                    solver.solve(model, data)
            else:
                graph = None
        finally:
            solver._create_solver_context = original_make_ctx
        if args.mode != "fresh" and len(ctx_witness) != 1:
            raise RuntimeError("Expected exactly one captured solver context")
        restore_recorded_snapshot(data, entry)
        frozen_gpu = make_gpu_snapshot(data)
        entry_overflow = frozen_gpu["overflow"].numpy().copy()
        for repeat in range(args.max_repeats):
            if args.mode == "fresh":
                ctx_witness.clear()
                solver._create_solver_context = witness
                try:
                    with wp.ScopedCapture() as graph:
                        solver.solve(model, data)
                finally:
                    solver._create_solver_context = original_make_ctx
                if len(ctx_witness) != 1:
                    raise RuntimeError("Fresh capture context count changed")
            ctx = ctx_witness[0]
            restore_gpu_snapshot(data, frozen_gpu)
            current_arrays = enumerate_data_arrays(data)
            for item in entry["manifest"]:
                array = current_arrays[item["field_path"]]
                if sha_numpy(array.numpy()) != item["sha256"]:
                    raise RuntimeError(f"Entry array mismatch: {item['field_path']}")
            if trace is not None:
                trace.zero_()
            wp.capture_launch(graph.graph)
            wp.synchronize()
            observed = output_view(data)
            result = compare(reference, observed, entry_overflow, ctx, model, data, residual_envelope)
            result.update({"mode": args.mode, "repeat": repeat, "entry_sha256": ENTRY_SHA,
                           "constraint_coverage_exact": result["nefc_exact"],
                           "source_sha256": file_sha(Path(solver.__file__))})
            prefix = f"{args.mode.upper()}_{repeat:02d}"
            payload = {f"output_{key.replace('.', '_')}": value for key, value in observed.items()}
            if trace is not None:
                payload["trace"] = trace.numpy().copy()
            np.savez_compressed(RAW / f"{prefix}_FULL_OUTPUT_AND_TRACE.npz", **payload)
            result["raw_path"] = str(RAW / f"{prefix}_FULL_OUTPUT_AND_TRACE.npz")
            result["raw_sha256"] = file_sha(Path(result["raw_path"]))
            (RAW / f"{prefix}_RECEIPT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            records.append(result)
            print(json.dumps({"mode": args.mode, "repeat": repeat, "qualified": result["qualified"],
                              "world413_LS_ITERATIONS": result["world413_LS_ITERATIONS"],
                              "world413_niter": result["world413_solver_niter"],
                              "max_qacc_norm": result["floating"]["qacc"]["max_world_normalized"]}), flush=True)
            if not result["qualified"]:
                break
            if args.mode == "on" and len({x["world413_LS_ITERATIONS"] for x in records}) == 2:
                break
            if args.mode == "fresh" and len({x["world413_LS_ITERATIONS"] for x in records}) == 2:
                break
        summary = {"mode": args.mode, "repeats": len(records), "all_qualified": all(x["qualified"] for x in records),
                   "world413_flag_outcomes": sorted({x["world413_LS_ITERATIONS"] for x in records}),
                   "source_sha256": file_sha(Path(solver.__file__)), "entry_sha256": ENTRY_SHA,
                   "contract_sha256": CONTRACT_SHA}
        (RAW / f"{args.mode.upper()}_SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        print(json.dumps(summary, sort_keys=True), flush=True)
        if not summary["all_qualified"]:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
