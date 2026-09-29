#!/usr/bin/env python3
"""One discovery target plus conditionally enabled frozen validation target."""

import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics

TARGETS = {
    "discovery": {"M": 256, "K": 4096, "N": 49152,
                  "expected_output_sha": "43432f9cefc72f5ac5e74bb26d2fb4a601ef7abc8a2839539358e076b8550d0f",
                  "accepted_median_ms": 1.316864013671875},
    "validation": {"M": 256, "K": 3072, "N": 49152,
                   "expected_output_sha": "76be531cfe46bb847a95aad4fd49910d6715450a15c39681968b0ef1371a34db",
                   "accepted_median_ms": 0.9963520169258118},
}
ORDER = ("A", "B", "C", "C", "B", "A")


def load_gpu(path):
    import torch
    name = "awq_conversion_oracle_ext"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load extension {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return torch, module


def digest_tensor(t):
    return hashlib.sha256(t.detach().contiguous().cpu().numpy().tobytes()).hexdigest()


def make_assets(torch, target):
    m, k, n = target["M"], target["K"], target["N"]
    qweight = torch.full((k, n // 8), -324508640, dtype=torch.int32, device="cuda:0")
    qzeros = torch.full((k // 128, n // 8), 2004318071, dtype=torch.int32, device="cuda:0")
    scales = torch.full((k // 128, n), 2.0 ** -8, dtype=torch.float16, device="cuda:0")
    rows = torch.arange(m, dtype=torch.int64, device="cuda:0").view(m, 1)
    cols = torch.arange(k, dtype=torch.int64, device="cuda:0").view(1, k)
    x = ((1 + ((5 * rows + 3 * cols) % 7)).to(torch.float16) * (2.0 ** -10)).contiguous()
    return x, qweight, scales, qzeros


def call(module, torch, condition, assets, expanded):
    x, qweight, scales, qzeros = assets
    if condition == "A":
        return module.gemm_forward_cuda(x, qweight, scales, qzeros, 1, 1)
    if condition == "B":
        return module.gemm_forward_oracle_cuda(x, qweight, scales, qzeros, 1, 1)
    if condition == "C":
        return torch.mm(x, expanded)
    raise ValueError(condition)


def flip_all_low_bits(torch, tensor):
    flat = tensor.view(torch.int16 if tensor.dtype == torch.float16 else tensor.dtype).view(-1)
    flat.bitwise_xor_(1)
    return flat


def oracle_dependency_canaries(torch, module, assets, expanded, reference):
    rows = []
    for name, tensor in (("qweight", assets[1]), ("qzeros", assets[3]), ("scales", assets[2])):
        flat = flip_all_low_bits(torch, tensor)
        changed = call(module, torch, "B", assets, expanded)
        torch.cuda.synchronize()
        unequal = int(torch.count_nonzero(changed != reference).item())
        rows.append((name, unequal, unequal > 0, digest_tensor(changed)))
        flat.bitwise_xor_(1)
        torch.cuda.synchronize()
    if not all(row[2] for row in rows):
        raise RuntimeError(f"oracle compressed-load dependency canary failed: {rows}")
    return rows


def timed_ms(torch, fn):
    for _ in range(2):
        fn()
    start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    start.record()
    fn()
    end.record()
    end.synchronize()
    return float(start.elapsed_time(end))


def write_tsv(path, header, rows):
    with path.open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def run_target(torch, module, name, out):
    target = TARGETS[name]
    assets = make_assets(torch, target)
    expanded = module.dequantize_weights_cuda(assets[1], assets[2], assets[3], 1, 0, 0, False).contiguous()
    torch.cuda.synchronize()
    outputs = {condition: call(module, torch, condition, assets, expanded) for condition in ("A", "B", "C")}
    torch.cuda.synchronize()
    baseline_sha = digest_tensor(outputs["A"])
    baseline_authority = baseline_sha == target["expected_output_sha"]
    c_close = bool(torch.allclose(outputs["A"], outputs["C"], rtol=1e-2, atol=5e-2))
    c_finite = bool(torch.isfinite(outputs["C"]).all())
    b_finite = bool(torch.isfinite(outputs["B"]).all())
    correctness = {
        "target": name, "baseline_authority_pass": baseline_authority,
        "baseline_sha256": baseline_sha, "expected_baseline_sha256": target["expected_output_sha"],
        "baseline_shape": list(outputs["A"].shape), "baseline_dtype": str(outputs["A"].dtype),
        "predecoded_correct": c_close and c_finite,
        "predecoded_sha256": digest_tensor(outputs["C"]),
        "predecoded_max_abs": float((outputs["A"] - outputs["C"]).abs().max()),
        "predecoded_mean_abs": float((outputs["A"] - outputs["C"]).abs().mean()),
        "oracle_status": "ORACLE_INVALID_OUTPUT", "oracle_finite": b_finite,
        "oracle_sha256": digest_tensor(outputs["B"]),
        "expanded_weight_bytes": expanded.numel() * expanded.element_size(),
        "expanded_weight_shape": list(expanded.shape), "expanded_weight_dtype": str(expanded.dtype),
        "compressed_weight_bytes": sum(t.numel() * t.element_size() for t in (assets[1], assets[2], assets[3])),
        "weight_sha256": {"qweight": digest_tensor(assets[1]), "scales": digest_tensor(assets[2]), "qzeros": digest_tensor(assets[3])},
    }
    if not baseline_authority or not correctness["predecoded_correct"] or not b_finite:
        raise RuntimeError(f"target correctness/canary failure: {correctness}")
    canaries = oracle_dependency_canaries(torch, module, assets, expanded, outputs["B"])
    for condition in ("A", "B", "C"):
        for _ in range(10):
            call(module, torch, condition, assets, expanded)
    torch.cuda.synchronize()
    samples, counts = [], {condition: 0 for condition in ("A", "B", "C")}
    fns = {condition: (lambda c=condition: call(module, torch, c, assets, expanded)) for condition in ("A", "B", "C")}
    for block in range(25):
        for position, condition in enumerate(ORDER):
            value = timed_ms(torch, fns[condition])
            samples.append((name, condition, block, position, counts[condition], value))
            counts[condition] += 1
    summary = {}
    for condition in ("A", "B", "C"):
        vals = [row[5] for row in samples if row[1] == condition]
        summary[condition] = {"n": len(vals), "median_ms": statistics.median(vals),
                              "mean_ms": statistics.mean(vals),
                              "cv": statistics.pstdev(vals) / statistics.mean(vals),
                              "min_ms": min(vals), "max_ms": max(vals)}
    summary["local_oracle_speedup"] = summary["A"]["median_ms"] / summary["B"]["median_ms"]
    summary["predecoded_speedup_vs_baseline"] = summary["A"]["median_ms"] / summary["C"]["median_ms"]
    summary["baseline_relative_to_accepted"] = summary["A"]["median_ms"] / target["accepted_median_ms"] - 1.0
    return correctness, canaries, samples, summary, assets, expanded, outputs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--extension", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--isolation-audit", type=Path, required=True)
    args = p.parse_args()
    isolation = json.loads(args.isolation_audit.read_text())
    if isolation["status"] != "ORACLE_ISOLATION_PASS":
        raise RuntimeError("ORACLE_NOT_ISOLATABLE")
    torch, module = load_gpu(args.extension)
    args.out.mkdir(parents=True, exist_ok=True)
    all_correctness, all_canaries, all_samples, summaries = [], [], [], {}
    result = run_target(torch, module, "discovery", args.out)
    correctness, canaries, samples, summary, assets, expanded, outputs = result
    all_correctness.append(correctness)
    all_canaries.extend(("discovery",) + row for row in canaries)
    all_samples.extend(samples)
    summaries["discovery"] = summary
    validation_pass = (summary["local_oracle_speedup"] >= 1.10 and
                       summary["A"]["cv"] <= 0.05 and summary["B"]["cv"] <= 0.05 and
                       abs(summary["baseline_relative_to_accepted"]) <= 0.05 and
                       correctness["baseline_authority_pass"] and correctness["predecoded_correct"] and
                       all(row[2] for row in canaries))
    decision = {"threshold_speedup": 1.10, "observed_speedup": summary["local_oracle_speedup"],
                "baseline_cv": summary["A"]["cv"], "oracle_cv": summary["B"]["cv"],
                "baseline_relative_to_accepted": summary["baseline_relative_to_accepted"],
                "isolation_status": isolation["status"], "validation_authorized": validation_pass,
                "decision": "RUN_FROZEN_VALIDATION" if validation_pass else "STOP_AFTER_DISCOVERY"}
    (args.out / "DISCOVERY_GATE.json").write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n")
    del assets, expanded, outputs
    torch.cuda.empty_cache()
    if validation_pass:
        correctness, canaries, samples, summary, assets, expanded, outputs = run_target(torch, module, "validation", args.out)
        all_correctness.append(correctness)
        all_canaries.extend(("validation",) + row for row in canaries)
        all_samples.extend(samples)
        summaries["validation"] = summary
        del assets, expanded, outputs
        torch.cuda.empty_cache()
    write_tsv(args.out / "CORRECTNESS.tsv",
              ("target", "baseline_authority_pass", "baseline_sha256", "expected_baseline_sha256",
               "predecoded_correct", "predecoded_sha256", "predecoded_max_abs", "predecoded_mean_abs",
               "oracle_status", "oracle_finite", "oracle_sha256", "expanded_weight_bytes", "compressed_weight_bytes"),
              [(x["target"], x["baseline_authority_pass"], x["baseline_sha256"], x["expected_baseline_sha256"],
                x["predecoded_correct"], x["predecoded_sha256"], x["predecoded_max_abs"], x["predecoded_mean_abs"],
                x["oracle_status"], x["oracle_finite"], x["oracle_sha256"], x["expanded_weight_bytes"], x["compressed_weight_bytes"]) for x in all_correctness])
    write_tsv(args.out / "ORACLE_DEPENDENCY_CANARIES.tsv",
              ("target", "source", "changed_output_elements", "pass", "mutated_oracle_sha256"), all_canaries)
    write_tsv(args.out / "TIMING_SAMPLES.tsv",
              ("target", "condition", "block", "position", "sample_in_condition", "ms"), all_samples)
    rows = []
    for target_name, summary in summaries.items():
        for condition in ("A", "B", "C"):
            x = summary[condition]
            rows.append((target_name, condition, x["n"], x["median_ms"], x["mean_ms"], x["cv"], x["min_ms"], x["max_ms"]))
    write_tsv(args.out / "TIMING_SUMMARY.tsv", ("target", "condition", "n", "median_ms", "mean_ms", "cv", "min_ms", "max_ms"), rows)
    (args.out / "TARGET_SUMMARY.json").write_text(json.dumps(summaries, indent=2, sort_keys=True) + "\n")
    (args.out / "GPU_IDENTITY.json").write_text(json.dumps({
        "device_name": torch.cuda.get_device_name(0), "capability": list(torch.cuda.get_device_capability(0)),
        "extension": str(Path(args.extension).resolve()),
        "extension_sha256": hashlib.sha256(Path(args.extension).read_bytes()).hexdigest(),
        "validation_executed": validation_pass,
    }, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
