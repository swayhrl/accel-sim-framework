#!/usr/bin/env python3
"""One-way batch memory/conditional-graph admission, not performance timing."""

import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

import mujoco
import numpy as np
import warp as wp


ROOT = Path("/data/c16/awma/r20_active_world_native_v1")
SCENE = ROOT / "scene/unitree_g1_hfield"
RAW = ROOT / "raw"


def array_sha(value):
    return hashlib.sha256(np.ascontiguousarray(value).view(np.uint8).tobytes()).hexdigest()


def memory_snapshot():
    line = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.free,memory.total", "--format=csv,noheader,nounits"],
        text=True,
    ).strip().splitlines()[0]
    free_mib, total_mib = (int(part.strip()) for part in line.split(","))
    return {"free_MiB": free_mib, "total_MiB": total_mib, "free_fraction": free_mib / total_mib}


def main():
    assert os.environ.get("R20_GPU_LOCK_HELD") == "1"
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, required=True, choices=(1024, 512, 256))
    args = parser.parse_args()
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    import mujoco_warp as mjw
    from mujoco_warp._src.cli import _ctrl_noise
    from mujoco_warp._src.io import load_trajectory, override_model

    device = wp.get_device("cuda:0")
    start_memory = memory_snapshot()
    mjm = mujoco.MjSpec.from_file(str(SCENE / "scene_hfield.xml")).compile()
    mjd = mujoco.MjData(mjm)
    centers = load_trajectory(str(SCENE / "shuffle_dance.npz"), mjm, mjd)
    assert len(centers) == 1000
    with wp.ScopedDevice(device):
        model = mjw.put_model(mjm)
        override_model(model, ["opt.warn_overflow=~ITERATIONS|~LS_ITERATIONS"])
        data = mjw.put_data(mjm, mjd, nworld=args.batch, nconmax=48, njmax=192)
        observed_while = []
        original = wp.capture_while

        def witness(*wargs, **kwargs):
            observed_while.append(bool(device.captures) and wargs[0].device.is_cuda)
            return original(*wargs, **kwargs)

        wp.capture_while = witness
        try:
            begin = time.perf_counter()
            with wp.ScopedCapture() as capture:
                mjw.step(model, data)
            wp.synchronize()
            capture_seconds = time.perf_counter() - begin
        finally:
            wp.capture_while = original
        assert observed_while and all(observed_while)
        assert model.opt.graph_conditional
        for step in range(2):
            center = wp.array(centers[step], dtype=wp.float32, device=device)
            wp.launch(
                _ctrl_noise,
                dim=(data.nworld, model.nu),
                inputs=[model.opt.timestep, model.actuator_ctrllimited, model.actuator_ctrlrange,
                        data.ctrl, center, step, 0.01, 0.1],
                outputs=[data.ctrl],
            )
            wp.capture_launch(capture.graph)
            wp.synchronize()
        ctrl = data.ctrl.numpy()
        qpos = data.qpos.numpy()
        qvel = data.qvel.numpy()
        nefc = data.nefc.numpy()
        niter = data.solver_niter.numpy()
        overflow = data.overflow.numpy()
        assert np.isfinite(qpos).all() and np.isfinite(qvel).all() and np.isfinite(ctrl).all()
        after_memory = memory_snapshot()
        receipt = {
            "stage": "AWMA_R20_ACTIVE_WORLD_NATIVE_109_V1",
            "classification": "MEMORY_AND_GRAPH_ADMISSION_NOT_FORMAL_TIMING",
            "batch": args.batch,
            "requested_nconmax_per_world": 48,
            "actual_naconmax_pooled": data.naconmax,
            "njmax_per_world": data.njmax,
            "model_graph_conditional": bool(model.opt.graph_conditional),
            "capture_while_device_node_witness": observed_while,
            "graph_captures": 1,
            "graph_replays": 2,
            "capture_seconds_not_primary": capture_seconds,
            "start_memory": start_memory,
            "after_capture_and_two_replays_memory": after_memory,
            "required_free_fraction": 0.20,
            "memory_admitted": after_memory["free_fraction"] >= 0.20,
            "control_step1_sha256": array_sha(ctrl),
            "control_step1_unique_world_rows": int(np.unique(ctrl, axis=0).shape[0]),
            "qpos_sha256": array_sha(qpos),
            "qvel_sha256": array_sha(qvel),
            "nefc_min_max": [int(nefc.min()), int(nefc.max())],
            "solver_niter_min_max": [int(niter.min()), int(niter.max())],
            "overflow_nonzero_worlds": int(np.count_nonzero(overflow)),
            "overflow_or": int(np.bitwise_or.reduce(overflow.reshape(-1))),
        }
        path = RAW / f"B{args.batch}_ADMISSION.json"
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(json.dumps(receipt, sort_keys=True))
        if not receipt["memory_admitted"]:
            raise SystemExit(2)


if __name__ == "__main__":
    main()
