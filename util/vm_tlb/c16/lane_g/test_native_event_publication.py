#!/usr/bin/env python3
"""Focused offline tests for the native-event publication validator."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))
import native_event_publication as publisher  # noqa: E402


class NativeEventPublicationTest(unittest.TestCase):
    def make_source(self, root: Path) -> tuple[Path, Path]:
        raw = root / "report.nsys-rep"
        raw.write_bytes(b"closed raw profile\n")
        digest = publisher.sha256_file(raw)
        identity = {
            "deployment_id": "d", "model_id": "m", "model_revision": "r", "tokenizer_revision": "r",
            "scenario_id": "S1", "input_hash": "i", "run_id": "run", "code_commit": "a" * 40,
            "dtype": "float16", "implementation_key": "EAGER", "quantization": "NONE",
        }
        profile = {
            "execution_mode": "NATIVE_GPU", "scientific_eligible": True, "identity": identity,
            "runtime": {}, "artifacts": {"terminal_status": "COMPLETE"},
            "checks": {"package_id": "P", "package_fixed_commit": "b" * 40,
                       "package_manifest_sha256": "c" * 64},
        }
        nsys = {
            "execution_mode": "NATIVE_GPU", "scientific_eligible": True, "identity": identity,
            "runtime": {"profiler_mode": "NSYS"}, "artifacts": {"terminal_status": "COMPLETE", "tool": "nsys"},
            "checks": {"command": ["nsys", "profile"], "nsys_capture_range": "none", "target_identity_fields": {}},
        }
        profile_path, nsys_path = root / "profile.json", root / "nsys.json"
        profile_path.write_text(json.dumps(profile)); nsys_path.write_text(json.dumps(nsys))
        spec = {
            "schema_version": "C16_G_NATIVE_EVENT_PUBLICATION_SOURCES_V1", "producer_branch": "g",
            "publication_source_anchor": "d" * 40,
            "remote_nsys_version": {"remote_host_label": "host", "nsys_logical_path": "/nsys", "command": "nsys --version", "stdout": "NVIDIA Nsight Systems version X", "version": "X", "measurement_active_observation": "absent"},
            "events": [{"event_id": "ONE", "profile_receipt": str(profile_path), "nsys_receipt": str(nsys_path),
                        "producer_branch": "g", "publication_source_anchor": "d" * 40,
                        "raw": {"remote_logical_path": "/remote/report.nsys-rep", "local_path": str(raw), "size_bytes": raw.stat().st_size, "sha256": digest,
                                "remote_endpoint_state": "REMOTE_PRESENT", "remote_recheck_mode": "LIVE_READ_ONLY_RECHECK"}}],
        }
        spec_path = root / "sources.json"; spec_path.write_text(json.dumps(spec))
        return spec_path, root / "out"

    def test_write_validate_and_tamper_detection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            spec, output = self.make_source(Path(temporary))
            publisher.write_publication(spec, output)
            self.assertEqual(len(publisher.validate_publication(output, spec)), 7)
            event = output / "events" / "ONE.json"
            event.write_text(event.read_text() + "tamper\n")
            with self.assertRaises(publisher.ContractError):
                publisher.validate_publication(output, spec)


if __name__ == "__main__":
    unittest.main()
