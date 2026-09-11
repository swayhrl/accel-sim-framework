#!/usr/bin/env python3
"""Positive and identity-negative fixtures for the fail-closed Stage5 v2 path."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "util/dtc_l1/build_fast64_5_feature_tables_v2.py"
ROSTER = ("ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree", "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q")


def tsv(path: Path, fields: tuple[str, ...], records: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t")
        writer.writeheader(); writer.writerows(records)


def metrics(mode: str) -> dict:
    common = {"DTC_L1_mode": f"PAPER_{mode}", "gpu_tot_sim_cycle": 100 if mode == "BASE" else 80,
              "gpu_tot_sim_insn": 10, "DTC_L1_lower_outstanding": 0,
              "DTC_L1_lower_outstanding_peak": 2, "DTC_L1_lower_cap_full_events": 0,
              "L1D_total_cache_accesses": 1, "L1D_total_cache_misses": 1, "L2_total_cache_accesses": 1,
              "L2_total_cache_misses": 1, "L2_total_cache_reservation_fails": 0,
              "gpgpu_n_mem_read_global": 1, "gpgpu_n_mem_write_global": 1}
    if mode == "BASE": common.update(DTC_L1_lower_requests_acquired=1, DTC_L1_lower_requests_released=1)
    if mode == "IO": common.update(DTC_L1_io_lower_created=1, DTC_L1_io_lower_issued=1, DTC_L1_io_lower_responses=1, DTC_L1_io_completion_dependency_count=1, DTC_L1_io_completion_dependency_closed=1, DTC_L1_io_inflight_current=0, DTC_L1_io_pib_occupancy=0)
    if mode == "OO": common.update(DTC_L1_oo_lower_created=1, DTC_L1_oo_lower_issued=1, DTC_L1_oo_lower_responses=1, DTC_L1_oo_completion_dependency_count=1, DTC_L1_oo_completion_dependency_closed=1, DTC_L1_oo_inflight_current=0, DTC_L1_oo_pib_occupancy=0, DTC_L1_oo_active_refs=0)
    return common


with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory); matrix = directory / "fast64_4_primary_matrix.tsv"; structural = directory / "fast64_3_structural_pressure.tsv"; ledger = directory / "ledger.tsv"
    matrix_rows = []
    fields = ("workload", "mode", "evidence_path", "acceptance_status", "core_sha", "runtime_binary_sha256", "observer_overlay_sha256", "framework_sha", "payload_sha256")
    for workload in ROSTER:
        for mode in ("BASE", "IO", "OO"):
            evidence = directory / f"{workload}-{mode}.json"
            payload = f"payload-{workload}"
            evidence.write_text(json.dumps({"schema": "dtc_l1_summary_v1", "provenance": {"workload_id": workload, "core_sha": "core", "runtime_binary_sha256": "runtime", "observer_overlay_sha256": "observer", "framework_sha": "framework"}, "external_artifacts": {"trace_list_sha256": payload}, "metrics": metrics(mode)}), encoding="utf-8")
            matrix_rows.append(dict(zip(fields, (workload, mode, str(evidence), "STRICT_TERMINAL_ACCEPTED", "core", "runtime", "observer", "framework", payload))))
    tsv(matrix, fields, matrix_rows)
    tsv(structural, ("workload", "pib_full_events"), [{"workload": workload, "pib_full_events": 0} for workload in ROSTER])
    tsv(ledger, ("stage", "current_state"), [{"stage": "FAST64.4", "current_state": "PASS"}])
    command = [sys.executable, str(TOOL), "--stage-ledger", str(ledger), "--stage4-matrix", str(matrix), "--stage3-structural", str(structural), "--output-dir", str(directory / "out")]
    good = subprocess.run(command, text=True, capture_output=True); assert good.returncode == 0, good.stderr
    assert (directory / "out" / "fast64_5_emitted_column_provenance.tsv").is_file()
    matrix_rows[0]["acceptance_status"] = "PENDING"; tsv(matrix, fields, matrix_rows)
    bad = subprocess.run(command[:-1] + [str(directory / "bad")], text=True, capture_output=True)
    assert bad.returncode != 0 and "PRIMARY_ACCEPTANCE_REQUIRED" in bad.stderr
print("FAST64_5_FEATURE_TABLES_V2_REGRESSION_PASS")
