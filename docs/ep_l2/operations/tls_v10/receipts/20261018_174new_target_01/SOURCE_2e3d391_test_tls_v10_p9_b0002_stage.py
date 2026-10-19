#!/usr/bin/env python3
"""Fixture tests for the exact B0002 controller's fail-closed entrypoints."""

from pathlib import Path
import tempfile
import unittest
from unittest import mock

import tls_v10_p9_b0002_stage as controller
import tls_v10_p9_grouped_source_range as sender


class B0002ControllerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="tls-v10-b0002-controller-")
        self.addCleanup(self.tmp.cleanup)
        self.pass_path = Path(self.tmp.name) / "PASS.json"
        self.ready_path = Path(self.tmp.name) / "READY.json"
        self.pass_patch = mock.patch.object(controller, "PASS", self.pass_path)
        self.ready_patch = mock.patch.object(controller, "READY", self.ready_path)
        self.pass_patch.start(); self.ready_patch.start()
        self.addCleanup(self.pass_patch.stop); self.addCleanup(self.ready_patch.stop)

    def test_gate_pass_is_not_ready_or_payload(self):
        snapshot = {"decision": {"decision": "POLICY_ELIGIBLE_NOT_READY", "reasons": []},
                    "range_count": 34, "source_originals": "SOURCE_KEEP"}
        with mock.patch.object(controller.check, "inspect", return_value=snapshot):
            controller.prepare_gate()
        self.assertTrue(self.pass_path.exists())
        self.assertFalse(self.ready_path.exists())
        self.assertIn("GATE_PASS_NOT_READY_NO_PAYLOAD_STAGED", self.pass_path.read_text())

    def test_gate_hold_writes_nothing(self):
        snapshot = {"decision": {"decision": "RESOURCE_HOLD", "reasons": ["READER"]}}
        with mock.patch.object(controller.check, "inspect", return_value=snapshot):
            with self.assertRaises(sender.Hold):
                controller.prepare_gate()
        self.assertFalse(self.pass_path.exists())

    def test_no_duplicate_gate_or_ready(self):
        self.pass_path.write_text("already exists")
        with self.assertRaises(sender.Hold):
            controller.prepare_gate()
        self.pass_path.unlink()
        self.ready_path.write_text("already exists")
        with self.assertRaises(sender.Hold):
            controller.prepare_gate()

    def test_publication_rejects_non_sha(self):
        with self.assertRaises(sender.Hold):
            controller.publish_bridge("not-a-commit")


if __name__ == "__main__":
    unittest.main()
