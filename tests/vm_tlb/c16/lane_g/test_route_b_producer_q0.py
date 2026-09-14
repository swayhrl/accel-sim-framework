#!/usr/bin/env python3
"""CPU-only Q0 coverage for Route-B producer admission."""
from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "util" / "vm_tlb" / "c16" / "lane_g"))

from route_b_memory_event_contract import RouteBContractError, WhitelistRow, validate_stream
from route_b_producer_q0 import ProducerBinding, deterministic_partitions, validate_partition_union, verify_binding, whitelist_sha256


ROWS = (WhitelistRow(1, "LDG.E.32", "GLOBAL", True, "READ", 4, 0),
        WhitelistRow(2, "STG.E.64", "GLOBAL", True, "WRITE", 8, 0),
        WhitelistRow(3, "ATOM.E.ADD.32", "GLOBAL", True, "ATOMIC", 4, 1, 2))


def event(row: WhitelistRow):
    return {"observed_event_sequence": 1, "sequence_label": "OBSERVED_CALLBACK_ORDER", "kernel_launch_id": 1,
            "function_mangled_name": "_Zexact", "cta": [0, 0, 0], "warp_id": 0, "static_index": row.static_index,
            "instruction_offset": 4, "opcode": row.opcode, "mref_ordinal": row.mref_ordinal,
            "access_kind": row.access_kind, "width_bytes": row.width_bytes, "memory_space": "GLOBAL",
            "active_mask": 3, "predicate_mask": 1, "predicate_semantics": "GUARD_PREDICATE_MASK",
            "record_kind": "LANE_EVENT", "raw_schema": "C16_ROUTE_B_LANE_EVENT_V1",
            "warp_instruction_instance_id": 0, "lane_id": 0, "gpu_va": 0x1000}


class RouteBProducerQ0Tests(unittest.TestCase):
    def test_read_write_atomic_width_and_explicit_mref_ordinal(self):
        for row in ROWS:
            self.assertEqual(1, validate_stream([event(row)], [row], {"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0}))

    def test_binding_checks_code_map_and_whitelist_sha(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code, static_map = root / "code.so", root / "map.tsv"
            code.write_bytes(b"code-object")
            static_map.write_bytes(b"static-map")
            binding = ProducerBinding("_Zexact", code, hashlib.sha256(b"code-object").hexdigest(), static_map,
                                      hashlib.sha256(b"static-map").hexdigest(), whitelist_sha256(ROWS), 1024)
            verify_binding(binding, ROWS)
            with self.assertRaises(RouteBContractError):
                verify_binding(binding, ROWS[:2])
            with self.assertRaises(RouteBContractError):
                verify_binding(ProducerBinding("_Zexact", code, "0" * 64, static_map,
                                               binding.static_map_sha256, binding.whitelist_sha256, 1024), ROWS)

    def test_partition_union_is_deterministic_and_no_overlap(self):
        partitions = deterministic_partitions([1, 2, 3, 4, 5], 2)
        self.assertEqual(((1, 2), (3, 4), (5,)), partitions)
        validate_partition_union([1, 2, 3, 4, 5], partitions)
        with self.assertRaises(RouteBContractError):
            validate_partition_union([1, 2, 3], ((1, 2), (2, 3)))

    def test_missing_terminal_and_invalid_space_fail(self):
        with self.assertRaises(RouteBContractError):
            validate_stream([event(ROWS[0])], [ROWS[0]], {})
        with self.assertRaises(RouteBContractError):
            validate_stream([event(ROWS[0])], [WhitelistRow(1, "LDG", "LOCAL", True, "READ", 4, 0)],
                            {"terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0})


if __name__ == "__main__":
    unittest.main()
