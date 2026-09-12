#!/usr/bin/env python3
"""Direct standard-library tests for C15 lane-B guards."""
import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[4] / "util/vm_tlb/c15/lane_b/c15_lane_b.py"
FIXTURE = Path(__file__).resolve().parents[4] / "docs/vm_tlb/chatgpt_handoff/c15_lowcost/fixtures/contract_examples.json"
SPEC = importlib.util.spec_from_file_location("c15_lane_b", MODULE)
lane_b = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(lane_b)


class LaneBContractTests(unittest.TestCase):
    def test_fixture_contracts(self):
        result = lane_b.self_tests(FIXTURE)
        self.assertEqual({row["status"] for row in result}, {"PASS"})
        self.assertEqual({row["test_id"] for row in result},
                         {"T00", "T01", "T06", "T07", "T08", "T09", "T10", "T14", "T15", "T20", "T21", "T23", "T24"})

    def test_capture_guard(self):
        with self.assertRaises(PermissionError):
            lane_b.guarded_operation("capture", False, lane_b.CAPTURE_LIMIT_B)
        with self.assertRaises(PermissionError):
            lane_b.guarded_operation("capture", True, lane_b.CAPTURE_LIMIT_B + 1)

    def test_c12_import_is_header_only(self):
        rows = lane_b.header_only_rows([{"roi": "prefill", "arm": "F0", "lseg": "NONE",
            "trace_sha256": "a" * 64, "kernel_markers": "692"}])
        self.assertEqual(rows[0]["catalog_origin"], "TRACE_HEADER_ONLY")
        self.assertEqual(rows[0]["duration_ns"], "NA")
        self.assertEqual(rows[0]["operator_class"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
