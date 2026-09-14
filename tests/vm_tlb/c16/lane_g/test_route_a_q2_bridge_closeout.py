#!/usr/bin/env python3
"""CPU-only tests for the offline Route-A/Q2 bridge checker."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "util" / "vm_tlb" / "c16" / "lane_g"))
from route_a_q2_bridge_closeout import BridgeError, check_phase


FUNCTION = "_Zhistorical_exact"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


class RouteABridgeCloseoutTest(unittest.TestCase):
    def phase(self) -> dict:
        return {
            "exact_function_mangled_name": FUNCTION,
            "selected_static_index": 7,
            "selected_mref_ordinal": 0,
            "selected_instruction": {
                "instruction_offset": 16, "opcode": "LDG.E", "memory_space": "GLOBAL",
                "is_load": 1, "is_store": 0, "has_mref": 1, "mref_count": 1,
                "width_bytes": 4, "code_object_sha256": "code",
            },
            "historical_capture_signatures": [{
                "selected_event_count": 2, "selected_request_count": 1,
                "executing_lane_cardinality_histogram": {"2": 1},
                "unique_exact_gpu_va_count": 2, "unique_32b_block_count": 1,
                "unique_64b_block_count": 1, "unique_128b_line_count": 1,
                "unique_4k_va_bucket_count": 1, "unique_64k_va_bucket_count": 1,
                "unique_2m_va_bucket_count": 1,
            }],
        }

    def test_accepts_cardinality_without_absolute_va_equality(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory); raw = work / "raw.jsonl"; static = work / "map.tsv"; receipt = work / "receipt.json"
            rows = [
                {"record_kind": "LANE_EVENT", "function_mangled_name": FUNCTION, "static_index": 7, "mref_ordinal": 0, "memory_space": "GLOBAL", "gpu_va": 0x2010, "kernel_launch_id": 9, "warp_instruction_instance_id": 3, "lane_id": 0, "executing_mask": 3},
                {"record_kind": "LANE_EVENT", "function_mangled_name": FUNCTION, "static_index": 7, "mref_ordinal": 0, "memory_space": "GLOBAL", "gpu_va": 0x2014, "kernel_launch_id": 9, "warp_instruction_instance_id": 3, "lane_id": 1, "executing_mask": 3},
                {"record_kind": "TERMINAL", "terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0, "event_count": 2},
            ]
            raw.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            static.write_text("nvbit_static_index\tinstruction_offset\topcode\tmemory_space\tis_load\tis_store\thas_mref\tmref_count\twidth_bytes\tfunction_mangled_name\tcode_object_sha256\n7\t16\tLDG.E\tGLOBAL\t1\t0\t1\t1\t4\t_Zhistorical_exact\tcode\n", encoding="utf-8")
            receipt.write_text(json.dumps({"raw": {"sha256": digest(raw)}, "result": {"terminal": rows[-1]}}), encoding="utf-8")
            result = check_phase(self.phase(), raw, static, receipt)
            self.assertEqual("PASS", result["status"])
            self.assertEqual("PROHIBITED", result["absolute_gpu_va_comparison"])

    def test_mref_ordinal_and_terminal_count_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory); raw = work / "raw.jsonl"; static = work / "map.tsv"; receipt = work / "receipt.json"
            rows = [
                {"record_kind": "LANE_EVENT", "function_mangled_name": FUNCTION, "static_index": 7, "mref_ordinal": 1, "memory_space": "GLOBAL", "gpu_va": 0x2010, "kernel_launch_id": 9, "warp_instruction_instance_id": 3, "lane_id": 0, "executing_mask": 1},
                {"record_kind": "TERMINAL", "terminal_status": "COMPLETE", "overflow_count": 0, "drop_count": 0, "event_count": 99},
            ]
            raw.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            static.write_text("nvbit_static_index\tinstruction_offset\topcode\tmemory_space\tis_load\tis_store\thas_mref\tmref_count\twidth_bytes\tfunction_mangled_name\tcode_object_sha256\n7\t16\tLDG.E\tGLOBAL\t1\t0\t1\t1\t4\t_Zhistorical_exact\tcode\n", encoding="utf-8")
            receipt.write_text("{}", encoding="utf-8")
            with self.assertRaises(BridgeError):
                check_phase(self.phase(), raw, static, receipt)


if __name__ == "__main__":
    unittest.main()
