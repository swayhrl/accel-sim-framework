#!/usr/bin/env python3
"""Source-only B0001 SOURCE_KEEP ACK after exact target Git/native proof.

Never unlinks a source or bridge file; target alone performs exact bridge
cleanup after the Git-backed ACK has been read back.
"""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

import tls_v10_copy16_real_preflight as preflight
import tls_v10_copy_only20g_gate as old
from tls_v10_p9_b0001_stage import no_clobber_json


HERE = Path(__file__).resolve().parent
TARGET_COMMIT = "97b1d4f15e8f79e5dae3c6a253ef5f65029c25ee"
TARGET_RECEIPT_ROOT = "docs/ep_l2/operations/tls_v10/receipts/20261018_174new_target_01/"
DEST_NAME = "TLS_V10_P9_PUBLIC_B0001_DEST_VERIFIED.json"
RESTORE_NAME = "TLS_V10_P9_PUBLIC_B0001_RESTORE_VERIFIED.json"
TARGET_STATUS_NAME = "TLS_V10_P9_PUBLIC_B0001_TARGET_RECEIVING_RECEIPT_COPY16.json"
EXPECTED_SHA = {
    DEST_NAME: "a1c33a96ea290887837cd1fab60bd78fef178d7c15adc2bbc6f09714aa402b6b",
    RESTORE_NAME: "12396266cb345a87abf08b0c68e6428facb4cea861345bddc50b13cda1c79456",
    TARGET_STATUS_NAME: "07cf08cbe295016c334ac8574d1601b564307684c5491c8c731dafe2da6e9550",
}
SOURCE_READY = HERE / "TLS_V10_P9_PUBLIC_B0001_SOURCE_READY_COPY16.json"
ACK = HERE / "TLS_V10_P9_PUBLIC_B0001_SOURCE_KEEP_ACK.json"
BRIDGE_ACK = old.BRIDGE / ACK.name
BRIDGE_PUBLICATION = old.BRIDGE / "TLS_V10_P9_PUBLIC_B0001_SOURCE_KEEP_ACK_PUBLICATION.json"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def remote_raw(name):
    api = "repos/swayhrl/accel-sim-framework/contents/" + TARGET_RECEIPT_ROOT + name + "?ref=" + TARGET_COMMIT
    encoded = subprocess.check_output(["gh", "api", api, "--jq", ".content"])
    import base64
    return base64.b64decode(encoded)


