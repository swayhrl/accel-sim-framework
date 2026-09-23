#!/usr/bin/env python3
import copy
import math
import unittest

import coverage_analysis_consumer as ca


def make_run(rep, selected, *, fair=False, decode_fair_ms=98.0):
    occurrences = []
    for layer in ca.LAYERS:
        for decode in range(4):
            timing = 0.9 if fair and layer in selected else (0.99 if fair else 1.0)
            occurrences.append({
                "layer_index": layer,
                "role": "up_proj",
                "decode_index": decode,
                "timing_ms": timing + rep * 1e-7,
            })
    return {
        "rep": rep,
        "occurrences": occurrences,
        "decode_steps": [
            {"decode_index": decode,
             "timing_ms": (decode_fair_ms if fair else 100.0) + rep * 1e-5}
            for decode in range(4)
        ],
    }


def make_condition(name, set_name, *, fair=False, full=False):
    selected = ca.LAYER_SETS[set_name]
    result = {
        "condition": name,
        "selected_layers": list(selected),
        "runs": [make_run(rep, selected, fair=fair) for rep in range(ca.EXPECTED_REPS)],
    }
    if full:
        result["hit_ratio"] = 1.0
    return result


def coverage_document():
    conditions = []
    for set_name in ca.PRIMARY_AND_HOLDOUT:
        conditions.append(make_condition(f"CONTROL_{set_name}", set_name))
        conditions.append(make_condition(f"FAIR_{set_name}", set_name, fair=True))
    return {"schema_version": 1, "conditions": conditions}


def fullhint_document():
    return {
        "schema_version": 1,
        "conditions": [
            make_condition("CONTROL_FULL_N8", "N8", full=True),
            make_condition("FULLHINT_N8", "N8", fair=True, full=True),
            make_condition("CONTROL_FULL_N28", "N28", full=True),
            make_condition("FULLHINT_N28", "N28", fair=True, full=True),
        ],
    }


def condition_map(set_name):
    control_name, fair_name = f"CONTROL_{set_name}", f"FAIR_{set_name}"
    control_raw = make_condition(control_name, set_name)
    fair_raw = make_condition(fair_name, set_name, fair=True)
    return {
        control_name: ca._condition_runs(control_raw, control_name, ca.LAYER_SETS[set_name]),
        fair_name: ca._condition_runs(fair_raw, fair_name, ca.LAYER_SETS[set_name]),
    }


def n28_point(benefit, dispersion, fraction):
    return {
        "material_selected_layer_fraction": fraction,
        "whole_decode_stable_effect": {
            "benefit_fraction": benefit,
            "combined_dispersion": dispersion,
        },
    }


class CoverageRunAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analysis = ca.consume_coverage_runs(coverage_document())

    def test_complete_matrix_passes(self):
        self.assertEqual(self.analysis["status"], "PASS")
        self.assertEqual(set(self.analysis["points"]), set(ca.PRIMARY_AND_HOLDOUT))
        self.assertEqual(len(self.analysis["points"]["N28"]["run_decode_metrics"]), 21)

    def test_run_aligned_metrics_and_unclamped_realization(self):
        point = self.analysis["points"]["N1"]
        self.assertAlmostEqual(point["selected_target_share"]["median"], 0.01, places=7)
        self.assertAlmostEqual(point["summed_local_saving_ms"]["median"], 0.1, places=6)
        self.assertGreater(
            point["realization_ratio"]["ratio_of_median_run_aligned_observed_to_local"], 1.0
        )
        self.assertTrue(point["realization_ratio"]["unclamped"])

    def test_stable_effect_uses_d1_through_d3_only(self):
        document = coverage_document()
        for condition in document["conditions"]:
            if condition["condition"] == "FAIR_N1":
                for run in condition["runs"]:
                    run["decode_steps"][0]["timing_ms"] = 1_000_000.0
        analysis = ca.consume_coverage_runs(document)
        self.assertAlmostEqual(
            analysis["points"]["N1"]["whole_decode_stable_effect"]["benefit_fraction"],
            self.analysis["points"]["N1"]["whole_decode_stable_effect"]["benefit_fraction"],
        )

    def test_nonselected_effect_is_separate(self):
        point = self.analysis["points"]["N1"]
        self.assertEqual(point["nonselected_aggregate_effect"]["nonselected_layer_count"], 27)
        self.assertAlmostEqual(
            point["nonselected_aggregate_effect"]["benefit_fraction"]["median"], 0.01, places=6
        )

    def test_median_of_layer_medians_bug_is_not_present(self):
        conditions = condition_map("N2")
        xs = [1, 100, 100, 1, 1, 100, 100]
        ys = [100, 1, 100, 1, 100, 1, 100]
        for rep in range(ca.EXPECTED_REPS):
            for decode in ca.STABLE_DECODE_INDICES:
                # Timings remain positive; x/y are the per-layer savings.
                conditions["CONTROL_N2"][rep]["occurrences"][(0, decode)] = 201.0
                conditions["CONTROL_N2"][rep]["occurrences"][(14, decode)] = 201.0
                conditions["FAIR_N2"][rep]["occurrences"][(0, decode)] = 201.0 - xs[rep]
                conditions["FAIR_N2"][rep]["occurrences"][(14, decode)] = 201.0 - ys[rep]
        point = ca._analyze_pair("N2", "CONTROL_N2", "FAIR_N2", conditions)
        # median(x) + median(y) is 200, while median(x+y) is 101.
        self.assertEqual(point["summed_local_saving_ms"]["median"], 101.0)
        self.assertNotEqual(point["summed_local_saving_ms"]["median"], 200.0)

    def test_zero_local_saving_denominator_is_explicitly_undefined(self):
        conditions = condition_map("N1")
        for rep in range(ca.EXPECTED_REPS):
            for decode in ca.STABLE_DECODE_INDICES:
                conditions["FAIR_N1"][rep]["occurrences"][(0, decode)] = 1.0 + rep * 1e-7
        point = ca._analyze_pair("N1", "CONTROL_N1", "FAIR_N1", conditions)
        self.assertIsNone(point["run_stable_metrics"][0]["realization_ratio"])
        self.assertEqual(point["run_stable_metrics"][0]["realization_status"],
                         "UNDEFINED_ZERO_DENOMINATOR")

    def test_negative_local_saving_denominator_is_explicitly_undefined(self):
        conditions = condition_map("N1")
        for rep in range(ca.EXPECTED_REPS):
            for decode in ca.STABLE_DECODE_INDICES:
                conditions["FAIR_N1"][rep]["occurrences"][(0, decode)] = 1.1
        point = ca._analyze_pair("N1", "CONTROL_N1", "FAIR_N1", conditions)
        self.assertIsNone(point["run_stable_metrics"][0]["realization_ratio"])
        self.assertEqual(point["run_stable_metrics"][0]["realization_status"],
                         "UNDEFINED_NEGATIVE_DENOMINATOR")

    def test_wrong_layer_set_fails_closed(self):
        document = coverage_document()
        document["conditions"][0]["selected_layers"] = [14]
        with self.assertRaisesRegex(ca.CoverageAnalysisError, "layer set mismatch"):
            ca.consume_coverage_runs(document)

    def test_missing_occurrence_fails_closed(self):
        document = coverage_document()
        document["conditions"][0]["runs"][0]["occurrences"].pop()
        with self.assertRaisesRegex(ca.CoverageAnalysisError, "all-28 occurrence matrix"):
            ca.consume_coverage_runs(document)

    def test_duplicate_rep_fails_closed(self):
        document = coverage_document()
        document["conditions"][0]["runs"][1]["rep"] = 0
        with self.assertRaisesRegex(ca.CoverageAnalysisError, "duplicate/out-of-range rep"):
            ca.consume_coverage_runs(document)

    def test_nonfinite_timing_fails_closed(self):
        document = coverage_document()
        document["conditions"][0]["runs"][0]["occurrences"][0]["timing_ms"] = math.nan
        with self.assertRaisesRegex(ca.CoverageAnalysisError, "nonfinite"):
            ca.consume_coverage_runs(document)


