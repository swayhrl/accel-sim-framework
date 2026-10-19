#!/usr/bin/env python3
"""Exact one-window B0002 source controller; originals always SOURCE_KEEP."""

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
import tls_v10_p9_b0002_preflight as check
import tls_v10_p9_grouped_copy16_gate as grouped
import tls_v10_p9_grouped_source_range as sender


HERE = Path(__file__).resolve().parent
PASS = HERE / "TLS_V10_P9_PUBLIC_B0002_SOURCE_GATE_PASS_COPY16.json"
READY = HERE / "TLS_V10_P9_PUBLIC_B0002_SOURCE_READY_COPY16.json"
ADOPTION = HERE / "TLS_V10_P9_PUBLIC_B0002_SOURCE_PROTOCOL_ADOPTION_COPY16.json"
BRIDGE_READY = old.BRIDGE / READY.name
BRIDGE_PUBLICATION = old.BRIDGE / "TLS_V10_P9_PUBLIC_B0002_SOURCE_READY_PUBLICATION_COPY16.json"
LOCK = old.BRIDGE / ".TLS_V10_SOURCE_SENDER.lock"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def no_clobber_json(path, obj):
    raw = (json.dumps(obj, sort_keys=True, indent=2) + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(raw)
            out.flush()
            os.fsync(out.fileno())
    finally:
        sync_dir(path.parent)
    return sha(raw)


def current_branch_remote_exact():
    branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    remote = subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/" + old.SOURCE_BRANCH],
                                     text=True).split()[0]
    if branch != old.SOURCE_BRANCH or head != remote:
        raise sender.Hold("source production branch not GitHub readback exact")
    return head


def prepare_gate():
    if PASS.exists() or READY.exists():
        raise sender.Hold("B0002 PASS/READY exists; inspect instead of repeating")
    snapshot = check.inspect()
    if snapshot["decision"]["decision"] != "POLICY_ELIGIBLE_NOT_READY":
        raise sender.Hold("fresh B0002 resource/activity gate HOLD: " +
                          json.dumps(snapshot["decision"]["reasons"]))
    snapshot["schema"] = "TLS_V10_B0002_SOURCE_COPY_ONLY16G_GATE_PASS_V1"
    snapshot["status"] = "GATE_PASS_NOT_READY_NO_PAYLOAD_STAGED"
    snapshot["source_gate_code_sha256"] = sha((HERE / "tls_v10_p9_grouped_copy16_gate.py").read_bytes())
    snapshot["source_stage_primitive_sha256"] = sha((HERE / "tls_v10_p9_grouped_source_range.py").read_bytes())
    snapshot["source_controller_sha256"] = sha(Path(__file__).read_bytes())
    snapshot["target_protocol_sha256"] = "587163ce9e355e0a42603090cb43e7c6a9a661817d5b340eee58ac0589aef9d9"
    snapshot["source_authority_sha256"] = copy16.AUTHORITY_SHA256
    snapshot["source_user_approval_sha256"] = copy16.APPROVAL_SHA256
    snapshot["source_protocol_adoption_sha256"] = sha(ADOPTION.read_bytes())
    digest = no_clobber_json(PASS, snapshot)
    print(json.dumps({"gate_status": snapshot["status"], "gate_sha256": digest,
                      "path": str(PASS), "ranges": snapshot["range_count"]}))


