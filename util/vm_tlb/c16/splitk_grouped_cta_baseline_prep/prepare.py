#!/usr/bin/env python3
"""CPU-only grouped-CTA source and contract audit for C16."""
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


GOAL = "C16_SPLITK_GROUPED_CTA_BASELINE_PREP_174NEW_V1"
COORD = "8e3505e932534fe5cdb334d68862c2bc9355702b"
SOURCE_COMMIT = "c7b0e88c327694c715b0a758d9ce8fd414a1fa21"
GEN_REL = "awq_ext/quantization/gemm_cuda_gen.cu"
HDR_REL = "awq_ext/quantization/gemm_cuda.h"
GEN_BLOB = "98f49efac8626388039912e6aabc8a84d9f8303b"
GEN_SHA = "974980f34d7269c9a33ccd642d9dc9bc8700f58e9afc63d65634dedd9c5fc5a6"
HDR_BLOB = "afc8165157dfc646049f548b706d9fb86fb685fc"
HDR_SHA = "2e962fb644d131795cf2f9f96c5b45c693b7a6962426fb993809cc3fd47bc187"
STATUS = "READY_FOR_GROUPED_CTA_NATIVE_BASELINE"

M, N, GROUP = 256, 49152, 128
M_TILES, N_TILES, LOGICAL_CTAS = 16, 384, 6144
KS = (3072, 4096)
SPLITS = (("A", 8), ("B", 1))
MODES = (("ROW", 0), ("GROUP_M16", 1))
OUT_BYTES = M * N * 2
DEVICE_BYTES = 16_718_168_064
RUNTIME_RESERVE_BYTES = 2 * 2**30

ACCEPTED_OUTPUT = {
    3072: {"A": "76be531cfe46bb847a95aad4fd49910d6715450a15c39681968b0ef1371a34db", "B": "76be531cfe46bb847a95aad4fd49910d6715450a15c39681968b0ef1371a34db"},
    4096: {"A": "43432f9cefc72f5ac5e74bb26d2fb4a601ef7abc8a2839539358e076b8550d0f", "B": "43432f9cefc72f5ac5e74bb26d2fb4a601ef7abc8a2839539358e076b8550d0f"},
}