def inspect():
    if ACK.exists() or BRIDGE_ACK.exists():
        raise RuntimeError("ACK exists; inspect prior transaction rather than duplicate")
    ready_raw = SOURCE_READY.read_bytes()
    ready = json.loads(ready_raw)
    if sha(ready_raw) != "ad665c055ad2210bab1df5e9ead075d0fec6344bfa4414db6f0dbe7263101575":
        raise RuntimeError("source READY drift")
    receipts = {}
    for name, expected in EXPECTED_SHA.items():
        raw = (old.BRIDGE / name).read_bytes()
        if sha(raw) != expected or sha(remote_raw(name)) != expected:
            raise RuntimeError("bridge/target-Git raw readback mismatch: " + name)
        receipts[name] = json.loads(raw)
    dest, restore, target = (receipts[DEST_NAME], receipts[RESTORE_NAME], receipts[TARGET_STATUS_NAME])
    common = (dest, restore, target)
    if any(v["window_id"] != old.WINDOW or v["txid"] != old.TXID or
           v["selector_sha256"] != old.SELECTOR for v in common):
        raise RuntimeError("target receipt transaction mismatch")
    if any(v["source_ready_sha256"] != sha(ready_raw) or
           v["source_ready_git_commit"] != "e6199c059b52d8ad08eed90c6f0438e42250b431"
           for v in common):
        raise RuntimeError("target did not cite exact source READY")
    if (dest["canonical_manifest_sha256"] != old.MANIFEST_SHA256 or
            restore["canonical_manifest_sha256"] != old.MANIFEST_SHA256 or
            dest["status"] != "DEST_VERIFIED" or restore["status"] != "RESTORE_VERIFIED" or
            target["status"] != "DEST_AND_NATIVE_RANGE_RESTORE_VERIFIED_AWAIT_SOURCE_KEEP_ACK"):
        raise RuntimeError("target proof status/manifest mismatch")
    if (not dest["genuine164_mount_verified"] or not restore["independent_actual_native_restore"] or
            dest["archived_close_reopen_sha256"] != preflight.FIRST_SHA or
            restore["native_chunk_proof"]["receipt"]["chunk_sha256"] != preflight.FIRST_SHA or
            restore["native_chunk_proof"]["receipt"]["native_metadata_verified"] is not True or
            dest["native164_base"] != old.TARGET_ROOT or
            dest["archived_chunk_path"] != json.loads(preflight.TARGET_REQUEST.read_bytes())["target_expected_NAS_chunk"] or
            target["target_dest_receipt_sha256"] != EXPECTED_SHA[DEST_NAME] or
            target["target_native_receipt_sha256"] != EXPECTED_SHA[RESTORE_NAME]):
        raise RuntimeError("real164/native/range proof mismatch")
    first = next(v for v in json.loads((HERE / "TLS_V10_P9_PUBLIC_TARGET_TRANSACTION_MANIFEST.json").read_bytes())["files"]
                 if v["relative_path"] == preflight.FIRST_REL)
    restored_meta = restore["native_chunk_proof"]["receipt"]["numeric_metadata"]
    if (restored_meta != {"uid": first["uid"], "gid": first["gid"],
                          "mode": first["mode"], "mtime_ns": first["mtime_ns"]} or
            restore["native_chunk_proof"]["receipt"]["original_full_file_restored"] is not False or
            restore["native_chunk_proof"]["receipt"]["complete_group_restored"] is not False):
        raise RuntimeError("native metadata or proof scope mismatch")
    if (dest["proof_scope"] != "CHUNK_RANGE_ONLY" or restore["proof_scope"] != "CHUNK_RANGE_ONLY" or
            dest["full_group_native_restored"] or restore["full_group_native_restored"] or
            target["full_group_native_restored_files"] != 0 or
            any(v["source_originals"] != "SOURCE_KEEP" for v in common)):
        raise RuntimeError("first range incorrectly presented as full-group proof")
    if (dest["source_files_deleted_by_target"] != 0 or
            restore["source_files_deleted_by_target"] != 0 or
            not dest["await_source_signed_SOURCE_KEEP_ACK"] or
            not restore["await_source_signed_SOURCE_KEEP_ACK"]):
        raise RuntimeError("target source/ACK status mismatch")
    exact_source, source_entry = preflight.first_source()
    if not exact_source or source_entry != ready["source_file_identity"]:
        raise RuntimeError("original source identity/content changed")
    payload = Path(ready["bridge_payload_path"])
    identity = os.lstat(payload)
    pinned = ready["bridge_payload_identity"]
    if (not stat.S_ISREG(identity.st_mode) or identity.st_dev != pinned["dev"] or
            identity.st_ino != pinned["inode"] or identity.st_nlink != pinned["nlink"] or
            identity.st_size != pinned["size"] or identity.st_blocks * 512 != pinned["allocated"] or
            sha(payload.read_bytes()) != pinned["sha256"] or
            dest["bridge_identity"]["inode"] != identity.st_ino or
            dest["bridge_identity"]["dev"] != identity.st_dev):
        raise RuntimeError("bridge payload changed or target cited wrong inode")
    ws, share = os.statvfs("/workspace"), os.statvfs("/root/share")
    return {
        "schema": "TLS_V10_P9_PUBLIC_B0001_OLD174_SOURCE_KEEP_ACK_COPY16_V1",
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "SOURCE_KEEP_ACK_TARGET_MAY_CLEAN_EXACT_VERIFIED_BRIDGE_PAYLOAD",
        "policy_id": "TLS_V10_FROZEN_EXCLUSIVE_COPY_ONLY_16G_20261019",
        "window_id": old.WINDOW, "group": old.GROUP, "txid": old.TXID,
        "selector_sha256": old.SELECTOR, "canonical_manifest_sha256": old.MANIFEST_SHA256,
        "source_ready_git_commit": "e6199c059b52d8ad08eed90c6f0438e42250b431",
        "source_ready_sha256": sha(ready_raw),
        "target_dest_restore_git_commit": TARGET_COMMIT,
        "target_dest_receipt_sha256": EXPECTED_SHA[DEST_NAME],
        "target_native_restore_receipt_sha256": EXPECTED_SHA[RESTORE_NAME],
        "target_receiving_receipt_sha256": EXPECTED_SHA[TARGET_STATUS_NAME],
        "target_true164_native_root": old.TARGET_ROOT,
        "target_archived_chunk_path": dest["archived_chunk_path"],
        "target_native_chunk_receipt_path": restore["native_restore_receipt_path"],
        "verified_scope": "144_BYTE_CHUNK_RANGE_ONLY_NOT_FULL_FILE_GROUP_CERTIFICATE",
        "source_original_path": str(Path(old.SOURCE_ROOT) / preflight.FIRST_REL),
        "source_original_identity_and_sha_refreshed": source_entry,
        "bridge_payload_exact_cleanup_permission": {
            "path": str(payload), "dev": identity.st_dev, "inode": identity.st_ino,
            "nlink": identity.st_nlink, "size": identity.st_size,
            "allocated": identity.st_blocks * 512, "sha256": pinned["sha256"],
            "owner": "174-new TARGET ONLY AFTER_GITHUB_SOURCE_ACK_READBACK",
        },
        "source_originals": "SOURCE_KEEP",
        "source_science_files_unlinked": 0,
        "source_science_df_gain_bytes": 0,
        "workspace_f_bavail_bytes_at_ack": ws.f_bavail * ws.f_frsize,
        "share_f_bavail_bytes_at_ack": share.f_bavail * share.f_frsize,
        "next_window_requires_verified_bridge_cleanup": True,
    }


