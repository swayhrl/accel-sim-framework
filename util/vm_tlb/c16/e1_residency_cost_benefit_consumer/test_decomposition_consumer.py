#!/usr/bin/env python3
import copy
import unittest

import decomposition_consumer as dc


SHA0 = "0" * 64
SHA1 = "1" * 64
TOKENS = [23578, 11, 323, 3950]


def authority(finals=True):
    result = {
        "layers": [{
            "layer_index": layer,
            "categories": {category: f"model.layers.{layer}.{category}"
                           for category in dc.LAYER_CATEGORIES},
        } for layer in dc.LAYERS],
        "final_stages": [],
    }
    if finals:
        result["final_stages"] = [
            {"category": "final_norm", "semantic_name": "model.norm",
             "cleanly_hookable": True},
            {"category": "output", "semantic_name": "lm_head",
             "cleanly_hookable": True},
        ]
    return result


def run(rep, *, fair=False, residual=0.0, overlap=False, order_flip=False,
        overhead_unit="us"):
    top = []
    # Savings: MLP 2.8 ms, self-attn -1.4 ms, norms -0.28 ms,
    # final -0.14 ms => accounted 0.98 ms. Child savings total 2.8 ms
    # (up 2.8, gate/down 0), hence MLP internal residual is zero.
    delta = {"input_layernorm": -0.005, "self_attn": -0.05,
             "post_attention_layernorm": -0.005, "mlp": 0.10,
             "final_norm": -0.07, "output": -0.07}
    for decode in dc.DECODE_INDICES:
        sequence = [(layer, category) for layer in dc.LAYERS
                    for category in dc.LAYER_CATEGORIES]
        sequence += [(None, "final_norm"), (None, "output")]
        if order_flip and decode == 2:
            sequence[0], sequence[1] = sequence[1], sequence[0]
        cursor = decode * 1000.0
        for pos, (layer, category) in enumerate(sequence):
            duration = 1.0 - (delta[category] if fair else 0.0)
            start = cursor if not (overlap and pos == 1 and decode == 0) else cursor - 0.5
            semantic = (f"model.layers.{layer}.{category}" if layer is not None
                        else {"final_norm": "model.norm", "output": "lm_head"}[category])
            top.append({
                "layer_index": layer, "category": category, "decode_index": decode,
                "semantic_name": semantic, "start_ms": start,
                "end_ms": start + duration, "timing_ms": duration,
                "input_sha256": SHA0, "output_sha256": SHA1,
            })
            cursor += duration + 0.1

    children = []
    for layer in dc.LAYERS:
        for role in dc.ROLES:
            for decode in dc.DECODE_INDICES:
                saving = 0.10 if role == "up_proj" else 0.0
                children.append({
                    "layer_index": layer, "role": role, "decode_index": decode,
                    "timing_ms": 1.0 - (saving if fair else 0.0),
                    "input_sha256": SHA0, "output_sha256": SHA1,
                    "module_name": f"model.layers.{layer}.mlp.{role}",
                    "backend": "WQLinear_GEMM",
                })
    # CONTROL-FAIR = accounted + desired residual.
    fair_decode = 100.0 - (0.98 + residual)
    return {
        "rep": rep, "generated_tokens": list(TOKENS),
        "top_level_occurrences": top, "ffn_child_occurrences": children,
        "decode_steps": [{"decode_index": d,
                          "timing_ms": fair_decode if fair else 100.0,
                          "input_sha256": SHA0, "output_sha256": SHA1}
                         for d in dc.DECODE_INDICES],
        "policy_overheads": [{"update_index": i, "duration": 2.0, "unit": overhead_unit}
                             for i in range(140)],
    }


def document(*, residual=0.0):
    return {
        "schema_version": 1,
        "module_authority": authority(),
        "conditions": [
            {"condition": "CONTROL_16", "runs": [run(i) for i in range(7)]},
            {"condition": "FAIR_16", "runs": [run(i, fair=True, residual=residual)
                                                for i in range(7)]},
        ],
        "budget_pairs": [{"budget_bytes": 16 * 1024 * 1024,
                          "control_condition": "CONTROL_16",
                          "fair_condition": "FAIR_16"}],
    }


