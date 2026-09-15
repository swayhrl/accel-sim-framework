#!/usr/bin/env python3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c16_warp_container import HEADER, MAGIC, RECORD, WarpError, decode_c16warp1


class C16WarpTests(unittest.TestCase):
    def make_binary(self, directory, *, addresses=None, mask=0b11, count=1, extra=b""):
        addresses = addresses or [10, 20] + [999] * 30
        payload = HEADER.pack(MAGIC, 7, 0, count, 0, 1) + RECORD.pack(7, mask, 1, 2, 3, 4, *addresses) + extra
        path = Path(directory) / "mref_7.bin"; path.write_bytes(payload); return path

    def test_active_mask_is_exact_and_inactive_addresses_are_not_synthesized(self):
        with tempfile.TemporaryDirectory() as directory:
            decoded, events = decode_c16warp1(self.make_binary(directory, mask=0b01), 7, 0)
            self.assertEqual(decoded["active_lane_address_events"], 1)
            self.assertEqual(events[0]["address"], 10)

    def test_trailing_and_callback_count_mismatch_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(WarpError): decode_c16warp1(self.make_binary(directory, extra=b"x"), 7, 0)
            with self.assertRaises(WarpError): decode_c16warp1(self.make_binary(directory, count=2), 7, 0)


if __name__ == "__main__": unittest.main()
