#!/usr/bin/env python3
"""Exact B0002 SOURCE_KEEP ACK; never deletes source or bridge files."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

import tls_v10_copy_only20g_gate as old
import tls_v10_p9_b0002_preflight as check
import tls_v10_p9_grouped_copy16_gate as grouped
import tls_v10_p9_grouped_source_range as sender
from tls_v10_p9_b0002_stage import no_clobber_json


HERE = Path(__file__).resolve().parent
TARGET_COMMIT = "eb92658fa38cdd4aa83a092ea41feda93fde684a"
TARGET_ROOT = "docs/ep_l2/operations/tls_v10/receipts/20261018_174new_target_01/"
DEST = "TLS_V10_P9_PUBLIC_B0002_DEST_VERIFIED.json"
RESTORE = "TLS_V10_P9_PUBLIC_B0002_RESTORE_VERIFIED.json"
RECEIVING = "TLS_V10_P9_PUBLIC_B0002_TARGET_RECEIVING_RECEIPT_COPY16.json"
EXPECTED = {
    DEST: "76b2ae157424d682e6fffd3118b74d4a1575e2a76f726d6e7a47f6fb5efe34d0",
    RESTORE: "d640613a0697efb9a41279bbac5e2d768f2b0d0b959be81a4e14ddaf8a813b03",
    RECEIVING: "73f859c7b9c5acc53a8f83feb33de0e73063be0ed90de6305e0180878942c8d9",
}
READY = HERE / "TLS_V10_P9_PUBLIC_B0002_SOURCE_READY_COPY16.json"
ACK = HERE / "TLS_V10_P9_PUBLIC_B0002_SOURCE_KEEP_ACK.json"
BRIDGE_ACK = old.BRIDGE / ACK.name
BRIDGE_PUBLICATION = old.BRIDGE / "TLS_V10_P9_PUBLIC_B0002_SOURCE_KEEP_ACK_PUBLICATION.json"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git_raw(commit, name):
    return subprocess.check_output(["git", "show", commit + ":" + name])


def _identity(info):
    return sender._fingerprint(info)


def inspect():
    if ACK.exists() or BRIDGE_ACK.exists():
        raise sender.Hold("B0002 ACK already exists; inspect instead of repeating")
    ready_raw = READY.read_bytes()
    ready_name = str(READY.relative_to(Path.cwd()))
    if (sha(ready_raw) != "ae2a0a44b48c685e5f2533ee24619893bd84145650a077893c0f9a70341f2529" or
            git_raw("2e3d391d9e3982e76c31ba521a708e6e3dbb8308", ready_name) != ready_raw or
            (old.BRIDGE / READY.name).read_bytes() != ready_raw):
        raise sender.Hold("Source READY Git/local/bridge drift")
    ready = json.loads(ready_raw)
    receipts = {}
    for name, expected in EXPECTED.items():
        raw = (old.BRIDGE / name).read_bytes()
        if sha(raw) != expected or git_raw(TARGET_COMMIT, TARGET_ROOT + name) != raw:
            raise sender.Hold("Target Git/bridge raw SHA drift: " + name)
        receipts[name] = json.loads(raw)
    dest, restore, receiving = receipts[DEST], receipts[RESTORE], receipts[RECEIVING]
    for r in (dest, restore, receiving):
        if (r["window_id"] != grouped.WINDOW or r["txid"] != old.TXID or
                r["selector_sha256"] != old.SELECTOR or
                r["canonical_manifest_sha256"] != old.MANIFEST_SHA256 or
                r["source_ready_git_commit"] != "2e3d391d9e3982e76c31ba521a708e6e3dbb8308" or
                r["source_ready_sha256"] != sha(ready_raw) or
                r["target_window_git_commit"] != grouped.TARGET_GIT_COMMIT or
                r["target_window_sha256"] != grouped.REQUEST_SHA256 or
                r["source_originals"] != "SOURCE_KEEP" or
                r["source_files_deleted_by_target"] != 0):
            raise sender.Hold("target receipt transaction/source binding mismatch")
    if (dest["status"] != "DEST_VERIFIED" or restore["status"] != "RESTORE_VERIFIED" or
            receiving["status"] != "B0002_DEST_AND_NATIVE_RANGE_RESTORE_VERIFIED_AWAIT_SOURCE_KEEP_ACK" or
            receiving["dest_receipt_sha256"] != EXPECTED[DEST] or
            receiving["restore_receipt_sha256"] != EXPECTED[RESTORE] or
            receiving["bridge_payloads_retained"] is not True or
            dest["genuine164_mount_verified"] is not True or
            restore["independent_actual_native_restore"] is not True or
            restore["numeric_metadata_verified_every_range"] is not True or
            dest["native164_base"] != old.TARGET_ROOT or
            any(r["proof_scope"] != "COLLECTION_OF_CHUNK_RANGES" or
                r["full_group_archived"] is not False or
                r["full_group_native_restored"] is not False or
                r["await_source_signed_SOURCE_KEEP_ACK"] is not True or
                r["range_count"] != 34 or r["raw_bytes"] != 7660873 or
                r["science_source_release_bytes"] != 0 for r in (dest, restore)) or
            receiving["full_group_certificate_created"] is not False or
            receiving["full_group_all141_native_tree_restored"] is not False):
        raise sender.Hold("target real164/native proof status or scope mismatch")
    for r in (dest, restore):
        if (r["source_gate_sha256"] != ready["source_gate_sha256"] or
                r["source_protocol_adoption_sha256"] != ready["source_protocol_adoption_sha256"]):
            raise sender.Hold("target source gate/adoption binding mismatch")
    if (not (len(ready["entries"]) == len(dest["entries"]) == len(restore["entries"])) or
            len(ready["entries"]) != 34 or
            receiving["range_count"] != 34 or receiving["raw_bytes"] != 7660873):
        raise sender.Hold("ordered range vector cardinality mismatch")
    manifest_raw = check.MANIFEST.read_bytes()
    if sha(manifest_raw) != old.MANIFEST_SHA256:
        raise sender.Hold("source canonical manifest changed")
    manifest = json.loads(manifest_raw)
    frozen = {row["relative_path"]: row for row in manifest["files"]}
    if len(frozen) != 141 or len(manifest["directories"]) != 4:
        raise sender.Hold("source group cardinality mismatch")
    for rel, row in frozen.items():
        s = os.lstat(Path(old.SOURCE_ROOT) / rel)
        want = {k: row[k] for k in
                ("dev", "inode", "nlink", "uid", "gid", "mode", "size",
                 "mtime_ns", "ctime_ns", "allocated")}
        if not stat.S_ISREG(s.st_mode) or _identity(s) != want:
            raise sender.Hold("frozen source metadata drift: " + rel)
    cleanup = []
    archived = []
    native = []
    for index, (src, dst, rst) in enumerate(zip(ready["entries"], dest["entries"], restore["entries"])):
        row = frozen[src["relative_path"]]
        source_want = {k: row[k] for k in
                       ("dev", "inode", "nlink", "uid", "gid", "mode", "size",
                        "mtime_ns", "ctime_ns", "allocated")}
        keys = ("relative_path", "offset", "length", "source_identity", "source_full_sha256",
                "chunk_sha256", "bridge_path", "bridge_identity")
        if (any(dst[k] != src[k] for k in keys) or
                any(rst[k] != src[k] for k in ("relative_path", "offset", "length", "chunk_sha256")) or
                src["source_identity"] != source_want or src["source_full_sha256"] != row["sha256"] or
                src["bridge_path"] != str(old.BRIDGE / (grouped.WINDOW + "_" + old.TXID[:12]) /
                                          "files" / ("range-%04d.bin" % index)) or
                dst["original_size"] != row["size"]):
            raise sender.Hold("source/dest/native ordered entry mismatch at " + str(index))
        current_sha = check._source_range_sha(Path(old.SOURCE_ROOT),
                                               dict(source_want, relative_path=src["relative_path"]),
                                               src["offset"], src["length"])
        if current_sha != src["chunk_sha256"]:
            raise sender.Hold("current source range SHA drift at " + str(index))
        path = Path(src["bridge_path"])
        s = os.lstat(path)
        archive_key = sha(src["relative_path"].encode()) + ".%016d" % src["offset"]
        expected_archive = ("/root/share/mnt164/huangrulin/host174_storage_recovery/tls_v10/" +
                            Path(old.TARGET_ROOT).name + "/" + old.TXID + ".partial/chunks/" +
                            archive_key)
        if (not stat.S_ISREG(s.st_mode) or _identity(s) != src["bridge_identity"] or
                sha(path.read_bytes()) != src["chunk_sha256"] or
                dst["archived_close_reopen_sha256"] != src["chunk_sha256"] or
                dst["archived_chunk_path"] != expected_archive):
            raise sender.Hold("bridge/raw/archive identity mismatch at " + str(index))
        proof = rst["native_chunk_proof"]["receipt"]
        expected_meta = {k: row[k] for k in ("uid", "gid", "mode", "mtime_ns")}
        if (proof["status"] != "RESTORE_VERIFIED" or proof["proof_scope"] != "CHUNK_RANGE_ONLY" or
                proof["txid"] != old.TXID or proof["manifest_sha256"] != old.MANIFEST_SHA256 or
                proof["relative_path"] != src["relative_path"] or
                proof["offset"] != src["offset"] or proof["length"] != src["length"] or
                proof["chunk_sha256"] != src["chunk_sha256"] or
                proof["original_sha256"] != row["sha256"] or proof["original_size"] != row["size"] or
                proof["numeric_metadata"] != expected_meta or
                proof["native_metadata_verified"] is not True or
                proof["original_full_file_restored"] is not False or
                proof["complete_group_restored"] is not False or
                proof["source_action"] != "SOURCE_KEEP" or
                proof["source_release_authorized"] is not False):
            raise sender.Hold("native proof/metadata/scope mismatch at " + str(index))
        cleanup.append({"path": str(path), **src["bridge_identity"],
                        "sha256": src["chunk_sha256"],
                        "owner": "174-new TARGET ONLY AFTER_GITHUB_SOURCE_ACK_READBACK"})
        archived.append(dst["archived_chunk_path"])
        native.append(rst["native_restore_receipt_path"])
    ws, share = os.statvfs("/workspace"), os.statvfs("/root/share")
    return {"schema": "TLS_V10_B0002_OLD174_SOURCE_KEEP_ACK_V1",
            "at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "SOURCE_KEEP_ACK_TARGET_MAY_CLEAN_EXACT_34_VERIFIED_BRIDGE_PAYLOADS",
            "policy_id": "TLS_V10_FROZEN_EXCLUSIVE_COPY_ONLY_16G_20261019",
            "window_id": grouped.WINDOW, "group": old.GROUP,
            "txid": old.TXID, "selector_sha256": old.SELECTOR,
            "canonical_manifest_sha256": old.MANIFEST_SHA256,
            "source_ready_git_commit": "2e3d391d9e3982e76c31ba521a708e6e3dbb8308",
            "source_ready_sha256": sha(ready_raw),
            "target_dest_restore_git_commit": TARGET_COMMIT,
            "target_dest_receipt_sha256": EXPECTED[DEST],
            "target_native_restore_receipt_sha256": EXPECTED[RESTORE],
            "target_receiving_receipt_sha256": EXPECTED[RECEIVING],
            "target_true164_native_root": old.TARGET_ROOT,
            "verified_scope": "34_CHUNK_RANGES_ONLY_NOT_FULL141_GROUP_CERTIFICATE",
            "range_count": 34, "raw_bytes": 7660873,
            "target_archive_chunk_paths": archived,
            "target_native_receipt_paths": native,
            "bridge_payload_exact_cleanup_permissions": cleanup,
            "source_all141_frozen_metadata_exact": True,
            "source_34_ranges_current_sha_refreshed": True,
            "source_originals": "SOURCE_KEEP",
            "source_science_files_unlinked": 0,
            "source_science_df_gain_bytes": 0,
            "workspace_f_bavail_bytes_at_ack": ws.f_bavail * ws.f_frsize,
            "share_f_bavail_bytes_at_ack": share.f_bavail * share.f_frsize,
            "next_window_requires_verified_bridge_cleanup": True}


def prepare():
    receipt = inspect()
    digest = no_clobber_json(ACK, receipt)
    print(json.dumps({"source_keep_ack": str(ACK), "sha256": digest,
                      "range_count": receipt["range_count"]}, sort_keys=True))


def publish_bridge(commit):
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise sender.Hold("invalid source commit")
    raw = ACK.read_bytes()
    if git_raw(commit, str(ACK.relative_to(Path.cwd()))) != raw:
        raise sender.Hold("ACK not exact Git readback")
    ack = json.loads(raw)
    if ack["source_originals"] != "SOURCE_KEEP" or ack["source_science_files_unlinked"] != 0:
        raise sender.Hold("not SOURCE_KEEP")
    for entry in ack["bridge_payload_exact_cleanup_permissions"]:
        p = Path(entry["path"])
        s = os.lstat(p)
        expected_identity = {k: entry[k] for k in
                             ("dev", "inode", "nlink", "uid", "gid", "mode", "size",
                              "mtime_ns", "ctime_ns", "allocated")}
        if _identity(s) != expected_identity or sha(p.read_bytes()) != entry["sha256"]:
            raise sender.Hold("bridge changed before ACK publication")
    no_clobber_json(BRIDGE_ACK, ack)
    no_clobber_json(BRIDGE_PUBLICATION, {
        "schema": "TLS_V10_B0002_SOURCE_KEEP_ACK_GITHUB_BRIDGE_READBACK_V1",
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "source_git_commit": commit, "source_branch": old.SOURCE_BRANCH,
        "target_dest_restore_git_commit": TARGET_COMMIT,
        "source_keep_ack_name": ACK.name, "source_keep_ack_sha256": sha(raw),
        "bridge_keep_ack_sha256": sha(BRIDGE_ACK.read_bytes()),
        "window_id": grouped.WINDOW, "txid": old.TXID,
        "range_count": ack["range_count"], "source_originals": "SOURCE_KEEP",
        "source_files_unlinked": 0})
    print(json.dumps({"ack_commit": commit, "ack_sha256": sha(raw),
                      "bridge_ack": str(BRIDGE_ACK)}, sort_keys=True))


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif len(sys.argv) == 3 and sys.argv[1] == "publish-bridge":
        publish_bridge(sys.argv[2])
    else:
        raise SystemExit("usage: tls_v10_p9_b0002_ack.py prepare | publish-bridge COMMIT")
