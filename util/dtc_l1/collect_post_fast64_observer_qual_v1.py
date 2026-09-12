#!/usr/bin/env python3
"""Materialize compact, hash-bound records from immutable D3 run receipts.

The raw simulator output remains in its immutable /tmp run namespace.  This
tool accepts only complete observer-off/on pairs already checked by the D3
comparator and emits review-sized TSVs with the source identity and relevant
observer values.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import sys
from typing import Final


SCHEMA: Final = "POST_FAST64_OBSERVER_CLOSEOUT_V1"
TERMINAL_MARKER: Final = "GPGPU-Sim: *** exit detected ***"
STAT: Final = re.compile(r"^([A-Za-z][A-Za-z0-9_]*) = (.+)$")
def observed_keys(mode: str) -> tuple[str, ...]:
    """Return only new observer fields; IO duplicate is pre-existing science."""
    if mode == "IO":
        return (
            "DTC_L1_io_alloc_to_ready_count",
            "DTC_L1_io_alloc_to_ready_sum_cycles",
            "DTC_L1_io_alloc_to_ready_max_cycles",
            "DTC_L1_io_pending_tag_evictions",
            "DTC_L1_io_pending_eviction_to_response_count",
            "DTC_L1_io_pending_eviction_to_response_sum_cycles",
            "DTC_L1_io_pending_eviction_to_response_max_cycles",
            "DTC_L1_io_observer_live_records",
        )
    if mode == "OO":
        return (
            "DTC_L1_oo_duplicate_after_eviction",
            "DTC_L1_oo_alloc_to_ready_count",
            "DTC_L1_oo_alloc_to_ready_sum_cycles",
            "DTC_L1_oo_alloc_to_ready_max_cycles",
            "DTC_L1_oo_pending_tag_evictions",
            "DTC_L1_oo_deferred_tag_eviction_to_final_reclaim_count",
            "DTC_L1_oo_deferred_tag_eviction_to_final_reclaim_sum_cycles",
            "DTC_L1_oo_deferred_tag_eviction_to_final_reclaim_max_cycles",
            "DTC_L1_oo_observer_live_records",
        )
    raise ValueError(f"unsupported observer mode {mode!r}")
SCIENTIFIC_PREFIXES: Final = ("DTC_L1_", "L2_", "gpu_tot_sim_", "gpgpu_n_")
IDENTITY_KEYS: Final = (
    "runner_schema",
    "result_classification",
    "runner_sha256",
    "simulator_sha256",
    "core_source_head",
    "workload",
    "mode",
    "config",
    "config_sha256",
    "trace_list",
    "trace_list_sha256",
    "trace_config",
    "trace_config_sha256",
)


def read_tsv_map(path: pathlib.Path) -> dict[str, str]:
    if not path.is_file():
        raise ValueError(f"missing immutable receipt {path}")
    rows = list(csv.DictReader(path.open(encoding="utf-8"), delimiter="\t"))
    if not rows or set(rows[0]) != {"key", "value"}:
        raise ValueError(f"invalid receipt schema in {path}")
    result = {row["key"]: row["value"] for row in rows}
    if len(result) != len(rows):
        raise ValueError(f"duplicate key in {path}")
    return result


def read_stats(run: pathlib.Path, mode: str) -> dict[str, str]:
    stdout = run / "simulator.stdout"
    if not stdout.is_file():
        raise ValueError(f"missing simulator output {stdout}")
    text = stdout.read_text(encoding="utf-8", errors="replace")
    if TERMINAL_MARKER not in text:
        raise ValueError(f"no natural terminal marker in {stdout}")
    stats: dict[str, str] = {}
    for line in text.splitlines():
        match = STAT.match(line)
        if match:
            key, value = match.groups()
            if not key.startswith(SCIENTIFIC_PREFIXES):
                continue
            if key in stats and stats[key] != value:
                raise ValueError(f"ambiguous repeated stat {key!r} in {stdout}")
            stats[key] = value
    for key in ("gpu_tot_sim_cycle", "gpu_tot_sim_insn", *observed_keys(mode)):
        if key not in stats:
            raise ValueError(f"missing required stat {key!r} in {stdout}")
    return stats


def read_run(run: pathlib.Path) -> tuple[dict[str, str], dict[str, str]]:
    manifest = read_tsv_map(run / "RUN_MANIFEST.tsv")
    terminal = read_tsv_map(run / "RUN_TERMINAL.tsv")
    if manifest.get("runner_schema") != "POST_FAST64_OBSERVER_QUAL_V1":
        raise ValueError(f"unexpected runner schema in {run}")
    if manifest.get("result_classification") != "POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT":
        raise ValueError(f"invalid result class in {run}")
    if terminal.get("receipt_type") != "TERMINAL" or terminal.get("simulator_exit_status") != "0":
        raise ValueError(f"non-natural/nonzero terminal receipt in {run}")
    if manifest.get("simulator_exit_status") != "0":
        raise ValueError(f"manifest does not record terminal success in {run}")
    if manifest.get("attempt_uuid") != terminal.get("attempt_uuid"):
        raise ValueError(f"attempt UUID mismatch in {run}")
    return manifest, read_stats(run, manifest.get("mode", ""))


def parse_pair(value: str) -> tuple[str, pathlib.Path, pathlib.Path, pathlib.Path]:
    try:
        name, off, on, report = value.split("=", 1)[0], *value.split("=", 1)[1].split(",")
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "pair must be NAME=OFF_RUN,ON_RUN,COMPARATOR_JSON"
        ) from error
    if not name or len((off, on, report)) != 3:
        raise argparse.ArgumentTypeError(
            "pair must be NAME=OFF_RUN,ON_RUN,COMPARATOR_JSON"
        )
    return name, pathlib.Path(off), pathlib.Path(on), pathlib.Path(report)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pair",
        type=parse_pair,
        action="append",
        required=True,
        help="NAME=OFF_RUN,ON_RUN,COMPARATOR_JSON; repeat for each D3 pair",
    )
    parser.add_argument("--identity-output", type=pathlib.Path, required=True)
    parser.add_argument("--telemetry-output", type=pathlib.Path, required=True)
    parser.add_argument(
        "--index-output",
        type=pathlib.Path,
        help="optional retained D3 qualification index TSV",
    )
    args = parser.parse_args()
    try:
        seen: set[str] = set()
        identity_rows: list[dict[str, str]] = []
        telemetry_rows: list[dict[str, str]] = []
        index_rows: list[dict[str, str]] = []
        for name, off_path, on_path, report_path in args.pair:
            if name in seen:
                raise ValueError(f"duplicate pair name {name!r}")
            seen.add(name)
            if not report_path.is_file():
                raise ValueError(f"missing comparator report {report_path}")
            report = json.loads(report_path.read_text(encoding="utf-8"))
            if report.get("schema") != "POST_FAST64_OBSERVER_EQUIVALENCE_V1" or report.get("pass") is not True:
                raise ValueError(f"comparator did not pass for {name}")
            if pathlib.Path(str(report.get("off_run"))).resolve() != off_path.resolve():
                raise ValueError(f"off path mismatch in comparator report for {name}")
            if pathlib.Path(str(report.get("on_run"))).resolve() != on_path.resolve():
                raise ValueError(f"on path mismatch in comparator report for {name}")
            off_manifest, off_stats = read_run(off_path)
            on_manifest, on_stats = read_run(on_path)
            if off_manifest.get("observer_enabled") != "0" or on_manifest.get("observer_enabled") != "1":
                raise ValueError(f"invalid observer polarity for {name}")
            mismatched = [
                key for key in IDENTITY_KEYS if off_manifest.get(key) != on_manifest.get(key)
            ]
            if mismatched:
                raise ValueError(f"scientific identity mismatch for {name}: {', '.join(mismatched)}")
            if report.get("cycles") != {"off": off_stats["gpu_tot_sim_cycle"], "on": on_stats["gpu_tot_sim_cycle"]}:
                raise ValueError(f"cycle mismatch versus comparator report for {name}")
            if report.get("instructions") != {"off": off_stats["gpu_tot_sim_insn"], "on": on_stats["gpu_tot_sim_insn"]}:
                raise ValueError(f"instruction mismatch versus comparator report for {name}")
            expected_observer_count = len(observed_keys(off_manifest["mode"]))
            if report.get("new_observer_stat_count") != expected_observer_count:
                raise ValueError(
                    f"observer field-count mismatch for {name}: "
                    f"expected {expected_observer_count}, got "
                    f"{report.get('new_observer_stat_count')!r}"
                )
            row = {
                "schema": SCHEMA,
                "pair": name,
                "classification": off_manifest["result_classification"],
                "workload": off_manifest["workload"],
                "mode": off_manifest["mode"],
                "off_attempt_uuid": off_manifest["attempt_uuid"],
                "on_attempt_uuid": on_manifest["attempt_uuid"],
                "runner_sha256": off_manifest["runner_sha256"],
                "immutable_runner_path": off_manifest["immutable_runner_path"],
                "simulator": off_manifest["simulator"],
                "simulator_sha256": off_manifest["simulator_sha256"],
                "core_source_head": off_manifest["core_source_head"],
                "config": off_manifest["config"],
                "config_sha256": off_manifest["config_sha256"],
                "trace_list": off_manifest["trace_list"],
                "trace_list_sha256": off_manifest["trace_list_sha256"],
                "trace_config": off_manifest["trace_config"],
                "trace_config_sha256": off_manifest["trace_config_sha256"],
                "off_exit_status": off_manifest["simulator_exit_status"],
                "on_exit_status": on_manifest["simulator_exit_status"],
                "cycles": off_stats["gpu_tot_sim_cycle"],
                "instructions": off_stats["gpu_tot_sim_insn"],
                "preexisting_stat_count": str(report["preexisting_stat_count"]),
                "new_observer_stat_count": str(report["new_observer_stat_count"]),
                "preexisting_exact_match": "true",
                "observer_off_all_zero": "true",
                "terminal_live_records_zero": "true",
                "comparator_report": str(report_path.resolve()),
            }
            identity_rows.append(row)
            index_rows.append(
                {
                    "schema": SCHEMA,
                    "pair": name,
                    "classification": off_manifest["result_classification"],
                    "retained_scope": "D3_OBSERVER_EQUIVALENCE_QUALIFICATION_ONLY",
                    "workload": off_manifest["workload"],
                    "mode": off_manifest["mode"],
                    "cycles": off_stats["gpu_tot_sim_cycle"],
                    "instructions": off_stats["gpu_tot_sim_insn"],
                    "preexisting_exact_match": "true",
                    "observer_off_all_zero": "true",
                    "terminal_live_records_zero": "true",
                    "identity_manifest_pair": name,
                }
            )
            for key in observed_keys(off_manifest["mode"]):
                telemetry_rows.append(
                    {
                        "schema": SCHEMA,
                        "pair": name,
                        "classification": off_manifest["result_classification"],
                        "workload": off_manifest["workload"],
                        "mode": off_manifest["mode"],
                        "counter": key,
                        "observer_off_value": off_stats[key],
                        "observer_on_value": on_stats[key],
                    }
                )
        for output, rows in ((args.identity_output, identity_rows), (args.telemetry_output, telemetry_rows)):
            output.parent.mkdir(parents=True, exist_ok=True)
            if not rows:
                raise ValueError("no rows to write")
            with output.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
        if args.index_output:
            args.index_output.parent.mkdir(parents=True, exist_ok=True)
            with args.index_output.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=list(index_rows[0]),
                    delimiter="\t",
                    lineterminator="\n",
                )
                writer.writeheader()
                writer.writerows(index_rows)
        print(f"POST_FAST64_OBSERVER_CLOSEOUT_PASS\tpairs={len(identity_rows)}")
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"POST_FAST64_OBSERVER_CLOSEOUT_ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
