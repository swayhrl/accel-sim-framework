#!/usr/bin/env python3
"""Tests for the FFN timeline patch application correction."""

import importlib.util
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "util/vm_tlb/c16/ffn_timeline_patch_application_correction.py"
SPEC = importlib.util.spec_from_file_location("ffn_patch_correction", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
PACK = ROOT / MODULE.PACK


class PatchApplicationCorrectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = MODULE.reproduce(ROOT)

    def test_authorized_gnu_result(self):
        self.assertEqual(self.receipt["base"]["base_source_sha256"], MODULE.BASE_SHA256)
        self.assertEqual(self.receipt["patch"]["patch_sha256"], MODULE.PATCH_SHA256)
        authorized = self.receipt["authorized_application"]
        self.assertEqual(authorized["application_tool"], "GNU patch")
        self.assertEqual(authorized["result_sha256"], MODULE.EXPECTED_GNU_SHA256)
        self.assertEqual(authorized["expected_result_sha256"], MODULE.EXPECTED_GNU_SHA256)
        self.assertEqual(authorized["status"], "PASS_EXACT")

    def test_git_apply_result_is_rejected(self):
        rejected = self.receipt["prohibited_application"]
        self.assertEqual(rejected["result_sha256"], MODULE.EXPECTED_GIT_SHA256)
        self.assertNotEqual(rejected["result_sha256"], MODULE.EXPECTED_GNU_SHA256)
        self.assertFalse(rejected["authorized"])
        self.assertEqual(rejected["syntax_validation"]["status"], "FAIL_AS_EXPECTED")

    def test_instrumentation_structure_and_tail(self):
        validation = self.receipt["authorized_application"]["instrumentation_validation"]
        self.assertEqual(validation["syntax"], "PASS")
        self.assertEqual(validation["tail"], "PASS_NO_APPENDED_BLOCK")
        self.assertTrue(all(validation["required_points"].values()))

    def test_scientific_contract_unchanged(self):
        current = (ROOT / MODULE.CONTRACT_PATH).read_bytes()
        historical = MODULE.git_show(ROOT, MODULE.AUTHORIZATION_COMMIT, MODULE.CONTRACT_PATH)
        self.assertEqual(current, historical)
        self.assertEqual(MODULE.sha256(current), MODULE.CONTRACT_SHA256)
        self.assertEqual(self.receipt["scientific_identity_change"], "NONE")
        self.assertEqual(self.receipt["instrumentation_change"], "NONE")

    def test_pack_checksums(self):
        published = json.loads((PACK / "PATCH_APPLICATION_RECEIPT.json").read_text())
        self.assertEqual(published, self.receipt)
        subprocess.run(["sha256sum", "-c", "SHA256SUMS"], cwd=PACK, check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
