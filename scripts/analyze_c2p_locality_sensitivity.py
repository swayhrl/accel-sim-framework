#!/usr/bin/env python3
"""Validate and summarize matched C2P near/outer latency sensitivity runs."""

import argparse
import csv
import re
from pathlib import Path


VARIANTS = ("uniform", "near_d0", "near_d2", "near_d4")
NUMBER_RE = re.compile(r"^\s*([A-Za-z0-9_]+) = ([0-9]+)$")


def read_values(path):
    values = {}
    for line in path.read_text(errors="replace").splitlines():
        match = NUMBER_RE.match(line)
        if match:
            values[match.group(1)] = int(match.group(2))
    return values


def get(values, key):
    if key not in values:
        raise KeyError(key)
    return values[key]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--case", required=True)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()

    failures, rows = [], []
    for case in filter(None, args.case.split(",")):
        values = {}
        for variant in VARIANTS:
            path = args.root / case / variant / "c2p" / "run.out"
            if not path.is_file():
                failures.append(f"{case}/{variant}: missing run.out")
                continue
            values[variant] = read_values(path)
        if len(values) != len(VARIANTS):
            continue
        for variant, item in values.items():
            try:
                if get(item, "c2p_locality_observe") != 1:
                    failures.append(f"{case}/{variant}: locality observation disabled")
                if get(item, "c2p_locality_group_size") != 4:
                    failures.append(f"{case}/{variant}: group size is not four")
                if get(item, "c2p_remote_hits") != get(item, "c2p_l2_requests_avoided"):
                    failures.append(f"{case}/{variant}: remote-hit/L2 invariant failed")
                if (get(item, "c2p_locality_probes_local") +
                        get(item, "c2p_locality_probes_outer") !=
                        get(item, "c2p_peer_probes")):
                    failures.append(f"{case}/{variant}: probe locality invariant failed")
            except KeyError as error:
                failures.append(f"{case}/{variant}: missing {error}")
        try:
            if get(values["uniform"], "c2p_locality_aware_candidate_order") != 0:
                failures.append(f"{case}/uniform: ordering must remain canonical")
            for variant, delta in (("near_d0", 0), ("near_d2", 2), ("near_d4", 4)):
                item = values[variant]
                if get(item, "c2p_locality_aware_candidate_order") != 1:
                    failures.append(f"{case}/{variant}: locality ordering disabled")
                if (get(item, "c2p_locality_outer_probe_extra_latency") != delta or
                        get(item, "c2p_locality_outer_return_extra_latency") != delta):
                    failures.append(f"{case}/{variant}: incorrect outer delay")
            row = {"case": case}
            for variant, item in values.items():
                row[f"{variant}_cycles"] = get(item, "gpu_tot_sim_cycle")
                row[f"{variant}_remote_hits"] = get(item, "c2p_remote_hits")
                row[f"{variant}_l2"] = get(item, "L2_total_cache_accesses")
                row[f"{variant}_probes"] = get(item, "c2p_peer_probes")
            rows.append(row)
        except KeyError as error:
            failures.append(f"{case}: missing {error}")

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["case"]
    with args.csv.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    lines = ["# C2P 4-SM near/outer latency sensitivity", "",
             "`uniform` is canonical ordering/timing with observation enabled. "
             "`near_d0` changes only candidate priority; `near_d2` and `near_d4` "
             "add the stated per-direction outer latency.  These are explicit "
             "model sensitivities, not a claim about measured GV100 wire delay.", "",
             "| Case | Uniform cycles | Near-d0 | Near-d2 | Near-d4 | "
             "Uniform remote hit | d0 / d2 / d4 remote hit |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(
            f"| {row['case']} | {row['uniform_cycles']} | "
            f"{row['near_d0_cycles']} | {row['near_d2_cycles']} | "
            f"{row['near_d4_cycles']} | {row['uniform_remote_hits']} | "
            f"{row['near_d0_remote_hits']} / {row['near_d2_remote_hits']} / "
            f"{row['near_d4_remote_hits']} |")
    if failures:
        lines += ["", "## Validation failures", ""]
        lines += [f"- {failure}" for failure in failures]
    else:
        lines += ["", "All locality configuration and remote-hit ownership invariants passed."]
    args.markdown.write_text("\n".join(lines) + "\n")
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
