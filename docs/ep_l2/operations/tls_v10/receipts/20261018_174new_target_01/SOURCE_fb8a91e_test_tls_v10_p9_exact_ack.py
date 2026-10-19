#!/usr/bin/env python3
"""Synthetic /tmp qualification of B0004+ ACK sidecar; no production writes."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

import tls_v10_p9_exact_ack as ack
import tls_v10_p9_streaming_ack_core as core
import test_tls_v10_p9_streaming_ack_core as fixture_module


def raw(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


class ExactAckTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture_module.StreamingReceiptTests(
            "test_valid_partial_scope_and_no_source_deletion")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        f = self.fixture
        self.base = Path(f.tmp.name)
        self.bridge_root = self.base / "bridge-root"
        self.bridge_root.mkdir()
        self.window = "TLS_V10_P9_PUBLIC_B0004"
        self.txid = "a" * 64
        actual_directory = self.bridge_root / (self.window + "_" + self.txid[:12])
        os.rename(f.bridge_directory, actual_directory)
        f.bridge_directory = actual_directory
        for directory in ("a", "b", "c"):
            (f.source_root / directory).mkdir()
        f.manifest["directories"] = [{"relative_path": name} for name in
                                     (".", "a", "b", "c")]
        for index in range(140):
            path = f.source_root / "a" / ("empty-%03d" % index)
            path.touch()
            f.manifest["files"].append({"relative_path": "a/" + path.name,
                                        "sha256": sha(b""), **core._identity(path.stat())})
        manifest_raw = raw(f.manifest)
        f.common["window_id"] = self.window
        f.common["canonical_manifest_sha256"] = sha(manifest_raw)
        for doc in (f.ready, f.dest, f.restore):
            doc["window_id"] = self.window
            doc["canonical_manifest_sha256"] = sha(manifest_raw)
        for item in f.restore["entries"]:
            item["native_chunk_proof"]["receipt"]["manifest_sha256"] = sha(manifest_raw)
        f.ready["source_files_unlinked"] = 0
        f.ready["status"] = "READY_SOURCE_KEEP"
        for index, src in enumerate(f.ready["entries"]):
            src["bridge_path"] = str(actual_directory / "files" /
                                     ("range-%04d.bin" % index))
            f.dest["entries"][index]["bridge_path"] = src["bridge_path"]
        native = "/home/shared/huangrulin/host174_storage_recovery/tls_v10/test-p9"
        archive = ("/root/share/mnt164/huangrulin/host174_storage_recovery/tls_v10/"
                   "test-p9/" + self.txid + ".partial/chunks")
        f.dest["native164_base"] = native
        for item in f.dest["entries"]:
            item["archived_chunk_path"] = (archive + "/" +
                                            sha(b"partial.bin") + ".%016d" % item["offset"])
        self.manifest_path = self.base / "TLS_V10_P9_PUBLIC_TARGET_TRANSACTION_MANIFEST.json"
        self.manifest_path.write_bytes(manifest_raw)
        self.native = native
        self.archive = archive
        self.source_repo = self.base / "source-git"
        self.target_repo = self.base / "target-git"
        self.source_repo.mkdir()
        self.target_repo.mkdir()
        self.ctx = ack.Context(self.source_repo, self.target_repo, "source-remote",
                               "target-remote", "hrl/ops-174-tls-v10-source-exec-v1",
                               "hrl/tls-v10-174new-target-exec-v1", f.source_root,
                               self.bridge_root, self.manifest_path, self.base,
                               production=False)
        self.make_evidence()

    def make_evidence(self):
        f = self.fixture
        f.dest["source_ready_git_commit"] = "1" * 40
        f.restore["source_ready_git_commit"] = "1" * 40
        ready_raw = raw(f.ready)
        f.dest["source_ready_sha256"] = sha(ready_raw)
        f.restore["source_ready_sha256"] = sha(ready_raw)
        dest_raw, restore_raw = raw(f.dest), raw(f.restore)
        receiving = {
            "window_id": self.window, "txid": self.txid,
            "selector_sha256": f.common["selector_sha256"],
            "canonical_manifest_sha256": sha(self.manifest_path.read_bytes()),
            "source_ready_git_commit": "1" * 40,
            "source_ready_sha256": sha(ready_raw),
            "target_window_git_commit": "c" * 40,
            "target_window_sha256": "d" * 64,
            "dest_receipt_sha256": sha(dest_raw),
            "restore_receipt_sha256": sha(restore_raw),
            "range_count": 2, "raw_bytes": 3000000,
            "source_originals": "SOURCE_KEEP", "source_files_deleted_by_target": 0,
            "bridge_payloads_retained": True,
            "full_group_certificate_created": False,
            "full_group_all141_native_tree_restored": False,
            "source_scientific_release_bytes": 0,
            "status": "B0004_DEST_AND_NATIVE_RANGE_RESTORE_VERIFIED_AWAIT_SOURCE_KEEP_ACK",
        }
        self.binding = ack.ExactWindow(
            self.window, self.txid, f.common["selector_sha256"],
            sha(self.manifest_path.read_bytes()), "1" * 40, sha(ready_raw),
            "c" * 40, "d" * 64, "2" * 40, sha(dest_raw), sha(restore_raw),
            sha(raw(receiving)), self.native, self.archive)
        self.git_map = {}
        names = ack._names(self.window)
        request = {
            "window_id": self.window, "txid": self.txid,
            "selector_sha256": f.common["selector_sha256"],
            "canonical_manifest_sha256": sha(self.manifest_path.read_bytes()),
            "target_root_native164": self.native,
            "group": "P9_PUBLIC", "source_originals": "SOURCE_KEEP",
            "range_count": 2, "raw_bytes": 3000000,
            "source_scientific_release_authorized_by_this_window": False,
            "ranges": [{"relative_path": entry["relative_path"],
                        "offset": entry["offset"], "length": entry["length"],
                        "original_sha256": entry["source_full_sha256"],
                        "bridge_path": entry["bridge_path"],
                        "source_identity": entry["source_identity"]}
                       for entry in f.ready["entries"]],
        }
        request_raw = raw(request)
        self.binding = ack.ExactWindow(**{**self.binding.__dict__,
                                         "target_window_sha256": sha(request_raw)})
        for doc in (f.ready, f.dest, f.restore):
            doc["target_window_sha256"] = sha(request_raw)
        # DEST/RESTORE bytes changed after the request SHA binding.
        f.dest["source_ready_sha256"] = sha(raw(f.ready))
        f.restore["source_ready_sha256"] = sha(raw(f.ready))
        receiving["target_window_sha256"] = sha(request_raw)
        receiving["source_ready_sha256"] = sha(raw(f.ready))
        receiving["dest_receipt_sha256"] = sha(raw(f.dest))
        receiving["restore_receipt_sha256"] = sha(raw(f.restore))
        self.binding = ack.ExactWindow(
            self.window, self.txid, f.common["selector_sha256"],
            sha(self.manifest_path.read_bytes()), "1" * 40, sha(raw(f.ready)),
            "c" * 40, sha(request_raw), "2" * 40, sha(raw(f.dest)),
            sha(raw(f.restore)), sha(raw(receiving)), self.native, self.archive)
        for key, content, prefix, commit in (
                ("request", request_raw, ack.TARGET_PREFIX, "c" * 40),
                ("ready", raw(f.ready), ack.SOURCE_PREFIX, "1" * 40),
                ("dest", raw(f.dest), ack.TARGET_PREFIX, "2" * 40),
                ("restore", raw(f.restore), ack.TARGET_PREFIX, "2" * 40),
                ("receiving", raw(receiving), ack.TARGET_PREFIX, "2" * 40)):
            (self.bridge_root / names[key]).write_bytes(content)
            self.git_map[(commit, prefix + names[key])] = content

    def _git_raw(self, repo, commit, relative):
        return self.git_map[(commit, relative)]

    def prepare(self):
        with patch.object(ack, "_remote_commits"), patch.object(
                ack, "_git_raw", side_effect=self._git_raw):
            return ack.prepare(self.binding, self.ctx)

    def test_prepare_and_publish_exact_partial_keep(self):
        path, digest = self.prepare()
        self.assertEqual(sha(path.read_bytes()), digest)
        item = json.loads(path.read_bytes())
        self.assertEqual(item["range_count"], 2)
        self.assertEqual(item["source_originals"], "SOURCE_KEEP")
        self.assertEqual(item["source_science_files_unlinked"], 0)
        self.assertIn("NOT_FULL_ORIGINAL_OR_GROUP", item["verified_scope"])
        self.assertTrue((self.fixture.source_root / "partial.bin").exists())
        self.git_map[("3" * 40, ack.SOURCE_PREFIX + path.name)] = path.read_bytes()
        with patch.object(ack, "_remote_commits"), patch.object(
                ack, "_git_raw", side_effect=self._git_raw):
            bridge_path, _ = ack.publish_bridge(self.binding, self.ctx, "3" * 40)
        self.assertEqual(path.read_bytes(), bridge_path.read_bytes())
        self.assertTrue((self.fixture.bridge_directory / "files" / "range-0000.bin").exists())

    def test_git_bridge_sha_mismatch_holds_without_ack(self):
        name = ack._names(self.window)["dest"]
        (self.bridge_root / name).write_bytes(b"{}")
        with self.assertRaises(ack.Hold):
            self.prepare()
        self.assertFalse((self.base / ack._names(self.window)["ack"]).exists())

    def test_forged_native_full_file_claim_holds(self):
        self.fixture.restore["entries"][0]["native_chunk_proof"]["receipt"][
            "original_full_file_restored"] = True
        self.make_evidence()
        with self.assertRaises(core.VerificationHold):
            self.prepare()

    def test_source_range_drift_holds(self):
        source = self.fixture.source_root / "partial.bin"
        with source.open("r+b") as out:
            out.write(b"Z")
        with self.assertRaises(core.VerificationHold):
            self.prepare()

    def test_duplicate_ack_no_clobber(self):
        path, raw_sha = self.prepare()
        with self.assertRaises(ack.Hold):
            self.prepare()
        self.assertEqual(sha(path.read_bytes()), raw_sha)

    def test_publish_requires_exact_git_ack(self):
        self.prepare()
        with patch.object(ack, "_remote_commits"), patch.object(
                ack, "_git_raw", return_value=b"forged"):
            with self.assertRaises(ack.Hold):
                ack.publish_bridge(self.binding, self.ctx, "3" * 40)
        self.assertFalse((self.bridge_root / ack._names(self.window)["ack"]).exists())

    def test_publish_rejects_changed_bridge_payload(self):
        path, _ = self.prepare()
        payload = self.fixture.bridge_directory / "files" / "range-0000.bin"
        with payload.open("r+b") as out:
            out.write(b"Z")
        self.git_map[("3" * 40, ack.SOURCE_PREFIX + path.name)] = path.read_bytes()
        with patch.object(ack, "_remote_commits"), patch.object(
                ack, "_git_raw", side_effect=self._git_raw):
            with self.assertRaises(core.VerificationHold):
                ack.publish_bridge(self.binding, self.ctx, "3" * 40)

    def test_wrong_window_is_rejected(self):
        bad = ack.ExactWindow(**{**self.binding.__dict__,
                                 "window_id": "TLS_V10_P9_PUBLIC_B0003"})
        with self.assertRaises(ack.Hold):
            ack.prepare(bad, self.ctx)

    def test_exact_request_range_mismatch_holds(self):
        name = ack._names(self.window)["request"]
        request = json.loads((self.bridge_root / name).read_bytes())
        request["ranges"][0]["offset"] = 1
        modified = raw(request)
        (self.bridge_root / name).write_bytes(modified)
        self.git_map[("c" * 40, ack.TARGET_PREFIX + name)] = modified
        self.binding = ack.ExactWindow(**{**self.binding.__dict__,
                                         "target_window_sha256": sha(modified)})
        with self.assertRaises(ack.Hold):
            self.prepare()

    def test_actual_local_bare_remote_ancestry_readback(self):
        repo = self.base / "git-fixture"
        bare = self.base / "git-origin.git"
        subprocess.run(("git", "init", "-q", "-b", "test-branch", str(repo)), check=True)
        subprocess.run(("git", "init", "-q", "--bare", str(bare)), check=True)
        subprocess.run(("git", "-C", str(repo), "config", "user.email", "test@example.invalid"), check=True)
        subprocess.run(("git", "-C", str(repo), "config", "user.name", "Test"), check=True)
        subprocess.run(("git", "-C", str(repo), "remote", "add", "origin", str(bare)), check=True)
        (repo / "receipt.json").write_text("{}\n")
        subprocess.run(("git", "-C", str(repo), "add", "receipt.json"), check=True)
        subprocess.run(("git", "-C", str(repo), "commit", "-qm", "receipt"), check=True)
        commit = subprocess.check_output(("git", "-C", str(repo), "rev-parse", "HEAD")).decode().strip()
        subprocess.run(("git", "-C", str(repo), "push", "-q", "origin", "test-branch"), check=True)
        ack._remote_commits(repo, "origin", "test-branch", (commit,))
        self.assertEqual(ack._git_raw(repo, commit, "receipt.json"), b"{}\n")
        (repo / "receipt.json").write_text('{"new":true}\n')
        subprocess.run(("git", "-C", str(repo), "commit", "-qam", "unpublished"), check=True)
        unpublished = subprocess.check_output(("git", "-C", str(repo), "rev-parse", "HEAD")).decode().strip()
        with self.assertRaises(ack.Hold):
            ack._remote_commits(repo, "origin", "test-branch", (unpublished,))


if __name__ == "__main__":
    unittest.main()
