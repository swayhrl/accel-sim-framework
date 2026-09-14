from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from retry570_recovery_v3_campaign_budget import CAMPAIGN_ID, RecoveryV3CampaignLease, initialize


IDENTITY = {"deployment_id": "c16_qwen25_05b_native_reference", "scenario_id": "S0", "run_id": "run-1"}
SCOPE = "c16_qwen25_05b_native_reference/S0/PREFILL_DIRECT_MEMORY"


class RecoveryV3CampaignBudgetTests(unittest.TestCase):
    def test_new_ledger_preserves_history_and_binds_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); historical = root / "legacy.json"; historical.write_text('{"entries":[1]}', encoding="utf-8")
            historical_sha = hashlib.sha256(historical.read_bytes()).hexdigest(); ledger = root / "v3.json"
            value = initialize(ledger_path=ledger, historical_ledger=historical, expected_historical_sha256=historical_sha,
                               identity=IDENTITY, budget_scope=SCOPE)
            self.assertEqual(value["campaign_id"], CAMPAIGN_ID)
            self.assertEqual(hashlib.sha256(historical.read_bytes()).hexdigest(), historical_sha)
            with RecoveryV3CampaignLease(ledger, IDENTITY, "NVBIT", capture=True, budget_scope=SCOPE) as lease:
                self.assertEqual(lease.max_elapsed_seconds, 1200)
                lease.finish(elapsed_seconds=0, raw_bytes=0, terminal_status="COMPLETE")
            row = json.loads(ledger.read_text())["entries"][0]
            self.assertEqual(row["budget_scope"], SCOPE)
            self.assertEqual(row["campaign_id"], CAMPAIGN_ID)

    def test_scope_must_match_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); historical = root / "legacy.json"; historical.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(Exception, "deployment/scenario/phase-target-class"):
                initialize(ledger_path=root / "v3.json", historical_ledger=historical,
                           expected_historical_sha256=hashlib.sha256(historical.read_bytes()).hexdigest(),
                           identity=IDENTITY, budget_scope="wrong/S0/PREFILL")


if __name__ == "__main__":
    unittest.main()
