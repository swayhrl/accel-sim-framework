"""No-GPU tests for immutable one-unit NCU target filtering."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from profiler_wrapper import parse_args, plan_command  # noqa: E402


class NcuTargetFilterTests(unittest.TestCase):
    def test_frozen_filter_is_one_structural_name_ordinal(self) -> None:
        args = SimpleNamespace(
            output=Path("/tmp/c16-unit.ncu-rep"),
            metrics_file=Path(__file__),
            ncu_kernel_id=None,
            ncu_kernel_name_filter="regex:^unit\\(kernel\\)$",
            ncu_kernel_name_base="demangled",
            ncu_launch_skip=16,
            ncu_launch_count=1,
            command=["python", "runner.py"],
        )
        command = plan_command("ncu", args)
        self.assertNotIn("--kernel-id", command)
        self.assertEqual(command[command.index("--kernel-name") + 1], "regex:^unit\\(kernel\\)$")
        self.assertEqual(command[command.index("--launch-skip") + 1], "16")
        self.assertEqual(command[command.index("--launch-count") + 1], "1")
        self.assertEqual(command[command.index("--replay-mode") + 1], "kernel")
        self.assertEqual(command[command.index("--target-processes") + 1], "application-only")

    def test_nvbit_fixture_can_be_explicitly_non_scientific(self) -> None:
        previous = sys.argv
        try:
            sys.argv = [
                "nvbit_wrapper.py", "--execute", "--diagnostic-only",
                "--receipt", "/tmp/receipt.json", "--target-json", "/tmp/target.json",
                "--output", "/tmp/output", "--nvbit-tool", "/tmp/tool.so", "--raw-dir", "/tmp/raw",
                "--budget-ledger", "/tmp/ledger.json", "--", "echo", "fixture",
            ]
            args = parse_args("nvbit")
        finally:
            sys.argv = previous
        self.assertTrue(args.diagnostic_only)
        self.assertEqual(args.command, ["echo", "fixture"])


if __name__ == "__main__":
    unittest.main()
