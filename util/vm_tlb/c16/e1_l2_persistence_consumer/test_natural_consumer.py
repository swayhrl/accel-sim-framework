#!/usr/bin/env python3
import csv
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from natural_consumer import (
    CONDITIONS, METRICS, MIB, NATURAL_MATRIX, NCU_MATRIX,
    NaturalPersistenceError, compute_policy_effects, consume_budget_sweep,
    consume_natural_ncu, consume_natural_runs, derive_final_state,
)
from test_policy_receipt import receipt as real_policy_receipt

PREFIX = "a" * 64
TOKENS = [23578, 11, 323, 3950]
BUDGET = 33_947_648


def authority():
    result = []
    for number, (layer, role, decode) in enumerate(sorted(NATURAL_MATRIX), 1):
        result.append({
            "layer_index": layer, "role": role, "decode_index": decode, "M": 1,
            "implementation": "AWQ_FP16_INPUT", "generated_token_id": TOKENS[decode],
            "input_sha256": f"{number:064x}", "output_sha256": f"{number + 100:064x}",
            "range_name": f"NAT_L{layer}_{role}_D{decode}",
        })
    return result


def condition_range(condition, item):
    target = f"L{item['layer_index']}_{'UP' if item['role'] == 'up_proj' else 'DOWN'}"
    return f"C16_E1_L2P_{condition}_{target}_D{item['decode_index']}"


def policy(condition, budget=BUDGET, ratio=1.0):
    target = ("L0_UP" if condition.startswith("PERSIST_L0_UP") else
              {"PERSIST_L14_UP": "L14_UP", "PERSIST_L0_DOWN": "L0_DOWN"}.get(condition))
    return {"condition": condition, "budget": 0 if condition == "BASELINE" else budget,
            "target": target,
            "window": BUDGET if condition.startswith("PERSIST_") else 0, "hit_ratio": ratio}


def fake_policy(receipt, *, expected_condition, expected_target=None, expected_budget_bytes=None):
    if receipt["condition"] != expected_condition or receipt["target"] != expected_target:
        raise ValueError("condition/target mismatch")
    if receipt["budget"] != expected_budget_bytes:
        raise ValueError("budget mismatch")
    return {"status": "PASS", "condition": expected_condition, "target": expected_target,
            "requested_setaside_bytes": receipt["budget"], "actual_setaside_bytes": receipt["budget"],
            "access_window_num_bytes": receipt["window"], "hit_ratio": receipt["hit_ratio"]}


def natural_document():
    auth = authority()
    conditions = []
    medians = {"BASELINE": 10.2, "SETASIDE_ONLY": 10.0, "PERSIST_L0_UP": 8.0,
               "PERSIST_L14_UP": 9.8, "PERSIST_L0_DOWN": 8.2}
    for ci, condition in enumerate(CONDITIONS):
        runs = []
        for rep in range(7):
            occurrences = []
            for item in auth:
                row = dict(item)
                row["range_name"] = condition_range(condition, item)
                row["timing_ms"] = medians[condition] + rep * 0.001 + item["decode_index"] * 0.01
                occurrences.append(row)
            runs.append({
                "rep": rep, "fresh_process_id": f"{condition}-{rep}",
                "prefix_token_sha256": PREFIX, "generated_token_ids": list(TOKENS),
                "occurrences": occurrences,
                "decode_steps": [{"decode_index": d, "generated_token_id": TOKENS[d],
                                  "timing_ms": 20 + ci + d + rep * 0.001} for d in range(4)],
                "policy_receipt": policy(condition),
            })
        conditions.append({"condition": condition, "runs": runs})
    return {"schema_version": 1, "accepted_prefix_sha256": PREFIX,
            "generated_token_ids": list(TOKENS), "occurrence_authority": auth,
            "primary_budget_bytes": BUDGET, "conditions": conditions}


