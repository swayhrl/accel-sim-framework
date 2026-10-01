#!/usr/bin/env python3
"""Predeclared continuous original-B0 fallback lineage for t128/136/144/152."""

import csv
import json
import os
from pathlib import Path

import mujoco
import numpy as np
import warp as wp

from snapshot_io import allocate_data_buffers, file_sha, record_data_copy, restore_parent_data, sha_numpy, snapshot_to_npz


PARENT = Path("/data/c16/awma/r20_active_world_native_v1")
ROOT = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001")
RAW = ROOT / "raw"
SCENE = PARENT / "scene/unitree_g1_hfield"
PARENT_T128_STEP_SHA = "17f59a5ebbedff9e544eb7c35cede114c3f9ec97b9b26d0ddfd363370bbcf6e3"
SELECTED = (128, 136, 144, 152)


def main():
    assert os.environ.get("R20R1_GPU_LOCK_HELD") == "1"
    assert file_sha(PARENT / "raw/DISCOVERY_ENTRY_FULL_DATA.npz") == PARENT_T128_STEP_SHA
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    import mujoco_warp as mjw
    from mujoco_warp._src import solver
    from mujoco_warp._src.cli import _ctrl_noise
    from mujoco_warp._src.io import load_trajectory, override_model
    from mujoco_warp._src.types import OverflowType

    device = wp.get_device("cuda:0")
    mjm = mujoco.MjSpec.from_file(str(SCENE / "scene_hfield.xml")).compile()
    mjd = mujoco.MjData(mjm)
    centers = load_trajectory(str(SCENE / "shuffle_dance.npz"), mjm, mjd)
    assert len(centers) == 1000
    parent_ctrl = {}
    with (PARENT / "raw/ACTIVITY_AND_CAPACITY.tsv").open() as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            if int(row["step"]) in SELECTED:
                parent_ctrl[int(row["step"])] = row["ctrl_sha256"]
    assert set(parent_ctrl) == set(SELECTED)

    with wp.ScopedDevice(device):
        model = mjw.put_model(mjm)
        override_model(model, ["opt.warn_overflow=~ITERATIONS|~LS_ITERATIONS"])
        data = mjw.put_data(mjm, mjd, nworld=1024, nconmax=48, njmax=192)
        entry_buffers = allocate_data_buffers(data)
        exit_buffers = allocate_data_buffers(data)
        source_solve = solver.solve
        calls = []

        def witness(m, d):
            if m is not model or d is not data:
                raise RuntimeError("Continuous B0 lineage changed solver model/Data identity")
            calls.append("solve")
            record_data_copy(d, entry_buffers)
            source_solve(m, d)
            record_data_copy(d, exit_buffers)

        solver.solve = witness
        try:
            with wp.ScopedCapture() as graph:
                mjw.step(model, data)
        finally:
            solver.solve = source_solve
        if calls != ["solve"]:
            raise RuntimeError(f"Expected one original solver call: {calls}")
        restore_parent_data(data, PARENT / "raw", PARENT_T128_STEP_SHA)
        capacity_mask = int(OverflowType.ALL) & ~(int(OverflowType.ITERATIONS) | int(OverflowType.LS_ITERATIONS))
        rows = []
        for step in range(128, 153):
            center = wp.array(centers[step], dtype=wp.float32, device=device)
            wp.launch(
                _ctrl_noise, dim=(data.nworld, model.nu),
                inputs=[model.opt.timestep, model.actuator_ctrllimited, model.actuator_ctrlrange,
                        data.ctrl, center, step, 0.01, 0.1], outputs=[data.ctrl],
            )
            wp.synchronize()
            ctrl_sha = sha_numpy(data.ctrl.numpy())
            if step in SELECTED and ctrl_sha != parent_ctrl[step]:
                raise RuntimeError(f"Original control rule diverged at predeclared step {step}")
            wp.capture_launch(graph.graph)
            wp.synchronize()
            overflow = data.overflow.numpy()
            if np.count_nonzero(overflow & capacity_mask):
                raise RuntimeError(f"True capacity overflow in B0 lineage at step {step}")
            if step not in SELECTED:
                continue
            entry = snapshot_to_npz(entry_buffers, RAW / f"R2_T{step}_SOLVER_ENTRY_FULL_DATA.npz")
            exit_ = snapshot_to_npz(exit_buffers, RAW / f"R2_T{step}_SOLVER_EXIT_FULL_DATA.npz")
            niter = exit_buffers["solver_niter"].numpy()
            nefc = entry_buffers["nefc"].numpy()
            input_overflow = entry_buffers["overflow"].numpy()
            new_overflow = exit_buffers["overflow"].numpy() & ~input_overflow
            row = {
                "step": step,
                "ctrl_sha256": ctrl_sha,
                "entry_snapshot": entry,
                "exit_snapshot": exit_,
                "nefc_min_max": [int(nefc.min()), int(nefc.max())],
                "solver_niter_min_max": [int(niter.min()), int(niter.max())],
                "new_overflow_or": int(np.bitwise_or.reduce(new_overflow.reshape(-1))),
                "new_capacity_overflow_worlds": int(np.count_nonzero(new_overflow & capacity_mask)),
                "post_step_qpos_sha256": sha_numpy(data.qpos.numpy()),
                "post_step_qvel_sha256": sha_numpy(data.qvel.numpy()),
            }
            rows.append(row)
            print(json.dumps({"step": step, "entry_sha256": entry["sha256"], "exit_sha256": exit_["sha256"],
                              "niter": row["solver_niter_min_max"], "nefc": row["nefc_min_max"]}, sort_keys=True), flush=True)
        receipt = {
            "stage": "AWMA_R20R1_SOLVER_ENTRY_LOCAL_CONTRACT_109_V1",
            "classification": "ONE_NEW_CONTINUOUS_ORIGINAL_B0_REALIZATION_FROM_ACCEPTED_T128_STEP_INPUT_NOT_SELECTED_BY_OUTPUT_OR_SPEED",
            "parent_t128_step_entry_sha256": PARENT_T128_STEP_SHA,
            "first_G0_solver_entry_sha256_historical_separate_realization": "239a58956b70bd738902fb1b8f55cb92e79445ebe3435078165437b187ef1f3b",
            "fallback_reason": "first G0 process did not retain post-integrator t129 Data; this predeclared new lineage must requalify t128",
            "source_commit": "3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5",
            "batch": 1024,
            "selected_steps_predeclared": list(SELECTED),
            "full_original_step_graph_captured_once": True,
            "full_step_graph_replays_t128_through_t152": 25,
            "all_selected_actual_ctrl_equal_parent_rule": True,
            "entrances": rows,
        }
        (RAW / "R2_DISCOVERY_ENTRY_LINEAGE.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"entry_steps": [row["step"] for row in rows],
                          "entry_hashes": [row["entry_snapshot"]["sha256"] for row in rows]}, sort_keys=True))


if __name__ == "__main__":
    main()
