#!/usr/bin/env python3
"""Bounded parallel orchestration for exact one-pass C16 trace summaries.

The scanner produces raw trace-address/128B-line reference proxies.  This
orchestrator optionally calls the separately built accepted-Core mapper and
adds the 16x2048 non-target set-reference histogram.  It never launches the
timing simulator and never writes into the trace tree or B16 run directories.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import os
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "C16_E1_TRACE_REFERENCE_SUMMARY_INDEX_V1"
SET_BINS = 16 * 2048
FULL_KERNEL_COUNT = 4515
FULL_INSTRUCTIONS = 16_313_481_995
FULL_CTAS = 3_653_040
ACCEPTED_CORE_SHA = "a2322069b9701597db7019080b5b54d29518e3a2"
ACCEPTED_CONFIG_SHA256 = "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8"
PAIR = struct.Struct("<QQ")
U64 = struct.Struct("<Q")


class ContractError(ValueError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise ContractError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    require(bool(rows), f"empty TSV: {path}")
    return rows


def integer(row: dict[str, str], names: Iterable[str], label: str, default: int | None = None) -> int:
    for name in names:
        value = row.get(name)
        if value not in (None, ""):
            try:
                return int(value)
            except ValueError as error:
                raise ContractError(f"invalid {label}: {value!r}") from error
    if default is not None:
        return default
    raise ContractError(f"missing {label}; tried {tuple(names)}")


def text(row: dict[str, str], names: Iterable[str], default: str = "") -> str:
    for name in names:
        value = row.get(name)
        if value not in (None, ""):
            return value
    return default


def normalize_sequence(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[int] = set()
    for ordinal, row in enumerate(rows):
        kernel_id = integer(row, ("global_dynamic_order", "kernel_id", "dynamic_kernel"), "kernel ID")
        require(kernel_id not in seen, f"duplicate kernel ID {kernel_id}")
        seen.add(kernel_id)
        layer = integer(row, ("semantic_layer", "layer_index"), "semantic layer", -1)
        profile_range_active = text(
            row, ("profile_range_active", "semantic_range_active")).lower() in ("true", "1", "yes")
        identity = text(row, ("semantic_identity", "role"))
        meaningful_range = (profile_range_active and layer >= 0 and bool(identity) and
                            identity.upper() != "UNKNOWN")
        result.append({
            "ordinal": ordinal,
            "kernel_id": kernel_id,
            "decode_iteration": integer(row, ("decode_iteration", "decode_index", "decode"), "decode", -1),
            "semantic_layer": layer,
            "semantic_identity": identity,
            "exact_function": text(row, ("exact_function", "kernel_name", "function")),
            "stream": integer(row, ("stream", "cuda_stream_id"), "stream", 0),
            "profile_range_active": profile_range_active,
            "semantic_range_active": meaningful_range,
            "source": row,
        })
    runs: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    current_key: tuple[int, int, str] | None = None
    for item in result:
        key = ((item["decode_iteration"], item["semantic_layer"], item["semantic_identity"])
               if item["semantic_range_active"] else None)
        if (key is not None and key == current_key and current and
                item["kernel_id"] == current[-1]["kernel_id"] + 1):
            current.append(item)
            continue
        if current:
            runs.append(current)
        current = [item] if key is not None else []
        current_key = key
    if current:
        runs.append(current)
    for items in runs:
        ids = [item["kernel_id"] for item in items]
        for position, item in enumerate(items):
            item["semantic_range_first_dynamic_kernel"] = ids[0]
            item["semantic_range_last_dynamic_kernel"] = ids[-1]
            item["semantic_range_kernel_count"] = len(ids)
            item["semantic_range_position"] = position
    return result


def validate_full_formal_semantic_ranges(rows: list[dict[str, Any]]) -> None:
    require(len(rows) == FULL_KERNEL_COUNT, "formal semantic validation requires 4515 kernels")
    for decode in (1, 2, 3):
        for layer in range(28):
            selected = [row for row in rows
                        if row["decode_iteration"] == decode and
                        row["semantic_layer"] == layer and
                        row["semantic_identity"] == "up_proj" and
                        row["semantic_range_active"]]
            require(len(selected) == 2,
                    f"D{decode}/L{layer} up_proj range must contain fill+awq")
            ids = [row["kernel_id"] for row in selected]
            require(ids[1] == ids[0] + 1, f"D{decode}/L{layer} up_proj range not contiguous")
            require("FillFunctor" in selected[0]["exact_function"] and
                    selected[1]["exact_function"] == "awq_gemm_kernel",
                    f"D{decode}/L{layer} up_proj range function drift")
            require(all(row["semantic_range_first_dynamic_kernel"] == ids[0] and
                        row["semantic_range_last_dynamic_kernel"] == ids[1] and
                        row["semantic_range_kernel_count"] == 2
                        for row in selected),
                    f"D{decode}/L{layer} semantic boundary annotation drift")


def attach_trace_index(rows: list[dict[str, Any]], path: Path) -> None:
    raw_rows = read_tsv(path)
    indexed: dict[int, dict[str, str]] = {}
    for raw in raw_rows:
        kernel_id = integer(raw, ("global_dynamic_order", "kernel_id"), "trace-index kernel ID")
        require(kernel_id not in indexed, f"duplicate trace-index kernel {kernel_id}")
        indexed[kernel_id] = raw
    for row in rows:
        kernel_id = row["kernel_id"]
        require(kernel_id in indexed, f"trace index misses kernel {kernel_id}")
        authority = indexed[kernel_id]
        row["authority_dynamic_instructions"] = integer(
            authority, ("instructions",), "trace-index instructions")
        row["authority_cta_count"] = integer(
            authority, ("thread_blocks",), "trace-index thread blocks")
        row["authority_trace_artifact"] = text(authority, ("traceg_artifact",))
        row["authority_trace_bytes"] = integer(
            authority, ("size_bytes",), "trace-index size")
        require(text(authority, ("grammar_status",), "TRACEG_GRAMMAR_PASS") == "TRACEG_GRAMMAR_PASS",
                f"kernel {kernel_id}: trace grammar not PASS")


def trace_for(trace_root: Path, kernel_id: int, row: dict[str, Any]) -> Path:
    explicit = text(row["source"], ("trace_artifact", "trace_filename", "filename"))
    if explicit:
        candidate = trace_root / "traces" / explicit
        if not candidate.is_file():
            candidate = trace_root / explicit
        require(candidate.is_file(), f"missing explicit trace {explicit}")
        return candidate
    matches = sorted((trace_root / "traces").glob(f"kernel-{kernel_id}-ctx_*.traceg"))
    matches += sorted((trace_root / "traces").glob(f"kernel-{kernel_id}-ctx_*.traceg.xz"))
    require(len(matches) == 1, f"kernel {kernel_id}: expected one traceg[.xz], got {len(matches)}")
    return matches[0]


def read_pairs(path: Path) -> list[tuple[int, int]]:
    size = path.stat().st_size
    require(size % PAIR.size == 0, f"ragged pair binary: {path}")
    rows = []
    with path.open("rb") as stream:
        for raw in iter(lambda: stream.read(PAIR.size), b""):
            require(len(raw) == PAIR.size, f"short read: {path}")
            rows.append(PAIR.unpack(raw))
    require(rows == sorted(rows), f"pair binary is not sorted: {path}")
    require(len({address for address, _ in rows}) == len(rows), f"duplicate line key: {path}")
    require(all(address % 128 == 0 and count > 0 for address, count in rows),
            f"invalid line/count pair: {path}")
    return rows


def write_u64(path: Path, values: Iterable[int]) -> None:
    with path.open("wb") as stream:
        for value in values:
            stream.write(U64.pack(value))


def read_u64(path: Path) -> list[int]:
    raw = path.read_bytes()
    require(len(raw) % U64.size == 0, f"ragged u64 binary: {path}")
    values = [value for (value,) in struct.iter_unpack("<Q", raw)]
    require(values == sorted(set(values)), f"u64 binary is not sorted unique: {path}")
    return values


def apply_mapper(kernel_dir: Path, mapper: Path, mapper_identity: dict[str, Any]) -> dict[str, Any]:
    unique_lines = read_u64(kernel_dir / "all_unique_lines.u64")
    coordinates: dict[int, tuple[int, int]] = {}
    if unique_lines:
        with tempfile.TemporaryDirectory(prefix="trace-pressure-map-", dir=kernel_dir) as temporary:
            temp = Path(temporary)
            input_path = temp / "lines.u64"
            output_path = temp / "mapping.tsv"
            write_u64(input_path, unique_lines)
            command = [str(mapper), "map", "--input-lines-u64", str(input_path),
                       "--output-tsv", str(output_path)]
            subprocess.run(command, check=True)
            mapped = read_tsv(output_path)
        require(len(mapped) == len(unique_lines), "mapper row count drift")
        for expected_address, row in zip(unique_lines, mapped):
            actual = int(row["line_address_hex"], 0)
            subpartition = int(row["subpartition"])
            set_index = int(row["set_index"])
            require(actual == expected_address, "mapper address order/identity drift")
            require(0 <= subpartition < 16 and 0 <= set_index < 2048,
                    "mapper result out of accepted geometry")
            coordinates[actual] = (subpartition, set_index)

    def histogram(pair_name: str, output_name: str) -> tuple[int, int]:
        values = [0] * SET_BINS
        for address, count in read_pairs(kernel_dir / pair_name):
            require(address in coordinates, f"mapper omitted line {address:#x}")
            subpartition, set_index = coordinates[address]
            values[subpartition * 2048 + set_index] += count
        write_u64(kernel_dir / output_name, values)
        return sum(values), sum(value != 0 for value in values)

    non_target_sum, non_target_nonzero = histogram(
        "non_target_line_refs.u64", "non_target_set_refs.u64")
    all_sum, all_nonzero = histogram("all_line_refs.u64", "all_set_refs.u64")
    segment_sums = {}
    for prefix in ("prefix_", "suffix_"):
        segment_sums[prefix + "non_target"] = histogram(
            prefix + "non_target_line_refs.u64", prefix + "non_target_set_refs.u64")[0]
        segment_sums[prefix + "all"] = histogram(
            prefix + "all_line_refs.u64", prefix + "all_set_refs.u64")[0]
    return {
        "status": "MAPPED_ACCEPTED_CORE",
        "identity": mapper_identity,
        "histogram_file": "non_target_set_refs.u64",
        "histogram_encoding": "32768_LITTLE_ENDIAN_UINT64_INDEX_SP_TIMES_2048_PLUS_SET",
        "histogram_sum": non_target_sum,
        "nonzero_bins": non_target_nonzero,
        "all_histogram_file": "all_set_refs.u64",
        "all_histogram_sum": all_sum,
        "all_nonzero_bins": all_nonzero,
        "segment_histogram_sums": segment_sums,
    }


def validate_histogram_closure(summary: dict[str, Any], mapped: dict[str, Any]) -> None:
    require(mapped["histogram_sum"] == summary["non_target_128b_line_references"],
            "non-target set histogram does not close to non-target line references")
    require(mapped["all_histogram_sum"] == summary["global_128b_line_references"],
            "all set histogram does not close to all line references")
    sums = mapped["segment_histogram_sums"]
    for segment in ("prefix", "suffix"):
        require(sums[segment + "_all"] == summary[segment]["line_references"],
                f"{segment} all-set histogram closure failed")
        require(sums[segment + "_non_target"] ==
                summary[segment]["non_target_line_references"],
                f"{segment} non-target-set histogram closure failed")


def update_summary(path: Path, updates: dict[str, Any]) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    require(document.get("status") == "PASS", f"scanner summary not PASS: {path}")
    document.update(updates)
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return document


def scan_one(spec: dict[str, Any], args: argparse.Namespace,
             sidecar_sha: str, mapper_identity: dict[str, Any] | None) -> dict[str, Any]:
    kernel_id = spec["kernel_id"]
    destination = args.analysis_root / "kernels" / str(kernel_id)
    require(not destination.exists(), f"destination exists; formal scans require a fresh root: {destination}")
    trace = trace_for(args.trace_root, kernel_id, spec)
    temp_parent = args.analysis_root / ".tmp"
    temp_parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f"kernel-{kernel_id}-", dir=temp_parent))
    scan_dir = temporary / "scan"
    command = [str(args.scanner), "--trace", str(trace), "--sidecar", str(args.sidecar),
               "--output", str(scan_dir), "--kernel-id", str(kernel_id),
               "--decode", str(spec["decode_iteration"]),
               "--semantic-layer", str(spec["semantic_layer"]),
               "--semantic-identity", spec["semantic_identity"],
               "--exact-function", spec["exact_function"]]
    try:
        subprocess.run(command, check=True)
        updates: dict[str, Any] = {
            "trace_artifact": trace.name,
            "trace_compressed_bytes": trace.stat().st_size,
            "trace_sequence_ordinal": spec["ordinal"],
            "trace_sidecar_sha256": sidecar_sha,
            "stream": spec["stream"],
            "profile_range_active": spec["profile_range_active"],
            "semantic_range_active": spec["semantic_range_active"],
        }
        for key in ("semantic_range_first_dynamic_kernel", "semantic_range_last_dynamic_kernel",
                    "semantic_range_kernel_count", "semantic_range_position"):
            if key in spec:
                updates[key] = spec[key]
        source_sha = text(spec["source"], ("sha256", "trace_sha256", "artifact_sha256"))
        if source_sha:
            require(len(source_sha) == 64, f"kernel {kernel_id}: malformed trace SHA")
            updates["trace_sha256_from_authority"] = source_sha
        summary = update_summary(scan_dir / "summary.json", updates)
        if not args.skip_trace_index_validation:
            require(summary["dynamic_instructions"] == spec["authority_dynamic_instructions"],
                    f"kernel {kernel_id}: scanner/index instruction mismatch")
            require(summary["cta_count"] == spec["authority_cta_count"],
                    f"kernel {kernel_id}: scanner/index CTA mismatch")
            require(trace.name == spec["authority_trace_artifact"],
                    f"kernel {kernel_id}: trace artifact identity mismatch")
            require(trace.stat().st_size == spec["authority_trace_bytes"],
                    f"kernel {kernel_id}: compressed byte size mismatch")
            summary = update_summary(scan_dir / "summary.json", {
                "trace_index_validation": {
                    "status": "PASS",
                    "dynamic_instructions": spec["authority_dynamic_instructions"],
                    "cta_count": spec["authority_cta_count"],
                    "trace_artifact": spec["authority_trace_artifact"],
                    "compressed_bytes": spec["authority_trace_bytes"],
                }
            })
        if args.skip_mapper:
            for prefix in ("", "prefix_", "suffix_"):
                write_u64(scan_dir / f"{prefix}non_target_set_refs.u64", [0] * SET_BINS)
                write_u64(scan_dir / f"{prefix}all_set_refs.u64", [0] * SET_BINS)
            summary = update_summary(scan_dir / "summary.json", {
                "mapper": {"status": "SKIPPED", "reason": "--skip-mapper"},
                "non_target_set_refs_semantically_valid": False,
            })
        else:
            require(mapper_identity is not None, "mapper identity missing")
            mapped = apply_mapper(scan_dir, args.mapper, mapper_identity)
            validate_histogram_closure(summary, mapped)
            summary = update_summary(scan_dir / "summary.json", {
                "mapper": mapped,
                "non_target_set_refs_semantically_valid": True,
            })
        destination.parent.mkdir(parents=True, exist_ok=True)
        os.replace(scan_dir, destination)
        return summary
    finally:
        shutil.rmtree(temporary, ignore_errors=True)


def build_index(args: argparse.Namespace, rows: list[dict[str, Any]],
                summaries: list[dict[str, Any]], sidecar_sha: str,
                mapper_identity: dict[str, Any] | None) -> None:
    ordered = sorted(zip(rows, summaries), key=lambda pair: pair[0]["ordinal"])
    ids = [spec["kernel_id"] for spec, _ in ordered]
    document = {
        "schema": SCHEMA,
        "status": "PASS",
        "claim_boundary": "TRACE_ADDRESS_REFERENCE_AND_128B_LINE_REFERENCE_PROXY_ONLY_NOT_ACTUAL_L2_TRAFFIC",
        "kernel_count": len(ordered),
        "first_kernel_id": ids[0],
        "last_kernel_id": ids[-1],
        "sequence_sha256": sha256(args.kernel_sequence),
        "sidecar_sha256": sidecar_sha,
        "scanner_sha256": sha256(args.scanner),
        "mapper": {"status": "SKIPPED"} if args.skip_mapper else mapper_identity,
        "workers": args.workers,
        "kernel_summaries": [f"kernels/{kernel_id}/summary.json" for kernel_id in ids],
        "totals": {
            key: sum(int(summary[key]) for _, summary in ordered)
            for key in ("dynamic_instructions", "cta_count", "global_memory_instructions",
                        "global_address_references", "global_128b_line_references",
                        "target_128b_line_references", "non_target_128b_line_references",
                        "target_address_references", "non_target_address_references")
        },
    }
    if not args.skip_trace_index_validation:
        authority_instructions = sum(row["authority_dynamic_instructions"] for row, _ in ordered)
        authority_ctas = sum(row["authority_cta_count"] for row, _ in ordered)
        require(document["totals"]["dynamic_instructions"] == authority_instructions,
                "top-level scanner/index instruction closure failed")
        require(document["totals"]["cta_count"] == authority_ctas,
                "top-level scanner/index CTA closure failed")
        document["trace_index_validation"] = {
            "status": "PASS", "path": str(args.trace_index),
            "sha256": sha256(args.trace_index),
            "dynamic_instructions": authority_instructions, "cta_count": authority_ctas,
        }
        if args.require_kernel_count == FULL_KERNEL_COUNT:
            require(authority_instructions == FULL_INSTRUCTIONS,
                    "qualified full-sequence instruction authority drift")
            require(authority_ctas == FULL_CTAS, "qualified full-sequence CTA authority drift")
            document["qualified_full_sequence_closure"] = {
                "status": "PASS", "kernel_count": FULL_KERNEL_COUNT,
                "dynamic_instructions": FULL_INSTRUCTIONS, "cta_count": FULL_CTAS,
            }
    (args.analysis_root / "TRACE_REFERENCE_SUMMARY.json").write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fields = ["sequence_ordinal", "kernel_id", "decode_iteration", "semantic_layer",
              "semantic_identity", "exact_function", "profile_range_active",
              "semantic_range_active",
              "semantic_range_first_dynamic_kernel", "semantic_range_last_dynamic_kernel",
              "semantic_range_kernel_count", "semantic_range_position",
              "dynamic_instructions", "cta_count",
              "global_memory_instructions", "global_address_references",
              "target_address_references", "non_target_address_references",
              "unique_128b_lines", "target_unique_128b_lines", "non_target_unique_128b_lines",
              "expected_target_class", "expected_target_observed"]
    with (args.analysis_root / "TRACE_REFERENCE_SUMMARY.tsv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for spec, summary in ordered:
            row = {key: summary.get(key, "") for key in fields}
            row["sequence_ordinal"] = spec["ordinal"]
            writer.writerow(row)


def mapper_identity(args: argparse.Namespace) -> dict[str, Any] | None:
    if args.skip_mapper:
        return None
    require(args.mapper.is_file() and os.access(args.mapper, os.X_OK), f"mapper is not executable: {args.mapper}")
    provenance_run = subprocess.run([str(args.mapper), "--provenance"], text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    check=True)
    provenance = {}
    for raw in provenance_run.stdout.splitlines():
        key, separator, value = raw.partition("=")
        require(separator == "=" and key and value, f"malformed mapper provenance: {raw!r}")
        provenance[key] = value
    require(provenance.get("accepted_core_sha") == ACCEPTED_CORE_SHA,
            "mapper Core authority drift")
    require(provenance.get("accepted_config_sha256") == ACCEPTED_CONFIG_SHA256,
            "mapper config authority drift")
    identity: dict[str, Any] = {
        "mapper_cli": str(args.mapper),
        "mapper_cli_sha256": sha256(args.mapper),
        "provenance": provenance,
    }
    if args.mapper_identity_json:
        raw = json.loads(args.mapper_identity_json.read_text(encoding="utf-8"))
        require(isinstance(raw, dict), "mapper identity JSON must be an object")
        identity["authority"] = raw
        identity["authority_sha256"] = sha256(args.mapper_identity_json)
    return identity


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scanner", type=Path)
    parser.add_argument("--mapper", type=Path)
    parser.add_argument("--mapper-identity-json", type=Path)
    parser.add_argument("--skip-mapper", action="store_true")
    parser.add_argument("--trace-root", type=Path, required=True)
    parser.add_argument("--kernel-sequence", type=Path, required=True)
    parser.add_argument("--trace-index", type=Path)
    parser.add_argument("--skip-trace-index-validation", action="store_true")
    parser.add_argument("--sidecar", type=Path, required=True)
    parser.add_argument("--sidecar-sha256")
    parser.add_argument("--analysis-root", type=Path)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int)
    parser.add_argument("--require-kernel-count", type=int, default=0)
    args = parser.parse_args()
    if not args.preflight_only:
        require(args.scanner is not None and args.scanner.is_file() and
                os.access(args.scanner, os.X_OK), f"scanner is not executable: {args.scanner}")
        require(args.analysis_root is not None, "--analysis-root required unless --preflight-only")
        require(args.skip_mapper or args.mapper is not None, "--mapper required unless --skip-mapper")
    require(args.workers > 0 and args.workers <= 64, "workers must be 1..64")
    return args


def main() -> int:
    args = parse_args()
    sidecar_sha = sha256(args.sidecar)
    if args.sidecar_sha256:
        require(sidecar_sha == args.sidecar_sha256, "sidecar SHA drift")
    all_rows = normalize_sequence(read_tsv(args.kernel_sequence))
    if not args.skip_trace_index_validation:
        if args.trace_index is None:
            args.trace_index = args.trace_root / "control" / "TRACE_ARTIFACT_INDEX.tsv"
        require(args.trace_index.is_file(), f"missing trace artifact index: {args.trace_index}")
        attach_trace_index(all_rows, args.trace_index)
    if args.require_kernel_count:
        require(len(all_rows) == args.require_kernel_count,
                f"sequence count {len(all_rows)} != {args.require_kernel_count}")
        if args.require_kernel_count == FULL_KERNEL_COUNT:
            require([row["kernel_id"] for row in all_rows] == list(range(2926, 7441)),
                    "qualified full sequence must be exact ordered kernel IDs 2926..7440")
            validate_full_formal_semantic_ranges(all_rows)
    if args.preflight_only:
        print(json.dumps({
            "status": "PASS", "preflight_only": True, "kernel_count": len(all_rows),
            "sequence_sha256": sha256(args.kernel_sequence),
            "trace_index_sha256": (sha256(args.trace_index)
                                   if not args.skip_trace_index_validation else None),
            "sidecar_sha256": sidecar_sha,
        }, sort_keys=True))
        return 0
    stop = len(all_rows) if args.stop is None else args.stop
    require(0 <= args.start <= stop <= len(all_rows), "invalid [start, stop) range")
    rows = all_rows[args.start:stop]
    require(bool(rows), "selected sequence is empty")
    require(not args.analysis_root.exists(), "analysis root exists; formal scans require a fresh root")
    args.analysis_root.mkdir(parents=True, exist_ok=True)
    identity = mapper_identity(args)
    summaries_by_id: dict[int, dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        pending = {executor.submit(scan_one, row, args, sidecar_sha, identity): row for row in rows}
        for future in concurrent.futures.as_completed(pending):
            row = pending[future]
            summary = future.result()
            summaries_by_id[row["kernel_id"]] = summary
            print(f"TRACE_PRESSURE_KERNEL_PASS {row['kernel_id']}", flush=True)
    summaries = [summaries_by_id[row["kernel_id"]] for row in rows]
    build_index(args, rows, summaries, sidecar_sha, identity)
    print(json.dumps({"status": "PASS", "kernel_count": len(rows),
                      "analysis_root": str(args.analysis_root)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
