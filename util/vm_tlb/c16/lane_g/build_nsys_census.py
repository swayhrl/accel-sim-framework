#!/usr/bin/env python3
"""Build a raw-free C16 native catalog from independently validated nsys SQLite exports."""
from __future__ import annotations

import argparse
import csv
import json
import os
import sqlite3
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from c16_native_common import ContractError, atomic_json, sha256_file
from native_catalog import CATALOG_FIELDS, COVERAGE_FIELDS, HEAVY_TAIL_FIELDS, IMPLEMENTATION_FIELDS, SEMANTIC_FIELDS


BASELINE_FIELDS = (
    "run_id", "deployment_id", "scenario_id", "input_hash", "measurement_kind", "measurement_index",
    "profiler_mode", "output_checksum", "duration_ms", "peak_allocated_bytes", "peak_reserved_bytes",
    "evidence_tier", "status",
)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON root is not an object: {path}")
    return value


def write_rows(path: Path, fields: tuple[str, ...], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def marker_intervals(connection: sqlite3.Connection) -> tuple[list[tuple[int, int]], list[tuple[int, int, str]], list[tuple[int, int, int]]]:
    rows = connection.execute("SELECT start, end, text FROM NVTX_EVENTS WHERE end IS NOT NULL AND text LIKE 'C16_%' ORDER BY start").fetchall()
    full: list[tuple[int, int]] = []
    phases: list[tuple[int, int, str]] = []
    steps: list[tuple[int, int, int]] = []
    for start, end, text in rows:
        if not isinstance(start, int) or not isinstance(end, int) or end < start or not isinstance(text, str):
            continue
        if text == "C16_NATIVE_FULL_FORWARD":
            full.append((start, end))
        elif text == "C16_PHASE_PREFILL":
            phases.append((start, end, "PREFILL"))
        elif text == "C16_PHASE_DECODE":
            phases.append((start, end, "DECODE"))
        elif text.startswith("C16_DECODE_STEP_"):
            try:
                steps.append((start, end, int(text.rsplit("_", 1)[1])))
            except ValueError:
                continue
    if not full or not any(kind == "PREFILL" for _, _, kind in phases) or not any(kind == "DECODE" for _, _, kind in phases):
        raise ContractError("Nsight export lacks required C16 full/prefill/decode NVTX intervals")
    return full, phases, steps


def contains(intervals: Iterable[tuple[int, int]], point: int) -> bool:
    return any(start <= point <= end for start, end in intervals)


def classify(midpoint: int, phases: list[tuple[int, int, str]], steps: list[tuple[int, int, int]]) -> tuple[str, str]:
    for start, end, step in steps:
        if start <= midpoint <= end:
            return "DECODE", f"STEP_{step}"
    for start, end, phase in phases:
        if start <= midpoint <= end:
            return phase, "NOT_APPLICABLE" if phase == "PREFILL" else "UNBINNED"
    return "FULL_FORWARD_UNATTRIBUTED", "NOT_APPLICABLE"


def catalog_rows(source: dict[str, Any]) -> Iterable[dict[str, Any]]:
    profile = read_json(Path(source["profile_receipt"]))
    runner = read_json(Path(source["runner_receipt"]))
    binding = read_json(Path(source["binding_receipt"]))
    validation = read_json(Path(source["validation_receipt"]))
    if validation.get("status") != "G1_EXPORT_VALIDATED_PASS" or validation.get("scientific_eligible") is not True:
        raise ContractError("refusing to catalog a source without independent G1 export validation")
    if profile.get("identity") != runner.get("identity") or profile.get("identity") != validation.get("identity"):
        raise ContractError("profile/runner/validation identity mismatch")
    checks = runner.get("checks", {})
    if checks.get("package_id") != binding.get("package_id") or checks.get("package_fixed_commit") != binding.get("package_fixed_commit"):
        raise ContractError("catalog source package identity mismatch")
    identity = profile["identity"]
    scenario = binding.get("scenario", {})
    shape_key = f"B{scenario.get('batch_size')}_T{scenario.get('prefill_tokens')}_D{scenario.get('decode_tokens')}"
    connection = sqlite3.connect(source["sqlite"])
    try:
        full, phases, steps = marker_intervals(connection)
        query = """
            SELECT k.rowid, k.start, k.end, k.deviceId, k.contextId, k.streamId, k.correlationId,
                   k.gridX, k.gridY, k.gridZ, k.blockX, k.blockY, k.blockZ, s.value
            FROM CUPTI_ACTIVITY_KIND_KERNEL k
            LEFT JOIN StringIds s ON s.id = k.demangledName
            ORDER BY k.start, k.rowid
        """
        for ordinal, (rowid, start, end, device, context, stream, correlation, gx, gy, gz, bx, by, bz, name) in enumerate(connection.execute(query), start=1):
            midpoint = (int(start) + int(end)) // 2
            if not contains(full, midpoint):
                continue
            phase, decode_step = classify(midpoint, phases, steps)
            kernel_name = name if isinstance(name, str) and name else "[UNRESOLVED_KERNEL_NAME]"
            yield {
                "run_id": identity["run_id"], "deployment_id": identity["deployment_id"], "model_id": identity["model_id"],
                "model_revision": identity["model_revision"], "tokenizer_revision": identity["tokenizer_revision"],
                "scenario_id": identity["scenario_id"], "input_hash": identity["input_hash"], "phase": phase,
                "decode_step_bin": decode_step, "device": f"cuda:{device}", "context": f"CUDA_CONTEXT_{context}",
                "stream": f"CUDA_STREAM_{stream}", "correlation_id": f"CUDA_CORRELATION_{correlation}",
                "launch_ordinal": ordinal, "kernel_name": kernel_name, "implementation_key": identity["implementation_key"],
                "grid": f"{gx}x{gy}x{gz}", "block": f"{bx}x{by}x{bz}", "start_ns": int(start), "end_ns": int(end),
                "duration_ns": int(end) - int(start), "operator_class": "UNKNOWN", "layer_id": "UNKNOWN",
                "shape_key": shape_key, "dtype_key": identity["dtype"], "semantic_evidence": "NSYS_KERNEL_NAME_PLUS_NVTX_PHASE",
                "mapping_status": "UNKNOWN_OPERATOR_LAYER", "evidence_tier": "NATIVE_PROFILED",
            }
    finally:
        connection.close()


def baseline_rows(paths: list[Path]) -> Iterable[dict[str, Any]]:
    for path in paths:
        receipt = read_json(path)
        if receipt.get("execution_mode") != "NATIVE_GPU" or receipt.get("scientific_eligible") is not True:
            raise ContractError(f"baseline receipt is not native: {path}")
        identity, artifacts = receipt["identity"], receipt["artifacts"]
        for index, duration in enumerate(artifacts["duration_ms"]):
            yield {
                "run_id": identity["run_id"], "deployment_id": identity["deployment_id"], "scenario_id": identity["scenario_id"],
                "input_hash": identity["input_hash"], "measurement_kind": "MEASURE", "measurement_index": index,
                "profiler_mode": "UNPROFILED", "output_checksum": receipt["checks"]["output_checksum"], "duration_ms": duration,
                "peak_allocated_bytes": artifacts["peak_allocated_bytes"], "peak_reserved_bytes": artifacts["peak_reserved_bytes"],
                "evidence_tier": "NATIVE_BASELINE", "status": "COMPLETE",
            }


def derived_tables(output_dir: Path) -> dict[str, int]:
    catalog = output_dir / "KERNEL_CATALOG.tsv"
    semantic_seen: set[tuple[str, str, str, str]] = set()
    semantic: list[dict[str, Any]] = []
    coverage: dict[tuple[str, str, str], list[int]] = defaultdict(lambda: [0, 0])
    heavy_candidates: list[dict[str, str]] = []
    implementation: dict[tuple[str, str, str], dict[str, Any]] = {}
    count = 0
    with catalog.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            count += 1
            key = (row["run_id"], row["scenario_id"], row["kernel_name"], row["phase"])
            if key not in semantic_seen:
                semantic_seen.add(key)
                semantic.append({field: row[field] for field in SEMANTIC_FIELDS})
            ckey = (row["run_id"], row["scenario_id"], row["phase"])
            coverage[ckey][0] += int(row["duration_ns"])
            heavy_candidates.append(row)
            ikey = (row["run_id"], row["deployment_id"], row["scenario_id"])
            implementation.setdefault(ikey, {
                "run_id": row["run_id"], "deployment_id": row["deployment_id"], "scenario_id": row["scenario_id"],
                "attention_backend": "TRANSFORMERS_CONFIG:sdpa (native receipt)",
                "runtime_kv_representation": "UNRESOLVED_NO_DIRECT_RUNTIME_LAYOUT_EVIDENCE",
                "quantization_runtime": "NONE (immutable deployment identity)", "compile_state": "EAGER_UNCOMPILED (native receipt)",
                "logits_policy": "GREEDY_ARGMAX_CACHE_CORRECT_RUNNER", "evidence": "native receipt plus nsys export; no operator/layer inference",
                "status": "PARTIAL_DIRECT_RUNTIME_EVIDENCE",
            })
    write_rows(output_dir / "KERNEL_SEMANTIC_MAP.tsv", SEMANTIC_FIELDS, semantic)
    coverage_rows = []
    for (run_id, scenario_id, phase), (total, mapped) in sorted(coverage.items()):
        coverage_rows.append({"run_id": run_id, "deployment_id": heavy_candidates[0]["deployment_id"], "scenario_id": scenario_id, "phase": phase, "total_gpu_duration_ns": total, "mapped_gpu_duration_ns": mapped, "mapped_gpu_time_fraction": 0.0 if total else 0.0, "status": "SEMANTIC_OPERATOR_LAYER_GAP"})
    write_rows(output_dir / "SEMANTIC_COVERAGE.tsv", COVERAGE_FIELDS, coverage_rows)
    write_rows(output_dir / "RUNTIME_IMPLEMENTATION_AUDIT.tsv", IMPLEMENTATION_FIELDS, implementation.values())
    totals = {key: values[0] for key, values in coverage.items()}
    heavy = []
    for row in heavy_candidates:
        total = totals[(row["run_id"], row["scenario_id"], row["phase"])]
        if total and int(row["duration_ns"]) / total >= 0.01:
            heavy.append({"run_id": row["run_id"], "deployment_id": row["deployment_id"], "scenario_id": row["scenario_id"], "phase": row["phase"], "kernel_identity": "|".join((row["kernel_name"], row["grid"], row["block"], row["dtype_key"])), "duration_ns": row["duration_ns"], "phase_gpu_time_fraction": int(row["duration_ns"]) / total, "certainty_reason": "SINGLE_LAUNCH_AT_LEAST_ONE_PERCENT_PHASE_GPU_TIME", "status": "CANDIDATE_NOT_SELECTOR_FREEZE"})
    write_rows(output_dir / "HEAVY_TAIL_KERNELS.tsv", HEAVY_TAIL_FIELDS, heavy)
    return {"kernel_launch_rows": count, "semantic_rows": len(semantic), "heavy_tail_rows": len(heavy)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--baseline-receipt", type=Path, action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source_manifest = read_json(args.source_manifest)
    sources = source_manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ContractError("source manifest requires one or more validated nsys sources")
    for source in sources:
        if not isinstance(source, dict) or any(not isinstance(source.get(key), str) or not source[key] for key in ("sqlite", "raw_profile", "profile_receipt", "runner_receipt", "binding_receipt", "validation_receipt")):
            raise ContractError("source manifest has incomplete census inputs")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_rows(args.output_dir / "KERNEL_CATALOG.tsv", CATALOG_FIELDS, (row for source in sources for row in catalog_rows(source)))
    write_rows(args.output_dir / "NATIVE_BASELINE.tsv", BASELINE_FIELDS, baseline_rows(args.baseline_receipt))
    stats = derived_tables(args.output_dir)
    receipt = {
        "schema_version": "C16_G_NSYS_CENSUS_V1", "stage_id": "C16-2.2", "status": "COMPLETE_LIGHTWEIGHT_NSYS_CENSUS",
        "scientific_eligible": True, "raw_data_committed": False, "sources": [{key: {"path": value, "sha256": sha256_file(Path(value))} for key, value in source.items()} for source in sources],
        "baseline_receipts": [{"path": str(path), "sha256": sha256_file(path)} for path in args.baseline_receipt], "derived": stats,
        "semantic_scope": "operator/layer remain UNKNOWN without direct runtime evidence; name/NVTX provide phase-only context",
    }
    atomic_json(args.output_dir / "CENSUS_RECEIPT.json", receipt)
    print(f"PASS C16 raw-free nsys census catalog: {args.output_dir}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 raw-free nsys census catalog: {exc}", file=__import__("sys").stderr)
        raise SystemExit(2)
