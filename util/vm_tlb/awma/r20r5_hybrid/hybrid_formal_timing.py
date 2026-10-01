#!/usr/bin/env python3
"""Frozen R20R5 B0/H1 complete-solver timing with debug branch recorder OFF."""

import csv
import json
import math
import os
import statistics
import sys
import time
from pathlib import Path

import mujoco
import numpy as np
import warp as wp


ROOT = Path("/data/c16/awma/r20r5_hybrid_native_20261002")
RAW = ROOT / "raw"
R1 = Path("/data/c16/awma/r20r1_solver_entry_local_contract_20261001")
HERE = Path(__file__).resolve()
AWMA = HERE.parents[1]
sys.path.insert(0, str(AWMA / "r20r3p1_profiler"))
sys.path.insert(0, str(AWMA / "r20r3p2_residual"))
sys.path.insert(0, str(AWMA / "r20r1_solver_entry"))
sys.path.insert(0, str(AWMA / "r20_active_world"))
sys.path.insert(0, str(HERE.parent))
from r20r3p1_scientific_profile import EXPECTED_SHA, SCENE, STEPS, check_output, reference
from r20r3p2_b0 import source_stop_predicates, summarize_stop
from b0_repeatability_t128 import output_view
from snapshot_io import enumerate_data_arrays, file_sha, restore_recorded_snapshot, sha_numpy
from state_utils import make_gpu_snapshot, restore_gpu_snapshot


def median_mad(values):
    center = statistics.median(values)
    return center, statistics.median(abs(x-center) for x in values)


