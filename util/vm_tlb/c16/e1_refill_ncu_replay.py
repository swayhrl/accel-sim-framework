#!/usr/bin/env python3
"""Exact post-pressure K1..K6 refill replay with one selected Ki NVTX range."""

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=("q_proj", "down_proj", "up_proj"), required=True)
    parser.add_argument("--impl", choices=("RAW_FP16", "AWQ_FP16_INPUT"), required=True)
    parser.add_argument("--selected-k", type=int, choices=(1, 2, 4), required=True)
    args = parser.parse_args()

    pressure = torch.ones(PRESSURE_ELEMENTS, dtype=torch.float32, device="cuda")
    torch.cuda.synchronize()
    module, owner = load_single_module(args.role, args.impl)
    tensor = load_text_input(args.role, 1)
    authority = accepted_text_points()[(args.role, 1, args.impl)]
    input_sha = tensor_sha(tensor)
    if input_sha != authority["input_sha"]:
        raise RuntimeError("refill input authority mismatch")
    short_impl = "RAW" if args.impl == "RAW_FP16" else "AWQ"
    name = f"C16_E1_REFILL_{args.role.upper()}_{short_impl}_K{args.selected_k}"
    selected_output = None
    with torch.inference_mode():
        warm(module, tensor)
        pressure_ms = pressure_touch(pressure, "DENSE_MEMORY_PRESSURE")
        outputs = []
        for call_index in range(1, 7):
            if call_index == args.selected_k:
                torch.cuda.nvtx.range_push(name)
            output = module(tensor)
            if call_index == args.selected_k:
                torch.cuda.nvtx.range_pop()
                selected_output = output
            outputs.append(output)
        torch.cuda.synchronize()
    output_sha = tensor_sha(selected_output)
    if output_sha != authority["output_sha"]:
        raise RuntimeError("refill output authority mismatch")
    print(
        json.dumps(
            {
                "status": "PASS",
                "role": args.role,
                "M": 1,
                "implementation": args.impl,
                "selected_k": args.selected_k,
                "range": name,
                "input_sha256": input_sha,
                "output_sha256": output_sha,
                "module_class": type(module).__name__,
                "pressure_ms": pressure_ms,
                "pressure_buffer_bytes": pressure.numel() * pressure.element_size(),
                "sequence_calls": 6,
                "no_intervening_pressure_or_target_calls": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
