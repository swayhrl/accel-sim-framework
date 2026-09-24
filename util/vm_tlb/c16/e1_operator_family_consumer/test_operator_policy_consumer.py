#!/usr/bin/env python3
import copy
import unittest

import operator_policy_consumer as op


PREFIX = "a" * 64
INPUT_SHA = "1" * 64
OUTPUT_SHA = "2" * 64


def qweight(layer, role):
    role_number = {"gate_proj": 0, "up_proj": 1, "down_proj": 2}[role]
    pointer = 0x10000000 + layer * 0x100000 + role_number * 0x20000
    size = 4096 + role_number * 512
    return {"pointer": pointer, "bytes": size, "span_start": pointer,
            "span_end": pointer + size, "shape": [32, 64], "contiguous": True}


def modules():
    return [{"layer_index": layer, "role": role,
             "module_class": op.EXPECTED_MODULE_CLASS,
             "implementation": op.EXPECTED_IMPLEMENTATION,
             "backend": "autoawq", "qweight": qweight(layer, role)}
            for layer in op.LAYERS for role in op.ROLES]


def arbitrary_order(phase):
    # Intentionally not gate/up/down.  Each phase can have its own raw-derived order.
    role_order = ("up_proj", "down_proj", "gate_proj")
    values = [(layer, role) for layer in reversed(op.LAYERS) for role in role_order]
    rotation = op.PHASES.index(phase) * 7
    return values[rotation:] + values[:rotation]


def natural_row(index, key, timeline=None):
    layer, role = key
    row = {"natural_order_index": index, "layer_index": layer, "role": role,
           "module_class": op.EXPECTED_MODULE_CLASS,
           "implementation": op.EXPECTED_IMPLEMENTATION,
           "backend": "autoawq", "qweight": qweight(layer, role)}
    if timeline is not None:
        row["timeline_event_index"] = timeline
    return row


def natural_authority():
    return {"schema_version": 1, "accepted_prefix_sha256": PREFIX,
            "generated_token_ids": list(op.EXPECTED_TOKENS), "module_authority": modules(),
            "probe_runs": [
                {"rep": rep, "fresh_process_id": f"probe-{rep}",
                 "prefix_token_sha256": PREFIX,
                 "generated_token_ids": list(op.EXPECTED_TOKENS),
                 "phases": {phase: [natural_row(i, key) for i, key in enumerate(arbitrary_order(phase))]
                            for phase in op.PHASES}}
                for rep in range(op.EXPECTED_REPS)]}


def reset():
    return {"status": "PASS", "performed": True,
            "operation": "cudaCtxResetPersistingL2Cache"}


def run_calls_and_policy(condition):
    mode, family = condition.split("_", 1)
    roles = op.CONDITION_SETS[family]
    selected = {(layer, role) for layer in op.LAYERS for role in roles}
    calls, switches, durations = {}, [], []
    for phase in op.PHASES:
        timeline, phase_calls = 1, []
        for natural_index, key in enumerate(arbitrary_order(phase)):
            if key in selected:
                duration = 1.0 + natural_index / 10000
                switches.append({"phase": phase,
                    "attached_natural_order_index": natural_index,
                    "layer_index": key[0], "role": key[1],
                    "timeline_event_index": timeline,
                    "base_pointer": qweight(*key)["pointer"],
                    "num_bytes": qweight(*key)["bytes"],
                    "hit_ratio": 1 / len(selected),
                    "hit_prop": "NORMAL" if mode == "CONTROL" else "PERSISTING",
                    "miss_prop": "NORMAL" if mode == "CONTROL" else "STREAMING",
                    "target_persisting": mode == "FAIR",
                    "stream_identity": "stream-0", "reset_performed": False,
                    "api_duration_us": duration})
                durations.append(duration)
                timeline += 1
            phase_calls.append(natural_row(natural_index, key, timeline))
            timeline += 1
        calls[phase] = phase_calls
    policy = {"status": "PASS", "condition": condition,
              "selected_roles": list(roles),
              "selected_modules": [{"layer_index": layer, "role": role}
                                   for layer, role in sorted(selected)],
              "requested_setaside_bytes": op.REQUESTED_SETASIDE_BYTES,
              "actual_setaside_bytes": op.ACTUAL_SETASIDE_BYTES,
              "stream_identity": "stream-0", "reset_before": reset(),
              "switches": switches, "reset_after": reset(), "other_reset_events": [],
              "total_api_duration_us": sum(durations)}
    return calls, policy


def occurrence_authority():
    return [{"layer_index": layer, "role": role, "decode_index": d,
             "generated_token_id": op.EXPECTED_TOKENS[d],
             "input_sha256": INPUT_SHA, "output_sha256": OUTPUT_SHA}
            for layer in op.LAYERS for role in op.ROLES for d in op.DECODE_INDICES]


