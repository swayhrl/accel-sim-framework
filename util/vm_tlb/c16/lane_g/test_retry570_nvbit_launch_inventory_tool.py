from __future__ import annotations

import unittest
from pathlib import Path


SOURCE = (Path(__file__).parent / "retry570_nvbit_launch_inventory_tool.cu").read_text()


class LaunchInventoryToolTests(unittest.TestCase):
    def test_direct_inventory_has_no_instruction_or_trace_path(self) -> None:
        for required in ("global_launch_ordinal", "function_mangled_name", "nvbit_get_func_name", "grid", "block"):
            self.assertIn(required, SOURCE)
        for forbidden in ("nvbit_get_instrs", "nvbit_insert_call", "nvbit_enable_instrumented", "cudaDeviceSynchronize"):
            self.assertNotIn(forbidden, SOURCE)


if __name__ == "__main__":
    unittest.main()
