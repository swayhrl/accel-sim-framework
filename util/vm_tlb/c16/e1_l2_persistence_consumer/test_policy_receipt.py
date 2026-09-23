#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

from policy_receipt import PolicyReceiptError, validate_policy_receipt


QWEIGHT_BYTES = 33_947_648
QWEIGHT_POINTER = 0x7F00_1234_0000


def receipt(condition: str = "PERSIST_L0_UP", *, budget: int = QWEIGHT_BYTES) -> dict:
    target = "L0_UP" if condition not in {"BASELINE", "SETASIDE_ONLY", "ISO_BASELINE_DENSE"} else "NONE"
    target_mode = condition not in {"BASELINE", "SETASIDE_ONLY", "ISO_BASELINE_DENSE"}
    baseline = condition in {"BASELINE", "ISO_BASELINE_DENSE"}
    setaside = 0 if baseline else budget
    return {
        "status": "PASS",
        "condition": condition,
        "cuda_runtime_version": "12.4",
        "device_ordinal": 0,
        "device_name": "NVIDIA GeForce RTX 4080",
        "persistence_supported": True,
        "l2_bytes": 67_108_864,
        "max_persisting_l2_bytes": 46_137_344,
        "max_access_policy_window_bytes": 134_213_632,
        "target": target,
        "qweight_pointer": hex(QWEIGHT_POINTER),
        "qweight_bytes": QWEIGHT_BYTES,
        "qweight_contiguous": True,
        "requested_setaside_bytes": setaside,
        "actual_setaside_bytes": setaside,
        "stream_identity": "stream:0x1234",
        "access_window_enabled": target_mode,
        "access_window_base_pointer": hex(QWEIGHT_POINTER) if target_mode else "0x0",
        "access_window_num_bytes": QWEIGHT_BYTES if target_mode else 0,
        "hitRatio": min(1.0, budget / QWEIGHT_BYTES) if target_mode else 0.0,
        "hitProp": "cudaAccessPropertyPersisting" if target_mode else "cudaAccessPropertyNormal",
        "missProp": "cudaAccessPropertyNormal",
        "policy_enabled": not baseline,
        "target_persisting_enabled": target_mode,
        "reset_before": {
            "status": "PASS",
            "executed": True,
            "operation": "cudaCtxResetPersistingL2Cache",
        },
        "reset_after": {
            "status": "PASS",
            "executed": True,
            "operation": "cudaCtxResetPersistingL2Cache",
        },
    }


