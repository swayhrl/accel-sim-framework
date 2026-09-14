from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


LANE = Path(__file__).resolve().parents[4] / "util" / "vm_tlb" / "c16" / "lane_g"
sys.path.insert(0, str(LANE))
SPEC = importlib.util.spec_from_file_location("join", LANE / "retry570_recovery_v3_source_to_nvbit_join.py")
assert SPEC and SPEC.loader
JOIN = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(JOIN)


class SourceToNvbitJoinTest(unittest.TestCase):
    def test_known_abi_renderings_canonicalize_identically(self) -> None:
        direct = "void x::f<x::t<64, false, cutlass::half_t> >(x::p)"
        nsys = "void x::f<x::t<(int)64, (bool)0, cutlass::half_t>>(x::p)"
        self.assertEqual(JOIN.canonical_function(direct), JOIN.canonical_function(nsys))

    def test_rejects_kernel_name_only_source_row(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            catalog = Path(temp) / "catalog.tsv"
            catalog.write_text("deployment_id\tscenario_id\tphase\tkernel_name\tgrid\tblock\tlaunch_ordinal\tcorrelation_id\n"
                               "d\ts\tPREFILL\tshort_name_only\t1x1x1\t128x1x1\t7\tc\n", encoding="utf-8")
            direct = {"deployment_id": "d", "scenario_id": "s", "direct_function_full_name": "void x::f()",
                      "direct_function_mangled_name": "_Z", "grid": "1x1x1", "block": "128x1x1"}
            with self.assertRaises(JOIN.ContractError):
                JOIN.matching_source_rows(catalog, direct, "PREFILL")

    def test_receipt_contract_forbids_ordinal_and_time_join(self) -> None:
        self.assertIn("NSYS_SOURCE_LAUNCH_ORDINAL_EQUALS_NVBIT_STATIC_INDEX", JOIN.FORBIDDEN)
        self.assertIn("CROSS_RUN_ABSOLUTE_TIMESTAMP_JOIN", JOIN.FORBIDDEN)


if __name__ == "__main__":
    unittest.main()
