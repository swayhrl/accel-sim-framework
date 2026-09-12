#!/usr/bin/env python3
"""Materialize an immutable Lane-D interim checkpoint from terminal rows only.

The D4/D5 controller owns its live run directories.  This generator never
writes beneath that controller root: each completed row is first passed through
the fail-closed single-row collector into a temporary directory, and only the
resulting compact evidence is written to an explicitly empty output directory.
"""

from __future__ import annotations

import argparse
import csv
import io
import pathlib
import subprocess
import sys
import tempfile
from typing import Iterable


SCHEMA = "POST_FAST64_LANE_D_INTERIM_V1"
CLASSIFICATION = "POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT"
TERMINAL = "STRICT_TERMINAL_ACCEPTED_FOR_INTERIM_ANALYSIS"
LIVE = "LIVE_NOT_YET_ANALYZED"
REUSE = "EXACT_D3B_REUSE"
ALLOW_EXISTING_IDENTICAL = False


def read_rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_map(path: pathlib.Path) -> dict[str, str]:
    rows = read_rows(path)
    if not rows or set(rows[0]) != {"key", "value"}:
        raise ValueError(f"invalid key/value TSV: {path}")
    values = {row["key"]: row["value"] for row in rows}
    if len(values) != len(rows):
        raise ValueError(f"duplicate key in {path}")
    return values


