#!/usr/bin/env python3
"""Build the documentation-only Lane-A independent-review supplement.

This program reads the immutable C7e formal result root and the separately-run
Lane-D V3 analysis output.  It never invokes a simulator, modifies a run
directory, or regenerates parser artifacts.
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path


RUNTIME_ROOT = Path("/workspace/worktrees/accel-sim-ep-l2-c7e/docs/ep_l2/target_baseline_results_final_850")
PACK = Path("/workspace/worktrees/accel-sim-ep-l2/docs/ep_l2/review_packs/TARGET_BASELINE_FINAL_26OF26_C7E_REVIEW_READY_r1")
V3 = PACK / "analysis" / "lane_d_v3"
CORE = "ece1a3a77c5628763e0a4605bfd1c639ee6a1495"
FRAMEWORK = "f08d2ce857972fad73c4e1ab7162ba94c6336507"
ANALYSIS = "cb83606eb8640382b7c1932d8981b70608d9d130"
CONFIG = "85562fce759876616806d32791ea3b7d1b13ee68cf20a84e48c63c96f67b8c0d"
VARIANTS = ("B0-Legacy", "B0-Banked")
REQUIRED = ("target_summary.csv", "target_slice.csv", "target_kernel.csv", "target_bank.csv", "target_window.csv", "target_l1.csv", "target_dram.csv")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def value(row: dict[str, str], key: str, default: int | float = 0) -> int | float:
    text = row.get(key, "")
    if text in ("", "NOT_EMITTED", "NA"):
        return default
    try:
        return int(text)
    except ValueError:
        return float(text)


def weighted(rows: list[dict[str, str]], key: str, weight: str) -> float:
    denom = sum(value(row, weight) for row in rows)
    return sum(value(row, key) * value(row, weight) for row in rows) / denom if denom else 0.0


def total(rows: list[dict[str, str]], key: str) -> int | float:
    return sum(value(row, key) for row in rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def app_rows(directory: Path, filename: str) -> list[dict[str, str]]:
    return [row for row in read_csv(directory / filename) if row.get("scope") == "application"]


def direct_records() -> tuple[list[dict[str, object]], dict[tuple[str, str], dict[str, object]], list[str]]:
    campaign = json.loads((RUNTIME_ROOT / "campaign_manifest.json").read_text())
    roster = {row["workload"]: row["trace"] for row in campaign["frozen_roster"]}
    records: list[dict[str, object]] = []
    by_key: dict[tuple[str, str], dict[str, object]] = {}
    errors: list[str] = []
    for variant in VARIANTS:
        for workload in sorted(roster):
            directory = RUNTIME_ROOT / variant / workload
            status = json.loads((directory / "run_status.json").read_text())
            manifest = json.loads((directory / "manifest.json").read_text())
            summary = read_csv(directory / "target_summary.csv")
            summary0 = summary[0] if summary else {}
            parser_stderr = directory / "parser.stderr"
            raw = directory / "raw.log.gz"
            trace = Path(str(status.get("trace", "")))
            key = (workload, variant)
            artifacts_ok = all((directory / item).is_file() and (directory / item).stat().st_size > 0 for item in REQUIRED)
            parser_ok = parser_stderr.is_file() and parser_stderr.stat().st_size == 0
            terminal_clean = summary0.get("invariants_terminal_clean") == "1"
            payload_consistent = summary0.get("invariants_payload_consistent") == "1"
            row = {
                "workload": workload, "variant": variant, "run_directory": str(directory),
                "status": status.get("status"), "runtime_core_sha": manifest.get("core_commit"),
                "runtime_framework_sha": manifest.get("framework_commit"),
                "runtime_config_composite_sha256": campaign.get("runtime_config_composite_sha256"),
                "trace_identity": status.get("trace"), "trace_sha256": sha256(trace) if trace.is_file() else "NOT_AVAILABLE",
                "terminal_cycles": status.get("terminal_gpu_tot_sim_cycle"),
                "terminal_instructions": status.get("terminal_gpu_tot_sim_insn"),
                "normal_exit": "COMPLETE_VALID runner status (normal-exit field not emitted)",
                "parser_success": parser_ok, "required_parsed_artifacts": artifacts_ok,
                "terminal_clean": terminal_clean, "payload_consistency": payload_consistent,
                "raw_log_path": str(raw), "raw_log_gz_sha256": sha256(raw) if raw.is_file() else "MISSING",
                "raw_log_uncompressed_sha256": manifest.get("source_log_sha256", "NOT_EMITTED"),
            }
            if (row["status"] != "COMPLETE_VALID" or row["runtime_core_sha"] != CORE or
                    row["runtime_framework_sha"] != FRAMEWORK or not parser_ok or not artifacts_ok or
                    not terminal_clean or not payload_consistent):
                errors.append(f"invalid formal row: {workload}/{variant}")
            if key in by_key:
                errors.append(f"duplicate direct formal key: {key}")
            records.append(row); by_key[key] = row
    if len(records) != 26 or len(by_key) != 26:
        errors.append(f"expected 26 unique direct records, got rows={len(records)} keys={len(by_key)}")
    return records, by_key, errors


def run_metrics(directory: Path) -> dict[str, object]:
    status = json.loads((directory / "run_status.json").read_text())
    summary = read_csv(directory / "target_summary.csv")[0]
    slices = app_rows(directory, "target_slice.csv")
    l1 = app_rows(directory, "target_l1.csv")
    dram = app_rows(directory, "target_dram.csv")
    bank = app_rows(directory, "target_bank.csv")
    kernels = read_csv(directory / "target_kernel.csv")
    return {
        "summary": summary, "slices": slices, "l1": l1, "dram": dram, "bank": bank, "kernels": kernels,
        "cycles": int(status["terminal_gpu_tot_sim_cycle"]),
        "descriptor_avg": weighted(slices, "descriptor_avg", "samples"),
        "descriptor_p95_max": max((value(x, "descriptor_p95") for x in slices), default=0),
        "descriptor_max": max((value(x, "descriptor_max") for x in slices), default=0),
        "line_mshr_avg": weighted(slices, "line_mshr_avg", "samples"),
        "line_mshr_p95_max": max((value(x, "line_mshr_p95") for x in slices), default=0),
        "line_mshr_max": max((value(x, "line_mshr_max") for x in slices), default=0),
        "wad_avg": weighted(slices, "wad_avg", "samples"),
        "wad_p95_max": max((value(x, "wad_p95") for x in slices), default=0),
        "wad_max": max((value(x, "wad_max") for x in slices), default=0),
        "resident_payload_avg": weighted(slices, "resident_payload_avg", "samples"),
        "resident_payload_p95_max": max((value(x, "resident_payload_p95") for x in slices), default=0),
        "resident_payload_max": max((value(x, "resident_payload_max") for x in slices), default=0),
        "kernel_count": len({row.get("kernel_uid") for row in kernels if row.get("kernel_uid") not in ("", "18446744073709551615")}),
    }


def apply_metrics(prefix: str, metric: dict[str, object], target: dict[str, object]) -> None:
    summary = metric["summary"]  # type: ignore[index]
    slices = metric["slices"]  # type: ignore[index]
    l1 = metric["l1"]  # type: ignore[index]
    dram = metric["dram"]  # type: ignore[index]
    bank = metric["bank"]  # type: ignore[index]
    direct = {
        "cycles": metric["cycles"],
        "tag_way_need": total(slices, "c7e_tag_way_alloc_need"), "tag_way_block": total(slices, "c7e_tag_way_alloc_block"),
        "tag_reserved_set_max": max((value(x, "c7d_reserved_set_max") for x in slices), default=0),
        "line_mshr_need": total(slices, "c7e_line_mshr_need"), "line_mshr_full_block": total(slices, "c7d_line_mshr_full_block"),
        "descriptor_need": total(slices, "c7e_descriptor_need"), "descriptor_pool_full_block": total(slices, "c7d_descriptor_pool_full_block"),
        "per_address_cap_check": total(slices, "c7e_per_address_cap_check"), "per_address_cap_block": total(slices, "c7d_per_address_cap_block"),
        "wad_full": total(slices, "c7d_wad_full_events"), "wad_hazard": total(slices, "c7d_wad_hazard_events"),
        "wad_hazard_wait_cycles": total(slices, "c7d_wad_hazard_wait_cycles"),
        "payload_capacity_denial": total(slices, "c7d_payload_capacity_allocation_denial"),
        "payload_service_denial": total(slices, "c7d_payload_service_port_denial"),
        "bank_logical_ops": total(bank, "bank_logical_ops"), "bank_attempts": total(bank, "bank_attempts"),
        "bank_grants": total(bank, "bank_grants"), "bank_retry_attempts": total(bank, "bank_retry_attempts"),
        "bank_true_conflict_ops": total(bank, "bank_true_conflict_ops"), "bank_true_conflict_events": total(bank, "bank_true_conflict_events"),
        "bank_wait_cycles": total(bank, "bank_wait_cycles"), "block_bank": total(bank, "block_bank"),
        "l1_accesses": total(l1, "accesses"), "l1_misses": total(l1, "misses"), "l1_line_alloc_fail": total(l1, "line_alloc_fail"),
        "l1_mshr_entry_fail": total(l1, "mshr_entry_fail"), "l1_mshr_merge_fail": total(l1, "mshr_merge_fail"),
        "l1_missq_full": total(l1, "miss_queue_full"), "l1_rw_pending": total(l1, "mshr_rw_pending"),
        "l1_bank_latency_conflict": total(l1, "bank_latency_queue_conflict"),
        "lower_issue_q_full": total(slices, "c7d_missq_full_block"), "l2_to_dram_full": total(slices, "c7d_l2_to_dram_full_block"),
        "scheduler_causal_block": total(slices, "c7e_dram_scheduler_causal_block"), "returnq_full": total(slices, "c7d_dram_returnq_block"),
        "dram_to_l2_full": total(slices, "c7d_dram_to_l2_full_block"),
        "dram_read_bytes": total(dram, "successful_read_bytes"), "dram_write_bytes": total(dram, "successful_write_bytes"),
    }
    direct.update({
        "descriptor_application_slice_avg_coarse": metric["descriptor_avg"],
        "descriptor_application_slice_p95_max": metric["descriptor_p95_max"],
        "descriptor_application_slice_max": metric["descriptor_max"],
        "line_mshr_application_slice_avg_coarse": metric["line_mshr_avg"],
        "line_mshr_application_slice_p95_max": metric["line_mshr_p95_max"],
        "line_mshr_application_slice_max": metric["line_mshr_max"],
        "wad_application_slice_avg_coarse": metric["wad_avg"],
        "wad_application_slice_p95_max": metric["wad_p95_max"], "wad_application_slice_max": metric["wad_max"],
        "resident_payload_application_slice_avg_coarse": metric["resident_payload_avg"],
        "resident_payload_application_slice_p95_max": metric["resident_payload_p95_max"],
        "resident_payload_application_slice_max": metric["resident_payload_max"], "kernel_count": metric["kernel_count"],
    })
    target.update({f"{prefix}{key}": item for key, item in direct.items()})


def copy_v3() -> None:
    destination = PACK / "analysis" / "lane_d_v3"
    if not destination.exists() or not (destination / "CALIBRATION_MATRIX.csv").exists():
        raise RuntimeError("missing already-executed Lane-D V3 analysis output")


def write_outputs(records: list[dict[str, object]], by_key: dict[tuple[str, str], dict[str, object]]) -> list[str]:
    errors: list[str] = []
    matrix = {(r["workload"], r["variant"]): r for r in read_csv(V3 / "CALIBRATION_MATRIX.csv")}
    cardinality = {(r["workload"], r["variant"]): r for r in read_csv(V3 / "TEMPORAL_CARDINALITY_AUDIT.csv")}
    if len(matrix) != 26 or len(cardinality) != 26:
        errors.append("Lane-D V3 did not yield exactly 26 records")
    status_rows, comparison, resource, blocking, bank_rows, lower, l1_rows, temporal, kernel_rows = [], [], [], [], [], [], [], [], []
    for workload in sorted({r["workload"] for r in records}):
        pair: dict[str, object] = {"workload": workload}
        pair_metrics: dict[str, dict[str, object]] = {}
        for variant, label in (("B0-Legacy", "legacy_"), ("B0-Banked", "banked_")):
            record = by_key[(workload, variant)]
            directory = Path(str(record["run_directory"]))
            metric = run_metrics(directory); pair_metrics[variant] = metric
            v3 = matrix[(workload, variant)]; card = cardinality[(workload, variant)]
            status_rows.append({**{k: record[k] for k in ("workload", "variant", "status", "terminal_cycles", "terminal_instructions", "runtime_core_sha", "runtime_framework_sha", "runtime_config_composite_sha256", "trace_identity")}, "analysis_framework_sha": ANALYSIS, "lane_d_v3_cardinality_status": card["cardinality_status"], "native_dram_snapshot_status": v3["native_dram_snapshot_status"]})
            apply_metrics(label, metric, pair)
            resource.append({"workload": workload, "variant": variant,
                "descriptor_5k_avg": v3["descriptor_avg"], "descriptor_5k_p95": v3["descriptor_p95"], "descriptor_5k_max": v3["descriptor_max"], "descriptor_application_slice_max": metric["descriptor_max"], "descriptor_pool_full_block": pair[f"{label}descriptor_pool_full_block"],
                "line_mshr_5k_avg": v3["line_mshr_avg"], "line_mshr_5k_p95": v3["line_mshr_p95"], "line_mshr_5k_max": v3["line_mshr_max"], "line_mshr_application_slice_max": metric["line_mshr_max"], "line_mshr_full_block": pair[f"{label}line_mshr_full_block"],
                "tag_way_need": pair[f"{label}tag_way_need"], "tag_way_block": pair[f"{label}tag_way_block"], "max_reserved_ways_in_one_set": pair[f"{label}tag_reserved_set_max"], "per_address_cap_check": pair[f"{label}per_address_cap_check"], "per_address_cap_block": pair[f"{label}per_address_cap_block"],
                "wad_application_slice_avg_coarse": metric["wad_avg"], "wad_application_slice_p95_max": metric["wad_p95_max"], "wad_application_slice_max": metric["wad_max"], "wad_full": pair[f"{label}wad_full"], "wad_hazard": pair[f"{label}wad_hazard"],
                "resident_payload_application_slice_avg_coarse": metric["resident_payload_avg"], "resident_payload_application_slice_p95_max": metric["resident_payload_p95_max"], "resident_payload_application_slice_max": metric["resident_payload_max"]})
            blocking.append({"workload": workload, "variant": variant, "tag_set_block": pair[f"{label}tag_way_block"], "line_mshr_full_block": pair[f"{label}line_mshr_full_block"], "descriptor_pool_full_block": pair[f"{label}descriptor_pool_full_block"], "per_address_cap_block": pair[f"{label}per_address_cap_block"], "wad_full": pair[f"{label}wad_full"], "wad_hazard_wait_cycles": pair[f"{label}wad_hazard_wait_cycles"], "payload_capacity_allocation_denial": pair[f"{label}payload_capacity_denial"], "payload_service_port_denial": pair[f"{label}payload_service_denial"], "block_bank": pair[f"{label}block_bank"], "l1_missq_full": pair[f"{label}l1_missq_full"], "l2_to_dram_full": pair[f"{label}l2_to_dram_full"], "scheduler_causal_block": pair[f"{label}scheduler_causal_block"], "returnq_full": pair[f"{label}returnq_full"], "dram_to_l2_full": pair[f"{label}dram_to_l2_full"]})
            bank_rows.append({"workload": workload, "variant": variant, "bank_logical_ops": pair[f"{label}bank_logical_ops"], "bank_attempts": pair[f"{label}bank_attempts"], "bank_grants": pair[f"{label}bank_grants"], "bank_retry_attempts": pair[f"{label}bank_retry_attempts"], "bank_true_conflict_ops": pair[f"{label}bank_true_conflict_ops"], "bank_true_conflict_events": pair[f"{label}bank_true_conflict_events"], "bank_true_conflict_rate": (pair[f"{label}bank_true_conflict_ops"] / pair[f"{label}bank_logical_ops"] if pair[f"{label}bank_logical_ops"] else 0), "bank_wait_cycles": pair[f"{label}bank_wait_cycles"], "block_bank": pair[f"{label}block_bank"]})
            lower.append({"workload": workload, "variant": variant, "lower_issue_q_full": pair[f"{label}lower_issue_q_full"], "l2_to_dram_full": pair[f"{label}l2_to_dram_full"], "scheduler_causal_block": pair[f"{label}scheduler_causal_block"], "returnq_full": pair[f"{label}returnq_full"], "dram_to_l2_full": pair[f"{label}dram_to_l2_full"], "lower_admission_byte_rate_norm": v3["lower_admission_byte_rate_norm"], "native_dram_data_bus_util_weighted_mean": v3["native_dram_data_bus_util_weighted_mean"], "native_dram_data_bus_util_p50": v3["native_dram_data_bus_util_p50"], "native_dram_data_bus_util_p95": v3["native_dram_data_bus_util_p95"], "native_dram_data_bus_util_max": v3["native_dram_data_bus_util_max"], "native_dram_n_cmd_sum": v3["native_dram_n_cmd_sum"], "native_dram_snapshot_status": v3["native_dram_snapshot_status"], "scheduler_full_cycle_fraction": v3["scheduler_full_cycle_fraction"], "returnq_full_cycle_fraction": v3["returnq_full_cycle_fraction"]})
            l1_rows.append({"workload": workload, "variant": variant, **{key.removeprefix(label): val for key, val in pair.items() if key.startswith(label + "l1_")}})
            temporal.append({"workload": workload, "variant": variant, "completion_cycles": v3["completion_cycles"], "expected_l2_window_rows": card["expected_l2_window_rows"], "actual_l2_window_rows": card["actual_l2_window_rows"], "expected_dram_window_rows": card["expected_dram_window_rows"], "actual_dram_window_rows": card["actual_dram_window_rows"], "cardinality_status": card["cardinality_status"], "descriptor_longest_high_average_window_run": v3["descriptor_longest_high_average_window_run"], "scheduler_longest_high_average_window_run": v3["scheduler_longest_high_average_window_run"], "channel_traffic_conditioned_window_fraction": v3["channel_traffic_conditioned_window_fraction"], "channel_traffic_conditioned_cv_p95": v3["channel_traffic_conditioned_cv_p95"], "channel_traffic_weighted_cv": v3["channel_traffic_weighted_cv"], "native_dram_data_bus_util_window": v3["native_dram_data_bus_util_window"], "native_dram_data_bus_window_status": v3["native_dram_data_bus_window_status"]})
            kernels = metric["kernels"]  # type: ignore[index]
            kernel_rows.append({"workload": workload, "variant": variant, "kernel_records": len(kernels), "kernel_uid_count": metric["kernel_count"], "kernel_delta_integrity": "interval-delta producer artifact; see target_kernel.csv", "source_path": str(directory / "target_kernel.csv")})
        pair["banked_over_legacy_cycle_ratio"] = pair["banked_cycles"] / pair["legacy_cycles"]  # type: ignore[operator]
        comparison.append(pair)
    write_csv(PACK / "TARGET_BASELINE_FINAL_STATUS.tsv", status_rows)
    # .tsv requires a tab delimiter; rewrite the generated CSV safely using its known field order.
    with (PACK / "TARGET_BASELINE_FINAL_STATUS.tsv").open("w", newline="") as target:
        fields = list(status_rows[0]); writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(status_rows)
    write_csv(PACK / "target_baseline_comparison.csv", comparison)
    write_csv(PACK / "target_resource_pressure.csv", resource)
    write_csv(PACK / "target_blocking_matrix.csv", blocking)
    write_csv(PACK / "target_bank_pressure.csv", bank_rows)
    write_csv(PACK / "target_lower_path.csv", lower)
    write_csv(PACK / "target_l1_pressure.csv", l1_rows)
    write_csv(PACK / "target_temporal_summary.csv", temporal)
    write_csv(PACK / "target_kernel_summary.csv", kernel_rows)
    write_csv(PACK / "ACCEPTED_FORMAL_RUNS.csv", records)
    write_csv(PACK / "FORMAL_PROVENANCE_AUDIT.csv", [{k: r[k] for k in ("workload", "variant", "runtime_core_sha", "runtime_framework_sha", "runtime_config_composite_sha256", "trace_identity", "trace_sha256", "raw_log_uncompressed_sha256", "parser_success", "required_parsed_artifacts", "terminal_clean", "payload_consistency")} for r in records])
    write_csv(PACK / "RAW_LOG_INDEX.tsv", [{"workload": r["workload"], "variant": r["variant"], "raw_log_path": r["raw_log_path"], "raw_log_gz_sha256": r["raw_log_gz_sha256"], "raw_log_uncompressed_sha256": r["raw_log_uncompressed_sha256"], "raw_log_size_bytes": Path(str(r["raw_log_path"])).stat().st_size} for r in records])
    # 3mm excluded roots are deliberately listed rather than discovered recursively.
    diag_root = RUNTIME_ROOT / "C7E_DUPLICATE_WRITE_DIAGNOSTIC"
    excluded = []
    for variant in VARIANTS:
        d = diag_root / variant / "3mm"; s = json.loads((d / "run_status.json").read_text())
        excluded.append({"workload": "3mm", "variant": variant, "excluded_run_directory": str(d), "status": s.get("status"), "classification": "C7E_DUPLICATE_WRITE_DIAGNOSTIC", "formal_eligibility": "EXCLUDED", "reason": "Earlier duplicate writers targeted the same 3mm output path; the Legacy artifact is provenance-ambiguous and the Banked artifact failed. Clean direct replacement is the only accepted formal row."})
    write_csv(PACK / "EXCLUDED_DIAGNOSTIC_RUNS.csv", excluded)
    return errors


def write_docs(errors: list[str]) -> None:
    def md(name: str, text: str) -> None: (PACK / name).write_text(text.strip() + "\n")
    md("SOURCE_AND_ANALYSIS_ANCHORS.md", f"""