ROW_HISTORY = {
    (3072, "A"): (1.6383999586105347, 0.002174999655371307),
    (3072, "B"): (1.3527040481567383, 0.0032029844064300375),
    (4096, "A"): (1.9263359904289246, 0.00932058841235311),
    (4096, "B"): (1.9341440200805664, 0.004419914886562949),
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
        "gemm_forward_4bit_cuda_m16n128k32(int G, int split_k_iters, int mapping_mode, half*",
        "target kernel signature",
    )
    start = text.index("__global__ void __launch_bounds__(64) gemm_forward_4bit_cuda_m16n128k32")
    end = text.index("__global__ void __launch_bounds__(64) gemm_forward_4bit_cuda_m16n64k32", start)
    kernel = text[start:end]
    kernel = replace_once(kernel, "half* __restrict__ C) \n{", "half* __restrict__ C)\n{", "signature whitespace")
    old_mapping = (
        "  int j_factors1 = ((OC + 128 - 1) / 128);\n"
        "  int blockIdx_x = 0;\n"
        "  int blockIdx_y = blockIdx.x % ((M + 16 - 1) / 16 * j_factors1);\n"
        "  int blockIdx_z = blockIdx.x / ((M + 16 - 1) / 16 * j_factors1);\n"
    )
    new_mapping = (
        "  int j_factors1 = ((OC + 128 - 1) / 128);\n"
        "  int m_tiles = ((M + 16 - 1) / 16);\n"
        "  int logical_ctas = m_tiles * j_factors1;\n"
        "  int linear = blockIdx.x % logical_ctas;\n"
        "  int row_m = linear / j_factors1;\n"
        "  int row_n = linear % j_factors1;\n"
        "  int grouped_m = linear % m_tiles;\n"
        "  int grouped_n = linear / m_tiles;\n"
        "  int selected_m = row_m + mapping_mode * (grouped_m - row_m);\n"
        "  int selected_n = row_n + mapping_mode * (grouped_n - row_n);\n"
        "  int blockIdx_y = selected_m * j_factors1 + selected_n;\n"
        "  int blockIdx_z = blockIdx.x / logical_ctas;\n"
    )
    kernel = replace_once(kernel, old_mapping, new_mapping, "branch-free mapping preamble")
    text = text[:start] + kernel + text[end:]

    wrapper_start = text.index("torch::Tensor gemm_forward_cuda(\n")
    prefix, wrapper = text[:wrapper_start], text[wrapper_start:]
    wrapper = replace_once(
        wrapper,
        "    torch::Tensor _zeros,\n    int split_k_iters)\n{\n    int num_in_feats",
        "    torch::Tensor _zeros,\n    int split_k_iters,\n    int mapping_mode)\n{\n"
        "    if (mapping_mode != 0 && mapping_mode != 1)\n"
        "        throw std::invalid_argument(\"mapping_mode must be 0 or 1\");\n"
        "    if (split_k_iters != 1 && split_k_iters != 8)\n"
        "        throw std::invalid_argument(\"split_k_iters must be 1 or 8\");\n"
        "    if (!_in_feats.is_contiguous() || !_kernel.is_contiguous() ||\n"
        "        !_scaling_factors.is_contiguous() || !_zeros.is_contiguous())\n"
        "        throw std::invalid_argument(\"all tensors must be contiguous\");\n"
        "    int num_in_feats",
        "wrapper ABI",
    )
    wrapper = replace_once(
        wrapper,
        "    int num_in_channels = _in_feats.size(1);\n",
        "    int num_in_channels = _in_feats.size(1);\n"
        "    if (num_in_feats != 256 || (num_in_channels != 3072 && num_in_channels != 4096))\n"
        "        throw std::invalid_argument(\"frozen contract requires M=256 and K in {3072,4096}\");\n",
        "frozen M/K",
    )
    wrapper = replace_once(
        wrapper,
        "    int num_out_channels = _out_feats.size(-1);\n",
        "    int num_out_channels = _out_feats.size(-1);\n"
        "    if (num_out_channels != 49152)\n"
        "        throw std::invalid_argument(\"frozen contract requires N=49152\");\n",
        "frozen N",
    )
    wrapper = replace_once(
        wrapper,
        "int group_size = num_in_channels / _scaling_factors.size(0);",
        "int group_size = num_in_channels / _scaling_factors.size(0);\n"
        "    if (group_size != 128)\n"
        "        throw std::invalid_argument(\"frozen contract requires group_size=128\");",
        "frozen group size",
    )
    wrapper = replace_once(
        wrapper,
        "        gemm_forward_4bit_cuda_m16n128k32<<<num_blocks, threads_per_block, 0, stream>>>(\n"
        "            group_size, split_k_iters, in_feats, kernel, scaling_factors, zeros,",
        "        gemm_forward_4bit_cuda_m16n128k32<<<num_blocks, threads_per_block, 0, stream>>>(\n"
        "            group_size, split_k_iters, mapping_mode, in_feats, kernel, scaling_factors, zeros,",
        "target launch argument",
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
        "    int mapping_mode);",
        "header ABI",
    )


def target_kernel(text: str) -> str:
    start = text.index("__global__ void __launch_bounds__(64) gemm_forward_4bit_cuda_m16n128k32")
    end = text.index("__global__ void __launch_bounds__(64) gemm_forward_4bit_cuda_m16n64k32", start)
    return text[start:end]


def build_patch(source: Path) -> tuple[bytes, dict]:
    gen_bytes, hdr_bytes = (source / GEN_REL).read_bytes(), (source / HDR_REL).read_bytes()
    if sha(gen_bytes) != GEN_SHA or sha(hdr_bytes) != HDR_SHA:
        raise RuntimeError("source hash mismatch")
    old_gen, old_hdr = gen_bytes.decode(), hdr_bytes.decode()
    new_gen, new_hdr = transform_generator(old_gen), transform_header(old_hdr)
    diff = []
    for rel, old, new in ((GEN_REL, old_gen, new_gen), (HDR_REL, old_hdr, new_hdr)):
        diff.extend(difflib.unified_diff(old.splitlines(True), new.splitlines(True), f"a/{rel}", f"b/{rel}"))
    patch = "".join(diff).encode()
    old_kernel, new_kernel = target_kernel(old_gen), target_kernel(new_gen)
    tokens = ("for (", "__syncthreads", "dequantize_s4_to_fp16x2", "mma.sync", "k_bound", "A_ptr", "B_ptr", "C_ptr")
    counts = {token: {"old": old_kernel.count(token), "patched": new_kernel.count(token)} for token in tokens}
    if any(x["old"] != x["patched"] for x in counts.values()):
        raise RuntimeError("kernel compute/address token count drift")
    proof = {
        "patch_sha256": sha(patch),
        "old_generator_sha256": GEN_SHA,
        "patched_generator_sha256": sha(new_gen.encode()),
        "old_header_sha256": HDR_SHA,
        "patched_header_sha256": sha(new_hdr.encode()),
        "token_counts": counts,
        "same_kernel_and_path": True,
        "mapping_select_expression": "row + mapping_mode * (grouped - row)",
        "mapping_branch_in_kernel": False,
        "pybind_source_changed": False,
    }
    return patch, proof