def _post_stage(pre, expected_staged_bytes):
    ws, share = os.statvfs("/workspace"), os.statvfs("/root/share")
    hits, unknown, lane_pids, transfers = prior.physical_refs()
    registry = old.real_snapshot()["registry"]
    scripts = {name: sha(Path(name).read_bytes()) for name in prior.SCRIPT_SHA}
    scheduled_clear = scripts == prior.SCRIPT_SHA and all(
        old.SOURCE_ROOT not in Path(name).read_text() and
        "tls-cache-p9-public-v1" not in Path(name).read_text()
        for name in prior.SCRIPT_SHA)
    lane_closure, lane_sha = prior.lane_closure()
    b = old.GateInput(**pre["input"])
    b = replace(b, workspace_available_bytes=ws.f_bavail * ws.f_frsize,
                share_available_bytes=share.f_bavail * share.f_frsize,
                planned_overlay_write_bytes=old.MIB,
                planned_bridge_staged_bytes=0,
                copy_lease_authorized=lane_closure and not lane_pids and not transfers and
                                      registry["active_leases"] == 0,
                physical_scan_complete=not unknown,
                candidate_root_idle=not hits,
                scheduled_readers_clear=scheduled_clear,
                sole_source_sender=not transfers)
    verdict = grouped.evaluate(grouped.GroupedInput(
        b, grouped.TARGET_GIT_COMMIT, grouped.PRIOR_CLEANUP_SHA256,
        copy16.APPROVAL_SHA256, expected_staged_bytes,
        pre["range_count"], True, lane_closure, not lane_pids))
    if verdict["decision"] != "POLICY_ELIGIBLE_NOT_READY":
        raise sender.Hold("post-stage gate HOLD, preserve staged evidence: " +
                          json.dumps(verdict["reasons"]))
    return {"at_utc": datetime.now(timezone.utc).isoformat(),
            "workspace_available_bytes": ws.f_bavail * ws.f_frsize,
            "share_available_bytes": share.f_bavail * share.f_frsize,
            "lane_closure_sha256": lane_sha,
            "lane_registry": registry,
            "source_process_refs": hits,
            "unreadable_proc_pids": unknown,
            "lane_physical_pids": lane_pids,
            "other_transfer_pids": transfers,
            "scheduled_readers_clear": scheduled_clear,
            "decision": verdict}


