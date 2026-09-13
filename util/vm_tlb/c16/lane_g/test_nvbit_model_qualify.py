#!/usr/bin/env python3
"""CPU-only unit tests for the diagnostic-only model NVBit runner guards."""
from __future__ import annotations

import hashlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from c16_native_common import ContractError  # noqa: E402
from nvbit_model_qualify import output_checksum, validate_tool_contract  # noqa: E402


class FakeTokens:
    def __init__(self, values: list[int]) -> None:
        self.values = values

    def detach(self) -> "FakeTokens":
        return self

    def to(self, _device: str) -> "FakeTokens":
        return self

    def flatten(self) -> "FakeTokens":
        return self

    def tolist(self) -> list[int]:
        return self.values


class FakeLogits:
    def __getitem__(self, _item: object) -> "FakeLogits":
        return self

    def argmax(self, *, dim: int) -> FakeTokens:
        self.dim = dim
        return FakeTokens([7])


class ModelQualificationTests(unittest.TestCase):
    def test_baseline_rejects_declared_or_preloaded_tool(self) -> None:
        self.assertEqual(validate_tool_contract("BASELINE", None, None, None)["tool_path"], "NA")
        with self.assertRaises(ContractError):
            validate_tool_contract("BASELINE", None, None, "/tmp/tool.so")

    def test_profile_tool_requires_exact_file_hash_and_preload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tool.so"
            path.write_bytes(b"fixed tool")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            closed = validate_tool_contract("OFFICIAL_MEM_TRACE", path, digest, str(path))
            self.assertEqual(closed["tool_sha256"], digest)
            with self.assertRaises(ContractError):
                validate_tool_contract("OFFICIAL_MEM_TRACE", path, digest, "/wrong/tool.so")
            with self.assertRaises(ContractError):
                validate_tool_contract("OFFICIAL_MEM_TRACE", path, "0" * 64, str(path))

    def test_terminal_token_checksum_is_canonical(self) -> None:
        checksum, values = output_checksum(FakeLogits())
        self.assertEqual(values, [7])
        self.assertEqual(checksum, hashlib.sha256(b"[7]").hexdigest())


if __name__ == "__main__":
    unittest.main()
