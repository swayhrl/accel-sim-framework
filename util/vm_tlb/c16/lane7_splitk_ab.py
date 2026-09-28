#!/usr/bin/env python3
import argparse
import csv
import hashlib
import importlib
import json
import math
import os
import statistics
import sys
from pathlib import Path

import torch
from awq import AutoAWQForCausalLM

ROOT = Path("/data/c16/e1_lowbit_splitk_native_ab_v1")
RAW = ROOT / "raw"
BUILD_LIB = ROOT / "build" / "lib"
MODEL = "/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641"
AUTH = Path("/data/c16/e1_clean_baseline_v1/capture_a")
EXPECTED = {
    "up_proj_M1": {
        "input": "b3999f6fe161d47efdff4c7d88aa044e2cec3396f9c69fde63c53f2ba208f82e",
        "a_output": "5618125fc9563f42860d5df37ae9b4b6569dfc4af1d995eeb7922d9f60b31d99",
        "a_grid": 1184, "b_grid": 148, "a_scratch": 303104, "b_scratch": 37888,
    },
    "up_proj_M256": {
        "input": "eeae491edfdbee761de47aa6c4ea35b293bb2796227927778fa51c9e58ef1b41",
        "a_output": "59b56af85d0480542fa396a655f23179f879eccaa9ab32a7b98ba88e8cb33d50",
        "a_grid": 18944, "b_grid": 2368, "a_scratch": 77594624, "b_scratch": 9699328,
    },
    "down_proj_M1": {
        "input": "e39ee4d42396f044115b2ec20734c5a0b7d41958c642ad264b1cbbe597aa2c59",
        "a_output": "ccfcd3eb82b4f60eabf13950b9739a6a2098ee23f6bbe347a12492520fc71689",
        "a_grid": 224, "b_grid": 28, "a_scratch": 57344, "b_scratch": 7168,
    },
    "down_proj_M256": {
        "input": "a1f158a113f56314f4ee5f4a5f10ee41ac9afe732a4f1735b88a1c01b25b9aff",
        "a_output": "34dfa2432bd3598dcbd694b576d52b74f08b43e38f231d44f6a10a949f0de477",
        "a_grid": 3584, "b_grid": 448, "a_scratch": 14680064, "b_scratch": 1835008,
    },
}
POINTS = [("up_proj", 1), ("up_proj", 256), ("down_proj", 1), ("down_proj", 256)]