class N14HoldoutTests(unittest.TestCase):
    def test_holdout_never_ranks_a_winner(self):
        result = ca.consume_coverage_runs(coverage_document())["n14_holdout"]
        self.assertFalse(result["winner_selected"])
        self.assertFalse(result["ranking_performed"])
        self.assertEqual(set(result["comparison"]), {"N14A", "N14B"})

    def test_n14_set_mismatch_fails_closed(self):
        points = ca.consume_coverage_runs(coverage_document())["points"]
        broken = copy.deepcopy(points)
        broken["N14B"]["selected_layers"][0] = 0
        with self.assertRaisesRegex(ca.CoverageAnalysisError, "N14B holdout set mismatch"):
            ca.analyze_n14_holdout(broken)


class FullhintTests(unittest.TestCase):
    def test_false_trigger_forbids_run(self):
        point = n28_point(0.021, 0.0, 0.75)
        with self.assertRaisesRegex(ca.CoverageAnalysisError, "trigger was false"):
            ca.consume_fullhint(point, fullhint_document())

    def test_false_trigger_accepts_no_run(self):
        result = ca.consume_fullhint(n28_point(0.021, 0.0, 0.75), None)
        self.assertFalse(result["triggered"])
        self.assertFalse(result["producer_run_observed"])

    def test_true_trigger_requires_evidence(self):
        with self.assertRaisesRegex(ca.CoverageAnalysisError, "evidence is missing"):
            ca.consume_fullhint(n28_point(0.019999, 0.0, 0.50), None)

    def test_true_trigger_requires_exact_four_condition_matrix(self):
        evidence = fullhint_document()
        evidence["conditions"].pop()
        with self.assertRaisesRegex(ca.CoverageAnalysisError, "condition matrix mismatch"):
            ca.consume_fullhint(n28_point(0.0, 0.01, 0.50), evidence)

    def test_true_trigger_closes_four_condition_matrix(self):
        result = ca.consume_fullhint(n28_point(-0.01, 0.0, 0.50), fullhint_document())
        self.assertTrue(result["triggered"])
        self.assertEqual(set(result["points"]), {"N8", "N28"})
        self.assertIn("OVERSUBSCRIBED_INTENT", result["hit_ratio_interpretation"])

    def test_fullhint_hit_ratio_must_be_one(self):
        evidence = fullhint_document()
        evidence["conditions"][0]["hit_ratio"] = 1 / 8
        with self.assertRaisesRegex(ca.CoverageAnalysisError, "hitRatio=1"):
            ca.consume_fullhint(n28_point(0.0, 0.0, 0.50), evidence)


class StageDecisionBoundaryTests(unittest.TestCase):
    def test_policy_unqualified_has_precedence(self):
        result = ca.classify_stage(n28_point(0.5, 0.0, 1.0), policy_qualified=False)
        self.assertEqual(result["stage_label"], "POLICY_SCALING_UNQUALIFIED")

    def test_exact_two_percent_is_system_relevant(self):
        result = ca.classify_stage(n28_point(0.02, 0.0, 0.0), policy_qualified=True)
        self.assertEqual(result["stage_label"], "COVERAGE_SCALING_SYSTEM_RELEVANT")

    def test_positive_but_subthreshold(self):
        result = ca.classify_stage(n28_point(0.019, 0.001, 0.0), policy_qualified=True)
        self.assertEqual(result["stage_label"], "COVERAGE_SCALING_POSITIVE_BUT_SUBTHRESHOLD")

    def test_equal_to_dispersion_is_not_materially_positive(self):
        result = ca.classify_stage(n28_point(0.01, 0.01, 0.50), policy_qualified=True)
        self.assertEqual(result["stage_label"], "COVERAGE_SCALING_LOCAL_BUT_NOT_SYSTEMIC")

    def test_not_supported_below_half_local_materiality(self):
        result = ca.classify_stage(n28_point(0.0, 0.0, 0.499999), policy_qualified=True)
        self.assertEqual(result["stage_label"], "COVERAGE_SCALING_NOT_SUPPORTED")

    def test_no_stage_label_auto_authorizes_simulator(self):
        for point in (
            n28_point(0.02, 0.0, 1.0),
            n28_point(0.01, 0.0, 1.0),
            n28_point(0.0, 0.0, 1.0),
            n28_point(0.0, 0.0, 0.0),
        ):
            self.assertFalse(ca.classify_stage(point, policy_qualified=True)["simulator_auto_authorized"])


if __name__ == "__main__":
    unittest.main()
