#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gc
import json
import statistics
import time
import traceback
from pathlib import Path

import torch

from common import (
    ACCEPTED_ZERO_FILL_MS,
    ATOL,
    RTOL,
    backward_on_leaves,
    compare_outputs,
    fixed_meta,
    forward_backward,
    init_state_accounting,
    load_real_inputs,
    make_leaves,
    qualified,
    set_arm,
    tensor_bytes,
    write_json,
)


ARMS = ("C0", "C1")


def clone_output(value):
    return tuple(t.detach().clone() for t in value)


def time_one(arm, hidden, weight, labels):
    set_arm(arm)
    active_h, active_w = make_leaves(hidden, weight)
    torch.cuda.synchronize()
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    start.record()
    host_start = time.perf_counter_ns()
    loss = backward_on_leaves(arm, active_h, active_w, labels)
    end.record()
    torch.cuda.synchronize()
    host_ms = (time.perf_counter_ns() - host_start) / 1e6
    gpu_ms = start.elapsed_time(end)
    value = float(loss.detach().cpu())
    del loss, active_h, active_w, start, end
    gc.collect()
    return gpu_ms, host_ms, value


def memory_one(arm, hidden, weight, labels):
    set_arm(arm)
    active_h, active_w = make_leaves(hidden, weight)
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.synchronize()
    baseline_allocated = torch.cuda.memory_allocated()
    baseline_reserved = torch.cuda.memory_reserved()
    torch.cuda.reset_peak_memory_stats()
    loss = backward_on_leaves(arm, active_h, active_w, labels)
    torch.cuda.synchronize()
    result = {
        "baseline_allocated_bytes": baseline_allocated,
        "baseline_reserved_bytes": baseline_reserved,
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
        "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
        "peak_allocated_delta_bytes": torch.cuda.max_memory_allocated() - baseline_allocated,
        "peak_reserved_delta_bytes": torch.cuda.max_memory_reserved() - baseline_reserved,
        "mandatory_output_bytes": tensor_bytes(active_h.grad) + tensor_bytes(active_w.grad) + tensor_bytes(loss),
        "full_fp32_dc_bytes": weight.numel() * 4,
        "init_state": init_state_accounting(weight.shape[0], weight.shape[1]),
        "allocator_bytes_are_not_dram_traffic": True,
    }
    del loss, active_h, active_w
    gc.collect()
    torch.cuda.empty_cache()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    raw = args.root / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    campaign = {
        "stage": "AWMA_CCE_ZERO_INIT_REMOVAL_109_V1",
        "status": "RUNNING",
        "started_unix_ns": time.time_ns(),
    }
    try:
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA unavailable")
        meta = fixed_meta()
        hidden, weight, labels, input_receipt = load_real_inputs()
        input_receipt["fixed_meta"] = meta
        write_json(raw / "REAL_INPUT_RECEIPT.json", input_receipt)

        reference = clone_output(forward_backward("C0", hidden, weight, labels))
        candidate = clone_output(forward_backward("C1", hidden, weight, labels))
        torch.cuda.synchronize()
        metrics = compare_outputs(candidate, reference)
        numerical = {
            "stage": campaign["stage"],
            "atol": ATOL,
            "rtol": RTOL,
            "C0_C1": metrics,
            "qualified": qualified(metrics),
            "fixed_meta_C0": meta,
            "fixed_meta_C1": meta,
            "same_fixed_meta": True,
        }
        write_json(raw / "REAL_NUMERICAL_QUALIFICATION.json", numerical)
        if not numerical["qualified"]:
            campaign.update({
                "status": "COUNTERFACTUAL_NOT_QUALIFIED",
                "reason": "real numerical contract failed",
                "finished_unix_ns": time.time_ns(),
            })
            write_json(raw / "REAL_CAMPAIGN_RESULT.json", campaign)
            return
        del reference, candidate
        gc.collect()
        torch.cuda.empty_cache()

        memory = {arm: memory_one(arm, hidden, weight, labels) for arm in ARMS}
        write_json(raw / "MEMORY_ACCOUNTING.json", memory)

        samples = []
        orders = (("C0", "C1"), ("C1", "C0"), ("C0", "C1"))
        for group, order in enumerate(orders):
            for repeat in range(2):
                for position, arm in enumerate(order):
                    gpu_ms, host_ms, loss = time_one(arm, hidden, weight, labels)
                    samples.append({
                        "group": group,
                        "phase": "warmup",
                        "repeat": repeat,
                        "position": position,
                        "arm": arm,
                        "gpu_ms": gpu_ms,
                        "host_ms": host_ms,
                        "loss": loss,
                    })
            for repeat in range(5):
                for position, arm in enumerate(order):
                    gpu_ms, host_ms, loss = time_one(arm, hidden, weight, labels)
                    samples.append({
                        "group": group,
                        "phase": "formal",
                        "repeat": repeat,
                        "position": position,
                        "arm": arm,
                        "gpu_ms": gpu_ms,
                        "host_ms": host_ms,
                        "loss": loss,
                    })

        with (raw / "TIMING_SAMPLES.tsv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(samples[0]), delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(samples)

        summary = {}
        for arm in ARMS:
            formal = [row for row in samples if row["arm"] == arm and row["phase"] == "formal"]
            gpu = [row["gpu_ms"] for row in formal]
            host = [row["host_ms"] for row in formal]
            gpu_median = statistics.median(gpu)
            host_median = statistics.median(host)
            group_medians = {
                str(group): statistics.median(
                    row["gpu_ms"] for row in formal if row["group"] == group
                )
                for group in range(3)
            }
            summary[arm] = {
                "formal_samples": len(formal),
                "gpu_ms_median": gpu_median,
                "gpu_ms_mad": statistics.median(abs(value - gpu_median) for value in gpu),
                "host_ms_median": host_median,
                "host_ms_mad": statistics.median(abs(value - host_median) for value in host),
                "group_gpu_ms_medians": group_medians,
                "group_median_range_fraction": (
                    max(group_medians.values()) - min(group_medians.values())
                ) / gpu_median,
            }

        paired_groups = {}
        paired_deltas = []
        for group in range(3):
            group_deltas = []
            for repeat in range(5):
                c0 = next(row["gpu_ms"] for row in samples if row["phase"] == "formal" and row["group"] == group and row["repeat"] == repeat and row["arm"] == "C0")
                c1 = next(row["gpu_ms"] for row in samples if row["phase"] == "formal" and row["group"] == group and row["repeat"] == repeat and row["arm"] == "C1")
                group_deltas.append(c0 - c1)
                paired_deltas.append(c0 - c1)
            paired_groups[str(group)] = {
                "deltas_ms": group_deltas,
                "median_delta_ms": statistics.median(group_deltas),
            }
        delta = summary["C0"]["gpu_ms_median"] - summary["C1"]["gpu_ms_median"]
        analysis = {
            "C0": summary["C0"],
            "C1": summary["C1"],
            "median_delta_ms_C0_minus_C1": delta,
            "improvement_fraction": delta / summary["C0"]["gpu_ms_median"],
            "accepted_zero_fill_ms": ACCEPTED_ZERO_FILL_MS,
            "accepted_zero_fill_recovery_fraction": delta / ACCEPTED_ZERO_FILL_MS,
            "paired_delta_ms_median": statistics.median(paired_deltas),
            "paired_delta_ms_mad": statistics.median(
                abs(value - statistics.median(paired_deltas)) for value in paired_deltas
            ),
            "paired_groups": paired_groups,
            "decision_pending_nsys": True,
        }
        write_json(raw / "PAIRED_ANALYSIS.json", analysis)
        campaign.update({
            "status": "TIMING_COMPLETE_PENDING_NSYS",
            "numerical_qualified": True,
            "formal_samples_per_arm": 15,
            "warmups_per_arm": 6,
            "fixed_meta_equal": True,
            "finished_unix_ns": time.time_ns(),
        })
        write_json(raw / "REAL_CAMPAIGN_RESULT.json", campaign)
        print(json.dumps({"status": campaign["status"], "analysis": analysis}, sort_keys=True))
    except Exception as exc:
        campaign.update({
            "status": "FAILED",
            "error": repr(exc),
            "traceback": traceback.format_exc(),
            "finished_unix_ns": time.time_ns(),
        })
        write_json(raw / "REAL_CAMPAIGN_FAILURE.json", campaign)
        raise
    finally:
        if torch.cuda.is_initialized():
            torch.cuda.synchronize()
            torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
