#!/usr/bin/env python3
"""Validate emitted C10B-4 F5 physical-PWC telemetry, not source fields."""

from __future__ import print_function

import re
import sys


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def values(path):
    result = {}
    with open(path, "r") as source:
        for line in source:
            match = re.match(r"^(vm_[A-Za-z0-9_]+) = (.+)$", line.rstrip())
            if match:
                result[match.group(1)] = match.group(2)
    return result


def number(table, key):
    require(key in table, "missing emitted field: %s" % key)
    return int(table[key])


def main():
    require(len(sys.argv) == 2, "usage: validate_c10b_f5_physical_pwc.py <run.log>")
    table = values(sys.argv[1])
    require(table.get("vm_fair_arm_id") == "6" and
            table.get("vm_fair_arm_name") == "F5" and
            number(table, "vm_fair_arm_charged_bits") == 64745,
            "F5 selector/accounting mismatch")
    require(number(table, "vm_translation_page_size_bytes") == 65536 and
            number(table, "vm_translation_virtual_address_bits") == 49 and
            number(table, "vm_fair_l2_entries_realized") == 656 and
            number(table, "vm_fair_l2_sets_realized") == 41,
            "F5 C9 base-page/exact remainder geometry mismatch")
    require(number(table, "vm_pwc_mode") == 3 and
            number(table, "vm_pwc_entries_configured") == 120 and
            number(table, "vm_pwc_physical_f5_enabled") == 1 and
            number(table, "vm_pwc_physical_f5_entries_total") == 120 and
            number(table, "vm_pwc_physical_f5_entries_per_nonleaf_level") == 40 and
            number(table, "vm_pwc_physical_f5_sets_per_level") == 10 and
            number(table, "vm_pwc_physical_f5_ways") == 4 and
            table.get("vm_pwc_physical_f5_prefix_bits_l0_l1_l2") == "6|15|24",
            "F5 physical PWC geometry mismatch")
    require(number(table, "vm_pwc_physical_f5_payload_bits") == 33 and
            number(table, "vm_pwc_physical_f5_attributes_bits") == 2 and
            number(table, "vm_pwc_physical_f5_array_bits") == 8280 and
            number(table, "vm_pwc_physical_f5_plru_bits") == 90 and
            number(table, "vm_pwc_physical_f5_charged_bits") == 8370,
            "F5 pointer-payload or PLRU accounting mismatch")
    accesses = number(table, "vm_pwc_accesses")
    hits = number(table, "vm_pwc_hits")
    misses = number(table, "vm_pwc_misses")
    require(accesses == hits + misses and
            number(table, "vm_pwc_port_accepts") == accesses and
            number(table, "vm_pwc_port_denials") > 0 and
            number(table, "vm_pwc_queue_wait_cycles_total") > 0 and
            number(table, "vm_pwc_queue_high_watermark") > 0,
            "F5 one-port queue or PWC conservation mismatch")
    require(number(table, "vm_pwc_physical_payload_validations") == hits and
            number(table, "vm_pwc_evictions") > 0 and
            number(table, "vm_pwc_occupancy_high_watermark") <= 120,
            "F5 payload validation or four-way replacement missing")
    require(number(table, "vm_pte_requests") == number(table, "vm_pte_responses") and
            number(table, "vm_functional_completed") ==
            number(table, "vm_translation_mshr_entries_completed") and
            number(table, "vm_translation_mshr_active") == 0 and
            number(table, "vm_translation_walkers_active") == 0,
            "F5 requester/PTE drain conservation mismatch")
    require(number(table, "vm_weight_segmentation_enabled") == 0 and
            number(table, "vm_weight_segment_hits") == 0,
            "F5 must not silently enable Weight Segmentation")
    print("C10B F5 emitted telemetry PASS: physical 3x40/4-way pointer PWC, "
          "one-port queue, PLRU/remainder accounting, and drained PTE state")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, IOError, ValueError) as error:
        print("C10B F5 emitted telemetry FAIL: %s" % error, file=sys.stderr)
        sys.exit(1)