def write_base(path, range_name, dram=100_000_000, unit="byte"):
    header = ["ID", "Process ID", "Kernel Name", "profiler__replayer_passes",
              "NVTX Push/Pop_Range", *METRICS]
    units = ["", "", "", "", "", unit, unit, unit]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(header); writer.writerow(units)
        writer.writerow(["1", "42", "target_kernel", "1", range_name,
                         dram // 4, dram // 2, dram])


def write_session(path, range_name, replay="application"):
    path.write_text(f"ncu --replay-mode {replay} --cache-control none --nvtx-include {range_name}/ "
                    f"--metrics {','.join(METRICS)}\n", encoding="utf-8")


def write_profile(path, item, condition):
    receipt = {"status": "PASS", "condition": condition, "layer_index": item["layer_index"],
               "role": item["role"], "decode_index": item["decode_index"], "M": 1,
               "implementation": "AWQ_FP16_INPUT", "generated_token_id": item["generated_token_id"],
               "range": item["range_name"], "input_sha256": item["input_sha256"],
               "output_sha256": item["output_sha256"], "prefix_token_sha256": PREFIX,
               "generated_token_ids": list(TOKENS)}
    path.write_text("==PROF== raw\n" + json.dumps(receipt) + "\n", encoding="utf-8")


class NaturalRunTests(unittest.TestCase):
    def test_five_conditions_seven_fresh_runs_close(self):
        result = consume_natural_runs(natural_document(), policy_validator=fake_policy)
        self.assertEqual(result["fresh_process_count"], 35)
        self.assertEqual(len(result["timing_points"]), 60)
        self.assertEqual(len(result["decode_step_timing"]), 20)
        self.assertEqual(len(result["policy_receipts"]), 35)

    def test_real_policy_parser_api_integration(self):
        doc = natural_document()
        for block in doc["conditions"]:
            condition = block["condition"]
            for run in block["runs"]:
                receipt = real_policy_receipt(condition)
                if condition == "PERSIST_L14_UP":
                    receipt["target"] = "L14_UP"
                elif condition == "PERSIST_L0_DOWN":
                    receipt["target"] = "L0_DOWN"
                run["policy_receipt"] = receipt
        self.assertEqual(consume_natural_runs(doc)["fresh_process_count"], 35)

    def test_missing_condition_or_run_fails(self):
        doc = natural_document(); doc["conditions"].pop()
        with self.assertRaisesRegex(NaturalPersistenceError, "five-condition"):
            consume_natural_runs(doc, policy_validator=fake_policy)
        doc = natural_document(); doc["conditions"][0]["runs"].pop()
        with self.assertRaisesRegex(NaturalPersistenceError, "exactly 7"):
            consume_natural_runs(doc, policy_validator=fake_policy)

    def test_token_sha_and_fresh_process_reuse_fail(self):
        doc = natural_document(); doc["conditions"][0]["runs"][0]["generated_token_ids"][2] += 1
        with self.assertRaisesRegex(NaturalPersistenceError, "token sequence mismatch"):
            consume_natural_runs(doc, policy_validator=fake_policy)
        doc = natural_document(); doc["conditions"][1]["runs"][0]["fresh_process_id"] = "BASELINE-0"
        with self.assertRaisesRegex(NaturalPersistenceError, "fresh_process_id reused"):
            consume_natural_runs(doc, policy_validator=fake_policy)
        doc = natural_document(); doc["conditions"][0]["runs"][0]["occurrences"][0]["input_sha256"] = "f" * 64
        with self.assertRaisesRegex(NaturalPersistenceError, "SHA/identity mismatch"):
            consume_natural_runs(doc, policy_validator=fake_policy)
        doc = natural_document(); doc["conditions"][0]["runs"][0]["occurrences"][0]["range_name"] = "WRONG"
        with self.assertRaisesRegex(NaturalPersistenceError, "range mismatch"):
            consume_natural_runs(doc, policy_validator=fake_policy)

    def test_decode_and_policy_mismatch_fail(self):
        doc = natural_document(); doc["conditions"][0]["runs"][0]["decode_steps"].pop()
        with self.assertRaisesRegex(NaturalPersistenceError, "decode-step matrix"):
            consume_natural_runs(doc, policy_validator=fake_policy)
        doc = natural_document(); doc["conditions"][1]["runs"][0]["policy_receipt"]["budget"] = 1
        with self.assertRaisesRegex(NaturalPersistenceError, "policy receipt failed"):
            consume_natural_runs(doc, policy_validator=fake_policy)


class RawNcuTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def document(self):
        auth = {(x["layer_index"], x["role"], x["decode_index"]): x for x in authority()}
        profiles = []
        for number, key in enumerate(sorted(NCU_MATRIX)):
            condition, layer, role, decode = key; item = dict(auth[(layer, role, decode)])
            item["range_name"] = condition_range(condition, item)
            base, session, profile = [self.root / f"p{number}_{suffix}" for suffix in ("BASE.csv", "SESSION.csv", "PROFILE.log")]
            write_base(base, item["range_name"], 100_000_000 - number * 1_000_000)
            write_session(session, item["range_name"]); write_profile(profile, item, condition)
            profiles.append({"condition": condition, **item, "expected_kernel_names": ["target_kernel"],
                             "expected_pass_count": 1, "base_path": base.name,
                             "session_path": session.name, "profile_path": profile.name,
                             "policy_receipt": policy(condition)})
        return {"schema_version": 1, "accepted_prefix_sha256": PREFIX,
                "generated_token_ids": TOKENS, "occurrence_authority": authority(),
                "primary_budget_bytes": BUDGET, "profiles": profiles}

    def test_direct_sixteen_profile_closure(self):
        got = consume_natural_ncu(self.document(), self.root, fake_policy)
        self.assertEqual(got["profile_count"], 16)
        self.assertEqual(got["authority"], "DIRECT_RAW_BASE_SESSION_PROFILE_POLICY_RECEIPT_ONLY")

    def test_missing_duplicate_and_summary_substitution_fail(self):
        doc = self.document(); doc["profiles"].pop()
        with self.assertRaisesRegex(NaturalPersistenceError, "exactly 16"):
            consume_natural_ncu(doc, self.root, fake_policy)
        doc = self.document(); doc["profiles"][-1] = deepcopy(doc["profiles"][0])
        with self.assertRaisesRegex(NaturalPersistenceError, "duplicate NCU"):
            consume_natural_ncu(doc, self.root, fake_policy)

    def test_session_unit_profile_identity_fail(self):
        doc = self.document(); p = self.root / doc["profiles"][0]["session_path"]
        p.write_text(p.read_text().replace("application", "kernel"), encoding="utf-8")
        with self.assertRaisesRegex(NaturalPersistenceError, "replay mode"):
            consume_natural_ncu(doc, self.root, fake_policy)
        doc = self.document(); item = doc["profiles"][0]
        write_base(self.root / item["base_path"], item["range_name"], unit="Kbyte")
        with self.assertRaisesRegex(NaturalPersistenceError, "unit mismatch"):
            consume_natural_ncu(doc, self.root, fake_policy)
        doc = self.document(); item = doc["profiles"][0]
        payload = json.loads((self.root / item["profile_path"]).read_text().splitlines()[-1]); payload["condition"] = "WRONG"
        (self.root / item["profile_path"]).write_text(json.dumps(payload) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(NaturalPersistenceError, "PROFILE semantic"):
            consume_natural_ncu(doc, self.root, fake_policy)


def effect_inputs(target_timing=8.0, unrelated_timing=9.9, target_dram=60 * MIB, unrelated_dram=99 * MIB):
    timing, profiles = [], []
    for layer, role, decode in ((0, "up_proj", 1), (0, "up_proj", 3), (14, "up_proj", 3), (0, "down_proj", 3)):
        target = {(0, "up_proj"): "PERSIST_L0_UP", (14, "up_proj"): "PERSIST_L14_UP",
                  (0, "down_proj"): "PERSIST_L0_DOWN"}[(layer, role)]
        unrelated = {(0, "up_proj"): "PERSIST_L14_UP", (14, "up_proj"): "PERSIST_L0_UP",
                     (0, "down_proj"): "PERSIST_L0_UP"}[(layer, role)]
        values = {"BASELINE": 10.1, "SETASIDE_ONLY": 10.0, target: target_timing, unrelated: unrelated_timing}
        dram = {"BASELINE": 101 * MIB, "SETASIDE_ONLY": 100 * MIB, target: target_dram, unrelated: unrelated_dram}
        for condition in ("BASELINE", "SETASIDE_ONLY", target, unrelated):
            timing.append({"condition": condition, "layer_index": layer, "role": role,
                           "decode_index": decode, "statistics": {"median_ms": values[condition], "cv": .005}})
            profiles.append({"condition": condition,
                             "semantic_identity": {"layer_index": layer, "role": role, "decode_index": decode},
                             "base": {"metric_sums": {"dram__bytes.sum": str(dram[condition])}}})
    return {"timing_points": timing}, {"profiles": profiles}


class EffectTests(unittest.TestCase):
    def test_material_target_specific_effects(self):
        result = compute_policy_effects(*effect_inputs())
        self.assertEqual(len(result["effects"]), 4)
        self.assertTrue(all(row["MATERIAL_TIMING_BENEFIT"] for row in result["effects"]))
        self.assertTrue(all(row["MATERIAL_DRAM_BENEFIT"] for row in result["effects"]))
        self.assertTrue(all(row["TARGET_SPECIFIC"] for row in result["effects"]))
        self.assertEqual(derive_final_state(True, result), "MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW")

    def test_traffic_only_no_effect_and_unqualified_states(self):
        traffic = compute_policy_effects(*effect_inputs(target_timing=9.9))
        self.assertEqual(derive_final_state(True, traffic), "TARGETED_PERSISTENCE_TRAFFIC_ONLY")
        timing_only = compute_policy_effects(*effect_inputs(target_dram=99 * MIB))
        self.assertEqual(
            derive_final_state(True, timing_only),
            "TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED",
        )
        no_effect = compute_policy_effects(*effect_inputs(target_timing=9.9, target_dram=99 * MIB))
        self.assertEqual(derive_final_state(True, no_effect), "TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED")
        self.assertEqual(derive_final_state(False, no_effect), "CUDA_PERSISTENCE_POLICY_UNQUALIFIED")

    def test_matched_unrelated_effect_blocks_specificity(self):
        result = compute_policy_effects(*effect_inputs(unrelated_timing=8.1, unrelated_dram=61 * MIB))
        self.assertTrue(all(row["MATERIAL_TIMING_BENEFIT"] for row in result["effects"]))
        self.assertFalse(any(row["TARGET_SPECIFIC"] for row in result["effects"]))


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def document(self):
        qweight = BUDGET
        auth = authority(); d3 = next(x for x in auth if (x["layer_index"], x["role"], x["decode_index"]) == (0, "up_proj", 3))
        budgets = [8 * MIB, 16 * MIB, 24 * MIB, 32 * MIB, qweight]
        points = []
        for number, budget in enumerate(budgets):
            ratio = min(1.0, budget / qweight)
            policy_condition = f"PERSIST_L0_UP_BUDGET_{number}"
            runs = []
            timing = {8 * MIB: 9.8, 16 * MIB: 9.0, 24 * MIB: 8.5, 32 * MIB: 8.0, qweight: 7.9}[budget]
            for rep in range(7):
                occurrence = dict(d3)
                occurrence["range_name"] = condition_range("BUDGET_L0_UP", occurrence)
                occurrence["timing_ms"] = timing + rep * .001
                runs.append({"rep": rep, "fresh_process_id": f"budget-{budget}-{rep}",
                             "prefix_token_sha256": PREFIX, "generated_token_ids": TOKENS,
                             "d3_occurrence": occurrence,
                             "policy_receipt": policy(policy_condition, budget, ratio)})
            base, session, profile = [self.root / f"b{number}_{suffix}" for suffix in ("BASE.csv", "SESSION.csv", "PROFILE.log")]
            dram = {8 * MIB: 95 * MIB, 16 * MIB: 75 * MIB, 24 * MIB: 65 * MIB,
                    32 * MIB: 55 * MIB, qweight: 50 * MIB}[budget]
            budget_d3 = dict(d3); budget_d3["range_name"] = condition_range("BUDGET_L0_UP", budget_d3)
            write_base(base, budget_d3["range_name"], dram); write_session(session, budget_d3["range_name"])
            write_profile(profile, budget_d3, "BUDGET_L0_UP")
            points.append({"budget_bytes": budget, "runs": runs,
                           "ncu_profile": {"base_path": base.name, "session_path": session.name,
                                           "profile_path": profile.name, "expected_kernel_names": ["target_kernel"],
                                           "expected_pass_count": 1,
                                           "policy_receipt": policy(policy_condition, budget, ratio)}})
        return {"schema_version": 1, "triggered": True, "full_qweight_material_timing": True,
                "full_qweight_material_dram": True, "accepted_prefix_sha256": PREFIX,
                "generated_token_ids": TOKENS, "occurrence_authority": auth, "qweight_bytes": qweight,
                "setaside_only_reference": {"timing_median_ms": 10.0, "timing_cv": .005,
                                             "dram_bytes": 100 * MIB}, "points": points}

    def test_triggered_sweep_and_first_tested_material_budget(self):
        result = consume_budget_sweep(self.document(), self.root, fake_policy)
        self.assertTrue(result["triggered"])
        self.assertEqual(result["first_tested_material_budget_bytes"], 16 * MIB)
        self.assertIn("FIRST_TESTED", result["threshold_claim"])
        self.assertEqual(len(result["points"]), 5)

    def test_full_window_hit_ratio_and_seven_runs_fail_closed(self):
        doc = self.document(); doc["points"][0]["runs"][0]["policy_receipt"]["window"] -= 1
        with self.assertRaisesRegex(NaturalPersistenceError, "changed full qweight window"):
            consume_budget_sweep(doc, self.root, fake_policy)
        doc = self.document(); doc["points"][0]["runs"][0]["policy_receipt"]["hit_ratio"] = .9
        with self.assertRaisesRegex(NaturalPersistenceError, "hitRatio formula"):
            consume_budget_sweep(doc, self.root, fake_policy)
        doc = self.document(); doc["points"][0]["runs"].pop()
        with self.assertRaisesRegex(NaturalPersistenceError, "seven fresh runs"):
            consume_budget_sweep(doc, self.root, fake_policy)

    def test_d3_identity_and_tested_budget_matrix_fail(self):
        doc = self.document(); doc["points"][0]["runs"][0]["d3_occurrence"]["output_sha256"] = "f" * 64
        with self.assertRaisesRegex(NaturalPersistenceError, "D3 occurrence identity"):
            consume_budget_sweep(doc, self.root, fake_policy)
        doc = self.document(); doc["points"][0]["budget_bytes"] = 12 * MIB
        with self.assertRaisesRegex(NaturalPersistenceError, "wrong/duplicate tested budget"):
            consume_budget_sweep(doc, self.root, fake_policy)

    def test_untriggered_requires_false_materiality_and_no_points(self):
        doc = {"schema_version": 1, "triggered": False, "full_qweight_material_timing": False,
               "full_qweight_material_dram": False, "points": []}
        self.assertTrue(consume_budget_sweep(doc)["trigger_condition_verified_false"])
        doc["full_qweight_material_dram"] = True
        with self.assertRaisesRegex(NaturalPersistenceError, "trigger disagrees"):
            consume_budget_sweep(doc)


if __name__ == "__main__":
    unittest.main()
