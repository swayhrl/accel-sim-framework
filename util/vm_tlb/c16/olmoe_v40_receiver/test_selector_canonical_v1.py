#!/usr/bin/env python3
"""Synthetic non-authority tests for the 174 selector canonicalizer."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from selector_canonical_v1 import SelectorError, canonicalize_tsv


class SelectorCanonicalV1Tests(unittest.TestCase):
    def write(self, directory: Path, name: str, text: str) -> Path:
        path = directory / name
        path.write_text(text, encoding="utf-8", newline="")
        return path

    def test_order_invariant_and_field_sensitive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            first = self.write(directory, "a.tsv", "opcode\tstatic_index\npc2\t0x2\npc1\t1\n")
            reordered = self.write(directory, "b.tsv", "opcode\tstatic_index\npc1\t1\npc2\t0x2\n")
            changed = self.write(directory, "c.tsv", "opcode\tstatic_index\npcX\t1\npc2\t0x2\n")
            self.assertEqual(canonicalize_tsv(first)[1]["canonical_sha256"], canonicalize_tsv(reordered)[1]["canonical_sha256"])
            self.assertNotEqual(canonicalize_tsv(first)[1]["canonical_sha256"], canonicalize_tsv(changed)[1]["canonical_sha256"])

    def test_duplicate_static_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write(Path(temporary), "duplicate.tsv", "static_index\tx\n1\ta\n0x1\tb\n")
            with self.assertRaises(SelectorError):
                canonicalize_tsv(path)

    def test_missing_and_extra_fields_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            missing = self.write(directory, "missing.tsv", "static_index\tx\n1\n")
            extra = self.write(directory, "extra.tsv", "static_index\tx\n1\ta\nb\n")
            with self.assertRaises(SelectorError):
                canonicalize_tsv(missing)
            with self.assertRaises(SelectorError):
                canonicalize_tsv(extra)


if __name__ == "__main__":
    unittest.main()
