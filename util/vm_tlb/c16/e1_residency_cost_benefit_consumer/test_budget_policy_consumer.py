#!/usr/bin/env python3
import copy
import unittest

import budget_policy_consumer as bp


PREFIX = "a" * 64
INPUT_SHA = "1" * 64
OUTPUT_SHA = "2" * 64
RUNTIME_MAX = 48 * 1024 * 1024
ACTUALS = {
    "B8": 8 * 1024 * 1024,
    "B16": 16 * 1024 * 1024,
    "B24": 24 * 1024 * 1024,
    "BFULL": 36 * 1024 * 1024,
}


def module_size(role):
    return bp.UP_QWEIGHT_BYTES if role == "up_proj" else 1_048_576


def modules():
    return [
        {"layer_index": layer, "role": role,
         "module_class": bp.EXPECTED_MODULE_CLASS,
         "implementation": bp.EXPECTED_IMPLEMENTATION,
         "backend": "autoawq", "qweight_bytes": module_size(role),
         "qweight_shape": [32, 64], "contiguous": True}
        for layer in bp.LAYERS for role in bp.ROLES
    ]


def order(phase):
    # Deliberately not an assumed gate/up/down order.
    values = [(layer, role) for layer in reversed(bp.LAYERS)
              for role in ("up_proj", "down_proj", "gate_proj")]
    shift = bp.PHASES.index(phase) * 11
    return values[shift:] + values[:shift]


def natural_order():
    return {
        phase: [{"natural_order_index": i, "layer_index": key[0], "role": key[1]}
                for i, key in enumerate(order(phase))]
        for phase in bp.PHASES
    }


def region(layer, role, process_number):
    role_number = bp.ROLES.index(role)
    pointer = 0x100000000 + process_number * 0x100000000 + layer * 0x1000000 + role_number * 0x200000
    size = module_size(role)
    return {"pointer": pointer, "bytes": size, "span_start": pointer,
            "span_end": pointer + size, "contiguous": True}


def authority_rows():
    return [
        {"layer_index": layer, "role": role, "decode_index": d,
         "generated_token_id": bp.EXPECTED_TOKENS[d],
         "input_sha256": INPUT_SHA, "output_sha256": OUTPUT_SHA}
        for layer in bp.LAYERS for role in bp.ROLES for d in bp.DECODE_INDICES
    ]


def top_authority():
    rows = [
        {"layer_index": layer, "category": category, "decode_index": d,
         "generated_token_id": bp.EXPECTED_TOKENS[d],
         "input_sha256": INPUT_SHA, "output_sha256": OUTPUT_SHA}
        for layer in bp.LAYERS for category in bp.CORE_TOPLEVEL for d in bp.DECODE_INDICES
    ]
    rows.extend(
        {"layer_index": None, "category": category, "decode_index": d,
         "generated_token_id": bp.EXPECTED_TOKENS[d],
         "input_sha256": INPUT_SHA, "output_sha256": OUTPUT_SHA}
        for category in bp.OPTIONAL_FINAL for d in bp.DECODE_INDICES
    )
    return rows


def reset():
    return {"status": "PASS", "performed": True,
            "operation": "cudaCtxResetPersistingL2Cache"}


def run(condition, rep, process_number):
    mode, _, budget = condition.split("_", 2)
    requested = bp.BUDGETS[budget]
    ratio = min(1.0, requested / bp.FULL_UP28_BYTES)
    calls, switches, durations = {}, [], []
    for phase in bp.PHASES:
        timeline, phase_calls = 1, []
        for i, (layer, role) in enumerate(order(phase)):
            qweight = region(layer, role, process_number)
            if role == "up_proj":
                duration = 1.0 + i / 10000
                switches.append({"phase": phase, "attached_natural_order_index": i,
                    "layer_index": layer, "role": role,
                    "timeline_event_index": timeline,
                    "base_pointer": qweight["pointer"], "num_bytes": qweight["bytes"],
                    "hit_ratio": ratio,
                    "hit_prop": "NORMAL" if mode == "CONTROL" else "PERSISTING",
                    "miss_prop": "NORMAL" if mode == "CONTROL" else "STREAMING",
                    "target_persisting": mode == "FAIR", "stream_identity": "stream-0",
                    "reset_performed": False, "api_duration_us": duration})
                durations.append(duration)
                timeline += 1
            phase_calls.append({"natural_order_index": i, "layer_index": layer, "role": role,
                "module_class": bp.EXPECTED_MODULE_CLASS,
                "implementation": bp.EXPECTED_IMPLEMENTATION, "backend": "autoawq",
                "qweight": qweight, "timeline_event_index": timeline})
            timeline += 1
        calls[phase] = phase_calls
    policy = {"status": "PASS", "condition": condition, "budget_name": budget,
        "requested_setaside_bytes": requested, "actual_setaside_bytes": ACTUALS[budget],
        "query_back_actual_setaside_bytes": ACTUALS[budget],
        "runtime_max_setaside_bytes": RUNTIME_MAX,
        "selected_modules": [{"layer_index": layer, "role": "up_proj"} for layer in bp.LAYERS],
        "stream_identity": "stream-0", "reset_before": reset(), "reset_after": reset(),
        "other_reset_events": [], "switches": switches,
        "total_api_duration_us": sum(durations)}
    occurrences = [
        {**row, "module_class": bp.EXPECTED_MODULE_CLASS,
         "implementation": bp.EXPECTED_IMPLEMENTATION, "backend": "autoawq",
         "timing_ms": 0.01 + row["layer_index"] / 100000 +
                      bp.ROLES.index(row["role"]) / 1000000 + rep / 10000000}
        for row in authority_rows()
    ]
    top = [
        {**row, "timing_ms": 0.02 + (row["layer_index"] or 0) / 100000 + rep / 10000000}
        for row in top_authority()
    ]
    decode = [
        {"decode_index": d, "generated_token_id": bp.EXPECTED_TOKENS[d],
         "input_sha256": INPUT_SHA, "output_sha256": OUTPUT_SHA,
         "timing_ms": 20 + d / 10 + rep / 1000}
        for d in bp.DECODE_INDICES
    ]
    return {"rep": rep, "fresh_process_id": f"process-{process_number}",
            "prefix_token_sha256": PREFIX, "generated_token_ids": list(bp.EXPECTED_TOKENS),
            "natural_calls": calls, "policy_receipt": policy,
            "policy_api_duration_us": sum(durations), "occurrences": occurrences,
            "top_level_occurrences": top, "decode_steps": decode}


