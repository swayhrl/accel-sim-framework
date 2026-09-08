#!/usr/bin/env python3
"""Static C10-A validator for the frozen C9 fair-arm manifest contract.

It deliberately validates metadata only.  It does not build or invoke a
simulator, read an ROI, or turn any speculative arm into a performance result.
"""

from __future__ import print_function

import csv
import os
import sys


ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONTRACT = os.path.join(ROOT, "configs", "vm_tlb",
                        "M4B_C10A_FAIR_ARM_CONTRACT.tsv")


def rows(path):
    with open(path, "r") as source:
        return list(csv.DictReader(
            (line for line in source if not line.startswith("#")),
            delimiter="\t"))


def as_int(row, column):
    return int(row[column])


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    table = rows(CONTRACT)
    by_id = dict((row["arm_id"], row) for row in table)
    expected = set(["F%d" % number for number in range(10)] + ["H0"])
    require(set(by_id) == expected, "arm IDs must be exactly F0--F9 plus H0")
    require(len(table) == len(by_id), "arm IDs must be unique")

    for arm in sorted(expected - set(["H0"])):
        require(by_id[arm]["official_selectable"] == "true",
                "%s must be selectable" % arm)
    historical = by_id["H0"]
    require(historical["official_selectable"] == "false",
            "historical 768-group arm must be rejected")
    require(as_int(historical, "group_count") == 768 and
            as_int(historical, "charged_bits") == 478416,
            "historical arm must retain its charged, unfair cost")
    require("HISTORICAL_UNFAIR" in historical["status"],
            "historical arm requires an explicit unfair label")

    # C9 accounting ABI: exact entry=85b, group=622b, PLRU=15b/set.
    exact = lambda entries: entries * 85 + (entries // 16) * 15
    subentry = lambda groups: groups * 622 + (groups // 16) * 15
    expect_bits = {
        "F0": exact(768), "F1": subentry(96), "F2": exact(688),
        "F4": exact(1536), "F5": exact(656) + 8370,
        "F6": 848 * 76 + 53 * 15,
        "F7": 35 * 8 * 135 + exact(320),
        "F8": 35 * 8 * 135 + subentry(32), "F9": exact(656),
    }
    for arm, bits in sorted(expect_bits.items()):
        require(as_int(by_id[arm], "charged_bits") == bits,
                "%s charged bits disagree with C9 ABI" % arm)

    for arm, groups, sets in (("F1", 96, 6), ("F8", 32, 2)):
        row = by_id[arm]
        require(as_int(row, "group_count") == groups and
                as_int(row, "associativity") == 16 and
                as_int(row, "sets") == sets and
                as_int(row, "leaves_per_group") == 16,
                "%s sub-entry geometry is not C9 fair geometry" % arm)
        require(groups % 16 == 0, "%s must have whole 16-way sets" % arm)
        require(row["page_size_class"] == "64KiB", "%s must be base-page only" % arm)

    for arm in ("F7", "F8"):
        row = by_id[arm]
        require(as_int(row, "segment_replicas") == 35 and
                as_int(row, "segment_slots_per_replica") == 8 and
                row["segment_latency_cycles"] == "5|10|20" and
                as_int(row, "segment_accepts_per_cycle") == 1,
                "%s Segment contract is incomplete" % arm)
    require(by_id["F5"]["pwc_entries"] == "120" and
            "one_port_queue" in by_id["F5"]["pwc_layout"] and
            "OFFICIAL_C10B_PHYSICAL_PWC" in by_id["F5"]["status"],
            "F5 must name the implemented C10B physical-PWC contract")

    print("C10A fair contract PASS: F0--F9 accounting, F1/F8 geometry, "
          "Segment latency/port contract, F5 physical PWC, and H0 unfair-arm guard")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, KeyError, ValueError) as error:
        print("C10A fair contract FAIL: %s" % error, file=sys.stderr)
        sys.exit(1)
