#!/usr/bin/env python3
"""No-GPU contract tests for resident session plan admission."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from c16_native_common import ContractError  # noqa: E402
from resident_model_runner import PLAN_SCHEMA, load_plan  # noqa: E402


class ResidentPlanTests(unittest.TestCase):
    def test_accepts_ordered_unique_plan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_text(json.dumps({
                "schema_version": PLAN_SCHEMA,
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "reset_policy": "GC_ONLY",
                "scenarios": [
                    {"binding_receipt": "s1.json", "run_id": "123e4567-e89b-12d3-a456-426614174001", "receipt": "s1.out.json"},
                    {"binding_receipt": "s2.json", "run_id": "123e4567-e89b-12d3-a456-426614174002", "receipt": "s2.out.json"},
                ],
            }), encoding="utf-8")
            self.assertEqual(load_plan(path)["reset_policy"], "GC_ONLY")

    def test_rejects_duplicate_run_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_text(json.dumps({
                "schema_version": PLAN_SCHEMA,
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "reset_policy": "GC_ONLY",
                "scenarios": [
                    {"binding_receipt": "s1.json", "run_id": "123e4567-e89b-12d3-a456-426614174001", "receipt": "one.json"},
                    {"binding_receipt": "s2.json", "run_id": "123e4567-e89b-12d3-a456-426614174001", "receipt": "two.json"},
                ],
            }), encoding="utf-8")
            with self.assertRaises(ContractError):
                load_plan(path)


if __name__ == "__main__":
    unittest.main()
