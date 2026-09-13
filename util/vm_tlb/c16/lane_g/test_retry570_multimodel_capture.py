from __future__ import annotations

import unittest
from pathlib import Path


SOURCE = (Path(__file__).parent / "retry570_multimodel_capture.py").read_text(encoding="utf-8")


class MultimodelFormalCaptureTests(unittest.TestCase):
    def test_parent_is_the_only_budget_lease_owner(self) -> None:
        self.assertEqual(SOURCE.count("with Lease("), 1)
        for token in ("write_parent_lease_start", "wrapper_owned_budget(args, ident)", "child_acquired_second_lease\": False"):
            self.assertIn(token, SOURCE)

    def test_capture_is_after_ready_and_live_measurement_marker(self) -> None:
        self.assertLess(SOURCE.index('"LANE_G_RUNTIME_READY"'), SOURCE.index("with MeasurementActive"))
        for token in ("wrapper_measurement_marker(args, ident)", "C16_G_MEASUREMENT_ACTIVE_MARKER", '"CAPTURE_BEGIN"', '"CAPTURE_END"', "prewarm emitted formal trace"):
            self.assertIn(token, SOURCE)

    def test_lifecycle_uses_exact_root_and_nvbit_static_index(self) -> None:
        for token in ("C16_EXACT_ROOT_FUNCTION_ONLY", "C16_USE_NVBIT_STATIC_INDEX", "INSTR_BEGIN", "DYNAMIC_KERNEL_RANGE", "index != 101", "index == 34"):
            self.assertIn(token, SOURCE)

    def test_decode_target_is_independent_from_largeindex_prefill_target(self) -> None:
        for token in ("TARGET_ROLES", "DECODE_INDEX_TARGET", "indexSelectSmallIndex", "index != 17", "every actual frozen decode forward"):
            self.assertIn(token, SOURCE)

    def test_frozen_workload_executes_all_decode_steps(self) -> None:
        for token in ("range(1, 4)", "len(generated) != 4", "S5_COMPLETE_DECODE", "phase_trace_summary", "logical_decode_coverage", "DECODE4", "cudaProfilerStart failed for DECODE"):
            self.assertIn(token, SOURCE)

    def test_formal_capture_has_external_process_group_cleanup(self) -> None:
        for token in ("start_new_session=True", "os.killpg(process.pid, signal.SIGTERM)", "os.killpg(process.pid, signal.SIGKILL)"):
            self.assertIn(token, SOURCE)


if __name__ == "__main__":
    unittest.main()
