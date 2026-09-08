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
import hashlib
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


def write_tsv(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    """Write a compact review-facing projection without mutating source tables."""
    with path.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=header, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def copy_table(source: Path, destination: Path) -> None:
    """Copy one already-validated compact table under a handoff-mandated name."""
    shutil.copyfile(source, destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--characterization-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--resource-snapshot", type=Path, required=True,
                        help="small TSV captured after C3 release; copied verbatim")
    parser.add_argument("--attestation-file", type=Path, required=True,
                        help="Window-A external attestation whose first line is required")
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
    resource_snapshot = args.resource_snapshot.resolve()
    if not resource_snapshot.is_file():
        fail(f"missing resource snapshot: {resource_snapshot}")
    attestation_file = args.attestation_file.resolve()
    if not attestation_file.is_file():
        fail(f"missing Window-A attestation: {attestation_file}")
    if attestation_file.read_text().splitlines()[:1] != ["A_TERMINAL_CONFIRMED"]:
        fail("Window-A attestation first line is not A_TERMINAL_CONFIRMED")
    output.mkdir(parents=True, exist_ok=True)
    for name in TABLES:
        shutil.copyfile(source / name, output / name)

    # These names are the compact review entry points named by the terminal
    # handoff.  They are projections/copies of the validation-backed source
    # tables above; no raw log, trace, or simulator artifact is copied.
    write_tsv(output / "C3_FINAL_ARM_MATRIX.tsv", list(formal[0].keys()), formal)
    runtime_values = {row["field"]: row["value"] for row in runtime}
    provenance_header = [
        "arm", "roi", "profile", "framework_head", "core_head",
        "simulator_binary_sha256", "mapped_libcudart_sha256",
        "mapped_libcudart_realpath", "run_manifest_sha256",
        "kernel_list_sha256", "run_log_sha256",
    ]
    provenance_rows = [{
        "arm": row["arm"], "roi": row["roi"], "profile": row["profile"],
        "framework_head": row["framework_head"], "core_head": row["core_head"],
        "simulator_binary_sha256": runtime_values.get("simulator_binary_sha256", "MISSING"),
        "mapped_libcudart_sha256": runtime_values.get("mapped_libcudart_sha256", "MISSING"),
        "mapped_libcudart_realpath": runtime_values.get("mapped_libcudart_realpath", "MISSING"),
        "run_manifest_sha256": row["run_manifest_sha256"],
        "kernel_list_sha256": row["kernel_list_sha256"],
        "run_log_sha256": row["run_log_sha256"],
    } for row in formal]
    write_tsv(output / "C3_FINAL_PROVENANCE.tsv", provenance_header, provenance_rows)
    performance_header = list(performance[0].keys())
    for roi, name in (("prefill", "PREFILL_FINAL_PROFILE_COMPARISON.tsv"),
                      ("decode1", "DECODE_FINAL_PROFILE_COMPARISON.tsv")):
        write_tsv(output / name, performance_header,
                  [row for row in performance if row["roi"] == roi])
    copy_table(source / "CROSS_LAYER_TRANSLATION_L1D_L2.tsv",
               output / "C4_CROSS_LAYER_SUMMARY.tsv")
    copy_table(source / "TRACE_LOCALITY_OFFLINE.tsv",
               output / "C4_TRACE_LOCALITY_SUMMARY.tsv")
    copy_table(resource_snapshot, output / "RESOURCE_RELEASE_SNAPSHOT.tsv")

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
    write(output / "C4_OBSERVABILITY_GAPS.md", """# C4 observability gaps

- Object-specific Weight/KV/PTE attribution by DRAM channel, bank, or row is
  not available; no such attribution is inferred from global native DRAM
  statistics.
- `L1D_ACCESS_ATTEMPT_WINDOW` is an observation-only access-attempt window,
  not an exact unique coalesced-transaction window.  It must not be used to
  derive exact transactions per memory instruction.
- Native global DRAM channel/bank/read/write/latency/row-locality values are
  reused existing GPGPU-Sim statistics and are retained in
  `NATIVE_DRAM_MEMORY_SYSTEM_STATS.tsv`.
- A counter difference alone is not a causal mechanism proof; the package
  separates measured facts from supported signals and unresolved gaps.
""")
    attestation_sha256 = hashlib.sha256(attestation_file.read_bytes()).hexdigest()
    write(output / "A_TERMINAL_ATTESTATION_RECORD.md", """# Window-A terminal attestation record

- External attestation: `{path}`
- SHA256: `{digest}`
- First line verified: `A_TERMINAL_CONFIRMED`
- Scope: C3 simulator-heavy execution is terminal and its eight-arm formal
  gate passed.  This is not a claim that other windows have passed their own
  independent resource gates.
""".format(path=attestation_file, digest=attestation_sha256))
    write(output / "FINAL_REPORT.md", """# M4C C3+C4 final report

Status: **C3 TERMINAL PASS / C4 OFFLINE CHARACTERIZATION COMPLETE — PENDING CHATGPT REVIEW**

All eight authorized C3 arms have terminal exit status zero and exact
kernel-marker/telemetry-record agreement with their immutable kernel lists.
The C4 package uses existing C3 logs, structured exports, and immutable-trace
offline locality only; it launches no replay.  The pre-correction/post-
correction Framework provenance split remains explicit in the final matrix.

Primary measured comparison tables are
`DECODE_FINAL_PROFILE_COMPARISON.tsv`,
`PREFILL_FINAL_PROFILE_COMPARISON.tsv`,
`C4_CROSS_LAYER_SUMMARY.tsv`, and
`C4_TRACE_LOCALITY_SUMMARY.tsv`.  Interpretation limits are recorded in
`C4_OBSERVABILITY_GAPS.md`.

Scope terminates after C4.  C5, M4B-P, M4B-S, and M5 are not started.
""")
    print(f"PASS review_pack={output}")


if __name__ == "__main__":
    main()
