#!/usr/bin/env python3
"""Unprofiled paired Stage A P/M timing on exact Qwen TE sibling consumers."""

import csv
import gc
import hashlib
import json
import os
import statistics
import time
from pathlib import Path

import torch
import torch.nn.functional as F


ROOT = Path("/data/c16/awma/r19f2_fp8_software_counterfactual_20261001/raw")
PAYLOAD = ROOT / "QWEN25_LAYER0_MLP_REAL_X_GATE_UP_DOWN.pt"
ARMS = ("B0_DUPLICATE", "S1_SHARED", "D0_READY_PAIR")
ARM_ORDERS = (
    ("B0_DUPLICATE", "S1_SHARED", "D0_READY_PAIR"),
    ("S1_SHARED", "D0_READY_PAIR", "B0_DUPLICATE"),
    ("D0_READY_PAIR", "B0_DUPLICATE", "S1_SHARED"),
)
REGION_ORDERS = (("P", "M"), ("M", "P"), ("P", "M"))


def tensor_sha(tensor):
    data = tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()
    return hashlib.sha256(data).hexdigest()


def med_mad(values):
    med = statistics.median(values)
    return med, statistics.median(abs(v - med) for v in values)


def main():
    assert os.environ.get("R19F2_GPU_LOCK_HELD") == "1"
    import transformer_engine.pytorch as te
    from transformer_engine.common import recipe

    authority = json.loads((ROOT / "REAL_MLP_INPUT_WEIGHT_RECEIPT.json").read_text())
    identity = json.loads((ROOT / "SHARED_REP_IDENTITY.json").read_text())
    profile = json.loads((ROOT / "NSYS_CONSUMER_SUMMARY.json").read_text())
    assert identity["gate_output_bitwise_identical_all_arms"]
    assert identity["up_output_bitwise_identical_all_arms"]
    assert identity["mlp_output_bitwise_identical_all_arms"]
    assert profile["range_count"] == 9
    assert "sm89_xmma_gemm_e4m3" in profile["consumer_function"]
    assert profile["consumer_grid"] == "4,38,1"
    assert profile["consumer_block"] == "128,1,1"
    assert hashlib.sha256(PAYLOAD.read_bytes()).hexdigest() == authority["payload_sha256"]
    assert torch.cuda.get_device_capability(0) == (8, 9)
    obj = torch.load(PAYLOAD, map_location="cpu", weights_only=True)
    x = obj["input"].to("cuda:0")
    weights = {role: obj[f"{role}_weight"].to("cuda:0") for role in ("gate", "up", "down")}
    fp8_recipe = recipe.Float8CurrentScaling(fp8_format=recipe.Format.E4M3)
    layers = {}
    for role in ("gate", "up"):
        layer = te.Linear(896, 4864, bias=False, params_dtype=torch.bfloat16, device="cuda:0").eval()
        with torch.no_grad():
            layer.weight.copy_(weights[role])
        layer.requires_grad_(False)
        layers[role] = layer
        with torch.no_grad(), te.autocast(enabled=True, recipe=fp8_recipe):
            layer(x, is_first_microbatch=True)
            layer(x, is_first_microbatch=False)
    torch.cuda.synchronize()
    cache_ptrs = {}
    for role in layers:
        weight_cache = layers[role]._fp8_workspaces["weight"]
        assert tensor_sha(weight_cache._data) == identity["cached_weight_before"][role]["data"]["sha256"]
        assert tensor_sha(weight_cache._scale_inv) == identity["cached_weight_before"][role]["scale_inv"]["sha256"]
        cache_ptrs[role] = weight_cache._data.data_ptr()
    q_shared = te.Float8CurrentScalingQuantizer(
        fp8_dtype=te.DType.kFloat8E4M3,
        device=x.device,
        rowwise=True,
        columnwise=False,
        force_pow_2_scales=False,
    )
    q_ready = q_shared(x)
    torch.cuda.synchronize()
    assert tensor_sha(q_ready._data) == identity["shared_input"]["data"]["sha256"]
    assert tensor_sha(q_ready._scale_inv) == identity["shared_input"]["scale_inv"]["sha256"]

    def invoke(arm, region):
        with torch.no_grad(), te.autocast(enabled=True, recipe=fp8_recipe):
            if arm == "B0_DUPLICATE":
                gate = layers["gate"](x, is_first_microbatch=False)
                up = layers["up"](x, is_first_microbatch=False)
            else:
                quantized = q_ready if arm == "D0_READY_PAIR" else q_shared(x)
                gate = layers["gate"](quantized, is_first_microbatch=False)
                up = layers["up"](quantized, is_first_microbatch=False)
        if region == "P":
            return gate, up
        hidden = F.silu(gate) * up
        return F.linear(hidden, weights["down"])

    expected = identity["output_ids"]["B0_DUPLICATE"]

    def verify_outputs():
        for arm in ARMS:
            gate, up = invoke(arm, "P")
            mlp = invoke(arm, "M")
            torch.cuda.synchronize()
            assert tensor_sha(gate) == expected["gate"]["sha256"]
            assert tensor_sha(up) == expected["up"]["sha256"]
            assert tensor_sha(mlp) == expected["mlp"]["sha256"]
            assert torch.isfinite(gate).all() and torch.isfinite(up).all() and torch.isfinite(mlp).all()
            del gate, up, mlp

    verify_outputs()
    start_event = torch.cuda.Event(enable_timing=True)
    end_event = torch.cuda.Event(enable_timing=True)
    samples = {"P": [], "M": []}
    old_gc = gc.isenabled()
    gc.disable()
    try:
        for group in range(3):
            arm_order = ARM_ORDERS[group]
            for region in REGION_ORDERS[group]:
                for arm in arm_order:
                    for _ in range(2):
                        warm = invoke(arm, region)
                        torch.cuda.synchronize()
                        del warm
                for repeat in range(5):
                    for arm in arm_order:
                        torch.cuda.synchronize()
                        start_event.record()
                        begin = time.perf_counter_ns()
                        result = invoke(arm, region)
                        end_event.record()
                        torch.cuda.synchronize()
                        end = time.perf_counter_ns()
                        samples[region].append({
                            "group": group,
                            "repeat": repeat,
                            "arm_order": ">".join(arm_order),
                            "region_order": ">".join(REGION_ORDERS[group]),
                            "arm": arm,
                            "wall_ms": (end - begin) / 1e6,
                            "cuda_event_ms": start_event.elapsed_time(end_event),
                        })
                        del result
    finally:
        if old_gc:
            gc.enable()
    verify_outputs()
    for role in layers:
        weight_cache = layers[role]._fp8_workspaces["weight"]
        assert weight_cache._data.data_ptr() == cache_ptrs[role]
        assert tensor_sha(weight_cache._data) == identity["cached_weight_before"][role]["data"]["sha256"]
        assert tensor_sha(weight_cache._scale_inv) == identity["cached_weight_before"][role]["scale_inv"]["sha256"]

    allocation = {}
    for region in ("P", "M"):
        allocation[region] = {}
        for arm in ARMS:
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()
            before = torch.cuda.memory_allocated()
            result = invoke(arm, region)
            torch.cuda.synchronize()
            allocation[region][arm] = {
                "allocated_before_bytes": before,
                "allocated_with_output_bytes": torch.cuda.memory_allocated(),
                "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
                "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
            }
            del result

    summary = {
        "stage": "AWMA_R19F2_FP8_SOFTWARE_COUNTERFACTUAL_109_V1",
        "payload_sha256": authority["payload_sha256"],
        "region_boundaries": {
            "P": "X BF16 ready -> gate+up outputs synchronized",
            "M": "X BF16 ready -> gate+up -> silu*up -> down output synchronized",
        },
        "same_consumer_function": profile["consumer_function"],
        "same_consumer_grid": profile["consumer_grid"],
        "same_consumer_block": profile["consumer_block"],
        "arm_orders": ARM_ORDERS,
        "region_orders": REGION_ORDERS,
        "warmups_per_arm_per_group_per_region": 2,
        "formal_samples_per_arm_per_group_per_region": 5,
        "allocation_probe_not_primary": allocation,
        "input_representation_bytes": identity["shared_input"]["data"]["bytes"],
        "input_inverse_scale_bytes": identity["shared_input"]["scale_inv"]["bytes"],
        "cached_weight_bytes": {role: identity["cached_weight_before"][role]["data"]["bytes"] for role in layers},
        "logical_input_quantizer_invocations_per_arm": identity["logical_input_quantizer_invocations_per_arm"],
        "regions": {},
    }
    for region in ("P", "M"):
        rows = samples[region]
        assert len(rows) == 45
        path = ROOT / f"STAGE_A_TIMING_{region}.tsv"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        region_result = {}
        for metric in ("wall_ms", "cuda_event_ms"):
            arm_stats = {}
            for arm in ARMS:
                values = [row[metric] for row in rows if row["arm"] == arm]
                assert len(values) == 15
                median, mad = med_mad(values)
                arm_stats[arm] = {"median": median, "mad": mad, "min": min(values), "max": max(values)}
            pairs = {}
            for left, right in (("B0_DUPLICATE", "S1_SHARED"), ("S1_SHARED", "D0_READY_PAIR"), ("B0_DUPLICATE", "D0_READY_PAIR")):
                group_stats = []
                for group in range(3):
                    gaps = []
                    for repeat in range(5):
                        lv = next(row[metric] for row in rows if row["group"] == group and row["repeat"] == repeat and row["arm"] == left)
                        rv = next(row[metric] for row in rows if row["group"] == group and row["repeat"] == repeat and row["arm"] == right)
                        gaps.append(lv - rv)
                    group_stats.append({"group": group, "paired_gaps_ms": gaps, "paired_gap_median_ms": statistics.median(gaps)})
                left_med = arm_stats[left]["median"]
                right_med = arm_stats[right]["median"]
                pairs[f"{left}_minus_{right}"] = {
                    "median_gap_ms": left_med - right_med,
                    "relative_gap_pct_of_left": (left_med - right_med) / left_med * 100,
                    "all_three_group_gaps_positive": all(g["paired_gap_median_ms"] > 0 for g in group_stats),
                    "gap_gt_3x_larger_arm_mad": (left_med - right_med) > 3 * max(arm_stats[left]["mad"], arm_stats[right]["mad"]),
                    "groups": group_stats,
                }
            b0 = arm_stats["B0_DUPLICATE"]["median"]
            s1 = arm_stats["S1_SHARED"]["median"]
            d0 = arm_stats["D0_READY_PAIR"]["median"]
            recovered = ((b0 - s1) / (b0 - d0)) if b0 > d0 else None
            region_result[metric] = {
                "arms": arm_stats,
                "pairs": pairs,
                "H_ideal_ms": b0 - d0,
                "H_shared_ms": b0 - s1,
                "R_remaining_ms": s1 - d0,
                "shared_fraction_of_positive_ideal_recovered": recovered,
            }
        summary["regions"][region] = region_result
    (ROOT / "STAGE_A_TIMING_SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    compact = {
        "P_wall_medians": {arm: summary["regions"]["P"]["wall_ms"]["arms"][arm]["median"] for arm in ARMS},
        "M_wall_medians": {arm: summary["regions"]["M"]["wall_ms"]["arms"][arm]["median"] for arm in ARMS},
        "P_remaining_pct": summary["regions"]["P"]["wall_ms"]["pairs"]["S1_SHARED_minus_D0_READY_PAIR"]["relative_gap_pct_of_left"],
        "M_remaining_pct": summary["regions"]["M"]["wall_ms"]["pairs"]["S1_SHARED_minus_D0_READY_PAIR"]["relative_gap_pct_of_left"],
        "M_recovered_fraction": summary["regions"]["M"]["wall_ms"]["shared_fraction_of_positive_ideal_recovered"],
    }
    print(json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    main()
