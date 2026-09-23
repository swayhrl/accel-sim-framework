#!/usr/bin/env python3
import copy
import csv
import json
import math
import tempfile
import unittest
from pathlib import Path

import shared_consumer as sc


S1, S2, PREFIX = "1" * 64, "2" * 64, "a" * 64
TOKENS = [11, 22, 33, 44]


def regions():
    return {
        "L0_UP": {"pointer": 0x100000, "bytes": 1000, "contiguous": True},
        "L14_UP": {"pointer": 0x200000, "bytes": 1000, "contiguous": True},
        "L0_DOWN": {"pointer": 0x300000, "bytes": 1000, "contiguous": True},
    }


def reset(index):
    return {"status": "PASS", "performed": True,
            "operation": "cudaCtxResetPersistingL2Cache", "event_index": index}


def policy(condition, *, rotating=False):
    rs = regions()
    if rotating:
        sequence = [(None, target) for target in ("L0_UP", "L14_UP", "L0_UP")]
        ratio = 0.5
        selected = {"L0_UP", "L14_UP"} if condition == "ROTATING_PERSIST" else set()
    else:
        sequence = [] if condition == "SETASIDE_ONLY" else list(sc.FULL_SWITCH_SEQUENCE)
        ratio = sc.HIT_RATIO[condition]
        selected = set(sc.SELECTED_TARGETS[condition])
    switches = []
    for i, (phase, target) in enumerate(sequence, 1):
        persisting = target in selected
        item = {"sequence_index": i, "target": target,
                "base_pointer": rs[target]["pointer"], "num_bytes": rs[target]["bytes"],
                "hit_ratio": ratio, "hit_prop": "PERSISTING" if persisting else "NORMAL",
                "miss_prop": "NORMAL", "target_persisting": persisting,
                "stream_identity": "stream-7", "reset_performed": False,
                "api_duration_us": 2.0 + i / 100.0}
        if phase is not None:
            item["phase"] = phase
        switches.append(item)
    return {"status": "PASS", "condition": condition,
            "requested_setaside_bytes": sc.FIXED_SETASIDE_BYTES,
            "actual_setaside_bytes": sc.EXPECTED_ACTUAL_SETASIDE_BYTES,
            "stream_identity": "stream-7", "reset_before": reset(0),
            "switches": switches, "reset_after": reset(len(switches) + 1),
            "other_reset_events": []}


def authority():
    rows = []
    for target, (layer, role) in sc.TARGET_KEY.items():
        for d in range(4):
            rows.append({"layer_index": layer, "role": role, "decode_index": d,
                         "M": 1, "implementation": "AWQ_FP16_INPUT",
                         "generated_token_id": TOKENS[d], "input_sha256": S1,
                         "output_sha256": S2})
    return rows


def occurrence(row, timing=10.0):
    return {**row, "timing_ms": timing}


def shared_document():
    auth = authority()
    conditions = []
    process = 0
    factors = {"SETASIDE_ONLY": 1.02, "ROTATE_CONTROL_3": 1.0,
               "SINGLE_L0_UP": .90, "SHARE2_UP": .88,
               "SHARE2_L0": .89, "SHARE3": .87}
    for condition in sc.CONDITIONS:
        runs = []
        for rep in range(7):
            process += 1
            runs.append({"rep": rep, "fresh_process_id": f"p{process}",
                         "prefix_token_sha256": PREFIX, "generated_token_ids": list(TOKENS),
                         "occurrences": [occurrence(row, 10 * factors[condition] + rep * .001) for row in auth],
                         "decode_steps": [{"decode_index": d, "generated_token_id": TOKENS[d],
                                           "timing_ms": 100 * factors[condition] + rep * .01}
                                          for d in range(4)],
                         "policy_receipt": policy(condition)})
        conditions.append({"condition": condition, "runs": runs})
    return {"schema_version": 1, "fixed_setaside_bytes": sc.FIXED_SETASIDE_BYTES,
            "accepted_prefix_sha256": PREFIX, "generated_token_ids": list(TOKENS),
            "occurrence_authority": auth, "qweight_regions": regions(), "conditions": conditions}


