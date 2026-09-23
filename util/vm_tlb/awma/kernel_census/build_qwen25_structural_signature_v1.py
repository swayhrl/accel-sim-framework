#!/usr/bin/env python3
"""Build the S2-only structural signature and scenario-weighted kernel catalog.

The input V2 inventory is read-only.  This tool records repetitions observed
inside the single B=1, Prefill=2048, Decode=32, FP16, SDPA, TEXT S2 execution;
it does not turn those observations into model-intrinsic claims.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


STAGE = "AWMA_QWEN25_STRUCTURAL_SIGNATURE_AND_SCENARIO_WEIGHT_V1"
SCENARIO = "B=1;Prefill=2048;Decode=32;FP16;SDPA;TEXT_S2"
DECODE_STEPS = tuple(str(number) for number in range(1, 33))


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, columns: list[str], values: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(values)


def normalize_shape(value: str) -> str:
    return ",".join(part.strip() for part in value.strip().strip("()").split(","))


def implementation_key(name: str) -> str:
    lowered = name.lower()
    if "flash_fwd_splitkv_combine_kernel" in lowered:
        return "FLASH_FWD_SPLITKV_COMBINE"
    if "flash_fwd_splitkv_kernel" in lowered:
        return "FLASH_FWD_SPLITKV"
    if "flash_fwd_kernel" in lowered:
        return "FLASH_FWD"
    if "internal::gemvx" in lowered or "gemvx::kernel" in lowered:
        return "CUBLAS_GEMV"
    if "cutlass_80_tensorop_f16_s16816gemm_relu_f16_256x128_32x3_tn_align8" in lowered:
        return "CUTLASS_F16_GEMM_256X128_32X3_TN_ALIGN8"
    return "EXACT_IMPLEMENTATION_UNNORMALIZED"


def family_from_function(name: str) -> str:
    lowered = name.lower()
    if "flash_fwd" in lowered:
        return "PYTORCH_FLASH_FWD"
    if "gemvx" in lowered or "gemv" in lowered:
        return "CUBLAS_GEMV"
    if "gemm" in lowered or "cutlass" in lowered:
        return "CUBLAS_GEMM"
    if "vectorized_elementwise_kernel" in lowered:
        return "AT_NATIVE_VECTORIZED_ELEMENTWISE"
    if "unrolled_elementwise_kernel" in lowered:
        return "AT_NATIVE_UNROLLED_ELEMENTWISE"
    if "elementwise_kernel" in lowered:
        return "AT_NATIVE_ELEMENTWISE"
    if "reduce_kernel" in lowered:
        return "AT_NATIVE_REDUCE"
    if "copy" in lowered or "memcpy" in lowered:
        return "COPY_KERNEL"
    if "rms_norm" in lowered or "layer_norm" in lowered:
        return "NORM_KERNEL"
    if "rotary" in lowered or "rope" in lowered:
        return "ROPE_KERNEL"
    return "OTHER_EXACT_IMPLEMENTATION"


def nonempty_set(values: list[str]) -> tuple[str, ...]:
    return tuple(sorted(set(value for value in values if value)))


def stable_sets(by_step: dict[str, set[tuple[str, ...]]]) -> str:
    ordered = [tuple(sorted(by_step.get(step, set()))) for step in DECODE_STEPS]
    return "YES" if ordered and all(item == ordered[0] for item in ordered[1:]) else "NO"


def asset_status(candidates: list[dict[str, str]]) -> tuple[str, str, str]:
    if not candidates:
        return "MISSING_SIM_TRACE", "", ""
    priority = ("REUSABLE_NOW", "REQUIRES_REQUALIFICATION", "NATIVE_ONLY", "MISSING_SIM_TRACE")
    statuses = set(row["classification"] for row in candidates)
    selected = next(status for status in priority if status in statuses)
    selected_rows = [row for row in candidates if row["classification"] == selected]
    targets = ";".join(sorted(set(row["accepted_target"] for row in selected_rows)))
    asset_ids = ";".join(sorted(set(row["candidate"] for row in selected_rows)))
    return selected, targets, asset_ids


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v2-inventory", type=Path, required=True)
    parser.add_argument("--lane-c-inventory", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    if not args.v2_inventory.is_file() or not args.lane_c_inventory.is_file():
        raise FileNotFoundError("both accepted inventory files are required")
    args.out_dir.mkdir(parents=True, exist_ok=False)

    v2 = rows(args.v2_inventory)
    assets = rows(args.lane_c_inventory)
    if len(v2) != 34677:
        raise ValueError(f"unexpected V2 launch count: {len(v2)}")
    if sum(1 for row in v2 if row["phase_class"] == "UNKNOWN"):
        raise ValueError("accepted V2 authority must not contain UNKNOWN rows")

    # Derive exact-safe Lane C matching metadata.  Exact function strings differ
    # in demangler spelling across inventories, so matching is limited to a
    # narrow implementation-kind key plus exact phase/family/grid/block.
    asset_index: dict[tuple[str, str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    native_unmapped = []
    for asset in assets:
        phase = asset["phase"]
        if asset["classification"] == "NATIVE_ONLY":
            native_unmapped.append(asset)
            continue
        exact = asset["exact_function"]
        if exact == "UNKNOWN" or asset["grid"] == "UNKNOWN" or asset["block"] == "UNKNOWN":
            continue
        key = (phase, family_from_function(exact), implementation_key(exact), normalize_shape(asset["grid"]), normalize_shape(asset["block"]))
        asset_index[key].append(asset)

    phase_total = Counter()
    family_total = Counter()
    stratum_total: dict[tuple[str, str, str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    family_impl_by_step: dict[tuple[str, str], dict[str, set[tuple[str, ...]]]] = defaultdict(lambda: defaultdict(set))
    impl_shape_by_step: dict[tuple[str, str, str], dict[str, set[tuple[str, str]]]] = defaultdict(lambda: defaultdict(set))
    for row in v2:
        duration = int(row["duration_ns"])
        phase = row["phase"]
        family = row["normalized_kernel_family"]
        exact = row["exact_kernel_function"]
        grid, block = row["grid"], row["block"]
        phase_total[phase] += duration
        family_total[(phase, family)] += duration
        stratum_total[(row["phase_class"], phase, family, exact, grid, block)].append(row)
        if phase == "DECODE":
            step = row["decode_step"]
            family_impl_by_step[(phase, family)][step].add((exact,))
            impl_shape_by_step[(phase, family, exact)][step].add((grid, block))

    full_total = sum(int(row["duration_ns"]) for row in v2)
    catalog: list[dict[str, Any]] = []
    for (phase_class, phase, family, exact, grid, block), members in stratum_total.items():
        duration = sum(int(row["duration_ns"]) for row in members)
        key = implementation_key(exact)
        base: dict[str, Any] = {
            "catalog_row_type": "STRUCTURAL_STRATUM",
            "scenario_binding": SCENARIO,
            "phase_class": phase_class,
            "phase": phase,
            "normalized_kernel_family": family,
            "exact_implementation": exact,
            "implementation_match_key": key,
            "grid": grid,
            "block": block,
            "launches_per_prefill_pass": "NOT_APPLICABLE",
            "launches_per_decode_step_mean": "NOT_APPLICABLE",
            "launches_per_decode_step_min": "NOT_APPLICABLE",
            "launches_per_decode_step_max": "NOT_APPLICABLE",
            "launch_count_variation_max_minus_min": "NOT_APPLICABLE",
            "decode_step_count": "NOT_APPLICABLE",
            "count_stable_across_32_decode_steps": "NOT_APPLICABLE",
            "implementation_stable_across_32_decode_steps": "NOT_APPLICABLE",
            "shape_stable_across_32_decode_steps": "NOT_APPLICABLE",
            "structural_observation_label": "DATA_DEPENDENT_NOT_APPLICABLE_OR_UNKNOWN",
            "cross_context_label": "UNTESTED_ACROSS_CONTEXT",
            "performance_weight_label": "SCENARIO_SPECIFIC",
            "stratum_launch_count_s2": len(members),
            "stratum_accumulated_gpu_duration_ns": duration,
            "stratum_gpu_time_share_full_s2": duration / full_total,
            "stratum_gpu_time_share_within_phase": duration / phase_total[phase],
            "family_accumulated_gpu_duration_ns": family_total[(phase, family)],
            "family_gpu_time_share_full_s2": family_total[(phase, family)] / full_total,
            "family_gpu_time_share_within_phase": family_total[(phase, family)] / phase_total[phase],
            "phase_accumulated_gpu_duration_ns": phase_total[phase],
            "phase_gpu_time_share_full_s2": phase_total[phase] / full_total,
            "lane_c_asset_status": "MISSING_SIM_TRACE",
            "lane_c_accepted_target": "",
            "lane_c_candidate_ids": "",
            "asset_join_basis": "EXACT_PHASE_FAMILY_IMPLEMENTATION_KEY_GRID_BLOCK",
        }
        if phase == "PREFILL":
            base["launches_per_prefill_pass"] = len(members)
            # One observed pass cannot establish recurrence.
            base["structural_observation_label"] = "SCENARIO_SPECIFIC"
        elif phase == "DECODE":
            count_by_step = Counter(row["decode_step"] for row in members)
            all_counts = [count_by_step[step] for step in DECODE_STEPS]
            minimum, maximum = min(all_counts), max(all_counts)
            count_stable = "YES" if minimum == maximum else "NO"
            implementation_stable = stable_sets(family_impl_by_step[(phase, family)])
            shape_stable = stable_sets(impl_shape_by_step[(phase, family, exact)])
            base.update({
                "launches_per_decode_step_mean": statistics.mean(all_counts),
                "launches_per_decode_step_min": minimum,
                "launches_per_decode_step_max": maximum,
                "launch_count_variation_max_minus_min": maximum - minimum,
                "decode_step_count": 32,
                "count_stable_across_32_decode_steps": count_stable,
                "implementation_stable_across_32_decode_steps": implementation_stable,
                "shape_stable_across_32_decode_steps": shape_stable,
                "structural_observation_label": "OBSERVED_STABLE_WITHIN_S2" if count_stable == implementation_stable == shape_stable == "YES" else "SCENARIO_SPECIFIC",
            })
        match = (phase, family, key, normalize_shape(grid), normalize_shape(block))
        status, targets, candidates = asset_status(asset_index.get(match, []))
        base.update({"lane_c_asset_status": status, "lane_c_accepted_target": targets, "lane_c_candidate_ids": candidates})
        catalog.append(base)

    # Preserve Lane C Native-only provenance without pretending its UNKNOWN
    # exact functions/shapes are evidence for an observed structural stratum.
    for asset in native_unmapped:
        catalog.append({
            "catalog_row_type": "LANE_C_UNMAPPED_NATIVE_ONLY",
            "scenario_binding": SCENARIO,
            "phase_class": asset["phase"], "phase": asset["phase"],
            "normalized_kernel_family": "UNKNOWN", "exact_implementation": "UNKNOWN",
            "implementation_match_key": "UNKNOWN", "grid": "UNKNOWN", "block": "UNKNOWN",
            "launches_per_prefill_pass": "DATA_DEPENDENT_NOT_APPLICABLE_OR_UNKNOWN",
            "launches_per_decode_step_mean": "DATA_DEPENDENT_NOT_APPLICABLE_OR_UNKNOWN",
            "launches_per_decode_step_min": "DATA_DEPENDENT_NOT_APPLICABLE_OR_UNKNOWN",
            "launches_per_decode_step_max": "DATA_DEPENDENT_NOT_APPLICABLE_OR_UNKNOWN",
            "launch_count_variation_max_minus_min": "DATA_DEPENDENT_NOT_APPLICABLE_OR_UNKNOWN",
            "decode_step_count": "DATA_DEPENDENT_NOT_APPLICABLE_OR_UNKNOWN",
            "count_stable_across_32_decode_steps": "DATA_DEPENDENT_NOT_APPLICABLE_OR_UNKNOWN",
            "implementation_stable_across_32_decode_steps": "DATA_DEPENDENT_NOT_APPLICABLE_OR_UNKNOWN",
            "shape_stable_across_32_decode_steps": "DATA_DEPENDENT_NOT_APPLICABLE_OR_UNKNOWN",
            "structural_observation_label": "DATA_DEPENDENT_NOT_APPLICABLE_OR_UNKNOWN",
            "cross_context_label": "UNTESTED_ACROSS_CONTEXT",
            "performance_weight_label": "DATA_DEPENDENT_NOT_APPLICABLE_OR_UNKNOWN",
            "stratum_launch_count_s2": "", "stratum_accumulated_gpu_duration_ns": "",
            "stratum_gpu_time_share_full_s2": "", "stratum_gpu_time_share_within_phase": "",
            "family_accumulated_gpu_duration_ns": "", "family_gpu_time_share_full_s2": "", "family_gpu_time_share_within_phase": "",
            "phase_accumulated_gpu_duration_ns": "", "phase_gpu_time_share_full_s2": "",
            "lane_c_asset_status": "NATIVE_ONLY", "lane_c_accepted_target": asset["accepted_target"],
            "lane_c_candidate_ids": asset["candidate"],
            "asset_join_basis": "LANE_C_NATIVE_ONLY_EXACT_FUNCTION_AND_SHAPE_UNKNOWN_NOT_JOINED",
        })

    catalog.sort(key=lambda row: (row["catalog_row_type"], row["phase"], -float(row["stratum_accumulated_gpu_duration_ns"] or 0), row["normalized_kernel_family"], row["grid"]))
    catalog_columns = list(catalog[0])
    catalog_path = args.out_dir / "QWEN25_STRUCTURAL_AND_WEIGHTED_KERNEL_CATALOG_V1.tsv"
    write_tsv(catalog_path, catalog_columns, catalog)

    structural_summary = []
    for row in catalog:
        if row["catalog_row_type"] != "STRUCTURAL_STRATUM":
            continue
        structural_summary.append({key: row[key] for key in [
            "phase", "normalized_kernel_family", "exact_implementation", "grid", "block",
            "launches_per_prefill_pass", "launches_per_decode_step_mean", "launches_per_decode_step_min",
            "launches_per_decode_step_max", "launch_count_variation_max_minus_min", "decode_step_count",
            "count_stable_across_32_decode_steps", "implementation_stable_across_32_decode_steps",
            "shape_stable_across_32_decode_steps", "structural_observation_label", "cross_context_label",
        ]})
    structural_path = args.out_dir / "STRUCTURAL_SIGNATURE_SUMMARY_V1.tsv"
    write_tsv(structural_path, list(structural_summary[0]), structural_summary)

    weight_summary = []
    for row in catalog:
        if row["catalog_row_type"] != "STRUCTURAL_STRATUM":
            continue
        weight_summary.append({key: row[key] for key in [
            "scenario_binding", "phase", "normalized_kernel_family", "exact_implementation", "grid", "block",
            "phase_accumulated_gpu_duration_ns", "phase_gpu_time_share_full_s2",
            "family_accumulated_gpu_duration_ns", "family_gpu_time_share_full_s2", "family_gpu_time_share_within_phase",
            "stratum_accumulated_gpu_duration_ns", "stratum_gpu_time_share_full_s2", "stratum_gpu_time_share_within_phase",
            "performance_weight_label",
        ]})
    weight_path = args.out_dir / "SCENARIO_SPECIFIC_WEIGHT_SUMMARY_V1.tsv"
    write_tsv(weight_path, list(weight_summary[0]), weight_summary)

    receipt = {
        "stage": STAGE, "scenario_binding": SCENARIO,
        "v2_inventory": {"path": str(args.v2_inventory), "sha256": sha256(args.v2_inventory), "rows": len(v2)},
        "lane_c_inventory": {"path": str(args.lane_c_inventory), "sha256": sha256(args.lane_c_inventory), "rows": len(assets)},
        "catalog": {"rows": len(catalog), "structural_strata": len(stratum_total), "unmapped_native_only_rows": len(native_unmapped)},
        "phase_gpu_time_ns": dict(phase_total),
        "phase_gpu_time_share_full_s2": {phase: value / full_total for phase, value in phase_total.items()},
        "labels": ["OBSERVED_STABLE_WITHIN_S2", "SCENARIO_SPECIFIC", "UNTESTED_ACROSS_CONTEXT", "DATA_DEPENDENT_NOT_APPLICABLE_OR_UNKNOWN"],
        "prohibitions": {"new_gpu_capture": False, "accel_sim_replay": False, "layer_or_operator_inference_from_recurrence": False},
    }
    receipt_path = args.out_dir / "RUN_RECEIPT_V1.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    files = [catalog_path, structural_path, weight_path, receipt_path]
    (args.out_dir / "SHA256SUMS").write_text("".join(f"{sha256(path)}  {path.name}\n" for path in sorted(files)) + "")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
