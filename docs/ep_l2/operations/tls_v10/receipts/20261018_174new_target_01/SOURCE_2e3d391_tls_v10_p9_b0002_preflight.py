#!/usr/bin/env python3
"""Read-only exact B0002 admission; a PASS is not SOURCE READY."""

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
import tls_v10_p9_grouped_copy16_gate as grouped
import tls_v10_p9_grouped_source_range as ranges


HERE = Path(__file__).resolve().parent
REQUEST = old.BRIDGE / "TLS_V10_P9_PUBLIC_B0002_TARGET_SOLE_WINDOW_REQUEST_COPY16.json"
MANIFEST = HERE / "TLS_V10_P9_PUBLIC_TARGET_TRANSACTION_MANIFEST.json"
PLAN = old.BRIDGE / "TLS_V10_P9_PUBLIC_INACTIVE_BATCHING_PROPOSAL_AFTER_B0001.json"
QUAL = HERE / "TLS_V10_P9_PUBLIC_B0002_GROUPED_SOURCE_FIXTURE_QUALIFICATION.json"
TARGET_PATH = ("docs/ep_l2/operations/tls_v10/receipts/20261018_174new_target_01/"
               "TLS_V10_P9_PUBLIC_B0002_TARGET_SOLE_WINDOW_REQUEST_COPY16.json")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _target_git_raw():
    return subprocess.check_output(["git", "show", grouped.TARGET_GIT_COMMIT + ":" + TARGET_PATH])


def _identity(info):
    return ranges._fingerprint(info)


def _source_range_sha(root, row, offset, length):
    parts = ranges._parts(row["relative_path"])
    expected = {k: v for k, v in row.items() if k != "relative_path"}
    parent, fd = ranges._source_fd(root, parts)
    try:
        before = os.fstat(fd)
        named = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        if (not stat.S_ISREG(before.st_mode) or
                _identity(before) != expected or _identity(named) != expected):
            raise ranges.Hold("preflight source identity drift")
        os.lseek(fd, offset, os.SEEK_SET)
        digest = hashlib.sha256()
        remaining = length
        while remaining:
            block = os.read(fd, min(1024 * 1024, remaining))
            if not block:
                raise ranges.Hold("preflight source short read")
            digest.update(block)
            remaining -= len(block)
        if (_identity(os.fstat(fd)) != expected or
                _identity(os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)) != expected):
            raise ranges.Hold("source changed during preflight range hash")
        return digest.hexdigest()
    finally:
        os.close(fd)
        os.close(parent)