def rotating_document():
    blocks = []
    for ci, condition in enumerate(("ROTATING_PERSIST", "ROTATING_CONTROL")):
        runs = []
        for rep in range(9):
            runs.append({"rep": rep, "fresh_process_id": f"r{ci}-{rep}",
                         "input_sha256": S1, "output_sha256": S2,
                         "target_timing_ms": (7.0 if ci == 0 else 10.0) + rep * .001,
                         "policy_receipt": policy(condition, rotating=True)})
        blocks.append({"condition": condition, "runs": runs})
    return {"schema_version": 1, "qweight_regions": regions(), "conditions": blocks}


class PolicyReceiptTests(unittest.TestCase):
    def test_every_condition_passes(self):
        for condition in sc.CONDITIONS:
            out = sc.validate_policy_receipt(policy(condition), condition, regions())
            self.assertEqual(out["status"], "PASS")
            self.assertEqual(out["requested_setaside_bytes"], sc.FIXED_SETASIDE_BYTES)

    def test_stale_reset_rejected(self):
        raw = policy("SHARE3")
        raw["reset_before"]["event_index"] = 2
        with self.assertRaisesRegex(sc.SharedConsumerError, "stale"):
            sc.validate_policy_receipt(raw, "SHARE3", regions())

    def test_in_run_reset_rejected(self):
        raw = policy("SHARE3")
        raw["switches"][2]["reset_performed"] = True
        with self.assertRaisesRegex(sc.SharedConsumerError, "forbidden reset"):
            sc.validate_policy_receipt(raw, "SHARE3", regions())

    def test_wrong_window_rejected(self):
        raw = policy("SHARE2_UP")
        raw["switches"][0]["num_bytes"] -= 1
        with self.assertRaisesRegex(sc.SharedConsumerError, "full exact"):
            sc.validate_policy_receipt(raw, "SHARE2_UP", regions())

    def test_wrong_pointer_rejected(self):
        raw = policy("SHARE2_UP")
        raw["switches"][0]["base_pointer"] += 1
        with self.assertRaisesRegex(sc.SharedConsumerError, "exact qweight"):
            sc.validate_policy_receipt(raw, "SHARE2_UP", regions())

    def test_wrong_hit_ratio_rejected(self):
        raw = policy("SHARE3")
        raw["switches"][0]["hit_ratio"] = .5
        with self.assertRaisesRegex(sc.SharedConsumerError, "hitRatio"):
            sc.validate_policy_receipt(raw, "SHARE3", regions())

    def test_missing_switch_rejected(self):
        raw = policy("SHARE3")
        raw["switches"].pop()
        with self.assertRaisesRegex(sc.SharedConsumerError, "missing/duplicate"):
            sc.validate_policy_receipt(raw, "SHARE3", regions())

    def test_duplicate_switch_rejected(self):
        raw = policy("SHARE3")
        raw["switches"].append(copy.deepcopy(raw["switches"][-1]))
        with self.assertRaisesRegex(sc.SharedConsumerError, "missing/duplicate"):
            sc.validate_policy_receipt(raw, "SHARE3", regions())

    def test_wrong_switch_order_rejected(self):
        raw = policy("SHARE3")
        raw["switches"][0], raw["switches"][1] = raw["switches"][1], raw["switches"][0]
        with self.assertRaises(sc.SharedConsumerError):
            sc.validate_policy_receipt(raw, "SHARE3", regions())

    def test_api_control_accidental_persistence_rejected(self):
        raw = policy("ROTATE_CONTROL_3")
        raw["switches"][0]["hit_prop"] = "PERSISTING"
        raw["switches"][0]["target_persisting"] = True
        with self.assertRaisesRegex(sc.SharedConsumerError, "accidentally"):
            sc.validate_policy_receipt(raw, "ROTATE_CONTROL_3", regions())

    def test_fixed_budget_rejected_if_changed(self):
        raw = policy("SHARE2_L0")
        raw["requested_setaside_bytes"] -= 1
        with self.assertRaisesRegex(sc.SharedConsumerError, "fixed total"):
            sc.validate_policy_receipt(raw, "SHARE2_L0", regions())

    def test_actual_setaside_queryback_drift_rejected(self):
        raw = policy("SHARE2_UP")
        raw["actual_setaside_bytes"] = sc.EXPECTED_ACTUAL_SETASIDE_BYTES - 1
        with self.assertRaisesRegex(sc.SharedConsumerError, "query-back set-aside drift"):
            sc.validate_policy_receipt(raw, "SHARE2_UP", regions())

    def test_region_overlap_rejected(self):
        doc = shared_document()
        doc["qweight_regions"]["L14_UP"]["pointer"] = 0x100001
        with self.assertRaisesRegex(sc.SharedConsumerError, "overlapping"):
            sc.consume_shared_runs(doc)


