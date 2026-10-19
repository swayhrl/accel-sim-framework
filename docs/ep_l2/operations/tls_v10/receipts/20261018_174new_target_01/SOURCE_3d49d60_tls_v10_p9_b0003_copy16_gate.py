#!/usr/bin/env python3
"""Pure exact B0003 COPY_ONLY16 gate; no staging/READY/release authority."""

from dataclasses import replace

import tls_v10_copy_only16g_gate as original
import tls_v10_copy_only20g_gate as old
from tls_v10_p9_grouped_copy16_gate import GroupedInput


WINDOW = "TLS_V10_P9_PUBLIC_B0003"
REQUEST_SHA256 = "7ac0a361458644e74bd39482ee3243b9b184afac6d440c9a4aac2f141e571a49"
TARGET_GIT_COMMIT = "04fce1cc8f0f54a058941fb108b786ca874401b3"
PRIOR_CLEANUP_SHA256 = "5d28c348cee88be74dd1dbae0bf5924eb73b61fc3fb86cc80160e9b4c81a3ab0"


def evaluate(item: GroupedInput):
    b = item.base
    exact = (b.window_id == WINDOW and b.target_request_sha256 == REQUEST_SHA256 and
             item.request_git_commit == TARGET_GIT_COMMIT and
             item.prior_cleanup_sha256 == PRIOR_CLEANUP_SHA256 and
             item.approval_sha256 == original.APPROVAL_SHA256 and
             b.policy_id == original.POLICY_ID and
             b.amendment_sha256 == original.AUTHORITY_SHA256 and
             item.all_ranges_bound_and_current and
             type(item.raw_window_bytes) is int and
             item.raw_window_bytes == 128 * old.MIB and
             type(item.range_count) is int and item.range_count == 1)
    adapter = replace(b, window_id=old.WINDOW,
                      target_request_sha256=old.TARGET_REQUEST_SHA256)
    result = original.evaluate(original.Copy16Input(
        adapter, item.approval_sha256, item.raw_window_bytes,
        exact, exact, item.lane_final_closure_verified,
        item.lane_physical_clear))
    if not exact:
        result["decision"] = "RESOURCE_HOLD"
        result["reasons"].append("B0003_EXACT_WINDOW_OR_RANGE_BINDING_FAILURE")
    result["window_id"] = WINDOW
    result["target_request_sha256"] = REQUEST_SHA256
    result["ready_published"] = False
    result["payload_transfer_authorized_by_this_evaluator"] = False
    result["source_unlink_authorized"] = False
    return result
