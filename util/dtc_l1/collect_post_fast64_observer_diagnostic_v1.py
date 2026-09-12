#!/usr/bin/env python3
"""Validate and compact one observer-on diagnostic run against FAST64 evidence.

This is intentionally a collector, not a simulator parser that synthesizes
science: it accepts a natural-terminal immutable run receipt and an accepted
FAST64 compact summary, proves all pre-existing scalar metrics are identical,
and emits only the observer occupancy integrals plus their explicit
time-normalized descriptive reductions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import re
import sys
from typing import Final


SCHEMA: Final = "POST_FAST64_OBSERVER_DIAGNOSTIC_V1"
CLASSIFICATION: Final = "POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT"
RUNNER_SCHEMA: Final = "POST_FAST64_OBSERVER_QUAL_V1"
TERMINAL_MARKER: Final = "GPGPU-Sim: *** exit detected ***"
# Cache summaries indent their scalar rows; DTC and global rows do not.
STAT: Final = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*) = (.+)$")


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tsv_map(path: pathlib.Path) -> dict[str, str]:
    rows = list(csv.DictReader(path.open(encoding="utf-8"), delimiter="\t"))
    if not rows or set(rows[0]) != {"key", "value"}:
        raise ValueError(f"invalid receipt schema: {path}")
    values = {row["key"]: row["value"] for row in rows}
    if len(values) != len(rows):
        raise ValueError(f"duplicate receipt key: {path}")
    return values


def final_stats(run: pathlib.Path) -> dict[str, str]:
    stdout = run / "simulator.stdout"
    text = stdout.read_text(encoding="utf-8", errors="replace")
    if TERMINAL_MARKER not in text:
        raise ValueError(f"missing natural terminal marker: {stdout}")
    stats: dict[str, str] = {}
    for line in text.splitlines():
        match = STAT.match(line)
        if match:
            key, value = match.groups()
            if key.startswith(("DTC_L1_", "L1D_", "L2_", "gpu_tot_sim_", "gpgpu_n_")):
                stats[key] = value
    return stats


def integer(stats: dict[str, str], key: str) -> int:
    if key not in stats:
        raise ValueError(f"missing observer statistic {key}")
    try:
        return int(stats[key])
    except ValueError as error:
        raise ValueError(f"non-integer observer statistic {key}={stats[key]!r}") from error


def mode_fields(mode: str) -> tuple[str, str, str, str, str]:
    prefix = f"DTC_L1_{mode.lower()}_"
    return (
        prefix + "observer_sample_sm_cycles",
        prefix + "physical_allocated_line_cycles",
        prefix + "physical_full_sm_cycles",
        prefix + "inflight_request_cycles",
        prefix + "observer_live_records",
    )


def division(numerator: int, denominator: int) -> str:
    return "NA_ZERO_SAMPLE_DENOMINATOR" if denominator == 0 else f"{numerator / denominator:.12g}"


def optional_integer(stats: dict[str, str], key: str) -> str:
    if key in stats:
        return str(integer(stats, key))
    if key.endswith("no_free_physical_events"):
        return "NA_NOT_REPORTED_IN_WHOLE_LINE_OO_COMPACT"
    return "NA_NOT_APPLICABLE"


def optional_average(stats: dict[str, str], sum_key: str, count_key: str) -> str:
    if sum_key not in stats or count_key not in stats:
        return "NA_NOT_APPLICABLE"
    return division(integer(stats, sum_key), integer(stats, count_key))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=pathlib.Path, required=True)
    parser.add_argument("--accepted-summary", type=pathlib.Path, required=True)
    parser.add_argument("--expected-core-sha", required=True)
    parser.add_argument("--wave", choices=("D4", "D5"), required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError(f"refusing to overwrite compact diagnostic output: {args.output}")
        manifest = tsv_map(args.run / "RUN_MANIFEST.tsv")
        terminal = tsv_map(args.run / "RUN_TERMINAL.tsv")
        required_manifest = {
            "runner_schema": RUNNER_SCHEMA,
            "result_classification": CLASSIFICATION,
            "observer_enabled": "1",
            "core_source_head": args.expected_core_sha,
            "simulator_exit_status": "0",
        }
        for key, expected in required_manifest.items():
            if manifest.get(key) != expected:
                raise ValueError(f"manifest {key}={manifest.get(key)!r}, expected {expected!r}")
        if terminal.get("receipt_type") != "TERMINAL" or terminal.get("simulator_exit_status") != "0":
            raise ValueError(f"non-natural/nonzero terminal receipt: {args.run}")
        if terminal.get("attempt_uuid") != manifest.get("attempt_uuid"):
            raise ValueError(f"receipt attempt identity mismatch: {args.run}")
        accepted = json.loads(args.accepted_summary.read_text(encoding="utf-8"))
        provenance = accepted.get("provenance", {})
        expected_metrics = accepted.get("metrics", {})
        artifacts = accepted.get("external_artifacts", {})
        if not isinstance(provenance, dict) or not isinstance(expected_metrics, dict) or not isinstance(artifacts, dict):
            raise ValueError(f"invalid accepted summary structure: {args.accepted_summary}")
        mode = manifest.get("mode", "")
        if mode not in {"IO", "OO"}:
            raise ValueError(f"invalid mode in run manifest: {mode!r}")
        if provenance.get("workload_id") != manifest.get("workload"):
            raise ValueError("accepted workload identity does not match run manifest")
        if provenance.get("config_sha256") != manifest.get("config_sha256"):
            raise ValueError("accepted config hash does not match run manifest")
        if artifacts.get("trace_list_sha256") != manifest.get("trace_list_sha256"):
            raise ValueError("accepted trace-list hash does not match run manifest")
        stats = final_stats(args.run)
        missing = [key for key in expected_metrics if key not in stats]
        changed = [
            key for key, expected in expected_metrics.items()
            if key in stats and stats[key] != str(expected)
        ]
        if missing or changed:
            detail = []
            if missing:
                detail.append("missing=" + ",".join(missing[:8]))
            if changed:
                detail.append("changed=" + ",".join(changed[:8]))
            raise ValueError("pre-existing FAST64 metric mismatch: " + " ".join(detail))
        sample_key, allocated_key, full_key, inflight_key, live_key = mode_fields(mode)
        sample = integer(stats, sample_key)
        allocated = integer(stats, allocated_key)
        full = integer(stats, full_key)
        inflight = integer(stats, inflight_key)
        live = integer(stats, live_key)
        if live != 0:
            raise ValueError(f"terminal observer records remain live: {live}")
        prefix = f"DTC_L1_{mode.lower()}_"
        lower_created = integer(stats, prefix + "lower_created")
        pending_hits = integer(stats, prefix + "pending_hits")
        tag_evictions = integer(stats, prefix + "tag_evictions")
        duplicate_after_eviction = integer(stats, prefix + "duplicate_after_eviction")
        no_free_physical_events = optional_integer(
            stats, prefix + "no_free_physical_events"
        )
        l2_misses = integer(stats, "L2_total_cache_misses")
        l2_reservation_fails = integer(stats, "L2_total_cache_reservation_fails")
        global_reads = integer(stats, "gpgpu_n_mem_read_global")
        global_writes = integer(stats, "gpgpu_n_mem_write_global")
        l2_accesses = integer(stats, "L2_total_cache_accesses")
        alloc_count_key = prefix + "alloc_to_ready_count"
        alloc_sum_key = prefix + "alloc_to_ready_sum_cycles"
        alloc_max_key = prefix + "alloc_to_ready_max_cycles"
        pending_evict_key = prefix + "pending_tag_evictions"
        row = {
            "schema": SCHEMA,
            "classification": CLASSIFICATION,
            "wave": args.wave,
            "workload": manifest["workload"],
            "mode": mode,
            "attempt_uuid": manifest["attempt_uuid"],
            "runner_sha256": manifest["runner_sha256"],
            "simulator": manifest["simulator"],
            "simulator_sha256": manifest["simulator_sha256"],
            "core_source_head": manifest["core_source_head"],
            "config": manifest["config"],
            "config_sha256": manifest["config_sha256"],
            "trace_list": manifest["trace_list"],
            "trace_list_sha256": manifest["trace_list_sha256"],
            "accepted_summary": str(args.accepted_summary.resolve()),
            "accepted_summary_sha256": sha256(args.accepted_summary),
            "preexisting_metric_count": str(len(expected_metrics)),
            "preexisting_exact_match": "true",
            "observer_sample_sm_cycles": str(sample),
            "physical_allocated_line_cycles": str(allocated),
            "physical_full_sm_cycles": str(full),
            "inflight_request_cycles": str(inflight),
            "observer_live_records_terminal": str(live),
            "average_physical_allocated_lines_per_sample": division(allocated, sample),
            "physical_full_sample_fraction": division(full, sample),
            "average_inflight_requests_per_sample": division(inflight, sample),
            "alloc_to_ready_count": optional_integer(stats, alloc_count_key),
            "alloc_to_ready_sum_cycles": optional_integer(stats, alloc_sum_key),
            "alloc_to_ready_max_cycles": optional_integer(stats, alloc_max_key),
            "alloc_to_ready_average_cycles": optional_average(
                stats, alloc_sum_key, alloc_count_key
            ),
            "pending_tag_evictions_observed": optional_integer(stats, pending_evict_key),
            "pending_tag_evictions_per_lower": optional_average(
                stats, pending_evict_key, prefix + "lower_created"
            ),
            "io_pending_eviction_to_response_count": optional_integer(
                stats, "DTC_L1_io_pending_eviction_to_response_count"
            ),
            "io_pending_eviction_to_response_average_cycles": optional_average(
                stats,
                "DTC_L1_io_pending_eviction_to_response_sum_cycles",
                "DTC_L1_io_pending_eviction_to_response_count",
            ),
            "io_pending_eviction_to_response_max_cycles": optional_integer(
                stats, "DTC_L1_io_pending_eviction_to_response_max_cycles"
            ),
            "oo_deferred_eviction_to_final_reclaim_count": optional_integer(
                stats, "DTC_L1_oo_deferred_tag_eviction_to_final_reclaim_count"
            ),
            "oo_deferred_eviction_to_final_reclaim_average_cycles": optional_average(
                stats,
                "DTC_L1_oo_deferred_tag_eviction_to_final_reclaim_sum_cycles",
                "DTC_L1_oo_deferred_tag_eviction_to_final_reclaim_count",
            ),
            "oo_deferred_eviction_to_final_reclaim_max_cycles": optional_integer(
                stats, "DTC_L1_oo_deferred_tag_eviction_to_final_reclaim_max_cycles"
            ),
            "lower_created": str(lower_created),
            "pending_hits": str(pending_hits),
            "tag_evictions": str(tag_evictions),
            "duplicate_after_eviction": str(duplicate_after_eviction),
            "no_free_physical_events": no_free_physical_events,
            "l2_misses": str(l2_misses),
            "l2_reservation_fails": str(l2_reservation_fails),
            "l2_accesses": str(l2_accesses),
            "global_reads": str(global_reads),
            "global_writes": str(global_writes),
            "oo_out_of_order_retires": optional_integer(
                stats, "DTC_L1_oo_out_of_order_retires"
            ),
            "oo_immediate_reclaims": optional_integer(stats, "DTC_L1_oo_immediate_reclaims"),
            "oo_deferred_reclaims": optional_integer(stats, "DTC_L1_oo_deferred_reclaims"),
            "oo_final_ref_reclaims": optional_integer(stats, "DTC_L1_oo_final_ref_reclaims"),
            "cycles": stats["gpu_tot_sim_cycle"],
            "instructions": stats["gpu_tot_sim_insn"],
            "raw_run_directory": str(args.run.resolve()),
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(row), delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerow(row)
        print("POST_FAST64_OBSERVER_DIAGNOSTIC_PASS\t" + f"wave={args.wave}\trun={args.run}")
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"POST_FAST64_OBSERVER_DIAGNOSTIC_ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