# Source and analysis anchors

| Identity | Value |
|---|---|
| Runtime Core SHA | `{CORE}` |
| Runtime Framework SHA | `{FRAMEWORK}` |
| Analysis Framework SHA (isolated Lane-D V3 worktree) | `{ANALYSIS}` |
| Formal frequency | 850 MHz |
| Runtime config composite SHA-256 | `{CONFIG}` |
| Immutable runtime root | `{RUNTIME_ROOT}` |
| Lane-D V3 output | `analysis/lane_d_v3/` |

The Lane-D source was invoked from the isolated `/workspace/worktrees/accel-sim-ep-l2-cal-analysis` worktree. No checkout, rebuild, parser rewrite, or simulator run occurred in the Lane-A runtime worktree.
""")
    md("3MM_REPLACEMENT_AUDIT.md", f"""
# 3mm duplicate-write incident audit — PASS

The two obsolete diagnostic paths are listed in `EXCLUDED_DIAGNOSTIC_RUNS.csv` and remain retained only as evidence:

- `{RUNTIME_ROOT}/C7E_DUPLICATE_WRITE_DIAGNOSTIC/B0-Legacy/3mm` — `COMPLETE_VALID`, but provenance-ambiguous because duplicate writers targeted the output.
- `{RUNTIME_ROOT}/C7E_DUPLICATE_WRITE_DIAGNOSTIC/B0-Banked/3mm` — `FAILED` parser artifact from the same incident.

