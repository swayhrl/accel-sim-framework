#!/usr/bin/env python3
import csv
import tempfile
import unittest
from pathlib import Path

from aggregator import AggregationError, aggregate, compare, read_csv


POLICY = {
    "additive_metrics": {
        "dram__bytes.sum": "byte",
        "lts__bytes.sum": "byte",
    },
    "non_additive_metrics": {
        "sm__throughput.avg.pct_of_peak_sustained_elapsed": "%",
    },
    "required_denominators": [
        "input_elements",
        "output_elements",
        "dense_weight_bytes",
    ],
}


def row(point, rng, occ, kid, name, metric, unit, value, **overrides):
    base = {
        "semantic_point": point,
        "range_name": rng,
        "range_occurrence": str(occ),
        "kernel_id": str(kid),
        "kernel_name": name,
        "metric_name": metric,
        "metric_unit": unit,
        "metric_value": str(value),
        "input_elements": "10",
        "output_elements": "20",
        "dense_weight_bytes": "100",
        "packed_weight_bytes": "25",
    }
    base.update(overrides)
    return base


def kernel(point, rng, occ, kid, name, dram, l2, util):
    return [
        row(point, rng, occ, kid, name, "dram__bytes.sum", "byte", dram),
        row(point, rng, occ, kid, name, "lts__bytes.sum", "byte", l2),
        row(point, rng, occ, kid, name, "sm__throughput.avg.pct_of_peak_sustained_elapsed", "%", util),
    ]


