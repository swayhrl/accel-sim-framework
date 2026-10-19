#!/usr/bin/env python3
"""Pure P9_PUBLIC exact141 post-restoration source-release gate.

This is not an executor.  No synthetic PASS is a real-science release proof.
"""

from dataclasses import dataclass, replace

import tls_v10_copy_only16g_gate as copy
import tls_v10_copy_only20g_gate as old


FILES_SHA = "38e5d71dae3d92c8728d511f7d648eb9eca12e99443c2072b4eb531e022072f4"
DIRS_SHA = "43589244defa70615b43b031c1df8edd1213e7f967cf93834ff229e4095c918b"
FIRST_RESTORE_NOT_ENOUGH = "CHUNK_RANGE_ONLY"


@dataclass(frozen=True)
class ReleaseInput:
    policy_id: str
    authority_sha256: str
    approval_sha256: str
    operation: str
    source_repo: str
    source_branch: str
    source_namespace: str
    source_dev: int
    source_root: str
    group: str
    selector_sha256: str
    file_inventory_sha256: str
    directory_inventory_sha256: str
    canonical_manifest_sha256: str
    txid: str
    target_root_native164: str
    frozen_file_count: int
    source_present_count: int
    archived_full_file_count: int
    native_full_restored_count: int
    restored_directory_metadata_count: int
    all_path_size_sha_join: bool
    all_numeric_file_metadata_join: bool
    all_numeric_directory_metadata_join: bool
    target_archive_durable_and_current: bool
    target_restore_independent_absent_destination: bool
    target_git_raw_readback: bool
    source_git_raw_readback: bool
    source_all_file_fresh_content_and_identity: bool
    no_unselected_or_new_file: bool
    no_symlink_hardlink_or_traversal: bool
    current_and_scheduled_readers_clear: bool
    lease_and_lane_clear: bool
    source_release_tool_fixture_qualified: bool
    journal_intent_fsync_before_unlink_and_done_ready: bool
    crash_reconciliation_qualified: bool
    snapshot_age_seconds: float
    workspace_f_bavail_bytes: int
    projected_control_write_bytes: int
    share_f_bavail_bytes: int
    memory_available_bytes: int
    cgroup_headroom_bytes: int | None


def synthetic_input(**updates):
    """Test-only all-true fixture; NEVER use as a real inspection result."""
    baseline = ReleaseInput(
        policy_id=copy.RELEASE_POLICY_ID, authority_sha256=copy.AUTHORITY_SHA256,
        approval_sha256=copy.APPROVAL_SHA256,
        operation="P9_PUBLIC_POSTRESTORE_EXACT_RELEASE",
        source_repo=old.SOURCE_REPO, source_branch=old.SOURCE_BRANCH,
        source_namespace=old.SOURCE_NAMESPACE, source_dev=old.SOURCE_DEV,
        source_root=old.SOURCE_ROOT, group=old.GROUP,
        selector_sha256=old.SELECTOR, file_inventory_sha256=FILES_SHA,
        directory_inventory_sha256=DIRS_SHA,
        canonical_manifest_sha256=old.MANIFEST_SHA256,
        txid=old.TXID, target_root_native164=old.TARGET_ROOT,
        frozen_file_count=141, source_present_count=141,
        archived_full_file_count=141, native_full_restored_count=141,
        restored_directory_metadata_count=4,
        all_path_size_sha_join=True, all_numeric_file_metadata_join=True,
        all_numeric_directory_metadata_join=True,
        target_archive_durable_and_current=True,
        target_restore_independent_absent_destination=True,
        target_git_raw_readback=True, source_git_raw_readback=True,
        source_all_file_fresh_content_and_identity=True,
        no_unselected_or_new_file=True, no_symlink_hardlink_or_traversal=True,
        current_and_scheduled_readers_clear=True, lease_and_lane_clear=True,
        source_release_tool_fixture_qualified=True,
        journal_intent_fsync_before_unlink_and_done_ready=True,
        crash_reconciliation_qualified=True, snapshot_age_seconds=0,
        workspace_f_bavail_bytes=17 * old.GIB,
        projected_control_write_bytes=old.MIB,
        share_f_bavail_bytes=42 * old.GIB,
        memory_available_bytes=80 * old.GIB,
        cgroup_headroom_bytes=40 * old.GIB)
    return replace(baseline, **updates)


