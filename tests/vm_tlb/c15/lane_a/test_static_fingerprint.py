#!/usr/bin/env python3
"""Unit coverage for C15 lane A bounded static-fingerprint primitives."""

import importlib.util
import json
import struct
import sys
import tempfile
import unittest
import urllib.error
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

    def test_416_and_disconnect_are_bounded_failures(self):
        response = FakeResponse(416, {"Content-Length": "0"}, b"")
        with self.assertRaises(M.C15Error):
            M.BoundedHTTP(opener=lambda *_args, **_kwargs: response).range("https://example.invalid/x", 0, 7)
        self.assertEqual(response.read_calls, 0)
        with self.assertRaises(M.C15Error):
            M.BoundedHTTP(opener=lambda *_args, **_kwargs: (_ for _ in ()).throw(urllib.error.URLError("fixture disconnect")), retries=1).range("https://example.invalid/x", 0, 7)

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

    def test_shards_never_share_the_same_offset_namespace(self):
        rows = [
            {"shard": "a", "storage_dtype": "F16", "disk_data_start": "0", "disk_data_end": "16"},
            {"shard": "b", "storage_dtype": "F16", "disk_data_start": "0", "disk_data_end": "16"},
        ]
        self.assertEqual(M.physical_bytes_by_dtype(rows)[0]["physical_bytes"], 32)
        self.assertEqual(sum(M.page_union_count(ranges, 4096) for ranges in {"a": [(0, 16)], "b": [(0, 16)]}.values()), 2)

    def test_tsv_write_is_atomic_and_normalizes_missing_to_na(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "small.tsv"
            M.tsv_write(target, ["id", "value"], [{"id": "one", "value": None}])
            self.assertFalse(target.with_name("small.tsv.tmp").exists())
            self.assertEqual(target.read_text(encoding="utf-8").splitlines()[1], "one\tNA")

    def test_quantized_payload_is_not_misclassified_as_unknown(self):
        self.assertEqual(M.role_for_tensor("model.layers.0.mlp.up_proj.qweight"), "WEIGHT_QUANTIZED_PACKED")
        self.assertEqual(M.extract_weight_dtype([
            {"role": "WEIGHT_QUANTIZED_PACKED", "storage_dtype": "I32"},
            {"role": "WEIGHT_NORM", "storage_dtype": "F16"},
        ]), "MIXED:F16,I32")

    def test_revision_and_authorization_guards_reject_bad_requests(self):
        M.require_immutable_resolve_url("https://example.invalid/m/resolve/0123456789abcdef0123456789abcdef01234567/config.json", "0123456789abcdef0123456789abcdef01234567")
        with self.assertRaises(M.C15Error):
            M.require_immutable_resolve_url("https://example.invalid/m/resolve/main/config.json", "0123456789abcdef0123456789abcdef01234567")
        for operation in ("full_weight_download", "new_simulator_replay", "gpu_profile"):
            with self.assertRaises(M.C15Error):
                M.assert_authorized_operation(operation, 1)

    def test_integration_manifest_declares_only_fixed_hash_bound_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            integration = root / "integration"
            integration.mkdir()
            (integration / "INTEGRATION_RECEIPT.json").write_text("{}\n", encoding="utf-8")
            M.write_static_publish_manifest(root)
            manifest = json.loads((root / "PUBLISH_MANIFEST.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["run_id"], "c15-a-integration-20260912")
            self.assertTrue({"C15-5.1", "C15-5.2", "C15-5.4"}.issubset(manifest["ready_stage_ids"]))
            sources = {item["name"]: item for item in manifest["input_sources"]}
            self.assertEqual(sources["LANE_B_PUBLISH"]["read_policy"], "READ_ONLY_FIXED_COMMIT_HASH_BOUND")
            self.assertEqual(sources["LANE_C_PUBLISH"]["read_policy"], "READ_ONLY_FIXED_COMMIT_HASH_BOUND")
            M.verify_publish_manifest(root)


if __name__ == "__main__":
    unittest.main()
