#!/usr/bin/env python3
"""Check C10B-5 emitted fair-arm controller blocks without performance claims."""

from __future__ import print_function

import re
import sys


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def parse(path):
    blocks = []
    current = None
    with open(path, "r") as source:
        for line in source:
            line = line.rstrip()
            begin = re.match(r"^C10B_FAIR_SANITY_BEGIN (.+)$", line)
            end = re.match(r"^C10B_FAIR_SANITY_END (.+)$", line)
            field = re.match(r"^(vm_[A-Za-z0-9_]+) = (.+)$", line)
            if begin:
                require(current is None, "nested fair-arm block")
                current = {"label": begin.group(1)}
            elif end:
                require(current is not None and current["label"] == end.group(1),
                        "unbalanced fair-arm block")
                blocks.append(current)
                current = None
            elif field and current is not None:
                current[field.group(1)] = field.group(2)
    require(current is None, "unterminated fair-arm block")
    return blocks


def number(block, field):
    require(field in block, "missing %s in %s" % (field, block["label"]))
    return int(block[field])


def assert_arm(block, arm_id, name, bits, entries, sets):
    require(number(block, "vm_fair_arm_id") == arm_id and
            block.get("vm_fair_arm_name") == name and
            number(block, "vm_fair_arm_charged_bits") == bits and
            number(block, "vm_fair_l2_entries_realized") == entries and
            number(block, "vm_fair_l2_sets_realized") == sets,
            "realized fair-arm geometry mismatch for %s" % block["label"])
    require(number(block, "vm_functional_completed") == 1 and
            number(block, "vm_translation_mshr_active") == 0 and
            number(block, "vm_translation_walkers_active") == 0,
            "exact-once/drain mismatch for %s" % block["label"])


def main():
    require(len(sys.argv) == 2, "usage: validate_c10b_fair_arm_sanity.py <run.out>")
    blocks = parse(sys.argv[1])
    by_label = dict((block["label"], block) for block in blocks)
    expected = {
        "F0": (1, "F0", 66000, 768, 48),
        "F1": (2, "F1", 59802, 96, 6),
        "F2": (3, "F2", 59125, 688, 43),
        "F3_E800": (4, "F3", 68750, 800, 50),
        "F4": (5, "F4", 132000, 1536, 96),
        "F5": (6, "F5", 64745, 656, 41),
        "F6": (7, "F6", 65243, 848, 53),
        "F9": (10, "F9", 56375, 656, 41),
    }
    for label, fields in expected.items():
        require(label in by_label, "missing official arm block %s" % label)
        assert_arm(by_label[label], *fields)
    f5 = by_label["F5"]
    require(number(f5, "vm_pwc_physical_f5_enabled") == 1 and
            number(f5, "vm_pwc_physical_f5_charged_bits") == 8370 and
            number(f5, "vm_translation_virtual_address_bits") == 49,
            "F5 physical-PWC configuration missing from fair sanity")
    for name, arm_id, bits, entries, sets in (
            ("F7", 8, 65300, 320, 20), ("F8", 9, 57734, 32, 2)):
        matches = [block for block in blocks
                   if block.get("vm_fair_arm_name") == name]
        require(len(matches) == 3, "%s must expose all three Lseg points" % name)
        latencies = set()
        for block in matches:
            assert_arm(block, arm_id, name, bits, entries, sets)
            latency = number(block, "vm_weight_segment_lookup_latency_cycles")
            latencies.add(latency)
            require(number(block, "vm_weight_segment_local_table_replicas") == 35 and
                    number(block, "vm_weight_segment_local_table_entries") == 8 and
                    number(block, "vm_weight_segment_hits") == 1 and
                    number(block, "vm_weight_segment_l2_suppressed") == 1,
                    "%s Segment realization/suppression mismatch" % name)
        require(latencies == set([5, 10, 20]),
                "%s Lseg sensitivity points incomplete" % name)
    print("C10B fair-arm emitted sanity PASS: F0--F9 official configurations, "
          "F5 physical PWC, F7/F8 5|10|20, and exact-once drains")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, IOError, ValueError) as error:
        print("C10B fair-arm emitted sanity FAIL: %s" % error, file=sys.stderr)
        sys.exit(1)
