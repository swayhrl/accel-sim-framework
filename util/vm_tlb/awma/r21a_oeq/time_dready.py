#!/usr/bin/env python3
"""Frozen A0 vs free-prepared Dready complete energy+force timing gate."""

import csv
import hashlib
import json
import math
import os
import statistics
import time
import traceback
from pathlib import Path

import numpy as np


ROOT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
RAW = ROOT / "raw"
A0 = ROOT / "compile/A0_ATOMIC_DISCOVERYDATA.nequip.pt2"
DREADY = ROOT / "compile/DREADY_OAM_S.nequip.pt2"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def first_bad(ref, observed):
    bad = ~np.isfinite(observed) | ~np.isclose(ref, observed, atol=5e-5, rtol=5e-5)
    if not np.any(bad):
        return None
    at = tuple(int(x) for x in np.argwhere(bad)[0])
    return {"index": at, "reference": float(ref[at]), "observed": str(observed[at]),
            "allowed_atol_plus_rtol_abs_ref": float(5e-5+5e-5*abs(ref[at]))}


def median_mad(values):
    m = statistics.median(values)
    return m, statistics.median(abs(x-m) for x in values)


def main():
    if os.environ.get("R21A_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU lock receipt absent")
    if (RAW / "DREADY_TIMING_ALL_SAMPLES.tsv").exists():
        raise RuntimeError("Dready formal timing already exists; no overwrite")
    import torch
    import openequivariance
    from nequip.data import AtomicDataDict
    from nequip.model.inference_models import load_compiled_model

    torch.set_default_dtype(torch.float32)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_float32_matmul_precision("highest")
    if json.loads((RAW / "A0_DATA_QUALIFICATION_STATUS.json").read_text())["status"] != "A0_ATOMIC_BASELINE_QUALIFIED":
        raise RuntimeError("A0 numerical authority absent")
    if json.loads((RAW / "DREADY_CORRECTNESS_STATUS.json").read_text())["status"] != "DREADY_NUMERICS_QUALIFIED":
        raise RuntimeError("Dready numerical authority absent")
    graph = json.loads((RAW / "DISCOVERY_GRAPH_AUTHORITY.json").read_text())
    prepared = json.loads((RAW / "DETERMINISTIC_FULLSORT_EAGER_PROBE_STATUS.json").read_text())
    natural_path = RAW / "DISCOVERY_NATURAL_GRAPH.npz"
    ready_path = RAW / "DISCOVERY_DETERMINISTIC_FULLSORT_GRAPH_READY.npz"
    if sha(natural_path) != graph["graph_npz_sha256"] or sha(ready_path) != prepared["prepared_graph_sha256"]:
        raise RuntimeError("Frozen graph representation hash changed")
    refs = []
    for i in range(5):
        with np.load(RAW / f"REFERENCE_DATA_RUN_{i}.npz", allow_pickle=False) as z:
            refs.append((z["energy"].copy(), z["forces"].copy()))
    ref_e = np.mean(np.stack([x[0] for x in refs]), axis=0)
    ref_f = np.mean(np.stack([x[1] for x in refs]), axis=0)
    samples = []
    state = {"stage": "AWMA_R21A_OEQ_GRAPH_READINESS_109_V1", "status": "STARTED",
             "frame_index": 55, "natural_graph_sha256": graph["graph_npz_sha256"],
             "prepared_graph_sha256": prepared["prepared_graph_sha256"],
             "A0_AOT_sha256": sha(A0), "Dready_AOT_sha256": sha(DREADY),
             "formal_sample_count": 0, "first_mismatch": None, "failed_payload_sha256": None,
             "timing_boundary": "required_graph_resident_GPU_to_energy_forces_committed"}
    (RAW / "DREADY_TIMING_STATUS.json").write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    try:
        models = {}
        data = {}
        for arm, package, graph_path in (("A0", A0, natural_path), ("Dready", DREADY, ready_path)):
            model, metadata = load_compiled_model(str(package), device="cuda")
            with np.load(graph_path, allow_pickle=False) as z:
                d = {k: torch.from_numpy(z[k].copy()) for k in z.files}
            models[arm] = model
            data[arm] = AtomicDataDict.to_(d, device=torch.device("cuda"))
            state[f"{arm}_compiled_inputs"] = model.input_keys
            state[f"{arm}_compiled_outputs"] = model.output_keys
        if state["A0_compiled_inputs"] != ["pos", "edge_index", "atom_types", "cell", "edge_cell_shift"]:
            raise RuntimeError("A0 compile input signature changed")
        if state["Dready_compiled_inputs"] != state["A0_compiled_inputs"] + [AtomicDataDict.EDGE_TRANSPOSE_PERM_KEY]:
            raise RuntimeError("Dready compile input signature changed")
        # One prewarm per arm forces any lazy loader/JIT outside all measured groups.
        for arm in ("A0", "Dready"):
            out = models[arm](dict(data[arm]))
            torch.cuda.synchronize()
            e = out[AtomicDataDict.TOTAL_ENERGY_KEY].detach().cpu().numpy().copy()
            f = out[AtomicDataDict.FORCE_KEY].detach().cpu().numpy().copy()
            if first_bad(ref_e, e) or first_bad(ref_f, f):
                path = RAW / f"DREADY_PREWARM_{arm}_FAILURE.npz"
                np.savez_compressed(path, energy=e, forces=f)
                state.update({"failed_arm": arm, "first_mismatch": first_bad(ref_e, e) or first_bad(ref_f, f),
                              "failed_payload_sha256": sha(path)})
                raise RuntimeError(f"Prewarm {arm} numeric failure")
        for group in range(3):
            order = ("A0", "Dready") if group % 2 == 0 else ("Dready", "A0")
            for arm in order:
                for within in range(7):
                    phase = "WARMUP" if within < 2 else "FORMAL"
                    repeat = within if phase == "WARMUP" else within-2
                    torch.cuda.synchronize()
                    start = torch.cuda.Event(enable_timing=True)
                    end = torch.cuda.Event(enable_timing=True)
                    t0 = time.perf_counter_ns()
                    start.record()
                    out = models[arm](dict(data[arm]))
                    end.record()
                    torch.cuda.synchronize()
                    wall_ms = (time.perf_counter_ns()-t0)/1e6
                    event_ms = start.elapsed_time(end)
                    if not (math.isfinite(wall_ms) and math.isfinite(event_ms) and wall_ms > 0 and event_ms > 0):
                        raise RuntimeError("Invalid whole-model timer")
                    e = out[AtomicDataDict.TOTAL_ENERGY_KEY].detach().cpu().numpy().copy()
                    f = out[AtomicDataDict.FORCE_KEY].detach().cpu().numpy().copy()
                    row = {"group": group, "arm": arm, "order": ",".join(order),
                           "phase": phase, "repeat": repeat, "wall_ms": wall_ms,
                           "cuda_event_ms": event_ms, "numerical_pass": "NOT_CHECKED_WARMUP",
                           "output_sha256": "NOT_SAVED_WARMUP"}
                    if phase == "FORMAL":
                        output_path = RAW / f"DREADY_TIMING_G{group}_{arm}_R{repeat}.npz"
                        np.savez_compressed(output_path, energy=e, forces=f)
                        row["output_sha256"] = sha(output_path)
                        bad_e, bad_f = first_bad(ref_e, e), first_bad(ref_f, f)
                        row["numerical_pass"] = bool(bad_e is None and bad_f is None and e.shape == ref_e.shape and f.shape == (64, 3))
                        state["formal_sample_count"] += 1
                        if not row["numerical_pass"]:
                            state.update({"status": "FORMAL_NUMERIC_GATE_FAILED", "failed_arm": arm,
                                          "failed_group": group, "failed_repeat": repeat,
                                          "first_mismatch": bad_e or bad_f, "failed_payload_sha256": row["output_sha256"]})
                            samples.append(row)
                            raise RuntimeError("Formal energy/force contract failed")
                    else:
                        if not (np.isfinite(e).all() and np.isfinite(f).all()):
                            path = RAW / f"DREADY_TIMING_WARMUP_G{group}_{arm}_{repeat}_FAILURE.npz"
                            np.savez_compressed(path, energy=e, forces=f)
                            state.update({"status": "WARMUP_NONFINITE", "failed_arm": arm,
                                          "first_mismatch": first_bad(ref_e, e) or first_bad(ref_f, f),
                                          "failed_payload_sha256": sha(path)})
                            samples.append(row)
                            raise RuntimeError("Warmup nonfinite output")
                    samples.append(row)
                    print(json.dumps({"group": group, "arm": arm, "phase": phase, "repeat": repeat,
                                      "wall_ms": wall_ms, "event_ms": event_ms, "numerical_pass": row["numerical_pass"]}), flush=True)
        with (RAW / "DREADY_TIMING_ALL_SAMPLES.tsv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(samples[0]), delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(samples)
        groups = []
        for group in range(3):
            arm_stats = {}
            for arm in ("A0", "Dready"):
                values = [r["wall_ms"] for r in samples if r["group"] == group and r["arm"] == arm and r["phase"] == "FORMAL"]
                events = [r["cuda_event_ms"] for r in samples if r["group"] == group and r["arm"] == arm and r["phase"] == "FORMAL"]
                if len(values) != 5:
                    raise RuntimeError("Five formal samples missing")
                arm_stats[arm] = {"wall_median_ms": median_mad(values)[0], "wall_MAD_ms": median_mad(values)[1],
                                  "event_median_ms": median_mad(events)[0], "event_MAD_ms": median_mad(events)[1]}
            gap = arm_stats["A0"]["wall_median_ms"]-arm_stats["Dready"]["wall_median_ms"]
            noise = max(arm_stats["A0"]["wall_MAD_ms"], arm_stats["Dready"]["wall_MAD_ms"])
            groups.append({"group": group, "A0": arm_stats["A0"], "Dready": arm_stats["Dready"],
                           "gap_ms": gap, "relative_improvement": gap/arm_stats["A0"]["wall_median_ms"],
                           "gap_gt_3x_larger_MAD": gap > 3*noise})
        median_gain = statistics.median(x["relative_improvement"] for x in groups)
        material = all(x["gap_ms"] > 0 and x["gap_gt_3x_larger_MAD"] for x in groups) and median_gain >= 0.05
        stable_submaterial = ((all(x["gap_ms"] > 0 and x["gap_gt_3x_larger_MAD"] for x in groups) and median_gain < 0.05)
                              or all(x["gap_ms"] < 0 and -x["gap_ms"] > 3*max(x["A0"]["wall_MAD_ms"], x["Dready"]["wall_MAD_ms"]) for x in groups))
        state.update({"status": "DREADY_TIMING_COMPLETE", "all_30_formal_numeric_pass": True,
                      "groups": groups, "median_relative_improvement": median_gain,
                      "Dready_MATERIAL": material,
                      "classification_if_stop": None if material else ("R21A_READY_HEADROOM_NOT_MATERIAL" if stable_submaterial else "R21A_RESULT_MIXED_NEEDS_REVIEW")})
    except Exception as exc:
        if state["status"] == "STARTED":
            state["status"] = "DREADY_TIMING_EXECUTION_FAILED"
        state["error_type"] = type(exc).__name__
        state["error"] = str(exc)
        state["traceback_tail"] = traceback.format_exc()[-10000:]
    (RAW / "DREADY_TIMING_STATUS.json").write_text(json.dumps(state, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: state.get(k) for k in ("status", "formal_sample_count", "median_relative_improvement", "Dready_MATERIAL", "classification_if_stop", "failed_arm", "first_mismatch", "error_type", "error")}, default=str), flush=True)
    if state["status"] != "DREADY_TIMING_COMPLETE":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
