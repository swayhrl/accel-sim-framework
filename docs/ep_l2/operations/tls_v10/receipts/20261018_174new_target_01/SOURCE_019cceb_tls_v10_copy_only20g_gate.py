#!/usr/bin/env python3
"""Narrow, no-transfer TLS-V10 COPY_ONLY admission evaluator.

This module cannot publish READY, stage bytes or unlink source files. The
original freeze_p9_group.py 48-GiB gate is deliberately not modified.
Synthetic tests call evaluate(); real_snapshot() is read-only.
"""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

import audit_process_refs


GIB = 1024 ** 3
MIB = 1024 ** 2
POLICY_ID = "TLS_V10_COPY_ONLY_20G_20261019"
AMENDMENT_SHA256 = "bfbab6aa88a974c3f2b0708534f8738ac23186e4f9e64556379ec3491d45715a"
SOURCE_REPO = "swayhrl/gpu-l2-cache-verilog"
SOURCE_BRANCH = "hrl/ops-174-tls-v10-source-exec-v1"
SOURCE_NAMESPACE = "mnt:[4026534768]"
SOURCE_DEV = 156
BRIDGE_DEV = 2431
SOURCE_ROOT = "/workspace/worktrees/accel-sim-tls-cache/hw_run/tls-cache-p9-public-v1"
GROUP = "P9_PUBLIC"
WINDOW = "TLS_V10_P9_PUBLIC_B0001"
TXID = "574747b05622a2a0f3ef1a58c11044ee724e5e585d0edd5f0fc32937eda12e6b"
SELECTOR = "315c008ee1757637b4f68172f93e58c4916cda061936dc4d0125762e6aa9ba0a"
MANIFEST_SHA256 = "ad7e45a12d486ea3a62ff8452df321fb9ad093ca582eb23a3c05ac716267c597"
TARGET_ROOT = (
    "/home/shared/huangrulin/host174_storage_recovery/tls_v10/"
    "20261018_P9_PUBLIC_315c008ee1757637b4f68172f93e58c4916cda061936dc4d0125762e6aa9ba0a"
)
TARGET_REQUEST_SHA256 = "4e45132897553b758cd073292492ffe5ea317d91c0ff85265fd77c8efa3dfe06"
BRIDGE = Path("/root/share/host174_storage_recovery_bridge/20261016_storageops_02")
HERE = Path(__file__).resolve().parent
HOLD_RECEIPT = HERE / "TLS_V10_COPY_ONLY_20G_RESOURCE_HOLD.json"
DEFAULT_FLOOR = 48 * GIB
COPY_ONLY_FLOOR = 20 * GIB
SHARE_FLOOR = 40 * GIB
RAM_FLOOR = 64 * GIB
MAX_OVERLAY_WRITES = 32 * MIB
MAX_BRIDGE_STAGED = 256 * MIB
MAX_RATE_BPS = 30 * MIB
MAX_SNAPSHOT_AGE_SECONDS = 30


@dataclass(frozen=True)
class GateInput:
    policy_id: str
    amendment_sha256: str
    operation: str
    source_repo: str
    source_branch: str
    source_namespace: str
    source_dev: int
    bridge_dev: int
    source_root: str
    source_asset_class: str
    group: str
    window_id: str
    txid: str
    selector_sha256: str
    manifest_sha256: str
    target_root_native164: str
    target_request_sha256: str
    snapshot_age_seconds: float
    workspace_available_bytes: int
    workspace_total_free_bytes_non_gate: int
    planned_overlay_write_bytes: int
    share_available_bytes: int
    memory_available_bytes: int
    cgroup_headroom_bytes: int | None
    planned_memory_bytes: int
    lane_registry_fresh: bool
    lane_runs_clear: bool
    lane_leases_clear: bool
    copy_lease_authorized: bool
    physical_scan_complete: bool
    candidate_root_idle: bool
    scheduled_readers_clear: bool
    first_source_identity_ok: bool
    first_source_sha_refreshed: bool
    target_request_present_and_exact: bool
    planned_bridge_staged_bytes: int
    planned_rate_bytes_per_second: int
    sole_source_sender: bool
    sole_target_receiver: bool
    source_signed_ready: bool
    source_unlink_requested: bool


