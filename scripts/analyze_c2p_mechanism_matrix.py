#!/usr/bin/env python3
"""Render an auditable C2P mechanism matrix for selected diagnostic cases.

This deliberately complements, rather than replaces, the strict paper16
analyzer.  It keeps the most useful per-transaction evidence for a small set
of workload roles (positive, stress, and negative control) in one CSV and one
short Markdown report before any 16-workload aggregate is interpreted.
"""

import argparse
import csv
import sys
from pathlib import Path


MODES = ("baseline", "oracle", "ideal", "c2p")
FIELDS = (
    "gpu_tot_sim_cycle", "l2_total_cache_accesses", "c2p_l1_misses",
    "c2p_oracle_peer_hits", "c2p_queries_accepted", "c2p_candidate_total",
    "c2p_candidate_queries", "c2p_peer_probes", "c2p_peer_probe_hits",
    "c2p_remote_hits", "c2p_l2_requests_avoided",
    "c2p_queries_queue_bypass", "c2p_fallback_no_candidate",
    "c2p_fallback_candidates_exhausted", "c2p_fallback_probe_timeout",
    "c2p_target_probe_port_busy_cycles", "c2p_target_probe_fifo_wait_cycles",
)


def read_summary(run_dir):
    path = run_dir / "summary.txt"
    if not path.is_file():
        return None
    values = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        key, sep, value = line.partition(" = ")
        if sep:
            values[key] = value.strip()
    return values


def read_provenance(run_dir):
    path = run_dir / "provenance.txt"
    values = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            key, sep, value = line.partition("=")
            if sep:
                values[key] = value.strip()
    return values


def locate(roots, case, mode):
    for root in roots:
        run_dir = root / case / mode
        data = read_summary(run_dir)
        if data is not None:
            return run_dir, data
    return None, None


def number(data, field):
    if data is None or field not in data:
        return None
    try:
        return int(data[field])
    except ValueError:
        return None


def ratio(numerator, denominator):
    if numerator is None or denominator in (None, 0):
        return ""
    return f"{numerator / denominator:.6f}"


