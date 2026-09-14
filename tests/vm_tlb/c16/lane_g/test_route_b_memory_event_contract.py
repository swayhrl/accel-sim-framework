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
        "width_bytes": 8, "memory_space": "GLOBAL", "active_mask": 0b101, "predicate_mask": 0b001,
        "active_lane_ids": [0, 2], "gpu_va_by_active_lane": [0x1000, 0x1010],
    }
    value.update(updates)
    return value


class RouteBMemoryEventContractTests(unittest.TestCase):
    def test_complete_global_mref_event_passes(self):
        self.assertEqual(1, validate_stream([event()], [ROW], {"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0}))

    def test_whitelist_rejects_non_global_and_unsorted(self):
        with self.assertRaises(RouteBContractError):
            validate_whitelist([WhitelistRow(7, "LD", "LOCAL", True, "READ", 4, 0)])
        with self.assertRaises(RouteBContractError):
            validate_whitelist([WhitelistRow(8, "LD", "GLOBAL", True, "READ", 4, 0), ROW])

    def test_mask_address_mref_and_terminal_fail_closed(self):
        for updates in ({"active_lane_ids": [0]}, {"gpu_va_by_active_lane": [0, 0]}, {"mref_ordinal": 1}):
            with self.assertRaises(RouteBContractError):
                validate_stream([event(**updates)], [ROW], {"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0})
        with self.assertRaises(RouteBContractError):
            validate_stream([event()], [ROW], {"terminal_status": "COMPLETE", "overflow_count": 1, "drop_count": 0})

    def test_sequence_is_observed_not_hardware_order(self):
        with self.assertRaises(RouteBContractError):
            validate_stream([event(sequence_label="HARDWARE_GLOBAL_ORDER")], [ROW], {"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0})


if __name__ == "__main__":
    unittest.main()
