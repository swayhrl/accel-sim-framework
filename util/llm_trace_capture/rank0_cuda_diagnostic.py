#!/usr/bin/env python3
"""Tiny real-GPU Route-E rank/injection proof; intentionally model-free."""
from __future__ import annotations

import json
import os

import torch
import torch.distributed as dist


def main() -> int:
    rank, local_rank, world = int(os.environ["RANK"]), int(os.environ["LOCAL_RANK"]), int(os.environ["WORLD_SIZE"])
    if world != 4:
        raise RuntimeError(f"Route-E diagnostic requires WORLD_SIZE=4, got {world}")
    # P4 proves rank placement and injection, rather than NCCL performance.
    # Gloo prevents a NCCL watchdog from expiring while rank 0 performs
    # NVBit's one-time CUDA module instrumentation.  P5 tests real TP=4/NCCL.
    dist.init_process_group("gloo")
    torch.cuda.set_device(local_rank)
    value = torch.tensor([rank], dtype=torch.int64, device="cuda")
    torch.cuda.synchronize()
    details = {"rank": rank, "local_rank": local_rank, "world_size": world,
               "cuda_injection64_path": os.environ.get("CUDA_INJECTION64_PATH", "ABSENT"),
               "device": torch.cuda.get_device_name(local_rank),
               "capability": list(torch.cuda.get_device_capability(local_rank)),
               "process_group_backend": dist.get_backend(),
               "cuda_sync_value": int(value.item())}
    print("M4A_RANK_DIAGNOSTIC=" + json.dumps(details, sort_keys=True), flush=True)
    dist.barrier(); dist.destroy_process_group(); return 0


if __name__ == "__main__":
    raise SystemExit(main())