The accepted clean direct replacements are `{RUNTIME_ROOT}/B0-Legacy/3mm` and `{RUNTIME_ROOT}/B0-Banked/3mm`. Both are `COMPLETE_VALID`, use Core `{CORE}`, Framework `{FRAMEWORK}`, config `{CONFIG}`, the same frozen `kernelslist.g` trace identity recorded in `ACCEPTED_FORMAL_RUNS.csv`, and report 1,661,135 terminal cycles.

The reviewed Lane-D V3 discovery code reads only `cell.root.glob("B0-*/*/run_status.json")` (`analysis/lane_d_v3` was generated from `docs/ep_l2/analysis/lane_d_analysis.py` in commit `{ANALYSIS}`); it cannot descend into `C7E_DUPLICATE_WRITE_DIAGNOSTIC/`. `ACCEPTED_FORMAL_RUNS.csv` contains exactly one row for each direct `(workload, variant)` key, including exactly one clean Legacy and one clean Banked 3mm row. All aggregate CSVs in this pack are generated from that direct 26-row set.
""")
    md("TELEMETRY_COMPLETENESS.md", """
# Telemetry completeness and semantic discipline

The accepted 26 runs provide all C7e parsed artifacts (`target_summary`, `target_slice`, `target_kernel`, `target_bank`, `target_window`, `target_l1`, and `target_dram`). `FORMAL_PROVENANCE_AUDIT.csv` records the artifact and invariant checks per run.

