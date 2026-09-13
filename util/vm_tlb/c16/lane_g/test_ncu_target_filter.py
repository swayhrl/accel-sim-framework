"""No-GPU tests for immutable one-unit NCU target filtering."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from profiler_wrapper import plan_command  # noqa: E402


class NcuTargetFilterTests(unittest.TestCase):
    def test_frozen_filter_is_one_structural_kernel_id(self) -> None:
        args = SimpleNamespace(
            output=Path("/tmp/c16-unit.ncu-rep"),
            metrics_file=Path(__file__),
            ncu_kernel_id="::regex:^unit\\(kernel\\)$:17",
            ncu_kernel_name_base="demangled",
            ncu_launch_count=1,
            command=["python", "runner.py"],
        )
        command = plan_command("ncu", args)
        self.assertIn("--kernel-id", command)
        self.assertEqual(command[command.index("--kernel-id") + 1], "::regex:^unit\\(kernel\\)$:17")
        self.assertEqual(command[command.index("--launch-count") + 1], "1")
        self.assertEqual(command[command.index("--replay-mode") + 1], "kernel")
        self.assertEqual(command[command.index("--target-processes") + 1], "application-only")


if __name__ == "__main__":
    unittest.main()
