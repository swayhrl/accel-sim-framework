"""No-GPU contract tests for model-asset endpoint comparison."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SOURCE = Path(__file__).with_name("retry570_recovery_v3_asset_dual_closure.py")
SPEC = importlib.util.spec_from_file_location("asset_dual_closure", SOURCE)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AssetDualClosureTest(unittest.TestCase):
    def test_payloads_reject_duplicate_names(self) -> None:
        value = {"payloads": [{"filename": "a", "size_bytes": 1, "sha256": "a" * 64}, {"filename": "a", "size_bytes": 1, "sha256": "a" * 64}]}
        with self.assertRaises(MODULE.ContractError):
            MODULE.payloads(value)

    def test_payloads_accept_unique_closed_set(self) -> None:
        value = {"payloads": [{"filename": "a", "size_bytes": 1, "sha256": "a" * 64}, {"filename": "b", "size_bytes": 2, "sha256": "b" * 64}]}
        self.assertEqual(MODULE.payloads(value), {"a": (1, "a" * 64), "b": (2, "b" * 64)})


if __name__ == "__main__":
    unittest.main()
