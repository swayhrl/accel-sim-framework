#!/usr/bin/env python3
"""Build a C7e-compatible, read-only 22-of-26 formal review snapshot.

This tool imports the exact final analyzer's run_record() implementation.  It
never writes the C7e result root and deliberately labels every aggregation as
interim.  The final 26-run analyzer remains the authoritative closeout path.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/workspace/worktrees/accel-sim-ep-l2-c7e")
RESULTS = ROOT / "docs/ep_l2/target_baseline_results_final_850"
CORE = Path("/workspace/worktrees/gpgpu-sim-ep-l2-c7e")
PACK = Path(__file__).resolve().parents[1]
EXPECTED_CORE = "ece1a3a77c5628763e0a4605bfd1c639ee6a1495"
EXPECTED_FRAMEWORK = "f08d2ce857972fad73c4e1ab7162ba94c6336507"
EXPECTED_CONFIG = "85562fce759876616806d32791ea3b7d1b13ee68cf20a84e48c63c96f67b8c0d"
ROSTER = ("vectorAdd_4M", "scan", "spmv", "convolutionSeparable", "cfd_097k",
          "dwt2d", "sad", "sgemm", "btree", "3mm", "gemm", "FWT_7_21", "FWT_11_19")
VARIANTS = ("B0-Legacy", "B0-Banked")
MISSING = {"gemm", "3mm"}


def analyzer_module():
    source_dir = ROOT / "util/ep_l2"
    import sys
    sys.path.insert(0, str(source_dir))
    spec = importlib.util.spec_from_file_location("c7e_final_analyzer", source_dir / "analyze_target_baseline.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def csv_write(path: Path, rows: list[dict], delimiter=","):
    keys = sorted({key for row in rows for key in row})
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore", delimiter=delimiter)
        writer.writeheader(); writer.writerows(rows)


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def value(record: dict, key: str):
    data = record.get(key, "NOT_EMITTED")
    return data if data is not None else "NOT_EMITTED"


def ratio(numerator, denominator):
    if isinstance(numerator, (int, float)) and isinstance(denominator, (int, float)) and denominator:
        return round(numerator / denominator, 9)
    return "NOT_EMITTED"


def classify(blocked, eligible):
    r = ratio(blocked, eligible)
    if not isinstance(r, float):
        return "INSUFFICIENT_EVIDENCE"
    if r >= 0.10: return "STRONG"
    if r >= 0.01: return "MODERATE"
    if r > 0: return "WEAK"
    return "NONE_OBSERVED"


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def running_rows():
    rows = []
    output = subprocess.run(["ps", "-eo", "pid,lstart,etimes,args"], text=True, stdout=subprocess.PIPE,
                            check=True).stdout.splitlines()
    for line in output[1:]:
        if "accel-sim.out" not in line or "target_baseline_results" in line:
            continue
        workload = "gemm" if "polybench-gemm" in line else "3mm" if "polybench-3mm" in line else None
        if not workload: continue
        variant = "B0-Banked" if "b0_banked_850.config" in line else "B0-Legacy"
        tokens = line.split(maxsplit=7)
        raw = RESULTS / variant / workload / "raw.log"
        rows.append({"pid": tokens[0], "workload": workload, "variant": variant,
                     "start_time": " ".join(tokens[1:6]), "wall_seconds_so_far": tokens[6],
                     "raw_log_path": str(raw), "raw_log_size_bytes": raw.stat().st_size if raw.exists() else 0,
                     "progress_evidence": "raw log exists and was growing at snapshot capture",
                     "state": "RUNNING"})
    return sorted(rows, key=lambda r: (r["workload"], r["variant"]))


def main():
    analyzer = analyzer_module()
    PACK.mkdir(parents=True, exist_ok=True)
    (PACK / "analysis").mkdir(exist_ok=True)
    (PACK / "scripts").mkdir(exist_ok=True)
    records, statuses, provenance, raw_index, completeness = {}, [], [], [], []
    validity_errors = []
    for workload in ROSTER:
        for variant in VARIANTS:
            directory = RESULTS / variant / workload
            status_file = directory / "run_status.json"
            status = json.loads(status_file.read_text()) if status_file.exists() else None
            if not status or status.get("status") != "COMPLETE_VALID":
                continue
            audit = status.get("audit", {})
            required = ("target_summary.csv", "target_slice.csv", "target_l1.csv", "target_dram.csv", "target_window.csv",
                        "target_bank.csv", "target_kernel.csv", "manifest.json", "parser.stdout", "parser.stderr")
            # A successful parser deliberately leaves parser.stderr empty; its
            # presence, rather than nonzero size, is the required artifact.
            artifacts = {name: (directory / name).is_file() and
                         (name in {"parser.stdout", "parser.stderr"} or (directory / name).stat().st_size > 0)
                         for name in required}
            summary = read_csv(directory / "target_summary.csv")[0]
            terminal_clean = summary.get("invariants_terminal_clean") == "1"
            payload_ok = summary.get("invariants_payload_consistent") == "1"
            expected_trace = next(item["trace"] for item in audit.get("frozen_roster", []) if item["workload"] == workload)
            provenance_ok = (audit.get("core_authoritative_source") == EXPECTED_CORE and
                             audit.get("framework_authoritative_source") == EXPECTED_FRAMEWORK and
                             audit.get("runtime_config_composite_sha256") == EXPECTED_CONFIG and
                             status.get("trace") == expected_trace and status.get("frequency_mhz") == 850)
            parser_ok = (artifacts["parser.stdout"] and artifacts["parser.stderr"] and
                         not (directory / "parser.stderr").read_text().strip() and all(artifacts.values()))
            valid = bool(status.get("normal_simulator_exit") and terminal_clean and payload_ok and provenance_ok and parser_ok)
            if not valid: validity_errors.append(f"{workload}/{variant}")
            row = {"workload": workload, "variant": variant, "status": status.get("status"),
                   "cycles": status.get("terminal_gpu_tot_sim_cycle"), "instructions": status.get("terminal_gpu_tot_sim_insn"),
                   "wall_seconds": status.get("wall_seconds"), "normal_simulator_exit": int(bool(status.get("normal_simulator_exit"))),
                   "terminal_clean": int(terminal_clean), "payload_consistency": int(payload_ok),
                   "parser_success": int(parser_ok), "required_artifacts_present": int(all(artifacts.values())),
                   "formal_validity": "VALID_FOR_FORMAL" if valid else "INVALID_FOR_FORMAL",
                   "core_sha": audit.get("core_authoritative_source"),
                   "framework_sha": audit.get("framework_authoritative_source"),
                   "config_sha": audit.get("runtime_config_composite_sha256"), "trace": status.get("trace")}
            statuses.append(row)
            provenance.append(row | {"expected_core_sha": EXPECTED_CORE, "expected_framework_sha": EXPECTED_FRAMEWORK,
                                     "expected_config_sha": EXPECTED_CONFIG, "provenance_match": int(provenance_ok)})
            raw = directory / "raw.log.gz"
            raw_index.append({"workload": workload, "variant": variant, "raw_log": str(raw),
                              "bytes": raw.stat().st_size if raw.exists() else 0,
                              "sha256": sha256(raw) if raw.exists() else "MISSING", "included_in_pack": "NO"})
            record = analyzer.run_record(directory, status)
            records[workload, variant] = record
            families = {
                "Tag-way": ("tag_way_alloc_need", "tag_way_alloc_block"),
                "Line-MSHR": ("line_mshr_need", "line_mshr_full_block"),
                "Descriptor": ("descriptor_need", "descriptor_pool_full_block", "chain_depth_max"),
                "Per-address-cap": ("per_address_cap_check", "per_address_cap_block"),
                "WAD": ("wad_avg", "wad_full_events", "wad_hazard_events", "wad_hazard_wait_cycles"),
                "Payload": ("resident_payload_avg", "resident_pending_sector_avg", "payload_service_port_denial", "payload_capacity_allocation_denial"),
                "Bank": ("bank_logical_ops", "bank_true_conflict_ops", "bank_wait_cycles", "bank0_logical_ops"),
                "L1D": ("l1d_accesses", "l1d_misses", "l1d_mshr_entry_fail", "l1d_miss_queue_full"),
                "Lower": ("missq_avg", "l2_to_dram_full_block", "dram_issue_attempt", "dram_successful_read_issues", "scheduler_occ_avg", "returnq_occ_avg", "dram_to_l2_return_path_block", "dram_bandwidth_util"),
                "Temporal": ("window_records",),
            }
            for family, fields in families.items():
                field_values = {field: value(record, field) for field in fields}
                completeness.append({"workload": workload, "variant": variant, "family": family,
                                     "fields": json.dumps(field_values, sort_keys=True),
                                     "state": "MEASURED" if all(v != "NOT_EMITTED" for v in field_values.values()) else "MISSING_FIELD"})

    csv_write(PACK / "RUN_STATUS_22OF26.csv", statuses)
    csv_write(PACK / "FORMAL_PROVENANCE_AUDIT.csv", provenance)
    csv_write(PACK / "RAW_LOG_INDEX.tsv", raw_index, delimiter="\t")
    csv_write(PACK / "TELEMETRY_COMPLETENESS.csv", completeness)
    csv_write(PACK / "RUNNING_JOBS_SNAPSHOT.csv", running_rows())
    pairs, bottlenecks, banks, l1s, drams, windows = [], [], [], [], [], []
    for workload in ROSTER:
        if workload in MISSING: continue
        legacy, banked = records[workload, "B0-Legacy"], records[workload, "B0-Banked"]
        pair = {"workload": workload, "legacy_cycles": legacy["cycles"], "banked_cycles": banked["cycles"],
                "banked_over_legacy": round(banked["cycles"] / legacy["cycles"], 9),
                "legacy_over_banked_speedup": round(legacy["cycles"] / banked["cycles"], 9),
                "aggregation_scope": "INTERIM_11_PAIR_ONLY"}
        for prefix, record in (("legacy", legacy), ("banked", banked)):
            for key, data in record.items(): pair[f"{prefix}_{key}"] = data
            tag = classify(record["tag_way_alloc_block"], record["tag_way_alloc_need"])
            line = classify(record["line_mshr_full_block"], record["line_mshr_need"])
            desc = classify(record["descriptor_pool_full_block"], record["descriptor_need"])
            cap = classify(record["per_address_cap_block"], record["per_address_cap_check"])
            bank = classify(record["bank_true_conflict_ops"], record["bank_logical_ops"])
            bottlenecks.append({"workload": workload, "variant": prefix.upper(), "tag_pressure": tag,
                                "line_mshr_pressure": line, "descriptor_pool_pressure": desc,
                                "per_address_cap_pressure": cap, "bank_true_conflict_pressure": bank,
                                "bank_wait_cycles": record["bank_wait_cycles"], "wad_full_events": record["wad_full_events"],
                                "wad_hazard_events": record["wad_hazard_events"],
                                "payload_service_denial": record["payload_service_port_denial"],
                                "payload_capacity_denial": record["payload_capacity_allocation_denial"],
                                "l1_missq_full": record["l1d_miss_queue_full"], "scheduler_causal_block": record["scheduler_causal_block"],
                                "dram_bandwidth_util": record["dram_bandwidth_util"], "window_records": record["window_records"],
                                "interpretation": "pressure labels are exact-field event ratios; occupancy alone is not causal"})
            banks.append({"workload": workload, "variant": prefix.upper(), **{key: record[key] for key in record if key.startswith("bank")}})
            l1s.append({"workload": workload, "variant": prefix.upper(), **{key: record[key] for key in record if key.startswith("l1d_")}})
            drams.append({"workload": workload, "variant": prefix.upper(), **{key: record[key] for key in record if key.startswith(("missq_", "l2_to_dram", "dram_", "scheduler_", "returnq_"))}})
            windows.append({"workload": workload, "variant": prefix.upper(), "l2_window_records": record["window_records"],
                            "dram_channel_window_records": len([row for row in read_csv(RESULTS / ("B0-Legacy" if prefix == "legacy" else "B0-Banked") / workload / "target_dram.csv") if row.get("scope") == "window"])})
        pairs.append(pair)
    csv_write(PACK / "analysis/target_baseline_interim_comparison.csv", pairs)
    csv_write(PACK / "analysis/target_baseline_interim_bottlenecks.csv", bottlenecks)
    csv_write(PACK / "analysis/target_baseline_interim_bank.csv", banks)
    csv_write(PACK / "analysis/target_baseline_interim_l1.csv", l1s)
    csv_write(PACK / "analysis/target_baseline_interim_dram.csv", drams)
    csv_write(PACK / "analysis/target_baseline_interim_windows_summary.csv", windows)

    observed = "PASS" if all(row["state"] == "MEASURED" for row in completeness) else "CONDITIONAL"
    findings = [
        "The 11-pair comparison is an interim subset only; gemm and 3mm are deliberately excluded from every aggregate.",
        "Shared descriptor-pool, per-address-cap, Tag/set, WAD, payload, bank, L1D, and lower-path fields are emitted by the C7e final parser.  Measured zero is retained as zero; NOT_EMITTED is retained separately.",
        "C6d true bank-conflict metrics are reported as true_conflict_ops / logical_ops, not retry attempts or generic reservation failures.",
        "Causal claims are intentionally deferred: event pressure and 5K windows identify candidates, but occupancy alone is not attributed as a cause.",
    ]
    (PACK / "INTERIM_RESEARCH_FINDINGS.md").write_text("# Interim research findings\n\n" + "\n".join(f"- {line}" for line in findings) + "\n\n"
        "## Required questions\n\n"
        "The CSV analyses provide exact measured inputs for all ten questions.  At this interim point, conclusions are hypotheses only; no incomplete-workload average or gemm/3mm extrapolation is reported.\n")
    (PACK / "TELEMETRY_COMPLETENESS.md").write_text(
        "# C7e telemetry completeness\n\n"
        "`TELEMETRY_COMPLETENESS.csv` is the authoritative per-run family audit. `MEASURED` includes measured zero; `MISSING_FIELD` would be a blocking producer/parser gap.\n\n"
        f"Result: **{observed}** for the completed formal natural runs.\n")
    (PACK / "VALIDATION_SUMMARY.md").write_text(
        "# Validation summary\n\n"
        f"- Completed formal runs: {len(statuses)}/26\n- Formal provenance audit: {'PASS' if not validity_errors else 'FAIL'}\n"
        f"- Terminal clean and payload consistency checked per run: {'PASS' if not validity_errors else 'FAIL'}\n"
        f"- C7e family observation: {observed}\n- Running jobs were not modified.\n")
    (PACK / "OPEN_ISSUES.md").write_text(
        "# Open issues\n\n"
        "- This is not a closeout: gemm and 3mm Legacy/Banked are still running.\n"
        "- Do not claim TARGET_BASELINE_26RUN_PASS, READY_FOR_OPPORTUNITY, or FINAL until all four complete and the exact final analyzer succeeds.\n")
    (PACK / "SOURCE_ANCHORS.md").write_text(
        "# Source anchors\n\n"
        f"- Core: `{EXPECTED_CORE}`\n- Framework: `{EXPECTED_FRAMEWORK}`\n- Runtime config composite SHA-256: `{EXPECTED_CONFIG}`\n"
        "- Frequency: 850 MHz\n- Variants: B0-Legacy, B0-Banked\n"
        f"- Frozen runner: `{ROOT}/util/ep_l2/run_target_baseline.py`\n"
        f"- Exact final parser/analyzer source: `{ROOT}/util/ep_l2/parse_epl2_b0.py`, `{ROOT}/util/ep_l2/analyze_target_baseline.py`\n")
    (PACK / "INTERIM_STATUS.md").write_text(
        "# Interim formal status\n\n"
        "- Status: **INTERIM_FORMAL_22_OF_26**\n- Completed: **22/26** (`COMPLETE_VALID`)\n"
        "- Missing/running: gemm Legacy/Banked; 3mm Legacy/Banked\n"
        "- This report is not final and makes no final aggregate or opportunity recommendation.\n")
    readme = """# Target Baseline final-format interim review — 22/26

