from __future__ import annotations

import unittest
from pathlib import Path

SOURCE = (Path(__file__).parent / "retry570_first_use_completion.py").read_text(encoding="utf-8")
EMPTY = (Path(__file__).parent / "retry570_empty_callback_dispatch_tool.cu").read_text(encoding="utf-8")


class FirstUseCompletionTests(unittest.TestCase):
    def test_exact_eager_two_round_contract(self) -> None:
        self.assertIn('"CUDA_MODULE_LOADING": "EAGER"', SOURCE)
        self.assertIn("for ordinal in (1, 2)", SOURCE)
        self.assertIn('f"ROUND{ordinal}_BEGIN"', SOURCE)
        self.assertIn('f"ROUND{ordinal}_END"', SOURCE)
        self.assertIn('event(args.stage_path, "READY", measurement_active=False)', SOURCE)
        self.assertIn("torch.cuda.synchronize()", SOURCE)

    def test_external_budget_and_cleanup_contract(self) -> None:
        self.assertIn("TARGET_HARD_BUDGET_S = 60", SOURCE)
        self.assertIn("os.killpg(process.pid, signal.SIGTERM)", SOURCE)
        self.assertIn("os.killpg(process.pid, signal.SIGKILL)", SOURCE)
        self.assertIn("MeasurementActive.assert_available", SOURCE)
        self.assertNotIn("with MeasurementActive(", SOURCE)

    def test_forbidden_diagnostic_mechanisms_absent(self) -> None:
        for forbidden in ("gdb", "perf record", "nvbit_get_instrs", "nvbit_insert_call", "trace.xz"):
            self.assertNotIn(forbidden, SOURCE)
        callback = EMPTY[EMPTY.index("void nvbit_at_cuda_event"):EMPTY.index("void nvbit_at_term")]
        self.assertIn("return;", callback)
        self.assertNotIn("std::", callback)


if __name__ == "__main__":
    unittest.main()
