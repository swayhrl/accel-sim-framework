#!/usr/bin/env python3
"""CPU-only contracts for the no-op callback-census diagnostic."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from retry570_callback_census_diagnostic import CURRENT_MATCHER_LAUNCH_APIS, analyze  # noqa: E402


TOOL = (LANE / "retry570_callback_census_tool.cu").read_text(encoding="utf-8")
RUNNER = (LANE / "retry570_callback_census_diagnostic.py").read_text(encoding="utf-8")
BUILD = (LANE / "retry570_build_callback_census_tool.sh").read_text(encoding="utf-8")


class CallbackCensusTests(unittest.TestCase):
    def test_tool_logs_all_callbacks_without_nvbit_introspection_or_instrumentation(self) -> None:
        for fragment in ("nvbit_at_cuda_event", "is_exit", "cbid", "event_name", "std::fflush(stdout)", "CALLBACK_CENSUS_ONLY"):
            self.assertIn(fragment, TOOL)
        for forbidden in ("nvbit_get_related_functions", "nvbit_get_instrs", "nvbit_insert_call", "nvbit_enable_instrumented", "cudaDeviceSynchronize"):
            self.assertNotIn(forbidden, TOOL)
        self.assertIn("-Wl,--whole-archive -lnvbit -Wl,--no-whole-archive", BUILD)

    def test_application_marker_is_directly_before_torch_index_select_and_not_claimed_as_launch(self) -> None:
        self.assertIn('_app_event(stage_path, "EXACT_TARGET_SUBMISSION_BEGIN", round_id=round_id)\n    output = torch.index_select', RUNNER)
        self.assertIn("application-operation boundary, not a CUDA launch proof", RUNNER)
        for fragment in ("BEFORE_EXACT_OPERATION", "EXACT_OPERATION_RETURN", "BEFORE_SYNC", "AFTER_SYNC", "cuModuleGetLoadingMode"):
            self.assertIn(fragment, RUNNER)

    def test_current_matcher_audit_lists_missing_legacy_async_variant(self) -> None:
        self.assertIn("cuLaunchGridAsync", "".join(CURRENT_MATCHER_LAUNCH_APIS) + " cuLaunchGridAsync")
        self.assertNotIn("cuLaunchGridAsync", CURRENT_MATCHER_LAUNCH_APIS)

    def test_analyzer_identifies_unmatched_driver_entry(self) -> None:
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as temporary:
            log = Path(temporary) / "stdout.log"
            log.write_text("\n".join((
                "C16_CALLBACK_CENSUS_TOOL_READY mode=CALLBACK_CENSUS_ONLY introspection=0 instrumentation=0 trace=0",
                "C16_CALLBACK_CENSUS_APP ts_ns=100 event=EXACT_TARGET_SUBMISSION_BEGIN",
                "C16_CALLBACK_CENSUS ts_ns=101 seq=1 pid=1 tid=1 is_exit=0 cbid=117 callback=cuLaunchGridAsync",
            )) + "\n", encoding="utf-8")
            self.assertEqual(analyze(log)["classification"], "CUDA_DRIVER_API_STALL_IDENTIFIED:cuLaunchGridAsync")

    def test_analyzer_fail_closes_when_static_nvbit_core_was_not_linked(self) -> None:
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as temporary:
            log = Path(temporary) / "stdout.log"
            log.write_text("C16_CALLBACK_CENSUS_APP ts_ns=100 event=EXACT_TARGET_SUBMISSION_BEGIN\n", encoding="utf-8")
            self.assertEqual(analyze(log)["classification"], "HARNESS_FAIL_CLOSED_NVBIT_TOOL_NOT_LOADED")


if __name__ == "__main__":
    unittest.main()
