#!/usr/bin/env python3
"""Bounded native runner; Torch/CUDA imports occur only in explicit GPU modes."""

import argparse
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import statistics
import sys

M, N, GROUP, REPLICAS = 256, 49152, 128, 16
KS = (2560, 3072)
STATES = {"SHARED": 0, "PER_MTILE": 15}
MIRROR = ((8, "SHARED"), (1, "SHARED"), (8, "PER_MTILE"), (1, "PER_MTILE"),
          (1, "PER_MTILE"), (8, "PER_MTILE"), (1, "SHARED"), (8, "SHARED"))


def load_gpu(extension_path):
    import torch
    name = "awq_crossm_replica_ext"
    spec = importlib.util.spec_from_file_location(name, extension_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load extension: {extension_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return torch, module


def make_assets(torch, k):
    device = "cuda:0"
    qweight = torch.full((REPLICAS, k, N // 8), -324508640, dtype=torch.int32, device=device)
    qzeros = torch.full((REPLICAS, k // GROUP, N // 8), 2004318071, dtype=torch.int32, device=device)
    scales = torch.full((REPLICAS, k // GROUP, N), 2.0 ** -8, dtype=torch.float16, device=device)
    rows = torch.arange(M, dtype=torch.int64, device=device).view(M, 1)
    cols = torch.arange(k, dtype=torch.int64, device=device).view(1, k)
    x = ((1 + ((5 * rows + 3 * cols) % 7)).to(torch.float16) * (2.0 ** -10)).contiguous()
    return x, qweight, scales, qzeros


def call(module, assets, split, state):
    x, qweight, scales, qzeros = assets
    return module.gemm_forward_cuda(x, qweight, scales, qzeros, split, STATES[state])


def digest_tensor(t):
    return hashlib.sha256(t.detach().contiguous().cpu().numpy().tobytes()).hexdigest()


def verify_replicas(torch, qweight, scales, qzeros):
    rows = []
    for name, tensor in (("qweight", qweight), ("qzeros", qzeros), ("scales", scales)):
        stride = tensor[0].numel() * tensor.element_size()
        base = tensor.data_ptr()
        ref_sha = digest_tensor(tensor[0])
        for rid in range(REPLICAS):
            equal = bool(torch.equal(tensor[0], tensor[rid]))
            sha = digest_tensor(tensor[rid])
            start = tensor[rid].data_ptr()
            rows.append((name, rid, start, start + stride, stride, sha, equal and sha == ref_sha))
    if not all(r[-1] for r in rows):
        raise RuntimeError("replica identity failure")
    return rows


def timed_ms(torch, module, assets, split, state):
    for _ in range(2):
        call(module, assets, split, state)
    start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    start.record()
    call(module, assets, split, state)
    end.record()
    end.synchronize()
    return float(start.elapsed_time(end))


def write_tsv(path, header, rows):
    with path.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def campaign(args):
    torch, module = load_gpu(args.extension)
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    timing, correctness, bindings = [], [], []
    function_id = id(module.gemm_forward_cuda)
    for k in KS:
        assets = make_assets(torch, k)
        torch.cuda.synchronize()
        bindings.extend((k,) + row for row in verify_replicas(torch, assets[1], assets[2], assets[3]))
        outputs = {}
        for split in (8, 1):
            for state in ("SHARED", "PER_MTILE"):
                outputs[(split, state)] = call(module, assets, split, state)
        torch.cuda.synchronize()
        for split in (8, 1):
            shared, per = outputs[(split, "SHARED")], outputs[(split, "PER_MTILE")]
            bitwise = bool(torch.equal(shared, per))
            correctness.append((k, split, "SHARED_vs_PER_MTILE", bitwise,
                                digest_tensor(shared), digest_tensor(per), 0.0 if bitwise else float((shared-per).abs().max())))
            if not bitwise:
                raise RuntimeError(f"bitwise state correctness failure K={k} split={split}")
        a, b = outputs[(8, "SHARED")], outputs[(1, "SHARED")]
        close = bool(torch.allclose(a, b, rtol=1e-2, atol=5e-2))
        correctness.append((k, "8_vs_1", "A_vs_B", close, digest_tensor(a), digest_tensor(b), float((a-b).abs().max())))
        if not close:
            raise RuntimeError(f"A/B correctness failure K={k}")
        for split in (8, 1):
            for state in ("SHARED", "PER_MTILE"):
                for _ in range(10):
                    call(module, assets, split, state)
        torch.cuda.synchronize()
        counts = {(s, st): 0 for s in (8, 1) for st in STATES}
        for block in range(25):
            for position, (split, state) in enumerate(MIRROR):
                idx = counts[(split, state)]
                ms = timed_ms(torch, module, assets, split, state)
                timing.append((k, split, state, STATES[state], block, position, idx, ms, function_id))
                counts[(split, state)] += 1
        del outputs, assets
        torch.cuda.empty_cache()
    write_tsv(out / "REPLICA_BINDINGS.tsv",
              ("K", "tensor", "replica", "va_start", "va_end", "bytes", "sha256", "identity_pass"), bindings)
    write_tsv(out / "CORRECTNESS.tsv",
              ("K", "split", "comparison", "pass", "lhs_sha256", "rhs_sha256", "max_abs"), correctness)
    write_tsv(out / "TIMING_SAMPLES.tsv",
              ("K", "split", "state", "replica_mask", "block", "position", "sample_in_cell", "ms", "function_identity"), timing)
    summary = []
    for k in KS:
        for split in (8, 1):
            for state in STATES:
                vals = [r[7] for r in timing if r[0] == k and r[1] == split and r[2] == state]
                summary.append((k, split, state, len(vals), statistics.median(vals), statistics.mean(vals), min(vals), max(vals)))
    write_tsv(out / "TIMING_SUMMARY.tsv", ("K", "split", "state", "n", "median_ms", "mean_ms", "min_ms", "max_ms"), summary)
    (out / "CAMPAIGN_GPU_IDENTITY.json").write_text(json.dumps({
        "device_name": torch.cuda.get_device_name(0),
        "capability": list(torch.cuda.get_device_capability(0)),
        "extension": str(Path(args.extension).resolve()),
        "extension_sha256": hashlib.sha256(Path(args.extension).read_bytes()).hexdigest(),
        "function_identity": function_id,
    }, indent=2, sort_keys=True) + "\n")


def profile(args):
    if args.k not in KS or args.split not in (8, 1) or args.state not in STATES:
        raise ValueError("profile point outside frozen matrix")
    torch, module = load_gpu(args.extension)
    assets = make_assets(torch, args.k)
    for _ in range(2):
        call(module, assets, args.split, args.state)
    torch.cuda.synchronize()
    label = f"C16_CROSSM_K{args.k}_S{args.split}_{args.state}"
    torch.cuda.nvtx.range_push(label)
    call(module, assets, args.split, args.state)
    torch.cuda.nvtx.range_pop()
    torch.cuda.synchronize()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("campaign", "profile"))
    p.add_argument("--extension", required=True)
    p.add_argument("--out")
    p.add_argument("--k", type=int)
    p.add_argument("--split", type=int)
    p.add_argument("--state")
    args = p.parse_args()
    if args.mode == "campaign":
        if not args.out:
            p.error("campaign requires --out")
        campaign(args)
    else:
        profile(args)


if __name__ == "__main__":
    main()

