#!/usr/bin/env python3
"""CPU-only unit checks for the C16 V5 LDGSTS consumer safeguards."""
from __future__ import annotations

import json
import struct
import tempfile
import unittest
from pathlib import Path

import c16_ldgsts_analysis as a


class LdgstsConsumerTests(unittest.TestCase):
    def test_01_operand_authority_is_one(self):
        self.assertTrue(a.terminal_ok(self._log("C16_LDGSTS_OPERANDS static=7 memory_space=GLOBAL_TO_SHARED selected_operand=1 mref_count=2\nC16_WARP_TERMINAL static=7 occurrence=0 records=0 overflow=0\n"), 7, 0, 0, 0, True))

    def test_02_operand_zero_is_rejected(self):
        self.assertFalse(a.terminal_ok(self._log("C16_LDGSTS_OPERANDS static=7 memory_space=GLOBAL_TO_SHARED selected_operand=0 mref_count=2\nC16_WARP_TERMINAL static=7 occurrence=0 records=0 overflow=0\n"), 7, 0, 0, 0, True))

    def test_03_zero_requires_terminal_closure(self):
        self.assertFalse(a.terminal_ok(self._log(""), 7, 0, 0, 0, True))

    def test_04_nonzero_overflow_fails_terminal(self):
        self.assertFalse(a.terminal_ok(self._log("C16_LDGSTS_OPERANDS static=7 memory_space=GLOBAL_TO_SHARED selected_operand=1 mref_count=2\nC16_WARP_TERMINAL static=7 occurrence=0 records=1 overflow=1\n"), 7, 0, 1, 0, True))

    def test_05_exact_128_width(self):
        self.assertEqual(a.exact_width({"opcode": "LDGSTS.E.BYPASS.LTC128B.128", "sass": "LDGSTS.E.BYPASS.LTC128B.128 [R1], [R2] ;"}), 16)

    def test_06_width_needs_exact_sass(self):
        self.assertIsNone(a.exact_width({"opcode": "LDGSTS.E.BYPASS.LTC128B.128", "sass": "LDG.E.128 R1, [R2] ;"}))

    def test_07_start_and_touched_boundary_differ(self):
        start, touched = set(), set()
        start.add(0x7F >> 7); a.bucket_add(touched, 0x7F, 16, 7)
        self.assertEqual(len(start), 1); self.assertEqual(len(touched), 2)

    def test_08_same_process_range_match(self):
        starts, table, overlaps = a.ranges(self._context([{ "address_start_hex":"0x1000", "address_end_hex":"0x1100", "class":"WEIGHT", "runtime_name":"w" }]))
        self.assertEqual(a.object_match(0x1008, starts, table, overlaps)[0], "WEIGHT")

    def test_09_foreign_or_missing_range_is_unknown(self):
        starts, table, overlaps = a.ranges(self._context([{ "address_start_hex":"0x1000", "address_end_hex":"0x1100", "class":"WEIGHT", "runtime_name":"w" }]))
        self.assertEqual(a.object_match(0x2000, starts, table, overlaps)[0], "UNKNOWN_RUNTIME")

    def test_10_overlap_fails_closed_to_ambiguous(self):
        starts, table, overlaps = a.ranges(self._context([{ "address_start_hex":"0x1000", "address_end_hex":"0x1200", "class":"WEIGHT", "runtime_name":"a" }, { "address_start_hex":"0x1100", "address_end_hex":"0x1300", "class":"KV_CACHE", "runtime_name":"b" }]))
        self.assertEqual(a.object_match(0x1180, starts, table, overlaps)[0], "AMBIGUOUS_RUNTIME_RANGE")

    def test_11_no_absolute_va_union_representation(self):
        self.assertNotIn("absolute_va_union", a.main.__code__.co_names)

    def test_12_c16warp_header_rejects_overflow(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.bin"; c = self._context([])
            p.write_bytes(a.HEADER.pack(a.MAGIC, 3, 0, 0, 1, 0))
            with self.assertRaises(a.ClosedError):
                a.parse_shard(p, 3, 0, 0, 1, 16, c)

    def _log(self, text: str) -> Path:
        d = Path(tempfile.mkdtemp()); p = d / "x.stdout.log"; p.write_text(text); self.addCleanup(lambda: __import__("shutil").rmtree(d)); return p

    def _context(self, rows: list[dict]) -> Path:
        d = Path(tempfile.mkdtemp()); p = d / "ctx.json"; p.write_text(json.dumps({"ranges": rows})); self.addCleanup(lambda: __import__("shutil").rmtree(d)); return p


if __name__ == "__main__":
    unittest.main()
