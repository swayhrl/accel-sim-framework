#!/usr/bin/env python3
"""CPU-only source and contract preparation for the C16 cross-M reuse screen."""
from __future__ import annotations

import argparse
import csv
import difflib
import gzip
import hashlib
import json
import subprocess
from pathlib import Path
from textwrap import dedent


GOAL = "C16_SPLITK_CROSSM_REUSE_CAUSAL_PREP_174NEW_V1"
COORD = "2d1db5b8262f07fa7ebdec6122ac7359fdd86960"
SOURCE_COMMIT = "c7b0e88c327694c715b0a758d9ce8fd414a1fa21"
GEN_REL = "awq_ext/quantization/gemm_cuda_gen.cu"
HDR_REL = "awq_ext/quantization/gemm_cuda.h"
GEN_BLOB = "98f49efac8626388039912e6aabc8a84d9f8303b"
GEN_SHA = "974980f34d7269c9a33ccd642d9dc9bc8700f58e9afc63d65634dedd9c5fc5a6"
HDR_BLOB = "afc8165157dfc646049f548b706d9fb86fb685fc"
HDR_SHA = "2e962fb644d131795cf2f9f96c5b45c693b7a6962426fb993809cc3fd47bc187"
STATUS = "READY_FOR_NATIVE_CAUSAL_SCREEN"

M, N, GROUP, REPLICAS = 256, 49152, 128, 16
KS = (2560, 3072)
SPLITS = (("A", 8), ("B", 1))
STATES = (("SHARED", 0), ("PER_MTILE", 15))
DEVICE_BYTES = 16_718_168_064
RUNTIME_RESERVE_BYTES = 2 * 2**30
OUT_BYTES = M * N * 2

TENSOR_HASHES = {
    2560: {
        "input": "c1ddb7e0036fc80a2726dc63e5a880653abc7a08f741df783994c938ab6e3b19",
        "qweight": "dab8866b4eb644ca9e7be2e34e237f95428ded0771d661ad5ca311d01384b50b",
        "qzeros": "3c389c0733bc9a91b32156a4627bb10cd853fe011f028b320ae5d85c463bb6a9",
        "scales": "b0222a5228d1ae3ddb9cac42ba31181ad90fb11728090bb69fe797582ba17a04",
    },
    3072: {
        "input": "6866666ea32d1e37956bdba16c1b6a6c4b5c63f887153aa6004b77696c92c974",
        "qweight": "09f3642eab83ded59a6c30fc70763256524a6706d2d8015699c0db442fde5b67",
        "qzeros": "d1123eed445d6e124e63cd3762c9ac98cbdf64a696b770dc518d72d43191bb17",
        "scales": "e7d8f76ae975fa6e31c766e831b3d9e7f7b60ff72929b1102b036153509e69fa",
    },
}