def inspect():
    problems = []
    target_raw, request_raw, manifest_raw, plan_raw = (
        _target_git_raw(), REQUEST.read_bytes(), MANIFEST.read_bytes(), PLAN.read_bytes())
    request, manifest, plan = json.loads(request_raw), json.loads(manifest_raw), json.loads(plan_raw)
    exact_request = (target_raw == request_raw and sha(request_raw) == grouped.REQUEST_SHA256 and
                     request["schema"] == "TLS_V10_TARGET_GROUPED_RAW_WINDOW_V1" and
                     request["window_id"] == grouped.WINDOW and request["txid"] == old.TXID and
                     request["selector_sha256"] == old.SELECTOR and
                     request["canonical_manifest_sha256"] == old.MANIFEST_SHA256 and
                     request["source_root"] == old.SOURCE_ROOT and
                     request["target_root_native164"] == old.TARGET_ROOT and
                     request["prior_window_cleanup_sha256"] == grouped.PRIOR_CLEANUP_SHA256 and
                     request["plan_sha256"] == sha(plan_raw) and request["plan_batch_index"] == 1 and
                     request["source_originals"] == "SOURCE_KEEP" and
                     not request["source_scientific_release_authorized_by_this_window"] and
                     not request["copy_ready"])
    if not exact_request or sha(manifest_raw) != old.MANIFEST_SHA256:
        problems.append("TARGET_GIT_BRIDGE_OR_FROZEN_MANIFEST_MISMATCH")
    expected = plan["batches"][1]
    entries = request["ranges"]
    root = Path(old.SOURCE_ROOT)
    bridge_root = old.BRIDGE / (grouped.WINDOW + "_" + old.TXID[:12]) / "files"
    if (request["bridge_root"] != str(bridge_root) or bridge_root.parent.exists() or
            root.resolve(strict=True) != root or len(entries) != request["range_count"] or
            not 0 < len(entries) <= 128 or
            sum(e["length"] for e in entries) != request["raw_bytes"] or
            request["raw_bytes"] > 128 * old.MIB or
            expected["entries"] != [{k: e[k] for k in
                                      ("relative_path", "offset", "length", "original_size", "original_sha256")}
                                     for e in entries]):
        problems.append("B0002_RANGE_PLAN_OR_STAGE_BINDING_MISMATCH")
    frozen = {r["relative_path"]: r for r in manifest["files"]}
    if len(frozen) != 141 or len(manifest["directories"]) != 4:
        problems.append("FROZEN_GROUP_CARDINALITY_MISMATCH")
    all_metadata_exact = True
    for rel, row in frozen.items():
        path = root / rel
        try:
            info = os.lstat(path)
            want = {k: row[k] for k in
                    ("dev", "inode", "nlink", "uid", "gid", "mode", "size",
                     "mtime_ns", "ctime_ns", "allocated")}
            if not stat.S_ISREG(info.st_mode) or _identity(info) != want:
                all_metadata_exact = False
        except OSError:
            all_metadata_exact = False
    if not all_metadata_exact:
        problems.append("ALL_FROZEN_SOURCE_METADATA_NOT_EXACT")
    checked = []
    for index, entry in enumerate(entries):
        rel = entry["relative_path"]
        row = frozen.get(rel)
        if row is None:
            problems.append("RANGE_NOT_FROZEN"); break
        want = {k: row[k] for k in
                ("dev", "inode", "nlink", "uid", "gid", "mode", "size",
                 "mtime_ns", "ctime_ns", "allocated")}
        if (entry["source_identity"] != want or entry["source_path"] != str(root / rel) or
                entry["bridge_path"] != str(bridge_root / ("range-%04d.bin" % index)) or
                entry["original_size"] != row["size"] or
                entry["original_sha256"] != row["sha256"] or
                type(entry["offset"]) is not int or type(entry["length"]) is not int or
                entry["offset"] < 0 or not 0 < entry["length"] <= 128 * old.MIB or
                entry["offset"] + entry["length"] > row["size"]):
            problems.append("RANGE_IDENTITY_OR_BOUNDS_MISMATCH"); break
        current_sha = _source_range_sha(root, dict(want, relative_path=rel),
                                        entry["offset"], entry["length"])
        if entry["offset"] == 0 and entry["length"] == row["size"] and current_sha != row["sha256"]:
            problems.append("WHOLE_FILE_CURRENT_SHA_MISMATCH"); break
        checked.append({"relative_path": rel, "offset": entry["offset"],
                        "length": entry["length"], "current_chunk_sha256": current_sha})
    snap = old.real_snapshot()
    hits, unknown, lane_pids, transfer_pids = prior.physical_refs()
    script_sha = {name: sha(Path(name).read_bytes()) for name in prior.SCRIPT_SHA}
    scheduled_clear = (script_sha == prior.SCRIPT_SHA and all(
        old.SOURCE_ROOT not in Path(name).read_text() and
        "tls-cache-p9-public-v1" not in Path(name).read_text()
        for name in prior.SCRIPT_SHA))
    try:
        closure, closure_sha = prior.lane_closure()
    except (OSError, ValueError, subprocess.CalledProcessError):
        closure, closure_sha = False, None
    target_meta_path = ("docs/ep_l2/operations/tls_v10/receipts/20261018_174new_target_01/"
                        "TLS_V10_P9_PUBLIC_B0002_TARGET_METADATA_PREFLIGHT_COPY16.json")
    target_meta = json.loads(subprocess.check_output(
        ["git", "show", grouped.TARGET_GIT_COMMIT + ":" + target_meta_path]))
    target_idle = (target_meta["receiver_idle"] is True and
                   target_meta["bridge_payloads_absent"] is True and
                   target_meta["B0001_closed"] is True)
    base = old.GateInput(**snap["input"])
    base = replace(base, policy_id=copy16.POLICY_ID,
                   amendment_sha256=copy16.AUTHORITY_SHA256,
                   window_id=grouped.WINDOW,
                   target_request_sha256=grouped.REQUEST_SHA256,
                   planned_overlay_write_bytes=old.MIB,
                   planned_bridge_staged_bytes=request["raw_bytes"] + 1024 * 1024,
                   planned_rate_bytes_per_second=old.MAX_RATE_BPS,
                   copy_lease_authorized=(closure and not lane_pids and not transfer_pids and
                                          snap["registry"]["active_leases"] == 0),
                   physical_scan_complete=not unknown,
                   candidate_root_idle=not hits,
                   scheduled_readers_clear=scheduled_clear,
                   first_source_identity_ok=all_metadata_exact,
                   first_source_sha_refreshed=(len(checked) == len(entries)),
                   target_request_present_and_exact=exact_request,
                   sole_source_sender=not transfer_pids,
                   sole_target_receiver=target_idle)
    decision = grouped.evaluate(grouped.GroupedInput(
        base, grouped.TARGET_GIT_COMMIT, grouped.PRIOR_CLEANUP_SHA256,
        copy16.APPROVAL_SHA256, request["raw_bytes"], len(entries),
        not problems and len(checked) == len(entries), closure, not lane_pids))
    if problems:
        decision["decision"] = "RESOURCE_HOLD"
        decision["reasons"].extend(problems)
    return {"schema": "TLS_V10_B0002_OLD174_READ_ONLY_PREFLIGHT_V1",
            "at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "ELIGIBLE_NOT_READY" if decision["decision"] == "POLICY_ELIGIBLE_NOT_READY" else "HOLD",
            "window_id": grouped.WINDOW, "target_request_git_commit": grouped.TARGET_GIT_COMMIT,
            "target_request_sha256": sha(request_raw),
            "source_fixture_receipt_sha256": sha(QUAL.read_bytes()),
            "source_grouped_gate_code_sha256": sha((HERE / "tls_v10_p9_grouped_copy16_gate.py").read_bytes()),
            "source_grouped_range_code_sha256": sha((HERE / "tls_v10_p9_grouped_source_range.py").read_bytes()),
            "source_originals": "SOURCE_KEEP", "source_files_unlinked": 0,
            "source_payload_staged_bytes": 0, "range_count": len(entries),
            "current_range_sha": checked,
            "all_141_frozen_metadata_exact": all_metadata_exact,
            "physical_source_refs": hits, "proc_unreadable": unknown,
            "lane_physical_pids": lane_pids, "other_transfer_pids": transfer_pids,
            "lane_final_closure_receipt_sha256": closure_sha,
            "lane_current_registry": snap["registry"],
            "active_script_sha256": script_sha,
            "active_script_chain_clear": scheduled_clear,
            "target_receiver_metadata": target_meta,
            "input": asdict(base), "decision": decision}


if __name__ == "__main__":
    result = inspect()
    print(json.dumps({"status": result["status"],
                      "reasons": result["decision"]["reasons"],
                      "workspace_available_bytes": result["input"]["workspace_available_bytes"],
                      "share_available_bytes": result["input"]["share_available_bytes"],
                      "ranges_sha_checked": len(result["current_range_sha"])}))
