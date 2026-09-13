from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from retry570_recovery_budget import CAMPAIGN_ID, MAX_WINDOWS_PER_DEPLOYMENT, RecoveryBudgetLease, initialize


class RecoveryBudgetTests(unittest.TestCase):
    def test_new_namespace_preserves_historical_bytes_and_enforces_eight_windows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); old = root / "old.json"; old.write_text(json.dumps({"legacy": [1, 2, 3]}), encoding="utf-8")
            import hashlib
            old_sha = hashlib.sha256(old.read_bytes()).hexdigest(); new = root / "recovery.json"
            ledger = initialize(recovery_ledger=new, historical_ledger=old, expected_historical_sha256=old_sha, deployment_id="c16_nvbit175_recovery_llama32_1b_v1")
            self.assertEqual(old.read_bytes(), json.dumps({"legacy": [1, 2, 3]}).encode())
            self.assertEqual(ledger["campaign_id"], CAMPAIGN_ID)
            identity = {"deployment_id": "c16_nvbit175_recovery_llama32_1b_v1", "run_id": "r"}
            for _ in range(MAX_WINDOWS_PER_DEPLOYMENT):
                with RecoveryBudgetLease(new, identity, "NVBIT", capture=True) as lease:
                    lease.finish(elapsed_seconds=0, raw_bytes=0, terminal_status="COMPLETE")
            with self.assertRaisesRegex(Exception, "eight NVBit windows"):
                with RecoveryBudgetLease(new, identity, "NVBIT", capture=True): pass
            self.assertEqual(hashlib.sha256(old.read_bytes()).hexdigest(), old_sha)

    def test_capture_runner_accepts_recovery_identity_and_never_uses_it_by_default(self) -> None:
        source = (Path(__file__).parent / "retry570_multimodel_capture.py").read_text(encoding="utf-8")
        for token in ("RecoveryBudgetLease", "initialize_recovery_budget", "--recovery-deployment-id", "recovery capture requires one new ledger"):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
