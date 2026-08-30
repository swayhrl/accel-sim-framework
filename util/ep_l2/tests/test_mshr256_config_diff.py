#!/usr/bin/env python3
"""Fail closed unless each Lane-E MSHR256 overlay changes only Line-MSHRs."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
CONFIGS = (
    ("b0_banked_850.config", "b0_banked_mshr256_850.config"),
    ("b0_banked_d512_850.config", "b0_banked_d512_mshr256_850.config"),
)


def options(path: Path):
    return [line.strip() for line in path.read_text().splitlines()
            if line.strip() and not line.lstrip().startswith("#")]


class Mshr256ConfigDiffTest(unittest.TestCase):
    def test_line_mshr_is_the_only_modeled_delta(self):
        for baseline_name, mshr256_name in CONFIGS:
            baseline = options(ROOT / "tests/ep_l2" / baseline_name)
            mshr256 = options(ROOT / "tests/ep_l2" / mshr256_name)
            self.assertEqual(len(baseline), len(mshr256))
            delta = [(old, new) for old, new in zip(baseline, mshr256)
                     if old != new]
            self.assertEqual(delta, [
                ("-gpgpu_cache:dl2 S:64:128:16,L:B:m:L:P,A:128:1,128:0,32",
                 "-gpgpu_cache:dl2 S:64:128:16,L:B:m:L:P,A:256:1,128:0,32")
            ])


if __name__ == "__main__":
    unittest.main()
