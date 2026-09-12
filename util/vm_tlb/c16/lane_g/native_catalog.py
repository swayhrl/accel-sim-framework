#!/usr/bin/env python3
"""Validate and publish a small C16 Wave-1 native catalog, never raw profiler data."""
from __future__ import annotations

import argparse
import csv
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file


WAVE1_FIELDS = ("deployment_id", "model_id", "deployment_variant", "wave", "catalog_status", "gap_reason")
CATALOG_FIELDS = (
    "run_id", "deployment_id", "model_id", "model_revision", "tokenizer_revision", "scenario_id", "input_hash", "phase", "decode_step_bin", "device", "context", "stream", "correlation_id", "launch_ordinal", "kernel_name", "implementation_key", "grid", "block", "start_ns", "end_ns", "duration_ns", "operator_class", "layer_id", "shape_key", "dtype_key", "semantic_evidence", "mapping_status", "evidence_tier",
)
BASELINE_FIELDS = ("run_id", "deployment_id", "scenario_id", "input_hash", "measurement_kind", "measurement_index", "profiler_mode", "output_checksum", "duration_ms", "peak_allocated_bytes", "peak_reserved_bytes", "evidence_tier", "status")
SEMANTIC_FIELDS = ("run_id", "deployment_id", "scenario_id", "kernel_name", "implementation_key", "operator_class", "layer_id", "shape_key", "dtype_key", "semantic_evidence", "mapping_status")
COVERAGE_FIELDS = ("run_id", "deployment_id", "scenario_id", "phase", "total_gpu_duration_ns", "mapped_gpu_duration_ns", "mapped_gpu_time_fraction", "status")
IMPLEMENTATION_FIELDS = ("run_id", "deployment_id", "scenario_id", "attention_backend", "runtime_kv_representation", "quantization_runtime", "compile_state", "logits_policy", "evidence", "status")
HEAVY_TAIL_FIELDS = ("run_id", "deployment_id", "scenario_id", "phase", "kernel_identity", "duration_ns", "phase_gpu_time_fraction", "certainty_reason", "status")
TABLES = {
    "KERNEL_CATALOG.tsv": CATALOG_FIELDS,
    "NATIVE_BASELINE.tsv": BASELINE_FIELDS,
    "KERNEL_SEMANTIC_MAP.tsv": SEMANTIC_FIELDS,
    "SEMANTIC_COVERAGE.tsv": COVERAGE_FIELDS,
    "RUNTIME_IMPLEMENTATION_AUDIT.tsv": IMPLEMENTATION_FIELDS,
    "HEAVY_TAIL_KERNELS.tsv": HEAVY_TAIL_FIELDS,
}


