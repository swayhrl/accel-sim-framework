#!/usr/bin/env python3
"""Export bounded M4C/M4B telemetry records into provenance-bound TSVs.

The simulator log is intentionally the only runtime telemetry source.  This
exporter performs no replay and emits compact aggregate/kernel/window tables.
"""

import argparse
import csv
import hashlib
import re
from pathlib import Path


REQUIRED = (
    "KERNEL_MEMORY_STATS.tsv",
    "WINDOW_MEMORY_STATS.tsv",
    "L1D_OBJECT_STATS.tsv",
    "L1D_FAIL_PRESSURE.tsv",
    "L2_REQUEST_CLASS_STATS.tsv",
    "L2_QUEUE_PRESSURE.tsv",
    "L2_CLASS_REPLACEMENT_MATRIX.tsv",
    "DRAM_REQUEST_CLASS_STATS.tsv",
    "CROSS_LAYER_OUTCOME_MATRIX.tsv",
    "TELEMETRY_SCHEMA.md",
)
PROVENANCE_COLUMNS = (
    "roi", "trace_policy", "run_dir", "framework_head", "core_head",
    "run_manifest_sha256", "telemetry_schema",
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def parse_manifest(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text().splitlines()[1:]:
        if "\t" not in line:
            continue
        key, value = line.split("\t", 1)
        result[key] = value
    return result


def semantic_identity(lines: list[str]) -> dict[int, tuple[str, str]]:
    """Bind telemetry's deterministic kernel index to trace filename/name."""
    result: dict[int, tuple[str, str]] = {}
    current_trace = "UNKNOWN"
    current_name = "UNKNOWN"
    seen_trace = -1
    for line in lines:
        if line.startswith("Processing kernel "):
            seen_trace += 1
            current_trace = Path(line[len("Processing kernel "):]).name
            current_name = "UNKNOWN"
        elif line.startswith("-kernel name = "):
            current_name = line[len("-kernel name = "):]
            if seen_trace >= 0:
                result[seen_trace] = (current_trace, current_name)
    return result


def parse_records(lines: list[str]) -> list[tuple[str, list[str]]]:
    records: list[tuple[str, list[str]]] = []
    for line in lines:
        if not line.startswith("m4c_telemetry") or "\t" not in line:
            continue
        fields = line.split("\t")
        records.append((fields[0], fields[1:]))
    return records


def record_scope(fields: list[str]) -> str:
    return fields[0] if fields and fields[0] in (
        "KERNEL", "FIXED_WINDOW", "FIXED_WINDOW_PARTIAL") else ""


def indexed_identity(fields: list[str], identities: dict[int, tuple[str, str]]) -> tuple[str, str, str]:
    if len(fields) < 3:
        return "", "UNKNOWN", "UNKNOWN"
    index = fields[2]
    try:
        trace, name = identities.get(int(index), ("UNKNOWN", "UNKNOWN"))
    except ValueError:
        trace, name = "UNKNOWN", "UNKNOWN"
    return index, trace, name


def write_tsv(path: Path, provenance: list[str], header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow([*PROVENANCE_COLUMNS, *header])
        for row in rows:
            writer.writerow([*provenance, *row])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--trace-policy", required=True,
                        choices=("COMPUTE_ONLY_TP_PARTITION", "FULL_RANK0"))
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    manifest_path = run_dir / "RUN_MANIFEST.tsv"
    log_path = run_dir / "run.log"
    if not manifest_path.is_file() or not log_path.is_file():
        fail("run directory lacks RUN_MANIFEST.tsv or run.log")
    manifest = parse_manifest(manifest_path)
    for key in ("roi", "framework_head", "core_head"):
        if key not in manifest:
            fail(f"run manifest misses {key}")
    lines = log_path.read_text(errors="strict").splitlines()
    if "m4c_telemetry_schema = M4C_MEMORY_TELEMETRY_V1" not in lines:
        fail("missing M4C_MEMORY_TELEMETRY_V1 schema marker")
    records = parse_records(lines)
    if not records:
        fail("no structured telemetry records")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = [name for name in REQUIRED if (output_dir / name).exists()]
    if existing:
        fail("refusing to overwrite artifact(s): " + ", ".join(existing))
    provenance = [
        manifest["roi"], args.trace_policy, str(run_dir),
        manifest["framework_head"], manifest["core_head"],
        hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "M4C_MEMORY_TELEMETRY_V1",
    ]
    identities = semantic_identity(lines)

    normalized_kernel: list[list[str]] = []
    normalized_window: list[list[str]] = []
    l1_rows: list[list[str]] = []
    l2_rows: list[list[str]] = []
    queue_rows: list[list[str]] = []
    replacement_rows: list[list[str]] = []
    dram_rows: list[list[str]] = []
    cross_rows: list[list[str]] = []

    for kind, fields in records:
        scope = record_scope(fields)
        if not scope:
            continue
        index, trace, kernel_name = indexed_identity(fields, identities)
        normalized = [kind, scope, index, trace, kernel_name, *fields[3:]]
        if scope == "KERNEL":
            normalized_kernel.append(normalized)
        else:
            normalized_window.append(normalized)
        if kind == "m4c_telemetry":
            l1_rows.append([scope, index, trace, kernel_name, *fields[3:]])
        elif kind == "m4c_telemetry_l2":
            l2_rows.append([scope, index, trace, kernel_name, *fields[3:]])
        elif kind == "m4c_telemetry_l2_queue":
            queue_rows.append([scope, index, trace, kernel_name, *fields[3:]])
        elif kind == "m4c_telemetry_l2_replacement":
            replacement_rows.append([scope, index, trace, kernel_name, *fields[3:]])
        elif kind in ("m4c_telemetry_dram", "m4c_telemetry_dram_rw"):
            dram_rows.append([kind, scope, index, trace, kernel_name, *fields[3:]])
        elif kind in ("m4c_telemetry_cross_l1", "m4c_telemetry_cross_l1_l2"):
            cross_rows.append([kind, scope, index, trace, kernel_name, *fields[3:]])

    write_tsv(output_dir / "KERNEL_MEMORY_STATS.tsv", provenance,
              ["record_type", "scope", "semantic_kernel_index", "trace_filename",
               "kernel_name", "payload"],
              [row[:5] + ["\t".join(row[5:])] for row in normalized_kernel])
    write_tsv(output_dir / "WINDOW_MEMORY_STATS.tsv", provenance,
              ["record_type", "scope", "semantic_kernel_index", "trace_filename",
               "kernel_name", "payload"],
              [row[:5] + ["\t".join(row[5:])] for row in normalized_window])
    write_tsv(output_dir / "L1D_OBJECT_STATS.tsv", provenance,
              ["scope", "semantic_kernel_index", "trace_filename", "kernel_name",
               "object_or_request_class", "outcome", "count"], l1_rows)
    write_tsv(output_dir / "L2_REQUEST_CLASS_STATS.tsv", provenance,
              ["scope", "semantic_kernel_index", "trace_filename", "kernel_name",
               "request_class", "outcome", "count"], l2_rows)
    write_tsv(output_dir / "L2_QUEUE_PRESSURE.tsv", provenance,
              ["scope", "semantic_kernel_index", "trace_filename", "kernel_name",
               "samples", "icnt_to_l2_total", "l2_to_dram_total",
               "dram_to_l2_total", "l2_to_icnt_total", "icnt_to_l2_hwm",
               "l2_to_dram_hwm", "dram_to_l2_hwm", "l2_to_icnt_hwm"], queue_rows)
    write_tsv(output_dir / "L2_CLASS_REPLACEMENT_MATRIX.tsv", provenance,
              ["scope", "semantic_kernel_index", "trace_filename", "kernel_name",
               "incoming_class", "victim_class", "count"], replacement_rows)
    write_tsv(output_dir / "DRAM_REQUEST_CLASS_STATS.tsv", provenance,
              ["record_type", "scope", "semantic_kernel_index", "trace_filename",
               "kernel_name", "payload"],
              [row[:5] + ["\t".join(row[5:])] for row in dram_rows])
    write_tsv(output_dir / "CROSS_LAYER_OUTCOME_MATRIX.tsv", provenance,
              ["record_type", "scope", "semantic_kernel_index", "trace_filename",
               "kernel_name", "payload"],
              [row[:5] + ["\t".join(row[5:])] for row in cross_rows])

    pressure_rows: list[list[str]] = []
    l1_total = re.compile(r"^\s*(L1D_total_cache_[A-Za-z_]+)\s*=\s*(\S+)")
    l1_core = re.compile(r"^\s*(L1D_cache_core\[\d+\]:.*)$")
    for line in lines:
        match = l1_total.match(line)
        if match:
            pressure_rows.append(["L1D_TOTAL", match.group(1), match.group(2)])
        elif l1_core.match(line):
            pressure_rows.append(["L1D_CORE", "raw_core_stats", line.strip()])
    # Object-split reservation-fail counts are present in L1D_OBJECT_STATS;
    # core-native capacity detail is preserved here without inventing a new
    # shadow cache-pressure model.
    write_tsv(output_dir / "L1D_FAIL_PRESSURE.tsv", provenance,
              ["scope", "metric", "value"], pressure_rows)

    (output_dir / "TELEMETRY_SCHEMA.md").write_text(
        "# M4C/M4B bounded memory telemetry schema\n\n"
        "Schema: `M4C_MEMORY_TELEMETRY_V1`.  The simulator emits ROI-per-run, "
        "per-kernel, and deterministic fixed transaction-window aggregate records. "
        "It never emits a formal per-access log. `m4c_telemetry` is L1D; "
        "`m4c_telemetry_l2` is L2; `m4c_telemetry_dram*` is DRAM; "
        "`m4c_telemetry_l2_replacement` is incoming-to-victim attribution; "
        "and `m4c_telemetry_cross_*` is the sparse translation-to-cache matrix.\n\n"
        "Frontend records expose memory instructions, active-lane references, "
        "coalesced transactions, requested/transaction bytes, sector population, "
        "and load/store/atomic class.  Sparse matrix omissions are zero. "
        "Every TSV repeats the provenance columns bound to this run manifest.\n\n"
        "`KERNEL_MEMORY_STATS.tsv` and `WINDOW_MEMORY_STATS.tsv` retain the "
        "simulator record type plus its ordered payload; the typed layer-specific "
        "tables provide named columns for L1D, L2, queue, replacement, and "
        "cross-layer records.  The window payload is a deterministic bounded "
        "aggregate, never an access sequence.\n\n"
        "Translation source is exact only for application transactions that passed "
        "the shader-side admission point: VM_DISABLED, IDEAL_IDENTITY, "
        "L1_TLB_HIT, L2_TLB_HIT, or PTW.  In mode-2 profiles, the simulator "
        "asserts that such an application transaction is never UNOBSERVED.  A "
        "sparse cross-layer row tagged UNOBSERVED instead denotes cache-internal "
        "store/write-allocate traffic for which no application translation source "
        "exists; it must be reported separately and must not be relabeled or "
        "counted as translated application traffic.\n"
    )
    print("PASS exported=" + str(output_dir))


if __name__ == "__main__":
    main()
