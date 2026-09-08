#!/usr/bin/env python3
"""Validate the current-binary C10B-3 bounded F8 telemetry stream.

This consumes a saved three-kernel, immutable-trace log.  It is a correctness
and observability check only; it does not calculate or report performance.
"""

from __future__ import print_function

import sys


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def values_from_last_block(path):
    values = {}
    with open(path, "r") as source:
        for raw in source:
            if raw.startswith("vm_") and " = " in raw:
                key, value = raw.rstrip("\n").split(" = ", 1)
                values[key] = value
    return values


def integer(values, key):
    require(key in values, "missing final emitted field: %s" % key)
    try:
        return int(values[key])
    except ValueError:
        raise AssertionError("non-integer final field %s=%r" %
                             (key, values[key]))


def equal(values, key, expected):
    actual = integer(values, key)
    require(actual == expected, "%s=%d, expected %d" %
            (key, actual, expected))


def main(path):
    values = values_from_last_block(path)
    require(values.get("vm_fair_arm_name") == "F8",
            "bounded run did not realize F8")
    for key, expected in (
            ("vm_fair_arm_id", 9),
            ("vm_fair_arm_charged_bits", 57734),
            ("vm_fair_l2_entries_realized", 32),
            ("vm_fair_l2_sets_realized", 2),
            ("vm_fair_l2_associativity_realized", 16),
            ("vm_weight_segment_entries_configured", 8),
            ("vm_weight_segment_descriptors_loaded", 1),
            ("vm_weight_segment_lifecycle_active_asid", 0),
            ("vm_weight_segment_lifecycle_active_epoch", 1),
            ("vm_weight_segment_local_table_replicas", 35),
            ("vm_weight_segment_local_table_entries", 8),
            ("vm_weight_segment_local_accepts_per_cycle", 1),
            ("vm_weight_segment_lookup_latency_cycles", 10),
            ("vm_weight_segment_port_denials", 0),
            ("vm_weight_segment_mapping_mismatch_faults", 0),
            ("vm_weight_segment_install_attempts", 1),
            ("vm_weight_segment_install_acks", 1),
            ("vm_weight_segment_install_replica_acks", 35),
            ("vm_l2_tlb_mode", 1),
            ("vm_l2_tlb_subentry_group_entries", 32),
            ("vm_l2_tlb_subentry_count_per_group", 16),
            ("vm_translation_mshr_active", 0),
            ("vm_translation_pwq_occupancy", 0),
            ("vm_translation_walkers_active", 0),
            ("vm_pte_response_misassociations", 0),
            ("vm_object_attribution_conservation_pass", 1)):
        equal(values, key, expected)
    require(values.get("vm_weight_segment_registration_schema") ==
            "C10A_REGISTERED_PA_V2", "V2 registration schema not emitted")
    require(values.get("vm_weight_segment_registration_status") == "ACCEPTED_V2",
            "V2 registration not accepted")
    require(values.get("vm_weight_segment_lifecycle_state") == "ACTIVE",
            "all 35 install acknowledgements did not activate Segment")
    require(values.get("vm_l2_tlb_subentry_schema") ==
            "REFERENCE_APPROX_SUBENTRY_16", "sub-entry label/schema changed")

    attempts = integer(values, "vm_weight_segment_lookup_attempts")
    require(attempts > 0 and attempts ==
            integer(values, "vm_weight_segment_lookup_accepts") ==
            integer(values, "vm_weight_segment_lookup_launches") ==
            integer(values, "vm_weight_segment_lookup_completions"),
            "Segment admission/launch/completion does not conserve")
    hits = integer(values, "vm_weight_segment_hits")
    misses = integer(values, "vm_weight_segment_misses")
    require(hits > 0 and hits + misses == attempts,
            "Segment hit/miss outcomes do not conserve")
    for key in ("vm_weight_segment_l2_suppressed",
                "vm_weight_segment_mshr_suppressed",
                "vm_weight_segment_pwq_suppressed",
                "vm_weight_segment_walker_suppressed",
                "vm_weight_segment_pwc_suppressed",
                "vm_weight_segment_pte_suppressed",
                "vm_weight_segment_l1_fills_suppressed"):
        require(integer(values, key) == hits,
                "%s must equal Segment-owned hit count" % key)
    require(integer(values, "vm_functional_completed") == attempts,
            "external frontend completions are not exact-once per attempt")
    require(integer(values, "vm_translation_requester_completions") ==
            integer(values, "vm_functional_completed") +
            integer(values, "vm_translation_waiter_wakeups"),
            "critical-path observations do not account for PTW wakeups")

    require(integer(values, "vm_l2_tlb_accesses") ==
            integer(values, "vm_l2_tlb_hits") +
            integer(values, "vm_l2_tlb_misses"),
            "aggregate L2 TLB accounting does not conserve")
    require(integer(values, "vm_l2_tlb_subentry_hits") +
            integer(values, "vm_l2_tlb_subentry_misses") ==
            integer(values, "vm_l2_tlb_subentry_base_tag_hits"),
            "sub-entry selected-leaf accounting does not conserve")
    require(integer(values, "vm_translation_mshr_allocations") ==
            integer(values, "vm_translation_mshr_entries_completed"),
            "MSHR allocation/completion accounting does not conserve")
    require(integer(values, "vm_pte_requests") ==
            integer(values, "vm_pte_responses"),
            "PTE request/response accounting does not conserve")
    require(integer(values, "vm_pte_l2_only_responses") +
            integer(values, "vm_pte_dram_responses") ==
            integer(values, "vm_pte_responses"),
            "PTE L2-only/DRAM partition does not conserve")
    require(integer(values, "vm_pwc_accesses") ==
            integer(values, "vm_pwc_hits") + integer(values, "vm_pwc_misses"),
            "PWC hit/miss accounting does not conserve")

    with open(path, "r") as source:
        text = source.read()
    require("m4c_telemetry_cross_l1\tKERNEL\tUNKNOWN\t0\tDATA_WEIGHT\t"
            "SEGMENT_HIT" in text,
            "current emitted cross-layer telemetry lacks DATA_WEIGHT/SEGMENT_HIT")
    require("m4c_telemetry_dram\tKERNEL\tUNKNOWN\t0\tPTE_L0" in text and
            "m4c_telemetry_l2_queue\tKERNEL" in text,
            "current emitted L2-queue/DRAM PTE continuity is absent")
    print("C10B bounded F8 telemetry PASS: V2 non-identity registration, "
          "Segment suppression, sub-entry, frontend exact-once, and "
          "L1D/L2/queue/DRAM cross-layer observability")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: validate_c10b_bounded_f8.py <run.log>", file=sys.stderr)
        sys.exit(2)
    try:
        main(sys.argv[1])
    except (AssertionError, IOError) as error:
        print("C10B bounded F8 telemetry FAIL: %s" % error, file=sys.stderr)
        sys.exit(1)
