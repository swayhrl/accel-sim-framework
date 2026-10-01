#!/usr/bin/env python3
"""Tests for FFN two-stream correctness repair V2."""

import importlib.util
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "util/vm_tlb/c16/ffn_two_stream_correctness_repair_v2.py"
SPEC = importlib.util.spec_from_file_location("ffn_repair_v2", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
PACK = ROOT / MODULE.PACK_OUT


class FfnTwoStreamRepairV2Test(unittest.TestCase):
    def test_v1_scope_contamination(self):
        receipt = json.loads((PACK / "V1_SCOPE_CONTAMINATION_RECEIPT.json").read_text())
        self.assertEqual(receipt["status"], "PREFILL_SCOPE_CONTAMINATION_CONFIRMED")
        self.assertFalse(receipt["evidence"]["concurrent_forward_active_decode_guard_in_V1"])
        self.assertEqual(receipt["evidence"]["B1_observed_first_token"], 143907)
        self.assertTrue(receipt["classification_is_not_unique_low_level_cause"])

    def test_v2_source_qualification(self):
        qualification = MODULE.qualify_source(ROOT, PACK / MODULE.PATCH_NAME)
        self.assertEqual(qualification["base_runner_sha256"], MODULE.V1_RUNNER_SHA)
        self.assertEqual(qualification["patch_sha256"], MODULE.PATCH_SHA)
        self.assertEqual(qualification["result_runner_sha256"], MODULE.V2_RUNNER_SHA)
        self.assertTrue(all(qualification["checks"].values()))

    def test_autoawq_exact_wheel_and_unknown_binary(self):
        audit = MODULE.audit_autoawq(ROOT, MODULE.WHEEL_DEFAULT)
        self.assertEqual(audit["wheel_sha256"], MODULE.AUTOAWQ_WHEEL_SHA)
        self.assertEqual(audit["python_source"]["prefill_M2048"], "awq_ext.dequantize_weights_cuda(...) then torch.matmul")
        self.assertEqual(audit["actual_109_extension"]["awq_ext_binary_sha256"], "UNKNOWN")
        self.assertEqual(audit["actual_109_extension"]["dequantize_kernel_current_stream_binding"], "UNKNOWN")

    def test_canary_first_contract_and_v1_preservation(self):
        contract = json.loads((PACK / "LANE7_FFN_GATE_UP_CONCURRENCY_NATIVE_CONTRACT_V2.json").read_text())
        final = json.loads((PACK / "FINAL_DECISION.json").read_text())
        self.assertEqual(contract["status"], "AUTHORIZED_CANARY_FIRST")
        self.assertEqual(contract["stage_1_canary_only"]["runs"], ["1 x B0 lightweight NSYS cuda,nvtx", "1 x B1_V2 lightweight NSYS cuda,nvtx"])
        self.assertFalse(contract["stage_1_canary_only"]["formal_timing_before_pass"])
        self.assertEqual(contract["failure_after_repair"]["classification"], "CORRECTNESS_MISMATCH_AFTER_PREFILL_REPAIR")
        self.assertEqual(final["V1_failure_preserved"], "CORRECTNESS_MISMATCH_STOP")
        self.assertEqual(final["scientific_target_change"], "NONE")

    def test_checksums(self):
        subprocess.run(["sha256sum", "-c", "SHA256SUMS"], cwd=PACK, check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
