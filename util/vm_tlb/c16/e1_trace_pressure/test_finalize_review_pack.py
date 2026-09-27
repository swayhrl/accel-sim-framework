#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "finalize_review_pack.py"
CORE = "a2322069b9701597db7019080b5b54d29518e3a2"
CONFIG = "de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8"
SIDECAR = "6c60839714d136b9f6f596218588e658e245e0b7cc6f8e8550cce8d683ce13c6"


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def fixture(root: Path, *, missing_status: bool = False,
            bad_transition_count: bool = False) -> tuple[Path, Path]:
    analysis = root / "analysis"
    summary_root = analysis / "TRACE_REFERENCE_SUMMARY"
    results = analysis / "results"
    artifacts = analysis / "artifacts"
    mapper = {"mapper_cli": "/accepted/mapper", "mapper_cli_sha256": "a" * 64,
              "provenance": {"accepted_core_sha": CORE,
                             "accepted_config_sha256": CONFIG}}
    summary = {
        "schema": "C16_E1_TRACE_REFERENCE_SUMMARY_INDEX_V1", "status": "PASS",
        "claim_boundary": "TRACE_ADDRESS_REFERENCE_AND_128B_LINE_REFERENCE_PROXY_ONLY_NOT_ACTUAL_L2_TRAFFIC",
        "kernel_count": 2, "first_kernel_id": 10, "last_kernel_id": 11,
        "kernel_summaries": ["kernels/10/summary.json", "kernels/11/summary.json"],
        "totals": {"dynamic_instructions": 30, "cta_count": 3,
                   "global_address_references": 40},
        "qualified_full_sequence_closure": {"status": "PASS", "kernel_count": 2,
                                             "dynamic_instructions": 30, "cta_count": 3},
        "sequence_sha256": "b" * 64, "sidecar_sha256": SIDECAR,
        "scanner_sha256": "c" * 64,
        "trace_index_validation": {"status": "PASS", "sha256": "d" * 64},
        "mapper": {"status": "MAPPED_ACCEPTED_CORE", "identity": mapper},
    }
    dump(summary_root / "TRACE_REFERENCE_SUMMARY.json", summary)
    (summary_root / "TRACE_REFERENCE_SUMMARY.tsv").write_text(
        "kernel_id\tdynamic_instructions\n10\t10\n11\t20\n", encoding="utf-8")
    dump(summary_root / "kernels/10/summary.json", {"status": "PASS"})
    dump(summary_root / "kernels/11/summary.json", {"status": "PASS"})

    static = {"schema": "C16_E1_QWEIGHT_L2_SET_MAPPING_MAPPER_V1", "status": "PASS",
              "mapper": mapper, "sidecar_sha256": SIDECAR, "region_count": 2}
    dump(artifacts / "QWEIGHT_L2_SET_MAPPING.mapper.json", static)
    regions = []
    for layer in range(2):
        regions.append({"layer_index": layer, "target_class": layer + 1,
                        "begin": 0x1000 + layer * 0x1000,
                        "end_exclusive": 0x1080 + layer * 0x1000,
                        "bytes": 128, "line_count": 1,
                        "subpartition_line_counts": [1] + [0] * 15,
                        "set_line_counts": [{"subpartition": 0, "set": layer,
                                             "line_count": 1}],
                        "set_distribution": {"count": 32768, "min": 0,
                                             "median": 0, "max": 1}})
    status = {} if missing_status else {"status": "PASS"}
    qweight = {
        "schema": "C16_E1_QWEIGHT_L2_SET_MAPPING_V1", **status,
        "claim_boundary": "STATIC_ACCEPTED_MAPPER_OUTPUT",
        "geometry": {"associativity": 16, "l2_bytes": 64 << 20,
                     "line_size_bytes": 128, "sets_per_subpartition": 2048,
                     "subpartition_count": 16},
        "region_count": 2, "total_target_lines": 2, "regions": regions,
        "aggregate_target_set_population": {"count": 32768, "min": 0,
                                            "median": 0, "max": 1},
        "region_pair_set_overlap": [{"left_layer": 0, "right_layer": 1,
                                    "set_intersection": 0, "set_jaccard": 0.0}],
        "input_provenance": {"mapper": mapper, "sidecar_sha256": SIDECAR},
    }
    dump(results / "QWEIGHT_L2_SET_MAPPING.json", qweight)
    keys = [(layer, transition) for layer in range(2)
            for transition in ("D1_D2", "D2_D3")]
    if bad_transition_count:
        keys.pop()
    reuse = {"schema": "C16_E1_PER_LAYER_REUSE_DISTANCE_MATRIX_V1", **status,
             "claim_boundary": "128B_LINE_REFERENCE_PROXY",
             "rows": [{"layer_index": layer, "transition": transition}
                      for layer, transition in keys]}
    dump(results / "PER_LAYER_REUSE_DISTANCE_MATRIX.json", reuse)
    with (results / "PER_LAYER_REUSE_DISTANCE_MATRIX.tsv").open(
            "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("layer_index", "transition"),
                                delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(reuse["rows"])
    pressure = {"schema": "C16_E1_SET_CONFLICT_PRESSURE_ANALYSIS_V1", **status,
                "claim_boundary": "SET_CONFLICT_REFERENCE_PRESSURE_PROXY",
                "actual_l2_hit_miss_or_eviction_claimed": False,
                "rows": [{"layer_index": layer, "transition": transition}
                         for layer, transition in keys]}
    dump(results / "SET_CONFLICT_PRESSURE_ANALYSIS.json", pressure)
    dump(results / "D1_D2_D2_D3_STABILITY.json",
         {"schema": "C16_E1_D1_D2_D2_D3_STABILITY_V1", **status,
          "claim_boundary": "SET_CONFLICT_REFERENCE_PRESSURE_PROXY",
          "layer_count": 2, "metrics": {}})
    budgets = [{"budget": name, "per_layer_static_admission": [{}, {}]}
               for name in ("B8", "B16", "B24", "BFULL")]
    dump(results / "QUOTA_STATIC_MAPPING.json",
         {"schema": "C16_E1_QUOTA_STATIC_MAPPING_V1", **status,
          "claim_boundary": "STATIC_QUOTA_AND_SET_PLACEMENT_INTERPRETATION",
          "performance_ranking_claimed": False, "budgets": budgets})
    authority = {"mode": "FAIL_CLOSED_ACCEPTED_EXECUTABLE",
                 "provenance": {"accepted_core_sha": CORE,
                                "accepted_config_sha256": CONFIG}}
    provenance = {
        "schema": "C16_E1_TRACE_PRESSURE_AGGREGATE_V1", **status,
        "kernel_count": 2, "kernel_range": [10, 11], "raw_trace_opened": False,
        "summary_index_sha256": digest(summary_root / "TRACE_REFERENCE_SUMMARY.json"),
        "static_mapping_sha256": digest(artifacts / "QWEIGHT_L2_SET_MAPPING.mapper.json"),
        "sidecar_sha256": SIDECAR,
        "runtime_mapper_authority": authority,
        "runtime_mapper_authority_sha256": canonical(authority),
        "input_mapper_identity_sha256": canonical(mapper),
    }
    dump(results / "AGGREGATION_PROVENANCE.json", provenance)
    pack = root / "review_pack"
    pack.mkdir()
    (pack / "README.md").write_text("scaffold\n", encoding="utf-8")
    return analysis, pack


def command(analysis: Path, pack: Path, *extra: str) -> list[str]:
    return ["python3", str(SCRIPT), "--analysis-root", str(analysis),
            "--review-pack", str(pack), "--expected-kernel-count", "2",
            "--expected-layer-count", "2", *extra]


class FinalizerTest(unittest.TestCase):
    def test_scaffold_guard_success_manifests_and_checksums(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            analysis, pack = fixture(Path(directory))
            denied = subprocess.run(command(analysis, pack), text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertNotEqual(denied.returncode, 0)
            self.assertIn("review pack exists", denied.stderr)
            subprocess.run(command(analysis, pack, "--allow-existing-scaffold"), check=True)
            self.assertFalse((pack / "QWEIGHT_L2_SET_MAPPING.json").exists())
            for name in ("QWEIGHT_L2_SET_MAPPING_MANIFEST.json",
                         "TRACE_REFERENCE_SUMMARY_MANIFEST.json",
                         "VALIDATION_SUMMARY.json", "RESULT_SHA256SUMS"):
                self.assertTrue((pack / name).is_file(), name)
            validation = json.loads((pack / "VALIDATION_SUMMARY.json").read_text())
            self.assertEqual(validation["status"], "PASS")
            qmanifest = json.loads((pack / "QWEIGHT_L2_SET_MAPPING_MANIFEST.json").read_text())
            self.assertEqual(qmanifest["durable_artifact"]["sha256"],
                             digest(analysis / "results/QWEIGHT_L2_SET_MAPPING.json"))
            for raw in (pack / "RESULT_SHA256SUMS").read_text().splitlines():
                expected, name = raw.split("  ", 1)
                self.assertEqual(expected, digest(pack / name))
            repeated = subprocess.run(
                command(analysis, pack, "--allow-existing-scaffold"), text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertNotEqual(repeated.returncode, 0)
            self.assertIn("refusing to overwrite", repeated.stderr)

    def test_missing_derived_status_requires_explicit_flag(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            analysis, pack = fixture(Path(directory), missing_status=True)
            denied = subprocess.run(
                command(analysis, pack, "--allow-existing-scaffold"), text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertNotEqual(denied.returncode, 0)
            self.assertIn("missing status", denied.stderr)
            subprocess.run(command(analysis, pack, "--allow-existing-scaffold",
                                   "--allow-missing-derived-status"), check=True)
            validation = json.loads((pack / "VALIDATION_SUMMARY.json").read_text())
            self.assertTrue(validation["missing_derived_status_explicitly_allowed"])
            self.assertFalse(any(validation["derived_source_status_present"].values()))

    def test_transition_matrix_drift_fails_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            analysis, pack = fixture(Path(directory), bad_transition_count=True)
            result = subprocess.run(
                command(analysis, pack, "--allow-existing-scaffold"), text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("transition matrix drift", result.stderr)
            self.assertEqual(sorted(path.name for path in pack.iterdir()), ["README.md"])


if __name__ == "__main__":
    unittest.main()
