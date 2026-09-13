"""No-GPU contracts for the Recovery V3 direct-memory discriminator."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from retry570_recovery_targeted_memory import map_target_evidence, marker_evidence  # noqa: E402


TARGET = {
    "function": {"mangled_name": "_Zexact", "libtorch_cuda_sha256": "a" * 64},
    "target_instruction": {"nvbit_static_index": 29, "opcode": "LDG.E.64"},
}


class RecoveryTargetedMemoryTests(unittest.TestCase):
    def test_map_requires_one_exact_direct_target_row(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "map.tsv"
            path.write_text(
                "nvbit_static_index\tvector_ordinal\tinstruction_offset\topcode\tmemory_space\tis_load\tis_store\thas_mref\tsass\tfunction_full_name\tfunction_mangled_name\tfunction_address\tlibtorch_cuda_sha256\n"
                "29\t29\t464\tLDG.E.64\tGLOBAL\t1\t0\t1\tLDG.E.64 R2,[R2]\tfull\t_Zexact\t0x1\t" + "a" * 64 + "\n",
                encoding="utf-8",
            )
            evidence = map_target_evidence(path, TARGET)
            self.assertEqual(evidence["static_index"], 29)
            self.assertTrue(evidence["satisfies_direct_global_mref"])

    def test_marker_requires_exact_launch_and_callback(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "stdout.log"
            path.write_text(
                "C16_TARGETED_NVBIT_FUNCTION_LAUNCH function_mangled=_Zexact launch_id=0 nvbit_static_index=29\n"
                "C16_TARGETED_NVBIT_MEMORY_RECORD function_mangled=_Zexact present=1 address=0x1 launch_id=0 nvbit_static_index=29\n",
                encoding="utf-8",
            )
            evidence = marker_evidence(path, TARGET)
            self.assertTrue(evidence["memory_record_present"])
            self.assertEqual(evidence["exact_function_launch_count"], 1)

    def test_parent_contract_has_one_recovery_lease_and_external_group_cleanup(self) -> None:
        source = (LANE / "retry570_recovery_targeted_memory.py").read_text(encoding="utf-8")
        for token in ("RecoveryBudgetLease", "write_parent_lease_start", "wrapper-owned", "start_new_session=True", "kill_group(process)", "NON_SCIENTIFIC_DIAGNOSTIC"):
            self.assertIn(token, source)
        self.assertNotIn("from execution_budget import BudgetLease", source)


if __name__ == "__main__":
    unittest.main()
