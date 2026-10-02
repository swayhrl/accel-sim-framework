#!/usr/bin/env python3
"""Small CPU-only fail-closed checks for independent raw computations."""

import unittest

from consume import cache_signature, compare_rows, sample_stats


class IndependentConsumerTests(unittest.TestCase):
    def test_median_mad_are_from_formal_samples(self):
        rows = [{"role": "FORMAL", "timing_role": "SCIENCE_FORMAL", "request_gpu_elapsed_ms": value}
                for value in (1.0, 2.0, 3.0, 4.0, 5.0)]
        result = sample_stats(rows)
        self.assertEqual((result["median_ms"], result["mad_ms"], result["min_ms"], result["max_ms"]), (3.0, 1.0, 1.0, 5.0))
        rows[0]["role"] = "WARMUP"
        with self.assertRaises(AssertionError):
            sample_stats(rows)

    def test_token_and_logprob_fail_closed(self):
        base = {"source_id": "TRAIN_A_DISCOVERY_00", "batch_row": 0,
                "prompt_token_count": 512, "tokens": list(range(32)), "sampled_logprobs": [-1.0] * 32}
        self.assertEqual(compare_rows([base], [dict(base)], ["TRAIN_A_DISCOVERY_00"])[0], 32)
        altered = dict(base)
        altered["tokens"] = list(range(31)) + [99]
        with self.assertRaises(AssertionError):
            compare_rows([base], [altered], ["TRAIN_A_DISCOVERY_00"])
        altered = dict(base)
        altered["sampled_logprobs"] = [-1.0] * 31 + [-1.2]
        with self.assertRaises(AssertionError):
            compare_rows([base], [altered], ["TRAIN_A_DISCOVERY_00"])

    def test_cache_signature_includes_file_identity(self):
        source = {"path": "/cache/a", "actual_file_count": 1, "actual_sha256": "a" * 64,
                  "files": [{"relative_path": "model", "sha256": "b" * 64, "size_bytes": 12}]}
        signature = cache_signature(source)
        self.assertEqual(signature["files"], {"model": ("b" * 64, 12)})
        source["files"][0]["size_bytes"] = 13
        self.assertNotEqual(signature, cache_signature(source))


if __name__ == "__main__":
    unittest.main()
