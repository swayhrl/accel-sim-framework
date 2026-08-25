#!/usr/bin/env python3
"""Choose one bank candidate from a provenance-gated observability report.

This intentionally does not perform a sweep.  It makes the diagnosis rule
explicit: uniformly distributed, substantial tag-side requeues favour more
abstract banks; a skewed distribution would instead justify a hash test.
"""

import argparse
import csv
import json
import sys
from pathlib import Path


def fail(message):
    raise RuntimeError(message)


def number(row, name):
    try:
        return float(row[name])
    except (KeyError, ValueError) as error:
        raise RuntimeError("bad %s in case %s" % (name, row.get("case"))) from error


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--observability-csv", required=True)
    parser.add_argument("--markdown", required=True)
    parser.add_argument("--json", required=True)
    parser.add_argument("--require-case", action="append", default=[])
    parser.add_argument("--tag-requeue-min", type=int, default=100000)
    parser.add_argument("--hotspot-max-share", type=float, default=0.35)
    parser.add_argument("--aad-capacity", type=int, default=256)
    parser.add_argument("--lower-read-capacity", type=int, default=32)
    parser.add_argument("--wbq-capacity", type=int, default=4)
    args = parser.parse_args()

    with Path(args.observability_csv).open(newline="") as source:
        rows = list(csv.DictReader(source))
    if not rows:
        fail("empty observability report")
    cases = {row.get("case") for row in rows}
    missing = set(args.require_case) - cases
    if missing:
        fail("missing required cases: %s" % ", ".join(sorted(missing)))
    if len(cases) != len(rows):
        fail("observability report has duplicate cases")
    for row in rows:
        if row.get("bank_hash") != "mod" or int(number(row, "internal_banks")) != 4:
            fail("case %s is not a default four-bank mod diagnosis" % row["case"])

    substantial_tag = [row["case"] for row in rows
                       if number(row, "bank_requeue_tag") >= args.tag_requeue_min]
    hotspot_cases = [row["case"] for row in rows
                     if number(row, "tag_grant_max_share") > args.hotspot_max_share]
    tag_blocks_lower = [row["case"] for row in rows
                        if number(row, "lower_tag") != 0]
    aad_near_limit = [row["case"] for row in rows
                      if number(row, "aad_max_slice") >= args.aad_capacity * 0.75]
    wbq_pressured = [row["case"] for row in rows
                     if number(row, "wbq_max_slice") >= args.wbq_capacity]
    fill_credit_cases = [row["case"] for row in rows
                         if number(row, "fill_max_slice") >= args.lower_read_capacity
                         and number(row, "read_credit_stall") > 0]

    if substantial_tag and not hotspot_cases and not tag_blocks_lower:
        candidate = "bank_count_8"
        rationale = ("substantial tag-side requeues are balanced across banks; "
                     "lower reads are not losing to tag arbitration")
    elif substantial_tag and hotspot_cases:
        candidate = "bank_hash_xor"
        rationale = "substantial tag-side requeues are concentrated on one or more banks"
    else:
        candidate = "none"
        rationale = "bank evidence does not yet select a safe single candidate"

    result = {
        "required_cases": args.require_case,
        "cases": sorted(cases),
        "candidate": candidate,
        "rationale": rationale,
        "substantial_tag_requeue_cases": substantial_tag,
        "hotspot_cases": hotspot_cases,
        "lower_reads_blocked_by_tag_cases": tag_blocks_lower,
        "aad_near_limit_cases": aad_near_limit,
        "wbq_pressured_cases": wbq_pressured,
        "fill_credit_cases": fill_credit_cases,
        "thresholds": {
            "tag_requeue_min": args.tag_requeue_min,
            "hotspot_max_share": args.hotspot_max_share,
            "aad_capacity": args.aad_capacity,
            "lower_read_capacity": args.lower_read_capacity,
            "wbq_capacity": args.wbq_capacity,
        },
    }
    Path(args.json).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with Path(args.markdown).open("w") as output:
        output.write("# Decoupled-L2 bank candidate selection\n\n")
        output.write("Input is a provenance-gated default four-bank, `mod` observability report. "
                     "This gate selects one bank candidate; capacity observations remain separate "
                     "single-variable experiments.\n\n")
        output.write("## Selection\n\n")
        output.write("- Candidate: `%s`\n" % candidate)
        output.write("- Evidence: %s.\n" % rationale)
        output.write("- Tag requeue >= %d: %s\n" %
                     (args.tag_requeue_min, ", ".join(substantial_tag) or "none"))
        output.write("- Tag grant share > %.0f%% (hash-hotspot evidence): %s\n" %
                     (args.hotspot_max_share * 100, ", ".join(hotspot_cases) or "none"))
        output.write("- Lower-read requeued behind tag: %s\n" %
                     (", ".join(tag_blocks_lower) or "none"))
        output.write("- AAD >= 75%% of %d: %s\n" %
                     (args.aad_capacity, ", ".join(aad_near_limit) or "none"))
        output.write("- WBQ reaches its %d-entry capacity: %s\n" %
                     (args.wbq_capacity, ", ".join(wbq_pressured) or "none"))
        output.write("- Fill reaches %d with read-credit stalls: %s\n" %
                     (args.lower_read_capacity, ", ".join(fill_credit_cases) or "none"))
        output.write("\n`lower_read_64/128` may be evaluated only as a separate capacity "
                     "sensitivity study; it is not folded into the selected bank candidate.\n")
    if candidate == "none":
        fail("no single bank candidate selected")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print("error: %s" % error, file=sys.stderr)
        sys.exit(1)
