#!/usr/bin/env python3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c16_warp_container import HEADER, MAGIC, RECORD, WarpError, decode_c16warp1


class C16WarpTests(unittest.TestCase):
    def make_binary(self, directory, *, addresses=None, mask=0b11, count=1, extra=b"", magic=MAGIC, static=7, occurrence=0, callbacks=None, overflow=0, record_static=None):
        addresses = addresses or [10, 20] + [999] * 30
        callbacks = count if callbacks is None else callbacks
        record_static = static if record_static is None else record_static
        payload = HEADER.pack(magic, static, occurrence, callbacks, overflow, 1) + RECORD.pack(record_static, mask, 1, 2, 3, 4, *addresses) + extra
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

    def test_valid_record_reports_exact_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            decoded, events = decode_c16warp1(self.make_binary(directory), 7, 0)
            self.assertEqual((decoded["callback_warp_records"], decoded["records_written"], len(events)), (1, 1, 2))

    def test_truncated_header_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.bin"; path.write_bytes(b"C16WARP")
            with self.assertRaises(WarpError): decode_c16warp1(path, 7, 0)

    def test_magic_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(WarpError): decode_c16warp1(self.make_binary(directory, magic=b"BADWARP1"), 7, 0)

    def test_header_static_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(WarpError): decode_c16warp1(self.make_binary(directory, static=8), 7, 0)

    def test_header_occurrence_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(WarpError): decode_c16warp1(self.make_binary(directory, occurrence=1), 7, 0)

    def test_overflow_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(WarpError): decode_c16warp1(self.make_binary(directory, overflow=1), 7, 0)

    def test_callback_count_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(WarpError): decode_c16warp1(self.make_binary(directory, callbacks=2), 7, 0)

    def test_record_static_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(WarpError): decode_c16warp1(self.make_binary(directory, record_static=8), 7, 0)

    def test_truncated_record_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.make_binary(directory)
            path.write_bytes(path.read_bytes()[:-1])
            with self.assertRaises(WarpError): decode_c16warp1(path, 7, 0)


if __name__ == "__main__": unittest.main()