def document():
    process = 0
    conditions = []
    for condition in bp.CONDITIONS:
        runs = []
        for rep in range(bp.EXPECTED_REPS):
            process += 1
            runs.append(run(condition, rep, process))
        conditions.append({"condition": condition, "runs": runs})
    return {"schema_version": 1, "accepted_prefix_sha256": PREFIX,
            "generated_token_ids": list(bp.EXPECTED_TOKENS),
            "runtime_max_setaside_bytes": RUNTIME_MAX,
            "budget_authority": [
                {"budget_name": name, "requested_bytes": requested,
                 "runtime_actual_setaside_bytes": ACTUALS[name],
                 "runtime_max_setaside_bytes": RUNTIME_MAX}
                for name, requested in bp.BUDGETS.items()],
            "module_authority": modules(), "natural_order": natural_order(),
            "occurrence_authority": authority_rows(),
            "top_level_authority": top_authority(),
            "decode_authority": [
                {"decode_index": d, "generated_token_id": bp.EXPECTED_TOKENS[d],
                 "input_sha256": INPUT_SHA, "output_sha256": OUTPUT_SHA}
                for d in bp.DECODE_INDICES],
            "conditions": conditions}


class BudgetPolicyPassTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = bp.consume_budget_policy_runs(document())

    def test_complete_matrix_passes(self):
        self.assertEqual(self.result["condition_count"], 8)
        self.assertEqual(self.result["fresh_process_count"], 56)
        self.assertEqual(len(self.result["run_aligned_points"]), 56)

    def test_budget_querybacks_are_preserved_without_alignment_claim(self):
        self.assertEqual(self.result["budget_authority"]["BFULL"]["runtime_actual_setaside_bytes"],
                         36 * 1024 * 1024)
        self.assertTrue(self.result["no_alignment_law_inferred"])

    def test_native_timing_and_api_overhead_are_passed_through(self):
        point = self.result["run_aligned_points"][0]
        self.assertEqual(len(point["ffn_child_timing"]), 336)
        self.assertEqual(len(point["top_level_timing"]), 456)
        self.assertEqual(len(point["decode_step_ms"]), 4)
        self.assertEqual(len(point["policy_api_update_durations_us"]), 140)

    def test_hit_ratio_is_budget_scaled_and_unclamped_only_at_one(self):
        by_budget = {}
        for point in self.result["run_aligned_points"]:
            by_budget.setdefault(point["budget_name"], point["hit_ratio"])
        self.assertAlmostEqual(by_budget["B8"], bp.BUDGETS["B8"] / bp.FULL_UP28_BYTES)
        self.assertEqual(by_budget["BFULL"], 1.0)


