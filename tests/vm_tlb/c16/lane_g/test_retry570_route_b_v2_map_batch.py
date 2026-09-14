from __future__ import annotations
import csv
import sys
import tempfile
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parents[4] / "util/vm_tlb/c16/lane_g"
sys.path.insert(0, str(LANE))
from retry570_route_b_v2_map_batch import inventory_functions  # noqa: E402


class RouteBV2MapBatchTest(unittest.TestCase):
    def test_deduplicates_by_exact_mangled_function(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "inventory.tsv"
            with path.open("w", encoding="utf-8", newline="") as out:
                writer = csv.DictWriter(out, fieldnames=["function_mangled_name"], delimiter="\t")
                writer.writeheader(); writer.writerow({"function_mangled_name": "_Zb"}); writer.writerow({"function_mangled_name": "_Za"}); writer.writerow({"function_mangled_name": "_Za"})
            self.assertEqual(inventory_functions(path), ["_Za", "_Zb"])

    def test_active_map_window_denies_transfer_slot_and_is_function_level(self):
        source = (LANE / "retry570_route_b_v2_map_batch.py").read_text(encoding="utf-8")
        self.assertIn('"transfer_slot_granted": active == "none"', source)
        self.assertIn('"--phase", "FUNCTION"', source)
        self.assertIn('"--fatbin-owner-preload"', source)
        self.assertIn('"--culibrary-owner-preload"', source)


if __name__ == "__main__":
    unittest.main()
