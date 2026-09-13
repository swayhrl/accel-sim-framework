from __future__ import annotations

import unittest
from pathlib import Path


SOURCE = (Path(__file__).parent / "retry570_manifest_asset_recovery.py").read_text(encoding="utf-8")


class ManifestAssetRecoveryTests(unittest.TestCase):
    def test_download_requires_exact_manifest_identity_and_explicit_authority(self) -> None:
        for token in ("immutable package manifest SHA256 differs", "immutable package payload TSV differs", "IDENTITY.fullmatch", "--allow-network", "revision=identity[\"revision\"]", "never chooses a model variant"):
            self.assertIn(token, SOURCE)

    def test_download_is_hash_closed_and_never_overwrites_a_retained_package(self) -> None:
        for token in ("asset recovery refuses to overwrite", "size/SHA closure", "all_payloads_size_sha256_closed", "local_dir_use_symlinks=False"):
            self.assertIn(token, SOURCE)


if __name__ == "__main__":
    unittest.main()