def main():
    if os.environ.get("R20R5_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU campaign lock receipt absent")
    if not json.loads((RAW / "BASELINE_SUMMARY.json").read_text())["all_qualified"]:
        raise RuntimeError("Four-entry hybrid OFF regression gate absent")
    if not json.loads((HERE.parents[4] / "docs/vm_tlb/review_packs/AWMA_R20R3P2_RESIDUAL_CONTRACT_RESUME_109_V1/CANDIDATE_IDENTITY.json").read_text())["B0_all_32_qualified_before_S1"]:
        raise RuntimeError("Accepted R20R3P2 source-semantic contract gate absent")
    if not json.loads((RAW / "CANDIDATE_CORRECTNESS_SUMMARY.json").read_text())["all_four_qualified"]:
        raise RuntimeError("Four-entry candidate correctness gate absent")
    if (RAW / "DISCOVERY_TIMING_ALL_SAMPLES.tsv").exists():
        raise RuntimeError("Discovery timing already exists; no retry or overwrite")
    if Path(os.environ.get("PYTHONPATH", "").split(os.pathsep)[0]).resolve() != ROOT / "source_overlay":
        raise RuntimeError("Wrong source overlay")
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    import mujoco_warp as mjw
    from mujoco_warp._src import solver
    from mujoco_warp._src.io import load_trajectory, override_model
    if file_sha(Path(solver.__file__)) != "aba0862337371bb1f09b24d2089654b5571b5be59e8f6695e97409c22e1680e8":
        raise RuntimeError("Frozen R20R5 hybrid source identity changed")
    device = wp.get_device("cuda:0")
    if device.sm_count != 76:
        raise RuntimeError("Frozen SM count changed")
    lineage = json.loads((R1 / "raw/R2_DISCOVERY_ENTRY_LINEAGE.json").read_text())
    entries = {x["step"]: x["entry_snapshot"] for x in lineage["entrances"]}
    mjm = mujoco.MjSpec.from_file(str(SCENE / "scene_hfield.xml")).compile()
    mjd = mujoco.MjData(mjm)
    if len(load_trajectory(str(SCENE / "shuffle_dance.npz"), mjm, mjd)) != 1000:
        raise RuntimeError("Frozen control trajectory changed")
    samples = []
    with wp.ScopedDevice(device):
        model = mjw.put_model(mjm)
        override_model(model, ["opt.warn_overflow=~ITERATIONS|~LS_ITERATIONS"])
        if not (model.opt.graph_conditional and model.is_sparse and int(model.opt.iterations) == 10
                and int(model.opt.ls_iterations) == 20):
            raise RuntimeError("Frozen solver options changed")
        expected_model = {x["path"]: x["sha256"] for x in json.loads((R1 / "raw/G0_MODEL_ARRAY_MANIFEST.json").read_text())}
        model_arrays = enumerate_data_arrays(model)
        if set(model_arrays) != set(expected_model) or any(sha_numpy(v.numpy()) != expected_model[k] for k, v in model_arrays.items()):
            raise RuntimeError("Frozen Model identity changed")
        data = mjw.put_data(mjm, mjd, nworld=1024, nconmax=48, njmax=192)
        contexts = []
        original_factory = solver._create_solver_context

        def witness(m, d):
            ctx = original_factory(m, d)
            contexts.append(ctx)
            return ctx

        solver._create_solver_context = witness
        try:
            solver._R20R3P1_ACTIVE = False
            solver._R20R5_HYBRID = False
            solver._R20R5_DEBUG = False
            with wp.ScopedCapture() as graph_b0:
                solver.solve(model, data)
            solver._R20R3P1_ACTIVE_IDS = wp.empty(1024, dtype=int, device=device)
            solver._R20R3P1_ACTIVE_COUNT = wp.empty(1, dtype=int, device=device)
            solver._R20R3P1_WORKERS = 304
            solver._R20R5_LATE_CONDITION = wp.empty(1, dtype=int, device=device)
            solver._R20R5_HYBRID = True
            with wp.ScopedCapture() as graph_h1:
                solver.solve(model, data)
        finally:
            solver._R20R5_HYBRID = False
            solver._R20R5_DEBUG = False
            solver._R20R3P1_ACTIVE = False
            solver._create_solver_context = original_factory
        if len(contexts) != 2:
            raise RuntimeError("Expected B0/H1 SolverContext captures")
        ctxs = {"B0": contexts[0], "H1": contexts[1]}
        graphs = {"B0": graph_b0, "H1": graph_h1}
        masks = wp.empty(1024, dtype=int, device=device)
        values = wp.empty((1024, 6), dtype=float, device=device)
        frozen = {}
        for step in STEPS:
            entry = entries[step]
            if entry["sha256"] != EXPECTED_SHA[step] or file_sha(R1 / f"raw/R2_T{step}_SOLVER_ENTRY_FULL_DATA.npz") != EXPECTED_SHA[step]:
                raise RuntimeError(f"Entry t{step} identity changed")
            restore_recorded_snapshot(data, entry)
            frozen[step] = make_gpu_snapshot(data)
        wp.synchronize()
        for group in range(3):
            order = ("B0", "H1") if group % 2 == 0 else ("H1", "B0")
            for step in STEPS:
                entry = entries[step]
                for arm in order:
                    graph, ctx = graphs[arm], ctxs[arm]
                    for within in range(7):
                        phase = "WARMUP" if within < 2 else "FORMAL"
                        repeat = within if phase == "WARMUP" else within-2
                        restore_gpu_snapshot(data, frozen[step])
                        wp.synchronize()
                        if within == 0:
                            arrays = enumerate_data_arrays(data)
                            for item in entry["manifest"]:
                                if sha_numpy(arrays[item["field_path"]].numpy()) != item["sha256"]:
                                    raise RuntimeError(f"Restored entry differs at t{step}:{item['field_path']}")
                        start = wp.Event(enable_timing=True)
                        end = wp.Event(enable_timing=True)
                        t0 = time.perf_counter_ns()
                        wp.record_event(start)
                        wp.capture_launch(graph.graph)
                        wp.record_event(end)
                        wp.synchronize()
                        t1 = time.perf_counter_ns()
                        wall_ms = (t1-t0)/1e6
                        event_ms = wp.get_event_elapsed_time(start, end)
                        if not (math.isfinite(wall_ms) and math.isfinite(event_ms) and wall_ms > 0 and event_ms > 0):
                            raise RuntimeError("Invalid complete-solver time")
                        row = {"group": group, "step": step, "arm": arm, "phase": phase, "repeat": repeat,
                               "order": "B0,H1" if group % 2 == 0 else "H1,B0",
                               "entry_sha256": EXPECTED_SHA[step], "wall_ms": wall_ms, "cuda_event_ms": event_ms,
                               "sample_semantic_pass": "NOT_CHECKED_WARMUP"}
                        if phase == "FORMAL":
                            out = output_view(data)
                            source_status, _, _ = check_output(step, reference(step), out, data, ctx, model,
                                                               frozen[step]["overflow"].numpy())
                            wp.launch(source_stop_predicates, dim=1024,
                                      inputs=[model.nv, model.opt.tolerance, model.stat.meaninertia, ctx.alpha,
                                              ctx.improvement, ctx.grad_dot, ctx.newton_decrement],
                                      outputs=[masks, values])
                            wp.synchronize()
                            stop = summarize_stop(masks.numpy().copy(), values.numpy().copy(), out["solver_niter"],
                                                  frozen[step]["overflow"].numpy(), out["overflow"], ctx.done.numpy().copy(),
                                                  int(model.opt.iterations))
                            row.update({"sample_semantic_pass": bool(source_status["qualified"] and stop["pass"]),
                                        "nefc_exact": source_status["nefc_exact"],
                                        "niter_exact": source_status["solver_niter_exact"],
                                        "LS_count": source_status["LS_ITERATIONS_count"],
                                        "new_ITERATIONS_count": len(stop["new_ITERATIONS_worlds"]),
                                        "source_stop_fail_count": len(stop["fail_worlds"]),
                                        "H1_final_active_count": int(solver._R20R3P1_ACTIVE_COUNT.numpy()[0]) if arm == "H1" else "NA"})
                            if not row["sample_semantic_pass"]:
                                samples.append(row)
                                raise RuntimeError(f"Formal sample semantic gate failed at {row}")
                        samples.append(row)
                        print(json.dumps({"group": group, "step": step, "arm": arm, "phase": phase,
                                          "repeat": repeat, "wall_ms": wall_ms, "event_ms": event_ms,
                                          "semantic": row["sample_semantic_pass"]}), flush=True)
        with (RAW / "DISCOVERY_TIMING_ALL_SAMPLES.tsv").open("w", newline="") as stream:
            fields = list(dict.fromkeys(key for row in samples for key in row))
            writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(samples)
    formal = [r for r in samples if r["phase"] == "FORMAL"]
    groups = []
    for group in range(3):
        sums = {}
        for arm in ("B0", "H1"):
            medians = []
            mads = []
            event_medians = []
            for step in STEPS:
                selected = [r for r in formal if r["group"] == group and r["step"] == step and r["arm"] == arm]
                if len(selected) != 5:
                    raise RuntimeError("Formal sample count differs from frozen protocol")
                median, mad = median_mad([r["wall_ms"] for r in selected])
                medians.append(median)
                mads.append(mad)
                event_medians.append(statistics.median(r["cuda_event_ms"] for r in selected))
            sums[arm] = {"sum_entry_wall_medians_ms": sum(medians),
                         "sum_entry_wall_MADs_ms": sum(mads),
                         "sum_entry_event_medians_ms": sum(event_medians)}
        gap = sums["B0"]["sum_entry_wall_medians_ms"]-sums["H1"]["sum_entry_wall_medians_ms"]
        larger_mad = max(sums["B0"]["sum_entry_wall_MADs_ms"], sums["H1"]["sum_entry_wall_MADs_ms"])
        groups.append({"group": group, "B0_wall_sum_ms": sums["B0"]["sum_entry_wall_medians_ms"],
                       "H1_wall_sum_ms": sums["H1"]["sum_entry_wall_medians_ms"],
                       "B0_event_sum_ms": sums["B0"]["sum_entry_event_medians_ms"],
                       "H1_event_sum_ms": sums["H1"]["sum_entry_event_medians_ms"],
                       "gap_ms": gap, "relative_improvement": gap/sums["B0"]["sum_entry_wall_medians_ms"],
                       "larger_arm_aggregate_MAD_estimate_ms": larger_mad,
                       "gap_exceeds_3x_MAD": gap > 3*larger_mad})
    median_gain = statistics.median(r["relative_improvement"] for r in groups)
    material = all(r["gap_ms"] > 0 and r["gap_exceeds_3x_MAD"] for r in groups) and median_gain >= 0.05
    stable_submaterial = ((all(r["gap_ms"] > 0 and r["gap_exceeds_3x_MAD"] for r in groups) and median_gain < 0.05)
                          or all(r["gap_ms"] < 0 and -r["gap_ms"] > 3*r["larger_arm_aggregate_MAD_estimate_ms"] for r in groups))
    outcome = {"stage": "AWMA_R20R5_HYBRID_ACTIVE_WORLD_NATIVE_109_V1",
               "all_formal_samples_semantically_qualified": all(r["sample_semantic_pass"] for r in formal),
               "sample_count": len(samples), "formal_count": len(formal), "warmup_count": len(samples)-len(formal),
               "groups": groups, "median_aggregate_relative_improvement": median_gain,
               "discovery_MATERIAL": material,
               "classification_if_stop": None if material else ("R20_ACTIVE_WORLD_LINE_CLOSED_AFTER_HYBRID_NEGATIVE" if stable_submaterial else "R20_ACTIVE_WORLD_LINE_CLOSED_AFTER_HYBRID_MIXED"),
               "aggregate_MAD_rule": "sum of per-entry wall MADs per arm, take larger arm; frozen before timing"}
    (RAW / "DISCOVERY_TIMING_DECISION.json").write_text(json.dumps(outcome, indent=2, sort_keys=True) + "\n")
    print(json.dumps(outcome, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
