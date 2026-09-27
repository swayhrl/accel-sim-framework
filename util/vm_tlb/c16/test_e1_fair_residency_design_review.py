#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
BUILDER = HERE / "e1_fair_residency_design_review.py"
FRAMEWORK = Path("/root/workspace/accel-sim-framework-c16-e1-target-class-fair-residency-design-review-174new-v1")
CORE = Path("/root/workspace/gpgpu-sim-c16-trace-address-namespace-integration-v1")
LANE4 = Path("/root/workspace/gpgpu-sim-c16-b16-reuse-canary-telemetry-v1")


class ReviewTest(unittest.TestCase):
    def build(self, root: Path) -> Path:
        output = root / "pack"
        subprocess.run([
            "python3", str(BUILDER),
            "--framework-repo", str(FRAMEWORK),
            "--core-repo", str(CORE),
            "--lane4-core-repo", str(LANE4),
            "--output-dir", str(output),
        ], check=True)
        return output

    def test_frozen_semantics_and_recommendation(self):
        with tempfile.TemporaryDirectory() as directory:
            pack = self.build(Path(directory))
            semantics = json.loads((pack / "NATIVE_VS_M1_RESIDENCY_SEMANTICS.json").read_text())
            rows = {row["budget"]: row for row in semantics["budget_comparison"]}
            self.assertEqual(rows["BFULL"]["native_actual_setaside_bytes"], 37_748_736)
            self.assertEqual(rows["BFULL"]["m1_one_class_max_protected_lines_target_only"], 265_216)
            self.assertAlmostEqual(rows["B16"]["native_hit_ratio"], 0.01765030336458908)
            self.assertFalse(semantics["current_m1"]["target_class_use_in_victim_choice"])
            self.assertTrue(semantics["current_m1"]["source"]
                            ["lane4_cache_policy_callsite_semantics_match"])
            recommendation = json.loads((pack / "RECOMMENDATION.json").read_text())
            self.assertEqual(recommendation["final_label"], "TARGET_CLASS_FAIRNESS_MECHANISM_JUSTIFIED")
            self.assertEqual(recommendation["recommended_next_mechanism"],
                             "M1F_GLOBAL_ELASTIC_FRACTIONAL_ADMISSION")
            self.assertFalse(recommendation["implementation_authorized"])

    def test_churn_and_lane4_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            pack = self.build(Path(directory))
            churn = json.loads((pack / "TARGET_TARGET_CHURN_ANALYSIS.json").read_text())
            rows = {row["budget"]: row for row in churn["budgets"]}
            self.assertAlmostEqual(rows["B8"]["conditional_L1_through_L27_pool_turns"], 109.265625)
            self.assertEqual(rows["BFULL"]["conditional_L1_through_L27_pool_turns"], 27)
            self.assertEqual(churn["ideal_target_only_all_miss_proof"]
                             ["latest_layer_with_zero_original_L0_protected_lines"], 3)
            contract = json.loads((pack / "LANE4_INTERPRETATION_CONTRACT.json").read_text())
            self.assertEqual(len(contract["branches"]), 4)
            self.assertFalse(contract["partial_data_used"])
            self.assertEqual(contract["status"], "PREREGISTERED_BEFORE_LANE4_COMPLETION")
            sources = json.loads((pack / "RELATED_WORK_COLLISION_MATRIX.json").read_text())
            self.assertFalse(sources["novelty_claim"])
            self.assertGreaterEqual(len(sources["sources"]), 6)
            self.assertEqual(len(sources["existing_repository_notes_reviewed"]), 2)

    def test_checksums_and_fresh_output(self):
        with tempfile.TemporaryDirectory() as directory:
            pack = self.build(Path(directory))
            subprocess.run(["sha256sum", "-c", "SHA256SUMS"], cwd=pack, check=True,
                           stdout=subprocess.PIPE, text=True)
            completed = subprocess.run([
                "python3", str(BUILDER),
                "--framework-repo", str(FRAMEWORK),
                "--core-repo", str(CORE),
                "--lane4-core-repo", str(LANE4),
                "--output-dir", str(pack),
            ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("fresh", completed.stderr)


if __name__ == "__main__":
    unittest.main()