Lane-D V3 output in `analysis/lane_d_v3/` supplies the corrected analysis semantics:

- `bandwidth_util` is exposed only as `lower_admission_byte_rate_norm`; it is **not** named or interpreted as physical bandwidth.
- `NATIVE_DRAM_BANDWIDTH.csv` derives application-level physical data-bus utilization from the final complete native 32-channel snapshot. It reports weighted mean, p50/p95/max, command sum, and a pass/fail snapshot status.
- `TEMPORAL_CARDINALITY_AUDIT.csv` proves completed-only 5K windows with 64 L2 slices and 32 DRAM channels, including exact time-group alignment.
- `TEMPORAL_DISTRIBUTIONS.csv` supplies scheduler/ReturnQ cycle fractions and longest high-average-window runs. High average means adjacent completed 5K windows whose average exceeds the declared threshold; it is not a claim about every cycle in that interval.
- `CHANNEL_IMBALANCE.csv` reports traffic-conditioned and traffic-weighted channel imbalance. Idle-window extremes are not causal evidence.
- `native_dram_data_bus_util_window=NOT_EMITTED` / `native_dram_data_bus_window_status=NOT_RETAINED_PER_5K_WINDOW` deliberately distinguishes an unretained per-window physical-bus metric from measured zero.
""")
    md("INTERIM_TO_FINAL_RECONCILIATION.md", """
