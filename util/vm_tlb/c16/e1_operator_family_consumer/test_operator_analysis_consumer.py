#!/usr/bin/env python3
import copy
import math
import statistics
import unittest

import operator_analysis_consumer as oa


def make_run(rep, selected_roles, *, fair=False, fair_decode=98.5,
             selected_delta=0.10, unselected_delta=0.01, overhead=1.0):
    occurrences = []
    for layer in oa.LAYERS:
        for role in oa.ROLES:
            for decode in oa.DECODE_INDICES:
                delta = selected_delta if role in selected_roles else unselected_delta
                timing = 1.0 - delta if fair else 1.0
                occurrences.append({
                    "layer_index": layer, "role": role, "decode_index": decode,
                    "timing_ms": timing + rep * 1e-8,
                })
    count = 5 * 28 * len(selected_roles)
    return {
        "rep": rep,
        "ffn_occurrences": occurrences,
        "decode_steps": [
            {"decode_index": decode,
             "timing_ms": (fair_decode if fair else 100.0) + rep * 1e-6}
            for decode in oa.DECODE_INDICES
        ],
        "policy_overheads": [
            {"update_index": index, "duration": overhead, "unit": "us"}
            for index in range(count)
        ],
    }


def make_condition(name, family, *, fair=False, fair_decode=98.5,
                   selected_delta=0.10, unselected_delta=0.01,
                   overhead=1.0, fullhint=False):
    roles = oa.FAMILY_ROLES[family]
    result = {
        "condition": name,
        "selected_roles": list(roles),
        "runs": [make_run(rep, roles, fair=fair, fair_decode=fair_decode,
                          selected_delta=selected_delta,
                          unselected_delta=unselected_delta,
                          overhead=overhead)
                 for rep in range(oa.EXPECTED_REPS)],
    }
    if fullhint:
        result["hit_ratio"] = 1.0
    return result


def primary_document(**kwargs):
    conditions = []
    for family, (control, fair) in oa.PRIMARY_PAIRS.items():
        conditions.append(make_condition(control, family))
        conditions.append(make_condition(fair, family, fair=True, overhead=1.1,
                                         **kwargs))
    return {"schema_version": 1, "conditions": conditions}


def fullhint_document(*, fair_decode=97.5):
    return {
        "schema_version": 1,
        "conditions": [
            make_condition(oa.FULLHINT_PAIR[0], "GUD84", fullhint=True),
            make_condition(oa.FULLHINT_PAIR[1], "GUD84", fair=True,
                           fair_decode=fair_decode, fullhint=True),
        ],
    }


def point(benefit=0.01, dispersion=0.001, material=0.75,
          direct=3.0, control=100.0, residual=-1.0):
    return {
        "material_selected_fraction": material,
        "whole_decode_stable_effect": {
            "benefit_fraction": benefit,
            "combined_dispersion": dispersion,
            "control": {"median": control},
        },
        "summaries": {
            "direct_selected_saving_ms": {"median": direct},
            "direct_selected_saving_fraction_of_control_decode": {
                "median": direct / control
            },
            "outside_ffn_residual_ms": {"median": residual},
        },
    }


def decision_analysis(default=None):
    default = default or point()
    return {"points": {family: copy.deepcopy(default) for family in oa.FAMILY_ORDER}}


class RunAlignedAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analysis = oa.analyze_operator_family(primary_document())

    def test_exact_fourteen_condition_matrix_passes(self):
        self.assertEqual(self.analysis["status"], "PASS")
        self.assertEqual(set(self.analysis["points"]), set(oa.FAMILY_ORDER))
        self.assertEqual(len(self.analysis["points"]["GUD84"]["run_decode_metrics"]), 21)

    def test_run_aligned_decomposition_is_exact(self):
        row = self.analysis["points"]["UP28"]["run_stable_metrics"][0]
        self.assertAlmostEqual(row["direct_selected_saving_ms"], 2.8)
        self.assertAlmostEqual(row["unselected_ffn_saving_ms"], 0.56)
        self.assertAlmostEqual(row["total_ffn_saving_ms"], 3.36)
        self.assertAlmostEqual(row["observed_decode_saving_ms"], 1.5)
        self.assertAlmostEqual(row["outside_ffn_residual_ms"], -1.86)
        self.assertAlmostEqual(
            row["direct_selected_saving_fraction_of_control_decode"], 0.028)
        self.assertNotIn("cache", row["outside_ffn_residual_interpretation"].lower())

    def test_ratios_are_unclamped(self):
        row = self.analysis["points"]["GATE28"]["run_stable_metrics"][0]
        self.assertAlmostEqual(row["selected_realization"], 1.5 / 2.8)
        self.assertTrue(self.analysis["points"]["GATE28"]["summaries"]
                        ["selected_realization"]["unclamped"])

    def test_median_of_medians_bug_is_rejected_by_run_alignment(self):
        conditions = oa._normalize_document(primary_document(), oa.PRIMARY_PAIRS)
        control, fair = conditions["CONTROL_GU56"], conditions["FAIR_GU56"]
        xs = [1, 100, 100, 1, 1, 100, 100]
        ys = [100, 1, 100, 1, 100, 1, 100]
        for rep in range(oa.EXPECTED_REPS):
            for decode in oa.STABLE_DECODE_INDICES:
                for layer in oa.LAYERS:
                    control[rep]["occurrences"][(layer, "gate_proj", decode)] = 201.0
                    control[rep]["occurrences"][(layer, "up_proj", decode)] = 201.0
                    fair[rep]["occurrences"][(layer, "gate_proj", decode)] = 201.0 - xs[rep] / 28
                    fair[rep]["occurrences"][(layer, "up_proj", decode)] = 201.0 - ys[rep] / 28
        result = oa._analyze_pair("GU56", "CONTROL_GU56", "FAIR_GU56", conditions)
        self.assertAlmostEqual(result["summaries"]["direct_selected_saving_ms"]["median"], 101.0)
        self.assertNotAlmostEqual(result["summaries"]["direct_selected_saving_ms"]["median"], 200.0)

    def test_direct_fraction_is_median_of_run_aligned_ratios(self):
        conditions = oa._normalize_document(primary_document(), oa.PRIMARY_PAIRS)
        control, fair = conditions["CONTROL_UP28"], conditions["FAIR_UP28"]
        direct = [1, 100, 100, 1, 1, 100, 100]
        decode = [100, 10000, 100, 10000, 100, 10000, 100]
        for rep in range(oa.EXPECTED_REPS):
            for d in oa.STABLE_DECODE_INDICES:
                for layer in oa.LAYERS:
                    control[rep]["occurrences"][(layer, "up_proj", d)] = 201.0
                    fair[rep]["occurrences"][(layer, "up_proj", d)] = 201.0 - direct[rep] / 28
                control[rep]["decode_steps"][d] = decode[rep]
                fair[rep]["decode_steps"][d] = decode[rep] - 0.5
        result = oa._analyze_pair("UP28", "CONTROL_UP28", "FAIR_UP28", conditions)
        actual = result["summaries"]["direct_selected_saving_fraction_of_control_decode"]["median"]
        expected = statistics.median(a / b for a, b in zip(direct, decode))
        ratio_of_medians = statistics.median(direct) / statistics.median(decode)
        self.assertAlmostEqual(actual, expected)
        self.assertNotAlmostEqual(actual, ratio_of_medians)

    def test_zero_selected_denominator_is_undefined(self):
        doc = primary_document(selected_delta=0.0, unselected_delta=0.0)
        row = oa.analyze_operator_family(doc)["points"]["UP28"]["run_stable_metrics"][0]
        self.assertIsNone(row["selected_realization"])
        self.assertEqual(row["selected_realization_status"], "UNDEFINED_ZERO_DENOMINATOR")

    def test_negative_total_denominator_is_undefined(self):
        doc = primary_document(selected_delta=-0.10, unselected_delta=-0.01)
        row = oa.analyze_operator_family(doc)["points"]["GUD84"]["run_stable_metrics"][0]
        self.assertIsNone(row["ffn_realization"])
        self.assertEqual(row["ffn_realization_status"], "UNDEFINED_NEGATIVE_DENOMINATOR")

    def test_missing_all_84_event_fails_closed(self):
        doc = primary_document()
        doc["conditions"][0]["runs"][0]["ffn_occurrences"].pop()
        with self.assertRaisesRegex(oa.OperatorAnalysisError, "all-84"):
            oa.analyze_operator_family(doc)

    def test_wrong_selected_family_fails_closed(self):
        doc = primary_document()
        doc["conditions"][0]["selected_roles"] = ["up_proj"]
        with self.assertRaisesRegex(oa.OperatorAnalysisError, "role family mismatch"):
            oa.analyze_operator_family(doc)


