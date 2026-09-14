"""No-GPU tests for exact phase-specific direct-memory target freezing."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from retry570_recovery_v3_phase_target_freeze import select  # noqa: E402


class PhaseTargetFreezeTests(unittest.TestCase):
    def test_selects_earliest_unpredicated_global_mref(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "map.tsv"
            header = "nvbit_static_index\tvector_ordinal\tinstruction_offset\topcode\tmemory_space\tis_load\tis_store\thas_mref\tsass\tfunction_full_name\tfunction_mangled_name\tfunction_address\tlibtorch_cuda_sha256\n"
            def row(index: int, sass: str) -> str:
                return f"{index}\t{index}\t{index * 16}\tLDG.E\tGLOBAL\t1\t0\t1\t{sass}\tfull\t_Zexact\t0x1\t" + "a" * 64 + "\n"
            path.write_text(header + row(3, "@P0 LDG.E R2,[R2];") + row(7, "LDG.E R2,[R2];"), encoding="utf-8")
            target, count = select(path, mangled="_Zexact", code_sha="a" * 64)
            self.assertEqual(count, 2)
            self.assertEqual(target["nvbit_static_index"], 7)

    def test_forbids_ordinal_equality_and_cross_phase_reuse(self) -> None:
        source = (LANE / "retry570_recovery_v3_phase_target_freeze.py").read_text(encoding="utf-8")
        self.assertIn("NSYS_ORDINAL_EQUALS_NVBIT_ORDINAL", source)
        self.assertIn("CROSS_PHASE_TARGET_REUSE", source)


if __name__ == "__main__":
    unittest.main()
