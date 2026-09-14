from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from util.vm_tlb.c16.lane_h.llama_s0_analysis import analyze_trace, overlap_rows, three_way_overlap_row  # noqa: E402


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

    def test_raw_cta_prefix_preserves_selected_pc_and_lane_addresses(self) -> None:
        trace = """-kernel name = fixture_indexSelectSmallIndex
2 0 0 1 0010 00000005 0 LDG.E 1 R2 4 0 0x100 0x108 0
2 0 0 1 0011 00000001 0 LDG.E 1 R2 4 0 0x200 0
"""
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "fixture.raw_cta"
            path.write_text(trace, encoding="utf-8")
            summary, sets = analyze_trace(path, 0x10, "indexSelectSmallIndex", "RAW_CTA", "LDG.E")
        self.assertEqual(summary["record_count"], 1)
        self.assertEqual(summary["active_lane_count"], 2)
        self.assertEqual(summary["requested_bytes"], 8)
        self.assertEqual(summary["unique_exact_gpu_va"], 2)
        self.assertEqual(sets["exact_address"], {0x100, 0x108})

    def test_three_way_overlap_includes_32_and_64_byte_blocks(self) -> None:
        sets = {
            "a": {"exact_address": {0x100}, "32b_block": {8}, "64b_block": {4}, "128b_line": {2}, "4k_va_bucket": {0}, "64k_va_bucket": {0}, "2m_va_bucket": {0}},
            "b": {"exact_address": {0x100}, "32b_block": {8}, "64b_block": {4}, "128b_line": {2}, "4k_va_bucket": {0}, "64k_va_bucket": {0}, "2m_va_bucket": {0}},
            "c": {"exact_address": {0x120}, "32b_block": {9}, "64b_block": {4}, "128b_line": {2}, "4k_va_bucket": {0}, "64k_va_bucket": {0}, "2m_va_bucket": {0}},
        }
        rows = three_way_overlap_row(sets, "a", "b", "c")
        exact = next(row for row in rows if row["granularity"] == "exact_address")
        block_64 = next(row for row in rows if row["granularity"] == "64b_block")
        self.assertEqual((exact["intersection"], exact["union"], exact["jaccard"]), (0, 2, 0.0))
        self.assertEqual((block_64["intersection"], block_64["union"], block_64["jaccard"]), (1, 1, 1.0))


if __name__ == "__main__":
    unittest.main()
