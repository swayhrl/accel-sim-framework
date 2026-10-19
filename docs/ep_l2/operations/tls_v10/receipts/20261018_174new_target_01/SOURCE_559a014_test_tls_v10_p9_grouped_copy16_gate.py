#!/usr/bin/env python3
"""Pure synthetic B0002 policy test matrix; no real-world PASS claims."""

from dataclasses import replace
import unittest

import tls_v10_copy_only16g_gate as policy
import tls_v10_copy_only20g_gate as old
import tls_v10_p9_grouped_copy16_gate as grouped


class GroupedGateTests(unittest.TestCase):
    def item(self, **updates):
        b = old.policy_input(policy_id=policy.POLICY_ID,
                             amendment_sha256=policy.AUTHORITY_SHA256,
                             window_id=grouped.WINDOW,
                             target_request_sha256=grouped.REQUEST_SHA256,
                             workspace_available_bytes=17 * old.GIB)
        base_updates = {k: v for k, v in updates.items() if hasattr(b, k)}
        outer_updates = {k: v for k, v in updates.items() if k not in base_updates}
        return replace(grouped.GroupedInput(replace(b, **base_updates),
                       grouped.TARGET_GIT_COMMIT, grouped.PRIOR_CLEANUP_SHA256,
                       policy.APPROVAL_SHA256, 7660873, 34, True, True, True),
                       **outer_updates)

    def test_exact_fixture_eligible_but_not_ready(self):
        result = grouped.evaluate(self.item())
        self.assertEqual(result["decision"], "POLICY_ELIGIBLE_NOT_READY")
        self.assertFalse(result["ready_published"])

    def test_binding_and_resource_fail_closed(self):
        failures = (
            ("window_id", old.WINDOW), ("target_request_sha256", old.TARGET_REQUEST_SHA256),
            ("request_git_commit", "0" * 40), ("prior_cleanup_sha256", "0" * 64),
            ("approval_sha256", "0" * 64), ("selector_sha256", "0" * 64),
            ("manifest_sha256", "0" * 64), ("source_root", "/tmp/other"),
            ("raw_window_bytes", 129 * old.MIB), ("range_count", 129),
            ("all_ranges_bound_and_current", False), ("workspace_available_bytes", 15 * old.GIB),
            ("share_available_bytes", 39 * old.GIB), ("memory_available_bytes", 63 * old.GIB),
            ("candidate_root_idle", False), ("scheduled_readers_clear", False),
            ("lane_final_closure_verified", False), ("lane_physical_clear", False),
            ("copy_lease_authorized", False), ("sole_source_sender", False),
            ("sole_target_receiver", False), ("source_unlink_requested", True),
            ("source_signed_ready", True), ("operation", "TLS_V10_RELEASE"),
            ("policy_id", old.POLICY_ID), ("planned_bridge_staged_bytes", 257 * old.MIB),
        )
        for key, value in failures:
            with self.subTest(key=key):
                self.assertEqual(grouped.evaluate(self.item(**{key: value}))["decision"],
                                 "RESOURCE_HOLD")


if __name__ == "__main__":
    unittest.main()
