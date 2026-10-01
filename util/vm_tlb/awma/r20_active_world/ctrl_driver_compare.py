#!/usr/bin/env python3
"""B16-only original cli.unroll versus R20 runner actual control identity."""

import hashlib
import json
import os
from pathlib import Path

import mujoco
import numpy as np
import warp as wp
from absl import flags


ROOT = Path("/data/c16/awma/r20_active_world_native_v1")
SCENE = ROOT / "scene/unitree_g1_hfield"
RAW = ROOT / "raw"


def sha(value):
    return hashlib.sha256(np.ascontiguousarray(value).view(np.uint8).tobytes()).hexdigest()


def main():
    assert os.environ.get("R20_GPU_LOCK_HELD") == "1"
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    import mujoco_warp as mjw
    from mujoco_warp._src import cli
    from mujoco_warp._src.io import load_trajectory, override_model

    if not flags.FLAGS.is_parsed():
        flags.FLAGS(["r20_ctrl_compare", "--nstep=4", "--nworld=16", "--device=cuda:0", "--noise_std=0.01", "--noise_rate=0.1"])
    device = wp.get_device("cuda:0")
    model_cpu = mujoco.MjSpec.from_file(str(SCENE / "scene_hfield.xml")).compile()
    initial_cpu = mujoco.MjData(model_cpu)
    ctrls = load_trajectory(str(SCENE / "shuffle_dance.npz"), model_cpu, initial_cpu)
    assert len(ctrls) == 1000
    with wp.ScopedDevice(device):
        model = mjw.put_model(model_cpu)
        override_model(model, ["opt.warn_overflow=~ITERATIONS|~LS_ITERATIONS"])
        original_data = mjw.put_data(model_cpu, initial_cpu, nworld=16, nconmax=48, njmax=192)
        candidate_data = mjw.put_data(model_cpu, initial_cpu, nworld=16, nconmax=48, njmax=192)
        original_actual = []

        def callback(step, _trace, _latency):
            original_actual.append(original_data.ctrl.numpy().copy())
            assert len(original_actual) == step + 1

        cli.unroll(mjw.step, model, original_data, None, callback=callback, ctrls=ctrls)
        assert len(original_actual) == 4
        with wp.ScopedCapture() as capture:
            mjw.step(model, candidate_data)
        candidate_actual = []
        for step in range(4):
            center = wp.array(ctrls[step], dtype=wp.float32, device=device)
            wp.launch(
                cli._ctrl_noise,
                dim=(candidate_data.nworld, model.nu),
                inputs=[model.opt.timestep, model.actuator_ctrllimited, model.actuator_ctrlrange,
                        candidate_data.ctrl, center, step, 0.01, 0.1],
                outputs=[candidate_data.ctrl],
            )
            wp.synchronize()
            wp.capture_launch(capture.graph)
            wp.synchronize()
            candidate_actual.append(candidate_data.ctrl.numpy().copy())
        rows = []
        for step in range(4):
            old = original_actual[step]
            new = candidate_actual[step]
            rows.append({
                "step": step,
                "original_cli_actual_ctrl_sha256": sha(old),
                "r20_runner_actual_ctrl_sha256": sha(new),
                "center_sha256": sha(ctrls[step]),
                "actual_ctrl_bitwise_equal": bool(np.array_equal(old, new)),
                "actual_ctrl_differs_from_center": not np.array_equal(old[0], ctrls[step]),
                "unique_world_ctrl_rows": int(np.unique(new, axis=0).shape[0]),
            })
        assert all(row["actual_ctrl_bitwise_equal"] for row in rows)
        assert all(row["actual_ctrl_differs_from_center"] for row in rows)
        result = {
            "stage": "AWMA_R20_ACTIVE_WORLD_NATIVE_109_V1",
            "classification": "B16_ENGINEERING_CONTROL_AUTHORITY_ONLY",
            "source": "mujoco_warp/_src/cli.py::_ctrl_noise and cli.unroll at 3d537ea",
            "noise_std": 0.01,
            "noise_rate": 0.1,
            "original_runner_steps": 4,
            "candidate_runner_steps": 4,
            "all_actual_controls_bitwise_identical": True,
            "rows": rows,
        }
        (RAW / "CONTROL_DRIVER_IDENTITY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