def run(condition, rep, process):
    calls, policy = run_calls_and_policy(condition)
    occurrences = []
    for authority in occurrence_authority():
        layer, role, d = authority["layer_index"], authority["role"], authority["decode_index"]
        occurrences.append({**authority,
            "module_class": op.EXPECTED_MODULE_CLASS,
            "implementation": op.EXPECTED_IMPLEMENTATION, "backend": "autoawq",
            "qweight": qweight(layer, role),
            "timing_ms": 0.01 + layer / 100000 + op.ROLES.index(role) / 1000000 + rep / 10000000})
    return {"rep": rep, "fresh_process_id": process,
            "prefix_token_sha256": PREFIX,
            "generated_token_ids": list(op.EXPECTED_TOKENS),
            "natural_calls": calls, "policy_receipt": policy,
            "policy_api_duration_us": policy["total_api_duration_us"],
            "all_84_event": {"status": "PASS",
                             "decode_phase_counts": {phase: 84 for phase in op.DECODE_PHASES}},
            "decode_steps": [{"decode_index": d, "generated_token_id": op.EXPECTED_TOKENS[d],
                              "timing_ms": 20 + d / 10 + rep / 1000}
                             for d in op.DECODE_INDICES],
            "occurrences": occurrences}


def document():
    conditions, process = [], 0
    for condition in op.CONDITIONS:
        runs = []
        for rep in range(op.EXPECTED_REPS):
            process += 1
            runs.append(run(condition, rep, f"condition-{process}"))
        conditions.append({"condition": condition, "runs": runs})
    return {"schema_version": 1, "accepted_prefix_sha256": PREFIX,
            "generated_token_ids": list(op.EXPECTED_TOKENS),
            "module_authority": modules(),
            "natural_call_order_authority": natural_authority(),
            "occurrence_authority": occurrence_authority(), "conditions": conditions}


class NaturalOrderAndModuleTests(unittest.TestCase):
    def test_raw_arbitrary_order_is_accepted_without_role_order_assumption(self):
        out = op.consume_natural_call_order_authority(natural_authority())
        self.assertEqual(out["module_count"], 84)
        self.assertEqual(out["derived_order"]["D0"][0]["role"], "down_proj")

    def test_wrong_order_in_later_fresh_process_fails(self):
        raw = natural_authority()
        rows = raw["probe_runs"][1]["phases"]["D2"]
        rows[0], rows[1] = rows[1], rows[0]
        rows[0]["natural_order_index"], rows[1]["natural_order_index"] = 0, 1
        with self.assertRaisesRegex(op.OperatorPolicyError, "order drift"):
            op.consume_natural_call_order_authority(raw)

    def test_missing_module_fails(self):
        raw = natural_authority(); raw["module_authority"].pop()
        with self.assertRaisesRegex(op.OperatorPolicyError, "missing role/module"):
            op.consume_natural_call_order_authority(raw)

    def test_role_drift_fails(self):
        raw = natural_authority(); raw["module_authority"][0]["role"] = "up_proj"
        with self.assertRaisesRegex(op.OperatorPolicyError, "duplicate module"):
            op.consume_natural_call_order_authority(raw)

    def test_backend_drift_fails(self):
        raw = natural_authority(); raw["probe_runs"][0]["phases"]["D0"][0]["backend"] = "torch"
        with self.assertRaisesRegex(op.OperatorPolicyError, "identity drift"):
            op.consume_natural_call_order_authority(raw)

    def test_qweight_span_drift_fails(self):
        raw = natural_authority(); raw["module_authority"][0]["qweight"]["span_end"] += 1
        with self.assertRaisesRegex(op.OperatorPolicyError, "span drift"):
            op.consume_natural_call_order_authority(raw)

    def test_probe_token_drift_fails(self):
        raw = natural_authority(); raw["probe_runs"][0]["generated_token_ids"][3] += 1
        with self.assertRaisesRegex(op.OperatorPolicyError, "token sequence drift"):
            op.consume_natural_call_order_authority(raw)

    def test_probe_prefix_sha_drift_fails(self):
        raw = natural_authority(); raw["probe_runs"][0]["prefix_token_sha256"] = "b" * 64
        with self.assertRaisesRegex(op.OperatorPolicyError, "prefix SHA drift"):
            op.consume_natural_call_order_authority(raw)


