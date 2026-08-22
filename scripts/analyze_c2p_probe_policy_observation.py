#!/usr/bin/env python3
"""Audit the observation-only evidence used to choose C2P+ probe policy.

This consumes only the isolated observation campaign.  It deliberately does
not choose a policy or alter paper16 aggregates: it reports whether an
ordinal-only signal is homogeneous enough to justify a small global predictor,
or whether the offline PC-hash study exposes material variation.
"""

import argparse
import csv
import math
import re
from pathlib import Path


MAX_ORDINAL = 4
ORDINAL_RE = re.compile(r"c2p_probe_ordinal_(\d+)_(hits|misses)")
PC_RE = re.compile(r"c2p_probe_pc_bucket_(\d+)_ordinal_(\d+)_(hits|misses)")
CONT_RE = re.compile(
    r"c2p_continuation_after_fail_(\d+)_lower_ready_([01])_target_credit_([01])"
)
BASE_FIELDS = (
    "gpu_tot_sim_cycle", "gpu_sim_insn", "c2p_queries_accepted",
    "c2p_candidate_total", "c2p_candidate_queries", "c2p_peer_probes",
    "c2p_peer_probe_hits", "c2p_peer_probe_misses", "c2p_remote_hits",
    "c2p_l2_requests_avoided",
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


def rate(hits, attempts):
    return "" if not attempts else f"{hits / attempts:.6f}"


def weighted_stddev(points):
    """Return weighted standard deviation of (rate, sample_count) points."""
    total = sum(weight for _, weight in points)
    if not total:
        return ""
    mean = sum(value * weight for value, weight in points) / total
    variance = sum(weight * (value - mean) ** 2 for value, weight in points) / total
    return f"{math.sqrt(variance):.6f}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--pc-csv", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()

    summaries = sorted(args.root.glob("**/c2p/summary.txt"))
    if not summaries:
        raise SystemExit(f"no C2P summaries under {args.root}")

    rows, pc_rows, failures = [], [], []
    for path in summaries:
        values = read_summary(path)
        if not all(field in values for field in BASE_FIELDS):
            continue
        ordinal = {(n, kind): values.get(f"c2p_probe_ordinal_{n}_{kind}", 0)
                   for n in range(1, MAX_ORDINAL + 1)
                   for kind in ("hits", "misses")}
        if not any(ordinal.values()) and values["c2p_peer_probes"]:
            # A legacy Stage-A run is not evidence for this particular study.
            continue
        case_dir = path.parent.parent
        case = case_dir.name
        rel = case_dir.relative_to(args.root)
        row = {"scope": str(rel.parent) if str(rel.parent) != "." else "root",
               "case": case, "run_dir": str(path.parent)}
        row.update({field: values[field] for field in BASE_FIELDS})
        ordinal_hits = ordinal_misses = 0
        for n in range(1, MAX_ORDINAL + 1):
            hits, misses = ordinal[n, "hits"], ordinal[n, "misses"]
            attempts = hits + misses
            ordinal_hits += hits
            ordinal_misses += misses
            row[f"ordinal_{n}_hits"] = hits
            row[f"ordinal_{n}_misses"] = misses
            row[f"ordinal_{n}_attempts"] = attempts
            row[f"ordinal_{n}_hit_rate"] = rate(hits, attempts)
        overflow_hits = values.get("c2p_probe_ordinal_overflow_hits", 0)
        overflow_misses = values.get("c2p_probe_ordinal_overflow_misses", 0)
        row["overflow_hits"] = overflow_hits
        row["overflow_misses"] = overflow_misses
        row["overflow_attempts"] = overflow_hits + overflow_misses
        row["overflow_hit_rate"] = rate(overflow_hits, overflow_hits + overflow_misses)
        ordinal_hits += overflow_hits
        ordinal_misses += overflow_misses
        if ordinal_hits != values["c2p_remote_hits"]:
            failures.append(f"{path}: ordinal hits {ordinal_hits} != remote hits "
                            f"{values['c2p_remote_hits']}")
        if ordinal_misses != values["c2p_peer_probe_misses"]:
            failures.append(f"{path}: ordinal misses {ordinal_misses} != peer probe misses "
                            f"{values['c2p_peer_probe_misses']}")

        continuation_total = 0
        for n in range(1, MAX_ORDINAL + 1):
            for lower_ready in range(2):
                for target_credit in range(2):
                    key = (f"c2p_continuation_after_fail_{n}_lower_ready_"
                           f"{lower_ready}_target_credit_{target_credit}")
                    count = values.get(key, 0)
                    row[f"after_fail_{n}_lr{lower_ready}_tc{target_credit}"] = count
                    continuation_total += count
        row["continuation_decisions"] = continuation_total

        pc_points = {n: [] for n in range(1, MAX_ORDINAL + 1)}
        pc_total_hits = pc_total_misses = 0
        for key, value in values.items():
            match = PC_RE.fullmatch(key)
            if not match:
                continue
            bucket, n, kind = int(match.group(1)), int(match.group(2)), match.group(3)
            if n > MAX_ORDINAL:
                continue
            peer = key.rsplit("_", 1)[0] + ("_misses" if kind == "hits" else "_hits")
            hits = value if kind == "hits" else values.get(peer, 0)
            misses = value if kind == "misses" else values.get(peer, 0)
            # Emit one row when reading the hit field to avoid duplicates.
            if kind != "hits":
                continue
            attempts = hits + misses
            if attempts:
                pc_points[n].append((hits / attempts, attempts))
            pc_total_hits += hits
            pc_total_misses += misses
            pc_rows.append({"scope": row["scope"], "case": case, "bucket": bucket,
                            "ordinal": n, "hits": hits, "misses": misses,
                            "attempts": attempts, "hit_rate": rate(hits, attempts)})
        if pc_total_hits != sum(ordinal[n, "hits"] for n in range(1, MAX_ORDINAL + 1)):
            failures.append(f"{path}: PC hash first-four hit total mismatch")
        if pc_total_misses != sum(ordinal[n, "misses"] for n in range(1, MAX_ORDINAL + 1)):
            failures.append(f"{path}: PC hash first-four miss total mismatch")
        for n in range(1, MAX_ORDINAL + 1):
            row[f"ordinal_{n}_pc_buckets"] = len(pc_points[n])
            row[f"ordinal_{n}_pc_hit_rate_stddev"] = weighted_stddev(pc_points[n])
        rows.append(row)

    columns = ["scope", "case", "run_dir", *BASE_FIELDS]
    for n in range(1, MAX_ORDINAL + 1):
        columns += [f"ordinal_{n}_hits", f"ordinal_{n}_misses",
                    f"ordinal_{n}_attempts", f"ordinal_{n}_hit_rate",
                    f"ordinal_{n}_pc_buckets", f"ordinal_{n}_pc_hit_rate_stddev"]
    columns += ["overflow_hits", "overflow_misses", "overflow_attempts",
                "overflow_hit_rate", "continuation_decisions"]
    for n in range(1, MAX_ORDINAL + 1):
        for lower_ready in range(2):
            for target_credit in range(2):
                columns.append(f"after_fail_{n}_lr{lower_ready}_tc{target_credit}")
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    with args.pc_csv.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=(
            "scope", "case", "bucket", "ordinal", "hits", "misses",
            "attempts", "hit_rate"))
        writer.writeheader()
        writer.writerows(pc_rows)

    lines = ["# C2P+ adaptive-policy observation", "",
             "Observation-only statistics; no result here is a policy result or "
             "eligible for the canonical paper16 aggregate.", "",
             "| Scope | Case | Ordinal-1 hit rate | Ordinal-2 hit rate | "
             "Ordinal-3 hit rate | Ordinal-4 hit rate | Overflow attempts | "
             "Continuation decisions |", 
             "|---|---|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(
            f"| {row['scope']} | {row['case']} | {row['ordinal_1_hit_rate']} | "
            f"{row['ordinal_2_hit_rate']} | {row['ordinal_3_hit_rate']} | "
            f"{row['ordinal_4_hit_rate']} | {row['overflow_attempts']} | "
            f"{row['continuation_decisions']} |")
    if failures:
        lines += ["", "## Validation failures", ""]
        lines += [f"- {failure}" for failure in failures]
    else:
        lines += ["", "All ordinal and PC-hash observation totals preserve their "
                  "corresponding C2P probe counters."]
    args.markdown.write_text("\n".join(lines) + "\n")
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
