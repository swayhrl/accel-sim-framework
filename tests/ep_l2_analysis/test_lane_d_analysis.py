#!/usr/bin/env python3
"""Small deterministic regression fixtures for Lane-D analysis semantics."""
import importlib.util
import sys
from pathlib import Path

MODULE = Path(__file__).parents[2] / "docs/ep_l2/analysis/lane_d_analysis.py"
SPEC = importlib.util.spec_from_file_location("lane_d_analysis", MODULE)
lane_d = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = lane_d
SPEC.loader.exec_module(lane_d)


def test_nearest_rank_distribution_fixture():
    # Nearest-rank: p50=3 and p95=5 for this five-value fixture.
    records = [{"v": str(value)} for value in (1, 2, 3, 4, 5)]
    actual = lane_d.distribution(records, "v", capacity=5)
    assert actual == {"avg": 3.0, "p50": 3.0, "p95": 5.0, "max": 5.0,
                      "near_full_fraction": 1 / 5, "full_fraction": 1 / 5}


def test_missing_is_not_zero():
    assert lane_d.distribution([{"v": ""}], "v")["avg"] == lane_d.NA
    assert lane_d.field_total([{"v": ""}], "v") == lane_d.NA


def test_burst_requires_consecutive_windows_per_stream():
    records = [
        {"slice": "0", "start_cycle": "0", "descriptor_avg": "240"},
        {"slice": "0", "start_cycle": "5000", "descriptor_avg": "240"},
        {"slice": "0", "start_cycle": "10000", "descriptor_avg": "0"},
        {"slice": "1", "start_cycle": "0", "descriptor_avg": "240"},
    ]
    assert lane_d.longest_burst(records, "slice", "start_cycle", "descriptor_avg", 230, 5000) == 2


def test_burst_gap_breaks_a_run():
    records = [
        {"slice": "0", "start_cycle": "0", "descriptor_avg": "240"},
        {"slice": "0", "start_cycle": "10000", "descriptor_avg": "240"},
    ]
    assert lane_d.longest_burst(records, "slice", "start_cycle", "descriptor_avg", 230, 5000) == 1


def test_window_key_audit_rejects_duplicate_and_missing_stream_windows():
    duplicate = [{"slice": "0", "start_cycle": "0"}, {"slice": "0", "start_cycle": "0"}]
    assert lane_d.validate_window_stream(duplicate, "slice", "start_cycle", 1, 5000, 2) == "FAIL_DUPLICATE_STREAM_WINDOW_KEY"
    missing = [{"slice": "0", "start_cycle": "0"}, {"slice": "0", "start_cycle": "10000"}]
    assert lane_d.validate_window_stream(missing, "slice", "start_cycle", 1, 5000, 3) == "FAIL_MISSING_OR_GAPPED_STREAM_WINDOW"


def _record(**overrides):
    record = {"workload": "scan", "variant": "B0-Legacy", "core_sha": "core", "framework_sha": "fw",
              "frequency_mhz": 850, "trace_identity": "trace", "descriptor_capacity": 256,
              "l1_config_class": "BASE", "config_hash": "base", "cycles": 100,
              "descriptor_need": 1, "descriptor_block": 1, "descriptor_occ_avg": 1.0,
              "line_mshr_need": 1, "line_mshr_block": 0, "line_mshr_occ_avg": 1.0,
              "l1_mshr_entry_fail": 0, "l1_missq_full": 0, "l1_bank_latency_conflict": 0,
              "wad_full": 0, "wad_hazard": 0, "bank_conflict_ops": 0, "bank_wait_cycles": 0,
              "l2_to_dram_full": 0, "scheduler_causal_block": 0, "dram_read_bytes": 0,
              "dram_write_bytes": 0, "lower_admission_byte_rate_norm": 0.0, "native_dram_data_bus_util_weighted_mean": 0.0,
              "descriptor_longest_high_average_window_run": 0, "scheduler_longest_high_average_window_run": 0,
              "channel_traffic_conditioned_cv_p95": 0.0, "cell": "D256_BASE"}
    record.update(overrides)
    allowed = lane_d.expected_allowed_config_fields(record["descriptor_capacity"], record["l1_config_class"])
    effective = {"descriptor_pool_size": 256, "descriptor_per_line_cap": 32, "line_mshr_entries": 128,
                 "l1_mshr_entries": 512, "l1_merge_cap": 8, "l1_missq_entries": 16, "l1_bank_count": 4,
                 "frequency_mhz": 850}
    if "descriptor_pool_size" in allowed:
        effective["descriptor_pool_size"] = record["descriptor_capacity"]
    if "l1_mshr_entries" in allowed:
        effective.update({"l1_mshr_entries": 1024, "l1_merge_cap": 32, "l1_missq_entries": 64})
    if "l1_bank_count" in allowed:
        effective["l1_bank_count"] = 8
    record["_contract"] = {"schema": "EP_L2_CALIBRATION_CONTRACT_V2", "semantic_base_id": "base", "base_core_sha": "core", "base_framework_sha": "fw",
                           "candidate_core_sha": record["core_sha"], "candidate_framework_sha": record["framework_sha"],
                           "equivalence_gate": {"id": "gate", "status": "PASS", "evidence_path": "evidence"},
                           "allowed_source_delta_class": "NONE", "allowed_config_fields": sorted(allowed),
                           "effective_config": effective, "runtime_config_composite_sha256": record["config_hash"],
                           "config_delta_gate": {"status": "PASS", "evidence_path": "config-evidence"}}
    return record