def value(data, field):
    result = number(data, field)
    return "" if result is None else result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", required=True, type=Path)
    parser.add_argument("--supplemental-results-root", action="append", default=[],
                        type=Path)
    parser.add_argument("--l2-fast-root", required=True, type=Path)
    parser.add_argument("--supplemental-l2-fast-root", action="append", default=[],
                        type=Path)
    parser.add_argument("--target-normal-root", required=True, type=Path,
                        help="C2P diagnostic replay with target-port counters enabled")
    parser.add_argument("--target-bypass-root", required=True, type=Path)
    parser.add_argument("--cases", default="btree,sgemm,nn",
                        help="comma-separated workload case names")
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    cases = [case.strip() for case in args.cases.split(",") if case.strip()]
    if not cases:
        parser.error("--cases must contain at least one case")
    roots = [args.results_root, *args.supplemental_results_root]
    fast_roots = [args.l2_fast_root, *args.supplemental_l2_fast_root]
    rows = []
    failures = []

    for case in cases:
        runs = {mode: locate(roots, case, mode) for mode in MODES}
        fast_dir, fast = locate(fast_roots, case, "baseline")
        target_normal_dir, target_normal = locate([args.target_normal_root], case, "c2p")
        bypass_dir, bypass = locate([args.target_bypass_root], case, "c2p")
        for mode, (run_dir, _) in runs.items():
            if run_dir is None:
                failures.append(f"{case}/{mode}: missing summary")
        if fast_dir is None:
            failures.append(f"{case}: missing L2=50 baseline")
        if target_normal_dir is None:
            failures.append(f"{case}: missing target-port normal diagnostic")
        if bypass_dir is None:
            failures.append(f"{case}: missing target-port bypass diagnostic")
        if any(run_dir is None for run_dir, _ in runs.values()) or \
                fast_dir is None or target_normal_dir is None or bypass_dir is None:
            continue

        baseline_dir, baseline = runs["baseline"]
        oracle_dir, oracle = runs["oracle"]
        ideal_dir, ideal = runs["ideal"]
        c2p_dir, c2p = runs["c2p"]
        base_cycles = number(baseline, "gpu_tot_sim_cycle")
        base_l2 = number(baseline, "l2_total_cache_accesses")
        if number(oracle, "gpu_tot_sim_cycle") != base_cycles:
            failures.append(f"{case}: oracle changed baseline cycle count")
        for mode, data in (("ideal", ideal), ("c2p", c2p)):
            if number(data, "c2p_remote_hits") != \
                    number(data, "c2p_l2_requests_avoided"):
                failures.append(f"{case}/{mode}: remote-hit/L2-avoid invariant failed")
        # The normal target-port diagnostic intentionally differs only by
        # counters.  Verify its architectural result before borrowing its
        # port/FIFO statistics for the canonical C2P point.
        for field in ("gpu_tot_sim_cycle", "l2_total_cache_accesses",
                      "c2p_remote_hits", "c2p_l2_requests_avoided"):
            if number(target_normal, field) != number(c2p, field):
                failures.append(
                    f"{case}: target-port diagnostic differs from canonical C2P ({field})")

        row = {
            "case": case,
            "baseline_cycles": value(baseline, "gpu_tot_sim_cycle"),
            "l2_50_cycles": value(fast, "gpu_tot_sim_cycle"),
            "l2_sensitivity": ratio(base_cycles, number(fast, "gpu_tot_sim_cycle")),
            "oracle_cycles": value(oracle, "gpu_tot_sim_cycle"),
            "oracle_peer_hits": value(oracle, "c2p_oracle_peer_hits"),
            "oracle_redundancy": ratio(number(oracle, "c2p_oracle_peer_hits"),
                                        number(oracle, "c2p_l1_misses")),
            "ideal_cycles": value(ideal, "gpu_tot_sim_cycle"),
            "ideal_remote_hits": value(ideal, "c2p_remote_hits"),
            "c2p_cycles": value(c2p, "gpu_tot_sim_cycle"),
            "c2p_ipc_normalized": ratio(base_cycles, number(c2p, "gpu_tot_sim_cycle")),
            "c2p_l2_normalized": ratio(number(c2p, "l2_total_cache_accesses"), base_l2),
            "c2p_remote_hits": value(c2p, "c2p_remote_hits"),
            "c2p_queries": value(c2p, "c2p_queries_accepted"),
            "c2p_candidates_per_query": ratio(number(c2p, "c2p_candidate_total"),
                                                number(c2p, "c2p_candidate_queries")),
            "c2p_peer_probes": value(c2p, "c2p_peer_probes"),
            "c2p_peer_probe_hits": value(c2p, "c2p_peer_probe_hits"),
            "c2p_queue_bypass": value(c2p, "c2p_queries_queue_bypass"),
            "c2p_no_candidate": value(c2p, "c2p_fallback_no_candidate"),
            "c2p_exhausted": value(c2p, "c2p_fallback_candidates_exhausted"),
            "c2p_timeout": value(c2p, "c2p_fallback_probe_timeout"),
            "c2p_target_busy_cycles": value(target_normal, "c2p_target_probe_port_busy_cycles"),
            "c2p_fifo_wait_cycles": value(target_normal, "c2p_target_probe_queue_wait_cycles"),
            "target_bypass_cycles": value(bypass, "gpu_tot_sim_cycle"),
            "target_bypass_ipc_normalized": ratio(
                base_cycles, number(bypass, "gpu_tot_sim_cycle")),
            "target_port_cycles_saved": "" if number(c2p, "gpu_tot_sim_cycle") is None or
                number(bypass, "gpu_tot_sim_cycle") is None else
                number(c2p, "gpu_tot_sim_cycle") - number(bypass, "gpu_tot_sim_cycle"),
            "baseline_run": str(baseline_dir),
            "c2p_run": str(c2p_dir),
            "target_normal_run": str(target_normal_dir),
            "bypass_run": str(bypass_dir),
            "c2p_gpgpusim_commit": read_provenance(c2p_dir).get("gpgpusim_commit", ""),
        }
        rows.append(row)

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0]) if rows else ["case"]
    with args.csv.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    report = ["# C2P mechanism validation matrix", "",
              "This is a diagnostic evidence matrix, not a paper16 aggregate.",
              "It checks that the observational oracle keeps baseline timing and that",
              "every realized remote return replaces exactly one lower-L2 request.", ""]
    if rows:
        report.extend(["| case | C2P IPC | C2P L2/base | remote hit | candidates/query | timeout | target busy | FIFO wait | bypass IPC |",
                       "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"])
        for row in rows:
            report.append("| {case} | {c2p_ipc_normalized} | {c2p_l2_normalized} | "
                          "{c2p_remote_hits} | {c2p_candidates_per_query} | {c2p_timeout} | "
                          "{c2p_target_busy_cycles} | {c2p_fifo_wait_cycles} | "
                          "{target_bypass_ipc_normalized} |".format(**row))
    if failures:
        report.extend(["", "## Missing or failed evidence", ""])
        report.extend(f"- {failure}" for failure in failures)
    else:
        report.extend(["", "All requested mechanism invariants passed."])
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(report) + "\n", encoding="utf-8")
    if failures and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
