from __future__ import annotations

import json
import unittest
from pathlib import Path

PROFILE = json.loads((Path(__file__).parents[4] / "docs/vm_tlb/runtime_profiles/NVBIT_LANE_G_RTX3090_CUDA124_KNOWN_GOOD.json").read_text())
SOURCE = (Path(__file__).parent / "retry570_nvbit175_preflight.py").read_text()


class Nvbit175PreflightTests(unittest.TestCase):
    def test_profile_has_known_good_and_scoped_known_bad(self) -> None:
        self.assertEqual(PROFILE["profile_status"], "KNOWN_GOOD_FOR_MINIMAL_LANE_G_FIRST_KERNEL")
        self.assertEqual(PROFILE["nvbit"]["version"], "1.7.5")
        self.assertEqual(PROFILE["nvbit"]["cuda_module_loading"], "EAGER")
        self.assertEqual(PROFILE["known_bad_for_this_lane"]["nvbit_version"], "1.8")
        self.assertIn("Nvbit::module_loaded", PROFILE["known_bad_for_this_lane"]["hot_path"])

    def test_preflight_is_diagnostic_and_fail_closed(self) -> None:
        for required in ("CAPTURE_ALLOWED", "NVDISASM_PATH", "CHILD_PATH", "STALE_GPU_PROCESS", "MEASUREMENT_ACTIVE"):
            self.assertIn(required, SOURCE)
        for forbidden in ("apt-get", "pip install", "curl", "wget", "os.system"):
            self.assertNotIn(forbidden, SOURCE)


if __name__ == "__main__":
    unittest.main()
