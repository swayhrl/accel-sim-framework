#!/usr/bin/env python3
"""Schema and checksum tests for the FFN timeline identity authorization pack."""

import csv
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "docs/vm_tlb/review_packs/C16_FFN_TIMELINE_CAPTURE_IDENTITY_RECOVERY_AND_AUTHORIZATION_174NEW_V1"


class TimelineIdentityPackTest(unittest.TestCase):
    def test_identity_table_is_closed(self):
        with (PACK / "SCIENTIFIC_IDENTITY_RECOVERY.tsv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        self.assertGreaterEqual(len(rows), 35)
        self.assertEqual(len(rows), len({row["field"] for row in rows}))
        self.assertFalse([row for row in rows if row["status"] == "UNKNOWN"])
        self.assertTrue(all(row["status"] in {"DIRECT_ACCEPTED_AUTHORITY", "DETERMINISTICALLY_DERIVED", "UNKNOWN"} for row in rows))

    def test_authorization_scope(self):
        contract = json.loads((PACK / "AUTHORIZED_FFN_TIMELINE_CAPTURE_CONTRACT_V1.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "AUTHORIZED")
        self.assertEqual(contract["decision"], "IDENTITY_RECOVERED_FROM_ACCEPTED_AUTHORITY")
        self.assertEqual(contract["scientific_identity_change"], "NONE")
        self.assertEqual(contract["purpose"], "TIMELINE_AUTHORITY_ONLY")
        self.assertEqual(contract["measurement_protocol"]["total_gpu_process_launches_max"], 3)
        for tool in ("NCU", "NVBit", "SASS", "oracle", "Accel_Sim"):
            self.assertFalse(contract["tools"][tool])

    def test_project_review_and_checksums(self):
        review = json.loads((PACK / "PROJECT_REVIEW.json").read_text(encoding="utf-8"))
        self.assertEqual(review["unknown_required_fields"], 0)
        subprocess.run(["sha256sum", "-c", "SHA256SUMS"], cwd=PACK, check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
