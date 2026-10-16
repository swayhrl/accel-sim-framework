#!/usr/bin/python3
"""Synthetic intake checks only; no simulator workload or scientific result generation."""
import copy
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from plot_verified_results import COORD, COHORTS, FEATURES, GATES, IDEALS, validate_manifest


def manifest(workload="sad", mode="B16_BANKED", cycles=100):
    return {"run_id": workload + ":" + mode, "workload": workload, "mode": mode,
            "evidence_kind": "FUNCTIONAL_IMPLEMENTATION", "status": "COMPLETE_VALID",
            "core_source_commit": "1" * 40, "framework_source_commit": "2" * 40,
            "binary_sha256": "3" * 64, "config_sha256": "4" * 64,
            "trace_sha256": "5" * 64, "raw_log_sha256": "6" * 64,
            "epoch_range": {"kernel": 0, "begin": 0, "end": 1},
            "feature_vector": {k: mode == "U_WB16" and k == "unified_wb" for k in sorted(FEATURES)},
            "ideal_vector": {k: False for k in sorted(IDEALS)},
            "effective_config": {"payload_slots_per_slice": 1168, "banks": 4, "line_ops_per_bank_cycle": 1, "dram_mhz": 850},
            "cycles": cycles, "instructions": 1000, "validation": {k: True for k in GATES},
            "fixture_scope": "SYNTHETIC_TEST_ONLY_NOT_SCIENTIFIC_EVIDENCE"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


class IntakeTests(unittest.TestCase):
    def test_complete_identity_is_accepted(self):
        validate_manifest(manifest(), "FUNCTIONAL_IMPLEMENTATION")

    def reject(self, update):
        m = manifest()
        update(m)
        with self.assertRaises(ValueError):
            validate_manifest(m, "FUNCTIONAL_IMPLEMENTATION")

    def test_missing_binary_is_rejected(self):
        self.reject(lambda m: m.pop("binary_sha256"))

    def test_oracle_is_not_ordinary_implementation(self):
        self.reject(lambda m: m["feature_vector"].update(oracle_ro=True))

    def test_ideal_is_not_ordinary_implementation(self):
        self.reject(lambda m: m["ideal_vector"].update(I_WB=True))

    def test_shadow_cannot_be_relabelled(self):
        self.reject(lambda m: m.update(evidence_kind="SHADOW_OBSERVATION"))

    def test_incomplete_and_nonboolean_gates_are_rejected(self):
        self.reject(lambda m: m.update(status="RUNNING"))
        self.reject(lambda m: m["validation"].update(data_version_check=1))

    def test_coordination_is_not_runtime(self):
        self.reject(lambda m: m.update(framework_source_commit=COORD))

    def test_empty_vector_is_not_all_off_proof(self):
        self.reject(lambda m: m.update(ideal_vector={}))

    def test_git_bound_roundtrip_and_tamper(self):
        with tempfile.TemporaryDirectory(prefix="ep-l2-lane6-intake-test-") as tmp:
            root = Path(tmp)
            repo = root / "synthetic-repo"
            repo.mkdir()
            def git(*args):
                return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.STDOUT).decode().strip()
            git("init", "-q")
            rows, locations, hashes = [], {}, {}
            for i, w in enumerate(COHORTS["development"]):
                for mode in ("B16_BANKED", "U_WB16"):
                    # Deliberately include a slowdown; it must remain in the output.
                    m = manifest(w, mode, 125 if i == 0 and mode == "U_WB16" else 100)
                    f = root / (w + "_" + mode + ".json")
                    f.write_text(json.dumps(m, sort_keys=True))
                    locations[m["run_id"]], hashes[m["run_id"]] = str(f), sha(f.read_bytes())
                    rows.append({k: m[k] for k in ("run_id", "workload", "mode", "evidence_kind", "status", "cycles", "instructions")})
            data = root / "synthetic_results.csv"
            with data.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            (repo / "bundle.json").write_text(json.dumps({"results_csv_sha256": sha(data.read_bytes()), "run_manifest_sha256s": hashes}))
            (repo / "receipt.json").write_text(json.dumps({"lane_id": 5, "coordination_commit": COORD, "artifacts": ["bundle.json"]}))
            git("add", "bundle.json", "receipt.json")
            git("-c", "user.name=Lane6 Synthetic Test", "-c", "user.email=lane6-test@example.invalid", "commit", "-qm", "synthetic provenance fixture only")
            revision = git("rev-parse", "HEAD")
            a = {"schema": "EP_L2_LANE6_VERIFIED_RESULT_ADAPTER_V1", "coordination_commit": COORD,
                 "source_lane": 5, "evidence_kind": "FUNCTIONAL_IMPLEMENTATION", "publication_commit": revision,
                 "receipt_repository_path": "receipt.json", "receipt_sha256": sha((repo / "receipt.json").read_bytes()),
                 "bundle_repository_path": "bundle.json", "bundle_sha256": sha((repo / "bundle.json").read_bytes()),
                 "results_csv": str(data), "run_manifests": locations, "baseline_mode": "B16_BANKED", "candidate_mode": "U_WB16", "cohort": "development"}
            adapter = root / "adapter.json"
            adapter.write_text(json.dumps(a))
            cmd = [sys.executable, str(Path(__file__).with_name("plot_verified_results.py")), str(adapter), "--framework-repo", str(repo), "--output-dir", str(root / "synthetic_plot")]
            r = subprocess.run(cmd, text=True, capture_output=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            output = json.loads((root / "synthetic_plot/FIGURE_INPUT_MANIFEST.json").read_text())
            self.assertEqual(len(output["rows"]), 5)
            self.assertEqual(output["rows"][0]["speedup"], .8)
            self.assertLess(output["geomean_all_predeclared_workloads"], 1)
            # Scientific CSV changed without updating the published authority: reject.
            data.write_text(data.read_text() + "tamper\n")
            r = subprocess.run(cmd[:-1] + [str(root / "rejected_plot")], text=True, capture_output=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("Results CSV hash mismatch", r.stderr)
            self.assertFalse((root / "rejected_plot").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
