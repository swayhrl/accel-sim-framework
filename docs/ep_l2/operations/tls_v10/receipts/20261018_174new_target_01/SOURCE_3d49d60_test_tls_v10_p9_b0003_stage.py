#!/usr/bin/env python3
"""Bounded controller fixtures in /tmp; no science file stage or unlink."""

from pathlib import Path
import tempfile
import unittest
from unittest import mock

import tls_v10_p9_b0003_stage as controller
import tls_v10_p9_grouped_source_range as sender


class B0003ControllerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="tls-v10-b0003-fixture-")
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        (base / "ADOPTION.json").write_text("{}\n")
        (base / "TEST_RECEIPT.json").write_text("{}\n")
        p1 = mock.patch.object(controller, "PASS", base / "PASS.json")
        p2 = mock.patch.object(controller, "READY", base / "READY.json")
        p3 = mock.patch.object(controller, "ADOPTION", base / "ADOPTION.json")
        p4 = mock.patch.object(controller, "TEST_RECEIPT", base / "TEST_RECEIPT.json")
        for patch in (p1, p2, p3, p4):
            patch.start()
            self.addCleanup(patch.stop)

    def test_gate_pass_is_not_ready(self):
        snap = {"decision": {"decision": "POLICY_ELIGIBLE_NOT_READY", "reasons": []},
                "source_originals": "SOURCE_KEEP"}
        with mock.patch.object(controller.check, "inspect", return_value=snap):
            controller.prepare_gate()
        self.assertTrue(controller.PASS.exists())
        self.assertFalse(controller.READY.exists())
        self.assertIn("GATE_PASS_NOT_READY_NO_PAYLOAD_STAGED", controller.PASS.read_text())

    def test_gate_hold_writes_nothing(self):
        snap = {"decision": {"decision": "RESOURCE_HOLD", "reasons": ["LOW_SHARE"]}}
        with mock.patch.object(controller.check, "inspect", return_value=snap):
            with self.assertRaises(sender.Hold):
                controller.prepare_gate()
        self.assertFalse(controller.PASS.exists())

    def test_duplicate_pass_refused(self):
        controller.PASS.write_text("existing")
        with self.assertRaises(sender.Hold):
            controller.prepare_gate()

    def test_bounded_stream_hash(self):
        p = Path(self.tmp.name) / "fixture.bin"
        p.write_bytes(b"z" * (2 * sender.MIB + 17))
        seen = []
        original = controller.os.read
        def checked(fd, size):
            seen.append(size)
            return original(fd, size)
        with mock.patch.object(controller.os, "read", side_effect=checked):
            self.assertEqual(controller.stream_sha(p), controller.sha(p.read_bytes()))
        self.assertTrue(seen)
        self.assertLessEqual(max(seen), sender.MIB)

    def test_publication_invalid_commit_refused(self):
        with self.assertRaises(sender.Hold):
            controller.publish_bridge("invalid")


if __name__ == "__main__":
    unittest.main()
