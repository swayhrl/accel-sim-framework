#!/usr/bin/env python3
"""No-GPU tests for the C16 Lane G bootstrap, runner, wrappers, and package."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
LANE = ROOT / "util/vm_tlb/c16/lane_g"
sys.path.insert(0, str(LANE))

import c16_native_common as COMMON
import execution_budget as BUDGET
import identity_guard as GUARD
import model_adapters as ADAPTERS
import consume_upstreams as UPSTREAMS
import native_catalog as CATALOG
import offline_dry_run as DRY
import prepare_gpu_package as PACKAGE
import profiler_wrapper as PROFILER
import run_model as RUNNER
import run_schema as SCHEMA
import scenario_driver as SCENARIO
import transfer_verify as TRANSFER
import wheelhouse_verify as WHEELS
import wheelhouse_manifest as WHEEL_MANIFEST


class NativeContractTest(unittest.TestCase):
    def test_wave1_adapter_contracts_do_not_silently_substitute_awq(self):
        self.assertEqual(ADAPTERS.resolve_adapter("qwen25_05b", "float16", "NONE").model_loader, "TRANSFORMERS_CAUSAL_LM")
        with self.assertRaises(COMMON.ContractError):
            ADAPTERS.resolve_adapter("qwen25_7b_awq", "bfloat16", "AWQ")
        with self.assertRaises(COMMON.ContractError):
            ADAPTERS.resolve_adapter("qwen25_7b_awq", "float16", "NONE")

    def test_mock_receipt_is_explicitly_non_scientific(self):
        args = type("Args", (), {
            "model_id": "fixture/mock-model", "model_revision": "fixture-r", "tokenizer_revision": "fixture-t",
            "deployment_id": "fixture-deployment", "implementation_key": "fixture-implementation", "dtype": "float16",
            "quantization": "NONE", "scenario_id": "S0", "input_hash": "0" * 64, "run_id": "fixture-run",
        })()
        receipt = RUNNER.mock_receipt(args)
        SCHEMA.validate_receipt(receipt, require_native=False)
        self.assertFalse(receipt["scientific_eligible"])
        self.assertEqual(receipt["execution_mode"], "MOCK")
        with self.assertRaises(COMMON.ContractError):
            SCHEMA.validate_receipt(receipt, require_native=True)

    def test_second_pass_target_identity_rejects_naked_ordinal_equivalence(self):
        expected = DRY.target()
        observed = dict(expected)
        observed["launch_ordinal"] = 99
        receipt = GUARD.validate_target_pair(expected, observed)
        self.assertTrue(receipt["identity_verified"])
        observed["grid"] = "2,1,1"
        with self.assertRaises(COMMON.ContractError):
            GUARD.validate_target_pair(expected, observed)

    def test_ncu_full_metric_set_is_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "metrics.txt"
            path.write_text("--set full\n", encoding="utf-8")
            with self.assertRaises(COMMON.ContractError):
                PROFILER.metric_names(path)

    def test_scenario_driver_requires_frozen_canary_and_disabled_dynamic_features(self):
        fixture = SCENARIO.fixture()
        self.assertTrue(SCENARIO.validate_scenario(fixture, canary=True)["runtime_mutation_forbidden"])
        changed = dict(fixture)
        changed["continuous_batching"] = True
        with self.assertRaises(COMMON.ContractError):
            SCENARIO.validate_scenario(changed, canary=True)

    def test_wheelhouse_requires_closed_hash_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "WHEELHOUSE_MANIFEST.tsv"
            manifest.write_text("wheel_filename\tpackage\tversion\tsha256\tstatus\n", encoding="utf-8")
            with self.assertRaises(COMMON.ContractError):
                WHEELS.validate(root, manifest)

    def test_wheel_manifest_records_metadata_size_source_and_compatibility_tag(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            wheel = root / "demo_pkg-1.2.3-py3-none-any.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("demo_pkg-1.2.3.dist-info/METADATA", "Metadata-Version: 2.1\nName: demo-pkg\nVersion: 1.2.3\n")
                archive.writestr("demo_pkg-1.2.3.dist-info/WHEEL", "Wheel-Version: 1.0\nTag: py3-none-any\n")
            requirements = root / "requirements.lock"
            requirements.write_text("demo-pkg==1.2.3\n", encoding="utf-8")
            manifest = root / "WHEELHOUSE_MANIFEST.tsv"
            rows = WHEEL_MANIFEST.rows_for(root, requirements)
            WHEEL_MANIFEST.write_manifest(manifest, rows)
            self.assertEqual(tuple(rows[0]), WHEEL_MANIFEST.FIELDS)
            self.assertEqual(rows[0]["size_bytes"], str(wheel.stat().st_size))
            self.assertEqual(rows[0]["source"], WHEEL_MANIFEST.PYPI_SOURCE)
            self.assertEqual(rows[0]["compatibility_tag"], "py3-none-any")
            self.assertEqual(WHEELS.validate(root, manifest, requirements), 1)
            self.assertFalse(WHEEL_MANIFEST.target_compatible("cp310-cp310-win_amd64"))

    def test_execution_budget_serializes_and_bounds_first_wave_capture_windows(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / "C16_EXECUTION_BUDGET.json"
            identity = DRY.target()["identity"]
            with self.assertRaises(COMMON.ContractError):
                with BUDGET.BudgetLease(ledger, identity, "NVBIT", capture=True):
                    pass
            BUDGET.initialize_ledger(
                ledger,
                instance_start_unix=time.time(),
                start_source="UNIT_TEST_OBSERVED_START",
                instance_receipt_path=Path("fixture-instance-receipt.json"),
            )
            for _ in range(BUDGET.MAX_NVBIT_WINDOWS_PER_DEPLOYMENT):
                with BUDGET.BudgetLease(ledger, identity, "NVBIT", capture=True) as lease:
                    self.assertEqual(lease.max_raw_bytes, BUDGET.MAX_NVBIT_WINDOW_BYTES)
                    self.assertEqual(lease.max_elapsed_seconds, BUDGET.MAX_NVBIT_WINDOW_SECONDS)
                    lease.finish(elapsed_seconds=0.01, raw_bytes=1, terminal_status="COMPLETE")
            with self.assertRaises(COMMON.ContractError):
                with BUDGET.BudgetLease(ledger, identity, "NVBIT", capture=True):
                    pass
            ledger_payload = json.loads(ledger.read_text(encoding="utf-8"))
            self.assertEqual(len(ledger_payload["entries"]), BUDGET.MAX_NVBIT_WINDOWS_PER_DEPLOYMENT)
            self.assertEqual(sum(entry["raw_bytes"] for entry in ledger_payload["entries"]), BUDGET.MAX_NVBIT_WINDOWS_PER_DEPLOYMENT)
            self.assertEqual(ledger_payload["instance"]["start_source"], "UNIT_TEST_OBSERVED_START")
            self.assertEqual(ledger_payload["limits"]["gpu_instance_wall_seconds"], BUDGET.MAX_GPU_INSTANCE_WALL_SECONDS)

    def test_native_execute_requires_budget_ledger_before_any_cuda_import(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tokens = root / "tokens.json"
            tokens.write_text("[1]", encoding="utf-8")
            completed = subprocess.run([
                sys.executable, str(LANE / "run_model.py"), "--mode", "canary", "--execute-native",
                "--receipt", str(root / "receipt.json"), "--model-path", str(root),
                "--input-token-ids", str(tokens), "--attention-backend", "TEST_BACKEND",
            ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("--budget-ledger", completed.stderr)

    def test_profiler_execute_requires_budget_ledger_before_tool_lookup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            completed = subprocess.run([
                sys.executable, str(LANE / "nsys_wrapper.py"), "--receipt", str(root / "receipt.json"),
                "--target-json", str(root / "target.json"), "--output", str(root / "out"), "--execute",
                "--", sys.executable, "-c", "raise SystemExit(0)",
            ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("--budget-ledger", completed.stderr)

    def test_autodl_resource_execute_requires_observed_start_before_gpu_query(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            completed = subprocess.run([
                sys.executable, str(LANE / "autodl_instance_receipt.py"), "--receipt", str(root / "receipt.json"),
                "--work-root", str(root), "--execute", "--exclusive-confirmation", "PROVIDER_CONFIRMED_EXCLUSIVE",
            ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("--budget-ledger and observed --instance-start-unix", completed.stderr)

    def test_transfer_verifier_exposes_unclosed_a_package(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "pack"
            PACKAGE.prepare(out, None)
            rows = TRANSFER.read_rows(out / "EXPECTED_HASHES.tsv")
            self.assertIn("G_LOCAL_WHEELHOUSE_MANIFEST", {row["artifact_id"] for row in rows})
            self.assertIn("A_MODEL_ASSET_MANIFEST", TRANSFER.preconditions(rows))
            with self.assertRaises(COMMON.ContractError):
                TRANSFER.verify(rows, ROOT)

    def test_publication_scan_rejects_duplicate_missing_size_and_hash_mismatches(self):
        import hashlib
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            payload = out / "payload.txt"
            payload.write_text("payload", encoding="utf-8")
            digest = hashlib.sha256(payload.read_bytes()).hexdigest()
            base = {"files": [{"path": "payload.txt", "size_bytes": payload.stat().st_size, "sha256": digest}]}
            (out / "PUBLISH_MANIFEST.json").write_text(json.dumps(base), encoding="utf-8")
            self.assertEqual(PACKAGE.scan_published_payloads(out)[0]["status"], "PASS")
            for changed in (
                {"files": [base["files"][0], dict(base["files"][0])]},
                {"files": [{"path": "missing.txt", "size_bytes": 1, "sha256": "0" * 64}]},
                {"files": [{"path": "payload.txt", "size_bytes": 999, "sha256": digest}]},
                {"files": [{"path": "payload.txt", "size_bytes": payload.stat().st_size, "sha256": "0" * 64}]},
            ):
                (out / "PUBLISH_MANIFEST.json").write_text(json.dumps(changed), encoding="utf-8")
                with self.assertRaises(COMMON.ContractError):
                    PACKAGE.scan_published_payloads(out)

    def test_native_catalog_rejects_non_wave1_declaration_before_publish(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            wave1 = root / "WAVE1_DEPLOYMENTS.tsv"
            CATALOG.write_tsv(wave1, CATALOG.WAVE1_FIELDS, [{
                "deployment_id": "only-one", "model_id": "fixture", "deployment_variant": "fixture",
                "wave": "W1", "catalog_status": "GAP", "gap_reason": "fixture",
            }])
            with self.assertRaises(COMMON.ContractError):
                CATALOG.validate(root, wave1)

    def test_fixed_manifest_validator_rejects_payload_tampering(self):
        payload = b"fixed payload"
        manifest = {"files": [{"path": "one.txt", "sha256": __import__("hashlib").sha256(payload).hexdigest(), "size_bytes": len(payload)}]}
        self.assertEqual(UPSTREAMS.verify_manifest_payload(manifest, "base", lambda path: payload), 1)
        with self.assertRaises(COMMON.ContractError):
            UPSTREAMS.verify_manifest_payload(manifest, "base", lambda path: b"tampered")

    def test_h_dedicated_manifest_validator_rejects_dynamic_or_hash_tampering(self):
        code = b"hash-bound H code"
        receipt = b"hash-bound H test receipt"
        digest = __import__("hashlib").sha256
        manifest = {
            "schema_version": "c16-h-offline-publish-manifest-v1",
            "status": "C16_H_OFFLINE_PREP_READY_FOR_FINAL_REVIEW",
            "planning_sha": COMMON.PLANNING_SHA,
            "dynamic_scientific_rows": {"present": False},
            "implementation_commit": "a" * 40,
            "admission_hardening_commit": "b" * 40,
            "code_sha256": {"util/h.py": digest(code).hexdigest()},
            "test_receipt": {"path": "TEST_RECEIPT.json", "sha256": digest(receipt).hexdigest()},
        }
        def read_blob(path):
            return code if path == "util/h.py" else receipt
        provenance, count = UPSTREAMS.verify_h_manifest_payload(manifest, read_blob)
        self.assertIn("implementation=" + "a" * 40, provenance)
        self.assertEqual(count, 2)
        manifest["dynamic_scientific_rows"] = {"present": True}
        with self.assertRaises(COMMON.ContractError):
            UPSTREAMS.verify_h_manifest_payload(manifest, read_blob)

    def test_upstream_consumer_cli_is_import_complete(self):
        self.assertEqual(UPSTREAMS.A_COMMIT, "b458225e")
        self.assertEqual(UPSTREAMS.C_COMMIT, "29e669ec")
        self.assertEqual(UPSTREAMS.H_COMMIT, "932c6fa4")
        artifact = "a" * 40
        producer = "b" * 40
        receipt = (
            f"| C16 A integration artifact checkpoint | `{artifact}` |\n"
            f"| C16 A integration producer checkpoint | `{producer}` |\n"
        )
        self.assertEqual(
            UPSTREAMS.parse_a_integration_provenance(receipt),
            f"integration_artifact={artifact};integration_producer={producer}",
        )
        completed = subprocess.run([sys.executable, str(LANE / "consume_upstreams.py"), "--help"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_complete_offline_suite_builds_only_non_scientific_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "pack"
            DRY.run(out)
            PACKAGE.validate(out)
            receipt = json.loads((out / "OFFLINE_DRY_RUN_RECEIPTS.json").read_text(encoding="utf-8"))
            self.assertFalse(receipt["scientific_eligible"])
            self.assertEqual(receipt["mode"], "OFFLINE_DRY_RUN")
            self.assertTrue(all(row["status"] == "PASS" for row in PACKAGE.rows(out / "OFFLINE_DRY_RUN.tsv")))


if __name__ == "__main__":
    unittest.main()