class Tests(unittest.TestCase):
    def test_single_raw_kernel(self):
        x = aggregate(kernel("M1_RAW", "TARGET", 0, 1, "dense", 100, 50, 20), "M1_RAW", "TARGET", POLICY)
        self.assertEqual(x["kernel_count"], 1)
        self.assertEqual(x["SEMANTIC_MODULE_SUM"]["dram__bytes.sum"]["value"], 100)
        self.assertEqual(x["SEMANTIC_MODULE_SUM"]["dram__bytes.sum"]["value_exact"], "100")

    def test_multi_kernel_awq_adds_bytes_not_util(self):
        rows = (
            kernel("M1_AWQ", "TARGET", 0, 1, "dequant", 100, 50, 20)
            + kernel("M1_AWQ", "TARGET", 0, 2, "gemm", 300, 150, 40)
        )
        x = aggregate(rows, "M1_AWQ", "TARGET", POLICY)
        self.assertEqual(x["SEMANTIC_MODULE_SUM"]["dram__bytes.sum"]["value"], 400)
        self.assertNotIn("sm__throughput.avg.pct_of_peak_sustained_elapsed", x["SEMANTIC_MODULE_SUM"])
        self.assertEqual(len(x["non_additive_per_kernel"]["sm__throughput.avg.pct_of_peak_sustained_elapsed"]), 2)
        self.assertTrue(x["non_additive_coverage"]["sm__throughput.avg.pct_of_peak_sustained_elapsed"]["complete"])

    def test_warmup_excluded(self):
        rows = (
            kernel("M1_RAW", "WARMUP", 0, 9, "warm", 999, 999, 99)
            + kernel("M1_RAW", "TARGET", 0, 1, "dense", 100, 50, 20)
        )
        x = aggregate(rows, "M1_RAW", "TARGET", POLICY)
        self.assertEqual(x["kernel_count"], 1)

    def test_ambiguous_range_fails(self):
        rows = (
            kernel("M1_RAW", "TARGET", 0, 1, "a", 1, 1, 1)
            + kernel("M1_RAW", "TARGET", 1, 2, "b", 1, 1, 1)
        )
        with self.assertRaises(AggregationError):
            aggregate(rows, "M1_RAW", "TARGET", POLICY)

    def test_noncanonical_range_occurrence_fails(self):
        rows = kernel("M1_RAW", "TARGET", "00", 1, "a", 1, 1, 1)
        with self.assertRaises(AggregationError):
            aggregate(rows, "M1_RAW", "TARGET", POLICY)

    def test_unit_mismatch_fails(self):
        rows = kernel("M1_RAW", "TARGET", 0, 1, "a", 1, 1, 1)
        rows[0]["metric_unit"] = "kbyte"
        with self.assertRaises(AggregationError):
            aggregate(rows, "M1_RAW", "TARGET", POLICY)

    def test_nonfinite_metric_fails(self):
        rows = kernel("M1_RAW", "TARGET", 0, 1, "a", "nan", 1, 1)
        with self.assertRaises(AggregationError):
            aggregate(rows, "M1_RAW", "TARGET", POLICY)

    def test_duplicate_metric_row_fails(self):
        rows = kernel("M1_RAW", "TARGET", 0, 1, "a", 1, 1, 1)
        rows.append(dict(rows[0]))
        with self.assertRaises(AggregationError):
            aggregate(rows, "M1_RAW", "TARGET", POLICY)

    def test_same_kernel_id_different_name_fails(self):
        rows = kernel("M1_RAW", "TARGET", 0, 1, "a", 1, 1, 1)
        rows[-1]["kernel_name"] = "different"
        with self.assertRaises(AggregationError):
            aggregate(rows, "M1_RAW", "TARGET", POLICY)

    def test_missing_additive_metric_on_one_kernel_fails(self):
        rows = kernel("M1_AWQ", "TARGET", 0, 1, "a", 1, 1, 1)
        rows += [
            row("M1_AWQ", "TARGET", 0, 2, "b", "dram__bytes.sum", "byte", 1),
            row("M1_AWQ", "TARGET", 0, 2, "b", "sm__throughput.avg.pct_of_peak_sustained_elapsed", "%", 1),
        ]
        with self.assertRaises(AggregationError):
            aggregate(rows, "M1_AWQ", "TARGET", POLICY)

    def test_partially_missing_denominator_fails(self):
        rows = kernel("M1_RAW", "TARGET", 0, 1, "a", 1, 1, 1)
        rows[0]["input_elements"] = ""
        with self.assertRaises(AggregationError):
            aggregate(rows, "M1_RAW", "TARGET", POLICY)

    def test_unknown_metric_fails(self):
        rows = kernel("M1_RAW", "TARGET", 0, 1, "a", 1, 1, 1)
        rows.append(row("M1_RAW", "TARGET", 0, 1, "a", "unknown.metric", "byte", 1))
        with self.assertRaises(AggregationError):
            aggregate(rows, "M1_RAW", "TARGET", POLICY)

    def test_duplicate_csv_header_fails(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.csv"
            fields = list(sorted({
                "semantic_point", "range_name", "range_occurrence", "kernel_id", "kernel_name",
                "metric_name", "metric_unit", "metric_value", "input_elements", "output_elements",
                "dense_weight_bytes", "packed_weight_bytes",
            }))
            p.write_text(",".join(fields + ["metric_value"]) + "\n", encoding="utf-8")
            with self.assertRaises(AggregationError):
                read_csv(p)

    def test_compare_unit_mismatch_fails(self):
        pts = {}
        for M in (1, 256):
            for impl in ("RAW", "AWQ"):
                x = aggregate(kernel(f"M{M}_{impl}", "TARGET", 0, 1, "a", 10, 5, 1), f"M{M}_{impl}", "TARGET", POLICY)
                pts[(M, impl)] = x
        pts[(256, "AWQ")]["SEMANTIC_MODULE_SUM"]["dram__bytes.sum"]["unit"] = "kbyte"
        with self.assertRaises(AggregationError):
            compare(pts, ["dram__bytes.sum"])

    def test_compare_zero_denominator_returns_undefined_not_exception(self):
        pts = {}
        for M in (1, 256):
            for impl in ("RAW", "AWQ"):
                x = aggregate(kernel(f"M{M}_{impl}", "TARGET", 0, 1, "a", 10, 5, 1), f"M{M}_{impl}", "TARGET", POLICY)
                pts[(M, impl)] = x
        pts[(1, "RAW")]["SEMANTIC_MODULE_SUM"]["dram__bytes.sum"]["value"] = 0
        pts[(1, "RAW")]["SEMANTIC_MODULE_SUM"]["dram__bytes.sum"]["value_exact"] = "0"
        out = compare(pts, ["dram__bytes.sum"])[0]
        self.assertEqual(out["ratio_status"], "UNDEFINED_ZERO_DENOMINATOR")
        self.assertIsNone(out["M1_AWQ_over_RAW"])

    def test_decimal_addition_preserves_exact_sum(self):
        rows = kernel("M1_AWQ", "TARGET", 0, 1, "a", "0.1", "0.2", 1)
        rows += kernel("M1_AWQ", "TARGET", 0, 2, "b", "0.2", "0.3", 1)
        x = aggregate(rows, "M1_AWQ", "TARGET", POLICY)
        self.assertEqual(x["SEMANTIC_MODULE_SUM"]["dram__bytes.sum"]["value_exact"], "0.3")


if __name__ == "__main__":
    unittest.main()
