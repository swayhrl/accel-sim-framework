#!/usr/bin/env python3
"""Frozen CPU-safe contracts for the GPT-3 public-shape scale-transfer screen."""
from __future__ import annotations

import hashlib
import json
import math
import struct

SYNTH_VERSION = "GPT3_SHAPE_SYNTH_V1"
GROUP_SIZE = 128
L2_BYTES = 67_108_864
CONDITIONER_BYTES = 268_435_456
DEVICE_CAPACITY_BYTES = 16 * 1024**3
WORKSPACE_RESERVE_BYTES = 4 * 1024**3
A_BINARY_SHA256 = "9e8d38a04c28770338fcef8ae0f9a90a984b7a8f95bcb98a407738594e1c08d7"
B_BINARY_SHA256 = "1aa8db13f5fd10651aa4241f58200e3a7075214d34cca4d70fbcbe7cbbc07887"
QWEIGHT_WORD_U32 = 0xECA86420
QWEIGHT_WORD_I32 = QWEIGHT_WORD_U32 - (1 << 32)
QZERO_WORD_U32 = 0x77777777
QZERO_WORD_I32 = QZERO_WORD_U32
SCALE = 2.0**-8
EXPECTED_TINY_REFERENCE_SHA256 = "bc5b86bb5c440be4fa308f3c6d85922297148cf911cad8a33e0d3373928a7e3e"

POINTS = (
    {"point": "EXPAND_M1", "operator": "EXPAND", "M": 1, "K": 12288, "N": 49152},
    {"point": "EXPAND_M256", "operator": "EXPAND", "M": 256, "K": 12288, "N": 49152},
    {"point": "CONTRACT_M1", "operator": "CONTRACT", "M": 1, "K": 49152, "N": 12288},
    {"point": "CONTRACT_M256", "operator": "CONTRACT", "M": 256, "K": 49152, "N": 12288},
)


def dense_input_value(m: int, k: int) -> float:
    return (1 + ((3 * m + k) % 7)) * 2.0**-10


def dense_weight_value(k: int, n: int) -> float:
    return (1 + ((5 * k + n) % 11)) * 2.0**-12


def w4_input_value(m: int, k: int) -> float:
    return (1 + ((5 * m + 3 * k) % 7)) * 2.0**-10


def packed_nibbles(word: int) -> list[int]:
    return [(word >> (4 * index)) & 0xF for index in range(8)]


def dequantized_nibbles() -> list[float]:
    q = packed_nibbles(QWEIGHT_WORD_U32)
    z = packed_nibbles(QZERO_WORD_U32)
    return [(a - b) * SCALE for a, b in zip(q, z)]


