"""No-GPU tests for predicate-aware offline address forensic accounting."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from retry570_recovery_v3_address_zero_forensics import inspect  # noqa: E402


class AddressZeroForensicsTests(unittest.TestCase):
    def test_predicate_false_rows_do_not_become_zero_address_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "kernel.trace").write_text(
                "-kernel name = _Zexact\n"
                "0 0 0 0 0010 00000000 0 LDG.E.64 0 4 0 0 \n",
                encoding="utf-8",
            )
            value = inspect(root, target_opcode="LDG.E.64", target_static_index=1,
                            target_offset=0x10, target_function="_Zexact")
            self.assertEqual(value["classification"], "PREDICATED_OFF_TARGET")
            self.assertEqual(value["predicate_mask_zero_rows"], 1)
            self.assertEqual(value["zero_address_lane_count"], 0)

    def test_predicate_true_row_counts_only_its_listed_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "kernel.trace").write_text(
                "-kernel name = _Zexact\n"
                "0 0 0 0 0010 00000003 0 LDG.E.64 0 4 0 0x0000000000000000 0x0000000000000010 0 \n",
                encoding="utf-8",
            )
            value = inspect(root, target_opcode="LDG.E.64", target_static_index=1,
                            target_offset=0x10, target_function="_Zexact")
            self.assertEqual(value["predicate_mask_nonzero_rows"], 1)
            self.assertEqual(value["zero_address_lane_count"], 1)
            self.assertEqual(value["nonzero_address_lane_count"], 1)


if __name__ == "__main__":
    unittest.main()
