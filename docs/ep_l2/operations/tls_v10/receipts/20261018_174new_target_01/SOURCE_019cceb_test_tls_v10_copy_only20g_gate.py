#!/usr/bin/env python3
"""Finite synthetic policy tests; never touch a frozen TLS science file."""

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import tls_v10_copy_only20g_gate as gate


HERE = Path(__file__).resolve().parent
RECEIPT = HERE / "TLS_V10_COPY_ONLY_20G_POLICY_TEST_RECEIPT.json"

# Each case has synthetic input only; the real read-only snapshot is separate.
CASES = [
    ("P01_exact_copy_only_21g", {}, "POLICY_ELIGIBLE_NOT_READY", gate.COPY_ONLY_FLOOR, None),
    ("N01_previous_actual_17_93g", {"workspace_available_bytes": 19253473280},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "WORKSPACE_F_BAVAIL_OR_PROJECTED_HEADROOM_BELOW_FLOOR"),
    ("N02_exact20_with32m_writes", {"workspace_available_bytes": gate.COPY_ONLY_FLOOR,
                                     "planned_overlay_write_bytes": gate.MAX_OVERLAY_WRITES},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "WORKSPACE_F_BAVAIL_OR_PROJECTED_HEADROOM_BELOW_FLOOR"),
    ("P02_exact20_zero_overlay_all_other_gates", {"workspace_available_bytes": gate.COPY_ONLY_FLOOR,
                                                    "planned_overlay_write_bytes": 0},
     "POLICY_ELIGIBLE_NOT_READY", gate.COPY_ONLY_FLOOR, None),
    ("N03_simulation_default48", {"operation": "SIMULATION"},
     "RESOURCE_HOLD", gate.DEFAULT_FLOOR, "NOT_EXACT_COPY_ONLY_OPT_IN_DEFAULT_48G"),
    ("N04_build_default48", {"operation": "BUILD"},
     "RESOURCE_HOLD", gate.DEFAULT_FLOOR, "NOT_EXACT_COPY_ONLY_OPT_IN_DEFAULT_48G"),
    ("N05_release_default48", {"operation": "SOURCE_RELEASE"},
     "RESOURCE_HOLD", gate.DEFAULT_FLOOR, "NOT_EXACT_COPY_ONLY_OPT_IN_DEFAULT_48G"),
    ("N06_reverse_restore_default48", {"operation": "REVERSE_RESTORE"},
     "RESOURCE_HOLD", gate.DEFAULT_FLOOR, "NOT_EXACT_COPY_ONLY_OPT_IN_DEFAULT_48G"),
    ("N07_missing_policy_id", {"policy_id": ""},
     "RESOURCE_HOLD", gate.DEFAULT_FLOOR, "NOT_EXACT_COPY_ONLY_OPT_IN_DEFAULT_48G"),
    ("N08_wrong_amendment_sha", {"amendment_sha256": "0" * 64},
     "RESOURCE_HOLD", gate.DEFAULT_FLOOR, "NOT_EXACT_COPY_ONLY_OPT_IN_DEFAULT_48G"),
    ("N09_wrong_txid", {"txid": "wrong"},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "SOURCE_OR_TRANSACTION_IDENTITY_MISMATCH"),
    ("N10_wrong_selector", {"selector_sha256": "wrong"},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "SOURCE_OR_TRANSACTION_IDENTITY_MISMATCH"),
    ("N11_wrong_target_root", {"target_root_native164": "/tmp/wrong"},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "SOURCE_OR_TRANSACTION_IDENTITY_MISMATCH"),
    ("N12_wrong_manifest", {"manifest_sha256": "wrong"},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "SOURCE_OR_TRANSACTION_IDENTITY_MISMATCH"),
    ("N13_wrong_window", {"window_id": "B0002"},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "SOURCE_OR_TRANSACTION_IDENTITY_MISMATCH"),
    ("N14_wrong_namespace", {"source_namespace": "mnt:[1]"},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "SOURCE_OR_TRANSACTION_IDENTITY_MISMATCH"),
    ("N15_wrong_source_dev", {"source_dev": 2128},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "SOURCE_OR_TRANSACTION_IDENTITY_MISMATCH"),
    ("N16_wrong_bridge_dev", {"bridge_dev": 156},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "SOURCE_OR_TRANSACTION_IDENTITY_MISMATCH"),
    ("N17_wrong_source_branch", {"source_branch": "hrl/ops-174-source-audit-exec-v1"},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "SOURCE_OR_TRANSACTION_IDENTITY_MISMATCH"),
    ("N18_f_bfree_not_substitute", {"workspace_available_bytes": 19253473280,
                                    "workspace_total_free_bytes_non_gate": 200 * gate.GIB},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "WORKSPACE_F_BAVAIL_OR_PROJECTED_HEADROOM_BELOW_FLOOR"),
    ("N19_share_under40", {"share_available_bytes": gate.SHARE_FLOOR - 1},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "SHARE_F_BAVAIL_OR_PROJECTED_HEADROOM_BELOW_FLOOR"),
    ("N20_ram_under64", {"memory_available_bytes": gate.RAM_FLOOR - 1},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "RAM_OR_CGROUP_HEADROOM"),
    ("N21_cgroup_short", {"cgroup_headroom_bytes": gate.MIB},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "RAM_OR_CGROUP_HEADROOM"),
    ("N22_registry_stale", {"lane_registry_fresh": False},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "LANE_REGISTRY_OR_LEASE_NOT_FRESH_CLEAR"),
    ("N23_active_run", {"lane_runs_clear": False},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "LANE_REGISTRY_OR_LEASE_NOT_FRESH_CLEAR"),
    ("N24_active_lease", {"lane_leases_clear": False},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "LANE_REGISTRY_OR_LEASE_NOT_FRESH_CLEAR"),
    ("N25_scan_incomplete", {"physical_scan_complete": False},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "PHYSICAL_OR_SCHEDULED_READER_NOT_PROVEN_CLEAR"),
    ("N26_candidate_active", {"candidate_root_idle": False},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "PHYSICAL_OR_SCHEDULED_READER_NOT_PROVEN_CLEAR"),
    ("N27_scheduled_reader", {"scheduled_readers_clear": False},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "PHYSICAL_OR_SCHEDULED_READER_NOT_PROVEN_CLEAR"),
    ("N28_identity_changed", {"first_source_identity_ok": False},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "FIRST_SOURCE_IDENTITY_OR_SHA_NOT_FRESH"),
    ("N29_sha_not_refreshed", {"first_source_sha_refreshed": False},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "FIRST_SOURCE_IDENTITY_OR_SHA_NOT_FRESH"),
    ("N30_target_request_missing", {"target_request_present_and_exact": False},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "PINNED_TARGET_WINDOW_REQUEST_NOT_EXACT"),
    ("N31_bridge_over256m", {"planned_bridge_staged_bytes": gate.MAX_BRIDGE_STAGED + 1},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "BRIDGE_STAGING_LIMIT"),
    ("N32_rate_over30mps", {"planned_rate_bytes_per_second": gate.MAX_RATE_BPS + 1},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "RATE_OR_SINGLE_STREAM_LIMIT"),
    ("N33_second_sender", {"sole_source_sender": False},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "RATE_OR_SINGLE_STREAM_LIMIT"),
    ("N34_second_receiver", {"sole_target_receiver": False},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "RATE_OR_SINGLE_STREAM_LIMIT"),
    ("N35_overlay_over32m", {"planned_overlay_write_bytes": gate.MAX_OVERLAY_WRITES + 1},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "OVERLAY_CONTROL_WRITE_BUDGET_INVALID"),
    ("N36_unlink_attempt", {"source_unlink_requested": True},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "SOURCE_UNLINK_OUTSIDE_COPY_ONLY_POLICY"),
    ("N37_source_ready_claim_in_evaluator", {"source_signed_ready": True},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "EVALUATOR_CANNOT_ACCEPT_OR_ISSUE_SOURCE_READY"),
    ("N38_p9_matrix_v2", {"group": "P9_MATRIX_V2"},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "SOURCE_OR_TRANSACTION_IDENTITY_MISMATCH"),
    ("N39_mixed_c2p", {"source_asset_class": "MIXED_TLS_C2P"},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "SOURCE_OR_TRANSACTION_IDENTITY_MISMATCH"),
    ("N40_shared_trace", {"source_asset_class": "SHARED_TRACE"},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "SOURCE_OR_TRANSACTION_IDENTITY_MISMATCH"),
    ("N41_modified_code", {"source_asset_class": "CODE_KEEP"},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "SOURCE_OR_TRANSACTION_IDENTITY_MISMATCH"),
    ("N42_symlink_ambiguous", {"source_asset_class": "SYMLINK_AMBIGUOUS"},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "SOURCE_OR_TRANSACTION_IDENTITY_MISMATCH"),
    ("N43_stale_source_snapshot", {"snapshot_age_seconds": 31},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "SOURCE_RESOURCE_SNAPSHOT_STALE"),
    ("N44_copy_lease_not_authorized", {"copy_lease_authorized": False},
     "RESOURCE_HOLD", gate.COPY_ONLY_FLOOR, "LANE_REGISTRY_OR_LEASE_NOT_FRESH_CLEAR"),
]


