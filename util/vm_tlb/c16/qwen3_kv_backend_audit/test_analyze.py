#!/usr/bin/env python3
import unittest

from analyze import interval_role, nearest_rank, ranges_from_context


class ConsumerUnitTests(unittest.TestCase):
    def setUp(self):
        self.context = {
            "same_process_only": True,
            "ranges": [
                {"class": "KV_POST_UPDATE_K", "address_start_hex": "0x1000", "storage_bytes": 16},
                {"class": "KV_DERIVED_REPEAT_K", "address_start_hex": "0x2000", "storage_bytes": 64},
            ],
        }
        self.ranges = ranges_from_context(self.context)

    def test_interval_join_and_boundary(self):
        self.assertEqual(interval_role(0x1000, 2, self.ranges), "KV_POST_UPDATE_K")
        self.assertEqual(interval_role(0x2002, 2, self.ranges), "KV_DERIVED_REPEAT_K")
        self.assertEqual(interval_role(0x100F, 2, self.ranges), "NEITHER_OR_AMBIGUOUS")
        self.assertEqual(interval_role(0x3000, 2, self.ranges), "NEITHER_OR_AMBIGUOUS")

    def test_nearest_rank(self):
        self.assertEqual(nearest_rank([1, 2, 3, 4])["median"], 2)
        self.assertEqual(nearest_rank([1, 2, 3, 4])["p75"], 3)

    def test_context_requires_same_process(self):
        invalid = dict(self.context)
        invalid["same_process_only"] = False
        with self.assertRaises(ValueError):
            ranges_from_context(invalid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