def tsha(t):
    return hashlib.sha256(t.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()


def dump(name, value):
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def tensor_meta(t):
    return {
        "sha256": tsha(t), "shape": list(t.shape), "stride": list(t.stride()),
        "dtype": str(t.dtype), "bytes": t.numel() * t.element_size(),
    }


def load_all():
    sys.path.insert(0, str(BUILD_LIB))
    split1 = importlib.import_module("awq_split1_ext")
    model = AutoAWQForCausalLM.from_quantized(MODEL, fuse_layers=False)
    layer = model.model.model.layers[0]
    modules = {"up_proj": layer.mlp.up_proj, "down_proj": layer.mlp.down_proj}
    inputs = {}
    for role, m in POINTS:
        key = f"{role}_M{m}"
        x = torch.load(AUTH / f"{key}_input.pt", map_location="cpu", weights_only=True).to(torch.float16)
        if tsha(x) != EXPECTED[key]["input"]:
            raise RuntimeError(f"INPUT_AUTHORITY_FAIL {key} {tsha(x)}")
        inputs[key] = x.cuda()
    return model, modules, inputs, split1


def call_a(mod, x):
    return mod(x)


def call_b(split1, mod, x):
    out_shape = x.shape[:-1] + (mod.out_features,)
    out = split1.gemm_forward_cuda(
        x.reshape(-1, x.shape[-1]), mod.qweight, mod.scales, mod.qzeros, 1
    )
    if mod.bias is not None:
        out = out + mod.bias
    out = out.reshape(out_shape)
    if len(out.shape) == 2:
        out = out.unsqueeze(0)
    return out


def correctness():
    model, modules, inputs, split1 = load_all()
    bindings = []
    for role in ("up_proj", "down_proj"):
        mod = modules[role]
        for tensor_name in ("qweight", "qzeros", "scales"):
            bindings.append({"operator": role, "tensor": tensor_name, **tensor_meta(getattr(mod, tensor_name))})
    for role, m in POINTS:
        key = f"{role}_M{m}"
        bindings.append({"operator": role, "tensor": f"input_M{m}", **tensor_meta(inputs[key])})
    dump("bindings.json", bindings)

    a_rows, c_rows = [], []
    with torch.inference_mode():
        for role, m in POINTS:
            key = f"{role}_M{m}"
            mod, x = modules[role], inputs[key]
            a = call_a(mod, x)
            torch.cuda.synchronize()
            a_sha = tsha(a)
            a_ok = a_sha == EXPECTED[key]["a_output"]
            a_rows.append({"point": key, "expected_sha256": EXPECTED[key]["a_output"], "observed_sha256": a_sha,
                           "shape": list(a.shape), "dtype": str(a.dtype), "all_finite": bool(torch.isfinite(a).all()), "pass": a_ok})
            if not a_ok:
                dump("a_reproduction.json", a_rows)
                raise RuntimeError(f"A_AUTHORITY_REPRODUCTION_FAIL {key} {a_sha}")
            b = call_b(split1, mod, x)
            torch.cuda.synchronize()
            diff = (b.float() - a.float()).abs()
            denom = torch.linalg.vector_norm(a.float())
            rel_l2 = float(torch.linalg.vector_norm(b.float() - a.float()) / denom) if float(denom) else 0.0
            close = torch.isclose(b, a, rtol=1e-2, atol=5e-2)
            row = {
                "point": key, "a_sha256": a_sha, "b_sha256": tsha(b),
                "a_shape": list(a.shape), "b_shape": list(b.shape), "a_dtype": str(a.dtype), "b_dtype": str(b.dtype),
                "a_all_finite": bool(torch.isfinite(a).all()), "b_all_finite": bool(torch.isfinite(b).all()),
                "max_abs": float(diff.max()), "mean_abs": float(diff.mean()), "relative_l2": rel_l2,
                "changed_element_count": int(torch.ne(a, b).sum()), "element_count": a.numel(),
                "rtol": 1e-2, "atol": 5e-2, "pass": bool(close.all()),
            }
            c_rows.append(row)
            if not row["pass"]:
                dump("a_reproduction.json", a_rows)
                dump("correctness.json", c_rows)
                raise RuntimeError(f"NUMERICAL_ORDER_CHANGE_REJECTS_AB {key}")
    dump("a_reproduction.json", a_rows)
    dump("correctness.json", c_rows)
    print(json.dumps({"status": "PASS", "a_points": len(a_rows), "correctness_points": len(c_rows)}))


def audit_all():
    model, modules, inputs, split1 = load_all()
    receipts = []
    with torch.inference_mode():
        for role, m in POINTS:
            key = f"{role}_M{m}"
            for _ in range(2):
                call_a(modules[role], inputs[key]); call_b(split1, modules[role], inputs[key])
        torch.cuda.synchronize()
        torch.cuda.cudart().cudaProfilerStart()
        for role, m in POINTS:
            key = f"{role}_M{m}"
            for arm in ("A", "B"):
                label = f"C16_SPLITK_AUDIT_{key}_{arm}"
                torch.cuda.nvtx.range_push(label)
                out = call_a(modules[role], inputs[key]) if arm == "A" else call_b(split1, modules[role], inputs[key])
                torch.cuda.synchronize()
                torch.cuda.nvtx.range_pop()
                receipts.append({"point": key, "arm": arm, "output_sha256": tsha(out), "nvtx": label})
        torch.cuda.cudart().cudaProfilerStop()
    dump("launch_audit_invocations.json", receipts)
    print(json.dumps({"status": "PASS", "invocations": len(receipts)}))


def event_ms(fn):
    torch.cuda.synchronize()
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    start.record()
    out = fn()
    end.record()
    end.synchronize()
    return float(start.elapsed_time(end)), out


def timing():
    model, modules, inputs, split1 = load_all()
    samples = []
    with torch.inference_mode():
        for role, m in POINTS:
            key = f"{role}_M{m}"
            fa = lambda: call_a(modules[role], inputs[key])
            fb = lambda: call_b(split1, modules[role], inputs[key])
            for _ in range(10):
                fa()
            torch.cuda.synchronize()
            for _ in range(10):
                fb()
            torch.cuda.synchronize()
            for block in range(25):
                for position, (arm, fn) in enumerate((("A", fa), ("B", fb), ("B", fb), ("A", fa))):
                    ms, out = event_ms(fn)
                    samples.append({"point": key, "block": block, "position": position, "arm": arm, "ms": ms})
    dump("timing_samples.json", samples)
    summaries = []
    for role, m in POINTS:
        key = f"{role}_M{m}"
        arm_stats = {}
        for arm in ("A", "B"):
            vals = [r["ms"] for r in samples if r["point"] == key and r["arm"] == arm]
            arm_stats[arm] = {"n": len(vals), "min_ms": min(vals), "median_ms": statistics.median(vals),
                              "max_ms": max(vals), "mean_ms": statistics.mean(vals),
                              "cv": statistics.pstdev(vals) / statistics.mean(vals)}
        block_deltas = []
        for block in range(25):
            av = [r["ms"] for r in samples if r["point"] == key and r["block"] == block and r["arm"] == "A"]
            bv = [r["ms"] for r in samples if r["point"] == key and r["block"] == block and r["arm"] == "B"]
            block_deltas.append(statistics.mean(bv) - statistics.mean(av))
        a_med, b_med = arm_stats["A"]["median_ms"], arm_stats["B"]["median_ms"]
        summaries.append({"point": key, "A": arm_stats["A"], "B": arm_stats["B"],
                          "b_vs_a_fraction": b_med / a_med, "improvement_fraction": 1.0 - b_med / a_med,
                          "block_delta_mean_ms": statistics.mean(block_deltas),
                          "block_delta_median_ms": statistics.median(block_deltas),
                          "block_deltas_ms": block_deltas})
    dump("timing_summary.json", summaries)
    print(json.dumps({"status": "PASS", "samples": len(samples)}))


def profile(arm):
    model, modules, inputs, split1 = load_all()
    mod, x = modules["up_proj"], inputs["up_proj_M256"]
    fn = (lambda: call_a(mod, x)) if arm == "A" else (lambda: call_b(split1, mod, x))
    with torch.inference_mode():
        for _ in range(2):
            fn()
        torch.cuda.synchronize()
        label = f"C16_LOWBIT_SPLITK_UP_M256_{arm}"
        torch.cuda.nvtx.range_push(label)
        out = fn()
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_pop()
    got = tsha(out)
    if arm == "A" and got != EXPECTED["up_proj_M256"]["a_output"]:
        raise RuntimeError("A_AUTHORITY_REPRODUCTION_FAIL profile")
    print(json.dumps({"status": "PASS", "arm": arm, "range": label, "output_sha256": got}))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("correctness", "audit", "timing", "profile"))
    p.add_argument("--arm", choices=("A", "B"))
    a = p.parse_args()
    if a.mode == "correctness": correctness()
    elif a.mode == "audit": audit_all()
    elif a.mode == "timing": timing()
    elif a.mode == "profile":
        if not a.arm: p.error("--arm required for profile")
        profile(a.arm)


if __name__ == "__main__":
    main()
