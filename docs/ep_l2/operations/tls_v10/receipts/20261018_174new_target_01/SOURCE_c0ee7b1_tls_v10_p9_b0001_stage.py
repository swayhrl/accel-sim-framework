#!/usr/bin/env python3
"""One exact 144-byte P9_PUBLIC B0001 source stage; no source unlink."""

from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

import tls_v10_copy16_real_preflight as preflight
import tls_v10_copy_only20g_gate as old


HERE = Path(__file__).resolve().parent
PASS = HERE / "TLS_V10_COPY_ONLY_16G_GATE_PASS_B0001.json"
READY = HERE / "TLS_V10_P9_PUBLIC_B0001_SOURCE_READY_COPY16.json"
BRIDGE_READY = old.BRIDGE / READY.name
BRIDGE_PUBLICATION = old.BRIDGE / "TLS_V10_P9_PUBLIC_B0001_SOURCE_READY_COPY16_PUBLICATION.json"
LOCK = old.BRIDGE / ".TLS_V10_SOURCE_SENDER.lock"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def fsync_directory(path):
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
        fsync_directory(path.parent)
    return sha(raw)


def prepare():
    if READY.exists() or BRIDGE_READY.exists():
        raise RuntimeError("READY already exists; inspect instead of repeating stage")
    lockfd = os.open(LOCK, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        check = preflight.inspect()
        if check["decision"]["decision"] != "POLICY_ELIGIBLE_NOT_READY":
            raise RuntimeError("fresh gate HOLD: " + json.dumps(check["decision"]["reasons"]))
        if sha(PASS.read_bytes()) != "82409a8d6e14efc7eb66c1731dc5d6d05a7079d73bd5660bcb17f3987bffe724":
            raise RuntimeError("Git-readback source PASS drift")
        request = json.loads(preflight.TARGET_REQUEST.read_bytes())
        range_record = request["range"]
        dest = Path(range_record["bridge_payload_path"])
        if not str(dest).startswith(str(old.BRIDGE) + os.sep):
            raise RuntimeError("bridge path outside sole root")
        if dest.exists() or dest.parent.parent.exists():
            raise RuntimeError("staged directory preexists")
        rootfd = os.open(old.SOURCE_ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            dirfd = os.open("matrix-d10fe92", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=rootfd)
            try:
                fd = os.open(Path(preflight.FIRST_REL).name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=dirfd)
                try:
                    src_before = os.fstat(fd)
                    payload = os.read(fd, 145)
                    src_after = os.fstat(fd)
                finally:
                    os.close(fd)
            finally:
                os.close(dirfd)
        finally:
            os.close(rootfd)
        if not stat.S_ISREG(src_before.st_mode) or src_before != src_after or len(payload) != 144 or sha(payload) != preflight.FIRST_SHA:
            raise RuntimeError("first source identity/content changed")
        if (src_before.st_ino != check["first_source"]["inode"] or
                src_before.st_dev != check["first_source"]["dev"] or
                src_before.st_ctime_ns != check["first_source"]["ctime_ns"]):
            raise RuntimeError("source changed since fresh gate")
        dest.parent.parent.mkdir(mode=0o700)
        dest.parent.mkdir(mode=0o700)
        fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        try:
            with os.fdopen(fd, "wb") as out:
                out.write(payload)
                out.flush()
                os.fsync(out.fileno())
        finally:
            fsync_directory(dest.parent)
            fsync_directory(dest.parent.parent)
            fsync_directory(old.BRIDGE)
        staged = os.lstat(dest)
        if (not stat.S_ISREG(staged.st_mode) or staged.st_nlink != 1 or
                staged.st_size != 144 or sha(dest.read_bytes()) != preflight.FIRST_SHA or
                staged.st_blocks * 512 > 256 * old.MIB):
            raise RuntimeError("staged payload not exact")
        ws, share = os.statvfs("/workspace"), os.statvfs("/root/share")
        if (ws.f_bavail * ws.f_frsize < 16 * old.GIB + old.MIB or
                share.f_bavail * share.f_frsize < old.SHARE_FLOOR):
            raise RuntimeError("post-stage resource floor failed; payload retained for audit")
        ready = {
            "schema": "TLS_V10_P9_PUBLIC_B0001_OLD174_SOURCE_READY_COPY16_V1",
            "status": "READY_SOURCE_KEEP", "at_utc": datetime.now(timezone.utc).isoformat(),
            "policy_id": "TLS_V10_FROZEN_EXCLUSIVE_COPY_ONLY_16G_20261019",
            "source_gate_git_commit": "c2c40c6b0538d2f71bd81783bfa729ac54c8f174",
            "source_gate_sha256": sha(PASS.read_bytes()),
            "source_gate_fresh_at_stage": check,
            "target_request_sha256": sha(preflight.TARGET_REQUEST.read_bytes()),
            "window_id": old.WINDOW, "txid": old.TXID,
            "group": old.GROUP, "selector_sha256": old.SELECTOR,
            "canonical_manifest_sha256": old.MANIFEST_SHA256,
            "source_root": old.SOURCE_ROOT, "target_root_native164": old.TARGET_ROOT,
            "relative_path": preflight.FIRST_REL, "offset": 0, "length": 144,
            "source_full_sha256": preflight.FIRST_SHA,
            "bridge_payload_path": str(dest),
            "bridge_payload_identity": {"dev": staged.st_dev, "inode": staged.st_ino,
                                        "nlink": staged.st_nlink, "size": staged.st_size,
                                        "allocated": staged.st_blocks * 512,
                                        "sha256": sha(dest.read_bytes())},
            "source_file_identity": check["first_source"],
            "post_stage_workspace_f_bavail_bytes": ws.f_bavail * ws.f_frsize,
            "post_stage_share_f_bavail_bytes": share.f_bavail * share.f_frsize,
            "source_originals": "SOURCE_KEEP", "source_unlink_count": 0,
            "target_full_group_restore_claim": False,
        }
        digest = no_clobber_json(READY, ready)
        print(json.dumps({"ready_path": str(READY), "sha256": digest, "bridge_payload": str(dest),
                          "bridge_payload_sha256": preflight.FIRST_SHA}))
    finally:
        os.close(lockfd)


def publish_bridge(commit):
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise RuntimeError("source Git commit must be 40 lowercase hex chars")
    raw = READY.read_bytes()
    receipt = json.loads(raw)
    if receipt["source_originals"] != "SOURCE_KEEP" or receipt["source_unlink_count"] != 0:
        raise RuntimeError("source READY not COPY_ONLY")
    if sha(preflight.TARGET_REQUEST.read_bytes()) != receipt["target_request_sha256"]:
        raise RuntimeError("target request changed")
    payload = Path(receipt["bridge_payload_path"])
    if sha(payload.read_bytes()) != receipt["bridge_payload_identity"]["sha256"]:
        raise RuntimeError("payload drift")
    no_clobber_json(BRIDGE_READY, receipt)
    pub = {"schema": "TLS_V10_B0001_SOURCE_READY_GITHUB_BRIDGE_READBACK_V1",
           "at_utc": datetime.now(timezone.utc).isoformat(), "source_git_commit": commit,
           "source_repo": old.SOURCE_REPO, "source_branch": old.SOURCE_BRANCH,
           "source_ready_name": READY.name, "source_ready_sha256": sha(raw),
           "bridge_ready_path": str(BRIDGE_READY), "bridge_ready_sha256": sha(BRIDGE_READY.read_bytes()),
           "window_id": old.WINDOW, "txid": old.TXID,
           "source_originals": "SOURCE_KEEP"}
    no_clobber_json(BRIDGE_PUBLICATION, pub)
    print(json.dumps(pub, sort_keys=True))


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif len(sys.argv) == 3 and sys.argv[1] == "publish-bridge":
        publish_bridge(sys.argv[2])
    else:
        raise SystemExit("usage: tls_v10_p9_b0001_stage.py prepare | publish-bridge COMMIT")
