#!/usr/bin/env python3
"""Frozen B1024 discovery entry, complete Data restore and five B0 replays."""

import csv
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

import mujoco
import numpy as np
import warp as wp

from state_utils import digest_fields, enumerate_data_arrays, make_gpu_snapshot, restore_gpu_snapshot, sha_numpy


ROOT = Path("/data/c16/awma/r20_active_world_native_v1")
SCENE = ROOT / "scene/unitree_g1_hfield"
RAW = ROOT / "raw"
BATCH = 1024
SELECTED_FIELDS = (
    "qpos", "qvel", "act", "history", "qacc_warmstart", "ctrl", "time",
    "mocap_pos", "mocap_quat", "qfrc_applied", "xfrc_applied", "eq_active",
    "userdata", "tree_asleep", "tree_awake", "body_awake", "solver_niter",
    "nefc", "overflow", "nacon", "ncollision",
)


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def coverage_u64(nefc, efc_type, efc_id):
    values = np.empty(len(nefc), dtype=np.uint64)
    for world in range(len(nefc)):
        count = int(nefc[world])
        if count < 0 or count > efc_type.shape[1]:
            raise RuntimeError(f"Invalid nefc={count} at world {world}")
        digest = hashlib.blake2b(digest_size=8)
        digest.update(np.ascontiguousarray(efc_type[world, :count]).view(np.uint8).tobytes())
        digest.update(np.ascontiguousarray(efc_id[world, :count]).view(np.uint8).tobytes())
        values[world] = int.from_bytes(digest.digest(), "little")
    return values


def memory_snapshot():
    line = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.free,memory.total", "--format=csv,noheader,nounits"], text=True
    ).strip().splitlines()[0]
    free_mib, total_mib = (int(part.strip()) for part in line.split(","))
    return {"free_MiB": free_mib, "total_MiB": total_mib, "free_fraction": free_mib / total_mib}


