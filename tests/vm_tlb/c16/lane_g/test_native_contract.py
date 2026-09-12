#!/usr/bin/env python3
"""No-GPU tests for the C16 Lane G bootstrap, runner, wrappers, and package."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
LANE = ROOT / "util/vm_tlb/c16/lane_g"
sys.path.insert(0, str(LANE))

import c16_native_common as COMMON
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

    def test_transfer_verifier_exposes_unclosed_a_package(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "pack"
            PACKAGE.prepare(out, None)
            rows = TRANSFER.read_rows(out / "EXPECTED_HASHES.tsv")
            self.assertIn("A_MODEL_ASSET_MANIFEST", TRANSFER.preconditions(rows))
            with self.assertRaises(COMMON.ContractError):
                TRANSFER.verify(rows, ROOT)

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

    def test_upstream_consumer_cli_is_import_complete(self):
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