class AuthorityTests(unittest.TestCase):
    def test_runtime_authority_passes(self):
        got = dc.validate_module_authority(authority())
        self.assertEqual(len(got["layers"]), 28)
        self.assertEqual(set(got["final_stages"]), {"final_norm", "output"})

    def test_missing_self_attention_fails(self):
        raw = authority()
        del raw["layers"][0]["categories"]["self_attn"]
        with self.assertRaisesRegex(dc.DecompositionError, "missing self_attn"):
            dc.validate_module_authority(raw)

    def test_unhookable_final_not_guessed(self):
        raw = authority()
        raw["final_stages"][0]["cleanly_hookable"] = False
        with self.assertRaisesRegex(dc.DecompositionError, "must not enter"):
            dc.validate_module_authority(raw)


class DecompositionTests(unittest.TestCase):
    def test_exact_accounting_and_no_nested_double_count(self):
        got = dc.analyze_decomposition(document())
        point = got["points"][16 * 1024 * 1024]
        row = point["run_aligned_rows"][0]
        self.assertAlmostEqual(row["DIRECT_UP_SAVING"], 2.8)
        self.assertAlmostEqual(row["TOTAL_FFN_PROJECTION_SAVING"], 2.8)
        self.assertAlmostEqual(row["MLP_TOP_SAVING"], 2.8)
        self.assertAlmostEqual(row["MLP_INTERNAL_RESIDUAL"], 0.0)
        self.assertAlmostEqual(row["SELF_ATTN_SAVING"], -1.4)
        self.assertAlmostEqual(row["NORM_SAVING"], -0.28)
        self.assertAlmostEqual(row["FINAL_STAGE_SAVING"], -0.14)
        self.assertAlmostEqual(row["ACCOUNTED_TOPLEVEL_SAVING"], 0.98)
        self.assertAlmostEqual(row["OBSERVED_DECODE_SAVING"], 0.98)
        self.assertAlmostEqual(row["UNEXPLAINED_RESIDUAL"], 0.0)
        self.assertEqual(got["accounting_rule"],
                         "NONOVERLAPPING_TOPLEVEL_ONLY; FFN_CHILDREN_NESTED_DIAGNOSTIC")

    def test_run_aligned_d1_d3_exact_rows(self):
        point = dc.analyze_decomposition(document())["points"][16 * 1024 * 1024]
        self.assertEqual(len(point["run_aligned_rows"]), 21)
        self.assertEqual({r["decode_index"] for r in point["run_aligned_rows"]}, {1, 2, 3})

    def test_residual_sign_and_qualification_boundary(self):
        positive = dc.analyze_decomposition(document(residual=0.10))["points"][16*1024*1024]
        self.assertAlmostEqual(positive["summaries"]["UNEXPLAINED_RESIDUAL"]["median"], 0.10)
        self.assertTrue(positive["decomposition_qualified"])
        negative = dc.analyze_decomposition(document(residual=-0.11))["points"][16*1024*1024]
        self.assertAlmostEqual(negative["summaries"]["UNEXPLAINED_RESIDUAL"]["median"], -0.11)
        self.assertFalse(negative["decomposition_qualified"])
        self.assertEqual(negative["decomposition_status"], "TOPLEVEL_DECOMPOSITION_INCOMPLETE")

    def test_top_level_overlap_fails(self):
        doc = document()
        doc["conditions"][0]["runs"][0] = run(0, overlap=True)
        with self.assertRaisesRegex(dc.DecompositionError, "overlapping"):
            dc.analyze_decomposition(doc)

    def test_missing_mlp_occurrence_fails(self):
        doc = document()
        doc["conditions"][0]["runs"][0]["top_level_occurrences"] = [
            row for row in doc["conditions"][0]["runs"][0]["top_level_occurrences"]
            if not (row["layer_index"] == 0 and row["category"] == "mlp" and row["decode_index"] == 0)]
        with self.assertRaisesRegex(dc.DecompositionError, "missing self_attn/mlp"):
            dc.analyze_decomposition(doc)

    def test_missing_ffn_child_fails(self):
        doc = document()
        doc["conditions"][0]["runs"][0]["ffn_child_occurrences"].pop()
        with self.assertRaisesRegex(dc.DecompositionError, "all-84"):
            dc.analyze_decomposition(doc)

    def test_semantic_sha_drift_fails(self):
        doc = document()
        doc["conditions"][1]["runs"][6]["ffn_child_occurrences"][0]["output_sha256"] = "2"*64
        with self.assertRaisesRegex(dc.DecompositionError, "semantic SHA"):
            dc.analyze_decomposition(doc)

    def test_token_drift_fails(self):
        doc = document()
        doc["conditions"][0]["runs"][1]["generated_tokens"][0] += 1
        with self.assertRaisesRegex(dc.DecompositionError, "token sequence drift"):
            dc.analyze_decomposition(doc)

    def test_cross_run_order_drift_fails(self):
        doc = document()
        doc["conditions"][0]["runs"][1] = run(1, order_flip=True)
        with self.assertRaisesRegex(dc.DecompositionError, "call order drift"):
            dc.analyze_decomposition(doc)

    def test_host_api_us_is_not_subtracted(self):
        got = dc.analyze_decomposition(document())
        host = got["host_policy_overhead"]["FAIR_16"]
        self.assertEqual(host["unit"], "us")
        self.assertAlmostEqual(host["total_per_run"]["median"], 280.0)
        self.assertFalse(host["subtracted_from_gpu_timing"])

    def test_host_api_unit_mismatch_fails(self):
        doc = document()
        doc["conditions"][0]["runs"][0]["policy_overheads"][0]["unit"] = "ms"
        with self.assertRaisesRegex(dc.DecompositionError, "unit mismatch"):
            dc.analyze_decomposition(doc)


