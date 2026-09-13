from __future__ import annotations
import unittest
from pathlib import Path

SOURCE = (Path(__file__).parent / "retry570_multimodel_campaign.py").read_text()

class CampaignInventoryTests(unittest.TestCase):
    def test_roster_and_no_substitution_contract_are_explicit(self) -> None:
        for token in ("llama_3p2_1b", "qwen_0p5", "qwen_7b_awq", "deepseek", "glm", "BLOCKED_ASSET_UNAVAILABLE"):
            self.assertIn(token, SOURCE)

    def test_inventory_is_metadata_only(self) -> None:
        for token in ("repo_root()", "torch_imported\": False", "weights_loaded\": False", "network_download\": False", "gpu_work\": False"):
            self.assertIn(token, SOURCE)

    def test_lama_requires_exact_p0_and_s0_binding(self) -> None:
        for token in ("C16_GPU_PACKAGE_P0", "4e20de362430cd3b72f300e6b0f18e50e7166e08", "S0/B1/T128/Decode4/TEXT"):
            self.assertIn(token, SOURCE)

if __name__ == "__main__": unittest.main()