class PolicyReceiptTests(unittest.TestCase):
    def assert_fails(self, value: dict, **kwargs) -> None:
        with self.assertRaises(PolicyReceiptError):
            validate_policy_receipt(value, **kwargs)

    def test_target_condition_exact_window(self) -> None:
        result = validate_policy_receipt(
            receipt(), "PERSIST_L0_UP", "L0_UP", QWEIGHT_BYTES
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["policy_mode"], "TARGET_PERSIST")
        self.assertEqual(result["access_window_base_pointer"], QWEIGHT_POINTER)
        self.assertEqual(result["access_window_num_bytes"], QWEIGHT_BYTES)
        self.assertEqual(result["hit_ratio"], 1.0)

    def test_isolated_target_condition(self) -> None:
        value = receipt("ISO_QWEIGHT_PERSIST_DENSE")
        result = validate_policy_receipt(
            value, "ISO_QWEIGHT_PERSIST_DENSE", "L0_UP", QWEIGHT_BYTES
        )
        self.assertEqual(result["target"], "L0_UP")

    def test_baseline_proves_reset_and_disabled(self) -> None:
        result = validate_policy_receipt(receipt("BASELINE"), "BASELINE")
        self.assertEqual(result["requested_setaside_bytes"], 0)
        self.assertFalse(result["access_window"]["enabled"])
        self.assertEqual(result["reset"]["before"]["status"], "PASS")
        self.assertEqual(result["reset"]["after"]["status"], "PASS")

    def test_isolated_baseline(self) -> None:
        result = validate_policy_receipt(
            receipt("ISO_BASELINE_DENSE"), "ISO_BASELINE_DENSE"
        )
        self.assertEqual(result["policy_mode"], "BASELINE")

    def test_setaside_only_same_budget_no_window(self) -> None:
        result = validate_policy_receipt(
            receipt("SETASIDE_ONLY"), "SETASIDE_ONLY", None, QWEIGHT_BYTES
        )
        self.assertEqual(result["actual_setaside_bytes"], QWEIGHT_BYTES)
        self.assertEqual(result["access_window_num_bytes"], 0)
        self.assertFalse(result["access_window"]["enabled"])

    def test_setaside_only_requires_matched_budget_authority(self) -> None:
        self.assert_fails(
            receipt("SETASIDE_ONLY"),
            expected_condition="SETASIDE_ONLY",
        )

    def test_budget_sweep_keeps_full_window_and_fractional_hit_ratio(self) -> None:
        budget = 8 * 1024 * 1024
        value = receipt("PERSIST_L0_UP_BUDGET_8MIB", budget=budget)
        result = validate_policy_receipt(
            value, "PERSIST_L0_UP_BUDGET_8MIB", "L0_UP", budget
        )
        self.assertEqual(result["access_window_num_bytes"], QWEIGHT_BYTES)
        self.assertAlmostEqual(result["hit_ratio"], budget / QWEIGHT_BYTES)

    def test_declared_setaside_alignment_rounding(self) -> None:
        budget = 8 * 1024 * 1024 + 1
        value = receipt("PERSIST_L0_UP_BUDGET_ODD", budget=budget)
        value["setaside_alignment_bytes"] = 256
        value["actual_setaside_bytes"] = ((budget + 255) // 256) * 256
        result = validate_policy_receipt(
            value, "PERSIST_L0_UP_BUDGET_ODD", "L0_UP", budget
        )
        self.assertEqual(result["actual_setaside_bytes"], value["actual_setaside_bytes"])

    def test_nested_schema_aliases(self) -> None:
        flat = receipt()
        value = {
            "status": flat["status"],
            "condition": flat["condition"],
            "target": flat["target"],
            "capability": {
                "cuda_runtime_version": flat["cuda_runtime_version"],
                "device_ordinal": flat["device_ordinal"],
                "device_name": flat["device_name"],
                "persistence_supported": flat["persistence_supported"],
                "l2_bytes": flat["l2_bytes"],
                "max_persisting_l2_bytes": flat["max_persisting_l2_bytes"],
                "max_access_policy_window_bytes": flat["max_access_policy_window_bytes"],
            },
            "qweight": {
                "pointer": flat["qweight_pointer"],
                "bytes": flat["qweight_bytes"],
                "contiguous": True,
            },
            "setaside": {
                "requested_bytes": flat["requested_setaside_bytes"],
                "actual_bytes": flat["actual_setaside_bytes"],
            },
            "stream": {"id": flat["stream_identity"]},
            "access_window": {
                "enabled": True,
                "base_pointer": flat["access_window_base_pointer"],
                "num_bytes": flat["access_window_num_bytes"],
                "hitRatio": flat["hitRatio"],
                "hitProp": flat["hitProp"],
                "missProp": flat["missProp"],
                "target_persisting_enabled": True,
            },
            "policy_enabled": True,
            "reset": {
                "before": flat["reset_before"],
                "after": flat["reset_after"],
            },
        }
        result = validate_policy_receipt(
            value, "PERSIST_L0_UP", "L0_UP", QWEIGHT_BYTES
        )
        self.assertEqual(result["stream_identity"], "stream:0x1234")

    def test_missing_capability_field_fails(self) -> None:
        value = receipt()
        del value["max_access_policy_window_bytes"]
        self.assert_fails(
            value,
            expected_condition="PERSIST_L0_UP",
            expected_target="L0_UP",
        )

    def test_wrong_device_capability_fails(self) -> None:
        value = receipt()
        value["l2_bytes"] -= 1
        self.assert_fails(
            value,
            expected_condition="PERSIST_L0_UP",
            expected_target="L0_UP",
        )

    def test_noncontiguous_qweight_fails(self) -> None:
        value = receipt()
        value["qweight_contiguous"] = False
        self.assert_fails(
            value,
            expected_condition="PERSIST_L0_UP",
            expected_target="L0_UP",
        )

    def test_wrong_condition_and_target_fail(self) -> None:
        value = receipt()
        self.assert_fails(
            value,
            expected_condition="PERSIST_L14_UP",
            expected_target="L14_UP",
        )
        value["condition"] = "PERSIST_L14_UP"
        self.assert_fails(
            value,
            expected_condition="PERSIST_L14_UP",
            expected_target="L14_UP",
        )

    def test_qweight_window_pointer_or_size_mismatch_fails(self) -> None:
        for field, replacement in (
            ("access_window_base_pointer", hex(QWEIGHT_POINTER + 256)),
            ("access_window_num_bytes", QWEIGHT_BYTES - 1),
        ):
            with self.subTest(field=field):
                value = receipt()
                value[field] = replacement
                self.assert_fails(
                    value,
                    expected_condition="PERSIST_L0_UP",
                    expected_target="L0_UP",
                )

    def test_setaside_above_runtime_max_fails(self) -> None:
        value = receipt()
        value["requested_setaside_bytes"] = 46_137_345
        value["actual_setaside_bytes"] = 46_137_345
        self.assert_fails(
            value,
            expected_condition="PERSIST_L0_UP",
            expected_target="L0_UP",
        )

    def test_window_above_runtime_max_fails(self) -> None:
        value = receipt()
        value["qweight_bytes"] = 134_213_633
        value["access_window_num_bytes"] = 134_213_633
        self.assert_fails(
            value,
            expected_condition="PERSIST_L0_UP",
            expected_target="L0_UP",
        )

    def test_missing_or_failed_reset_fails(self) -> None:
        missing = receipt()
        del missing["reset_after"]
        failed = receipt()
        failed["reset_before"]["status"] = "FAIL"
        for value in (missing, failed):
            self.assert_fails(
                value,
                expected_condition="PERSIST_L0_UP",
                expected_target="L0_UP",
            )

    def test_baseline_with_reservation_or_window_fails(self) -> None:
        reserved = receipt("BASELINE")
        reserved["requested_setaside_bytes"] = QWEIGHT_BYTES
        reserved["actual_setaside_bytes"] = QWEIGHT_BYTES
        window = receipt("BASELINE")
        window["access_window_enabled"] = True
        for value in (reserved, window):
            self.assert_fails(value, expected_condition="BASELINE")

    def test_setaside_only_target_window_fails(self) -> None:
        value = receipt("SETASIDE_ONLY")
        value["access_window_enabled"] = True
        value["access_window_base_pointer"] = hex(QWEIGHT_POINTER)
        value["access_window_num_bytes"] = QWEIGHT_BYTES
        value["hitRatio"] = 1.0
        value["hitProp"] = "cudaAccessPropertyPersisting"
        value["target_persisting_enabled"] = True
        self.assert_fails(
            value,
            expected_condition="SETASIDE_ONLY",
            expected_budget_bytes=QWEIGHT_BYTES,
        )

    def test_budget_and_hit_ratio_mismatch_fail(self) -> None:
        budget = 8 * 1024 * 1024
        wrong_budget = receipt("PERSIST_L0_UP_BUDGET_8MIB", budget=budget)
        wrong_ratio = copy.deepcopy(wrong_budget)
        wrong_ratio["hitRatio"] = 1.0
        self.assert_fails(
            wrong_budget,
            expected_condition="PERSIST_L0_UP_BUDGET_8MIB",
            expected_target="L0_UP",
            expected_budget_bytes=16 * 1024 * 1024,
        )
        self.assert_fails(
            wrong_ratio,
            expected_condition="PERSIST_L0_UP_BUDGET_8MIB",
            expected_target="L0_UP",
            expected_budget_bytes=budget,
        )

    def test_ambiguous_aliases_fail(self) -> None:
        value = receipt()
        value["capability"] = {"l2_bytes": 123}
        self.assert_fails(
            value,
            expected_condition="PERSIST_L0_UP",
            expected_target="L0_UP",
        )


if __name__ == "__main__":
    unittest.main()
