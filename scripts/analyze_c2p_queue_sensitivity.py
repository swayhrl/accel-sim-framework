#!/usr/bin/env python3
"""Audit requester/target queue headroom without mixing it into paper results."""

import argparse
import csv
from pathlib import Path


COUNTERS = (
    "gpu_tot_sim_cycle", "c2p_candidate_queries", "c2p_peer_probes",
    "c2p_remote_hits", "c2p_l2_requests_avoided",
    "c2p_queries_queue_bypass", "c2p_fallback_probe_timeout",
)
OPTIONS = (
    "-c2p_cache_query_queue_size", "-c2p_cache_target_probe_queue_size",
    "-c2p_cache_probe_timeout",
)


def read_summary(path):
    values = {}
    for line in path.read_text().splitlines():
        if " = " not in line:
            continue
        key, value = line.split(" = ", 1)
        try:
            values[key] = int(value)
        except ValueError:
            pass
    return values


def read_options(path):
    values = {}
    for line in path.read_text().splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[0] in OPTIONS:
            values[fields[0]] = int(fields[1])
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--default-run", required=True, type=Path,
                        help="canonical C2P run directory (for example btree/c2p)")
    parser.add_argument("--sensitivity-root", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    default = read_summary(args.default_run / "summary.txt")
    rows, missing, failures = [], [], []
    if "gpu_tot_sim_cycle" not in default:
        missing.append("default run lacks a summary")
    for point in sorted(path for path in args.sensitivity_root.iterdir()
                        if path.is_dir()):
        run_dir = point / "btree" / "c2p"
        summary_path = run_dir / "summary.txt"
        if not summary_path.is_file():
            missing.append(f"{point.name}: missing btree/c2p summary")
            continue
        data = read_summary(summary_path)
        options = read_options(run_dir / "gpgpusim.config")
        absent = [key for key in COUNTERS if key not in data]
        if absent:
            missing.append(f"{point.name}: missing {', '.join(absent)}")
            continue
        if data["c2p_remote_hits"] != data["c2p_l2_requests_avoided"]:
            failures.append(f"{point.name}: remote hits do not equal L2 avoids")
        rows.append({
            "point": point.name,
            "query_queue_size": options.get("-c2p_cache_query_queue_size", ""),
            "target_probe_queue_size": options.get("-c2p_cache_target_probe_queue_size", ""),
            "probe_timeout": options.get("-c2p_cache_probe_timeout", ""),
            **{key: data[key] for key in COUNTERS},
            "cycle_ratio_to_default": (
                data["gpu_tot_sim_cycle"] / default["gpu_tot_sim_cycle"]
                if default.get("gpu_tot_sim_cycle") else ""),
            "remote_hit_ratio_to_default": (
                data["c2p_remote_hits"] / default["c2p_remote_hits"]
                if default.get("c2p_remote_hits") else ""),
        })

    fields = ["point", "query_queue_size", "target_probe_queue_size",
              "probe_timeout", *COUNTERS, "cycle_ratio_to_default",
              "remote_hit_ratio_to_default"]
    with (args.out_dir / "queue_sensitivity.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    report = ["# C2P queue sensitivity status", "",
              "This diagnostic is separate from the paper table: it changes only "
              "finite queue/timeout assumptions to quantify their effect.", ""]
    if missing:
        report.extend(["## Missing evidence", "", *[f"- {item}" for item in missing]])
    if failures:
        report.extend(["", "## Invariant failures", "", *[f"- {item}" for item in failures]])
    if not missing and not failures:
        report.append("All requested diagnostic points completed with remote-hit/L2-avoid invariants intact.")
    (args.out_dir / "queue_sensitivity_status.md").write_text("\n".join(report) + "\n")
    if args.strict and (missing or failures):
        raise SystemExit("; ".join(missing + failures))


if __name__ == "__main__":
    main()