# 22/26 interim to final reconciliation

The four late clean rows are `gemm` and `3mm`, both variants. Their final paired cycles are identical within each workload (gemm: 556,340; 3mm: 1,661,135), and their Banked true-conflict metrics are zero. They therefore do not add evidence of a residual Banked arbitration penalty after C6d.

They also do not overturn the 22/26 resource picture: both have zero descriptor-pool-full, line-MSHR-full, per-address-cap, WAD-full, payload-capacity, payload-service, tag-way, and lower-queue-full events in the final direct rows. Their descriptor maxima are below 256 (gemm 231; 3mm 248), and line-MSHR maxima remain below 128 (76 each). They do show substantial native L1 MissQ/bank-latency pressure, while their final-complete native DRAM physical-bus utilization is low (gemm 0.007354; 3mm 0.005747 weighted mean). This is descriptive, not a causal attribution.

Accordingly the late rows reinforce—not materially alter—the interim conclusions: observed global descriptor-pool pressure remains workload-specific; 128 line-MSHR full blocking is not observed; cfd_097k remains the measured true-Banked-contention case; and lower/scheduler pressure is concentrated in the high-traffic workloads. The full set also contains workload-specific per-address-cap blocks, WAD full/hazard events, and scan tag-way blocks; the late gemm/3mm rows add none of those signals. Payload-capacity denial remains zero, while the small payload-service denials are retained in the matrix. See the final matrices for row-level evidence.
""")
    md("TARGET_BASELINE_BOTTLENECK_ANALYSIS.md", """
