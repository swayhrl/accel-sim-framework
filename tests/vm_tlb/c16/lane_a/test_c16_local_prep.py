import unittest

from util.vm_tlb.c16.lane_a.c16_local_prep import canonical_json_bytes, repeat_to_length, selftest


class C16LocalPrepTests(unittest.TestCase):
    def test_repeat_then_trim_is_deterministic(self):
        self.assertEqual(repeat_to_length([7, 9], 5), [7, 9, 7, 9, 7])

    def test_empty_source_is_rejected(self):
        with self.assertRaises(ValueError):
            repeat_to_length([], 128)

    def test_canonical_token_encoding(self):
        self.assertEqual(canonical_json_bytes([1, 2]), b"[1,2]")

    def test_builtin_selftest(self):
        self.assertEqual(selftest(), [])
