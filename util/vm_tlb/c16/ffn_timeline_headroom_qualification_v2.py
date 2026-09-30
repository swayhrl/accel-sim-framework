#!/usr/bin/env python3
"""Independent CPU-only consumer for the accepted natural FFN timeline."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import statistics
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


PRODUCER = "071297ae7f4aa772a27fae0cf31ad47ab7d967be"
PRODUCER_TREE = "1e6a4f5ed19dfc76f91795524a29ac652156c653"
CAPTURE_SOURCE = "5fe650664a8f7adebf034052d2ac08b2fdbc2348"
PACK_IN = "docs/vm_tlb/review_packs/C16_FFN_TIMELINE_AUTHORITY_CAPTURE_109_V1"
PACK_OUT = "docs/vm_tlb/review_packs/C16_FFN_TIMELINE_HEADROOM_QUALIFICATION_174NEW_V2"
RUNNER = "util/vm_tlb/c16/e1_operator_family_natural.py"
RUNNER_SHA256 = "ad922629a9898c01400a165b2f6565659f1c6e422784c10bc1d013265c45b5fb"
HISTORICAL_MODULE_FRACTION = 0.445746799882408
EXPECTED_DECODE_WALL_NS = 97_970_144
EXPECTED_WINDOW_UNION_NS = 27_901_594
LR10_BLOB = "d479680123abab8b4e3e462a55f9aa0312ef1258"
STAGES = ("gate", "activation", "up", "multiply", "down")
GAPS = ("gap_gate_activation", "gap_activation_up", "gap_up_multiply", "gap_multiply_down")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(repo: Path, commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=repo)


def git_text(repo: Path, commit: str, path: str) -> str:
    return git_bytes(repo, commit, path).decode("utf-8")


def read_json(repo: Path, name: str) -> dict:
    return json.loads(git_bytes(repo, PRODUCER, f"{PACK_IN}/{name}"))


def read_tsv(repo: Path, name: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(git_text(repo, PRODUCER, f"{PACK_IN}/{name}")), delimiter="\t"))


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            values = {}
            for field in fields:
                value = row.get(field, "NA")
                values[field] = "NA" if value is None or value == "" else value
            writer.writerow(values)


def merged_union(intervals: list[tuple[int, int]]) -> tuple[int, int]:
    total = 0
    overlaps = 0
    current_start = current_end = None
    for start, end in sorted(intervals):
        if not start < end:
            raise AssertionError(f"invalid interval {start}..{end}")
        if current_start is None:
            current_start, current_end = start, end
        elif start <= current_end:
            overlaps += 1
            current_end = max(current_end, end)
        else:
            total += current_end - current_start
            current_start, current_end = start, end
    if current_start is not None:
        total += current_end - current_start
    return total, overlaps


def robust_outlier_flags(records: list[dict]) -> dict[tuple[int, int], list[str]]:
    flags: dict[tuple[int, int], list[str]] = defaultdict(list)
    metrics = list(STAGES) + list(GAPS) + ["window", "unattributed"]
    for decode in range(4):
        group = [row for row in records if row["decode_step"] == decode]
        for metric in metrics:
            values = [row[f"{metric}_ns"] for row in group]
            med = statistics.median(values)
            mad = statistics.median(abs(value - med) for value in values)
            threshold = max(6.0 * 1.4826 * mad, 0.10 * max(med, 1), 2_000.0)
            for row in group:
                if abs(row[f"{metric}_ns"] - med) > threshold:
                    flags[(decode, row["layer"])].append(metric)
    return flags


def validate_inputs(repo: Path) -> dict:
    actual_tree = subprocess.check_output(["git", "rev-parse", f"{PRODUCER}^{{tree}}"], cwd=repo, text=True).strip()
    if actual_tree != PRODUCER_TREE:
        raise AssertionError(f"producer tree mismatch: {actual_tree}")
    manifest = git_text(repo, PRODUCER, f"{PACK_IN}/SHA256SUMS")
    manifest_rows = []
    for line in manifest.splitlines():
        expected, name = line.split("  ", 1)
        actual = sha256(git_bytes(repo, PRODUCER, f"{PACK_IN}/{name}"))
        if actual != expected:
            raise AssertionError(f"producer SHA mismatch for {name}")
        manifest_rows.append({"name": name, "sha256": actual})
    required = {
        "FINAL_STATUS.json", "RUN_IDENTITY.json", "SOURCE_AND_AUTHORITY.json", "INSTRUMENTATION_NEUTRALITY.json",
        "FORMAL_SANITY.json", "NATIVE_SANITY.json", "DECODE_WALL_INTERVAL.tsv", "FFN_LAYER_WINDOWS.tsv",
        "FFN_LAYER_ACTIVITY.tsv", "GATE_UP_RELATION.tsv", "CUDA_CORRELATION.tsv", "IMPLEMENTATION_FACTS.json",
    }
    if not required.issubset({row["name"] for row in manifest_rows}):
        raise AssertionError("required producer file missing from manifest")

    final = read_json(repo, "FINAL_STATUS.json")
    identity = read_json(repo, "RUN_IDENTITY.json")
    source = read_json(repo, "SOURCE_AND_AUTHORITY.json")
    neutrality = read_json(repo, "INSTRUMENTATION_NEUTRALITY.json")
    formal = read_json(repo, "FORMAL_SANITY.json")
    native = read_json(repo, "NATIVE_SANITY.json")
    assertions = read_json(repo, "RAW_ASSERTIONS.json")
    implementation = read_json(repo, "IMPLEMENTATION_FACTS.json")
    for doc in (final, identity, source, neutrality, formal, native, assertions, implementation):
        if not str(doc["status"]).startswith("PASS") and doc["status"] != "TIMELINE_AUTHORITY_CAPTURE_PASS":
            raise AssertionError(f"producer gate not passed: {doc['status']}")
    if source["patch_correction_commit"] != "efe091e8dda5ad27ff70ccb264aed84ed501a576":
        raise AssertionError("patch correction authority mismatch")
    if sha256(git_bytes(repo, CAPTURE_SOURCE, RUNNER)) != RUNNER_SHA256:
        raise AssertionError("capture runner SHA mismatch")
    if not neutrality["checks"]["kernel_name_count_order_equal"] or neutrality["left_kernel_count"] != 7441 or neutrality["right_kernel_count"] != 7441:
        raise AssertionError("7441-kernel neutrality did not close")
    if formal["right_range_counts"] != {"activation": 112, "decode_wall": 1, "multiply": 112, "projection": 336}:
        raise AssertionError("formal semantic range counts drifted")
    if assertions["semantic_range_count"] != 560 or assertions["projection_missing_activity"] != 0:
        raise AssertionError("semantic/correlation closure failed")
    if final["layer_decode_windows"] != 112 or final["gate_up_overlap_observed_count"] != 0:
        raise AssertionError("window/overlap authority failed")
    historical_path = repo / "docs/vm_tlb/review_packs/C16_FFN_HANDOFF_AUTHORITY_RECOVERY_V1/FINAL_DECISION.json"
    historical = json.loads(historical_path.read_text(encoding="utf-8"))
    if historical["module_duration_sum_fraction"] != HISTORICAL_MODULE_FRACTION:
        raise AssertionError("historical module-duration fraction drifted")
    lr10 = subprocess.check_output(["git", "cat-file", "-p", LR10_BLOB], cwd=repo, text=True)
    for term in ("Kitsune", "VTC", "ComFuse", "Rubin", "普通融合"):
        if term not in lr10:
            raise AssertionError(f"LR10 term missing: {term}")
    return {
        "manifest_count": len(manifest_rows),
        "manifest_sha256": sha256(manifest.encode()),
        "final": final,
        "identity": identity,
        "neutrality": neutrality,
        "formal": formal,
        "native": native,
        "assertions": assertions,
        "implementation": implementation,
        "lr10_sha256": sha256(lr10.encode()),
        "historical_authority_sha256": sha256(historical_path.read_bytes()),
    }


def compute(repo: Path) -> dict:
    authority = validate_inputs(repo)
    wall_rows = read_tsv(repo, "DECODE_WALL_INTERVAL.tsv")
    windows_raw = read_tsv(repo, "FFN_LAYER_WINDOWS.tsv")
    activity = read_tsv(repo, "FFN_LAYER_ACTIVITY.tsv")
    relations = read_tsv(repo, "GATE_UP_RELATION.tsv")
    correlation = read_tsv(repo, "CUDA_CORRELATION.tsv")
    if len(wall_rows) != 1 or len(windows_raw) != 112 or len(activity) != 560 or len(relations) != 112 or len(correlation) != 6020:
        raise AssertionError("producer table row-count closure failed")
    wall_start = int(wall_rows[0]["gpu_start"])
    wall_end = int(wall_rows[0]["gpu_end"])
    decode_wall_ns = wall_end - wall_start
    if decode_wall_ns != EXPECTED_DECODE_WALL_NS:
        raise AssertionError(f"decode wall drift: {decode_wall_ns}")

    records = []
    for row in windows_raw:
        parsed = {key: int(value) for key, value in row.items()}
        rec = {
            "decode_step": parsed["decode_step"],
            "layer": parsed["layer"],
            "start_ns": parsed["earliest_producer_start"],
            "end_ns": parsed["last_consumer_completion"],
            "window_ns": parsed["last_consumer_completion"] - parsed["earliest_producer_start"],
            "gate_ns": parsed["gate_end"] - parsed["gate_start"],
            "activation_ns": parsed["activation_end"] - parsed["activation_start"],
            "up_ns": parsed["up_end"] - parsed["up_start"],
            "multiply_ns": parsed["multiply_end"] - parsed["multiply_start"],
            "down_ns": parsed["down_end"] - parsed["down_start"],
            "gap_gate_activation_ns": parsed["activation_start"] - parsed["gate_end"],
            "gap_activation_up_ns": parsed["up_start"] - parsed["activation_end"],
            "gap_up_multiply_ns": parsed["multiply_start"] - parsed["up_end"],
            "gap_multiply_down_ns": parsed["down_start"] - parsed["multiply_end"],
        }
        rec["stage_sum_ns"] = sum(rec[f"{stage}_ns"] for stage in STAGES)
        rec["unattributed_ns"] = rec["window_ns"] - rec["stage_sum_ns"]
        if min(rec[f"{gap}_ns"] for gap in GAPS) < 0 or rec["unattributed_ns"] != sum(rec[f"{gap}_ns"] for gap in GAPS):
            raise AssertionError(f"stage order/gap closure failed: {rec}")
        records.append(rec)
    if {(row["decode_step"], row["layer"]) for row in records} != {(decode, layer) for decode in range(4) for layer in range(28)}:
        raise AssertionError("112 layer/decode keys do not close")
    flags = robust_outlier_flags(records)
    for row in records:
        row["anomaly_flags"] = ",".join(flags.get((row["decode_step"], row["layer"]), []))

    all_intervals = [(row["start_ns"], row["end_ns"]) for row in records]
    union_ns, overlap_count = merged_union(all_intervals)
    if union_ns != EXPECTED_WINDOW_UNION_NS:
        raise AssertionError(f"window union drift: {union_ns}")
    if overlap_count != 0:
        raise AssertionError("FFN windows unexpectedly overlap")
    legal_fraction = union_ns / decode_wall_ns

    wall_output = []
    running_end = None
    for row in sorted(records, key=lambda item: item["start_ns"]):
        contribution = row["end_ns"] - max(row["start_ns"], running_end or row["start_ns"])
        wall_output.append({
            "record_type": "WINDOW", "decode_step": row["decode_step"], "layer": row["layer"],
            "start_ns": row["start_ns"], "end_ns": row["end_ns"], "duration_ns": row["window_ns"],
            "union_contribution_ns": max(0, contribution), "overlaps_previous": str(running_end is not None and row["start_ns"] <= running_end),
            "window_count": 1,
        })
        running_end = max(running_end or row["end_ns"], row["end_ns"])
    for label, selected in [(f"D{decode}", [row for row in records if row["decode_step"] == decode]) for decode in range(4)] + [("ALL", records)]:
        value, overlaps = merged_union([(row["start_ns"], row["end_ns"]) for row in selected])
        wall_output.append({
            "record_type": "SUMMARY", "decode_step": label, "layer": "ALL", "start_ns": min(row["start_ns"] for row in selected),
            "end_ns": max(row["end_ns"] for row in selected), "duration_ns": sum(row["window_ns"] for row in selected),
            "union_contribution_ns": value, "overlaps_previous": str(overlaps > 0), "window_count": len(selected),
        })

    stage_output = []
    for row in sorted(records, key=lambda item: (item["decode_step"], item["layer"])):
        stage_output.append({"record_type": "WINDOW", "window_count": 1, **row})
    stage_summaries = {}
    for label, selected in [(f"D{decode}", [row for row in records if row["decode_step"] == decode]) for decode in range(4)] + [("ALL", records)]:
        summary = {"record_type": "SUMMARY", "decode_step": label, "layer": "ALL", "window_count": len(selected)}
        for metric in ["window", "stage_sum", "unattributed"] + list(STAGES) + list(GAPS):
            values = [row[f"{metric}_ns"] for row in selected]
            summary[f"{metric}_ns"] = sum(values)
            summary[f"{metric}_median_ns"] = statistics.median(values)
        summary["anomaly_flags"] = str(sum(bool(row["anomaly_flags"]) for row in selected))
        stage_summaries[label] = summary
        stage_output.append(summary)

    activity_counts = Counter(row["semantic_role"] for row in activity)
    if activity_counts != {"gate_proj": 112, "activation": 112, "up_proj": 112, "multiply": 112, "down_proj": 112}:
        raise AssertionError(f"activity role counts drifted: {activity_counts}")
    if any(row["status"] != "CORRELATED_GPU_ACTIVITY" for row in activity):
        raise AssertionError("uncorrelated semantic activity")
    if any(row["overlap_observed"] != "False" or int(row["overlap_ns"]) != 0 for row in relations):
        raise AssertionError("gate/up overlap authority drifted")
    semantic_correlation = [row for row in correlation if row["semantic_role"] != "NON_FFN_WITHIN_DECODE"]
    streams = sorted({int(row["stream"]) for row in semantic_correlation})
    if streams != [7]:
        raise AssertionError(f"expected one semantic CUDA stream, got {streams}")
    role_kernel_facts = defaultdict(set)
    for row in semantic_correlation:
        role_kernel_facts[row["semantic_role"]].add((row["kernel_name"], row["grid"], row["block"]))

    elementwise_ns = sum(row["activation_ns"] + row["multiply_ns"] for row in records)
    handoff_tensor_bytes = 18_944 * 2
    handoff_bytes_per_window = 4 * 2 * handoff_tensor_bytes
    handoff_bytes_all = handoff_bytes_per_window * 112
    if handoff_tensor_bytes != 37_888 or handoff_bytes_all != 33_947_648:
        raise AssertionError("physical handoff byte accounting drifted")
    dataflow = [
        {"tensor": "hidden", "producer": "preceding layer normalization", "consumers": "gate_proj;up_proj", "shape": "[1,1,3584]", "dtype": "FP16", "logical_bytes": 7168, "global_tensor": "YES", "alias_or_view": "NO_EVIDENCE_OF_ALIAS", "writes_within_ffn": 0, "reads_within_ffn": 2, "cross_operator_handoff": "NO_FFN_INTERNAL_PRODUCER", "counted_handoff_bytes_per_window": 0, "authority": "accepted runner source + projection kernel signatures"},
        {"tensor": "gate_output", "producer": "gate_proj WQLinear_GEMM", "consumers": "SiLU", "shape": "[1,1,18944]", "dtype": "FP16", "logical_bytes": handoff_tensor_bytes, "global_tensor": "YES_DISTINCT_KERNEL_OUTPUT", "alias_or_view": "NO_OUT_OF_PLACE_SOURCE_PATH", "writes_within_ffn": 1, "reads_within_ffn": 1, "cross_operator_handoff": "YES", "counted_handoff_bytes_per_window": 2 * handoff_tensor_bytes, "authority": "runner source + GEMM/reduce then SiLU correlation"},
        {"tensor": "activated_gate", "producer": "out-of-place SiLU", "consumers": "multiply", "shape": "[1,1,18944]", "dtype": "FP16", "logical_bytes": handoff_tensor_bytes, "global_tensor": "YES_DISTINCT_KERNEL_OUTPUT", "alias_or_view": "NO_OUT_OF_PLACE_SOURCE_PATH", "writes_within_ffn": 1, "reads_within_ffn": 1, "cross_operator_handoff": "YES", "counted_handoff_bytes_per_window": 2 * handoff_tensor_bytes, "authority": "runner source + distinct SiLU/multiply GPU activities"},
        {"tensor": "up_output", "producer": "up_proj WQLinear_GEMM", "consumers": "multiply", "shape": "[1,1,18944]", "dtype": "FP16", "logical_bytes": handoff_tensor_bytes, "global_tensor": "YES_DISTINCT_KERNEL_OUTPUT", "alias_or_view": "NO_OUT_OF_PLACE_SOURCE_PATH", "writes_within_ffn": 1, "reads_within_ffn": 1, "cross_operator_handoff": "YES", "counted_handoff_bytes_per_window": 2 * handoff_tensor_bytes, "authority": "runner source + GEMM/reduce then multiply correlation"},
        {"tensor": "product", "producer": "out-of-place multiply", "consumers": "down_proj", "shape": "[1,1,18944]", "dtype": "FP16", "logical_bytes": handoff_tensor_bytes, "global_tensor": "YES_DISTINCT_KERNEL_OUTPUT", "alias_or_view": "NO_OUT_OF_PLACE_SOURCE_PATH", "writes_within_ffn": 1, "reads_within_ffn": 1, "cross_operator_handoff": "YES", "counted_handoff_bytes_per_window": 2 * handoff_tensor_bytes, "authority": "runner source + multiply then down GEMM correlation"},
        {"tensor": "down_output", "producer": "down_proj WQLinear_GEMM", "consumers": "residual path outside audited FFN window", "shape": "[1,1,3584]", "dtype": "FP16", "logical_bytes": 7168, "global_tensor": "YES", "alias_or_view": "NO_OUT_OF_PLACE_SOURCE_PATH", "writes_within_ffn": 1, "reads_within_ffn": 0, "cross_operator_handoff": "OUTSIDE_THIS_FFN_HANDOFF_BOUND", "counted_handoff_bytes_per_window": 0, "authority": "runner source + accepted projection shapes"},
        {"tensor": "AWQ_internal_partial_accumulation", "producer": "WQLinear_GEMM main kernel", "consumers": "same projection's reduce kernel", "shape": "UNKNOWN_INTERNAL_LAYOUT", "dtype": "FP16_PARTIAL_PATH", "logical_bytes": "UNKNOWN_NOT_NEEDED_FOR_HANDOFF_BOUND", "global_tensor": "INTERNAL_OPERATOR_SCRATCH", "alias_or_view": "NOT_APPLICABLE", "writes_within_ffn": "INTERNAL", "reads_within_ffn": "INTERNAL", "cross_operator_handoff": "NO", "counted_handoff_bytes_per_window": 0, "authority": "two correlated kernels per accepted AWQ projection; exact scratch layout not captured"},
    ]

    f2a_rows = []
    for row in records:
        branch_gate = row["gate_ns"] + row["activation_ns"]
        branch_up = row["up_ns"]
        saving = min(branch_gate, branch_up)
        ideal_stage = max(branch_gate, branch_up) + row["multiply_ns"] + row["down_ns"]
        f2a_rows.append({
            "decode_step": row["decode_step"], "layer": row["layer"], "gate_activation_ns": branch_gate,
            "up_ns": branch_up, "serialized_stage_ns": row["stage_sum_ns"], "ideal_stage_ns": ideal_stage,
            "gap_preserving_saving_ns": saving, "gap_preserving_ideal_window_ns": row["window_ns"] - saving,
            "gap_elided_ideal_window_ns": ideal_stage,
        })
    f2a_saving_ns = sum(row["gap_preserving_saving_ns"] for row in f2a_rows)
    gap_elided_saving_ns = union_ns - sum(row["gap_elided_ideal_window_ns"] for row in f2a_rows)

    decode_drift = {}
    for metric in ["window", "stage_sum", "unattributed"] + list(STAGES) + list(GAPS):
        medians = [stage_summaries[f"D{decode}"][f"{metric}_median_ns"] for decode in range(4)]
        decode_drift[metric] = {"per_decode_median_ns": medians, "max_to_min_ratio": max(medians) / min(medians), "visible_ge_10pct": max(medians) / min(medians) >= 1.10}

    return {
        "authority": authority,
        "decode_wall_ns": decode_wall_ns,
        "union_ns": union_ns,
        "overlap_count": overlap_count,
        "legal_fraction": legal_fraction,
        "records": records,
        "wall_output": wall_output,
        "stage_output": stage_output,
        "stage_summaries": stage_summaries,
        "decode_drift": decode_drift,
        "outlier_windows": [{"decode_step": key[0], "layer": key[1], "metrics": values} for key, values in sorted(flags.items())],
        "streams": streams,
        "role_kernel_facts": {role: [{"kernel": item[0], "grid": item[1], "block": item[2]} for item in sorted(items)] for role, items in sorted(role_kernel_facts.items())},
        "dataflow": dataflow,
        "handoff_bytes_per_window": handoff_bytes_per_window,
        "handoff_bytes_all": handoff_bytes_all,
        "elementwise_ns": elementwise_ns,
        "f2a_rows": f2a_rows,
        "f2a_saving_ns": f2a_saving_ns,
        "gap_elided_saving_ns": gap_elided_saving_ns,
    }


def dump_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def build(repo: Path, out: Path) -> None:
    c = compute(repo)
    out.mkdir(parents=True, exist_ok=True)
    validation = {
        "schema_version": 2,
        "status": "PASS",
        "producer_commit": PRODUCER,
        "producer_tree": PRODUCER_TREE,
        "capture_source_commit": CAPTURE_SOURCE,
        "producer_manifest_file_count": c["authority"]["manifest_count"],
        "producer_manifest_sha256": c["authority"]["manifest_sha256"],
        "exact_natural_scenario": True,
        "instrumentation_neutral": True,
        "kernel_identity": {"count_each": 7441, "sequence_sha256": c["authority"]["neutrality"]["left_kernel_sequence_sha256"]},
        "semantic_ranges": {"total": 560, "projection": 336, "activation": 112, "multiply": 112, "decode_wall": 1},
        "layer_decode_windows": 112,
        "correlation_authority": "NVTX launch scope + CUDA runtime correlationId -> GPU kernel",
        "correlated_decode_gpu_activities": 6020,
        "projection_missing_activity": 0,
        "single_stream_ids_for_semantic_activity": c["streams"],
        "gate_up_overlap_observed_count": 0,
        "window_overlap_count": c["overlap_count"],
        "descriptive_outlier_rule": "within each decode and metric: deviation > max(6*1.4826*MAD, 10% of median, 2000 ns); descriptive only",
        "descriptive_outlier_windows": c["outlier_windows"],
        "decode_step_drift": c["decode_drift"],
        "gpu_used_by_consumer": False,
        "cuda_initialized_by_consumer": False,
        "gpu_lock_used_by_consumer": False,
        "lane4_partial_accessed": False,
    }
    dump_json(out / "FFN_TIMELINE_CONSUMER_VALIDATION.json", validation)

    write_tsv(out / "FFN_WALL_UNION.tsv", c["wall_output"], ["record_type", "decode_step", "layer", "start_ns", "end_ns", "duration_ns", "union_contribution_ns", "overlaps_previous", "window_count"])
    stage_fields = ["record_type", "decode_step", "layer", "window_count", "start_ns", "end_ns", "window_ns", "stage_sum_ns"]
    stage_fields += [f"{stage}_ns" for stage in STAGES] + [f"{gap}_ns" for gap in GAPS] + ["unattributed_ns"]
    stage_fields += ["window_median_ns", "stage_sum_median_ns"] + [f"{stage}_median_ns" for stage in STAGES] + [f"{gap}_median_ns" for gap in GAPS] + ["unattributed_median_ns", "anomaly_flags"]
    write_tsv(out / "FFN_STAGE_DECOMPOSITION.tsv", c["stage_output"], stage_fields)
    write_tsv(out / "FFN_PHYSICAL_HANDOFF_DATAFLOW.tsv", c["dataflow"], ["tensor", "producer", "consumers", "shape", "dtype", "logical_bytes", "global_tensor", "alias_or_view", "writes_within_ffn", "reads_within_ffn", "cross_operator_handoff", "counted_handoff_bytes_per_window", "authority"])

    f0 = {
        "schema_version": 2,
        "status": "WHOLE_FFN_ZERO_COST_HARD_CEILING",
        "decode_gpu_wall_ns": c["decode_wall_ns"],
        "ffn_window_union_ns": c["union_ns"],
        "ffn_window_overlap_count": c["overlap_count"],
        "legal_ffn_wall_fraction": c["legal_fraction"],
        "historical_module_duration_sum_fraction": HISTORICAL_MODULE_FRACTION,
        "historical_scope": "run-aligned stable D1-D3 additive gate/up/down CUDA-event module-duration share",
        "legal_scope": "single accepted formal D0-D3 GPU timeline; union of 112 producer-start to final-down-completion windows",
        "historical_authority_sha256": c["authority"]["historical_authority_sha256"],
        "absolute_difference_percentage_points": 100.0 * (HISTORICAL_MODULE_FRACTION - c["legal_fraction"]),
        "historical_to_legal_ratio": HISTORICAL_MODULE_FRACTION / c["legal_fraction"],
        "legal_to_historical_ratio": c["legal_fraction"] / HISTORICAL_MODULE_FRACTION,
        "relative_overstatement_vs_legal": HISTORICAL_MODULE_FRACTION / c["legal_fraction"] - 1.0,
        "whole_ffn_zero_cost_speedup": 1.0 / (1.0 - c["legal_fraction"]),
        "interpretation": "The historical value is an additive CUDA-event projection-module share, not a non-double-counted producer-to-final-consumer wall union. The numeric gap is reported, but it is not attributed solely to overlap because phase scope and measurement construction differ.",
        "handoff_specific": False,
    }
    dump_json(out / "FFN_F0_CEILING.json", f0)

    elementwise_fraction_local = c["elementwise_ns"] / c["union_ns"]
    elementwise_fraction_decode = c["elementwise_ns"] / c["decode_wall_ns"]
    f1 = {
        "schema_version": 2,
        "status": "MATERIALIZATION_TIME_CEILING_NOT_IDENTIFIABLE",
        "decision": "F1_STOP_SMALL_OR_UNIDENTIFIABLE",
        "explicit_elementwise_zero_ceiling": {
            "label": "EXPLICIT_ELEMENTWISE_ZERO_CEILING",
            "activation_plus_multiply_ns": c["elementwise_ns"],
            "local_ffn_time_reduction_fraction": elementwise_fraction_local,
            "local_ffn_speedup": c["union_ns"] / (c["union_ns"] - c["elementwise_ns"]),
            "whole_decode_time_reduction_fraction": elementwise_fraction_decode,
            "whole_decode_speedup": c["decode_wall_ns"] / (c["decode_wall_ns"] - c["elementwise_ns"]),
            "not_full_materialization_ceiling": True,
        },
        "handoff_traffic_bound": {
            "intermediate_tensor_count_per_window": 4,
            "logical_tensor_bytes_each": 37_888,
            "logical_writes_per_window": 4,
            "logical_reads_per_window": 4,
            "logical_bytes_per_window": c["handoff_bytes_per_window"],
            "window_count": 112,
            "logical_bytes_all_windows": c["handoff_bytes_all"],
            "logical_mib_all_windows": c["handoff_bytes_all"] / (1024 * 1024),
            "excludes": ["hidden shared input", "down output consumed outside bound", "AWQ GEMM internal scratch and reduction"],
            "is_not_dram_bytes": True,
        },
        "time_conversion": "UNKNOWN",
        "reason_time_unknown": "No accepted authority isolates handoff traffic on the critical path or maps logical intermediate bytes to elapsed time; cache residency, overlap, allocation, and synchronization prevent a bandwidth-only conversion.",
    }
    dump_json(out / "FFN_F1_MATERIALIZATION_BOUND.json", f1)

    f2a_fraction = c["f2a_saving_ns"] / c["decode_wall_ns"]
    f2a = {
        "schema_version": 2,
        "status": "PERFECT_GATE_UP_CONCURRENCY_NO_CONTENTION_ORACLE",
        "decision": "F2A_QUALIFIED_FOR_NATIVE_CONCURRENCY_DIAGNOSTIC",
        "current_runtime": {"semantic_cuda_stream_ids": c["streams"], "gate_up_nonoverlap_windows": 112, "gate_up_overlap_windows": 0, "stage_order": ["gate", "activation", "up", "multiply", "down"]},
        "formula": {"producer_ready": "max(T_gate + T_activation, T_up)", "ideal_stage": "producer_ready + T_multiply + T_down", "gap_preserving_saving": "min(T_gate + T_activation, T_up)"},
        "gap_preserving_oracle": {
            "saving_ns": c["f2a_saving_ns"],
            "saving_ms": c["f2a_saving_ns"] / 1e6,
            "local_ffn_time_reduction_fraction": c["f2a_saving_ns"] / c["union_ns"],
            "local_ffn_speedup": c["union_ns"] / (c["union_ns"] - c["f2a_saving_ns"]),
            "whole_decode_time_reduction_fraction": f2a_fraction,
            "whole_decode_speedup": c["decode_wall_ns"] / (c["decode_wall_ns"] - c["f2a_saving_ns"]),
            "preserved_non_target_gap_ns": sum(row["unattributed_ns"] for row in c["records"]),
        },
        "gap_elided_reference_not_admission": {
            "saving_ns": c["gap_elided_saving_ns"],
            "whole_decode_speedup": c["decode_wall_ns"] / (c["decode_wall_ns"] - c["gap_elided_saving_ns"]),
            "warning": "removes every within-window launch gap and therefore is not the F2A admission value",
        },
        "source_feasibility": {
            "two_stream_possible_without_kernel_change": True,
            "kernel_implementation_unchanged": True,
            "quantization_unchanged": True,
            "tensor_layout_unchanged": True,
            "numerical_dag_unchanged": True,
            "required_dependencies": ["both producer streams wait for hidden-ready event", "activation waits for gate", "multiply waits for activation and up", "down follows multiply", "cross-stream tensor lifetimes recorded"],
        },
        "admission_threshold_whole_decode_saving_fraction": 0.05,
        "admission_threshold_pass": f2a_fraction >= 0.05,
        "limitations": ["not a claim that CUDA streams realize the oracle", "not materialization elimination", "not new hardware", "no-contention assumption ignores resource and bandwidth interference"],
    }
    dump_json(out / "FFN_F2A_GATE_UP_CONCURRENCY_CEILING.json", f2a)

    f2b = {
        "schema_version": 2,
        "status": "TILE_PIPELINE_ORACLE_NOT_WELL_DEFINED",
        "decision": "F2B_REQUIRES_DEPENDENCY_GRANULARITY_EVIDENCE",
        "product": {"shape": [1, 1, 18_944], "dtype": "FP16", "bytes": 37_888, "production_dimension": "contiguous K/intermediate dimension", "current_producer": "one whole-tensor vectorized multiply kernel", "tile_ready_signal_in_authority": False},
        "down_projection": {"M": 1, "K": 18_944, "N": 3_584, "current_launch_dependency": "same-stream launch after complete multiply kernel", "actual_kernel_facts": c["role_kernel_facts"].get("down_proj", []), "internal_partial_accumulation": "EVIDENCE_PRESENT_GEMM_PLUS_REDUCE", "exact_split_k_factor": "UNKNOWN", "internal_partial_accumulation_is_not_cross_operator_readiness": True},
        "missing_for_legal_tile_dag": ["mapping from multiply output K chunks to down consumer CTA/chunk", "per-chunk memory visibility and dependency primitive", "layout-compatible chunk interface for current W4 kernel", "partial-output ownership and reduction order", "sync/scratch/launch cost"],
        "changes_required_by_hypothetical_pipeline": ["split or persistent multiply producer", "chunk-aware down launch/CTA schedule", "partial sums across K chunks", "new synchronization", "possibly additional scratch or relayout"],
        "perfect_tile_pipeline_ceiling": None,
        "max_producer_down_formula_legal": False,
        "literature_boundary": "LR10 records Kitsune queues, VTC virtual tensors, ComFuse staged fusion, and Rubin tile-ready triggering as neighbors; tile-ready triggering alone is not a new contribution.",
    }
    dump_json(out / "FFN_F2B_TILE_PIPELINE_ANALYSIS.json", f2b)

    baseline = f"""# FFN strong software baseline audit