def prepare():
    receipt = inspect()
    digest = no_clobber_json(ACK, receipt)
    print(json.dumps({"source_keep_ack": str(ACK), "sha256": digest,
                      "target_commit": TARGET_COMMIT}, sort_keys=True))


def publish_bridge(commit):
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise RuntimeError("invalid source commit")
    raw = ACK.read_bytes()
    ack = json.loads(raw)
    if ack["source_originals"] != "SOURCE_KEEP" or ack["source_science_files_unlinked"] != 0:
        raise RuntimeError("not a source KEEP ACK")
    if sha(Path(ack["bridge_payload_exact_cleanup_permission"]["path"]).read_bytes()) != preflight.FIRST_SHA:
        raise RuntimeError("bridge payload drift before ACK publication")
    no_clobber_json(BRIDGE_ACK, ack)
    pub = {"schema": "TLS_V10_P9_PUBLIC_B0001_SOURCE_KEEP_ACK_GITHUB_BRIDGE_READBACK_V1",
           "at_utc": datetime.now(timezone.utc).isoformat(),
           "source_git_commit": commit, "source_branch": old.SOURCE_BRANCH,
           "target_dest_restore_git_commit": TARGET_COMMIT,
           "source_keep_ack_name": ACK.name, "source_keep_ack_sha256": sha(raw),
           "bridge_keep_ack_sha256": sha(BRIDGE_ACK.read_bytes()),
           "window_id": old.WINDOW, "txid": old.TXID,
           "source_originals": "SOURCE_KEEP", "source_files_unlinked": 0}
    no_clobber_json(BRIDGE_PUBLICATION, pub)
    print(json.dumps(pub, sort_keys=True))


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif len(sys.argv) == 3 and sys.argv[1] == "publish-bridge":
        publish_bridge(sys.argv[2])
    else:
        raise SystemExit("usage: tls_v10_p9_b0001_ack.py prepare | publish-bridge COMMIT")
