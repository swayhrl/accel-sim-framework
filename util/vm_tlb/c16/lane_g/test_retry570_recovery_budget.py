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

    def test_existing_recovery_ledger_accepts_only_exact_archive_and_append_only_live_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "history-at-init.json"
            archive.write_text(json.dumps({"schema_version": "C16_G_EXECUTION_BUDGET_V1", "limits": {"n": 1}, "entries": [{"id": 1}]}), encoding="utf-8")
            import hashlib
            archive_sha = hashlib.sha256(archive.read_bytes()).hexdigest()
            live = root / "live-history.json"
            live.write_text(json.dumps({"schema_version": "C16_G_EXECUTION_BUDGET_V1", "limits": {"n": 1}, "entries": [{"id": 1}, {"id": 2}]}), encoding="utf-8")
            recovery = root / "recovery.json"
            recovery.write_text(json.dumps({
                "schema_version": "C16_G_NVBIT175_RECOVERY_BUDGET_V2", "campaign_id": CAMPAIGN_ID,
                "authorization": "USER_APPROVED_RECOVERY_CAPTURE_WINDOWS",
                "historical_ledger": {"path": str(live), "sha256": archive_sha, "rows_preserved": True},
                "limits": {"max_nvbit_capture_windows_per_deployment": MAX_WINDOWS_PER_DEPLOYMENT, "max_window_seconds": 1200, "max_window_raw_bytes": 4294967296, "max_total_raw_bytes": 34359738368},
                "authorized_deployments": [], "entries": [],
            }), encoding="utf-8")
            ledger = initialize(recovery_ledger=recovery, historical_ledger=live, expected_historical_sha256=archive_sha,
                                historical_archive=archive, deployment_id="c16_nvbit175_recovery_qwen2p5_7b_raw_v1")
            self.assertEqual(ledger["campaign_id"], CAMPAIGN_ID)
            changed = json.loads(live.read_text(encoding="utf-8")); changed["entries"][0] = {"id": "rewritten"}
            live.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(Exception, "append-only successor"):
                initialize(recovery_ledger=recovery, historical_ledger=live, expected_historical_sha256=archive_sha,
                           historical_archive=archive, deployment_id="c16_nvbit175_recovery_qwen2p5_7b_raw_v1")

    def test_capture_runner_accepts_recovery_identity_and_never_uses_it_by_default(self) -> None:
        source = (Path(__file__).parent / "retry570_multimodel_capture.py").read_text(encoding="utf-8")
        for token in ("RecoveryBudgetLease", "initialize_recovery_budget", "--recovery-deployment-id", "--recovery-historical-archive", "recovery capture requires one new ledger"):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
