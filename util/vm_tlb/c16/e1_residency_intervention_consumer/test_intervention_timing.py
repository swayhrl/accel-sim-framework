#!/usr/bin/env python3
import math
import unittest

from intervention_timing import (
    ContractError,
    DOSES_MIB,
    STATES,
    analyze_dose_rows,
    analyze_timing_rows,
    recompute_decision,
)


INPUT_SHA = "1" * 64
OUTPUT_SHA = "2" * 64
PRIMARY_POINT = frozenset({("TEXT", "up_proj", 1, "AWQ_FP16_INPUT")})


def analyze_fixture(rows):
    return analyze_timing_rows(rows, expected_points=PRIMARY_POINT)


def timing_fixture(
    warm=1.0,
    sparse=1.01,
    dense=1.20,
    warm_b=1.01,
    jitter=0.002,
):
    rows = []
    values = {
        "WARM_A": warm,
        "SPARSE_PAGE_PRESSURE": sparse,
        "DENSE_MEMORY_PRESSURE": dense,
        "WARM_B": warm_b,
    }
    for state in STATES:
        for rep in range(7):
            factor = 1.0 + jitter * (rep - 3)
            rows.append(
                {
                    "domain": "TEXT",
                    "role": "up_proj",
                    "M": "1",
                    "implementation": "AWQ_FP16_INPUT",
                    "state": state,
                    "rep": str(rep),
                    "timing_ms": str(values[state] * factor),
                    "input_sha256": INPUT_SHA,
                    "output_sha256": OUTPUT_SHA,
                }
            )
    return rows


def dose_fixture(medians=None):
    medians = medians or [1.0, 1.02, 1.04, 1.08, 1.12, 1.20]
    rows = []
    for implementation, scale in (("RAW_FP16", 2.0), ("AWQ_FP16_INPUT", 1.0)):
        for dose, median in zip(DOSES_MIB, medians):
            for rep in range(7):
                rows.append(
                    {
                        "domain": "TEXT",
                        "role": "up_proj",
                        "M": "1",
                        "implementation": implementation,
                        "dose_mib": str(dose),
                        "rep": str(rep),
                        "timing_ms": str(scale * median * (1 + 0.001 * (rep - 3))),
                        "input_sha256": INPUT_SHA,
                        "output_sha256": OUTPUT_SHA,
                    }
                )
    return rows


class NativeTimingTests(unittest.TestCase):
    def point(self, result):
        self.assertEqual(result["point_count"], 1)
        return result["points"][0]

    def test_material_dense_effect_and_recovery(self):
        point = self.point(analyze_fixture(timing_fixture()))
        self.assertTrue(point["MATERIAL_TIMING_PERTURBATION"])
        self.assertTrue(point["REVERSIBLE"])
        self.assertTrue(point["DENSE_SPECIFIC_TIMING"])
        self.assertAlmostEqual(point["ratios"]["DENSE_over_WARM_A"], 1.2)

    def test_no_effect(self):
        point = self.point(
            analyze_fixture(timing_fixture(sparse=1.005, dense=1.01, warm_b=1.0))
        )
        self.assertFalse(point["MATERIAL_TIMING_PERTURBATION"])
        self.assertTrue(point["REVERSIBLE"])
        self.assertFalse(point["DENSE_SPECIFIC_TIMING"])

    def test_sparse_approximately_dense_is_not_dense_specific(self):
        point = self.point(
            analyze_fixture(timing_fixture(sparse=1.19, dense=1.20, warm_b=1.0))
        )
        self.assertTrue(point["MATERIAL_TIMING_PERTURBATION"])
        self.assertFalse(point["DENSE_SPECIFIC_TIMING"])

    def test_failed_recovery(self):
        point = self.point(analyze_fixture(timing_fixture(warm_b=1.20)))
        self.assertFalse(point["REVERSIBLE"])

    def test_duplicate_timing_fails(self):
        rows = timing_fixture()
        rows.append(dict(rows[0]))
        with self.assertRaisesRegex(ContractError, "duplicate point/state/rep"):
            analyze_fixture(rows)

    def test_missing_timing_state_fails(self):
        rows = [row for row in timing_fixture() if row["state"] != "WARM_B"]
        with self.assertRaisesRegex(ContractError, "state matrix mismatch"):
            analyze_fixture(rows)

    def test_sample_count_fails(self):
        rows = timing_fixture()
        rows.pop()
        with self.assertRaisesRegex(ContractError, "sample-count mismatch"):
            analyze_fixture(rows)

    def test_sha_drift_fails(self):
        rows = timing_fixture()
        rows[-1]["output_sha256"] = "3" * 64
        with self.assertRaisesRegex(ContractError, "SHA mismatch"):
            analyze_fixture(rows)

    def test_nonfinite_fails(self):
        rows = timing_fixture()
        rows[0]["timing_ms"] = "nan"
        with self.assertRaisesRegex(ContractError, "nonpositive/nonfinite"):
            analyze_fixture(rows)


