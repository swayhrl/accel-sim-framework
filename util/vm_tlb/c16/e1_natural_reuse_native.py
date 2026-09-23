#!/usr/bin/env python3
"""Native refill-sequence and role-specific capacity-knee measurements."""

import gc
import json
from pathlib import Path

import torch
from awq import AutoAWQForCausalLM

from e1_residency_common import (
    AWQ,
    PRESSURE_ELEMENTS,
    accepted_text_points,
    cuda_timed,
    dense_fp16_copy,
    load_raw_layer_cpu,
    load_text_input,
    pressure_touch,
    role_module,
    tensor_sha,
    warm,
)


OUT = Path("/data/c16/e1_natural_reuse_residency_v1")
DOSES = {
    "q_proj": [0, 32, 48, 56, 60, 64, 72, 96],
    "down_proj": [0, 16, 24, 28, 32, 36, 48, 64],
    "up_proj": [0, 16, 24, 28, 30, 32, 36, 40, 48, 64],
}


def main():
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite {OUT}")
    OUT.mkdir(parents=True)

    # Reuse one initialized accepted-size pressure allocation for all native work.
    pressure = torch.ones(PRESSURE_ELEMENTS, dtype=torch.float32, device="cuda")
    torch.cuda.synchronize()

    _, raw_layer, _ = load_raw_layer_cpu()
    raw_modules = {role: dense_fp16_copy(role_module(raw_layer, role)) for role in ("q_proj", "down_proj", "up_proj")}
    del raw_layer
    gc.collect()
    torch.cuda.empty_cache()
    awq_model = AutoAWQForCausalLM.from_quantized(AWQ, fuse_layers=False)
    awq_layer = awq_model.model.model.layers[0]
    awq_modules = {role: role_module(awq_layer, role) for role in ("q_proj", "down_proj", "up_proj")}

    accepted = accepted_text_points()
    inputs = {role: load_text_input(role, 1) for role in ("q_proj", "down_proj", "up_proj")}
    for role, tensor in inputs.items():
        for implementation in ("RAW_FP16", "AWQ_FP16_INPUT"):
            if tensor_sha(tensor) != accepted[(role, 1, implementation)]["input_sha"]:
                raise RuntimeError(f"input authority mismatch: {role} {implementation}")

    points = [(role, implementation) for role in ("q_proj", "down_proj", "up_proj") for implementation in ("RAW_FP16", "AWQ_FP16_INPUT")]
    refill_rows = []
    with torch.inference_mode():
        for repetition in range(9):
            ordered = points[repetition % len(points):] + points[:repetition % len(points)]
            for role, implementation in ordered:
                module = raw_modules[role] if implementation == "RAW_FP16" else awq_modules[role]
                tensor = inputs[role]
                expected_output = accepted[(role, 1, implementation)]["output_sha"]
                warm(module, tensor)
                pressure_ms = pressure_touch(pressure, "DENSE_MEMORY_PRESSURE")
                event_pairs = []
                outputs = []
                # No pressure, synchronization, hashing, or unrelated module call occurs between K1..K6.
                for call_index in range(1, 7):
                    start = torch.cuda.Event(enable_timing=True)
                    stop = torch.cuda.Event(enable_timing=True)
                    start.record()
                    output = module(tensor)
                    stop.record()
                    event_pairs.append((start, stop))
                    outputs.append(output)
                torch.cuda.synchronize()
                for call_index, ((start, stop), output) in enumerate(zip(event_pairs, outputs), start=1):
                    output_sha = tensor_sha(output)
                    if output_sha != expected_output:
                        raise RuntimeError(f"refill output mismatch: {role} {implementation} K{call_index}")
                    refill_rows.append(
                        {
                            "role": role,
                            "M": 1,
                            "implementation": implementation,
                            "repetition": repetition,
                            "call_index": call_index,
                            "target_ms": float(start.elapsed_time(stop)),
                            "pressure_ms": pressure_ms,
                            "input_sha256": tensor_sha(tensor),
                            "output_sha256": output_sha,
                        }
                    )

    knee_rows = []
    roles = ["q_proj", "down_proj", "up_proj"]
    with torch.inference_mode():
        for repetition in range(7):
            ordered_roles = roles[repetition % len(roles):] + roles[:repetition % len(roles)]
            for role in ordered_roles:
                module = awq_modules[role]
                tensor = inputs[role]
                expected_output = accepted[(role, 1, "AWQ_FP16_INPUT")]["output_sha"]
                doses = DOSES[role]
                ordered_doses = doses[repetition % len(doses):] + doses[:repetition % len(doses)]
                for dose_mib in ordered_doses:
                    warm(module, tensor)
                    pressure_ms = pressure_touch(pressure, "DENSE_DOSE", dose_mib * 1024 * 1024)
                    output, target_ms = cuda_timed(lambda: module(tensor))
                    output_sha = tensor_sha(output)
                    if output_sha != expected_output:
                        raise RuntimeError(f"knee output mismatch: {role} {dose_mib}")
                    knee_rows.append(
                        {
                            "role": role,
                            "M": 1,
                            "implementation": "AWQ_FP16_INPUT",
                            "dose_mib": dose_mib,
                            "repetition": repetition,
                            "target_ms": target_ms,
                            "pressure_ms": pressure_ms,
                            "input_sha256": tensor_sha(tensor),
                            "output_sha256": output_sha,
                        }
                    )

    result = {
        "status": "PASS",
        "pressure_buffer": {
            "bytes": pressure.numel() * pressure.element_size(),
            "dtype": str(pressure.dtype),
            "data_ptr": pressure.data_ptr(),
            "initialized_before_modules": True,
        },
        "refill_rows": refill_rows,
        "knee_doses_mib": DOSES,
        "knee_rows": knee_rows,
    }
    (OUT / "NATIVE_REFILL_KNEE_RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "refill_samples": len(refill_rows), "knee_samples": len(knee_rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