def policy_input(**updates):
    """Construct a testable fully-bound baseline, never a real-world proof."""
    item = GateInput(
        policy_id=POLICY_ID, amendment_sha256=AMENDMENT_SHA256,
        operation="TLS_V10_COPY_ONLY", source_repo=SOURCE_REPO,
        source_branch=SOURCE_BRANCH, source_namespace=SOURCE_NAMESPACE,
        source_dev=SOURCE_DEV, bridge_dev=BRIDGE_DEV, source_root=SOURCE_ROOT,
        source_asset_class="TLS_EXCLUSIVE_FROZEN_NONCODE", group=GROUP,
        window_id=WINDOW, txid=TXID, selector_sha256=SELECTOR,
        manifest_sha256=MANIFEST_SHA256, target_root_native164=TARGET_ROOT,
        target_request_sha256=TARGET_REQUEST_SHA256,
        snapshot_age_seconds=0,
        workspace_available_bytes=21 * GIB,
        workspace_total_free_bytes_non_gate=21 * GIB,
        planned_overlay_write_bytes=MIB, share_available_bytes=42 * GIB,
        memory_available_bytes=80 * GIB, cgroup_headroom_bytes=40 * GIB,
        planned_memory_bytes=64 * MIB, lane_registry_fresh=True,
        lane_runs_clear=True, lane_leases_clear=True, physical_scan_complete=True,
        copy_lease_authorized=True,
        candidate_root_idle=True, scheduled_readers_clear=True,
        first_source_identity_ok=True, first_source_sha_refreshed=True,
        target_request_present_and_exact=True, planned_bridge_staged_bytes=144,
        planned_rate_bytes_per_second=MIB, sole_source_sender=True,
        sole_target_receiver=True, source_signed_ready=False,
        source_unlink_requested=False)
    return replace(item, **updates)


def evaluate(item):
    """Pure fail-closed decision. ELIGIBLE is never a signed COPY_READY."""
    reasons = []
    exact_policy = (item.policy_id == POLICY_ID and
                    item.amendment_sha256 == AMENDMENT_SHA256 and
                    item.operation == "TLS_V10_COPY_ONLY")
    floor = COPY_ONLY_FLOOR if exact_policy else DEFAULT_FLOOR
    if not exact_policy:
        reasons.append("NOT_EXACT_COPY_ONLY_OPT_IN_DEFAULT_48G")
    exact_identity = (
        item.source_repo == SOURCE_REPO and item.source_branch == SOURCE_BRANCH and
        item.source_namespace == SOURCE_NAMESPACE and item.source_dev == SOURCE_DEV and
        item.bridge_dev == BRIDGE_DEV and item.source_root == SOURCE_ROOT and
        item.source_asset_class == "TLS_EXCLUSIVE_FROZEN_NONCODE" and
        item.group == GROUP and item.window_id == WINDOW and item.txid == TXID and
        item.selector_sha256 == SELECTOR and item.manifest_sha256 == MANIFEST_SHA256 and
        item.target_root_native164 == TARGET_ROOT and
        item.target_request_sha256 == TARGET_REQUEST_SHA256
    )
    if not exact_identity:
        reasons.append("SOURCE_OR_TRANSACTION_IDENTITY_MISMATCH")
    if item.source_unlink_requested:
        reasons.append("SOURCE_UNLINK_OUTSIDE_COPY_ONLY_POLICY")
    if (item.snapshot_age_seconds < 0 or
            item.snapshot_age_seconds > MAX_SNAPSHOT_AGE_SECONDS):
        reasons.append("SOURCE_RESOURCE_SNAPSHOT_STALE")
    if item.planned_overlay_write_bytes < 0 or item.planned_overlay_write_bytes > MAX_OVERLAY_WRITES:
        reasons.append("OVERLAY_CONTROL_WRITE_BUDGET_INVALID")
    if item.workspace_available_bytes < floor or (
            item.workspace_available_bytes - item.planned_overlay_write_bytes < floor):
        reasons.append("WORKSPACE_F_BAVAIL_OR_PROJECTED_HEADROOM_BELOW_FLOOR")
    if item.planned_bridge_staged_bytes < 0 or item.planned_bridge_staged_bytes > MAX_BRIDGE_STAGED:
        reasons.append("BRIDGE_STAGING_LIMIT")
    if (item.share_available_bytes < SHARE_FLOOR or
            item.share_available_bytes - item.planned_bridge_staged_bytes < SHARE_FLOOR):
        reasons.append("SHARE_F_BAVAIL_OR_PROJECTED_HEADROOM_BELOW_FLOOR")
    if (item.memory_available_bytes < RAM_FLOOR or
            item.planned_memory_bytes < 0 or
            item.memory_available_bytes - item.planned_memory_bytes < RAM_FLOOR or
            item.cgroup_headroom_bytes is None or
            item.cgroup_headroom_bytes < item.planned_memory_bytes):
        reasons.append("RAM_OR_CGROUP_HEADROOM")
    if (not item.lane_registry_fresh or not item.lane_runs_clear or
            not item.lane_leases_clear or not item.copy_lease_authorized):
        reasons.append("LANE_REGISTRY_OR_LEASE_NOT_FRESH_CLEAR")
    if not item.physical_scan_complete or not item.candidate_root_idle or not item.scheduled_readers_clear:
        reasons.append("PHYSICAL_OR_SCHEDULED_READER_NOT_PROVEN_CLEAR")
    if not item.first_source_identity_ok or not item.first_source_sha_refreshed:
        reasons.append("FIRST_SOURCE_IDENTITY_OR_SHA_NOT_FRESH")
    if not item.target_request_present_and_exact:
        reasons.append("PINNED_TARGET_WINDOW_REQUEST_NOT_EXACT")
    if (item.planned_rate_bytes_per_second < 0 or
            item.planned_rate_bytes_per_second > MAX_RATE_BPS or
            not item.sole_source_sender or not item.sole_target_receiver):
        reasons.append("RATE_OR_SINGLE_STREAM_LIMIT")
    if item.source_signed_ready:
        reasons.append("EVALUATOR_CANNOT_ACCEPT_OR_ISSUE_SOURCE_READY")
    return {
        "decision": "POLICY_ELIGIBLE_NOT_READY" if not reasons else "RESOURCE_HOLD",
        "effective_workspace_floor_bytes": floor,
        "projected_workspace_available_bytes": (
            item.workspace_available_bytes - item.planned_overlay_write_bytes),
        "reasons": reasons, "ready_published": False,
        "payload_transfer_authorized_by_this_evaluator": False,
        "source_unlink_authorized": False,
    }


