#!/usr/bin/env python3
"""Synthetic regression for the fail-closed FAST64.4 matrix collector."""
from __future__ import annotations

import csv
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "util/dtc_l1/collect_fast64_4_primary_matrix_v1.py"
ROSTER = ("ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree", "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q")
CONFIG = {
    "BASE": ("FAST64_BASE_A1", "1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde", "PAPER_BASE"),
    "IO": ("FAST64_IO_A1", "d4a2d9d0088946b950370b922a8d8e34422bbca9bac26f109b3977fe02a7f621", "PAPER_IO"),
    "OO": ("FAST64_OO_A1", "546c68f96d47f4650703ccfbc925bd789f923501d5607a77e79ca4845f234caa", "PAPER_OO"),
}


def record(workload: str, mode: str) -> dict:
    config_id, config_sha, dtc_mode = CONFIG[mode]
    metrics = {"DTC_L1_mode": dtc_mode, "gpu_tot_sim_cycle": {"BASE": 300, "IO": 200, "OO": 150}[mode], "gpu_tot_sim_insn": 999, "DTC_L1_lower_outstanding": 0, "DTC_L1_lower_cap_full_events": 0}
    if mode == "BASE":
        metrics.update(DTC_L1_pib_admits=4, DTC_L1_pib_retires=4, DTC_L1_pib_occupancy=0, DTC_L1_lower_requests_acquired=5, DTC_L1_lower_requests_released=5)
    elif mode == "IO":
        metrics.update(DTC_L1_io_lower_created=5, DTC_L1_io_lower_issued=5, DTC_L1_io_lower_responses=5, DTC_L1_io_completion_dependency_count=6, DTC_L1_io_completion_dependency_closed=6, DTC_L1_lower_credit_acquired=5, DTC_L1_lower_credit_released=5, DTC_L1_io_inflight_current=0, DTC_L1_io_pib_occupancy=0)
    else:
        metrics.update(DTC_L1_oo_lower_created=5, DTC_L1_oo_lower_issued=5, DTC_L1_oo_lower_responses=5, DTC_L1_oo_completion_dependency_count=6, DTC_L1_oo_completion_dependency_closed=6, DTC_L1_lower_credit_acquired=5, DTC_L1_lower_credit_released=5, DTC_L1_oo_inflight_current=0, DTC_L1_oo_pib_occupancy=0, DTC_L1_oo_active_refs=0)
    return {"schema": "dtc_l1_summary_v1", "provenance": {"workload_id": workload, "workload_sha256": f"payload-{workload}", "config_id": config_id, "config_sha256": config_sha, "core_sha": "core", "runtime_binary_sha256": "runtime", "observer_overlay_sha256": "observer", "framework_sha": "framework", "source_log": f"/raw/{workload}/{mode}"}, "metrics": metrics, "immutable_attempt": {"attempt_uuid": "uuid", "runner_sha256": "runner", "start_receipt_sha256": "start", "terminal_receipt_sha256": "terminal"}, "external_artifacts": {"trace_list_sha256": f"trace-{workload}", "run_dir": f"/raw/{workload}/{mode}", "simulator_stdout_sha256": "stdout", "simulator_stderr_sha256": "stderr"}}


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="fast64-primary-matrix-v1-") as tmp:
        root = Path(tmp); evidence = root / "evidence"; evidence.mkdir(); registry = root / "registry.tsv"
        rows = []
        for workload in ROSTER:
            for mode in CONFIG:
                path = evidence / f"{workload}-{mode}.json"; path.write_text(json.dumps(record(workload, mode)), encoding="utf-8")
                rows.append((workload, mode, str(path), "SYNTHETIC_TEST", "ZERO", "NONE"))
        with registry.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, delimiter="\t", lineterminator="\n"); writer.writerow(("workload", "mode", "summary", "origin", "cap_disposition", "retry_resolution")); writer.writerows(rows)
        output = root / "out"
        subprocess.run([str(TOOL), "--registry", str(registry), "--output-dir", str(output)], check=True)
        assert (output / "fast64_4_speedup.tsv").is_file()
        assert "GM-FAST12" in (output / "fast64_4_speedup.tsv").read_text(encoding="utf-8")
        bad = json.loads((evidence / "ATAX-IO.json").read_text()); bad["metrics"]["DTC_L1_io_lower_issued"] = 4; (evidence / "ATAX-IO.json").write_text(json.dumps(bad), encoding="utf-8")
        failed = subprocess.run([str(TOOL), "--registry", str(registry), "--output-dir", str(root / "bad")], text=True, capture_output=True)
        assert failed.returncode != 0 and "CONSERVATION" in failed.stderr
    print("FAST64_4_PRIMARY_MATRIX_V1_REGRESSION_PASS")


if __name__ == "__main__":
    main()
