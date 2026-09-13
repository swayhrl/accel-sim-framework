"""No-GPU tests for Recovery V3 raw-tree copyback closure."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parent
sys.path.insert(0, str(LANE))

from retry570_recovery_v3_tree_transfer import payload_rows, tree_sha  # noqa: E402


class TreeTransferTests(unittest.TestCase):
    def test_payload_rows_are_stable_and_exclude_the_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "nested").mkdir()
            (root / "b").write_bytes(b"two")
            (root / "nested" / "a").write_bytes(b"one")
            manifest = root / "MANIFEST.json"
            manifest.write_text("not a payload", encoding="utf-8")
            rows = payload_rows(root, exclude=manifest)
            self.assertEqual([row["relative_path"] for row in rows], ["b", "nested/a"])
            self.assertEqual(len(tree_sha(rows)), 64)

    def test_closeout_requires_bulk_root_and_exact_named_payloads(self) -> None:
        source = (LANE / "retry570_recovery_v3_tree_transfer.py").read_text(encoding="utf-8")
        for token in ("remote_only_required_artifact_count_after_closure", "local raw root is outside the required bulk root", "all_payloads_size_sha256_identical"):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