def read_tsv(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if tuple(reader.fieldnames or ()) != fields:
                raise ContractError(f"schema mismatch in {path.name}")
            return list(reader)
    except OSError as exc:
        raise ContractError(f"missing catalog table: {path}") from exc


def write_tsv(path: Path, fields: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def validate(catalog_dir: Path, wave1_path: Path) -> tuple[dict[str, list[dict[str, str]]], list[dict[str, str]]]:
    expected = read_tsv(wave1_path, WAVE1_FIELDS)
    if len(expected) != 4 or {row["wave"] for row in expected} != {"W1"} or len({row["deployment_id"] for row in expected}) != 4:
        raise ContractError("Wave-1 declaration must contain exactly four unique W1 deployments")
    if any(row["catalog_status"] not in {"COMPLETE", "GAP"} for row in expected):
        raise ContractError("Wave-1 deployment catalog status must be COMPLETE or GAP")
    tables = {name: read_tsv(catalog_dir / name, fields) for name, fields in TABLES.items()}
    complete = {row["deployment_id"] for row in expected if row["catalog_status"] == "COMPLETE"}
    for name, rows in tables.items():
        for row in rows:
            if row.get("deployment_id") not in complete:
                raise ContractError(f"{name} has a row for undeclared/incomplete deployment")
            if any("MOCK" in value or "FIXTURE" in value for value in row.values()):
                raise ContractError(f"{name} contains non-scientific fixture content")
    catalog_by_deployment = Counter(row["deployment_id"] for row in tables["KERNEL_CATALOG.tsv"])
    baseline_by_deployment = Counter(row["deployment_id"] for row in tables["NATIVE_BASELINE.tsv"] if row["measurement_kind"] == "MEASURE")
    for deployment in complete:
        if catalog_by_deployment[deployment] == 0:
            raise ContractError(f"complete deployment lacks kernel catalog: {deployment}")
        if baseline_by_deployment[deployment] < 3:
            raise ContractError(f"complete deployment lacks three retained native measures: {deployment}")
    for row in tables["NATIVE_BASELINE.tsv"]:
        if row["profiler_mode"] != "UNPROFILED" or row["evidence_tier"] != "NATIVE_BASELINE":
            raise ContractError("baseline table mixes profiled/fallback evidence")
    for row in tables["KERNEL_CATALOG.tsv"]:
        if row["evidence_tier"] != "NATIVE_PROFILED" or int(row["duration_ns"]) < 0 or int(row["end_ns"]) < int(row["start_ns"]):
            raise ContractError("kernel catalog has invalid native profile row")
    return tables, expected


def schema_markdown() -> str:
    return """# Wave-1 native catalog schema

`native_catalog.py` publishes only small, hash-listed TSV summaries after real G0/G1 runs. A Wave-1 declaration must contain exactly the four frozen deployments (Llama3.2-1B, Qwen2.5-0.5B, Qwen2.5-7B raw, Qwen2.5-7B AWQ), each `COMPLETE` or an explicit `GAP`.

For every `COMPLETE` deployment the validator requires at least three retained `UNPROFILED` `NATIVE_BASELINE` measurements and a `NATIVE_PROFILED` kernel catalog with closed model/tokenizer/input/run identity. Mock/fixture rows are rejected. Raw profiler databases and NVBit traces are never published by this tool.
"""


def publish(catalog_dir: Path, wave1_path: Path) -> dict[str, Any]:
    tables, expected = validate(catalog_dir, wave1_path)
    files = []
    for name in sorted(TABLES):
        path = catalog_dir / name
        files.append({"path": name, "sha256": sha256_file(path), "size_bytes": path.stat().st_size})
    complete = [row["deployment_id"] for row in expected if row["catalog_status"] == "COMPLETE"]
    gaps = [{"deployment_id": row["deployment_id"], "reason": row["gap_reason"]} for row in expected if row["catalog_status"] == "GAP"]
    manifest = {
        "schema_version": "C16_G_NATIVE_CATALOG_V1",
        "stage_id": "C16-2.6",
        "status": "WAVE1_NATIVE_CATALOG_COMPLETE" if not gaps else "WAVE1_NATIVE_CATALOG_PARTIAL_PUBLISHED",
        "scientific_evidence": "NATIVE_BASELINE_AND_PROFILED",
        "completed_deployments": complete,
        "deployment_gaps": gaps,
        "files": files,
        "raw_data_committed": False,
    }
    atomic_json(catalog_dir / "WAVE1_PUBLISH_MANIFEST.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog-dir", type=Path, required=True)
    parser.add_argument("--wave1-deployments", type=Path, required=True)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--write-schema", type=Path)
    args = parser.parse_args()
    if args.write_schema:
        args.write_schema.write_text(schema_markdown(), encoding="utf-8")
    if args.validate == args.publish:
        parser.error("choose exactly one of --validate or --publish")
    if args.publish:
        manifest = publish(args.catalog_dir, args.wave1_deployments)
        print(f"PASS C16 Wave-1 catalog publish: {manifest['status']}")
    else:
        validate(args.catalog_dir, args.wave1_deployments)
        print("PASS C16 Wave-1 catalog validation")


if __name__ == "__main__":
    try:
        main()
    except (ContractError, ValueError) as exc:
        print(f"FAIL C16 Wave-1 catalog: {exc}", file=__import__("sys").stderr)
        raise SystemExit(2)