def test_calibration_pairing_accepts_only_declared_dimensions():
    base = _record()
    d512 = _record(cell="D512_BASE", descriptor_capacity=512, config_hash="d512", cycles=80)
    assert lane_d.pair_status(base, d512) == "COMPATIBLE_DECLARED_CELL_DELTA"
    assert lane_d.make_deltas([base, d512])[0]["cycle_speedup"] == 1.25


def test_meta_and_bank_cells_pair_against_d256_base():
    base = _record()
    meta = _record(cell="D256_META_HR", l1_config_class="META_HR", config_hash="meta")
    bank = _record(cell="D256_BANK_HR", l1_config_class="BANK_HR", config_hash="bank")
    deltas = lane_d.make_deltas([base, meta, bank])
    assert [row["comparison_status"] for row in deltas] == [
        "COMPATIBLE_DECLARED_CELL_DELTA", "COMPATIBLE_DECLARED_CELL_DELTA"]


def test_provenance_mismatch_and_missing_baseline_are_visible():
    base = _record()
    wrong_trace = _record(cell="D512_BASE", descriptor_capacity=512, config_hash="d512", trace_identity="other")
    assert lane_d.pair_status(base, wrong_trace) == "REJECTED_TRACE_IDENTITY_MISMATCH"
    only_d512 = _record(cell="D512_BASE", descriptor_capacity=512, config_hash="d512")
    assert lane_d.make_deltas([only_d512])[0]["comparison_status"] == "MISSING_D256_BASELINE"


def test_reviewed_equivalent_changed_sha_is_accepted():
    base = _record()
    candidate = _record(cell="D512_BASE", descriptor_capacity=512, config_hash="d512", core_sha="new-core", framework_sha="new-fw")
    candidate["_contract"].update({"candidate_core_sha": "new-core", "candidate_framework_sha": "new-fw", "allowed_source_delta_class": "TELEMETRY_GENERALIZATION_EQUIVALENT"})
    assert lane_d.pair_status(base, candidate) == "COMPATIBLE_DECLARED_CELL_DELTA"


def test_changed_sha_without_equivalence_and_wrong_lineage_are_rejected():
    base = _record()
    candidate = _record(cell="D512_BASE", descriptor_capacity=512, config_hash="d512", core_sha="new-core", framework_sha="new-fw")
    candidate["_contract"].update({"candidate_core_sha": "new-core", "candidate_framework_sha": "new-fw", "equivalence_gate": {"id": "", "status": "PENDING", "evidence_path": ""}})
    assert lane_d.pair_status(base, candidate) == "REJECTED_CHANGED_SHA_WITHOUT_PASS_EQUIVALENCE"
    candidate["_contract"].update({"equivalence_gate": {"id": "gate", "status": "PASS", "evidence_path": "evidence"}, "allowed_source_delta_class": "EQUIVALENT", "base_core_sha": "wrong"})
    assert lane_d.pair_status(base, candidate) == "REJECTED_BASE_LINEAGE_MISMATCH"


