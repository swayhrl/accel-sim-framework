#!/usr/bin/env python3
import copy
import math
import unittest

import census_policy_consumer as cp


S1, S2, PREFIX = "1" * 64, "2" * 64, "a" * 64


def qweight(layer, role="up_proj"):
    role_offset = {"gate_proj": 0, "up_proj": 1, "down_proj": 2}[role]
    return {"pointer": 0x100000 + layer * 0x10000 + role_offset * 0x1000,
            "bytes": 1024 + role_offset * 128, "shape": [8, 16], "contiguous": True}


def modules(*, unsupported_role=None):
    return [{"layer_index": layer, "role": role,
             "supported": role != unsupported_role,
             "module_class": cp.EXPECTED_MODULE_CLASS,
             "backend": "autoawq", "implementation": cp.EXPECTED_IMPLEMENTATION,
             "qweight": qweight(layer, role)}
            for layer in cp.LAYERS for role in cp.ROLES]


def census_document(*, unsupported_role=None):
    mods = modules(unsupported_role=unsupported_role)
    authority = [{"layer_index": layer, "role": role, "decode_index": d,
                  "generated_token_id": cp.EXPECTED_TOKENS[d],
                  "input_sha256": S1, "output_sha256": S2}
                 for layer in cp.LAYERS for role in cp.ROLES if role != unsupported_role
                 for d in cp.DECODE_INDICES]
    runs = []
    by_key = {(x["layer_index"], x["role"]): x for x in mods}
    for rep in range(cp.EXPECTED_REPS):
        occurrences = []
        for auth in authority:
            module = by_key[(auth["layer_index"], auth["role"])]
            occurrences.append({**auth, "module_class": module["module_class"],
                "backend": module["backend"], "implementation": module["implementation"],
                "qweight": copy.deepcopy(module["qweight"]),
                "timing_ms": 0.1 + auth["layer_index"] / 10000 + rep / 100000})
        runs.append({"rep": rep, "fresh_process_id": f"census-{rep}",
            "prefix_token_sha256": PREFIX, "generated_token_ids": list(cp.EXPECTED_TOKENS),
            "decode_steps": [{"decode_index": d, "generated_token_id": cp.EXPECTED_TOKENS[d],
                              "timing_ms": 20 + d / 10 + rep / 1000}
                             for d in cp.DECODE_INDICES],
            "occurrences": occurrences})
    return {"schema_version": 1, "accepted_prefix_sha256": PREFIX,
            "generated_token_ids": list(cp.EXPECTED_TOKENS),
            "module_authority": mods, "occurrence_authority": authority, "runs": runs}


def manifest():
    return {"status": "FROZEN_BEFORE_COVERAGE_PRODUCER",
            "no_post_data_selection": True, "selected_after_observing_data": False,
            "selection_order": list(cp.SELECTION_ORDER),
            "sets": {name: list(value) for name, value in cp.LAYER_SETS.items()}}


def reset(index):
    return {"status": "PASS", "performed": True,
            "operation": "cudaCtxResetPersistingL2Cache", "event_index": index}


def policy(condition):
    mode, set_name = condition.split("_", 1)
    selected, switches = cp.LAYER_SETS[set_name], []
    for i, (phase, layer) in enumerate(((p, l) for p in cp.PHASES for l in sorted(selected)), 1):
        switches.append({"sequence_index": i, "phase": phase, "layer_index": layer,
            "role": "up_proj", "base_pointer": qweight(layer)["pointer"],
            "num_bytes": qweight(layer)["bytes"], "hit_ratio": 1 / len(selected),
            "hit_prop": "NORMAL" if mode == "CONTROL" else "PERSISTING",
            "miss_prop": "NORMAL" if mode == "CONTROL" else "STREAMING",
            "target_persisting": mode == "FAIR", "stream_identity": "stream-0",
            "reset_performed": False, "api_duration_us": 1.0 + i / 1000})
    return {"status": "PASS", "condition": condition, "selected_layers": list(selected),
            "requested_setaside_bytes": cp.REQUESTED_SETASIDE_BYTES,
            "actual_setaside_bytes": cp.ACTUAL_SETASIDE_BYTES,
            "stream_identity": "stream-0", "reset_before": reset(0), "switches": switches,
            "reset_after": reset(len(switches) + 1), "other_reset_events": []}