class SharedRunTests(unittest.TestCase):
    def test_complete_matrix_passes(self):
        out = sc.consume_shared_runs(shared_document())
        self.assertEqual(out["status"], "PASS")
        self.assertEqual(out["fresh_process_count"], 42)
        self.assertEqual(len(out["timing_points"]), 72)
        self.assertEqual(len(out["decode_step_timing"]), 24)

    def test_process_local_region_authority_passes(self):
        doc = shared_document()
        local = doc.pop("qweight_regions")
        for block in doc["conditions"]:
            for run in block["runs"]:
                run["qweight_regions"] = copy.deepcopy(local)
        self.assertEqual(sc.consume_shared_runs(doc)["fresh_process_count"], 42)

    def test_sha_drift_rejected(self):
        doc = shared_document()
        doc["conditions"][2]["runs"][1]["occurrences"][0]["input_sha256"] = "3" * 64
        with self.assertRaisesRegex(sc.SharedConsumerError, "SHA drift"):
            sc.consume_shared_runs(doc)

    def test_token_drift_rejected(self):
        doc = shared_document()
        doc["conditions"][0]["runs"][0]["generated_token_ids"][3] += 1
        with self.assertRaisesRegex(sc.SharedConsumerError, "token sequence"):
            sc.consume_shared_runs(doc)

    def test_missing_occurrence_rejected(self):
        doc = shared_document()
        doc["conditions"][0]["runs"][0]["occurrences"].pop()
        with self.assertRaisesRegex(sc.SharedConsumerError, "12-occurrence"):
            sc.consume_shared_runs(doc)

    def test_duplicate_occurrence_rejected(self):
        doc = shared_document()
        run = doc["conditions"][0]["runs"][0]
        run["occurrences"][-1] = copy.deepcopy(run["occurrences"][0])
        with self.assertRaisesRegex(sc.SharedConsumerError, "duplicate"):
            sc.consume_shared_runs(doc)

    def test_nonfinite_target_timing_rejected(self):
        doc = shared_document()
        doc["conditions"][0]["runs"][0]["occurrences"][0]["timing_ms"] = math.nan
        with self.assertRaisesRegex(sc.SharedConsumerError, "nonfinite"):
            sc.consume_shared_runs(doc)

    def test_nonfinite_decode_timing_rejected(self):
        doc = shared_document()
        doc["conditions"][0]["runs"][0]["decode_steps"][0]["timing_ms"] = math.inf
        with self.assertRaisesRegex(sc.SharedConsumerError, "nonfinite"):
            sc.consume_shared_runs(doc)

    def test_duplicate_rep_rejected(self):
        doc = shared_document()
        doc["conditions"][0]["runs"][1]["rep"] = 0
        with self.assertRaisesRegex(sc.SharedConsumerError, "duplicate"):
            sc.consume_shared_runs(doc)

    def test_missing_rep_rejected(self):
        doc = shared_document()
        doc["conditions"][0]["runs"].pop()
        with self.assertRaisesRegex(sc.SharedConsumerError, "exactly 7"):
            sc.consume_shared_runs(doc)

    def test_fresh_process_reuse_rejected(self):
        doc = shared_document()
        doc["conditions"][0]["runs"][1]["fresh_process_id"] = doc["conditions"][0]["runs"][0]["fresh_process_id"]
        with self.assertRaisesRegex(sc.SharedConsumerError, "reused"):
            sc.consume_shared_runs(doc)


