#!/usr/bin/env python3
"""Materialize hash-bound D4/D5 tables from validated compact run rows."""

from __future__ import annotations

import argparse
import csv
import pathlib
import sys
from typing import Final


SCHEMA: Final = "POST_FAST64_OBSERVER_WAVE_V1"
CLASSIFICATION: Final = "POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT"


def read_tsv(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError(f"missing TSV: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows:
        raise ValueError(f"empty TSV: {path}")
    return rows


def ratio(numerator: int, denominator: int, zero_label: str) -> str:
    return zero_label if denominator == 0 else f"{numerator / denominator:.12g}"


def derived(row: dict[str, str]) -> dict[str, str]:
    duplicate = int(row["duplicate_after_eviction"])
    lower = int(row["lower_created"])
    tag_evictions = int(row["tag_evictions"])
    pending_hits = int(row["pending_hits"])
    instructions = int(row["instructions"])
    no_free = row["no_free_physical_events"]
    no_free_per_instruction = (
        "NA_NOT_REPORTED_IN_WHOLE_LINE_OO_COMPACT"
        if no_free == "NA_NOT_REPORTED_IN_WHOLE_LINE_OO_COMPACT"
        else ratio(
            int(no_free), instructions, "NA_ZERO_INSTRUCTION_DENOMINATOR"
        )
    )
    observer_samples = int(row["observer_sample_sm_cycles"])
    no_free_per_active_sm_cycle = (
        "NA_NOT_REPORTED_IN_WHOLE_LINE_OO_COMPACT"
        if no_free == "NA_NOT_REPORTED_IN_WHOLE_LINE_OO_COMPACT"
        else ratio(
            int(no_free), observer_samples, "NA_ZERO_OBSERVER_SAMPLE_DENOMINATOR"
        )
    )
    no_free_per_1k_active_sm_cycles = (
        "NA_NOT_REPORTED_IN_WHOLE_LINE_OO_COMPACT"
        if no_free == "NA_NOT_REPORTED_IN_WHOLE_LINE_OO_COMPACT"
        else ratio(
            int(no_free) * 1000,
            observer_samples,
            "NA_ZERO_OBSERVER_SAMPLE_DENOMINATOR",
        )
    )
    result = {
        "duplicate_share_of_lower": ratio(
            duplicate, lower, "NA_ZERO_LOWER_CREATED_DENOMINATOR"
        ),
        "duplicate_per_tag_eviction": ratio(
            duplicate, tag_evictions, "NA_ZERO_TAG_EVICTIONS_DENOMINATOR"
        ),
        "duplicate_event_ratio": ratio(
            duplicate,
            duplicate + pending_hits,
            "NA_ZERO_DUPLICATE_PLUS_PENDING_DENOMINATOR",
        ),
        "duplicate_payload_bytes_128B_lower_request_only": str(duplicate * 128),
        "duplicate_traffic_inflation": ratio(
            duplicate,
            lower - duplicate,
            "NA_ZERO_NON_DUPLICATE_LOWER_DENOMINATOR",
        ),
        "lower_created_per_instruction": ratio(
            lower, instructions, "NA_ZERO_INSTRUCTION_DENOMINATOR"
        ),
        "pending_hits_per_lower": ratio(
            pending_hits, lower, "NA_ZERO_LOWER_CREATED_DENOMINATOR"
        ),
        "tag_evictions_per_lower": ratio(
            tag_evictions, lower, "NA_ZERO_LOWER_CREATED_DENOMINATOR"
        ),
        "no_free_physical_events_per_instruction": no_free_per_instruction,
        "l2_misses_per_lower": ratio(
            int(row["l2_misses"]), lower, "NA_ZERO_LOWER_CREATED_DENOMINATOR"
        ),
        "l2_misses_per_instruction": ratio(
            int(row["l2_misses"]), instructions, "NA_ZERO_INSTRUCTION_DENOMINATOR"
        ),
        "l2_reservation_fails_per_lower": ratio(
            int(row["l2_reservation_fails"]),
            lower,
            "NA_ZERO_LOWER_CREATED_DENOMINATOR",
        ),
        "l2_reservation_fails_per_instruction": ratio(
            int(row["l2_reservation_fails"]),
            instructions,
            "NA_ZERO_INSTRUCTION_DENOMINATOR",
        ),
        "cycles_per_instruction": ratio(
            int(row["cycles"]), instructions, "NA_ZERO_INSTRUCTION_DENOMINATOR"
        ),
    }
    if row["wave"] == "D4":
        result.update(
            {
                "no_free_events_per_active_sm_cycle": no_free_per_active_sm_cycle,
                "no_free_events_per_1k_active_sm_cycles": no_free_per_1k_active_sm_cycles,
            }
        )
    return result


def write_tsv(path: pathlib.Path, rows: list[dict[str, str]], overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise ValueError(f"refusing to overwrite output: {path}")
    if not rows:
        raise ValueError(f"refusing to write empty output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if overwrite else "x"
    with path.open(mode, encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=pathlib.Path, required=True)
    parser.add_argument("--compact-dir", type=pathlib.Path, required=True)
    parser.add_argument("--reuse-row", type=pathlib.Path, required=True)
    parser.add_argument("--output-d4", type=pathlib.Path, required=True)
    parser.add_argument("--output-d5", type=pathlib.Path, required=True)
    parser.add_argument("--output-index", type=pathlib.Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        plan = read_tsv(args.plan)
        plan_by_raw = {row["run_directory"]: row for row in plan}
        if len(plan_by_raw) != 29:
            raise ValueError(f"expected 29 launched plan rows, found {len(plan_by_raw)}")
        # The wave collector retains the exact D3B reuse compact row beside the
        # 29 launched compact rows, then also passes that row explicitly so its
        # provenance remains a required materializer input.  Do not count that
        # single file twice when enumerating the compact directory.
        reuse_resolved = args.reuse_row.resolve()
        compact_rows: list[dict[str, str]] = []
        for path in sorted(args.compact_dir.glob("*.tsv")):
            if path.resolve() == reuse_resolved:
                continue
            rows = read_tsv(path)
            if len(rows) != 1:
                raise ValueError(f"compact row must be singular: {path}")
            compact_rows.append(rows[0])
        reuse_rows = read_tsv(args.reuse_row)
        if len(reuse_rows) != 1:
            raise ValueError("D3B Btree reuse row must be singular")
        compact_rows.extend(reuse_rows)
        if len(compact_rows) != 30:
            raise ValueError(f"expected 30 D4/D5 compact rows, found {len(compact_rows)}")
        seen: set[tuple[str, str, str]] = set()
        d4: list[dict[str, str]] = []
        d5: list[dict[str, str]] = []
        index: list[dict[str, str]] = []
        for row in compact_rows:
            if row.get("classification") != CLASSIFICATION:
                raise ValueError("invalid diagnostic classification")
            wave = row.get("wave")
            if wave not in {"D4", "D5"}:
                raise ValueError(f"unexpected wave: {wave!r}")
            raw_path = row["raw_run_directory"]
            plan_row = plan_by_raw.get(raw_path)
            reused = plan_row is None
            if reused:
                if not (wave == "D5" and row.get("workload") == "Btree" and row.get("mode") == "OO"):
                    raise ValueError(f"unplanned non-Btree reuse row: {raw_path}")
                dimension, point, source_kind = "primary", "primary", "D3B_EXACT_REUSE"
            else:
                dimension = plan_row["dimension"]
                point = plan_row["point"]
                source_kind = "NEW_DIAGNOSTIC_RUN"
                for key in ("wave", "workload", "mode", "core_sha", "config_sha256", "trace_list_sha256"):
                    expected = plan_row[key] if key in plan_row else plan_row.get(key.replace("core_sha", "core_sha"))
                    actual_key = "core_source_head" if key == "core_sha" else key
                    if row.get(actual_key) != expected:
                        raise ValueError(f"plan/compact identity mismatch for {raw_path}: {key}")
            key = (wave, row["workload"], row["mode"], point)
            if key in seen:
                raise ValueError(f"duplicate workload/mode row: {key}")
            seen.add(key)
            physical_kib = point if wave == "D4" else "PRIMARY_NOT_PHYSICAL_SWEEP"
            physical_lines = str(int(point) * 1024 // 128) if wave == "D4" else "PRIMARY_CONFIG_NOT_SWEEP"
            output = {
                **row,
                "schema": SCHEMA,
                "classification": CLASSIFICATION,
                "wave": wave,
                "source_row_kind": source_kind,
                "physical_pool_kib": physical_kib,
                "physical_capacity_lines_128B": physical_lines,
                "average_physical_occupancy_fraction_of_capacity": (
                    ratio(
                        int(row["physical_allocated_line_cycles"]),
                        int(row["observer_sample_sm_cycles"]) * int(physical_lines),
                        "NA_ZERO_SAMPLE_OR_CAPACITY_DENOMINATOR",
                    )
                    if wave == "D4"
                    else "NA_PRIMARY_CONFIG_NOT_PHYSICAL_SWEEP"
                ),
                "cycles_relative_to_24k_same_mode": (
                    "PENDING_D4_24K_BASELINE" if wave == "D4"
                    else "NA_PRIMARY_CONFIG_NOT_PHYSICAL_SWEEP"
                ),
                **derived(row),
            }
            index.append(
                {
                    "schema": SCHEMA,
                    "classification": CLASSIFICATION,
                    "wave": wave,
                    "workload": row["workload"],
                    "mode": row["mode"],
                    "source_row_kind": source_kind,
                    "physical_pool_kib": physical_kib,
                    "attempt_uuid": row["attempt_uuid"],
                    "core_source_head": row["core_source_head"],
                    "simulator_sha256": row["simulator_sha256"],
                    "config_sha256": row["config_sha256"],
                    "trace_list_sha256": row["trace_list_sha256"],
                    "accepted_summary_sha256": row["accepted_summary_sha256"],
                    "raw_run_directory": raw_path,
                }
            )
            (d4 if wave == "D4" else d5).append(output)
        if len(d4) != 18 or len(d5) != 12:
            raise ValueError(f"unexpected D4/D5 coverage: {len(d4)}/{len(d5)}")
        d4_baselines: dict[tuple[str, str], int] = {}
        for row in d4:
            if row["physical_pool_kib"] == "24":
                key = (row["workload"], row["mode"])
                if key in d4_baselines:
                    raise ValueError(f"duplicate 24-KiB baseline: {key}")
                d4_baselines[key] = int(row["cycles"])
        if len(d4_baselines) != 6:
            raise ValueError(f"expected six D4 24-KiB baselines, found {len(d4_baselines)}")
        for row in d4:
            baseline = d4_baselines[(row["workload"], row["mode"])]
            row["cycles_relative_to_24k_same_mode"] = ratio(
                int(row["cycles"]), baseline, "NA_ZERO_24K_CYCLE_BASELINE"
            )
        d4.sort(key=lambda r: (r["workload"], int(r["physical_pool_kib"]), r["mode"]))
        d5.sort(key=lambda r: r["workload"])
        index.sort(key=lambda r: (r["wave"], r["workload"], r["mode"]))
        write_tsv(args.output_d4, d4, args.overwrite)
        write_tsv(args.output_d5, d5, args.overwrite)
        write_tsv(args.output_index, index, args.overwrite)
        print("POST_FAST64_OBSERVER_WAVE_MATERIALIZE_PASS\tD4=18\tD5=12")
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"POST_FAST64_OBSERVER_WAVE_MATERIALIZE_ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
