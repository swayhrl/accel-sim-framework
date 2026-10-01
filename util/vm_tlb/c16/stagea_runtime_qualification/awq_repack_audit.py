#!/usr/bin/env python3
"""CPU-only full-checkpoint canonical AWQ repack identity audit."""

import argparse
import hashlib
import json
import os
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""

import torch
from safetensors import safe_open


ORDER = torch.tensor([0, 4, 1, 5, 2, 6, 3, 7], dtype=torch.long)
SHIFTS = torch.arange(0, 32, 4, dtype=torch.int32)


def tensor_sha(tensor):
    return hashlib.sha256(tensor.contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()


def canonical_awq(tensor):
    unpacked = (tensor.unsqueeze(-1) >> SHIFTS) & 15
    return unpacked[:, :, ORDER].reshape(tensor.shape[0], -1).to(torch.uint8).contiguous()


def convert_qweight(tensor):
    logical = canonical_awq(tensor).to(torch.int32)
    k, n = logical.shape
    return (logical.reshape(k // 8, 8, n) << SHIFTS[None, :, None]).sum(dim=1, dtype=torch.int32).contiguous()


def unpack_standard_qweight(tensor):
    unpacked = ((tensor.unsqueeze(-1) >> SHIFTS) & 15).to(torch.uint8)
    return unpacked.permute(0, 2, 1).reshape(tensor.shape[0] * 8, tensor.shape[1]).contiguous()


def convert_qzeros(tensor):
    logical = canonical_awq(tensor).to(torch.int32)
    groups, n = logical.shape
    transposed = logical.T.contiguous()
    return (transposed.reshape(n // 8, 8, groups) << SHIFTS[None, :, None]).sum(dim=1, dtype=torch.int32).contiguous()


def unpack_standard_qzeros(tensor):
    unpacked = ((tensor.unsqueeze(-1) >> SHIFTS) & 15).to(torch.uint8)
    return unpacked.permute(1, 0, 2).reshape(tensor.shape[1], tensor.shape[0] * 8).contiguous()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if torch.cuda.is_available() or torch.cuda.is_initialized():
        raise RuntimeError("CUDA visible during CPU repack audit")
    model_file = args.model / "model.safetensors"
    rows = []
    with safe_open(model_file, framework="pt", device="cpu") as handle:
        names = sorted(name for name in handle.keys() if name.endswith((".qweight", ".qzeros", ".scales")))
        for index, name in enumerate(names):
            tensor = handle.get_tensor(name)
            if name.endswith(".qweight"):
                before = canonical_awq(tensor)
                converted = convert_qweight(tensor)
                after = unpack_standard_qweight(converted)
                kind = "qweight"
            elif name.endswith(".qzeros"):
                before = canonical_awq(tensor)
                converted = convert_qzeros(tensor)
                after = unpack_standard_qzeros(converted)
                kind = "qzeros"
            else:
                before = tensor.contiguous().view(torch.uint8)
                converted = tensor.contiguous()
                after = converted.view(torch.uint8)
                kind = "scales"
            equal = torch.equal(before, after)
            if not equal:
                raise RuntimeError(f"canonical repack mismatch: {name}")
            rows.append({"name": name, "kind": kind, "source_shape": list(tensor.shape),
                         "converted_shape": list(converted.shape), "source_dtype": str(tensor.dtype),
                         "source_raw_sha256": tensor_sha(tensor),
                         "canonical_before_sha256": tensor_sha(before),
                         "canonical_after_sha256": tensor_sha(after), "status": "PASS"})
            if (index + 1) % 100 == 0:
                print(f"AUDITED {index + 1}/{len(names)}", flush=True)
    counts = {kind: sum(row["kind"] == kind for row in rows) for kind in ("qweight", "qzeros", "scales")}
    result = {"status": "PASS", "model": str(args.model), "tensor_counts": counts,
              "all_canonical_before_after_exact": all(row["status"] == "PASS" for row in rows),
              "no_requantization": True, "cuda_initialized": torch.cuda.is_initialized(),
              "algorithm": "pinned vLLM _convert_awq_to_standard_format semantics",
              "source_path": "vllm/model_executor/layers/quantization/auto_awq.py",
              "source_sha256": hashlib.sha256((args.source / "vllm/model_executor/layers/quantization/auto_awq.py").read_bytes()).hexdigest(),
              "rows": rows}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "tensor_counts": counts}, sort_keys=True))


if __name__ == "__main__":
    main()
