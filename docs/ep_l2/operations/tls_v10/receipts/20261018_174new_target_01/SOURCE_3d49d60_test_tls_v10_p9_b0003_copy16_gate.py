#!/usr/bin/env python3
"""Synthetic exact B0003 policy matrix; no real-world PASS assertion."""

from dataclasses import replace
import unittest

import tls_v10_copy_only16g_gate as policy
import tls_v10_copy_only20g_gate as old
from tls_v10_p9_grouped_copy16_gate import GroupedInput
import tls_v10_p9_b0003_copy16_gate as b3


class B0003GateTests(unittest.TestCase):
    def item(self, **updates):
        base = old.policy_input(policy_id=policy.POLICY_ID,
                                amendment_sha256=policy.AUTHORITY_SHA256,
                                window_id=b3.WINDOW,
                                target_request_sha256=b3.REQUEST_SHA256,
                                workspace_available_bytes=17 * old.GIB,
                                planned_bridge_staged_bytes=128 * old.MIB)
        b_updates = {k: v for k, v in updates.items() if hasattr(base, k)}
        o_updates = {k: v for k, v in updates.items() if k not in b_updates}
        return replace(GroupedInput(replace(base, **b_updates), b3.TARGET_GIT_COMMIT,
                       b3.PRIOR_CLEANUP_SHA256, policy.APPROVAL_SHA256,
                       128 * old.MIB, 1, True, True, True), **o_updates)

    def test_exact_fixture_is_only_eligible(self):
        result = b3.evaluate(self.item())
        self.assertEqual(result["decision"], "POLICY_ELIGIBLE_NOT_READY")
        self.assertFalse(result["ready_published"])

    def test_negative_matrix(self):
        cases = (("window_id", old.WINDOW), ("target_request_sha256", "0" * 64),
                 ("request_git_commit", "0" * 40), ("prior_cleanup_sha256", "0" * 64),
                 ("approval_sha256", "0" * 64), ("raw_window_bytes", 128 * old.MIB - 1),
                 ("range_count", 2), ("all_ranges_bound_and_current", False),
                 ("workspace_available_bytes", 15 * old.GIB),
                 ("share_available_bytes", 40 * old.GIB),
                 ("memory_available_bytes", 63 * old.GIB),
                 ("candidate_root_idle", False), ("scheduled_readers_clear", False),
                 ("lane_final_closure_verified", False), ("lane_physical_clear", False),
                 ("copy_lease_authorized", False), ("sole_source_sender", False),
                 ("sole_target_receiver", False), ("source_unlink_requested", True),
                 ("source_signed_ready", True), ("operation", "TLS_V10_RELEASE"),
                 ("policy_id", old.POLICY_ID), ("source_root", "/tmp/wrong"),
                 ("planned_bridge_staged_bytes", 257 * old.MIB))
        for key, value in cases:
            with self.subTest(key=key):
                self.assertEqual(b3.evaluate(self.item(**{key: value}))["decision"],
                                 "RESOURCE_HOLD")


if __name__ == "__main__":
    unittest.main()
