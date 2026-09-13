#!/usr/bin/env python3
"""Ensure the final Retry570 static-map discriminator remains lifecycle-free."""
from __future__ import annotations

import unittest
from pathlib import Path


SOURCE = Path(__file__).with_name("retry570_exact_map_only_tool.cu")


class ExactMapOnlyToolTests(unittest.TestCase):
    def test_tool_has_no_context_allocation_or_instrumentation_path(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("void nvbit_at_ctx_init", source)
        self.assertNotIn("void nvbit_tool_init", source)
        self.assertNotIn("cudaMalloc", source)
        self.assertNotIn("nvbit_insert_call", source)

    def test_tool_requires_exact_mangled_identity_before_instruction_enumeration(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        event = source[source.index("void nvbit_at_cuda_event"):]
        self.assertLess(event.index("target_function_mangled !="), event.index("emit_map(context, function)"))
        emit = source[source.index("static void emit_map"):source.index("void nvbit_at_init")]
        self.assertIn("nvbit_get_instrs(context, function)", emit)
        self.assertIn("libtorch_cuda_sha256", emit)
        self.assertIn("has_mref", emit)

    def test_launch_callback_uses_the_nvbit_parameter_layout_for_each_launch_abi(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        extract = source[source.index("static bool extract_launch_function"):source.index("static void emit_map")]
        self.assertIn("static_cast<cuLaunch_params*>(parameters)->f", extract)
        self.assertIn("static_cast<cuLaunchKernel_params*>(parameters)->f", extract)
        self.assertIn("static_cast<cuLaunchKernelEx_params*>(parameters)->f", extract)


if __name__ == "__main__":
    unittest.main()