class PolicyMatrixTests(unittest.TestCase):
    def setUp(self):
        self.doc = document()

    def test_complete_14_by_7_matrix_passes(self):
        out = op.consume_operator_policy_runs(self.doc)
        self.assertEqual(out["condition_count"], 14)
        self.assertEqual(out["fresh_process_count"], 98)
        self.assertEqual(len(out["run_aligned_points"]), 98)
        self.assertEqual(len(out["module_timing_statistics"]), 14 * 84)
        self.assertEqual(len(out["run_aligned_points"][0]["policy_api_update_durations_us"]), 28 * 5)

    def test_wrong_selected_family_fails(self):
        self.doc["conditions"][0]["runs"][0]["policy_receipt"]["selected_roles"] = ["up_proj"]
        with self.assertRaisesRegex(op.OperatorPolicyError, "selected family"):
            op.consume_operator_policy_runs(self.doc)

    def test_wrong_selected_module_set_fails(self):
        self.doc["conditions"][0]["runs"][0]["policy_receipt"]["selected_modules"].pop()
        with self.assertRaisesRegex(op.OperatorPolicyError, "selected module set"):
            op.consume_operator_policy_runs(self.doc)

    def test_wrong_update_attachment_fails(self):
        switch = self.doc["conditions"][0]["runs"][0]["policy_receipt"]["switches"][0]
        switch["attached_natural_order_index"] += 1
        with self.assertRaisesRegex(op.OperatorPolicyError, "update attachment"):
            op.consume_operator_policy_runs(self.doc)

    def test_wrong_hit_ratio_fails(self):
        self.doc["conditions"][1]["runs"][0]["policy_receipt"]["switches"][0]["hit_ratio"] = .5
        with self.assertRaisesRegex(op.OperatorPolicyError, "1/K"):
            op.consume_operator_policy_runs(self.doc)

    def test_actual_setaside_drift_fails(self):
        self.doc["conditions"][2]["runs"][0]["policy_receipt"]["actual_setaside_bytes"] -= 1
        with self.assertRaisesRegex(op.OperatorPolicyError, "actual set-aside"):
            op.consume_operator_policy_runs(self.doc)

    def test_in_run_reset_fails(self):
        self.doc["conditions"][3]["runs"][0]["policy_receipt"]["switches"][0]["reset_performed"] = True
        with self.assertRaisesRegex(op.OperatorPolicyError, "in-run reset"):
            op.consume_operator_policy_runs(self.doc)

    def test_control_policy_drift_fails(self):
        self.doc["conditions"][0]["runs"][0]["policy_receipt"]["switches"][0]["hit_prop"] = "PERSISTING"
        with self.assertRaisesRegex(op.OperatorPolicyError, "CONTROL policy"):
            op.consume_operator_policy_runs(self.doc)

    def test_fair_policy_drift_fails(self):
        self.doc["conditions"][1]["runs"][0]["policy_receipt"]["switches"][0]["miss_prop"] = "NORMAL"
        with self.assertRaisesRegex(op.OperatorPolicyError, "FAIR policy"):
            op.consume_operator_policy_runs(self.doc)

    def test_token_drift_fails(self):
        self.doc["conditions"][4]["runs"][0]["generated_token_ids"][0] += 1
        with self.assertRaisesRegex(op.OperatorPolicyError, "token sequence drift"):
            op.consume_operator_policy_runs(self.doc)

    def test_sha_drift_fails(self):
        self.doc["conditions"][5]["runs"][0]["occurrences"][0]["input_sha256"] = "3" * 64
        with self.assertRaisesRegex(op.OperatorPolicyError, "SHA drift"):
            op.consume_operator_policy_runs(self.doc)

    def test_missing_all84_event_fails(self):
        del self.doc["conditions"][6]["runs"][0]["all_84_event"]
        with self.assertRaisesRegex(op.OperatorPolicyError, "all-84"):
            op.consume_operator_policy_runs(self.doc)

    def test_missing_timing_event_fails(self):
        self.doc["conditions"][7]["runs"][0]["occurrences"].pop()
        with self.assertRaisesRegex(op.OperatorPolicyError, "all-84 D0-D3"):
            op.consume_operator_policy_runs(self.doc)

    def test_duplicate_rep_fails(self):
        self.doc["conditions"][8]["runs"][1]["rep"] = 0
        with self.assertRaisesRegex(op.OperatorPolicyError, "duplicate condition rep"):
            op.consume_operator_policy_runs(self.doc)

    def test_missing_condition_fails(self):
        self.doc["conditions"].pop()
        with self.assertRaisesRegex(op.OperatorPolicyError, "14-condition"):
            op.consume_operator_policy_runs(self.doc)

    def test_api_duration_mismatch_fails(self):
        self.doc["conditions"][9]["runs"][0]["policy_api_duration_us"] += 1
        with self.assertRaisesRegex(op.OperatorPolicyError, "API duration mismatch"):
            op.consume_operator_policy_runs(self.doc)

    def test_fresh_process_reuse_fails(self):
        self.doc["conditions"][10]["runs"][1]["fresh_process_id"] = \
            self.doc["conditions"][10]["runs"][0]["fresh_process_id"]
        with self.assertRaisesRegex(op.OperatorPolicyError, "fresh process reused"):
            op.consume_operator_policy_runs(self.doc)

    def test_unrecorded_timeline_update_fails(self):
        calls = self.doc["conditions"][11]["runs"][0]["natural_calls"]["D1"]
        calls[-1]["timeline_event_index"] += 1
        with self.assertRaisesRegex(op.OperatorPolicyError, "timeline|immediately before"):
            op.consume_operator_policy_runs(self.doc)


if __name__ == "__main__":
    unittest.main()
