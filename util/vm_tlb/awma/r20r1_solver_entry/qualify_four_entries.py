#!/usr/bin/env python3
"""Frozen-contract B0 solver qualification at t128,136,144,152; no S1."""

import csv
import json
import os
from pathlib import Path

import mujoco
import numpy as np
import warp as wp

from b0_repeatability_t128 import OUTPUT_FIELDS, output_from_record, output_view
from local_contract_validator import MAX_WORLD_NORM, RMS_NORM, RELATION_WORLD_NORM, world_normed
from snapshot_io import enumerate_data_arrays, file_sha, restore_recorded_snapshot, sha_numpy
from state_utils import make_gpu_snapshot, restore_gpu_snapshot


PARENT = Path("/data/c16/awma/r20_active_world_native_v1")
ROOT = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001")
RAW = ROOT / "raw"
SCENE = PARENT / "scene/unitree_g1_hfield"
STEPS = (128, 136, 144, 152)
EFFECTIVE_FLOAT = ("qacc", "qfrc_constraint", "efc.Ma", "efc.force")
EXACT_DISCRETE = ("nefc", "solver_niter", "overflow")


def compare(reference, candidate):
    nefc = reference["nefc"]
    floating = {}
    for field in EFFECTIVE_FLOAT:
        metric = world_normed(reference[field], candidate[field], nefc if field == "efc.force" else None)
        metric["max_world_pass"] = metric["max_world_normalized"] <= MAX_WORLD_NORM
        metric["rms_global_pass"] = metric["rms_global_normalized"] <= RMS_NORM
        floating[field] = metric
    discrete = {field: bool(np.array_equal(reference[field], candidate[field])) for field in EXACT_DISCRETE}
    return {"floating": floating, "discrete_exact": discrete,
            "pass": all(discrete.values()) and all(value["max_world_pass"] and value["rms_global_pass"] for value in floating.values())}


def context_values(ctx, data, meaninertia, nv, tolerance):
    grad_dot = ctx.grad_dot.numpy().copy()
    decrement = ctx.newton_decrement.numpy().copy()
    grad = ctx.grad.numpy().copy()
    grad_scale = ctx.grad_scale.numpy().copy()
    done = ctx.done.numpy().copy()
    Ma = data.efc.Ma.numpy().copy()
    smooth = data.qfrc_smooth.numpy().copy()
    qfrc = data.qfrc_constraint.numpy().copy()
    predicted = Ma.astype(np.float64) - smooth.astype(np.float64) - grad_scale[:, None].astype(np.float64) * grad[:, :nv].astype(np.float64)
    scale = np.maximum(np.sqrt(np.mean(qfrc.astype(np.float64) ** 2, axis=1)), 1.0)
    relation = np.max(np.abs(predicted - qfrc.astype(np.float64)), axis=1) / scale
    gradient = np.sqrt(np.maximum(grad_dot.astype(np.float64), 0)) / (meaninertia * nv)
    model_improvement = 0.5 * decrement.astype(np.float64) / (meaninertia * nv)
    if not all(np.isfinite(value).all() for value in (grad_dot, decrement, grad, grad_scale, gradient, model_improvement)):
        raise RuntimeError("Nonfinite SolverContext result")
    return {"gradient": gradient, "model_improvement": model_improvement,
            "source_relation_max_world_normalized": float(relation.max()),
            "source_relation_pass": bool(np.all(relation <= RELATION_WORLD_NORM)),
            "done_all": bool(np.all(done)),
            "gradient_sha256": sha_numpy(gradient),
            "model_improvement_sha256": sha_numpy(model_improvement)}


def full_input_check(data, record):
    arrays = enumerate_data_arrays(data)
    for row in record["manifest"]:
        if sha_numpy(arrays[row["field_path"]].numpy()) != row["sha256"]:
            raise RuntimeError(f"Frozen solver input changed at {row['field_path']}")