class DoseTests(unittest.TestCase):
    def test_exact_matrix_ratios_and_monotonicity(self):
        result = analyze_dose_rows(dose_fixture())
        self.assertEqual(len(result["implementations"]), 2)
        for implementation in result["implementations"]:
            self.assertTrue(
                implementation["monotonicity_diagnostic"]["nondecreasing_medians"]
            )
            self.assertFalse(
                implementation["monotonicity_diagnostic"]["is_pass_gate"]
            )
            self.assertAlmostEqual(implementation["doses"][-1]["ratio_to_0MiB"], 1.2)

    def test_nonmonotonicity_is_diagnostic_not_failure(self):
        result = analyze_dose_rows(dose_fixture([1.0, 1.1, 1.05, 1.2, 1.15, 1.3]))
        for implementation in result["implementations"]:
            diagnostic = implementation["monotonicity_diagnostic"]
            self.assertFalse(diagnostic["nondecreasing_medians"])
            self.assertGreater(len(diagnostic["violations"]), 0)

    def test_missing_dose_fails(self):
        rows = [
            row
            for row in dose_fixture()
            if not (row["implementation"] == "RAW_FP16" and row["dose_mib"] == "64")
        ]
        with self.assertRaisesRegex(ContractError, "dose matrix mismatch"):
            analyze_dose_rows(rows)

    def test_duplicate_dose_rep_fails(self):
        rows = dose_fixture()
        rows.append(dict(rows[0]))
        with self.assertRaisesRegex(ContractError, "duplicate implementation/dose/rep"):
            analyze_dose_rows(rows)


class DecisionTests(unittest.TestCase):
    def timing(self, **kwargs):
        return analyze_fixture(timing_fixture(**kwargs))

    def test_strong_requires_all_four_booleans(self):
        decision = recompute_decision(
            self.timing(),
            {
                "WARM_A": 1024.0,
                "SPARSE_PAGE_PRESSURE": 2 * 1024 * 1024.0,
                "DENSE_MEMORY_PRESSURE": 5 * 1024 * 1024.0,
            },
        )
        self.assertTrue(decision["MATERIAL_TIMING_PERTURBATION"])
        self.assertTrue(decision["MATERIAL_DRAM_PERTURBATION"])
        self.assertTrue(decision["REVERSIBLE"])
        self.assertTrue(decision["DENSE_SPECIFIC"])
        self.assertEqual(
            decision["scope_label"], "RESIDENCY_INTERVENTION_STRONGLY_SUPPORTED"
        )

    def test_failed_recovery_is_partial(self):
        decision = recompute_decision(
            self.timing(warm_b=1.2),
            {
                "WARM_A": 1024.0,
                "SPARSE_PAGE_PRESSURE": 2 * 1024 * 1024.0,
                "DENSE_MEMORY_PRESSURE": 5 * 1024 * 1024.0,
            },
        )
        self.assertFalse(decision["REVERSIBLE"])
        self.assertEqual(
            decision["scope_label"], "RESIDENCY_INTERVENTION_PARTIALLY_SUPPORTED"
        )

    def test_no_material_effect_is_not_supported(self):
        decision = recompute_decision(
            self.timing(sparse=1.0, dense=1.01, warm_b=1.0),
            {
                "WARM_A": 1024.0,
                "SPARSE_PAGE_PRESSURE": 2048.0,
                "DENSE_MEMORY_PRESSURE": 4096.0,
            },
        )
        self.assertFalse(decision["MATERIAL_TIMING_PERTURBATION"])
        self.assertFalse(decision["MATERIAL_DRAM_PERTURBATION"])
        self.assertEqual(
            decision["scope_label"], "RESIDENCY_INTERVENTION_NOT_SUPPORTED"
        )

    def test_sparse_approximately_dense_prevents_strong(self):
        decision = recompute_decision(
            self.timing(sparse=1.19, dense=1.20),
            {
                "WARM_A": 1024.0,
                "SPARSE_PAGE_PRESSURE": 4 * 1024 * 1024.0,
                "DENSE_MEMORY_PRESSURE": 5 * 1024 * 1024.0,
            },
        )
        self.assertFalse(decision["DENSE_SPECIFIC"])
        self.assertEqual(
            decision["scope_label"], "RESIDENCY_INTERVENTION_PARTIALLY_SUPPORTED"
        )


if __name__ == "__main__":
    unittest.main()