def main():
    assert os.environ.get("R20_GPU_LOCK_HELD") == "1"
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    import mujoco_warp as mjw
    from mujoco_warp._src.cli import _ctrl_noise
    from mujoco_warp._src.io import load_trajectory, override_model
    from mujoco_warp._src.types import OverflowType

    frozen = json.loads((RAW / "SOURCE_ASSET_WINDOW_RECEIPT.json").read_text())
    assert frozen["discovery_half_open"] == [128, 160]
    assert frozen["holdout_half_open_SEALED"] == [384, 416]
    d_start, d_end = frozen["discovery_half_open"]
    scene_receipt = json.loads((RAW / "SCENE_MODEL_RECEIPT.json").read_text())
    assert file_sha(SCENE / "scene_hfield.xml") == scene_receipt["scene_xml_sha256"]
    device = wp.get_device("cuda:0")
    model_cpu = mujoco.MjSpec.from_file(str(SCENE / "scene_hfield.xml")).compile()
    state_cpu = mujoco.MjData(model_cpu)
    ctrls = load_trajectory(str(SCENE / "shuffle_dance.npz"), model_cpu, state_cpu)
    assert len(ctrls) == frozen["control_replay_length_formula_L"] == 1000
    with wp.ScopedDevice(device):
        model = mjw.put_model(model_cpu)
        override_model(model, ["opt.warn_overflow=~ITERATIONS|~LS_ITERATIONS"])
        data = mjw.put_data(model_cpu, state_cpu, nworld=BATCH, nconmax=48, njmax=192)
        assert model.opt.graph_conditional and int(model.opt.iterations) == 10 and int(model.opt.ls_iterations) == 20
        with wp.ScopedCapture() as capture:
            mjw.step(model, data)
        wp.synchronize()

        def publish_ctrl(step):
            center = wp.array(ctrls[step], dtype=wp.float32, device=device)
            wp.launch(
                _ctrl_noise,
                dim=(data.nworld, model.nu),
                inputs=[model.opt.timestep, model.actuator_ctrllimited, model.actuator_ctrlrange,
                        data.ctrl, center, step, 0.01, 0.1],
                outputs=[data.ctrl],
            )
            wp.synchronize()

        prefix_begin = time.perf_counter()
        for step in range(d_start):
            publish_ctrl(step)
            wp.capture_launch(capture.graph)
            wp.synchronize()
        prefix_seconds_not_primary = time.perf_counter() - prefix_begin

        arrays = enumerate_data_arrays(data)
        assert len(arrays) > 50
        snapshot = make_gpu_snapshot(data)
        entry_selected = digest_fields(data, SELECTED_FIELDS)
        assert {"qpos", "qvel", "qacc_warmstart", "ctrl", "time"}.issubset(entry_selected)
        manifest = []
        cpu_payload = {}
        for index, (path, saved) in enumerate(snapshot.items()):
            value = saved.numpy()
            key = f"array_{index:04d}"
            cpu_payload[key] = value
            manifest.append({
                "key": key,
                "field_path": path,
                "warp_shape": list(saved.shape),
                "warp_dtype": str(saved.dtype),
                "numpy_shape": list(value.shape),
                "numpy_dtype": str(value.dtype),
                "bytes": value.nbytes,
                "sha256": sha_numpy(value),
            })
        state_path = RAW / "DISCOVERY_ENTRY_FULL_DATA.npz"
        np.savez_compressed(state_path, **cpu_payload)
        total_state_bytes = sum(row["bytes"] for row in manifest)
        entry = {
            "stage": "AWMA_R20_ACTIVE_WORLD_NATIVE_109_V1",
            "classification": "B1024_DISCOVERY_ENTRY_FULL_DATA_SNAPSHOT",
            "window_half_open": [d_start, d_end],
            "prefix_steps": d_start,
            "prefix_seconds_not_primary": prefix_seconds_not_primary,
            "model_graph_conditional": bool(model.opt.graph_conditional),
            "solver": str(model.opt.solver),
            "cone": str(model.opt.cone),
            "is_sparse": bool(model.is_sparse),
            "iterations": int(model.opt.iterations),
            "ls_iterations": int(model.opt.ls_iterations),
            "tolerance": float(model.opt.tolerance.numpy().reshape(-1)[0]),
            "ls_tolerance": float(model.opt.ls_tolerance.numpy().reshape(-1)[0]),
            "nworld": data.nworld,
            "naconmax_pooled": data.naconmax,
            "naccdmax_pooled": data.naccdmax,
            "njmax_per_world": data.njmax,
            "njmax_nnz": data.njmax_nnz,
            "nvmax": data.nvmax,
            "data_array_field_count": len(manifest),
            "data_array_total_logical_bytes_with_aliases": total_state_bytes,
            "state_npz_path": str(state_path),
            "state_npz_sha256": file_sha(state_path),
            "selected_field_digests": entry_selected,
            "manifest": manifest,
            "memory_after_snapshot": memory_snapshot(),
        }
        (RAW / "DISCOVERY_ENTRY_STATE_MANIFEST.json").write_text(json.dumps(entry, indent=2, sort_keys=True) + "\n")

        # Observation and numerical repeatability are outside formal timing.
        start_event = wp.Event(enable_timing=True)
        end_event = wp.Event(enable_timing=True)
        repeat_records = []
        trajectory = {key: [] for key in ("qpos", "qvel", "qacc_warmstart", "ctrl", "niter", "nefc", "overflow", "coverage_u64")}
        first_repeat_rows = []
        capacity_mask = int(OverflowType.ALL) & ~(int(OverflowType.ITERATIONS) | int(OverflowType.LS_ITERATIONS))
        for repeat in range(5):
            restore_gpu_snapshot(data, snapshot)
            restored = digest_fields(data, SELECTED_FIELDS)
            if restored != entry_selected:
                raise RuntimeError(f"Full Data restore changed selected entry fields in repeat {repeat}")
            observed = {key: [] for key in trajectory}
            per_step = []
            for step in range(d_start, d_end):
                publish_ctrl(step)
                ctrl = data.ctrl.numpy()
                wp.record_event(start_event)
                wall_begin = time.perf_counter_ns()
                wp.capture_launch(capture.graph)
                wp.record_event(end_event)
                wp.synchronize()
                wall_end = time.perf_counter_ns()
                qpos = data.qpos.numpy()
                qvel = data.qvel.numpy()
                warmstart = data.qacc_warmstart.numpy()
                niter = data.solver_niter.numpy()
                nefc = data.nefc.numpy()
                overflow = data.overflow.numpy()
                cover = coverage_u64(nefc, data.efc.type.numpy(), data.efc.id.numpy())
                nacon = int(data.nacon.numpy().reshape(-1)[0])
                ncollision = int(data.ncollision.numpy().reshape(-1)[0])
                if not np.isfinite(qpos).all() or not np.isfinite(qvel).all() or not np.isfinite(warmstart).all():
                    raise RuntimeError(f"Nonfinite state at repeat={repeat}, step={step}")
                for key, value in (("qpos", qpos), ("qvel", qvel), ("qacc_warmstart", warmstart),
                                   ("ctrl", ctrl), ("niter", niter), ("nefc", nefc),
                                   ("overflow", overflow), ("coverage_u64", cover)):
                    observed[key].append(value.copy())
                J = int(niter.max())
                active_by_iteration = [int(np.count_nonzero(niter >= j)) for j in range(1, J + 1)]
                capacity_overflow = overflow & capacity_mask
                if np.count_nonzero(capacity_overflow):
                    diagnostic = {
                        "step": step,
                        "repeat": repeat,
                        "capacity_overflow_worlds": int(np.count_nonzero(capacity_overflow)),
                        "capacity_overflow_or": int(np.bitwise_or.reduce(capacity_overflow.reshape(-1))),
                        "capacity_mask": capacity_mask,
                        "requested_nconmax_per_world": 48,
                        "njmax_per_world": data.njmax,
                    }
                    (RAW / "CAPACITY_OVERFLOW_PRE_REPAIR.json").write_text(json.dumps(diagnostic, indent=2, sort_keys=True) + "\n")
                    raise RuntimeError(f"Capacity overflow before valid baseline at step {step}: {diagnostic}")
                row = {
                    "step": step,
                    "nworld": BATCH,
                    "solver_rounds_J": J,
                    "niter_min": int(niter.min()),
                    "niter_max": J,
                    "niter_mean": float(niter.mean()),
                    "entry_active": active_by_iteration[0] if active_by_iteration else 0,
                    "active_by_iteration_derived_from_niter": active_by_iteration,
                    "active_slot_fraction": (sum(active_by_iteration) / (BATCH * J)) if J else None,
                    "non_limit_terminated_reason_tolerance_or_alpha_unknown": int(np.count_nonzero((overflow & int(OverflowType.ITERATIONS)) == 0)),
                    "iteration_limit_worlds": int(np.count_nonzero(overflow & int(OverflowType.ITERATIONS))),
                    "line_search_limit_worlds": int(np.count_nonzero(overflow & int(OverflowType.LS_ITERATIONS))),
                    "capacity_overflow_worlds": int(np.count_nonzero(capacity_overflow)),
                    "capacity_overflow_or": int(np.bitwise_or.reduce(capacity_overflow.reshape(-1))),
                    "nefc_min": int(nefc.min()),
                    "nefc_max": int(nefc.max()),
                    "nefc_mean": float(nefc.mean()),
                    "nacon_pooled": nacon,
                    "ncollision_pooled": ncollision,
                    "ctrl_sha256": sha_numpy(ctrl),
                    "qpos_sha256": sha_numpy(qpos),
                    "qvel_sha256": sha_numpy(qvel),
                    "coverage_u64_sha256": sha_numpy(cover),
                    "step_wall_ms_observer_only": (wall_end - wall_begin) / 1e6,
                    "step_cuda_event_ms_observer_only": float(wp.get_event_elapsed_time(start_event, end_event)),
                }
                per_step.append(row)
            stacked = {key: np.stack(value) for key, value in observed.items()}
            for key in trajectory:
                trajectory[key].append(stacked[key])
            repeat_records.append({
                "repeat": repeat,
                "window_half_open": [d_start, d_end],
                "selected_entry_restored_exact": True,
                "fields": {key: sha_numpy(value) for key, value in stacked.items()},
                "last_qpos_sha256": per_step[-1]["qpos_sha256"],
                "last_ctrl_sha256": per_step[-1]["ctrl_sha256"],
            })
            if repeat == 0:
                first_repeat_rows = per_step

        all_repeats = {key: np.stack(value) for key, value in trajectory.items()}
        raw_repeat = RAW / "BASELINE_DISCOVERY_REPEATS.npz"
        np.savez_compressed(raw_repeat, **all_repeats)
        field_exact = {key: all(np.array_equal(all_repeats[key][0], all_repeats[key][i]) for i in range(1, 5)) for key in all_repeats}
        field_max_abs_spread = {}
        for key in ("qpos", "qvel", "qacc_warmstart", "ctrl"):
            reference = all_repeats[key][0].astype(np.float64)
            field_max_abs_spread[key] = float(max(np.max(np.abs(all_repeats[key][i].astype(np.float64) - reference)) for i in range(1, 5)))
        repeatability = {
            "stage": "AWMA_R20_ACTIVE_WORLD_NATIVE_109_V1",
            "classification": "B0_DISCOVERY_BASELINE_NUMERICAL_GATE_BEFORE_CANDIDATE",
            "full_data_entry_sha256": entry["state_npz_sha256"],
            "repeats": repeat_records,
            "field_bitwise_repeatability": field_exact,
            "field_max_abs_spread": field_max_abs_spread,
            "all_required_field_trajectories_bitwise": all(field_exact.values()),
            "baseline_repeats_raw_sha256": file_sha(raw_repeat),
            "active_counts_method": "DERIVED_FROM_EXACT_SOLVER_NITER_AND_MONOTONIC_CTX_DONE_SOURCE",
            "true_tolerance_convergence_reason": "UNKNOWN_WITHOUT_CTX_REASON_INSTRUMENTATION; non-limit combines alpha==0/tolerance predicates",
            "observer_extra_gpu_kernels": 0,
            "observer_formal_timing": False,
        }
        (RAW / "BASELINE_REPEATABILITY.json").write_text(json.dumps(repeatability, indent=2, sort_keys=True) + "\n")
        (RAW / "DISCOVERY_ACTIVITY_PER_STEP.json").write_text(json.dumps(first_repeat_rows, indent=2, sort_keys=True) + "\n")
        with (RAW / "ACTIVITY_AND_CAPACITY.tsv").open("w", newline="", encoding="utf-8") as stream:
            keys = [key for key in first_repeat_rows[0] if key != "active_by_iteration_derived_from_niter"]
            writer = csv.DictWriter(stream, fieldnames=[*keys, "active_by_iteration_derived_from_niter"], delimiter="\t", lineterminator="\n")
            writer.writeheader()
            for row in first_repeat_rows:
                writer.writerow({**row, "active_by_iteration_derived_from_niter": ",".join(str(value) for value in row["active_by_iteration_derived_from_niter"])})
        summary = {
            "stage": "AWMA_R20_ACTIVE_WORLD_NATIVE_109_V1",
            "discovery_half_open": [d_start, d_end],
            "batch": BATCH,
            "entry_state_sha256": entry["state_npz_sha256"],
            "field_count": len(manifest),
            "state_logical_bytes_with_aliases": total_state_bytes,
            "repeatability_bitwise": repeatability["all_required_field_trajectories_bitwise"],
            "discovery_niter_min": min(row["niter_min"] for row in first_repeat_rows),
            "discovery_niter_max": max(row["niter_max"] for row in first_repeat_rows),
            "steps_with_active_shrinkage": sum(any(value < row["entry_active"] for value in row["active_by_iteration_derived_from_niter"][1:]) for row in first_repeat_rows),
            "steps_with_capacity_overflow": sum(row["capacity_overflow_worlds"] > 0 for row in first_repeat_rows),
            "steps_with_iteration_limit": sum(row["iteration_limit_worlds"] > 0 for row in first_repeat_rows),
            "mean_active_slot_fraction": float(np.mean([row["active_slot_fraction"] for row in first_repeat_rows if row["active_slot_fraction"] is not None])),
            "memory_after_observation": memory_snapshot(),
        }
        (RAW / "DISCOVERY_BASELINE_SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