def target_can_receive(gate_result, signed_source_ready):
    return gate_result["decision"] == "POLICY_ELIGIBLE_NOT_READY" and signed_source_ready


def _memavailable():
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) * 1024
    raise RuntimeError("MemAvailable missing")


def _cgroup_headroom():
    root = Path("/sys/fs/cgroup")
    try:
        maximum = (root / "memory.max").read_text().strip()
        current = int((root / "memory.current").read_text().strip())
        return None if maximum == "max" else max(0, int(maximum) - current)
    except (OSError, ValueError):
        return None


def _first_identity():
    manifest_path = HERE / "TLS_V10_P9_PUBLIC_TARGET_TRANSACTION_MANIFEST.json"
    raw = manifest_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != MANIFEST_SHA256:
        return False, "frozen target manifest SHA drift"
    manifest = json.loads(raw)
    if len(manifest["files"]) != 141:
        return False, "frozen file count drift"
    first = next((row for row in manifest["files"] if
                  row["relative_path"] ==
                  "matrix-d10fe92/cfd_097k.baseline.dynamic.driver.out"), None)
    if first is None:
        return False, "frozen first range missing"
    path = Path(SOURCE_ROOT) / first["relative_path"]
    if path.resolve(strict=True) != path:
        return False, "source symlink/path mismatch"
    info = os.lstat(path)
    field_map = {"st_dev": "dev", "st_ino": "inode", "st_nlink": "nlink",
                 "st_uid": "uid", "st_gid": "gid", "st_mtime_ns": "mtime_ns",
                 "st_ctime_ns": "ctime_ns", "st_size": "size"}
    ok = stat.S_ISREG(info.st_mode) and all(
        getattr(info, field) == first[key] for field, key in field_map.items())
    ok = ok and info.st_blocks * 512 == first["allocated"] and info.st_mode & 0o777 == first["mode"]
    return ok, str(path)


