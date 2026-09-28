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


def tensor_sha(tensor) -> str:
    payload = tensor.detach().contiguous().cpu().view(-1).view(__import__("torch").uint8).numpy().tobytes()
    return hashlib.sha256(payload).hexdigest()


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
    torch.cuda.synchronize()
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
    l2_bytes = int(getattr(prop, "L2_cache_size", getattr(prop, "l2_cache_size", -1)))
    if l2_bytes != CONDITIONER_BYTES // 4:
        raise RuntimeError(f"GPU L2 identity mismatch: {l2_bytes}")
    ext_a = import_extension(A_PATH, "awq_ext")
    ext_b = import_extension(B_PATH, "awq_split1_ext")
    args.raw.mkdir(parents=True, exist_ok=True)
    point_map = {row["point"]: row for row in POINTS}

    if args.mode == "qualify":
        rows = []; receipts = []; lifecycle = []
        with torch.inference_mode():
            for point in POINTS:
                m,k,n = point["M"],point["K"],point["N"]
                torch.cuda.reset_peak_memory_stats()
                x = make_input(torch,m,k,"dense"); w = make_dense_weight(torch,k,n)
                receipts.extend([
                    {"track":"DENSE","point":point["point"],"tensor":"input","shape":list(x.shape),"dtype":str(x.dtype),"bytes":x.numel()*x.element_size(),"sha256":tensor_sha(x),"formula":"dense_input_value"},
                    {"track":"DENSE","point":point["point"],"tensor":"weight","shape":list(w.shape),"dtype":str(w.dtype),"bytes":w.numel()*w.element_size(),"sha256":tensor_sha(w),"formula":"dense_weight_value"},
                ])
                torch.cuda.nvtx.range_push(f"C16_GPT3_LAUNCH_AUDIT_DENSE_{point['point']}")
                dense = x @ w; torch.cuda.synchronize(); torch.cuda.nvtx.range_pop()
                dense_repeat = x @ w; torch.cuda.synchronize()
                dense_sha = tensor_sha(dense); repeat_sha = tensor_sha(dense_repeat)
                rows.append({"track":"DENSE","point":point["point"],"shape":list(dense.shape),"dtype":str(dense.dtype),"finite":bool(torch.isfinite(dense).all()),"output_sha256":dense_sha,"repeat_output_sha256":repeat_sha,"same_process_repeat_bitwise_equal":dense_sha==repeat_sha})
                receipts.append({"track":"DENSE","point":point["point"],"tensor":"output","shape":list(dense.shape),"dtype":str(dense.dtype),"bytes":dense.numel()*dense.element_size(),"sha256":dense_sha,"formula":"x@w synthetic shape anchor"})
                lifecycle.append({"track":"DENSE","point":point["point"],"phase":"assets_live","allocated_bytes":int(torch.cuda.memory_allocated()),"reserved_bytes":int(torch.cuda.memory_reserved()),"peak_allocated_bytes":int(torch.cuda.max_memory_allocated()),"peak_reserved_bytes":int(torch.cuda.max_memory_reserved())})
                del dense,dense_repeat,x,w; gc.collect(); torch.cuda.synchronize()
                lifecycle.append({"track":"DENSE","point":point["point"],"phase":"after_delete","allocated_bytes":int(torch.cuda.memory_allocated()),"reserved_bytes":int(torch.cuda.memory_reserved())})
                torch.cuda.reset_peak_memory_stats()
                tensors = make_w4(torch,m,k,n)
                for name,value in tensors.items():
                    receipts.append({"track":"W4","point":point["point"],"tensor":name,"shape":list(value.shape),"dtype":str(value.dtype),"bytes":value.numel()*value.element_size(),"sha256":tensor_sha(value),"formula":"GPT3_SHAPE_SYNTH_V1"})
                a = b = None
                for arm in ("A","B"):
                    torch.cuda.nvtx.range_push(f"C16_GPT3_LAUNCH_AUDIT_W4_{point['point']}_{arm}")
                    out = call_w4(ext_a,ext_b,tensors,arm,m,n); torch.cuda.synchronize(); torch.cuda.nvtx.range_pop()
                    rows.append({"track":"W4","point":point["point"],"arm":arm,"shape":list(out.shape),"dtype":str(out.dtype),"finite":bool(torch.isfinite(out).all()),"output_sha256":tensor_sha(out)})
                    if arm == "A": a = out
                    else: b = out
                close = torch.isclose(a,b,rtol=1e-2,atol=5e-2)
                if not bool(close.all()) or not all(row["finite"] for row in rows[-3:]):
                    raise RuntimeError(f"correctness/finite failure: {point['point']}")
                diff=(a.float()-b.float()).abs(); denom=torch.linalg.vector_norm(a.float())
                rows.append({"track":"W4_CORRECTNESS","point":point["point"],"a_sha256":tensor_sha(a),"b_sha256":tensor_sha(b),"shape":list(a.shape),"dtype":str(a.dtype),"all_finite":bool(torch.isfinite(a).all() and torch.isfinite(b).all()),"max_abs":float(diff.max()),"mean_abs":float(diff.mean()),"relative_l2":float(torch.linalg.vector_norm(a.float()-b.float())/denom),"changed_element_count":int(torch.ne(a,b).sum()),"element_count":a.numel(),"rtol":1e-2,"atol":5e-2,"pass":True})
                lifecycle.append({"track":"W4","point":point["point"],"phase":"assets_live","allocated_bytes":int(torch.cuda.memory_allocated()),"reserved_bytes":int(torch.cuda.memory_reserved()),"peak_allocated_bytes":int(torch.cuda.max_memory_allocated()),"peak_reserved_bytes":int(torch.cuda.max_memory_reserved())})
                del a,b,diff,tensors; gc.collect(); torch.cuda.synchronize()
                lifecycle.append({"track":"W4","point":point["point"],"phase":"after_delete","allocated_bytes":int(torch.cuda.memory_allocated()),"reserved_bytes":int(torch.cuda.memory_reserved())})
        write_json(args.raw/"qualification.json", {"status":"PASS","rows":rows,"synthetic_tensor_receipts":receipts,"memory_lifecycle":lifecycle,"ready":ready["validated_prep_head"],"gpu":{"name":prop.name,"total_memory":int(prop.total_memory),"l2_bytes":l2_bytes,"compute_capability":[prop.major,prop.minor]}})
    elif args.mode == "timing":
        samples=[]; lifecycle=[]
        with torch.inference_mode():
            for point in POINTS:
                m,k,n=point["M"],point["K"],point["N"]
                torch.cuda.reset_peak_memory_stats()
                x=make_input(torch,m,k,"dense"); w=make_dense_weight(torch,k,n); fn=lambda:x@w
                for _ in range(10): fn()
                torch.cuda.synchronize()
                for sample in range(50):
                    ms,out=event_ms(torch,fn); samples.append({"track":"DENSE","point":point["point"],"sample":sample,"ms":ms}); del out
                lifecycle.append({"track":"DENSE","point":point["point"],"phase":"timing_assets_live","allocated_bytes":int(torch.cuda.memory_allocated()),"reserved_bytes":int(torch.cuda.memory_reserved()),"peak_allocated_bytes":int(torch.cuda.max_memory_allocated()),"peak_reserved_bytes":int(torch.cuda.max_memory_reserved())})
                del x,w; gc.collect(); torch.cuda.synchronize()
            conditioner=torch.zeros(CONDITIONER_BYTES//4,dtype=torch.int32,device="cuda")
            conditioner_calls=0; conditioner_begin,conditioner_end=range_bounds(conditioner)
            for point in POINTS:
                m,k,n=point["M"],point["K"],point["N"]; tensors=make_w4(torch,m,k,n); assert_nonoverlap(tensors,conditioner)
                torch.cuda.reset_peak_memory_stats()
                block_counts={cell:0 for cell in ("A_W","B_W","A_E","B_E")}
                for block in range(25):
                    for position,cell in enumerate(CELL_ORDER):
                        arm,state=cell.split("_"); fn=lambda arm=arm:call_w4(ext_a,ext_b,tensors,arm,m,n)
                        warm=fn(); del warm; warm=fn(); del warm; torch.cuda.synchronize()
                        if state=="E": condition(torch,conditioner); conditioner_calls+=1
                        torch.cuda.synchronize()
                        ms,out=event_ms(torch,fn); del out
                        samples.append({"track":"W4","point":point["point"],"cell":cell,"arm":arm,"state":state,"block":block,"position":position,"sample_in_cell":block_counts[cell],"ms":ms})
                        block_counts[cell]+=1
                if set(block_counts.values())!={50}: raise RuntimeError(f"sample count failure {point['point']}")
                lifecycle.append({"track":"W4","point":point["point"],"phase":"timing_assets_and_conditioner_live","allocated_bytes":int(torch.cuda.memory_allocated()),"reserved_bytes":int(torch.cuda.memory_reserved()),"peak_allocated_bytes":int(torch.cuda.max_memory_allocated()),"peak_reserved_bytes":int(torch.cuda.max_memory_reserved())})
                del tensors; gc.collect(); torch.cuda.synchronize()
            first,last=int(conditioner[0].item()),int(conditioner[-1].item())
            if conditioner_calls!=400 or first!=conditioner_calls or last!=conditioner_calls: raise RuntimeError(f"conditioner side-effect/count failure {conditioner_calls}/{first}/{last}")
        write_json(args.raw/"timing_samples.json", {"status":"PASS","samples":samples,"memory_lifecycle":lifecycle,"conditioner":{"bytes":CONDITIONER_BYTES,"dtype":str(conditioner.dtype),"calls":conditioner_calls,"first_value":first,"last_value":last,"start":conditioner_begin,"end":conditioner_end,"l2_bytes":l2_bytes,"full_buffer_read_modify_write":True,"outside_timed_event":True,"empty_cache_used":False,"persisting_hint_used":False}})
    elif args.mode == "profile_dense":
        point=point_map[args.point]
        if point["M"]!=256: raise RuntimeError("Dense NCU is M256-only")
        m,k,n=point["M"],point["K"],point["N"]
        with torch.inference_mode():
            x=make_input(torch,m,k,"dense"); w=make_dense_weight(torch,k,n)
            for _ in range(2): x@w
            torch.cuda.synchronize()
            label=f"C16_GPT3_NCU_DENSE_{point['point']}"; torch.cuda.nvtx.range_push(label); out=x@w; torch.cuda.synchronize(); torch.cuda.nvtx.range_pop()
        print(json.dumps({"status":"PASS_PROFILE","range":label,"finite":bool(torch.isfinite(out).all())}))
    else:
        point=point_map[args.point]
        if point["M"]!=256 or not args.cell: raise RuntimeError("W4 NCU is M256 cell-only")
        m,k,n=point["M"],point["K"],point["N"]; arm,state=args.cell.split("_")
        with torch.inference_mode():
            tensors=make_w4(torch,m,k,n); conditioner=torch.zeros(CONDITIONER_BYTES//4,dtype=torch.int32,device="cuda"); assert_nonoverlap(tensors,conditioner)
            fn=lambda:call_w4(ext_a,ext_b,tensors,arm,m,n); warm=fn(); del warm; warm=fn(); del warm; torch.cuda.synchronize()
            if state=="E": condition(torch,conditioner)
            torch.cuda.synchronize()
            label=f"C16_GPT3_NCU_W4_{point['point']}_{args.cell}"; torch.cuda.nvtx.range_push(label); out=fn(); torch.cuda.synchronize(); torch.cuda.nvtx.range_pop()
        print(json.dumps({"status":"PASS_PROFILE","range":label,"finite":bool(torch.isfinite(out).all()),"shape":list(out.shape),"dtype":str(out.dtype),"output_sha256":tensor_sha(out),"conditioner_calls":1 if state=="E" else 0,"conditioner_first_value":int(conditioner[0].item()),"conditioner_last_value":int(conditioner[-1].item())}))


if __name__ == "__main__":
    main()
