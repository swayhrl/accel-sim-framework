#!/usr/bin/env python3
"""Source-level guards for Retry570's exact-function NVBit mapper fast path."""
from __future__ import annotations

import unittest
from pathlib import Path


SOURCE = Path(__file__).with_name("retry570_targeted_memory_tool.cu")


class TargetedMapperSourceTests(unittest.TestCase):
    def test_makefile_preserves_relocatable_device_code_for_mref_helper(self) -> None:
        makefile = Path(__file__).with_name("Makefile.retry570_targeted_memory_tool").read_text(encoding="utf-8")
        target = makefile.index("retry570_targeted_memory_tool.o:")
        body = makefile[target:makefile.index("retry570_targeted_memory_inject.o:", target)]
        self.assertIn("-dc", body)

    def test_map_only_tool_init_does_not_allocate_cuda_memory(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        begin = source.index("void nvbit_tool_init")
        body = source[begin:source.index("void nvbit_at_cuda_event", begin)]
        self.assertIn("if (!trace_enabled) return;", body)
        self.assertLess(body.index("if (!trace_enabled) return;"), body.index("cudaMallocManaged"))

    def test_nonlaunch_and_cached_nontarget_paths_precede_target_mutex(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        begin = source.index("void nvbit_at_cuda_event")
        body = source[begin:source.index("void nvbit_at_ctx_term", begin)]
        self.assertLess(body.index("if (!extract_launch_function"), body.index("pthread_mutex_lock(&mutex)"))
        self.assertIn("classify_function(context, function) != FunctionClassification::TARGET) return", body)


if __name__ == "__main__":
    unittest.main()
