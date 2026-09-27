#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import e1_m1f_static_analysis as analysis


class StaticAnalysisTest(unittest.TestCase):
    def test_distribution(self):
        value = analysis.distribution([0, 1, 2, 3])
        self.assertEqual(value["sum"], 6)
        self.assertEqual(value["min"], 0)
        self.assertEqual(value["max"], 3)
        self.assertEqual(value["zero_fraction"], .25)
        self.assertGreater(value["coefficient_of_variation"], 0)

    def test_toy_parser(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.log"
            path.write_text(
                "M1F_TOY_SURVIVAL_PASS m1_occupancy=4 "
                "class_quota_occupancy=4 m1f_occupancy=3 "
                "m1_next_round_hits=0 class_quota_next_round_hits=0 "
                "m1f_next_round_hits=3 m1_old_address_survived=0 "
                "class_quota_old_address_survived=0 "
                "m1f_old_address_survived=1 old_address_class=1 "
                "old_address_line=4\n", encoding="utf-8")
            result = analysis.parse_toy(path)
            self.assertEqual(result["policies"]["M1F_STABLE_ADDRESS_SUBSET"]
                             ["next_round_old_address_hits"], 3)
            self.assertTrue(result["policies"]["M1F_STABLE_ADDRESS_SUBSET"]
                            ["old_address_survived_after_round_one"])
            self.assertEqual(result["claim_boundary"],
                             "CPU_ONLY_PROTECTED_POOL_REFERENCE_NOT_FULL_CACHE_OR_TIMING")

    def test_constants(self):
        self.assertEqual(analysis.GLOBAL_QUOTA_LINES, 131072)
        self.assertEqual(analysis.FAMILY_LINES, 7426048)
        self.assertEqual(analysis.THRESHOLD_HEX, "0x0484baf3b723b966")


if __name__ == "__main__":
    unittest.main()
