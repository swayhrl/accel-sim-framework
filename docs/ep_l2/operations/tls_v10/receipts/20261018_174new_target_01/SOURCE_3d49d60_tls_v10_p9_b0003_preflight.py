#!/usr/bin/env python3
"""Read-only old174 exact B0003 admission; streams only the requested range."""

from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

import tls_v10_copy_only16g_gate as copy16
import tls_v10_copy_only20g_gate as old
import tls_v10_copy16_real_preflight as prior
import tls_v10_p9_b0002_preflight as previous
import tls_v10_p9_b0003_copy16_gate as gate
from tls_v10_p9_grouped_copy16_gate import GroupedInput
import tls_v10_p9_grouped_source_range as sender


HERE = Path(__file__).resolve().parent
REQUEST = old.BRIDGE / "TLS_V10_P9_PUBLIC_B0003_TARGET_SOLE_WINDOW_REQUEST_COPY16.json"
MANIFEST = HERE / "TLS_V10_P9_PUBLIC_TARGET_TRANSACTION_MANIFEST.json"
PLAN = old.BRIDGE / "TLS_V10_P9_PUBLIC_INACTIVE_BATCHING_PROPOSAL_AFTER_B0001.json"
TARGET_BASE = "docs/ep_l2/operations/tls_v10/receipts/20261018_174new_target_01/"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def target_raw(name):
    return subprocess.check_output(["git", "show", gate.TARGET_GIT_COMMIT + ":" + TARGET_BASE + name])


