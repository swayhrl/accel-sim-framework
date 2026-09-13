from __future__ import annotations

import unittest
from pathlib import Path


SOURCE = (Path(__file__).parent / "retry570_llama_decode_static_map.py").read_text(encoding="utf-8")


class LlamaDecodeStaticMapTests(unittest.TestCase):
    def test_is_exact_map_only_under_recovery_ledger(self) -> None:
        for token in ("C16_NVBIT_TARGET_FUNCTION_MANGLED", "C16_NVBIT_STATIC_MAP_PATH", "C16_NVBIT_TARGET_INSTR_INDEX", "RecoveryBudgetLease", "historical_ledger", "instruction_instrumentation\": False", "trace_emission\": False"):
            self.assertIn(token, SOURCE)

    def test_preserves_frozen_workload_and_measurement_boundary(self) -> None:
        for token in ("run_full(model, prompt, torch, phase=\"DECODE\", capture=False)", "EXPECTED_CHECKSUM", "measurement_marker.exists()", "CUDA_MODULE_LOADING"):
            self.assertIn(token, SOURCE)


if __name__ == "__main__": unittest.main()
