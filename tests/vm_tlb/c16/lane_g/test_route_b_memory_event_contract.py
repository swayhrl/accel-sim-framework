#!/usr/bin/env python3
"""CPU-only Q0 fixtures for the Route-B memory-event contract."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "util" / "vm_tlb" / "c16" / "lane_g"))

from route_b_memory_event_contract import RouteBContractError, WhitelistRow, validate_stream, validate_whitelist


ROW = WhitelistRow(7, "LDG.E.64", "GLOBAL", True, "READ", 8, 0)


def event(**updates):
    value = {
        "observed_event_sequence": 1, "sequence_label": "OBSERVED_CALLBACK_ORDER", "kernel_launch_id": 3,
        "function_mangled_name": "_Zexact", "cta": [0, 0, 0], "warp_id": 0, "static_index": 7,
        "instruction_offset": 16, "opcode": "LDG.E.64", "mref_ordinal": 0, "access_kind": "READ",
        "width_bytes": 8, "memory_space": "GLOBAL", "active_mask": 0b101, "predicate_mask": 0b001, "predicate_semantics": "GUARD_PREDICATE_MASK",
        "record_kind": "LANE_EVENT", "raw_schema": "C16_ROUTE_B_LANE_EVENT_V1",
        "warp_instruction_instance_id": 9, "lane_id": 0, "gpu_va": 0x1000,
    }
    value.update(updates)
    return value


class RouteBMemoryEventContractTests(unittest.TestCase):
    def test_complete_global_mref_event_passes(self):
        self.assertEqual(1, validate_stream([event()], [ROW], {"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0, "event_count": 1}))

    def test_whitelist_rejects_non_global_and_unsorted(self):
        with self.assertRaises(RouteBContractError):
            validate_whitelist([WhitelistRow(7, "LD", "LOCAL", True, "READ", 4, 0)])
        with self.assertRaises(RouteBContractError):
            validate_whitelist([WhitelistRow(8, "LD", "GLOBAL", True, "READ", 4, 0), ROW])

    def test_mask_address_mref_and_terminal_fail_closed(self):
        for updates in ({"lane_id": 2}, {"gpu_va": 0}, {"mref_ordinal": 1}):
            with self.assertRaises(RouteBContractError):
                validate_stream([event(**updates)], [ROW], {"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0, "event_count": 1})
        with self.assertRaises(RouteBContractError):
            validate_stream([event()], [ROW], {"terminal_status": "COMPLETE", "overflow_count": 1, "drop_count": 0, "event_count": 1})
        with self.assertRaises(RouteBContractError):
            validate_stream([event()], [ROW], {"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0, "event_count": 2})

    def test_sequence_is_observed_not_hardware_order(self):
        with self.assertRaises(RouteBContractError):
            validate_stream([event(sequence_label="HARDWARE_GLOBAL_ORDER")], [ROW], {"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0, "event_count": 1})
        with self.assertRaises(RouteBContractError):
            validate_stream([event(predicate_semantics="STATIC_PREDICATE_GUESSED")], [ROW],
                            {"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0, "event_count": 1})

    def test_lane_event_is_exactly_one_predicate_true_executing_lane(self):
        self.assertEqual(1, validate_stream([event()], [ROW], {"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0, "event_count": 1}))
        with self.assertRaises(RouteBContractError):
            validate_stream([event(lane_id=2)], [ROW], {"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0, "event_count": 1})
        events = [event(predicate_mask=0b101, lane_id=0, gpu_va=0x1000),
                  event(observed_event_sequence=2, predicate_mask=0b101, lane_id=2, gpu_va=0x1010)]
        self.assertEqual(2, validate_stream(events, [ROW], {"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0, "event_count": 2}))

    def test_instance_id_not_adjacent_sequence_groups_lanes(self):
        first_lane0 = event(predicate_mask=0b101, lane_id=0, warp_instruction_instance_id=4)
        second = event(observed_event_sequence=2, predicate_mask=0b101, lane_id=0,
                       warp_instruction_instance_id=5, gpu_va=0x2000)
        first_lane2 = event(observed_event_sequence=3, predicate_mask=0b101, lane_id=2,
                            warp_instruction_instance_id=4, gpu_va=0x1010)
        second_lane2 = event(observed_event_sequence=4, predicate_mask=0b101, lane_id=2,
                             warp_instruction_instance_id=5, gpu_va=0x2010)
        self.assertEqual(4, validate_stream([first_lane0, second, first_lane2, second_lane2], [ROW],
                                            {"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0, "event_count": 4}))
        with self.assertRaises(RouteBContractError):
            validate_stream([first_lane0, first_lane2, first_lane2], [ROW],
                            {"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0, "event_count": 3})

    def test_instance_id_is_scoped_by_kernel_launch(self):
        # Device buffers reset each launch, so instance 0 is valid in both.
        launch_one = event(predicate_mask=0b001, warp_instruction_instance_id=0, kernel_launch_id=1)
        launch_two = event(observed_event_sequence=2, predicate_mask=0b001, warp_instruction_instance_id=0,
                           kernel_launch_id=2, gpu_va=0x2000)
        self.assertEqual(2, validate_stream([launch_one, launch_two], [ROW],
                                            {"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0, "event_count": 2}))

    def test_multi_mref_is_explicitly_keyed_and_bounded(self):
        second = WhitelistRow(7, "LDG.E.64", "GLOBAL", True, "READ", 8, 1, 2)
        self.assertEqual(1, validate_stream([event(mref_ordinal=1)], [second], {"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0, "event_count": 1}))
        with self.assertRaises(RouteBContractError):
            validate_whitelist([WhitelistRow(7, "LDG.E.64", "GLOBAL", True, "READ", 8, 2, 2)])


if __name__ == "__main__":
    unittest.main()
