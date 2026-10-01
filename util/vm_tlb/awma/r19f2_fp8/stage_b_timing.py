#!/usr/bin/env python3
"""Unprofiled paired S1/S2/D0 Stage B P/M formal timing."""

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
from torch.utils.cpp_extension import load


ROOT = Path("/data/c16/awma/r19f2_fp8_software_counterfactual_20261001")
RAW = ROOT / "raw"
SOURCE = Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r19f2-fp8-software-counterfactual-109-v1/util/vm_tlb/awma/r19f2_fp8")
ARMS = ("S1_SHARED", "S2_FUSED_SHARED", "D0_READY_PAIR")
ARM_ORDERS = (
    ("S1_SHARED", "S2_FUSED_SHARED", "D0_READY_PAIR"),
    ("S2_FUSED_SHARED", "D0_READY_PAIR", "S1_SHARED"),
    ("D0_READY_PAIR", "S1_SHARED", "S2_FUSED_SHARED"),
)
REGION_ORDERS = (("P", "M"), ("M", "P"), ("P", "M"))


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def tensor_sha(tensor):
    return hashlib.sha256(tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()


def med_mad(values):
    median = statistics.median(values)
    return median, statistics.median(abs(value - median) for value in values)


def main():
    assert os.environ.get("R19F2_GPU_LOCK_HELD") == "1"
    import transformer_engine.pytorch as te
    from transformer_engine.common import recipe

    source_cpp = SOURCE / "fused_current_scale.cpp"
    source_cu = SOURCE / "fused_current_scale.cu"
    fused_receipt = json.loads((RAW / "FUSED_REP_IDENTITY.json").read_text())
    identity = json.loads((RAW / "SHARED_REP_IDENTITY.json").read_text())
    authority = json.loads((RAW / "REAL_MLP_INPUT_WEIGHT_RECEIPT.json").read_text())
    stage_a = json.loads((RAW / "STAGE_A_TIMING_SUMMARY.json").read_text())
    assert fused_receipt["status"] == "EXACT_ONE_LAUNCH_FUSED_REP_QUALIFIED"
    assert file_sha(source_cpp) == fused_receipt["source_cpp_sha256"]
    assert file_sha(source_cu) == fused_receipt["source_cu_sha256"]
    extension = load(
        name="r19f2_fused_cs_v1",
        sources=[str(source_cpp), str(source_cu)],
        build_directory=str(ROOT / "build/fused_cs_v1"),
        extra_cflags=["-O3"],
        extra_cuda_cflags=["-O3", "--expt-relaxed-constexpr", "-arch=sm_89"],
        verbose=False,
    )
    assert file_sha(Path(extension.__file__).resolve()) == fused_receipt["extension_so_sha256"]
    payload = RAW / "QWEN25_LAYER0_MLP_REAL_X_GATE_UP_DOWN.pt"
    assert file_sha(payload) == authority["payload_sha256"]
    obj = torch.load(payload, map_location="cpu", weights_only=True)
    x = obj["input"].to("cuda:0")
    weights = {role: obj[f"{role}_weight"].to("cuda:0") for role in ("gate", "up", "down")}
    assert torch.cuda.get_device_capability(0) == (8, 9)
    blocks = torch.cuda.get_device_properties(0).multi_processor_count
    assert blocks == fused_receipt["cooperative_blocks"]
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
        cached = layers[role]._fp8_workspaces["weight"]
        assert tensor_sha(cached._data) == identity["cached_weight_before"][role]["data"]["sha256"]
        assert tensor_sha(cached._scale_inv) == identity["cached_weight_before"][role]["scale_inv"]["sha256"]
        cache_ptrs[role] = cached._data.data_ptr()

    quantizer = te.Float8CurrentScalingQuantizer(
        fp8_dtype=te.DType.kFloat8E4M3,
        device=x.device,
        rowwise=True,
        columnwise=False,
        force_pow_2_scales=False,
    )
    q_ready = quantizer(x)
    q_fused = quantizer.create_tensor_from_data(torch.empty(x.shape, dtype=torch.uint8, device=x.device), fake_dtype=torch.bfloat16, internal=False)
    amax = torch.empty((1,), dtype=torch.float32, device=x.device)
    torch.cuda.synchronize()
    assert tensor_sha(q_ready._data) == fused_receipt["fp8_data_sha256"]
    assert tensor_sha(q_ready._scale_inv) == fused_receipt["inverse_scale_sha256"]
    q_fused_data_ptr = q_fused._data.data_ptr()
    q_fused_scale_ptr = q_fused._scale_inv.data_ptr()

    def invoke(arm, region):
        with torch.no_grad(), te.autocast(enabled=True, recipe=fp8_recipe):
            if arm == "D0_READY_PAIR":
                q = q_ready
            elif arm == "S1_SHARED":
                q = quantizer(x)
            else:
                extension.fused_current_scale_(x, q_fused._data, q_fused._scale_inv, amax, blocks)
                q = q_fused
            gate = layers["gate"](q, is_first_microbatch=False)
            up = layers["up"](q, is_first_microbatch=False)
        if region == "P":
            return gate, up
        return F.linear(F.silu(gate) * up, weights["down"])

    expected = {key: identity["output_ids"]["B0_DUPLICATE"][key]["sha256"] for key in ("gate", "up", "mlp")}

    def verify_outputs():
        for arm in ARMS:
            gate, up = invoke(arm, "P")
            mlp = invoke(arm, "M")
            torch.cuda.synchronize()
            assert tensor_sha(gate) == expected["gate"]
            assert tensor_sha(up) == expected["up"]
            assert tensor_sha(mlp) == expected["mlp"]
            assert torch.isfinite(gate).all() and torch.isfinite(up).all() and torch.isfinite(mlp).all()
            del gate, up, mlp
        assert tensor_sha(q_fused._data) == fused_receipt["fp8_data_sha256"]
        assert tensor_sha(q_fused._scale_inv) == fused_receipt["inverse_scale_sha256"]
        assert q_fused._data.data_ptr() == q_fused_data_ptr
        assert q_fused._scale_inv.data_ptr() == q_fused_scale_ptr
        for role in layers:
            cached = layers[role]._fp8_workspaces["weight"]
            assert cached._data.data_ptr() == cache_ptrs[role]
            assert tensor_sha(cached._data) == identity["cached_weight_before"][role]["data"]["sha256"]
            assert tensor_sha(cached._scale_inv) == identity["cached_weight_before"][role]["scale_inv"]["sha256"]

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
                        output = invoke(arm, region)
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
                        del output
    finally:
        if old_gc:
            gc.enable()
    verify_outputs()
    allocation = {}
    for region in ("P", "M"):
        allocation[region] = {}
        for arm in ARMS:
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()
            before = torch.cuda.memory_allocated()
            output = invoke(arm, region)
            torch.cuda.synchronize()
            allocation[region][arm] = {
                "allocated_before_bytes": before,
                "allocated_with_output_bytes": torch.cuda.memory_allocated(),
                "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
                "peak_reserved_bytes": torch.cuda.max_memory_reserved(),
            }
            del output
    assert tensor_sha(q_fused._data) == fused_receipt["fp8_data_sha256"]
    assert tensor_sha(q_fused._scale_inv) == fused_receipt["inverse_scale_sha256"]

    summary = {
        "stage": "AWMA_R19F2_FP8_SOFTWARE_COUNTERFACTUAL_109_V1",
        "payload_sha256": authority["payload_sha256"],
        "extension_so_sha256": fused_receipt["extension_so_sha256"],
        "s2_preallocated_fp8_data_and_inverse_scale": True,
        "source_exact_one_launch": True,
        "arm_orders": ARM_ORDERS,
        "region_orders": REGION_ORDERS,
        "warmups_per_arm_per_group_per_region": 2,
        "formal_samples_per_arm_per_group_per_region": 5,
        "allocation_probe_not_primary": allocation,
        "stage_a_frozen_B0_D0_wall_medians": {
            region: {
                arm: stage_a["regions"][region]["wall_ms"]["arms"][arm]["median"]
                for arm in ("B0_DUPLICATE", "D0_READY_PAIR")
            }
            for region in ("P", "M")
        },
        "regions": {},
    }
    for region in ("P", "M"):
        rows = samples[region]
        assert len(rows) == 45
        with (RAW / f"STAGE_B_TIMING_{region}.tsv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        region_result = {}
        for metric in ("wall_ms", "cuda_event_ms"):
            arms = {}
            for arm in ARMS:
                values = [row[metric] for row in rows if row["arm"] == arm]
                assert len(values) == 15
                med, mad = med_mad(values)
                arms[arm] = {"median": med, "mad": mad, "min": min(values), "max": max(values)}
            pairs = {}
            for left, right in (("S1_SHARED", "S2_FUSED_SHARED"), ("S2_FUSED_SHARED", "D0_READY_PAIR"), ("S1_SHARED", "D0_READY_PAIR")):
                group_info = []
                for group in range(3):
                    gaps = []
                    for repeat in range(5):
                        lv = next(row[metric] for row in rows if row["group"] == group and row["repeat"] == repeat and row["arm"] == left)
                        rv = next(row[metric] for row in rows if row["group"] == group and row["repeat"] == repeat and row["arm"] == right)
                        gaps.append(lv - rv)
                    group_info.append({"group": group, "paired_gaps_ms": gaps, "paired_gap_median_ms": statistics.median(gaps)})
                left_med, right_med = arms[left]["median"], arms[right]["median"]
                pairs[f"{left}_minus_{right}"] = {
                    "median_gap_ms": left_med - right_med,
                    "relative_gap_pct_of_left": (left_med - right_med) / left_med * 100,
                    "all_three_group_gaps_positive": all(g["paired_gap_median_ms"] > 0 for g in group_info),
                    "gap_gt_3x_larger_arm_mad": (left_med - right_med) > 3 * max(arms[left]["mad"], arms[right]["mad"]),
                    "groups": group_info,
                }
            s1 = arms["S1_SHARED"]["median"]
            s2 = arms["S2_FUSED_SHARED"]["median"]
            d0 = arms["D0_READY_PAIR"]["median"]
            region_result[metric] = {
                "arms": arms,
                "pairs": pairs,
                "S1_to_D0_ideal_ms": s1 - d0,
                "S1_to_S2_recovered_ms": s1 - s2,
                "S2_to_D0_remaining_ms": s2 - d0,
                "fused_fraction_of_positive_S1_to_D0_recovered": ((s1 - s2) / (s1 - d0)) if s1 > d0 else None,
            }
        summary["regions"][region] = region_result
    (RAW / "STAGE_B_TIMING_SUMMARY.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    compact = {
        "P_wall_medians": {arm: summary["regions"]["P"]["wall_ms"]["arms"][arm]["median"] for arm in ARMS},
        "M_wall_medians": {arm: summary["regions"]["M"]["wall_ms"]["arms"][arm]["median"] for arm in ARMS},
        "M_S2_remaining_pct": summary["regions"]["M"]["wall_ms"]["pairs"]["S2_FUSED_SHARED_minus_D0_READY_PAIR"]["relative_gap_pct_of_left"],
        "M_S2_recovered_fraction": summary["regions"]["M"]["wall_ms"]["fused_fraction_of_positive_S1_to_D0_recovered"],
    }
    print(json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    main()
