#!/usr/bin/env python3
"""Validate emitted C10B-3 directed telemetry, without a simulator run.

The input is saved output from the tiny Core-side directed workload.  This
validator checks the emitted interface and conservation relationships; it does
not infer a performance result and it does not replace C5.
"""

from __future__ import print_function

import sys


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read_stats(path):
    values = {}
    with open(path, "r") as source:
        for raw in source:
            if " = " not in raw:
                continue
            key, value = raw.rstrip("\n").split(" = ", 1)
            values[key] = value
    return values


def integer(values, key):
    require(key in values, "missing emitted telemetry field: %s" % key)
    try:
        return int(values[key])
    except ValueError:
        raise AssertionError("non-integer emitted telemetry field %s=%r" %
                             (key, values[key]))


def equal(values, key, expected):
    actual = integer(values, key)
    require(actual == expected, "%s=%d, expected %d" %
            (key, actual, expected))


def validate_subentry(path):
    values = read_stats(path)
    equal(values, "vm_l2_tlb_mode", 1)
    require(values.get("vm_l2_tlb_subentry_schema") ==
            "REFERENCE_APPROX_SUBENTRY_16",
            "sub-entry candidate label/schema regressed")
    for key, expected in (
            ("vm_l2_tlb_subentry_group_entries", 2),
            ("vm_l2_tlb_subentry_count_per_group", 16),
            ("vm_l2_tlb_accesses", 3),
            ("vm_l2_tlb_hits", 1),
            ("vm_l2_tlb_misses", 2),
            ("vm_l2_tlb_subentry_valid_occupancy", 2),
            ("vm_l2_tlb_subentry_group_fills", 1),
            ("vm_l2_tlb_subentry_existing_group_fills", 1),
            ("vm_l2_tlb_subentry_group_evictions", 0),
            ("vm_l2_tlb_subentry_valid_evictions", 0),
            ("vm_object_attribution_conservation_pass", 1)):
        equal(values, key, expected)
    require(integer(values, "vm_l2_tlb_subentry_base_tag_hits") == 2 and
            integer(values, "vm_l2_tlb_subentry_base_tag_misses") == 1,
            "sub-entry group tag accounting changed")
    # A base-tag miss has no resident group whose leaf can be selected.  The
    # selected-leaf counters therefore partition *base-tag hits*, while the
    # aggregate L2 hit/miss counters partition all accesses.
    require(integer(values, "vm_l2_tlb_subentry_hits") +
            integer(values, "vm_l2_tlb_subentry_misses") ==
            integer(values, "vm_l2_tlb_subentry_base_tag_hits"),
            "sub-entry selected-leaf accounting does not conserve")


