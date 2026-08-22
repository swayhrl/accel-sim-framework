#!/usr/bin/env python3
"""Summarize observation-only C2P transaction-attribution replays.

This deliberately consumes a diagnostic root only.  It neither reads nor
rewrites the strict paper16 analysis, so C2P+ investigation cannot leak into
the paper aggregate.
"""

import argparse
import csv
from pathlib import Path


COUNTERS = (
    "gpu_tot_sim_cycle", "gpu_sim_insn", "c2p_queries_accepted",
    "c2p_candidate_total", "c2p_candidate_queries", "c2p_peer_probes",
    "c2p_remote_hits", "c2p_l2_requests_avoided",
    "c2p_residence_encode_cycles", "c2p_residence_rows_cycles",
    "c2p_residence_match_cycles", "c2p_residence_ready_cycles",
    "c2p_residence_target_probe_cycles", "c2p_residence_probe_cycles",
    "c2p_residence_return_cycles", "c2p_residence_fallback_cycles",
    "c2p_remote_hit_probe_ordinal_total",
    "c2p_remote_hit_probe_ordinal_samples",
    "c2p_fallback_probe_ordinal_total",
    "c2p_fallback_probe_ordinal_samples",
    "c2p_fallback_no_candidate", "c2p_fallback_candidates_exhausted",
    "c2p_fallback_probe_timeout", "c2p_fallback_target_wait_timeout",
    "c2p_fallback_target_admission_timeout",
    "c2p_peer_lost_before_query", "c2p_peer_gained_before_query",
)


def read_summary(path):
    values = {}
    for line in path.read_text().splitlines():
        if " = " not in line:
            continue
        key, value = line.split(" = ", 1)
        if key in COUNTERS:
            values[key] = int(value)
    return values


def ratio(numerator, denominator):
    return "" if not denominator else f"{numerator / denominator:.4f}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()

    summaries = sorted(args.root.glob("**/c2p/summary.txt"))
    if not summaries:
        raise SystemExit(f"no C2P summaries below {args.root}")

    rows = []
    failures = []
    for path in summaries:
        values = read_summary(path)
        missing = [key for key in COUNTERS if key not in values]
        if missing:
            failures.append(f"{path}: missing {', '.join(missing)}")
            continue
        if values["c2p_remote_hits"] != values["c2p_l2_requests_avoided"]:
            failures.append(f"{path}: remote hits != L2 requests avoided")
        query_count = values["c2p_candidate_queries"]
        accepted = values["c2p_queries_accepted"]
        case_dir = path.parent.parent
        relative_case = case_dir.relative_to(args.root)
        row = {"case": case_dir.name,
               "scope": (str(relative_case.parent)
                         if str(relative_case.parent) != "." else "root")}
        row.update(values)
        row["candidates_per_query"] = ratio(
            values["c2p_candidate_total"], query_count)
        row["hit_probe_ordinal"] = ratio(
            values["c2p_remote_hit_probe_ordinal_total"],
            values["c2p_remote_hit_probe_ordinal_samples"])
        row["fallback_probe_ordinal"] = ratio(
            values["c2p_fallback_probe_ordinal_total"],
            values["c2p_fallback_probe_ordinal_samples"])
        for state in ("encode", "rows", "match", "ready", "target_probe",
                      "probe", "return", "fallback"):
            row[f"avg_{state}_cycles_per_accepted"] = ratio(
                values[f"c2p_residence_{state}_cycles"], accepted)
        row["peer_lost_rate"] = ratio(values["c2p_peer_lost_before_query"], accepted)
        row["peer_gained_rate"] = ratio(values["c2p_peer_gained_before_query"], accepted)
        rows.append(row)

    columns = ["scope", "case", *COUNTERS, "candidates_per_query",
               "hit_probe_ordinal", "fallback_probe_ordinal",
               "avg_encode_cycles_per_accepted",
               "avg_rows_cycles_per_accepted",
               "avg_match_cycles_per_accepted",
               "avg_ready_cycles_per_accepted",
               "avg_target_probe_cycles_per_accepted",
               "avg_probe_cycles_per_accepted",
               "avg_return_cycles_per_accepted",
               "avg_fallback_cycles_per_accepted", "peer_lost_rate",
               "peer_gained_rate"]
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    lines = ["# C2P Stage-A attribution summary", "",
             "This is an observation-only diagnostic artifact; it is excluded "
             "from the canonical paper16 aggregate.", "",
             "| Scope | Case | Candidates/query | Hit ordinal | Fallback ordinal | "
             "Target-FIFO cyc/accepted | Probe cyc/accepted | Fallback cyc/accepted | "
             "Lost peer rate | Target wait/admission timeout |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(
            f"| {row['scope']} | {row['case']} | {row['candidates_per_query']} | "
            f"{row['hit_probe_ordinal']} | {row['fallback_probe_ordinal']} | "
            f"{row['avg_target_probe_cycles_per_accepted']} | "
            f"{row['avg_probe_cycles_per_accepted']} | "
            f"{row['avg_fallback_cycles_per_accepted']} | {row['peer_lost_rate']} | "
            f"{row['c2p_fallback_target_wait_timeout']}/"
            f"{row['c2p_fallback_target_admission_timeout']} |")
    if failures:
        lines.extend(["", "## Validation failures", ""])
        lines.extend(f"- {item}" for item in failures)
    else:
        lines.extend(["", "All summarized runs preserve the remote-hit/L2-avoidance "
                      "conservation invariant."])
    args.markdown.write_text("\n".join(lines) + "\n")
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
