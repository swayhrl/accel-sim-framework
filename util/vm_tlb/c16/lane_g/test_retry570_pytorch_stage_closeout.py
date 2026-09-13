#!/usr/bin/env python3
"""Source-only guards for the bounded C0--C4 publication contract."""
from __future__ import annotations

import unittest
from pathlib import Path


SOURCE = (Path(__file__).resolve().parent / "retry570_pytorch_stage_closeout.py").read_text(encoding="utf-8")


class PytorchStageCloseoutTests(unittest.TestCase):
    def test_all_c0_to_c4_cases_and_non_scientific_scope_are_required(self) -> None:
        for item in ("C0_TORCH_CUDA_INIT", "C1_GPU_ALLOCATION", "C2_TENSOR_FILL_FIRST_KERNEL", "C3_ELEMENTWISE_FIRST_KERNEL", "C4_SMALL_GEMM_LIBRARY_KERNEL"):
            self.assertIn(item, SOURCE)
        self.assertIn("scientific_eligible\": False", SOURCE)
        self.assertIn("not_trace_not_model_not_c_target_not_timing", SOURCE.lower())

    def test_requires_hash_closed_remote_tree_and_rejects_timeout_as_success(self) -> None:
        self.assertIn("local payload fails remote existence/size/SHA closure", SOURCE)
        self.assertIn("receipt.get(\"status\") != \"COMPLETE\"", SOURCE)
        self.assertIn("rsync_checksum_dry_run", SOURCE)

    def test_boundary_classification_does_not_reopen_longwatch(self) -> None:
        self.assertIn("B_instrumentation_size_explosion", SOURCE)
        self.assertIn("EXISTING_ONE_SHOT_LONG_WATCH_REMAINS_CLOSED", SOURCE)
        self.assertIn("authorized_by_this_diagnostic\": False", SOURCE)


if __name__ == "__main__":
    unittest.main()
