"""Final-contract table adapters; independent from Lane7/109 postprocessing."""
from __future__ import annotations

import csv
from collections import defaultdict
from math import isfinite
from pathlib import Path

from core import sample_statistics


def read_contract_tsv(path: str | Path, required_columns: list[str], key_columns: list[str]) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not set(required_columns) <= set(reader.fieldnames or []):
            raise ValueError(f"contract table columns missing: {path}")
        rows = list(reader)
    keys = [tuple(row[col] for col in key_columns) for row in rows]
    if len(keys) != len(set(keys)) or any(not all(key) for key in keys):
        raise ValueError(f"duplicate/missing contract table key: {path}")
    return rows


def verify_point_identity(point_rows: list[dict[str, str]], binding_rows: list[dict[str, str]], contract: dict, complete_points: set[str] | None = None) -> dict:
    """Exact frozen point/source/token pairing, independent of producer summary."""
    expected_points = contract["points"]
    selected = set(expected_points) if complete_points is None else complete_points
    if not selected <= set(expected_points):
        raise ValueError("partial point set includes forbidden point")
    expected_keys = {(point_id, source_id) for point_id in selected for source_id in expected_points[point_id]["source_ids"]}
    actual_keys = {(r["point_id"], r["source_text_id"]) for r in point_rows}
    if len(actual_keys) != len(point_rows) or actual_keys != expected_keys:
        raise ValueError("point/source matrix does not match final contract")
    binding = {(r["point_id"], r["source_text_id"]): r for r in binding_rows}
    if not expected_keys <= set(binding):
        raise ValueError("frozen token-binding matrix mismatch")
    for row in point_rows:
        point_id, source_id = row["point_id"], row["source_text_id"]
        spec = expected_points[point_id]
        frozen = binding[(point_id, source_id)]
        model = contract["model_runtime_identity"][spec["target"]]
        checks = {
            "target": spec["target"], "model_revision": model["revision"],
            "phase": spec["phase"], "batch_size": str(spec["batch"]),
            "prompt_tokens": str(spec["prompt_tokens_per_request"]),
            "source_utf8_sha256": frozen["source_utf8_sha256"],
            "tokenizer_revision": frozen["tokenizer_revision"],
            "token_ids_sha256": frozen["token_ids_sha256"],
            "token_id_file_sha256": frozen["token_id_file_sha256"],
            "vllm_source_commit": contract["model_runtime_identity"]["vllm_source_commit"],
        }
        for key, value in checks.items():
            if row.get(key) != value:
                raise ValueError(f"point identity mismatch {point_id}/{source_id}/{key}")
        if row.get("correctness_status") != "PASS":
            raise ValueError(f"point identity correctness failed {point_id}/{source_id}")
        expected_steps = spec.get("decode_steps", spec.get("decode_steps_per_request"))
        if expected_steps is not None and row.get("decode_steps") != str(expected_steps):
            raise ValueError(f"decode-step identity mismatch {point_id}/{source_id}")
    return {"status": "PASS", "point_count": len(selected), "point_source_rows": len(point_rows)}


def verify_frozen_token_bindings(binding_rows: list[dict[str, str]], receipt_rows: list[dict[str, str]], contract: dict) -> dict:
    """Check final-contract point bindings against accepted asset/input receipt."""
    lookup = {(r["model_key"], r["source_text_id"]): r for r in receipt_rows}
    if len(lookup) != len(receipt_rows):
        raise ValueError("duplicate accepted tokenization receipt")
    expected = {(point_id, source_id) for point_id, spec in contract["points"].items() for source_id in spec["source_ids"]}
    actual = {(r["point_id"], r["source_text_id"]) for r in binding_rows}
    if actual != expected or len(binding_rows) != len(actual):
        raise ValueError("final-contract token binding point matrix mismatch")
    checked = 0
    for row in binding_rows:
        model_key = contract["points"][row["point_id"]]["target"]
        accepted = lookup.get((model_key, row["source_text_id"]))
        if accepted is None or row["model_key"] != model_key:
            raise ValueError("token receipt model/source mismatch")
        fields = ("source_utf8_sha256", "tokenizer_revision", "prompt_token_count",
                  "token_ids_sha256", "token_id_file_sha256", "token_ids_relative_path")
        for field in fields:
            if row[field] != accepted[field]:
                raise ValueError(f"token receipt drift: {row['point_id']}/{row['source_text_id']}/{field}")
        if row["prompt_token_count"] != "512":
            raise ValueError("not a frozen 512-token prompt")
        checked += 1
    return {"status": "PASS", "binding_rows": checked}


def recompute_native_request_samples(rows: list[dict[str, str]], complete_points: set[str], contract: dict) -> list[dict]:
    """Native CUDA-event statistics from individual OFF-instrumentation arms."""
    native_arms = {"GRAPH_ON_NATIVE", "GRAPH_OFF_NATIVE"}
    expected_points = set(contract["points"])
    if not complete_points <= expected_points:
        raise ValueError("native sample point outside contract")
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    keys = set()
    for row in rows:
        point, arm, role = row["point_id"], row["arm"], row["sample_role"]
        if point not in complete_points or arm not in native_arms or role not in {"WARMUP", "MEASURED"}:
            raise ValueError("foreign point or observed/instrumented row in native timing table")
        key = (point, arm, role, row["sample_index"])
        if key in keys:
            raise ValueError("duplicate native timing sample")
        keys.add(key)
        if row["status"] != "PASS" or not row["process_id"] or not row["request_id"]:
            raise ValueError("invalid native sample receipt")
        duration = float(row["request_cuda_event_ms"])
        if not isfinite(duration) or duration < 0:
            raise ValueError("invalid CUDA-event duration")
        if point in {"MP02", "MP03", "MP05"}:
            expected_tokens = 128 if point == "MP03" else 32
            if int(row["generated_token_count"]) != expected_tokens:
                raise ValueError("generated-token denominator mismatch")
        groups[(point, arm, role)].append(row)
    out = []
    for point in sorted(complete_points):
        for arm in ("GRAPH_ON_NATIVE", "GRAPH_OFF_NATIVE"):
            measured = groups.get((point, arm, "MEASURED"), [])
            warmup = groups.get((point, arm, "WARMUP"), [])
            if len(measured) != 3 or len(warmup) != 1:
                raise ValueError(f"missing/extra native repetitions {point}/{arm}")
            if {r["sample_index"] for r in measured} != {"0", "1", "2"} or {r["sample_index"] for r in warmup} != {"0"}:
                raise ValueError("native repetition index matrix mismatch")
            token_digests = {r["token_ids_sha256"] for r in measured}
            if len(token_digests) != 1 or len(next(iter(token_digests))) != 64:
                raise ValueError("native token identity drift")
            cuda_stats = sample_statistics(float(r["request_cuda_event_ms"]) for r in measured)
            host_stats = sample_statistics(float(r["host_wall_ms"]) for r in measured)
            out.append({
                "point_id": point, "arm": arm, **{f"cuda_{k}": v for k, v in cuda_stats.items()},
                "host_median_diagnostic_ms": host_stats["median"],
                "token_ids_sha256": next(iter(token_digests)),
                "warmup_count": len(warmup),
            })
    return out
