#!/usr/bin/env python3
"""Exact B0003 one-range source controller; COPY_ONLY, bounded streaming."""

from dataclasses import replace
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import tls_v10_copy_only16g_gate as copy16
import tls_v10_copy_only20g_gate as old
import tls_v10_copy16_real_preflight as prior
import tls_v10_p9_b0002_stage as previous
import tls_v10_p9_b0003_copy16_gate as gate
import tls_v10_p9_b0003_preflight as check
from tls_v10_p9_grouped_copy16_gate import GroupedInput
import tls_v10_p9_grouped_source_range as sender


HERE = Path(__file__).resolve().parent
PASS = HERE / "TLS_V10_P9_PUBLIC_B0003_SOURCE_GATE_PASS_COPY16.json"
READY = HERE / "TLS_V10_P9_PUBLIC_B0003_SOURCE_READY_COPY16.json"
ADOPTION = HERE / "TLS_V10_P9_PUBLIC_B0003_SOURCE_PROTOCOL_ADOPTION_COPY16.json"
TEST_RECEIPT = HERE / "TLS_V10_P9_PUBLIC_B0003_SOURCE_FIXTURE_QUALIFICATION.json"
BRIDGE_READY = old.BRIDGE / READY.name
BRIDGE_PUBLICATION = old.BRIDGE / "TLS_V10_P9_PUBLIC_B0003_SOURCE_READY_PUBLICATION_COPY16.json"
LOCK = old.BRIDGE / ".TLS_V10_SOURCE_SENDER.lock"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def stream_sha(path):
    digest = hashlib.sha256()
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        while True:
            block = os.read(fd, sender.BLOCK)
            if not block:
                break
            digest.update(block)
    finally:
        os.close(fd)
    return digest.hexdigest()


def prepare_gate():
    if PASS.exists() or READY.exists():
        raise sender.Hold("B0003 gate/READY exists; no duplicate")
    snap = check.inspect()
    if snap["decision"]["decision"] != "POLICY_ELIGIBLE_NOT_READY":
        raise sender.Hold("fresh B0003 gate HOLD: " + json.dumps(snap["decision"]["reasons"]))
    snap["schema"] = "TLS_V10_B0003_SOURCE_COPY_ONLY16G_GATE_PASS_V1"
    snap["status"] = "GATE_PASS_NOT_READY_NO_PAYLOAD_STAGED"
    snap["source_gate_code_sha256"] = sha((HERE / "tls_v10_p9_b0003_copy16_gate.py").read_bytes())
    snap["source_preflight_code_sha256"] = sha((HERE / "tls_v10_p9_b0003_preflight.py").read_bytes())
    snap["source_stage_primitive_sha256"] = sha((HERE / "tls_v10_p9_grouped_source_range.py").read_bytes())
    snap["source_controller_sha256"] = sha(Path(__file__).read_bytes())
    snap["source_protocol_adoption_sha256"] = sha(ADOPTION.read_bytes())
    snap["source_test_receipt_sha256"] = sha(TEST_RECEIPT.read_bytes())
    snap["source_authority_sha256"] = copy16.AUTHORITY_SHA256
    snap["source_user_approval_sha256"] = copy16.APPROVAL_SHA256
    digest = previous.no_clobber_json(PASS, snap)
    print(json.dumps({"gate_path": str(PASS), "sha256": digest, "status": snap["status"]}))


def _all_source_metadata_exact(manifest):
    for row in manifest["files"]:
        s = os.lstat(Path(old.SOURCE_ROOT) / row["relative_path"])
        want = {k: row[k] for k in
                ("dev", "inode", "nlink", "uid", "gid", "mode", "size",
                 "mtime_ns", "ctime_ns", "allocated")}
        if sender._fingerprint(s) != want:
            return False
    return len(manifest["files"]) == 141 and len(manifest["directories"]) == 4


