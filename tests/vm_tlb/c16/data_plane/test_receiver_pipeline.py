#!/usr/bin/env python3
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from util.vm_tlb.c16.data_plane.admit_capture import admit
from util.vm_tlb.c16.data_plane.receiver_common import AdmissionError, sha256_file
from util.vm_tlb.c16.data_plane.rebuild_catalog_snapshot import rebuild
from util.vm_tlb.c16.data_plane.verify_capture import verify_partial
from util.vm_tlb.c16.data_plane.write_transfer_ack import write_ack


RUN_ID = "C16R_synthetic_s0_prefill_fixture_vector-add_20260914T150000Z_0123456789ab"


def manifest_for(run_id: str, payload: bytes) -> dict:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "created_at_utc": "2026-09-14T15:00:00Z",
        "scientific_status": "DIAGNOSTIC",
        "producer": {"hostname": "synthetic-109", "gpu_name": "synthetic", "gpu_uuid": "synthetic-uuid", "driver": "synthetic", "cuda": "synthetic"},
        "git": {"repository": "synthetic", "commit": "a" * 40, "dirty": False},
        "model": {"model_id": "synthetic/model", "revision": "synthetic", "asset_receipt_sha256": "b" * 64},
        "input": {"binding_id": "synthetic", "authority_status": "DIAGNOSTIC", "receipt_sha256": "c" * 64, "token_ids_sha256_or_semantic_hash": "d" * 64},
        "scenario": {"batch": 1, "prefill_tokens": 8, "decode_tokens": 1, "input_class": "TEXT", "phase": "P0"},
        "runtime": {"python": "synthetic", "torch": "synthetic", "transformers": "synthetic", "dtype": "synthetic", "attention_backend": "synthetic"},
        "capture": {"instrument": "synthetic", "tool_version": "1", "tool_identity_sha256_if_applicable": None, "target": "vector-add", "exact_argv": ["synthetic"]},
        "artifacts": [{"relative_path": "payload.bin", "size_bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}],
    }


class ReceiverPipelineTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "root"
        for rel in ("inbox", "raw", "catalog/entries", "catalog/snapshots", "reports"):
            (self.root / rel).mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.temp.cleanup()

    def make_partial(self, payload=b"synthetic payload\n"):
        bundle = self.root / "inbox" / f"{RUN_ID}.partial"
        bundle.mkdir()
        (bundle / "payload.bin").write_bytes(payload)
        (bundle / "RUN_MANIFEST.json").write_text(json.dumps(manifest_for(RUN_ID, payload), sort_keys=True) + "\n")
        (bundle / "READY").write_text("READY\n")
        return bundle

    def test_verify_admit_catalog_ack_and_snapshot(self):
        self.make_partial()
        verification = verify_partial(self.root, RUN_ID)
        receipt = self.root / "reports" / "verify.json"
        receipt.write_text(json.dumps(verification, sort_keys=True) + "\n")
        admitted = admit(self.root, receipt)
        admission_receipt = self.root / "reports" / "admit.json"
        admission_receipt.write_text(json.dumps(admitted, sort_keys=True) + "\n")
        ack_path, ack = write_ack(self.root, admission_receipt)
        self.assertTrue((self.root / "raw" / RUN_ID / "payload.bin").is_file())
        self.assertFalse((self.root / "inbox" / f"{RUN_ID}.partial").exists())
        self.assertEqual(ack["verification_status"], "PASS")
        self.assertTrue(ack_path.is_file())
        entry = json.loads((self.root / "catalog" / "entries" / f"{RUN_ID}.json").read_text())
        self.assertIn("raw_manifest_sha256", entry)
        self.assertNotIn("raw_sha256", entry)
        snapshot = rebuild(self.root)
        first = snapshot.read_bytes()
        self.assertEqual(first, rebuild(self.root).read_bytes())
        self.assertIn(RUN_ID.encode(), first)

    def test_corruption_rejected_before_admit(self):
        bundle = self.make_partial()
        (bundle / "payload.bin").write_bytes(b"mutated")
        with self.assertRaises(AdmissionError):
            verify_partial(self.root, RUN_ID)
        self.assertFalse((self.root / "raw" / RUN_ID).exists())

    def test_existing_raw_refuses_no_overwrite(self):
        self.make_partial()
        verification = verify_partial(self.root, RUN_ID)
        receipt = self.root / "reports" / "verify.json"
        receipt.write_text(json.dumps(verification) + "\n")
        admit(self.root, receipt)
        replacement = self.root / "inbox" / f"{RUN_ID}.partial"
        replacement.mkdir()
        (replacement / "payload.bin").write_bytes(b"synthetic payload\n")
        (replacement / "RUN_MANIFEST.json").write_text(json.dumps(manifest_for(RUN_ID, b"synthetic payload\n")))
        with self.assertRaises(AdmissionError):
            admit(self.root, receipt)
        self.assertEqual((self.root / "raw" / RUN_ID / "payload.bin").read_bytes(), b"synthetic payload\n")


if __name__ == "__main__":
    unittest.main()
