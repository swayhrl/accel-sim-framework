#!/usr/bin/env python3
"""Bounded grouped-CTA runner; CUDA imports exist only in explicit GPU modes."""

import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics

M, N, GROUP = 256, 49152, 128
KS = (3072, 4096)
MODES = {"ROW": 0, "GROUP_M16": 1}
MIRROR = ((8, "ROW"), (1, "ROW"), (8, "GROUP_M16"), (1, "GROUP_M16"),
          (1, "GROUP_M16"), (8, "GROUP_M16"), (1, "ROW"), (8, "ROW"))
HISTORY = {
    (3072, 8): (1.6383999586105347, 0.002174999655371307, "76be531cfe46bb847a95aad4fd49910d6715450a15c39681968b0ef1371a34db"),
    (3072, 1): (1.3527040481567383, 0.0032029844064300375, "76be531cfe46bb847a95aad4fd49910d6715450a15c39681968b0ef1371a34db"),
    (4096, 8): (1.9263359904289246, 0.00932058841235311, "43432f9cefc72f5ac5e74bb26d2fb4a601ef7abc8a2839539358e076b8550d0f"),
    (4096, 1): (1.9341440200805664, 0.004419914886562949, "43432f9cefc72f5ac5e74bb26d2fb4a601ef7abc8a2839539358e076b8550d0f"),
}


