#!/usr/bin/env python3
"""CPU-only authority checks for the deterministic Route-B Q1 fixture."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LANE = ROOT / "util" / "vm_tlb" / "c16" / "lane_g"
sys.path.insert(0, str(LANE))

from route_b_memory_event_contract import RouteBContractError
from route_b_q1_fixture import Q1_EXACT_FUNCTION, freeze, whitelist_from_static_map


HEADER = "nvbit_static_index\tvector_ordinal\tinstruction_offset\topcode\tmemory_space\tis_load\tis_store\thas_mref\tmref_count\tsass\tfunction_full_name\tfunction_mangled_name\tfunction_address\tcode_object_path\tcode_object_sha256\n"


def map_row(index: int, opcode: str, load: int, store: int, *, function: str = Q1_EXACT_FUNCTION) -> str:
    return f"{index}\t{index}\t{index * 8}\t{opcode}\tGLOBAL\t{load}\t{store}\t1\t1\t{opcode}\t{function}\t{function}\t0x1\tfixture\t{'a' * 64}\n"


class RouteBQ1FixtureTests(unittest.TestCase):
    def test_fixture_writes_exact_runtime_owner_receipt(self):
        source = (LANE / "fixtures/route_b_q1_tiny.cu").read_text(encoding="utf-8")
        self.assertIn("C16_ROUTE_B_Q1_OWNER_RECEIPT_PATH", source)
        self.assertIn("dladdr", source)

    def test_exact_map_freezes_all_global_mrefs_and_sha_closes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); static_map, code = root / "map.tsv", root / "fixture.bin"
            static_map.write_text(HEADER + map_row(3, "LDG.E.32", 1, 0) + map_row(7, "STG.E.32", 0, 1), encoding="utf-8")
            code.write_bytes(b"q1-fixture")
            result = freeze(static_map, code, root / "whitelist.json", root / "whitelist.tsv")
            rows = json.loads((root / "whitelist.json").read_text())["whitelist"]
            self.assertEqual([(3, 0, "READ", 4), (7, 0, "WRITE", 4)],
                             [(row["static_index"], row["mref_ordinal"], row["access_kind"], row["width_bytes"]) for row in rows])
            self.assertEqual(hashlib.sha256(b"q1-fixture").hexdigest(), result["code_object_sha256"])
            self.assertEqual(2, result["whitelist_row_count"])

    def test_mixed_or_missing_exact_map_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "map.tsv"
            path.write_text(HEADER + map_row(3, "LDG.E.32", 1, 0) + map_row(4, "LDG.E.32", 1, 0, function="wrong"), encoding="utf-8")
            with self.assertRaises(RouteBContractError):
                whitelist_from_static_map(path)


if __name__ == "__main__":
    unittest.main()
