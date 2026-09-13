#!/usr/bin/env python3
"""CPU-only contract tests for the bounded exact-target discovery harness."""
from __future__ import annotations

import unittest
from pathlib import Path


SOURCE = (Path(__file__).resolve().parent / "retry570_exact_discovery_diagnostic.py").read_text(encoding="utf-8")


class ExactDiscoveryDiagnosticTests(unittest.TestCase):
    def test_frozen_exact_candidate_and_two_same_process_operations(self) -> None:
        for fragment in ("R2_D0_I64_A", "(64, 32)", '"index_count": 64', "EXACT_TARGET_MANGLED", "_one_exact_operation(torch", "operation_count\": 2"):
            self.assertIn(fragment, SOURCE)

    def test_has_fixed_bounded_non_capture_parent_lease(self) -> None:
        self.assertIn("WALL_LIMIT_SECONDS = 60", SOURCE)
        self.assertIn("capture=False", SOURCE)
        self.assertIn("NVBIT_EXACT_DISCOVERY_ONLY_DIAGNOSTIC", SOURCE)
        self.assertIn("NON_SCIENTIFIC_DIAGNOSTIC", SOURCE)
        self.assertNotIn("NVBIT_LONG_WATCH", SOURCE)
        self.assertNotIn("from_pretrained", SOURCE)

    def test_preserves_non_destructive_timeout_evidence(self) -> None:
        for fragment in ("_process_tree", "stack_snapshot", "last_discovery_markers", "BOUNDED_TIMEOUT_DISCOVERY_LAST_MARKER_RETAINED"):
            self.assertIn(fragment, SOURCE)
        self.assertIn("C16_NVBIT_TARGET_FUNCTION_MANGLED", SOURCE)


if __name__ == "__main__":
    unittest.main()
