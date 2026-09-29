#!/usr/bin/env python3
"""Bounded residual-parallelism runner; CUDA imports only in GPU modes."""

import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics

K, N, GROUP = 4096, 12288, 128
MS = (1, 16, 32, 64)
MAPPING_MODE = 1


def load_gpu(extension_path):
    import torch
    name = "awq_residual_parallelism_ext"
    spec = importlib.util.spec_from_file_location(name, extension_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load extension: {extension_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return torch, module


def make_weights(torch):
    device = "cuda:0"
    return (torch.full((K, N // 8), -324508640, dtype=torch.int32, device=device),
            torch.full((K // GROUP, N), 2.0 ** -8, dtype=torch.float16, device=device),
            torch.full((K // GROUP, N // 8), 2004318071, dtype=torch.int32, device=device))


def make_input(torch, m):
    rows = torch.arange(m, dtype=torch.int64, device="cuda:0").view(m, 1)
    cols = torch.arange(K, dtype=torch.int64, device="cuda:0").view(1, K)
    return ((1 + ((5 * rows + 3 * cols) % 7)).to(torch.float16) * (2.0 ** -10)).contiguous()


def call(module, assets, split):
    x, qweight, scales, qzeros = assets
    return module.gemm_forward_cuda(x, qweight, scales, qzeros, split, MAPPING_MODE)


def digest_tensor(t):
    return hashlib.sha256(t.detach().contiguous().cpu().numpy().tobytes()).hexdigest()


def timed_ms(torch, module, assets, split):
    for _ in range(2):
        call(module, assets, split)
    start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    start.record()
    call(module, assets, split)
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
    qweight, scales, qzeros = make_weights(torch)
    assets = {m: (make_input(torch, m), qweight, scales, qzeros) for m in MS}
    correctness, invocations, timing = [], [], []
    function_id = id(module.gemm_forward_cuda)
    for m in MS:
        a = call(module, assets[m], 8)
        b = call(module, assets[m], 1)
        torch.cuda.synchronize()
        finite = bool(torch.isfinite(a).all() and torch.isfinite(b).all())
        close = bool(torch.allclose(a, b, rtol=1e-2, atol=5e-2))
        bitwise = bool(torch.equal(a, b))
        correctness.append((m, close and finite, bitwise, list(a.shape), str(a.dtype),
                            digest_tensor(a), digest_tensor(b), float((a-b).abs().max())))
        if not close or not finite:
            raise RuntimeError(f"correctness failure M={m}")
        for split in (8, 1):
            invocations.append((m, split, "GROUP_FULL_M", MAPPING_MODE, function_id,
                                str(Path(args.extension).resolve())))
            for _ in range(10):
                call(module, assets[m], split)
    torch.cuda.synchronize()
    counts = {(m, split): 0 for m in MS for split in (8, 1)}
    for block in range(25):
        offset = block % len(MS)
        m_order = MS[offset:] + MS[:offset]
        for m_position, m in enumerate(m_order):
            for position, split in enumerate((8, 1, 1, 8)):
                idx = counts[(m, split)]
                ms = timed_ms(torch, module, assets[m], split)
                timing.append((m, split, block, m_position, position, idx, ms, function_id))
                counts[(m, split)] += 1
    write_tsv(out / "CORRECTNESS.tsv",
              ("M", "pass", "bitwise_equal", "shape", "dtype", "split8_sha256", "split1_sha256", "max_abs"), correctness)
    write_tsv(out / "MAPPING_INVOCATION_RECEIPT.tsv",
              ("M", "split", "mapping", "mapping_mode", "function_identity", "extension_path"), invocations)
    write_tsv(out / "TIMING_SAMPLES.tsv",
              ("M", "split", "block", "m_rotation_position", "abba_position", "sample_in_cell", "ms", "function_identity"), timing)
    summary = []
    for m in MS:
        for split in (8, 1):
            vals = [r[6] for r in timing if r[0] == m and r[1] == split]
            summary.append((m, split, len(vals), statistics.median(vals), statistics.mean(vals),
                            statistics.pstdev(vals) / statistics.mean(vals), min(vals), max(vals)))
    write_tsv(out / "TIMING_SUMMARY.tsv",
              ("M", "split", "n", "median_ms", "mean_ms", "cv", "min_ms", "max_ms"), summary)
    (out / "CAMPAIGN_GPU_IDENTITY.json").write_text(json.dumps({
        "device_name": torch.cuda.get_device_name(0), "capability": list(torch.cuda.get_device_capability(0)),
        "extension": str(Path(args.extension).resolve()),
        "extension_sha256": hashlib.sha256(Path(args.extension).read_bytes()).hexdigest(),
        "function_identity": function_id,
        "weight_sha256": {"qweight": digest_tensor(qweight), "scales": digest_tensor(scales), "qzeros": digest_tensor(qzeros)},
    }, indent=2, sort_keys=True) + "\n")


def profile(args):
    if args.m not in MS or args.split not in (8, 1):
        raise ValueError("profile point outside frozen matrix")
    torch, module = load_gpu(args.extension)
    qweight, scales, qzeros = make_weights(torch)
    assets = (make_input(torch, args.m), qweight, scales, qzeros)
    for _ in range(2):
        call(module, assets, args.split)
    torch.cuda.synchronize()
    label = f"C16_RESIDUAL_M{args.m}_S{args.split}"
    torch.cuda.nvtx.range_push(label)
    call(module, assets, args.split)
    torch.cuda.nvtx.range_pop()
    torch.cuda.synchronize()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("campaign", "profile"))
    p.add_argument("--extension", required=True)
    p.add_argument("--out")
    p.add_argument("--m", type=int)
    p.add_argument("--split", type=int)
    args = p.parse_args()
    if args.mode == "campaign":
        if not args.out:
            p.error("campaign requires --out")
        campaign(args)
    else:
        profile(args)


if __name__ == "__main__":
    main()
