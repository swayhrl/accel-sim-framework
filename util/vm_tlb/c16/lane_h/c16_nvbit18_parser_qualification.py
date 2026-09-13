#!/usr/bin/env python3
"""Qualify C16's offline decoder against a SHA-closed NVBit 1.8 fixture.

This is deliberately a parser/retention fixture, not a model-analysis tool.
It consumes only an input receipt containing paths and digests, reads the raw
trace outside Git, and emits a compact, explicitly fixture-only receipt.
"""
from __future__ import annotations

import argparse
import csv
import json
import lzma
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .memory_fingerprint import (
        is_metadata_line,
        memory_space,
        parse_trace_record,
        trace_file_metadata,
        validate_trace_format_metadata,
    )
    from .runtime_object_map_v2 import sha256_file
except ImportError:  # pragma: no cover - documented direct CLI invocation.
    from memory_fingerprint import (  # type: ignore[no-redef]
        is_metadata_line,
        memory_space,
        parse_trace_record,
        trace_file_metadata,
        validate_trace_format_metadata,
    )
    from runtime_object_map_v2 import sha256_file  # type: ignore[no-redef]


FIXTURE_LABEL = "NVBIT18_PARSER_QUALIFICATION_FIXTURE_ONLY"
INPUT_SCHEMA = "C16_H_NVBIT18_PARSER_QUALIFICATION_INPUT_V1"
OUTPUT_SCHEMA = "C16_H_NVBIT18_PARSER_QUALIFICATION_RESULT_V1"


