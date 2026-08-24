#!/usr/bin/env python3
"""Validate and summarize default-off C2P 4-SM locality observations."""

import argparse
import csv
import re
from pathlib import Path


CLASS = ("none", "local_only", "outer_only", "both")
BASE_FIELDS = (
    "gpu_tot_sim_cycle", "c2p_queries_accepted", "c2p_candidate_total",
    "c2p_candidate_queries", "c2p_peer_probes", "c2p_peer_probe_hits",
    "c2p_peer_probe_misses", "c2p_remote_hits", "c2p_l2_requests_avoided",
)
NUMBER_RE = re.compile(r"^\s*([A-Za-z0-9_]+) = ([0-9]+)$")


def read_values(path: Path):
    values = {}
    for line in path.read_text(errors="replace").splitlines():
        match = NUMBER_RE.match(line)
        if match:
            values[match.group(1)] = int(match.group(2))
    return values


def run_values(root: Path, case: str, variant: str):
    path = root / case / variant / "c2p" / "run.out"
    if not path.is_file():
        raise FileNotFoundError(path)
    return read_values(path), path


def value(values, key):
    if key not in values:
        raise KeyError(key)
    return values[key]


def ratio(numerator, denominator):
    return "" if denominator == 0 else f"{100 * numerator / denominator:.2f}%"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path,
                        help="root/<case>/{control,observe}/c2p/run.out")
    parser.add_argument("--case", required=True,
                        help="comma-separated case names")
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()

    cases = [case for case in args.case.split(",") if case]
    failures, rows = [], []
    for case in cases:
        try:
            control, control_path = run_values(args.root, case, "control")
            observe, observe_path = run_values(args.root, case, "observe")
        except (FileNotFoundError, KeyError) as error:
            failures.append(f"{case}: missing input ({error})")
            continue

        for key in BASE_FIELDS:
            if value(control, key) != value(observe, key):
                failures.append(
                    f"{case}: observation changed {key}: "
                    f"{value(control, key)} != {value(observe, key)}")

        if value(observe, "c2p_locality_observe") != 1:
            failures.append(f"{case}: observe replay did not enable locality")
        if value(control, "c2p_locality_observe") != 0:
            failures.append(f"{case}: control replay enabled locality")
        if value(observe, "c2p_locality_group_size") != 4:
            failures.append(f"{case}: expected 4-SM locality group")

        observed = value(observe, "c2p_locality_observed_queries")
        snapshot_sum = sum(value(observe, f"c2p_locality_snapshot_{item}")
                           for item in CLASS)
        accept_sum = sum(value(observe, f"c2p_locality_exact_accept_{item}")
                         for item in CLASS)
        query_sum = sum(value(observe, f"c2p_locality_exact_query_{item}")
                        for item in CLASS)
        if snapshot_sum != observed:
            failures.append(f"{case}: snapshot class sum {snapshot_sum} != {observed}")
        if accept_sum != observed:
            failures.append(f"{case}: accept exact class sum {accept_sum} != {observed}")
        if query_sum != observed:
            failures.append(f"{case}: query exact class sum {query_sum} != {observed}")
        if observed != value(observe, "c2p_candidate_queries"):
            failures.append(f"{case}: observed queries != candidate queries")

        candidate_local = value(observe, "c2p_locality_candidates_local")
        candidate_outer = value(observe, "c2p_locality_candidates_outer")
        if candidate_local + candidate_outer != value(observe, "c2p_candidate_total"):
            failures.append(f"{case}: locality candidates do not conserve")
        probes_local = value(observe, "c2p_locality_probes_local")
        probes_outer = value(observe, "c2p_locality_probes_outer")
        if probes_local + probes_outer != value(observe, "c2p_peer_probes"):
            failures.append(f"{case}: locality probes do not conserve")
        hits_local = value(observe, "c2p_locality_probe_hits_local")
        hits_outer = value(observe, "c2p_locality_probe_hits_outer")
        misses_local = value(observe, "c2p_locality_probe_misses_local")
        misses_outer = value(observe, "c2p_locality_probe_misses_outer")
        if hits_local + hits_outer != value(observe, "c2p_remote_hits"):
            failures.append(f"{case}: locality hits do not conserve")
        if misses_local + misses_outer != value(observe, "c2p_peer_probe_misses"):
            failures.append(f"{case}: locality misses do not conserve")
        if value(observe, "c2p_remote_hits") != value(observe, "c2p_l2_requests_avoided"):
            failures.append(f"{case}: remote-hit/L2-avoidance invariant failed")

        rows.append({
            "case": case,
            "cycles": value(observe, "gpu_tot_sim_cycle"),
            "queries": observed,
            "snapshot_local_only": value(observe, "c2p_locality_snapshot_local_only"),
            "snapshot_outer_only": value(observe, "c2p_locality_snapshot_outer_only"),
            "snapshot_both": value(observe, "c2p_locality_snapshot_both"),
            "exact_query_local_only": value(observe, "c2p_locality_exact_query_local_only"),
            "exact_query_outer_only": value(observe, "c2p_locality_exact_query_outer_only"),
            "exact_query_both": value(observe, "c2p_locality_exact_query_both"),
            "candidates_local": candidate_local,
            "candidates_outer": candidate_outer,
            "probes_local": probes_local,
            "probes_outer": probes_outer,
            "hits_local": hits_local,
            "hits_outer": hits_outer,
            "control_run": str(control_path.parent),
            "observe_run": str(observe_path.parent),
        })

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["case"]
    with args.csv.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    lines = ["# C2P 4-SM locality observation", "",
             "`local` means requester and target have the same `sid / 4` "
             "logical group.  This is a default-off observation experiment: "
             "the control and observed replays must have identical cycles and "
             "base C2P counters.", "",
             "| Case | Cycles | Queries | Snapshot local / outer / both | "
             "Exact-query local / outer / both | Candidate local share | "
             "Probe local share | Remote hit local share |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        candidates = row["candidates_local"] + row["candidates_outer"]
        probes = row["probes_local"] + row["probes_outer"]
        hits = row["hits_local"] + row["hits_outer"]
        lines.append(
            f"| {row['case']} | {row['cycles']} | {row['queries']} | "
            f"{row['snapshot_local_only']} / {row['snapshot_outer_only']} / "
            f"{row['snapshot_both']} | {row['exact_query_local_only']} / "
            f"{row['exact_query_outer_only']} / {row['exact_query_both']} | "
            f"{ratio(row['candidates_local'], candidates)} | "
            f"{ratio(row['probes_local'], probes)} | "
            f"{ratio(row['hits_local'], hits)} |")
    if failures:
        lines += ["", "## Validation failures", ""]
        lines += [f"- {failure}" for failure in failures]
    else:
        lines += ["", "All locality, probe, remote-hit, and default-off invariants passed."]
    args.markdown.write_text("\n".join(lines) + "\n")
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
