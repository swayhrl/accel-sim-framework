"""No-GPU contracts for the deterministic predicate-off replacement target."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from retry570_recovery_v3_predicated_off_target import select  # noqa: E402


class PredicatedOffReplacementTests(unittest.TestCase):
    def test_selects_earliest_unpredicated_direct_global_mref(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "map.tsv"
            header = "nvbit_static_index\tvector_ordinal\tinstruction_offset\topcode\tmemory_space\tis_load\tis_store\thas_mref\tsass\tfunction_full_name\tfunction_mangled_name\tfunction_address\tlibtorch_cuda_sha256\n"
            def row(index: int, sass: str) -> str:
                return f"{index}\t{index}\t{index * 16}\tLDG.E.64\tGLOBAL\t1\t0\t1\t{sass}\tfull\t_Zexact\t0x1\t" + "a" * 64 + "\n"
            path.write_text(header + row(45, "@P0 LDG.E.64 R2, [R2] ;") + row(86, "LDG.E.64 R2, [R2] ;"), encoding="utf-8")
            target = select(path, function="_Zexact", lib_sha="a" * 64, prior_index=45)
            self.assertEqual(target["nvbit_static_index"], 86)
            self.assertTrue(target["has_mref"])

    def test_contract_rejects_widening_and_name_based_substitution(self) -> None:
        source = (LANE / "retry570_recovery_v3_predicated_off_target.py").read_text(encoding="utf-8")
        for token in ("EARLIEST_UNPREDICATED_DIRECT_GLOBAL_MREF_IN_SAME_EXACT_FUNCTION_AFTER_PREDICATE_OFF_PROOF", "WIDEN_PRIOR_RANGE", "KERNEL_NAME_ONLY_SUBSTITUTION", "STATIC_ORDINAL_REUSE"):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
