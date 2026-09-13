#!/usr/bin/env python3
"""Source-only guard for the frozen-NVBit timing probe build contract."""
from __future__ import annotations

import unittest
from pathlib import Path


SOURCE = (Path(__file__).resolve().parent / "retry570_build_nvbit_timing_probe.sh").read_text(encoding="utf-8")


class BuildTimingProbeTests(unittest.TestCase):
    def test_uses_official_makefile_and_special_injection_filename(self) -> None:
        self.assertIn("tools/instr_count_bb/Makefile", SOURCE)
        self.assertIn("inject_funcs.cu", SOURCE)
        self.assertIn("NVBIT_PATH=\"${release_root}/core\"", SOURCE)
        self.assertIn("ARCH=sm_86", SOURCE)

    def test_refuses_overwrite_and_emits_tool_hash(self) -> None:
        self.assertIn("refusing to overwrite output directory", SOURCE)
        self.assertIn("sha256sum", SOURCE)


if __name__ == "__main__":
    unittest.main()
