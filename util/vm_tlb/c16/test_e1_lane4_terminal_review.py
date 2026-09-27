"""Synthetic-only tests: no Lane 4 result directory is read."""

import copy
import tempfile
import unittest
from pathlib import Path

import e1_lane4_terminal_review as review


def fixture_packet():
    receipt = {"status": "PASS", "exit_code": 0, "terminal_marker": True,
               "receipt_sha256": "a" * 64}
    workload = {"kernel_count": 1565, "kernel_sequence_sha256": "b" * 64,
                "instruction_count": 100, "CTA_count": 1259187}
    return {
        "schema": review.INPUT_SCHEMA,
        "publication_status": "TERMINAL_REVIEW_READY",
        "authority": copy.deepcopy(review.AUTHORITY),
        "identity": {**review.IDENTITY, "binary_sha256": "e" * 64},
        "terminal_receipts": {name: copy.deepcopy(receipt) for name in
                              ("R0_BASELINE", "M1_B16", "M1_B16_DIAGNOSTIC")},
        "reuse_window_scope": {**review.SCOPE, "status": "PASS",
                               "no_kernel_filtering_or_reordering": True,
                               "selected_sequence_sha256": review.IDENTITY["reuse_sequence_sha256"]},
        "workload_identity": {"R0_BASELINE": copy.deepcopy(workload),
                              "M1_B16": copy.deepcopy(workload)},
        "primary_correctness": {"status": "PASS", "R0_M1_equal": True,
                                "comparison_sha256": "f" * 64},
        "primary_timing": {"status": "PASS", "performance_sha256": "1" * 64,
                           "cycles": {name: {"R0_cycles": 100, "M1_cycles": 90}
                                      for name in review.WINDOWS}},
        "diagnostic": {"pre_gate_status": "SPECULATIVE_PRE_GATE",
                       "neutrality_status": "PASS", "counters_status": "PASS",
                       "diagnostic_sha256": "2" * 64,
                       "counters": {
                           "target_accesses": 100, "protected_fills": 20,
                           "protected_protected_evictions": 8,
                           "protected_victim_evictions": 10,
                           "eligible_target_fills": 40,
                           "quota_denials_invalid_priority": 3,
                           "quota_denials_no_local_protected_victim": 5,
                           "D1_class1_after_fill": 12,
                           "D1_class1_before_D2": 4,
                           "old_address_survivors": None,
                           "old_address_population": None}}
    }


def signals(**overrides):
    value = {"high_churn": False, "low_old_survival": False,
             "good_old_survival": False, "local_positive": False,
             "window_positive": False, "denial_dominant": False,
             "target_protection_low": False}
    value.update(overrides)
    return value


class TerminalReviewTests(unittest.TestCase):
    def test_admitted_packet_stays_review_only(self):
        result = review.evaluate(fixture_packet())
        self.assertEqual("PRIMARY_REVIEW_READY", result["status"])
        self.assertEqual("ADMITTED_FOR_REVIEW", result["diagnostic_admission"])
        self.assertEqual(0.1, result["normalized_metrics"]["primary_timing"]["C_window"]["response_fraction"])
        self.assertIsNone(result["normalized_metrics"]["diagnostic"]["old_address_survival_fraction"])
        self.assertEqual({case: "REQUIRES_PROJECT_REVIEW" for case in review.CASES}, result["ABCD"])
        self.assertFalse(result["scientific_result_row_generated"])

    def test_synthetic_A_B_C_D_routing_without_numeric_thresholds(self):
        fixtures = {
            "A": signals(high_churn=True, low_old_survival=True),
            "B": signals(good_old_survival=True),
            "C": signals(good_old_survival=True, local_positive=True, window_positive=True),
            "D": signals(denial_dominant=True, target_protection_low=True),
        }
        for expected, inputs in fixtures.items():
            with self.subTest(expected=expected):
                self.assertEqual(expected, review.classify_synthetic_signals(inputs))

    def test_conflicting_synthetic_signals_require_review(self):
        with self.assertRaises(review.ReviewError):
            review.classify_synthetic_signals(signals(low_old_survival=True,
                                                      good_old_survival=True))
        self.assertEqual("REQUIRES_PROJECT_REVIEW", review.classify_synthetic_signals(
            signals(high_churn=True, low_old_survival=True,
                    denial_dominant=True, target_protection_low=True)))

    def test_partial_packet_rejected(self):
        packet = fixture_packet()
        packet["publication_status"] = "PARTIAL"
        with self.assertRaisesRegex(review.ReviewError, "PARTIAL_REJECTED"):
            review.evaluate(packet)

    def test_schema_drift_rejected(self):
        packet = fixture_packet()
        packet["identity"]["unreviewed_identity"] = "0" * 64
        with self.assertRaisesRegex(review.ReviewError, "SCHEMA_DRIFT"):
            review.evaluate(packet)

    def test_missing_primary_terminal_receipt_rejected(self):
        packet = fixture_packet()
        del packet["terminal_receipts"]["M1_B16"]
        with self.assertRaisesRegex(review.ReviewError, "MISSING_TERMINAL_RECEIPT"):
            review.evaluate(packet)

    def test_identity_mismatch_fails_before_timing(self):
        packet = fixture_packet()
        packet["identity"]["sidecar_sha256"] = "0" * 64
        with self.assertRaisesRegex(review.ReviewError, "IDENTITY_MISMATCH"):
            review.evaluate(packet)

    def test_primary_terminal_failure_quarantines_diagnostic(self):
        packet = fixture_packet()
        packet["terminal_receipts"]["R0_BASELINE"]["status"] = "FAIL"
        result = review.evaluate(packet)
        self.assertEqual("PRIMARY_FAILED", result["status"])
        self.assertEqual("QUARANTINE_DIAGNOSTIC", result["diagnostic_admission"])
        self.assertEqual({}, result["normalized_metrics"])

    def test_primary_workload_failure_quarantines_diagnostic(self):
        packet = fixture_packet()
        packet["workload_identity"]["M1_B16"]["instruction_count"] += 1
        result = review.evaluate(packet)
        self.assertEqual("primary workload identity", result["failed_stage"])
        self.assertEqual("QUARANTINE_DIAGNOSTIC", result["diagnostic_admission"])

    def test_primary_correctness_failure_quarantines_diagnostic(self):
        packet = fixture_packet()
        packet["primary_correctness"]["status"] = "FAIL"
        result = review.evaluate(packet)
        self.assertEqual("primary correctness", result["failed_stage"])
        self.assertEqual("QUARANTINE_DIAGNOSTIC", result["diagnostic_admission"])

    def test_missing_diagnostic_terminal_receipt_rejected(self):
        packet = fixture_packet()
        del packet["terminal_receipts"]["M1_B16_DIAGNOSTIC"]
        with self.assertRaisesRegex(review.ReviewError, "MISSING_TERMINAL_RECEIPT"):
            review.evaluate(packet)

    def test_diagnostic_neutrality_failure_quarantines(self):
        packet = fixture_packet()
        packet["diagnostic"]["neutrality_status"] = "FAIL"
        result = review.evaluate(packet)
        self.assertEqual("QUARANTINE_DIAGNOSTIC", result["diagnostic_admission"])
        self.assertNotIn("diagnostic", result["normalized_metrics"])

    def test_active_output_path_forbidden(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / review.PACKET_NAME
            path.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(review.ReviewError, "ACTIVE_OUTPUT_FORBIDDEN"):
                review.committed_packet(path)


if __name__ == "__main__":
    unittest.main()