def load_gpu(extension_path):
    import torch
    name = "awq_grouped_cta_ext"
    spec = importlib.util.spec_from_file_location(name, extension_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load extension: {extension_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return torch, module


def make_assets(torch, k):
    device = "cuda:0"
    qweight = torch.full((k, N // 8), -324508640, dtype=torch.int32, device=device)
    qzeros = torch.full((k // GROUP, N // 8), 2004318071, dtype=torch.int32, device=device)
    scales = torch.full((k // GROUP, N), 2.0 ** -8, dtype=torch.float16, device=device)
    rows = torch.arange(M, dtype=torch.int64, device=device).view(M, 1)
    cols = torch.arange(k, dtype=torch.int64, device=device).view(1, k)
    x = ((1 + ((5 * rows + 3 * cols) % 7)).to(torch.float16) * (2.0 ** -10)).contiguous()
    return x, qweight, scales, qzeros


def call(module, assets, split, mapping):
    x, qweight, scales, qzeros = assets
    return module.gemm_forward_cuda(x, qweight, scales, qzeros, split, MODES[mapping])


def digest_tensor(t):
    return hashlib.sha256(t.detach().contiguous().cpu().numpy().tobytes()).hexdigest()


def timed_ms(torch, module, assets, split, mapping):
    for _ in range(2):
        call(module, assets, split, mapping)
    start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    start.record()
    call(module, assets, split, mapping)
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
    timing, correctness, invocations = [], [], []
    function_id = id(module.gemm_forward_cuda)
    for k in KS:
        assets = make_assets(torch, k)
        outputs = {}
        for split in (8, 1):
            for mapping in MODES:
                outputs[(split, mapping)] = call(module, assets, split, mapping)
                invocations.append((k, split, mapping, MODES[mapping], function_id,
                                    str(Path(args.extension).resolve())))
        torch.cuda.synchronize()
        for split in (8, 1):
            row, grouped = outputs[(split, "ROW")], outputs[(split, "GROUP_M16")]
            bitwise = bool(torch.equal(row, grouped))
            finite = bool(torch.isfinite(row).all() and torch.isfinite(grouped).all())
            correctness.append((k, split, "ROW_vs_GROUP_M16", bitwise and finite,
                                digest_tensor(row), digest_tensor(grouped), 0.0 if bitwise else float((row-grouped).abs().max())))
            if not bitwise or not finite:
                raise RuntimeError(f"mapping correctness failure K={k} split={split}")
            expected = HISTORY[(k, split)][2]
            actual = digest_tensor(row)
            correctness.append((k, split, "ROW_vs_ACCEPTED_SHA", actual == expected, actual, expected, 0.0))
            if actual != expected:
                raise RuntimeError(f"ROW authority output mismatch K={k} split={split}")
        a, b = outputs[(8, "ROW")], outputs[(1, "ROW")]
        close = bool(torch.allclose(a, b, rtol=1e-2, atol=5e-2))
        correctness.append((k, "8_vs_1", "A_vs_B", close, digest_tensor(a), digest_tensor(b), float((a-b).abs().max())))
        if not close:
            raise RuntimeError(f"A/B correctness failure K={k}")
        for split in (8, 1):
            for mapping in MODES:
                for _ in range(10):
                    call(module, assets, split, mapping)
        torch.cuda.synchronize()
        counts = {(s, m): 0 for s in (8, 1) for m in MODES}
        for block in range(25):
            for position, (split, mapping) in enumerate(MIRROR):
                idx = counts[(split, mapping)]
                ms = timed_ms(torch, module, assets, split, mapping)
                timing.append((k, split, mapping, MODES[mapping], block, position, idx, ms, function_id))
                counts[(split, mapping)] += 1
        del outputs, assets
        torch.cuda.empty_cache()

    write_tsv(out / "CORRECTNESS.tsv",
              ("K", "split", "comparison", "pass", "lhs_sha256", "rhs_sha256", "max_abs"), correctness)
    write_tsv(out / "MAPPING_INVOCATION_RECEIPT.tsv",
              ("K", "split", "mapping", "mapping_mode", "function_identity", "extension_path"), invocations)
    write_tsv(out / "TIMING_SAMPLES.tsv",
              ("K", "split", "mapping", "mapping_mode", "block", "position", "sample_in_cell", "ms", "function_identity"), timing)
    summary, calibration = [], []
    material = False
    for k in KS:
        for split in (8, 1):
            for mapping in MODES:
                vals = [r[7] for r in timing if r[0] == k and r[1] == split and r[2] == mapping]
                cv = statistics.pstdev(vals) / statistics.mean(vals)
                summary.append((k, split, mapping, len(vals), statistics.median(vals), statistics.mean(vals), cv, min(vals), max(vals)))
            row_vals = [r[7] for r in timing if r[0] == k and r[1] == split and r[2] == "ROW"]
            current_median = statistics.median(row_vals)
            current_cv = statistics.pstdev(row_vals) / statistics.mean(row_vals)
            hist_median, hist_cv, _ = HISTORY[(k, split)]
            relative = abs(current_median / hist_median - 1.0)
            is_material = relative > 0.05 and relative > hist_cv and relative > current_cv
            material = material or is_material
            calibration.append((k, split, hist_median, hist_cv, current_median, current_cv, relative, is_material,
                                "ROW_PATCH_OVERHEAD_MATERIAL" if is_material else "PASS"))
    write_tsv(out / "TIMING_SUMMARY.tsv",
              ("K", "split", "mapping", "n", "median_ms", "mean_ms", "cv", "min_ms", "max_ms"), summary)
    write_tsv(out / "ROW_CALIBRATION_PRECHECK.tsv",
              ("K", "split", "historical_median_ms", "historical_cv", "row_median_ms", "row_cv", "absolute_relative_delta", "material", "decision"), calibration)
    (out / "CAMPAIGN_GPU_IDENTITY.json").write_text(json.dumps({
        "device_name": torch.cuda.get_device_name(0), "capability": list(torch.cuda.get_device_capability(0)),
        "extension": str(Path(args.extension).resolve()),
        "extension_sha256": hashlib.sha256(Path(args.extension).read_bytes()).hexdigest(),
        "function_identity": function_id,
    }, indent=2, sort_keys=True) + "\n")
    if material:
        raise RuntimeError("ROW_PATCH_OVERHEAD_MATERIAL")


def profile(args):
    if args.k not in KS or args.split not in (8, 1) or args.mapping not in MODES:
        raise ValueError("profile point outside frozen matrix")
    torch, module = load_gpu(args.extension)
    assets = make_assets(torch, args.k)
    for _ in range(2):
        call(module, assets, args.split, args.mapping)
    torch.cuda.synchronize()
    label = f"C16_GROUPED_K{args.k}_S{args.split}_{args.mapping}"
    torch.cuda.nvtx.range_push(label)
    call(module, assets, args.split, args.mapping)
    torch.cuda.nvtx.range_pop()
    torch.cuda.synchronize()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("campaign", "profile"))
    p.add_argument("--extension", required=True)
    p.add_argument("--out")
    p.add_argument("--k", type=int)
    p.add_argument("--split", type=int)
    p.add_argument("--mapping")
    args = p.parse_args()
    if args.mode == "campaign":
        if not args.out:
            p.error("campaign requires --out")
        campaign(args)
    else:
        profile(args)


if __name__ == "__main__":
    main()
