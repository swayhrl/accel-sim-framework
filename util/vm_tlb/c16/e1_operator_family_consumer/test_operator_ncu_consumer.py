#!/usr/bin/env python3
import copy
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from operator_ncu_consumer import (
    ACTUAL_SETASIDE_BYTES,
    FULLHINT_MATRIX,
    PHASES,
    PRIMARY_MATRIX,
    REQUESTED_SETASIDE_BYTES,
    ROLES,
    OperatorNCUError,
    consume,
)


SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64
SHA_D = "d" * 64
TOKEN = 3950
GEMM = "awq_gemm_kernel"
REDUCE = "awq_reduce_kernel"


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class OperatorNCUConsumerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        version = "NVIDIA Nsight Compute 2025.1.1.0 build 35528883"
        query = self.root / "METRIC_QUERY.txt"
        query.write_text(version + "\nquery metrics: synthetic\n", encoding="utf-8")
        self.catalog = [
            {"category": "L1_TEX_BYTES", "available": True,
             "metric_name": "l1tex__t_bytes.sum", "unit": "byte", "aggregation": "SEMANTIC_SUM"},
            {"category": "L2_BYTES", "available": True,
             "metric_name": "lts__t_bytes.sum", "unit": "byte", "aggregation": "SEMANTIC_SUM"},
            {"category": "DRAM_BYTES", "available": True,
             "metric_name": "dram__bytes.sum", "unit": "byte", "aggregation": "SEMANTIC_SUM"},
            {"category": "KERNEL_ELAPSED_CYCLES", "available": True,
             "metric_name": "sm__cycles_elapsed.avg", "unit": "cycle", "aggregation": "SEMANTIC_SUM"},
            {"category": "LONG_SCOREBOARD_STALL", "available": True,
             "metric_name": "smsp__warp_issue_stalled_long_scoreboard_per_warp_active.pct",
             "unit": "%", "aggregation": "PER_KERNEL_ONLY"},
            {"category": "LSU_UTILIZATION", "available": False,
             "metric_name": None, "unit": None, "reason": "not exposed by installed NCU"},
        ]
        # Intentionally not gate/up/down role order: the consumer must use raw
        # natural-call authority rather than invent an order.
        natural_keys = []
        for layer in range(28):
            order = (("up_proj", "down_proj", "gate_proj") if layer % 2 == 0
                     else ("down_proj", "gate_proj", "up_proj"))
            natural_keys.extend((layer, role) for role in order)
        modules = []
        for ordinal, (layer, role) in enumerate(
                (pair for layer in range(28) for pair in ((layer, "gate_proj"),
                                                         (layer, "up_proj"),
                                                         (layer, "down_proj")))):
            modules.append({"layer_index": layer, "role": role,
                            "module_class": "WQLinear_GEMM", "backend": "AWQ",
                            "qweight_pointer": 0x10000000 + ordinal * 0x4000000,
                            "qweight_bytes": 6_680_576 if role != "down_proj" else 35_273_728,
                            "qweight_contiguous": True})
        self.module_by_key = {(row["layer_index"], row["role"]): row for row in modules}
        authority = {"modules": modules, "natural_call_order": {}}
        for phase_index, phase in enumerate(PHASES):
            rotation = phase_index * 7
            phase_keys = natural_keys[rotation:] + natural_keys[:rotation]
            authority["natural_call_order"][phase] = [
                {"call_index": index, "layer_index": layer, "role": role}
                for index, (layer, role) in enumerate(phase_keys)]
        self.document = {
            "schema_version": 1,
            "runtime_metric_query": {"status": "PASS", "command": "ncu --query-metrics",
                                     "ncu_version": version, "path": query.name,
                                     "sha256": file_sha(query)},
            "metric_availability": self.catalog,
            "module_authority": authority,
            "profiles": [],
            "fullhint_ncu": {"fair_gud84_whole_decode_benefit": 0.001,
                             "fullhint_gud84_whole_decode_benefit": 0.0059,
                             "triggered": False, "profiles": []},
        }
        for number, (condition, role) in enumerate(sorted(PRIMARY_MATRIX)):
            self.document["profiles"].append(self._write_profile(number, condition, role))

    def tearDown(self):
        self.temp.cleanup()

    def natural_order(self, phase):
        return [(row["layer_index"], row["role"])
                for row in self.document["module_authority"]["natural_call_order"][phase]]

    def _condition(self, condition):
        if condition in ("CONTROL_FULL_GUD84", "FULLHINT_GUD84"):
            roles, ratio = ROLES, 1.0
        else:
            suffix = condition.split("_", 1)[1]
            roles = {"GATE28": ("gate_proj",), "UP28": ("up_proj",),
                     "DOWN28": ("down_proj",), "GUD84": ROLES}[suffix]
            ratio = 1.0 / (28 * len(roles))
        mode = "CONTROL" if condition.startswith("CONTROL_") else "FAIR"
        return mode, roles, ratio

    def _policy(self, condition):
        mode, roles, ratio = self._condition(condition)
        selected = {(layer, role) for layer in range(28) for role in roles}
        stream = f"stream-{condition}"
        updates = []
        for sequence, (phase, call_index, key) in enumerate(
                ((phase, call_index, key)
                 for phase in PHASES
                 for call_index, key in enumerate(self.natural_order(phase))
                 if key in selected), 1):
            module = self.module_by_key[key]
            updates.append({"sequence_index": sequence, "phase": phase,
                            "natural_call_index": call_index,
                            "layer_index": key[0], "role": key[1],
                            "attached_immediately_before": True,
                            "base_pointer": module["qweight_pointer"],
                            "num_bytes": module["qweight_bytes"],
                            "stream_identity": stream, "reset_performed": False,
                            "hit_ratio": ratio,
                            "hit_prop": "NORMAL" if mode == "CONTROL" else "PERSISTING",
                            "miss_prop": "NORMAL" if mode == "CONTROL" else "STREAMING",
                            "target_persisting": mode != "CONTROL"})
        return {"status": "PASS", "condition": condition,
                "selected_modules": [{"layer_index": layer, "role": role}
                                     for layer, role in sorted(selected)],
                "requested_setaside_bytes": REQUESTED_SETASIDE_BYTES,
                "actual_setaside_bytes": ACTUAL_SETASIDE_BYTES,
                "stream_identity": stream,
                "reset_before": {"status": "PASS", "performed": True,
                                 "operation": "reset persisting L2", "event_index": 0},
                "updates": updates,
                "reset_after": {"status": "PASS", "performed": True,
                                "operation": "reset persisting L2",
                                "event_index": len(updates) + 1},
                "other_reset_events": []}

    def _write_profile(self, number, condition, role, prefix="P"):
        stem = f"{prefix}{number:02d}"
        range_name = f"C16_E1_OPERATOR_{condition}_L0_{role}_D3"
        policy = self.root / f"{stem}_POLICY.json"
        policy.write_text(json.dumps(self._policy(condition), sort_keys=True) + "\n",
                          encoding="utf-8")
        policy_sha = file_sha(policy)
        base = self.root / f"{stem}_BASE.csv"
        available = [row for row in self.catalog if row["available"]]
        header = ["ID", "Process ID", "Kernel Name", "NVTX Push/Pop_Range",
                  "profiler__replayer_passes", *[row["metric_name"] for row in available]]
        units = ["", "", "", "", "", *[row["unit"] for row in available]]
        with base.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerow(units)
            writer.writerow(["1", "77", GEMM, range_name, "2", "100", "200", "300", "400", "40"])
            writer.writerow(["2", "77", REDUCE, range_name, "2", "10", "20", "30", "40", "10"])
        metrics = ",".join(row["metric_name"] for row in available)
        session = self.root / f"{stem}_SESSION.csv"
        session.write_text(f"ncu --replay-mode application --cache-control none "
                           f"--nvtx-include {range_name}/ --metrics {metrics}\n", encoding="utf-8")
        identity = {"status": "PASS", "condition": condition, "layer_index": 0,
                    "role": role, "decode_index": 3, "generated_token_id": TOKEN,
                    "accepted_prefix_sha256": SHA_A, "input_sha256": SHA_B,
                    "output_sha256": SHA_C, "range_name": range_name,
                    "policy_history_sha256": policy_sha}
        profile = self.root / f"{stem}_PROFILE.log"
        profile.write_text(json.dumps(identity, sort_keys=True) + "\n" +
                           json.dumps(identity, sort_keys=True) + "\n", encoding="utf-8")
        return {"condition": condition, "layer_index": 0, "role": role,
                "decode_index": 3, "generated_token_id": TOKEN,
                "accepted_prefix_sha256": SHA_A, "input_sha256": SHA_B,
                "output_sha256": SHA_C, "range_name": range_name,
                "expected_kernel_names": [GEMM, REDUCE], "base_path": base.name,
                "session_path": session.name, "profile_path": profile.name,
                "policy_history_path": policy.name}

    def _path(self, index, kind):
        return self.root / self.document["profiles"][index][f"{kind}_path"]

    def test_exact_12_matrix_and_category_aggregation(self):
        result = consume(self.document, self.root)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["profile_count"], 12)
        self.assertEqual(result["profiles"][0]["base"]["additive_semantic_sums"]["DRAM_BYTES"], 330)
        self.assertEqual(result["profiles"][0]["base"]["additive_semantic_sums"]["KERNEL_ELAPSED_CYCLES"], 440)
        self.assertNotIn("LONG_SCOREBOARD_STALL",
                         result["profiles"][0]["base"]["additive_semantic_sums"])
        self.assertEqual([row["role"] for row in result["natural_call_order"]["PREFILL"][:3]],
                         ["up_proj", "down_proj", "gate_proj"])
        self.assertNotEqual(result["natural_call_order"]["PREFILL"],
                            result["natural_call_order"]["D1"])

    def test_duplicate_or_missing_matrix_point_fails(self):
        document = copy.deepcopy(self.document)
        document["profiles"][-1] = copy.deepcopy(document["profiles"][0])
        with self.assertRaisesRegex(OperatorNCUError, "duplicate operator-family"):
            consume(document, self.root)
        document = copy.deepcopy(self.document)
        document["profiles"].pop()
        with self.assertRaisesRegex(OperatorNCUError, "exact 12-profile"):
            consume(document, self.root)

    def test_unit_mismatch_fails(self):
        path = self._path(0, "base")
        with path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.reader(stream))
        rows[1][5] = "sector"
        with path.open("w", newline="", encoding="utf-8") as stream:
            csv.writer(stream).writerows(rows)
        with self.assertRaisesRegex(OperatorNCUError, "BASE unit mismatch"):
            consume(self.document, self.root)

    def test_pass_count_and_pass_identity_fail_closed(self):
        path = self._path(0, "profile")
        path.write_text(path.read_text(encoding="utf-8").splitlines()[0] + "\n", encoding="utf-8")
        with self.assertRaisesRegex(OperatorNCUError, "replayer passes/PASS receipt count"):
            consume(self.document, self.root)
        self.tearDown(); self.setUp()
        path = self._path(0, "profile")
        lines = path.read_text(encoding="utf-8").splitlines()
        altered = json.loads(lines[1]); altered["generated_token_id"] += 1
        path.write_text(lines[0] + "\n" + json.dumps(altered) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(OperatorNCUError, "semantic/token/policy identity"):
            consume(self.document, self.root)

    def test_runtime_query_version_and_sha_fail_closed(self):
        document = copy.deepcopy(self.document)
        document["runtime_metric_query"]["ncu_version"] = "wrong version"
        with self.assertRaisesRegex(OperatorNCUError, "query/version identity"):
            consume(document, self.root)
        document = copy.deepcopy(self.document)
        document["runtime_metric_query"]["sha256"] = SHA_D
        with self.assertRaisesRegex(OperatorNCUError, "query SHA mismatch"):
            consume(document, self.root)

    def test_kernel_inventory_and_duplicate_rows_fail(self):
        path = self._path(0, "base")
        with path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.reader(stream))
        rows.pop()
        with path.open("w", newline="", encoding="utf-8") as stream:
            csv.writer(stream).writerows(rows)
        with self.assertRaisesRegex(OperatorNCUError, "kernel inventory mismatch"):
            consume(self.document, self.root)
        self.tearDown(); self.setUp()
        path = self._path(0, "base")
        with path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.reader(stream))
        rows.append(rows[-1])
        with path.open("w", newline="", encoding="utf-8") as stream:
            csv.writer(stream).writerows(rows)
        with self.assertRaisesRegex(OperatorNCUError, "duplicate row|kernel inventory"):
            consume(self.document, self.root)

    def test_session_replay_cache_range_metric_identity_fails(self):
        path = self._path(0, "session")
        path.write_text(path.read_text(encoding="utf-8").replace("application", "kernel"),
                        encoding="utf-8")
        with self.assertRaisesRegex(OperatorNCUError, "replay mode mismatch"):
            consume(self.document, self.root)

    def test_semantic_occurrence_fails(self):
        document = copy.deepcopy(self.document)
        document["profiles"][0]["decode_index"] = 2
        with self.assertRaisesRegex(OperatorNCUError, "wrong semantic occurrence"):
            consume(document, self.root)

    def test_policy_wrong_attachment_and_incomplete_history_fail(self):
        path = self._path(0, "policy_history")
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["updates"][0]["natural_call_index"] += 1
        path.write_text(json.dumps(raw) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(OperatorNCUError, "attached to wrong natural"):
            consume(self.document, self.root)
        self.tearDown(); self.setUp()
        path = self._path(0, "policy_history")
        raw = json.loads(path.read_text(encoding="utf-8")); raw["updates"].pop()
        path.write_text(json.dumps(raw) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(OperatorNCUError, "complete natural policy history"):
            consume(self.document, self.root)

    def test_policy_hit_ratio_reset_and_setaside_fail(self):
        path = self._path(0, "policy_history")
        raw = json.loads(path.read_text(encoding="utf-8")); raw["updates"][0]["hit_ratio"] = 0.5
        path.write_text(json.dumps(raw) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(OperatorNCUError, "hitRatio"):
            consume(self.document, self.root)
        self.tearDown(); self.setUp()
        path = self._path(0, "policy_history")
        raw = json.loads(path.read_text(encoding="utf-8")); raw["updates"][0]["reset_performed"] = True
        path.write_text(json.dumps(raw) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(OperatorNCUError, "in-run reset"):
            consume(self.document, self.root)
        self.tearDown(); self.setUp()
        path = self._path(0, "policy_history")
        raw = json.loads(path.read_text(encoding="utf-8")); raw["actual_setaside_bytes"] += 1
        path.write_text(json.dumps(raw) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(OperatorNCUError, "actual set-aside drift"):
            consume(self.document, self.root)

    def test_module_authority_drift_fails(self):
        document = copy.deepcopy(self.document)
        document["module_authority"]["modules"][0]["backend"] = "torch"
        with self.assertRaisesRegex(OperatorNCUError, "class/backend drift"):
            consume(document, self.root)

    def test_fullhint_false_requires_absent_evidence(self):
        document = copy.deepcopy(self.document)
        document["fullhint_ncu"]["profiles"] = [copy.deepcopy(document["profiles"][0])]
        with self.assertRaisesRegex(OperatorNCUError, "false/true evidence matrix"):
            consume(document, self.root)
        document = copy.deepcopy(self.document)
        document["fullhint_ncu"]["triggered"] = True
        with self.assertRaisesRegex(OperatorNCUError, "trigger mismatch"):
            consume(document, self.root)

    def test_fullhint_true_requires_exact_six_and_passes(self):
        document = copy.deepcopy(self.document)
        document["fullhint_ncu"].update({
            "fair_gud84_whole_decode_benefit": 0.001,
            "fullhint_gud84_whole_decode_benefit": 0.006,
            "triggered": True,
            "profiles": [self._write_profile(100 + index, condition, role, "F")
                         for index, (condition, role) in enumerate(sorted(FULLHINT_MATRIX))],
        })
        result = consume(document, self.root)
        self.assertTrue(result["fullhint_ncu"]["triggered"])
        self.assertEqual(result["fullhint_ncu"]["profile_count"], 6)
        document["fullhint_ncu"]["profiles"].pop()
        with self.assertRaisesRegex(OperatorNCUError, "false/true evidence matrix|exact 6-profile"):
            consume(document, self.root)


if __name__ == "__main__":
    unittest.main()
