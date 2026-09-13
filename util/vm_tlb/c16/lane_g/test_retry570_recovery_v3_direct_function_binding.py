from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from c16_native_common import ContractError
from retry570_recovery_v3_direct_function_binding import build_bindings


class DirectFunctionBindingTests(unittest.TestCase):
    def write_fixture(self, root: Path, *, ambiguous: bool = False) -> tuple[Path, Path, Path]:
        plan = root / "plan.tsv"; inventory = root / "inventory.tsv"; receipt = root / "receipt.json"
        fields = ["target_plan_id", "phase", "deployment_id", "scenario_id", "source_run_id", "source_catalog_sha256", "grid", "block", "second_pass_validation_key"]
        with plan.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t"); writer.writeheader()
            for phase, ordinal, grid in (("PREFILL", 4, "2x1x1"), ("DECODE", 9, "3x1x1")):
                writer.writerow({"target_plan_id": "P", "phase": phase, "deployment_id": "D", "scenario_id": "S0", "source_run_id": "R", "source_catalog_sha256": "a" * 64, "grid": grid, "block": "128x1x1", "second_pass_validation_key": json.dumps({"source_launch_ordinal": str(ordinal), "grid": grid, "block": "128x1x1"})})
        fields = ["global_launch_ordinal", "function_full_name", "function_mangled_name", "function_address", "grid", "block"]
        with inventory.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t"); writer.writeheader()
            writer.writerows((
                {"global_launch_ordinal": "4", "function_full_name": "fullA", "function_mangled_name": "mangledA", "function_address": "0x1", "grid": "2x1x1", "block": "128x1x1"},
                {"global_launch_ordinal": "9", "function_full_name": "fullB", "function_mangled_name": "mangledB", "function_address": "0x2", "grid": "3x1x1", "block": "128x1x1"},
                *([{ "global_launch_ordinal": "10", "function_full_name": "other", "function_mangled_name": "other", "function_address": "0x3", "grid": "3x1x1", "block": "128x1x1"}] if ambiguous else []),
            ))
        receipt.write_text(json.dumps({"status": "MODEL_NVBIT_QUALIFICATION_FORWARD_COMPLETE", "scientific_eligible": False, "identity": {"run_id": "test"}}), encoding="utf-8")
        return plan, inventory, receipt

    def test_binds_only_direct_ordinal_and_geometry_agreement(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            plan, inventory, receipt = self.write_fixture(Path(directory))
            result = build_bindings(plan, inventory, receipt)
            self.assertEqual(result["bindings"][0]["direct_function_mangled_name"], "mangledB")
            self.assertFalse(result["bindings"][0]["kernel_name_used_for_selection"])

    def test_rejects_nonunique_function_identity_at_target_geometry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            plan, inventory, receipt = self.write_fixture(Path(directory), ambiguous=True)
            with self.assertRaises(ContractError):
                build_bindings(plan, inventory, receipt)


if __name__ == "__main__":
    unittest.main()
