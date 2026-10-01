#!/usr/bin/env python3
"""Tests for the merged gate/up strong-baseline guard."""

import importlib.util
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "util/vm_tlb/c16/merged_gate_up_strong_baseline_guard.py"
SPEC = importlib.util.spec_from_file_location("merged_guard", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
PACK = ROOT / MODULE.PACK


class MergedGateUpGuardTest(unittest.TestCase):
    def test_source_identity_and_anchors(self):
        source = MODULE.validate(ROOT, MODULE.VLLM_DEFAULT)
        self.assertEqual(len(source["files"]), 8)
        self.assertGreaterEqual(len(source["semantic_anchors"]), 9)

    def test_quantization_semantics(self):
        audit = json.loads((PACK / "QUANTIZATION_SEMANTICS_AUDIT.json").read_text())
        self.assertEqual(audit["status"], "SEMANTICALLY_MATCHED_MERGED_BASELINE_EXISTS")
        self.assertFalse(audit["merged_projection"]["requires_requantization"])
        self.assertTrue(audit["merged_projection"]["group_size_preserved"])
        self.assertTrue(audit["merged_projection"]["zero_point_preserved"])
        self.assertEqual(audit["merged_projection"]["total_logical_quant_bytes"], 70_547_456)
        self.assertEqual(audit["floating_point_output"]["bitwise_equivalence_across_backend"], "NOT_ASSUMED")

    def test_guard_and_contract_boundary(self):
        final = json.loads((PACK / "FINAL_DECISION.json").read_text())
        contract = json.loads((PACK / "LANE7_MERGED_GATE_UP_NATIVE_BASELINE_CONTRACT.json").read_text())
        self.assertEqual(final["decision"], "PLAIN_GATE_UP_CONCURRENCY_NOT_NOVEL_MECHANISM")
        self.assertTrue(final["merged_same_checkpoint_available"])
        self.assertFalse(final["strict_single_variable_ab_available"])
        self.assertTrue(final["two_stream_diagnostic_still_valid"])
        self.assertEqual(contract["status"], "QUALIFIED_STRONG_BASELINE_NOT_STRICT_SINGLE_VARIABLE_AB")
        self.assertIn("model re-quantization", contract["forbidden"])
        self.assertEqual(contract["execution"], "NOT_EXECUTED_BY_LANE6")

    def test_capability_matrix_columns(self):
        header = (PACK / "MERGED_GATE_UP_CAPABILITY_MATRIX.tsv").read_text().splitlines()[0].split("\t")
        self.assertEqual(header, ["capability", "CURRENT_AUTOAWQ", "TWO_STREAM_GATE_UP", "MERGED_GATE_UP_STRONG_BASELINE", "evidence_boundary"])

    def test_checksums(self):
        subprocess.run(["sha256sum", "-c", "SHA256SUMS"], cwd=PACK, check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
