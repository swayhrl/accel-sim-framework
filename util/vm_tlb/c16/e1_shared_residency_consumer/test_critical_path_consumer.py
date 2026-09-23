#!/usr/bin/env python3
import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from critical_path_consumer import CriticalPathError, consume


GEMM = "awq_gemm_kernel"
REDUCE = "awq_reduction_kernel"
RANGE = "NAT_L0_UP_D3"


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CriticalPathConsumerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        query = self.root / "QUERY.txt"
        query.write_text("ncu metric query synthetic receipt\n", encoding="utf-8")
        self.query_receipt = {
            "status": "PASS",
            "command": "ncu --query-metrics",
            "path": query.name,
            "sha256": file_sha(query),
        }
        self.catalog = [
            {
                "category": "DRAM_READ_BYTES",
                "available": True,
                "metric_name": "dram__bytes_read.sum",
                "unit": "byte",
                "aggregation": "SEMANTIC_SUM",
            },
            {
                "category": "LONG_SCOREBOARD_STALL",
                "available": True,
                "metric_name": "smsp__warp_issue_stalled_long_scoreboard_per_warp_active.pct",
                "unit": "%",
                "aggregation": "PER_KERNEL_ONLY",
            },
        ]

    def tearDown(self):
        self.temp.cleanup()

    def write_base(self, name="BASE.csv", *, rows=None, units=None, metrics=None):
        metrics = metrics or [entry["metric_name"] for entry in self.catalog if entry["available"]]
        path = self.root / name
        header = ["ID", "Kernel Name", "NVTX Push/Pop_Range", *metrics]
        units = units or ["", "", "", "byte", "%"]
        rows = rows or [
            ["1", GEMM, RANGE, "100", "40"],
            ["2", REDUCE, RANGE, "25", "10"],
        ]
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerow(units)
            writer.writerows(rows)
        return path

    def document(self, path: Path, *, catalog=None, condition="SETASIDE_ONLY"):
        return {
            "schema_version": 1,
            "query_receipt": self.query_receipt,
            "metric_availability": self.catalog if catalog is None else catalog,
            "profiles": [
                {
                    "condition": condition,
                    "target": "L0_UP_D3",
                    "range_name": RANGE,
                    "expected_kernel_names": [GEMM, REDUCE],
                    "base_path": path.name,
                }
            ],
        }

    def test_gemm_and_reduction_additive_sum_and_nonadditive_preserved(self):
        result = consume(self.document(self.write_base()), self.root)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(len(result["kernel_metrics"]), 4)
        dram = result["semantic_sums"]
        self.assertEqual(len(dram), 1)
        self.assertEqual(dram[0]["category"], "DRAM_READ_BYTES")
        self.assertEqual(dram[0]["value"], 125)
        self.assertEqual(dram[0]["kernel_count"], 2)
        stalls = [
            row for row in result["kernel_metrics"]
            if row["category"] == "LONG_SCOREBOARD_STALL"
        ]
        self.assertEqual([(row["kernel_name"], row["value"]) for row in stalls], [(GEMM, 40), (REDUCE, 10)])
        self.assertFalse(any(row["category"] == "LONG_SCOREBOARD_STALL" for row in dram))

    def test_explicit_unavailable_category_does_not_require_or_invent_metric(self):
        catalog = [
            self.catalog[0],
            {
                "category": "LSU_UTILIZATION",
                "available": False,
                "metric_name": None,
                "unit": None,
                "reason": "not exposed by installed NCU",
            },
        ]
        path = self.write_base(
            metrics=["dram__bytes_read.sum"],
            units=["", "", "", "byte"],
            rows=[["1", GEMM, RANGE, "100"], ["2", REDUCE, RANGE, "25"]],
        )
        result = consume(self.document(path, catalog=catalog), self.root)
        unavailable = [row for row in result["metric_availability"] if not row["available"]]
        self.assertEqual(unavailable[0]["category"], "LSU_UTILIZATION")
        self.assertFalse(any(row["category"] == "LSU_UTILIZATION" for row in result["kernel_metrics"]))

    def test_claimed_available_but_missing_metric_fails(self):
        path = self.write_base(
            metrics=["dram__bytes_read.sum"],
            units=["", "", "", "byte"],
            rows=[["1", GEMM, RANGE, "100"], ["2", REDUCE, RANGE, "25"]],
        )
        with self.assertRaisesRegex(CriticalPathError, "claimed metric available"):
            consume(self.document(path), self.root)

    def test_unknown_category_fails(self):
        catalog = [dict(self.catalog[0], category="MADE_UP_CACHE_SCORE")]
        with self.assertRaisesRegex(CriticalPathError, "unknown metric category"):
            consume(self.document(self.write_base(), catalog=catalog), self.root)

    def test_catalog_unit_mismatch_fails(self):
        catalog = [dict(self.catalog[0], unit="sector")]
        with self.assertRaisesRegex(CriticalPathError, "unit mismatch for category"):
            consume(self.document(self.write_base(), catalog=catalog), self.root)

    def test_duplicate_metric_row_fails(self):
        path = self.write_base(
            rows=[
                ["1", GEMM, RANGE, "100", "40"],
                ["1", GEMM, RANGE, "100", "40"],
                ["2", REDUCE, RANGE, "25", "10"],
            ]
        )
        with self.assertRaisesRegex(CriticalPathError, "duplicate metric row"):
            consume(self.document(path), self.root)

    def test_kernel_inventory_mismatch_fails(self):
        path = self.write_base(rows=[["1", GEMM, RANGE, "100", "40"]])
        with self.assertRaisesRegex(CriticalPathError, "kernel inventory mismatch"):
            consume(self.document(path), self.root)

    def test_cross_condition_unit_drift_fails(self):
        first = self.write_base("A.csv")
        second = self.write_base(
            "B.csv",
            units=["", "", "", "byte", "percent"],
        )
        document = self.document(first)
        document["profiles"].append(
            {
                "condition": "PERSIST_TARGET",
                "target": "L0_UP_D3",
                "range_name": RANGE,
                "expected_kernel_names": [GEMM, REDUCE],
                "base_path": second.name,
            }
        )
        with self.assertRaisesRegex(CriticalPathError, "unit mismatch.*PERSIST_TARGET"):
            consume(document, self.root)

    def test_duplicate_exact_metric_name_fails(self):
        catalog = [
            self.catalog[0],
            {
                "category": "KERNEL_ELAPSED_CYCLES",
                "available": True,
                "metric_name": self.catalog[0]["metric_name"],
                "unit": "cycle",
            },
        ]
        with self.assertRaisesRegex(CriticalPathError, "duplicate exact metric name"):
            consume(self.document(self.write_base(), catalog=catalog), self.root)

    def test_query_receipt_sha_mismatch_fails(self):
        document = self.document(self.write_base())
        document["query_receipt"] = dict(self.query_receipt, sha256="0" * 64)
        with self.assertRaisesRegex(CriticalPathError, "query receipt SHA256 mismatch"):
            consume(document, self.root)


if __name__ == "__main__":
    unittest.main()
