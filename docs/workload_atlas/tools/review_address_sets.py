#!/usr/bin/env python3
"""Enumerate source-derived byte address sets; never executes a workload."""
import json
from pathlib import Path


def units(addresses, width, unit):
    return {byte // unit for address in addresses for byte in range(address, address + width)}


def summarize(addresses, width=4):
    return {"unique_start_addresses": len(set(addresses)), "lines128": len(units(addresses, width, 128)), "sectors32": len(units(addresses, width, 32))}


def main():
    n = 4096
    # Interior full warp; allocation base and row starts 128-byte aligned.
    out = {}
    out["strided_row_thread_A"] = summarize([4 * ((32 + lane) * n + 64) for lane in range(32)])
    out["contiguous_column_thread_A"] = summarize([4 * (64 * n + 32 + lane) for lane in range(32)])
    out["uniform_vector_load"] = summarize([4 * 64] * 32)
    out["gemm_A_broadcast"] = summarize([4 * (8 * 512 + 64)] * 32)
    out["gemm_B_row"] = summarize([4 * (64 * 512 + 32 + lane) for lane in range(32)])
    out["conv2d_left_tap"] = summarize([4 * (64 * n + 32 + lane - 1) for lane in range(32)])
    out["conv2d_center_tap"] = summarize([4 * (64 * n + 32 + lane) for lane in range(32)])
    out["conv2d_right_tap"] = summarize([4 * (64 * n + 32 + lane + 1) for lane in range(32)])
    out["conv2d_nine_tap_union"] = summarize([4 * ((64 + dy) * n + 32 + lane + dx) for dy in [-1, 0, 1] for dx in [-1, 0, 1] for lane in range(32)])
    out["conv2d_interior_CTA_input_union"] = summarize([4 * ((64 + ty + dy) * n + 32 + tx + dx) for ty in range(8) for tx in range(32) for dy in [-1, 0, 1] for dx in [-1, 0, 1]])
    out["pf_naive_CDF_uniform_step"] = summarize([8 * 64] * 32, width=8)
    out["pf_naive_output_contiguous"] = summarize([8 * (32 + lane) for lane in range(32)], width=8)
    expected = {"strided_row_thread_A": (32, 32), "contiguous_column_thread_A": (1, 4), "uniform_vector_load": (1, 1), "gemm_A_broadcast": (1, 1), "gemm_B_row": (1, 4), "conv2d_left_tap": (2, 5), "conv2d_center_tap": (1, 4), "conv2d_right_tap": (2, 5), "conv2d_nine_tap_union": (9, 18), "conv2d_interior_CTA_input_union": (30, 60), "pf_naive_CDF_uniform_step": (1, 1), "pf_naive_output_contiguous": (2, 8)}
    for key, pair in expected.items():
        assert (out[key]["lines128"], out[key]["sectors32"]) == pair, (key, out[key])
    assert out["conv2d_nine_tap_union"]["unique_start_addresses"] == 3 * 34
    assert out["conv2d_interior_CTA_input_union"]["unique_start_addresses"] == 10 * 34
    result = {"status": "PASS", "kind": "SOURCE_DERIVED_ADDRESS_ENUMERATION_NOT_RUNTIME", "conditions": ["32-lane full interior warp", "FP32 except particlefilter FP64", "allocation base and row starts 128B aligned", "4096 row pitch except GEMM512", "line/sector sets ignore issue time, cache state and compiler transformations"], "cases": out}
    dest = Path(__file__).resolve().parents[1] / "ADDRESS_REVIEW_VALIDATION.json"
    dest.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "cases": len(out), "output": str(dest)}))


if __name__ == "__main__":
    main()
