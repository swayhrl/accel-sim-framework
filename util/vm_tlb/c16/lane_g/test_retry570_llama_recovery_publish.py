from __future__ import annotations

import unittest
from pathlib import Path

SOURCE = (Path(__file__).parent / "retry570_llama_recovery_publish.py").read_text(encoding="utf-8")


class LlamaRecoveryPublishTests(unittest.TestCase):
    def test_keeps_large_prefill_zero_distinct_from_decode_memory(self) -> None:
        for token in ("STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED", "LARGE_INDEX_PREFILL_TARGET", "DECODE_INDEX_TARGET", "indexSelectSmallIndex", "[17, 18]"):
            self.assertIn(token, SOURCE)

    def test_requires_independent_map_and_all_actual_decode_forwards(self) -> None:
        for token in ("DECODE_NVBIT_STATIC_MAP_PASS", "DECODE_INDEXSELECT_CANDIDATE_OBSERVED", "range(2, 5)", "trace_list", "remote/local trace SHA closure differs"):
            self.assertIn(token, SOURCE)

    def test_manifest_validates_materialized_nonraw_payloads(self) -> None:
        for token in ("PUBLISH_MANIFEST_VALIDATION_PASS", "raw_trace_payloads_committed", "no_duplicate_path", "DECODE_SMALLINDEX_STATIC_MAP.tsv"):
            self.assertIn(token, SOURCE)


if __name__ == "__main__":
    unittest.main()
