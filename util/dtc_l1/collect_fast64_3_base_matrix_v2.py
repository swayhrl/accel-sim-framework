#!/usr/bin/env python3
"""Fail-closed FAST64.3 Base aggregation across explicit repair-map classes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "docs/dtc_l1/fast64/generated"
FRAMEWORK = "037f008b330eb230353b60edf126d6be9f45afdc"
OBSERVER = "2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e"
CONFIG = "1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde"
CLASSES = {"REUSABLE_SOURCE_INERT_BASE", "REPAIRED_CORE_FRESH"}
ROSTER = {"ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree", "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsv(path: Path, headings: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        out = csv.writer(stream, delimiter="\t", lineterminator="\n")
        out.writerow(headings)
        out.writerows(rows)


def load_registry(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    required = {"workload", "source_class", "summary", "structural", "core_sha", "runtime_sha256"}
    if not rows or any(set(row) != required for row in rows):
        raise RuntimeError("invalid source registry schema")
    names = {row["workload"] for row in rows}
    if names != ROSTER or len(rows) != len(ROSTER):
        raise RuntimeError("registry must contain every FAST12 Base workload exactly once")
    if any(row["source_class"] not in CLASSES for row in rows):
        raise RuntimeError("unrecognized source class")
    return rows


def validate(row: dict[str, str]) -> tuple[Path, Path, dict, dict, dict]:
    summary = GENERATED / row["summary"]
    structural = GENERATED / row["structural"]
    if not summary.is_file() or not structural.is_file():
        raise RuntimeError(f"{row['workload']}: missing compact inputs")
    record = json.loads(summary.read_text(encoding="utf-8"))
    p, m = record.get("provenance", {}), record.get("metrics", {})
    expected = {"core_sha": row["core_sha"], "runtime_binary_sha256": row["runtime_sha256"],
                "framework_sha": FRAMEWORK, "observer_overlay_sha256": OBSERVER,
                "config_sha256": CONFIG, "config_id": "FAST64_BASE_A1"}
    if record.get("schema") != "dtc_l1_summary_v1" or any(p.get(k) != v for k, v in expected.items()):
        raise RuntimeError(f"{row['workload']}: Base provenance mismatch")
    if p.get("workload_id", "").casefold() != row["workload"].casefold():
        raise RuntimeError(f"{row['workload']}: payload/workload mismatch")
    needed = ("DTC_L1_mode", "DTC_L1_lower_outstanding_cap", "DTC_L1_lower_requests_acquired",
              "DTC_L1_lower_requests_released", "DTC_L1_lower_outstanding", "DTC_L1_pib_admits",
              "DTC_L1_pib_retires", "DTC_L1_pib_occupancy", "DTC_L1_lower_cap_full_events",
              "gpu_tot_sim_cycle", "gpu_tot_sim_insn")
    if any(k not in m for k in needed) or m["DTC_L1_mode"] != "PAPER_BASE" or m["DTC_L1_lower_outstanding_cap"] != 8192:
        raise RuntimeError(f"{row['workload']}: missing/mismatched Base metrics")
    if m["DTC_L1_lower_requests_acquired"] != m["DTC_L1_lower_requests_released"] or m["DTC_L1_pib_admits"] != m["DTC_L1_pib_retires"] or m["DTC_L1_lower_outstanding"] != 0 or m["DTC_L1_pib_occupancy"] != 0 or m["DTC_L1_lower_cap_full_events"] != 0:
        raise RuntimeError(f"{row['workload']}: unresolved accounting, drain, or cap condition")
    companion = json.loads(structural.read_text(encoding="utf-8")); cm = companion.get("metrics", {})
    fields = ("cacheline_all_lines_reserved_events", "tag_bank_conflicts", "mshr_entry_full_events", "mshr_merge_full_events", "miss_queue_downstream_full_events", "live_miss_lower_acquired", "live_miss_lower_released", "terminal_lower_outstanding", "terminal_pib_occupancy")
    if companion.get("schema") != "FAST64_3_BASE_STRUCTURAL_METRICS_V1" or any(k not in cm for k in fields):
        raise RuntimeError(f"{row['workload']}: incomplete structural companion")
    if cm["live_miss_lower_acquired"] != m["DTC_L1_lower_requests_acquired"] or cm["live_miss_lower_released"] != m["DTC_L1_lower_requests_released"] or cm["terminal_lower_outstanding"] != 0 or cm["terminal_pib_occupancy"] != 0:
        raise RuntimeError(f"{row['workload']}: structural lifecycle mismatch")
    return summary, structural, p, m, cm


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registry", type=Path, default=GENERATED / "FAST64_3_BASE_SOURCE_REGISTRY_V2.tsv")
    ap.add_argument("--output-dir", type=Path, default=GENERATED)
    args = ap.parse_args()
    accepted = [(r, *validate(r)) for r in load_registry(args.registry)]
    out = args.output_dir; out.mkdir(parents=True, exist_ok=True)
    tsv(out / "fast64_3_base_rows.tsv", ["workload", "source_class", "cycles", "instructions", "accepted"], [[r["workload"], r["source_class"], m["gpu_tot_sim_cycle"], m["gpu_tot_sim_insn"], "YES"] for r, _, _, _, m, _ in accepted])
    tsv(out / "fast64_3_structural_pressure.tsv", ["workload", "pib_full_events", "cacheline_all_lines_reserved_events", "tag_bank_conflicts", "mshr_entry_full_events", "mshr_merge_full_events", "miss_queue_downstream_full_events"], [[r["workload"], m.get("DTC_L1_pib_full_events", "NA"), c["cacheline_all_lines_reserved_events"], c["tag_bank_conflicts"], c["mshr_entry_full_events"], c["mshr_merge_full_events"], c["miss_queue_downstream_full_events"]] for r, _, _, _, m, c in accepted])
    tsv(out / "fast64_3_live_misses.tsv", ["workload", "lower_acquired", "lower_released", "lower_average", "lower_peak", "final_lower_outstanding", "lower_cap_full_events"], [[r["workload"], m["DTC_L1_lower_requests_acquired"], m["DTC_L1_lower_requests_released"], m.get("DTC_L1_lower_outstanding_average", "UNSUPPORTED"), m.get("DTC_L1_lower_outstanding_peak", "UNSUPPORTED"), m["DTC_L1_lower_outstanding"], m["DTC_L1_lower_cap_full_events"]] for r, _, _, _, m, _ in accepted])
    tsv(out / "fast64_3_host_runtime.tsv", ["workload", "elapsed_wall", "user_seconds", "system_seconds", "max_rss_kb", "cycles_per_host_second", "instructions_per_host_second", "raw_run_ref"], [[r["workload"], json.loads(s.read_text())["host"].get("elapsed_wall", "NA"), json.loads(s.read_text())["host"].get("user_seconds", "NA"), json.loads(s.read_text())["host"].get("system_seconds", "NA"), json.loads(s.read_text())["host"].get("max_rss_kb", "NA"), json.loads(s.read_text())["host"].get("cycles_per_second", "UNSUPPORTED"), json.loads(s.read_text())["host"].get("instructions_per_second", "UNSUPPORTED"), json.loads(s.read_text()).get("external_artifacts", {}).get("run_dir", "NA")] for r, s, _, _, _, _ in accepted])
    tsv(out / "fast64_3_identity_manifest.tsv", ["workload", "source_class", "compact_evidence_path", "evidence_sha256", "config_sha256", "payload_sha256", "core_sha", "runtime_sha256", "observer_sha256", "scientific_framework_sha", "raw_run_ref"], [[r["workload"], r["source_class"], str(s.relative_to(ROOT)), digest(s), p["config_sha256"], p.get("workload_sha256", "NA"), p["core_sha"], p["runtime_binary_sha256"], p["observer_overlay_sha256"], p["framework_sha"], json.loads(s.read_text()).get("external_artifacts", {}).get("run_dir", "NA")] for r, s, _, p, _, _ in accepted])
    print("FAST64_3_BASE_MATRIX_V2_PASS rows=" + str(len(accepted)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
