#!/usr/bin/env python3
import hashlib
import importlib.util
import json
from importlib.machinery import SourceFileLoader
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).with_name("finalize_e1_b16_reuse_canary.py")
SPEC = importlib.util.spec_from_loader(
    "finalize_e1_b16_reuse_canary",
    SourceFileLoader("finalize_e1_b16_reuse_canary", str(MODULE_PATH)),
)
FINALIZE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FINALIZE)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def response(r0, m1):
    return {
        "R0_cycles": r0,
        "M1_cycles": m1,
        "R0_minus_M1_cycles": r0 - m1,
        "response_fraction": (r0 - m1) / r0,
        "response_percent": 100.0 * (r0 - m1) / r0,
    }


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FinalizerTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.pack = root / "pack"
        self.run_root = root / "runs"
        self.pack.mkdir()
        self.run_root.mkdir()
        (self.pack / "configs").mkdir()
        sequence = self.pack / FINALIZE.SEQUENCE_FILE
        sequence.write_text("global_dynamic_order\texact_function\n2926\tkernel\n", encoding="utf-8")
        for condition, relative in FINALIZE.CONFIG_FILES.items():
            path = self.pack / relative
            path.write_text(f"# {condition}\n", encoding="utf-8")
        trace_config = self.pack / FINALIZE.TRACE_CONFIG_FILE
        trace_config.write_text("# trace config\n", encoding="utf-8")

        scope = {
            "schema": "C16_E1_B16_REUSE_WINDOW_SCOPE_V1", "status": "PASS",
            "total_kernel_count": 1565, "thread_blocks": 1259187,
            "D1_complete": True, "D2_prefix_complete": True,
            "selected_sequence_sha256": file_sha(sequence),
        }
        write_json(self.pack / "REUSE_WINDOW_SCOPE.json", scope)
        matrix_runs = {
            condition: {
                "condition": condition, "config": relative,
                "config_sha256": file_sha(self.pack / relative),
                "primary_performance_authority": condition != "M1_B16_DIAGNOSTIC",
                "diagnostic_only": condition == "M1_B16_DIAGNOSTIC",
            }
            for condition, relative in FINALIZE.CONFIG_FILES.items()
        }
        write_json(self.pack / "RUN_MATRIX.json", {
            "schema": "C16_E1_B16_REUSE_RUN_MATRIX_V1", "status": "PASS",
            "trace_scope_sha256": file_sha(self.pack / "REUSE_WINDOW_SCOPE.json"),
            "trace_config_sha256": file_sha(trace_config), "runs": matrix_runs,
        })
        write_json(self.pack / "HOST_SCALE_AND_TELEMETRY_QUALIFICATION.json", {
            "schema": "C16_E1_B16_REUSE_HOST_SCALE_AND_TELEMETRY_QUALIFICATION_V1",
            "status": "PASS",
        })
        write_json(self.pack / "BOUNDED_REPRODUCIBILITY_PREFIX_UID168.json", {
            "schema": "C16_E1_B16_BOUNDED_REPRODUCIBILITY_PREFIX_V1", "status": "PASS",
            "claim": FINALIZE.REPRODUCIBILITY_CLAIM, "bounded_prefix_last_uid": 168,
            "full_1565_kernel_repeat_claimed": False,
        })
        write_json(self.pack / "PRIMARY_DIAGNOSTIC_ADMISSION_GATE.json", {
            "schema": "C16_E1_B16_PRIMARY_DIAGNOSTIC_ADMISSION_GATE_V1", "status": "PASS",
            "kernel_count": 1565, "primary_terminal_PASS": True,
            "primary_launch_authority_PASS": True,
            "primary_full_window_kernel_identity_PASS": True,
            "primary_per_UID_instruction_CTA_identity_PASS": True,
            "primary_correctness_comparison_PASS": True,
        })
        write_json(self.pack / "M1_B16_DIAGNOSTIC_ADMISSION_STATUS.json", {
            "schema": "C16_E1_B16_DIAGNOSTIC_ADMISSION_STATUS_V1",
            "status": "ADMITTED_PRIMARY_GATES_PASS", "scientific_admission": "ADMITTED",
            "primary_terminal_PASS": True,
            "primary_workload_kernel_instruction_CTA_identity": True,
            "primary_correctness_comparison": True,
        })
        write_json(self.pack / "PREFLIGHT.json", {"status": "PASS"})
        identity = {
            "kernel_count": 1565,
            "kernel_sequence_sha256": "a" * 64,
            "instruction_count": 123,
            "CTA_count": 45,
        }
        checkpoints = {
            "after_D1_L0_up": {"uid": 60},
            "after_D1_complete": {"uid": 1505},
            "immediately_before_D2_L0_up": {
                "uid": 1563,
                "counters": {"sum": {
                    "target_protection_admission_denied": 0,
                    "normal_fallback_protected_victims": 0,
                }},
            },
            "after_D2_L0_up": {"uid": 1565},
        }
        raw_runs = {}
        receipt_runs = {}
        for condition in FINALIZE.CONDITIONS:
            run_dir = root / "raw" / condition
            run_dir.mkdir(parents=True)
            for member in FINALIZE.RAW_OUTPUT_MEMBERS:
                (run_dir / member).write_text(
                    "" if member == "simulator.stderr" else f"{condition}:{member}\n",
                    encoding="utf-8")
            verified = {member: file_sha(run_dir / member)
                        for member in FINALIZE.RAW_OUTPUT_MEMBERS}
            manifest = run_dir / "OUTPUT_SHA256SUMS"
            manifest.write_text("\n".join(
                f"{digest}  {member}" for member, digest in sorted(verified.items())) + "\n",
                encoding="utf-8")
            bounded = condition == "R0_BASELINE_REPEAT_BOUNDED"
            cycles = ({"C_prefix_UID168": 100} if bounded else
                      {"C_window": 1000 if condition == "R0_BASELINE" else 900,
                       "C_D2_prefix": 100 if condition == "R0_BASELINE" else 95,
                       "C_L0_up_D2": 10 if condition == "R0_BASELINE" else 9})
            raw_runs[condition] = {
                "condition": condition, "status": "PASS", "run_dir": str(run_dir),
                "receipt_sha256": file_sha(run_dir / "RUN_RECEIPT.json"),
                "output_manifest_sha256": file_sha(manifest),
                "stdout_sha256": file_sha(run_dir / "simulator.stdout"),
                "stderr_sha256": file_sha(run_dir / "simulator.stderr"),
                "stderr_bytes": 0, "verified_output_sha256": verified,
                "kernel_count": 168 if bounded else 1565,
                "kernel_sequence_sha256": "b" * 64 if bounded else "a" * 64,
                "instruction_count": 12 if bounded else 123,
                "CTA_count": 4 if bounded else 45, "cycles": cycles,
            }
            receipt_runs[condition] = {
                "run_dir": str(run_dir),
                "receipt_sha256": raw_runs[condition]["receipt_sha256"],
                "output_manifest_sha256": raw_runs[condition]["output_manifest_sha256"],
                "verified_output_sha256": verified,
            }
        documents = {
            "CORRECTNESS_COMPARISON.json": {
                "schema": "C16_E1_B16_REUSE_CORRECTNESS_V1", "status": "PASS",
                "R0_M1_equal": True, "primary_and_diagnostic_natural_termination": True,
                "full_expected_kernel_sequence_and_completion_coverage": True,
                "verified_simulator_stderr_empty": True,
                "runs": {name: dict(identity) for name in FINALIZE.CONDITIONS[:3]},
            },
            "B16_REUSE_WINDOW_PERFORMANCE.json": {
                "schema": "C16_E1_B16_REUSE_PERFORMANCE_V1", "status": "PASS",
                "primary_authority": ["R0_BASELINE", "M1_B16"],
                "diagnostic_excluded_from_primary_performance": True,
                "metrics": {
                    "C_window": response(1000, 900),
                    "C_D2_prefix": response(100, 95),
                    "C_L0_up_D2": response(10, 9),
                },
            },
            "REPRODUCIBILITY.json": {
                "schema": "C16_E1_B16_REUSE_REPRODUCIBILITY_V1", "status": "PASS",
                "reproducibility_claim": FINALIZE.REPRODUCIBILITY_CLAIM,
                "bounded_prefix_last_uid": 168, "full_window_repeat_claimed": False,
                "exact_cycle_instruction_CTA_kernel_reproduction": True,
                "M1_diagnostics_real_trace_neutral": True,
                "M1_diagnostics_per_UID_cycle_instruction_CTA_exact": True,
                "M1_diagnostics_kernel_identity_exact": True,
                "diagnostic_coverage": {
                    "UID_count": 1565, "instance_count_per_UID": 16,
                    "counter_row_count": 25040, "class_row_count": 25040,
                    "snapshot_begin_count": 1565, "snapshot_end_count": 1565,
                    "counter_schema_exact": True, "class_schema_exact": True,
                    "per_instance_class_sum_equals_occupancy_all_UIDs": True,
                    "per_instance_quota_lines": 8192,
                    "aggregate_quota_lines": 131072,
                    "occupancy_bounds_all_UIDs": True,
                },
            },
            "B16_MECHANISM_ACTIVATION.json": {
                "schema": "C16_E1_B16_MECHANISM_ACTIVATION_V1", "status": "PASS",
                "mechanism_activated": True, "target_accesses_nonzero": True,
                "protected_fills_nonzero": True, "checkpoints": checkpoints,
                "D1_L0_class1_occupancy_after_fill": 8,
                "D1_L0_class1_occupancy_retained_before_D2_reuse": 1,
                "case4_exact_zero_retention_subset": {
                    "satisfied": False,
                    "not_a_numeric_definition_of_qualitative_almost_or_large": True,
                    "constraint_events_are_global_cumulative_not_causal_attribution_for_class1": True,
                },
            },
            "RAW_OUTPUT_INDEX.json": {
                "schema": "C16_E1_B16_REUSE_RAW_OUTPUT_INDEX_V1", "status": "PASS",
                "runs": raw_runs,
            },
            "RUN_RECEIPTS.json": {
                "schema": "C16_E1_B16_REUSE_RUN_RECEIPTS_V1", "status": "PASS",
                "primary_and_diagnostic_natural_terminal": True,
                "bounded_repeat_scope": {
                    "claim": FINALIZE.REPRODUCIBILITY_CLAIM,
                    "intentional_exit_code": 143,
                    "terminal_exit_detected": False,
                    "full_window_repeat_claimed": False,
                },
                "runs": receipt_runs,
            },
            "FINAL_DECISION.json": {
                "schema": "C16_E1_B16_REUSE_FINAL_DECISION_V1", "status": "PASS",
                "stage_label": FINALIZE.STAGE_LABEL,
                "interpretation": "CASE_1_SIGNED_FIRST_MECHANISM_SIGNAL_POSITIVE",
                "mechanism_activated": True, "correctness_qualified": True,
                "reproducibility_qualified": True, "diagnostic_neutrality_qualified": True,
                "not_whole_model_or_system_speedup": True,
                "no_budget_matrix_or_promotion_decision": True,
                "claim_boundary": "FIRST_QUALIFIED_REAL_TRACE_B16_REUSE_WINDOW_CANARY_ONLY",
                "case4_exact_zero_retention_subset_satisfied": False,
                "case4_qualitative_threshold_not_invented": True,
                "case4_constraint_events_not_claimed_as_cause_of_class1_loss": True,
            },
            "DIAGNOSTIC_COUNTERS.json": checkpoints,
        }
        for name, value in documents.items():
            write_json(self.pack / name, value)
        write_json(self.run_root / "FOLLOWUP_RECEIPT.json", {
            "schema": FINALIZE.FOLLOWUP_SCHEMA, "status": "PASS",
            "diagnostic_exit_code": 0, "bounded_repeat_exit_code": 0,
            "analysis_exit_code": 0,
            "reproducibility_claim": FINALIZE.REPRODUCIBILITY_CLAIM,
        })

    def tearDown(self):
        self.temporary.cleanup()

    def test_finalize_and_stable_recursive_sha_manifest(self):
        summary = FINALIZE.finalize(self.pack, self.run_root, True)
        self.assertEqual(summary["status"], "PASS")
        self.assertIn(FINALIZE.STAGE_LABEL,
                      (self.pack / "README.md").read_text(encoding="utf-8"))
        source = self.run_root / "FOLLOWUP_RECEIPT.json"
        copied = self.pack / "FOLLOWUP_RECEIPT.json"
        self.assertEqual(copied.read_bytes(), source.read_bytes())
        first = (self.pack / "SHA256SUMS").read_bytes()
        FINALIZE.finalize(self.pack, self.run_root, True)
        self.assertEqual(first, (self.pack / "SHA256SUMS").read_bytes())
        lines = first.decode().splitlines()
        self.assertFalse(any(line.endswith("  SHA256SUMS") for line in lines))
        members = [line.split("  ", 1)[1] for line in lines]
        self.assertEqual(members, sorted(members))
        for line in lines:
            digest, member = line.split("  ", 1)
            self.assertEqual(digest, hashlib.sha256((self.pack / member).read_bytes()).hexdigest())

    def test_failed_followup_is_fail_closed_without_publication(self):
        receipt = self.run_root / "FOLLOWUP_RECEIPT.json"
        document = json.loads(receipt.read_text(encoding="utf-8"))
        document["analysis_exit_code"] = 1
        write_json(receipt, document)
        with self.assertRaises(FINALIZE.ContractError):
            FINALIZE.finalize(self.pack, self.run_root, True)
        self.assertFalse((self.pack / "README.md").exists())
        self.assertFalse((self.pack / "VALIDATION_SUMMARY.json").exists())
        self.assertFalse((self.pack / "FOLLOWUP_RECEIPT.json").exists())
        self.assertFalse((self.pack / "SHA256SUMS").exists())

    def test_metric_arithmetic_drift_is_rejected(self):
        path = self.pack / "B16_REUSE_WINDOW_PERFORMANCE.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["metrics"]["C_window"]["response_fraction"] = 0.11
        write_json(path, document)
        with self.assertRaisesRegex(FINALIZE.ContractError, "response fraction drift"):
            FINALIZE.finalize(self.pack, self.run_root, False)

    def test_symlink_in_pack_is_rejected_by_recursive_manifest(self):
        target = Path(self.temporary.name) / "outside"
        target.write_text("outside", encoding="utf-8")
        (self.pack / "escape").symlink_to(target)
        with self.assertRaisesRegex(FINALIZE.ContractError, "symlink is forbidden"):
            FINALIZE.finalize(self.pack, self.run_root, False)
        self.assertFalse((self.pack / "README.md").exists())

    def test_raw_receipt_cross_match_and_coverage_fail_closed(self):
        path = self.pack / "RAW_OUTPUT_INDEX.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["runs"]["M1_B16"]["receipt_sha256"] = "0" * 64
        write_json(path, document)
        with self.assertRaisesRegex(FINALIZE.ContractError, "raw/receipt authority mismatch"):
            FINALIZE.finalize(self.pack, self.run_root, False)
        self.assertFalse((self.pack / "README.md").exists())

    def test_exact_diagnostic_coverage_is_required(self):
        path = self.pack / "REPRODUCIBILITY.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["diagnostic_coverage"]["counter_row_count"] = 25039
        write_json(path, document)
        with self.assertRaisesRegex(FINALIZE.ContractError, "exact diagnostic coverage"):
            FINALIZE.finalize(self.pack, self.run_root, False)

    def test_interpretation_is_recomputed(self):
        path = self.pack / "FINAL_DECISION.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["interpretation"] = "CASE_3_RESIDENCY_ACTIVITY_WITHOUT_TARGET_LOCAL_TIMING_BENEFIT"
        write_json(path, document)
        with self.assertRaisesRegex(FINALIZE.ContractError, "interpretation recomputation"):
            FINALIZE.finalize(self.pack, self.run_root, False)

    def test_claim_boundary_drift_is_rejected(self):
        path = self.pack / "FINAL_DECISION.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["claim_boundary"] = "EXPANDED_CLAIM"
        write_json(path, document)
        with self.assertRaisesRegex(FINALIZE.ContractError, "claim boundary drift"):
            FINALIZE.finalize(self.pack, self.run_root, False)

    def test_external_test_summary_is_reported_truthfully(self):
        external = Path(self.temporary.name) / "external-tests.json"
        write_json(external, {
            "schema": "SYNTHETIC_TEST_RECEIPT_V1", "status": "PASS",
            "exit_code": 0, "tests_passed": 7, "tests_failed": 0,
        })
        summary = FINALIZE.finalize(self.pack, self.run_root, False, external)
        self.assertTrue(summary["validation"]["external_test_summary_supplied"])
        self.assertTrue(summary["validation"]["external_tests_claimed_PASS"])
        reported = summary["input_artifacts"]["EXTERNAL_TEST_SUMMARY"]["reported"]
        self.assertEqual(reported["tests_passed"], 7)

    def test_missing_required_config_fails_before_publication(self):
        (self.pack / FINALIZE.CONFIG_FILES["M1_B16"]).unlink()
        with self.assertRaisesRegex(FINALIZE.ContractError, "required publication input"):
            FINALIZE.finalize(self.pack, self.run_root, False)
        self.assertFalse((self.pack / "README.md").exists())

    def test_case4_is_recomputed_and_readme_preserves_caveat(self):
        activation_path = self.pack / "B16_MECHANISM_ACTIVATION.json"
        activation = json.loads(activation_path.read_text(encoding="utf-8"))
        activation["D1_L0_class1_occupancy_retained_before_D2_reuse"] = 0
        activation["checkpoints"]["immediately_before_D2_L0_up"]["counters"]["sum"][
            "target_protection_admission_denied"] = 1
        activation["case4_exact_zero_retention_subset"]["satisfied"] = True
        write_json(activation_path, activation)
        write_json(self.pack / "DIAGNOSTIC_COUNTERS.json", activation["checkpoints"])
        final_path = self.pack / "FINAL_DECISION.json"
        final = json.loads(final_path.read_text(encoding="utf-8"))
        final["interpretation"] = "CASE_4_EXACT_ZERO_RETENTION_WITH_OBSERVED_CONSTRAINT_EVENTS"
        final["case4_exact_zero_retention_subset_satisfied"] = True
        write_json(final_path, final)
        FINALIZE.finalize(self.pack, self.run_root, False)
        readme = (self.pack / "README.md").read_text(encoding="utf-8")
        self.assertIn("exact zero-retention subset", readme)
        self.assertIn("not a numeric definition", readme)
        self.assertIn("global and cumulative", readme)
        self.assertIn("not claimed to have caused class-1 loss", readme)


if __name__ == "__main__":
    unittest.main()
