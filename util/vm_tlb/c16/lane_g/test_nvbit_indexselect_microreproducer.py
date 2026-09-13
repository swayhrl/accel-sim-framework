#!/usr/bin/env python3
"""CPU-only structural guards for the bounded index_select microreproducer."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from nvbit_indexselect_microreproducer import CANDIDATES, DIAGNOSTIC_DEPLOYMENT  # noqa: E402


class IndexSelectMicroreproducerTests(unittest.TestCase):
    def test_candidate_search_is_finite_and_rank_dimension_closed(self) -> None:
        self.assertEqual(DIAGNOSTIC_DEPLOYMENT, "c16_retry570_indexselect_microreproducer")
        self.assertGreater(len(CANDIDATES), 0)
        self.assertLessEqual(len(CANDIDATES), 12)
        for candidate in CANDIDATES:
            shape = candidate["shape"]
            self.assertIsInstance(shape, tuple)
            self.assertIn(len(shape), (2, 3))
            self.assertGreaterEqual(candidate["dim"], 0)
            self.assertLess(candidate["dim"], len(shape))
            self.assertIn(candidate["index_dtype"], ("int32", "int64"))


if __name__ == "__main__":
    unittest.main()
