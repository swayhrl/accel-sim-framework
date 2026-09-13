from __future__ import annotations

import unittest
from pathlib import Path


SOURCE = (Path(__file__).parent / "retry570_llama_decode_path_census.py").read_text(encoding="utf-8")


class LlamaDecodePathCensusTests(unittest.TestCase):
    def test_is_diagnostic_only_and_forbids_measurement_capture(self) -> None:
        for token in ("scientific_eligible_for_timing\": False", "no_nvbit_trace_or_instrumentation\": True", "CUDA_INJECTION64_PATH", "MEASUREMENT_ACTIVE", "torch.profiler.profile"):
            self.assertIn(token, SOURCE)

    def test_preserves_frozen_decode_semantics(self) -> None:
        for token in ("range(1, 4)", "len(generated) != 4", "PREFILL_DERIVED_GREEDY_TOKEN_NO_SEPARATE_CUDA_FORWARD", "EXPECTED_CHECKSUM"):
            self.assertIn(token, SOURCE)

    def test_distinguishes_large_prefill_zero_from_decode_dispatch(self) -> None:
        for token in ("STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED", "indexSelectLargeIndex", "indexSelectSmallIndex", "requires_independent_nvbit_static_map_before_decode_capture"):
            self.assertIn(token, SOURCE)


if __name__ == "__main__":
    unittest.main()
