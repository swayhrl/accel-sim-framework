#!/usr/bin/env python3
"""Pass/mismatch fixtures for the selected Parboil Python-3 checker adapter."""

import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("verify_m5_extended_parboil_output.py")
SPEC = importlib.util.spec_from_file_location("extended_parboil_checker", MODULE_PATH)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class ParboilCheckerTests(unittest.TestCase):
    def write(self, directory, name, data):
        path = directory / name
        if isinstance(data, str):
            path.write_text(data, encoding="utf-8")
        else:
            path.write_bytes(data)
        return path

    def assert_pass_and_mismatch(self, workload, passing, failing):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            reference = self.write(directory, "reference", passing)
            good = self.write(directory, "good", passing)
            bad = self.write(directory, "bad", failing)
            CHECKER.check(workload, reference, good)
            with self.assertRaises(CHECKER.Mismatch):
                CHECKER.check(workload, reference, bad)

    def test_bfs(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            reference = self.write(directory, "reference", "1\n1.0\n2.0 3.0\n")
            good = self.write(directory, "good", "1.0\n2.0 3.0\n")
            bad = self.write(directory, "bad", "1.0\n2.0 4.0\n")
            CHECKER.check("bfs", reference, good)
            with self.assertRaises(CHECKER.Mismatch):
                CHECKER.check("bfs", reference, bad)

    def test_cutcp(self):
        passing = struct.pack("<fI2f", 1.0, 1, 1.0, 2.0)
        failing = struct.pack("<fI2f", 2.0, 1, 1.0, 2.0)
        self.assert_pass_and_mismatch("cutcp", passing, failing)

    def test_histo(self):
        self.assert_pass_and_mismatch("histo", b"exact", b"different")

    def test_mri_q(self):
        passing = struct.pack("<I2f", 1, 1.0, 2.0)
        failing = struct.pack("<I2f", 1, 2.0, 2.0)
        self.assert_pass_and_mismatch("mri-q", passing, failing)

    def test_sad(self):
        body = struct.pack("<I", 0) + (b"\0\0" * (41 * 1089))
        passing = struct.pack("<I", 1) + body
        failing = passing[:-1] + b"\1"
        self.assert_pass_and_mismatch("sad", passing, failing)

    def test_stencil(self):
        passing = struct.pack("i4f", 4, 1.0, 2.0, 3.0, 4.0)
        failing = struct.pack("i4f", 4, 2.0, 2.0, 3.0, 4.0)
        self.assert_pass_and_mismatch("stencil", passing, failing)


if __name__ == "__main__":
    unittest.main()