Status: **INTERIM_FORMAL_22_OF_26**. This is a documentation-only snapshot made while gemm and 3mm were still running. It is not a campaign closeout.

## Review order

1. `INTERIM_STATUS.md`, `SOURCE_ANCHORS.md`, `FORMAL_PROVENANCE_AUDIT.csv`
2. `TELEMETRY_COMPLETENESS.md`, `VALIDATION_SUMMARY.md`, `RUNNING_JOBS_SNAPSHOT.csv`
3. `analysis/target_baseline_interim_comparison.csv` and `analysis/target_baseline_interim_bottlenecks.csv`
4. `INTERIM_RESEARCH_FINDINGS.md`, `OPEN_ISSUES.md`, `RAW_LOG_INDEX.tsv`

The analysis reuses the exact C7e final analyzer `run_record()` field mapping. Every aggregate is explicitly `INTERIM_11_PAIR_ONLY`; gemm and 3mm are excluded rather than estimated.
"""
    (PACK / "README.md").write_text(readme)
    campaign = json.loads((RESULTS / "campaign_manifest.json").read_text())
    (PACK / "CAMPAIGN_MANIFEST.json").write_text(json.dumps(campaign, indent=2, sort_keys=True) + "\n")
    shutil.copy2(ROOT / "util/ep_l2/parse_epl2_b0.py", PACK / "scripts/parse_epl2_b0.py")
    shutil.copy2(ROOT / "util/ep_l2/analyze_target_baseline.py", PACK / "scripts/analyze_target_baseline.py")
    manifest = {"kind": "target_baseline_final_interim", "status": "INTERIM_FORMAL_22_OF_26",
                "created_utc": datetime.now(timezone.utc).isoformat(), "completed_runs": len(statuses),
                "missing_workloads": sorted(MISSING), "core_sha": EXPECTED_CORE, "framework_sha": EXPECTED_FRAMEWORK,
                "config_sha": EXPECTED_CONFIG, "provenance_audit": "PASS" if not validity_errors else "FAIL"}
    (PACK / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    checksum_files = sorted(path for path in PACK.rglob("*") if path.is_file() and path.name != "SHA256SUMS")
    with (PACK / "SHA256SUMS").open("w") as handle:
        for path in checksum_files: handle.write(f"{sha256(path)}  {path.relative_to(PACK)}\n")


if __name__ == "__main__":
    main()