def point_math(point: dict, split: int) -> dict:
    m, k, n = point["M"], point["K"], point["N"]
    if k % GROUP_SIZE or n % 128 or n % 8:
        raise ValueError(f"unsupported static divisibility: {point}")
    return {
        "grid": math.ceil(m / 16) * (n // 128) * split,
        "scratch_bytes": split * m * n * 2,
        "input_bytes": m * k * 2,
        "output_bytes": m * n * 2,
        "dense_parameter_count": k * n,
        "dense_weight_bytes": k * n * 2,
        "qweight_shape": [k, n // 8],
        "qweight_bytes": k * (n // 8) * 4,
        "qzeros_shape": [k // GROUP_SIZE, n // 8],
        "qzeros_bytes": (k // GROUP_SIZE) * (n // 8) * 4,
        "scales_shape": [k // GROUP_SIZE, n],
        "scales_bytes": (k // GROUP_SIZE) * n * 2,
    }


def canonical_tables() -> tuple[list[dict], list[dict]]:
    budget_rows, launch_rows = [], []
    for point in POINTS:
        a = point_math(point, 8)
        b = point_math(point, 1)
        w4_weight_bytes = a["qweight_bytes"] + a["qzeros_bytes"] + a["scales_bytes"]
        dense_peak = a["dense_weight_bytes"] + a["input_bytes"] + a["output_bytes"] + WORKSPACE_RESERVE_BYTES
        # A is the maximum W4 arm. Keep A result and B result simultaneously for correctness.
        w4_peak = (
            w4_weight_bytes
            + a["input_bytes"]
            + 2 * a["output_bytes"]
            + a["scratch_bytes"]
            + CONDITIONER_BYTES
            + WORKSPACE_RESERVE_BYTES
        )
        common = {
            "point": point["point"], "operator": point["operator"], "M": point["M"], "K": point["K"], "N": point["N"],
            "dense_parameter_count": a["dense_parameter_count"], "dense_weight_bytes": a["dense_weight_bytes"],
            "qweight_shape": json.dumps(a["qweight_shape"], separators=(",", ":")), "qweight_bytes": a["qweight_bytes"],
            "qzeros_shape": json.dumps(a["qzeros_shape"], separators=(",", ":")), "qzeros_bytes": a["qzeros_bytes"],
            "scales_shape": json.dumps(a["scales_shape"], separators=(",", ":")), "scales_bytes": a["scales_bytes"],
            "w4_weight_total_bytes": w4_weight_bytes, "input_bytes": a["input_bytes"], "output_bytes": a["output_bytes"],
            "qweight_over_l2": a["qweight_bytes"] / L2_BYTES,
            "dense_peak_bound_bytes": dense_peak, "w4_peak_bound_bytes": w4_peak,
            "max_peak_bound_bytes": max(dense_peak, w4_peak), "device_capacity_bytes": DEVICE_CAPACITY_BYTES,
            "headroom_bytes": DEVICE_CAPACITY_BYTES - max(dense_peak, w4_peak),
            "peak_fraction_of_16GiB": max(dense_peak, w4_peak) / DEVICE_CAPACITY_BYTES,
        }
        budget_rows.append(common)
        for arm, split, values in (("A", 8, a), ("B", 1, b)):
            launch_rows.append({
                "point": point["point"], "operator": point["operator"], "M": point["M"], "K": point["K"], "N": point["N"],
                "arm": arm, "split_k_iters": split, "gemm_grid": values["grid"], "gemm_block": "[32,2,1]",
                "scratch_shape": json.dumps([split, point["M"], point["N"]], separators=(",", ":")),
                "scratch_bytes": values["scratch_bytes"], "reduction_expected": arm == "A",
                "reduction_grid": math.ceil(point["M"] * point["N"] / 512) if arm == "A" else 0,
                "reduction_block": "[32,4,1]" if arm == "A" else "NA",
            })
    return budget_rows, launch_rows


def _half_bytes(values) -> bytes:
    return b"".join(struct.pack("<e", float(value)) for value in values)


def _int32_bytes(values) -> bytes:
    return b"".join(struct.pack("<i", int(value)) for value in values)


def tiny_reference() -> dict:
    m, k, n = 2, 256, 16
    tensors = {
        "dense_input_f16": _half_bytes(dense_input_value(i, j) for i in range(m) for j in range(k)),
        "dense_weight_f16": _half_bytes(dense_weight_value(i, j) for i in range(k) for j in range(n)),
        "w4_input_f16": _half_bytes(w4_input_value(i, j) for i in range(m) for j in range(k)),
        "qweight_i32": _int32_bytes(QWEIGHT_WORD_I32 for _ in range(k * (n // 8))),
        "qzeros_i32": _int32_bytes(QZERO_WORD_I32 for _ in range((k // GROUP_SIZE) * (n // 8))),
        "scales_f16": _half_bytes(SCALE for _ in range((k // GROUP_SIZE) * n)),
    }
    per_tensor = {name: hashlib.sha256(value).hexdigest() for name, value in tensors.items()}
    manifest = {
        "version": SYNTH_VERSION,
        "shape": {"M": m, "K": k, "N": n, "group_size": GROUP_SIZE},
        "byte_order": "little-endian; IEEE-754 binary16 and signed int32 two's complement",
        "tensor_sha256": per_tensor,
    }
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    manifest["reference_sha256"] = hashlib.sha256(canonical).hexdigest()
    return manifest