class QualificationError(ValueError):
    """The supplied G fixture did not meet its immutable parser contract."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise QualificationError(f"cannot read qualification input {path}: {error}") from error
    if not isinstance(payload, dict) or payload.get("schema_version") != INPUT_SCHEMA:
        raise QualificationError(f"expected schema_version={INPUT_SCHEMA}")
    if payload.get("fixture_label") != FIXTURE_LABEL or payload.get("scientific_model_evidence") is not False:
        raise QualificationError("qualification input must be explicitly fixture-only and non-scientific")
    return payload


def _expect_sha(path: Path, expected: str, what: str) -> str:
    if not path.is_file():
        raise QualificationError(f"missing {what}: {path}")
    actual = sha256_file(path)
    if actual.lower() != expected.lower():
        raise QualificationError(f"{what} SHA256 mismatch: expected {expected}, got {actual}")
    return actual


def _stats_by_trace(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source, skipinitialspace=True))
    required = {"kernel id", "kernel mangled name", "total_reported_insts"}
    if not rows or not required.issubset(rows[0]):
        raise QualificationError(f"unrecognized kernel stats catalog: {path}")
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        trace_name = row["kernel id"].strip()
        if not trace_name or trace_name in result:
            raise QualificationError(f"duplicate/missing trace name in stats catalog {path}")
        result[trace_name] = {key: (value or "").strip() for key, value in row.items() if key is not None}
    return result


def _catalog_names(path: Path) -> list[str]:
    names = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not names or len(names) != len(set(names)):
        raise QualificationError(f"kernel catalog must contain unique nonempty trace names: {path}")
    return names


def _integer(value: str, what: str) -> int:
    try:
        return int(value, 10)
    except ValueError as error:
        raise QualificationError(f"{what} is not decimal: {value!r}") from error


def _parse_trace(path: Path, expected_sha: str, expected_stats: dict[str, str]) -> dict[str, Any]:
    _expect_sha(path, expected_sha, f"trace {path.name}")
    metadata = validate_trace_format_metadata(path, "RAW_CTA_NVBIT18")
    header = trace_file_metadata(path)
    if header != metadata:  # Defensive: avoid a qualification split between two metadata readers.
        raise QualificationError(f"non-deterministic header metadata read for {path}")
    required_header = {"kernel name", "kernel id", "grid dim", "block dim", "nvbit version", "accelsim tracer version"}
    missing = sorted(required_header - set(header))
    if missing:
        raise QualificationError(f"missing trace header fields in {path}: {', '.join(missing)}")
    if header["kernel name"] != expected_stats["kernel mangled name"]:
        raise QualificationError(f"kernel catalog identity mismatch for {path.name}")
    records = 0
    memory_events = 0
    zero_active_memory_events = 0
    active_masks: Counter[str] = Counter()
    widths: Counter[str] = Counter()
    spaces: Counter[str] = Counter()
    kinds: Counter[str] = Counter()
    pages_4k: set[int] = set()
    pages_64k: set[int] = set()
    lines_128b: set[int] = set()
    modulo_16: set[int] = set()
    with lzma.open(path, "rt", encoding="utf-8", errors="strict") as source:
        for line_number, raw in enumerate(source, start=1):
            if is_metadata_line(raw):
                continue
            records += 1
            event = parse_trace_record(raw, line_number, "RAW_CTA_NVBIT18")
            if event is None:
                continue
            memory_events += 1
            active_masks[f"0x{event.active_mask:08x}"] += 1
            widths[str(event.width)] += 1
            spaces[event.memory_space] += 1
            kinds[event.access_kind] += 1
            if not event.lanes:
                zero_active_memory_events += 1
            for lane in event.lanes:
                # Page buckets are structural GPU-VA observations only for explicitly GLOBAL events.
                if event.memory_space != "GLOBAL":
                    continue
                for line in range(lane.address // 128, (lane.address + lane.width - 1) // 128 + 1):
                    lines_128b.add(line)
                    modulo_16.add(line % 16)
                pages_4k.update(range(lane.address // 4096, (lane.address + lane.width - 1) // 4096 + 1))
                pages_64k.update(range(lane.address // 65536, (lane.address + lane.width - 1) // 65536 + 1))
    reported = _integer(expected_stats["total_reported_insts"], f"{path.name} total_reported_insts")
    if records != reported:
        raise QualificationError(
            f"instruction-record count mismatch for {path.name}: parsed {records}, catalog reports {reported}"
        )
    return {
        "trace": path.name,
        "kernel_name": header["kernel name"],
        "kernel_id": _integer(header["kernel id"], f"{path.name} kernel id"),
        "grid_dim": header["grid dim"],
        "block_dim": header["block dim"],
        "nvbit_version": header["nvbit version"],
        "accelsim_tracer_version": header["accelsim tracer version"],
        "instruction_record_count": records,
        "memory_event_count": memory_events,
        "zero_active_memory_event_count": zero_active_memory_events,
        "active_mask_counts": dict(sorted(active_masks.items())),
        "access_width_event_counts": dict(sorted(widths.items(), key=lambda item: int(item[0]))),
        "memory_space_event_counts": dict(sorted(spaces.items())),
        "access_kind_event_counts": dict(sorted(kinds.items())),
        "global_gpu_va_structural_buckets": {
            "unique_4kb": len(pages_4k),
            "unique_64kb": len(pages_64k),
            "unique_128b_lines": len(lines_128b),
            "unique_modulo_16_line_set_projections": len(modulo_16),
            "modulo_projection_label": "PROXY_NOT_MEASURED_HARDWARE_CACHE_SET",
        },
    }


def _semantic_fixture_checks() -> dict[str, Any]:
    """Exercise semantic classes absent from a particular hardware canary.

    These are compact parser fixtures, not observations about the Retry570
    workloads.  They prevent an all-GLOBAL canary from masking a decoder
    regression in LOCAL/SHARED/UNKNOWN or atomic handling.
    """
    records = {
        "GLOBAL": "0 0 0 0 0100 00000001 0 LDG.E.32 0 4 0 0x1000 0",
        "LOCAL": "0 0 0 0 0100 00000001 0 LDL.E.32 0 4 0 0x20 0",
        "SHARED": "0 0 0 0 0100 00000001 0 LDS.E.32 0 4 0 0x30 0",
        "UNKNOWN_SPACE": "0 0 0 0 0100 00000001 0 LD.E.32 0 4 0 0x40 0",
        "ATOMIC": "0 0 0 0 0100 00000001 0 ATOM.E.ADD.32 0 4 0 0x80000 0",
    }
    observed: dict[str, Any] = {}
    for expected, line in records.items():
        event = parse_trace_record(line, 1, "RAW_CTA_NVBIT18")
        if event is None:
            raise QualificationError(f"semantic fixture unexpectedly decoded as non-memory: {expected}")
        if expected != "ATOMIC" and event.memory_space != expected:
            raise QualificationError(f"semantic fixture memory-space mismatch: expected {expected}, got {event.memory_space}")
        if expected == "ATOMIC" and event.access_kind != "ATOMIC":
            raise QualificationError("semantic fixture atomic classification failed")
        observed[expected] = {
            "memory_space": event.memory_space,
            "access_kind": event.access_kind,
            "active_mask": f"0x{event.active_mask:08x}",
            "access_width": event.width,
        }
    if memory_space("LD.E.32") != "UNKNOWN_SPACE":
        raise QualificationError("UNKNOWN_SPACE conservative classification regressed")
    return observed


def qualify(input_path: Path, artifact_root: Path) -> dict[str, Any]:
    source = _load_json(input_path)
    if not artifact_root.is_dir():
        raise QualificationError(f"artifact root does not exist: {artifact_root}")
    tool = source.get("tool_identity")
    groups = source.get("fixture_groups")
    if not isinstance(tool, dict) or not isinstance(groups, list) or not groups:
        raise QualificationError("qualification input requires tool_identity and nonempty fixture_groups")
    tool_path = (artifact_root / str(tool.get("tool_identity_path", ""))).resolve()
    _expect_sha(tool_path, str(tool.get("tool_identity_sha256", "")), "NVBit tool identity")
    parsed_groups: list[dict[str, Any]] = []
    actual_trace_count = 0
    aggregate_spaces: Counter[str] = Counter()
    aggregate_kinds: Counter[str] = Counter()
    for group in groups:
        if not isinstance(group, dict):
            raise QualificationError("fixture group must be an object")
        trace_dir = artifact_root / str(group.get("trace_directory", ""))
        catalog = trace_dir / str(group.get("kernel_catalog", ""))
        stats = trace_dir / str(group.get("kernel_stats", ""))
        _expect_sha(catalog, str(group.get("kernel_catalog_sha256", "")), "kernel catalog")
        _expect_sha(stats, str(group.get("kernel_stats_sha256", "")), "kernel stats catalog")
        catalog_names = _catalog_names(catalog)
        stats_by_trace = _stats_by_trace(stats)
        declared_traces = group.get("traces")
        if not isinstance(declared_traces, list) or not declared_traces:
            raise QualificationError("fixture group needs nonempty traces")
        declared_names = [str(item.get("path", "")) for item in declared_traces if isinstance(item, dict)]
        if set(catalog_names) != set(declared_names) or set(stats_by_trace) != set(declared_names):
            raise QualificationError(f"catalog/stats/receipt trace identity mismatch in {trace_dir}")
        parsed_traces: list[dict[str, Any]] = []
        for declared in declared_traces:
            if not isinstance(declared, dict):
                raise QualificationError("trace declaration must be an object")
            name = str(declared.get("path", ""))
            result = _parse_trace(trace_dir / name, str(declared.get("sha256", "")), stats_by_trace[name])
            parsed_traces.append(result)
            actual_trace_count += 1
            aggregate_spaces.update(result["memory_space_event_counts"])
            aggregate_kinds.update(result["access_kind_event_counts"])
        parsed_groups.append({
            "fixture_group": group.get("fixture_group"),
            "kernel_catalog_identity": {"path": str(catalog), "sha256": sha256_file(catalog), "trace_count": len(catalog_names)},
            "kernel_stats_identity": {"path": str(stats), "sha256": sha256_file(stats)},
            "traces": parsed_traces,
        })
    actual_semantics = {"memory_spaces": dict(sorted(aggregate_spaces.items())), "access_kinds": dict(sorted(aggregate_kinds.items()))}
    return {
        "schema_version": OUTPUT_SCHEMA,
        "fixture_label": FIXTURE_LABEL,
        "scientific_model_evidence": False,
        "source_publication_commit": source["source_publication_commit"],
        "source_transfer_receipt": source["source_transfer_receipt"],
        "input_sha256": sha256_file(input_path),
        "artifact_root": str(artifact_root.resolve()),
        "tool_identity": tool,
        "fixture_trace_count": actual_trace_count,
        "qualification": {
            "status": "PASS_NVBIT18_RAW_CTA_PARSER_QUALIFICATION",
            "kernel_catalog_identity": "PASS",
            "instruction_record_parsing": "PASS_ALL_CATALOG_REPORTED_RECORDS",
            "actual_fixture_semantics": actual_semantics,
            "semantic_parser_fixture_only": _semantic_fixture_checks(),
            "page_line_bucket_semantics": "PASS_GLOBAL_GPU_VA_4KB_64KB_128B_STRUCTURAL_BUCKETS",
            "traceg_order_model": "SET_ONLY_ONLY_NOT_GLOBAL_L2_ORDER",
            "modulo_set_projection": "PROXY_NOT_MEASURED_HARDWARE_CACHE_SET",
            "limitations": [
                "fixture-derived parser qualification only; not model scientific evidence",
                "GPU virtual-address buckets are not hardware page mappings or TLB-miss evidence",
                "NVBit traceg CTA grouping does not establish global L2 arrival order",
            ],
        },
        "fixture_groups": parsed_groups,
    }


def _write_new_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as output:
        json.dump(payload, output, indent=2, sort_keys=True)
        output.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="committed SHA/path-only G fixture receipt")
    parser.add_argument("--artifact-root", type=Path, required=True, help="uncommitted raw fixture root outside Git")
    parser.add_argument("--output", type=Path, required=True, help="new compact fixture-only JSON receipt")
    args = parser.parse_args()
    try:
        _write_new_json(args.output, qualify(args.input, args.artifact_root))
    except (OSError, QualificationError, ValueError) as error:
        raise SystemExit(f"FAIL c16-nvbit18-parser-qualification: {error}") from error
    print(f"PASS c16-nvbit18-parser-qualification output={args.output}")


if __name__ == "__main__":
    main()
