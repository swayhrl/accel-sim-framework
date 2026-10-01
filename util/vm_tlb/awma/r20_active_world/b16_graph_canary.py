#!/usr/bin/env python3
"""B16 engineering-only canary for exact MuJoCo Warp conditional graph."""

import hashlib
import json
import os
import time
from pathlib import Path

import mujoco
import numpy as np
import warp as wp


ROOT = Path("/data/c16/awma/r20_active_world_native_v1")
SCENE = ROOT / "scene/unitree_g1_hfield"
RAW = ROOT / "raw"
SOURCE = ROOT / "source/mujoco_warp"


def array_sha(value):
    return hashlib.sha256(np.ascontiguousarray(value).view(np.uint8).tobytes()).hexdigest()


def main():
    assert os.environ.get("R20_GPU_LOCK_HELD") == "1"
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    import mujoco_warp as mjw
    from mujoco_warp._src.cli import _ctrl_noise
    from mujoco_warp._src.io import load_trajectory, override_model

    device = wp.get_device("cuda:0")
    model_cpu = mujoco.MjSpec.from_file(str(SCENE / "scene_hfield.xml")).compile()
    state_cpu = mujoco.MjData(model_cpu)
    centers = load_trajectory(str(SCENE / "shuffle_dance.npz"), model_cpu, state_cpu)
    assert len(centers) == 1000
    with wp.ScopedDevice(device):
        model = mjw.put_model(model_cpu)
        override_model(model, ["opt.warn_overflow=~ITERATIONS|~LS_ITERATIONS"])
        data = mjw.put_data(model_cpu, state_cpu, nworld=16, nconmax=48, njmax=192)
        observed_capture_while = []
        original_capture_while = wp.capture_while

        def capture_while_witness(*args, **kwargs):
            observed_capture_while.append({
                "condition_device": str(args[0].device) if args else "UNKNOWN",
                "outer_capture_active": bool(device.captures),
            })
            return original_capture_while(*args, **kwargs)

        wp.capture_while = capture_while_witness
        try:
            capture_begin = time.perf_counter()
            with wp.ScopedCapture() as capture:
                mjw.step(model, data)
            wp.synchronize()
            capture_seconds = time.perf_counter() - capture_begin
        finally:
            wp.capture_while = original_capture_while
        assert observed_capture_while, "No capture_while inserted during graph capture"
        assert all(item["outer_capture_active"] for item in observed_capture_while)
        assert model.opt.graph_conditional

        center = wp.array(centers[0], dtype=wp.float32, device=device)
        wp.launch(
            _ctrl_noise,
            dim=(data.nworld, model.nu),
            inputs=[
                model.opt.timestep,
                model.actuator_ctrllimited,
                model.actuator_ctrlrange,
                data.ctrl,
                center,
                0,
                0.01,
                0.1,
            ],
            outputs=[data.ctrl],
        )
        wp.synchronize()
        ctrl = data.ctrl.numpy()
        assert ctrl.shape == (16, model.nu)
        assert np.all(np.isfinite(ctrl))
        replay_begin = time.perf_counter()
        wp.capture_launch(capture.graph)
        wp.synchronize()
        replay_seconds = time.perf_counter() - replay_begin
        niter = data.solver_niter.numpy()
        nefc = data.nefc.numpy()
        overflow = data.overflow.numpy()
        qpos = data.qpos.numpy()
        qvel = data.qvel.numpy()
        assert np.all(np.isfinite(qpos)) and np.all(np.isfinite(qvel))
        result = {
            "stage": "AWMA_R20_ACTIVE_WORLD_NATIVE_109_V1",
            "classification": "ENGINEERING_CANARY_NOT_SCIENTIFIC_WORKPOINT",
            "source_commit": "3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5",
            "scene_sha256": hashlib.sha256((SCENE / "scene_hfield.xml").read_bytes()).hexdigest(),
            "trajectory_sha256": hashlib.sha256((SCENE / "shuffle_dance.npz").read_bytes()).hexdigest(),
            "mujoco_package_version": mujoco.__version__,
            "warp_version": wp.__version__,
            "device": str(device),
            "device_arch": int(device.arch),
            "nworld": data.nworld,
            "requested_nconmax_per_world": 48,
            "actual_naconmax_pooled": data.naconmax,
            "njmax": data.njmax,
            "model_solver": str(model.opt.solver),
            "model_cone": str(model.opt.cone),
            "model_iterations": int(model.opt.iterations),
            "model_ls_iterations": int(model.opt.ls_iterations),
            "model_graph_conditional": bool(model.opt.graph_conditional),
            "model_tolerance": float(model.opt.tolerance.numpy().reshape(-1)[0]),
            "capture_while_witness": observed_capture_while,
            "graph_captured_once": True,
            "graph_replayed": True,
            "capture_seconds_not_primary": capture_seconds,
            "replay_seconds_not_primary": replay_seconds,
            "control_step0_sha256": array_sha(ctrl),
            "control_step0_unique_world_rows": int(np.unique(ctrl, axis=0).shape[0]),
            "control_center_step0_sha256": array_sha(centers[0]),
            "solver_niter_min_max": [int(niter.min()), int(niter.max())],
            "solver_niter_nonzero": int(np.count_nonzero(niter)),
            "nefc_min_max": [int(nefc.min()), int(nefc.max())],
            "overflow_nonzero": int(np.count_nonzero(overflow)),
            "overflow_or": int(np.bitwise_or.reduce(overflow.reshape(-1))),
            "qpos_sha256": array_sha(qpos),
            "qvel_sha256": array_sha(qvel),
        }
        (RAW / "B16_GRAPH_CANARY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
