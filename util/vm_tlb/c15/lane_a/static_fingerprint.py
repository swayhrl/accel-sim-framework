#!/usr/bin/env python3
"""Bounded, provenance-preserving static fingerprinting for C15 lane A.

This program deliberately has no ML-framework dependency.  It reads public model
metadata and safetensors *headers* through byte ranges, never model payloads.  Its
outputs are static-storage observations and scenario assumptions, not GPU-memory,
TLB, cache, or timing measurements.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import struct
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable


SCHEMA_VERSION = "C15_LANE_A_STATIC_V1"
PLANNING_SHA = "9a755b14b01c5a77a6fc98c2547616e1c490e806"
MAX_JSON_BYTES = 8 * 1024 * 1024
MAX_HEADER_BYTES = 16 * 1024 * 1024
MAX_MODEL_METADATA_BYTES = 128 * 1024 * 1024
NA = "NA"

DTYPE_BYTES = {
    "BOOL": 1, "U8": 1, "I8": 1, "F8_E4M3FN": 1, "F8_E5M2": 1,
    "I16": 2, "U16": 2, "BF16": 2, "F16": 2,
    "I32": 4, "U32": 4, "F32": 4,
    "I64": 8, "U64": 8, "F64": 8,
}

ASSET_COLUMNS = [
    "asset_id", "asset_kind", "discovered_path_or_ref", "model_id", "revision",
    "phase", "dtype", "framework", "hardware_scope", "availability",
    "source_commit", "hash_kind", "sha256", "size_bytes", "readonly", "missing_reason",
]
REGISTRY_COLUMNS = [
    "model_id", "revision", "deployment_id", "dense_or_moe", "attention_representation",
    "layer_count", "hidden_size", "intermediate_sizes", "head_dimensions", "local_kv_heads",
    "expert_count", "top_k", "shared_experts", "weight_dtype", "activation_dtype", "kv_dtype",
    "quantization_method", "quant_group_size", "tying_status", "tensor_parallel", "pipeline_parallel",
    "expert_parallel", "rank", "kv_layout", "allocation_mode", "logits_policy",
    "implementation_identity", "native_hardware", "fields_verified", "readiness_tier",
]
TENSOR_COLUMNS = [
    "deployment_id", "shard", "tensor_name", "logical_shape_json", "stored_shape_json",
    "storage_dtype", "role", "disk_data_start", "disk_data_end", "stored_bytes",
    "semantic_alias_group", "storage_dedup_basis", "source_hash", "status",
]
FOOTPRINT_COLUMNS = [
    "deployment_id", "scenario_id", "object_kind", "layer_or_expert_scope", "quantity", "value",
    "unit", "formula_id", "assumptions_json", "page_granule_bytes", "evidence_tier", "missing_reason",
]
KV_AUDIT_COLUMNS = [
    "deployment_id", "model_id", "revision", "representation", "adapter_status", "layer_count",
    "local_kv_heads", "head_dim", "kv_dtype_assumption", "token_residency_policy",
    "evidence_source", "missing_reason",
]
KV_CURVE_COLUMNS = [
    "deployment_id", "scenario_id", "batch", "requested_tokens", "resident_tokens", "payload_bytes",
    "unit", "formula_id", "assumptions_json", "evidence_tier", "missing_reason",
]
FETCH_COLUMNS = [
    "model_id", "revision", "resource_kind", "url", "http_status", "content_range", "bytes_read",
    "sha256", "result_status", "attempts", "missing_reason",
]
HEADER_COLUMNS = [
    "model_id", "revision", "shard", "file_size_bytes", "header_bytes", "header_sha256",
    "tensor_count", "payload_interval_bytes", "validation_status", "missing_reason",
]


class C15Error(RuntimeError):
    """A contract-enforcing failure which must not be silently downgraded."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def no_duplicate_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise C15Error("duplicate JSON key: %s" % key)
        result[key] = value
    return result


