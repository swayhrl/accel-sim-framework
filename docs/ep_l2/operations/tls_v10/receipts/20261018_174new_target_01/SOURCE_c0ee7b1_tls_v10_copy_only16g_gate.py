#!/usr/bin/env python3
"""Pure, narrow TLS-V10 P9_PUBLIC B0001 COPY_ONLY resource policy.

This deliberately does not change the historical 20-GiB or default 48-GiB
policy, stage bytes, sign READY, or grant source-release authority.  A caller
must separately prove every real-world boolean and recheck at publication.
"""

from dataclasses import dataclass, replace

import tls_v10_copy_only20g_gate as old


POLICY_ID = "TLS_V10_FROZEN_EXCLUSIVE_COPY_ONLY_16G_20261019"
AUTHORITY_SHA256 = "745fb24b603627b63bc43a1cb130a9e61038d23adee618e2850e3d80755c7bf1"
APPROVAL_SHA256 = "789528e6dd4e7b51c3a437e14f8a9b3df1045bfa5e1eefc71974b3324ce9b61d"
RELEASE_POLICY_ID = "TLS_V10_P9_PUBLIC_POSTRESTORE_EXACT_RELEASE_16G_20261019"
COPY_FLOOR = 16 * old.GIB
MAX_RAW_RANGE = 128 * old.MIB


@dataclass(frozen=True)
class Copy16Input:
    base: old.GateInput
    approval_sha256: str
    planned_raw_range_bytes: int
    nonce_or_txid_exact: bool
    frozen_manifest_member: bool
    lane_final_closure_verified: bool
    lane_physical_clear: bool


def policy_input(**updates):
    """Synthetic fixture only; never evidence that old174 is currently safe."""
    base = old.policy_input(policy_id=POLICY_ID,
                            amendment_sha256=AUTHORITY_SHA256,
                            workspace_available_bytes=17 * old.GIB,
                            lane_registry_fresh=True)
    base_updates = {k: v for k, v in updates.items() if hasattr(base, k)}
    outer_updates = {k: v for k, v in updates.items() if k not in base_updates}
    item = Copy16Input(replace(base, **base_updates), APPROVAL_SHA256,
                       144, True, True, True, True)
    return replace(item, **outer_updates)


def evaluate(item: Copy16Input):
    b = item.base
    reasons = []
    exact_policy = (b.policy_id == POLICY_ID and
                    b.amendment_sha256 == AUTHORITY_SHA256 and
                    item.approval_sha256 == APPROVAL_SHA256 and
                    b.operation == "TLS_V10_COPY_ONLY")
    floor = COPY_FLOOR if exact_policy else old.DEFAULT_FLOOR
    if not exact_policy:
        reasons.append("NOT_EXACT_COPY16_OPT_IN_DEFAULT_48G")
    exact_identity = (
        b.source_repo == old.SOURCE_REPO and b.source_branch == old.SOURCE_BRANCH and
        b.source_namespace == old.SOURCE_NAMESPACE and b.source_dev == old.SOURCE_DEV and
        b.bridge_dev == old.BRIDGE_DEV and b.source_root == old.SOURCE_ROOT and
        b.source_asset_class == "TLS_EXCLUSIVE_FROZEN_NONCODE" and
        b.group == old.GROUP and b.window_id == old.WINDOW and b.txid == old.TXID and
        b.selector_sha256 == old.SELECTOR and b.manifest_sha256 == old.MANIFEST_SHA256 and
        b.target_root_native164 == old.TARGET_ROOT and
        b.target_request_sha256 == old.TARGET_REQUEST_SHA256 and
        item.nonce_or_txid_exact and item.frozen_manifest_member)
    if not exact_identity:
        reasons.append("SOURCE_OR_TRANSACTION_IDENTITY_MISMATCH")
    if b.source_unlink_requested:
        reasons.append("COPY_POLICY_NEVER_ALLOWS_UNLINK")
    if b.snapshot_age_seconds < 0 or b.snapshot_age_seconds > old.MAX_SNAPSHOT_AGE_SECONDS:
        reasons.append("SOURCE_RESOURCE_SNAPSHOT_STALE")
    if b.planned_overlay_write_bytes < 0 or b.planned_overlay_write_bytes > old.MAX_OVERLAY_WRITES:
        reasons.append("OVERLAY_CONTROL_WRITE_BUDGET_INVALID")
    if b.workspace_available_bytes < floor or b.workspace_available_bytes - b.planned_overlay_write_bytes < floor:
        reasons.append("WORKSPACE_F_BAVAIL_OR_PROJECTED_HEADROOM_BELOW_FLOOR")
    if b.planned_bridge_staged_bytes < 0 or b.planned_bridge_staged_bytes > old.MAX_BRIDGE_STAGED:
        reasons.append("BRIDGE_STAGING_LIMIT")
    if b.share_available_bytes < old.SHARE_FLOOR or b.share_available_bytes - b.planned_bridge_staged_bytes < old.SHARE_FLOOR:
        reasons.append("SHARE_F_BAVAIL_OR_PROJECTED_HEADROOM_BELOW_FLOOR")
    if (b.memory_available_bytes < old.RAM_FLOOR or b.planned_memory_bytes < 0 or
            b.memory_available_bytes - b.planned_memory_bytes < old.RAM_FLOOR or
            b.cgroup_headroom_bytes is None or b.cgroup_headroom_bytes < b.planned_memory_bytes):
        reasons.append("RAM_OR_CGROUP_HEADROOM")
    if (not item.lane_final_closure_verified or not item.lane_physical_clear or
            not b.lane_runs_clear or not b.lane_leases_clear or not b.copy_lease_authorized):
        reasons.append("LANE_FINAL_CLOSURE_OR_LEASE_NOT_PROVEN")
    if not b.physical_scan_complete or not b.candidate_root_idle or not b.scheduled_readers_clear:
        reasons.append("PHYSICAL_OR_SCHEDULED_READER_NOT_PROVEN_CLEAR")
    if not b.first_source_identity_ok or not b.first_source_sha_refreshed:
        reasons.append("FIRST_SOURCE_IDENTITY_OR_SHA_NOT_FRESH")
    if not b.target_request_present_and_exact:
        reasons.append("PINNED_TARGET_WINDOW_REQUEST_NOT_EXACT")
    if item.planned_raw_range_bytes < 0 or item.planned_raw_range_bytes > MAX_RAW_RANGE:
        reasons.append("RAW_RANGE_LIMIT")
    if (b.planned_rate_bytes_per_second < 0 or b.planned_rate_bytes_per_second > old.MAX_RATE_BPS or
            not b.sole_source_sender or not b.sole_target_receiver):
        reasons.append("RATE_OR_SINGLE_STREAM_LIMIT")
    if b.source_signed_ready:
        reasons.append("EVALUATOR_CANNOT_ACCEPT_OR_ISSUE_SOURCE_READY")
    return {
        "decision": "POLICY_ELIGIBLE_NOT_READY" if not reasons else "RESOURCE_HOLD",
        "effective_workspace_floor_bytes": floor,
        "projected_workspace_available_bytes": b.workspace_available_bytes - b.planned_overlay_write_bytes,
        "reasons": reasons,
        "ready_published": False,
        "payload_transfer_authorized_by_this_evaluator": False,
        "source_unlink_authorized": False,
    }
