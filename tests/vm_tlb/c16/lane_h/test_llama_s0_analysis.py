from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from util.vm_tlb.c16.lane_h.llama_s0_analysis import analyze_trace, overlap_rows  # noqa: E402


class LlamaS0AnalysisTest(unittest.TestCase):
    def test_selected_pc_metrics_and_set_overlap(self) -> None:
        trace = """-kernel name = fixture_indexSelectSmallIndex\n# metadata\n0010 00000003 0 LDG.E.32 0 4 0 0x80 0x84 0\n0010 00000003 0 LDG.E.32 0 4 0 0x80 0x1040 0\n0020 00000001 0 STG.E.32 0 4 0 0x2000 0\n"""
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "fixture.traceg"
            path.write_text(trace, encoding="utf-8")
            summary, sets = analyze_trace(path, 0x10, "indexSelectSmallIndex")
        self.assertEqual(summary["record_count"], 2)
        self.assertEqual(summary["address_record_count"], 4)
        self.assertEqual(summary["unique_exact_gpu_va"], 3)
        self.assertEqual(summary["unique_128b_lines"], 2)
        self.assertEqual(summary["unique_4k_va_buckets"], 2)
        self.assertEqual(summary["read_address_records"], 4)
        self.assertEqual(summary["write_address_records"], 0)
        self.assertEqual(summary["contiguous_lane_pair_fraction"], 0.5)
        self.assertEqual(summary["order_model"], "SET_ONLY")
        rows = overlap_rows({"a": sets, "b": sets})
        exact = next(row for row in rows if row["granularity"] == "exact_address")
        self.assertEqual((exact["intersection"], exact["union"], exact["jaccard"]), (3, 3, 1.0))


if __name__ == "__main__":
    unittest.main()
