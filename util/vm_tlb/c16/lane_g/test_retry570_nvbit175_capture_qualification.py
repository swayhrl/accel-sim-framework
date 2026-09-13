from __future__ import annotations
import unittest
from pathlib import Path

SOURCE = (Path(__file__).parent / "retry570_nvbit175_capture_qualification.py").read_text()

class Nvbit175CaptureQualificationTests(unittest.TestCase):
    def test_lifecycle_orders_ready_before_measurement_and_capture(self) -> None:
        self.assertLess(SOURCE.index('"LANE_G_RUNTIME_READY"'), SOURCE.index('with MeasurementActive'))
        for token in ("CAPTURE_BEGIN", "CAPTURE_END", "prewarm emitted a trace", "trace exists before Q1 capture arm"):
            self.assertIn(token, SOURCE)
    def test_bounded_external_cleanup_and_no_models(self) -> None:
        for token in ("TARGET_CAP_S, TERM_GRACE_S = 30, 2", "os.killpg(process.pid, signal.SIGTERM)", "os.killpg(process.pid, signal.SIGKILL)"):
            self.assertIn(token, SOURCE)
        for forbidden in ("AutoModelForCausalLM", "AutoAWQ", "Llama", "Qwen"):
            self.assertNotIn(forbidden, SOURCE)
    def test_trace_validation_requires_direct_q0_identity(self) -> None:
        for token in ("indexSelectLargeIndex", "len(matches) != 1", "traces[0][\"kernel_id\"]", "traces[0][\"kernel_name\"]"):
            self.assertIn(token, SOURCE)

if __name__ == "__main__": unittest.main()