def run():
    results = []
    for name, updates, expected_decision, expected_floor, expected_reason in CASES:
        actual = gate.evaluate(gate.policy_input(**updates))
        passed = (actual["decision"] == expected_decision and
                  actual["effective_workspace_floor_bytes"] == expected_floor and
                  (expected_reason is None or expected_reason in actual["reasons"]) and
                  actual["ready_published"] is False and
                  actual["source_unlink_authorized"] is False and
                  actual["payload_transfer_authorized_by_this_evaluator"] is False)
        results.append({"case": name, "synthetic_overrides": updates,
                        "expected_decision": expected_decision,
                        "observed_decision": actual["decision"],
                        "expected_workspace_floor_bytes": expected_floor,
                        "observed_workspace_floor_bytes":
                            actual["effective_workspace_floor_bytes"],
                        "expected_reason": expected_reason,
                        "observed_reasons": actual["reasons"], "pass": passed})
        if not passed:
            raise AssertionError(f"failed policy case {name}: {actual}")
    eligible = gate.evaluate(gate.policy_input())
    if gate.target_can_receive(eligible, signed_source_ready=False):
        raise AssertionError("target accepted without source READY")
    results.append({"case": "N45_target_waits_without_signed_ready",
                    "expected_decision": "WAITING", "observed_decision": "WAITING",
                    "pass": True})
    return results