def _post_stage(pre, manifest, entry, range_sha, physical_bytes):
    current_sha = check.previous._source_range_sha(Path(old.SOURCE_ROOT),
        dict(entry["source_identity"], relative_path=entry["relative_path"]),
        entry["offset"], entry["length"])
    hits, unknown, lane_pids, transfers = prior.physical_refs()
    registry = old.real_snapshot()["registry"]
    scripts = {name: sha(Path(name).read_bytes()) for name in prior.SCRIPT_SHA}
    scheduled_clear = scripts == prior.SCRIPT_SHA and all(
        old.SOURCE_ROOT not in Path(name).read_text() and
        "tls-cache-p9-public-v1" not in Path(name).read_text()
        for name in prior.SCRIPT_SHA)
    lane_closed, lane_sha = prior.lane_closure()
    ws, share = os.statvfs("/workspace"), os.statvfs("/root/share")
    request_exact = (sha(check.REQUEST.read_bytes()) == gate.REQUEST_SHA256 and
                     check.target_raw(check.REQUEST.name) == check.REQUEST.read_bytes())
    all_exact = _all_source_metadata_exact(manifest)
    b = old.GateInput(**pre["input"])
    b = replace(b, workspace_available_bytes=ws.f_bavail * ws.f_frsize,
                share_available_bytes=share.f_bavail * share.f_frsize,
                planned_overlay_write_bytes=old.MIB,
                planned_bridge_staged_bytes=0,
                copy_lease_authorized=lane_closed and not lane_pids and not transfers and
                                      registry["active_leases"] == 0,
                physical_scan_complete=not unknown,
                candidate_root_idle=not hits,
                scheduled_readers_clear=scheduled_clear,
                first_source_identity_ok=all_exact,
                first_source_sha_refreshed=current_sha == range_sha,
                target_request_present_and_exact=request_exact,
                sole_source_sender=not transfers)
    decision = gate.evaluate(GroupedInput(
        b, gate.TARGET_GIT_COMMIT, gate.PRIOR_CLEANUP_SHA256,
        copy16.APPROVAL_SHA256, 128 * old.MIB, 1,
        all_exact and current_sha == range_sha and request_exact,
        lane_closed, not lane_pids))
    if (decision["decision"] != "POLICY_ELIGIBLE_NOT_READY" or
            physical_bytes > 256 * old.MIB or
            share.f_bavail * share.f_frsize < old.SHARE_FLOOR):
        raise sender.Hold("B0003 post-stage gate HOLD, preserve exact staged evidence: " +
                          json.dumps(decision["reasons"]))
    return {"at_utc": datetime.now(timezone.utc).isoformat(),
            "workspace_available_bytes": ws.f_bavail * ws.f_frsize,
            "share_available_bytes": share.f_bavail * share.f_frsize,
            "lane_final_closure_receipt_sha256": lane_sha,
            "lane_current_registry": registry,
            "source_process_refs": hits, "unreadable_proc_pids": unknown,
            "lane_physical_pids": lane_pids, "other_transfer_pids": transfers,
            "scheduled_readers_clear": scheduled_clear,
            "all141_source_metadata_exact": all_exact,
            "source_range_sha256_after_stage": current_sha,
            "decision": decision}


