#!/usr/bin/env python3
"""Unit coverage for C15 lane A bounded static-fingerprint primitives."""

import importlib.util
import json
import struct
import sys
import unittest
from pathlib import Path


MODULE = Path(__file__).resolve().parents[4] / "util/vm_tlb/c15/lane_a/static_fingerprint.py"
SPEC = importlib.util.spec_from_file_location("c15_static", MODULE)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


class FakeResponse:
    def __init__(self, status, headers, body, url="https://example.invalid/fixed"):
        self.status = status
        self.headers = headers
        self._body = body
        self._url = url
        self.read_calls = 0

    def getcode(self):
        return self.status

    def read(self, amount=-1):
        self.read_calls += 1
        return self._body if amount < 0 else self._body[:amount]

    def geturl(self):
        return self._url

    def close(self):
        pass


class StaticFingerprintTest(unittest.TestCase):
    def test_contract_fixture_math(self):
        self.assertEqual(dict(M.static_fixture_checks())["T05"], "PASS")

    def test_range_200_is_rejected_before_read(self):
        response = FakeResponse(200, {"Content-Length": "99999999"}, b"never consume")
        with self.assertRaises(M.C15Error):
            M.BoundedHTTP(opener=lambda *_args, **_kwargs: response).range("https://example.invalid/x", 0, 7)
        self.assertEqual(response.read_calls, 0)

    def test_bad_content_range_is_rejected_before_read(self):
        response = FakeResponse(206, {"Content-Range": "bytes 1-8/9", "Content-Length": "8"}, b"12345678")
        with self.assertRaises(M.C15Error):
            M.BoundedHTTP(opener=lambda *_args, **_kwargs: response).range("https://example.invalid/x", 0, 7)
        self.assertEqual(response.read_calls, 0)

    def test_safetensors_header_and_offsets(self):
        header = json.dumps({"weight": {"dtype": "F16", "shape": [2, 4], "data_offsets": [0, 16]}}).encode()
        total = 8 + len(header) + 16
        responses = [
            FakeResponse(206, {"Content-Range": "bytes 0-7/%d" % total, "Content-Length": "8"}, struct.pack("<Q", len(header))),
            FakeResponse(206, {"Content-Range": "bytes 8-%d/%d" % (7 + len(header), total), "Content-Length": str(len(header))}, header),
        ]
        parsed, _prelude, _actual = M.read_safetensors_header(M.BoundedHTTP(opener=lambda *_args, **_kwargs: responses.pop(0)), "https://example.invalid/x")
        self.assertEqual(parsed["weight"]["data_offsets"], [0, 16])

    def test_duplicate_json_and_unresolved_page_boundaries(self):
        with self.assertRaises(M.C15Error):
            M.json_object(b'{"x": 1, "x": 2}', "fixture")
        self.assertEqual(M.pages_for_range(0, 0, 4096), 0)
        self.assertEqual(M.union_bytes([(0, 8), (4, 12)]), 12)


if __name__ == "__main__":
    unittest.main()
