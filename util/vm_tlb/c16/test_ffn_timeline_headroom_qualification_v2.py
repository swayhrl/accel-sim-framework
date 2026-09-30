#!/usr/bin/env python3
"""Tests for the CPU-only FFN timeline headroom consumer."""

import importlib.util
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "util/vm_tlb/c16/ffn_timeline_headroom_qualification_v2.py"
SPEC = importlib.util.spec_from_file_location("ffn_headroom_v2", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
PACK = ROOT / MODULE.PACK_OUT


class FfnTimelineHeadroomV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.computed = MODULE.compute(ROOT)

    def test_authority_and_union_close(self):
        self.assertEqual(self.computed["decode_wall_ns"], MODULE.EXPECTED_DECODE_WALL_NS)
        self.assertEqual(self.computed["union_ns"], MODULE.EXPECTED_WINDOW_UNION_NS)
        self.assertEqual(self.computed["overlap_count"], 0)
        self.assertEqual(len(self.computed["records"]), 112)
        self.assertEqual(self.computed["authority"]["manifest_count"], 28)
        self.assertGreater(self.computed["decode_wall_ns"], self.computed["union_ns"])

    def test_stage_and_physical_accounting(self):
        self.assertTrue(all(row["unattributed_ns"] == sum(row[f"{gap}_ns"] for gap in MODULE.GAPS) for row in self.computed["records"]))
        self.assertEqual(self.computed["handoff_bytes_per_window"], 303_104)
        self.assertEqual(self.computed["handoff_bytes_all"], 33_947_648)
        self.assertGreater(self.computed["elementwise_ns"], 0)

    def test_f2a_and_f2b_decisions(self):
        f2a = json.loads((PACK / "FFN_F2A_GATE_UP_CONCURRENCY_CEILING.json").read_text())
        f2b = json.loads((PACK / "FFN_F2B_TILE_PIPELINE_ANALYSIS.json").read_text())
        self.assertEqual(f2a["decision"], "F2A_QUALIFIED_FOR_NATIVE_CONCURRENCY_DIAGNOSTIC")
        self.assertGreaterEqual(f2a["gap_preserving_oracle"]["whole_decode_time_reduction_fraction"], 0.05)
        self.assertEqual(f2b["status"], "TILE_PIPELINE_ORACLE_NOT_WELL_DEFINED")
        self.assertIsNone(f2b["perfect_tile_pipeline_ceiling"])

    def test_no_gpu_and_contract_bounds(self):
        validation = json.loads((PACK / "FFN_TIMELINE_CONSUMER_VALIDATION.json").read_text())
        contract = json.loads((PACK / "LANE7_FFN_GATE_UP_CONCURRENCY_NATIVE_CONTRACT.json").read_text())
        self.assertFalse(validation["gpu_used_by_consumer"])
        self.assertFalse(validation["cuda_initialized_by_consumer"])
        self.assertFalse(validation["gpu_lock_used_by_consumer"])
        self.assertEqual(contract["measurement"]["samples"], {"B0": 24, "B1": 24, "total": 48})
        self.assertIn("NCU in first step", contract["forbidden_changes"])

    def test_pack_checksums(self):
        subprocess.run(["sha256sum", "-c", "SHA256SUMS"], cwd=PACK, check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
