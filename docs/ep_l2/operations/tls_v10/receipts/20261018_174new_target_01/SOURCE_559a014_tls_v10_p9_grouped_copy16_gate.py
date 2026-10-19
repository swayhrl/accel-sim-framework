#!/usr/bin/env python3
"""Exact B0002 COPY_ONLY extension; no staging, READY, or source release."""

from dataclasses import dataclass, replace

import tls_v10_copy_only16g_gate as original
import tls_v10_copy_only20g_gate as old


WINDOW = "TLS_V10_P9_PUBLIC_B0002"
REQUEST_SHA256 = "72083570bbdccee9ef02d1760f1d2adcb15de4f273a76ec9e28bb98fa5eccb2b"
TARGET_GIT_COMMIT = "38a773b06b7dcc3c1000cba04be1ca2f7a22be6e"
PRIOR_CLEANUP_SHA256 = "03eebe1fda12bf0fc5613041166833b9ab65d3b1003b0cb82ab5b4a587ed10a3"


@dataclass(frozen=True)
class GroupedInput:
    base: old.GateInput
    request_git_commit: str
    prior_cleanup_sha256: str
    approval_sha256: str
    raw_window_bytes: int
    range_count: int
    all_ranges_bound_and_current: bool
    lane_final_closure_verified: bool
    lane_physical_clear: bool


def evaluate(item: GroupedInput):
    b = item.base
    exact = (b.window_id == WINDOW and b.target_request_sha256 == REQUEST_SHA256 and
             item.request_git_commit == TARGET_GIT_COMMIT and
             item.prior_cleanup_sha256 == PRIOR_CLEANUP_SHA256 and
             item.approval_sha256 == original.APPROVAL_SHA256 and
             b.policy_id == original.POLICY_ID and
             b.amendment_sha256 == original.AUTHORITY_SHA256 and
             item.all_ranges_bound_and_current and
             type(item.raw_window_bytes) is int and 0 < item.raw_window_bytes <= original.MAX_RAW_RANGE and
             type(item.range_count) is int and 0 < item.range_count <= 128)
    # The B0001 evaluator remains immutable. Only after exact new-window
    # binding, reuse its unchanged 16-GiB resource/operation checks.
    adapter = replace(b, window_id=old.WINDOW,
                      target_request_sha256=old.TARGET_REQUEST_SHA256)
    decision = original.evaluate(original.Copy16Input(
        adapter, item.approval_sha256, item.raw_window_bytes,
        exact, exact, item.lane_final_closure_verified,
        item.lane_physical_clear))
    if not exact:
        decision["decision"] = "RESOURCE_HOLD"
        decision["reasons"].append("GROUPED_B0002_EXACT_BINDING_OR_RANGE_FAILURE")
    decision["window_id"] = WINDOW
    decision["target_request_sha256"] = REQUEST_SHA256
    decision["ready_published"] = False
    decision["payload_transfer_authorized_by_this_evaluator"] = False
    decision["source_unlink_authorized"] = False
    return decision
