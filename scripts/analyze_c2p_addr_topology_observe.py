#!/usr/bin/env python3
"""Summarize read-only C2P+ address-region and requester-topology evidence."""

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path


CASES = ("bfs", "lps", "btree")
FIELDS = ("opportunities", "later_peer", "within_4", "lower_ready",
          "target_credit")
KEY_RE = re.compile(
    r"^c2p_addr_obs_(?:region_(?P<region>\d+)"
    r"(?:_cluster_(?P<region_cluster>\d+))?|cluster_(?P<cluster>\d+))"
    r"_bin_(?P<bin>\d+)_(?P<field>opportunities|later_peer|within_4|"
    r"lower_ready|target_credit)$")


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


def parse_key(key):
    match = KEY_RE.match(key)
    if not match:
        return None
    candidate_bin = int(match.group("bin"))
    if match.group("region") is None:
        return "cluster", "", int(match.group("cluster")), candidate_bin, match.group("field")
    if match.group("region_cluster") is None:
        return "region", int(match.group("region")), "", candidate_bin, match.group("field")
    return ("region_cluster", int(match.group("region")),
            int(match.group("region_cluster")), candidate_bin,
            match.group("field"))


def rate(numerator, denominator):
    return "" if not denominator else f"{100 * numerator / denominator:.3f}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()

    rows, failures = [], []
    for case in CASES:
        summary = args.root / case / "c2p" / "summary.txt"
        if not summary.is_file():
            failures.append(f"{case}: missing summary")
            continue
        grouped = defaultdict(dict)
        for key, value in read_summary(summary).items():
            parsed = parse_key(key)
            if parsed is None:
                continue
            domain, region, cluster, candidate_bin, field = parsed
            grouped[(domain, region, cluster, candidate_bin)][field] = value
        if not grouped:
            failures.append(f"{case}: no address/topology observation counters")
            continue
        for (domain, region, cluster, candidate_bin), values in grouped.items():
            missing = [field for field in FIELDS if field not in values]
            if missing:
                failures.append(f"{case}/{domain}: incomplete bucket counters")
                continue
            if values["within_4"] > values["later_peer"]:
                failures.append(f"{case}/{domain}: within-4 exceeds later-peer")
            if values["later_peer"] > values["opportunities"]:
                failures.append(f"{case}/{domain}: later-peer exceeds opportunities")
            rows.append({
                "case": case, "domain": domain, "region": region,
                "cluster": cluster, "candidate_bin": candidate_bin,
                **values,
                "later_peer_rate": rate(values["later_peer"], values["opportunities"]),
                "within_4_rate": rate(values["within_4"], values["opportunities"]),
                "lower_ready_rate": rate(values["lower_ready"], values["opportunities"]),
                "target_credit_rate": rate(values["target_credit"], values["opportunities"]),
            })

    rows.sort(key=lambda row: (row["case"], row["domain"],
                               row["candidate_bin"], row["region"], row["cluster"]))
    columns = ["case", "domain", "region", "cluster", "candidate_bin", *FIELDS,
               "later_peer_rate", "within_4_rate", "lower_ready_rate",
               "target_credit_rate"]
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    lines = ["# C2P+ address/topology observation", "",
             "All rows are read-only observations after the first failed peer probe. "
             "`within_4` is the exact counterfactual that a four-probe confirmation "
             "package could still find a peer. Bucket ranges omit buckets with fewer "
             "than 64 opportunities.", "",
             "| Case | Feature | Candidate bin | Opportunities | Eligible buckets | "
             "Later-peer rate | Eligible range | Within-4 rate | Lower-ready rate | "
             "Target-credit rate |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    domains = ("region", "cluster", "region_cluster")
    for case in CASES:
        for domain in domains:
            for candidate_bin in range(4):
                subset = [row for row in rows if row["case"] == case and
                          row["domain"] == domain and
                          row["candidate_bin"] == candidate_bin]
                if not subset:
                    continue
                total = sum(row["opportunities"] for row in subset)
                later = sum(row["later_peer"] for row in subset)
                within = sum(row["within_4"] for row in subset)
                lower = sum(row["lower_ready"] for row in subset)
                credit = sum(row["target_credit"] for row in subset)
                eligible = [row for row in subset if row["opportunities"] >= 64]
                if eligible:
                    values = [100 * row["later_peer"] / row["opportunities"]
                              for row in eligible]
                    spread = f"{min(values):.1f}–{max(values):.1f}%"
                else:
                    spread = ""
                lines.append(
                    f"| {case} | {domain} | {candidate_bin} | {total} | "
                    f"{len(eligible)} | {rate(later, total)}% | {spread} | "
                    f"{rate(within, total)}% | {rate(lower, total)}% | "
                    f"{rate(credit, total)}% |")
    if failures:
        lines += ["", "## Validation failures", ""]
        lines += [f"- {failure}" for failure in failures]
    else:
        lines += ["", "All emitted observation buckets satisfy counter conservation."]
    args.markdown.write_text("\n".join(lines) + "\n")
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
