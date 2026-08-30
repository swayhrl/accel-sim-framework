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
    assert lane_d.longest_burst(records, "slice", "start_cycle", "descriptor_avg", 230) == 2


def _record(**overrides):
    record = {"workload": "scan", "variant": "B0-Legacy", "core_sha": "core", "framework_sha": "fw",
              "frequency_mhz": 850, "trace_identity": "trace", "descriptor_capacity": 256,
              "l1_config_class": "BASE", "config_hash": "base", "cycles": 100,
              "descriptor_need": 1, "descriptor_block": 1, "descriptor_occ_avg": 1.0,
              "line_mshr_need": 1, "line_mshr_block": 0, "line_mshr_occ_avg": 1.0,
              "l1_mshr_entry_fail": 0, "l1_missq_full": 0, "l1_bank_latency_conflict": 0,
              "wad_full": 0, "wad_hazard": 0, "bank_conflict_ops": 0, "bank_wait_cycles": 0,
              "l2_to_dram_full": 0, "scheduler_causal_block": 0, "dram_read_bytes": 0,
              "dram_write_bytes": 0, "dram_bandwidth_util": 0.0, "descriptor_high_burst_windows": 0,
              "scheduler_high_burst_windows": 0, "channel_cv_p95": 0.0, "cell": "D256_BASE"}
    record.update(overrides)
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
    same_dim_other_config = _record(cell="OTHER", config_hash="other")
    assert lane_d.pair_status(base, same_dim_other_config) == "REJECTED_UNDECLARED_CONFIG_MISMATCH"
    only_d512 = _record(cell="D512_BASE", descriptor_capacity=512, config_hash="d512")
    assert lane_d.make_deltas([only_d512])[0]["comparison_status"] == "MISSING_D256_BASELINE"


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
