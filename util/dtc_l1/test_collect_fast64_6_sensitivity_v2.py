#!/usr/bin/env python3
"""Regression for accepted historical primary reuse in future-only v2."""
from __future__ import annotations

import csv
import json
import tempfile
from pathlib import Path

import collect_fast64_6_sensitivity_v2 as tool

FAST12 = ("ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree",
          "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q")

with tempfile.TemporaryDirectory() as name:
    root = Path(name); evidence = root / "bicg-io.json"
    record = {"schema":"dtc_l1_summary_v1", "provenance":{"workload_id":"BICG","config_id":"PRIMARY","config_sha256":"cfg","core_sha":"core","runtime_binary_sha256":"runtime","observer_overlay_sha256":"observer","framework_sha":"framework","result_classification":"PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE"}, "external_artifacts":{"trace_list_sha256":"trace"}, "immutable_attempt":{"attempt_uuid":"uuid","runner_sha256":"runner","start_receipt_sha256":"start","terminal_receipt_sha256":"terminal"}, "metrics":{"DTC_L1_mode":"PAPER_IO","gpu_tot_sim_cycle":1,"gpu_tot_sim_insn":1,"DTC_L1_lower_outstanding":0,"DTC_L1_lower_cap_full_events":0,"DTC_L1_io_lower_created":1,"DTC_L1_io_lower_issued":1,"DTC_L1_io_lower_responses":1,"DTC_L1_io_completion_dependency_count":1,"DTC_L1_io_completion_dependency_closed":1,"DTC_L1_lower_credit_acquired":1,"DTC_L1_lower_credit_released":1,"DTC_L1_io_inflight_current":0,"DTC_L1_io_pib_occupancy":0}}
    evidence.write_text(json.dumps(record), encoding="utf-8")
    primary = root / "primary.tsv"
    with primary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n"); writer.writerow(("workload","mode","evidence_path","acceptance_status"))
        for workload in FAST12:
            for mode in ("BASE","IO","OO"):
                writer.writerow((workload, mode, str(evidence) if (workload,mode)==("BICG","IO") else str(root/f"unused-{workload}-{mode}"), "STRICT_TERMINAL_ACCEPTED"))
    accepted = tool.primary_acceptance(primary)
    row = {"workload":"BICG","dimension":"logical","point":"16","mode":"IO","origin":"EXACT_FAST64_4_PRIMARY_REUSE","_path":str(evidence)}
    matrix = {"config_sha256":"cfg", "payload_sha256":"trace"}; meta = {"formal_core_sha":"core","formal_runtime_sha256":"runtime","observer_sha256":"observer","scientific_framework_sha":"framework"}
    tool.validate(row, matrix, meta, record, accepted)
    try:
        tool.validate(row, matrix, meta, record, set())
        raise AssertionError("unaccepted reuse unexpectedly passed")
    except RuntimeError as error:
        assert "PRIMARY_REUSE_ACCEPTANCE_MISSING" in str(error)
print("FAST64_6_SENSITIVITY_V2_REGRESSION_PASS")
