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
    dist.init_process_group("nccl")
    torch.cuda.set_device(local_rank)
    value = torch.tensor([rank], dtype=torch.int64, device="cuda")
    dist.all_reduce(value)
    details = {"rank": rank, "local_rank": local_rank, "world_size": world,
               "cuda_injection64_path": os.environ.get("CUDA_INJECTION64_PATH", "ABSENT"),
               "device": torch.cuda.get_device_name(local_rank),
               "capability": list(torch.cuda.get_device_capability(local_rank)),
               "all_reduce_rank_sum": int(value.item())}
    print("M4A_RANK_DIAGNOSTIC=" + json.dumps(details, sort_keys=True), flush=True)
    if int(value.item()) != 6:
        raise RuntimeError("four-rank synchronization/all-reduce failed")
    dist.barrier(); dist.destroy_process_group(); return 0


if __name__ == "__main__":
    raise SystemExit(main())
