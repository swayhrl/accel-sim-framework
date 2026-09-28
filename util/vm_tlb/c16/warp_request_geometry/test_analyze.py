#!/usr/bin/env python3
import unittest

from analyze import (
    AMBIG,
    classify_interval,
    covered_units,
    g0_metrics,
    g1_metrics,
    process_addresses,
    self_test,
    union_size,
    width_from_opcode,
)


class GeometryTests(unittest.TestCase):
    def test_required_synthetic_suite(self):
        receipt = self_test()
        self.assertEqual(receipt["status"], "PASS")
        self.assertGreaterEqual(receipt["case_count"], 12)

    def test_broadcast_contiguous_stride_and_crossing(self):
        broadcast = g1_metrics([(0, 4)] * 32)
        self.assertEqual(tuple(broadcast[k] for k in ("L", "U", "C32")), (128, 4, 32))
        self.assertEqual(g1_metrics([(i * 4, i * 4 + 4) for i in range(32)])["C32"], 128)
        self.assertEqual(g1_metrics([(i * 32, i * 32 + 4) for i in range(32)])["C32"], 1024)
        self.assertEqual(g1_metrics([(31, 35)])["C32"], 64)

    def test_masked_zero_and_partial_overlap(self):
        self.assertIsNone(g0_metrics([])["multiplicity"])
        self.assertEqual(union_size([(0, 16), (8, 24)]), 24)
        self.assertEqual(covered_units([(31, 35)], 32), {0, 1})

    def test_roles_and_unresolved_width(self):
        ranges = [("INPUT", "input", 0, 32), ("WEIGHT", "weight", 64, 96)]
        self.assertEqual(classify_interval(30, 34, ranges)[0], AMBIG)
        result = process_addresses([0, 64], 4, ranges)
        self.assertEqual(set(result["g1_roles"]), {"INPUT", "WEIGHT"})
        self.assertIsNone(process_addresses([0], None, ranges)["g1"])

    def test_width_decoder(self):
        self.assertEqual(width_from_opcode("LDG.E.U16.STRONG.SM")[:2], ("QUALIFIED", 2))
        self.assertEqual(width_from_opcode("STG.E.U16")[:2], ("QUALIFIED", 2))
        self.assertEqual(width_from_opcode("LDG.E")[:2], ("QUALIFIED", 4))
        self.assertEqual(width_from_opcode("LDGSTS.E.BYPASS.128")[0], "WIDTH_UNRESOLVED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
