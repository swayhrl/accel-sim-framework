#!/usr/bin/env python3
"""Exact AWQ M1 capacity-knee dose replay with one selected target range."""

import argparse
import json

import torch

from e1_residency_common import (
    PRESSURE_ELEMENTS,
    accepted_text_points,
    load_single_module,
    load_text_input,
    pressure_touch,
    tensor_sha,
    warm,
)


DOSES = {
    "q_proj": (0, 32, 48, 56, 60, 64, 72, 96),
    "down_proj": (0, 16, 24, 28, 32, 36, 48, 64),
    "up_proj": (0, 16, 24, 28, 30, 32, 36, 40, 48, 64),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=tuple(DOSES), required=True)
    parser.add_argument("--dose-mib", type=int, required=True)
    args = parser.parse_args()
    if args.dose_mib not in DOSES[args.role]:
        raise RuntimeError("dose outside frozen role matrix")
    pressure = torch.ones(PRESSURE_ELEMENTS, dtype=torch.float32, device="cuda")
    torch.cuda.synchronize()
    module, owner = load_single_module(args.role, "AWQ_FP16_INPUT")
    tensor = load_text_input(args.role, 1)
    authority = accepted_text_points()[(args.role, 1, "AWQ_FP16_INPUT")]
    input_sha = tensor_sha(tensor)
    if input_sha != authority["input_sha"]:
        raise RuntimeError("knee input authority mismatch")
    name = f"C16_E1_KNEE_{args.role.upper()}_{args.dose_mib}MIB"
    with torch.inference_mode():
        warm(module, tensor)
        pressure_ms = pressure_touch(pressure, "DENSE_DOSE", args.dose_mib * 1024 * 1024)
        torch.cuda.nvtx.range_push(name)
        output = module(tensor)
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_pop()
    output_sha = tensor_sha(output)
    if output_sha != authority["output_sha"]:
        raise RuntimeError("knee output authority mismatch")
    print(
        json.dumps(
            {
                "status": "PASS",
                "role": args.role,
                "M": 1,
                "implementation": "AWQ_FP16_INPUT",
                "dose_mib": args.dose_mib,
                "range": name,
                "input_sha256": input_sha,
                "output_sha256": output_sha,
                "module_class": type(module).__name__,
                "pressure_ms": pressure_ms,
                "pressure_buffer_bytes": pressure.numel() * pressure.element_size(),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