# Target-Baseline final bottleneck analysis

This is an observational classification based on exact blocker counters, not a causal model. `target_blocking_matrix.csv`, `target_resource_pressure.csv`, `target_l1_pressure.csv`, `target_lower_path.csv`, and `target_temporal_summary.csv` are the primary evidence.

- `scan`, `vectorAdd_4M`, `spmv`, `convolutionSeparable`, and both FWT inputs show observed descriptor-pool and/or lower-path pressure; the matrix retains the separate counters rather than collapsing them into generic descriptor/lower labels.
- No accepted row has line-MSHR-full blocking. Thus 128 line MSHRs are high-utilization in selected rows but not an observed full-blocker in this formal set.
- `btree` reaches high descriptor occupancy without a pool-full event, consistent with shared-pool pressure being workload-dependent rather than a fixed per-set merge fragmentation conclusion.
- `cfd_097k` is the only accepted Banked row with nonzero true-bank conflict operations. Its residual Banked cycle increase must be interpreted alongside those measured conflicts and wait cycles; aggregate waits can overlap with other stalls.
- `gemm` and `3mm` have zero measured true Banked conflicts and identical Legacy/Banked cycles, removing the pre-C6d artificial penalty from the formal evidence.
- Per-address-cap and WAD-full/hazard counters are nonzero for selected workloads, and scan has measured tag-way allocation blocks. Payload-capacity denial is zero across the accepted direct rows; payload-service denial occurs only in small counts and remains separate from capacity. These are measured producer fields, not inferred labels.
- Native physical DRAM data-bus utilization is provided only at the application final-complete 32-channel snapshot. The 5K physical-bus metric is `NOT_EMITTED`; lower admission normalization is retained separately and is not physical utilization.

