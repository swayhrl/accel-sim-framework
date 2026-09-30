#!/usr/bin/env python3
"""Single bounded NSYS target for the fastest qualified strong arm (B1)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from safetensors import safe_open

from run_exact_loss import arm_forward, make_liger, tensor_sha


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--model-root", type=Path, required=True)
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable")
    runtime = json.loads((args.root / "raw" / "RUNTIME_INPUT_RECEIPT.json").read_text())
    snapshot = torch.load(args.root / "raw" / "REAL_FINAL_HIDDEN_AND_LABELS.pt", map_location="cpu", weights_only=True)
    hidden = snapshot["hidden"].to("cuda:0")
    labels = snapshot["labels"].to("cuda:0")
    with safe_open(args.model_root / "model.safetensors", framework="pt", device="cpu") as source:
        weight = source.get_tensor(runtime["checkpoint_tensor_key"]).to("cuda:0")
    if tensor_sha(hidden) != runtime["hidden_sha256"]:
        raise RuntimeError("hidden identity mismatch")
    if tensor_sha(weight) != runtime["lm_head_sha256"]:
        raise RuntimeError("weight identity mismatch")
    liger = make_liger()
    for _ in range(2):
        h = hidden.detach().clone().requires_grad_(True)
        w = weight.detach().clone().requires_grad_(True)
        loss = arm_forward("B1", h, w, labels, liger)
        loss.backward()
        torch.cuda.synchronize()
        del h, w, loss
    h = hidden.detach().clone().requires_grad_(True)
    w = weight.detach().clone().requires_grad_(True)
    torch.cuda.synchronize()
    torch.cuda.cudart().cudaProfilerStart()
    loss = arm_forward("B1", h, w, labels, liger)
    loss.backward()
    torch.cuda.synchronize()
    torch.cuda.cudart().cudaProfilerStop()
    print(json.dumps({"status": "PROFILE_COMPLETE", "loss": float(loss.detach().cpu()), "arm": "B1"}))


if __name__ == "__main__":
    main()