class RotatingQualificationTests(unittest.TestCase):
    def test_ab_a_qualification_passes(self):
        out = sc.consume_rotating_qualification(rotating_document())
        self.assertEqual(out["status"], "PASS")
        self.assertGreater(out["persist_vs_control_timing_benefit_fraction"], .29)

    def test_rotating_accepts_exact_a_b_region_authority_only(self):
        doc = rotating_document()
        doc["qweight_regions"].pop("L0_DOWN")
        self.assertEqual(sc.consume_rotating_qualification(doc)["status"], "PASS")

    def test_rotating_process_local_regions_pass(self):
        doc = rotating_document()
        local = doc.pop("qweight_regions")
        for block in doc["conditions"]:
            for run in block["runs"]:
                run["qweight_regions"] = copy.deepcopy(local)
        self.assertEqual(sc.consume_rotating_qualification(doc)["status"], "PASS")

    def test_rotating_wrong_order_rejected(self):
        doc = rotating_document()
        doc["conditions"][0]["runs"][0]["policy_receipt"]["switches"][1]["target"] = "L0_UP"
        with self.assertRaisesRegex(sc.SharedConsumerError, "order"):
            sc.consume_rotating_qualification(doc)

    def test_rotating_sha_drift_rejected(self):
        doc = rotating_document()
        doc["conditions"][0]["runs"][3]["output_sha256"] = "4" * 64
        with self.assertRaisesRegex(sc.SharedConsumerError, "SHA drift"):
            sc.consume_rotating_qualification(doc)

    def test_rotating_duplicate_rep_rejected(self):
        doc = rotating_document()
        doc["conditions"][0]["runs"][4]["rep"] = 3
        with self.assertRaisesRegex(sc.SharedConsumerError, "duplicate"):
            sc.consume_rotating_qualification(doc)


class NcuTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def make_document(self):
        metrics = [{"name": name, "unit": "byte", "additive": True} for name in sc.BASE_METRICS]
        profiles = []
        for idx, (condition, target) in enumerate(sorted(sc.NCU_MATRIX)):
            stem = f"p{idx}"
            range_name = f"SHARED_{condition}_{target}_D3"
            base = self.root / f"{stem}_BASE.csv"
            session = self.root / f"{stem}_SESSION.csv"
            profile = self.root / f"{stem}_PROFILE.log"
            receipt = self.root / f"{stem}_POLICY.json"
            with base.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Process ID", "Kernel Name", "NVTX Push/Pop_Range",
                                 "profiler__replayer_passes", *sc.BASE_METRICS])
                writer.writerow(["", "", "", "", "", "byte", "byte", "byte"])
                writer.writerow([1, 55, "gemm", range_name, 2, 100, 200, 300])
                writer.writerow([2, 55, "reduce", range_name, 2, 10, 20, 30])
            session.write_text("ncu --replay-mode application --cache-control none "
                               f"--nvtx-include {range_name}/ --metrics {','.join(sc.BASE_METRICS)}\n",
                               encoding="utf-8")
            pass_row = {"status": "PASS", "condition": condition,
                        "target": target, "decode_index": 3,
                        "range": range_name, "input_sha256": S1,
                        "output_sha256": S2}
            profile.write_text((json.dumps(pass_row) + "\n") * 2, encoding="utf-8")
            receipt.write_text(json.dumps(policy(condition)), encoding="utf-8")
            profiles.append({"condition": condition, "target": target, "decode_index": 3,
                             "range_name": range_name, "input_sha256": S1, "output_sha256": S2,
                             "expected_kernel_names": ["gemm", "reduce"], "expected_pass_count": 2,
                             "base_path": base.name, "session_path": session.name,
                             "profile_path": profile.name, "policy_receipt_path": receipt.name})
        return {"schema_version": 1, "qweight_regions": regions(), "metrics": metrics, "profiles": profiles}

    def test_exact_four_source_matrix_passes(self):
        out = sc.consume_shared_ncu(self.make_document(), self.root)
        self.assertEqual(out["profile_count"], 14)
        self.assertEqual(out["profiles"][0]["base"]["additive_metric_sums"]["dram__bytes.sum"], "330")

    def test_profile_local_region_authority_passes(self):
        doc = self.make_document()
        local = doc.pop("qweight_regions")
        for profile in doc["profiles"]:
            profile["qweight_regions"] = copy.deepcopy(local)
        self.assertEqual(sc.consume_shared_ncu(doc, self.root)["profile_count"], 14)

    def test_duplicate_semantic_point_rejected(self):
        doc = self.make_document()
        doc["profiles"][-1] = copy.deepcopy(doc["profiles"][0])
        with self.assertRaisesRegex(sc.SharedConsumerError, "duplicate"):
            sc.consume_shared_ncu(doc, self.root)

    def test_session_replay_rejected(self):
        doc = self.make_document()
        path = self.root / doc["profiles"][0]["session_path"]
        path.write_text(path.read_text().replace("application", "kernel"), encoding="utf-8")
        with self.assertRaisesRegex(sc.SharedConsumerError, "replay"):
            sc.consume_shared_ncu(doc, self.root)

    def test_unit_mismatch_rejected(self):
        doc = self.make_document()
        path = self.root / doc["profiles"][0]["base_path"]
        with path.open() as f:
            rows = list(csv.reader(f))
        rows[1][-1] = "sector"
        with path.open("w", newline="") as f:
            csv.writer(f).writerows(rows)
        with self.assertRaisesRegex(sc.SharedConsumerError, "unit mismatch"):
            sc.consume_shared_ncu(doc, self.root)

    def test_profile_identity_rejected(self):
        doc = self.make_document()
        path = self.root / doc["profiles"][0]["profile_path"]
        rows = [json.loads(x) for x in path.read_text().splitlines()]
        rows[0]["output_sha256"] = "9" * 64
        path.write_text("\n".join(json.dumps(x) for x in rows) + "\n")
        with self.assertRaisesRegex(sc.SharedConsumerError, "semantic identity"):
            sc.consume_shared_ncu(doc, self.root)

    def test_profile_pass_count_must_match_replay_passes(self):
        doc = self.make_document()
        path = self.root / doc["profiles"][0]["profile_path"]
        path.write_text(path.read_text().splitlines()[0] + "\n")
        with self.assertRaisesRegex(sc.SharedConsumerError, "PASS receipt count"):
            sc.consume_shared_ncu(doc, self.root)

    def test_nonadditive_metric_is_not_semantically_summed_here(self):
        doc = self.make_document()
        doc["metrics"].append({"name": "stall.pct", "unit": "%", "additive": False})
        for profile in doc["profiles"]:
            session = self.root / profile["session_path"]
            session.write_text(session.read_text().replace(
                ",dram__bytes.sum", ",dram__bytes.sum,stall.pct"))
        out = sc.consume_shared_ncu(doc, self.root)
        self.assertEqual(out["nonadditive_metrics_delegated_to_critical_path_consumer"], ["stall.pct"])
        self.assertNotIn("stall.pct", out["profiles"][0]["base"]["additive_metric_sums"])

    def test_analysis_classifies_end_to_end(self):
        native = sc.consume_shared_runs(shared_document())
        ncu = sc.consume_shared_ncu(self.make_document(), self.root)
        out = sc.analyze_shared_policy(native, ncu)
        self.assertEqual(out["stage_decision"], "SHARED_RESIDENCY_END_TO_END_SUPPORTED")
        self.assertTrue(out["MULTI_TARGET_RETAINED"]["SHARE3"])
        self.assertTrue(out["MATERIAL_DECODE_BENEFIT"]["SHARE3"])


if __name__ == "__main__":
    unittest.main()
