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
        for token in ("indexSelectLargeIndex", "len(matches) != 1", "traces[0][\"kernel_id\"]", "traces[0][\"kernel_name\"]", "plan.get(\"target\") != args.target"):
            self.assertIn(token, SOURCE)

    def test_q1_requires_clean_q0_and_fresh_arm(self) -> None:
        for token in ("Q1 requires a non-scientific LANE_G_RUNTIME_READY Q0 receipt", "Q1 rejects a Q0 receipt with prewarm trace or measurement activity", "Q1 arm path must be absent before parent creates it"):
            self.assertIn(token, SOURCE)

    def test_child_receives_serialized_target_not_a_python_dict(self) -> None:
        self.assertIn('json.dumps(args.target, sort_keys=True, separators=(",", ":"))', SOURCE)

if __name__ == "__main__": unittest.main()
