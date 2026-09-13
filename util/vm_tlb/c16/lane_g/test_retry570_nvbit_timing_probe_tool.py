#!/usr/bin/env python3
"""CPU-only source guards for the diagnostic-only NVBit timing probe."""
from __future__ import annotations

import unittest
from pathlib import Path


SOURCE = (Path(__file__).resolve().parent / "retry570_nvbit_timing_probe_tool.cu").read_text(encoding="utf-8")


class NvbitTimingProbeToolTests(unittest.TestCase):
    def test_required_stage_markers_and_related_function_walk_exist(self) -> None:
        for marker in ("LAUNCH_CALLBACK_ENTER", "RELATED_FUNCTIONS_BEGIN", "GET_INSTRS_BEGIN", "INSERTION_BEGIN", "ENABLE_INSTRUMENTED_BEGIN", "CUDA_SYNCHRONIZE_END"):
            self.assertIn(marker, SOURCE)
        self.assertIn("nvbit_get_related_functions", SOURCE)
        self.assertIn("nvbit_get_instrs", SOURCE)
        self.assertIn("nvbit_enable_instrumented", SOURCE)

    def test_probe_has_no_trace_or_memory_record_producer(self) -> None:
        self.assertNotIn("cudaMalloc", SOURCE)
        self.assertNotIn("mem_trace", SOURCE)
        self.assertNotIn("C16_TARGETED_NVBIT", SOURCE)
        self.assertIn("one_instruction_per_function=1", SOURCE)


if __name__ == "__main__":
    unittest.main()
