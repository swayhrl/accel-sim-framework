#!/usr/bin/env python3
"""Only synthetic /tmp fixtures; never inspect or stage the real P9 source."""

from dataclasses import replace
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import tls_v10_copy_only16g_gate as policy
import tls_v10_copy_only20g_gate as old
import tls_v10_p9_exact_window_runner as runner
import tls_v10_p9_grouped_source_range as sender


def raw(item):
    return (json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n").encode()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.DEVNULL,
                                   text=True).strip()


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="tls-v10-runner-fixture-", dir="/tmp")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "source"
        self.bridge = self.base / "bridge"
        self.target = self.base / "targetrepo"
        self.source_repo = self.base / "sourcerepo"
        self.receipts = self.source_repo / "receipts"
        for p in (self.source, self.bridge, self.target, self.source_repo, self.receipts):
            p.mkdir()
        write(self.bridge / ".TLS_V10_SOURCE_SENDER.lock", b"")
        (self.source / "data").mkdir()
        self.payload = self.source / "data" / "actual.bin"
        write(self.payload, b"abcdefgh")
        files = []
        for i in range(140):
            p = self.source / "data" / ("empty-%03d.bin" % i)
            write(p, b"")
        for p in sorted((self.source / "data").iterdir()):
            s = os.lstat(p)
            files.append(dict(sender._fingerprint(s), relative_path="data/" + p.name,
                              sha256=hashlib.sha256(p.read_bytes()).hexdigest(), type="regular"))
        self.file = next(v for v in files if v["relative_path"] == "data/actual.bin")
        self.manifest_obj = {"source_root": str(self.source),
                             "source_frozen_commit": "e" * 40, "files": files,
                             "directories": [{"relative_path": "."}, {"relative_path": "data"}]}
        self.manifest = self.base / "manifest.json"
        write(self.manifest, raw(self.manifest_obj))
        self.manifest_sha = runner.sha(self.manifest.read_bytes())
        batches = []
        for i in range(4):
            entry = {"relative_path": "data/actual.bin", "offset": 2 * i, "length": 2,
                     "original_size": 8, "original_sha256": self.file["sha256"]}
            batches.append({"entries": [entry], "raw_bytes": 2,
                            "txid": old.TXID, "selector_sha256": old.SELECTOR,
                            "manifest_sha256": self.manifest_sha})
        self.plan_obj = {"schema": "TLS_V10_INACTIVE_RAW_BATCH_PLAN_V1",
                         "txid": old.TXID, "selector_sha256": old.SELECTOR,
                         "manifest_sha256": self.manifest_sha,
                         "source_root": str(self.source), "native164_root": old.TARGET_ROOT,
                         "batches": batches}
        self.plan = self.base / "plan.json"
        write(self.plan, raw(self.plan_obj))
        self.plan_sha = runner.sha(self.plan.read_bytes())
        self.window = "TLS_V10_P9_PUBLIC_B0004"
        self.previous = "TLS_V10_P9_PUBLIC_B0003"
        self.request_name = self.window + "_TARGET_SOLE_WINDOW_REQUEST_COPY16.json"
        self.cleanup_name = self.previous + "_BRIDGE_CLEANUP_COPY16.json"
        self.cleanup = {"window_id": self.previous, "txid": old.TXID,
                        "source_originals": "SOURCE_KEEP", "source_files_deleted_by_target": 0,
                        "removed_count": 1, "archive_and_native_every_range_reverified": True}
        self.cleanup_raw = raw(self.cleanup)
        write(self.bridge / self.cleanup_name, self.cleanup_raw)
        self.cleanup_sha = runner.sha(self.cleanup_raw)
        stage_root = self.bridge / (self.window + "_" + old.TXID[:12]) / "files"
        entry = dict(self.plan_obj["batches"][3]["entries"][0],
                     source_path=str(self.payload),
                     source_identity={k: self.file[k] for k in runner.FIELDS},
                     bridge_path=str(stage_root / "range-0000.bin"))
        self.request = {"schema": "TLS_V10_TARGET_GROUPED_RAW_WINDOW_V1",
                        "window_id": self.window, "group": old.GROUP,
                        "txid": old.TXID, "selector_sha256": old.SELECTOR,
                        "canonical_manifest_sha256": self.manifest_sha,
                        "source_frozen_commit": "e" * 40,
                        "source_root": str(self.source),
                        "target_root_native164": old.TARGET_ROOT,
                        "plan_sha256": self.plan_sha, "plan_batch_index": 3,
                        "bridge_root": str(stage_root), "prior_window": self.previous,
                        "prior_window_cleanup_name": self.cleanup_name,
                        "prior_window_cleanup_sha256": self.cleanup_sha,
                        "source_originals": "SOURCE_KEEP",
                        "source_scientific_release_authorized_by_this_window": False,
                        "copy_ready": False, "payload_paths_created_by_target": False,
                        "ranges": [entry], "range_count": 1, "raw_bytes": 2}
        git(self.target, "init", "-q")
        git(self.target, "config", "user.email", "fixture@example.invalid")
        git(self.target, "config", "user.name", "Fixture")
        relative_cleanup = runner.TARGET_RECEIPTS + self.cleanup_name
        write(self.target / relative_cleanup, self.cleanup_raw)
        git(self.target, "add", relative_cleanup)
        git(self.target, "commit", "-qm", "cleanup")
        self.cleanup_commit = git(self.target, "rev-parse", "HEAD")
        self.request["prior_window_cleanup_commit"] = self.cleanup_commit
        self.request_raw = raw(self.request)
        write(self.bridge / self.request_name, self.request_raw)
        relative_req = runner.TARGET_RECEIPTS + self.request_name
        write(self.target / relative_req, self.request_raw)
        git(self.target, "add", relative_req)
        git(self.target, "commit", "-qm", "request")
        self.request_commit = git(self.target, "rev-parse", "HEAD")
        self.receiver_name = self.window + "_TARGET_METADATA_PREFLIGHT_COPY16.json"
        self.receiver = {"schema": "TLS_V10_NEXT_GROUPED_WINDOW_TARGET_METADATA_PREFLIGHT_V1",
                         "utc": datetime.now(timezone.utc).isoformat(),
                         "window_id": self.window, "prior_B0003_closed": True,
                         "bridge_payloads_absent": True, "receiver_idle": True,
                         "next_stage_not_created_by_target": True}
        receiver_raw = raw(self.receiver)
        write(self.bridge / self.receiver_name, receiver_raw)
        receiver_relative = runner.TARGET_RECEIPTS + self.receiver_name
        write(self.target / receiver_relative, receiver_raw)
        git(self.target, "add", receiver_relative)
        git(self.target, "commit", "-qm", "receiver preflight")
        self.receiver_commit = git(self.target, "rev-parse", "HEAD")
        git(self.source_repo, "init", "-q")
        git(self.source_repo, "config", "user.email", "fixture@example.invalid")
        git(self.source_repo, "config", "user.name", "Fixture")
        self.binding = {"schema": "TLS_V10_P9_EXACT_SOURCE_WINDOW_BINDING_V1",
                        "window_id": self.window, "plan_batch_index": 3,
                        "txid": old.TXID, "selector_sha256": old.SELECTOR,
                        "canonical_manifest_sha256": self.manifest_sha,
                        "source_root": str(self.source),
                        "target_root_native164": old.TARGET_ROOT,
                        "policy_id": policy.POLICY_ID,
                        "plan_sha256": self.plan_sha,
                        "target_request_name": self.request_name,
                        "target_request_sha256": runner.sha(self.request_raw),
                        "target_request_git_commit": self.request_commit,
                        "prior_cleanup_name": self.cleanup_name,
                        "prior_cleanup_sha256": self.cleanup_sha,
                        "prior_cleanup_git_commit": self.cleanup_commit,
                        "target_receiver_preflight_name": self.receiver_name,
                        "target_receiver_preflight_sha256": runner.sha(receiver_raw),
                        "target_receiver_preflight_git_commit": self.receiver_commit}
        self.binding_path = self.base / "binding.json"
        self.save_binding()
        self.context = runner.Context(self.source, self.bridge, self.source_repo,
                                      self.target, self.manifest, self.plan, self.receipts)
        self.gate = old.policy_input(
            policy_id=policy.POLICY_ID, amendment_sha256=policy.AUTHORITY_SHA256,
            source_root=str(self.source), manifest_sha256=self.manifest_sha,
            window_id=self.window, target_request_sha256=runner.sha(self.request_raw),
            workspace_available_bytes=17 * old.GIB,
            share_available_bytes=43 * old.GIB)
        self.clear = {"base": self.gate, "lane_final_closure_verified": True,
                      "lane_physical_clear": True, "source_reader_clear": True,
                      "scheduled_reader_clear": True, "sole_sender_clear": True,
                      "receiver_clear": True}
        self.controller = runner.ExactWindowRunner(self.context, self.binding_path,
                                                   lambda: self.clear)

    def save_binding(self):
        write(self.binding_path, raw(self.binding))

    def save_request(self, *, commit=True):
        self.request_raw = raw(self.request)
        write(self.bridge / self.request_name, self.request_raw)
        write(self.target / (runner.TARGET_RECEIPTS + self.request_name), self.request_raw)
        if commit:
            git(self.target, "add", runner.TARGET_RECEIPTS + self.request_name)
            git(self.target, "commit", "-qm", "revised request")
            self.binding["target_request_git_commit"] = git(self.target, "rev-parse", "HEAD")
        self.binding["target_request_sha256"] = runner.sha(self.request_raw)
        self.gate = replace(self.gate, target_request_sha256=self.binding["target_request_sha256"])
        self.clear["base"] = self.gate
        self.save_binding()

    def expect_hold(self, function):
        with self.assertRaises(runner.Hold):
            function()