def main(path, subentry_path):
    values = read_stats(path)
    require(values.get("vm_weight_segment_registration_schema") ==
            "C10A_REGISTERED_PA_V2", "registration provenance/schema regressed")
    require(values.get("vm_weight_segment_registration_status") == "ACCEPTED_V2",
            "directed registered descriptor was not accepted")
    require(values.get("vm_weight_segment_lifecycle_state") == "INACTIVE",
            "revoke must leave the directed controller inactive")

    # Segment ownership and suppression are emitted—not assumed from source.
    for key, expected in (
            ("vm_weight_segment_lookup_attempts", 3),
            ("vm_weight_segment_lookup_accepts", 3),
            ("vm_weight_segment_port_denials", 0),
            ("vm_weight_segment_lookup_launches", 3),
            ("vm_weight_segment_lookup_completions", 3),
            ("vm_weight_segment_hits", 1),
            ("vm_weight_segment_misses", 2),
            ("vm_weight_segment_l2_suppressed", 1),
            ("vm_weight_segment_mshr_suppressed", 1),
            ("vm_weight_segment_pwq_suppressed", 1),
            ("vm_weight_segment_walker_suppressed", 1),
            ("vm_weight_segment_pwc_suppressed", 1),
            ("vm_weight_segment_pte_suppressed", 1),
            ("vm_weight_segment_l1_fills_suppressed", 1),
            ("vm_weight_segment_first_owners", 1),
            ("vm_weight_segment_l1_first_owners", 0),
            ("vm_weight_segment_both_miss", 2),
            ("vm_weight_segment_mapping_mismatch_faults", 0),
            ("vm_weight_segment_install_attempts", 1),
            ("vm_weight_segment_install_acks", 1),
            ("vm_weight_segment_revoke_attempts", 1),
            ("vm_weight_segment_revoke_acks", 1),
            ("vm_weight_segment_install_replica_acks", 1),
            ("vm_weight_segment_revoke_replica_acks", 1),
            ("vm_translation_generation_advances", 0),
            ("vm_translation_stale_fills_discarded", 0),
            ("vm_translation_stale_ready_discards", 0),
            ("vm_translation_stale_waiters_discarded", 0)):
        equal(values, key, expected)

    require(integer(values, "vm_weight_segment_hits") +
            integer(values, "vm_weight_segment_misses") ==
            integer(values, "vm_weight_segment_lookup_completions"),
            "Segment terminal outcomes do not conserve")

    # Conventional pressure is present only for the two Segment misses.
    for key, expected in (
            ("vm_l2_tlb_lookup_launches", 2),
            ("vm_translation_mshr_allocations", 2),
            ("vm_translation_mshr_merges", 0),
            ("vm_translation_mshr_active", 0),
            ("vm_translation_pwq_occupancy", 0),
            ("vm_translation_walkers_active", 0),
            ("vm_translation_walk_starts", 2),
            ("vm_translation_walk_completions", 2),
            ("vm_pte_response_misassociations", 0),
            ("vm_object_attribution_conservation_pass", 1)):
        equal(values, key, expected)
    require(integer(values, "vm_l2_tlb_accesses") ==
            integer(values, "vm_l2_tlb_hits") +
            integer(values, "vm_l2_tlb_misses"),
            "L2 hit/miss accounting does not conserve")
    require(integer(values, "vm_translation_mshr_allocations") ==
            integer(values, "vm_translation_mshr_entries_completed"),
            "MSHR allocation/completion accounting does not conserve")
    require(integer(values, "vm_pte_requests") ==
            integer(values, "vm_pte_responses"),
            "physical PTE request/response accounting does not conserve")
    require(integer(values, "vm_pte_l2_only_responses") +
            integer(values, "vm_pte_dram_responses") ==
            integer(values, "vm_pte_responses"),
            "PTE L2-only/DRAM response partition does not conserve")
    require(integer(values, "vm_pwc_accesses") ==
            integer(values, "vm_pwc_hits") + integer(values, "vm_pwc_misses"),
            "PWC hit/miss accounting does not conserve")

    # `completed` is terminal frontend delivery and must be exactly-once.  The
    # older requester counter deliberately also samples MSHR wakeup for M3
    # latency accounting, hence the explicit—not accidental—relationship.
    completed = integer(values, "vm_functional_completed")
    require(completed == 3, "directed READ/READ/WRITE frontend completion changed")
    require(integer(values, "vm_translation_requester_completions") ==
            completed + integer(values, "vm_translation_waiter_wakeups"),
            "requester critical-path sampling relationship changed")

    if subentry_path is not None:
        validate_subentry(subentry_path)

    print("C10B telemetry PASS: emitted Segment, lifecycle, conventional "
          "translation, PTE/PWC, and exact-once frontend conservation")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print("usage: validate_c10b_telemetry.py <emitted-stats> [subentry-stats]",
              file=sys.stderr)
        sys.exit(2)
    try:
        main(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else None)
    except (AssertionError, IOError) as error:
        print("C10B telemetry FAIL: %s" % error, file=sys.stderr)
        sys.exit(1)