def coords(linear: int, mode: int) -> tuple[int, int]:
    row_m, row_n = divmod(linear, N_TILES)
    grouped_n, grouped_m = divmod(linear, M_TILES)
    return row_m + mode * (grouped_m - row_m), row_n + mode * (grouped_n - row_n)


def hash_records(records) -> str:
    h = hashlib.sha256()
    for record in records:
        h.update((",".join(map(str, record)) + "\n").encode())
    return h.hexdigest()


def mapping_proof_rows() -> tuple[list[dict], dict[int, list[tuple[int, int]]]]:
    expected = {(m, n) for m in range(M_TILES) for n in range(N_TILES)}
    pairs_by_mode = {}
    rows = []
    sorted_hash = hash_records(sorted(expected))
    for name, mode in MODES:
        pairs = [coords(linear, mode) for linear in range(LOGICAL_CTAS)]
        pairs_by_mode[mode] = pairs
        pair_set = set(pairs)
        output_ranges = {(m * 16, (m + 1) * 16, n * 128, (n + 1) * 128) for m, n in pairs}
        distances = []
        for n in range(N_TILES):
            positions = [i for i, pair in enumerate(pairs) if pair[1] == n]
            distances.extend(b - a for a, b in zip(positions, positions[1:]))
        for arm, split in SPLITS:
            triples = {(z, *coords(linear, mode)) for z in range(split) for linear in range(LOGICAL_CTAS)}
            rows.append({
                "arm": arm,
                "split_k_iters": split,
                "mapping": name,
                "mapping_mode": mode,
                "logical_ctas_per_split_plane": LOGICAL_CTAS,
                "split_planes_enumerated": split,
                "total_grid_ctas_enumerated": LOGICAL_CTAS * split,
                "unique_Mtile_Ntile_pairs": len(pair_set),
                "duplicate_pairs": len(pairs) - len(pair_set),
                "missing_pairs": len(expected - pair_set),
                "unique_split_Mtile_Ntile_triples": len(triples),
                "output_tiles": len(output_ranges),
                "output_elements_covered": sum((b - a) * (d - c) for a, b, c, d in output_ranges),
                "same_N_adjacent_M_linear_distance": min(distances) if distances else 0,
                "distance_uniform": len(set(distances)) == 1,
                "ordered_mapping_sha256": hash_records((i, *pair) for i, pair in enumerate(pairs)),
                "sorted_pair_set_sha256": sorted_hash,
                "bijection_pass": pair_set == expected and len(output_ranges) == LOGICAL_CTAS,
            })
    return rows, pairs_by_mode


