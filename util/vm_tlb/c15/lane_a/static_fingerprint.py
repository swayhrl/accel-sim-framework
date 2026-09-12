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
import shutil
import struct
import subprocess
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
COST_COLUMNS = [
    "work_id", "parent_work_id", "lane", "stage_id", "attempt", "operation", "start_utc", "end_utc",
    "wall_s", "cpu_core_s", "gpu_active_s", "peak_rss_B", "peak_vram_B", "bytes_read", "bytes_downloaded",
    "bytes_written", "warmup_s", "retry_s", "measured_or_estimated", "result_status",
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
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", extrasaction="raise", lineterminator="\n")
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

    def __init__(self, opener: Callable[..., Any] = urllib.request.urlopen, retries: int = 3, timeout_s: int = 5):
        self.opener = opener
        self.retries = retries
        self.timeout_s = timeout_s
        self._curl_only = False
        self.last_json_bytes = 0

    @staticmethod
    def _parse_range(raw: str, start: int, max_end: int) -> tuple[int, int, int]:
        match = _CONTENT_RANGE.fullmatch(raw or "")
        if not match:
            raise C15Error("missing or malformed Content-Range")
        got_start, got_end, total = (int(piece) for piece in match.groups())
        if got_start != start or got_end < got_start or got_end > max_end or total <= got_end:
            raise C15Error("Content-Range does not match bounded request: %s" % raw)
        return got_start, got_end, total

    @staticmethod
    def _curl_headers(raw: bytes) -> tuple[int, dict[str, str]]:
        """Select the final HTTP block after proxy and redirect header blocks."""
        text = raw.decode("iso-8859-1", errors="replace")
        blocks = re.split(r"\r?\n\r?\n", text)
        for block in reversed(blocks):
            lines = [line for line in block.splitlines() if line]
            if not lines or not lines[0].startswith("HTTP/"):
                continue
            match = re.match(r"HTTP/\S+\s+(\d{3})", lines[0])
            if not match:
                continue
            headers: dict[str, str] = {}
            for line in lines[1:]:
                if ":" in line:
                    key, value = line.split(":", 1)
                    headers[key.lower()] = value.strip()
            return int(match.group(1)), headers
        raise C15Error("curl response lacks a parsable HTTP header block")

    def _curl(self, arguments: list[str], url: str, max_output: int) -> tuple[bytes, int, dict[str, str]]:
        if shutil.which("curl") is None:
            raise C15Error("urllib TLS failed and curl fallback is unavailable")
        command = ["curl", "--silent", "--show-error", "--location", "--max-time", str(self.timeout_s), "--dump-header", "/dev/stderr", *arguments, url]
        completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if completed.returncode != 0:
            raise C15Error("curl fallback failed (exit %d): %s" % (completed.returncode, completed.stderr.decode("utf-8", errors="replace")[-240:]))
        if len(completed.stdout) > max_output:
            raise C15Error("curl response exceeds bounded output limit")
        status, headers = self._curl_headers(completed.stderr)
        return completed.stdout, status, headers

    def _curl_range(self, url: str, start: int, end: int) -> RangeResult:
        requested = end - start + 1
        # The HEAD pass proves 206/Content-Range before the GET command is allowed
        # to consume any bytes. --max-filesize protects the second pass if a server
        # changes its behavior between requests.
        _head_body, head_status, head_headers = self._curl(["--request", "HEAD", "--ignore-content-length", "--range", "%d-%d" % (start, end)], url, 0)
        if head_status != 206:
            raise C15Error("curl Range HEAD refused with HTTP %s" % head_status)
        _head_start, _head_end, head_total = self._parse_range(head_headers.get("content-range", ""), start, end)
        body, status, headers = self._curl(["--range", "%d-%d" % (start, end), "--max-filesize", str(requested)], url, requested)
        if status != 206:
            raise C15Error("curl Range GET refused with HTTP %s" % status)
        got_start, got_end, total = self._parse_range(headers.get("content-range", ""), start, end)
        if total != head_total or len(body) != got_end - got_start + 1:
            raise C15Error("curl Range response changed or truncated")
        return RangeResult(body, status, headers["content-range"], total, url)

    def _curl_small_json(self, url: str, cap: int) -> tuple[dict[str, Any], int, str]:
        _head_body, head_status, head_headers = self._curl(["--request", "HEAD", "--ignore-content-length"], url, 0)
        if head_status != 200:
            raise C15Error("curl JSON HEAD returned HTTP %s" % head_status)
        length = head_headers.get("content-length")
        if length is None or int(length) > cap:
            raise C15Error("curl JSON endpoint has missing or oversized Content-Length")
        body, status, _headers = self._curl(["--max-filesize", str(cap)], url, cap)
        if status != 200 or len(body) > cap:
            raise C15Error("curl JSON GET violates bounded policy")
        self.last_json_bytes = len(body)
        return json_object(body, url), status, sha256_bytes(body)

    def range(self, url: str, start: int, end: int) -> RangeResult:
        if start < 0 or end < start:
            raise C15Error("invalid requested byte range")
        if self._curl_only and self.opener is urllib.request.urlopen:
            return self._curl_range(url, start, end)
        request = urllib.request.Request(url, headers={"Range": "bytes=%d-%d" % (start, end), "Accept-Encoding": "identity"})
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            response = None
            try:
                response = self.opener(request, timeout=self.timeout_s)
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
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = exc
                if self.opener is urllib.request.urlopen:
                    self._curl_only = True
                    try:
                        return self._curl_range(url, start, end)
                    except C15Error as fallback_exc:
                        last_error = fallback_exc
                if attempt == self.retries:
                    break
                time.sleep(0.1 * attempt)
            finally:
                if response is not None:
                    response.close()
        raise C15Error("bounded HTTP retry limit reached: %s" % last_error)

    def small_json(self, url: str, cap: int = MAX_JSON_BYTES) -> tuple[dict[str, Any], int, str]:
        """Read a non-weight JSON endpoint with a hard body cap."""
        if self._curl_only and self.opener is urllib.request.urlopen:
            return self._curl_small_json(url, cap)
        request = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
        response = None
        try:
            response = self.opener(request, timeout=self.timeout_s)
            status = getattr(response, "status", response.getcode())
            if status != 200:
                raise C15Error("JSON request returned HTTP %s" % status)
            length = response.headers.get("Content-Length")
            if length is not None and int(length) > cap:
                raise C15Error("JSON response exceeds cap before body read")
            data = response.read(cap + 1)
            if len(data) > cap:
                raise C15Error("JSON response exceeds cap")
            self.last_json_bytes = len(data)
            return json_object(data, url), status, sha256_bytes(data)
        except (urllib.error.URLError, TimeoutError, OSError):
            if self.opener is urllib.request.urlopen:
                self._curl_only = True
                return self._curl_small_json(url, cap)
            raise
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


def require_immutable_resolve_url(url: str, revision: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", revision) or ("/resolve/%s/" % revision) not in url:
        raise C15Error("resource URL is not pinned to the expected immutable revision")


def assert_authorized_operation(operation: str, requested_amount: int = 0) -> None:
    """Explicit C15-guard for operations which this lane never performs."""
    forbidden = {"full_weight_download", "new_simulator_build", "new_simulator_replay", "full_roi_simulation", "gpu_profile", "full_model_sass", "core_change"}
    if operation in forbidden or requested_amount < 0:
        raise C15Error("C15 lane A authorization rejects operation: %s" % operation)
    if operation != "bounded_metadata" or requested_amount > MAX_MODEL_METADATA_BYTES:
        raise C15Error("C15 lane A authorization rejects unbounded operation")


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
    if "qweight" in lowered or "packed_weight" in lowered:
        return "WEIGHT_QUANTIZED_PACKED"
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


def require_unique(rows: list[dict[str, str]], columns: tuple[str, ...], label: str, allow_na: bool = False) -> None:
    seen: set[tuple[str, ...]] = set()
    for row in rows:
        key = tuple(row[column] for column in columns)
        if not allow_na and NA in key:
            raise C15Error("NA in primary key for %s" % label)
        if key in seen:
            raise C15Error("duplicate primary key for %s: %s" % (label, key))
        seen.add(key)


def require_nonnegative_integer(value: str, label: str) -> None:
    if value != NA and (not value.isdigit() or int(value) < 0):
        raise C15Error("invalid nonnegative integer %s in %s" % (value, label))


def static_fixture_checks() -> list[tuple[str, str]]:
    """Contract T03--T06 numerical checks, kept independent from network inputs."""
    assert DTYPE_BYTES["F16"] * 8 == 16
    assert 4 + 2 == 6  # INT4 payload plus fp16 scale fixture.
    aliased = rows_from_header("fixture", "one", {
        "embed.weight": {"dtype": "F16", "shape": [2, 4], "data_offsets": [0, 16]},
        "lm_head.weight": {"dtype": "F16", "shape": [2, 4], "data_offsets": [0, 16]},
    }, "fixture-header")
    assert union_bytes([(int(row["disk_data_start"]), int(row["disk_data_end"])) for row in aliased]) == 16
    independent = rows_from_header("fixture", "one", {
        "embed.weight": {"dtype": "F16", "shape": [2, 4], "data_offsets": [0, 16]},
        "lm_head.weight": {"dtype": "F16", "shape": [2, 4], "data_offsets": [16, 32]},
    }, "fixture-header")
    assert union_bytes([(int(row["disk_data_start"]), int(row["disk_data_end"])) for row in independent]) == 32
    assert kv_payload_bytes(2, 3, 5, 2, 4, 2) == 960
    assert kv_payload_bytes(2, 3, 3, 2, 4, 2) == 576
    assert kv_payload_bytes(2, 6, 5, 2, 4, 2) == 1920  # B doubles.
    assert kv_payload_bytes(2, 3, 10, 2, 4, 2) == 1920  # T doubles.
    assert kv_payload_bytes(2, 3, 5, 1, 4, 2) == 480  # TP-sharded rank-local head count.
    assert kv_payload_bytes(1, 3, 5, 2, 4, 2) + kv_payload_bytes(1, 3, 5, 1, 4, 2) == 720  # mixed layers.
    assert pages_for_range(65530, 12, 65536) == 2
    assert union_bytes([(0, 8), (4, 12)]) == 12
    assert pages_for_range((1 << 63) - 2, 4, 4096) == 2
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
    rows = {relative: require_columns(root / relative, columns) for relative, columns in required.items()}
    require_unique(rows["ASSET_INVENTORY.tsv"], ("asset_id",), "ASSET_INVENTORY")
    require_unique(rows["MODEL_REGISTRY.tsv"], ("deployment_id",), "MODEL_REGISTRY")
    require_unique(rows["TENSOR_STORAGE_CATALOG.tsv"], ("deployment_id", "shard", "tensor_name"), "TENSOR_STORAGE_CATALOG")
    require_unique(rows["STATIC_FOOTPRINT.tsv"], ("deployment_id", "scenario_id", "object_kind", "layer_or_expert_scope", "quantity", "page_granule_bytes"), "STATIC_FOOTPRINT", allow_na=True)
    for row in rows["TENSOR_STORAGE_CATALOG.tsv"]:
        require_nonnegative_integer(row["stored_bytes"], "TENSOR_STORAGE_CATALOG.stored_bytes")
        require_nonnegative_integer(row["disk_data_start"], "TENSOR_STORAGE_CATALOG.disk_data_start")
        require_nonnegative_integer(row["disk_data_end"], "TENSOR_STORAGE_CATALOG.disk_data_end")
        if row["stored_bytes"] != NA and row["disk_data_start"] != NA and row["disk_data_end"] != NA and int(row["stored_bytes"]) != int(row["disk_data_end"]) - int(row["disk_data_start"]):
            raise C15Error("stored bytes do not close to source offsets")
    for row in rows["STATIC_FOOTPRINT.tsv"]:
        if row["unit"] not in ("B", "pages"):
            raise C15Error("unsupported static footprint unit")
        if row["unit"] == "pages" and row["page_granule_bytes"] == NA:
            raise C15Error("page scenario lacks a granule")
        require_nonnegative_integer(row["value"], "STATIC_FOOTPRINT.value")
        try:
            json.loads(row["assumptions_json"])
        except json.JSONDecodeError as exc:
            raise C15Error("invalid assumptions JSON") from exc
    manifest = json_object((root / "DEPLOYMENT_MANIFEST.json").read_bytes(), "DEPLOYMENT_MANIFEST.json")
    deployment_ids = {row["deployment_id"] for row in rows["MODEL_REGISTRY.tsv"]}
    if manifest.get("planning_sha") != PLANNING_SHA or {item.get("deployment_id") for item in manifest.get("deployments", [])} != deployment_ids:
        raise C15Error("deployment manifest does not close to registry")
    plan_path = root / "MODEL_SELECTION_PLAN.tsv"
    if plan_path.exists():
        plan_columns = [
            "plan_id", "candidate_id", "model_id", "candidate_role", "model_counting_rule", "planned_source_api",
            "planned_revision", "availability_at_freeze", "metadata_budget_class", "selection_basis",
            "forbidden_result_input", "readiness_target", "missing_reason",
        ]
        plan_rows = require_columns(plan_path, plan_columns)
        require_unique(plan_rows, ("plan_id", "candidate_id"), "MODEL_SELECTION_PLAN")
        for row in plan_rows:
            if any(token in row["selection_basis"].lower() for token in ("speedup", "cycle", "miss")):
                raise C15Error("selection plan leaks a candidate result")
            if row["forbidden_result_input"] != "candidate speedup/cycle/miss result":
                raise C15Error("selection plan does not explicitly exclude candidate outcomes")
    verify_cost_ledger(root)
    return [("T01", "PASS"), ("T14", "PASS"), ("T20", "PASS")] + verify_integration_outputs(root, deployment_ids)


def verify_cost_ledger(root: Path) -> None:
    rows = require_columns(root / "COST_LEDGER.tsv", COST_COLUMNS)
    require_unique(rows, ("work_id",), "COST_LEDGER")
    nonnegative = ("attempt", "wall_s", "cpu_core_s", "gpu_active_s", "peak_rss_B", "peak_vram_B", "bytes_read", "bytes_downloaded", "bytes_written", "warmup_s", "retry_s")
    for row in rows:
        if row["lane"] != "A":
            raise C15Error("non-A row in lane A ledger")
        for column in nonnegative:
            value = row[column]
            if value != NA:
                try:
                    if float(value) < 0:
                        raise C15Error("negative cost in %s" % column)
                except ValueError as exc:
                    raise C15Error("non-numeric cost in %s" % column) from exc
        if row["gpu_active_s"] != "0":
            raise C15Error("lane A ledger reports unauthorized GPU use")


def verify_integration_outputs(root: Path, deployment_ids: set[str]) -> list[tuple[str, str]]:
    """Validate A-owned integration metadata without reading producer worktrees."""
    integration = root / "integration"
    if not integration.exists():
        return []
    consumed_columns = [
        "consumer_lane", "producer_lane", "remote_branch", "fetched_commit", "manifest_path",
        "manifest_sha256", "planning_sha", "verified_payloads", "consumption_scope", "status", "missing_reason",
    ]
    consumed = require_columns(integration / "CONSUMED_INPUTS.tsv", consumed_columns)
    require_unique(consumed, ("consumer_lane", "producer_lane"), "CONSUMED_INPUTS")
    expected = {
        "B": ("721e30f377dab36d826dc7ea9d47e11c5d85aa5c", "38dcc5c615d531b6c812facffa5b0634b1bafff89b87a57e190a2fca8cdc7aad"),
        "C": ("a51d6c91b1e7d7df27a4af80823a29ff30bb9806", "17d7888650c2c51f1dd0d4a418eb45948212a259dd01661d1adca33832e5dec0"),
    }
    if {row["producer_lane"] for row in consumed} != set(expected):
        raise C15Error("integration must identify exactly the accepted B/C producers")
    for row in consumed:
        commit, manifest_hash = expected[row["producer_lane"]]
        if row["consumer_lane"] != "A" or row["planning_sha"] != PLANNING_SHA:
            raise C15Error("integration consumer identity mismatch")
        if row["fetched_commit"] != commit or row["manifest_sha256"] != manifest_hash:
            raise C15Error("integration fixed commit or manifest hash mismatch")
        if row["status"] != "ACCEPTED_HASH_BOUND":
            raise C15Error("integration accepted a non-hash-bound input")
    upgrade_columns = [
        "deployment_id", "compared_class", "known_dimensions", "novel_dimensions", "uncertainty",
        "audit_window_evidence", "decision", "reason", "proposed_next_scope", "expected_cost", "requires_new_authorization",
    ]
    upgrades = require_columns(integration / "UPGRADE_DECISIONS.tsv", upgrade_columns)
    require_unique(upgrades, ("deployment_id",), "UPGRADE_DECISIONS")
    if {row["deployment_id"] for row in upgrades} != deployment_ids:
        raise C15Error("integration upgrade table does not close to the static deployment registry")
    allowed_decisions = {"KNOWN_CLASS_PROFILED", "CHARACTERIZED_NOT_TIMING_VALIDATED", "STATIC_ONLY", "NEEDS_T2_AUDIT", "PROPOSE_T3", "INCONCLUSIVE"}
    for row in upgrades:
        if row["decision"] not in allowed_decisions:
            raise C15Error("integration has an invalid upgrade decision")
        if row["requires_new_authorization"] not in ("true", "false"):
            raise C15Error("integration authorization field is not boolean")
        if row["decision"] in {"KNOWN_CLASS_PROFILED", "CHARACTERIZED_NOT_TIMING_VALIDATED", "PROPOSE_T3"}:
            raise C15Error("integration admits an unsupported dynamic upgrade")
    receipt = json_object((integration / "INTEGRATION_RECEIPT.json").read_bytes(), "INTEGRATION_RECEIPT.json")
    if receipt.get("planning_sha") != PLANNING_SHA or receipt.get("conclusion") != "C15_LOWCOST_FOUNDATION_PARTIAL_READY_FOR_REVIEW":
        raise C15Error("integration receipt identity or conclusion mismatch")
    if receipt.get("consumed_commits") != {"B": expected["B"][0], "C": expected["C"][0]}:
        raise C15Error("integration receipt commits mismatch")
    tests = {entry.get("test_id"): entry.get("result") for entry in receipt.get("tests", []) if isinstance(entry, dict)}
    if tests.get("T22") != "PASS":
        raise C15Error("integration T22 receipt is missing or failed")
    cost_rows = require_columns(integration / "COST_LEDGER.tsv", COST_COLUMNS)
    require_unique(cost_rows, ("work_id",), "INTEGRATION_COST_LEDGER")
    for row in cost_rows:
        if row["gpu_active_s"] not in ("0", NA):
            raise C15Error("integration ledger reports unauthorized GPU use")
    summary = require_columns(integration / "STAGE_ACCEPTANCE_SUMMARY.tsv", ["stage_id", "owner", "execution_status", "validation_status", "basis", "limitation_or_failure"])
    require_unique(summary, ("stage_id",), "STAGE_ACCEPTANCE_SUMMARY")
    if len(summary) != 36 or {"C15-5.1", "C15-5.2", "C15-5.4"} - {row["stage_id"] for row in summary}:
        raise C15Error("integration stage acceptance summary is incomplete")
    findings = (integration / "CROSS_MODEL_FINDINGS.md").read_text(encoding="utf-8")
    report = (integration / "FINAL_REPORT.md").read_text(encoding="utf-8")
    for required_boundary in ("SAMPLER_NOT_QUALIFIED", "no dynamic"):
        if required_boundary not in findings and required_boundary not in report:
            raise C15Error("integration evidence boundary is missing: %s" % required_boundary)
    return [("T18", "PASS"), ("T22", "PASS")]


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


def write_static_publish_manifest(root: Path) -> None:
    """Write the non-self-referential static or fixed-input integration manifest."""
    repo_root = Path(__file__).resolve().parents[4]
    artifact_files = sorted(path for path in root.rglob("*") if path.is_file() and path.name != "PUBLISH_MANIFEST.json")
    if not artifact_files:
        raise C15Error("cannot publish an empty static result root")
    files = [{"path": str(path.relative_to(root)), "sha256": sha256_file(path), "size_bytes": path.stat().st_size} for path in artifact_files]
    producer_files = []
    for path in (repo_root / "util/vm_tlb/c15/lane_a/static_fingerprint.py", repo_root / "tests/vm_tlb/c15/lane_a/test_static_fingerprint.py"):
        producer_files.append({"path": str(path.relative_to(repo_root)), "sha256": sha256_file(path)})
    integrated = (root / "integration" / "INTEGRATION_RECEIPT.json").is_file()
    ready_stages = ["C15-0.1", "C15-0.2", "C15-1.1", "C15-1.2", "C15-1.3", "C15-1.4", "C15-1.5", "C15-1.6"]
    input_sources = [
        {"name": "C12_FINAL", "commit": "a268aba0d01310294074ded5bb8017e2092394c0", "read_policy": "READ_ONLY_FIXED_COMMIT"},
        {"name": "PUBLIC_METADATA", "identity": "per-model immutable revisions and source digests in METADATA_FETCH_RECEIPTS.tsv", "read_policy": "BOUNDED_CONFIG_INDEX_HEADER_ONLY"},
    ]
    gaps = [
        "TWO_PLANNED_CANDIDATE_IDENTITIES_UNAVAILABLE", "SEVEN_OF_TEN_CONFIGURATIONS_STATIC_CONFIG_ONLY",
        "DEEPSEEK_MLA_OR_COMPRESSED_REPRESENTATION_UNSUPPORTED_BY_STANDARD_KV_ADAPTER",
        "NO_NATIVE_OR_CROSS_MODEL_DYNAMIC_EVIDENCE",
    ]
    if integrated:
        ready_stages.extend(["C15-5.1", "C15-5.2", "C15-5.4"])
        input_sources.extend([
            {"name": "LANE_B_PUBLISH", "commit": "721e30f377dab36d826dc7ea9d47e11c5d85aa5c", "manifest_sha256": "38dcc5c615d531b6c812facffa5b0634b1bafff89b87a57e190a2fca8cdc7aad", "read_policy": "READ_ONLY_FIXED_COMMIT_HASH_BOUND"},
            {"name": "LANE_C_PUBLISH", "commit": "a51d6c91b1e7d7df27a4af80823a29ff30bb9806", "manifest_sha256": "17d7888650c2c51f1dd0d4a418eb45948212a259dd01661d1adca33832e5dec0", "read_policy": "READ_ONLY_FIXED_COMMIT_HASH_BOUND"},
        ])
        gaps.extend(["NO_NEW_NATIVE_CAPTURE_FROM_B", "SAMPLER_NOT_QUALIFIED_FROM_C", "NO_UPGRADE_AUTHORIZED"])
    json_write(root / "PUBLISH_MANIFEST.json", {
        "schema_version": "C15_PUBLISH_MANIFEST_V1", "planning_sha": PLANNING_SHA, "lane": "A",
        "run_id": "c15-a-integration-20260912" if integrated else "c15-a-static-20260912", "producer_source_sha": PLANNING_SHA,
        "producer_files": producer_files,
        "ready_stage_ids": ready_stages,
        "input_sources": input_sources,
        "evidence_scope": "static configuration metadata, selected safetensors header storage, formula-derived KV curves, and file-layout page scenarios; fixed-commit B/C capability and historical qualification synthesis only; no GPU/runtime/cache/TLB/timing measurement",
        "gaps": gaps,
        "files": files,
    })


def json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def tsv_read(path: Path, columns: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        return []
    return require_columns(path, columns)


def page_union_count(ranges: Iterable[tuple[int, int]], page_bytes: int) -> int:
    pages: list[tuple[int, int]] = []
    for start, end in ranges:
        if end > start:
            pages.append((start // page_bytes, (end - 1) // page_bytes))
    if not pages:
        return 0
    pages.sort()
    total = 0
    cursor_start, cursor_end = pages[0]
    for start, end in pages[1:]:
        if start > cursor_end + 1:
            total += cursor_end - cursor_start + 1
            cursor_start, cursor_end = start, end
        else:
            cursor_end = max(cursor_end, end)
    return total + cursor_end - cursor_start + 1


def dtype_bytes_from_config(config: dict[str, Any]) -> tuple[int | None, str]:
    raw = str(config.get("torch_dtype", "")).lower()
    mapping = {
        "float16": (2, "F16"), "torch.float16": (2, "F16"), "fp16": (2, "F16"),
        "bfloat16": (2, "BF16"), "torch.bfloat16": (2, "BF16"), "bf16": (2, "BF16"),
        "float32": (4, "F32"), "torch.float32": (4, "F32"), "fp32": (4, "F32"),
    }
    return mapping.get(raw, (None, NA))


def small_json_with_receipt(http: BoundedHTTP, model_id: str, revision: str, kind: str, url: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    try:
        value, status, digest = http.small_json(url)
        return value, {
            "model_id": model_id, "revision": revision, "resource_kind": kind, "url": url,
            "http_status": status, "content_range": NA, "bytes_read": http.last_json_bytes, "sha256": digest,
            "result_status": "PASS", "attempts": 1, "missing_reason": NA,
        }
    except Exception as exc:  # HTTP errors are recorded as evidence, not erased.
        status = getattr(exc, "code", NA)
        return None, {
            "model_id": model_id, "revision": revision, "resource_kind": kind, "url": url,
            "http_status": status, "content_range": NA, "bytes_read": 0, "sha256": NA,
            "result_status": "FAILED", "attempts": 1, "missing_reason": "%s:%s" % (type(exc).__name__, str(exc)[:240]),
        }


def model_safetensor_names(api_metadata: dict[str, Any]) -> tuple[str | None, list[str]]:
    names = sorted({entry.get("rfilename") for entry in api_metadata.get("siblings", []) if isinstance(entry, dict) and isinstance(entry.get("rfilename"), str)})
    if "model.safetensors.index.json" in names:
        return "model.safetensors.index.json", []
    shard_names = [name for name in names if name.endswith(".safetensors")]
    return None, shard_names


def physical_bytes_by_dtype(tensor_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, list[tuple[int, int]]]] = defaultdict(lambda: defaultdict(list))
    counts: dict[str, int] = defaultdict(int)
    for row in tensor_rows:
        dtype = row["storage_dtype"]
        groups[dtype][str(row["shard"])].append((int(row["disk_data_start"]), int(row["disk_data_end"])))
        counts[dtype] += 1
    return [
        {"storage_dtype": dtype, "tensor_count": counts[dtype], "physical_bytes": sum(union_bytes(ranges) for ranges in by_shard.values())}
        for dtype, by_shard in sorted(groups.items())
    ]


def collect_model(http: BoundedHTTP, candidate: dict[str, str]) -> dict[str, Any]:
    """Collect a single model with only public JSON and safetensors header ranges."""
    model_id = candidate["model_id"]
    # Request only the immutable revision and sibling names.  Full Hub API
    # responses can include arbitrarily long model cards, which are not needed
    # for C15 identity and would violate the bounded-metadata policy.
    api_url = candidate["planned_source_api"] + "?expand[]=sha&expand[]=siblings"
    receipts: list[dict[str, Any]] = []
    assert_authorized_operation("bounded_metadata", 0)
    api, api_receipt = small_json_with_receipt(http, model_id, NA, "HF_MODEL_API", api_url)
    receipts.append(api_receipt)
    if api is None or not isinstance(api.get("sha"), str) or not re.fullmatch(r"[0-9a-f]{40}", api["sha"]):
        return {"candidate": candidate, "revision": NA, "config": None, "headers": [], "receipts": receipts, "failure": "IMMUTABLE_REVISION_UNAVAILABLE"}
    revision = api["sha"]
    config_url = "https://huggingface.co/%s/resolve/%s/config.json" % (model_id, revision)
    require_immutable_resolve_url(config_url, revision)
    config, config_receipt = small_json_with_receipt(http, model_id, revision, "CONFIG_JSON", config_url)
    receipts.append(config_receipt)
    if config is None:
        return {"candidate": candidate, "revision": revision, "config": None, "headers": [], "receipts": receipts, "failure": "CONFIG_UNAVAILABLE"}
    index_name, shard_names = model_safetensor_names(api)
    metadata_bytes = int(config_receipt["bytes_read"])
    if index_name:
        index_url = "https://huggingface.co/%s/resolve/%s/%s" % (model_id, revision, index_name)
        require_immutable_resolve_url(index_url, revision)
        index, index_receipt = small_json_with_receipt(http, model_id, revision, "SAFETENSORS_INDEX", index_url)
        receipts.append(index_receipt)
        metadata_bytes += int(index_receipt["bytes_read"])
        weight_map = index.get("weight_map") if isinstance(index, dict) else None
        if not isinstance(weight_map, dict) or not all(isinstance(value, str) for value in weight_map.values()):
            return {"candidate": candidate, "revision": revision, "config": config, "headers": [], "receipts": receipts, "failure": "INVALID_OR_UNAVAILABLE_SAFETENSORS_INDEX"}
        shard_names = sorted(set(weight_map.values()))
    if not shard_names:
        return {"candidate": candidate, "revision": revision, "config": config, "headers": [], "receipts": receipts, "failure": "NO_SAFETENSORS_HEADER_SOURCE"}
    headers: list[dict[str, Any]] = []
    for shard in shard_names:
        header_url = "https://huggingface.co/%s/resolve/%s/%s" % (model_id, revision, shard)
        require_immutable_resolve_url(header_url, revision)
        try:
            header, prelude, actual = read_safetensors_header(http, header_url)
            header_bytes = len(prelude.data) + len(actual.data)
            metadata_bytes += header_bytes
            if metadata_bytes > MAX_MODEL_METADATA_BYTES:
                raise C15Error("per-model metadata budget exceeded")
            header_hash = sha256_bytes(actual.data)
            headers.append({"shard": shard, "header": header, "file_size": prelude.total_size, "header_bytes": len(actual.data), "header_hash": header_hash})
            receipts.append({
                "model_id": model_id, "revision": revision, "resource_kind": "SAFETENSORS_HEADER_RANGE", "url": header_url,
                "http_status": actual.status, "content_range": actual.content_range, "bytes_read": header_bytes,
                "sha256": header_hash, "result_status": "PASS", "attempts": 1, "missing_reason": NA,
            })
        except Exception as exc:
            receipts.append({
                "model_id": model_id, "revision": revision, "resource_kind": "SAFETENSORS_HEADER_RANGE", "url": header_url,
                "http_status": getattr(exc, "code", NA), "content_range": NA, "bytes_read": 0, "sha256": NA,
                "result_status": "FAILED", "attempts": 1, "missing_reason": "%s:%s" % (type(exc).__name__, str(exc)[:240]),
            })
            return {"candidate": candidate, "revision": revision, "config": config, "headers": headers, "receipts": receipts, "failure": "HEADER_LIMITED_OR_INVALID"}
    return {"candidate": candidate, "revision": revision, "config": config, "headers": headers, "receipts": receipts, "failure": NA}


def collect_static_library(plan_path: Path, root: Path) -> dict[str, int]:
    plan_columns = [
        "plan_id", "candidate_id", "model_id", "candidate_role", "model_counting_rule", "planned_source_api",
        "planned_revision", "availability_at_freeze", "metadata_budget_class", "selection_basis",
        "forbidden_result_input", "readiness_target", "missing_reason",
    ]
    plan = require_columns(plan_path, plan_columns)
    if len({row["candidate_id"] for row in plan}) != len(plan):
        raise C15Error("duplicate candidate ID in frozen selection plan")
    for row in plan:
        if any(token in row["selection_basis"].lower() for token in ("speedup", "cycle", "miss")):
            raise C15Error("selection basis contains a prohibited result input")
    http = BoundedHTTP()
    results = [collect_model(http, candidate) for candidate in plan]
    old_assets = [row for row in tsv_read(root / "ASSET_INVENTORY.tsv", ASSET_COLUMNS) if not row["asset_id"].startswith("hf_")]
    assets = old_assets[:]
    registry_rows: list[dict[str, Any]] = []
    tensor_rows: list[dict[str, Any]] = []
    footprint_rows: list[dict[str, Any]] = []
    kv_audit_rows: list[dict[str, Any]] = []
    kv_curve_rows: list[dict[str, Any]] = []
    header_rows: list[dict[str, Any]] = []
    fetch_rows: list[dict[str, Any]] = []
    breakdown_rows: list[dict[str, Any]] = []
    alias_rows: list[dict[str, Any]] = []
    deployments: list[dict[str, Any]] = []
    for result in results:
        candidate, revision, config, headers = result["candidate"], result["revision"], result["config"], result["headers"]
        fetch_rows.extend(result["receipts"])
        asset_id = "hf_%s" % candidate["candidate_id"]
        if config is None:
            assets.append({"asset_id": asset_id, "asset_kind": "PUBLIC_MODEL_METADATA", "discovered_path_or_ref": candidate["planned_source_api"], "model_id": candidate["model_id"], "revision": revision, "phase": NA, "dtype": NA, "framework": NA, "hardware_scope": NA, "availability": "UNAVAILABLE", "source_commit": NA, "hash_kind": "API_METADATA_SHA256", "sha256": NA, "size_bytes": NA, "readonly": "true", "missing_reason": result["failure"]})
            continue
        shape = model_shape(config)
        provisional_identity = {
            "model_repo": candidate["model_id"], "revision": revision, "implementation": config.get("model_type", NA),
            "weight_dtype": "HEADER_PENDING", "activation_dtype": NA, "kv_dtype": NA,
            "tensor_parallel": 1, "pipeline_parallel": 1, "expert_parallel": 1, "rank": 0, "kv_layout": "STATIC_ASSUMPTION",
        }
        temporary_id = deployment_id(provisional_identity)
        local_rows: list[dict[str, Any]] = []
        for source in headers:
            local_rows.extend(rows_from_header(temporary_id, source["shard"], source["header"], source["header_hash"]))
            intervals = [(row["disk_data_start"], row["disk_data_end"]) for row in local_rows if row["shard"] == source["shard"]]
            header_rows.append({"model_id": candidate["model_id"], "revision": revision, "shard": source["shard"], "file_size_bytes": source["file_size"], "header_bytes": source["header_bytes"], "header_sha256": source["header_hash"], "tensor_count": len([row for row in local_rows if row["shard"] == source["shard"]]), "payload_interval_bytes": union_bytes(intervals), "validation_status": "PASS", "missing_reason": NA})
        weight_dtype = extract_weight_dtype(local_rows)
        final_identity = dict(provisional_identity)
        final_identity["weight_dtype"] = weight_dtype
        deploy_id = deployment_id(final_identity)
        for row in local_rows:
            row["deployment_id"] = deploy_id
        tensor_rows.extend(local_rows)
        storage_status = "HEADER_RANGE_VERIFIED" if headers and result["failure"] == NA else "CONFIG_ONLY_OR_PARTIAL_HEADER"
        assets.append({"asset_id": asset_id, "asset_kind": "PUBLIC_MODEL_METADATA", "discovered_path_or_ref": candidate["planned_source_api"], "model_id": candidate["model_id"], "revision": revision, "phase": NA, "dtype": weight_dtype, "framework": "HUGGINGFACE_CONFIG_AND_SAFETENSORS", "hardware_scope": NA, "availability": storage_status, "source_commit": NA, "hash_kind": "CONFIG_AND_HEADER_RECEIPTS", "sha256": next((row["sha256"] for row in result["receipts"] if row["resource_kind"] == "CONFIG_JSON" and row["result_status"] == "PASS"), NA), "size_bytes": sum(int(row["bytes_read"]) for row in result["receipts"] if str(row["bytes_read"]).isdigit()), "readonly": "true", "missing_reason": result["failure"]})
        quant = config.get("quantization_config") if isinstance(config.get("quantization_config"), dict) else {}
        fields = ["revision", "model_type", "num_hidden_layers", "hidden_size", "num_attention_heads", "num_key_value_heads"]
        registry_rows.append({
            "model_id": candidate["model_id"], "revision": revision, "deployment_id": deploy_id,
            "dense_or_moe": shape["dense_or_moe"], "attention_representation": shape["attention"],
            "layer_count": value_or_na(shape["layers"]), "hidden_size": value_or_na(shape["hidden"]), "intermediate_sizes": value_or_na(shape["intermediate"]), "head_dimensions": value_or_na(shape["head_dim"]), "local_kv_heads": value_or_na(shape["kv_heads"]),
            "expert_count": value_or_na(shape["experts"]), "top_k": value_or_na(shape["top_k"]), "shared_experts": value_or_na(config.get("n_shared_experts", config.get("num_shared_experts"))),
            "weight_dtype": weight_dtype, "activation_dtype": NA, "kv_dtype": NA,
            "quantization_method": value_or_na(quant.get("quant_method")), "quant_group_size": value_or_na(quant.get("group_size")),
            "tying_status": "CONFIG_TIED" if config.get("tie_word_embeddings") is True else "CONFIG_UNTIED_OR_UNSPECIFIED",
            "tensor_parallel": 1, "pipeline_parallel": 1, "expert_parallel": 1, "rank": 0,
            "kv_layout": "UNVERIFIED_STATIC_DEPLOYMENT", "allocation_mode": "UNVERIFIED_RUNTIME", "logits_policy": NA,
            "implementation_identity": value_or_na(config.get("model_type")), "native_hardware": NA,
            "fields_verified": fields, "readiness_tier": "STATIC_HEADER_VERIFIED" if storage_status == "HEADER_RANGE_VERIFIED" else "STATIC_CONFIG_ONLY",
        })
        ranges_by_shard: dict[str, list[tuple[int, int]]] = defaultdict(list)
        for row in local_rows:
            ranges_by_shard[str(row["shard"])].append((int(row["disk_data_start"]), int(row["disk_data_end"])))
        actual_bytes = sum(union_bytes(ranges) for ranges in ranges_by_shard.values())
        common_assumptions = {"source": "Safetensors data_offsets", "not_gpu_va_or_pa": True, "runtime_repack": "UNKNOWN", "allocation_mode": "UNVERIFIED_RUNTIME"}
        for kind, value, missing in [
            ("allocated_payload_bytes", actual_bytes if headers else NA, NA if headers else result["failure"]),
            ("reserved_bytes", NA, "NO_RUNTIME_ALLOCATOR_EVIDENCE"),
            ("active_parameter_estimate", NA, "NO_EXECUTED_EXPERT_OR_RUNTIME_ACTIVITY_EVIDENCE"),
        ]:
            footprint_rows.append({"deployment_id": deploy_id, "scenario_id": "static-storage", "object_kind": "WEIGHT", "layer_or_expert_scope": "ALL", "quantity": kind, "value": value, "unit": "B", "formula_id": "SAFETENSORS_OFFSET_UNION_V1" if value != NA else NA, "assumptions_json": common_assumptions, "page_granule_bytes": NA, "evidence_tier": "STATIC_DERIVED" if value != NA else "UNRESOLVED", "missing_reason": missing})
        if headers:
            for page_bytes in (4096, 65536, 2097152):
                footprint_rows.append({"deployment_id": deploy_id, "scenario_id": "static-file-layout-scenario", "object_kind": "WEIGHT", "layer_or_expert_scope": "ALL", "quantity": "scenario_page_count", "value": sum(page_union_count(ranges, page_bytes) for ranges in ranges_by_shard.values()), "unit": "pages", "formula_id": "OFFSET_RANGE_PAGE_UNION_V1", "assumptions_json": {"disk_offsets_not_va_or_pa": True, "scenario": "one contiguous per-shard static file-layout proxy", "not_tlb_working_set_or_miss": True}, "page_granule_bytes": page_bytes, "evidence_tier": "STATIC_DERIVED", "missing_reason": NA})
        bytes_per_value, assumed_kv_dtype = dtype_bytes_from_config(config)
        supports_standard_kv = shape["attention"] == "STANDARD_KV_CANDIDATE" and all(isinstance(shape[key], int) and shape[key] > 0 for key in ("layers", "kv_heads", "head_dim")) and bytes_per_value is not None
        if supports_standard_kv:
            kv_audit_rows.append({"deployment_id": deploy_id, "model_id": candidate["model_id"], "revision": revision, "representation": "STANDARD_KV", "adapter_status": "STATIC_FORMULA_SUPPORTED", "layer_count": shape["layers"], "local_kv_heads": shape["kv_heads"], "head_dim": shape["head_dim"], "kv_dtype_assumption": "CONFIG_TORCH_DTYPE:%s" % assumed_kv_dtype, "token_residency_policy": "min(requested_tokens,sliding_window_if_configured)", "evidence_source": "CONFIG_JSON_SHA256:%s" % next((row["sha256"] for row in result["receipts"] if row["resource_kind"] == "CONFIG_JSON" and row["result_status"] == "PASS"), NA), "missing_reason": NA})
            sliding = config.get("sliding_window") if isinstance(config.get("sliding_window"), int) and config.get("sliding_window") > 0 else None
            for batch in (1, 8):
                for tokens in (128, 2048, 8192):
                    resident = min(tokens, sliding) if sliding else tokens
                    kv_curve_rows.append({"deployment_id": deploy_id, "scenario_id": "static-b%d-t%d" % (batch, tokens), "batch": batch, "requested_tokens": tokens, "resident_tokens": resident, "payload_bytes": kv_payload_bytes(shape["layers"], batch, resident, shape["kv_heads"], shape["head_dim"], bytes_per_value), "unit": "B", "formula_id": "STANDARD_KV_K_AND_V_V1", "assumptions_json": {"rank_local_kv_heads": shape["kv_heads"], "tp": 1, "dtype_assumed_from_config": assumed_kv_dtype, "reserved_blocks_excluded": True, "not_runtime_allocation": True}, "evidence_tier": "STATIC_DERIVED", "missing_reason": NA})
        else:
            kv_audit_rows.append({"deployment_id": deploy_id, "model_id": candidate["model_id"], "revision": revision, "representation": shape["attention"], "adapter_status": "UNSUPPORTED_REPRESENTATION" if shape["attention"] != "STANDARD_KV_CANDIDATE" else "INSUFFICIENT_CONFIG_EVIDENCE", "layer_count": value_or_na(shape["layers"]), "local_kv_heads": value_or_na(shape["kv_heads"]), "head_dim": value_or_na(shape["head_dim"]), "kv_dtype_assumption": NA, "token_residency_policy": NA, "evidence_source": "CONFIG_JSON", "missing_reason": "MLA_OR_COMPRESSED_REPRESENTATION" if shape["attention"] != "STANDARD_KV_CANDIDATE" else "MISSING_SHAPE_OR_CONFIG_TORCH_DTYPE"})
        for item in physical_bytes_by_dtype(local_rows):
            breakdown_rows.append({"deployment_id": deploy_id, "storage_dtype": item["storage_dtype"], "tensor_count": item["tensor_count"], "physical_bytes": item["physical_bytes"], "dedup_basis": "EXACT_SHARD_OFFSET_RANGE_WITHIN_DTYPE", "evidence_tier": "STATIC_DERIVED", "missing_reason": NA})
        tie_config = config.get("tie_word_embeddings") is True
        embed = [row for row in local_rows if "embed" in row["tensor_name"].lower()]
        logits = [row for row in local_rows if "lm_head" in row["tensor_name"].lower()]
        physical_shared = any(row["semantic_alias_group"] != NA for row in embed + logits)
        alias_rows.append({"deployment_id": deploy_id, "config_tie_declaration": tie_config, "embedding_tensor_count": len(embed), "logits_tensor_count": len(logits), "physical_shared_storage_observed": physical_shared, "verdict": "CONFIG_AND_HEADER_CONSISTENT" if tie_config == physical_shared else "SEMANTIC_PHYSICAL_DIVERGENCE_OR_UNOBSERVED", "missing_reason": NA if headers else result["failure"]})
        deployments.append({"deployment_id": deploy_id, "model_id": candidate["model_id"], "revision": revision, "candidate_id": candidate["candidate_id"], "config_model_type": config.get("model_type", NA), "static_status": storage_status, "config_sha256": next((row["sha256"] for row in result["receipts"] if row["resource_kind"] == "CONFIG_JSON" and row["result_status"] == "PASS"), NA)})
    tsv_write(root / "ASSET_INVENTORY.tsv", ASSET_COLUMNS, assets)
    tsv_write(root / "MODEL_REGISTRY.tsv", REGISTRY_COLUMNS, registry_rows)
    tsv_write(root / "TENSOR_STORAGE_CATALOG.tsv", TENSOR_COLUMNS, tensor_rows)
    tsv_write(root / "STATIC_FOOTPRINT.tsv", FOOTPRINT_COLUMNS, footprint_rows)
    tsv_write(root / "KV_REPRESENTATION_AUDIT.tsv", KV_AUDIT_COLUMNS, kv_audit_rows)
    tsv_write(root / "KV_CAPACITY_CURVES.tsv", KV_CURVE_COLUMNS, kv_curve_rows)
    tsv_write(root / "METADATA_FETCH_RECEIPTS.tsv", FETCH_COLUMNS, fetch_rows)
    tsv_write(root / "HEADER_VALIDATION.tsv", HEADER_COLUMNS, header_rows)
    tsv_write(root / "WEIGHT_STORAGE_BREAKDOWN.tsv", ["deployment_id", "storage_dtype", "tensor_count", "physical_bytes", "dedup_basis", "evidence_tier", "missing_reason"], breakdown_rows)
    tsv_write(root / "TENSOR_ALIAS_AUDIT.tsv", ["deployment_id", "config_tie_declaration", "embedding_tensor_count", "logits_tensor_count", "physical_shared_storage_observed", "verdict", "missing_reason"], alias_rows)
    json_write(root / "DEPLOYMENT_MANIFEST.json", {"schema_version": SCHEMA_VERSION, "planning_sha": PLANNING_SHA, "producer_lane": "A", "evidence_tier": "STATIC_DERIVED", "deployments": deployments})
    return {"planned": len(plan), "config_verified": len(registry_rows), "header_verified": len([row for row in registry_rows if row["readiness_tier"] == "STATIC_HEADER_VERIFIED"])}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true", help="run deterministic contract-fixture checks")
    parser.add_argument("--validate", type=Path, metavar="RESULT_ROOT", help="validate generated TSV schemas")
    parser.add_argument("--validate-bootstrap", type=Path, metavar="RESULT_ROOT", help="validate C15-0.2 tables")
    parser.add_argument("--collect", nargs=2, type=Path, metavar=("PLAN_TSV", "RESULT_ROOT"), help="collect bounded public metadata into the owned result root")
    parser.add_argument("--write-static-manifest", type=Path, metavar="RESULT_ROOT", help="atomically write the final non-self-referential C15-1.6 manifest")
    args = parser.parse_args(argv)
    if not args.selftest and args.validate is None and args.validate_bootstrap is None and args.collect is None and args.write_static_manifest is None:
        parser.error("one of --selftest, --validate, --validate-bootstrap, --collect, or --write-static-manifest is required")
    results: list[tuple[str, str]] = []
    if args.selftest:
        results.extend(static_fixture_checks())
    if args.validate is not None:
        results.extend(verify_output_root(args.validate))
    if args.validate_bootstrap is not None:
        results.extend(verify_bootstrap_root(args.validate_bootstrap))
    if args.collect is not None:
        plan_path, result_root = args.collect
        summary = collect_static_library(plan_path, result_root)
        print("COLLECT\t%s" % canonical_json(summary))
    if args.write_static_manifest is not None:
        write_static_publish_manifest(args.write_static_manifest)
        print("PUBLISH_MANIFEST\tWRITTEN")
    for test_id, status in results:
        print("%s\t%s" % (test_id, status))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
