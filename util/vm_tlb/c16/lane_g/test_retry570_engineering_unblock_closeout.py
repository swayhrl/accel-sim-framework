from __future__ import annotations

import unittest
from pathlib import Path

SOURCE = (Path(__file__).parent / "retry570_engineering_unblock_closeout.py").read_text(encoding="utf-8")


class EngineeringUnblockCloseoutTests(unittest.TestCase):
    def test_scientific_boundary_and_decision_are_explicit(self) -> None:
        for required in (
            "NVBIT_VERSION_SENSITIVE_CORE_PATH",
            "NOT_DETERMINED_V1_8_NEVER_REACHED_READY",
            "PIN_NVBIT_1_7_5_EAGER_PREWARM_THEN_READY_THEN_MEASUREMENT_ACTIVE",
            "scientific_eligible\": False",
            "remote_only_required_artifact_count\": 0",
        ):
            self.assertIn(required, SOURCE)

    def test_manifest_validates_materialization_size_sha_and_duplicates(self) -> None:
        for required in ("payload.is_file()", "payload.stat().st_size", "sha256_file(payload)", "path in seen"):
            self.assertIn(required, SOURCE)

    def test_no_model_or_capture_execution_is_present(self) -> None:
        for forbidden in ("AutoModelForCausalLM", "AutoAWQ", "nvbit_insert_call", "subprocess.Popen", "CUDA_INJECTION64_PATH"):
            self.assertNotIn(forbidden, SOURCE)


if __name__ == "__main__":
    unittest.main()