## Current accepted runtime

All 560 semantic activities in the formal trace execute on CUDA stream `{c['streams'][0]}`. Every one of the 112 layer×decode windows follows gate → SiLU → up → multiply → down, and gate/up overlap is zero in all 112 windows. The accepted source performs these calls synchronously in that order; gate/up are logically independent siblings sharing `hidden`, but the current strong `WQLinear_GEMM` runtime serializes them.

## Minimal strong software baseline

A two-stream baseline is source-feasible without changing W4 kernels, quantization, tensor layout, or the numerical DAG. Both streams first wait for the original stream's hidden-ready event. One stream executes gate then SiLU; the other executes up. The original stream waits for both branch events before the unchanged multiply and down projection. Cross-stream tensor lifetimes must be recorded. Every run must retain the four generated tokens and all 336 projection input/output hashes and shapes.

This is only a feasibility result. Two W4 GEMMs may compete for SM, register, L2, and DRAM resources, so real overlap or speedup is not assumed. The accepted gap-preserving no-contention ceiling is `{c['f2a_saving_ns']/1e6:.6f}` ms, not a prediction.

## Related-work boundary

LR10 (blob `{LR10_BLOB}`, SHA256 `{c['authority']['lr10_sha256']}`) separates generic fusion, sibling-operator concurrency, cross-tile handoff, and layout-preserving pipelines. Kitsune provides queue-based spatial dataflow, VTC virtualizes mapped tensors but can hurt the compute kernel, ComFuse exposes fill/drain and stage-balance limits, and NVIDIA's Rubin description already discusses tile-ready producer/consumer triggers. These neighbors prevent claiming either “fusion” or “tile-ready” as novel by name alone; they do not eliminate the value of measuring the exact unchanged-kernel two-stream baseline first.
"""
    (out / "FFN_STRONG_SOFTWARE_BASELINE_AUDIT.md").write_text(baseline, encoding="utf-8")

    qualified = f2a["admission_threshold_pass"] and f2a["current_runtime"]["gate_up_overlap_windows"] == 0 and f2a["source_feasibility"]["two_stream_possible_without_kernel_change"]
    decision = {
        "schema_version": 2,
        "status": "PASS",
        "F0": "LEGAL_FFN_WALL_UNION_RECOVERED",
        "F1": f1["decision"],
        "F2A": f2a["decision"] if qualified else "F2A_STOP_SMALL_HEADROOM",
        "F2B": f2b["decision"],
        "legal_ffn_wall_fraction": c["legal_fraction"],
        "whole_ffn_zero_cost_speedup": f0["whole_ffn_zero_cost_speedup"],
        "explicit_elementwise_zero_whole_decode_fraction": elementwise_fraction_decode,
        "f2a_whole_decode_ideal_saving_fraction": f2a_fraction,
        "f2a_whole_decode_ideal_speedup": f2a["gap_preserving_oracle"]["whole_decode_speedup"],
        "lane7_native_contract_emitted": qualified,
        "gpu_used": False,
        "cuda_initialized": False,
        "lane4_partial_accessed": False,
        "splitk_grouped_branch_reopened": False,
    }
    dump_json(out / "FINAL_DECISION.json", decision)

    if qualified:
        contract = {
            "schema_version": 1,
            "status": "QUALIFIED_FOR_NATIVE_CONCURRENCY_DIAGNOSTIC",
            "execution": "NOT_EXECUTED_BY_LANE6",
            "purpose": "MINIMAL_STRONG_SOFTWARE_BASELINE_ONLY",
            "authority": {"timeline_producer_commit": PRODUCER, "timeline_producer_tree": PRODUCER_TREE, "accepted_scientific_contract_commit": "08f38d7163da95e895aaba10d72231a6d350dfe2", "accepted_scenario": "Qwen2.5-7B-Instruct-AWQ natural CONTROL_GUD84 B1/T2048/D0-D3"},
            "oracle_basis": {"label": "PERFECT_GATE_UP_CONCURRENCY_NO_CONTENTION_ORACLE", "saving_ns": c["f2a_saving_ns"], "whole_decode_saving_fraction": f2a_fraction, "whole_decode_speedup": f2a["gap_preserving_oracle"]["whole_decode_speedup"]},
            "B0": {"name": "CURRENT_SINGLE_STREAM_STRONG_RUNTIME", "implementation": "accepted runner/runtime unchanged"},
            "B1": {"name": "TWO_STREAM_GATE_UP_STRONG_BASELINE", "allowed_change": "scheduling/dependency events only", "gate_branch": "gate_proj then SiLU on gate stream", "up_branch": "up_proj on independent up stream", "join": "original stream waits for both branch completion events before multiply", "down": "unchanged after multiply", "cross_stream_lifetime": "record_stream/event-safe lifetime required"},
            "forbidden_changes": ["W4 kernel", "quantization", "tensor layout", "numerical semantics", "down kernel", "torch.compile", "new fused kernel", "NCU in first step", "new model/input/shape", "SASS", "NVBit", "Accel-Sim"],
            "correctness": {"generated_tokens": [23578, 11, 323, 3950], "projection_occurrences_each_run": 336, "require_input_output_hash_and_shape_identity": True, "require_call_order_identity": True},
            "measurement": {
                "primary_endpoint": "native CUDA-event complete natural D0-D3 wall time",
                "formal_order": "12 complete ABBA blocks: B0,B1,B1,B0",
                "fresh_process_per_sample": True,
                "samples": {"B0": 24, "B1": 24, "total": 48},
                "bootstrap": {"unit": "complete ABBA block", "resamples": 1000, "seed": 20261001},
                "timeline_canary": "one lightweight NSYS cuda,nvtx run for B0 and one for B1, excluded from native timing inference",
                "required_timeline_checks": ["actual gate/up GPU overlap", "gate kernel duration under overlap", "up kernel duration under overlap", "whole-decode realization fraction of oracle"],
                "gpu_wall_budget_minutes": 8,
            },
            "validation_target_frozen_before_results": {"primary": "complete D0-D3 wall over all layers", "held_out_validation": "D3 whole-step wall plus layers 14-27 gate/up overlap and kernel-duration response", "no_parameter_change_before_validation": True, "no_extra_gpu_run_for_validation": True},
            "gpu_lock": {"required": True, "path": "/data/c16/locks/c16_gpu_campaign.lock", "single_outer_lock": True, "release_receipt_required": True},
            "interpretation": {"software_opportunity_if": "B1 CI is positive and realizes at least 50% of oracle time reduction", "contention_diagnostic_if": "B1 shows overlap but little wall benefit or inflated kernel durations", "hardware_followup": "NOT_AUTOMATIC"},
            "stop_conditions": ["any identity/hash/shape/token mismatch", "B1 changes any kernel name/grid/block sequence beyond scheduling order", "no legal event dependency closure", "memory-lifetime warning or race", "GPU lock unavailable for 45 minutes", "8-minute GPU budget exceeded", "request expands beyond B0/B1 or adds NCU"],
        }
        dump_json(out / "LANE7_FFN_GATE_UP_CONCURRENCY_NATIVE_CONTRACT.json", contract)

    names = [path.name for path in out.iterdir() if path.is_file() and path.name != "SHA256SUMS"]
    sums = "".join(f"{sha256((out / name).read_bytes())}  {name}\n" for name in sorted(names))
    (out / "SHA256SUMS").write_text(sums, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[3]
    if args.check:
        compute(repo)
        return
    build(repo, args.output_dir or repo / PACK_OUT)


if __name__ == "__main__":
    main()
