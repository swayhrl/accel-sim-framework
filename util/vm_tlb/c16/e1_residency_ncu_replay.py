#!/usr/bin/env python3
"""Exact single-target residency-intervention replay for semantic NCU."""

import argparse
import json
from pathlib import Path

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


ROOT = Path("/data/c16/e1_residency_intervention_v1")
CODE_INPUT_SHA = "8617167912ed3cc89d5821b8621cde092374638a099965b4e1fe2a9fec4e6077"
CODE_OUTPUTS = {
    "RAW_FP16": "bfe831b628e7941de2a50222f0d9d6ed3f3dbb5e38a5861dc28276c00f156512",
    "AWQ_FP16_INPUT": "8138405fa621da78b51b5d050493a2140a5a5725a85519a8d91c61c2b8d0978a",
}


def range_name(input_kind, role, matrix_m, implementation, state):
    short_impl = "RAW" if implementation == "RAW_FP16" else "AWQ"
    return f"C16_E1_RES_{input_kind}_{role.upper()}_M{matrix_m}_{short_impl}_{state}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-kind", choices=("TEXT", "CODE"), required=True)
    parser.add_argument("--role", choices=("q_proj", "down_proj", "up_proj"), required=True)
    parser.add_argument("--M", type=int, required=True)
    parser.add_argument("--impl", choices=("RAW_FP16", "AWQ_FP16_INPUT"), required=True)
    parser.add_argument("--state", choices=("WARM", "SPARSE_PAGE_PRESSURE", "DENSE_MEMORY_PRESSURE", "DOSE64"), required=True)
    args = parser.parse_args()

    # The pressure allocation and its initialization precede target module construction.
    pressure = torch.ones(PRESSURE_ELEMENTS, dtype=torch.float32, device="cuda")
    torch.cuda.synchronize()
    module, owner = load_single_module(args.role, args.impl)
    if args.input_kind == "TEXT":
        tensor = load_text_input(args.role, args.M)
        accepted = accepted_text_points()[(args.role, args.M, args.impl)]
        expected_input = accepted["input_sha"]
        expected_output = accepted["output_sha"]
    else:
        if not (args.role == "down_proj" and args.M == 1):
            raise RuntimeError("CODE authority is frozen to down_proj M1")
        tensor = torch.load(ROOT / "CODE_DOWN_PROJ_M1_FP16_INPUT.pt", map_location="cpu", weights_only=True).cuda()
        expected_input = CODE_INPUT_SHA
        expected_output = CODE_OUTPUTS[args.impl]
    input_sha = tensor_sha(tensor)
    if input_sha != expected_input:
        raise RuntimeError(f"input authority mismatch: {input_sha}")

    with torch.inference_mode():
        warm(module, tensor)
        if args.state == "SPARSE_PAGE_PRESSURE":
            pressure_ms = pressure_touch(pressure, "SPARSE_PAGE_PRESSURE")
        elif args.state == "DENSE_MEMORY_PRESSURE":
            pressure_ms = pressure_touch(pressure, "DENSE_MEMORY_PRESSURE")
        elif args.state == "DOSE64":
            pressure_ms = pressure_touch(pressure, "DENSE_DOSE", 64 * 1024 * 1024)
        else:
            pressure_ms = 0.0
        name = range_name(args.input_kind, args.role, args.M, args.impl, args.state)
        torch.cuda.nvtx.range_push(name)
        output = module(tensor)
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_pop()
    output_sha = tensor_sha(output)
    if output_sha != expected_output:
        raise RuntimeError(f"output authority mismatch: {output_sha}")
    print(
        json.dumps(
            {
                "status": "PASS",
                "input_kind": args.input_kind,
                "role": args.role,
                "M": args.M,
                "implementation": args.impl,
                "state": args.state,
                "range": name,
                "input_sha256": input_sha,
                "output_sha256": output_sha,
                "module_class": type(module).__name__,
                "pressure_buffer_ptr": pressure.data_ptr(),
                "pressure_buffer_bytes": pressure.numel() * pressure.element_size(),
                "pressure_ms": pressure_ms,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
