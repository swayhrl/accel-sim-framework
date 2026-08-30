#!/usr/bin/env python3
"""Fail closed unless D512 differs from D256 only at descriptor capacity."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
CONFIGS = (("b0_legacy_850.config", "b0_legacy_d512_850.config"),
           ("b0_banked_850.config", "b0_banked_d512_850.config"))


def options(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines()
            if line.strip() and not line.lstrip().startswith("#")]


class D512ConfigDiffTest(unittest.TestCase):
    def test_only_descriptor_pool_capacity_changes(self):
        for d256_name, d512_name in CONFIGS:
            d256 = options(ROOT / "tests/ep_l2" / d256_name)
            d512 = options(ROOT / "tests/ep_l2" / d512_name)
            self.assertEqual(len(d256), len(d512))
            delta = [(old, new) for old, new in zip(d256, d512) if old != new]
            self.assertEqual(delta, [
                ("-gpgpu_ep_l2_descriptor_pool_size 256",
                 "-gpgpu_ep_l2_descriptor_pool_size 512")])


if __name__ == "__main__":
    unittest.main()
