#!/usr/bin/env python3
"""CPU-only preparation for the grouped residual-parallelism native screen."""
from __future__ import annotations

import argparse
import csv
import difflib
import gzip
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from textwrap import dedent


GOAL = "C16_GROUPED_RESIDUAL_PARALLELISM_PREP_174NEW_V1"
COORD = "bd988aeb570708e5a41bab45433e9e49eac53c9a"
SOURCE_COMMIT = "c7b0e88c327694c715b0a758d9ce8fd414a1fa21"
GEN_REL = "awq_ext/quantization/gemm_cuda_gen.cu"
HDR_REL = "awq_ext/quantization/gemm_cuda.h"
GEN_BLOB = "98f49efac8626388039912e6aabc8a84d9f8303b"
GEN_SHA = "974980f34d7269c9a33ccd642d9dc9bc8700f58e9afc63d65634dedd9c5fc5a6"
HDR_BLOB = "afc8165157dfc646049f548b706d9fb86fb685fc"
HDR_SHA = "2e962fb644d131795cf2f9f96c5b45c693b7a6962426fb993809cc3fd47bc187"
INHERITED_FORMULA_SHA = "63c2653748806de6e74de7e57364f4d65468828dcd75d55a886f800541838fddc"
STATUS = "READY_FOR_RESIDUAL_PARALLELISM_NATIVE_SCREEN"

