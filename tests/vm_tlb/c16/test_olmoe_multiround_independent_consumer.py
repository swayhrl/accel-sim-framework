import importlib.util
import unittest
from pathlib import Path

import numpy as np


SCRIPT = Path(__file__).resolve().parents[3] / "util/vm_tlb/c16/olmoe_multiround_independent_consumer.py"
SPEC = importlib.util.spec_from_file_location("consumer", SCRIPT)
consumer = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(consumer)


class ConsumerTests(unittest.TestCase):
    def test_route_matrices_distinguish_ordered_and_unordered_equality(self):
        ordered = np.asarray(
            [
                [0, 1, 2, 3, 4, 5, 6, 7],
                [7, 6, 5, 4, 3, 2, 1, 0],
                [0, 1, 2, 3, 8, 9, 10, 11],
            ],
            dtype=np.int16,
        )
        intersection, jaccard, retention, exact, ordered_equal = consumer.route_matrices(ordered)
        self.assertEqual(intersection[0, 1], 8)
        self.assertEqual(jaccard[0, 1], 1.0)
        self.assertEqual(retention[0, 2], 0.5)
        self.assertTrue(exact[0, 1])
        self.assertFalse(ordered_equal[0, 1])

    def test_holm_adjustment_is_monotone_and_mapped_back(self):
        adjusted = consumer.holm_adjust({"a": 0.01, "b": 0.03, "c": 0.20})
        self.assertEqual(adjusted, {"a": 0.03, "b": 0.06, "c": 0.20})


if __name__ == "__main__":
    unittest.main()
