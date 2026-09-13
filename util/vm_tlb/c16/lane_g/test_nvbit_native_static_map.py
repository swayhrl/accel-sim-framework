"""CPU-only tests for NVBit-native static-map closure and target selection."""
from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from c16_native_common import ContractError  # noqa: E402
from nvbit_native_static_map import MAP_FIELDS, read_native_map, target_receipt  # noqa: E402


MANGLED = "_Zexact_indexSelectLargeIndex"


def row(index: int, ordinal: int, offset: int, opcode: str, space: str, *, mangled: str = MANGLED) -> dict[str, str]:
    return {
        "nvbit_static_index": str(index), "vector_ordinal": str(ordinal),
        "instruction_offset": str(offset), "opcode": opcode, "memory_space": space,
        "is_load": "1" if opcode.startswith("LDG") else "0",
        "is_store": "1" if opcode.startswith("STG") else "0",
        "sass": f"{opcode} R0, [R2]", "function_full_name": "indexSelectLargeIndex",
        "function_mangled_name": mangled, "function_address": "0x1234",
    }


def write_map(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MAP_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


class NvbitNativeStaticMapTests(unittest.TestCase):
    def test_selects_nvbit_index_not_text_line_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "map.tsv"
            write_map(path, [row(7, 0, 0, "IMAD", "NONE"), row(91, 1, 16, "LDG.E", "GLOBAL")])
            payload = target_receipt(path, MANGLED)
        self.assertEqual(payload["target_instruction"]["nvbit_static_index"], 91)
        self.assertEqual(payload["historical_candidates"]["348"], "HISTORICAL_CANDIDATE_ORDINAL_NOT_USED_AS_NVBIT_INDEX")
        self.assertEqual(payload["historical_candidates"]["34"], "SASS_TEXT_LINE_COUNTER_NOT_USED_AS_NVBIT_INDEX")

    def test_rejects_non_exact_function_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "map.tsv"
            write_map(path, [row(3, 0, 0, "LDG.E", "GLOBAL", mangled="_Zother")])
            with self.assertRaises(ContractError):
                read_native_map(path, MANGLED)

    def test_rejects_noncontiguous_vector_ordinals(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "map.tsv"
            write_map(path, [row(3, 1, 0, "LDG.E", "GLOBAL")])
            with self.assertRaises(ContractError):
                read_native_map(path, MANGLED)


if __name__ == "__main__":
    unittest.main()
