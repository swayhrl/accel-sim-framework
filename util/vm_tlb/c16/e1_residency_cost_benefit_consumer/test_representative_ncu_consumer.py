#!/usr/bin/env python3
import copy
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from representative_ncu_consumer import (
    BUDGET_REQUESTS,
    PHASES,
    RepresentativeNCUError,
    consume,
)


SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64
QWEIGHT_BYTES = 33_947_648


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RepresentativeNCUConsumerTests(unittest.TestCase):
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
            {"category": "LSU_UTILIZATION", "available": False, "metric_name": None,
             "unit": None, "aggregation": "PER_KERNEL_ONLY", "reason": "unavailable"},
        ]
        self.document = {
            "schema_version": 1,
            "runtime_metric_query": {"status": "PASS", "command": "ncu --query-metrics",
                                     "ncu_version": version, "path": query.name,
                                     "sha256": file_sha(query)},
            "metric_availability": self.catalog,
            "exact_up_proj_qweight_bytes": QWEIGHT_BYTES,
            "budget_authority": [
                {"budget": "B16", "requested_setaside_bytes": BUDGET_REQUESTS["B16"],
                 "actual_setaside_bytes": 18_874_368, "runtime_max_setaside_bytes": 50_331_648},
                {"budget": "BFULL", "requested_setaside_bytes": BUDGET_REQUESTS["BFULL"],
                 "actual_setaside_bytes": 37_748_736, "runtime_max_setaside_bytes": 50_331_648},
            ],
            "profiles": [],
        }
        number = 0
        for budget in ("B16", "BFULL"):
            for mode in ("CONTROL", "FAIR"):
                for target in ("up_proj", "self_attn"):
                    self.document["profiles"].append(self._write_profile(number, budget, mode, target))
                    number += 1

    def tearDown(self):
        self.temp.cleanup()

    def _budget(self, name):
        return next(row for row in self.document["budget_authority"] if row["budget"] == name)

    def _policy(self, profile_number, budget, mode, process):
        authority = self._budget(budget)
        condition = f"{mode}_UP28_{budget}"
        ratio = min(1.0, authority["requested_setaside_bytes"] / (28 * QWEIGHT_BYTES))
        base0 = 0x100000000 + profile_number * 0x1000000000
        stride = QWEIGHT_BYTES + 4096
        modules = [
            {"layer_index": layer, "role": "up_proj", "module_class": "WQLinear_GEMM",
             "backend": "AWQ", "qweight_pointer": base0 + layer * stride,
             "qweight_bytes": QWEIGHT_BYTES, "qweight_contiguous": True,
             "process_identity": process}
            for layer in range(28)
        ]
        updates = []
        for sequence, (phase, layer) in enumerate(
                ((phase, layer) for phase in PHASES for layer in range(28)), 1):
            module = modules[layer]
            updates.append({"sequence_index": sequence, "phase": phase,
                            "natural_call_index": layer * 3 + 1,
                            "layer_index": layer, "role": "up_proj",
                            "attached_immediately_before": True,
                            "base_pointer": module["qweight_pointer"],
                            "num_bytes": QWEIGHT_BYTES, "process_identity": process,
                            "stream_identity": f"stream-{process}", "reset_performed": False,
                            "hit_ratio": ratio,
                            "hit_prop": "NORMAL" if mode == "CONTROL" else "PERSISTING",
                            "miss_prop": "NORMAL" if mode == "CONTROL" else "STREAMING",
                            "target_persisting": mode == "FAIR"})
        return {"status": "PASS", "condition": condition, "budget": budget,
                "process_identity": process, **{key: authority[key] for key in
                    ("requested_setaside_bytes", "actual_setaside_bytes", "runtime_max_setaside_bytes")},
                "selected_modules": modules, "hit_ratio": ratio,
                "stream_identity": f"stream-{process}",
                "reset_before": {"status": "PASS", "performed": True,
                                 "operation": "reset persisting L2", "event_index": 0},
                "updates": updates,
                "reset_after": {"status": "PASS", "performed": True,
                                "operation": "reset persisting L2", "event_index": 141},
                "other_reset_events": []}

    def _write_profile(self, number, budget, mode, target):
        stem = f"P{number:02d}"
        condition = f"{mode}_UP28_{budget}"
        process = f"fresh-process-{number}"
        pid = str(700 + number)
        range_name = f"C16_E1_COST_{condition}_L0_{target}_D3"
        policy_path = self.root / f"{stem}_POLICY.json"
        policy_path.write_text(json.dumps(self._policy(number, budget, mode, process), sort_keys=True) + "\n",
                               encoding="utf-8")
        policy_sha = file_sha(policy_path)
        kernels = (["awq_gemm", "awq_reduce"] if target == "up_proj"
                   else ["flash_attention", "flash_attention", "attention_epilogue"])
        available = [row for row in self.catalog if row["available"]]
        base_path = self.root / f"{stem}_BASE.csv"
        header = ["ID", "Process ID", "Kernel Name", "NVTX Push/Pop_Range",
                  "profiler__replayer_passes", *[row["metric_name"] for row in available]]
        units = ["", "", "", "", "", *[row["unit"] for row in available]]
        with base_path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream); writer.writerow(header); writer.writerow(units)
            for index, kernel in enumerate(kernels, 1):
                writer.writerow([index, pid, kernel, range_name, 2,
                                 100 * index, 200 * index, 300 * index, 400 * index, 10 * index])
        metrics = ",".join(row["metric_name"] for row in available)
        session_path = self.root / f"{stem}_SESSION.csv"
        session_path.write_text(f"ncu --replay-mode application --cache-control none "
                                f"--nvtx-include {range_name}/ --metrics {metrics}\n", encoding="utf-8")
        receipt = {"status": "PASS", "budget": budget, "mode": mode, "condition": condition,
                   "target_semantic": target, "layer_index": 0, "decode_index": 3,
                   "generated_token_id": 3950, "accepted_prefix_sha256": SHA_A,
                   "input_sha256": SHA_B, "output_sha256": SHA_C,
                   "process_identity": process, "ncu_process_id": pid,
                   "range_name": range_name, "policy_history_sha256": policy_sha}
        profile_path = self.root / f"{stem}_PROFILE.log"
        profile_path.write_text(json.dumps(receipt, sort_keys=True) + "\n" +
                                json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
        return {key: receipt[key] for key in receipt if key not in ("status", "policy_history_sha256")} | {
            "expected_kernel_names": kernels, "base_path": base_path.name,
            "session_path": session_path.name, "profile_path": profile_path.name,
            "policy_history_path": policy_path.name}

    def _file(self, index, kind):
        return self.root / self.document["profiles"][index][f"{kind}_path"]

    def _mutate_json(self, index, kind, mutate):
        path = self._file(index, kind); raw = json.loads(path.read_text(encoding="utf-8")); mutate(raw)
        path.write_text(json.dumps(raw, sort_keys=True) + "\n", encoding="utf-8")

    def test_exact_eight_matrix_process_local_and_multikernel_aggregation(self):
        result = consume(self.document, self.root)
        self.assertEqual((result["status"], result["profile_count"]), ("PASS", 8))
        self.assertEqual(result["qweight_pointer_scope"], "PROCESS_LOCAL_NO_CROSS_PROFILE_EQUALITY_REQUIRED")
        attention = next(row for row in result["profiles"] if row["budget"] == "B16" and
                         row["mode"] == "CONTROL" and row["target_semantic"] == "self_attn")
        self.assertEqual(attention["base"]["kernel_name_multiplicity"]["flash_attention"], 2)
        self.assertEqual(len(attention["base"]["per_kernel_metrics"]), 3)
        self.assertEqual(attention["base"]["additive_semantic_sums"]["DRAM_BYTES"], 1800)
        self.assertNotIn("LONG_SCOREBOARD_STALL", attention["base"]["additive_semantic_sums"])
        pointers = [row["policy_history"]["updates"][0]["base_pointer"] for row in result["profiles"]]
        self.assertEqual(len(set(pointers)), 8)

    def test_missing_or_duplicate_matrix_point_fails(self):
        document = copy.deepcopy(self.document); document["profiles"][-1] = copy.deepcopy(document["profiles"][0])
        with self.assertRaisesRegex(RepresentativeNCUError, "duplicate representative"):
            consume(document, self.root)
        document = copy.deepcopy(self.document); document["profiles"].pop()
        with self.assertRaisesRegex(RepresentativeNCUError, "exact 8-profile"):
            consume(document, self.root)

    def test_runtime_query_sha_and_version_fail(self):
        document = copy.deepcopy(self.document); document["runtime_metric_query"]["sha256"] = "d" * 64
        with self.assertRaisesRegex(RepresentativeNCUError, "query SHA mismatch"):
            consume(document, self.root)
        document = copy.deepcopy(self.document); document["runtime_metric_query"]["ncu_version"] = "wrong"
        with self.assertRaisesRegex(RepresentativeNCUError, "query/version"):
            consume(document, self.root)

    def test_catalog_and_base_unit_mismatch_fail(self):
        document = copy.deepcopy(self.document); document["metric_availability"][4]["aggregation"] = "SEMANTIC_SUM"
        with self.assertRaisesRegex(RepresentativeNCUError, "aggregation mismatch"):
            consume(document, self.root)
        path = self._file(0, "base")
        with path.open(newline="", encoding="utf-8") as stream: rows = list(csv.reader(stream))
        rows[1][5] = "sector"
        with path.open("w", newline="", encoding="utf-8") as stream: csv.writer(stream).writerows(rows)
        with self.assertRaisesRegex(RepresentativeNCUError, "BASE unit mismatch"):
            consume(self.document, self.root)

    def test_session_replay_cache_range_and_metric_fail(self):
        path = self._file(0, "session")
        path.write_text(path.read_text(encoding="utf-8").replace("application", "kernel"), encoding="utf-8")
        with self.assertRaisesRegex(RepresentativeNCUError, "replay mode mismatch"):
            consume(self.document, self.root)

    def test_multipass_count_and_identity_fail(self):
        path = self._file(0, "profile"); lines = path.read_text(encoding="utf-8").splitlines()
        path.write_text(lines[0] + "\n", encoding="utf-8")
        with self.assertRaisesRegex(RepresentativeNCUError, "replayer passes/PASS receipt count"):
            consume(self.document, self.root)
        self.tearDown(); self.setUp(); path = self._file(0, "profile")
        lines = path.read_text(encoding="utf-8").splitlines(); changed = json.loads(lines[1]); changed["input_sha256"] = "d" * 64
        path.write_text(lines[0] + "\n" + json.dumps(changed) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(RepresentativeNCUError, "semantic/token/process/policy identity"):
            consume(self.document, self.root)

    def test_kernel_inventory_and_process_identity_fail(self):
        path = self._file(1, "base")
        with path.open(newline="", encoding="utf-8") as stream: rows = list(csv.reader(stream))
        rows.pop()
        with path.open("w", newline="", encoding="utf-8") as stream: csv.writer(stream).writerows(rows)
        with self.assertRaisesRegex(RepresentativeNCUError, "kernel inventory mismatch"):
            consume(self.document, self.root)
        self.tearDown(); self.setUp(); path = self._file(0, "base")
        with path.open(newline="", encoding="utf-8") as stream: rows = list(csv.reader(stream))
        rows[2][1] = "9999"
        with path.open("w", newline="", encoding="utf-8") as stream: csv.writer(stream).writerows(rows)
        with self.assertRaisesRegex(RepresentativeNCUError, "process identity mismatch"):
            consume(self.document, self.root)

    def test_budget_query_back_and_hit_ratio_fail(self):
        self._mutate_json(0, "policy_history", lambda raw: raw.__setitem__("actual_setaside_bytes", raw["actual_setaside_bytes"] + 1))
        with self.assertRaisesRegex(RepresentativeNCUError, "query-back drift"):
            consume(self.document, self.root)
        self.tearDown(); self.setUp()
        self._mutate_json(0, "policy_history", lambda raw: raw.__setitem__("hit_ratio", 0.5))
        with self.assertRaisesRegex(RepresentativeNCUError, "hitRatio mismatch"):
            consume(self.document, self.root)

    def test_policy_complete_28_up_and_140_updates_fail(self):
        self._mutate_json(0, "policy_history", lambda raw: raw["updates"].pop())
        with self.assertRaisesRegex(RepresentativeNCUError, "complete 140-update"):
            consume(self.document, self.root)
        self.tearDown(); self.setUp()
        self._mutate_json(0, "policy_history", lambda raw: raw["selected_modules"].pop())
        with self.assertRaisesRegex(RepresentativeNCUError, "exact 28"):
            consume(self.document, self.root)

    def test_process_local_pointer_size_and_scope_fail(self):
        self._mutate_json(0, "policy_history", lambda raw: raw["selected_modules"][0].__setitem__("process_identity", "other"))
        with self.assertRaisesRegex(RepresentativeNCUError, "process-local qweight authority"):
            consume(self.document, self.root)
        self.tearDown(); self.setUp()
        self._mutate_json(0, "policy_history", lambda raw: raw["updates"][0].__setitem__("num_bytes", 4))
        with self.assertRaisesRegex(RepresentativeNCUError, "exact full qweight"):
            consume(self.document, self.root)

    def test_wrong_selected_family_and_attachment_fail(self):
        self._mutate_json(0, "policy_history", lambda raw: raw["selected_modules"][0].__setitem__("role", "gate_proj"))
        with self.assertRaisesRegex(RepresentativeNCUError, "selected family"):
            consume(self.document, self.root)
        self.tearDown(); self.setUp()
        self._mutate_json(0, "policy_history", lambda raw: raw["updates"][1].__setitem__("natural_call_index", 1))
        with self.assertRaisesRegex(RepresentativeNCUError, "duplicate update attachment"):
            consume(self.document, self.root)

    def test_in_run_reset_and_policy_semantics_fail(self):
        self._mutate_json(0, "policy_history", lambda raw: raw["updates"][0].__setitem__("reset_performed", True))
        with self.assertRaisesRegex(RepresentativeNCUError, "in-run reset"):
            consume(self.document, self.root)
        self.tearDown(); self.setUp()
        self._mutate_json(0, "policy_history", lambda raw: raw["updates"][0].__setitem__("hit_prop", "PERSISTING"))
        with self.assertRaisesRegex(RepresentativeNCUError, "policy semantics mismatch"):
            consume(self.document, self.root)

    def test_semantic_occurrence_token_and_policy_sha_fail(self):
        document = copy.deepcopy(self.document); document["profiles"][0]["decode_index"] = 2
        with self.assertRaisesRegex(RepresentativeNCUError, "wrong semantic occurrence"):
            consume(document, self.root)
        path = self._file(0, "profile"); lines = path.read_text(encoding="utf-8").splitlines()
        changed = json.loads(lines[0]); changed["generated_token_id"] += 1
        path.write_text(json.dumps(changed) + "\n" + lines[1] + "\n", encoding="utf-8")
        with self.assertRaisesRegex(RepresentativeNCUError, "semantic/token/process/policy identity"):
            consume(self.document, self.root)

    def test_actual_exceeds_runtime_max_fails(self):
        document = copy.deepcopy(self.document); document["budget_authority"][0]["actual_setaside_bytes"] = 99_999_999
        with self.assertRaisesRegex(RepresentativeNCUError, "exceeds runtime maximum"):
            consume(document, self.root)


if __name__ == "__main__":
    unittest.main()
