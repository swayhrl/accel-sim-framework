"""Focused static contract checks for the Recovery-V3 NVBit qualification parent."""
from pathlib import Path
import unittest


SOURCE = (Path(__file__).resolve().parents[4] / "util/vm_tlb/c16/lane_g/retry570_recovery_v3_nvbit_qualification.py").read_text(encoding="utf-8")


class RecoveryV3QualificationContractTest(unittest.TestCase):
    def test_parent_owned_fresh_campaign_lease(self):
        for token in ("RecoveryV3CampaignLease", "initialize(", "write_parent_lease_start", "C16_G_PARENT_LEASE_TOKEN", "MeasurementActive(args.campaign_ledger", "child_acquired_second_lease"):
            self.assertIn(token, SOURCE)

    def test_only_identity_diagnostics_are_admitted(self):
        self.assertIn('MODES = ("NVBIT_LAUNCH_INVENTORY", "NVBIT_STATIC_MAP")', SOURCE)
        self.assertIn("scientific_eligible_for_timing\": False", SOURCE)
        self.assertIn("RECOVERY_V3_DIRECT_NVBIT_IDENTITY_QUALIFICATION_NOT_FOR_TIMING", SOURCE)


if __name__ == "__main__":
    unittest.main()
