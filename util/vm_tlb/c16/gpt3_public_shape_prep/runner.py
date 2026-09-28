#!/usr/bin/env python3
"""Locked node109 runner; no torch/CUDA import occurs before lock and READY checks."""
from __future__ import annotations

import argparse
import fcntl
import gc
import hashlib
import importlib.util
import json
import os
import statistics
import subprocess
import sys
from pathlib import Path

from contracts import (
    A_BINARY_SHA256, B_BINARY_SHA256, CONDITIONER_BYTES, EXPECTED_TINY_REFERENCE_SHA256,
    POINTS, QWEIGHT_WORD_I32, QZERO_WORD_I32, SCALE, SYNTH_VERSION,
    dense_input_value, dense_weight_value, point_math, tiny_reference, w4_input_value,
)

A_PATH = Path("/data/c16/env/c16-awq-v6/lib/python3.10/site-packages/awq_ext.cpython-310-x86_64-linux-gnu.so")
B_PATH = Path("/data/c16/e1_lowbit_splitk_native_ab_v1/build/lib/awq_split1_ext.cpython-310-x86_64-linux-gnu.so")
CELL_ORDER = ("A_W", "B_W", "A_E", "B_E", "B_E", "A_E", "B_W", "A_W")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def require_outer_lock() -> None:
    if os.environ.get("C16_GPU_LOCK_HELD") != "1":
        raise RuntimeError("GPU lock attestation missing")
    fd = int(os.environ.get("C16_GPU_LOCK_FD", "-1"))
    if fd < 0:
        raise RuntimeError("inherited GPU lock fd missing")
    os.fstat(fd)
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)


def require_ready(repo: Path) -> dict:
    ready_path = repo / "docs/vm_tlb/review_packs/C16_GPT3_PUBLIC_SHAPE_PREP_174NEW_V1/PRE_GPU_READY.json"
    ready = json.loads(ready_path.read_text())
    if ready["status"] != "PRE_GPU_READY" or ready["synthetic_formula_version"] != SYNTH_VERSION:
        raise RuntimeError("PRE_GPU_READY mismatch")
    if tiny_reference()["reference_sha256"] != EXPECTED_TINY_REFERENCE_SHA256:
        raise RuntimeError("synthetic tiny-reference mismatch")
    if sha(A_PATH) != A_BINARY_SHA256 or sha(B_PATH) != B_BINARY_SHA256:
        raise RuntimeError("accepted binary mismatch")
    return ready