def policy_document():
    regions = [{"layer_index": l, "role": "up_proj",
                "module_class": cp.EXPECTED_MODULE_CLASS,
                "implementation": cp.EXPECTED_IMPLEMENTATION, "qweight": qweight(l)}
               for l in cp.LAYERS]
    authority = [{"layer_index": l, "role": "up_proj", "decode_index": d,
                  "generated_token_id": cp.EXPECTED_TOKENS[d],
                  "input_sha256": S1, "output_sha256": S2}
                 for l in cp.LAYERS for d in cp.DECODE_INDICES]
    conditions, pid = [], 0
    for condition in cp.CONDITIONS:
        runs = []
        for rep in range(cp.EXPECTED_REPS):
            pid += 1
            occurrences = [{**a, "qweight": qweight(a["layer_index"]),
                            "timing_ms": 0.1 + a["layer_index"] / 10000 + rep / 100000}
                           for a in authority]
            runs.append({"rep": rep, "fresh_process_id": f"policy-{pid}",
                "prefix_token_sha256": PREFIX, "generated_token_ids": list(cp.EXPECTED_TOKENS),
                "occurrences": occurrences,
                "decode_steps": [{"decode_index": d,
                    "generated_token_id": cp.EXPECTED_TOKENS[d], "timing_ms": 20 + d / 10}
                    for d in cp.DECODE_INDICES], "policy_receipt": policy(condition)})
        conditions.append({"condition": condition, "runs": runs})
    return {"schema_version": 1, "layer_selection_manifest": manifest(),
            "accepted_prefix_sha256": PREFIX, "generated_token_ids": list(cp.EXPECTED_TOKENS),
            "up_qweight_regions": regions, "occurrence_authority": authority,
            "conditions": conditions}


class CensusTests(unittest.TestCase):
    def test_complete_census_passes_and_is_run_aligned(self):
        out = cp.consume_ffn_census(census_document())
        self.assertEqual(out["status"], "PASS")
        self.assertEqual(out["fresh_process_count"], 7)
        self.assertEqual(len(out["run_aligned_shares"]), 28)
        self.assertTrue(all(out["role_support"].values()))

    def test_census_accepts_process_local_pointer_with_fixed_geometry(self):
        doc = census_document()
        for rep, run in enumerate(doc["runs"]):
            local = copy.deepcopy(doc["module_authority"])
            for module in local:
                module["qweight"]["pointer"] += rep * 0x10000000
            run["module_authority"] = local
            pointers = {(x["layer_index"], x["role"]): x["qweight"] for x in local}
            for event in run["occurrences"]:
                event["qweight"] = copy.deepcopy(pointers[(event["layer_index"], event["role"])])
        self.assertEqual(cp.consume_ffn_census(doc)["status"], "PASS")

    def test_runtime_can_mark_whole_role_unsupported(self):
        out = cp.consume_ffn_census(census_document(unsupported_role="gate_proj"))
        self.assertFalse(out["role_support"]["gate_proj"])
        self.assertIsNone(out["run_aligned_shares"][0]["role_share"]["gate_proj"])

    def test_wrong_module_class_fails(self):
        doc = census_document()
        doc["module_authority"][0]["module_class"] = "torch.nn.Linear"
        with self.assertRaisesRegex(cp.CoverageIdentityError, "wrong module class"):
            cp.consume_ffn_census(doc)

    def test_missing_layer_module_fails(self):
        doc = census_document(); doc["module_authority"].pop()
        with self.assertRaisesRegex(cp.CoverageIdentityError, "missing layer/module"):
            cp.consume_ffn_census(doc)

    def test_qweight_drift_fails(self):
        doc = census_document(); doc["runs"][0]["occurrences"][0]["qweight"]["pointer"] += 1
        with self.assertRaisesRegex(cp.CoverageIdentityError, "qweight identity drift"):
            cp.consume_ffn_census(doc)

    def test_nonfinite_timing_fails(self):
        doc = census_document(); doc["runs"][0]["occurrences"][0]["timing_ms"] = math.nan
        with self.assertRaisesRegex(cp.CoverageIdentityError, "nonfinite"):
            cp.consume_ffn_census(doc)

    def test_duplicate_rep_fails(self):
        doc = census_document(); doc["runs"][1]["rep"] = 0
        with self.assertRaisesRegex(cp.CoverageIdentityError, "duplicate rep"):
            cp.consume_ffn_census(doc)

    def test_token_drift_fails(self):
        doc = census_document(); doc["runs"][0]["generated_token_ids"][0] += 1
        with self.assertRaisesRegex(cp.CoverageIdentityError, "token sequence drift"):
            cp.consume_ffn_census(doc)

    def test_sha_drift_fails(self):
        doc = census_document(); doc["runs"][0]["occurrences"][0]["input_sha256"] = "3" * 64
        with self.assertRaisesRegex(cp.CoverageIdentityError, "SHA drift"):
            cp.consume_ffn_census(doc)

    def test_missing_event_fails(self):
        doc = census_document(); doc["runs"][0]["occurrences"].pop()
        with self.assertRaisesRegex(cp.CoverageIdentityError, "missing layer event"):
            cp.consume_ffn_census(doc)


