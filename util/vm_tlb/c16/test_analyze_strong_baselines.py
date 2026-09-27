#!/usr/bin/env python3
import unittest

import analyze_strong_baselines as analysis


class AnalyzeStrongBaselinesTest(unittest.TestCase):
    def test_tab_fields(self):
        numbers, strings = analysis.parse_tab_fields(
            "c16_strong_baseline_l2\tinstance=3\tpolicy=DRRIP\taccesses=9")
        self.assertEqual(numbers, {"instance": 3, "accesses": 9})
        self.assertEqual(strings, {"policy": "DRRIP"})

    def test_canonical_drops_only_host_rate(self):
        text = "gpu_sim_cycle = 7\nL2_x = 2\ngpgpu_simulation_rate = 4\nend"
        self.assertEqual(analysis.canonical_behavior(text),
                         ["gpu_sim_cycle = 7", "L2_x = 2", "end"])


if __name__ == "__main__":
    unittest.main()