class DecisionTests(unittest.TestCase):
    def analysis(self, *, benefit=0.0, dispersion=0.01, qualified=True,
                 localization=0.0, negative_offset=1.0):
        return {"points": {1: {
            "decomposition_qualified": qualified,
            "whole_decode_stable_effect": {
                "benefit_fraction": benefit,
                "combined_dispersion": dispersion,
                "positive_beyond_dispersion": benefit > 0 and benefit > dispersion,
                "material": benefit >= 0.02 and benefit > dispersion,
            },
            "negative_offset_localization": {"median": localization},
            "summaries": {"NEGATIVE_OFFSET_RELATIVE_TO_DIRECT_UP":
                          {"median": negative_offset}},
        }}}

    def test_decision_precedence_unqualified(self):
        got = dc.classify_stage(self.analysis(benefit=0.10), policy_qualified=False)
        self.assertEqual(got["stage_label"], "RESIDENCY_COST_DIAGNOSTIC_UNQUALIFIED")

    def test_system_relevant_exact_boundary(self):
        got = dc.classify_stage(self.analysis(benefit=0.02, dispersion=0.019))
        self.assertEqual(got["stage_label"], "RESIDENCY_COST_AWARE_SYSTEM_RELEVANT")

    def test_positive_subthreshold(self):
        got = dc.classify_stage(self.analysis(benefit=0.019, dispersion=0.01))
        self.assertEqual(got["stage_label"], "RESIDENCY_COST_AWARE_POSITIVE_SUBTHRESHOLD")

    def test_localization_exact_eighty_percent(self):
        got = dc.classify_stage(self.analysis(localization=0.80))
        self.assertEqual(got["stage_label"], "RESIDENCY_OFFSET_LOCALIZED")
        self.assertFalse(got["simulator_auto_authorized"])

    def test_weak_when_no_stronger_case(self):
        got = dc.classify_stage(self.analysis(localization=0.79))
        self.assertEqual(got["stage_label"], "RESIDENCY_SYSTEM_CASE_WEAK")


if __name__ == "__main__":
    unittest.main()
