#!/usr/bin/env python3
"""Synthetic regression for the fail-closed FAST64.6 collector."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "util/dtc_l1/collect_fast64_6_sensitivity_v1.py"
WORKLOADS = ("BICG", "GESUMMV", "Btree")
POINTS = {"logical": ("16", "32", "64"), "physical": ("16.5", "24", "32", "40", "48"), "pib": ("32", "64", "128", "192", "256")}


def record(workload: str, dimension: str, point: str, mode: str, config_sha: str) -> dict:
    metrics = {"DTC_L1_mode": f"PAPER_{mode}", "gpu_tot_sim_cycle": 100 + len(point), "gpu_tot_sim_insn": 999, "DTC_L1_lower_outstanding": 0, "DTC_L1_lower_cap_full_events": 0}
    if mode == "IO":
        metrics.update(DTC_L1_io_lower_created=5, DTC_L1_io_lower_issued=5, DTC_L1_io_lower_responses=5, DTC_L1_io_completion_dependency_count=6, DTC_L1_io_completion_dependency_closed=6, DTC_L1_lower_credit_acquired=5, DTC_L1_lower_credit_released=5, DTC_L1_io_inflight_current=0, DTC_L1_io_pib_occupancy=0)
    else:
        metrics.update(DTC_L1_oo_lower_created=5, DTC_L1_oo_lower_issued=5, DTC_L1_oo_lower_responses=5, DTC_L1_oo_completion_dependency_count=6, DTC_L1_oo_completion_dependency_closed=6, DTC_L1_lower_credit_acquired=5, DTC_L1_lower_credit_released=5, DTC_L1_oo_inflight_current=0, DTC_L1_oo_pib_occupancy=0, DTC_L1_oo_active_refs=0)
    stem = {"logical": f"LOGICAL_{point}KB", "physical": f"PHYSICAL_{'16p5' if point == '16.5' else point}KB", "pib": f"PIB_{point}ENTRIES"}[dimension]
    return {"schema": "dtc_l1_summary_v1", "provenance": {"workload_id": workload, "config_id": "PRIMARY_REUSE" if dimension == "logical" and point == "16" else f"FAST64_SENS_{stem}_{mode}", "config_sha256": config_sha, "core_sha": "core", "runtime_binary_sha256": "runtime", "observer_overlay_sha256": "observer", "framework_sha": "framework", "result_classification": "PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE"}, "metrics": metrics, "immutable_attempt": {"attempt_uuid": "uuid", "runner_sha256": "runner", "start_receipt_sha256": "start", "terminal_receipt_sha256": "terminal"}, "external_artifacts": {"trace_list_sha256": f"trace-{workload}", "run_dir": "/raw", "simulator_stdout_sha256": "stdout", "simulator_stderr_sha256": "stderr"}}


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="fast64-sensitivity-v1-") as name:
        tmp = Path(name); matrix, registry, evidence, out = tmp / "matrix.tsv", tmp / "registry.tsv", tmp / "evidence", tmp / "out"; evidence.mkdir()
        matrix_rows, registry_rows = [], []
        for workload in WORKLOADS:
            for dimension, points in POINTS.items():
                reference = {"logical": "logical_16_same_mode", "physical": "physical_32_IO", "pib": "pib_128_IO"}[dimension]
                for point in points:
                    for mode in ("IO", "OO"):
                        config_sha = hashlib.sha256(f"{dimension}/{point}/{mode}".encode()).hexdigest()
                        matrix_rows.append((workload, f"trace-{workload}", dimension, point, point, mode, "config", config_sha, reference, "IO" if dimension != "logical" else mode, "policy", "pending", "PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE"))
                        path = evidence / f"{workload}-{dimension}-{point}-{mode}.json"; path.write_text(json.dumps(record(workload, dimension, point, mode, config_sha)), encoding="utf-8")
                        registry_rows.append((workload, dimension, point, mode, str(path), "EXACT_FAST64_4_PRIMARY_REUSE" if dimension == "logical" and point == "16" else "STRICT_TERMINAL_SENSITIVITY"))
        matrix.write_text("\n".join(("schema\tFAST64_6_SENSITIVITY_MATRIX_V1", "scientific_framework_sha\tframework", "formal_core_sha\tcore", "formal_runtime_sha256\truntime", "observer_sha256\tobserver", "workload\tpayload_sha256\tdimension\tpoint\tmodeled_value\tmode\tconfig_path\tconfig_sha256\treference_point\treference_mode\tmode_policy\treuse_candidate\tclassification")) + "\n", encoding="utf-8")
        with matrix.open("a", encoding="utf-8", newline="") as f: csv.writer(f, delimiter="\t", lineterminator="\n").writerows(matrix_rows)
        with registry.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n"); w.writerow(("workload", "dimension", "point", "mode", "summary", "origin")); w.writerows(registry_rows)
        subprocess.run([str(TOOL), "--matrix", str(matrix), "--registry", str(registry), "--output-dir", str(out)], check=True)
        assert (out / "fast64_6_logical_plot.tsv").is_file() and len((out / "fast64_6_cells.tsv").read_text().splitlines()) == 79
        registry_rows.pop()
        bad = tmp / "bad.tsv"
        with bad.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n"); w.writerow(("workload", "dimension", "point", "mode", "summary", "origin")); w.writerows(registry_rows)
        failed = subprocess.run([str(TOOL), "--matrix", str(matrix), "--registry", str(bad), "--output-dir", str(tmp / "badout")], text=True, capture_output=True)
        assert failed.returncode != 0 and "EXACTLY_78" in failed.stderr
    print("FAST64_6_SENSITIVITY_V1_REGRESSION_PASS")


if __name__ == "__main__":
    main()
