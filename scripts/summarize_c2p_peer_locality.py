#!/usr/bin/env python3
"""Aggregate qualified C2P peer-locality diagnostic stages.

This deliberately consumes only the CSV and invariant report emitted by
``analyze_c2p_peer_locality.py``.  It refuses partial or failed stages so a
geometry comparison cannot accidentally mix an audited result with a live run.
"""
import argparse
import csv
import sys
from pathlib import Path

STAGES = ("current64", "literal16k", "fourset64k")
GEOMETRY_CASES = ("hotspot1", "gaussian", "lud", "sgemm", "3mm", "gemm")
CASE_TO_PAPER_ABBR = {
    "mri-q": "MR", "nn": "NN", "dwt2d": "DW", "cutcp": "CU",
    "hotspot1": "HO", "gaussian": "GA", "atax": "AT", "bicg": "BI",
    "gesummv": "GS", "lud": "LU", "sgemm": "SG", "3mm": "3M",
    "gemm": "GE", "btree": "B+", "2DConvolution": "2D", "stencil": "ST",
}
COUNT_FIELDS = (
    "accepted_l1_events", "detect_events", "detect_lower_events",
    "detect_mshr_merge_events", "issue_events", "detect_sector_redundant",
    "issue_sector_redundant", "detect_line_redundant", "issue_line_redundant",
    "detect_0_issue_0", "detect_0_issue_1", "detect_1_issue_0",
    "detect_1_issue_1", "wait_cycles_total",
)


def load_stage(root, stage):
    audit = root / stage / "analysis" / "invariant_report.md"
    summary = root / stage / "analysis" / "diagnostic_summary.csv"
    if not audit.exists() or not summary.exists():
        raise RuntimeError("%s: missing completed audit" % stage)
    text = audit.read_text()
    if "- failed: 0" not in text or "| FAIL |" in text or "| MISSING |" in text:
        raise RuntimeError("%s: invariant audit is not a clean PASS" % stage)
    with summary.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise RuntimeError("%s: empty diagnostic summary" % stage)
    for row in rows:
        for field in COUNT_FIELDS:
            row[field] = int(row[field])
        row["issue_sector_redundant_ratio"] = float(
            row["issue_sector_redundant_ratio"])
        row["wait_cycles_mean"] = float(row["wait_cycles_mean"])
    return rows


def write_csv(path, fields, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def load_paper_reference(path):
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    reference = {row["abbr"]: row for row in rows}
    if len(reference) != 16 or set(reference) != set(CASE_TO_PAPER_ABBR.values()):
        raise RuntimeError("paper Figure 3 reference is incomplete")
    return reference


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True,
                        help="campaign root containing the three stage directories")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument(
        "--paper-ref", type=Path,
        default=Path(__file__).resolve().parents[1] / "docs" / "c2p-cache" /
        "paper_fig3_inferred" / "paper_fig3_inferred_points.csv",
        help="conditionally inferred paper Figure 3 reference CSV")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    stage_rows = {stage: load_stage(args.root, stage) for stage in STAGES}
    all_rows = []
    totals = []
    for stage, rows in stage_rows.items():
        total = {"stage": stage, "workloads": len(rows)}
        for field in COUNT_FIELDS:
            total[field] = sum(row[field] for row in rows)
        total["issue_sector_redundant_ratio"] = (
            float(total["issue_sector_redundant"]) / total["issue_events"])
        total["wait_cycles_mean"] = (
            float(total["wait_cycles_total"]) / total["issue_events"])
        totals.append(total)
        for row in rows:
            all_rows.append(dict(row, stage=stage))

    by_stage_case = {(r["stage"], r["case"]): r for r in all_rows}
    geometry_rows = []
    for case in GEOMETRY_CASES:
        base = by_stage_case[("current64", case)]
        row = {"case": case}
        for stage in STAGES:
            current = by_stage_case[(stage, case)]
            row[stage + "_ratio"] = current["issue_sector_redundant_ratio"]
            row[stage + "_issues"] = current["issue_events"]
        row["literal16k_minus_current64_pp"] = 100.0 * (
            row["literal16k_ratio"] - row["current64_ratio"])
        row["fourset64k_minus_current64_pp"] = 100.0 * (
            row["fourset64k_ratio"] - row["current64_ratio"])
        geometry_rows.append(row)

    paper_reference = load_paper_reference(args.paper_ref)
    paper_rows = []
    for row in sorted(by_stage_case.values(), key=lambda r: r["case"]):
        if row["stage"] != "current64":
            continue
        reference = paper_reference[CASE_TO_PAPER_ABBR[row["case"]]]
        paper_ratio = float(reference["paper_fig3_redundancy_ratio"])
        paper_rows.append({
            "case": row["case"],
            "abbr": reference["abbr"],
            "paper_group": reference["paper_group"],
            "paper_fig3_redundancy_ratio": paper_ratio,
            "paper_marker_source": reference["marker_source"],
            "paper_identity_confidence": reference["identity_confidence"],
            "current64_issue_sector_redundant_ratio":
                row["issue_sector_redundant_ratio"],
            "current64_minus_paper_pp": 100.0 * (
                row["issue_sector_redundant_ratio"] - paper_ratio),
        })

    stage_fields = ["stage", "workloads"] + list(COUNT_FIELDS) + [
        "issue_sector_redundant_ratio", "wait_cycles_mean"]
    write_csv(args.out_dir / "stage_totals.csv", stage_fields, totals)
    all_fields = ["stage", "label", "case"] + list(COUNT_FIELDS) + [
        "issue_sector_redundant_ratio", "wait_cycles_mean"]
    write_csv(args.out_dir / "all_workloads.csv", all_fields, all_rows)
    geometry_fields = ["case", "current64_ratio", "current64_issues",
                       "literal16k_ratio", "literal16k_issues",
                       "fourset64k_ratio", "fourset64k_issues",
                       "literal16k_minus_current64_pp",
                       "fourset64k_minus_current64_pp"]
    write_csv(args.out_dir / "geometry_comparison.csv", geometry_fields,
              geometry_rows)
    paper_fields = ["case", "abbr", "paper_group",
                    "paper_fig3_redundancy_ratio", "paper_marker_source",
                    "paper_identity_confidence",
                    "current64_issue_sector_redundant_ratio",
                    "current64_minus_paper_pp"]
    write_csv(args.out_dir / "current64_vs_paper_fig3_inferred.csv",
              paper_fields, paper_rows)
    print("wrote %s" % args.out_dir)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print("error: %s" % error, file=sys.stderr)
        sys.exit(2)