def evaluate(item):
    reasons = []
    exact_policy = (item.policy_id == copy.RELEASE_POLICY_ID and
                    item.authority_sha256 == copy.AUTHORITY_SHA256 and
                    item.approval_sha256 == copy.APPROVAL_SHA256 and
                    item.operation == "P9_PUBLIC_POSTRESTORE_EXACT_RELEASE")
    floor = copy.COPY_FLOOR if exact_policy else old.DEFAULT_FLOOR
    if not exact_policy:
        reasons.append("NOT_EXACT_POSTRESTORE_RELEASE_OPT_IN_DEFAULT_48G")
    identity = (item.source_repo == old.SOURCE_REPO and
                item.source_branch == old.SOURCE_BRANCH and
                item.source_namespace == old.SOURCE_NAMESPACE and
                item.source_dev == old.SOURCE_DEV and
                item.source_root == old.SOURCE_ROOT and item.group == old.GROUP and
                item.selector_sha256 == old.SELECTOR and
                item.file_inventory_sha256 == FILES_SHA and
                item.directory_inventory_sha256 == DIRS_SHA and
                item.canonical_manifest_sha256 == old.MANIFEST_SHA256 and
                item.txid == old.TXID and item.target_root_native164 == old.TARGET_ROOT)
    if not identity:
        reasons.append("FROZEN_SELECTOR_SOURCE_OR_TARGET_IDENTITY_MISMATCH")
    if not (item.frozen_file_count == item.source_present_count ==
            item.archived_full_file_count == item.native_full_restored_count == 141 and
            item.restored_directory_metadata_count == 4):
        reasons.append("INCOMPLETE_141_FILES_OR_4_DIRECTORIES")
    if not (item.all_path_size_sha_join and item.all_numeric_file_metadata_join and
            item.all_numeric_directory_metadata_join and
            item.target_archive_durable_and_current and
            item.target_restore_independent_absent_destination and
            item.target_git_raw_readback and item.source_git_raw_readback):
        reasons.append("ARCHIVE_RESTORE_OR_READBACK_PROOF_GAP")
    if not (item.source_all_file_fresh_content_and_identity and
            item.no_unselected_or_new_file and item.no_symlink_hardlink_or_traversal):
        reasons.append("CURRENT_SOURCE_IDENTITY_OR_SCOPE_CHANGED")
    if not item.current_and_scheduled_readers_clear or not item.lease_and_lane_clear:
        reasons.append("ACTIVE_OR_PLANNED_READER_OR_LEASE")
    if not (item.source_release_tool_fixture_qualified and
            item.journal_intent_fsync_before_unlink_and_done_ready and
            item.crash_reconciliation_qualified):
        reasons.append("DURABLE_RELEASE_EXECUTOR_NOT_QUALIFIED")
    if item.snapshot_age_seconds < 0 or item.snapshot_age_seconds > old.MAX_SNAPSHOT_AGE_SECONDS:
        reasons.append("SOURCE_SNAPSHOT_STALE")
    if (item.projected_control_write_bytes < 0 or
            item.projected_control_write_bytes > old.MAX_OVERLAY_WRITES or
            item.workspace_f_bavail_bytes - item.projected_control_write_bytes < floor):
        reasons.append("SOURCE_F_BAVAIL_OR_PROJECTED_FLOOR")
    if item.share_f_bavail_bytes < old.SHARE_FLOOR:
        reasons.append("SHARE_F_BAVAIL_FLOOR")
    if (item.memory_available_bytes < old.RAM_FLOOR or
            item.cgroup_headroom_bytes is None or
            item.cgroup_headroom_bytes < item.projected_control_write_bytes):
        reasons.append("RAM_OR_CGROUP_FLOOR")
    return {"decision": "RELEASE_ELIGIBLE_NOT_RELEASED" if not reasons else "RELEASE_HOLD",
            "effective_workspace_floor_bytes": floor, "reasons": reasons,
            "source_unlink_authorized_by_this_evaluator": False,
            "source_files_released": 0}
