#!/usr/bin/env python3
"""Contract checks for explicit integrated M0a+M1 modes and provenance."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
RUNNER = ROOT / "util/ep_l2/run_m0a_observability.py"
SPEC = importlib.util.spec_from_file_location("m0a_m1_runner", RUNNER)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class M0aM1ModeContractTest(unittest.TestCase):
    def test_expected_modes_are_explicit_and_off_by_default(self):
        self.assertEqual(set(MODULE.MODES), {"BASE_M1_STATIC", "M0A_ON_M1_STATIC"})
        self.assertFalse(MODULE.MODES["BASE_M1_STATIC"]["m0a_stats_enabled"])
        for mode in MODULE.MODES.values():
            self.assertEqual(mode["ep_l2_features"]["payload_policy"], "static")
            self.assertFalse(mode["ep_l2_features"]["unified_payload"])
            self.assertFalse(mode["ep_l2_features"]["ro_pending_state"])
            self.assertFalse(mode["ep_l2_features"]["tvd"])
            self.assertFalse(mode["ep_l2_features"]["adaptive_policy"])

    def test_promotion_state_is_explicit(self):
        self.assertEqual(MODULE.MATURE, "SPECULATIVE_PENDING_GATE")
        self.assertEqual(MODULE.PROMOTION_DEPENDENCIES,
                         ("M0A_FINAL_PASS", "M1_FINAL_PASS"))


if __name__ == "__main__":
    unittest.main()
