#!/usr/bin/env python3
"""Native isolated positive-control timing for exact qweight persistence."""

import json
from pathlib import Path

import torch
from awq import AutoAWQForCausalLM

from e1_cuda_persistence import PersistenceHelper, qweight_region
from e1_residency_common import AWQ, PRESSURE_ELEMENTS, accepted_text_points, cuda_timed, load_text_input, pressure_touch, tensor_sha, warm


OUT = Path("/data/c16/e1_l2_persistence_intervention_v1/isolated")


def main():
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite {OUT}")
    OUT.mkdir(parents=True)
    pressure = torch.ones(PRESSURE_ELEMENTS, dtype=torch.float32, device="cuda")
    torch.cuda.synchronize()
    model = AutoAWQForCausalLM.from_quantized(AWQ, fuse_layers=False)
    module = model.model.model.layers[0].mlp.up_proj
    qweight = module.qweight
    qweight_bytes = qweight.numel() * qweight.element_size()
    tensor = load_text_input("up_proj", 1)
    authority = accepted_text_points()[("up_proj", 1, "AWQ_FP16_INPUT")]
    if tensor_sha(tensor) != authority["input_sha"]:
        raise RuntimeError("isolated input identity")
    helper = PersistenceHelper()
    rows = []
    conditions = ("ISO_BASELINE_DENSE", "ISO_QWEIGHT_PERSIST_DENSE")
    for repetition in range(9):
        order = conditions if repetition % 2 == 0 else tuple(reversed(conditions))
        for condition in order:
            persistent = condition == "ISO_QWEIGHT_PERSIST_DENSE"
            receipt = helper.begin_condition(condition, qweight_bytes if persistent else 0, qweight if persistent else None, 1.0)
            try:
                with torch.inference_mode():
                    warm(module, tensor)
                    pressure_ms = pressure_touch(pressure, "DENSE_MEMORY_PRESSURE")
                    output, target_ms = cuda_timed(lambda: module(tensor))
                output_sha = tensor_sha(output)
                if output_sha != authority["output_sha"]:
                    raise RuntimeError("isolated output identity")
            finally:
                receipt = helper.end_condition(receipt)
            rows.append(
                {
                    "condition": condition,
                    "repetition": repetition,
                    "target_ms": target_ms,
                    "pressure_ms": pressure_ms,
                    "input_sha256": authority["input_sha"],
                    "output_sha256": output_sha,
                    "policy_receipt": receipt,
                }
            )
    result = {
        "status": "PASS",
        "qweight_region": qweight_region(module, "layer0.mlp.up_proj.qweight"),
        "rows": rows,
    }
    (OUT / "NATIVE_RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "rows": len(rows), "qweight_bytes": qweight_bytes}, sort_keys=True))


if __name__ == "__main__":
    main()
