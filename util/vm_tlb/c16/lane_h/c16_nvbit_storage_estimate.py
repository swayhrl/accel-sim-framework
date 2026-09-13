#!/usr/bin/env python3
"""Emit a storage-only estimate from a hash-closed C16 real-model canary.

Fixture input is allowed solely to exercise the schema.  It is conspicuously
marked and intentionally refuses to project a formal LLM campaign.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


INPUT_SCHEMA = "C16_NVBIT_STORAGE_CANARY_INPUT_V1"
OUTPUT_SCHEMA = "NVBIT_STORAGE_ESTIMATE_V1"
REAL_TRACE_KIND = "REAL_MODEL_TRACE"
FIXTURE_LABEL = "NVBIT18_PARSER_QUALIFICATION_FIXTURE_ONLY"
TARGET_BATCHES = (4, 8, 12, 24, 48)


class EstimateError(ValueError):
    """The canary cannot safely support a campaign storage estimate."""


def _int(value: Any, name: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool):
        raise EstimateError(f"{name} must be an integer")
    try:
        result = int(value)
    except (TypeError, ValueError) as error:
        raise EstimateError(f"{name} must be an integer") from error
    if result < minimum:
        raise EstimateError(f"{name} must be >= {minimum}")
    return result


def _optional_int(value: Any, name: str) -> int | None:
    return None if value is None else _int(value, name)


def _load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EstimateError(f"cannot read storage input {path}: {error}") from error
    if not isinstance(payload, dict) or payload.get("schema_version") != INPUT_SCHEMA:
        raise EstimateError(f"expected schema_version={INPUT_SCHEMA}")
    return payload


def _new_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, sort_keys=True)
        output.write("\n")


def _project(canary: dict[str, Any], batch: int, compressed_bytes: int | None) -> dict[str, Any]:
    source_batch = _int(canary.get("source_batch_size"), "canary.source_batch_size", minimum=1)
    multiplier = batch / source_batch
    raw = _int(canary.get("raw_bytes"), "canary.raw_bytes")
    records = _optional_int(canary.get("memory_record_count"), "canary.memory_record_count")
    return {
        "scale_assumption": "linear storage-only extrapolation from the admitted canary; not a performance or scientific model",
        "multiplier": multiplier,
        "raw_bytes": raw * multiplier,
        "compressed_bytes": compressed_bytes * multiplier if compressed_bytes is not None else None,
        "memory_record_count": records * multiplier if records is not None else None,
    }


def estimate(payload: dict[str, Any], output_parent: Path, *, allow_fixture_test: bool) -> dict[str, Any]:
    output_parent.mkdir(parents=True, exist_ok=True)
    canary = payload.get("canary")
    storage = payload.get("storage", {})
    if not isinstance(canary, dict) or not isinstance(storage, dict):
        raise EstimateError("input requires canary and storage objects")
    trace_kind = payload.get("trace_kind")
    scientific = payload.get("scientific_model_evidence")
    fixture = trace_kind == FIXTURE_LABEL or scientific is False
    real = trace_kind == REAL_TRACE_KIND and scientific is True
    if not real and not (fixture and allow_fixture_test):
        raise EstimateError(
            "formal storage estimates require trace_kind=REAL_MODEL_TRACE and scientific_model_evidence=true; "
            "fixture schema tests require --allow-fixture-test"
        )
    if real:
        admission = payload.get("admission")
        if not isinstance(admission, dict) or admission.get("status") != "ADMITTED_REAL_TRACE_PIPELINE_CANARY" or admission.get("pipeline_mode") != "REAL_TRACE_PIPELINE_CANARY":
            raise EstimateError("real-model storage estimate requires an ADMITTED_REAL_TRACE_PIPELINE_CANARY admission object")
    raw_bytes = _int(canary.get("raw_bytes"), "canary.raw_bytes")
    compressed_bytes = _optional_int(canary.get("compressed_bytes"), "canary.compressed_bytes")
    trace_file_count = _int(canary.get("trace_file_count"), "canary.trace_file_count")
    kernel_count = _int(canary.get("kernel_count"), "canary.kernel_count")
    memory_record_count = _optional_int(canary.get("memory_record_count"), "canary.memory_record_count")
    duration = _optional_int(canary.get("capture_duration_seconds"), "canary.capture_duration_seconds")
    ratio = (compressed_bytes / raw_bytes) if compressed_bytes is not None and raw_bytes else None
    bytes_per_record = (raw_bytes / memory_record_count) if memory_record_count else None
    current_free = shutil.disk_usage(output_parent).free
    before = _optional_int(storage.get("local_available_before_bytes"), "storage.local_available_before_bytes")
    if before is None:
        before = current_free
    base: dict[str, Any] = {
        "schema_version": OUTPUT_SCHEMA,
        "trace_kind": trace_kind,
        "fixture_label": FIXTURE_LABEL if fixture else None,
        "scientific_model_evidence": bool(scientific),
        "scientific_conclusion_evidence": False,
        "formal_llm_campaign_estimate": real,
        "canary_identity": payload.get("canary_identity", {}),
        "raw_bytes": raw_bytes,
        "compressed_bytes": compressed_bytes,
        "compression_ratio": ratio,
        "compression_ratio_compressed_over_raw": ratio,
        "trace_file_count": trace_file_count,
        "kernel_count": kernel_count,
        "memory_record_count": memory_record_count,
        "capture_duration": duration,
        "capture_duration_seconds": duration,
        "bytes_per_record": bytes_per_record,
        "local_available_before": before,
        "local_available_before_bytes": before,
        "local_available_after": current_free,
        "local_available_after_bytes": current_free,
    }
    if fixture:
        base.update({
            "projected_storage_B4": None,
            "projected_storage_B8": None,
            "projected_storage_B12": None,
            "projected_storage_B24": None,
            "projected_storage_B48": None,
            "safe_campaign_budget": None,
            "limitation": "Fixture bytes exercise only this script. They MUST NOT estimate a formal LLM campaign.",
        })
        return base
    projections = {f"projected_storage_B{batch}": _project(canary, batch, compressed_bytes) for batch in TARGET_BATCHES}
    source_batch = _int(canary.get("source_batch_size"), "canary.source_batch_size", minimum=1)
    # Retain raw + compressed and reserve a raw-sized scratch copy during parser work.
    retained_per_source = raw_bytes + (compressed_bytes or 0) + raw_bytes
    safety_reserve = max(10 * 1024**3, retained_per_source)
    usable = max(0, current_free - safety_reserve)
    safe_runs = usable // retained_per_source if retained_per_source else 0
    base.update(projections)
    base["safe_campaign_budget"] = {
        "available_after_bytes": current_free,
        "safety_reserve_bytes": safety_reserve,
        "per_source_batch_retained_plus_scratch_bytes": retained_per_source,
        "safe_parallel_source_batch_captures": safe_runs,
        "safe_parallel_batch_equivalent": safe_runs * source_batch,
        "rule": "budget reserves raw retention, optional compressed copy, and one raw-sized parser scratch copy",
    }
    base["limitation"] = "Storage planning only; it does not establish model behavior, performance, or scientific conclusions."
    return base


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="real-model canary metadata or fixture schema-test input")
    parser.add_argument("--output", type=Path, required=True, help="fresh NVBIT_STORAGE_ESTIMATE.json")
    parser.add_argument("--allow-fixture-test", action="store_true", help="permit fixture-only schema exercise without campaign projections")
    args = parser.parse_args()
    try:
        payload = estimate(_load(args.input), args.output.parent, allow_fixture_test=args.allow_fixture_test)
        _new_json(args.output, payload)
    except (EstimateError, OSError, ValueError) as error:
        raise SystemExit(f"FAIL c16-nvbit-storage-estimate: {error}") from error
    print(f"PASS c16-nvbit-storage-estimate output={args.output}")


if __name__ == "__main__":
    main()
