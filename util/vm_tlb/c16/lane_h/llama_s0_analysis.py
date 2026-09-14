#!/usr/bin/env python3
"""Set-only analysis for explicitly selected historical Llama NVBit records.

This is intentionally separate from :mod:`memory_fingerprint`.  The latter
only consumes a C16 committed, manifest-bound exchange.  This utility is for
an *exploratory* raw index whose inputs have been admitted as historical but
not as C16 scientific rows.  It accepts an exact trace SHA through its caller,
but does not turn that fact into a formal provenance admission.

The input schema is ``c16-h-llama-exploratory-input-v1``.  Each entry names a
trace, its exact selected instruction PC, and the expected kernel substring.
All results are address-set structural metrics.  TRACEG file order is never
used as a global (or local) temporal order.
"""
from __future__ import annotations

import argparse
import csv
import json
import lzma
import math
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .memory_fingerprint import TraceParseError, is_metadata_line, parse_trace_record
except ImportError:  # pragma: no cover - direct CLI invocation
    from memory_fingerprint import TraceParseError, is_metadata_line, parse_trace_record  # type: ignore[no-redef]


INPUT_SCHEMA = "c16-h-llama-exploratory-input-v1"
SUMMARY_COLUMNS = [
    "capture_id", "trace_path", "target_pc", "kernel_identity", "record_count", "address_record_count",
    "active_lane_count", "requested_bytes", "unique_exact_gpu_va", "unique_32b_blocks",
    "unique_64b_blocks", "unique_128b_lines", "unique_4k_va_buckets", "unique_64k_va_buckets",
    "unique_2m_va_buckets", "read_address_records", "write_address_records", "atomic_address_records",
    "mean_active_lanes_per_request", "mean_32b_blocks_per_request", "mean_64b_blocks_per_request",
    "mean_128b_blocks_per_request", "contiguous_lane_pair_fraction", "covered_128b_block_requested_byte_proxy",
    "top1_line_access_fraction", "top5_line_access_fraction", "top10pct_line_access_fraction",
    "top1_page_access_fraction", "repeated_exact_address_fraction", "repeated_line_fraction",
    "repeated_4k_page_fraction", "memory_space", "address_domain", "object_attribution", "order_model",
]
OVERLAP_COLUMNS = [
    "left_capture_id", "right_capture_id", "granularity", "intersection", "union", "jaccard",
    "left_containment", "right_containment", "order_model",
]


def _open_text(path: Path):
    return lzma.open(path, "rt", encoding="utf-8", errors="strict") if path.suffix == ".xz" else path.open("rt", encoding="utf-8")


def _pc(raw: str, trace_format: str) -> int:
    """Extract the PC without confusing an optional RAW_CTA prefix for it."""
    prefix_widths = {
        "TRACEG": 0,
        "RAW_CTA": 4,
        "RAW_CTA_CORE": 6,
        "RAW_CTA_LINEINFO": 5,
        "RAW_CTA_CORE_LINEINFO": 7,
    }
    try:
        token = raw.split()[prefix_widths[trace_format]]
    except (KeyError, IndexError) as error:
        raise TraceParseError(f"missing or unsupported trace-format PC: {trace_format!r}") from error
    try:
        return int(token, 16)
    except ValueError as error:
        raise TraceParseError(f"instruction PC is not hexadecimal: {token!r}") from error


def _top_fraction(counter: Counter[int], count: int) -> float:
    total = sum(counter.values())
    return sum(value for _, value in counter.most_common(count)) / total if total else 0.0


def _repeated_fraction(counter: Counter[int]) -> float:
    total = sum(counter.values())
    return sum(value for value in counter.values() if value > 1) / total if total else 0.0


