#!/usr/bin/env python3
"""Fail-closed compact aggregation for the 12-row FAST64.3 Base matrix."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "docs/dtc_l1/fast64/generated"
CORE = "bbcbb5e7565417102087bc80b14c349b4e568c05"
FRAMEWORK = "037f008b330eb230353b60edf126d6be9f45afdc"
RUNTIME = "6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041"
OBSERVER = "2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e"
CONFIG_SHA = "1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde"


def dynamic(workload: str) -> tuple[Path, Path]:
    row = f"fast64_3_{workload}_base_cap8192_a1_v2"
    stem = workload.upper().replace("-", "_")
    root = GENERATED / "fast64_3_dynamic_base_v1"
    return root / f"{row}.json", root / f"FAST64_3_{stem}_BASE_STRUCTURAL_METRICS_V1.json"


ROWS = (
    ("ATAX", GENERATED / "fast64_3_atax_base_alias_v3/fast64_3_precomputed_atax_base_cap8192_a1_r2.json", GENERATED / "fast64_3_atax_base_alias_v3/FAST64_3_ATAX_BASE_STRUCTURAL_METRICS_V1.json"),
    ("BICG", GENERATED / "qualification_r2_full_wave_alias_v2/fast64_1r2_bicg_base_cap8192_a1.json", GENERATED / "fast64_3_bicg_base_structural_v1/FAST64_3_BICG_BASE_STRUCTURAL_METRICS_V1.json"),
    ("GESUMMV", GENERATED / "fast64_3_gesummv_base_alias_v3/fast64_3_precomputed_gesummv_base_cap8192_a1_r2.json", GENERATED / "fast64_3_gesummv_base_alias_v3/FAST64_3_GESUMMV_BASE_STRUCTURAL_METRICS_V1.json"),
    ("GEMM", GENERATED / "fast64_3_gemm_base_alias_v4/fast64_3_precomputed_gemm_base_cap8192_a1_r2.json", GENERATED / "fast64_3_gemm_base_alias_v4/FAST64_3_GEMM_BASE_STRUCTURAL_METRICS_V1.json"),
    ("2DConvolution", *dynamic("2DConvolution")),
    ("Btree", *dynamic("Btree")),
    ("DWT2D", GENERATED / "fast64_3_dwt2d_base_alias_v3/fast64_3_precomputed_dwt2d_base_cap8192_a1_r2.json", GENERATED / "fast64_3_dwt2d_base_alias_v3/FAST64_3_DWT2D_BASE_STRUCTURAL_METRICS_V1.json"),
    ("Gaussian", *dynamic("Gaussian")),
    ("Hotspot1", *dynamic("Hotspot1")),
    ("LUD", *dynamic("LUD")),
    ("NN", *dynamic("NN")),
    ("MRI-Q", *dynamic("MRI-Q")),
)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_tsv(path: Path, headings: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(headings)
        writer.writerows(rows)


def require(record: dict, workload: str, summary: Path) -> tuple[dict, dict]:
    if record.get("schema") != "dtc_l1_summary_v1":
        raise RuntimeError(f"{workload}: unexpected summary schema")
    p = record.get("provenance", {})
    expected = {
        "core_sha": CORE, "framework_sha": FRAMEWORK,
        "observer_overlay_sha256": OBSERVER, "runtime_binary_sha256": RUNTIME,
        "config_sha256": CONFIG_SHA, "config_id": "FAST64_BASE_A1",
    }
    for key, value in expected.items():
        if p.get(key) != value:
            raise RuntimeError(f"{workload}: identity mismatch {key}")
    if p.get("workload_id", "").casefold() != workload.casefold():
        raise RuntimeError(f"{workload}: payload workload mismatch")
    m = record.get("metrics", {})
    needed = ("DTC_L1_mode", "DTC_L1_lower_outstanding_cap", "DTC_L1_lower_requests_acquired", "DTC_L1_lower_requests_released", "DTC_L1_lower_outstanding", "DTC_L1_pib_admits", "DTC_L1_pib_retires", "DTC_L1_pib_occupancy", "DTC_L1_lower_cap_full_events", "gpu_tot_sim_cycle", "gpu_tot_sim_insn")
    absent = [key for key in needed if key not in m]
    if absent:
        raise RuntimeError(f"{workload}: missing metrics {','.join(absent)}")
    if m["DTC_L1_mode"] != "PAPER_BASE" or m["DTC_L1_lower_outstanding_cap"] != 8192:
        raise RuntimeError(f"{workload}: Base mode/cap mismatch")
    if m["DTC_L1_lower_requests_acquired"] != m["DTC_L1_lower_requests_released"] or m["DTC_L1_pib_admits"] != m["DTC_L1_pib_retires"]:
        raise RuntimeError(f"{workload}: accounting mismatch")
    if m["DTC_L1_lower_outstanding"] != 0 or m["DTC_L1_pib_occupancy"] != 0 or m["DTC_L1_lower_cap_full_events"] != 0:
        raise RuntimeError(f"{workload}: terminal or cap condition failed")
    if m["gpu_tot_sim_cycle"] <= 0 or m["gpu_tot_sim_insn"] <= 0:
        raise RuntimeError(f"{workload}: nonpositive progress")
    if not summary.is_file():
        raise RuntimeError(f"{workload}: summary absent")
    return p, m


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=GENERATED)
    args = parser.parse_args()
    pending = [str(path) for _, summary, structural in ROWS for path in (summary, structural) if not path.is_file()]
    if pending:
        raise SystemExit("FAST64_3_BASE_MATRIX_V1_MISSING_INPUTS\n" + "\n".join(pending))
    accepted: list[tuple[str, Path, Path, dict, dict, dict]] = []
    for workload, summary, structural in ROWS:
        record = json.loads(summary.read_text(encoding="utf-8"))
        provenance, metrics = require(record, workload, summary)
        companion = json.loads(structural.read_text(encoding="utf-8"))
        cm = companion.get("metrics", {})
        required_structural = ("cacheline_all_lines_reserved_events", "tag_bank_conflicts", "mshr_entry_full_events", "mshr_merge_full_events", "miss_queue_downstream_full_events", "live_miss_lower_acquired", "live_miss_lower_released", "terminal_lower_outstanding", "terminal_pib_occupancy")
        if companion.get("schema") != "FAST64_3_BASE_STRUCTURAL_METRICS_V1" or any(key not in cm for key in required_structural):
            raise RuntimeError(f"{workload}: structural companion incomplete")
        if cm["live_miss_lower_acquired"] != metrics["DTC_L1_lower_requests_acquired"] or cm["live_miss_lower_released"] != metrics["DTC_L1_lower_requests_released"]:
            raise RuntimeError(f"{workload}: structural lower mismatch")
        accepted.append((workload, summary, structural, provenance, metrics, cm))
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    write_tsv(out / "fast64_3_base_rows.tsv", ["workload", "cycles", "instructions", "loads", "stores", "atomics", "l1_accesses", "l1_misses", "l2_accesses", "l2_misses", "accepted"], [[w, m["gpu_tot_sim_cycle"], m["gpu_tot_sim_insn"], m.get("DTC_L1_m4_dynamic_loads", "NA"), m.get("DTC_L1_m4_dynamic_stores", "NA"), m.get("DTC_L1_m4_dynamic_atomics", "NA"), m.get("L1D_total_cache_accesses", "NA"), m.get("L1D_total_cache_misses", "NA"), m.get("L2_total_cache_accesses", "NA"), m.get("L2_total_cache_misses", "NA"), "YES"] for w, _, _, _, m, _ in accepted])
    write_tsv(out / "fast64_3_structural_pressure.tsv", ["workload", "pib_full_events", "cacheline_all_lines_reserved_events", "tag_bank_conflicts", "mshr_entry_full_events", "mshr_merge_full_events", "miss_queue_downstream_full_events"], [[w, m.get("DTC_L1_pib_full_events", "NA"), c["cacheline_all_lines_reserved_events"], c["tag_bank_conflicts"], c["mshr_entry_full_events"], c["mshr_merge_full_events"], c["miss_queue_downstream_full_events"]] for w, _, _, _, m, c in accepted])
    write_tsv(out / "fast64_3_live_misses.tsv", ["workload", "lower_acquired", "lower_released", "lower_average", "lower_peak", "final_lower_outstanding", "lower_cap_full_events"], [[w, m["DTC_L1_lower_requests_acquired"], m["DTC_L1_lower_requests_released"], m.get("DTC_L1_lower_outstanding_average", "UNSUPPORTED"), m.get("DTC_L1_lower_outstanding_peak", "UNSUPPORTED"), m["DTC_L1_lower_outstanding"], m["DTC_L1_lower_cap_full_events"]] for w, _, _, _, m, _ in accepted])
    # The host table is written separately to retain exact external-run references.
    host_rows = []
    for workload, summary, _, _, _, _ in accepted:
        record = json.loads(summary.read_text(encoding="utf-8"))
        host = record.get("host", {}); external = record.get("external_artifacts", {})
        host_rows.append([workload, host.get("elapsed_wall", "NA"), host.get("user_seconds", "NA"), host.get("system_seconds", "NA"), host.get("max_rss_kb", "NA"), host.get("cycles_per_second", "UNSUPPORTED"), host.get("instructions_per_second", "UNSUPPORTED"), external.get("run_dir", "NA")])
    write_tsv(out / "fast64_3_host_runtime.tsv", ["workload", "elapsed_wall", "user_seconds", "system_seconds", "max_rss_kb", "cycles_per_host_second", "instructions_per_host_second", "raw_run_ref"], host_rows)
    write_tsv(out / "fast64_3_identity_manifest.tsv", ["workload", "accepted_row", "classification", "compact_evidence_path", "evidence_sha256", "config_sha256", "payload_sha256", "core_sha", "runtime_sha256", "observer_sha256", "scientific_framework_sha", "raw_run_ref"], [[w, summary.stem, p.get("result_classification", "PROMOTED_FAST64_3_BASE"), str(summary.relative_to(ROOT)), digest(summary), p["config_sha256"], p.get("workload_sha256", "NA"), p["core_sha"], p["runtime_binary_sha256"], p["observer_overlay_sha256"], p["framework_sha"], json.loads(summary.read_text(encoding="utf-8")).get("external_artifacts", {}).get("run_dir", "NA")] for w, summary, _, p, _, _ in accepted])
    print("FAST64_3_BASE_MATRIX_V1_PASS rows=" + str(len(accepted)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
