"""No-network tests for the C16-only hash-closed NVBit bootstrap plan."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from c16_nvbit_bootstrap import NVBIT_SHA256, NVBIT_VERSION, plan  # noqa: E402


class NvbitBootstrapTests(unittest.TestCase):
    def test_plan_is_pinned_and_non_destructive(self) -> None:
        value = plan(Path('/framework'), Path('/work'), Path('/cuda-12.4'))
        self.assertEqual(value['nvbit']['version'], NVBIT_VERSION)
        self.assertEqual(value['nvbit']['sha256'], NVBIT_SHA256)
        self.assertEqual(value['architecture'], 'sm_86')
        self.assertTrue(value['non_destructive'])
        self.assertTrue(value['nvcc'].endswith('/cuda-12.4/bin/nvcc'))


if __name__ == '__main__':
    unittest.main()