def main():
    assert os.environ.get("R20R1_GPU_LOCK_HELD") == "1"
    contract_path = Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r20r1-solver-entry-local-contract-109-v1/docs/vm_tlb/review_packs/AWMA_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_V1/LOCAL_NUMERICAL_CONTRACT.md")
    contract_sha = file_sha(contract_path)
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    import mujoco_warp as mjw
    from mujoco_warp._src import solver
    from mujoco_warp._src.io import load_trajectory, override_model
    from mujoco_warp._src.types import OverflowType

    lineage = json.loads((RAW / "R2_DISCOVERY_ENTRY_LINEAGE.json").read_text())
    rows = lineage["entrances"]
    assert [row["step"] for row in rows] == list(STEPS)
    device = wp.get_device("cuda:0")
    mjm = mujoco.MjSpec.from_file(str(SCENE / "scene_hfield.xml")).compile()
    mjd = mujoco.MjData(mjm)
    assert len(load_trajectory(str(SCENE / "shuffle_dance.npz"), mjm, mjd)) == 1000
    with wp.ScopedDevice(device):
        model = mjw.put_model(mjm)
        override_model(model, ["opt.warn_overflow=~ITERATIONS|~LS_ITERATIONS"])
        data = mjw.put_data(mjm, mjd, nworld=1024, nconmax=48, njmax=192)
        expected_model = {row["path"]: row["sha256"] for row in json.loads((RAW / "G0_MODEL_ARRAY_MANIFEST.json").read_text())}
        actual_model = enumerate_data_arrays(model)
        assert set(actual_model) == set(expected_model)
        for path, array in actual_model.items():
            if sha_numpy(array.numpy()) != expected_model[path]:
                raise RuntimeError(f"Frozen Model array mismatch at {path}")
        original_make_ctx = solver._create_solver_context
        contexts = []

        def witness(m, d):
            ctx = original_make_ctx(m, d)
            contexts.append(ctx)
            return ctx

        solver._create_solver_context = witness
        try:
            with wp.ScopedCapture() as graph:
                solver.solve(model, data)
        finally:
            solver._create_solver_context = original_make_ctx
        assert len(contexts) == 1 and model.opt.graph_conditional
        ctx = contexts[0]
        fresh_data = mjw.put_data(mjm, mjd, nworld=1024, nconmax=48, njmax=192)
        with wp.ScopedCapture() as fresh_graph:
            solver.solve(model, fresh_data)
        meaninertia = float(model.stat.meaninertia.numpy().reshape(-1)[0])
        tolerance = float(model.opt.tolerance.numpy().reshape(-1)[0])
        assert tolerance == 1e-6 or abs(tolerance - 1e-6) < 1e-12
        all_receipts = []
        compact = []
        for row in rows:
            step = row["step"]
            entry = row["entry_snapshot"]
            original_exit = output_from_record(row["exit_snapshot"])
            restore_recorded_snapshot(data, entry)
            gpu_snapshot = make_gpu_snapshot(data)
            outputs = []
            contexts_per_run = []
            for repeat in range(5):
                restore_gpu_snapshot(data, gpu_snapshot)
                full_input_check(data, entry)
                wp.capture_launch(graph.graph)
                wp.synchronize()
                outputs.append(output_view(data))
                contexts_per_run.append(context_values(ctx, data, meaninertia, model.nv, tolerance))
            if step == 128:
                restore_gpu_snapshot(fresh_data, gpu_snapshot)
                full_input_check(fresh_data, entry)
                wp.capture_launch(fresh_graph.graph)
                wp.synchronize()
                outputs.append(output_view(fresh_data))
            reference = outputs[0]
            comparisons = [compare(reference, observed) for observed in outputs[1:]]
            original_comparison = compare(reference, original_exit)
            relation_pass = all(record["source_relation_pass"] and record["done_all"] for record in contexts_per_run)
            entry_overflow = gpu_snapshot["overflow"].numpy()
            new_bits = reference["overflow"] & ~entry_overflow
            capacity_mask = int(OverflowType.ALL) & ~(int(OverflowType.ITERATIONS) | int(OverflowType.LS_ITERATIONS))
            no_new_capacity = not np.count_nonzero(new_bits & capacity_mask)
            finite_outputs = all(np.isfinite(observed[field]).all() for observed in outputs for field in ("qacc", "qfrc_constraint", "efc.Ma", "efc.force_valid_concat"))
            qualified = all(comp["pass"] for comp in comparisons) and original_comparison["pass"] and relation_pass and no_new_capacity and finite_outputs
            raw_outputs = RAW / f"T{step}_B0_REPEAT_OUTPUTS.npz"
            np.savez_compressed(raw_outputs, **{
                f"run_{i}_{field.replace('.', '_')}": value
                for i, result in enumerate(outputs) for field, value in result.items()
            })
            raw_residual = RAW / f"T{step}_B0_RESIDUAL_ARRAYS.npz"
            np.savez_compressed(raw_residual,
                                gradient=np.stack([item["gradient"] for item in contexts_per_run]),
                                model_improvement=np.stack([item["model_improvement"] for item in contexts_per_run]))
            context_summaries = [
                {key: value for key, value in item.items() if key not in ("gradient", "model_improvement")}
                for item in contexts_per_run
            ]
            result = {
                "step": step,
                "classification": "PREDECLARED_R2_B0_ONLY_ENTRANCE_QUALIFICATION",
                "contract_sha256_frozen_before_R2": contract_sha,
                "entry_sha256": entry["sha256"],
                "in_situ_exit_sha256": row["exit_snapshot"]["sha256"],
                "model_array_hashes_exact": True,
                "all_138_data_input_hashes_exact_each_run": True,
                "five_same_graph_repeats": 5,
                "independent_new_graph_repeats": 1 if step == 128 else 0,
                "B0_comparisons_to_first": comparisons,
                "in_situ_exit_comparison_to_first": original_comparison,
                "source_relation_and_done": context_summaries,
                "source_relation_all_pass": relation_pass,
                "no_new_capacity_overflow": no_new_capacity,
                "finite_outputs": finite_outputs,
                "solver_niter_min_max": [int(reference["solver_niter"].min()), int(reference["solver_niter"].max())],
                "nefc_min_max": [int(reference["nefc"].min()), int(reference["nefc"].max())],
                "new_overflow_or": int(np.bitwise_or.reduce(new_bits.reshape(-1))),
                "outputs_npz_path": str(raw_outputs),
                "outputs_npz_sha256": file_sha(raw_outputs),
                "residual_npz_path": str(raw_residual),
                "residual_npz_sha256": file_sha(raw_residual),
                "B0_local_contract_qualified": qualified,
            }
            (RAW / f"T{step}_B0_QUALIFICATION.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            all_receipts.append(result)
            compact.append({
                "step": step,
                "entry_sha256": entry["sha256"],
                "B0_qualified": qualified,
                "niter_min": result["solver_niter_min_max"][0],
                "niter_max": result["solver_niter_min_max"][1],
                "nefc_min": result["nefc_min_max"][0],
                "nefc_max": result["nefc_min_max"][1],
                "same_graph_repeat_count": 5,
                "fresh_graph_repeat_count": result["independent_new_graph_repeats"],
                "all_discrete_signatures_exact": all(all(comp["discrete_exact"].values()) for comp in comparisons) and all(original_comparison["discrete_exact"].values()),
                "source_relation_pass": relation_pass,
                "max_qacc_world_normalized": max([original_comparison["floating"]["qacc"]["max_world_normalized"], *[comp["floating"]["qacc"]["max_world_normalized"] for comp in comparisons]]),
                "max_qfrc_world_normalized": max([original_comparison["floating"]["qfrc_constraint"]["max_world_normalized"], *[comp["floating"]["qfrc_constraint"]["max_world_normalized"] for comp in comparisons]]),
            })
            print(json.dumps(compact[-1], sort_keys=True), flush=True)
            if step == 128 and not qualified:
                break
        with (RAW / "FOUR_ENTRY_B0_QUALIFICATION.tsv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(compact[0]), delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(compact)
        aggregate = {
            "stage": "AWMA_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_V1",
            "R2_lineage_source": "R2_DISCOVERY_ENTRY_LINEAGE.json",
            "contract_sha256_frozen_before_R2": contract_sha,
            "entries_completed": [item["step"] for item in all_receipts],
            "all_four_B0_qualified": len(all_receipts) == 4 and all(item["B0_local_contract_qualified"] for item in all_receipts),
            "t128_requalification_required_and_performed": True,
            "rows": compact,
        }
        (RAW / "FOUR_ENTRY_B0_SUMMARY.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"all_four_B0_qualified": aggregate["all_four_B0_qualified"], "entries_completed": aggregate["entries_completed"]}, sort_keys=True))
        if not aggregate["all_four_B0_qualified"]:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
