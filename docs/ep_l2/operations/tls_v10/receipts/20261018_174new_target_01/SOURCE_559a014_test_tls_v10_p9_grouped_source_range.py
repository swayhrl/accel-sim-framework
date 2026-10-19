#!/usr/bin/env python3
"""Synthetic /tmp-only tests; never stages an actual TLS source file."""

import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import tls_v10_p9_grouped_source_range as stage


class RangeStageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="tls-v10-range-fixture-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "source"
        self.bridge = Path(self.tmp.name) / "bridge"
        (self.root / "nested").mkdir(parents=True)
        self.bridge.mkdir()
        self.original = self.root / "nested" / "evidence.bin"
        self.content = b"alpha" * 2048
        self.original.write_bytes(self.content)
        self.frozen = stage._fingerprint(os.lstat(self.original))
        self.frozen["relative_path"] = "nested/evidence.bin"

    def call(self, **updates):
        kw = dict(root=self.root, frozen=self.frozen, offset=0,
                  length=len(self.content), bridge_directory=self.bridge,
                  payload_name="range-0000.bin", existing_bridge_allocated_bytes=0)
        kw.update(updates)
        return stage.stage_range(**kw)

    def test_full_exact_and_original_kept(self):
        receipt = self.call()
        self.assertEqual(receipt["fresh_chunk_sha256"], hashlib.sha256(self.content).hexdigest())
        self.assertEqual((self.bridge / "range-0000.bin").read_bytes(), self.content)
        self.assertEqual(self.original.read_bytes(), self.content)
        self.assertEqual(receipt["source_originals"], "SOURCE_KEEP")

    def test_partial_range(self):
        receipt = self.call(offset=17, length=53)
        self.assertEqual((self.bridge / "range-0000.bin").read_bytes(), self.content[17:70])
        self.assertEqual(receipt["length"], 53)

    def test_no_overwrite(self):
        self.call()
        with self.assertRaises(FileExistsError):
            self.call()

    def test_frozen_identity_drift(self):
        changed = dict(self.frozen, inode=self.frozen["inode"] + 1)
        with self.assertRaises(stage.Hold):
            self.call(frozen=changed)
        self.assertFalse((self.bridge / "range-0000.bin").exists())

    def test_source_symlink_rejected(self):
        alias = self.root / "nested" / "alias.bin"
        alias.symlink_to("evidence.bin")
        with self.assertRaises(OSError):
            self.call(frozen=dict(self.frozen, relative_path="nested/alias.bin"))

    def test_directory_symlink_rejected(self):
        (self.root / "alias").symlink_to("nested")
        with self.assertRaises(OSError):
            self.call(frozen=dict(self.frozen, relative_path="alias/evidence.bin"))

    def test_traversal_rejected(self):
        for rel in ("../nested/evidence.bin", "/nested/evidence.bin", "nested//evidence.bin"):
            with self.subTest(rel=rel), self.assertRaises(stage.Hold):
                self.call(frozen=dict(self.frozen, relative_path=rel))
        with self.assertRaises(stage.Hold):
            self.call(payload_name="../escape")

    def test_range_limits(self):
        for values in (dict(length=0), dict(offset=-1), dict(offset=1, length=len(self.content)),
                       dict(existing_bridge_allocated_bytes=stage.MAX_PHYSICAL),
                       dict(limiter=object())):
            with self.subTest(values=values), self.assertRaises(stage.Hold):
                self.call(**values)

    def test_bridge_symlink_rejected(self):
        alias = Path(self.tmp.name) / "bridge-alias"
        alias.symlink_to(self.bridge, target_is_directory=True)
        with self.assertRaises(stage.Hold):
            self.call(bridge_directory=alias)

    def test_postcopy_source_change_holds_and_keeps_stage(self):
        original_sleep = stage.time.sleep
        def mutate(_):
            self.original.write_bytes(self.content + b"!")
        try:
            with mock.patch.object(stage.time, "sleep", side_effect=mutate):
                with self.assertRaises(stage.Hold):
                    self.call(limiter=stage.RateLimiter(1))
        finally:
            stage.time.sleep = original_sleep
        self.assertTrue((self.bridge / "range-0000.bin").exists())

    def test_named_path_swap_holds_and_keeps_stage(self):
        def swap(_):
            replacement = self.original.with_suffix(".new")
            replacement.write_bytes(self.content)
            os.replace(replacement, self.original)
        with mock.patch.object(stage.time, "sleep", side_effect=swap):
            with self.assertRaises(stage.Hold):
                self.call(limiter=stage.RateLimiter(1))
        self.assertTrue((self.bridge / "range-0000.bin").exists())

    def test_aggregate_rate_budget_across_ranges(self):
        limiter = stage.RateLimiter(stage.MAX_RATE)
        self.call(length=1024, limiter=limiter)
        self.call(offset=1024, length=2048, payload_name="range-0001.bin", limiter=limiter,
                  existing_bridge_allocated_bytes=4096)
        self.assertEqual(limiter.total_bytes, 3072)


if __name__ == "__main__":
    unittest.main()
