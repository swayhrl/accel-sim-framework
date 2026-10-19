#!/usr/bin/env python3
"""Finite synthetic P9 exact-release policy tests; never delete originals."""

import json

import tls_v10_p9_exact_release_gate as gate
import tls_v10_copy_only16g_gate as copy
import tls_v10_copy_only20g_gate as old


CASES = [
    ("P_full_exact141_native", {}, True, copy.COPY_FLOOR),
    ("N_copy_id_not_release", {"policy_id": copy.POLICY_ID}, False, old.DEFAULT_FLOOR),
    ("N_other_group", {"group": "P9_MATRIX_V2"}, False, copy.COPY_FLOOR),
    ("N_other_source", {"source_root": "/workspace/worktrees/accel-sim-c2p-cache"}, False, copy.COPY_FLOOR),
    ("N_other_namespace", {"source_namespace": "mnt:[1]"}, False, copy.COPY_FLOOR),
    ("N_wrong_selector", {"selector_sha256": "0" * 64}, False, copy.COPY_FLOOR),
    ("N_wrong_inventory", {"file_inventory_sha256": "0" * 64}, False, copy.COPY_FLOOR),
    ("N_wrong_manifest", {"canonical_manifest_sha256": "0" * 64}, False, copy.COPY_FLOOR),
    ("N_wrong_target", {"target_root_native164": "/tmp"}, False, copy.COPY_FLOOR),
    ("N_wrong_txid", {"txid": "wrong"}, False, copy.COPY_FLOOR),
    ("N_only_chunk_restore", {"native_full_restored_count": 0}, False, copy.COPY_FLOOR),
    ("N_140_of141", {"native_full_restored_count": 140}, False, copy.COPY_FLOOR),
    ("N_source_missing", {"source_present_count": 140}, False, copy.COPY_FLOOR),
    ("N_missing_dir", {"restored_directory_metadata_count": 3}, False, copy.COPY_FLOOR),
    ("N_changed_sha", {"all_path_size_sha_join": False}, False, copy.COPY_FLOOR),
    ("N_file_metadata", {"all_numeric_file_metadata_join": False}, False, copy.COPY_FLOOR),
    ("N_directory_metadata", {"all_numeric_directory_metadata_join": False}, False, copy.COPY_FLOOR),
    ("N_archive_not_current", {"target_archive_durable_and_current": False}, False, copy.COPY_FLOOR),
    ("N_native_not_absent", {"target_restore_independent_absent_destination": False}, False, copy.COPY_FLOOR),
    ("N_target_readback", {"target_git_raw_readback": False}, False, copy.COPY_FLOOR),
    ("N_source_identity", {"source_all_file_fresh_content_and_identity": False}, False, copy.COPY_FLOOR),
    ("N_new_file", {"no_unselected_or_new_file": False}, False, copy.COPY_FLOOR),
    ("N_link", {"no_symlink_hardlink_or_traversal": False}, False, copy.COPY_FLOOR),
    ("N_reader", {"current_and_scheduled_readers_clear": False}, False, copy.COPY_FLOOR),
    ("N_lease", {"lease_and_lane_clear": False}, False, copy.COPY_FLOOR),
    ("N_unqualified_tool", {"source_release_tool_fixture_qualified": False}, False, copy.COPY_FLOOR),
    ("N_no_intent", {"journal_intent_fsync_before_unlink_and_done_ready": False}, False, copy.COPY_FLOOR),
    ("N_crash_reconcile", {"crash_reconciliation_qualified": False}, False, copy.COPY_FLOOR),
    ("N_stale", {"snapshot_age_seconds": 31}, False, copy.COPY_FLOOR),
    ("N_below16", {"workspace_f_bavail_bytes": copy.COPY_FLOOR - 1}, False, copy.COPY_FLOOR),
    ("N_exact16_control", {"workspace_f_bavail_bytes": copy.COPY_FLOOR, "projected_control_write_bytes": 1}, False, copy.COPY_FLOOR),
    ("N_share", {"share_f_bavail_bytes": old.SHARE_FLOOR - 1}, False, copy.COPY_FLOOR),
    ("N_ram", {"memory_available_bytes": old.RAM_FLOOR - 1}, False, copy.COPY_FLOOR),
]


def run():
    results = []
    for name, updates, eligible, floor in CASES:
        decision = gate.evaluate(gate.synthetic_input(**updates))
        expected = "RELEASE_ELIGIBLE_NOT_RELEASED" if eligible else "RELEASE_HOLD"
        assert decision["decision"] == expected, (name, decision)
        assert decision["effective_workspace_floor_bytes"] == floor, name
        assert decision["source_unlink_authorized_by_this_evaluator"] is False, name
        results.append({"case": name, "expected": expected, "observed": decision["decision"],
                        "reasons": decision["reasons"], "pass": True})
    return results


if __name__ == "__main__":
    from datetime import datetime, timezone
    import hashlib
    import os
    from pathlib import Path
    import sys

    rows = run()
    here = Path(__file__).resolve().parent
    receipt = here / "TLS_V10_P9_PUBLIC_EXACT_RELEASE_POLICY_TEST_RECEIPT.json"
    if sys.argv[1:] == ["--write-receipt"]:
        payload = {
            "schema": "TLS_V10_P9_PUBLIC_EXACT_RELEASE_POLICY_TEST_RECEIPT_V1",
            "at_utc": datetime.now(timezone.utc).isoformat(),
            "policy_id": copy.RELEASE_POLICY_ID,
            "authority_sha256": copy.AUTHORITY_SHA256,
            "approval_sha256": copy.APPROVAL_SHA256,
            "gate_code_sha256": hashlib.sha256((here / "tls_v10_p9_exact_release_gate.py").read_bytes()).hexdigest(),
            "tests": rows, "passed": len(rows), "failed": 0,
            "synthetic_only": True,
            "real_source_release_tool_qualified": False,
            "full_164_archive_and_native_restore_verified": False,
            "source_files_released": 0,
        }
        with receipt.open("x") as out:
            json.dump(payload, out, sort_keys=True, indent=2)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
    elif sys.argv[1:]:
        raise SystemExit("usage: test_tls_v10_p9_exact_release_gate.py [--write-receipt]")
    print(json.dumps({"passed": len(rows), "failed": 0,
                      "synthetic_only": True, "real_release_authorized": False}))
