#!/usr/bin/env python3
"""Recompute and freeze all CPU-only GPT-3 public-shape preparation assets."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

from contracts import (
    A_BINARY_SHA256, B_BINARY_SHA256, CONDITIONER_BYTES, EXPECTED_TINY_REFERENCE_SHA256,
    GROUP_SIZE, L2_BYTES, POINTS, QWEIGHT_WORD_I32, QWEIGHT_WORD_U32, QZERO_WORD_I32,
    QZERO_WORD_U32, SCALE, SYNTH_VERSION, WORKSPACE_RESERVE_BYTES, canonical_tables,
    dequantized_nibbles, tiny_reference,
)

AB_COMMIT = "0e88faa28c9066b48e394dce657d7a16e6332a32"
STATE_COMMIT = "3aad5887b9b4c5bec801962bf8035fed9d485f47"
AWQ_COMMIT = "c7b0e88c327694c715b0a758d9ce8fd414a1fa21"
PAB = "docs/vm_tlb/review_packs/C16_LOWBIT_SPLITK_NATIVE_AB_109_V1"
PSTATE = "docs/vm_tlb/review_packs/C16_SPLITK_MEMORY_STATE_INTERACTION_109_V1"


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def show(repo: Path, commit: str, path: str) -> str:
    return git(repo, "show", f"{commit}:{path}")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", extrasaction="ignore", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def old_qwen_contract(repo: Path) -> dict:
    bindings = list(csv.DictReader(show(repo, AB_COMMIT, f"{PAB}/INPUT_AND_WEIGHT_BINDINGS.tsv").splitlines(), delimiter="\t"))
    old_timing = list(csv.DictReader(show(repo, AB_COMMIT, f"{PAB}/TIMING_SUMMARY.tsv").splitlines(), delimiter="\t"))
    state_timing = list(csv.DictReader(show(repo, STATE_COMMIT, f"{PSTATE}/TIMING_SUMMARY.tsv").splitlines(), delimiter="\t"))
    manifest = json.loads(show(repo, STATE_COMMIT, f"{PSTATE}/SOURCE_AND_RUN_MANIFEST.json"))
    qweight = {row["operator"]: int(row["bytes"]) for row in bindings if row["tensor"] == "qweight"}
    warm = {}
    for row in old_timing:
        warm.setdefault(row["point"], {})[row["arm"]] = float(row["median_ms"])
    state_cells, derived = {}, {}
    for row in state_timing:
        if row["record_type"] == "CELL":
            state_cells.setdefault(row["operator"], {})[row["cell"]] = float(row["median_ms"])
        elif row["record_type"] == "DERIVED":
            derived[row["operator"]] = {key: float(row[key]) for key in ("gain_W", "gain_E", "state_interaction")}
    return {
        "status": "FROZEN_COMPARISON_FIELDS_ONLY_NO_NEW_CONCLUSION",
        "authorities": {"native_ab": AB_COMMIT, "state_interaction": STATE_COMMIT},
        "accepted_binaries": manifest["accepted_binaries"],
        "l2_bytes": manifest["conditioner"]["expected_l2_bytes"],
        "qweight_bytes": qweight,
        "qweight_over_l2": {key: value / L2_BYTES for key, value in qweight.items()},
        "old_launch_contract_M256": manifest["launch_contract"],
        "old_launch_contract_M1": {
            "up_proj": {"A_gemm_grid": 1184, "B_gemm_grid": 148},
            "down_proj": {"A_gemm_grid": 224, "B_gemm_grid": 28},
        },
        "old_native_ab_median_ms": warm,
        "old_M256_state_cell_median_ms": state_cells,
        "old_M256_state_derived": derived,
        "comparison_rules": [
            "compare directions and preregistered fields only",
            "do not splice medians across ABBA and per-sample-state protocols",
            "do not prewrite the GPT-3-size conclusion",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--awq-source-repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out; out.mkdir(parents=True, exist_ok=True)
    if git(args.awq_source_repo, "rev-parse", AWQ_COMMIT) != AWQ_COMMIT:
        raise RuntimeError("AutoAWQ source commit mismatch")
    gemm_path = "awq_ext/quantization/gemm_cuda_gen.cu"
    gemv_path = "awq_ext/quantization/gemv_cuda.cu"
    gemm = git(args.awq_source_repo, "show", f"{AWQ_COMMIT}:{gemm_path}")
    gemv = git(args.awq_source_repo, "show", f"{AWQ_COMMIT}:{gemv_path}")
    required = (
        "uint32_t zeros_loaded", "dequantize_s4_to_fp16x2(zeros_loaded)",
        'asm volatile("sub.f16x2', "current_single_weight_fp - current_zeros",
    )
    if not all(token in gemm + gemv for token in required):
        raise RuntimeError("packed zero semantics unresolved")
    if dequantized_nibbles() != [-7*SCALE, -5*SCALE, -3*SCALE, -1*SCALE, 1*SCALE, 3*SCALE, 5*SCALE, 7*SCALE]:
        raise RuntimeError("synthetic nibble pattern is not symmetric nondegenerate")
    tiny = tiny_reference()
    if EXPECTED_TINY_REFERENCE_SHA256 != "TO_BE_FROZEN" and tiny["reference_sha256"] != EXPECTED_TINY_REFERENCE_SHA256:
        raise RuntimeError("tiny reference hash mismatch")
    budget, launch = canonical_tables()
    if max(row["max_peak_bound_bytes"] for row in budget) >= 16 * 1024**3:
        raise RuntimeError("16GiB peak budget failed")
    write_tsv(out / "SHAPE_AND_MEMORY_BUDGET.tsv", budget, list(budget[0]))
    write_tsv(out / "EXPECTED_LAUNCH_AND_SCRATCH.tsv", launch, list(launch[0]))
    synthetic = {
        "version": SYNTH_VERSION,
        "dense": {
            "input_formula": "x[m,k]=(1+((3*m+k)%7))*2^-10, generated in-place by 7 row-residue classes",
            "weight_formula": "w[k,n]=(1+((5*k+n)%11))*2^-12, generated in-place by 11 row-residue classes",
            "dtype": "float16", "all_values_finite_nonzero": True,
        },
        "w4": {
            "input_formula": "x[m,k]=(1+((5*m+3*k)%7))*2^-10",
            "qweight_word_hex": f"0x{QWEIGHT_WORD_U32:08x}", "qweight_word_signed_int32": QWEIGHT_WORD_I32,
            "qweight_little_endian_nibbles": [0,2,4,6,8,10,12,14],
            "qzero_word_hex": f"0x{QZERO_WORD_U32:08x}", "qzero_word_signed_int32": QZERO_WORD_I32,
            "qzero_nibble": 7, "scale_float16": SCALE,
            "dequantized_nibble_values": dequantized_nibbles(), "group_size": GROUP_SIZE,
            "zero_semantics": "kernel dequantizes packed qweight and packed qzero nibbles, then computes (q-z)*scale; no hidden +1",
            "source_authority": {"commit": AWQ_COMMIT, "gemm_path": gemm_path, "gemv_path": gemv_path,
                                 "gemm_blob": git(args.awq_source_repo,"rev-parse",f"{AWQ_COMMIT}:{gemm_path}"),
                                 "gemv_blob": git(args.awq_source_repo,"rev-parse",f"{AWQ_COMMIT}:{gemv_path}")},
        },
        "tiny_reference": tiny,
        "generation_constraints": ["no Python hash/random/global RNG", "no full-size tensor files", "generate only current operator", "A/B share bit-exact tensors"],
    }
    dump(out / "SYNTHETIC_TENSOR_CONTRACT.json", synthetic)
    dump(out / "OLD_QWEN_COMPARISON_CONTRACT.json", old_qwen_contract(args.repo))
    validation = {
        "status": "PASS",
        "independent_point_count": len(POINTS), "launch_row_count": len(launch),
        "all_dimensions_divisible": True, "all_peak_bounds_below_16GiB": True,
        "maximum_peak_bound_bytes": max(row["max_peak_bound_bytes"] for row in budget),
        "minimum_headroom_bytes": min(row["headroom_bytes"] for row in budget),
        "workspace_reserve_bytes": WORKSPACE_RESERVE_BYTES,
        "conditioner_bytes": CONDITIONER_BYTES,
        "tiny_reference_sha256": tiny["reference_sha256"],
        "packed_zero_semantics": "PASS_EXACT_HISTORICAL_SOURCE",
        "gpu_used": False, "cuda_imported": False, "gpu_lock_requested": False, "lane4_partial_accessed": False,
    }
    dump(out / "STATIC_VALIDATION.json", validation)
    print(json.dumps(validation, sort_keys=True))


if __name__ == "__main__":
    main()
