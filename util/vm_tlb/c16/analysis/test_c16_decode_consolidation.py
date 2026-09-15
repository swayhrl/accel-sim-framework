#!/usr/bin/env python3
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c16_decode_consolidation import (  # noqa: E402
    DecodeError,
    attribute_same_process_event,
    canonical_sha,
    compare_object_relative,
    output_record,
    semantic_identity,
    verified_context,
)


class DecodeConsolidationTests(unittest.TestCase):
    def context(self):
        return {
            "schema_version": "C16_ADDRESS_CONTEXT_V1",
            "target_id": "T",
            "static_index": "7",
            "function_occurrence": "3",
            "trace_sha256": "a" * 64,
            "static_map_sha256": "b" * 64,
            "model_id": "model",
            "revision": "rev",
            "scenario": "S2_TEXT",
            "process_pid": 10,
            "process_started_monotonic": 1.5,
            "address_space_id": "c" * 64,
            "gpu_uuid": "GPU-1234-abcd",
            "object_map_sha256": "d" * 64,
            "ranges": [],
        }

    def range(self):
        item = {"address_start_hex": "0x1000", "address_end_hex": "0x2000", "class": "KV_CACHE", "runtime_name": "past_key_values[0][0]", "layer": "0", "storage_bytes": 4096, "dtype": "torch.float16", "shape": [1, 2, 16, 64]}
        identity = semantic_identity(item)
        return {**item, "start": 0x1000, "end": 0x2000, "identity": identity, "identity_sha256": canonical_sha(identity)}

    def test_exact_same_process_object_attribution_positive(self):
        context = self.context()
        event = {"address": 0x1080, "address_space_id": context["address_space_id"], "process_pid": context["process_pid"]}
        result = attribute_same_process_event(event, [self.range()], context)
        self.assertEqual(result["object_class"], "KV_CACHE")
        self.assertEqual(result["object_relative_offset"], 0x80)

    def test_cross_process_object_map_rejected(self):
        context = self.context()
        event = {"address": 0x1080, "address_space_id": "e" * 64, "process_pid": 11}
        with self.assertRaisesRegex(DecodeError, "cross-process"):
            attribute_same_process_event(event, [self.range()], context)

    def test_object_relative_normalization_positive(self):
        identity = self.range()["identity"]; digest = canonical_sha(identity)
        early = [{"object_identity": identity, "object_identity_sha256": digest, "object_relative_offset": 128}]
        late = [{"object_identity": identity, "object_identity_sha256": digest, "object_relative_offset": 128}, {"object_identity": identity, "object_identity_sha256": digest, "object_relative_offset": 256}]
        row = compare_object_relative(early, late)[0]
        self.assertEqual(row["relative_offset_set_relation"], "EARLY_SUBSET")

    def test_object_relative_identity_mismatch_fails_closed(self):
        identity = self.range()["identity"]
        event = {"object_identity": identity, "object_identity_sha256": "0" * 64, "object_relative_offset": 1}
        with self.assertRaisesRegex(DecodeError, "identity/offset"):
            compare_object_relative([event], [])

    def test_no_common_identity_is_explicitly_unsupported(self):
        row = compare_object_relative([], [])[0]
        self.assertEqual(row["relative_offset_set_relation"], "UNSUPPORTED_NO_COMMON_ATTRIBUTED_SEMANTIC_IDENTITY")

    def test_address_context_binding_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "context.json"
            data = self.context(); data["trace_sha256"] = "f" * 64
            path.write_text(json.dumps(data), encoding="utf-8")
            shard = {"static_index": 7, "occurrence": 3}
            entry = {"model": "model", "revision": "rev"}
            with self.assertRaisesRegex(DecodeError, "trace_sha256 mismatch"):
                verified_context(path, shard, "T", "a" * 64, "b" * 64, entry)

    def test_derived_output_record_binds_path_size_and_sha(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "output.json"; path.write_text("{}\n", encoding="utf-8")
            record = output_record(path)
            self.assertEqual(record["size_bytes"], 3)
            self.assertEqual(record["sha256"], hashlib.sha256(b"{}\n").hexdigest())
            self.assertEqual(record["path"], str(path.resolve()))


if __name__ == "__main__":
    unittest.main()
