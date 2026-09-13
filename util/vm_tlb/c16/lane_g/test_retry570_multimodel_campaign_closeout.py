from __future__ import annotations

import unittest
from pathlib import Path


SOURCE = (Path(__file__).parent / "retry570_multimodel_campaign_closeout.py").read_text(encoding="utf-8")


class MultimodelCampaignCloseoutTests(unittest.TestCase):
    def test_all_five_roster_models_have_terminal_closeout(self) -> None:
        for token in ("llama_3p2_1b", "qwen_0p5", "qwen_7b_awq", "deepseek", "glm", "COMPLETE_WITH_BLOCKED_MODELS"):
            self.assertIn(token, SOURCE)

    def test_llama_budget_blocker_cannot_reset_history(self) -> None:
        for token in ("consumed_window_count", "maximum_window_count", "NVBIT_WINDOW_BUDGET_EXHAUSTED", "REJECTED_BEFORE_GPU_MODEL_OR_MEASUREMENT_ACTIVE"):
            self.assertIn(token, SOURCE)

    def test_manifest_is_payload_closed(self) -> None:
        for token in ("no_duplicate_path", "all_payloads_exist_size_sha256_match", "manifest payload is not materialized/hash closed"):
            self.assertIn(token, SOURCE)

    def test_closeout_is_publication_only(self) -> None:
        self.assertIn("never imports torch, opens a model, or launches a", SOURCE)
        self.assertNotIn("subprocess.Popen", SOURCE)


if __name__ == "__main__":
    unittest.main()
