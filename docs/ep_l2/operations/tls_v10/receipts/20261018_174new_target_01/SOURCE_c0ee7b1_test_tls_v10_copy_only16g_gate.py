#!/usr/bin/env python3
"""Synthetic positive and fail-closed negative tests for the opt-in 16G gate."""

import tls_v10_copy_only16g_gate as gate
import tls_v10_copy_only20g_gate as old


CASES = [
    ("P_exact_17G", {}, True, gate.COPY_FLOOR),
    ("P_exact16_zero_control", {"workspace_available_bytes": gate.COPY_FLOOR, "planned_overlay_write_bytes": 0}, True, gate.COPY_FLOOR),
    ("N_exact16_one_control", {"workspace_available_bytes": gate.COPY_FLOOR, "planned_overlay_write_bytes": 1}, False, gate.COPY_FLOOR),
    ("N_16_minus_one", {"workspace_available_bytes": gate.COPY_FLOOR - 1, "planned_overlay_write_bytes": 0}, False, gate.COPY_FLOOR),
    ("N_old_snapshot_not_real", {"workspace_available_bytes": gate.COPY_FLOOR - 1, "workspace_total_free_bytes_non_gate": 100 * old.GIB}, False, gate.COPY_FLOOR),
    ("N_old20_id", {"policy_id": old.POLICY_ID}, False, old.DEFAULT_FLOOR),
    ("N_release_id", {"policy_id": gate.RELEASE_POLICY_ID}, False, old.DEFAULT_FLOOR),
    ("N_wrong_approval", {"approval_sha256": "0" * 64}, False, old.DEFAULT_FLOOR),
    ("N_wrong_authority", {"amendment_sha256": "0" * 64}, False, old.DEFAULT_FLOOR),
    ("N_sim", {"operation": "SIMULATION"}, False, old.DEFAULT_FLOOR),
    ("N_build", {"operation": "BUILD"}, False, old.DEFAULT_FLOOR),
    ("N_restore", {"operation": "REVERSE_RESTORE"}, False, old.DEFAULT_FLOOR),
    ("N_unlink", {"source_unlink_requested": True}, False, gate.COPY_FLOOR),
    ("N_other_group", {"group": "P9_MATRIX_V2"}, False, gate.COPY_FLOOR),
    ("N_shared_trace", {"source_asset_class": "SHARED_TRACE"}, False, gate.COPY_FLOOR),
    ("N_unmanifested", {"frozen_manifest_member": False}, False, gate.COPY_FLOOR),
    ("N_wrong_txid", {"txid": "wrong"}, False, gate.COPY_FLOOR),
    ("N_wrong_nonce", {"nonce_or_txid_exact": False}, False, gate.COPY_FLOOR),
    ("N_wrong_selector", {"selector_sha256": "wrong"}, False, gate.COPY_FLOOR),
    ("N_wrong_manifest", {"manifest_sha256": "wrong"}, False, gate.COPY_FLOOR),
    ("N_wrong_target", {"target_root_native164": "/tmp"}, False, gate.COPY_FLOOR),
    ("N_wrong_namespace", {"source_namespace": "mnt:[1]"}, False, gate.COPY_FLOOR),
    ("N_wrong_dev", {"source_dev": 999}, False, gate.COPY_FLOOR),
    ("N_wrong_bridge", {"bridge_dev": 999}, False, gate.COPY_FLOOR),
    ("N_wrong_request", {"target_request_sha256": "wrong"}, False, gate.COPY_FLOOR),
    ("N_stale", {"snapshot_age_seconds": 31}, False, gate.COPY_FLOOR),
    ("N_share", {"share_available_bytes": old.SHARE_FLOOR}, False, gate.COPY_FLOOR),
    ("N_ram", {"memory_available_bytes": old.RAM_FLOOR - 1}, False, gate.COPY_FLOOR),
    ("N_cgroup", {"cgroup_headroom_bytes": 0}, False, gate.COPY_FLOOR),
    ("N_active_lane", {"lane_runs_clear": False}, False, gate.COPY_FLOOR),
    ("N_lane_closure", {"lane_final_closure_verified": False}, False, gate.COPY_FLOOR),
    ("N_lane_pid", {"lane_physical_clear": False}, False, gate.COPY_FLOOR),
    ("N_lease", {"copy_lease_authorized": False}, False, gate.COPY_FLOOR),
    ("N_scan", {"physical_scan_complete": False}, False, gate.COPY_FLOOR),
    ("N_current_reader", {"candidate_root_idle": False}, False, gate.COPY_FLOOR),
    ("N_future_reader", {"scheduled_readers_clear": False}, False, gate.COPY_FLOOR),
    ("N_changed_source", {"first_source_identity_ok": False}, False, gate.COPY_FLOOR),
    ("N_missing_sha", {"first_source_sha_refreshed": False}, False, gate.COPY_FLOOR),
    ("N_target_request", {"target_request_present_and_exact": False}, False, gate.COPY_FLOOR),
    ("N_bridge_size", {"planned_bridge_staged_bytes": old.MAX_BRIDGE_STAGED + 1}, False, gate.COPY_FLOOR),
    ("N_raw_range", {"planned_raw_range_bytes": gate.MAX_RAW_RANGE + 1}, False, gate.COPY_FLOOR),
    ("N_rate", {"planned_rate_bytes_per_second": old.MAX_RATE_BPS + 1}, False, gate.COPY_FLOOR),
    ("N_second_sender", {"sole_source_sender": False}, False, gate.COPY_FLOOR),
    ("N_second_receiver", {"sole_target_receiver": False}, False, gate.COPY_FLOOR),
    ("N_premature_ready", {"source_signed_ready": True}, False, gate.COPY_FLOOR),
]


