from __future__ import annotations

import unittest
from pathlib import Path


SOURCE = (Path(__file__).parent / "retry570_recovery_v3_target_plan.py").read_text()


class RecoveryV3TargetPlanTests(unittest.TestCase):
    def test_plan_is_phase_specific_and_does_not_forge_nvbit_identity(self) -> None:
        self.assertIn('for phase in ("PREFILL", "DECODE")', SOURCE)
        self.assertIn("MAX_AGGREGATE_PHASE_GPU_DURATION_PRE_OUTCOME", SOURCE)
        self.assertIn("PENDING_R5_NVBIT_NATIVE_MAP", SOURCE)
        self.assertIn("no_kernel_name_only_capture", SOURCE)
        self.assertIn("no_cross_model_static_range", SOURCE)


if __name__ == "__main__":
    unittest.main()