def stage():
    if READY.exists() or BRIDGE_READY.exists():
        raise sender.Hold("B0003 READY exists; do not repeat stage")
    lockfd = os.open(LOCK, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        head = previous.current_branch_remote_exact()
        if subprocess.check_output(["git", "show", head + ":" +
                                    str(PASS.relative_to(Path.cwd()))]) != PASS.read_bytes():
            raise sender.Hold("B0003 PASS not exact GitHub-readback HEAD")
        pinned = json.loads(PASS.read_bytes())
        fresh = check.inspect()
        if (fresh["decision"]["decision"] != "POLICY_ELIGIBLE_NOT_READY" or
                fresh["target_request_sha256"] != pinned["target_request_sha256"] or
                fresh["current_range_sha256"] != pinned["current_range_sha256"] or
                sha(ADOPTION.read_bytes()) != pinned["source_protocol_adoption_sha256"] or
                sha(Path(__file__).read_bytes()) != pinned["source_controller_sha256"]):
            raise sender.Hold("B0003 fresh gate/source SHA/adoption drift")
        req = json.loads(check.REQUEST.read_bytes())
        manifest = json.loads(check.MANIFEST.read_bytes())
        entry = req["ranges"][0]
        row = next(v for v in manifest["files"] if v["relative_path"] == entry["relative_path"])
        identity = {k: row[k] for k in
                    ("dev", "inode", "nlink", "uid", "gid", "mode", "size",
                     "mtime_ns", "ctime_ns", "allocated")}
        directory = Path(req["bridge_root"])
        if directory.parent.exists() or directory.exists():
            raise sender.Hold("B0003 stage exists; no blind retry")
        directory.parent.mkdir(mode=0o700)
        directory.mkdir(mode=0o700)
        previous.sync_dir(old.BRIDGE)
        previous.sync_dir(directory.parent)
        limiter = sender.RateLimiter(old.MAX_RATE_BPS)
        staged = sender.stage_range(old.SOURCE_ROOT,
                                    dict(identity, relative_path=entry["relative_path"]),
                                    entry["offset"], entry["length"], directory, "range-0000.bin",
                                    existing_bridge_allocated_bytes=0, limiter=limiter)
        if staged["fresh_chunk_sha256"] != fresh["current_range_sha256"]:
            raise sender.Hold("B0003 fresh staged chunk/source mismatch; preserve evidence")
        previous.sync_dir(directory)
        physical = staged["bridge_identity"]["allocated"]
        post = _post_stage(fresh, manifest, entry, staged["fresh_chunk_sha256"], physical)
        ready = {"schema": "TLS_V10_OLD174_GROUPED_RAW_READY_V1",
                 "status": "READY_SOURCE_KEEP", "at_utc": datetime.now(timezone.utc).isoformat(),
                 "source_repo": old.SOURCE_REPO, "source_branch": old.SOURCE_BRANCH,
                 "source_frozen_commit": req["source_frozen_commit"],
                 "source_namespace": old.SOURCE_NAMESPACE, "source_dev": old.SOURCE_DEV,
                 "source_root": old.SOURCE_ROOT, "window_id": gate.WINDOW,
                 "group": old.GROUP, "txid": old.TXID, "selector_sha256": old.SELECTOR,
                 "canonical_manifest_sha256": old.MANIFEST_SHA256,
                 "target_window_git_commit": gate.TARGET_GIT_COMMIT,
                 "target_window_sha256": gate.REQUEST_SHA256,
                 "target_root_native164": old.TARGET_ROOT,
                 "prior_cleanup_sha256": gate.PRIOR_CLEANUP_SHA256,
                 "policy_id": copy16.POLICY_ID,
                 "source_gate_sha256": sha(PASS.read_bytes()),
                 "qualified_source_sender_code_sha256": sha((HERE / "tls_v10_p9_grouped_source_range.py").read_bytes()),
                 "qualified_source_controller_code_sha256": sha(Path(__file__).read_bytes()),
                 "source_test_receipt_sha256": pinned["source_test_receipt_sha256"],
                 "source_protocol_adoption_sha256": pinned["source_protocol_adoption_sha256"],
                 "gate_before_stage": fresh, "gate_after_stage": post,
                 "entries": [{"relative_path": entry["relative_path"],
                              "offset": entry["offset"], "length": entry["length"],
                              "source_identity": identity,
                              "source_full_sha256": entry["original_sha256"],
                              "chunk_sha256": staged["fresh_chunk_sha256"],
                              "bridge_path": staged["bridge_payload_path"],
                              "bridge_identity": staged["bridge_identity"]}],
                 "range_count": 1, "raw_bytes": entry["length"],
                 "bridge_payload_allocated_bytes": physical,
                 "source_originals": "SOURCE_KEEP", "source_files_unlinked": 0,
                 "complete_group_archived": False, "complete_group_native_restored": False}
        digest = previous.no_clobber_json(READY, ready)
        print(json.dumps({"ready_path": str(READY), "sha256": digest,
                          "raw_bytes": entry["length"], "physical_bridge_bytes": physical}))
    finally:
        os.close(lockfd)


def publish_bridge(commit):
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise sender.Hold("invalid source commit")
    raw = READY.read_bytes()
    if subprocess.check_output(["git", "show", commit + ":" +
                                str(READY.relative_to(Path.cwd()))]) != raw:
        raise sender.Hold("B0003 READY not Git-readback exact")
    ready = json.loads(raw)
    if (ready["target_window_sha256"] != sha(check.REQUEST.read_bytes()) or
            ready["source_originals"] != "SOURCE_KEEP" or ready["source_files_unlinked"] != 0):
        raise sender.Hold("B0003 READY/request drift")
    entry = ready["entries"][0]
    path = Path(entry["bridge_path"])
    if (sender._fingerprint(os.lstat(path)) != entry["bridge_identity"] or
            stream_sha(path) != entry["chunk_sha256"]):
        raise sender.Hold("B0003 bridge identity/streamed SHA changed")
    previous.no_clobber_json(BRIDGE_READY, ready)
    previous.no_clobber_json(BRIDGE_PUBLICATION, {
        "schema": "TLS_V10_B0003_SOURCE_READY_GITHUB_BRIDGE_READBACK_V1",
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "source_git_commit": commit, "source_repo": old.SOURCE_REPO,
        "source_branch": old.SOURCE_BRANCH, "window_id": gate.WINDOW,
        "txid": old.TXID, "source_ready_name": READY.name,
        "source_ready_sha256": sha(raw),
        "bridge_ready_sha256": sha(BRIDGE_READY.read_bytes()),
        "range_count": 1, "source_originals": "SOURCE_KEEP"})
    print(json.dumps({"source_ready_commit": commit, "ready_sha256": sha(raw),
                      "bridge_ready": str(BRIDGE_READY)}))


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare-gate"]:
        prepare_gate()
    elif sys.argv[1:] == ["stage"]:
        stage()
    elif len(sys.argv) == 3 and sys.argv[1] == "publish-bridge":
        publish_bridge(sys.argv[2])
    else:
        raise SystemExit("usage: tls_v10_p9_b0003_stage.py prepare-gate | stage | publish-bridge COMMIT")