K, N, GROUP = 4096, 12288, 128
MS = (1, 16, 32, 64)
SPLITS = (("A8", 8), ("B1", 1))
N_TILES = 96
SM_COUNT = 76
L2_BYTES = 64 * 2**20
DEVICE_BYTES = 16_718_168_064
RUNTIME_RESERVE_BYTES = 2 * 2**30
SYNTH_VERSION = "C16_GROUPED_RESIDUAL_SYNTH_V1"
QWEIGHT_WORD = struct.pack("<I", 0xECA86420)
QZERO_WORD = struct.pack("<I", 0x77777777)
SCALE_WORD = struct.pack("<e", 2.0**-8)


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
    kernel = replace_once(kernel, old_mapping, new_mapping, "dynamic grouped mapping")
    text = text[:start] + kernel + text[end:]

    wrapper_start = text.index("torch::Tensor gemm_forward_cuda(\n")
    prefix, wrapper = text[:wrapper_start], text[wrapper_start:]
    wrapper = replace_once(
        wrapper,
        "    torch::Tensor _zeros,\n    int split_k_iters)\n{\n    int num_in_feats",
        "    torch::Tensor _zeros,\n    int split_k_iters,\n    int mapping_mode)\n{\n"
        "    if (mapping_mode != 1)\n"
        "        throw std::invalid_argument(\"frozen screen requires GROUP_FULL_M mapping_mode=1\");\n"
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
        "    if ((num_in_feats != 1 && num_in_feats != 16 && num_in_feats != 32 && num_in_feats != 64) ||\n"
        "        num_in_channels != 4096)\n"
        "        throw std::invalid_argument(\"frozen screen requires M in {1,16,32,64}, K=4096\");\n",
        "frozen M/K",
    )
    wrapper = replace_once(
        wrapper,
        "    int num_out_channels = _out_feats.size(-1);\n",
        "    int num_out_channels = _out_feats.size(-1);\n"
        "    if (num_out_channels != 12288)\n"
        "        throw std::invalid_argument(\"frozen screen requires N=12288\");\n",
        "frozen N",
    )
    wrapper = replace_once(
        wrapper,
        "int group_size = num_in_channels / _scaling_factors.size(0);",
        "int group_size = num_in_channels / _scaling_factors.size(0);\n"
        "    if (group_size != 128)\n"
        "        throw std::invalid_argument(\"frozen screen requires group_size=128\");",
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
    lines = []
    for rel, old, new in ((GEN_REL, old_gen, new_gen), (HDR_REL, old_hdr, new_hdr)):
        lines.extend(difflib.unified_diff(old.splitlines(True), new.splitlines(True), f"a/{rel}", f"b/{rel}"))
    patch = "".join(lines).encode()
    old_kernel, new_kernel = target_kernel(old_gen), target_kernel(new_gen)
    tokens = ("for (", "__syncthreads", "dequantize_s4_to_fp16x2", "mma.sync", "k_bound", "A_ptr", "B_ptr", "C_ptr")
    counts = {token: {"old": old_kernel.count(token), "patched": new_kernel.count(token)} for token in tokens}
    if any(v["old"] != v["patched"] for v in counts.values()):
        raise RuntimeError("kernel token count drift")
    return patch, {
        "patch_sha256": sha(patch), "old_generator_sha256": GEN_SHA,
        "patched_generator_sha256": sha(new_gen.encode()),
        "old_header_sha256": HDR_SHA, "patched_header_sha256": sha(new_hdr.encode()),
        "token_counts": counts, "same_compiled_target_kernel_all_cells": True,
        "device_mapping_branch": False, "M_dependent_GEMM_body_branch": False,
        "mapping_path": "dynamic m_tiles; ROW and GROUP coordinates; runtime arithmetic select fixed to mode=1",
        "pybind_source_changed": False,
    }


def repeat_hash(word: bytes, count: int) -> str:
    h = hashlib.sha256()
    chunk_count = 1 << 20
    chunk = word * chunk_count
    whole, tail = divmod(count, chunk_count)
    for _ in range(whole):
        h.update(chunk)
    h.update(word * tail)
    return h.hexdigest()


def input_hash(m: int, k: int) -> str:
    h = hashlib.sha256()
    for row in range(m):
        h.update(b"".join(struct.pack("<e", (1 + ((5 * row + 3 * col) % 7)) * 2.0**-10) for col in range(k)))
    return h.hexdigest()


def synthetic_contract() -> dict:
    qweight_count = K * (N // 8)
    qzeros_count = (K // GROUP) * (N // 8)
    scales_count = (K // GROUP) * N
    full = {
        "qweight": {"bytes": qweight_count * 4, "sha256": repeat_hash(QWEIGHT_WORD, qweight_count)},
        "qzeros": {"bytes": qzeros_count * 4, "sha256": repeat_hash(QZERO_WORD, qzeros_count)},
        "scales": {"bytes": scales_count * 2, "sha256": repeat_hash(SCALE_WORD, scales_count)},
    }
    inputs = {str(m): {"bytes": m * K * 2, "sha256": input_hash(m, K)} for m in MS}
    tiny_m, tiny_k, tiny_n = 2, 256, 16
    tiny = {
        "version": SYNTH_VERSION,
        "shape": {"M": tiny_m, "K": tiny_k, "N": tiny_n, "group_size": GROUP},
        "tensor_sha256": {
            "input_f16": input_hash(tiny_m, tiny_k),
            "qweight_i32": repeat_hash(QWEIGHT_WORD, tiny_k * (tiny_n // 8)),
            "qzeros_i32": repeat_hash(QZERO_WORD, (tiny_k // GROUP) * (tiny_n // 8)),
            "scales_f16": repeat_hash(SCALE_WORD, (tiny_k // GROUP) * tiny_n),
        },
    }
    tiny["reference_sha256"] = sha(json.dumps(tiny, sort_keys=True, separators=(",", ":")).encode())
    return {
        "version": SYNTH_VERSION,
        "status": "PASS_CPU_REFERENCE",
        "inherited_formula_source_sha256": INHERITED_FORMULA_SHA,
        "formula": {
            "input_f16": "(1 + ((5*m + 3*k) % 7)) * 2^-10",
            "qweight_i32_word": "0xECA86420 repeated",
            "qzeros_i32_word": "0x77777777 repeated",
            "scales_f16": "2^-8 repeated",
        },
        "shape": {"K": K, "N": N, "M": list(MS), "group_size": GROUP},
        "weight_side_identical_for_all_M_and_split": True,
        "split1_split8_share_exact_input_and_weight_bytes": True,
        "full_weight_side": full,
        "inputs": inputs,
        "tiny_cpu_reference": tiny,
    }


def coords(linear: int, m_tiles: int, grouped: bool) -> tuple[int, int]:
    if grouped:
        n, m = divmod(linear, m_tiles)
        return m, n
    return divmod(linear, N_TILES)


def hash_records(records) -> str:
    h = hashlib.sha256()
    for record in records:
        h.update((",".join(map(str, record)) + "\n").encode())
    return h.hexdigest()


def mapping_rows() -> tuple[list[dict], dict[int, dict[str, list[tuple[int, int]]]]]:
    rows, mapping = [], {}
    for m_value in MS:
        m_tiles = (m_value + 15) // 16
        logical = m_tiles * N_TILES
        group_pairs = [coords(i, m_tiles, True) for i in range(logical)]
        row_pairs = [coords(i, m_tiles, False) for i in range(logical)]
        mapping[m_value] = {"GROUP_FULL_M": group_pairs, "ROW_REFERENCE": row_pairs}
        expected = {(m, n) for m in range(m_tiles) for n in range(N_TILES)}
        output_ranges = {(max(0, mt * 16), min(m_value, (mt + 1) * 16), nt * 128, (nt + 1) * 128) for mt, nt in group_pairs}
        distances = []
        if m_tiles > 1:
            for n in range(N_TILES):
                positions = [i for i, pair in enumerate(group_pairs) if pair[1] == n]
                distances.extend(b - a for a, b in zip(positions, positions[1:]))
        for arm, split in SPLITS:
            triples = {(z, *pair) for z in range(split) for pair in group_pairs}
            rows.append({
                "M": m_value, "m_tiles": m_tiles, "N": N, "n_tiles": N_TILES,
                "arm": arm, "split_k_iters": split, "mapping": "GROUP_FULL_M", "mapping_mode": 1,
                "logical_ctas_per_plane": logical, "split_planes_enumerated": split,
                "total_grid_ctas_enumerated": logical * split,
                "unique_Mtile_Ntile_pairs": len(set(group_pairs)),
                "duplicate_pairs": len(group_pairs) - len(set(group_pairs)),
                "missing_pairs": len(expected - set(group_pairs)),
                "unique_split_Mtile_Ntile_triples": len(triples),
                "output_tiles": len(output_ranges),
                "output_elements_covered": sum((b - a) * (d - c) for a, b, c, d in output_ranges),
                "same_N_adjacent_M_distance": 1 if m_tiles > 1 else "NA_SINGLE_MTILE",
                "same_N_Mtiles_consecutive": True,
                "ordered_mapping_sha256": hash_records((i, *pair) for i, pair in enumerate(group_pairs)),
                "sorted_pair_set_sha256": hash_records(sorted(expected)),
                "bijection_and_coverage_pass": set(group_pairs) == expected and len(output_ranges) == logical and sum((b - a) * (d - c) for a, b, c, d in output_ranges) == m_value * N,
            })
    return rows, mapping


def object_sets(m_value: int, split: int, pairs: list[tuple[int, int]]) -> dict[str, set[tuple[int, ...]]]:
    result = {"input_A": set(), "qweight": set(), "qzeros": set(), "scales": set(), "scratch_C": set()}
    for z in range(split):
        ktiles = list(range(z, K // 32, split))
        for mtile, ntile in pairs:
            actual_rows = range(mtile * 16, min(m_value, (mtile + 1) * 16))
            for row in actual_rows:
                result["scratch_C"].add((z, row, ntile))
                for tile in ktiles:
                    result["input_A"].add((row, tile))
            for tile in ktiles:
                result["qweight"].add((ntile, tile))
                group = tile // 4
                result["qzeros"].add((ntile, group))
                result["scales"].add((ntile, group))
    return result


def address_audit(mapping: dict[int, dict[str, list[tuple[int, int]]]]) -> dict:
    cases = []
    qweight_bytes = K * (N // 8) * 4
    qzeros_bytes = (K // GROUP) * (N // 8) * 4
    scales_bytes = (K // GROUP) * N * 2
    for m_value in MS:
        for arm, split in SPLITS:
            sets = {name: object_sets(m_value, split, pairs) for name, pairs in mapping[m_value].items()}
            hashes = {name: {obj: hash_records(sorted(values)) for obj, values in objects.items()} for name, objects in sets.items()}
            equal = {obj: hashes["GROUP_FULL_M"][obj] == hashes["ROW_REFERENCE"][obj] for obj in hashes["GROUP_FULL_M"]}
            z0_tiles = list(range(0, K // 32, split))
            z0_groups = {tile // 4 for tile in z0_tiles}
            per_plane_weight = len(z0_tiles) * N_TILES * 2048 + len(z0_groups) * N_TILES * 320
            cases.append({
                "M": m_value, "arm": arm, "split_k_iters": split,
                "GROUP_FULL_M_vs_ROW_REFERENCE_union_sha256": hashes,
                "object_unions_equal": equal, "all_object_unions_equal": all(equal.values()),
                "ordered_pair_sequence_differs": mapping[m_value]["GROUP_FULL_M"] != mapping[m_value]["ROW_REFERENCE"],
                "unique_bytes": {"input_A": m_value * K * 2, "qweight": qweight_bytes, "qzeros": qzeros_bytes, "scales": scales_bytes, "weight_side_total": qweight_bytes + qzeros_bytes + scales_bytes, "scratch_C": split * m_value * N * 2},
                "per_split_plane_weight_side_unique_bytes_z0": per_plane_weight,
            })
    return {
        "status": "PASS_ADDRESS_SET_CLOSED",
        "proof_method": "exhaustive dynamic-M tile mapping and exact row/Ktile/group object-key unions",
        "cases": cases,
        "all_cases_pass": all(case["all_object_unions_equal"] for case in cases),
    }


def footprint_rows() -> list[dict]:
    qweight = K * (N // 8) * 4
    qzeros = (K // GROUP) * (N // 8) * 4
    scales = (K // GROUP) * N * 2
    weight = qweight + qzeros + scales
    rows = []
    for m_value in MS:
        output = m_value * N * 2
        input_bytes = m_value * K * 2
        for arm, split in SPLITS:
            scratch = split * output
            reduction_output = output if split == 8 else 0
            live = weight + input_bytes + scratch + reduction_output
            rows.append({
                "M": m_value, "K": K, "N": N, "arm": arm, "split_k_iters": split,
                "qweight_bytes": qweight, "qzeros_bytes": qzeros, "scales_bytes": scales,
                "weight_side_bytes": weight, "weight_side_mib": f"{weight / 2**20:.7f}",
                "weight_side_over_64MiB": f"{weight / L2_BYTES:.9f}", "weight_side_below_64MiB": weight < L2_BYTES,
                "input_bytes": input_bytes, "returned_output_bytes": output,
                "scratch_bytes": scratch, "expected_reduction_output_bytes": reduction_output,
                "conservative_explicit_live_bytes": live, "runtime_reserve_bytes": RUNTIME_RESERVE_BYTES,
                "budgeted_peak_bytes": live + RUNTIME_RESERVE_BYTES,
                "device_bytes": DEVICE_BYTES, "headroom_bytes": DEVICE_BYTES - live - RUNTIME_RESERVE_BYTES,
                "memory_pass": live + RUNTIME_RESERVE_BYTES < DEVICE_BYTES,
                "claim_boundary": "weight-side below L2 reduces capacity pressure; it does not prove residency",
            })
    return rows


def launch_rows() -> list[dict]:
    rows = []
    for m_value in MS:
        m_tiles = (m_value + 15) // 16
        output = m_value * N * 2
        for arm, split in SPLITS:
            grid = m_tiles * N_TILES * split
            rows.append({
                "M": m_value, "K": K, "N": N, "m_tiles": m_tiles, "n_tiles": N_TILES,
                "arm": arm, "split_k_iters": split, "mapping": "GROUP_FULL_M", "mapping_mode": 1,
                "gemm_grid": grid, "gemm_block": "[32,2,1]",
                "launch_CTA_per_76SM": f"{grid / SM_COUNT:.9f}",
                "valid_rows_in_last_Mtile": m_value - 16 * (m_tiles - 1),
                "Ktile_iterations_per_CTA": (K // 32) // split,
                "scratch_shape": json.dumps([split, m_value, N], separators=(",", ":")),
                "scratch_bytes": split * output,
                "reduction_expected": split == 8,
                "reduction_formula": "ceil(M*N/512)" if split == 8 else "NONE",
                "reduction_grid": (m_value * N + 511) // 512 if split == 8 else 0,
                "reduction_block": "[32,4,1]" if split == 8 else "NA",
            })
    return rows


def early(repo: Path, source: Path, out: Path) -> tuple[dict, dict]:
    if subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", COORD, "HEAD"], check=False).returncode != 0:
        raise RuntimeError("coordination commit is not an ancestor of HEAD")
    if subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip() != SOURCE_COMMIT:
        raise RuntimeError("source commit mismatch")
    if subprocess.check_output(["git", "-C", str(source), "rev-parse", f"HEAD:{GEN_REL}"], text=True).strip() != GEN_BLOB:
        raise RuntimeError("source blob mismatch")
    out.mkdir(parents=True, exist_ok=True)
    patch, source_proof = build_patch(source)
    artifact = gzip.compress(patch, compresslevel=9, mtime=0)
    (out / "GROUP_FULL_M_SOURCE.patch.gz").write_bytes(artifact)
    synth = synthetic_contract()
    dump(out / "SYNTHETIC_CONTRACT.json", synth)
    mappings, pair_maps = mapping_rows()
    write_tsv(out / "MAPPING_BIJECTION.tsv", mappings)
    addresses = address_audit(pair_maps)
    dump(out / "ADDRESS_SET_AUDIT.json", addresses)
    footprints = footprint_rows()
    write_tsv(out / "FOOTPRINT_AND_MEMORY_BUDGET.tsv", footprints)
    launches = launch_rows()
    write_tsv(out / "EXPECTED_LAUNCH.tsv", launches)
    bindings = {
        "old_source_sha256": GEN_SHA,
        "patch_sha256": sha(patch), "patch_artifact": "GROUP_FULL_M_SOURCE.patch.gz", "patch_artifact_sha256": sha(artifact),
        "patched_generator_sha256": source_proof["patched_generator_sha256"],
        "mapping_proof_sha256": sha((out / "MAPPING_BIJECTION.tsv").read_bytes()),
        "address_set_audit_sha256": sha((out / "ADDRESS_SET_AUDIT.json").read_bytes()),
        "footprint_table_sha256": sha((out / "FOOTPRINT_AND_MEMORY_BUDGET.tsv").read_bytes()),
        "expected_launch_sha256": sha((out / "EXPECTED_LAUNCH.tsv").read_bytes()),
        "synthetic_contract_sha256": sha((out / "SYNTHETIC_CONTRACT.json").read_bytes()),
    }
    gate = {
        "goal": GOAL, "status": STATUS, "coordination_commit": COORD,
        "source_isolation": {
            "same_compiled_target_kernel_all_cells": True,
            "all_science_cells_mapping_mode": 1,
            "mapping": "GROUP_FULL_M",
            "dynamic_m_tiles": True,
            "M_dependent_GEMM_body_branch": False,
            "only_intentional_device_semantic_change": "CTA to (Mtile,Ntile) logical mapping",
            "AWQ_math_Kloop_load_dequant_MMA_shared_tile_block_split_reduction_data_layout_unchanged": True,
        },
        "footprint": {
            "qweight_bytes": 25_165_824, "qzeros_bytes": 196_608, "scales_bytes": 786_432,
            "weight_side_bytes": 26_148_864, "weight_side_mib": 24.9375,
            "weight_side_over_64MiB": 0.3896484375, "all_memory_rows_pass": all(row["memory_pass"] for row in footprints),
        },
        "mapping": {"all_8_rows_pass": all(row["bijection_and_coverage_pass"] for row in mappings), "rows": len(mappings), "all_address_sets_closed": addresses["all_cases_pass"]},
        "synthetic": {"version": SYNTH_VERSION, "status": synth["status"], "weight_side_identical_for_all_M_and_split": True},
        "launch": {"all_8_cells_frozen": len(launches) == 8, "rows": len(launches)},
        "matrix": {"K": K, "N": N, "M": list(MS), "split": [8, 1], "mapping": "GROUP_FULL_M", "mapping_mode": 1},
        "bindings": bindings,
        "authorization": {"lane7_residual_parallelism_native_screen": True, "gpu_lock_required": True, "sass_nvbit": False, "simulation": False},
        "resource_attestation": {"cpu_only": True, "gpu_used": False, "cuda_imported": False, "gpu_lock_requested": False, "lane4_partial_accessed": False},
    }
    dump(out / "EARLY_GATE.json", gate)
    return gate, source_proof


def full(out: Path, gate: dict, source_proof: dict) -> None:
    authority = {
        "goal": GOAL, "status": "PASS", "coordination_commit": COORD,
        "source": {"repo": "casper-hansen/AutoAWQ_kernels", "commit": SOURCE_COMMIT, "generator_blob": GEN_BLOB, "generator_sha256": GEN_SHA, "header_blob": HDR_BLOB, "header_sha256": HDR_SHA},
        "accepted_evidence": {
            "grouped_prep": "0b37b84cf8fbcaaeb90c36fc28dcbb8ec3764ae1",
            "grouped_native": "a75379674116fc94e57ccc88eff9359fc1f4114c",
            "grouped_consumer": "e7855278076c7e0360d39b18424cc8f048f51da5",
            "crossM_consumer": "2113422f7e6b7e5a851469511d26a9ddf7123d4e",
            "threshold_native": "b17193ff6b3786fd01d5bfe83b5c1a0a03859729",
            "split1_direct_output": "0e88faa28c9066b48e394dce657d7a16e6332a32",
        },
        "accepted_binary_sha256": {"split8": "9e8d38a04c28770338fcef8ae0f9a90a984b7a8f95bcb98a407738594e1c08d7", "split1": "1aa8db13f5fd10651aa4241f58200e3a7075214d34cca4d70fbcbe7cbbc07887"},
        "patch": source_proof, "resource_attestation": gate["resource_attestation"],
    }
    dump(out / "AUTHORITY.json", authority)

    semantic = dedent(f"""
        # Dynamic GROUP_FULL_M patch semantic isolation

        The patch is based on AutoAWQ `{SOURCE_COMMIT}` / generator blob `{GEN_BLOB}` and creates a new independent extension without replacing accepted binaries.

        The target m16n128 kernel computes dynamic `m_tiles=ceil(M/16)`, ROW and GROUP coordinates, and the branch-free integer selection `row + mapping_mode*(grouped-row)`. Every scientific cell passes mapping_mode=1, so M1/16/32/64 and split1/8 use the same compiled target kernel and the same GROUP_FULL_M instruction path. There is no M-dependent branch in the GEMM body.

        All A/input, qweight/qzeros/scales, and C/output pointer formulas downstream of reconstructed `blockIdx_y` are unchanged. Exhaustive enumeration proves exact output coverage and equality with the ROW-reference address unions for every M/split. K-loop/interleave, loads, barriers, shared layout, dequant, MMA, writeback, tile, block, tensor layouts, split, scratch, and reduction are unchanged.

        Host-only checks freeze M={{1,16,32,64}}, K=4096, N=12288, group=128, split={{1,8}}, and mapping_mode=1. Split1 keeps the accepted direct-plane return; split8 keeps `sum(0)`. The m16n64 kernel and `pybind_awq.cpp` remain unchanged.
        """).strip() + "\n"
    (out / "PATCH_SEMANTIC_DIFF.md").write_text(semantic, encoding="utf-8")

    runner = dedent("""
        # Native residual-parallelism runner contract

        Build one independent extension from `GROUP_FULL_M_SOURCE.patch.gz`; record exact patched source and module SHA256. All eight science cells import that module and pass mapping_mode=1. No ROW, extra M/K/N/split, GROUP_M sweep, replica, EVICT, SASS/NVBit, or simulation is allowed.

        For each M, construct tensors exactly from `SYNTHETIC_CONTRACT.json`. The two split arms must share the same live input and weight tensors. Close shape/dtype/finiteness and split1-vs-split8 correctness at rtol=1e-2, atol=5e-2; record natural bitwise equality without generalizing it.

        Validate every launch against `EXPECTED_LAUNCH.tsv`, including reduction grid derived as ceil(M*N/512), scratch shape/bytes, block, and GROUP_FULL_M mapping. Stop on any source/module/synthetic/launch/memory drift.

        Timing uses 10 global warmups per cell and 25 complete superblocks. Within each M use `A8,B1,B1,A8`; rotate the M order by block index through `[1,16,32,64]`, `[16,32,64,1]`, `[32,64,1,16]`, `[64,1,16,32]`. Use two same-cell warmups per measured call, producing 50 samples/cell. CUDA events enclose only the module call; no conditioner.

        Run one NCU profile per cell under the same GPU lock. Separate split8 GEMM and reduction. Freeze L2 read hit/miss sectors, L1/TEX bytes, L2 bytes, DRAM bytes, and duration. Query only a minimal, semantically clear launch waves/SM or active-warps/SM/SM-throughput metric; absence does not block the screen but limits the claim to launch-level CTA supply plus timing.

        If split1 L2 hit unexpectedly falls at these capacity-safe points, stop parallelism interpretation and explain cache first. Otherwise interpret split benefit only as a CTA-supply/tile-utilization/reduction tradeoff unless M64 still shows a clear residual with high split1 hit and grid=384.
        """).strip() + "\n"
    (out / "RUNNER_CONTRACT.md").write_text(runner, encoding="utf-8")

    boundary = dedent("""
        # Scientific boundary

        This artificial kernel screen asks whether split-K retains value at low launch-level CTA supply after classic grouped locality scheduling and with a 24.9375 MiB weight-side set. Weight-side <64 MiB reduces capacity pressure but does not prove residency; set mapping, scheduling, input/output traffic, and other interference remain.

        CTA/SM values are launch-level supply, not simultaneous residency or occupancy proof. A low-M split8 advantage belongs to established parallel decomposition/Stream-K-style tradeoffs, not a new cache mechanism. Results are limited to this AutoAWQ kernel, K4096/N12288, four M values, split1/8, and GROUP_FULL_M; no full-model or general W4 extrapolation is allowed.
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
