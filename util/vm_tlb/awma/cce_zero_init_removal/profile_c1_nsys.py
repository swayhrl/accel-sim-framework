#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from common import backward_on_leaves, fixed_meta, load_real_inputs, make_leaves, set_arm


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    hidden, weight, labels, receipt = load_real_inputs()
    meta = fixed_meta()
    for _ in range(2):
        set_arm("C1")
        active_h, active_w = make_leaves(hidden, weight)
        loss = backward_on_leaves("C1", active_h, active_w, labels)
        torch.cuda.synchronize()
        del active_h, active_w, loss
    set_arm("C1")
    active_h, active_w = make_leaves(hidden, weight)
    torch.cuda.synchronize()
    torch.cuda.cudart().cudaProfilerStart()
    loss = backward_on_leaves("C1", active_h, active_w, labels)
    torch.cuda.synchronize()
    torch.cuda.cudart().cudaProfilerStop()
    print(json.dumps({
        "status": "PROFILE_COMPLETE",
        "arm": "C1",
        "loss": float(loss.detach().cpu()),
        "fixed_meta": meta,
        "input": receipt,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