def inspect():
    problems = []
    req_raw, manifest_raw, plan_raw = REQUEST.read_bytes(), MANIFEST.read_bytes(), PLAN.read_bytes()
    req, manifest, plan = json.loads(req_raw), json.loads(manifest_raw), json.loads(plan_raw)
    exact_req = (sha(req_raw) == gate.REQUEST_SHA256 and
                 target_raw(REQUEST.name) == req_raw and
                 req["schema"] == "TLS_V10_TARGET_GROUPED_RAW_WINDOW_V1" and
                 req["window_id"] == gate.WINDOW and req["group"] == old.GROUP and
                 req["txid"] == old.TXID and req["selector_sha256"] == old.SELECTOR and
                 req["canonical_manifest_sha256"] == old.MANIFEST_SHA256 and
                 req["source_root"] == old.SOURCE_ROOT and
                 req["target_root_native164"] == old.TARGET_ROOT and
                 req["prior_window"] == "TLS_V10_P9_PUBLIC_B0002" and
                 req["prior_window_cleanup_commit"] == "9a70eab40a1ba4635510bd5fd6ef719dfd75559f" and
                 req["prior_window_cleanup_sha256"] == gate.PRIOR_CLEANUP_SHA256 and
                 req["plan_sha256"] == sha(plan_raw) and req["plan_batch_index"] == 2 and
                 req["source_originals"] == "SOURCE_KEEP" and
                 req["source_scientific_release_authorized_by_this_window"] is False and
                 req["copy_ready"] is False and
                 sha(manifest_raw) == old.MANIFEST_SHA256)
    if not exact_req:
        problems.append("TARGET_GIT_BRIDGE_REQUEST_OR_FROZEN_BINDING_MISMATCH")
    bridge_dir = old.BRIDGE / (gate.WINDOW + "_" + old.TXID[:12]) / "files"
    rows = req["ranges"]
    if (req["bridge_root"] != str(bridge_dir) or bridge_dir.parent.exists() or
            len(rows) != req["range_count"] or req["range_count"] != 1 or
            req["raw_bytes"] != 128 * old.MIB or
            plan["batches"][2]["entries"] != [{k: r[k] for k in
                     ("relative_path", "offset", "length", "original_size", "original_sha256")}
                     for r in rows]):
        problems.append("EXACT_B0003_PLAN_OR_STAGE_MISMATCH")
    root = Path(old.SOURCE_ROOT)
    if root.resolve(strict=True) != root:
        problems.append("SOURCE_ROOT_SYMLINK")
    frozen = {v["relative_path"]: v for v in manifest["files"]}
    all_metadata_exact = len(frozen) == 141 and len(manifest["directories"]) == 4
    for rel, row in frozen.items():
        p = root / rel
        try:
            s = os.lstat(p)
            want = {k: row[k] for k in
                    ("dev", "inode", "nlink", "uid", "gid", "mode", "size",
                     "mtime_ns", "ctime_ns", "allocated")}
            if not stat.S_ISREG(s.st_mode) or sender._fingerprint(s) != want:
                all_metadata_exact = False
        except OSError:
            all_metadata_exact = False
    if not all_metadata_exact:
        problems.append("ALL141_FROZEN_METADATA_DRIFT")
    chunk_sha = None
    r = rows[0]
    row = frozen.get(r["relative_path"])
    if row is None:
        problems.append("RANGE_NOT_IN_FROZEN_MANIFEST")
    else:
        want = {k: row[k] for k in
                ("dev", "inode", "nlink", "uid", "gid", "mode", "size",
                 "mtime_ns", "ctime_ns", "allocated")}
        if (r["source_identity"] != want or r["source_path"] != str(root / r["relative_path"]) or
                r["bridge_path"] != str(bridge_dir / "range-0000.bin") or
                r["original_size"] != row["size"] or r["original_sha256"] != row["sha256"] or
                type(r["offset"]) is not int or r["offset"] != 0 or
                type(r["length"]) is not int or r["length"] != 128 * old.MIB or
                r["length"] >= row["size"]):
            problems.append("PARTIAL_RANGE_IDENTITY_OR_BOUND_MISMATCH")
        else:
            chunk_sha = previous._source_range_sha(root, dict(want, relative_path=r["relative_path"]),
                                                    r["offset"], r["length"])
    snap = old.real_snapshot()
    hits, unknown, lane_pids, transfer_pids = prior.physical_refs()
    scripts = {name: sha(Path(name).read_bytes()) for name in prior.SCRIPT_SHA}
    scheduled_clear = scripts == prior.SCRIPT_SHA and all(
        old.SOURCE_ROOT not in Path(name).read_text() and
        "tls-cache-p9-public-v1" not in Path(name).read_text() for name in prior.SCRIPT_SHA)
    try:
        lane_closed, lane_sha = prior.lane_closure()
    except (OSError, ValueError, subprocess.CalledProcessError):
        lane_closed, lane_sha = False, None
    target_meta = json.loads(target_raw("TLS_V10_P9_PUBLIC_B0003_TARGET_METADATA_PREFLIGHT_COPY16.json"))
    target_idle = (target_meta["window_id"] == gate.WINDOW and
                   target_meta["prior_B0002_closed"] is True and
                   target_meta["bridge_payloads_absent"] is True and
                   target_meta["receiver_idle"] is True and
                   target_meta["next_stage_not_created_by_target"] is True)
    # Truthful physical projection: full 128MiB payload plus 1MiB control and
    # filesystem directory slack; old overlay control remains bounded to 1MiB.
    projected_share = 128 * old.MIB + old.MIB
    b = old.GateInput(**snap["input"])
    b = replace(b, policy_id=copy16.POLICY_ID,
                amendment_sha256=copy16.AUTHORITY_SHA256,
                window_id=gate.WINDOW, target_request_sha256=gate.REQUEST_SHA256,
                planned_overlay_write_bytes=old.MIB,
                planned_bridge_staged_bytes=projected_share,
                planned_rate_bytes_per_second=old.MAX_RATE_BPS,
                copy_lease_authorized=lane_closed and not lane_pids and not transfer_pids and
                                      snap["registry"]["active_leases"] == 0,
                physical_scan_complete=not unknown,
                candidate_root_idle=not hits,
                scheduled_readers_clear=scheduled_clear,
                first_source_identity_ok=all_metadata_exact,
                first_source_sha_refreshed=chunk_sha is not None,
                target_request_present_and_exact=exact_req,
                sole_source_sender=not transfer_pids,
                sole_target_receiver=target_idle)
    decision = gate.evaluate(GroupedInput(
        b, gate.TARGET_GIT_COMMIT, gate.PRIOR_CLEANUP_SHA256,
        copy16.APPROVAL_SHA256, req["raw_bytes"], req["range_count"],
        not problems and chunk_sha is not None, lane_closed, not lane_pids))
    if problems:
        decision["decision"] = "RESOURCE_HOLD"
        decision["reasons"].extend(problems)
    return {"schema": "TLS_V10_B0003_OLD174_READ_ONLY_PREFLIGHT_V1",
            "at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "ELIGIBLE_NOT_READY" if decision["decision"] == "POLICY_ELIGIBLE_NOT_READY" else "HOLD",
            "window_id": gate.WINDOW, "target_request_git_commit": gate.TARGET_GIT_COMMIT,
            "target_request_sha256": sha(req_raw),
            "partial_original_full_sha256_from_frozen_manifest": row["sha256"] if row else None,
            "current_range_sha256": chunk_sha,
            "range_is_partial_original": True,
            "source_originals": "SOURCE_KEEP", "source_files_unlinked": 0,
            "source_payload_staged_bytes": 0,
            "all141_frozen_metadata_exact": all_metadata_exact,
            "physical_source_refs": hits, "proc_unreadable": unknown,
            "lane_physical_pids": lane_pids, "other_transfer_pids": transfer_pids,
            "lane_final_closure_receipt_sha256": lane_sha,
            "lane_current_registry": snap["registry"],
            "active_script_sha256": scripts, "active_script_chain_clear": scheduled_clear,
            "target_receiver_metadata": target_meta,
            "input": asdict(b), "decision": decision}


if __name__ == "__main__":
    result = inspect()
    print(json.dumps({"status": result["status"], "reasons": result["decision"]["reasons"],
                      "current_range_sha256": result["current_range_sha256"],
                      "workspace_available_bytes": result["input"]["workspace_available_bytes"],
                      "share_available_bytes": result["input"]["share_available_bytes"]}))
