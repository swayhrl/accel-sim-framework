from __future__ import annotations

import unittest
from pathlib import Path

SOURCE = (Path(__file__).parent / "retry570_post_llama_phase_a_inventory.py").read_text(encoding="utf-8")


class PostLlamaPhaseAInventoryTests(unittest.TestCase):
    def test_is_metadata_only_and_bounded_to_authorized_roots(self) -> None:
        for token in ("No model, torch, GPU", "--root", "os.walk(root", "followlinks=False", "no_gpu_or_model_execution\": True"):
            self.assertIn(token, SOURCE)

    def test_requires_manifest_closed_qwen_and_explicit_glm_deepseek_blockers(self) -> None:
        for token in ("C16_GPU_PACKAGE_P1", "C16_GPU_PACKAGE_P3", "BLOCKED_IDENTITY_UNRESOLVED_REQUIRES_USER", "No C16 exact tokenizer/input/runtime package", "generic GLM is not an identity"):
            self.assertIn(token, SOURCE)

    def test_network_boundary_must_be_retained_and_current(self) -> None:
        for token in ("p3_attempt_stderr", "Network is unreachable", "upstream reachability changed", "IDENTITY_RECOVERED_ASSET_MISSING"):
            self.assertIn(token, SOURCE)


if __name__ == "__main__": unittest.main()