def stage():
    if READY.exists() or BRIDGE_READY.exists():
        raise sender.Hold("B0002 READY already exists")
    lockfd = os.open(LOCK, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        head = current_branch_remote_exact()
        path_in_git = str(PASS.relative_to(Path.cwd()))
        if subprocess.check_output(["git", "show", head + ":" + path_in_git]) != PASS.read_bytes():
            raise sender.Hold("source PASS not exact GitHub-readback HEAD")
        pinned = json.loads(PASS.read_bytes())
        current = check.inspect()
        if (current["decision"]["decision"] != "POLICY_ELIGIBLE_NOT_READY" or
                current["target_request_sha256"] != pinned["target_request_sha256"] or
                current["current_range_sha"] != pinned["current_range_sha"] or
                current["source_grouped_gate_code_sha256"] != pinned["source_grouped_gate_code_sha256"] or
                current["source_grouped_range_code_sha256"] != pinned["source_grouped_range_code_sha256"]):
            raise sender.Hold("fresh B0002 gate or source SHA changed")
        request = json.loads(check.REQUEST.read_bytes())
        manifest = json.loads(check.MANIFEST.read_bytes())
        frozen = {v["relative_path"]: v for v in manifest["files"]}
        directory = Path(request["bridge_root"])
        if directory.parent.exists() or directory.exists():
            raise sender.Hold("B0002 stage already exists; do not blindly retry")
        directory.parent.mkdir(mode=0o700)
        directory.mkdir(mode=0o700)
        sync_dir(old.BRIDGE)
        sync_dir(directory.parent)
        limiter = sender.RateLimiter(old.MAX_RATE_BPS)
        vector = []
        allocated = 0
        for index, want in enumerate(request["ranges"]):
            row = frozen[want["relative_path"]]
            identity = {k: row[k] for k in
                        ("dev", "inode", "nlink", "uid", "gid", "mode", "size",
                         "mtime_ns", "ctime_ns", "allocated")}
            identity["relative_path"] = want["relative_path"]
            staged = sender.stage_range(old.SOURCE_ROOT, identity, want["offset"], want["length"],
                                        directory, "range-%04d.bin" % index,
                                        existing_bridge_allocated_bytes=allocated,
                                        limiter=limiter)
            if staged["fresh_chunk_sha256"] != current["current_range_sha"][index]["current_chunk_sha256"]:
                raise sender.Hold("fresh staged/source chunk mismatch; preserve staged evidence")
            allocated += staged["bridge_identity"]["allocated"]
            vector.append({"relative_path": want["relative_path"],
                           "offset": want["offset"], "length": want["length"],
                           "source_identity": want["source_identity"],
                           "source_full_sha256": want["original_sha256"],
                           "chunk_sha256": staged["fresh_chunk_sha256"],
                           "bridge_path": staged["bridge_payload_path"],
                           "bridge_identity": staged["bridge_identity"]})
        sync_dir(directory)
        post = _post_stage(current, request["raw_bytes"])
        if allocated > 256 * old.MIB or len(vector) != request["range_count"]:
            raise sender.Hold("post-stage count/physical cap mismatch")
        ready = {"schema": "TLS_V10_OLD174_GROUPED_RAW_READY_V1",
                 "status": "READY_SOURCE_KEEP", "at_utc": datetime.now(timezone.utc).isoformat(),
                 "source_repo": old.SOURCE_REPO, "source_branch": old.SOURCE_BRANCH,
                 "source_frozen_commit": request["source_frozen_commit"],
                 "source_namespace": old.SOURCE_NAMESPACE, "source_dev": old.SOURCE_DEV,
                 "source_root": old.SOURCE_ROOT, "window_id": grouped.WINDOW,
                 "group": old.GROUP, "txid": old.TXID, "selector_sha256": old.SELECTOR,
                 "canonical_manifest_sha256": old.MANIFEST_SHA256,
                 "target_window_git_commit": grouped.TARGET_GIT_COMMIT,
                 "target_window_sha256": grouped.REQUEST_SHA256,
                 "target_root_native164": old.TARGET_ROOT,
                 "prior_cleanup_sha256": grouped.PRIOR_CLEANUP_SHA256,
                 "policy_id": copy16.POLICY_ID,
                 "source_gate_sha256": sha(PASS.read_bytes()),
                 "qualified_source_sender_code_sha256": sha((HERE / "tls_v10_p9_grouped_source_range.py").read_bytes()),
                 "qualified_source_controller_code_sha256": sha(Path(__file__).read_bytes()),
                 "source_test_receipt_sha256": sha(check.QUAL.read_bytes()),
                 "source_protocol_adoption_sha256": pinned["source_protocol_adoption_sha256"],
                 "gate_before_stage": current, "gate_after_stage": post,
                 "entries": vector, "range_count": len(vector),
                 "raw_bytes": request["raw_bytes"],
                 "bridge_payload_allocated_bytes": allocated,
                 "source_originals": "SOURCE_KEEP", "source_files_unlinked": 0,
                 "complete_group_archived": False, "complete_group_native_restored": False}
        digest = no_clobber_json(READY, ready)
        print(json.dumps({"ready_path": str(READY), "sha256": digest,
                          "ranges": len(vector), "raw_bytes": request["raw_bytes"],
                          "bridge_allocated_bytes": allocated}))
    finally:
        os.close(lockfd)


def publish_bridge(commit):
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise sender.Hold("invalid source commit")
    raw = READY.read_bytes()
    if subprocess.check_output(["git", "show", commit + ":" +
                                str(READY.relative_to(Path.cwd()))]) != raw:
        raise sender.Hold("READY not exact Git readback")
    request = json.loads(check.REQUEST.read_bytes())
    receipt = json.loads(raw)
    if (receipt["target_window_sha256"] != sha(check.REQUEST.read_bytes()) or
            receipt["source_originals"] != "SOURCE_KEEP" or
            receipt["source_files_unlinked"] != 0):
        raise sender.Hold("READY/request changed")
    for entry in receipt["entries"]:
        p = Path(entry["bridge_path"])
        if (sender._fingerprint(os.lstat(p)) != entry["bridge_identity"] or
                sha(p.read_bytes()) != entry["chunk_sha256"]):
            raise sender.Hold("bridge payload changed before publish")
    no_clobber_json(BRIDGE_READY, receipt)
    no_clobber_json(BRIDGE_PUBLICATION, {
        "schema": "TLS_V10_B0002_SOURCE_READY_GITHUB_BRIDGE_READBACK_V1",
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "source_git_commit": commit, "source_repo": old.SOURCE_REPO,
        "source_branch": old.SOURCE_BRANCH, "window_id": grouped.WINDOW,
        "txid": old.TXID, "source_ready_name": READY.name,
        "source_ready_sha256": sha(raw),
        "bridge_ready_sha256": sha(BRIDGE_READY.read_bytes()),
        "range_count": request["range_count"], "source_originals": "SOURCE_KEEP"})
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
        raise SystemExit("usage: tls_v10_p9_b0002_stage.py prepare-gate | stage | publish-bridge COMMIT")
