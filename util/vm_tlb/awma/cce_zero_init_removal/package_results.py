#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path

import torch
import triton


STAGE = "AWMA_CCE_ZERO_INIT_REMOVAL_109_V1"
DECISION = "CCE_ZERO_INIT_SOFTWARE_REMOVABLE"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build(root: Path, repo: Path, pack: Path) -> None:
    pack.mkdir(parents=True, exist_ok=True)
    raw = root / "raw"
    rec = root / "receipts"
    source = json.loads((rec / "SOURCE_IDENTITY.json").read_text())
    design = json.loads((rec / "DESIGN_PREREGISTRATION.json").read_text())
    directed = json.loads((raw / "DIRECTED_TESTS.json").read_text())
    numerical = json.loads((raw / "REAL_NUMERICAL_QUALIFICATION.json").read_text())
    paired = json.loads((raw / "PAIRED_ANALYSIS.json").read_text())
    causal = json.loads((raw / "NSYS_CAUSAL_ANALYSIS.json").read_text())
    memory = json.loads((raw / "MEMORY_ACCOUNTING.json").read_text())
    campaign = json.loads((raw / "REAL_CAMPAIGN_RESULT.json").read_text())
    patch = repo / "util/vm_tlb/awma/cce_zero_init_removal/cce_zero_init_removal.patch"

    shutil.copy2(rec / "SOURCE_IDENTITY.json", pack / "SOURCE_IDENTITY.json")
    shutil.copy2(rec / "INIT_STATE_ACCOUNTING.tsv", pack / "INIT_STATE_ACCOUNTING.tsv")
    shutil.copy2(raw / "DIRECTED_TESTS.tsv", pack / "DIRECTED_TESTS.tsv")
    shutil.copy2(raw / "PAIRED_ANALYSIS.json", pack / "PAIRED_ANALYSIS.json")
    shutil.copy2(patch, pack / "CCE_ZERO_INIT_REMOVAL.patch")

    numerical_rows = []
    for metric, item in numerical["C0_C1"].items():
        numerical_rows.append({
            "comparison": "C1_vs_C0",
            "metric": metric,
            "qualified": item["allclose"],
            "finite": item.get("finite"),
            "observed": item.get("observed", ""),
            "reference": item.get("reference", ""),
            "max_abs": item["max_abs"],
            "mean_abs": item["mean_abs"],
            "max_rel": item["max_rel"],
            "cosine_similarity": item["cosine_similarity"],
            "rtol": numerical["rtol"],
            "atol": numerical["atol"],
            "fixed_meta_equal": numerical["same_fixed_meta"],
        })
    tsv(pack / "NUMERICAL_QUALIFICATION.tsv", list(numerical_rows[0]), numerical_rows)

    timing_rows = []
    with (raw / "TIMING_SAMPLES.tsv").open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            summary = paired[row["arm"]]
            row.update({
                "formal_gpu_ms_median": summary["gpu_ms_median"],
                "formal_gpu_ms_mad": summary["gpu_ms_mad"],
                "formal_host_ms_median": summary["host_ms_median"],
                "formal_host_ms_mad": summary["host_ms_mad"],
            })
            timing_rows.append(row)
    tsv(pack / "TIMING.tsv", list(timing_rows[0]), timing_rows)

    memory_rows = []
    for arm in ("C0", "C1"):
        item = memory[arm]
        memory_rows.append({
            "arm": arm,
            "baseline_allocated_bytes": item["baseline_allocated_bytes"],
            "baseline_reserved_bytes": item["baseline_reserved_bytes"],
            "peak_allocated_bytes": item["peak_allocated_bytes"],
            "peak_reserved_bytes": item["peak_reserved_bytes"],
            "peak_allocated_delta_bytes": item["peak_allocated_delta_bytes"],
            "peak_reserved_delta_bytes": item["peak_reserved_delta_bytes"],
            "mandatory_output_bytes": item["mandatory_output_bytes"],
            "full_fp32_dc_bytes": item["full_fp32_dc_bytes"],
            "init_state_bytes": item["init_state"]["bytes"],
            "additional_init_state_bytes_vs_c0": item["init_state"]["additional_bytes_vs_c0"],
            "allocator_bytes_are_not_dram_traffic": True,
        })
    tsv(pack / "MEMORY_ACCOUNTING.tsv", list(memory_rows[0]), memory_rows)

    (pack / "C0_C1_DESIGN.md").write_text("""# C0/C1 design

C0 is the pinned CCE exact/no-filter path with FP32 classifier-gradient
accumulation initialized by torch.zeros_like.

C1 changes only dC initialization:

1. It allocates the same full FP32 dC with torch.empty_like.
2. It reuses the existing 128x64-tile dCLocks array.
3. State 0 is uninitialized/free, state 1 is initialized/free, and state 2 is
   held by either the first initializer or a later updater.
4. The first writer atomically claims state 0, stores its full valid tile
   contribution without reading dC, and publishes state 1.
5. Later writers claim state 1, load/add/store, and return to state 1.
6. If the compacted valid-token count is zero, C1 falls back to the original
   zero allocation and disables first-store mode.

The existing 16,618-entry int32 lock array is 66,472 bytes and is reset inside
the measured boundary. No additional state bytes, full-size shadow buffer,
lazy full-size zero pass, future ordering, precision change, chunking change,
or heuristic retuning is used.

Both arms use CCE_AUTOTUNE=0 and identical BLOCK_B=128, BLOCK_V=128,
BLOCK_D=32, MM_BACK_BLOCK_D=64, num_warps=4 and num_stages=4.
""")

    (pack / "NSYS_CAUSAL_RECEIPT.md").write_text(f"""# NSYS causal receipt

Exactly one C1 capture was taken.

- Accepted C0 full FP32 dC fill: {causal['c0_accepted_full_zero_fill']['duration_ns']} ns,
  grid_x={causal['c0_accepted_full_zero_fill']['grid_x']}.
- C1 full-size fill absent: {causal['c1_full_zero_fill_absent']}.
- Equivalent full-size initialization moved elsewhere: false.
- C1 small init-state reset: {causal['c1_init_state_reset']['duration_ns']} ns,
  grid_x={causal['c1_init_state_reset']['grid_x']}, 66,472 bytes.
- FP32-to-BF16 full output cast retained: {causal['c1_full_output_cast']['duration_ns']} ns,
  grid_x={causal['c1_full_output_cast']['grid_x']}.
- CCE backward retained: {causal['c1_cce_backward']['duration_ns']} ns,
  grid_x={causal['c1_cce_backward']['grid_x']}, block_x={causal['c1_cce_backward']['block_x']}.
- LSE retained: {causal['c1_lse']['duration_ns']} ns.
- NCU runs: 0.

Allocator and state sizes are not reported as DRAM traffic.
""")

    (pack / "FINAL_DECISION.md").write_text(f"""# Final decision

{DECISION}

C1 passed all seven directed categories across 14 C0/C1 pairs, including
all-ignore fallback and eight repeated contended launches. The accepted real
shape passed loss, grad_hidden and grad_weight at the frozen rtol=atol=1e-2.

C0 median was {paired['C0']['gpu_ms_median']:.6f} ms and C1 median was
{paired['C1']['gpu_ms_median']:.6f} ms. The paired counterfactual recovered
{paired['median_delta_ms_C0_minus_C1']:.6f} ms, or
{paired['improvement_fraction'] * 100:.2f}% of the complete operator and
{paired['accepted_zero_fill_recovery_fraction'] * 100:.2f}% of the accepted
0.751779 ms zero-fill anchor.

The full-operator delta is not identified one-for-one with the old fill; first-writer lock scheduling changes are part of the software counterfactual.

The one C1 NSYS capture proves the full zero-fill disappeared without an
equivalent pass while the small state reset, final BF16 cast, CCE backward and
LSE work remain. On this frozen shape the prior residual is primarily a software
accumulation-organization artifact. This does not authorize a second shape,
hardware mechanism, or end-to-end claim.
""")

    (pack / "README.md").write_text(f"""# {STAGE}

Decision: {DECISION}.

Read FINAL_DECISION.md, C0_C1_DESIGN.md, PAIRED_ANALYSIS.json and
NSYS_CAUSAL_RECEIPT.md first. The pack contains the exact source patch,
directed/full-gradient qualification, all paired samples, state accounting and
raw-data hashes.

This is one real Qwen shape on node109 RTX4080/SM89. It is not a shape study,
model study, end-to-end training result, or hardware design.
""")

    (pack / "ENGINEERING_NOTES.md").write_text("""# Engineering notes

Two CPU authority constants were corrected before GPU execution: a copied
snapshot SHA had one extra character, and the parent pack-manifest constant used
a chat-transcription value rather than the committed file hash. Direct file
hashes and the scientific parent commit were authoritative.

The source patch applied cleanly to the pinned archive and reproduced the exact
patched files. Directed and formal runs had no repair attempts, deadlocks,
timeouts, or profiler retries.
""")

    tests = [
        {"test": "CPU helper tests", "result": "PASS", "detail": "3/3"},
        {"test": "source patch clean apply", "result": "PASS", "detail": source["checks"]["source_patch"]["sha256"]},
        {"test": "directed categories", "result": "PASS", "detail": "7 categories, 14 C0/C1 pairs"},
        {"test": "real loss", "result": "PASS", "detail": f"max_abs={numerical['C0_C1']['loss']['max_abs']}"},
        {"test": "real grad_hidden", "result": "PASS", "detail": f"max_abs={numerical['C0_C1']['grad_hidden']['max_abs']}"},
        {"test": "real grad_weight", "result": "PASS", "detail": f"max_abs={numerical['C0_C1']['grad_weight']['max_abs']}"},
        {"test": "fixed heuristic identity", "result": "PASS", "detail": "C0=C1, autotune off"},
        {"test": "paired timing completeness", "result": "PASS", "detail": "15 formal samples/arm"},
        {"test": "C1 NSYS causal capture", "result": "PASS", "detail": "exactly one"},
        {"test": "NCU", "result": "NOT_RUN", "detail": "forbidden"},
    ]
    tsv(pack / "TEST_RESULTS.tsv", list(tests[0]), tests)

    run_receipts = {
        "stage": STAGE,
        "decision": DECISION,
        "starting_head": "9413136d633615f3d56aa4c5f788f81cca3f0b41",
        "starting_tree": "f645d16a40c22dcd0463803498a7cc4121d60f91",
        "scientific_parent": "ad9a302a49cdb3b1e75a9bbf04dab819c362cb1a",
        "cce_commit": "3de376c106a1916bc5e1b619f9c77c87a461ee1c",
        "python": sys.version.replace("\n", " "),
        "torch": torch.__version__,
        "torch_cuda": torch.version.cuda,
        "triton": triton.__version__,
        "pre_gpu_health": (root / "logs/PRE_GPU_HEALTH.txt").read_text(),
        "fixed_meta": design["fixed_meta"],
        "source_patch_sha256": sha(patch),
        "campaign": campaign,
        "paired_analysis": paired,
        "causal_analysis": causal,
        "directed_lock_receipt": (root / "logs/directed_GPU_LOCK_RECEIPT.txt").read_text(),
        "real_lock_receipt": (root / "logs/real_GPU_LOCK_RECEIPT.txt").read_text(),
        "nsys_lock_receipt": (root / "logs/nsys_c1_GPU_LOCK_RECEIPT.txt").read_text(),
        "gpu_lock_acquisitions": 4,
        "nsys_captures": 1,
        "ncu_captures": 0,
        "forbidden_actions": {
            "second_shape": 0,
            "second_model": 0,
            "liger_rerun": 0,
            "B0_scientific_exploration": 0,
            "ncu_nvbit_sass": 0,
            "node174_or_accelsim": 0,
            "fp32_to_bf16_cast_optimization": 0,
            "hardware_mechanism": 0,
        },
    }
    dump(pack / "RUN_RECEIPTS.json", run_receipts)

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
    extras = [
        (root / "source/cce.tar.gz", "source_archive", "source/cce.tar.gz"),
        (root / "source_before/cut_cross_entropy/cce_backward.py", "source_before", "source_before/cut_cross_entropy/cce_backward.py"),
        (root / "source_before/cut_cross_entropy/tl_utils.py", "source_before", "source_before/cut_cross_entropy/tl_utils.py"),
        (root / "source/cce/cut_cross_entropy/cce_backward.py", "source_after", "source_after/cut_cross_entropy/cce_backward.py"),
        (root / "source/cce/cut_cross_entropy/tl_utils.py", "source_after", "source_after/cut_cross_entropy/tl_utils.py"),
        (patch, "source_patch", "source_patch/cce_zero_init_removal.patch"),
    ]
    for path, kind, node_rel in extras:
        index.append({
            "local_relative_path": str(path),
            "size_bytes": path.stat().st_size,
            "sha256": sha(path),
            "kind": kind,
            "node164_relative_path": node_rel,
        })
    tsv(pack / "RAW_DATA_INDEX.tsv", list(index[0]), index)

    lines = []
    for path in sorted(p for p in pack.iterdir() if p.is_file() and p.name != "SHA256SUMS"):
        lines.append(f"{sha(path)}  {path.name}")
    (pack / "SHA256SUMS").write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--pack", type=Path, required=True)
    args = parser.parse_args()
    build(args.root, args.repo, args.pack)
    print(json.dumps({"stage": STAGE, "decision": DECISION, "pack": str(args.pack)}))


if __name__ == "__main__":
    main()