def write_rows(path: pathlib.Path, fields: list[str], rows: Iterable[dict[str, str]]) -> None:
    rendered = io.StringIO(newline="")
    writer = csv.DictWriter(rendered, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    expected = rendered.getvalue()
    if path.exists():
        if not ALLOW_EXISTING_IDENTICAL:
            raise ValueError(f"refusing to overwrite existing output: {path}")
        current = path.read_text(encoding="utf-8")
        if current != expected:
            raise ValueError(f"existing output is not byte-identical: {path}")
        return
    with path.open("x", encoding="utf-8", newline="") as handle:
        handle.write(expected)


def number(value: str) -> int:
    return int(value)


def ratio(numerator: int, denominator: int) -> str:
    return "NA_ZERO_DENOMINATOR" if denominator == 0 else f"{numerator / denominator:.12g}"


def compact_terminal(
    collector: pathlib.Path,
    plan_row: dict[str, str],
    scratch: pathlib.Path,
) -> dict[str, str]:
    output = scratch / (pathlib.Path(plan_row["run_directory"]).name + ".tsv")
    result = subprocess.run(
        [
            sys.executable,
            str(collector),
            "--run", plan_row["run_directory"],
            "--accepted-summary", plan_row["accepted_summary"],
            "--expected-core-sha", plan_row["core_sha"],
            "--wave", plan_row["wave"],
            "--output", str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise ValueError(
            "fail-closed collector rejected " + plan_row["run_directory"] + ": " + result.stderr.strip()
        )
    rows = read_rows(output)
    if len(rows) != 1:
        raise ValueError(f"collector did not emit exactly one row: {output}")
    return rows[0]


def d4_capacity_lines(point: str) -> tuple[str, str]:
    kib = int(point)
    if kib not in {24, 32, 48}:
        raise ValueError(f"unexpected D4 physical point: {point}")
    return str(kib), str(kib * 1024 // 128)


def ensure_output_targets_absent(output: pathlib.Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    names = (
        "LANE_D_INTERIM_LAUNCHED_COVERAGE.tsv",
        "LANE_D_INTERIM_D3B_REUSE.tsv",
        "LANE_D_INTERIM_TERMINAL_COLLECTION.tsv",
        "D4_INTERIM_TERMINAL_ROWS.tsv",
        "D4_INTERIM_ANALYSIS.tsv",
        "D5_INTERIM_IO_OO_DUPLICATE.tsv",
    )
    present = [name for name in names if (output / name).exists()]
    if present and not ALLOW_EXISTING_IDENTICAL:
        raise ValueError("refusing to overwrite interim outputs: " + ",".join(present))


def main() -> int:
    global ALLOW_EXISTING_IDENTICAL
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=pathlib.Path, required=True)
    parser.add_argument("--collector", type=pathlib.Path, required=True)
    parser.add_argument("--d3b-btree-oo-run", type=pathlib.Path, required=True)
    parser.add_argument("--d3b-btree-oo-summary", type=pathlib.Path, required=True)
    parser.add_argument("--d3b-core-sha", required=True)
    parser.add_argument("--lane-c-io", type=pathlib.Path, required=True)
    parser.add_argument("--accepted-speedup", type=pathlib.Path, required=True)
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    parser.add_argument("--allow-existing-identical", action="store_true")
    parser.add_argument("--expected-plan-rows", type=int, default=29)
    parser.add_argument("--expected-terminal-rows", type=int, default=26)
    parser.add_argument("--expected-live-rows", type=int, default=3)
    args = parser.parse_args()
    ALLOW_EXISTING_IDENTICAL = args.allow_existing_identical

    try:
        plan = read_rows(args.plan)
        if len(plan) != args.expected_plan_rows:
            raise ValueError(f"plan count {len(plan)}, expected {args.expected_plan_rows}")
        if len({row["run_directory"] for row in plan}) != len(plan):
            raise ValueError("duplicate run directory in plan")
        terminal_plan: list[dict[str, str]] = []
        live_plan: list[dict[str, str]] = []
        for row in plan:
            run = pathlib.Path(row["run_directory"])
            if (run / "RUN_TERMINAL.tsv").exists():
                terminal_plan.append(row)
            else:
                live_plan.append(row)
        if len(terminal_plan) != args.expected_terminal_rows or len(live_plan) != args.expected_live_rows:
            raise ValueError(
                f"snapshot terminal/live count {len(terminal_plan)}/{len(live_plan)}, expected "
                f"{args.expected_terminal_rows}/{args.expected_live_rows}"
            )
        ensure_output_targets_absent(args.output_dir)
        with tempfile.TemporaryDirectory(prefix="post-fast64-lane-d-interim-") as temporary:
            scratch = pathlib.Path(temporary)
            compact_by_run = {
                row["run_directory"]: compact_terminal(args.collector, row, scratch)
                for row in terminal_plan
            }
            btree_row = {
                "wave": "D5",
                "run_directory": str(args.d3b_btree_oo_run),
                "accepted_summary": str(args.d3b_btree_oo_summary),
                "core_sha": args.d3b_core_sha,
            }
            btree_compact = compact_terminal(args.collector, btree_row, scratch)

        coverage_fields = [
            "schema", "classification", "wave", "workload", "dimension", "point", "mode",
            "attempt_uuid", "runner_sha256", "core_source_head", "simulator_sha256",
            "run_directory", "accepted_summary", "acceptance_disposition",
        ]
        coverage: list[dict[str, str]] = []
        for row in plan:
            run = pathlib.Path(row["run_directory"])
            manifest = read_map(run / "RUN_MANIFEST.tsv")
            coverage.append({
                "schema": SCHEMA,
                "classification": CLASSIFICATION,
                "wave": row["wave"],
                "workload": row["workload"],
                "dimension": row["dimension"],
                "point": row["point"],
                "mode": row["mode"],
                "attempt_uuid": manifest["attempt_uuid"],
                "runner_sha256": manifest["runner_sha256"],
                "core_source_head": manifest["core_source_head"],
                "simulator_sha256": manifest["simulator_sha256"],
                "run_directory": row["run_directory"],
                "accepted_summary": row["accepted_summary"],
                "acceptance_disposition": TERMINAL if row in terminal_plan else LIVE,
            })
        write_rows(args.output_dir / "LANE_D_INTERIM_LAUNCHED_COVERAGE.tsv", coverage_fields, coverage)

        terminal_collection: list[dict[str, str]] = []
        for plan_row in terminal_plan:
            compact = compact_by_run[plan_row["run_directory"]].copy()
            compact.update({
                "source_row_kind": "FRESH_" + plan_row["wave"] + "_TERMINAL",
                "acceptance_disposition": TERMINAL,
            })
            terminal_collection.append(compact)
        terminal_collection_fields = list(terminal_collection[0])
        write_rows(
            args.output_dir / "LANE_D_INTERIM_TERMINAL_COLLECTION.tsv",
            terminal_collection_fields,
            terminal_collection,
        )

        reuse_manifest = read_map(args.d3b_btree_oo_run / "RUN_MANIFEST.tsv")
        reuse = [{
            "schema": SCHEMA,
            "classification": CLASSIFICATION,
            "wave": "D5",
            "workload": "Btree",
            "dimension": "primary",
            "point": "primary",
            "mode": "OO",
            "attempt_uuid": reuse_manifest["attempt_uuid"],
            "runner_sha256": reuse_manifest["runner_sha256"],
            "core_source_head": reuse_manifest["core_source_head"],
            "simulator_sha256": reuse_manifest["simulator_sha256"],
            "run_directory": str(args.d3b_btree_oo_run),
            "accepted_summary": str(args.d3b_btree_oo_summary),
            "acceptance_disposition": REUSE,
        }]
        write_rows(args.output_dir / "LANE_D_INTERIM_D3B_REUSE.tsv", coverage_fields, reuse)

        d4_rows: list[dict[str, str]] = []
        for plan_row in terminal_plan:
            if plan_row["wave"] != "D4":
                continue
            compact = compact_by_run[plan_row["run_directory"]].copy()
            kib, lines = d4_capacity_lines(plan_row["point"])
            compact.update({
                "configured_physical_kib": kib,
                "configured_physical_lines": lines,
                "source_row_kind": "FRESH_D4_TERMINAL",
            })
            d4_rows.append(compact)
        if len(d4_rows) != 16:
            raise ValueError(f"D4 terminal count {len(d4_rows)}, expected 16")
        d4_fields = list(d4_rows[0])
        write_rows(args.output_dir / "D4_INTERIM_TERMINAL_ROWS.tsv", d4_fields, d4_rows)

        d4_baseline: dict[tuple[str, str], int] = {}
        for row in d4_rows:
            if row["configured_physical_kib"] == "24":
                d4_baseline[(row["workload"], row["mode"])] = number(row["cycles"])
        if len(d4_baseline) != 6:
            raise ValueError("D4 has no complete 24-KiB same-mode baseline set")
        analysis_fields = [
            "schema", "classification", "source_row_kind", "workload", "mode", "configured_physical_kib",
            "configured_physical_lines", "cycles", "instructions", "cycles_per_instruction",
            "cycles_relative_to_same_mode_24k", "observer_sample_sm_cycles",
            "average_physical_allocated_lines_per_sample", "physical_occupancy_fraction",
            "physical_full_sample_fraction", "average_inflight_requests_per_sample", "alloc_to_ready_count",
            "alloc_to_ready_average_cycles", "alloc_to_ready_max_cycles", "pending_tag_evictions_observed",
            "pending_tag_evictions_per_lower", "lower_created", "duplicate_after_eviction",
            "duplicate_share_of_lower", "lower_request_payload_inflation",
            "io_pending_eviction_to_response_average_cycles", "io_pending_eviction_to_response_max_cycles",
            "oo_deferred_eviction_to_final_reclaim_average_cycles",
            "oo_deferred_eviction_to_final_reclaim_max_cycles", "oo_out_of_order_retires",
            "oo_immediate_reclaims", "oo_deferred_reclaims", "oo_final_ref_reclaims", "l2_accesses",
            "l2_misses", "l2_misses_per_lower", "l2_reservation_fails", "l2_reservation_fails_per_lower",
            "global_reads", "global_writes", "no_free_physical_events", "raw_run_directory",
        ]
        analysis: list[dict[str, str]] = []
        for row in d4_rows:
            sample = number(row["observer_sample_sm_cycles"])
            lower = number(row["lower_created"])
            duplicates = number(row["duplicate_after_eviction"])
            capacity = number(row["configured_physical_lines"])
            analysis.append({
                "schema": SCHEMA,
                "classification": CLASSIFICATION,
                "source_row_kind": row["source_row_kind"],
                "workload": row["workload"],
                "mode": row["mode"],
                "configured_physical_kib": row["configured_physical_kib"],
                "configured_physical_lines": row["configured_physical_lines"],
                "cycles": row["cycles"],
                "instructions": row["instructions"],
                "cycles_per_instruction": ratio(number(row["cycles"]), number(row["instructions"])),
                "cycles_relative_to_same_mode_24k": ratio(number(row["cycles"]), d4_baseline[(row["workload"], row["mode"])]),
                "observer_sample_sm_cycles": row["observer_sample_sm_cycles"],
                "average_physical_allocated_lines_per_sample": row["average_physical_allocated_lines_per_sample"],
                "physical_occupancy_fraction": ratio(number(row["physical_allocated_line_cycles"]), sample * capacity),
                "physical_full_sample_fraction": row["physical_full_sample_fraction"],
                "average_inflight_requests_per_sample": row["average_inflight_requests_per_sample"],
                "alloc_to_ready_count": row["alloc_to_ready_count"],
                "alloc_to_ready_average_cycles": row["alloc_to_ready_average_cycles"],
                "alloc_to_ready_max_cycles": row["alloc_to_ready_max_cycles"],
                "pending_tag_evictions_observed": row["pending_tag_evictions_observed"],
                "pending_tag_evictions_per_lower": row["pending_tag_evictions_per_lower"],
                "lower_created": row["lower_created"],
                "duplicate_after_eviction": row["duplicate_after_eviction"],
                "duplicate_share_of_lower": ratio(duplicates, lower),
                "lower_request_payload_inflation": ratio(duplicates, lower - duplicates),
                "io_pending_eviction_to_response_average_cycles": row["io_pending_eviction_to_response_average_cycles"],
                "io_pending_eviction_to_response_max_cycles": row["io_pending_eviction_to_response_max_cycles"],
                "oo_deferred_eviction_to_final_reclaim_average_cycles": row["oo_deferred_eviction_to_final_reclaim_average_cycles"],
                "oo_deferred_eviction_to_final_reclaim_max_cycles": row["oo_deferred_eviction_to_final_reclaim_max_cycles"],
                "oo_out_of_order_retires": row["oo_out_of_order_retires"],
                "oo_immediate_reclaims": row["oo_immediate_reclaims"],
                "oo_deferred_reclaims": row["oo_deferred_reclaims"],
                "oo_final_ref_reclaims": row["oo_final_ref_reclaims"],
                "l2_accesses": row["l2_accesses"],
                "l2_misses": row["l2_misses"],
                "l2_misses_per_lower": ratio(number(row["l2_misses"]), lower),
                "l2_reservation_fails": row["l2_reservation_fails"],
                "l2_reservation_fails_per_lower": ratio(number(row["l2_reservation_fails"]), lower),
                "global_reads": row["global_reads"],
                "global_writes": row["global_writes"],
                "no_free_physical_events": row["no_free_physical_events"],
                "raw_run_directory": row["raw_run_directory"],
            })
        write_rows(args.output_dir / "D4_INTERIM_ANALYSIS.tsv", analysis_fields, analysis)

        lane_c = {row["workload"]: row for row in read_rows(args.lane_c_io)}
        speedups = {row["workload"]: row for row in read_rows(args.accepted_speedup) if row["workload"] != "GM-FAST12"}
        d5_compact: list[tuple[str, dict[str, str]]] = []
        for plan_row in terminal_plan:
            if plan_row["wave"] == "D5":
                d5_compact.append(("FRESH_D5_TERMINAL", compact_by_run[plan_row["run_directory"]]))
        d5_compact.append(("D3B_EXACT_REUSE", btree_compact))
        if len(d5_compact) != 11:
            raise ValueError(f"D5 terminal/reuse count {len(d5_compact)}, expected 11")
        d5_fields = [
            "schema", "classification", "source_row_kind", "workload", "io_evidence_status",
            "oo_observer_evidence_status", "io_duplicate_after_eviction", "io_lower_created",
            "io_duplicate_share_of_lower", "io_lower_request_payload_inflation", "io_pending_hits",
            "io_tag_evictions", "oo_duplicate_after_eviction", "oo_lower_created",
            "oo_duplicate_share_of_lower", "oo_lower_request_payload_inflation", "oo_pending_hits",
            "oo_tag_evictions", "accepted_speedup_io", "accepted_speedup_oo", "oo_cycles",
            "oo_instructions", "oo_raw_run_directory",
        ]
        d5_analysis: list[dict[str, str]] = []
        for source_kind, row in d5_compact:
            workload = row["workload"]
            if workload not in lane_c or workload not in speedups:
                raise ValueError(f"missing accepted IO or speedup row for {workload}")
            io = lane_c[workload]
            lower = number(row["lower_created"])
            duplicates = number(row["duplicate_after_eviction"])
            d5_analysis.append({
                "schema": SCHEMA,
                "classification": CLASSIFICATION,
                "source_row_kind": source_kind,
                "workload": workload,
                "io_evidence_status": io["acceptance_status"],
                "oo_observer_evidence_status": "STRICT_TERMINAL_EXACT_PREEXISTING_METRIC_MATCH",
                "io_duplicate_after_eviction": io["io_duplicate_after_eviction"],
                "io_lower_created": io["io_lower_created"],
                "io_duplicate_share_of_lower": io["duplicate_share_of_lower"],
                "io_lower_request_payload_inflation": ratio(number(io["io_duplicate_after_eviction"]), number(io["io_lower_created"]) - number(io["io_duplicate_after_eviction"])),
                "io_pending_hits": io["io_pending_hits"],
                "io_tag_evictions": io["io_tag_evictions"],
                "oo_duplicate_after_eviction": row["duplicate_after_eviction"],
                "oo_lower_created": row["lower_created"],
                "oo_duplicate_share_of_lower": ratio(duplicates, lower),
                "oo_lower_request_payload_inflation": ratio(duplicates, lower - duplicates),
                "oo_pending_hits": row["pending_hits"],
                "oo_tag_evictions": row["tag_evictions"],
                "accepted_speedup_io": speedups[workload]["speedup_io"],
                "accepted_speedup_oo": speedups[workload]["speedup_oo"],
                "oo_cycles": row["cycles"],
                "oo_instructions": row["instructions"],
                "oo_raw_run_directory": row["raw_run_directory"],
            })
        d5_analysis.sort(key=lambda row: row["workload"].casefold())
        write_rows(args.output_dir / "D5_INTERIM_IO_OO_DUPLICATE.tsv", d5_fields, d5_analysis)
        print(
            "POST_FAST64_LANE_D_INTERIM_PASS"
            f"\tplan={len(plan)}\tterminal={len(terminal_plan)}\tlive={len(live_plan)}\td5_reuse=1"
        )
        return 0
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print(f"POST_FAST64_LANE_D_INTERIM_ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
