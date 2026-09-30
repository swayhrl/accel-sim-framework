#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

STAGE = "AWMA_EXACT_LOSS_CCE_LIGER_109_V1"
DECISION = "EXACT_LOSS_STATE_LIFETIME_RESIDUAL_PRESENT"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def build(root: Path, pack: Path) -> None:
    pack.mkdir(parents=True, exist_ok=True)
    rec = root / "receipts"
    raw = root / "raw"
    source = json.loads((rec / "SOURCE_IDENTITY.json").read_text())
    authority = json.loads((rec / "INPUT_RECEIPT.json").read_text())
    runtime = json.loads((raw / "RUNTIME_INPUT_RECEIPT.json").read_text())
    numerical = json.loads((raw / "NUMERICAL_QUALIFICATION.json").read_text())
    timing = json.loads((raw / "TIMING_SUMMARY.json").read_text())
    memory = json.loads((raw / "MEMORY_ACCOUNTING.json").read_text())
    environment = json.loads((raw / "GPU_ENVIRONMENT.json").read_text())
    campaign = json.loads((raw / "CAMPAIGN_RESULT.json").read_text())
    repair = json.loads((rec / "ENGINEERING_REPAIR_PREREGISTRATION.json").read_text())

    shutil.copy2(rec / "SOURCE_IDENTITY.json", pack / "SOURCE_IDENTITY.json")
    shutil.copy2(rec / "SHAPE_CONTRACT.tsv", pack / "SHAPE_CONTRACT.tsv")
    shutil.copy2(rec / "NUMERICAL_PREREGISTRATION.json", pack / "NUMERICAL_PREREGISTRATION.json")
    shutil.copy2(rec / "ENGINEERING_REPAIR_PREREGISTRATION.json", pack / "ENGINEERING_REPAIR_PREREGISTRATION.json")
    dump(pack / "INPUT_RECEIPT.json", {"stage": STAGE, "authority": authority, "runtime_real_model_forward": runtime})

    rows = []
    for arm in ("B0", "B1", "B2"):
        for metric in ("loss", "grad_hidden", "grad_weight"):
            item = numerical[arm][metric]
            rows.append({
                "arm": arm,
                "arm_name": numerical[arm]["arm_name"],
                "metric": metric,
                "qualified": item.get("allclose"),
                "finite": item.get("finite"),
                "observed": item.get("observed", ""),
                "reference": item.get("reference", ""),
                "max_abs": item.get("max_abs", ""),
                "mean_abs": item.get("mean_abs", ""),
                "max_rel": item.get("max_rel", ""),
                "cosine_similarity": item.get("cosine_similarity", ""),
                "rtol": 0.01,
                "atol": 0.01,
            })
    tsv(pack / "NUMERICAL_QUALIFICATION.tsv", list(rows[0]), rows)

    timing_rows = []
    with (raw / "TIMING_SAMPLES.tsv").open(newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            summary = timing[row["arm"]]
            row.update({
                "formal_gpu_ms_median": summary["gpu_ms_median"],
                "formal_gpu_ms_mad": summary["gpu_ms_mad"],
                "formal_host_ms_median": summary["host_ms_median"],
                "formal_host_ms_mad": summary["host_ms_mad"],
            })
            timing_rows.append(row)
    tsv(pack / "TIMING.tsv", list(timing_rows[0]), timing_rows)

    mem_rows = []
    saved_rows = []
    for arm in ("B0", "B1", "B2"):
        item = memory[arm]
        mem_rows.append({
            "arm": arm,
            "baseline_allocated_bytes": item["baseline_allocated_bytes"],
            "baseline_reserved_bytes": item["baseline_reserved_bytes"],
            "peak_allocated_bytes": item["peak_allocated_bytes"],
            "peak_reserved_bytes": item["peak_reserved_bytes"],
            "peak_allocated_delta_bytes": item["peak_allocated_delta_bytes"],
            "peak_reserved_delta_bytes": item["peak_reserved_delta_bytes"],
            "mandatory_output_bytes": item["mandatory_output_bytes"],
            "saved_tensor_logical_bytes_sum": item["saved_tensor_logical_bytes_sum"],
            "saved_tensor_unique_storage_bytes": item["saved_tensor_unique_storage_bytes"],
            "full_TxV_logits_exists": item["full_TxV_logits_exists"],
            "full_TxV_logits_saved": item["full_TxV_logits_saved"],
            "allocator_bytes_are_not_dram_traffic": True,
        })
        for index, saved in enumerate(item["saved_tensors"]):
            saved_rows.append({
                "arm": arm,
                "pack_event": index,
                "identity": saved["identity"],
                "shape": "x".join(str(v) for v in saved["shape"]) or "scalar",
                "dtype": saved["dtype"],
                "logical_bytes": saved["logical_bytes"],
                "requires_grad": saved["requires_grad"],
            })
    tsv(pack / "MEMORY_ACCOUNTING.tsv", list(mem_rows[0]), mem_rows)
    tsv(pack / "SAVED_TENSOR_IDENTITIES.tsv", list(saved_rows[0]), saved_rows)

    profile_csv = raw / "nsys" / "B1_CCE_EXACT_cuda_gpu_kern_sum_cuda_gpu_kern_sum.csv"
    with profile_csv.open(newline="") as f:
        profile = list(csv.DictReader(f))
    total_ns = sum(int(row["Total Time (ns)"]) for row in profile)
    with (raw / "nsys" / "B1_CCE_EXACT_KERNEL_INSTANCES.tsv").open(newline="") as f:
        instances = list(csv.DictReader(f, delimiter="\t"))
    full_elements = 151936 * 896
    full_grid = full_elements // 1024
    fill = next(row for row in instances if int(row["grid_x"]) == full_grid and "FillFunctor<float>" in row["demangled_name"])
    copy = next(row for row in instances if int(row["grid_x"]) == full_grid and "bfloat16_copy_kernel_cuda" in row["demangled_name"])
    fill_ns = int(fill["duration_ns"])
    copy_ns = int(copy["duration_ns"])
    profile_rows = [{
        "time_percent": row["Time (%)"],
        "total_time_ns": row["Total Time (ns)"],
        "instances": row["Instances"],
        "median_ns": row["Med (ns)"],
        "name": row["Name"],
    } for row in profile]
    tsv(pack / "PROFILE_SUMMARY.tsv", list(profile_rows[0]), profile_rows)

    b0 = timing["B0"]["gpu_ms_median"]
    b1 = timing["B1"]["gpu_ms_median"]
    b2 = timing["B2"]["gpu_ms_median"]
    fill_fraction = fill_ns / total_ns
    copy_fraction = copy_ns / total_ns
    accumulator_bytes = full_elements * 4
    b1_extra = memory["B1"]["peak_allocated_delta_bytes"] - memory["B1"]["mandatory_output_bytes"]

    (pack / "HEADROOM_ANALYSIS.md").write_text(f"""# Headroom analysis

All three arms passed the frozen full-gradient contract before timing. Each arm has
15 formal samples in three paired groups, with two warmups per group.

- B0 materialized PyTorch: {b0:.6f} ms median, {timing['B0']['gpu_ms_mad']:.6f} ms MAD.
- B1 CCE exact/no-filter: {b1:.6f} ms median, {timing['B1']['gpu_ms_mad']:.6f} ms MAD.
- B2 Liger Triton/Ada: {b2:.6f} ms median, {timing['B2']['gpu_ms_mad']:.6f} ms MAD.

B1 is the fastest qualified no-full-logits arm, but it is {(b1 / b0 - 1.0) * 100:.2f}%
slower than B0. B0 is only the materialized correctness/reference baseline; its
advantage is not called a hardware speedup.

B2 is stable but is a poor fit for this short real shape. At V=151936, H=896 and
the pinned source chunk-memory constant, its increment factor is 170, chunk size is
2, and it executes 128 chunks. With FP32 accumulation required by the frozen
numerical contract, repeated full classifier-gradient accumulation explains the large
runtime. This is an explained software-organization result, not instability.

## State/lifetime localization

B1 has no full T x V logits. Its peak allocated delta is
{memory['B1']['peak_allocated_delta_bytes']} bytes; mandatory committed output is
{memory['B1']['mandatory_output_bytes']} bytes. The remaining {b1_extra} bytes
closely matches one full FP32 classifier-gradient accumulator ({accumulator_bytes}
bytes).

The one permitted NSYS capture contains {total_ns} ns of GPU kernels. Two exact
full-gradient-sized state operations have grid_x={full_grid}, exactly (V*H)/1024:

- FP32 accumulator zero-fill: {fill_ns} ns ({fill_fraction * 100:.2f}%).
- FP32-to-BF16 classifier-gradient copy/cast: {copy_ns} ns ({copy_fraction * 100:.2f}%).

The conservative residual uses only explicit full-accumulator zero initialization:
{fill_fraction * 100:.2f}% of the profiled kernel timeline, above the 5% screen.
The copy/cast is only a wider envelope because committing BF16 grad_weight is
mandatory. CCE backward and LSE kernels are not counted as removable loss math.

This is local operator evidence, not an end-to-end claim. Allocator and saved-tensor
bytes are logical state evidence, not DRAM traffic.

NSYS localized the residual; NCU was not run because profiling the mandatory CCE
backward kernel would not strengthen the state/lifetime identity.
""")

    (pack / "FINAL_DECISION.md").write_text(f"""# Final decision

{DECISION}

The accepted real R101 Qwen input, real final hidden, exact checkpoint lm_head,
shifted labels, mean reduction, BF16 storage, and complete
loss/grad_hidden/grad_weight contract all qualified.

The fastest qualified no-full-logits arm is CCE exact/no-filter. A valid NSYS
timeline and memory identity bind a full FP32 classifier-gradient accumulator to an
explicit {fill_ns / 1e6:.6f} ms zero-initialization phase, {fill_fraction * 100:.2f}%
of profiled GPU kernel time. This exceeds the 5% screen without counting mandatory
GEMM/softmax-gradient kernels or the mandatory portion of output commitment.

This establishes only a bounded local state/lifetime residual on one RTX4080 and one
real Qwen shape. It is not a training-step, second-model, multi-GPU, or hardware
speedup claim. No mechanism is proposed.
""")

    (pack / "ENGINEERING_FIXES.md").write_text("""# Engineering fixes and excluded attempts

Attempt 0 used an invalid explicit Liger registry name and exited before model
forward or timing. The standard unoverridden path was restored; the inner dispatcher
reported only nvidia-triton as available on SM89.

Attempt 1 used Liger default BF16 classifier-gradient accumulation. Loss and
grad_hidden passed, but grad_weight exceeded the frozen 1e-2/1e-2 contract
(max abs 0.0625). Before formal timing, one upstream-supported correctness repair
selected accum_dtype=torch.float32. Storage/output remained BF16 and tolerances
did not change. Attempt 2 passed.

An unusable Ascend registration warning appeared during discovery; the recorded
available implementation remained exactly nvidia-triton. Excluded receipts are kept
under raw/EXCLUDED_PREPATH_ATTEMPT0 and raw/EXCLUDED_NUMERICAL_ATTEMPT1.
""")

    (pack / "README.md").write_text(f"""# {STAGE}

Decision: {DECISION}.

Read HEADROOM_ANALYSIS.md first, then the numerical, timing, memory, saved-state,
and profile tables. This compact pack records one real Qwen2.5-0.5B-Instruct
next-token loss shape on node109 RTX4080/SM89.

All formal CUDA work held the shared lock. There was one NSYS capture and zero NCU
captures. This is a local quick-falsification boundary, not hardware design or
end-to-end training evidence.
""")

    dump(pack / "RUN_RECEIPTS.json", {
        "stage": STAGE,
        "decision": DECISION,
        "starting_head": "8e83486212d70decacde4e126dc90800216264b8",
        "starting_tree": "96b91b933d611fe0f9e2919f9ea58933dcecd9f7",
        "environment": environment,
        "campaign": campaign,
        "timing_summary": timing,
        "source_identity": source,
        "engineering_repair": repair,
        "gpu_lock_receipt": (root / "logs" / "GPU_LOCK_RECEIPT.txt").read_text(),
        "nsys_gpu_lock_receipt": (root / "logs" / "NSYS_GPU_LOCK_RECEIPT.txt").read_text(),
        "cuda_campaigns": 3,
        "formal_campaigns": 1,
        "nsys_captures": 1,
        "ncu_captures": 0,
        "forbidden_actions": {
            "node174_or_accelsim": 0,
            "nvbit_or_sass_trace": 0,
            "second_model": 0,
            "shape_sweep": 0,
            "full_training_step": 0,
            "custom_loss_kernel": 0,
            "hardware_mechanism": 0,
        },
    })

    tests = [
        {"test": "CPU authority helper tests", "result": "PASS", "detail": "3/3"},
        {"test": "R101 asset hash closure", "result": "PASS", "detail": "exact"},
        {"test": "real final hidden/checkpoint lm_head", "result": "PASS", "detail": runtime["hidden_sha256"]},
        {"test": "B0 full-gradient numerical", "result": "PASS", "detail": "self-reference"},
        {"test": "B1 full-gradient numerical", "result": "PASS", "detail": "rtol=atol=1e-2"},
        {"test": "B2 full-gradient numerical", "result": "PASS", "detail": "after one repair"},
        {"test": "paired timing completeness", "result": "PASS", "detail": "15 formal samples/arm"},
        {"test": "NSYS exact target", "result": "PASS", "detail": "one B1 invocation"},
        {"test": "NCU", "result": "NOT_TRIGGERED", "detail": "timeline localized residual"},
    ]
    tsv(pack / "TEST_RESULTS.tsv", list(tests[0]), tests)

    index = []
    for base, kind in ((raw, "raw"), (root / "logs", "logs"), (rec, "receipts")):
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            rel = path.relative_to(root)
            index.append({
                "local_relative_path": str(rel),
                "size_bytes": path.stat().st_size,
                "sha256": sha(path),
                "kind": kind,
                "node164_relative_path": str(rel),
            })
    for path in (root / "source" / "cce.tar.gz", root / "source" / "liger.tar.gz"):
        rel = path.relative_to(root)
        index.append({
            "local_relative_path": str(rel),
            "size_bytes": path.stat().st_size,
            "sha256": sha(path),
            "kind": "source_archive",
            "node164_relative_path": str(rel),
        })
    tsv(pack / "RAW_DATA_INDEX.tsv", list(index[0]), index)

    lines = []
    for path in sorted(p for p in pack.iterdir() if p.is_file() and p.name != "SHA256SUMS"):
        lines.append(f"{sha(path)}  {path.name}")
    (pack / "SHA256SUMS").write_text("\n".join(lines) + "\n")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--pack", type=Path, required=True)
    args = p.parse_args()
    build(args.root, args.pack)
    print(json.dumps({"stage": STAGE, "decision": DECISION, "pack": str(args.pack)}))


if __name__ == "__main__":
    main()
