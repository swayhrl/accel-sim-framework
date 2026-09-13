"""Source-contract tests for the NVBit profiler/target intersection gate.

The CUDA tool is compiled only on the frozen remote NVBit host.  These tests
make the safety contract reviewable before that bounded remote smoke: no
selected kernel means no discovery/insertion/trace metadata; a selected
kernel must satisfy both the profiler ROI and the exact selector.
"""
from __future__ import annotations

import unittest
from pathlib import Path


SOURCE = (Path(__file__).parents[3] / "tracer_nvbit" / "tracer_tool" / "tracer_tool.cu").read_text(encoding="utf-8")


class ProfilerTargetGateTests(unittest.TestCase):
    def test_profiler_roi_and_exact_selector_are_intersected(self) -> None:
        self.assertIn("bool trace_this_kernel = active_region && kernel_matches_selector;", SOURCE)
        self.assertIn("DYNAMIC_KERNEL_RANGE is always intersected with", SOURCE)

    def test_unselected_or_prewarm_kernel_returns_before_discovery(self) -> None:
        early = SOURCE.index("if (!trace_this_kernel)")
        discovery = SOURCE.index("instrument_function_if_needed(ctx, func);")
        self.assertLess(early, discovery)
        for token in ("No NVBit discovery, insertion, metadata", "ctx_kernelid[ctx]++", "return;"):
            self.assertIn(token, SOURCE[early:discovery])

    def test_exact_root_and_native_static_index_are_explicit_opt_ins(self) -> None:
        self.assertIn('C16_EXACT_ROOT_FUNCTION_ONLY', SOURCE)
        self.assertIn('C16_USE_NVBIT_STATIC_INDEX', SOURCE)
        self.assertIn("use_nvbit_static_index ? (uint32_t)instr->getIdx() : cnt", SOURCE)
        self.assertIn("if (exact_root_function_only)", SOURCE)

    def test_leave_path_does_not_flush_untraced_kernel(self) -> None:
        leave = SOURCE.index("static void leave_kernel_launch")
        sync = SOURCE.index("cudaDeviceSynchronize();", leave)
        self.assertLess(SOURCE.index("if (!ctx_trace_this_kernel[ctx])", leave), sync)


if __name__ == "__main__":
    unittest.main()
