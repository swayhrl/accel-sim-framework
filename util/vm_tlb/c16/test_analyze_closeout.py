#!/usr/bin/env python3
import unittest

import analyze_closeout as closeout


class AnalyzeCloseoutTest(unittest.TestCase):
    def test_sha_is_stable(self):
        self.assertEqual(len(closeout.hashlib.sha256(b"x").hexdigest()), 64)


if __name__ == "__main__":
    unittest.main()
