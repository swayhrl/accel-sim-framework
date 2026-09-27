import array
import json
import shlex
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import analyze_pressure as ap


def write_u64(path, values):
    data = array.array("Q", values)
    if sys.byteorder != "little": data.byteswap()
    path.write_bytes(data.tobytes())


class PressureAggregateTest(unittest.TestCase):
    def fixture(self, root):
        summaries = root / "summaries"
        mapper_rows = ["line_address\tsubpartition\tset"]
        for kernel_id in range(1, 7):
            directory = summaries / "kernels" / str(kernel_id)
            directory.mkdir(parents=True)
            address = 0x1000 + kernel_id * 0x80
            write_u64(directory / "all.u64", [address])
            write_u64(directory / "non.u64", [address])
            hist = [0] * 8; hist[kernel_id % 8] = kernel_id
            write_u64(directory / "refs.u64", hist)
            mapper_rows.append(f"{address:#x}\t{(kernel_id % 8) // 4}\t{kernel_id % 4}")
            decode = (kernel_id + 1) // 2
            target = kernel_id % 2 == 0
            boundary = {str(cls): {
                "referenced_target_unique_lines": 3,
                "semantic_range_start_kernel": kernel_id,
                "semantic_range_end_kernel": kernel_id,
                "prefix": {"dynamic_instructions": 2, "global_address_references": 1,
                  "non_target_address_references": 1, "artifacts": {
                    "all_unique_lines_u64le": "all.u64", "non_target_unique_lines_u64le": "non.u64",
                    "all_set_refs_u64le": "refs.u64"}},
                "suffix": {"dynamic_instructions": 3, "global_address_references": 1,
                  "non_target_address_references": 1, "artifacts": {
                    "all_unique_lines_u64le": "all.u64", "non_target_unique_lines_u64le": "non.u64",
                    "all_set_refs_u64le": "refs.u64"}}
                } for cls in range(1, 29)} if target else {}
            summary = {"schema": "C16_E1_TRACE_KERNEL_SUMMARY_V1", "kernel_id": kernel_id,
              "decode_index": decode, "semantic_layer": None, "semantic_identity": "UNKNOWN",
              "dynamic_instructions": 10, "global_address_references": 2,
              "non_target_address_references": 2,
              "per_target_class_references": {str(cls): 1 for cls in range(1, 29)} if target else {},
              "artifacts": {"all_unique_lines_u64le": "all.u64",
                "non_target_unique_lines_u64le": "non.u64", "all_set_refs_u64le": "refs.u64"},
              "target_boundaries": boundary}
            (directory / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
        mapping = {"schema": "C16_E1_QWEIGHT_L2_SET_MAPPING_MAPPER_V1",
          "status": "PASS", "sidecar_sha256": "a" * 64,
          "mapper": {"accepted_core_sha": "core", "config_sha256": "config"},
          "geometry": {"l2_bytes": 64 << 20, "line_size_bytes": 128,
          "subpartition_count": 2, "sets_per_subpartition": 4, "associativity": 4},
          "regions": [{"layer_index": layer, "target_class": layer + 1, "bytes": 128,
            "line_count": 1, "set_line_counts": [{"subpartition": layer % 2,
              "set": layer % 4, "line_count": 1}]} for layer in range(28)]}
        static = root / "static.json"; static.write_text(json.dumps(mapping), encoding="utf-8")
        mapper = root / "mapper.tsv"; mapper.write_text("\n".join(mapper_rows) + "\n", encoding="utf-8")
        authority = root / "mapper-authority.json"
        authority.write_text(json.dumps({"schema": "fixture-mapper-authority",
                                         "accepted_for_formal": False}), encoding="utf-8")
        (summaries / "TRACE_REFERENCE_SUMMARY.json").write_text(
            json.dumps({"schema": "fixture", "kernel_count": 6}), encoding="utf-8")
        return summaries, static, mapper, authority

    def test_end_to_end_outputs_and_claim_boundaries(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); summaries, static, mapper, authority = self.fixture(root)
            output = root / "out"
            self.assertEqual(0, ap.main(["--summary-root", str(summaries),
                "--static-mapping", str(static), "--line-mapping-tsv", str(mapper),
                "--mapper-authority-json", str(authority),
                "--output-dir", str(output)]))
            matrix = json.loads((output / "PER_LAYER_REUSE_DISTANCE_MATRIX.json").read_text())
            self.assertEqual(56, len(matrix["rows"]))
            self.assertEqual("LAST_TRUE_TARGET_REFERENCE_TO_NEXT_FIRST_TRUE_TARGET_REFERENCE",
                             matrix["boundary"])
            self.assertEqual(1, matrix["rows"][0]["intervening_full_kernel_count"])
            self.assertEqual(3, matrix["rows"][0]["elapsed_dynamic_kernels"])
            self.assertEqual(1, matrix["rows"][0]["semantic_range_intervening_full_kernel_count"])
            self.assertEqual(5, matrix["rows"][0]["same_subpartition_non_target_references"])
            self.assertEqual(matrix["rows"][0]["intervening_unique_128b_lines"],
                             matrix["rows"][0]["intervening_non_target_relative_current_layer_unique_128b_lines"])
            pressure = json.loads((output / "SET_CONFLICT_PRESSURE_ANALYSIS.json").read_text())
            self.assertFalse(pressure["actual_l2_hit_miss_or_eviction_claimed"])
            quota = json.loads((output / "QUOTA_STATIC_MAPPING.json").read_text())
            self.assertEqual(["B8", "B16", "B24", "BFULL"],
                             [item["budget"] for item in quota["budgets"]])
            self.assertTrue(quota["dynamic_pressure_context"]["lowest_median_unique_pressure"])
            self.assertIn("global_quota_sufficient_but_set_local_unfavorable_proxy",
                          quota["budgets"][-1]["per_layer_static_admission"][0])
            static_output = json.loads((output / "QWEIGHT_L2_SET_MAPPING.json").read_text())
            self.assertIn("coefficient_of_variation",
                          static_output["regions"][0]["set_distribution"])
            self.assertEqual("a" * 64, static_output["input_provenance"]["sidecar_sha256"])
            pair_01 = next(item for item in static_output["region_pair_set_overlap"]
                           if item["left_layer"] == 0 and item["right_layer"] == 1)
            self.assertEqual(0, pair_01["weighted_intersection_lines"])
            self.assertEqual(6, pair_01["equal_population_set_count"])
            self.assertEqual(0, pair_01["nine_line_set_intersection"])
            pair_04 = next(item for item in static_output["region_pair_set_overlap"]
                           if item["left_layer"] == 0 and item["right_layer"] == 4)
            self.assertEqual(1, pair_04["weighted_intersection_lines"])
            self.assertEqual(1.0, pair_04["weighted_overlap_over_region_lines"])
            self.assertEqual(8, pair_04["equal_population_set_count"])
            provenance = json.loads((output / "AGGREGATION_PROVENANCE.json").read_text())
            self.assertFalse(provenance["raw_trace_opened"])
            self.assertIsNotNone(provenance["summary_index_sha256"])
            self.assertIsNotNone(provenance["static_mapping_sha256"])
            self.assertIsNotNone(provenance["input_mapper_identity_sha256"])
            self.assertEqual("PRECOMPUTED_TSV_WITH_EXPLICIT_AUTHORITY_SIDECAR",
                             provenance["runtime_mapper_authority"]["mode"])
            self.assertIsNotNone(provenance["runtime_mapper_authority_sha256"])
            for name in (
                    "QWEIGHT_L2_SET_MAPPING.json", "QUOTA_STATIC_MAPPING.json",
                    "PER_LAYER_REUSE_DISTANCE_MATRIX.json",
                    "SET_CONFLICT_PRESSURE_ANALYSIS.json",
                    "D1_D2_D2_D3_STABILITY.json", "AGGREGATION_PROVENANCE.json"):
                self.assertEqual("PASS", json.loads((output / name).read_text())["status"], name)

    def test_rejects_unsorted_unique_lines(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.u64"
            write_u64(path, [2, 1])
            with self.assertRaisesRegex(ValueError, "sorted unique"):
                list(ap.u64s(path))

    def test_adapts_scanner_summary_schema_and_boundary_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            value = {"schema": "C16_E1_TRACE_PRESSURE_KERNEL_SUMMARY_V1",
              "kernel_id": 42, "decode_iteration": 2, "semantic_layer": 3,
              "semantic_identity": "up_proj", "dynamic_instructions": 100,
              "global_address_references": 50, "non_target_128b_line_references": 30,
              "target_refs_by_class": [0, 0, 0, 7] + [0] * 24,
              "expected_target_class": 4, "expected_target_observed": True,
              "first_expected_target_instruction_ordinal": 20,
              "last_expected_target_instruction_ordinal": 80,
              "target_unique_128b_lines": 6,
              "prefix": {"address_references": 9, "line_references": 8,
                         "unique_128b_lines": 4, "non_target_unique_128b_lines": 3},
              "suffix": {"address_references": 5, "line_references": 4,
                         "unique_128b_lines": 3, "non_target_unique_128b_lines": 2},
              "semantic_range_first_dynamic_kernel": 41,
              "semantic_range_last_dynamic_kernel": 42}
            path = root / "summary.json"; path.write_text(json.dumps(value), encoding="utf-8")
            kernel = ap.load_kernel(path)
            self.assertEqual({4: 7}, kernel.target_refs)
            self.assertEqual(19, ap.boundary(kernel, 4, "prefix").instructions)
            self.assertEqual(20, ap.boundary(kernel, 4, "suffix").instructions)
            self.assertEqual(root / "prefix_non_target_line_refs.u64",
                             ap.boundary(kernel, 4, "prefix").non_target_line_ref_pairs)
            self.assertEqual(root / "prefix_all_line_refs.u64",
                             ap.boundary(kernel, 4, "prefix").all_line_ref_pairs)

    def test_mapper_modes_fail_closed(self):
        command = f"{shlex.quote(sys.executable)} map --no-header"
        with tempfile.TemporaryDirectory() as temporary:
            table = Path(temporary) / "map.tsv"
            table.write_text("line_address\tsubpartition\tset\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "authority-json"):
                ap.Mapper(table, None, None)
        completed = mock.Mock(stdout="accepted_mapper_schema=WRONG\n")
        with mock.patch.object(ap.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(ValueError, "provenance mismatch"):
                ap.Mapper(None, command, None)
        accepted = mock.Mock(stdout="".join(
            f"{key}={value}\n" for key, value in ap.ACCEPTED_MAPPER.items()))
        with mock.patch.object(ap.subprocess, "run", return_value=accepted):
            mapper = ap.Mapper(None, command, None)
        self.assertEqual("FAIL_CLOSED_ACCEPTED_EXECUTABLE", mapper.authority["mode"])
        self.assertEqual(64, len(mapper.authority["executable_sha256"]))

    @unittest.skipUnless(sys.platform.startswith("linux"), "requires Linux fork")
    def test_workers_two_matches_workers_one_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            summaries, static, mapper, authority = self.fixture(root)
            outputs = [root / "workers-1", root / "workers-2"]
            for workers, output in enumerate(outputs, start=1):
                self.assertEqual(0, ap.main([
                    "--summary-root", str(summaries),
                    "--static-mapping", str(static),
                    "--line-mapping-tsv", str(mapper),
                    "--mapper-authority-json", str(authority),
                    "--workers", str(workers),
                    "--output-dir", str(output)]))
            names = [
                "QWEIGHT_L2_SET_MAPPING.json", "QUOTA_STATIC_MAPPING.json",
                "PER_LAYER_REUSE_DISTANCE_MATRIX.json",
                "PER_LAYER_REUSE_DISTANCE_MATRIX.tsv",
                "SET_CONFLICT_PRESSURE_ANALYSIS.json",
                "D1_D2_D2_D3_STABILITY.json", "AGGREGATION_PROVENANCE.json",
            ]
            for name in names:
                self.assertEqual((outputs[0] / name).read_bytes(),
                                 (outputs[1] / name).read_bytes(), name)


if __name__ == "__main__":
    unittest.main()