def import_extension(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load extension spec {path}")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def make_input(torch, m: int, k: int, formula: str):
    out = torch.empty((m, k), dtype=torch.float16, device="cuda")
    base = torch.arange(k, dtype=torch.int32, device="cuda")
    for residue in range(min(m, 7)):
        values = (1 + (((3 * residue + base) if formula == "dense" else (5 * residue + 3 * base)) % 7)).to(torch.float16) * (2.0**-10)
        out[residue::7] = values
    return out


def make_dense_weight(torch, k: int, n: int):
    out = torch.empty((k, n), dtype=torch.float16, device="cuda")
    base = torch.arange(n, dtype=torch.int32, device="cuda")
    for residue in range(11):
        out[residue::11] = (1 + ((5 * residue + base) % 11)).to(torch.float16) * (2.0**-12)
    return out


def make_w4(torch, m: int, k: int, n: int):
    return {
        "input": make_input(torch, m, k, "w4"),
        "qweight": torch.full((k, n // 8), QWEIGHT_WORD_I32, dtype=torch.int32, device="cuda"),
        "qzeros": torch.full((k // 128, n // 8), QZERO_WORD_I32, dtype=torch.int32, device="cuda"),
        "scales": torch.full((k // 128, n), SCALE, dtype=torch.float16, device="cuda"),
    }


def call_w4(ext_a, ext_b, tensors, arm: str, m: int, n: int):
    ext, split = (ext_a, 8) if arm == "A" else (ext_b, 1)
    out = ext.gemm_forward_cuda(tensors["input"], tensors["qweight"], tensors["scales"], tensors["qzeros"], split)
    return out.reshape(m, n)


def event_ms(torch, fn):
    start = torch.cuda.Event(enable_timing=True); end = torch.cuda.Event(enable_timing=True)
    start.record(); out = fn(); end.record(); end.synchronize()
    return float(start.elapsed_time(end)), out


def condition(torch, buffer):
    buffer.add_(1)


def range_bounds(tensor):
    begin = int(tensor.data_ptr()); return begin, begin + tensor.numel() * tensor.element_size()


def assert_nonoverlap(tensors: dict, conditioner) -> None:
    rows = [(name, *range_bounds(value)) for name, value in tensors.items()] + [("conditioner", *range_bounds(conditioner))]
    for i, (name, begin, end) in enumerate(rows):
        for other, obegin, oend in rows[i+1:]:
            if max(begin, obegin) < min(end, oend):
                raise RuntimeError(f"address overlap: {name}/{other}")


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("qualify", "timing", "profile_dense", "profile_w4"))
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--point", choices=[row["point"] for row in POINTS])
    parser.add_argument("--cell", choices=("A_W", "B_W", "A_E", "B_E"))
    args = parser.parse_args()
    require_outer_lock(); ready = require_ready(args.repo)
    # CUDA import is intentionally below both lock and READY checks.
    import importlib
    torch = importlib.import_module("torch")
    if not torch.cuda.is_available(): raise RuntimeError("CUDA unavailable inside locked phase")
    prop = torch.cuda.get_device_properties(0)
    if (prop.major, prop.minor) != (8, 9) or prop.total_memory < 15 * 1024**3:
        raise RuntimeError(f"GPU identity/capacity mismatch: {prop}")
    ext_a = import_extension(A_PATH, "awq_ext")
    ext_b = import_extension(B_PATH, "awq_split1_ext")
    args.raw.mkdir(parents=True, exist_ok=True)
    point_map = {row["point"]: row for row in POINTS}

    if args.mode == "qualify":
        rows = []
        with torch.inference_mode():
            for point in POINTS:
                m,k,n = point["M"],point["K"],point["N"]
                x = make_input(torch,m,k,"dense"); w = make_dense_weight(torch,k,n)
                torch.cuda.nvtx.range_push(f"C16_GPT3_LAUNCH_AUDIT_DENSE_{point['point']}")
                dense = x @ w; torch.cuda.synchronize(); torch.cuda.nvtx.range_pop()
                rows.append({"track":"DENSE","point":point["point"],"shape":list(dense.shape),"finite":bool(torch.isfinite(dense).all())})
                del dense,x,w; gc.collect()
                tensors = make_w4(torch,m,k,n)
                a = b = None
                for arm in ("A","B"):
                    torch.cuda.nvtx.range_push(f"C16_GPT3_LAUNCH_AUDIT_W4_{point['point']}_{arm}")
                    out = call_w4(ext_a,ext_b,tensors,arm,m,n); torch.cuda.synchronize(); torch.cuda.nvtx.range_pop()
                    rows.append({"track":"W4","point":point["point"],"arm":arm,"shape":list(out.shape),"finite":bool(torch.isfinite(out).all())})
                    if arm == "A": a = out
                    else: b = out
                close = torch.isclose(a,b,rtol=1e-2,atol=5e-2)
                if not bool(close.all()) or not all(row["finite"] for row in rows[-3:]):
                    raise RuntimeError(f"correctness/finite failure: {point['point']}")
                rows.append({"track":"W4_CORRECTNESS","point":point["point"],"max_abs":float((a.float()-b.float()).abs().max()),"pass":True})
                del a,b,tensors; gc.collect()
        write_json(args.raw/"qualification.json", {"status":"PASS","rows":rows,"ready":ready["validated_prep_head"]})
    elif args.mode == "timing":
        samples=[]
        with torch.inference_mode():
            for point in POINTS:
                m,k,n=point["M"],point["K"],point["N"]
                x=make_input(torch,m,k,"dense"); w=make_dense_weight(torch,k,n); fn=lambda:x@w
                for _ in range(10): fn()
                torch.cuda.synchronize()
                for sample in range(50):
                    ms,_=event_ms(torch,fn); samples.append({"track":"DENSE","point":point["point"],"sample":sample,"ms":ms})
                del x,w; gc.collect()
            conditioner=torch.zeros(CONDITIONER_BYTES//4,dtype=torch.int32,device="cuda")
            for point in POINTS:
                m,k,n=point["M"],point["K"],point["N"]; tensors=make_w4(torch,m,k,n); assert_nonoverlap(tensors,conditioner)
                block_counts={cell:0 for cell in ("A_W","B_W","A_E","B_E")}
                for block in range(25):
                    for position,cell in enumerate(CELL_ORDER):
                        arm,state=cell.split("_"); fn=lambda arm=arm:call_w4(ext_a,ext_b,tensors,arm,m,n)
                        fn(); fn()
                        if state=="E": condition(torch,conditioner)
                        ms,_=event_ms(torch,fn)
                        samples.append({"track":"W4","point":point["point"],"cell":cell,"arm":arm,"state":state,"block":block,"position":position,"sample_in_cell":block_counts[cell],"ms":ms})
                        block_counts[cell]+=1
                if set(block_counts.values())!={50}: raise RuntimeError(f"sample count failure {point['point']}")
                del tensors; gc.collect()
        write_json(args.raw/"timing_samples.json", {"status":"PASS","samples":samples})
    elif args.mode == "profile_dense":
        point=point_map[args.point]
        if point["M"]!=256: raise RuntimeError("Dense NCU is M256-only")
        m,k,n=point["M"],point["K"],point["N"]
        with torch.inference_mode():
            x=make_input(torch,m,k,"dense"); w=make_dense_weight(torch,k,n)
            for _ in range(2): x@w
            label=f"C16_GPT3_NCU_DENSE_{point['point']}"; torch.cuda.nvtx.range_push(label); out=x@w; torch.cuda.synchronize(); torch.cuda.nvtx.range_pop()
        print(json.dumps({"status":"PASS_PROFILE","range":label,"finite":bool(torch.isfinite(out).all())}))
    else:
        point=point_map[args.point]
        if point["M"]!=256 or not args.cell: raise RuntimeError("W4 NCU is M256 cell-only")
        m,k,n=point["M"],point["K"],point["N"]; arm,state=args.cell.split("_")
        with torch.inference_mode():
            tensors=make_w4(torch,m,k,n); conditioner=torch.zeros(CONDITIONER_BYTES//4,dtype=torch.int32,device="cuda"); assert_nonoverlap(tensors,conditioner)
            fn=lambda:call_w4(ext_a,ext_b,tensors,arm,m,n); fn(); fn()
            if state=="E": condition(torch,conditioner)
            label=f"C16_GPT3_NCU_W4_{point['point']}_{args.cell}"; torch.cuda.nvtx.range_push(label); out=fn(); torch.cuda.synchronize(); torch.cuda.nvtx.range_pop()
        print(json.dumps({"status":"PASS_PROFILE","range":label,"finite":bool(torch.isfinite(out).all()),"conditioner_calls":1 if state=="E" else 0}))


if __name__ == "__main__":
    main()