class LayerSelectionAndPolicyTests(unittest.TestCase):
    def test_manifest_exact_sets_pass(self):
        self.assertEqual(cp.validate_layer_selection_manifest(manifest())["status"], "PASS")

    def test_wrong_set_fails(self):
        raw = manifest(); raw["sets"]["N8"][-1] = 19
        with self.assertRaisesRegex(cp.CoverageIdentityError, "wrong frozen layer set"):
            cp.validate_layer_selection_manifest(raw)

    def test_post_data_selection_fails(self):
        raw = manifest(); raw["selected_after_observing_data"] = True
        with self.assertRaisesRegex(cp.CoverageIdentityError, "post-data"):
            cp.validate_layer_selection_manifest(raw)

    def test_every_control_and_fair_receipt_passes(self):
        regions = {l: qweight(l) for l in cp.LAYERS}
        for condition in cp.CONDITIONS:
            self.assertEqual(cp.validate_coverage_policy_receipt(
                policy(condition), condition, regions)["status"], "PASS")

    def test_wrong_hitratio_fails(self):
        raw = policy("FAIR_N8"); raw["switches"][0]["hit_ratio"] = .5
        with self.assertRaisesRegex(cp.CoverageIdentityError, "1/N"):
            cp.validate_coverage_policy_receipt(raw, "FAIR_N8", {l: qweight(l) for l in cp.LAYERS})

    def test_actual_setaside_drift_fails(self):
        raw = policy("CONTROL_N4"); raw["actual_setaside_bytes"] -= 1
        with self.assertRaisesRegex(cp.CoverageIdentityError, "actual set-aside"):
            cp.validate_coverage_policy_receipt(raw, "CONTROL_N4", {l: qweight(l) for l in cp.LAYERS})

    def test_in_run_reset_fails(self):
        raw = policy("FAIR_N2"); raw["switches"][2]["reset_performed"] = True
        with self.assertRaisesRegex(cp.CoverageIdentityError, "in-run reset"):
            cp.validate_coverage_policy_receipt(raw, "FAIR_N2", {l: qweight(l) for l in cp.LAYERS})

    def test_wrong_update_order_fails(self):
        raw = policy("FAIR_N4"); raw["switches"][0], raw["switches"][1] = raw["switches"][1], raw["switches"][0]
        with self.assertRaisesRegex(cp.CoverageIdentityError, "update order"):
            cp.validate_coverage_policy_receipt(raw, "FAIR_N4", {l: qweight(l) for l in cp.LAYERS})

    def test_control_persistence_fails(self):
        raw = policy("CONTROL_N1"); raw["switches"][0]["target_persisting"] = True
        with self.assertRaisesRegex(cp.CoverageIdentityError, "NORMAL/NORMAL"):
            cp.validate_coverage_policy_receipt(raw, "CONTROL_N1", {l: qweight(l) for l in cp.LAYERS})

    def test_fair_wrong_miss_policy_fails(self):
        raw = policy("FAIR_N1"); raw["switches"][0]["miss_prop"] = "NORMAL"
        with self.assertRaisesRegex(cp.CoverageIdentityError, "PERSISTING/STREAMING"):
            cp.validate_coverage_policy_receipt(raw, "FAIR_N1", {l: qweight(l) for l in cp.LAYERS})


