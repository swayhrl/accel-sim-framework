#!/usr/bin/env python3
import unittest

import e1_m1f_real_trace_analysis as analysis


class RealTraceAnalysisTest(unittest.TestCase):
    def test_frozen_hash_witnesses(self):
        self.assertEqual(analysis.stable_hash(1, 1186),
                         0xD92231F51D5C2EFB)
        self.assertEqual(analysis.stable_hash(15, 2),
                         0xC69C317586B04F9E)
        self.assertEqual(analysis.stable_hash(28, 1193),
                         0xFCF49FC4E0BF282D)
        self.assertTrue(all(value >= analysis.THRESHOLD for value in (
            analysis.stable_hash(1, 1186),
            analysis.stable_hash(15, 2),
            analysis.stable_hash(28, 1193))))

    def test_tab_counter_parser(self):
        row = analysis.parse_fields(
            "oracle_elastic_l2\tinstance=3\ttarget_accesses=17\t"
            "selected_target_accesses=2\n")
        self.assertEqual(row, {"instance": 3, "target_accesses": 17,
                               "selected_target_accesses": 2})


if __name__ == "__main__":
    unittest.main()
