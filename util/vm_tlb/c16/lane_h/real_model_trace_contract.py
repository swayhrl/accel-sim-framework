#!/usr/bin/env python3
"""Admission gate for the first real C16 model trace.

Admission creates only a ``REAL_TRACE_PIPELINE_CANARY`` receipt.  It does not
produce cross-model findings, fingerprints, or performance conclusions.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any


INPUT_SCHEMA = "C16_REAL_MODEL_TRACE_INPUT_V1"
OUTPUT_SCHEMA = "C16_REAL_TRACE_PIPELINE_CANARY_V1"
REAL_TRACE_KIND = "REAL_MODEL_TRACE"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


class AdmissionError(ValueError):
    """The trace lacks one of the mandatory real-model identity closures."""


def _string(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise AdmissionError(f"missing/nonempty required field: {key}")
    return value.strip()


def _sha(mapping: dict[str, Any], key: str) -> str:
    value = _string(mapping, key).lower()
    if not SHA256_RE.fullmatch(value):
        raise AdmissionError(f"{key} must be a SHA-256 hex digest")
    return value


def _int(mapping: dict[str, Any], key: str) -> int:
    value = mapping.get(key)
    if isinstance(value, bool):
        raise AdmissionError(f"{key} must be a nonnegative integer")
    try:
        result = int(value)
    except (TypeError, ValueError) as error:
        raise AdmissionError(f"{key} must be a nonnegative integer") from error
    if result < 0:
        raise AdmissionError(f"{key} must be a nonnegative integer")
    return result


def _load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AdmissionError(f"cannot read admission input {path}: {error}") from error
    if not isinstance(payload, dict) or payload.get("schema_version") != INPUT_SCHEMA:
        raise AdmissionError(f"expected schema_version={INPUT_SCHEMA}")
    return payload


def validate(payload: dict[str, Any], expected_g_commit: str | None = None) -> dict[str, Any]:
    if payload.get("trace_kind") != REAL_TRACE_KIND or payload.get("scientific_model_evidence") is not True:
        raise AdmissionError("only a declared REAL_MODEL_TRACE with scientific_model_evidence=true may be admitted")
    if payload.get("terminal_status") != "COMPLETE":
        raise AdmissionError("terminal_status must be COMPLETE")
    if payload.get("fixture_label") is not None or payload.get("fixture") is True:
        raise AdmissionError("fixture-labelled input can never enter the real-model pipeline")
    producer = payload.get("producer")
    identity = payload.get("identity")
    raw_artifacts = payload.get("raw_artifacts")
    if not isinstance(producer, dict) or not isinstance(identity, dict) or not isinstance(raw_artifacts, list) or not raw_artifacts:
        raise AdmissionError("input requires producer, identity, and nonempty raw_artifacts")
    g_commit = _string(producer, "g_producer_commit").lower()
    if not COMMIT_RE.fullmatch(g_commit):
        raise AdmissionError("producer.g_producer_commit must be an exact 40-hex Git commit")
    if expected_g_commit is not None and g_commit != expected_g_commit.lower():
        raise AdmissionError(f"producer G commit mismatch: expected {expected_g_commit}, got {g_commit}")
    tool = {
        "g_producer_commit": g_commit,
        "nvbit18_tool_sha256": _sha(producer, "nvbit18_tool_sha256"),
        "c16_tracer_sha256": _sha(producer, "c16_tracer_sha256"),
    }
    model_identity = {
        "model": _string(identity, "model"),
        "model_revision": _string(identity, "model_revision"),
        "package": _string(identity, "package"),
        "package_revision": _string(identity, "package_revision"),
        "scenario": _string(identity, "scenario"),
        "scenario_input_sha256": _sha(identity, "scenario_input_sha256"),
    }
    normalized_artifacts: list[dict[str, Any]] = []
    for ordinal, artifact in enumerate(raw_artifacts):
        if not isinstance(artifact, dict):
            raise AdmissionError("each raw_artifact must be an object")
        if artifact.get("remote_local_sha256_closed") is not True:
            raise AdmissionError(f"raw_artifacts[{ordinal}] lacks remote/local SHA closure")
        remote_sha = _sha(artifact, "remote_sha256")
        local_sha = _sha(artifact, "local_sha256")
        remote_size = _int(artifact, "remote_size_bytes")
        local_size = _int(artifact, "local_size_bytes")
        if remote_sha != local_sha or remote_size != local_size:
            raise AdmissionError(f"raw_artifacts[{ordinal}] remote/local size or SHA does not close")
        normalized_artifacts.append({
            "ordinal": ordinal,
            "raw_path": _string(artifact, "raw_path"),
            "remote_path": _string(artifact, "remote_path"),
            "size_bytes": remote_size,
            "sha256": remote_sha,
            "remote_local_sha256_closed": True,
        })
    return {"producer": tool, "identity": model_identity, "raw_artifacts": normalized_artifacts}


def _write_new(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, sort_keys=True)
        output.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="G-produced real-model trace identity/closure manifest")
    parser.add_argument("--output", type=Path, required=True, help="fresh REAL_TRACE_PIPELINE_CANARY receipt")
    parser.add_argument("--expected-g-producer-commit", help="optional exact G commit pin for this handoff")
    args = parser.parse_args()
    try:
        expected = args.expected_g_producer_commit.lower() if args.expected_g_producer_commit else None
        if expected is not None and not COMMIT_RE.fullmatch(expected):
            raise AdmissionError("--expected-g-producer-commit must be an exact 40-hex Git commit")
        admitted = validate(_load(args.input), expected)
        payload = {
            "schema_version": OUTPUT_SCHEMA,
            "status": "ADMITTED_REAL_TRACE_PIPELINE_CANARY",
            "pipeline_mode": "REAL_TRACE_PIPELINE_CANARY",
            "input_path": str(args.input.resolve()),
            "admission": admitted,
            "scientific_model_evidence": True,
            "cross_model_scientific_conclusions_permitted": False,
            "allowed_next_steps": [
                "integrity verification",
                "storage estimate",
                "single-trace parser canary",
                "compact-artifact registration",
            ],
            "forbidden_next_steps": [
                "cross-model scientific conclusion",
                "family-level generalization",
                "causal claim",
            ],
            "created_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }
        _write_new(args.output, payload)
    except (AdmissionError, OSError, ValueError) as error:
        raise SystemExit(f"FAIL c16-real-model-trace-admission: {error}") from error
    print(f"PASS c16-real-model-trace-admission output={args.output}")


if __name__ == "__main__":
    main()
