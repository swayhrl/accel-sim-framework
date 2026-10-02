#!/usr/bin/env python3
"""Bounded R22F Aorder, profiled bundle, and uninstrumented complete-region runs."""

import argparse
import contextlib
import csv
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
import statistics
import time
import traceback
from pathlib import Path

import numpy as np

ROOT = Path("/data/c16/awma/r22f_r21a_family_localization_20261002")
PARENT = Path("/data/c16/awma/r21a_oeq_graph_readiness_20261002")
RAW = ROOT / "raw"
LOCK = Path("/data/c16/locks/c16_gpu_campaign.lock")
A0 = PARENT / "compile/A0_ATOMIC_DISCOVERYDATA.nequip.pt2"
DREADY = PARENT / "compile/DREADY_OAM_S.nequip.pt2"
NATURAL = PARENT / "raw/DISCOVERY_NATURAL_GRAPH.npz"
SORTED = PARENT / "raw/DISCOVERY_DETERMINISTIC_FULLSORT_GRAPH_READY.npz"
EXPECTED = {
    A0: "fbfa6e9277507adfb60c8fe76ad747e86fd5586472073d4ffe32fe553b6d58cc",
    DREADY: "850c11b39e2ef4b82cb0ff8d773d1231f753a5a52432afc0dd4d57e67fbbb04e",
    NATURAL: "cacb25ae579d64813c83e91e17fc449faedeb79171f18fb6c2dce3917bfd8d94",
    SORTED: "f1e0eb6bafa2d8e528e58bc3296e2d808907862b8e6425808112cbc54ae00104",
}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(8 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")


def bad(ref, observed):
    mismatch = ~np.isfinite(observed) | ~np.isclose(ref, observed, atol=5e-5, rtol=5e-5)
    if not np.any(mismatch):
        return None
    idx = tuple(int(i) for i in np.argwhere(mismatch)[0])
    return {"index": idx, "reference": float(ref[idx]), "observed": str(observed[idx])}


@contextlib.contextmanager
def gpu_lock(mode):
    receipt_path = RAW / f"LOCK_{mode}.json"
    receipt = {"mode": mode, "path": str(LOCK), "pid": os.getpid(), "wait_begin_utc": now()}
    with LOCK.open("a+") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        receipt["acquired_utc"] = now()
        write_json(receipt_path, receipt)
        try:
            yield receipt
        finally:
            receipt["released_utc"] = now()
            receipt["terminal_status"] = receipt.get("terminal_status", "EXITED")
            write_json(receipt_path, receipt)
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def assets():
    for path, expected in EXPECTED.items():
        actual = sha(path)
        if actual != expected:
            raise RuntimeError(f"Parent asset SHA drift: {path} {actual} != {expected}")
    parent_pack = Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r21a-oeq-graph-readiness-109-v1/docs/vm_tlb/review_packs/AWMA_R21A_OEQ_GRAPH_READINESS_109_V1")
    model = parent_pack / "MODEL_AUTHORITY.json"
    input_authority = parent_pack / "INPUT_AUTHORITY.json"
    if json.loads(model.read_text())["sha256"] != "63d4bafd872850a014fd21dedeea416b61173a17750dee0b2b8dd2b126f407aa":
        raise RuntimeError("Model package drift")
    if json.loads(input_authority.read_text())["sha256"] != "c08d3771a06beb82b0ed4258f78eecc7ce623f73ca6df20be99bd5722163e770":
        raise RuntimeError("Input drift")


def setup_torch():
    os.environ.setdefault("TORCHINDUCTOR_CACHE_DIR", str(ROOT / "cache/inductor"))
    os.environ.setdefault("TRITON_CACHE_DIR", str(ROOT / "cache/triton"))
    os.environ.setdefault("CUDA_CACHE_PATH", str(ROOT / "cache/cuda"))
    import torch
    import openequivariance  # Registers the accepted libtorch_tp_jit operator schema before AOT load.
    from nequip.data import AtomicDataDict
    from nequip.model.inference_models import load_compiled_model
    torch.set_default_dtype(torch.float32)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_float32_matmul_precision("highest")
    return torch, AtomicDataDict, load_compiled_model


def reference():
    es, fs = [], []
    for repeat in range(5):
        with np.load(PARENT / f"raw/REFERENCE_DATA_RUN_{repeat}.npz", allow_pickle=False) as data:
            es.append(data["energy"].copy())
            fs.append(data["forces"].copy())
    return np.mean(np.stack(es), axis=0), np.mean(np.stack(fs), axis=0)


def load_arms(names, torch, ADD, loader):
    models, data = {}, {}
    for arm in names:
        package = DREADY if arm == "Dready" else A0
        graph = NATURAL if arm == "A0" else SORTED
        model, metadata = loader(str(package), device="cuda")
        with np.load(graph, allow_pickle=False) as source:
            tensors = {key: torch.from_numpy(source[key].copy()) for key in source.files if arm == "Dready" or key != ADD.EDGE_TRANSPOSE_PERM_KEY}
        models[arm] = model
        data[arm] = ADD.to_(tensors, device=torch.device("cuda"))
        expected_keys = ["pos", "edge_index", "atom_types", "cell", "edge_cell_shift"]
        if arm == "Dready":
            expected_keys += [ADD.EDGE_TRANSPOSE_PERM_KEY]
        if model.input_keys != expected_keys:
            raise RuntimeError(f"AOT signature drift {arm}: {model.input_keys}")
    return models, data


def call_and_check(arm, model, data, torch, ADD, ref_e, ref_f, save_path, timed=False, nvtx=None):
    torch.cuda.synchronize()
    if nvtx is not None:
        torch.cuda.nvtx.range_push(nvtx)
    try:
        start = torch.cuda.Event(enable_timing=True) if timed else None
        end = torch.cuda.Event(enable_timing=True) if timed else None
        t0 = time.perf_counter_ns() if timed else None
        if timed:
            start.record()
        output = model(dict(data))
        if timed:
            end.record()
        torch.cuda.synchronize()
        wall = (time.perf_counter_ns() - t0) / 1e6 if timed else None
        event = start.elapsed_time(end) if timed else None
    finally:
        if nvtx is not None:
            torch.cuda.nvtx.range_pop()
    energy = output[ADD.TOTAL_ENERGY_KEY].detach().cpu().numpy().copy()
    forces = output[ADD.FORCE_KEY].detach().cpu().numpy().copy()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(save_path, energy=energy, forces=forces)
    mismatch_e = bad(ref_e, energy) if energy.shape == ref_e.shape else {"shape": [list(ref_e.shape), list(energy.shape)]}
    mismatch_f = bad(ref_f, forces) if forces.shape == ref_f.shape else {"shape": [list(ref_f.shape), list(forces.shape)]}
    row = {"arm": arm, "wall_ms": wall, "cuda_event_ms": event, "numerical_pass": mismatch_e is None and mismatch_f is None,
           "first_energy_mismatch": mismatch_e, "first_force_mismatch": mismatch_f,
           "output_path": str(save_path), "output_sha256": sha(save_path)}
    if timed and not (math.isfinite(wall) and math.isfinite(event) and wall > 0 and event > 0):
        row["numerical_pass"] = False
        row["timer_error"] = "invalid_wall_or_event"
    return row


def mode_aorder(torch, ADD, loader, receipt):
    status = {"status": "STARTED", "arm": "Aorder", "A0_AOT_sha256": EXPECTED[A0],
              "sorted_graph_sha256": EXPECTED[SORTED], "repeat_count": 0,
              "timing": "NONE", "first_mismatch": None}
    path = RAW / "AORDER_QUALIFICATION_STATUS.json"
    write_json(path, status)
    models, data = load_arms(["Aorder"], torch, ADD, loader)
    ref_e, ref_f = reference()
    rows = []
    for repeat in range(5):
        row = call_and_check("Aorder", models["Aorder"], data["Aorder"], torch, ADD, ref_e, ref_f,
                             RAW / f"AORDER_RUN_{repeat}.npz")
        row["repeat"] = repeat
        rows.append(row)
        status["repeat_count"] = len(rows)
        status["rows"] = rows
        if not row["numerical_pass"]:
            status["status"] = "AORDER_NUMERIC_FAILURE"
            status["first_mismatch"] = row["first_energy_mismatch"] or row["first_force_mismatch"]
            write_json(path, status)
            raise RuntimeError(f"Aorder numerical failure repeat {repeat}")
        write_json(path, status)
    status["status"] = "AORDER_QUALIFIED"
    write_json(path, status)
    receipt["terminal_status"] = status["status"]
    print(json.dumps({"status": status["status"], "outputs": len(rows), "sorted_graph_sha256": EXPECTED[SORTED]}), flush=True)


def arm_order(names, block):
    if len(names) == 2:
        return names if block % 2 == 0 else list(reversed(names))
    return [names[(block + index) % 3] for index in range(3)]


def mode_profile(torch, ADD, loader, receipt, with_aorder):
    status_path = RAW / "PROFILE_RUN_STATUS.json"
    if status_path.exists():
        raise RuntimeError("Only one NSYS scientific profile is permitted")
    names = ["A0", "Aorder", "Dready"] if with_aorder else ["A0", "Dready"]
    status = {"status": "STARTED", "arms": names, "measured_count": 0, "planned_count": 3*4*len(names),
              "profiled_family_timing_evidence": "DIAGNOSTIC_ONLY", "first_mismatch": None}
    write_json(status_path, status)
    models, data = load_arms(names, torch, ADD, loader)
    ref_e, ref_f = reference()
    for arm in names:
        for warmup in range(2):
            row = call_and_check(arm, models[arm], data[arm], torch, ADD, ref_e, ref_f,
                                 RAW / f"PROFILE_WARMUP_{arm}_{warmup}.npz")
            if not row["numerical_pass"]:
                status.update({"status": "PROFILE_WARMUP_NUMERIC_FAILURE", "failed_row": row})
                write_json(status_path, status)
                raise RuntimeError("Profile warmup numeric failure")
    rows = []
    for block in range(3):
        order = arm_order(names, block)
        for cycle in range(4):
            for arm in order:
                label = f"R22F|arm={arm}|block={block}|repeat={cycle}|complete_energy_force"
                row = call_and_check(arm, models[arm], data[arm], torch, ADD, ref_e, ref_f,
                                     RAW / f"PROFILE_B{block}_{arm}_R{cycle}.npz", nvtx=label)
                row.update({"block": block, "repeat": cycle, "nvtx_label": label})
                rows.append(row)
                status["measured_count"] = len(rows)
                if not row["numerical_pass"]:
                    status.update({"status": "PROFILE_NUMERIC_FAILURE", "failed_row": row,
                                   "first_mismatch": row["first_energy_mismatch"] or row["first_force_mismatch"]})
                    write_json(status_path, status)
                    raise RuntimeError("Profile formal numeric failure")
                write_json(status_path, status)
    status.update({"status": "PROFILE_RUN_COMPLETE", "rows": rows})
    write_json(status_path, status)
    receipt["terminal_status"] = status["status"]
    print(json.dumps({"status": status["status"], "measured_count": len(rows), "arms": names}), flush=True)


def mode_formal(torch, ADD, loader, receipt, with_aorder):
    status_path = RAW / "FORMAL_RUN_STATUS.json"
    if status_path.exists():
        raise RuntimeError("No repeat formal timing")
    names = ["A0", "Aorder", "Dready"] if with_aorder else ["A0", "Dready"]
    status = {"status": "STARTED", "arms": names, "formal_count": 0, "planned_count": 4*6*len(names),
              "first_mismatch": None}
    write_json(status_path, status)
    models, data = load_arms(names, torch, ADD, loader)
    ref_e, ref_f = reference()
    for arm in names:
        for warmup in range(5):
            row = call_and_check(arm, models[arm], data[arm], torch, ADD, ref_e, ref_f,
                                 RAW / f"FORMAL_WARMUP_{arm}_{warmup}.npz")
            if not row["numerical_pass"]:
                status.update({"status": "WARMUP_NUMERIC_FAILURE", "failed_row": row})
                write_json(status_path, status)
                raise RuntimeError("Formal warmup numeric failure")
    rows = []
    for group in range(4):
        order = arm_order(names, group) if len(names) == 2 else (
            ["A0", "Dready", "Aorder"] if group == 3 else arm_order(names, group))
        for cycle in range(6):
            for arm in order:
                row = call_and_check(arm, models[arm], data[arm], torch, ADD, ref_e, ref_f,
                                     RAW / f"FORMAL_G{group}_{arm}_R{cycle}.npz", timed=True)
                row.update({"group": group, "repeat": cycle, "order": ",".join(order)})
                rows.append(row)
                status["formal_count"] = len(rows)
                if not row["numerical_pass"]:
                    status.update({"status": "FORMAL_NUMERIC_FAILURE", "failed_row": row,
                                   "first_mismatch": row["first_energy_mismatch"] or row["first_force_mismatch"]})
                    write_json(status_path, status)
                    raise RuntimeError("Formal numeric failure")
                write_json(status_path, status)
    with (RAW / "FORMAL_COMPLETE_TIMING.tsv").open("w", newline="") as stream:
        fields = ["group", "repeat", "order", "arm", "wall_ms", "cuda_event_ms", "numerical_pass", "output_path", "output_sha256"]
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: row[key] for key in fields} for row in rows)
    status.update({"status": "FORMAL_COMPLETE", "rows": rows})
    write_json(status_path, status)
    receipt["terminal_status"] = status["status"]
    print(json.dumps({"status": status["status"], "formal_count": len(rows), "arms": names}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["aorder", "profile", "formal"])
    parser.add_argument("--with-aorder", action="store_true")
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    assets()  # CPU-only hash qualification before any CUDA initialization.
    with gpu_lock(args.mode) as receipt:
        try:
            torch, ADD, loader = setup_torch()
            if args.mode == "aorder":
                mode_aorder(torch, ADD, loader, receipt)
            elif args.mode == "profile":
                mode_profile(torch, ADD, loader, receipt, args.with_aorder)
            else:
                mode_formal(torch, ADD, loader, receipt, args.with_aorder)
        except Exception as exc:
            receipt.update({"terminal_status": "FAILED", "error_type": type(exc).__name__, "error": str(exc),
                            "traceback_tail": traceback.format_exc()[-12000:]})
            raise


if __name__ == "__main__":
    main()
