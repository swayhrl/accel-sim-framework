#!/usr/bin/env python3
"""Tests for the C16 exploration-wave terminal synthesis."""

import csv
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "util/vm_tlb/c16/c16_exploration_wave_terminal_synthesis.py"
SPEC = importlib.util.spec_from_file_location("c16_terminal", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
PACK = ROOT / MODULE.PACK


class C16TerminalSynthesisTest(unittest.TestCase):
    def test_authority_chain(self):
        verified = MODULE.verify(ROOT)
        self.assertEqual(len(verified["receipts"]), 21)
        self.assertEqual(verified["two_v2"]["overlap"]["overlap_count"], 10)

    def test_final_terminal_state(self):
        final = json.loads((PACK / "FINAL_PROJECT_STATE.json").read_text())
        self.assertEqual(final["decision"], "NO_CURRENT_C16_MECHANISM_READY_FOR_PROMOTION")
        self.assertEqual(final["active_promotion_candidate_count"], 0)
        self.assertEqual(final["future_question_parking_lot_count"], 1)
        self.assertFalse(final["new_experiment_authorized"])
        self.assertFalse(final["gpu_used"])

    def test_two_stream_causal_boundary(self):
        final = json.loads((PACK / "FINAL_PROJECT_STATE.json").read_text())
        v2 = final["two_stream_v2"]
        self.assertAlmostEqual(v2["B0_median_ms"], 74.2159194946289)
        self.assertAlmostEqual(v2["B1_median_ms"], 81.43391799926758)
        self.assertAlmostEqual(v2["speedup"], 0.911363732926327)
        self.assertIn("not proven to explain entire slowdown", v2["causal_boundary"])
        self.assertIn("stream/event coordination", v2["causal_boundary"])

    def test_ledger_categories_and_closed_state(self):
        with (PACK / "C16_ACCEPTED_EVIDENCE_LEDGER.tsv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        self.assertGreaterEqual(len(rows), 19)
        self.assertTrue(any(row["evidence_class"] == "STRONG_SOFTWARE_BASELINE" for row in rows))
        self.assertTrue(any(row["evidence_class"] == "ORACLE_HEADROOM" for row in rows))
        self.assertTrue(any("CLOSED" in row["mechanism_state"] for row in rows))

    def test_handoff_context_updated(self):
        context = ROOT / "docs/vm_tlb/chatgpt_handoff/c16/AI_WORKLOAD_EXPLORATION_CURRENT_STATE.md"
        root_context = ROOT / "docs/vm_tlb/chatgpt_handoff/CURRENT_STATE.md"
        self.assertIn("NO_CURRENT_C16_MECHANISM_READY_FOR_PROMOTION", context.read_text())
        self.assertIn("AI_WORKLOAD_EXPLORATION_CURRENT_STATE.md", root_context.read_text())

    def test_checksums(self):
        subprocess.run(["sha256sum", "-c", "SHA256SUMS"], cwd=PACK, check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
