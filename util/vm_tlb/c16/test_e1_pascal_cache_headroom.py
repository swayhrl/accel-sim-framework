#!/usr/bin/env python3
import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).with_name("e1_pascal_cache_headroom.py")
SPEC = importlib.util.spec_from_loader(
    "e1_pascal_cache_headroom",
    SourceFileLoader("e1_pascal_cache_headroom", str(MODULE_PATH)))
PASCAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PASCAL)


class PascalHeadroomTest(unittest.TestCase):
    def test_cyclic_gap_footprint(self):
        gaps = [2, 3, 5]
        self.assertEqual(PASCAL.footprint(gaps, 0), 0)
        self.assertEqual(PASCAL.footprint(gaps, 2), 6)
        self.assertEqual(PASCAL.footprint(gaps, 4), 9)
        self.assertEqual(PASCAL.miss_gap_count(gaps, 2), 2)

    def test_characteristic_window(self):
        self.assertEqual(PASCAL.characteristic_window([384], 328), 328)
        self.assertEqual(PASCAL.characteristic_window([2, 3, 5], 6), 2)
        with self.assertRaises(PASCAL.ContractError):
            PASCAL.characteristic_window([4], 4)

    def test_aligned_ttl_and_lru_certificate(self):
        result = PASCAL.aligned_bound(612864, 16, 524288)
        self.assertEqual(result["TTL_misses_per_round"], 1)
        self.assertEqual(result["LRU_lower_misses_per_round"], 1)
        self.assertEqual(result["LRU_upper_misses_per_round"], 1)
        self.assertTrue(result["LRU_exact_under_certificate"])
        self.assertEqual(result["policy_miss_lower_bound_exact_fraction"],
                         "1417216/9805809")

    def test_fractional_residency_knapsack(self):
        misses, hits = PASCAL.policy_independent_bound(
            PASCAL.aligned_intervals(384, 16), 328)
        self.assertAlmostEqual(float(misses), 896 / 6129)
        self.assertAlmostEqual(float(hits + misses), 16.0)

    def test_manifest_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            pack = Path(directory)
            payload = pack / "payload"
            payload.write_text("ok")
            digest = PASCAL.sha256(payload)
            (pack / "SHA256SUMS").write_text(f"{digest}  payload\n")
            self.assertEqual(PASCAL.verify_manifest(pack), {"payload": digest})
            payload.write_text("drift")
            with self.assertRaises(PASCAL.ContractError):
                PASCAL.verify_manifest(pack)


if __name__ == "__main__":
    unittest.main()