def real_snapshot():
    """Bounded old174 read-only check; it never hashes all frozen TLS files."""
    at = datetime.now(timezone.utc)
    ws, share = os.statvfs("/workspace"), os.statvfs("/root/share")
    registry_path = Path("/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json")
    registry = json.loads(registry_path.read_text())
    updated = datetime.fromisoformat(registry["updated_at"])
    age = (at - updated).total_seconds()
    active_runs = sum(v.get("status") == "RUNNING" for v in registry["runs"].values())
    active_leases = sum(v.get("status") not in ("RELEASED", "CANCELLED")
                        for v in registry["resource_leases"].values())
    boot_id = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    rows = []
    scanned = 0
    for proc in Path("/proc").iterdir():
        if proc.name.isdecimal():
            scanned += 1
            found = audit_process_refs.scan(int(proc.name))
            if found:
                rows.append(found)
    candidate_refs = [row["pid"] for row in rows if
                      SOURCE_ROOT in row["argv"] or
                      (row["cwd"] or "").startswith(SOURCE_ROOT) or
                      any(SOURCE_ROOT in hit["target"] for hit in row["fd_hits"])]
    known_p9 = [row for row in rows if row["pid"] in (1789920, 1789922)]
    mixed_offloader = [row for row in rows if row["pid"] == 1920891]
    physical_complete = all(not row["fd_unreadable"] for row in rows)
    public_rows = [{"pid": row["pid"], "ppid": row["ppid"],
                    "state": row["state"], "start_ticks": row["start_ticks"],
                    "cwd": row["cwd"], "fd_hits": row["fd_hits"],
                    "fd_unreadable": row["fd_unreadable"],
                    "argv_sha256": hashlib.sha256(row["argv"].encode()).hexdigest()}
                   for row in rows]
    first_ok, first_detail = _first_identity()
    binding = json.loads((HERE / "TLS_V10_P9_PUBLIC_SELECTOR_BINDING.json").read_text())
    binding_exact = (binding["txid"] == TXID and
                     binding["selector_sha256"] == SELECTOR and
                     binding["target_transaction_manifest_sha256"] == MANIFEST_SHA256 and
                     binding["genuine164_destination_base_native164"] == TARGET_ROOT)
    request_path = BRIDGE / "TLS_V10_P9_PUBLIC_TARGET_SOLE_WINDOW_READY.json"
    request_exact = (binding_exact and request_path.exists() and
                     hashlib.sha256(request_path.read_bytes()).hexdigest() ==
                     TARGET_REQUEST_SHA256)
    source_branch = subprocess.check_output(
        ["git", "-C", str(HERE), "branch", "--show-current"], text=True).strip()
    request = policy_input(
        workspace_available_bytes=ws.f_bavail * ws.f_frsize,
        snapshot_age_seconds=(datetime.now(timezone.utc) - at).total_seconds(),
        workspace_total_free_bytes_non_gate=ws.f_bfree * ws.f_frsize,
        planned_overlay_write_bytes=MIB,
        share_available_bytes=share.f_bavail * share.f_frsize,
        memory_available_bytes=_memavailable(),
        cgroup_headroom_bytes=_cgroup_headroom(),
        source_namespace=os.readlink("/proc/self/ns/mnt"),
        source_branch=source_branch,
        source_dev=os.stat("/workspace").st_dev,
        bridge_dev=os.stat(BRIDGE).st_dev,
        lane_registry_fresh=0 <= age <= 180,
        lane_runs_clear=active_runs == 0,
        lane_leases_clear=active_leases == 0,
        copy_lease_authorized=False,
        physical_scan_complete=physical_complete,
        candidate_root_idle=not candidate_refs,
        scheduled_readers_clear=not known_p9 and not mixed_offloader,
        first_source_identity_ok=first_ok,
        first_source_sha_refreshed=False,
        target_request_present_and_exact=request_exact,
        sole_source_sender=False,
        sole_target_receiver=False,
    )
    return {"at_utc": at.isoformat(), "policy_caller": "real_snapshot() read-only",
            "input": asdict(request), "decision": evaluate(request),
            "physical": {"boot_id": boot_id, "pids_scanned": scanned,
                         "matched_processes": public_rows,
                         "candidate_root_refs": candidate_refs,
                         "known_p9_pids": [row["pid"] for row in known_p9],
                         "mixed_offloader_pids": [row["pid"] for row in mixed_offloader]},
            "registry": {"updated_at": registry["updated_at"], "age_seconds": age,
                         "active_runs": active_runs, "active_leases": active_leases},
            "first_source_identity_detail": first_detail,
            "local_frozen_binding_exact": binding_exact,
            "first_source_content_hash": "DEFERRED_WHILE_RESOURCE_HOLD",
            "single_stream_qualification": "NOT_INDEPENDENTLY_CLEARED_WHILE_RESOURCE_HOLD",
            "source_files_unlinked": 0, "scientific_payload_transferred_bytes": 0}


if __name__ == "__main__":
    import sys
    snapshot = real_snapshot()
    if len(sys.argv) == 2 and sys.argv[1] == "--write-hold":
        if snapshot["decision"]["decision"] != "RESOURCE_HOLD":
            raise SystemExit("no HOLD receipt: resource gate unexpectedly eligible")
        snapshot["schema"] = "TLS_V10_OLD174_COPY_ONLY_20G_RESOURCE_HOLD_V1"
        snapshot["source_originals"] = "SOURCE_KEEP"
        snapshot["frozen_group_count_unchanged"] = 25
        snapshot["frozen_regular_file_count_unchanged"] = 2328
        with HOLD_RECEIPT.open("x") as out:
            json.dump(snapshot, out, sort_keys=True, indent=2)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        print(json.dumps({"receipt": str(HOLD_RECEIPT),
                          "decision": snapshot["decision"]["decision"],
                          "workspace_available_bytes": snapshot["input"]["workspace_available_bytes"],
                          "share_available_bytes": snapshot["input"]["share_available_bytes"],
                          "memory_available_bytes": snapshot["input"]["memory_available_bytes"],
                          "reasons": snapshot["decision"]["reasons"]}, sort_keys=True))
    elif len(sys.argv) == 1:
        print(json.dumps(snapshot, sort_keys=True, indent=2))
    else:
        raise SystemExit("usage: tls_v10_copy_only20g_gate.py [--write-hold]")