if __name__ == "__main__":
    rows = run()
    receipt = {
        "schema": "TLS_V10_COPY_ONLY_20G_POLICY_TEST_RECEIPT_V1",
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "actual_policy_caller": "tls_v10_copy_only20g_gate.evaluate(GateInput)",
        "policy_id": gate.POLICY_ID,
        "amendment_sha256": gate.AMENDMENT_SHA256,
        "original_default_workspace_floor_bytes_unchanged": gate.DEFAULT_FLOOR,
        "scoped_copy_only_workspace_floor_bytes": gate.COPY_ONLY_FLOOR,
        "cases": rows, "passed": len(rows), "failed": 0,
        "synthetic_only": True, "science_files_read_or_hashed": 0,
        "source_ready_published": False, "scientific_payload_transferred_bytes": 0,
        "source_unlink_count": 0,
    }
    if len(sys.argv) == 2 and sys.argv[1] == "--write-receipt":
        with RECEIPT.open("x") as out:
            json.dump(receipt, out, sort_keys=True, indent=2)
            out.write("\n")
            out.flush()
            import os
            os.fsync(out.fileno())
    elif len(sys.argv) != 1:
        raise SystemExit("usage: test_tls_v10_copy_only20g_gate.py [--write-receipt]")
    print(json.dumps({"passed": len(rows), "failed": 0,
                      "receipt": str(RECEIPT) if RECEIPT.exists() else None}, sort_keys=True))
