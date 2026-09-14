"""CPU-only guards for Recovery-V3 G1 authority audit semantics."""
from pathlib import Path
import unittest


SOURCE = Path(__file__).with_name("retry570_recovery_v3_g1_authority_audit.py").read_text(encoding="utf-8")


class G1AuthorityAuditTests(unittest.TestCase):
    def test_incomplete_claims_are_explicitly_superseded(self):
        for token in ("previous_claimed_status", "nsys_rep_exists", "catalog_validation_status",
                      "parent_lease_authority", "SUPERSEDED_NON_AUTHORITATIVE_REQUIRES_CAMPAIGN_G1"):
            self.assertIn(token, SOURCE)

    def test_requires_all_native_profile_catalog_and_campaign_parent_evidence(self):
        self.assertIn("native_valid and profile_mode == \"NATIVE_GPU\"", SOURCE)
        self.assertIn("catalog_valid and parent_authority", SOURCE)


if __name__ == "__main__":
    unittest.main()
