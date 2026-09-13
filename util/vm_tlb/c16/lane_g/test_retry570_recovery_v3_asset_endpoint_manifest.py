"""No-GPU tests for compact Recovery-V3 asset endpoint enumeration."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SOURCE = Path(__file__).with_name("retry570_recovery_v3_asset_endpoint_manifest.py")
SPEC = importlib.util.spec_from_file_location("asset_endpoint_manifest", SOURCE)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AssetEndpointManifestTest(unittest.TestCase):
    def test_rows_are_filename_size_sha_and_exclude_output(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "b.bin").write_bytes(b"bb")
            (root / "a.json").write_bytes(b"a")
            output = root / "REMOTE_MANIFEST.json"
            output.write_text("placeholder", encoding="utf-8")
            values = MODULE.rows(root, output)
        self.assertEqual([row["filename"] for row in values], ["a.json", "b.bin"])
        self.assertEqual([row["size_bytes"] for row in values], [1, 2])
        self.assertTrue(all(len(str(row["sha256"])) == 64 for row in values))


if __name__ == "__main__":
    unittest.main()