def run():
    rows = []
    for name, changes, eligible, expected_floor in CASES:
        actual = gate.evaluate(gate.policy_input(**changes))
        expected = "POLICY_ELIGIBLE_NOT_READY" if eligible else "RESOURCE_HOLD"
        assert actual["decision"] == expected, (name, actual)
        assert actual["effective_workspace_floor_bytes"] == expected_floor, name
        assert not actual["ready_published"] and not actual["source_unlink_authorized"], name
        rows.append({"case": name, "expected": expected, "observed": actual["decision"], "reasons": actual["reasons"], "pass": True})
    assert old.evaluate(old.policy_input())["effective_workspace_floor_bytes"] == old.COPY_ONLY_FLOOR
    assert old.evaluate(old.policy_input(operation="BUILD"))["effective_workspace_floor_bytes"] == old.DEFAULT_FLOOR
    return rows


if __name__ == "__main__":
    from datetime import datetime, timezone
    import hashlib
    import json
    import os
    from pathlib import Path
    import sys

    rows = run()
    here = Path(__file__).resolve().parent
    receipt = here / "TLS_V10_COPY_ONLY_16G_POLICY_TEST_RECEIPT.json"
    if len(sys.argv) == 2 and sys.argv[1] == "--write-receipt":
        payload = {
            "schema": "TLS_V10_COPY_ONLY_16G_POLICY_TEST_RECEIPT_V1",
            "at_utc": datetime.now(timezone.utc).isoformat(),
            "policy_id": gate.POLICY_ID,
            "authority_sha256": gate.AUTHORITY_SHA256,
            "user_approval_sha256": gate.APPROVAL_SHA256,
            "gate_code_sha256": hashlib.sha256((here / "tls_v10_copy_only16g_gate.py").read_bytes()).hexdigest(),
            "test_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "historical_20g_gate_sha256_unchanged": hashlib.sha256((here / "tls_v10_copy_only20g_gate.py").read_bytes()).hexdigest(),
            "original_default_floor_bytes_unchanged": old.DEFAULT_FLOOR,
            "copy_only_floor_bytes": gate.COPY_FLOOR,
            "synthetic_cases": rows,
            "passed": len(rows), "failed": 0,
            "real_source_gate_pass": False, "source_ready_published": False,
            "scientific_payload_transferred_bytes": 0, "source_unlink_count": 0,
        }
        with receipt.open("x") as out:
            json.dump(payload, out, sort_keys=True, indent=2)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
    elif len(sys.argv) != 1:
        raise SystemExit("usage: test_tls_v10_copy_only16g_gate.py [--write-receipt]")
    print(json.dumps({"passed": len(rows), "failed": 0, "synthetic_only": True,
                      "receipt": str(receipt) if receipt.exists() else None}))
