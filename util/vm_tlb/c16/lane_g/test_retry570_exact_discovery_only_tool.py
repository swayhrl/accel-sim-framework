#!/usr/bin/env python3
"""CPU-only source guards for Retry570 exact discovery-only NVBit tooling."""
from __future__ import annotations

import unittest
from pathlib import Path


SOURCE = (Path(__file__).resolve().parent / "retry570_exact_discovery_only_tool.cu").read_text(encoding="utf-8")


class ExactDiscoveryOnlyToolTests(unittest.TestCase):
    def test_all_slow_boundaries_flush_before_and_after_each_function(self) -> None:
        for marker in ("PRE_TARGET_NAME_LOOKUP_BEGIN", "PRE_TARGET_NAME_LOOKUP_END", "TARGET_CALLBACK_ENTER", "RELATED_FUNCTIONS_BEGIN", "RELATED_FUNCTIONS_END", "FUNCTION_BEGIN", "FUNCTION_END", "DISCOVERY_COMPLETE"):
            self.assertIn(marker, SOURCE)
        self.assertIn("fflush(stdout)", SOURCE)
        self.assertIn("nvbit_get_related_functions", SOURCE)
        self.assertIn("nvbit_get_instrs", SOURCE)

    def test_no_insertion_enable_or_trace_path_exists(self) -> None:
        self.assertNotIn("nvbit_insert_call", SOURCE)
        self.assertNotIn("nvbit_enable_instrumented", SOURCE)
        self.assertNotIn("cudaMalloc", SOURCE)
        self.assertIn("diagnostic_discovery_only=1", SOURCE)

    def test_deduplicates_handles_and_reports_reuse(self) -> None:
        for marker in ("FUNCTION_DUPLICATE_SKIPPED", "unique_handle_count", "unique_name_count", "TARGET_REUSE_CALLBACK"):
            self.assertIn(marker, SOURCE)
        self.assertIn("std::unordered_set<CUfunction> seen_handles", SOURCE)

    def test_pre_target_lookup_is_explicitly_separated_from_related_discovery(self) -> None:
        event = SOURCE[SOURCE.index("void nvbit_at_cuda_event"):]
        self.assertLess(event.index("PRE_TARGET_NAME_LOOKUP_BEGIN"), event.index("const std::string observed_mangled"))
        self.assertLess(event.index("PRE_TARGET_NAME_LOOKUP_END"), event.index("TARGET_CALLBACK_ENTER"))


if __name__ == "__main__":
    unittest.main()