class TestRunner(Fixture):
    def test_positive_prepare_stage_bounded_and_no_unlink(self):
        passed = self.controller.prepare()
        self.assertEqual(passed["receipt"]["status"], "PASS_NOT_READY_NO_STAGE")
        with patch.object(sender, "BLOCK", 1):
            ready = self.controller.stage()
        self.assertEqual(ready["receipt"]["entries"][0]["chunk_sha256"],
                         hashlib.sha256(b"gh").hexdigest())
        self.assertEqual(ready["receipt"]["source_files_unlinked"], 0)
        self.assertEqual(self.payload.read_bytes(), b"abcdefgh")
        self.assertFalse((self.bridge / (self.window + "_SOURCE_READY_COPY16.json")).exists())
        self.expect_hold(self.controller.stage)

    def test_git_bridge_request_bytes_must_match(self):
        self.request["status"] = "tampered"
        self.save_request(commit=False)
        self.expect_hold(self.controller.prepare)

    def test_prior_cleanup_git_bridge_bytes_must_match(self):
        write(self.bridge / self.cleanup_name, self.cleanup_raw + b" ")
        self.expect_hold(self.controller.prepare)

    def test_exact_done_cleanup_filename_is_supported(self):
        done_name = self.previous + "_BRIDGE_CLEANUP_DONE_COPY16.json"
        write(self.bridge / done_name, self.cleanup_raw)
        write(self.target / (runner.TARGET_RECEIPTS + done_name), self.cleanup_raw)
        git(self.target, "add", runner.TARGET_RECEIPTS + done_name)
        git(self.target, "commit", "-qm", "done cleanup")
        self.cleanup_name = done_name
        self.cleanup_commit = git(self.target, "rev-parse", "HEAD")
        self.request["prior_window_cleanup_name"] = done_name
        self.request["prior_window_cleanup_commit"] = self.cleanup_commit
        self.save_request()
        self.binding["prior_cleanup_name"] = done_name
        self.binding["prior_cleanup_git_commit"] = self.cleanup_commit
        self.save_binding()
        self.assertEqual(self.controller.prepare()["receipt"]["status"],
                         "PASS_NOT_READY_NO_STAGE")

    def test_wrong_binding_and_plan_batch(self):
        self.binding["plan_batch_index"] = 2
        self.save_binding()
        self.expect_hold(self.controller.prepare)

    def test_range_overlap_and_raw_cap(self):
        self.request["ranges"][0]["length"] = 129 * old.MIB
        self.request["raw_bytes"] = 129 * old.MIB
        self.save_request()
        self.expect_hold(self.controller.prepare)

    def test_source_metadata_drift(self):
        os.chmod(self.payload, 0o600)
        self.expect_hold(self.controller.prepare)

    def test_stale_resource_and_lease(self):
        self.clear["base"] = replace(self.gate, snapshot_age_seconds=31)
        self.expect_hold(self.controller.prepare)
        self.clear["base"] = replace(self.gate, copy_lease_authorized=False)
        self.expect_hold(self.controller.prepare)

    def test_reader_and_lane_hold(self):
        self.clear["source_reader_clear"] = False
        self.expect_hold(self.controller.prepare)
        self.clear["source_reader_clear"] = True
        self.clear["lane_final_closure_verified"] = False
        self.expect_hold(self.controller.prepare)

    def test_preexisting_stage_hold_without_cleanup(self):
        stage = Path(self.request["bridge_root"])
        stage.mkdir(parents=True)
        write(stage / "unrelated.bin", b"preserve")
        self.expect_hold(self.controller.prepare)
        self.assertEqual((stage / "unrelated.bin").read_bytes(), b"preserve")

    def test_share_and_workspace_projection(self):
        self.clear["base"] = replace(self.gate, workspace_available_bytes=16 * old.GIB)
        self.expect_hold(self.controller.prepare)
        self.clear["base"] = replace(self.gate, share_available_bytes=40 * old.GIB)
        self.expect_hold(self.controller.prepare)

    def test_stage_preserves_uncertain_source_change(self):
        self.controller.prepare()
        os.chmod(self.payload, 0o600)
        self.expect_hold(self.controller.stage)
        self.assertEqual(self.payload.read_bytes(), b"abcdefgh")

    def test_publish_requires_source_git_readback(self):
        self.controller.prepare()
        self.controller.stage()
        self.expect_hold(lambda: self.controller.publish("0" * 40))
        self.assertFalse((self.bridge / (self.window + "_SOURCE_READY_COPY16.json")).exists())

    def test_publish_after_exact_source_git_readback(self):
        self.controller.prepare()
        prepared = self.controller.stage()
        path = Path(prepared["path"])
        git(self.source_repo, "add", str(path.relative_to(self.source_repo)))
        git(self.source_repo, "commit", "-qm", "ready")
        commit = git(self.source_repo, "rev-parse", "HEAD")
        published = self.controller.publish(commit)
        self.assertEqual(published["sha256"], runner.sha(path.read_bytes()))
        self.assertEqual(Path(published["bridge_ready"]).read_bytes(), path.read_bytes())
        self.assertEqual(prepared["receipt"]["source_protocol_adoption_sha256"],
                         runner.sha(runner.ADOPTION.read_bytes()))
        notice = self.bridge / (self.window + "_SOURCE_READY_PUBLICATION_COPY16.json")
        self.assertEqual(json.loads(notice.read_bytes())["source_git_commit"], commit)
        self.assertEqual(self.payload.read_bytes(), b"abcdefgh")
        self.expect_hold(lambda: self.controller.publish(commit))

    def test_stale_or_busy_target_receiver_hold(self):
        self.receiver["utc"] = (datetime.now(timezone.utc) - timedelta(minutes=16)).isoformat()
        receiver_raw = raw(self.receiver)
        write(self.bridge / self.receiver_name, receiver_raw)
        write(self.target / (runner.TARGET_RECEIPTS + self.receiver_name), receiver_raw)
        git(self.target, "add", runner.TARGET_RECEIPTS + self.receiver_name)
        git(self.target, "commit", "-qm", "stale receiver")
        self.binding["target_receiver_preflight_sha256"] = runner.sha(receiver_raw)
        self.binding["target_receiver_preflight_git_commit"] = git(self.target, "rev-parse", "HEAD")
        self.save_binding()
        self.expect_hold(self.controller.prepare)

    def test_stream_read_requests_are_one_mib_or_less(self):
        large = self.source / "data" / "bounded-large.bin"
        write(large, b"x" * (2 * runner.MIB + 7))
        identity = dict(sender._fingerprint(os.lstat(large)),
                        relative_path="data/bounded-large.bin")
        stage = self.base / "synthetic-stage"
        stage.mkdir()
        lengths = []
        real_read = os.read

        def observed(fd, count):
            lengths.append(count)
            return real_read(fd, count)

        with patch.object(os, "read", side_effect=observed):
            digest = runner._range_sha(self.source, identity, 0, identity["size"])
            staged = sender.stage_range(self.source, identity, 0, identity["size"],
                                        stage, "range.bin", existing_bridge_allocated_bytes=0)
        self.assertTrue(lengths)
        self.assertLessEqual(max(lengths), runner.MIB)
        self.assertEqual(staged["fresh_chunk_sha256"], digest)
        self.assertEqual(large.stat().st_size, 2 * runner.MIB + 7)


if __name__ == "__main__":
    unittest.main()