class FullCoverageRunTests(unittest.TestCase):
    def test_complete_matrix_passes(self):
        out = cp.consume_coverage_policy_runs(policy_document())
        self.assertEqual(out["condition_count"], 14)
        self.assertEqual(out["fresh_process_count"], 98)
        self.assertEqual(len(out["run_aligned_points"]), 98)

    def test_policy_accepts_process_local_pointer_with_fixed_geometry(self):
        doc = policy_document()
        for block in doc["conditions"]:
            for rep, run in enumerate(block["runs"]):
                local = copy.deepcopy(doc["up_qweight_regions"])
                for item in local:
                    item["qweight"]["pointer"] += rep * 0x10000000
                run["up_qweight_regions"] = local
                pointers = {x["layer_index"]: x["qweight"] for x in local}
                for event in run["occurrences"]:
                    event["qweight"] = copy.deepcopy(pointers[event["layer_index"]])
                for switch in run["policy_receipt"]["switches"]:
                    switch["base_pointer"] = pointers[switch["layer_index"]]["pointer"]
        self.assertEqual(cp.consume_coverage_policy_runs(doc)["status"], "PASS")

    def test_missing_qweight_layer_fails(self):
        doc = policy_document(); doc["up_qweight_regions"].pop()
        with self.assertRaisesRegex(cp.CoverageIdentityError, "missing up qweight layer"):
            cp.consume_coverage_policy_runs(doc)

    def test_missing_occurrence_fails(self):
        doc = policy_document(); doc["conditions"][0]["runs"][0]["occurrences"].pop()
        with self.assertRaisesRegex(cp.CoverageIdentityError, "all 28 up occurrences"):
            cp.consume_coverage_policy_runs(doc)

    def test_qweight_drift_fails(self):
        doc = policy_document(); doc["conditions"][0]["runs"][0]["occurrences"][0]["qweight"]["bytes"] += 1
        with self.assertRaisesRegex(cp.CoverageIdentityError, "qweight identity drift"):
            cp.consume_coverage_policy_runs(doc)

    def test_token_drift_fails(self):
        doc = policy_document(); doc["conditions"][0]["runs"][0]["generated_token_ids"][3] += 1
        with self.assertRaisesRegex(cp.CoverageIdentityError, "token sequence drift"):
            cp.consume_coverage_policy_runs(doc)

    def test_sha_drift_fails(self):
        doc = policy_document(); doc["conditions"][0]["runs"][0]["occurrences"][0]["output_sha256"] = "3" * 64
        with self.assertRaisesRegex(cp.CoverageIdentityError, "SHA drift"):
            cp.consume_coverage_policy_runs(doc)

    def test_duplicate_rep_fails(self):
        doc = policy_document(); doc["conditions"][0]["runs"][1]["rep"] = 0
        with self.assertRaisesRegex(cp.CoverageIdentityError, "duplicate rep"):
            cp.consume_coverage_policy_runs(doc)


if __name__ == "__main__":
    unittest.main()
