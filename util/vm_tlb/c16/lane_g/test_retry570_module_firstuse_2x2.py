#!/usr/bin/env python3
"""CPU-only contracts for the bounded module-first-use 2x2 diagnostic."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from retry570_module_firstuse_2x2 import EXACT_CANDIDATE, WALL_LIMIT_SECONDS, analyze  # noqa: E402


SOURCE = (LANE / "retry570_module_firstuse_2x2.py").read_text(encoding="utf-8")
RAW_TOOL = (LANE / "retry570_callback_census_raw_tool.cu").read_text(encoding="utf-8")
EMPTY_TOOL = (LANE / "retry570_empty_callback_dispatch_tool.cu").read_text(encoding="utf-8")
DEBUG_TOOL = (LANE / "retry570_callback_census_debug_tool.cu").read_text(encoding="utf-8")
BUILD = (LANE / "retry570_build_callback_tool_variant.sh").read_text(encoding="utf-8")


class ModuleFirstUse2x2Tests(unittest.TestCase):
    def test_callback_only_contract_forbids_discovery_insertion_enable_sync_trace_and_capture(self) -> None:
        self.assertIn("NVBIT_CALLBACK_CENSUS_ONLY", SOURCE)
        self.assertIn("CALLBACK_CENSUS_ONLY", SOURCE)
        self.assertIn("torch.index_select", SOURCE)
        self.assertEqual(WALL_LIMIT_SECONDS, 25)
        for forbidden in (
            "nvbit_get_related_functions", "nvbit_get_instrs", "nvbit_insert_call", "nvbit_enable_instrumented",
            "torch.cuda.synchronize()", "trace_generated\": True", "capture=True",
        ):
            self.assertNotIn(forbidden, SOURCE)

    def test_exact_input_and_markers_are_identical_single_operation_contract(self) -> None:
        self.assertEqual(EXACT_CANDIDATE["candidate_id"], "R2_D0_I64_A")
        expected = [
            "PROCESS_START", "BEFORE_TORCH_ARANGE_INDEX", "EXACT_TARGET_SUBMISSION_BEGIN", "EXACT_OPERATION_RETURN",
        ]
        for marker in expected:
            self.assertIn(marker, SOURCE)
        self.assertIn("PR_SET_PTRACER", SOURCE)
        self.assertIn("PTRACE_ATTACH_AUTHORIZED", SOURCE)
        self.assertIn('anchor_event != "EXACT_TARGET_SUBMISSION_BEGIN"', SOURCE)
        self.assertIn("do not reset its clock", SOURCE)

    def test_callback_timeline_pairs_library_calls_and_keeps_native_unobservable(self) -> None:
        with TemporaryDirectory() as temporary:
            log = Path(temporary) / "out.log"
            log.write_text("\n".join((
                "C16_CALLBACK_CENSUS_TOOL_READY mode=CALLBACK_CENSUS_ONLY introspection=0 instrumentation=0 trace=0",
                "C16_MODULE_FIRST_USE_APP ts_ns=100 event=PROCESS_START",
                "C16_MODULE_FIRST_USE_APP ts_ns=110 event=BEFORE_TORCH_ARANGE_INDEX",
                "C16_MODULE_FIRST_USE_APP ts_ns=120 event=EXACT_TARGET_SUBMISSION_BEGIN",
                "C16_CALLBACK_CENSUS ts_ns=121 seq=1 pid=1 tid=1 is_exit=0 cbid=681 callback=cuLibraryLoadData",
                "C16_CALLBACK_CENSUS ts_ns=131 seq=2 pid=1 tid=1 is_exit=1 cbid=681 callback=cuLibraryLoadData",
                "C16_CALLBACK_CENSUS ts_ns=132 seq=3 pid=1 tid=1 is_exit=0 cbid=682 callback=cuLibraryGetModule",
            )) + "\n", encoding="utf-8")
            analysis = analyze(log, "NVBIT_CALLBACK_CENSUS_ONLY")
            self.assertEqual(analysis["timeline"]["cuLibraryLoadData"][0]["elapsed_ns"], 10)
            self.assertIsNone(analysis["timeline"]["cuLibraryGetModule"][0]["exit_ts_ns"])
            native = analyze(log, "NATIVE")
            self.assertEqual(native["timeline"]["cuLibraryLoadData"], "NOT_OBSERVABLE_WITHOUT_NVBIT_CALLBACK_STREAM")

    def test_debug_variant_declares_vendor_map_only_for_gdb_type_information(self) -> None:
        self.assertIn("extern NvbitElfModuleMap elfModuleHashMap", DEBUG_TOOL)
        self.assertIn("neither reads nor writes it", DEBUG_TOOL)
        self.assertIn("-g -Og", BUILD)
        self.assertIn("thread apply all bt full", SOURCE)
        self.assertIn("elfModuleHashMap.size()", SOURCE)
        self.assertIn('"maps": _run_text_safe', SOURCE)

    def test_raw_callback_body_has_only_fixed_pod_ring_operations(self) -> None:
        body = RAW_TOOL[RAW_TOOL.index("void nvbit_at_cuda_event"):RAW_TOOL.index("void nvbit_at_term")]
        for forbidden in (
            "std::string", "std::vector", "std::unordered_map", "new", "delete", "malloc", "free",
            "printf", "fprintf", "nvbit_get_", "nvbit_insert", "nvbit_enable", "synchronize",
        ):
            self.assertNotIn(forbidden, body)
        for required in ("RawEvent", "events[sequence]", "callback_depth", "reentrant_callback_count"):
            self.assertIn(required, body)

    def test_empty_callback_returns_without_user_bookkeeping(self) -> None:
        body = EMPTY_TOOL[EMPTY_TOOL.index("void nvbit_at_cuda_event"):EMPTY_TOOL.index("void nvbit_at_term")]
        self.assertIn("return;", body)
        self.assertNotIn("nvbit_get_", body)
        self.assertNotIn("std::", body)


if __name__ == "__main__":
    unittest.main()
