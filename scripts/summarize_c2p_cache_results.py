#!/usr/bin/env python3
"""Validate and tabulate C2P core and optional comparator result bundles."""

import argparse
import csv
from pathlib import Path


FIELDS = (
    "gpu_tot_sim_cycle", "gpu_sim_insn", "l2_total_cache_accesses",
    "l2_global_read_accesses", "c2p_l1_misses",
    "c2p_oracle_peer_hits", "c2p_queries_accepted",
    "c2p_queries_queue_bypass", "c2p_updates_queue_bypass",
    "c2p_candidate_total", "c2p_candidate_queries", "c2p_peer_probes",
    "c2p_peer_l1_accesses",
    "c2p_remote_hits", "c2p_l2_requests_avoided",
    "c2p_fallback_no_candidate", "c2p_fallback_candidates_exhausted",
    "c2p_fallback_probe_timeout", "c2p_snapshot_false_positive",
    "c2p_snapshot_false_negative", "c2p_snapshot_true_positive",
    "c2p_snapshot_true_negative", "c2p_snapshot_query_false_positive",
    "c2p_snapshot_query_false_negative", "c2p_snapshot_query_true_positive",
    "c2p_snapshot_query_true_negative", "c2p_snapshot_updates",
    "c2p_snapshot_rebuilds", "c2p_snapshot_rebuild_transport_tags",
    "c2p_peer_access_hit_samples", "c2p_peer_access_hit_p90",
    "c2p_peer_access_hit_p95", "c2p_peer_access_hit_p99",
    "c2p_peer_access_hit_max", "c2p_peer_access_miss_samples",
    "c2p_peer_access_miss_p90", "c2p_peer_access_miss_p95",
    "c2p_peer_access_miss_p99", "c2p_peer_access_miss_max",
)
CORE_MODES = ("baseline", "oracle", "ideal", "c2p")
COMPARATOR_MODES = ("ata", "ccd", "ring")


def read_summary(path):
    data = {}
    for line in path.read_text().splitlines():
        if " = " in line:
            key, value = line.split(" = ", 1)
            data[key] = int(value)
    return data


def ratio(numerator, denominator):
    return "" if not denominator else f"{numerator / denominator:.4f}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    parser.add_argument("--strict", action="store_true",
                        help="fail if the root contains an incomplete case")
    args = parser.parse_args()

    rows = []
    failures = []
    cases = sorted(path for path in args.root.iterdir() if path.is_dir())
    for case in cases:
        results = {}
        for mode in CORE_MODES:
            summary = case / mode / "summary.txt"
            if not summary.is_file():
                failures.append(f"{case.name}: missing {mode}/summary.txt")
                continue
            results[mode] = read_summary(summary)
        if len(results) != len(CORE_MODES):
            continue
        comparator_present = [
            mode for mode in COMPARATOR_MODES
            if (case / mode / "summary.txt").is_file()
        ]
        if comparator_present:
            for mode in COMPARATOR_MODES:
                summary = case / mode / "summary.txt"
                if not summary.is_file():
                    failures.append(
                        f"{case.name}: incomplete comparator bundle, missing "
                        f"{mode}/summary.txt")
                    continue
                results[mode] = read_summary(summary)
        baseline = results["baseline"]
        oracle = results["oracle"]
        if baseline["gpu_tot_sim_cycle"] != oracle["gpu_tot_sim_cycle"]:
            failures.append(f"{case.name}: oracle changed baseline cycles")
        for mode in ("ideal", "c2p", *COMPARATOR_MODES):
            if mode not in results:
                continue
            result = results[mode]
            if result["c2p_remote_hits"] != result["c2p_l2_requests_avoided"]:
                failures.append(f"{case.name}/{mode}: remote hits != L2 avoided")
        for mode in (*CORE_MODES, *COMPARATOR_MODES):
            if mode not in results:
                continue
            result = results[mode]
            row = {"case": case.name, "mode": mode}
            row.update({field: result.get(field, 0) for field in FIELDS})
            row["oracle_rate"] = ratio(
                result.get("c2p_oracle_peer_hits", 0), result.get("c2p_l1_misses", 0))
            row["remote_hit_rate"] = ratio(
                result.get("c2p_remote_hits", 0), result.get("c2p_l1_misses", 0))
            row["candidates_per_query"] = ratio(
                result.get("c2p_candidate_total", 0),
                result.get("c2p_candidate_queries", 0))
            row["speedup_vs_baseline"] = ratio(
                baseline["gpu_tot_sim_cycle"] - result["gpu_tot_sim_cycle"],
                baseline["gpu_tot_sim_cycle"])
            rows.append(row)

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    columns = ["case", "mode", *FIELDS, "oracle_rate", "remote_hit_rate",
               "candidates_per_query", "speedup_vs_baseline"]
    with args.csv.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    lines = ["# C2P result summary", "",
             "| Case | Mode | Cycles | Oracle rate | Remote-hit rate | Candidates/query | Speedup vs baseline |",
             "|---|---|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(
            f"| {row['case']} | {row['mode']} | {row['gpu_tot_sim_cycle']} | "
            f"{row['oracle_rate']} | {row['remote_hit_rate']} | "
            f"{row['candidates_per_query']} | {row['speedup_vs_baseline']} |")
    if failures:
        lines.extend(["", "## Validation failures", ""])
        lines.extend(f"- {failure}" for failure in failures)
    else:
        lines.extend(["", "All completed four-mode bundles passed the oracle and ownership invariants."])
    args.markdown.write_text("\n".join(lines) + "\n")
    if failures and args.strict:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
