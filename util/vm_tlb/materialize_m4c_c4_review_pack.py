#!/usr/bin/env python3
"""Materialize an authoritative M4C C3+C4 review pack without replay.

The input is a completed C4 characterization directory.  This script copies
only compact structured evidence, preserves hashes/relative raw-log paths, and
generates a small Markdown index.  It never opens a simulator, trace, or raw
run log for writing.
"""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path


TABLES = (
    "FORMAL_RUN_MATRIX.tsv",
    "BASELINE_CONFIG_MATRIX.tsv",
    "PERFORMANCE_SUMMARY.tsv",
    "TRANSLATION_TOTALS.tsv",
    "OBJECT_VM_STATS.tsv",
    "L2_TLB_REPLACEMENT_MATRIX.tsv",
    "LATENCY_SUMMARY.tsv",
    "L1D_L2_OBJECT_SUMMARY.tsv",
    "DATA_L2_REPLACEMENT_MATRIX.tsv",
    "DRAM_CLASS_SUMMARY.tsv",
    "CROSS_LAYER_TRANSLATION_L1D_L2.tsv",
    "L2_QUEUE_PRESSURE_SUMMARY.tsv",
    "NATIVE_DRAM_MEMORY_SYSTEM_STATS.tsv",
    "WINDOW_TELEMETRY_INVENTORY.tsv",
    "TRACE_LOCALITY_OFFLINE.tsv",
    "RAW_LOG_INDEX.tsv",
    "INPUT_ARTIFACT_INDEX.tsv",
    "C3_RUNTIME_PROVENANCE.tsv",
    "C4_VALIDATION.tsv",
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if not reader.fieldnames:
            fail(f"empty TSV: {path}")
        rows = list(reader)
    return list(reader.fieldnames), rows


def table(dest: Path, rows: list[list[str]]) -> str:
    return "\n".join("| " + " | ".join(row) + " |" for row in rows)


def require_terminal_formal_matrix(rows: list[dict[str, str]]) -> None:
    if len(rows) != 8:
        fail(f"formal matrix has {len(rows)} arms, expected 8")
    expected = {
        f"{roi}-{profile}"
        for roi in ("decode1", "prefill")
        for profile in ("disabled", "ideal", "generic", "paper")
    }
    if {row.get("arm") for row in rows} != expected:
        fail("formal matrix arm set is not the authorized 2x4 matrix")
    for row in rows:
        if row.get("terminal_result") != "PASS" or row.get("simulator_exit_status") != "0":
            fail(f"formal arm is not terminal PASS: {row.get('arm')}")
        if row.get("expected_kernel_list_entries") != row.get("processing_kernel_markers") or \
           row.get("expected_kernel_list_entries") != row.get("telemetry_kernel_records"):
            fail(f"formal count mismatch: {row.get('arm')}")


def require_validation(rows: list[dict[str, str]]) -> None:
    if not rows:
        fail("C4 validation is empty")
    for row in rows:
        if row.get("result") not in {"PASS", "NOT_PERFORMED"}:
            fail(f"C4 validation failure: {row}")


def write(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--characterization-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    source = args.characterization_dir.resolve()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        fail(f"refusing to overwrite nonempty review pack: {output}")
    for name in TABLES:
        if not (source / name).is_file():
            fail(f"missing required C4 table: {name}")
    _, formal = read_tsv(source / "FORMAL_RUN_MATRIX.tsv")
    _, validation = read_tsv(source / "C4_VALIDATION.tsv")
    _, runtime = read_tsv(source / "C3_RUNTIME_PROVENANCE.tsv")
    _, performance = read_tsv(source / "PERFORMANCE_SUMMARY.tsv")
    require_terminal_formal_matrix(formal)
    require_validation(validation)
    output.mkdir(parents=True, exist_ok=True)
    for name in TABLES:
        shutil.copyfile(source / name, output / name)

    formal_rows = [[
        row["arm"], row["terminal_result"], row["expected_kernel_list_entries"],
        row["processing_kernel_markers"], row["telemetry_kernel_records"],
        row["simulator_exit_status"],
    ] for row in formal]
    perf_rows = [[
        row["roi"], row["profile"], row["gpu_tot_sim_cycle"],
        row["gpu_tot_sim_insn"], row["gpu_tot_ipc"],
        row["slowdown_vs_ideal_identity"], row["slowdown_vs_vm_disabled"],
    ] for row in performance]
    runtime_rows = [[row["scope"], row["field"], row["value"], row["evidence"]] for row in runtime]
    validation_rows = [[row["check"], row["result"], row["detail"]] for row in validation]

    write(output / "README.md", """# M4C C3+C4 authoritative review pack

Status: **C3+C4 EXECUTION COMPLETE — PENDING CHATGPT REVIEW**

This is the Window-A authoritative evidence package.  It includes only compact,
provenance-bound structured tables and Markdown.  It contains no raw formal
logs, traces, archives, or simulator binaries.  No replay was launched while
materializing this package.

Scope ends after C4.  C5, M4B-P, M4B-S, and M5 are intentionally not started.

Primary entry points: `C3_CLOSEOUT.md`, `CHARACTERIZATION_FINDINGS.md`,
`SOURCE_ANCHORS.md`, `VALIDATION_SUMMARY.md`, and the TSV inventory below.
""")
    write(output / "SOURCE_ANCHORS.md", """# Source and runtime anchors

The following values are derived from original per-arm manifests and the
direct runtime-provenance record.  Existing manifests are not rewritten.

| Scope | Field | Value | Evidence |
| --- | --- | --- | --- |
""" + table(output, runtime_rows) + """

The early decode manifests retain the pre-correction Framework SHA.  The later
Framework-only correction is restricted to docs and the offline exporter; the
provenance table records the verified Git path scope and the common frozen C3
binary/runtime identities.  This is not a claim that the historical manifests
were retroactively changed.
""")
    write(output / "C3_CLOSEOUT.md", """# C3 8/8 terminal closeout

Every arm below passed its formal terminal gate: simulator exit status is zero,
the `Processing kernel` / started-kernel marker count equals its immutable
kernel-list entry count, and telemetry-kernel record count equals that same
count.  A marker count by itself is not completion proof.

| Arm | Result | Expected list entries | Processing-kernel markers | Telemetry records | Simulator exit |
| --- | --- | ---: | ---: | ---: | ---: |
""" + table(output, formal_rows) + """

The C4 validation table additionally records generic/paper PTE/requester/object
conservation, terminal quiescence, exporter provenance, and no-replay status.
Raw formal log identities are retained only in `RAW_LOG_INDEX.tsv` and
`INPUT_ARTIFACT_INDEX.tsv`.
""")
    write(output / "VALIDATION_SUMMARY.md", """# Validation summary

| Check | Result | Detail |
| --- | --- | --- |
""" + table(output, validation_rows) + """

`NOT_PERFORMED` is used only for replay: C4 reads existing immutable C3
evidence and does not rerun an arm.
""")
    write(output / "CHARACTERIZATION_FINDINGS.md", """# Baseline characterization findings

## Measured facts

The table below is a direct rendering of `PERFORMANCE_SUMMARY.tsv`; all other
measured hierarchy data are retained in the named TSVs in this package.

| ROI | Profile | Cycles | Instructions | IPC | Slowdown vs ideal identity | Slowdown vs VM-disabled |
| --- | --- | ---: | ---: | ---: | ---: |
""" + table(output, perf_rows) + """

Measured translation facts are in `TRANSLATION_TOTALS.tsv`, `OBJECT_VM_STATS.tsv`,
`L2_TLB_REPLACEMENT_MATRIX.tsv`, and `LATENCY_SUMMARY.tsv`.  Measured cache and
memory context is in `L1D_L2_OBJECT_SUMMARY.tsv`,
`DATA_L2_REPLACEMENT_MATRIX.tsv`, `L2_QUEUE_PRESSURE_SUMMARY.tsv`,
`DRAM_CLASS_SUMMARY.tsv`, `NATIVE_DRAM_MEMORY_SYSTEM_STATS.tsv`, and
`CROSS_LAYER_TRANSLATION_L1D_L2.tsv`.  Offline exact trace locality is in
`TRACE_LOCALITY_OFFLINE.tsv`.

## Supported inference

No causal conclusion is inferred from a single counter.  Any claim about
translation-versus-cache/DRAM bottlenecks, object interference, or prefill
versus decode differences must be checked against the corresponding structured
tables above during review.

## Paper comparison

`generic` and `paper` are reported as separate measured platform profiles.  No
paper-mechanism approximation or Window-B/C result is imported into this
authoritative package.

## Unknown / unavailable

Object-specific Weight/KV/PTE attribution by DRAM channel, bank, or row remains
unavailable.  Native global channel/bank/read/write/latency/row-locality data
are existing GPGPU-Sim statistics.  `L1D_ACCESS_ATTEMPT_WINDOW` is not an exact
unique-coalesced-transaction window and must not be used to derive exact
transactions per memory instruction.
""")
    write(output / "OPEN_ISSUES.md", """# Open issues and scope boundary

- Object-specific DRAM channel/bank/row attribution is not available.
- `L1D_ACCESS_ATTEMPT_WINDOW` remains observation-only with its frozen
  access-attempt semantics; it is not an exact coalesced-transaction measure.
- The pre-correction/post-correction Framework manifest lineage is preserved
  explicitly in `C3_RUNTIME_PROVENANCE.tsv`; no historical manifest is edited.
- This package stops after C4.  No C5, M4B, or M5 execution is authorized here.
""")
    print(f"PASS review_pack={output}")


if __name__ == "__main__":
    main()