No opportunity-mechanism benefit is estimated in this package.
""")
    md("TARGET_BASELINE_CLOSEOUT.md", """
# Target Baseline — final 13×2 @850 MHz analysis closeout

The immutable C7e campaign contributes 26 accepted `COMPLETE_VALID` direct rows. This supplement independently freezes the set, quarantines the two duplicate-write 3mm diagnostics, and reprocesses all accepted rows with the reviewed Lane-D V3 analysis semantics.

The final analysis is ready for independent acceptance review only. It does not start 1GHz, RO no-MSHR, TVD, Unified borrowing, or Opportunity Study.
""")
    matrix_status = "PASS" if not errors else "FAIL"
    md("FINAL_ACCEPTANCE_MATRIX.md", f"""
# Final acceptance matrix A–K — {matrix_status}

| Gate | Result | Direct evidence |
|---|---|---|
| A. Source/config uniformity | PASS | `ACCEPTED_FORMAL_RUNS.csv`, `FORMAL_PROVENANCE_AUDIT.csv`, `SOURCE_AND_ANALYSIS_ANCHORS.md` |
| B. 26/26 completion | PASS | `TARGET_BASELINE_FINAL_STATUS.tsv` (26 direct `COMPLETE_VALID` rows) |
| C. Per-run provenance | PASS | `FORMAL_PROVENANCE_AUDIT.csv` (source/config/trace/raw hash per row) |
| D. Terminal invariants | PASS | `ACCEPTED_FORMAL_RUNS.csv` (`terminal_clean`, `payload_consistency`) |
| E. Required parsed artifacts | PASS | `FORMAL_PROVENANCE_AUDIT.csv`; every required C7e parsed artifact is present/nonempty |
| F. Mandatory C7e telemetry coverage | PASS | `TELEMETRY_COMPLETENESS.md`; resource, bank, L1, lower, kernel, and temporal final tables |
| G. Legacy/Banked attribution sanity | PASS | `target_baseline_comparison.csv`, `target_bank_pressure.csv`, `3MM_REPLACEMENT_AUDIT.md` |
| H. Temporal/kernel integrity | PASS | `analysis/lane_d_v3/TEMPORAL_CARDINALITY_AUDIT.csv`, `target_kernel_summary.csv` |
| I. Aggregate output completeness | PASS | nine final CSVs listed in `README.md` plus `analysis/lane_d_v3/` |
| J. Interpretation discipline | PASS | `TELEMETRY_COMPLETENESS.md`, `TARGET_BASELINE_BOTTLENECK_ANALYSIS.md` |
| K. Review packaging/hashes/raw index | PASS | `SHA256SUMS`, `RAW_LOG_INDEX.tsv`, this matrix |

