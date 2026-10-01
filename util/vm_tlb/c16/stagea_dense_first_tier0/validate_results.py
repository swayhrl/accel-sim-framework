#!/usr/bin/env python3
"""Validate exact result schema and frozen scientific/claim boundaries."""

import argparse
import csv
import json
from pathlib import Path


def rows(path):
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        return reader.fieldnames, list(reader)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--result-schema", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    schema = json.loads(args.result_schema.read_text())
    checks = {}
    counts = {}
    for name, rule in schema["row_rules"].items():
        path = args.review / name
        if name.endswith(".tsv"):
            fields, data = rows(path)
            checks[f"schema_{name}"] = fields == rule["columns"]
            counts[name] = len(data)
        elif name == "GPU_ACTIVE_BUDGET.json":
            data = json.loads(path.read_text())
            checks[f"schema_{name}"] = all(key in data for key in rule["required_keys"])
        elif name == "FINAL_DECISION.json":
            data = json.loads(path.read_text())
            checks[f"schema_{name}"] = all(key in data for key in rule["required_keys"])
    checks["point_identity_rows_7"] = counts["POINT_IDENTITY.tsv"] == 7
    checks["native_sample_rows_32"] = counts["NATIVE_REQUEST_SAMPLES.tsv"] == 32
    checks["native_summary_rows_8"] = counts["NATIVE_REQUEST_SUMMARY.tsv"] == 8
    checks["correctness_rows_12"] = counts["GRAPH_MODE_CORRECTNESS.tsv"] == 12
    checks["capture_rows_4"] = counts["NSYS_CAPTURE_INDEX.tsv"] == 4

    _, status_rows = rows(args.review / "POINT_EXECUTION_STATUS.tsv")
    status = {row["point_id"]: row for row in status_rows}
    checks["point_status_exact"] = ({point: row["status"] for point, row in status.items()}
                                    == {"MP01": "COMPLETE", "MP02": "PARTIAL", "MP03": "PARTIAL", "MP05": "COMPLETE"})
    checks["correctness_stop_exact"] = status["MP02"]["gpu_execution_status"] == "STOP_POINT_CORRECTNESS" and status["MP03"]["gpu_execution_status"] == "STOP_POINT_CORRECTNESS"
    checks["no_nsys_after_correctness_stop"] = status["MP02"]["nsys_status"] == "UNAVAILABLE" and status["MP03"]["nsys_status"] == "UNAVAILABLE"
    checks["successful_nsys_points"] = status["MP01"]["nsys_status"] == "PASS" and status["MP05"]["nsys_status"] == "PASS"

    budget = json.loads((args.review / "GPU_ACTIVE_BUDGET.json").read_text())
    lock = json.loads((args.review / "GPU_LOCK_RECEIPT.json").read_text())
    checks["budget_total_pass"] = budget["status"] == "PASS" and budget["total_used_seconds"] <= 540
    checks["point_caps_pass"] = all(budget["per_point_used_seconds"][point] <= budget["per_point_cap_seconds"][point] for point in budget["per_point_cap_seconds"])
    checks["lock_released"] = lock["released"] is True
    checks["no_cross_point_borrowing"] = budget["no_cross_point_borrowing"] is True

    final = json.loads((args.review / "FINAL_DECISION.json").read_text())
    checks["final_partial"] = final["status"] == "STAGEA_TIER0_PRODUCER_PARTIAL"
    checks["no_forbidden_execution"] = (final["holdout_executed"] is False and final["tier1_executed"] is False
                                         and final["ncunvbitsassaccelsim_executed"] is False)
    _, questions = rows(args.review / "QUESTION_GATE_STATUS.tsv")
    question = {row["question_id"]: row for row in questions}
    checks["matched_estimator_not_identifiable"] = question["DQ2"]["graph_control_gap_gate"] == "GRAPH_CONTROL_GAP_NOT_IDENTIFIABLE"
    checks["dq3_claim_bounded"] = question["DQ3"]["final_tier0_status"] in ("MEMORY_SERVICE_CANDIDATE", "NO_MEMORY_SERVICE_CANDIDATE")
    checks["deferred_rows_preserved"] = question["DQ4b"]["final_tier0_status"] == "DEFERRED_NOT_EXECUTION_READY" and question["translation"]["final_tier0_status"] == "UNKNOWN_INACTIVE"

    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "row_counts": counts}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
