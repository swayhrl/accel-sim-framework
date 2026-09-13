"""No-GPU tests for phase-specific Recovery V3 target replacement."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from retry570_recovery_v3_next_static_target import select  # noqa: E402


class NextStaticTargetTests(unittest.TestCase):
    def test_selects_earliest_unpredicated_direct_global_store_not_a_wider_range(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "map.tsv"
            header = "nvbit_static_index\tvector_ordinal\tinstruction_offset\topcode\tmemory_space\tis_load\tis_store\thas_mref\tsass\tfunction_full_name\tfunction_mangled_name\tfunction_address\tlibtorch_cuda_sha256\n"
            row = lambda index, sass: f"{index}\t{index}\t{index * 16}\tSTG.E.128\tGLOBAL\t0\t1\t1\t{sass}\tfull\t_Zexact\t0x1\t" + "a" * 64 + "\n"
            path.write_text(header + row(30, "@P1 STG.E.128 [R2], R4 ;") + row(41, "STG.E.128 [R2], R4 ;") + row(45, "STG.E.128 [R4], R8 ;"), encoding="utf-8")
            target = select(path, prior_index=29, function="_Zexact", lib_sha="a" * 64)
            self.assertEqual(target["nvbit_static_index"], 41)
            self.assertTrue(target["is_store"])

    def test_contract_is_explicitly_non_widening_and_outcome_independent(self) -> None:
        source = (LANE / "retry570_recovery_v3_next_static_target.py").read_text(encoding="utf-8")
        for token in ("EARLIEST_UNPREDICATED_GLOBAL_MREF_STORE_AFTER_DIRECT_INSTRUMENTED_ZERO", "WIDEN_PRIOR_RANGE", "KERNEL_NAME_ONLY_SUBSTITUTION", "PERFORMANCE_OUTCOME_SELECTION"):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