class HostOverheadTests(unittest.TestCase):
    def test_per_update_total_and_delta_are_independent_diagnostics(self):
        result = oa.analyze_operator_family(primary_document())["host_policy_overhead"]
        up = result["points"]["UP28"]
        self.assertEqual(up["unit"], "us")
        self.assertAlmostEqual(up["per_update"]["control"]["median"], 1.0)
        self.assertAlmostEqual(up["total_per_run"]["control"]["median"], 140.0)
        self.assertAlmostEqual(up["fair_minus_control_total_per_run_us"]["median"], 14.0)
        self.assertFalse(up["subtracted_from_gpu_timing"])

    def test_unit_mismatch_fails_closed(self):
        doc = primary_document()
        doc["conditions"][0]["runs"][0]["policy_overheads"][0]["unit"] = "ms"
        with self.assertRaisesRegex(oa.OperatorAnalysisError, "unit mismatch"):
            oa.analyze_operator_family(doc)

    def test_update_count_mismatch_fails_closed(self):
        doc = primary_document()
        doc["conditions"][0]["runs"][0]["policy_overheads"].pop()
        with self.assertRaisesRegex(oa.OperatorAnalysisError, "update count mismatch"):
            oa.analyze_operator_family(doc)

    def test_raw_policy_receipt_overhead_adapter(self):
        doc = primary_document()
        for condition in doc["conditions"]:
            condition.pop("selected_roles")
            for run in condition["runs"]:
                normalized = run.pop("policy_overheads")
                run["occurrences"] = run.pop("ffn_occurrences")
                run["policy_receipt"] = {
                    "selected_roles": list(oa.FAMILY_ROLES[
                        condition["condition"].split("_", 1)[1]]),
                    "switches": [
                        {"api_duration_us": row["duration"]} for row in normalized
                    ],
                    "total_api_duration_us": sum(row["duration"] for row in normalized),
                }
        result = oa.analyze_operator_family(doc)
        self.assertEqual(result["status"], "PASS")
        self.assertAlmostEqual(result["host_policy_overhead"]["points"]["UP28"]
                               ["per_update"]["control"]["median"], 1.0)


class FullhintTests(unittest.TestCase):
    def test_false_trigger_forbids_evidence(self):
        with self.assertRaisesRegex(oa.OperatorAnalysisError, "trigger is false"):
            oa.consume_fullhint(point(benefit=0.02), fullhint_document())

    def test_trigger_boundary_is_exact(self):
        self.assertTrue(oa.fullhint_trigger(point(benefit=0.019999, material=0.50)))
        self.assertFalse(oa.fullhint_trigger(point(benefit=0.02, material=0.50)))
        self.assertFalse(oa.fullhint_trigger(point(benefit=0.0, material=0.499999)))

    def test_true_trigger_requires_exact_matrix(self):
        evidence = fullhint_document()
        evidence["conditions"].pop()
        with self.assertRaisesRegex(oa.OperatorAnalysisError, "condition matrix mismatch"):
            oa.consume_fullhint(point(), evidence)

    def test_fullhint_hit_ratio_mismatch_fails(self):
        evidence = fullhint_document()
        evidence["conditions"][0]["hit_ratio"] = 0.5
        with self.assertRaisesRegex(oa.OperatorAnalysisError, "hitRatio=1"):
            oa.consume_fullhint(point(), evidence)

    def test_ncu_trigger_uses_absolute_half_percentage_point_boundary(self):
        result = oa.consume_fullhint(point(benefit=0.01),
                                     fullhint_document(fair_decode=98.5))
        self.assertTrue(result["triggered"])
        self.assertTrue(result["additional_ncu_required"])
        self.assertAlmostEqual(result["absolute_benefit_change_fraction"], 0.005)


class StageDecisionTests(unittest.TestCase):
    def test_unqualified_has_highest_precedence(self):
        analysis = decision_analysis(point(benefit=0.10))
        result = oa.classify_stage(analysis, policy_qualified=False)
        self.assertEqual(result["stage_label"], "POLICY_FAMILY_SCALING_UNQUALIFIED")

    def test_system_relevant_exact_two_percent_boundary(self):
        analysis = decision_analysis(point(benefit=0.0, material=0.0, direct=0.0,
                                           residual=0.0))
        analysis["points"]["UP28"] = point(benefit=0.02, dispersion=0.019)
        result = oa.classify_stage(analysis, policy_qualified=True)
        self.assertEqual(result["stage_label"], "OPERATOR_FAMILY_SYSTEM_RELEVANT")

    def test_equal_dispersion_is_not_positive(self):
        analysis = decision_analysis(point(benefit=0.01, dispersion=0.01,
                                           material=0.0, direct=0.0, residual=0.0))
        result = oa.classify_stage(analysis, policy_qualified=True)
        self.assertEqual(result["stage_label"], "OPERATOR_FAMILY_NOT_SUPPORTED")

    def test_collateral_boundaries_and_negative_residual(self):
        analysis = decision_analysis(point(benefit=0.0, dispersion=0.0,
                                           material=0.0, direct=0.0, residual=0.0))
        analysis["points"]["GUD84"] = point(
            benefit=0.0, dispersion=0.0, material=0.50,
            direct=2.0, control=100.0, residual=-1e-12)
        result = oa.classify_stage(analysis, policy_qualified=True)
        self.assertEqual(result["stage_label"], "OPERATOR_FAMILY_COLLATERAL_LIMITED")
        self.assertNotIn("cache", result["negative_residual_interpretation"].lower())

    def test_positive_but_subthreshold(self):
        analysis = decision_analysis(point(benefit=0.01, dispersion=0.005,
                                           material=0.0, direct=0.0, residual=0.0))
        result = oa.classify_stage(analysis, policy_qualified=True)
        self.assertEqual(result["stage_label"], "OPERATOR_FAMILY_POSITIVE_BUT_SUBTHRESHOLD")


if __name__ == "__main__":
    unittest.main()
