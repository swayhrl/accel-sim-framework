#!/usr/bin/env python3
"""Five exact-entry complete-solver B0 replays plus one fresh-graph witness."""

import csv
import json
import os
import time
from pathlib import Path

import mujoco
import numpy as np
import warp as wp

from snapshot_io import (
    enumerate_data_arrays, file_sha, restore_recorded_snapshot, sha_numpy,
)


PARENT = Path("/data/c16/awma/r20_active_world_native_v1")
ROOT = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001")
RAW = ROOT / "raw"
SCENE = PARENT / "scene/unitree_g1_hfield"
OUTPUT_FIELDS = ("qacc", "qfrc_constraint", "solver_niter", "overflow", "efc.force", "efc.Ma", "nefc")


def output_view(data):
    arrays = enumerate_data_arrays(data)
    out = {field: arrays[field].numpy().copy() for field in OUTPUT_FIELDS}
    count = out["nefc"]
    force = out["efc.force"]
    out["efc.force_valid_concat"] = np.concatenate([force[world, :int(n)] for world, n in enumerate(count)])
    return out


def output_from_record(record):
    by_path = {row["field_path"]: row for row in record["manifest"]}
    with np.load(record["path"], allow_pickle=False) as archive:
        out = {field: archive[by_path[field]["key"]].copy() for field in OUTPUT_FIELDS}
    count = out["nefc"]
    force = out["efc.force"]
    out["efc.force_valid_concat"] = np.concatenate([force[world, :int(n)] for world, n in enumerate(count)])
    return out


def numeric_pair(reference, observed):
    fields = {}
    for key in OUTPUT_FIELDS + ("efc.force_valid_concat",):
        left = reference[key]
        right = observed[key]
        if left.shape != right.shape:
            fields[key] = {"shape_equal": False}
            continue
        equal = bool(np.array_equal(left, right))
        row = {"shape_equal": True, "bitwise_equal": sha_numpy(left) == sha_numpy(right), "array_equal": equal,
               "reference_sha256": sha_numpy(left), "observed_sha256": sha_numpy(right)}
        if np.issubdtype(left.dtype, np.floating):
            delta = right.astype(np.float64) - left.astype(np.float64)
            row["max_abs"] = float(np.max(np.abs(delta))) if delta.size else 0.0
            row["mean_abs"] = float(np.mean(np.abs(delta))) if delta.size else 0.0
            row["rms"] = float(np.sqrt(np.mean(delta * delta))) if delta.size else 0.0
            row["finite_both"] = bool(np.isfinite(left).all() and np.isfinite(right).all())
        else:
            row["different_worlds_or_elements"] = int(np.count_nonzero(left != right))
        fields[key] = row
    return fields


