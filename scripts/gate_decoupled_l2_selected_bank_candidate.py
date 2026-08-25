#!/usr/bin/env python3
"""Make the selected Decoupled-L2 bank candidate admission rule explicit.

The preceding optimization reports prove matched provenance and preserve raw
numbers.  This script decides whether those numbers are strong enough to
justify a broad campaign: a bank-pressure trace must show actual requeue
relief, the atomic trace must exercise atomic traffic, and none of the five
workloads used to select the candidate may regress beyond a small tolerance.
"""

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path


PRIMARY_CASES = ("bicg", "atax", "mvt", "syrk", "gesummv")
ATOMIC_RE = re.compile(r"decoupled_l2\[.*atomic=[1-9]")


def fail(message):
    raise RuntimeError(message)


def read_rows(path):
    with Path(path).open(newline="") as source:
        rows = list(csv.DictReader(source))
    if not rows:
        fail("empty optimization report: %s" % path)
    rows_by_case = {}
    for row in rows:
        case = row.get("case")
        if not case or case in rows_by_case:
            fail("missing or duplicate case in %s" % path)
        rows_by_case[case] = row
    return rows_by_case


def number(row, key):
    try:
        return float(row[key])
    except (KeyError, TypeError, ValueError) as error:
        raise RuntimeError("%s lacks numeric %s" % (row.get("case"), key)) from error


def atomic_exercised(path):
    text = Path(path).read_text(errors="replace")
    return bool(ATOMIC_RE.search(text))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-csv", required=True)
    parser.add_argument("--primary-csv", required=True)
    parser.add_argument("--atomic-default-log", required=True)
    parser.add_argument("--atomic-optimized-log", required=True)
    parser.add_argument("--min-speedup", type=float, default=0.995,
                        help="minimum optimized/default speedup for every case")
    parser.add_argument("--json", required=True)
    parser.add_argument("--markdown", required=True)
    args = parser.parse_args()
    if not 0 < args.min_speedup <= 1:
        fail("--min-speedup must be in (0, 1]")
    for path in (args.preflight_csv, args.primary_csv,
                 args.atomic_default_log, args.atomic_optimized_log):
        if not Path(path).is_file():
            fail("missing input: %s" % path)

    preflight = read_rows(args.preflight_csv)
    primary = read_rows(args.primary_csv)
    expected_preflight = {"l2_bw_32f", "atomic_add_lat"}
    if set(preflight) != expected_preflight:
        fail("preflight cases must be %s, got %s" %
             (sorted(expected_preflight), sorted(preflight)))
    if set(primary) != set(PRIMARY_CASES):
        fail("primary cases must be %s, got %s" %
             (list(PRIMARY_CASES), sorted(primary)))

    bandwidth = preflight["l2_bw_32f"]
    bw_default_requeues = (number(bandwidth, "default_tag_requeue") +
                           number(bandwidth, "default_lower_requeue"))
    bw_optimized_requeues = (number(bandwidth, "optimized_tag_requeue") +
                             number(bandwidth, "optimized_lower_requeue"))
    bandwidth_relief = bw_default_requeues > 0 and \
        bw_optimized_requeues < bw_default_requeues

    atomic_default = atomic_exercised(args.atomic_default_log)
    atomic_optimized = atomic_exercised(args.atomic_optimized_log)
    atomic_ok = atomic_default and atomic_optimized

    rows = [preflight["l2_bw_32f"], preflight["atomic_add_lat"]] + \
        [primary[name] for name in PRIMARY_CASES]
    regressions = [
        {"case": row["case"], "speedup": number(row, "speedup")}
        for row in rows if number(row, "speedup") < args.min_speedup
    ]
    primary_relief = [
        row["case"] for row in primary.values()
        if (number(row, "default_tag_requeue") + number(row, "default_lower_requeue")) >
           (number(row, "optimized_tag_requeue") + number(row, "optimized_lower_requeue"))
    ]
    admitted = bandwidth_relief and atomic_ok and not regressions
    result = {
        "admitted": admitted,
        "min_speedup": args.min_speedup,
        "bandwidth_default_requeues": bw_default_requeues,
        "bandwidth_optimized_requeues": bw_optimized_requeues,
        "bandwidth_relief": bandwidth_relief,
        "atomic_default_exercised": atomic_default,
        "atomic_optimized_exercised": atomic_optimized,
        "primary_cases_with_requeue_relief": sorted(primary_relief),
        "regressions": regressions,
    }
    Path(args.json).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with Path(args.markdown).open("w") as output:
        output.write("# Decoupled-L2 selected bank candidate admission\n\n")
        output.write("- Admission: `%s`\n" % ("pass" if admitted else "reject"))
        output.write("- Bandwidth requeues, default / optimized: %.0f / %.0f — %s\n" %
                     (bw_default_requeues, bw_optimized_requeues,
                      "relieved" if bandwidth_relief else "not relieved"))
        output.write("- Atomic exercised, default / optimized: %s / %s\n" %
                     (atomic_default, atomic_optimized))
        output.write("- Primary cases with lower total bank requeue: %s\n" %
                     (", ".join(sorted(primary_relief)) or "none"))
        output.write("- Per-case speedup floor: %.4fx\n" % args.min_speedup)
        if regressions:
            output.write("- Regressions beyond floor: %s\n" %
                         ", ".join("%s=%.4fx" % (row["case"], row["speedup"])
                                   for row in regressions))
        else:
            output.write("- Regressions beyond floor: none\n")
    if not admitted:
        fail("candidate is not admitted; see %s" % args.markdown)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print("error: %s" % error, file=sys.stderr)
        sys.exit(1)