def test_hidden_effective_config_change_is_rejected():
    base = _record()
    candidate = _record(cell="D512_BASE", descriptor_capacity=512, config_hash="d512")
    candidate["_contract"]["effective_config"]["line_mshr_entries"] = 256
    assert lane_d.pair_status(base, candidate) == "REJECTED_UNAUTHORIZED_EFFECTIVE_CONFIG_DIFF"


def test_native_dram_uses_final_complete_snapshot_and_weighted_aggregate():
    # First two-channel snapshot is intentionally incomplete; the final one
    # has unequal command weights, so a last-channel implementation gives .9
    # while the required aggregate is .82.
    lines = [
        "DRAM[0]: header\n", "n_cmd=10 bw_util=0.1\n",
        "DRAM[0]: header\n", "n_cmd=10 bw_util=0.1\n",
        "DRAM[1]: header\n", "n_cmd=90 bw_util=0.9\n",
    ]
    actual = lane_d.native_dram_data_bus_util_from_lines(lines, 2)
    assert actual == {"native_dram_snapshot_status": "PASS_FINAL_COMPLETE_CHANNEL_SNAPSHOT",
                      "native_dram_channels_observed": 2,
                      "native_dram_data_bus_util_weighted_mean": 0.82,
                      "native_dram_data_bus_util_p50": 0.1,
                      "native_dram_data_bus_util_p95": 0.9,
                      "native_dram_data_bus_util_max": 0.9,
                      "native_dram_n_cmd_sum": 100}


def test_native_dram_fails_closed_without_all_channels():
    actual = lane_d.native_dram_data_bus_util_from_lines(["DRAM[0]: header\n", "n_cmd=1 bw_util=0.2\n"], 2)
    assert actual["native_dram_snapshot_status"] == "FAIL_NO_COMPLETE_CHANNEL_SNAPSHOT"
    assert actual["native_dram_data_bus_util_weighted_mean"] == lane_d.NA


def test_runtime_config_contract_binding_rejects_actual_hash_mismatch():
    contract = _record()["_contract"]
    assert lane_d.contract_binding_status(contract, "other-hash") == "REJECTED_RUNTIME_CONFIG_HASH_MISMATCH"


def test_runtime_config_contract_binding_accepts_expected_hash_and_gate():
    contract = _record()["_contract"]
    assert lane_d.contract_binding_status(contract, "base") == "PASS_RUNTIME_CONFIG_BOUND"


def test_channel_imbalance_requires_denominator_and_exact_group_alignment():
    missing_denominator = [{"window_start_cycle": "0", "channel": "0", "bandwidth_util_numerator_bytes": "1"}]
    assert lane_d.channel_imbalance(missing_denominator, 1)["all_window_cv_max"] == lane_d.NA
    shifted = [
        {"window_start_cycle": "0", "channel": "0", "bandwidth_util_numerator_bytes": "1", "bandwidth_util_denominator_bytes": "10"},
        {"window_start_cycle": "1", "channel": "1", "bandwidth_util_numerator_bytes": "1", "bandwidth_util_denominator_bytes": "10"},
    ]
    assert lane_d.validate_time_groups(shifted, "channel", "window_start_cycle", 2) == "FAIL_TIME_GROUP_STREAM_ALIGNMENT"
    assert lane_d.channel_imbalance(shifted, 2)["all_window_cv_max"] == lane_d.NA


def test_duplicate_run_detection(monkeypatch, tmp_path):
    cell = lane_d.Cell("D256_BASE", tmp_path, 256, "BASE")
    for variant in ("B0-Legacy", "B0-Banked"):
        path = tmp_path / variant / "placeholder"
        path.mkdir(parents=True)
        (path / "run_status.json").touch()
    duplicate = _record()
    monkeypatch.setattr(lane_d, "artifact_run", lambda _cell, _directory: duplicate)
    try:
        lane_d.discover(cell, None)
    except ValueError as error:
        assert "duplicate" in str(error)
    else:
        raise AssertionError("duplicate run record was accepted")