ACCEPTED_OUTPUT = {
    2560: {
        "A": "e758e1725afa7e4fd8520e6e5e3c43f11806a8854f482c46750ccbf44f4859eb",
        "B": "b71bed6bc0277ac3d69eeb84a91aef783f4eba40d1dce18ab100595d6078682d3",
    },
    3072: {
        "A": "76be531cfe46bb847a95aad4fd49910d6715450a15c39681968b0ef1371a34db",
        "B": "76be531cfe46bb847a95aad4fd49910d6715450a15c39681968b0ef1371a34db",
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_tsv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def transform_generator(old: str) -> str:
    text = replace_once(
        old,
        "gemm_forward_4bit_cuda_m16n128k32(int G, int split_k_iters, half*",
        "gemm_forward_4bit_cuda_m16n128k32(int G, int split_k_iters, int replica_mask, half*",
        "target kernel signature",
    )
    kernel_start = text.index("__global__ void __launch_bounds__(64) gemm_forward_4bit_cuda_m16n128k32")
    kernel_end = text.index("__global__ void __launch_bounds__(64) gemm_forward_4bit_cuda_m16n64k32", kernel_start)
    kernel = text[kernel_start:kernel_end]
    kernel = replace_once(kernel, "half* __restrict__ C) \n{", "half* __restrict__ C)\n{", "target signature whitespace")
    anchor = "  int blockIdx_z = blockIdx.x / ((M + 16 - 1) / 16 * j_factors1);\n"
    insert = (
        anchor
        + "  int replica_id = (blockIdx_y / j_factors1) & replica_mask;\n"
        + "  long long qweight_replica_stride = static_cast<long long>(IC) * (OC / 8);\n"
        + "  long long qzeros_replica_stride = static_cast<long long>(IC / G) * (OC / 8);\n"
        + "  long long scales_replica_stride = static_cast<long long>(IC / G) * OC;\n"
    )
    kernel = replace_once(kernel, anchor, insert, "replica arithmetic")
    kernel = replace_once(
        kernel,
        "  int* B_ptr = B\n            + ((int)threadIdx.y)",
        "  int* B_ptr = B\n            + replica_id * qweight_replica_stride\n            + ((int)threadIdx.y)",
        "qweight base",
    )
    kernel = replace_once(
        kernel,
        "  int* zeros_ptr = zeros\n                + (((int)blockIdx_y)",
        "  int* zeros_ptr = zeros\n                + replica_id * qzeros_replica_stride\n                + (((int)blockIdx_y)",
        "qzeros base",
    )
    kernel = replace_once(
        kernel,
        "  half* scaling_factors_ptr = scaling_factors\n                            + (((int)blockIdx_y)",
        "  half* scaling_factors_ptr = scaling_factors\n                            + replica_id * scales_replica_stride\n                            + (((int)blockIdx_y)",
        "scales base",
    )
    text = text[:kernel_start] + kernel + text[kernel_end:]

    start = text.index("torch::Tensor gemm_forward_cuda(\n")
    prefix, wrapper = text[:start], text[start:]
    wrapper = replace_once(
        wrapper,
        "    torch::Tensor _zeros,\n    int split_k_iters)\n{\n    int num_in_feats",
        "    torch::Tensor _zeros,\n    int split_k_iters,\n    int replica_mask)\n{\n"
        "    if (replica_mask != 0 && replica_mask != 15)\n"
        "        throw std::invalid_argument(\"replica_mask must be 0 or 15\");\n"
        "    if (split_k_iters != 1 && split_k_iters != 8)\n"
        "        throw std::invalid_argument(\"split_k_iters must be 1 or 8\");\n"
        "    if (_in_feats.dim() != 2 || _kernel.dim() != 3 ||\n"
        "        _scaling_factors.dim() != 3 || _zeros.dim() != 3)\n"
        "        throw std::invalid_argument(\"replica tensors must use frozen 3D layout\");\n"
        "    if (!_in_feats.is_contiguous() || !_kernel.is_contiguous() ||\n"
        "        !_scaling_factors.is_contiguous() || !_zeros.is_contiguous())\n"
        "        throw std::invalid_argument(\"all tensors must be contiguous\");\n"
        "    int num_in_feats",
        "wrapper ABI and validation",
    )
    wrapper = replace_once(
        wrapper,
        "    int num_in_channels = _in_feats.size(1);\n",
        "    int num_in_channels = _in_feats.size(1);\n"
        "    if (num_in_feats != 256 || (num_in_channels != 2560 && num_in_channels != 3072))\n"
        "        throw std::invalid_argument(\"frozen contract requires M=256 and K in {2560,3072}\");\n"
        "    if (_kernel.size(0) != 16 || _scaling_factors.size(0) != 16 ||\n"
        "        _zeros.size(0) != 16 || _kernel.size(1) != num_in_channels)\n"
        "        throw std::invalid_argument(\"replica count or qweight K extent mismatch\");\n",
        "frozen M/K/replicas",
    )
    wrapper = replace_once(wrapper, "_kernel.size(1) * 8", "_kernel.size(2) * 8", "replicated qweight shape")
    wrapper = replace_once(
        wrapper,
        "    int num_out_channels = _out_feats.size(-1);\n",
        "    int num_out_channels = _out_feats.size(-1);\n"
        "    if (num_out_channels != 49152 || _scaling_factors.size(2) != num_out_channels ||\n"
        "        _zeros.size(2) * 8 != num_out_channels ||\n"
        "        _scaling_factors.size(1) != _zeros.size(1) ||\n"
        "        _scaling_factors.size(1) == 0 ||\n"
        "        num_in_channels % _scaling_factors.size(1) != 0)\n"
        "        throw std::invalid_argument(\"frozen N/group metadata shape mismatch\");\n",
        "frozen N/metadata shape",
    )
    wrapper = replace_once(
        wrapper,
        "int group_size = num_in_channels / _scaling_factors.size(0);",
        "int group_size = num_in_channels / _scaling_factors.size(1);\n"
        "    if (group_size != 128)\n"
        "        throw std::invalid_argument(\"frozen contract requires group_size=128\");",
        "group size from per-replica extent",
    )
    wrapper = replace_once(
        wrapper,
        "        gemm_forward_4bit_cuda_m16n128k32<<<num_blocks, threads_per_block, 0, stream>>>(\n"
        "            group_size, split_k_iters, in_feats, kernel, scaling_factors, zeros,",
        "        gemm_forward_4bit_cuda_m16n128k32<<<num_blocks, threads_per_block, 0, stream>>>(\n"
        "            group_size, split_k_iters, replica_mask, in_feats, kernel, scaling_factors, zeros,",
        "target kernel launch argument",
    )
    wrapper = replace_once(
        wrapper,
        "    return _out_feats.sum(0);\n}",
        "    if (split_k_iters == 1)\n        return _out_feats.select(0, 0);\n"
        "    return _out_feats.sum(0);\n}",
        "split1 direct output",
    )
    return prefix + wrapper


def transform_header(old: str) -> str:
    return replace_once(
        old,
        "torch::Tensor _scaling_factors, torch::Tensor _zeros, int split_k_iters);",
        "torch::Tensor _scaling_factors, torch::Tensor _zeros, int split_k_iters,\n"
        "    int replica_mask);",
        "header ABI",
    )


def target_kernel(text: str) -> str:
    start = text.index("__global__ void __launch_bounds__(64) gemm_forward_4bit_cuda_m16n128k32")
    end = text.index("__global__ void __launch_bounds__(64) gemm_forward_4bit_cuda_m16n64k32", start)
    return text[start:end]


def build_patch(source: Path) -> tuple[bytes, dict]:
    gen_bytes = (source / GEN_REL).read_bytes()
    hdr_bytes = (source / HDR_REL).read_bytes()
    if sha(gen_bytes) != GEN_SHA or sha(hdr_bytes) != HDR_SHA:
        raise RuntimeError("exact AutoAWQ source hash mismatch")
    old_gen, old_hdr = gen_bytes.decode(), hdr_bytes.decode()
    new_gen, new_hdr = transform_generator(old_gen), transform_header(old_hdr)
    pieces = []
    for rel, old, new in ((GEN_REL, old_gen, new_gen), (HDR_REL, old_hdr, new_hdr)):
        pieces.extend(difflib.unified_diff(old.splitlines(True), new.splitlines(True), f"a/{rel}", f"b/{rel}"))
    patch = "".join(pieces).encode()
    old_kernel, new_kernel = target_kernel(old_gen), target_kernel(new_gen)
    count_keys = ("for (", "__syncthreads", "dequantize_s4_to_fp16x2", "mma.sync", "k_bound")
    counts = {key: {"old": old_kernel.count(key), "patched": new_kernel.count(key)} for key in count_keys}
    if any(x["old"] != x["patched"] for x in counts.values()):
        raise RuntimeError("compute/loop token count changed")
    for unchanged in ("half* A_ptr = A", "half* C_ptr = C", "int k_bound =", "for (int _k_0_0"):
        if old_kernel.count(unchanged) != new_kernel.count(unchanged):
            raise RuntimeError(f"unchanged anchor drift: {unchanged}")
    proof = {
        "old_generator_sha256": GEN_SHA,
        "old_header_sha256": HDR_SHA,
        "patched_generator_sha256": sha(new_gen.encode()),
        "patched_header_sha256": sha(new_hdr.encode()),
        "patch_sha256": sha(patch),
        "token_counts": counts,
        "state_path": "same compiled kernel; branch-free replica_id=(Mtile & replica_mask)",
        "device_kernel_added_semantics": [
            "runtime replica_mask parameter",
            "replica_id from accepted Mtile",
            "three replica strides",
            "replica base offsets for qweight/qzeros/scales",
        ],
        "host_only_changes": ["frozen tensor/shape checks", "3D replica layout", "split1 plane0 direct return inherited from accepted split1 authority"],
        "pybind_source_changed": False,
    }
    return patch, proof


def memory_rows() -> list[dict]:
    rows = []
    for k in KS:
        qweight = k * (N // 8) * 4
        qzeros = (k // GROUP) * (N // 8) * 4
        scales = (k // GROUP) * N * 2
        per_replica = qweight + qzeros + scales
        replica_assets = per_replica * REPLICAS
        input_bytes = M * k * 2
        for arm, split in SPLITS:
            scratch = split * OUT_BYTES
            output_extra = OUT_BYTES if split == 8 else 0
            explicit = replica_assets + input_bytes + scratch + output_extra
            budgeted = explicit + RUNTIME_RESERVE_BYTES
            for state, mask in STATES:
                rows.append({
                    "K": k,
                    "arm": arm,
                    "split_k_iters": split,
                    "state": state,
                    "replica_mask": mask,
                    "per_replica_weight_side_bytes": per_replica,
                    "replica_count": REPLICAS,
                    "all_replica_weight_side_bytes": replica_assets,
                    "input_bytes": input_bytes,
                    "scratch_bytes": scratch,
                    "extra_output_bytes": output_extra,
                    "explicit_live_bytes": explicit,
                    "runtime_reserve_bytes": RUNTIME_RESERVE_BYTES,
                    "budgeted_peak_bytes": budgeted,
                    "device_bytes": DEVICE_BYTES,
                    "headroom_bytes": DEVICE_BYTES - budgeted,
                    "headroom_gib": f"{(DEVICE_BYTES - budgeted) / 2**30:.6f}",
                    "pass": budgeted < DEVICE_BYTES,
                })
    return rows


def launch_rows() -> list[dict]:
    rows = []
    for k in KS:
        for arm, split in SPLITS:
            for state, mask in STATES:
                rows.append({
                    "K": k,
                    "M": M,
                    "N": N,
                    "arm": arm,
                    "split_k_iters": split,
                    "state": state,
                    "replica_mask": mask,
                    "gemm_grid": 49_152 if split == 8 else 6_144,
                    "gemm_block": "[32,2,1]",
                    "Ktile_iterations_per_CTA": (k // 32) // split,
                    "scratch_shape": json.dumps([split, M, N], separators=(",", ":")),
                    "scratch_bytes": split * OUT_BYTES,
                    "reduction_expected": split == 8,
                    "reduction_grid": 24_576 if split == 8 else 0,
                    "reduction_block": "[32,4,1]" if split == 8 else "NA",
                })
    return rows


def early(repo: Path, source: Path, out: Path) -> tuple[dict, dict]:
    if subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip() != COORD:
        raise RuntimeError("coordination HEAD mismatch")
    if subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip() != SOURCE_COMMIT:
        raise RuntimeError("AutoAWQ source commit mismatch")
    if subprocess.check_output(["git", "-C", str(source), "rev-parse", f"HEAD:{GEN_REL}"], text=True).strip() != GEN_BLOB:
        raise RuntimeError("AutoAWQ generator blob mismatch")
    if subprocess.check_output(["git", "-C", str(source), "rev-parse", f"HEAD:{HDR_REL}"], text=True).strip() != HDR_BLOB:
        raise RuntimeError("AutoAWQ header blob mismatch")
    out.mkdir(parents=True, exist_ok=True)
    patch, proof = build_patch(source)
    legacy_patch = out / "REPLICA_SOURCE.patch"
    if legacy_patch.exists():
        legacy_patch.unlink()
    patch_artifact = gzip.compress(patch, compresslevel=9, mtime=0)
    (out / "REPLICA_SOURCE.patch.gz").write_bytes(patch_artifact)
    memory = memory_rows()
    launches = launch_rows()
    write_tsv(out / "MEMORY_BUDGET.tsv", memory)
    write_tsv(out / "EXPECTED_LAUNCH.tsv", launches)
    bindings = {
        "patch_sha256": sha(patch),
        "patch_artifact": "REPLICA_SOURCE.patch.gz",
        "patch_artifact_sha256": sha(patch_artifact),
        "old_generator_sha256": GEN_SHA,
        "patched_generator_sha256": proof["patched_generator_sha256"],
        "expected_launch_sha256": sha((out / "EXPECTED_LAUNCH.tsv").read_bytes()),
        "memory_budget_sha256": sha((out / "MEMORY_BUDGET.tsv").read_bytes()),
    }
    gate = {
        "goal": GOAL,
        "status": STATUS,
        "coordination_commit": COORD,
        "source_isolation": {
            "same_patched_kernel_for_all_cells": True,
            "same_instruction_path_for_SHARED_and_PER_MTILE": True,
            "replica_address_arithmetic_has_branch": False,
            "only_state_dependent_kernel_value": "replica_mask (0 or 15)",
            "only_state_dependent_memory_semantic": "qweight/qzeros/scales replica base address",
            "A_input_formula_unchanged": True,
            "output_scratch_formula_unchanged": True,
            "load_counts_and_K_loop_unchanged": True,
            "dequant_mma_tile_grid_block_unchanged": True,
        },
        "memory": {
            "all_cells_pass": all(row["pass"] for row in memory),
            "maximum_budgeted_peak_bytes": max(row["budgeted_peak_bytes"] for row in memory),
            "minimum_headroom_bytes": min(row["headroom_bytes"] for row in memory),
            "runtime_reserve_bytes": RUNTIME_RESERVE_BYTES,
        },
        "launch": {"all_8_cells_frozen": len(launches) == 8, "matrix_rows": len(launches)},
        "replica": {
            "version": "GPT3_SHAPE_SYNTH_V1_CROSSM_REPLICA16_V1",
            "count": REPLICAS,
            "layout": {"qweight": "[16,K,N/8] int32", "qzeros": "[16,K/128,N/8] int32", "scales": "[16,K/128,N] float16"},
            "replica_sha_rule": "each replica slice SHA256 must equal replica0 and frozen per-K expected hash",
        },
        "matrix": {"K": list(KS), "M": M, "N": N, "split": [8, 1], "states": {"SHARED": 0, "PER_MTILE": 15}},
        "bindings": bindings,
        "authorization": {"lane7_native_causal_screen": True, "gpu_lock_required": True, "sass_capture": False, "simulation": False},
        "resource_attestation": {"cpu_only": True, "gpu_used": False, "cuda_imported": False, "gpu_lock_requested": False, "lane4_partial_accessed": False},
    }
    dump(out / "EARLY_GATE.json", gate)
    return gate, proof


def full(repo: Path, source: Path, out: Path, gate: dict, proof: dict) -> None:
    authority = {
        "goal": GOAL,
        "status": "PASS",
        "coordination_commit": COORD,
        "accepted_evidence": {
            "static_footprint_audit": "c72d28b17247f25d0c3613604ab6cab1737666e0",
            "native_threshold_series": "b17193ff6b3786fd01d5bfe83b5c1a0a03859729",
            "independent_threshold_consumer": "6d226cd99946d3bd7b41c5ee005285183efbb915",
            "native_L2_read_hit_diagnostic": "915707348617f7a8f432bad7a434a98d78b487c8",
            "simulator_non_admission": "f64a8c9100d0f2e779063291d31de1737a819304",
            "split1_patch_authority": "0e88faa28c9066b48e394dce657d7a16e6332a32",
        },
        "source": {"repo": "casper-hansen/AutoAWQ_kernels", "commit": SOURCE_COMMIT, "generator_blob": GEN_BLOB, "generator_sha256": GEN_SHA, "header_blob": HDR_BLOB, "header_sha256": HDR_SHA},
        "accepted_binaries": {"split8_sha256": "9e8d38a04c28770338fcef8ae0f9a90a984b7a8f95bcb98a407738594e1c08d7", "split1_sha256": "1aa8db13f5fd10651aa4241f58200e3a7075214d34cca4d70fbcbe7cbbc07887"},
        "patch": proof,
        "resource_attestation": gate["resource_attestation"],
    }
    dump(out / "AUTHORITY.json", authority)

    semantic = dedent(f"""
        # Replica patch semantic isolation

        The patch is based on AutoAWQ kernels `{SOURCE_COMMIT}`, generator blob `{GEN_BLOB}`. It creates a new independent extension and does not replace either accepted binary.

        Inside `gemm_forward_4bit_cuda_m16n128k32`, the only data-path additions are a runtime `replica_mask`, branch-free `replica_id=(blockIdx_y/j_factors1)&replica_mask`, three frozen per-replica strides, and those three offsets in the qweight, qzeros, and scales base pointers. SHARED uses mask 0; PER_MTILE uses mask 15. Both states execute the same compiled kernel and instruction path.

        The input/A pointer formula and output/scratch/C pointer formula are byte-for-byte unchanged. K bound, Ktile interleave, loop count, synchronization, global load count, dequantization, shared-memory layout, MMA, writeback, tile, grid, and block formulas are unchanged. Static token-count checks for loops, barriers, dequant calls, MMA statements, and `k_bound` are equal before and after the patch.

        Host-only changes adapt inputs to contiguous `[16,...]` replica tensors, reject any non-frozen M/K/N/mask/layout, pass `replica_mask`, and use the already accepted split1 direct-plane return while retaining split8 `sum(0)`. These host differences do not vary between SHARED and PER_MTILE within a split. `pybind_awq.cpp` is unchanged because it already binds the function pointer from `gemm_cuda.h`.

        Therefore the causal state contrast changes only which bit-identical weight-side replica base is addressed. It does not isolate qweight from qzeros/scales, so all conclusions must say “weight-side”.
        """).strip() + "\n"
    (out / "PATCH_SEMANTIC_DIFF.md").write_text(semantic, encoding="utf-8")

    points = {}
    for k in KS:
        qweight_elements = k * (N // 8)
        qzeros_elements = (k // GROUP) * (N // 8)
        scales_elements = (k // GROUP) * N
        points[str(k)] = {
            "input_sha256": TENSOR_HASHES[k]["input"],
            "per_replica_sha256": {name: TENSOR_HASHES[k][name] for name in ("qweight", "qzeros", "scales")},
            "strides_elements": {"qweight": qweight_elements, "qzeros": qzeros_elements, "scales": scales_elements},
            "accepted_output_sha256": ACCEPTED_OUTPUT[k],
        }
    replica = {
        "version": "GPT3_SHAPE_SYNTH_V1_CROSSM_REPLICA16_V1",
        "shape": {"M": M, "N": N, "K": list(KS), "group_size": GROUP},
        "states": {"SHARED": {"replica_mask": 0, "replica_id": "Mtile & 0 = 0"}, "PER_MTILE": {"replica_mask": 15, "replica_id": "Mtile & 15 = Mtile for Mtile 0..15"}},
        "allocation": "all cells allocate all 16 replicas directly in final contiguous 3D tensors; no full-size staging copy",
        "identity": "each of 16 slices must be byte-identical and independently hashed against the frozen per-K SHA256",
        "va_contract": "qweight/qzeros/scales slice ranges are half-open, non-overlapping, live through the cell, and recorded before GPU work",
        "input_output": "input is not replicated; scratch/output follow the original split contract",
        "points": points,
    }
    dump(out / "REPLICA_CONTRACT.json", replica)

    runner = dedent("""
        # Native runner contract

        This pack prepares but does not run the experiment. A future Lane 7 run must first bind the exact early-gate commit and obtain one GPU lock covering build qualification, correctness, timing, and eight NCU profiles.

        Build one independent extension from `REPLICA_SOURCE.patch`. Record patched source hashes and the resulting module SHA256. Every K/split/state cell must import that same module and launch the same patched target kernel; state is only runtime mask 0 or 15.

        For each K, allocate one input and direct final contiguous 16-replica qweight/qzeros/scales tensors. Hash every replica slice and record non-overlapping VA ranges. Reuse the identical live assets across SHARED/PER_MTILE; do not regenerate or reallocate between those states.

        Qualify all eight cells against `EXPECTED_LAUNCH.tsv`. Within a split, SHARED and PER_MTILE outputs must be bitwise equal. Across split8/split1, retain rtol=1e-2 and atol=5e-2; record naturally bitwise-equal cases without generalizing them.

        Timing uses 10 global warmups, then 25 mirror blocks and 50 samples/cell with two same-cell warmups per sample. Frozen mirror order is `A_SHARED,B_SHARED,A_PER_MTILE,B_PER_MTILE,B_PER_MTILE,A_PER_MTILE,B_SHARED,A_SHARED`.

        Run exactly one NCU profile per cell. Separate split8 GEMM and reduction rows. The primary causal comparison uses GEMM L2 read hit/miss sectors, GEMM DRAM bytes, and module timing; reduction is reported but excluded from the weight-side mechanism contrast.

        Stop on module/source drift, tensor hash or VA overlap failure, allocation asymmetry, launch/scratch/grid drift, same-split non-bitwise output, missing GEMM/reduction separation, NCU metric ambiguity, or any lock failure. Do not fall back to original binaries or broaden K/M/N/split.
        """).strip() + "\n"
    (out / "RUNNER_CONTRACT.md").write_text(runner, encoding="utf-8")

    boundary = dedent("""
        # Scientific boundary

        This is an artificial address-sharing intervention. It tests whether cross-M reuse of the combined qweight/qzeros/scales address set is an important source of the observed L2 advantage, and whether split-K's smaller local set helps that reuse survive.

        A supported screen may claim an important weight-side cross-M reuse contribution for this exact AutoAWQ kernel, GPT-3 proxy shape family, K2560/K3072, and RTX4080 experiment. It may not attribute the effect to qweight alone, infer NVIDIA replacement details, claim a pure-capacity isolation, or generalize to all GEMMs/LLMs.

        If PER_MTILE does not materially reduce GEMM read hits and increase misses/DRAM, the current cross-M reuse explanation must be downgraded. Correctness, allocation, and same-binary closure are prerequisites, not evidence for the causal effect by themselves.
        """).strip() + "\n"
    (out / "SCIENTIFIC_BOUNDARY.md").write_text(boundary, encoding="utf-8")

    checks = []
    for path in sorted(out.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            checks.append(f"{sha(path.read_bytes())}  {path.relative_to(out).as_posix()}")
    (out / "SHA256SUMS").write_text("\n".join(checks) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--early-only", action="store_true")
    args = parser.parse_args()
    gate, proof = early(args.repo.resolve(), args.source.resolve(), args.out.resolve())
    if not args.early_only:
        full(args.repo.resolve(), args.source.resolve(), args.out.resolve(), gate, proof)
    print(json.dumps({"status": gate["status"], "early_only": args.early_only, "patch_sha256": gate["bindings"]["patch_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
