#!/usr/bin/env python3
"""Capture first real t128 solver entry/exit inside the original full B0 step."""

import csv
import hashlib
import json
import os
import time
from pathlib import Path

import mujoco
import numpy as np
import warp as wp

from snapshot_io import (
    allocate_data_buffers, file_sha, record_data_copy, restore_parent_data,
    sha_numpy, snapshot_to_npz,
)


PARENT = Path("/data/c16/awma/r20_active_world_native_v1")
ROOT = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001")
RAW = ROOT / "raw"
SCENE = PARENT / "scene/unitree_g1_hfield"
EXPECTED_PARENT_STATE = "17f59a5ebbedff9e544eb7c35cede114c3f9ec97b9b26d0ddfd363370bbcf6e3"


def main():
    assert os.environ.get("R20R1_GPU_LOCK_HELD") == "1"
    assert file_sha(PARENT / "raw/DISCOVERY_ENTRY_FULL_DATA.npz") == EXPECTED_PARENT_STATE
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    import mujoco_warp as mjw
    from mujoco_warp._src import solver
    from mujoco_warp._src.cli import _ctrl_noise
    from mujoco_warp._src.io import load_trajectory, override_model
    from mujoco_warp._src.types import OverflowType

    scene_receipt = json.loads((PARENT / "raw/SCENE_MODEL_RECEIPT.json").read_text())
    device = wp.get_device("cuda:0")
    mjm = mujoco.MjSpec.from_file(str(SCENE / "scene_hfield.xml")).compile()
    mjd = mujoco.MjData(mjm)
    centers = load_trajectory(str(SCENE / "shuffle_dance.npz"), mjm, mjd)
    assert len(centers) == 1000
    assert file_sha(SCENE / "scene_hfield.xml") == scene_receipt["scene_xml_sha256"]
    with wp.ScopedDevice(device):
        model = mjw.put_model(mjm)
        override_model(model, ["opt.warn_overflow=~ITERATIONS|~LS_ITERATIONS"])
        data = mjw.put_data(mjm, mjd, nworld=1024, nconmax=48, njmax=192)
        assert model.opt.graph_conditional and model.is_sparse
        assert int(model.opt.iterations) == 10 and int(model.opt.ls_iterations) == 20
        entry_buffers = allocate_data_buffers(data)
        exit_buffers = allocate_data_buffers(data)
        source_solve = solver.solve
        source_capture_while = wp.capture_while
        solve_calls = []
        while_calls = []

        def solver_witness(m, d):
            if d is not data or m is not model:
                raise RuntimeError("Solver received an unexpected model/Data identity")
            solve_calls.append("BEFORE_SOLVER")
            record_data_copy(d, entry_buffers)
            source_solve(m, d)
            record_data_copy(d, exit_buffers)
            solve_calls.append("AFTER_SOLVER")

        def while_witness(*args, **kwargs):
            while_calls.append(bool(device.captures) and args[0].device.is_cuda)
            return source_capture_while(*args, **kwargs)

        solver.solve = solver_witness
        wp.capture_while = while_witness
        try:
            start = time.perf_counter()
            with wp.ScopedCapture() as in_situ_capture:
                mjw.step(model, data)
            wp.synchronize()
            capture_seconds_not_primary = time.perf_counter() - start
        finally:
            solver.solve = source_solve
            wp.capture_while = source_capture_while
        if solve_calls != ["BEFORE_SOLVER", "AFTER_SOLVER"]:
            raise RuntimeError(f"Original full step did not call the expected one complete solve: {solve_calls}")
        if not while_calls or not all(while_calls):
            raise RuntimeError(f"Original solve did not insert a CUDA conditional while node: {while_calls}")

        parent_manifest = restore_parent_data(data, PARENT / "raw", EXPECTED_PARENT_STATE)
        center = wp.array(centers[128], dtype=wp.float32, device=device)
        wp.launch(
            _ctrl_noise,
            dim=(data.nworld, model.nu),
            inputs=[model.opt.timestep, model.actuator_ctrllimited, model.actuator_ctrlrange,
                    data.ctrl, center, 128, 0.01, 0.1],
            outputs=[data.ctrl],
        )
        wp.synchronize()
        ctrl = data.ctrl.numpy()
        actual_ctrl_sha = sha_numpy(ctrl)
        with (PARENT / "raw/ACTIVITY_AND_CAPACITY.tsv").open() as stream:
            first = next(csv.DictReader(stream, delimiter="\t"))
        assert int(first["step"]) == 128
        if actual_ctrl_sha != first["ctrl_sha256"]:
            raise RuntimeError("Actual t128 control differs from the accepted R20 original control rule")

        wp.capture_launch(in_situ_capture.graph)
        wp.synchronize()
        entry_path = RAW / "G0_T128_IN_SITU_SOLVER_ENTRY_FULL_DATA.npz"
        exit_path = RAW / "G0_T128_IN_SITU_SOLVER_EXIT_FULL_DATA.npz"
        entry = snapshot_to_npz(entry_buffers, entry_path)
        exit_ = snapshot_to_npz(exit_buffers, exit_path)
        input_arrays = {row["field_path"]: row for row in entry["manifest"]}
        output_arrays = {row["field_path"]: row for row in exit_["manifest"]}
        if set(input_arrays) != set(output_arrays):
            raise RuntimeError("Entry/exit Data field sets differ")
        selected_inputs = (
            "qpos", "qvel", "act", "history", "qacc_warmstart", "ctrl", "time",
            "nefc", "nacon", "contact.worldid", "contact.geom", "contact.pos", "contact.dist",
            "contact.frame", "contact.friction", "contact.solref", "contact.solimp",
            "contact.efc_address", "efc.type", "efc.id", "efc.J", "efc.J_rownnz",
            "efc.J_rowadr", "efc.J_colind", "efc.D", "efc.aref", "efc.force", "efc.Ma",
            "M", "qLD", "qfrc_smooth", "qacc_smooth", "tree_awake", "body_awake",
            "dof_cdof", "cdof_dof", "ctol", "cls_tol", "overflow",
        )
        selected_entry = {key: input_arrays[key]["sha256"] for key in selected_inputs if key in input_arrays}
        selected_exit = {key: output_arrays[key]["sha256"] for key in (
            "qacc", "qfrc_constraint", "solver_niter", "overflow", "efc.force", "efc.Ma",
            "qacc_warmstart", "qpos", "qvel", "nefc",
        ) if key in output_arrays}
        niter = exit_buffers["solver_niter"].numpy()
        nefc = entry_buffers["nefc"].numpy()
        entry_overflow = entry_buffers["overflow"].numpy()
        exit_overflow = exit_buffers["overflow"].numpy()
        new_overflow = exit_overflow & ~entry_overflow
        capacity_mask = int(OverflowType.ALL) & ~(int(OverflowType.ITERATIONS) | int(OverflowType.LS_ITERATIONS))
        qacc = exit_buffers["qacc"].numpy()
        qfrc = exit_buffers["qfrc_constraint"].numpy()
        if not np.isfinite(qacc).all() or not np.isfinite(qfrc).all():
            raise RuntimeError("Nonfinite in-situ solver exit")

        model_manifest = []
        from snapshot_io import enumerate_data_arrays
        for path, array in enumerate_data_arrays(model).items():
            value = array.numpy()
            model_manifest.append({"path": path, "shape": list(array.shape), "dtype": str(array.dtype), "sha256": sha_numpy(value), "bytes": value.nbytes})
        (RAW / "G0_MODEL_ARRAY_MANIFEST.json").write_text(json.dumps(model_manifest, indent=2, sort_keys=True) + "\n")
        receipt = {
            "stage": "AWMA_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_V1",
            "classification": "NEW_B0_REALIZATION_FROM_ACCEPTED_T128_STEP_ENTRY_NOT_PARENT_BITWISE_HISTORICAL_STEP",
            "source_commit": "3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5",
            "source_solver_blob": "090061796792f4d11408eaa69b4ef3c44465c705",
            "parent_t128_step_entry_sha256": EXPECTED_PARENT_STATE,
            "parent_manifest_field_count": parent_manifest["data_array_field_count"],
            "actual_ctrl_step128_sha256": actual_ctrl_sha,
            "step_index": 128,
            "nworld": data.nworld,
            "solver_callpoint": "mujoco_warp._src.forward.forward -> solver.solve(m,d) before implicitfast integrator",
            "one_complete_original_solver_call_seen_during_graph_capture": True,
            "conditional_while_node_cuda_capture_witness": while_calls,
            "capture_seconds_not_primary": capture_seconds_not_primary,
            "solver": str(model.opt.solver),
            "cone": str(model.opt.cone),
            "is_sparse": bool(model.is_sparse),
            "graph_conditional": bool(model.opt.graph_conditional),
            "iterations": int(model.opt.iterations),
            "ls_iterations": int(model.opt.ls_iterations),
            "tolerance": float(model.opt.tolerance.numpy().reshape(-1)[0]),
            "ls_tolerance": float(model.opt.ls_tolerance.numpy().reshape(-1)[0]),
            "enableflags": int(model.opt.enableflags),
            "disableflags": int(model.opt.disableflags),
            "naconmax_pooled": data.naconmax,
            "njmax_per_world": data.njmax,
            "njmax_nnz": data.njmax_nnz,
            "entry_snapshot": entry,
            "exit_snapshot": exit_,
            "selected_effective_input_full_array_sha256": selected_entry,
            "selected_solver_output_full_array_sha256": selected_exit,
            "model_array_manifest_sha256": file_sha(RAW / "G0_MODEL_ARRAY_MANIFEST.json"),
            "model_array_count": len(model_manifest),
            "nefc_min_max": [int(nefc.min()), int(nefc.max())],
            "solver_niter_min_max": [int(niter.min()), int(niter.max())],
            "entry_overflow_or": int(np.bitwise_or.reduce(entry_overflow.reshape(-1))),
            "new_overflow_or": int(np.bitwise_or.reduce(new_overflow.reshape(-1))),
            "new_capacity_overflow_worlds": int(np.count_nonzero(new_overflow & capacity_mask)),
            "output_qacc_all_finite": True,
            "output_qfrc_constraint_all_finite": True,
        }
        (RAW / "G0_T128_SOLVER_ENTRY_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(json.dumps({key: receipt[key] for key in (
            "classification", "entry_snapshot", "exit_snapshot", "model_array_count", "nefc_min_max",
            "solver_niter_min_max", "new_overflow_or", "new_capacity_overflow_worlds",
        ) if key not in ("entry_snapshot", "exit_snapshot")}, sort_keys=True))
        print(json.dumps({"entry_sha256": entry["sha256"], "exit_sha256": exit_["sha256"], "entry_fields": entry["field_count"], "exit_fields": exit_["field_count"]}, sort_keys=True))


if __name__ == "__main__":
    main()