def main():
    assert os.environ.get("R20R1_GPU_LOCK_HELD") == "1"
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    import mujoco_warp as mjw
    from mujoco_warp._src import solver
    from mujoco_warp._src.io import load_trajectory, override_model
    from mujoco_warp._src.types import OverflowType

    g0 = json.loads((RAW / "G0_T128_SOLVER_ENTRY_RECEIPT.json").read_text())
    entry = g0["entry_snapshot"]
    exit_original = output_from_record(g0["exit_snapshot"])
    scene_receipt = json.loads((PARENT / "raw/SCENE_MODEL_RECEIPT.json").read_text())
    assert file_sha(SCENE / "scene_hfield.xml") == scene_receipt["scene_xml_sha256"]
    device = wp.get_device("cuda:0")
    mjm = mujoco.MjSpec.from_file(str(SCENE / "scene_hfield.xml")).compile()
    mjd = mujoco.MjData(mjm)
    assert len(load_trajectory(str(SCENE / "shuffle_dance.npz"), mjm, mjd)) == 1000
    with wp.ScopedDevice(device):
        model = mjw.put_model(mjm)
        override_model(model, ["opt.warn_overflow=~ITERATIONS|~LS_ITERATIONS"])
        data = mjw.put_data(mjm, mjd, nworld=1024, nconmax=48, njmax=192)
        assert model.opt.graph_conditional and model.is_sparse and int(model.opt.iterations) == 10
        expected_model = {row["path"]: row for row in json.loads((RAW / "G0_MODEL_ARRAY_MANIFEST.json").read_text())}
        actual_model = enumerate_data_arrays(model)
        if set(expected_model) != set(actual_model):
            raise RuntimeError("Model array field set differs from in-situ capture")
        for path, array in actual_model.items():
            if sha_numpy(array.numpy()) != expected_model[path]["sha256"]:
                raise RuntimeError(f"Model byte identity differs at {path}")
        print("R20R1_PHASE_MODEL_IDENTITY_OK", flush=True)

        original_make_ctx = solver._create_solver_context
        original_capture_while = wp.capture_while
        contexts = []
        conditional = []

        def context_witness(m, d):
            ctx = original_make_ctx(m, d)
            contexts.append(ctx)
            return ctx

        def while_witness(*args, **kwargs):
            conditional.append(bool(device.captures) and args[0].device.is_cuda)
            return original_capture_while(*args, **kwargs)

        solver._create_solver_context = context_witness
        wp.capture_while = while_witness
        try:
            print("R20R1_PHASE_ISOLATED_CAPTURE_BEGIN", flush=True)
            t0 = time.perf_counter()
            with wp.ScopedCapture() as graph:
                solver.solve(model, data)
            wp.synchronize()
            capture_seconds_not_primary = time.perf_counter() - t0
            print("R20R1_PHASE_ISOLATED_CAPTURE_COMPLETE", flush=True)
        finally:
            solver._create_solver_context = original_make_ctx
            wp.capture_while = original_capture_while
        if len(contexts) != 1 or conditional != [True]:
            raise RuntimeError(f"Complete solver graph/context not captured once: {len(contexts)}, {conditional}")
        ctx = contexts[0]
        context_arrays = enumerate_data_arrays(ctx)
        context_manifest = [{"path": path, "shape": list(array.shape), "dtype": str(array.dtype),
                             "device_ptr_hex": hex(int(array.ptr)), "capture_owned_bytes": "NOT_READ_BEFORE_GRAPH_REPLAY"}
                            for path, array in context_arrays.items()]
        print("R20R1_PHASE_CONTEXT_AUDIT_COMPLETE", flush=True)
        (RAW / "SOLVER_CONTEXT_ARRAY_AUDIT.json").write_text(json.dumps(context_manifest, indent=2, sort_keys=True) + "\n")

        restore_recorded_snapshot(data, entry)
        print("R20R1_PHASE_ENTRY_RESTORE_COMPLETE", flush=True)
        entry_gpu = {path: wp.empty_like(array) for path, array in enumerate_data_arrays(data).items()}
        for path, array in enumerate_data_arrays(data).items():
            wp.copy(entry_gpu[path], array)
        wp.synchronize()

        def restore_for_run(target):
            target_fields = enumerate_data_arrays(target)
            if set(target_fields) != set(entry_gpu):
                raise RuntimeError("Solver-entry Data field set differs on restore")
            for path, source in entry_gpu.items():
                wp.copy(target_fields[path], source)
            wp.synchronize()
            # Full 138-field byte identity, not merely qpos/qvel.
            for row in entry["manifest"]:
                if sha_numpy(target_fields[row["field_path"]].numpy()) != row["sha256"]:
                    raise RuntimeError(f"Solver input bytes changed before B0 at {row['field_path']}")

        outputs = []
        timing_not_primary = []
        for repeat in range(5):
            print(f"R20R1_PHASE_REPEAT_BEGIN_{repeat}", flush=True)
            restore_for_run(data)
            t0 = time.perf_counter()
            wp.capture_launch(graph.graph)
            wp.synchronize()
            timing_not_primary.append((time.perf_counter() - t0) * 1000)
            result = output_view(data)
            outputs.append(result)
            print(f"R20R1_PHASE_REPEAT_COMPLETE_{repeat}", flush=True)
        fresh_data = mjw.put_data(mjm, mjd, nworld=1024, nconmax=48, njmax=192)
        print("R20R1_PHASE_FRESH_CAPTURE_BEGIN", flush=True)
        with wp.ScopedCapture() as fresh_graph:
            solver.solve(model, fresh_data)
        print("R20R1_PHASE_FRESH_CAPTURE_COMPLETE", flush=True)
        restore_for_run(fresh_data)
        wp.capture_launch(fresh_graph.graph)
        wp.synchronize()
        fresh_output = output_view(fresh_data)
        outputs.append(fresh_output)
        np.savez_compressed(RAW / "B0_T128_SOLVER_REPEAT_OUTPUTS.npz", **{
            f"run_{index}_{field.replace('.', '_')}": value
            for index, result in enumerate(outputs)
            for field, value in result.items()
        })
        reference = outputs[0]
        compare_to_first = [numeric_pair(reference, result) for result in outputs[1:]]
        compare_in_situ = [numeric_pair(exit_original, result) for result in outputs]
        iteration_equal = all(pair["solver_niter"]["bitwise_equal"] for pair in compare_to_first)
        overflow_equal = all(pair["overflow"]["bitwise_equal"] for pair in compare_to_first)
        nefc_equal = all(pair["nefc"]["bitwise_equal"] for pair in compare_to_first)
        effective_outputs_bitwise = all(all(pair[key]["bitwise_equal"] for key in
                                           ("qacc", "qfrc_constraint", "efc.force_valid_concat", "efc.Ma"))
                                       for pair in compare_to_first)
        inputs_overflow = entry_gpu["overflow"].numpy()
        new_bits = reference["overflow"] & ~inputs_overflow
        capacity_mask = int(OverflowType.ALL) & ~(int(OverflowType.ITERATIONS) | int(OverflowType.LS_ITERATIONS))
        if np.count_nonzero(new_bits & capacity_mask):
            raise RuntimeError("New true capacity overflow appeared in isolated solver")
        if not all(np.isfinite(result["qacc"]).all() and np.isfinite(result["qfrc_constraint"]).all()
                   and np.isfinite(result["efc.force_valid_concat"]).all() and np.isfinite(result["efc.Ma"]).all()
                   for result in outputs):
            raise RuntimeError("Nonfinite effective solver output")
        receipt = {
            "stage": "AWMA_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_V1",
            "classification": "FIXED_T128_SOLVER_ENTRY_B0_FIVE_REPEATS_PLUS_FRESH_GRAPH",
            "source_commit": g0["source_commit"],
            "solver_entry_sha256": entry["sha256"],
            "in_situ_exit_sha256": g0["exit_snapshot"]["sha256"],
            "same_model_array_count_and_hashes": len(expected_model),
            "same_full_input_data_fields_and_hashes_per_run": entry["field_count"],
            "isolated_graph_conditional_node_witness": conditional,
            "isolated_complete_solver_graph_captured_once": True,
            "capture_seconds_not_primary": capture_seconds_not_primary,
            "observer_replay_ms_not_formal": timing_not_primary,
            "context_array_field_count": len(context_manifest),
            "context_array_after_each_run_sha256": "NOT_READ_FROM_CAPTURE_OWNED_SCRATCH; source initialization and repeatability audited separately",
            "repeated_outputs_raw_sha256": file_sha(RAW / "B0_T128_SOLVER_REPEAT_OUTPUTS.npz"),
            "comparison_to_first_run": compare_to_first,
            "comparison_in_situ_exit_to_each_isolated_run": compare_in_situ,
            "solver_niter_bitwise_stable": iteration_equal,
            "overflow_bitwise_stable": overflow_equal,
            "nefc_bitwise_stable": nefc_equal,
            "effective_solver_outputs_bitwise_stable": effective_outputs_bitwise,
            "entry_overflow_or": int(np.bitwise_or.reduce(inputs_overflow.reshape(-1))),
            "new_overflow_or_first_run": int(np.bitwise_or.reduce(new_bits.reshape(-1))),
            "new_capacity_overflow_worlds": 0,
            "true_tolerance_convergence_reason": "UNKNOWN_WHEN_ALPHA_ZERO_OR_LIMIT; niter/overflow are the available signatures",
        }
        (RAW / "B0_T128_REPEATABILITY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        with (RAW / "B0_REPEATABILITY.tsv").open("w", newline="", encoding="utf-8") as stream:
            keys = ("run", "graph", "solver_niter_bitwise", "overflow_bitwise", "nefc_bitwise",
                    "qacc_bitwise", "qacc_max_abs", "qfrc_constraint_bitwise", "qfrc_constraint_max_abs",
                    "efc_force_valid_bitwise", "efc_force_valid_max_abs", "efc_Ma_bitwise", "efc_Ma_max_abs")
            writer = csv.DictWriter(stream, fieldnames=keys, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            for index, pair in enumerate(compare_to_first, start=1):
                writer.writerow({
                    "run": index,
                    "graph": "fresh" if index == 5 else "same",
                    "solver_niter_bitwise": pair["solver_niter"]["bitwise_equal"],
                    "overflow_bitwise": pair["overflow"]["bitwise_equal"],
                    "nefc_bitwise": pair["nefc"]["bitwise_equal"],
                    "qacc_bitwise": pair["qacc"]["bitwise_equal"],
                    "qacc_max_abs": pair["qacc"]["max_abs"],
                    "qfrc_constraint_bitwise": pair["qfrc_constraint"]["bitwise_equal"],
                    "qfrc_constraint_max_abs": pair["qfrc_constraint"]["max_abs"],
                    "efc_force_valid_bitwise": pair["efc.force_valid_concat"]["bitwise_equal"],
                    "efc_force_valid_max_abs": pair["efc.force_valid_concat"]["max_abs"],
                    "efc_Ma_bitwise": pair["efc.Ma"]["bitwise_equal"],
                    "efc_Ma_max_abs": pair["efc.Ma"]["max_abs"],
                })
        print(json.dumps({key: receipt[key] for key in (
            "solver_entry_sha256", "context_array_field_count", "solver_niter_bitwise_stable",
            "overflow_bitwise_stable", "nefc_bitwise_stable", "effective_solver_outputs_bitwise_stable",
            "new_capacity_overflow_worlds",
        )}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        import traceback
        traceback.print_exc()
        raise
