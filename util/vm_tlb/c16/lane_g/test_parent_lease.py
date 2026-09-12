#!/usr/bin/env python3
"""Focused no-GPU tests for the C16 profiler parent-lease contract."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import multiprocessing
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from c16_native_common import ContractError  # noqa: E402
from execution_budget import BudgetLease, initialize_ledger, mark_existing_entry_diagnostic  # noqa: E402
from runtime_native_runner import wrapper_owned_budget  # noqa: E402


IDENTITY = {
    "model_id": "test-model", "model_revision": "a" * 40, "tokenizer_revision": "a" * 40,
    "deployment_id": "test-deployment", "implementation_key": "TEST", "dtype": "float16",
    "quantization": "NONE", "scenario_id": "S0", "input_hash": "b" * 64,
    "run_id": "123e4567-e89b-12d3-a456-426614174000", "code_commit": "c" * 40,
}


def hold_lock(path_text: str, ready: multiprocessing.Event, release: multiprocessing.Event) -> None:
    path = Path(path_text)
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        ready.set()
        release.wait(10)
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


class ParentLeaseTests(unittest.TestCase):
    def test_wrapper_mode_requires_receipt_token_and_live_foreign_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = root / "ledger.json"
            receipt = root / "parent.json"
            token = "unit-test-parent-token"
            parent = {
                "schema_version": "C16_G_PARENT_LEASE_V1",
                "state": "ACTIVE_IMMUTABLE_START_RECEIPT",
                "parent_lease_id": "123e4567-e89b-12d3-a456-426614174001",
                "lease_token_sha256": hashlib.sha256(token.encode("utf-8")).hexdigest(),
                "ledger_path": str(ledger),
                "max_elapsed_seconds": 120.0,
                "valid_until_unix": time.time() + 60,
                "identity": IDENTITY,
                "operation_kind": "NSYS",
                "wrapper_pid": 1,
            }
            receipt.write_text(json.dumps(parent), encoding="utf-8")
            args = argparse.Namespace(budget_ledger=ledger, parent_lease_receipt=receipt)
            previous = {key: os.environ.get(key) for key in ("C16_G_PARENT_LEASE_RECEIPT", "C16_G_PARENT_LEASE_TOKEN")}
            os.environ["C16_G_PARENT_LEASE_RECEIPT"] = str(receipt)
            os.environ["C16_G_PARENT_LEASE_TOKEN"] = token
            try:
                with self.assertRaises(ContractError):
                    wrapper_owned_budget(args, IDENTITY)
                ready, release = multiprocessing.Event(), multiprocessing.Event()
                process = multiprocessing.Process(target=hold_lock, args=(str(ledger.with_name("ledger.json.lock")), ready, release))
                process.start()
                self.assertTrue(ready.wait(5))
                budget, observed = wrapper_owned_budget(args, IDENTITY)
                self.assertEqual(budget.max_elapsed_seconds, 120.0)
                self.assertEqual(observed["parent_lease_id"], parent["parent_lease_id"])
            finally:
                if "release" in locals():
                    release.set()
                if "process" in locals():
                    process.join(5)
                for key, value in previous.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

    def test_diagnostic_annotation_preserves_budget_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / "ledger.json"
            initialize_ledger(ledger, instance_start_unix=time.time(), start_source="UNIT_TEST", instance_receipt_path=Path("unit-receipt.json"))
            with BudgetLease(ledger, IDENTITY, "NSYS", capture=False) as budget:
                budget.finish(elapsed_seconds=1.25, raw_bytes=0, terminal_status="FAILED_EMPTY_PROFILE", evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC", diagnostic_reason="UNIT_TEST")
            entry = mark_existing_entry_diagnostic(ledger, run_id=IDENTITY["run_id"], reason="REANNOTATED_UNIT_TEST")
            self.assertEqual(entry["elapsed_seconds"], 1.25)
            self.assertEqual(entry["raw_bytes"], 0)
            self.assertEqual(entry["evidence_classification"], "NON_SCIENTIFIC_DIAGNOSTIC")
            self.assertEqual(entry["diagnostic_reason"], "REANNOTATED_UNIT_TEST")


if __name__ == "__main__":
    unittest.main()
