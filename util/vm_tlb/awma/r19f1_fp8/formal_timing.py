#!/usr/bin/env python3
"""Uninstrumented paired A1-online vs D0-ready same-consumer TE timing."""

import csv
import gc
import hashlib
import json
import os
import statistics
import time
from pathlib import Path

import torch


ROOT = Path("/data/c16/awma/r19f1_fp8_numeric_decomposition_20261001/raw")
PAYLOAD = ROOT / "QWEN25_LAYER0_UP_PROJ_REAL_INPUT_WEIGHT.pt"


def tensor_sha(tensor):
    data = tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()
    return hashlib.sha256(data).hexdigest()


def med_mad(values):
    med = statistics.median(values)
    return med, statistics.median(abs(v - med) for v in values)


def main():
    assert os.environ.get("R19F1_GPU_LOCK_HELD") == "1"
    import transformer_engine.pytorch as te
    from transformer_engine.common import recipe

    receipt = json.loads((ROOT / "REPRESENTATION_RECEIPT.json").read_text())
    profile = json.loads((ROOT / "NSYS_KERNEL_IDENTITY_SUMMARY.json").read_text())
    assert receipt["rep_matched_numeric_gate_pass"]
    assert receipt["D0_preliminary_exact_safe_qualified"]
    assert hashlib.sha256(PAYLOAD.read_bytes()).hexdigest() == receipt["payload_sha256"]
    phases = profile["phases"]
    a_gemms = [s for s in phases["R19F1_A1_ONLINE"]["strata"] if "sm89_xmma_gemm_e4m3" in s["function"]]
    d_gemms = [s for s in phases["R19F1_D0_READY"]["strata"] if "sm89_xmma_gemm_e4m3" in s["function"]]
    assert len(a_gemms) == len(d_gemms) == 1
    assert a_gemms[0]["count"] == d_gemms[0]["count"] == 3
    assert (a_gemms[0]["function"], a_gemms[0]["grid"], a_gemms[0]["block"]) == (
        d_gemms[0]["function"], d_gemms[0]["grid"], d_gemms[0]["block"]
    )
    assert phases["R19F1_D0_READY"]["kernel_count"] == 3
    assert phases["R19F1_A1_ONLINE"]["kernel_count"] == 15

    obj = torch.load(PAYLOAD, map_location="cpu", weights_only=True)
    x = obj["input"].to("cuda:0")
    w = obj["weight"].to("cuda:0")
    assert torch.cuda.get_device_capability(0) == (8, 9)
    fp8_recipe = recipe.Float8CurrentScaling(fp8_format=recipe.Format.E4M3)
    layer = te.Linear(896, 4864, bias=False, params_dtype=torch.bfloat16, device="cuda:0").eval()
    with torch.no_grad():
        layer.weight.copy_(w)
    layer.requires_grad_(False)
    with torch.no_grad(), te.autocast(enabled=True, recipe=fp8_recipe):
        layer(x, is_first_microbatch=True)
        layer(x, is_first_microbatch=False)
    torch.cuda.synchronize()
    q_weight = layer._fp8_workspaces["weight"]
    assert tensor_sha(q_weight._data) == receipt["cached_weight_representation"]["data"]["sha256"]
    assert tensor_sha(q_weight._scale_inv) == receipt["cached_weight_representation"]["scale_inv"]["sha256"]
    weight_ptr = q_weight._data.data_ptr()
    q_ready = te.Float8CurrentScalingQuantizer(
        fp8_dtype=te.DType.kFloat8E4M3,
        device=x.device,
        rowwise=True,
        columnwise=False,
        force_pow_2_scales=False,
    )(x)
    torch.cuda.synchronize()
    assert tensor_sha(q_ready._data) == receipt["online_input_representation"]["data"]["sha256"]
    assert tensor_sha(q_ready._scale_inv) == receipt["online_input_representation"]["scale_inv"]["sha256"]

    def invoke(arm):
        with torch.no_grad(), te.autocast(enabled=True, recipe=fp8_recipe):
            if arm == "A1_ONLINE":
                return layer(x, is_first_microbatch=False)
            return layer(q_ready, is_first_microbatch=False)

    a = invoke("A1_ONLINE")
    d = invoke("D0_READY")
    torch.cuda.synchronize()
    assert torch.equal(a, d)
    assert tensor_sha(a) == receipt["F0_TE_FP8"]["sha256"]
    del a, d

    start_event = torch.cuda.Event(enable_timing=True)
    end_event = torch.cuda.Event(enable_timing=True)
    samples = []
    group_orders = [("A1_ONLINE", "D0_READY"), ("D0_READY", "A1_ONLINE"), ("A1_ONLINE", "D0_READY")]
    old_gc = gc.isenabled()
    gc.disable()
    try:
        for group, order in enumerate(group_orders):
            for arm in order:
                for _ in range(2):
                    warm = invoke(arm)
                    torch.cuda.synchronize()
                    del warm
            for repeat in range(5):
                for arm in order:
                    torch.cuda.synchronize()
                    start_event.record()
                    begin_ns = time.perf_counter_ns()
                    output = invoke(arm)
                    end_event.record()
                    torch.cuda.synchronize()
                    end_ns = time.perf_counter_ns()
                    samples.append({
                        "group": group,
                        "repeat": repeat,
                        "order": ">".join(order),
                        "arm": arm,
                        "wall_ms": (end_ns - begin_ns) / 1e6,
                        "cuda_event_ms": start_event.elapsed_time(end_event),
                        "output_shape": "x".join(str(v) for v in output.shape),
                    })
                    del output
    finally:
        if old_gc:
            gc.enable()

    # These allocation probes are outside formal timing and never feed it.
    memory = {}
    for arm in ("A1_ONLINE", "D0_READY"):
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        before = torch.cuda.memory_allocated()
        y = invoke(arm)
        torch.cuda.synchronize()
        memory[arm] = {
            "allocated_before_bytes": before,
            "allocated_with_output_bytes": torch.cuda.memory_allocated(),
            "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
            "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
        }
        del y
    a = invoke("A1_ONLINE")
    d = invoke("D0_READY")
    torch.cuda.synchronize()
    assert torch.equal(a, d)
    assert tensor_sha(a) == receipt["F0_TE_FP8"]["sha256"]
    assert tensor_sha(q_weight._data) == receipt["cached_weight_representation"]["data"]["sha256"]
    assert q_weight._data.data_ptr() == weight_ptr

    tsv = ROOT / "TIMING.tsv"
    with tsv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(samples[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(samples)

    summary = {
        "stage": "AWMA_R19F1_FP8_NUMERIC_DECOMPOSITION_109_V1",
        "sample_count_per_arm": 15,
        "warmups_per_arm_per_group": 2,
        "group_orders": group_orders,
        "boundary": "arm-ready input -> te.Linear current-scaling FP8 output synchronized",
        "allocation_probe_not_primary": memory,
        "producer_payload_sha256": receipt["payload_sha256"],
        "online_input_q_sha256": receipt["online_input_representation"]["data"]["sha256"],
        "ready_input_q_sha256": tensor_sha(q_ready._data),
        "cached_weight_q_sha256": tensor_sha(q_weight._data),
        "same_consumer_function": a_gemms[0]["function"],
        "same_consumer_grid": a_gemms[0]["grid"],
        "same_consumer_block": a_gemms[0]["block"],
        "metrics": {},
    }
    for metric in ("wall_ms", "cuda_event_ms"):
        arms = {}
        for arm in ("A1_ONLINE", "D0_READY"):
            vals = [r[metric] for r in samples if r["arm"] == arm]
            med, mad = med_mad(vals)
            arms[arm] = {"median": med, "mad": mad, "min": min(vals), "max": max(vals)}
        groups = []
        for group in range(3):
            pair_differences = []
            for repeat in range(5):
                a_val = next(r[metric] for r in samples if r["group"] == group and r["repeat"] == repeat and r["arm"] == "A1_ONLINE")
                d_val = next(r[metric] for r in samples if r["group"] == group and r["repeat"] == repeat and r["arm"] == "D0_READY")
                pair_differences.append(a_val - d_val)
            groups.append({"group": group, "paired_gap_median_ms": statistics.median(pair_differences), "paired_gaps_ms": pair_differences})
        a_med = arms["A1_ONLINE"]["median"]
        d_med = arms["D0_READY"]["median"]
        summary["metrics"][metric] = {
            "arms": arms,
            "group_paired_differences": groups,
            "median_gap_ms": a_med - d_med,
            "relative_reduction_pct": (a_med - d_med) / a_med * 100,
            "all_group_gap_sign_positive": all(g["paired_gap_median_ms"] > 0 for g in groups),
            "gap_gt_3x_larger_arm_mad": (a_med - d_med) > 3 * max(arms["A1_ONLINE"]["mad"], arms["D0_READY"]["mad"]),
        }
    wall = summary["metrics"]["wall_ms"]
    gpu = summary["metrics"]["cuda_event_ms"]
    summary["investment_screen_pass"] = (
        wall["relative_reduction_pct"] >= 5
        and wall["all_group_gap_sign_positive"]
        and wall["gap_gt_3x_larger_arm_mad"]
        and gpu["all_group_gap_sign_positive"]
    )
    (ROOT / "TIMING_SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
