#!/usr/bin/env python3
import csv
import json
import math
import tempfile
import unittest
from pathlib import Path

from refill_consumer import (
    METRICS,
    RefillConsumerError,
    analyze_timing_rows,
    consume_ncu,
)


INPUT_SHA = "1" * 64
OUTPUT_SHA = "2" * 64
TARGET_KERNEL = "target_gemm_kernel"
PRESSURE_KERNEL = "pressure_read_kernel"
POINT = ("TEXT", "up_proj", 1, "RAW_FP16")


def timing_rows(point=POINT, reps=3):
    rows = []
    for call_index in range(1, 7):
        for rep in range(reps):
            rows.append(
                {
                    "domain": point[0],
                    "role": point[1],
                    "M": str(point[2]),
                    "implementation": point[3],
                    "refill_call_index": f"K{call_index}",
                    "rep": str(rep),
                    "timing_ms": str(12.0 - call_index + rep / 100.0),
                    "input_sha256": INPUT_SHA,
                    "output_sha256": OUTPUT_SHA,
                }
            )
    return rows


def write_base(path, target_range, values=(100, 200, 300), *, bad_unit=None,
               omit_metric=None, pressure_inside=False):
    header = [
        "ID", "Process ID", "Kernel Name", "profiler__replayer_passes",
        "NVTX Push/Pop_Range", *METRICS,
    ]
    if omit_metric:
        header.remove(omit_metric)
    units = ["", "", "", "", "", *["byte" for _ in METRICS]]
    if omit_metric:
        units.pop(5 + METRICS.index(omit_metric))
    if bad_unit:
        units[header.index(bad_unit)] = "Kbyte"
    mapping = dict(zip(METRICS, values))
    rows = [[
        "1", "123", TARGET_KERNEL, "1", target_range,
        *[str(mapping[metric]) for metric in METRICS if metric != omit_metric],
    ]]
    if pressure_inside:
        rows.append([
            "2", "123", PRESSURE_KERNEL, "1", target_range,
            *["1" for metric in METRICS if metric != omit_metric],
        ])
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerow(units)
        writer.writerows(rows)


def write_session(path, target_range, *, replay="application", cache="none",
                  metrics=METRICS):
    path.write_text(
        f"ncu --replay-mode {replay} --cache-control {cache} "
        f"--nvtx-include {target_range}/ --metrics {','.join(metrics)}\n",
        encoding="utf-8",
    )


def write_profile(path, target_range, call_index, **changes):
    receipt = {
        "status": "PASS",
        "role": "up_proj",
        "M": 1,
        "implementation": "RAW_FP16",
        "refill_call_index": call_index,
        "range": target_range,
        "input_sha256": INPUT_SHA,
        "output_sha256": OUTPUT_SHA,
    }
    receipt.update(changes)
    path.write_text("==PROF== synthetic\n" + json.dumps(receipt) + "\n", encoding="utf-8")


class TimingTests(unittest.TestCase):
    def test_stats_ratios_recovery_and_nongating_monotonicity(self):
        result = analyze_timing_rows(
            timing_rows(), expected_reps=3, expected_points=frozenset({POINT})
        )
        point = result["points"][0]
        self.assertEqual(point["call_statistics"]["K1"]["sample_count"], 3)
        self.assertAlmostEqual(point["timing_ratios_over_K1"]["K1"], 1.0)
        self.assertGreater(point["K1_to_K6_fractional_recovery"], 0)
        self.assertTrue(point["monotonicity_diagnostic"]["is_nonincreasing"])
        self.assertFalse(point["monotonicity_diagnostic"]["is_pass_gate"])

    def test_missing_K_fails(self):
        rows = [row for row in timing_rows() if row["refill_call_index"] != "K6"]
        with self.assertRaisesRegex(RefillConsumerError, "K matrix mismatch"):
            analyze_timing_rows(rows, expected_reps=3, expected_points=frozenset({POINT}))

    def test_duplicate_rep_fails(self):
        rows = timing_rows()
        rows.append(dict(rows[0]))
        with self.assertRaisesRegex(RefillConsumerError, "duplicate point/K/rep"):
            analyze_timing_rows(rows, expected_reps=3, expected_points=frozenset({POINT}))

    def test_missing_or_wrong_rep_set_fails(self):
        rows = timing_rows()
        rows[0]["rep"] = "9"
        with self.assertRaisesRegex(RefillConsumerError, "rep matrix mismatch"):
            analyze_timing_rows(rows, expected_reps=3, expected_points=frozenset({POINT}))

    def test_input_or_output_SHA_drift_fails(self):
        for field in ("input_sha256", "output_sha256"):
            with self.subTest(field=field):
                rows = timing_rows()
                rows[-1][field] = "3" * 64
                with self.assertRaisesRegex(RefillConsumerError, "SHA drift"):
                    analyze_timing_rows(
                        rows, expected_reps=3, expected_points=frozenset({POINT})
                    )

    def test_nonfinite_timing_fails(self):
        for value in ("nan", "inf", "0"):
            with self.subTest(value=value):
                rows = timing_rows()
                rows[0]["timing_ms"] = value
                with self.assertRaisesRegex(RefillConsumerError, "positive and finite"):
                    analyze_timing_rows(
                        rows, expected_reps=3, expected_points=frozenset({POINT})
                    )

    def test_wrong_point_matrix_fails(self):
        with self.assertRaisesRegex(RefillConsumerError, "timing point matrix mismatch"):
            analyze_timing_rows(
                timing_rows(),
                expected_reps=3,
                expected_points=frozenset({("TEXT", "q_proj", 1, "RAW_FP16")}),
            )

    def test_monotonicity_violation_is_diagnostic_not_failure(self):
        rows = timing_rows()
        for row in rows:
            if row["refill_call_index"] == "K4":
                row["timing_ms"] = "20"
        result = analyze_timing_rows(
            rows, expected_reps=3, expected_points=frozenset({POINT})
        )
        diagnostic = result["points"][0]["monotonicity_diagnostic"]
        self.assertFalse(diagnostic["is_nonincreasing"])
        self.assertGreater(diagnostic["violation_count"], 0)


class NcuTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def add_profile(self, call_index, values=(100, 200, 300), **base_options):
        target = f"C16_E1_REFILL_UP_RAW_K{call_index}"
        stem = f"k{call_index}"
        base = self.root / f"{stem}_BASE.csv"
        session = self.root / f"{stem}_SESSION.csv"
        profile = self.root / f"{stem}_PROFILE.log"
        write_base(base, target, values, **base_options)
        write_session(session, target)
        write_profile(profile, target, call_index)
        spec = {
            "point": "TEXT_UP_M1_RAW_REFILL",
            "domain": "TEXT",
            "role": "up_proj",
            "M": 1,
            "implementation": "RAW_FP16",
            "refill_call_index": call_index,
            "range_name": target,
            "input_sha256": INPUT_SHA,
            "output_sha256": OUTPUT_SHA,
            "expected_pass_count": 1,
            "expected_kernel_names": [TARGET_KERNEL],
            "pressure_kernel_names": [PRESSURE_KERNEL],
            "base_path": base.name,
            "session_path": session.name,
            "profile_path": profile.name,
        }
        return spec

    def consume_three(self):
        specs = [
            self.add_profile(1, (100, 200, 300)),
            self.add_profile(2, (50, 100, 150)),
            self.add_profile(4, (25, 50, 75)),
        ]
        expected = frozenset(("TEXT", "up_proj", 1, "RAW_FP16", k) for k in (1, 2, 4))
        return consume_ncu(
            {"schema_version": 1, "profiles": specs}, self.root,
            expected_points=expected,
        ), specs, expected

    def test_three_source_consume_and_call_ratios(self):
        result, _, _ = self.consume_three()
        self.assertEqual(result["authority"], "DIRECT_RAW_BASE_SESSION_PROFILE_ONLY")
        self.assertIn("refill_call_index", result["semantic_identity_fields"])
        row = next(
            item for item in result["call_ratios"]
            if item["refill_call_index"] == 4 and item["metric_name"] == "dram__bytes.sum"
        )
        self.assertEqual(row["Ki_over_K1"], 0.25)

    def test_duplicate_semantic_call_fails(self):
        spec = self.add_profile(1)
        identity = frozenset({("TEXT", "up_proj", 1, "RAW_FP16", 1)})
        with self.assertRaisesRegex(RefillConsumerError, "duplicate semantic"):
            consume_ncu(
                {"schema_version": 1, "profiles": [spec, dict(spec)]},
                self.root, expected_points=identity,
            )

    def test_profile_call_index_or_SHA_mismatch_fails(self):
        spec = self.add_profile(1)
        identity = frozenset({("TEXT", "up_proj", 1, "RAW_FP16", 1)})
        profile_path = self.root / spec["profile_path"]
        for changes in ({"refill_call_index": 2}, {"input_sha256": "3" * 64}):
            with self.subTest(changes=changes):
                write_profile(profile_path, spec["range_name"], 1, **changes)
                with self.assertRaisesRegex(RefillConsumerError, "PROFILE replay identity mismatch"):
                    consume_ncu(
                        {"schema_version": 1, "profiles": [spec]}, self.root,
                        expected_points=identity,
                    )

    def test_session_replay_cache_range_and_metric_set_are_exact(self):
        cases = (
            ({"replay": "kernel"}, "replay mode"),
            ({"cache": "all"}, "cache control"),
            ({"metrics": METRICS[:-1]}, "metric set"),
        )
        for options, message in cases:
            with self.subTest(options=options):
                spec = self.add_profile(1)
                write_session(self.root / spec["session_path"], spec["range_name"], **options)
                with self.assertRaisesRegex(RefillConsumerError, message):
                    consume_ncu(
                        {"schema_version": 1, "profiles": [spec]}, self.root,
                        expected_points=frozenset({("TEXT", "up_proj", 1, "RAW_FP16", 1)}),
                    )

    def test_missing_metric_or_unit_mismatch_fails(self):
        cases = (
            ({"omit_metric": "dram__bytes.sum"}, "missing required columns"),
            ({"bad_unit": "lts__t_bytes.sum"}, "unit mismatch"),
        )
        for options, message in cases:
            with self.subTest(options=options):
                spec = self.add_profile(1, **options)
                with self.assertRaisesRegex(RefillConsumerError, message):
                    consume_ncu(
                        {"schema_version": 1, "profiles": [spec]}, self.root,
                        expected_points=frozenset({("TEXT", "up_proj", 1, "RAW_FP16", 1)}),
                    )

    def test_pressure_kernel_inside_target_range_fails(self):
        spec = self.add_profile(1, pressure_inside=True)
        with self.assertRaisesRegex(RefillConsumerError, "pressure kernel entered"):
            consume_ncu(
                {"schema_version": 1, "profiles": [spec]}, self.root,
                expected_points=frozenset({("TEXT", "up_proj", 1, "RAW_FP16", 1)}),
            )

    def test_missing_NCU_call_matrix_fails(self):
        spec = self.add_profile(1)
        expected = frozenset(("TEXT", "up_proj", 1, "RAW_FP16", k) for k in (1, 2, 4))
        with self.assertRaisesRegex(RefillConsumerError, "NCU point matrix mismatch"):
            consume_ncu(
                {"schema_version": 1, "profiles": [spec]}, self.root,
                expected_points=expected,
            )


if __name__ == "__main__":
    unittest.main()
