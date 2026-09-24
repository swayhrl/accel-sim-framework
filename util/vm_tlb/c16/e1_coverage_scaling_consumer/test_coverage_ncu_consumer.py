#!/usr/bin/env python3
import copy
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from coverage_ncu_consumer import (
    ACTUAL_SETASIDE_BYTES,
    LAYER_ORDER,
    MATRIX,
    PHASES,
    REQUESTED_SETASIDE_BYTES,
    CoverageNCUError,
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


class CoverageNCUConsumerTests(unittest.TestCase):
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
            {"category": "LONG_SCOREBOARD_STALL", "available": True,
             "metric_name": "smsp__warp_issue_stalled_long_scoreboard_per_warp_active.pct",
             "unit": "%", "aggregation": "PER_KERNEL_ONLY"},
            {"category": "LSU_UTILIZATION", "available": False,
             "metric_name": None, "unit": None, "reason": "not exposed by installed NCU"},
        ]
        self.document = {
            "schema_version": 1,
            "runtime_metric_query": {"status": "PASS", "command": "ncu --query-metrics",
                                     "ncu_version": version, "path": query.name,
                                     "sha256": file_sha(query)},
            "metric_availability": self.catalog,
            "qweight_regions": {
                str(layer): {"pointer": 0x100000 + layer * 0x10000,
                             "bytes": 6680576, "contiguous": True}
                for layer in range(28)
            },
            "profiles": [],
        }
        for number, (condition, layer) in enumerate(sorted(MATRIX)):
            self.document["profiles"].append(self._write_profile(number, condition, layer))

    def tearDown(self):
        self.temp.cleanup()

    def _policy(self, condition):
        count = int(condition.rsplit("N", 1)[1])
        mode = condition.split("_", 1)[0]
        selected = list(LAYER_ORDER[:count])
        stream = f"stream-{condition}"
        updates = []
        for index, (phase, layer) in enumerate(
                ((phase, layer) for phase in PHASES for layer in sorted(selected)), 1):
            region = self.document["qweight_regions"][str(layer)]
            updates.append({
                "sequence_index": index, "phase": phase, "layer_index": layer,
                "base_pointer": region["pointer"], "num_bytes": region["bytes"],
                "stream_identity": stream, "reset_performed": False,
                "hit_ratio": 1.0 / count,
                "hit_prop": "NORMAL" if mode == "CONTROL" else "PERSISTING",
                "miss_prop": "NORMAL" if mode == "CONTROL" else "STREAMING",
                "target_persisting": mode == "FAIR",
            })
        return {"status": "PASS", "condition": condition,
                "selected_layers": selected,
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

    def _write_profile(self, number, condition, layer):
        stem = f"P{number:02d}"
        range_name = f"C16_E1_COVERAGE_{condition}_L{layer}_UP_D3"
        policy = self.root / f"{stem}_POLICY.json"
        policy.write_text(json.dumps(self._policy(condition), sort_keys=True) + "\n", encoding="utf-8")
        policy_sha = file_sha(policy)
        base = self.root / f"{stem}_BASE.csv"
        header = ["ID", "Process ID", "Kernel Name", "NVTX Push/Pop_Range",
                  "profiler__replayer_passes", *[row["metric_name"] for row in self.catalog
                                                  if row["available"]]]
        units = ["", "", "", "", "", "byte", "byte", "byte", "%"]
        with base.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerow(units)
            writer.writerow(["1", "77", GEMM, range_name, "2", "100", "200", "300", "40"])
            writer.writerow(["2", "77", REDUCE, range_name, "2", "10", "20", "30", "10"])
        metrics = ",".join(row["metric_name"] for row in self.catalog if row["available"])
        session = self.root / f"{stem}_SESSION.csv"
        session.write_text(f"ncu --replay-mode application --cache-control none "
                           f"--nvtx-include {range_name}/ --metrics {metrics}\n", encoding="utf-8")
        identity = {"status": "PASS", "condition": condition, "layer_index": layer,
                    "role": "up_proj", "decode_index": 3,
                    "generated_token_id": TOKEN, "accepted_prefix_sha256": SHA_A,
                    "input_sha256": SHA_B, "output_sha256": SHA_C,
                    "range_name": range_name, "policy_history_sha256": policy_sha}
        profile = self.root / f"{stem}_PROFILE.log"
        profile.write_text(json.dumps(identity, sort_keys=True) + "\n" +
                           json.dumps(identity, sort_keys=True) + "\n", encoding="utf-8")
        return {"condition": condition, "layer_index": layer, "role": "up_proj",
                "decode_index": 3, "generated_token_id": TOKEN,
                "accepted_prefix_sha256": SHA_A, "input_sha256": SHA_B,
                "output_sha256": SHA_C, "range_name": range_name,
                "expected_kernel_names": [GEMM, REDUCE], "base_path": base.name,
                "session_path": session.name, "profile_path": profile.name,
                "policy_history_path": policy.name}

    def _profile_path(self, index, kind):
        return self.root / self.document["profiles"][index][f"{kind}_path"]

    def test_exact_16_matrix_additive_and_nonadditive_rules(self):
        result = consume(self.document, self.root)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["profile_count"], 16)
        first = result["profiles"][0]
        self.assertEqual(first["profile"]["pass_receipt_count"], 2)
        self.assertEqual(first["base"]["additive_semantic_sums"]["DRAM_BYTES"], 330)
        stalls = [metric for kernel in first["base"]["kernel_metrics"]
                  for metric in kernel["metrics"] if metric["category"] == "LONG_SCOREBOARD_STALL"]
        self.assertEqual([row["value"] for row in stalls], [40, 10])
        self.assertNotIn("LONG_SCOREBOARD_STALL", first["base"]["additive_semantic_sums"])

    def test_process_local_profile_regions_pass(self):
        document = copy.deepcopy(self.document)
        local = document.pop("qweight_regions")
        for profile in document["profiles"]:
            profile["qweight_regions"] = copy.deepcopy(local)
        self.assertEqual(consume(document, self.root)["profile_count"], 16)

    def test_duplicate_or_missing_matrix_point_fails(self):
        duplicate = copy.deepcopy(self.document)
        duplicate["profiles"][-1] = copy.deepcopy(duplicate["profiles"][0])
        with self.assertRaisesRegex(CoverageNCUError, "duplicate coverage NCU"):
            consume(duplicate, self.root)
        missing = copy.deepcopy(self.document)
        missing["profiles"].pop()
        with self.assertRaisesRegex(CoverageNCUError, "exact 16-profile"):
            consume(missing, self.root)

    def test_wrong_semantic_occurrence_fails(self):
        document = copy.deepcopy(self.document)
        document["profiles"][0]["decode_index"] = 2
        with self.assertRaisesRegex(CoverageNCUError, "wrong semantic occurrence"):
            consume(document, self.root)

    def test_query_version_or_sha_ambiguity_fails(self):
        document = copy.deepcopy(self.document)
        document["runtime_metric_query"]["ncu_version"] = "some other version"
        with self.assertRaisesRegex(CoverageNCUError, "query/version identity ambiguity"):
            consume(document, self.root)
        document = copy.deepcopy(self.document)
        document["runtime_metric_query"]["sha256"] = SHA_D
        with self.assertRaisesRegex(CoverageNCUError, "query SHA mismatch"):
            consume(document, self.root)

    def test_base_unit_mismatch_fails(self):
        path = self._profile_path(0, "base")
        with path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.reader(stream))
        rows[1][5] = "sector"
        with path.open("w", newline="", encoding="utf-8") as stream:
            csv.writer(stream).writerows(rows)
        with self.assertRaisesRegex(CoverageNCUError, "BASE unit mismatch"):
            consume(self.document, self.root)

    def test_pass_receipt_count_must_match_base(self):
        path = self._profile_path(0, "profile")
        path.write_text(path.read_text(encoding="utf-8").splitlines()[0] + "\n", encoding="utf-8")
        with self.assertRaisesRegex(CoverageNCUError, "replayer passes/PASS receipt count"):
            consume(self.document, self.root)

    def test_profile_pass_identity_drift_fails(self):
        path = self._profile_path(0, "profile")
        lines = path.read_text(encoding="utf-8").splitlines()
        altered = json.loads(lines[1])
        altered["generated_token_id"] += 1
        path.write_text(lines[0] + "\n" + json.dumps(altered) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(CoverageNCUError, "semantic/token/policy identity mismatch"):
            consume(self.document, self.root)

    def test_kernel_inventory_or_duplicate_row_fails(self):
        path = self._profile_path(0, "base")
        with path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.reader(stream))
        rows.pop()
        with path.open("w", newline="", encoding="utf-8") as stream:
            csv.writer(stream).writerows(rows)
        with self.assertRaisesRegex(CoverageNCUError, "kernel inventory mismatch"):
            consume(self.document, self.root)

        self.tearDown()
        self.setUp()
        path = self._profile_path(0, "base")
        with path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.reader(stream))
        rows.append(rows[-1])
        with path.open("w", newline="", encoding="utf-8") as stream:
            csv.writer(stream).writerows(rows)
        with self.assertRaisesRegex(CoverageNCUError, "duplicate row|kernel inventory"):
            consume(self.document, self.root)

    def test_missing_or_incomplete_policy_history_fails(self):
        path = self._profile_path(0, "policy_history")
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["updates"].pop()
        path.write_text(json.dumps(raw) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(CoverageNCUError, "complete policy history"):
            consume(self.document, self.root)

    def test_wrong_hit_ratio_and_in_run_reset_fail(self):
        path = self._profile_path(0, "policy_history")
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["updates"][0]["hit_ratio"] = 0.5
        path.write_text(json.dumps(raw) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(CoverageNCUError, "hitRatio"):
            consume(self.document, self.root)

        self.tearDown()
        self.setUp()
        path = self._profile_path(0, "policy_history")
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["updates"][0]["reset_performed"] = True
        path.write_text(json.dumps(raw) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(CoverageNCUError, "in-run reset"):
            consume(self.document, self.root)

    def test_session_replay_cache_range_metric_identity_fails(self):
        path = self._profile_path(0, "session")
        path.write_text(path.read_text(encoding="utf-8").replace("application", "kernel"),
                        encoding="utf-8")
        with self.assertRaisesRegex(CoverageNCUError, "replay mode mismatch"):
            consume(self.document, self.root)


if __name__ == "__main__":
    unittest.main()
