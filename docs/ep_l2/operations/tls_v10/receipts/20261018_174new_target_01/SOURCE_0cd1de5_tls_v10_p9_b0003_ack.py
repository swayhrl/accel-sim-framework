#!/usr/bin/env python3
"""Exact one-range B0003 SOURCE_KEEP ACK with bounded payload hashing."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

import tls_v10_copy_only20g_gate as old
import tls_v10_p9_b0002_stage as writer
import tls_v10_p9_b0003_copy16_gate as gate
import tls_v10_p9_b0003_preflight as preflight
import tls_v10_p9_b0003_stage as stage
import tls_v10_p9_grouped_source_range as sender


HERE = Path(__file__).resolve().parent
TARGET_COMMIT = "1e8ce34f38d1fa052d42047474ca85506c172ca9"
TARGET_BASE = "docs/ep_l2/operations/tls_v10/receipts/20261018_174new_target_01/"
DEST = "TLS_V10_P9_PUBLIC_B0003_DEST_VERIFIED.json"
RESTORE = "TLS_V10_P9_PUBLIC_B0003_RESTORE_VERIFIED.json"
RECEIVING = "TLS_V10_P9_PUBLIC_B0003_TARGET_RECEIVING_RECEIPT_COPY16.json"
EXPECTED_SHA = {
    DEST: "6c76c24fd3094aaad182f801152cde8eb671a8750225689d555bb604d0133de6",
    RESTORE: "21eed52a66d7447f78f05c03742de85ec454cd28a96249e1f113bf7214b627d7",
    RECEIVING: "081a4e042b696b5e13f557716b8af3274a1f3642d75dc293182cf8e188812633",
}
READY = HERE / "TLS_V10_P9_PUBLIC_B0003_SOURCE_READY_COPY16.json"
ACK = HERE / "TLS_V10_P9_PUBLIC_B0003_SOURCE_KEEP_ACK.json"
BRIDGE_ACK = old.BRIDGE / ACK.name
BRIDGE_PUBLICATION = old.BRIDGE / "TLS_V10_P9_PUBLIC_B0003_SOURCE_KEEP_ACK_PUBLICATION.json"
READY_COMMIT = "e5200732e55f17e248983231067f4aabc41a1742"
READY_SHA = "e5562cf2bd4f1d511b9fae92dd8c292f5d90f64da37475ba26c78a9980dd63af"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git_raw(commit, name):
    return subprocess.check_output(["git", "show", commit + ":" + name])


def inspect():
    if ACK.exists() or BRIDGE_ACK.exists():
        raise sender.Hold("B0003 ACK exists; inspect prior transaction")
    ready_raw = READY.read_bytes()
    if (sha(ready_raw) != READY_SHA or
            git_raw(READY_COMMIT, str(READY.relative_to(Path.cwd()))) != ready_raw or
            (old.BRIDGE / READY.name).read_bytes() != ready_raw):
        raise sender.Hold("B0003 READY Git/local/bridge drift")
    ready = json.loads(ready_raw)
    docs = {}
    for name, expected in EXPECTED_SHA.items():
        raw = (old.BRIDGE / name).read_bytes()
        if sha(raw) != expected or git_raw(TARGET_COMMIT, TARGET_BASE + name) != raw:
            raise sender.Hold("Target Git/bridge raw SHA drift: " + name)
        docs[name] = json.loads(raw)
    dest, restore, receiving = docs[DEST], docs[RESTORE], docs[RECEIVING]
    for r in (dest, restore, receiving):
        if (r["window_id"] != gate.WINDOW or r["txid"] != old.TXID or
                r["selector_sha256"] != old.SELECTOR or
                r["canonical_manifest_sha256"] != old.MANIFEST_SHA256 or
                r["source_ready_git_commit"] != READY_COMMIT or
                r["source_ready_sha256"] != READY_SHA or
                r["target_window_git_commit"] != gate.TARGET_GIT_COMMIT or
                r["target_window_sha256"] != gate.REQUEST_SHA256 or
                r["source_originals"] != "SOURCE_KEEP" or
                r["source_files_deleted_by_target"] != 0):
            raise sender.Hold("B0003 target transaction/source binding mismatch")
    if (dest["status"] != "DEST_VERIFIED" or restore["status"] != "RESTORE_VERIFIED" or
            receiving["status"] != "B0003_DEST_AND_NATIVE_RANGE_RESTORE_VERIFIED_AWAIT_SOURCE_KEEP_ACK" or
            receiving["dest_receipt_sha256"] != EXPECTED_SHA[DEST] or
            receiving["restore_receipt_sha256"] != EXPECTED_SHA[RESTORE] or
            receiving["bridge_payloads_retained"] is not True or
            dest["genuine164_mount_verified"] is not True or
            restore["independent_actual_native_restore"] is not True or
            restore["numeric_metadata_verified_every_range"] is not True or
            dest["native164_base"] != old.TARGET_ROOT or
            receiving["full_group_certificate_created"] is not False or
            receiving["full_group_all141_native_tree_restored"] is not False or
            any(r["proof_scope"] != "COLLECTION_OF_CHUNK_RANGES" or
                r["full_group_archived"] is not False or
                r["full_group_native_restored"] is not False or
                r["await_source_signed_SOURCE_KEEP_ACK"] is not True or
                r["range_count"] != 1 or r["raw_bytes"] != 128 * old.MIB or
                r["science_source_release_bytes"] != 0 or
                r["source_gate_sha256"] != ready["source_gate_sha256"] or
                r["source_protocol_adoption_sha256"] != ready["source_protocol_adoption_sha256"]
                for r in (dest, restore))):
        raise sender.Hold("B0003 real164/native proof status or scope mismatch")
    if (len(ready["entries"]) != 1 or len(dest["entries"]) != 1 or
            len(restore["entries"]) != 1 or receiving["range_count"] != 1 or
            receiving["raw_bytes"] != 128 * old.MIB):
        raise sender.Hold("B0003 range vector cardinality mismatch")
    src, dst, rst = ready["entries"][0], dest["entries"][0], restore["entries"][0]
    manifest_raw = preflight.MANIFEST.read_bytes()
    if sha(manifest_raw) != old.MANIFEST_SHA256:
        raise sender.Hold("source manifest SHA drift")
    manifest = json.loads(manifest_raw)
    if len(manifest["files"]) != 141 or len(manifest["directories"]) != 4:
        raise sender.Hold("P9 frozen cardinality mismatch")
    for row in manifest["files"]:
        s = os.lstat(Path(old.SOURCE_ROOT) / row["relative_path"])
        want = {k: row[k] for k in
                ("dev", "inode", "nlink", "uid", "gid", "mode", "size",
                 "mtime_ns", "ctime_ns", "allocated")}
        if not stat.S_ISREG(s.st_mode) or sender._fingerprint(s) != want:
            raise sender.Hold("P9 source metadata drift: " + row["relative_path"])
    row = next((v for v in manifest["files"] if v["relative_path"] == src["relative_path"]), None)
    if row is None:
        raise sender.Hold("B0003 range not frozen")
    source_want = {k: row[k] for k in
                   ("dev", "inode", "nlink", "uid", "gid", "mode", "size",
                    "mtime_ns", "ctime_ns", "allocated")}
    keys = ("relative_path", "offset", "length", "source_identity", "source_full_sha256",
            "chunk_sha256", "bridge_path", "bridge_identity")
    if (any(dst[k] != src[k] for k in keys) or
            any(rst[k] != src[k] for k in ("relative_path", "offset", "length", "chunk_sha256")) or
            src["source_identity"] != source_want or src["source_full_sha256"] != row["sha256"] or
            src["offset"] != 0 or src["length"] != 128 * old.MIB or
            src["length"] >= row["size"] or
            src["bridge_path"] != str(old.BRIDGE / (gate.WINDOW + "_" + old.TXID[:12]) /
                                      "files" / "range-0000.bin") or
            dst["original_size"] != row["size"]):
        raise sender.Hold("B0003 source/dest/native partial range mismatch")
    current_sha = preflight.previous._source_range_sha(Path(old.SOURCE_ROOT),
        dict(source_want, relative_path=src["relative_path"]), src["offset"], src["length"])
    if current_sha != src["chunk_sha256"]:
        raise sender.Hold("B0003 current source range SHA drift")
    payload = Path(src["bridge_path"])
    payload_stat = os.lstat(payload)
    archive_key = sha(src["relative_path"].encode()) + ".%016d" % src["offset"]
    archive_path = ("/root/share/mnt164/huangrulin/host174_storage_recovery/tls_v10/" +
                    Path(old.TARGET_ROOT).name + "/" + old.TXID + ".partial/chunks/" + archive_key)
    if (not stat.S_ISREG(payload_stat.st_mode) or
            sender._fingerprint(payload_stat) != src["bridge_identity"] or
            stage.stream_sha(payload) != src["chunk_sha256"] or
            dst["archived_chunk_path"] != archive_path or
            dst["archived_close_reopen_sha256"] != src["chunk_sha256"]):
        raise sender.Hold("B0003 bridge/archive streamed SHA or identity mismatch")
    proof = rst["native_chunk_proof"]["receipt"]
    numeric = {k: row[k] for k in ("uid", "gid", "mode", "mtime_ns")}
    if (proof["status"] != "RESTORE_VERIFIED" or proof["proof_scope"] != "CHUNK_RANGE_ONLY" or
            proof["txid"] != old.TXID or proof["manifest_sha256"] != old.MANIFEST_SHA256 or
            proof["relative_path"] != src["relative_path"] or
            proof["offset"] != src["offset"] or proof["length"] != src["length"] or
            proof["chunk_sha256"] != src["chunk_sha256"] or
            proof["original_sha256"] != row["sha256"] or proof["original_size"] != row["size"] or
            proof["numeric_metadata"] != numeric or proof["native_metadata_verified"] is not True or
            proof["original_full_file_restored"] is not False or
            proof["complete_group_restored"] is not False or
            proof["source_action"] != "SOURCE_KEEP" or
            proof["source_release_authorized"] is not False):
        raise sender.Hold("B0003 native partial proof/metadata mismatch")
    ws, share = os.statvfs("/workspace"), os.statvfs("/root/share")
    return {"schema": "TLS_V10_B0003_OLD174_SOURCE_KEEP_ACK_V1",
            "at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "SOURCE_KEEP_ACK_TARGET_MAY_CLEAN_EXACT_VERIFIED_BRIDGE_RANGE",
            "policy_id": "TLS_V10_FROZEN_EXCLUSIVE_COPY_ONLY_16G_20261019",
            "window_id": gate.WINDOW, "group": old.GROUP,
            "txid": old.TXID, "selector_sha256": old.SELECTOR,
            "canonical_manifest_sha256": old.MANIFEST_SHA256,
            "source_ready_git_commit": READY_COMMIT,
            "source_ready_sha256": READY_SHA,
            "target_dest_restore_git_commit": TARGET_COMMIT,
            "target_dest_receipt_sha256": EXPECTED_SHA[DEST],
            "target_native_restore_receipt_sha256": EXPECTED_SHA[RESTORE],
            "target_receiving_receipt_sha256": EXPECTED_SHA[RECEIVING],
            "target_true164_native_root": old.TARGET_ROOT,
            "target_archived_chunk_path": archive_path,
            "target_native_receipt_path": rst["native_restore_receipt_path"],
            "verified_scope": "ONE_128MiB_CHUNK_RANGE_ONLY_NOT_FULL_ORIGINAL_OR_GROUP",
            "source_frozen_files_metadata_rechecked": 141,
            "source_range_current_sha256": current_sha,
            "bridge_payload_exact_cleanup_permission": {
                "path": str(payload), **src["bridge_identity"],
                "sha256": src["chunk_sha256"],
                "owner": "174-new TARGET ONLY AFTER_GITHUB_SOURCE_ACK_READBACK"},
            "source_originals": "SOURCE_KEEP",
            "source_science_files_unlinked": 0,
            "source_science_df_gain_bytes": 0,
            "workspace_f_bavail_bytes_at_ack": ws.f_bavail * ws.f_frsize,
            "share_f_bavail_bytes_at_ack": share.f_bavail * share.f_frsize,
            "next_window_requires_verified_bridge_cleanup": True}


def prepare():
    receipt = inspect()
    digest = writer.no_clobber_json(ACK, receipt)
    print(json.dumps({"source_keep_ack": str(ACK), "sha256": digest}, sort_keys=True))


def publish_bridge(commit):
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise sender.Hold("invalid source commit")
    raw = ACK.read_bytes()
    if git_raw(commit, str(ACK.relative_to(Path.cwd()))) != raw:
        raise sender.Hold("B0003 ACK not Git-readback exact")
    ack = json.loads(raw)
    p = Path(ack["bridge_payload_exact_cleanup_permission"]["path"])
    identity = {k: ack["bridge_payload_exact_cleanup_permission"][k] for k in
                ("dev", "inode", "nlink", "uid", "gid", "mode", "size",
                 "mtime_ns", "ctime_ns", "allocated")}
    if (ack["source_originals"] != "SOURCE_KEEP" or ack["source_science_files_unlinked"] != 0 or
            sender._fingerprint(os.lstat(p)) != identity or
            stage.stream_sha(p) != ack["bridge_payload_exact_cleanup_permission"]["sha256"]):
        raise sender.Hold("B0003 bridge/source KEEP drift before ACK publication")
    writer.no_clobber_json(BRIDGE_ACK, ack)
    writer.no_clobber_json(BRIDGE_PUBLICATION, {
        "schema": "TLS_V10_B0003_SOURCE_KEEP_ACK_GITHUB_BRIDGE_READBACK_V1",
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "source_git_commit": commit, "source_branch": old.SOURCE_BRANCH,
        "target_dest_restore_git_commit": TARGET_COMMIT,
        "source_keep_ack_name": ACK.name, "source_keep_ack_sha256": sha(raw),
        "bridge_keep_ack_sha256": sha(BRIDGE_ACK.read_bytes()),
        "window_id": gate.WINDOW, "txid": old.TXID,
        "range_count": 1, "source_originals": "SOURCE_KEEP",
        "source_files_unlinked": 0})
    print(json.dumps({"ack_commit": commit, "ack_sha256": sha(raw),
                      "bridge_ack": str(BRIDGE_ACK)}))


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif len(sys.argv) == 3 and sys.argv[1] == "publish-bridge":
        publish_bridge(sys.argv[2])
    else:
        raise SystemExit("usage: tls_v10_p9_b0003_ack.py prepare | publish-bridge COMMIT")