def analyze_trace(
    trace_path: Path,
    target_pc: int,
    expected_kernel_substring: str,
    trace_format: str = "TRACEG",
    expected_opcode: str | None = None,
) -> tuple[dict[str, Any], dict[str, set[int]]]:
    """Analyze one selected static instruction without relying on record order."""
    kernel_identity = ""
    addresses: set[int] = set()
    lines: set[int] = set()
    pages_4k: set[int] = set()
    pages_64k: set[int] = set()
    pages_2m: set[int] = set()
    blocks_32: set[int] = set()
    blocks_64: set[int] = set()
    address_frequency: Counter[int] = Counter()
    line_frequency: Counter[int] = Counter()
    page_frequency: Counter[int] = Counter()
    access_counts: Counter[str] = Counter()
    active_lanes: list[int] = []
    request_blocks: dict[int, list[int]] = {32: [], 64: [], 128: []}
    lane_pairs = 0
    contiguous_lane_pairs = 0
    requested_bytes = 0
    record_count = 0
    address_record_count = 0

    with _open_text(trace_path) as source:
        for source_record, raw in enumerate(source, start=1):
            if raw.startswith("-kernel name ="):
                kernel_identity = raw.split("=", 1)[1].strip()
                continue
            if is_metadata_line(raw) or _pc(raw, trace_format) != target_pc:
                continue
            event = parse_trace_record(raw, source_record, trace_format)
            if event is None:
                continue
            if event.memory_space != "GLOBAL":
                raise TraceParseError(f"{trace_path}:{source_record}: selected target is not explicit GLOBAL memory")
            if expected_opcode is not None and event.opcode != expected_opcode:
                raise TraceParseError(
                    f"{trace_path}:{source_record}: selected target opcode {event.opcode!r} "
                    f"does not match expected {expected_opcode!r}"
                )
            record_count += 1
            active_lanes.append(len(event.lanes))
            lane_addresses = [lane.address for lane in event.lanes]
            for block_size in request_blocks:
                request_blocks[block_size].append(len({address // block_size for address in lane_addresses}))
            for left, right in zip(lane_addresses, lane_addresses[1:]):
                lane_pairs += 1
                contiguous_lane_pairs += int(right - left == event.width)
            for lane in event.lanes:
                address = lane.address
                address_record_count += 1
                requested_bytes += lane.width
                access_counts[event.access_kind] += 1
                addresses.add(address)
                line = address // 128
                page = address // 4096
                addresses.add(address)
                blocks_32.add(address // 32)
                blocks_64.add(address // 64)
                lines.add(line)
                pages_4k.add(page)
                pages_64k.add(address // (64 * 1024))
                pages_2m.add(address // (2 * 1024 * 1024))
                address_frequency[address] += 1
                line_frequency[line] += 1
                page_frequency[page] += 1
    if not kernel_identity:
        raise TraceParseError(f"{trace_path}: missing NVBit kernel header")
    if expected_kernel_substring not in kernel_identity:
        raise TraceParseError(f"{trace_path}: kernel header does not match expected identity substring")
    if not record_count:
        raise TraceParseError(f"{trace_path}: selected PC 0x{target_pc:x} emitted no GLOBAL memory records")
    summary: dict[str, Any] = {
        "kernel_identity": kernel_identity,
        "record_count": record_count,
        "address_record_count": address_record_count,
        "active_lane_count": address_record_count,
        "requested_bytes": requested_bytes,
        "unique_exact_gpu_va": len(addresses),
        "unique_32b_blocks": len(blocks_32),
        "unique_64b_blocks": len(blocks_64),
        "unique_128b_lines": len(lines),
        "unique_4k_va_buckets": len(pages_4k),
        "unique_64k_va_buckets": len(pages_64k),
        "unique_2m_va_buckets": len(pages_2m),
        "read_address_records": access_counts["READ"],
        "write_address_records": access_counts["WRITE"],
        "atomic_address_records": access_counts["ATOMIC"],
        "mean_active_lanes_per_request": address_record_count / record_count,
        "mean_32b_blocks_per_request": sum(request_blocks[32]) / record_count,
        "mean_64b_blocks_per_request": sum(request_blocks[64]) / record_count,
        "mean_128b_blocks_per_request": sum(request_blocks[128]) / record_count,
        "contiguous_lane_pair_fraction": contiguous_lane_pairs / lane_pairs if lane_pairs else 0.0,
        "covered_128b_block_requested_byte_proxy": requested_bytes / (128 * sum(request_blocks[128])),
        "top1_line_access_fraction": _top_fraction(line_frequency, 1),
        "top5_line_access_fraction": _top_fraction(line_frequency, 5),
        "top10pct_line_access_fraction": _top_fraction(line_frequency, max(1, math.ceil(len(lines) * 0.1))),
        "top1_page_access_fraction": _top_fraction(page_frequency, 1),
        "repeated_exact_address_fraction": _repeated_fraction(address_frequency),
        "repeated_line_fraction": _repeated_fraction(line_frequency),
        "repeated_4k_page_fraction": _repeated_fraction(page_frequency),
        "memory_space": "GLOBAL",
        "address_domain": "GPU_VA_OBSERVED",
        "object_attribution": "UNKNOWN_RUNTIME (no C16 receipt-bound temporal object map)",
        "order_model": "SET_ONLY",
    }
    return summary, {
        "exact_address": addresses,
        "32b_block": blocks_32,
        "64b_block": blocks_64,
        "128b_line": lines,
        "4k_va_bucket": pages_4k,
        "64k_va_bucket": pages_64k,
        "2m_va_bucket": pages_2m,
    }


def overlap_rows(results: dict[str, dict[str, set[int]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    identifiers = list(results)
    for index, left_id in enumerate(identifiers):
        for right_id in identifiers[index + 1:]:
            for granularity in ("exact_address", "32b_block", "64b_block", "128b_line", "4k_va_bucket", "64k_va_bucket", "2m_va_bucket"):
                left, right = results[left_id][granularity], results[right_id][granularity]
                intersection = len(left & right)
                union = len(left | right)
                rows.append({
                    "left_capture_id": left_id,
                    "right_capture_id": right_id,
                    "granularity": granularity,
                    "intersection": intersection,
                    "union": union,
                    "jaccard": intersection / union if union else 0.0,
                    "left_containment": intersection / len(left) if left else 0.0,
                    "right_containment": intersection / len(right) if right else 0.0,
                    "order_model": "SET_ONLY",
                })
    return rows


def three_way_overlap_row(
    results: dict[str, dict[str, set[int]]],
    left_id: str,
    middle_id: str,
    right_id: str,
) -> list[dict[str, Any]]:
    """Return explicit three-way set relations; no trace ordering is implied."""
    rows: list[dict[str, Any]] = []
    for granularity in ("exact_address", "32b_block", "64b_block", "128b_line", "4k_va_bucket", "64k_va_bucket", "2m_va_bucket"):
        left = results[left_id][granularity]
        middle = results[middle_id][granularity]
        right = results[right_id][granularity]
        intersection = len(left & middle & right)
        union = len(left | middle | right)
        rows.append({
            "left_capture_id": left_id,
            "middle_capture_id": middle_id,
            "right_capture_id": right_id,
            "granularity": granularity,
            "intersection": intersection,
            "union": union,
            "jaccard": intersection / union if union else 0.0,
            "left_containment": intersection / len(left) if left else 0.0,
            "middle_containment": intersection / len(middle) if middle else 0.0,
            "right_containment": intersection / len(right) if right else 0.0,
            "order_model": "SET_ONLY",
        })
    return rows


def _write_tsv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=columns, delimiter="\t", extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute exploratory SET_ONLY Llama selected-instruction address metrics.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overlap-output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if payload.get("schema_version") != INPUT_SCHEMA or not isinstance(payload.get("entries"), list):
        raise TraceParseError(f"expected {INPUT_SCHEMA} with a nonempty entries array")
    summaries: list[dict[str, Any]] = []
    sets: dict[str, dict[str, set[int]]] = {}
    for raw in payload["entries"]:
        capture_id = raw["capture_id"]
        target_pc = int(raw["target_pc"], 0)
        summary, capture_sets = analyze_trace(
            Path(raw["trace_path"]),
            target_pc,
            raw["expected_kernel_substring"],
            raw.get("trace_format", "TRACEG"),
            raw.get("expected_opcode"),
        )
        summary.update({"capture_id": capture_id, "trace_path": raw["trace_path"], "target_pc": f"0x{target_pc:04x}"})
        summaries.append(summary)
        sets[capture_id] = capture_sets
    _write_tsv(args.output, SUMMARY_COLUMNS, summaries)
    _write_tsv(args.overlap_output, OVERLAP_COLUMNS, overlap_rows(sets))
    print(f"PASS c16-h-llama-exploratory-analysis captures={len(summaries)} order_model=SET_ONLY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
