#!/usr/bin/env python3
"""CPU-only evidence-marker guard for the official NVBit smoke."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from retry570_nvbit_official_smoke import ALLOWED_NVBIT_VERSIONS, REQUIRED_MARKERS, official_evidence  # noqa: E402


class OfficialNvbitSmokeTests(unittest.TestCase):
    def test_version_differential_is_explicit_and_bounded(self) -> None:
        self.assertEqual(ALLOWED_NVBIT_VERSIONS, {"1.8", "1.7.5", "1.7.7.3"})

    def test_requires_banner_kernel_and_test_app_terminal_evidence(self) -> None:
        text = "NVBit (NVidia Binary Instrumentation Tool)\nkernel 0 - vecAdd\nFinal sum = 1.0"
        self.assertTrue(all(official_evidence(text).values()))
        self.assertEqual(len(REQUIRED_MARKERS), 3)
        self.assertFalse(all(official_evidence("kernel 0 - only").values()))


if __name__ == "__main__":
    unittest.main()