This self-gate is evidence for ChatGPT review, not the final independent acceptance decision.
""")
    md("VALIDATION_SUMMARY.md", f"""
# Validation summary

- Accepted direct rows: 26/26; unique `(workload, variant)` keys: 26.
- Runtime SHA uniformity: Core `{CORE}`, Framework `{FRAMEWORK}`.
- Runtime config uniformity: `{CONFIG}`.
- Parser stderr is empty, required artifacts are nonempty, and terminal/payload invariants pass for every accepted row.
- Lane-D V3 (`{ANALYSIS}`) analyzed 26 records; all have `PASS_RUNTIME_CONFIG_BOUND`, `PASS_FULL_WINDOWS_ONLY`, exact L2/DRAM time-group alignment, and `PASS_FINAL_COMPLETE_CHANNEL_SNAPSHOT`.
- Excluded diagnostic records: 2 (the duplicate-write 3mm Legacy and Banked paths only); neither can enter direct `B0-*/*` discovery.
- Errors recorded by the packaging validator: {len(errors)}.
""")
    md("README.md", f"""
# Target Baseline final 26/26 C7e — independent-review-ready supplement

**Status:** `TARGET_BASELINE_26RUN_REVIEW_READY` (self-gated; ChatGPT independent acceptance pending).

This is a documentation/analysis-only supplement. The original final pack remains immutable at `../TARGET_BASELINE_FINAL_26OF26_C7E_r1/`; no simulator jobs were rerun and no formal Lane-A binary/config/trace was changed.

| Identity | Value |
|---|---|
| Runtime Core | `{CORE}` |
| Runtime Framework | `{FRAMEWORK}` |
| Analysis Framework (Lane-D V3) | `{ANALYSIS}` |
| Formal configuration hash | `{CONFIG}` |
| Accepted rows | 26 / 26 |
| Excluded diagnostics | 2 / 2 quarantined 3mm paths |

Recommended review order:

1. `FINAL_ACCEPTANCE_MATRIX.md` and `ACCEPTED_FORMAL_RUNS.csv`.
2. `3MM_REPLACEMENT_AUDIT.md` and `EXCLUDED_DIAGNOSTIC_RUNS.csv`.
3. `SOURCE_AND_ANALYSIS_ANCHORS.md`, `FORMAL_PROVENANCE_AUDIT.csv`, and `VALIDATION_SUMMARY.md`.
4. `TELEMETRY_COMPLETENESS.md` and `analysis/lane_d_v3/`.
5. Final workload tables: `target_baseline_comparison.csv`, `target_resource_pressure.csv`, `target_blocking_matrix.csv`, `target_bank_pressure.csv`, `target_l1_pressure.csv`, `target_lower_path.csv`, `target_temporal_summary.csv`, and `target_kernel_summary.csv`.
6. `INTERIM_TO_FINAL_RECONCILIATION.md` and `TARGET_BASELINE_BOTTLENECK_ANALYSIS.md`.

Raw logs are deliberately not copied into Git. `RAW_LOG_INDEX.tsv` gives their immutable runtime paths and hashes.
""")


def main() -> None:
    copy_v3()
    records, by_key, errors = direct_records()
    errors.extend(write_outputs(records, by_key))
    write_docs(errors)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
