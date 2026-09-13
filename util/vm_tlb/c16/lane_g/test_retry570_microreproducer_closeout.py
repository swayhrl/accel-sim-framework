#!/usr/bin/env python3
"""CPU-only validation of Retry570 microreproducer closeout publication."""
from __future__ import annotations

import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from execution_budget import BudgetLease, initialize_ledger  # noqa: E402
from retry570_microreproducer_closeout import (  # noqa: E402
    MICRO_DEPLOYMENT, P0_DEPLOYMENT, STATUS, validate, write,
)


class MicroreproducerCloseoutTests(unittest.TestCase):
    def test_write_and_validate_requires_exact_window_accounting(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw = root / "raw"
            raw.mkdir()
            (raw / "stdout.log").write_text("bounded diagnostic", encoding="utf-8")
            ledger = root / "ledger.json"
            initialize_ledger(ledger, instance_start_unix=time.time(), start_source="UNIT_TEST", instance_receipt_path=Path("unit.json"))
            for deployment in (P0_DEPLOYMENT, MICRO_DEPLOYMENT):
                for index in range(6):
                    identity = {"deployment_id": deployment, "run_id": f"{deployment}-{index}"}
                    with BudgetLease(ledger, identity, "NVBIT", capture=True) as lease:
                        lease.finish(elapsed_seconds=0.1, raw_bytes=0, terminal_status="COMPLETE", evidence_classification="NON_SCIENTIFIC_DIAGNOSTIC", diagnostic_reason="UNIT_TEST")
            directory = root / "publish"
            write(directory, raw, ledger, "a" * 40)
            result = validate(directory)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(json.loads((directory / "PUBLISH_MANIFEST.json").read_text()) ["status"], STATUS)


if __name__ == "__main__":
    unittest.main()
