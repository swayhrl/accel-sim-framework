#!/usr/bin/env python3
"""Accepted split8/split1 memory-state interaction runner for Lane7/node109."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import sys
from pathlib import Path

import torch
from safetensors import safe_open

ROOT = Path("/data/c16/splitk_memory_state_interaction_v1")
MODEL = Path("/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641")
AUTH = Path("/data/c16/e1_clean_baseline_v1/capture_a")
BUILD_LIB = Path("/data/c16/e1_lowbit_splitk_native_ab_v1/build/lib")
EXPECTED_L2_BYTES = 67_108_864
BUFFER_MULTIPLE = 4
BUFFER_BYTES = EXPECTED_L2_BYTES * BUFFER_MULTIPLE
EXPECTED = {
    "up_proj": {
        "input": "eeae491edfdbee761de47aa6c4ea35b293bb2796227927778fa51c9e58ef1b41",
        "a_output": "59b56af85d0480542fa396a655f23179f879eccaa9ab32a7b98ba88e8cb33d50",
        "b_output_prior": "3fe2c757285a05c3503823971fc00ff4a77ae19c29c294902e03c55ec4c27494",
        "qweight": "b07a8dec390cec4f664bfd2384acf080c4676e1c6d29386bfaf225e4e68d181a",
        "qzeros": "fa29c34518732c98417613df87bbb46dcf3cd825bd681700a5daa0a49b24205b",
        "scales": "84e59277679d49510b3449687598d47cbe8f9ce356c73f07b2abc60019b0a175",
        "out_features": 18944, "a_grid": 18944, "b_grid": 2368,
        "reduction_grid": 9472, "a_scratch": 77594624, "b_scratch": 9699328,
    },
    "down_proj": {
        "input": "a1f158a113f56314f4ee5f4a5f10ee41ac9afe732a4f1735b88a1c01b25b9aff",
        "a_output": "34dfa2432bd3598dcbd694b576d52b74f08b43e38f231d44f6a10a949f0de477",
        "b_output_prior": "7a34436c1a1b1ee314a5e0f42981479ddfed11b9d8a0601f7e7d87190d80e1bc",
        "qweight": "d5e856f6cb2709c28092e74f3434faaf7bad371c8342a4b0553d148bf5d200cb",
        "qzeros": "06122002c48390245c77e071e2352ebabbc20eedc8dfd555aa222148844be8a80",
        "scales": "031c2f9b22f16ef4538004e3563e03e41ce3b1a015d7476420642d2772fe9cc1d",
        "out_features": 3584, "a_grid": 3584, "b_grid": 448,
        "reduction_grid": 1792, "a_scratch": 14680064, "b_scratch": 1835008,
    },
}
CELL_ORDER = ["A_W", "B_W", "A_E", "B_E", "B_E", "A_E", "B_W", "A_W"]


def run_dir() -> Path:
    run_id = (ROOT / "ACTIVE_RUN_ID").read_text().strip()
    return ROOT / run_id


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tensor_sha(t: torch.Tensor) -> str:
    return hashlib.sha256(t.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()


def atomic_json(path: Path, value) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True); f.write("\n"); f.flush(); os.fsync(f.fileno())
    tmp.replace(path)


def load_one_tensor(index, key):
    shard = MODEL / index[key]
    with safe_open(shard, framework="pt", device="cpu") as handle:
        return handle.get_tensor(key)


def load_assets(roles):
    accepted_a = importlib.import_module("awq_ext")
    sys.path.insert(0, str(BUILD_LIB))
    accepted_b = importlib.import_module("awq_split1_ext")
    index = json.loads((MODEL / "model.safetensors.index.json").read_text())["weight_map"]
    assets = {}
    for role in roles:
        prefix = f"model.layers.0.mlp.{role}"
        tensors = {}
        for name in ("qweight", "qzeros", "scales"):
            tensor = load_one_tensor(index, f"{prefix}.{name}")
            observed = tensor_sha(tensor)
            if observed != EXPECTED[role][name]:
                raise RuntimeError(f"WEIGHT_AUTHORITY_FAIL {role} {name} {observed}")
            tensors[name] = tensor.cuda()
        x_cpu = torch.load(AUTH / f"{role}_M256_input.pt", map_location="cpu", weights_only=True).to(torch.float16)
        observed_input = tensor_sha(x_cpu)
        if observed_input != EXPECTED[role]["input"]:
            raise RuntimeError(f"INPUT_AUTHORITY_FAIL {role} {observed_input}")
        tensors["input"] = x_cpu.cuda()
        assets[role] = tensors
    return accepted_a, accepted_b, assets


def call_arm(ext_a, ext_b, tensors, role, arm):
    x = tensors["input"]
    ext = ext_a if arm == "A" else ext_b
    split = 8 if arm == "A" else 1
    out = ext.gemm_forward_cuda(x.reshape(-1, x.shape[-1]), tensors["qweight"], tensors["scales"], tensors["qzeros"], split)
    return out.reshape(x.shape[:-1] + (EXPECTED[role]["out_features"],))


def ranges_for_assets(assets):
    rows = []
    for role, tensors in assets.items():
        for name, tensor in tensors.items():
            start = int(tensor.data_ptr()); size = tensor.numel() * tensor.element_size()
            rows.append({"role": role, "tensor": name, "start": start, "end": start + size, "bytes": size})
    return rows


class Conditioner:
    def __init__(self, asset_ranges):
        props = torch.cuda.get_device_properties(0)
        l2 = getattr(props, "L2_cache_size", getattr(props, "l2_cache_size", None))
        if l2 is None:
            raise RuntimeError("CONDITIONER_QUALIFICATION_INCOMPLETE missing L2 property")
        self.l2_bytes = int(l2)
        if self.l2_bytes != EXPECTED_L2_BYTES:
            raise RuntimeError(f"CONDITIONER_QUALIFICATION_INCOMPLETE L2={self.l2_bytes}")
        if BUFFER_BYTES % 4:
            raise RuntimeError("conditioner byte alignment")
        self.buffer = torch.zeros(BUFFER_BYTES // 4, dtype=torch.int32, device="cuda")
        self.count = 0
        self.start = int(self.buffer.data_ptr()); self.end = self.start + BUFFER_BYTES
        overlaps = [r for r in asset_ranges if not (self.end <= r["start"] or self.start >= r["end"])]
        if overlaps:
            raise RuntimeError(f"CONDITIONER_QUALIFICATION_INCOMPLETE overlap={overlaps}")
        torch.cuda.synchronize()
        self.asset_ranges = asset_ranges

    def apply(self):
        self.buffer.add_(1)
        torch.cuda.synchronize()
        self.count += 1

    def receipt(self):
        first = int(self.buffer[0].item()); last = int(self.buffer[-1].item())
        if first != self.count or last != self.count:
            raise RuntimeError(f"CONDITIONER_SIDE_EFFECT_FAIL {first} {last} {self.count}")
        return {
            "status": "PASS", "device_l2_bytes": self.l2_bytes, "buffer_multiple": BUFFER_MULTIPLE,
            "buffer_bytes": BUFFER_BYTES, "dtype": str(self.buffer.dtype), "elements": self.buffer.numel(),
            "operation": "in-place int32 add_(1), one coalesced full-buffer read-modify-write traversal",
            "stride_elements": 1, "covered_bytes_per_call": BUFFER_BYTES,
            "buffer_start": self.start, "buffer_end": self.end, "asset_ranges": self.asset_ranges,
            "nonoverlap": True, "calls": self.count, "first_value": first, "last_value": last,
            "allocator_empty_cache_used": False, "persisting_l2_hint_used": False,
            "claim_boundary": "EVICT_CONDITIONED only; not proof that every cache is cold",
        }


def correctness(ext_a, ext_b, assets):
    rows = []
    with torch.inference_mode():
        for role, tensors in assets.items():
            a = call_arm(ext_a, ext_b, tensors, role, "A"); torch.cuda.synchronize()
            b = call_arm(ext_a, ext_b, tensors, role, "B"); torch.cuda.synchronize()
            a_sha, b_sha = tensor_sha(a), tensor_sha(b)
            diff = (b.float() - a.float()).abs()
            denom = torch.linalg.vector_norm(a.float())
            close = torch.isclose(b, a, rtol=1e-2, atol=5e-2)
            row = {
                "operator": role, "input_sha256": tensor_sha(tensors["input"]),
                "a_expected_sha256": EXPECTED[role]["a_output"], "a_observed_sha256": a_sha,
                "b_prior_sha256": EXPECTED[role]["b_output_prior"], "b_observed_sha256": b_sha,
                "a_shape": list(a.shape), "b_shape": list(b.shape), "a_dtype": str(a.dtype), "b_dtype": str(b.dtype),
                "a_finite": bool(torch.isfinite(a).all()), "b_finite": bool(torch.isfinite(b).all()),
                "max_abs": float(diff.max()), "mean_abs": float(diff.mean()),
                "relative_l2": float(torch.linalg.vector_norm(b.float()-a.float()) / denom),
                "changed_element_count": int(torch.ne(a,b).sum()), "element_count": a.numel(),
                "rtol": 1e-2, "atol": 5e-2,
                "a_exact_pass": a_sha == EXPECTED[role]["a_output"], "b_tolerance_pass": bool(close.all()),
            }
            row["pass"] = row["a_exact_pass"] and row["b_tolerance_pass"] and row["a_finite"] and row["b_finite"]
            rows.append(row)
            del a, b, diff, close
            if not row["pass"]:
                atomic_json(run_dir() / "raw" / "correctness.json", rows)
                raise RuntimeError(f"CORRECTNESS_FAIL {role}")
    return rows


def bindings(assets):
    rows = []
    for role, tensors in assets.items():
        for name, tensor in tensors.items():
            rows.append({"operator": role, "tensor": name, "sha256": tensor_sha(tensor), "shape": list(tensor.shape), "stride": list(tensor.stride()), "dtype": str(tensor.dtype), "bytes": tensor.numel()*tensor.element_size(), "data_ptr": int(tensor.data_ptr())})
    return rows


def qualify():
    raw = run_dir() / "raw"; raw.mkdir(exist_ok=True)
    ext_a, ext_b, assets = load_assets(("up_proj", "down_proj"))
    cond = Conditioner(ranges_for_assets(assets))
    rows = correctness(ext_a, ext_b, assets)
    cond.apply()
    torch.cuda.synchronize()
    audit = []
    torch.cuda.cudart().cudaProfilerStart()
    with torch.inference_mode():
        for role, arm in (("up_proj","A"),("up_proj","B"),("down_proj","A"),("down_proj","B")):
            label = f"C16_SPLITK_STATE_AUDIT_{role}_{arm}"
            torch.cuda.nvtx.range_push(label)
            out = call_arm(ext_a, ext_b, assets[role], role, arm)
            torch.cuda.synchronize()
            torch.cuda.nvtx.range_pop()
            audit.append({"operator": role, "arm": arm, "label": label, "output_sha256": tensor_sha(out)})
            del out
    torch.cuda.cudart().cudaProfilerStop()
    atomic_json(raw / "bindings.json", bindings(assets))
    atomic_json(raw / "correctness.json", rows)
    atomic_json(raw / "conditioner_qualification.json", cond.receipt())
    atomic_json(raw / "launch_audit_invocations.json", audit)
    print(json.dumps({"status": "PASS_QUALIFICATION", "operators": 2, "audit_invocations": 4}))


def prepare_sample(fn, state, cond):
    for _ in range(2):
        out = fn(); del out
    torch.cuda.synchronize()
    before = cond.count
    if state == "E": cond.apply()
    torch.cuda.synchronize()
    return before, cond.count


def event_ms(fn):
    torch.cuda.synchronize()
    start = torch.cuda.Event(enable_timing=True); end = torch.cuda.Event(enable_timing=True)
    start.record(); out = fn(); end.record(); end.synchronize()
    ms = float(start.elapsed_time(end)); del out
    return ms


def timing():
    raw = run_dir() / "raw"; raw.mkdir(exist_ok=True)
    ext_a, ext_b, assets = load_assets(("up_proj", "down_proj"))
    cond = Conditioner(ranges_for_assets(assets))
    rows = correctness(ext_a, ext_b, assets)
    samples = []
    with torch.inference_mode():
        for role in ("up_proj", "down_proj"):
            fns = {arm: (lambda arm=arm, role=role: call_arm(ext_a, ext_b, assets[role], role, arm)) for arm in ("A","B")}
            for arm in ("A","B"):
                for _ in range(10):
                    out = fns[arm](); del out
                torch.cuda.synchronize()
            for block in range(25):
                for position, cell in enumerate(CELL_ORDER):
                    arm, state = cell.split("_")
                    before, after = prepare_sample(fns[arm], state, cond)
                    ms = event_ms(fns[arm])
                    samples.append({"operator": role, "cell": cell, "arm": arm, "state": "WARM_SAME_ARM" if state=="W" else "EVICT_CONDITIONED", "block": block, "position": position, "ms": ms, "conditioner_calls_before": before, "conditioner_calls_after": after})
    expected_calls = 25 * 4 * 2
    receipt = cond.receipt()
    if receipt["calls"] != expected_calls:
        raise RuntimeError(f"CONDITIONER_CALL_COUNT_FAIL {receipt['calls']}/{expected_calls}")
    atomic_json(raw / "timing_correctness_recheck.json", rows)
    atomic_json(raw / "timing_samples.json", samples)
    atomic_json(raw / "timing_conditioner_receipt.json", receipt)
    print(json.dumps({"status": "PASS_TIMING", "samples": len(samples), "conditioner_calls": receipt["calls"]}))


def profile(operator, cell):
    ext_a, ext_b, assets = load_assets((operator,))
    cond = Conditioner(ranges_for_assets(assets))
    arm, state = cell.split("_")
    fn = lambda: call_arm(ext_a, ext_b, assets[operator], operator, arm)
    with torch.inference_mode():
        for _ in range(2):
            out = fn(); del out
        torch.cuda.synchronize()
        if state == "E": cond.apply()
        torch.cuda.synchronize()
        label = f"C16_SPLITK_STATE_{operator}_{cell}"
        torch.cuda.nvtx.range_push(label)
        out = fn(); torch.cuda.synchronize(); torch.cuda.nvtx.range_pop()
    got = tensor_sha(out)
    if arm == "A" and got != EXPECTED[operator]["a_output"]:
        raise RuntimeError(f"A_AUTHORITY_REPRODUCTION_FAIL profile {operator} {cell}")
    receipt = cond.receipt()
    print(json.dumps({"status": "PASS_PROFILE", "operator": operator, "cell": cell, "range": label, "output_sha256": got, "conditioner": receipt}, sort_keys=True))


def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="mode", required=True)
    sub.add_parser("qualify"); sub.add_parser("timing")
    prof = sub.add_parser("profile"); prof.add_argument("--operator", choices=("up_proj","down_proj"), required=True); prof.add_argument("--cell", choices=("A_W","B_W","A_E","B_E"), required=True)
    args = p.parse_args()
    if args.mode == "qualify": qualify()
    elif args.mode == "timing": timing()
    else: profile(args.operator, args.cell)


if __name__ == "__main__": main()