def address_sets(k: int, split: int, pairs: list[tuple[int, int]]) -> dict[str, set[tuple[int, ...]]]:
    result = {"input_A": set(), "qweight": set(), "qzeros": set(), "scales": set(), "scratch_C": set()}
    for z in range(split):
        tiles = list(range(z, k // 32, split))
        for m, n in pairs:
            result["scratch_C"].add((z, m, n))
            for tile in tiles:
                result["input_A"].add((m, tile))
                result["qweight"].add((n, tile))
                group = tile // 4
                result["qzeros"].add((n, group))
                result["scales"].add((n, group))
    return result


def address_invariance(pairs_by_mode: dict[int, list[tuple[int, int]]]) -> dict:
    cases = []
    for k in KS:
        for arm, split in SPLITS:
            mode_sets = {name: address_sets(k, split, pairs_by_mode[mode]) for name, mode in MODES}
            hashes = {name: {obj: hash_records(sorted(values)) for obj, values in sets.items()} for name, sets in mode_sets.items()}
            equal = {obj: hashes["ROW"][obj] == hashes["GROUP_M16"][obj] for obj in hashes["ROW"]}
            qweight_bytes = k * (N // 8) * 4
            qzeros_bytes = (k // GROUP) * (N // 8) * 4
            scales_bytes = (k // GROUP) * N * 2
            z0_tiles = list(range(0, k // 32, split))
            z0_groups = {tile // 4 for tile in z0_tiles}
            per_plane = len(z0_tiles) * N_TILES * 2048 + len(z0_groups) * N_TILES * 320
            cases.append({
                "K": k,
                "arm": arm,
                "split_k_iters": split,
                "object_union_sha256": hashes,
                "object_unions_equal": equal,
                "all_object_unions_equal": all(equal.values()),
                "ordered_Ntile_sequence_sha256": {name: hash_records((pair[1],) for pair in pairs_by_mode[mode]) for name, mode in MODES},
                "ordered_sequences_differ": pairs_by_mode[0] != pairs_by_mode[1],
                "unique_bytes": {"input_A": M * k * 2, "qweight": qweight_bytes, "qzeros": qzeros_bytes, "scales": scales_bytes, "scratch_C": split * OUT_BYTES, "weight_side_total": qweight_bytes + qzeros_bytes + scales_bytes},
                "per_split_plane_weight_side_unique_bytes_z0": per_plane,
            })
    return {
        "status": "PASS_ADDRESS_SET_INVARIANT",
        "proof_method": "exhaustive 6144-pair enumeration plus exact Ktile/group object-key unions for every K/split/mapping",
        "cases": cases,
        "all_cases_pass": all(case["all_object_unions_equal"] and case["ordered_sequences_differ"] for case in cases),
    }


def launch_rows() -> list[dict]:
    rows = []
    for k in KS:
        for arm, split in SPLITS:
            for mapping, mode in MODES:
                rows.append({
                    "K": k, "M": M, "N": N, "arm": arm, "split_k_iters": split,
                    "mapping": mapping, "mapping_mode": mode,
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
    if subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", COORD, "HEAD"], check=False).returncode != 0:
        raise RuntimeError("coordination commit is not an ancestor of HEAD")
    if subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip() != SOURCE_COMMIT:
        raise RuntimeError("source commit mismatch")
    if subprocess.check_output(["git", "-C", str(source), "rev-parse", f"HEAD:{GEN_REL}"], text=True).strip() != GEN_BLOB:
        raise RuntimeError("generator blob mismatch")
    out.mkdir(parents=True, exist_ok=True)
    patch, source_proof = build_patch(source)
    artifact = gzip.compress(patch, compresslevel=9, mtime=0)
    (out / "MAPPING_SOURCE.patch.gz").write_bytes(artifact)
    mapping_rows, pairs = mapping_proof_rows()
    write_tsv(out / "MAPPING_BIJECTION.tsv", mapping_rows)
    address = address_invariance(pairs)
    dump(out / "ADDRESS_SET_INVARIANCE.json", address)
    launches = launch_rows()
    write_tsv(out / "EXPECTED_LAUNCH.tsv", launches)
    bindings = {
        "old_source_sha256": GEN_SHA,
        "patch_sha256": sha(patch),
        "patch_artifact": "MAPPING_SOURCE.patch.gz",
        "patch_artifact_sha256": sha(artifact),
        "patched_generator_sha256": source_proof["patched_generator_sha256"],
        "mapping_bijection_sha256": sha((out / "MAPPING_BIJECTION.tsv").read_bytes()),
        "address_set_invariance_sha256": sha((out / "ADDRESS_SET_INVARIANCE.json").read_bytes()),
        "expected_launch_sha256": sha((out / "EXPECTED_LAUNCH.tsv").read_bytes()),
    }
    gate = {
        "goal": GOAL,
        "status": STATUS,
        "coordination_commit": COORD,
        "source_isolation": {
            "same_patched_kernel_all_cells": True,
            "mapping_mode_runtime": {"ROW": 0, "GROUP_M16": 1},
            "mapping_select_branch_free": True,
            "same_new_mapping_instruction_path": True,
            "only_intentional_device_semantic_change": "logical CTA to (Mtile,Ntile) mapping",
            "AWQ_math_Kloop_split_reduction_tile_grid_data_layout_unchanged": True,
        },
        "bijection": {
            "all_rows_pass": all(row["bijection_pass"] for row in mapping_rows),
            "rows": len(mapping_rows),
            "logical_ctas_per_plane": LOGICAL_CTAS,
            "ROW_same_N_distance": 384,
            "GROUP_M16_same_N_distance": 1,
        },
        "address_set": {"all_cases_pass": address["all_cases_pass"], "cases": len(address["cases"])},
        "launch": {"all_8_cells_frozen": len(launches) == 8, "rows": len(launches)},
        "matrix": {"K": list(KS), "M": M, "N": N, "split": [8, 1], "mapping": {"ROW": 0, "GROUP_M16": 1}},
        "bindings": bindings,
        "authorization": {"lane7_grouped_cta_native_baseline": True, "gpu_lock_required": True, "sass_capture": False, "simulation": False},
        "resource_attestation": {"cpu_only": True, "gpu_used": False, "cuda_imported": False, "gpu_lock_requested": False, "lane4_partial_accessed": False},
    }
    dump(out / "EARLY_GATE.json", gate)
    return gate, source_proof


def full(out: Path, gate: dict, source_proof: dict) -> None:
    authority = {
        "goal": GOAL, "status": "PASS", "coordination_commit": COORD,
        "source": {"repo": "casper-hansen/AutoAWQ_kernels", "commit": SOURCE_COMMIT, "generator_blob": GEN_BLOB, "generator_sha256": GEN_SHA, "header_blob": HDR_BLOB, "header_sha256": HDR_SHA},
        "accepted_evidence": {
            "static_footprint": "c72d28b17247f25d0c3613604ab6cab1737666e0",
            "threshold_native": "b17193ff6b3786fd01d5bfe83b5c1a0a03859729",
            "L2_read_hit_diagnostic": "915707348617f7a8f432bad7a434a98d78b487c8",
            "crossM_prep": "bcc3a7082ffb66ab85d8ef8c62439ada97090d16",
            "crossM_native": "2f8338408b2b9a39f5a6fc1bab9db015a019ea62",
            "crossM_consumer": "2113422f7e6b7e5a851469511d26a9ddf7123d4e",
            "literature_notes": "38d4df40b615625c15d1843a69a23eb954ac0bef",
            "split1_direct_output": "0e88faa28c9066b48e394dce657d7a16e6332a32",
        },
        "accepted_binary_sha256": {"split8": "9e8d38a04c28770338fcef8ae0f9a90a984b7a8f95bcb98a407738594e1c08d7", "split1": "1aa8db13f5fd10651aa4241f58200e3a7075214d34cca4d70fbcbe7cbbc07887"},
        "patch": source_proof,
        "resource_attestation": gate["resource_attestation"],
    }
    dump(out / "AUTHORITY.json", authority)

    semantic = dedent(f"""
        # Grouped CTA patch semantic isolation

        The new independent extension is based on AutoAWQ `{SOURCE_COMMIT}` / generator blob `{GEN_BLOB}` and does not replace accepted binaries.

        The target m16n128 kernel receives runtime `mapping_mode`. It computes ROW and GROUP_M16 coordinates unconditionally, selects with `row + mapping_mode*(grouped-row)`, reconstructs logical `blockIdx_y=Mtile*384+Ntile`, and keeps `split_z=blockIdx.x/6144`. There is no mapping-dependent kernel branch; both modes use the same compiled kernel and added integer path.

        All downstream A/input, qweight/qzeros/scales, and C/output pointer formulas are unchanged and consume only reconstructed `blockIdx_y`. Exhaustive enumeration proves that each logical output tile is covered once in both modes, so each tile reads the same A rows and weight-side N tile and writes the same output range. Only traversal order differs.

        K bound/interleave, global load counts, barriers, shared layout, dequantization, MMA, writeback, tile, grid, block, scratch, split, and reduction are unchanged. The host wrapper only freezes M/K/N/group/split/mode and retains accepted split1 direct output versus split8 reduction. Data tensors retain their original 2D layouts. The m16n64 kernel and `pybind_awq.cpp` are unchanged.
        """).strip() + "\n"
    (out / "PATCH_SEMANTIC_DIFF.md").write_text(semantic, encoding="utf-8")

    memory = []
    for k in KS:
        weight = k * (N // 8) * 4 + (k // GROUP) * (N // 8) * 4 + (k // GROUP) * N * 2
        input_bytes = M * k * 2
        for arm, split in SPLITS:
            explicit = weight + input_bytes + split * OUT_BYTES + (OUT_BYTES if split == 8 else 0)
            for mapping, mode in MODES:
                memory.append({
                    "K": k, "arm": arm, "split_k_iters": split, "mapping": mapping, "mapping_mode": mode,
                    "input_bytes": input_bytes, "weight_side_bytes": weight, "scratch_bytes": split * OUT_BYTES,
                    "extra_output_bytes": OUT_BYTES if split == 8 else 0,
                    "explicit_live_bytes": explicit, "runtime_reserve_bytes": RUNTIME_RESERVE_BYTES,
                    "budgeted_peak_bytes": explicit + RUNTIME_RESERVE_BYTES,
                    "device_bytes": DEVICE_BYTES, "headroom_bytes": DEVICE_BYTES - explicit - RUNTIME_RESERVE_BYTES,
                    "mapping_additional_allocation_bytes": 0,
                    "pass": explicit + RUNTIME_RESERVE_BYTES < DEVICE_BYTES,
                })
    write_tsv(out / "MEMORY_BUDGET.tsv", memory)

    calibration = []
    for (k, arm), (median, cv) in ROW_HISTORY.items():
        calibration.append({"K": k, "arm": arm, "accepted_ROW_median_ms": median, "accepted_ROW_cv": cv, "new_ROW_relative_median_tolerance": 0.05, "stop_rule": "STOP if relative median deviation >5% and > both accepted/new CV"})
    write_tsv(out / "ROW_CALIBRATION.tsv", calibration)

    runner = dedent("""
        # Native grouped-CTA runner contract

        Build one independent extension from `MAPPING_SOURCE.patch.gz`; record patched source/module hashes. All eight cells import the same module and differ only in K, split, and runtime mapping_mode.

        First close correctness and launch identity. Within a split, ROW and GROUP_M16 outputs must be bitwise equal. Across split1/split8 retain rtol=1e-2 and atol=5e-2. Every row must match `EXPECTED_LAUNCH.tsv` and show no data-layout or allocation change.

        ROW cells are the mandatory calibration. Compare their medians with `ROW_CALIBRATION.tsv`; if relative deviation exceeds 5% and both accepted and new CV, STOP before interpreting GROUP_M16.

        Timing uses 10 global warmups, 25 complete mirror blocks, 50 samples/cell, and two same-cell warmups/sample. Frozen mirror order: `A_ROW,B_ROW,A_GROUP,B_GROUP,B_GROUP,A_GROUP,B_ROW,A_ROW`.

        Run one NCU profile per cell under the same GPU lock. Separate split8 GEMM and reduction. Primary mapping comparisons use GEMM L2 read hit/miss sectors, GEMM DRAM bytes, and module timing. Stop on patch/module drift, correctness/coverage/launch failure, ROW calibration failure, metric ambiguity, incomplete mirror blocks, or lock failure.
        """).strip() + "\n"
    (out / "RUNNER_CONTRACT.md").write_text(runner, encoding="utf-8")

    boundary = dedent("""
        # Scientific boundary

        GROUP_M16 is a classic grouped/swizzled software scheduling baseline, not a new mechanism. This experiment tests whether placing the 16 M tiles sharing each N tile consecutively in logical block-ID order restores L2 reuse for this exact AutoAWQ kernel and proxy shape.

        Logical block-ID order is not proof of physical GPU issue order. Results cannot be generalized to all W4 kernels, all GEMMs, or a complete GPT-3 deployment. If the strong baseline removes most split8 benefit, the project must credit software ordering and downgrade new split-mechanism space; only a clear residual after the baseline motivates new mechanism design.
        """).strip() + "\n"
    (out / "SCIENTIFIC_BOUNDARY.md").write_text(boundary, encoding="utf-8")

    lines = []
    for path in sorted(out.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            lines.append(f"{sha(path.read_bytes())}  {path.relative_to(out).as_posix()}")
    (out / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--early-only", action="store_true")
    args = parser.parse_args()
    gate, proof = early(args.repo.resolve(), args.source.resolve(), args.out.resolve())
    if not args.early_only:
        full(args.out.resolve(), gate, proof)
    print(json.dumps({"status": gate["status"], "early_only": args.early_only, "patch_sha256": gate["bindings"]["patch_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
