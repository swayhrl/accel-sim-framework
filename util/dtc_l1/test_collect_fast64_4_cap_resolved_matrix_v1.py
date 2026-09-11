#!/usr/bin/env python3
"""Regression for explicit cap-inert reuse versus final-cap acquisition."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "util/dtc_l1/collect_fast64_4_cap_resolved_matrix_v1.py"
ROSTER = ("ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree", "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q")
MODES = {"BASE": "PAPER_BASE", "IO": "PAPER_IO", "OO": "PAPER_OO"}


def record(workload: str, mode: str, config_id: str, config_sha: str) -> dict:
    m = {"DTC_L1_mode": MODES[mode], "gpu_tot_sim_cycle": {"BASE": 300, "IO": 200, "OO": 150}[mode], "gpu_tot_sim_insn": 999, "DTC_L1_lower_outstanding": 0, "DTC_L1_lower_cap_full_events": 0}
    if mode == "BASE":
        m.update(DTC_L1_pib_admits=4, DTC_L1_pib_retires=4, DTC_L1_pib_occupancy=0, DTC_L1_lower_requests_acquired=5, DTC_L1_lower_requests_released=5)
    elif mode == "IO":
        m.update(DTC_L1_io_lower_created=5, DTC_L1_io_lower_issued=5, DTC_L1_io_lower_responses=5, DTC_L1_io_completion_dependency_count=6, DTC_L1_io_completion_dependency_closed=6, DTC_L1_lower_credit_acquired=5, DTC_L1_lower_credit_released=5, DTC_L1_io_inflight_current=0, DTC_L1_io_pib_occupancy=0)
    else:
        m.update(DTC_L1_oo_lower_created=5, DTC_L1_oo_lower_issued=5, DTC_L1_oo_lower_responses=5, DTC_L1_oo_completion_dependency_count=6, DTC_L1_oo_completion_dependency_closed=6, DTC_L1_lower_credit_acquired=5, DTC_L1_lower_credit_released=5, DTC_L1_oo_inflight_current=0, DTC_L1_oo_pib_occupancy=0, DTC_L1_oo_active_refs=0)
    return {"schema": "dtc_l1_summary_v1", "provenance": {"workload_id": workload, "workload_sha256": f"payload-{workload}", "config_id": config_id, "config_sha256": config_sha, "core_sha": "core", "runtime_binary_sha256": "runtime", "observer_overlay_sha256": "observer", "framework_sha": "framework", "source_log": f"/raw/{workload}/{mode}"}, "metrics": m, "immutable_attempt": {"attempt_uuid": "uuid", "runner_sha256": "runner", "start_receipt_sha256": "start", "terminal_receipt_sha256": "terminal"}, "external_artifacts": {"trace_list_sha256": f"trace-{workload}", "run_dir": f"/raw/{workload}/{mode}", "simulator_stdout_sha256": "stdout", "simulator_stderr_sha256": "stderr"}}


with tempfile.TemporaryDirectory(prefix="fast64-cap-resolved-") as tmp:
    root = Path(tmp); evidence = root / "evidence"; evidence.mkdir(); authority = root / "resolution.md"; authority.write_text("source-backed cap resolution\n", encoding="utf-8")
    auth_sha = hashlib.sha256(authority.read_bytes()).hexdigest(); registry, capmap = root / "registry.tsv", root / "cap.tsv"; rows, caps = [], []
    for workload in ROSTER:
        for mode in MODES:
            inert = workload == "ATAX" and mode == "IO"
            # Exercise reuse from an intermediate observed cap, not just the
            # historical 8192 candidate: this is the recovery case needed
            # when a later workload sets a larger common formal cap.
            source_cap = "16384" if inert else "32768"; config_id = f"FAST64_{mode}_CAP{source_cap}_A1"; config_sha = f"sha-{mode}-{source_cap}"
            path = evidence / f"{workload}-{mode}.json"; path.write_text(json.dumps(record(workload, mode, config_id, config_sha)), encoding="utf-8")
            rows.append((workload, mode, str(path), "SYNTHETIC", "ZERO", "SYNTHETIC"))
            caps.append((workload, mode, "32768", source_cap, "SOURCE_PROVEN_CAP_INERT_REUSE_TO_FINAL" if inert else "REACQUIRED_AT_FINAL_CAP", config_id, config_sha, str(authority.relative_to(ROOT)) if authority.is_relative_to(ROOT) else str(authority), auth_sha))
    with registry.open("w", encoding="utf-8", newline="") as out:
        w = csv.writer(out, delimiter="\t", lineterminator="\n"); w.writerow(("workload", "mode", "summary", "origin", "cap_disposition", "retry_resolution")); w.writerows(rows)
    # The tool resolves authorities below ROOT, so supply a repository-local temporary authority proxy.
    local = ROOT / "docs/dtc_l1/fast64/.cap_resolved_test_authority.tmp"; local.write_text(authority.read_text(encoding="utf-8"), encoding="utf-8")
    try:
        caps = [c[:-2] + ("docs/dtc_l1/fast64/.cap_resolved_test_authority.tmp", hashlib.sha256(local.read_bytes()).hexdigest()) for c in caps]
        with capmap.open("w", encoding="utf-8", newline="") as out:
            w = csv.writer(out, delimiter="\t", lineterminator="\n"); w.writerow(("workload", "mode", "formal_cap", "source_cap", "cap_identity_class", "expected_config_id", "expected_config_sha256", "resolution_authority", "resolution_authority_sha256")); w.writerows(caps)
        output = root / "out"; subprocess.run(["python3", str(TOOL), "--registry", str(registry), "--cap-resolution", str(capmap), "--output-dir", str(output)], check=True)
        assert (output / "fast64_4_cap_identity_manifest.tsv").is_file()
        bad = list(caps); first = list(bad[0]); first[4] = "UNDECLARED"; bad[0] = tuple(first)
        with capmap.open("w", encoding="utf-8", newline="") as out:
            w = csv.writer(out, delimiter="\t", lineterminator="\n"); w.writerow(("workload", "mode", "formal_cap", "source_cap", "cap_identity_class", "expected_config_id", "expected_config_sha256", "resolution_authority", "resolution_authority_sha256")); w.writerows(bad)
        failed = subprocess.run(["python3", str(TOOL), "--registry", str(registry), "--cap-resolution", str(capmap), "--output-dir", str(root / "bad")], text=True, capture_output=True)
        assert failed.returncode != 0 and "FINAL_CAP_REACQUISITION_CLASS_REQUIRED" in failed.stderr
    finally:
        local.unlink(missing_ok=True)

print("FAST64_4_CAP_RESOLVED_MATRIX_V1_REGRESSION_PASS")
