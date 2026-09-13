#!/usr/bin/env python3
"""CPU-only contract tests for the C0--C4 first-kernel isolator."""
from __future__ import annotations

import unittest
from pathlib import Path


SOURCE = (Path(__file__).resolve().parent / "retry570_pytorch_stage_diagnostic.py").read_text(encoding="utf-8")


class PytorchStageDiagnosticTests(unittest.TestCase):
    def test_independent_c0_to_c4_cases_and_hard_limit_are_frozen(self) -> None:
        for testcase in (
            "C0_TORCH_CUDA_INIT", "C1_GPU_ALLOCATION", "C2_TENSOR_FILL_FIRST_KERNEL",
            "C3_ELEMENTWISE_FIRST_KERNEL", "C4_SMALL_GEMM_LIBRARY_KERNEL",
        ):
            self.assertIn(testcase, SOURCE)
        self.assertIn("WALL_LIMIT_SECONDS = 60", SOURCE)
        self.assertIn("SAMPLE_SECONDS = 5", SOURCE)

    def test_diagnostic_has_one_parent_lease_and_no_capture_or_model_path(self) -> None:
        self.assertIn("with BudgetLease", SOURCE)
        self.assertIn("capture=False", SOURCE)
        self.assertIn("NON_SCIENTIFIC_DIAGNOSTIC", SOURCE)
        self.assertNotIn("from_pretrained", SOURCE)
        self.assertNotIn("mem_trace", SOURCE)
        self.assertNotIn("NVBIT_LONG_WATCH", SOURCE)

    def test_read_only_stack_protocol_and_timing_contract_exist(self) -> None:
        for marker in ("/proc", "kernel_stack", "C16_NVBIT_TIMING"):
            self.assertIn(marker, SOURCE)
        self.assertIn("FIRST_CUDA_KERNEL_SUBMISSION_BEGIN", SOURCE)
        self.assertIn("FIRST_CUDA_KERNEL_COMPLETED", SOURCE)


if __name__ == "__main__":
    unittest.main()