class BudgetPolicyAdversarialTests(unittest.TestCase):
    def test_wrong_budget_fails(self):
        raw = document(); raw["budget_authority"][0]["requested_bytes"] += 1
        with self.assertRaisesRegex(bp.BudgetPolicyError, "requested budget"):
            bp.consume_budget_policy_runs(raw)

    def test_runtime_queryback_drift_fails(self):
        raw = document()
        raw["conditions"][0]["runs"][0]["policy_receipt"]["query_back_actual_setaside_bytes"] += 1
        with self.assertRaisesRegex(bp.BudgetPolicyError, "query-back"):
            bp.consume_budget_policy_runs(raw)

    def test_runtime_actual_above_max_fails(self):
        raw = document(); raw["budget_authority"][0]["runtime_actual_setaside_bytes"] = RUNTIME_MAX + 1
        with self.assertRaisesRegex(bp.BudgetPolicyError, "exceeds"):
            bp.consume_budget_policy_runs(raw)

    def test_wrong_hit_ratio_fails(self):
        raw = document(); raw["conditions"][1]["runs"][0]["policy_receipt"]["switches"][0]["hit_ratio"] = 0.5
        with self.assertRaisesRegex(bp.BudgetPolicyError, "hitRatio"):
            bp.consume_budget_policy_runs(raw)

    def test_missing_reset_fails(self):
        raw = document(); del raw["conditions"][2]["runs"][0]["policy_receipt"]["reset_after"]
        with self.assertRaisesRegex(bp.BudgetPolicyError, "reset_after"):
            bp.consume_budget_policy_runs(raw)

    def test_missing_reset_inventory_fails(self):
        raw = document(); del raw["conditions"][2]["runs"][0]["policy_receipt"]["other_reset_events"]
        with self.assertRaisesRegex(bp.BudgetPolicyError, "before/after"):
            bp.consume_budget_policy_runs(raw)

    def test_in_run_reset_fails(self):
        raw = document()
        raw["conditions"][3]["runs"][0]["policy_receipt"]["switches"][0]["reset_performed"] = True
        with self.assertRaisesRegex(bp.BudgetPolicyError, "in-run reset"):
            bp.consume_budget_policy_runs(raw)

    def test_token_drift_fails(self):
        raw = document(); raw["conditions"][4]["runs"][0]["generated_token_ids"][2] += 1
        with self.assertRaisesRegex(bp.BudgetPolicyError, "token sequence drift"):
            bp.consume_budget_policy_runs(raw)

    def test_prefix_sha_drift_fails(self):
        raw = document(); raw["conditions"][5]["runs"][0]["prefix_token_sha256"] = "b" * 64
        with self.assertRaisesRegex(bp.BudgetPolicyError, "prefix SHA drift"):
            bp.consume_budget_policy_runs(raw)

    def test_missing_ffn_event_fails(self):
        raw = document(); raw["conditions"][6]["runs"][0]["occurrences"].pop()
        with self.assertRaisesRegex(bp.BudgetPolicyError, "all-84"):
            bp.consume_budget_policy_runs(raw)

    def test_missing_top_level_event_fails(self):
        raw = document(); raw["conditions"][7]["runs"][0]["top_level_occurrences"].pop()
        with self.assertRaisesRegex(bp.BudgetPolicyError, "top-level"):
            bp.consume_budget_policy_runs(raw)

    def test_missing_decode_event_fails(self):
        raw = document(); raw["conditions"][0]["runs"][0]["decode_steps"].pop()
        with self.assertRaisesRegex(bp.BudgetPolicyError, "decode timing"):
            bp.consume_budget_policy_runs(raw)

    def test_wrong_natural_attachment_fails(self):
        raw = document()
        raw["conditions"][1]["runs"][0]["policy_receipt"]["switches"][0]["attached_natural_order_index"] += 1
        with self.assertRaisesRegex(bp.BudgetPolicyError, "attachment"):
            bp.consume_budget_policy_runs(raw)

    def test_wrong_exact_window_fails(self):
        raw = document(); raw["conditions"][2]["runs"][0]["policy_receipt"]["switches"][0]["num_bytes"] -= 1
        with self.assertRaisesRegex(bp.BudgetPolicyError, "exact full qweight"):
            bp.consume_budget_policy_runs(raw)

    def test_ffn_sha_drift_fails(self):
        raw = document(); raw["conditions"][3]["runs"][0]["occurrences"][0]["input_sha256"] = "3" * 64
        with self.assertRaisesRegex(bp.BudgetPolicyError, "FFN child SHA drift"):
            bp.consume_budget_policy_runs(raw)

    def test_top_level_sha_drift_fails(self):
        raw = document(); raw["conditions"][4]["runs"][0]["top_level_occurrences"][0]["output_sha256"] = "4" * 64
        with self.assertRaisesRegex(bp.BudgetPolicyError, "top-level SHA drift"):
            bp.consume_budget_policy_runs(raw)

    def test_final_stage_layer_identity_drift_fails(self):
        raw = document(); raw["conditions"][4]["runs"][0]["top_level_occurrences"][-1]["layer_index"] = 27
        with self.assertRaisesRegex(bp.BudgetPolicyError, "null layer_index"):
            bp.consume_budget_policy_runs(raw)

    def test_missing_condition_fails(self):
        raw = document(); raw["conditions"].pop()
        with self.assertRaisesRegex(bp.BudgetPolicyError, "eight-condition"):
            bp.consume_budget_policy_runs(raw)

    def test_fresh_process_reuse_fails(self):
        raw = document()
        raw["conditions"][0]["runs"][1]["fresh_process_id"] = raw["conditions"][0]["runs"][0]["fresh_process_id"]
        with self.assertRaisesRegex(bp.BudgetPolicyError, "fresh process reused"):
            bp.consume_budget_policy_runs(raw)

    def test_control_policy_drift_fails(self):
        raw = document(); raw["conditions"][0]["runs"][0]["policy_receipt"]["switches"][0]["hit_prop"] = "PERSISTING"
        with self.assertRaisesRegex(bp.BudgetPolicyError, "CONTROL policy"):
            bp.consume_budget_policy_runs(raw)


if __name__ == "__main__":
    unittest.main()
