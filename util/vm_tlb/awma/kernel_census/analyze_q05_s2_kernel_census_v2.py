#!/usr/bin/env python3
"""Offline, correlation-first Qwen2.5 S2 kernel-census reclassification.

This is deliberately an analysis-only consumer of the accepted NSYS SQLite
export.  A GPU kernel is assigned to a model phase only when its CUPTI
correlationId resolves to exactly one CPU CUDA runtime activity and that
activity's start timestamp belongs to an NVTX C16_PHASE range on the same CPU
thread.  No GPU wall-time/NVTX overlap is used for the V2 decision.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


STAGE = "AWMA_QWEN25_S2_KERNEL_CENSUS_RECLASSIFICATION_V2"
FIELDS = [
    "global_launch_index", "phase_class", "phase", "decode_step",
    "assignment_method", "runtime_correlation_id", "runtime_start_ns",
    "runtime_end_ns", "runtime_global_tid", "runtime_api_name",
    "start_ns", "end_ns", "duration_ns", "stream", "grid", "block",
    "exact_kernel_function", "normalized_kernel_family", "semantic_category",
    "v1_phase", "v1_decode_step", "v1_nvtx_overlap_ns",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def family(name: str) -> str:
    lowered = name.lower()
    if "pytorch_flash::flash_fwd" in lowered:
        return "PYTORCH_FLASH_FWD"
    if "pytorch_flash::flash" in lowered:
        return "PYTORCH_FLASH_OTHER"
    if "internal::gemm" in lowered or "gemm" in lowered:
        return "CUBLAS_GEMM"
    if "internal::gemvx" in lowered or "gemv" in lowered:
        return "CUBLAS_GEMV"
    if "vectorized_elementwise_kernel" in lowered:
        return "AT_NATIVE_VECTORIZED_ELEMENTWISE"
    if "unrolled_elementwise_kernel" in lowered:
        return "AT_NATIVE_UNROLLED_ELEMENTWISE"
    if "elementwise_kernel" in lowered:
        return "AT_NATIVE_ELEMENTWISE"
    if "reduce_kernel" in lowered:
        return "AT_NATIVE_REDUCE"
    if "layer_norm" in lowered or "rms_norm" in lowered:
        return "NORM_KERNEL"
    if "rotary" in lowered or "rope" in lowered:
        return "ROPE_KERNEL"
    if "copy" in lowered or "memcpy" in lowered:
        return "COPY_KERNEL"
    return "OTHER_EXACT_IMPLEMENTATION"


def semantic(name: str) -> str:
    lowered = name.lower()
    if "pytorch_flash::flash" in lowered:
        return "ATTENTION_CORE"
    if "rotary" in lowered or "rope" in lowered:
        return "ROPE"
    if "layer_norm" in lowered or "rms_norm" in lowered:
        return "NORM"
    if "direct_copy" in lowered or "copy_kernel" in lowered:
        return "COPY_LAYOUT"
    if "elementwise" in lowered or "reduce_kernel" in lowered:
        return "ELEMENTWISE"
    # No function/layer/operator inference is licensed for GEMM/GEMV or other
    # implementation names.
    return "UNKNOWN"


def parse_phase(text: str) -> dict[str, str]:
    return dict(field.split("=", 1) for field in text.split(";") if "=" in field)


def read_v1(path: Path) -> dict[int, dict[str, str]]:
    with path.open(newline="") as handle:
        rows = csv.DictReader(handle, delimiter="\t")
        result = {int(row["global_launch_index"]): row for row in rows}
    if not result:
        raise ValueError("V1 inventory is empty")
    return result


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def aggregate(
    rows: list[dict[str, Any]],
    keys: list[str],
    reference_duration: int | None = None,
    reference_count: int | None = None,
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[tuple(str(row[key]) for key in keys)].append(row)
    total_duration = sum(int(row["duration_ns"]) for row in rows) if reference_duration is None else reference_duration
    total_count = len(rows) if reference_count is None else reference_count
    output = []
    for key, values in groups.items():
        duration = sum(int(value["duration_ns"]) for value in values)
        item = dict(zip(keys, key))
        item.update({
            "launch_count": len(values),
            "accumulated_gpu_duration_ns": duration,
            "gpu_time_share_all_launches": duration / total_duration if total_duration else 0.0,
            "launch_count_share_all_launches": len(values) / total_count if total_count else 0.0,
        })
        output.append(item)
    return sorted(output, key=lambda item: (-int(item["accumulated_gpu_duration_ns"]), tuple(str(item[key]) for key in keys)))


def make_assignment(runtime_rows: list[dict[str, Any]], phases_by_tid: dict[int, list[dict[str, Any]]], all_phases: list[dict[str, Any]]) -> tuple[str, str, str, str, dict[str, Any] | None]:
    """Return phase class, phase, step, method, and resolved CPU API row."""
    if not runtime_rows:
        return "UNKNOWN", "UNKNOWN", "", "UNKNOWN_NO_CUPTI_RUNTIME_CORRELATION", None
    if len(runtime_rows) != 1:
        return "UNKNOWN", "UNKNOWN", "", "UNKNOWN_AMBIGUOUS_CUPTI_RUNTIME_CORRELATION", None
    runtime = runtime_rows[0]
    same_thread = phases_by_tid.get(runtime["global_tid"], [])
    contained = [phase for phase in same_thread if phase["start"] <= runtime["start"] <= phase["end"]]
    if len(contained) == 1:
        phase = contained[0]
        if phase["phase"] == "PREFILL":
            return "PREFILL", "PREFILL", "", "CUPTI_CORRELATED_RUNTIME_START_IN_SAME_THREAD_NVTX", runtime
        if phase["phase"] == "DECODE":
            return "DECODE", "DECODE", phase["step"], "CUPTI_CORRELATED_RUNTIME_START_IN_SAME_THREAD_NVTX", runtime
        raise ValueError(f"unexpected C16 phase {phase['phase']}")
    if any(phase["start"] <= runtime["start"] <= phase["end"] for phase in all_phases):
        return "UNKNOWN", "UNKNOWN", "", "UNKNOWN_RUNTIME_THREAD_CONTEXT_MISMATCH", runtime
    return "AUXILIARY", "AUXILIARY", "", "AUXILIARY_RUNTIME_START_OUTSIDE_ALL_C16_PHASE_RANGES", runtime


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sqlite", type=Path, required=True)
    parser.add_argument("--v1-inventory", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="durable node164-only V2 output directory")
    parser.add_argument("--review-dir", type=Path, required=True, help="compact Git review-pack directory")
    args = parser.parse_args()
    if not args.sqlite.is_file() or not args.v1_inventory.is_file():
        raise FileNotFoundError("SQLite and V1 inventory must be existing read-only inputs")
    args.out.mkdir(parents=True, exist_ok=False)
    args.review_dir.mkdir(parents=True, exist_ok=False)

    connection = sqlite3.connect(f"file:{args.sqlite}?mode=ro", uri=True)
    strings = dict(connection.execute("select id, value from StringIds"))
    phase_rows = []
    for start, end, text, tid in connection.execute("select start,end,text,globalTid from NVTX_EVENTS where text like 'C16_PHASE=%' order by start"):
        fields = parse_phase(text)
        phase_rows.append({"start": start, "end": end, "phase": fields["C16_PHASE"], "step": fields.get("STEP", ""), "global_tid": tid, "label": text})
    if len(phase_rows) != 33 or phase_rows[0]["phase"] != "PREFILL" or sum(row["phase"] == "DECODE" for row in phase_rows) != 32:
        raise ValueError("unexpected frozen C16 phase contract")
    phases_by_tid: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for item in phase_rows:
        phases_by_tid[item["global_tid"]].append(item)

    runtime_by_correlation: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for start, end, correlation, tid, name_id in connection.execute("select start,end,correlationId,globalTid,nameId from CUPTI_ACTIVITY_KIND_RUNTIME where correlationId is not null"):
        runtime_by_correlation[correlation].append({"start": start, "end": end, "global_tid": tid, "api_name": strings.get(name_id, "UNKNOWN_RUNTIME_API")})

    v1 = read_v1(args.v1_inventory)
    sql = "select start,end,streamId,correlationId,gridX,gridY,gridZ,blockX,blockY,blockZ,demangledName,shortName,mangledName from CUPTI_ACTIVITY_KIND_KERNEL order by start,end"
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(connection.execute(sql)):
        start, end, stream, correlation, gx, gy, gz, bx, by, bz, demangled, short, mangled = item
        old = v1.get(index)
        if old is None:
            raise ValueError(f"missing V1 row for launch {index}")
        name = strings.get(demangled) or strings.get(short) or strings.get(mangled) or "UNKNOWN_KERNEL_NAME"
        phase_class, phase, step, method, runtime = make_assignment(runtime_by_correlation.get(correlation, []), phases_by_tid, phase_rows)
        rows.append({
            "global_launch_index": index, "phase_class": phase_class, "phase": phase, "decode_step": step,
            "assignment_method": method, "runtime_correlation_id": "" if correlation is None else correlation,
            "runtime_start_ns": "" if runtime is None else runtime["start"], "runtime_end_ns": "" if runtime is None else runtime["end"],
            "runtime_global_tid": "" if runtime is None else runtime["global_tid"], "runtime_api_name": "" if runtime is None else runtime["api_name"],
            "start_ns": start, "end_ns": end, "duration_ns": end - start, "stream": stream,
            "grid": f"{gx},{gy},{gz}", "block": f"{bx},{by},{bz}", "exact_kernel_function": name,
            "normalized_kernel_family": family(name), "semantic_category": semantic(name),
            "v1_phase": old["phase"], "v1_decode_step": old["decode_step"], "v1_nvtx_overlap_ns": old["nvtx_overlap_ns"],
        })
    if len(rows) != len(v1):
        raise ValueError(f"V1/V2 launch-count mismatch: {len(v1)} != {len(rows)}")

    inventory = args.out / "ALL_KERNEL_LAUNCHES_V2.tsv"
    write_tsv(inventory, FIELDS, rows)
    phase_summary = aggregate(rows, ["phase_class", "phase", "decode_step", "assignment_method"])
    family_summary = aggregate(rows, ["phase_class", "phase", "decode_step", "semantic_category", "normalized_kernel_family", "exact_kernel_function", "grid", "block"])
    delta_rows = []
    for group in aggregate(rows, ["v1_phase", "v1_decode_step", "phase_class", "phase", "decode_step", "assignment_method"]):
        delta_rows.append(group)
    reclassified = [row for row in rows if row["v1_phase"] == "UNKNOWN" and row["phase_class"] != "UNKNOWN"]
    reclassified_summary = aggregate(
        reclassified,
        ["phase_class", "phase", "decode_step", "assignment_method", "normalized_kernel_family"],
        sum(int(row["duration_ns"]) for row in rows),
        len(rows),
    )
    top_rows = aggregate(rows, ["phase_class", "phase", "decode_step", "normalized_kernel_family", "exact_kernel_function", "grid", "block"])[:200]
    phase_path = args.out / "V2_PHASE_SUMMARY.tsv"
    family_path = args.out / "V2_FULL_CLASSIFICATION_SUMMARY.tsv"
    delta_path = args.out / "V1_TO_V2_ATTRIBUTION_DELTA.tsv"
    reclassified_path = args.out / "V1_UNKNOWN_RECLASSIFIED_V2.tsv"
    top_path = args.out / "V2_TOP_200_CLASSIFICATIONS.tsv"
    write_tsv(phase_path, list(phase_summary[0]), phase_summary)
    write_tsv(family_path, list(family_summary[0]), family_summary)
    write_tsv(delta_path, list(delta_rows[0]), delta_rows)
    write_tsv(reclassified_path, list(reclassified_summary[0]) if reclassified_summary else ["phase_class", "phase", "decode_step", "assignment_method", "normalized_kernel_family", "launch_count", "accumulated_gpu_duration_ns", "gpu_time_share_all_launches", "launch_count_share_all_launches"], reclassified_summary)
    write_tsv(top_path, list(top_rows[0]), top_rows)

    total_duration = sum(int(row["duration_ns"]) for row in rows)
    method_counts = Counter(row["assignment_method"] for row in rows)
    class_counts = Counter(row["phase_class"] for row in rows)
    class_time = Counter()
    for row in rows:
        class_time[row["phase_class"]] += int(row["duration_ns"])
    changed = [row for row in rows if (row["v1_phase"], row["v1_decode_step"]) != (row["phase"], row["decode_step"])]
    report = {
        "stage": STAGE,
        "method": "CUPTI kernel correlationId -> exactly-one CUPTI runtime API -> same-globalTid NVTX C16_PHASE range containing runtime API start",
        "prohibited_method": "GPU kernel wall-time overlap with NVTX ranges is not used for V2 phase attribution",
        "sqlite": {"path": str(args.sqlite), "sha256": sha256(args.sqlite)},
        "v1_inventory": {"path": str(args.v1_inventory), "sha256": sha256(args.v1_inventory), "rows": len(v1)},
        "v2_inventory": {"path": str(inventory), "sha256": sha256(inventory), "rows": len(rows)},
        "total_gpu_duration_ns": total_duration,
        "phase_ranges": phase_rows,
        "classification": {key: {"launch_count": class_counts[key], "accumulated_gpu_duration_ns": class_time[key], "gpu_time_share_all_launches": class_time[key] / total_duration} for key in sorted(class_counts)},
        "assignment_method_counts": dict(sorted(method_counts.items())),
        "v1_to_v2_changed": {"launch_count": len(changed), "accumulated_gpu_duration_ns": sum(int(row["duration_ns"]) for row in changed)},
        "v1_unknown_legally_reclassified": {"launch_count": len(reclassified), "accumulated_gpu_duration_ns": sum(int(row["duration_ns"]) for row in reclassified)},
        "invariants": {
            "v1_v2_launch_count_equal": len(rows) == len(v1),
            "all_v2_rows_accounted_for": sum(class_counts.values()) == len(rows),
            "all_v2_gpu_time_accounted_for": sum(class_time.values()) == total_duration,
            "no_operator_or_layer_inference": True,
            "new_gpu_capture_performed": False,
        },
    }
    manifest_paths = [inventory, phase_path, family_path, delta_path, reclassified_path, top_path]
    manifest = {path.name: {"size_bytes": path.stat().st_size, "sha256": sha256(path)} for path in manifest_paths}
    (args.out / "RUN_RECEIPT_V2.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    manifest_paths.append(args.out / "RUN_RECEIPT_V2.json")
    (args.out / "SHA256SUMS").write_text("".join(f"{sha256(path)}  {path.name}\n" for path in sorted(manifest_paths)) + "")
    manifest["RUN_RECEIPT_V2.json"] = {"size_bytes": (args.out / "RUN_RECEIPT_V2.json").stat().st_size, "sha256": sha256(args.out / "RUN_RECEIPT_V2.json")}

    # Only compact, independently reviewable derivatives enter Git.
    for source in (phase_path, delta_path, reclassified_path, top_path, args.out / "RUN_RECEIPT_V2.json", args.out / "SHA256SUMS"):
        (args.review_dir / source.name).write_bytes(source.read_bytes())
    (args.review_dir / "DURABLE_ARTIFACT_INDEX_V2.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