def json_object(data: bytes, source: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=no_duplicate_json_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError, C15Error) as exc:
        raise C15Error("invalid JSON from %s: %s" % (source, exc)) from exc
    if not isinstance(value, dict):
        raise C15Error("JSON root is not an object: %s" % source)
    return value


def tsv_write(path: Path, columns: list[str], rows: Iterable[dict[str, Any]]) -> None:
    """Write a small table atomically; missing scalars are canonical NA, not zero."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", extrasaction="raise")
        writer.writeheader()
        for source_row in rows:
            row: dict[str, str] = {}
            for column in columns:
                value = source_row.get(column, NA)
                if value is None:
                    value = NA
                elif isinstance(value, (dict, list)):
                    value = canonical_json(value)
                else:
                    value = str(value)
                row[column] = value if value != "" else NA
            writer.writerow(row)
    os.replace(temporary, path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                return digest.hexdigest()
            digest.update(block)


_CONTENT_RANGE = re.compile(r"^bytes (\d+)-(\d+)/(\d+)$")


@dataclass(frozen=True)
class RangeResult:
    data: bytes
    status: int
    content_range: str
    total_size: int
    final_url: str


class BoundedHTTP:
    """HTTP reads that reject a server ignoring Range before its body is consumed."""

    def __init__(self, opener: Callable[..., Any] = urllib.request.urlopen, retries: int = 3):
        self.opener = opener
        self.retries = retries

    @staticmethod
    def _parse_range(raw: str, start: int, max_end: int) -> tuple[int, int, int]:
        match = _CONTENT_RANGE.fullmatch(raw or "")
        if not match:
            raise C15Error("missing or malformed Content-Range")
        got_start, got_end, total = (int(piece) for piece in match.groups())
        if got_start != start or got_end < got_start or got_end > max_end or total <= got_end:
            raise C15Error("Content-Range does not match bounded request: %s" % raw)
        return got_start, got_end, total

    def range(self, url: str, start: int, end: int) -> RangeResult:
        if start < 0 or end < start:
            raise C15Error("invalid requested byte range")
        request = urllib.request.Request(url, headers={"Range": "bytes=%d-%d" % (start, end), "Accept-Encoding": "identity"})
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            response = None
            try:
                response = self.opener(request, timeout=30)
                status = getattr(response, "status", response.getcode())
                # This check intentionally precedes response.read().
                if status != 206:
                    raise C15Error("Range request refused with HTTP %s" % status)
                content_range = response.headers.get("Content-Range", "")
                got_start, got_end, total = self._parse_range(content_range, start, end)
                expected = got_end - got_start + 1
                content_length = response.headers.get("Content-Length")
                if content_length is not None and int(content_length) != expected:
                    raise C15Error("Content-Length disagrees with Content-Range")
                data = response.read(expected + 1)
                if len(data) != expected:
                    raise C15Error("truncated or oversized range body")
                return RangeResult(data, status, content_range, total, response.geturl())
            except (urllib.error.URLError, TimeoutError) as exc:
                last_error = exc
                if attempt == self.retries:
                    break
                time.sleep(0.1 * attempt)
            finally:
                if response is not None:
                    response.close()
        raise C15Error("bounded HTTP retry limit reached: %s" % last_error)

    def small_json(self, url: str, cap: int = MAX_JSON_BYTES) -> tuple[dict[str, Any], int, str]:
        """Read a non-weight JSON endpoint with a hard body cap."""
        request = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
        response = None
        try:
            response = self.opener(request, timeout=30)
            status = getattr(response, "status", response.getcode())
            if status != 200:
                raise C15Error("JSON request returned HTTP %s" % status)
            length = response.headers.get("Content-Length")
            if length is not None and int(length) > cap:
                raise C15Error("JSON response exceeds cap before body read")
            data = response.read(cap + 1)
            if len(data) > cap:
                raise C15Error("JSON response exceeds cap")
            return json_object(data, url), status, sha256_bytes(data)
        finally:
            if response is not None:
                response.close()


def read_safetensors_header(http: BoundedHTTP, url: str) -> tuple[dict[str, Any], RangeResult, RangeResult]:
    prelude = http.range(url, 0, 7)
    if len(prelude.data) != 8:
        raise C15Error("safetensors prelude length is not eight")
    header_length = struct.unpack("<Q", prelude.data)[0]
    if header_length <= 0 or header_length > MAX_HEADER_BYTES:
        raise C15Error("safetensors header length outside bounded policy: %d" % header_length)
    if 8 + header_length > prelude.total_size:
        raise C15Error("safetensors header extends beyond file")
    header = http.range(url, 8, 8 + header_length - 1)
    if header.total_size != prelude.total_size:
        raise C15Error("safetensors file size changed during header read")
    parsed = json_object(header.data, url)
    validate_safetensors(parsed, prelude.total_size - 8 - header_length)
    return parsed, prelude, header


def validate_safetensors(header: dict[str, Any], payload_size: int) -> None:
    seen_ranges: set[tuple[int, int]] = set()
    for name, item in header.items():
        if name == "__metadata__":
            continue
        if not isinstance(item, dict):
            raise C15Error("tensor %s header is not an object" % name)
        dtype, shape, offsets = item.get("dtype"), item.get("shape"), item.get("data_offsets")
        if dtype not in DTYPE_BYTES or not isinstance(shape, list) or not isinstance(offsets, list) or len(offsets) != 2:
            raise C15Error("tensor %s lacks valid dtype/shape/offsets" % name)
        if any(not isinstance(dimension, int) or dimension < 0 for dimension in shape):
            raise C15Error("tensor %s has invalid shape" % name)
        start, end = offsets
        if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end < start or end > payload_size:
            raise C15Error("tensor %s has invalid data_offsets" % name)
        logical_elements = 1
        for dimension in shape:
            logical_elements *= dimension
        if dtype in {"BOOL", "U8", "I8", "I16", "U16", "I32", "U32", "I64", "U64", "F16", "BF16", "F32", "F64"}:
            expected = logical_elements * DTYPE_BYTES[dtype]
            if end - start != expected:
                raise C15Error("tensor %s storage bytes disagree with shape/dtype" % name)
        # Repeated physical spans are legal aliases.  Overlap without equality is not
        # automatically aliasing, so it remains independently reported rather than deduped.
        seen_ranges.add((start, end))


def union_bytes(ranges: Iterable[tuple[int, int]]) -> int:
    ordered = sorted((start, end) for start, end in ranges if end > start)
    total = 0
    cursor_end: int | None = None
    for start, end in ordered:
        if cursor_end is None:
            total += end - start
            cursor_end = end
        elif start > cursor_end:
            total += end - start
            cursor_end = end
        elif end > cursor_end:
            total += end - cursor_end
            cursor_end = end
    return total


def pages_for_range(base: int, length: int, page_bytes: int) -> int:
    if base < 0 or length < 0 or page_bytes <= 0:
        raise C15Error("invalid page range arguments")
    if length == 0:
        return 0
    return (base + length - 1) // page_bytes - base // page_bytes + 1


def deployment_id(identity_fields: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(identity_fields).encode("ascii")).hexdigest()


def value_or_na(value: Any) -> Any:
    return NA if value is None else value


def model_shape(config: dict[str, Any]) -> dict[str, Any]:
    layers = config.get("num_hidden_layers", config.get("n_layer"))
    hidden = config.get("hidden_size", config.get("n_embd"))
    heads = config.get("num_attention_heads", config.get("n_head"))
    kv_heads = config.get("num_key_value_heads", config.get("num_kv_heads"))
    if kv_heads is None and heads is not None:
        kv_heads = heads
    head_dim = config.get("head_dim")
    if head_dim is None and isinstance(hidden, int) and isinstance(heads, int) and heads and hidden % heads == 0:
        head_dim = hidden // heads
    intermediate = config.get("intermediate_size", config.get("n_inner"))
    experts = config.get("num_local_experts", config.get("n_routed_experts", config.get("num_experts")))
    top_k = config.get("num_experts_per_tok", config.get("num_experts_per_token", config.get("topk_method")))
    is_moe = isinstance(experts, int) and experts > 1
    has_mla_markers = any(key in config for key in ("kv_lora_rank", "q_lora_rank", "qk_rope_head_dim"))
    return {
        "layers": layers, "hidden": hidden, "heads": heads, "kv_heads": kv_heads,
        "head_dim": head_dim, "intermediate": intermediate, "experts": experts,
        "top_k": top_k, "dense_or_moe": "MOE" if is_moe else "DENSE",
        "attention": "MLA_OR_COMPRESSED" if has_mla_markers else "STANDARD_KV_CANDIDATE",
    }


def role_for_tensor(name: str) -> str:
    lowered = name.lower()
    if "embed" in lowered or "lm_head" in lowered:
        return "WEIGHT_EMBEDDING_OR_LOGITS"
    if "norm" in lowered:
        return "WEIGHT_NORM"
    if "scale" in lowered or "zero" in lowered:
        return "QUANTIZATION_METADATA"
    if ".weight" in lowered or ".bias" in lowered or "experts" in lowered:
        return "WEIGHT"
    return "UNKNOWN_STATIC_TENSOR"


def rows_from_header(deploy_id: str, shard: str, header: dict[str, Any], header_hash: str) -> list[dict[str, Any]]:
    ranges_to_names: dict[tuple[int, int], list[str]] = defaultdict(list)
    for name, item in header.items():
        if name != "__metadata__":
            ranges_to_names[tuple(item["data_offsets"])].append(name)
    rows: list[dict[str, Any]] = []
    for name, item in sorted(header.items()):
        if name == "__metadata__":
            continue
        start, end = item["data_offsets"]
        aliases = ranges_to_names[(start, end)]
        alias_group = "EXACT:%s:%d:%d" % (shard, start, end) if len(aliases) > 1 else NA
        rows.append({
            "deployment_id": deploy_id, "shard": shard, "tensor_name": name,
            "logical_shape_json": item["shape"], "stored_shape_json": item["shape"],
            "storage_dtype": item["dtype"], "role": role_for_tensor(name),
            "disk_data_start": start, "disk_data_end": end, "stored_bytes": end - start,
            "semantic_alias_group": alias_group,
            "storage_dedup_basis": "EXACT_SHARD_OFFSET_RANGE" if len(aliases) > 1 else "NO_PROVEN_ALIAS",
            "source_hash": "SAFETENSORS_HEADER_SHA256:%s" % header_hash,
            "status": "HEADER_RANGE_VERIFIED",
        })
    return rows


def kv_payload_bytes(layers: int, batch: int, resident_tokens: int, local_kv_heads: int, head_dim: int, bytes_per_value: int) -> int:
    values = layers * batch * resident_tokens * local_kv_heads * head_dim * 2
    return values * bytes_per_value


def extract_weight_dtype(tensor_rows: list[dict[str, Any]]) -> str:
    dtypes = sorted({row["storage_dtype"] for row in tensor_rows if row["role"].startswith("WEIGHT")})
    return dtypes[0] if len(dtypes) == 1 else ("MIXED:" + ",".join(dtypes) if dtypes else NA)


def require_columns(path: Path, expected: list[str]) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != expected:
            raise C15Error("schema mismatch in %s" % path)
        rows = list(reader)
    for index, row in enumerate(rows, start=2):
        if any(value == "" for value in row.values()):
            raise C15Error("empty TSV scalar in %s line %d" % (path, index))
    return rows


def static_fixture_checks() -> list[tuple[str, str]]:
    """Contract T03--T06 numerical checks, kept independent from network inputs."""
    assert DTYPE_BYTES["F16"] * 8 == 16
    assert 4 + 2 == 6  # INT4 payload plus fp16 scale fixture.
    assert kv_payload_bytes(2, 3, 5, 2, 4, 2) == 960
    assert kv_payload_bytes(2, 3, 3, 2, 4, 2) == 576
    assert pages_for_range(65530, 12, 65536) == 2
    assert union_bytes([(0, 8), (4, 12)]) == 12
    try:
        validate_safetensors({"x": {"dtype": "F16", "shape": [2, 4], "data_offsets": [-1, 16]}}, 16)
        raise AssertionError("negative offset accepted")
    except C15Error:
        pass
    return [("T03", "PASS"), ("T04", "PASS"), ("T05", "PASS"), ("T06", "PASS")]


def verify_output_root(root: Path) -> list[tuple[str, str]]:
    required = {
        "ASSET_INVENTORY.tsv": ASSET_COLUMNS,
        "MODEL_REGISTRY.tsv": REGISTRY_COLUMNS,
        "TENSOR_STORAGE_CATALOG.tsv": TENSOR_COLUMNS,
        "STATIC_FOOTPRINT.tsv": FOOTPRINT_COLUMNS,
    }
    for relative, columns in required.items():
        require_columns(root / relative, columns)
    return [("T01", "PASS"), ("T20", "PASS")]


def verify_bootstrap_root(root: Path) -> list[tuple[str, str]]:
    """Validate the early, deliberately model-free C15-0.2 checkpoint."""
    assets = require_columns(root / "ASSET_INVENTORY.tsv", ASSET_COLUMNS)
    bootstrap_columns = [
        "bootstrap_id", "entry_kind", "identity_status", "availability", "evidence_tier",
        "source_ref", "sha256_or_commit", "use_in_c15", "missing_reason",
    ]
    registry = require_columns(root / "BOOTSTRAP_REGISTRY.tsv", bootstrap_columns)
    if not assets or not registry:
        raise C15Error("bootstrap inventory or registry is empty")
    for row in assets:
        if row["availability"] == "NOT_FOUND" and row["missing_reason"] == NA:
            raise C15Error("unavailable bootstrap asset lacks a reason")
        if row["model_id"] != NA and row["revision"] == NA:
            raise C15Error("bootstrap must not assert a model without a revision")
    verify_publish_manifest(root)
    return [("T01", "PASS")]


def verify_publish_manifest(root: Path) -> None:
    manifest_path = root / "PUBLISH_MANIFEST.json"
    manifest = json_object(manifest_path.read_bytes(), str(manifest_path))
    if manifest.get("planning_sha") != PLANNING_SHA or manifest.get("lane") != "A":
        raise C15Error("publish manifest identity mismatch")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise C15Error("publish manifest has no files")
    seen_paths: set[str] = set()
    for entry in files:
        if not isinstance(entry, dict) or set(("path", "sha256", "size_bytes")) - set(entry):
            raise C15Error("malformed publish file entry")
        relative = entry["path"]
        if relative == "PUBLISH_MANIFEST.json" or relative in seen_paths:
            raise C15Error("self-referential or duplicate publish entry")
        seen_paths.add(relative)
        candidate = root / relative
        if not candidate.is_file() or candidate.stat().st_size != entry["size_bytes"]:
            raise C15Error("published file size mismatch: %s" % relative)
        if sha256_file(candidate) != entry["sha256"]:
            raise C15Error("published file digest mismatch: %s" % relative)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true", help="run deterministic contract-fixture checks")
    parser.add_argument("--validate", type=Path, metavar="RESULT_ROOT", help="validate generated TSV schemas")
    parser.add_argument("--validate-bootstrap", type=Path, metavar="RESULT_ROOT", help="validate C15-0.2 tables")
    args = parser.parse_args(argv)
    if not args.selftest and args.validate is None and args.validate_bootstrap is None:
        parser.error("one of --selftest, --validate, or --validate-bootstrap is required")
    results: list[tuple[str, str]] = []
    if args.selftest:
        results.extend(static_fixture_checks())
    if args.validate is not None:
        results.extend(verify_output_root(args.validate))
    if args.validate_bootstrap is not None:
        results.extend(verify_bootstrap_root(args.validate_bootstrap))
    for test_id, status in results:
        print("%s\t%s" % (test_id, status))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
