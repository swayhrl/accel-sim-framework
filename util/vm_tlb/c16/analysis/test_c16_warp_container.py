#!/usr/bin/env python3
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c16_warp_container import HEADER, MAGIC, RECORD, WarpError, decode_c16warp1, ingest_container, sha256, static_access_kind, validated_static_width_bytes


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

    def test_static_access_kind_keeps_known_load_and_store_distinct(self):
        load = {"opcode": "LDG.E", "is_load": "1", "is_store": "0", "sass": "LDG.E R0, [R2] ;"}
        store = {"opcode": "STG.E", "is_load": "0", "is_store": "1", "sass": "STG.E [R2], R0 ;"}
        self.assertEqual(static_access_kind(load), "READ")
        self.assertEqual(static_access_kind(store), "WRITE")
        self.assertNotEqual(static_access_kind(load), static_access_kind(store))

    def test_static_access_kind_never_defaults_ambiguous_metadata(self):
        self.assertEqual(static_access_kind({"opcode": "LDG.E", "is_load": "0", "is_store": "0"}), "UNKNOWN_ACCESS_KIND")
        self.assertEqual(static_access_kind({"opcode": "STG.E", "is_load": "1", "is_store": "1"}), "UNKNOWN_ACCESS_KIND")
        self.assertEqual(static_access_kind({"opcode": "ATOM.E", "is_load": "1", "is_store": "1"}), "ATOMIC")

    def test_width_requires_validated_matching_static_sass_mnemonic(self):
        exact = {"opcode": "STG.E.128", "sass": "@P1 STG.E.128 [R2], R8 ;"}
        mismatch = {"opcode": "STG.E.128", "sass": "STG.E.64 [R2], R8 ;"}
        bare = {"opcode": "STG.E", "sass": "STG.E [R2], R8 ;"}
        self.assertEqual(validated_static_width_bytes(exact), 16)
        self.assertIsNone(validated_static_width_bytes(mismatch))
        self.assertIsNone(validated_static_width_bytes(bare))

    def test_generic_ingest_keeps_replay_union_diagnostic_and_object_join_disabled(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); run_id = "C16R_generic"; raw = root / "raw" / run_id; shards_dir = raw / "raw_shards"
            shards_dir.mkdir(parents=True)
            selected = [7, 8]; shard_rows = []
            for index, address in [(7, 0x1000), (8, 0x2000)]:
                payload = HEADER.pack(MAGIC, index, 0, 1, 0, 1) + RECORD.pack(index, 1, 0, 0, 0, 0, address, *([999] * 31))
                binary = shards_dir / f"mref_{index}.bin"; binary.write_bytes(payload)
                log = shards_dir / f"mref_{index}.stdout.log"; log.write_text(f"C16_WARP_TERMINAL static={index} occurrence=0 records=1 overflow=0\n", encoding="utf-8")
                shard_rows.append({"static_index": index, "occurrence": 0, "records": 1, "overflow": 0, "file": binary.name, "bytes": binary.stat().st_size, "sha256": sha256(binary)})
            logical = {"schema_version": "C16_V2_MREF_SHARDED_COMPLETE_SET_V1", "static_global_mref_set": selected, "shards": shard_rows}
            (raw / "WARP_SHARD_MANIFEST.json").write_text(json.dumps(logical), encoding="utf-8")
            static_header = "nvbit_static_index\topcode\tis_load\tis_store\thas_mref\tsass\tmemory_space\n"
            static_rows = "7\tSTG.E\t0\t1\t1\tSTG.E [R2], R0 ;\tGLOBAL\n8\tSTG.E\t0\t1\t1\tSTG.E [R2], R0 ;\tGLOBAL\n"
            (raw / "STATIC_MREF_MAP.tsv").write_text(static_header + static_rows, encoding="utf-8")
            # Deliberately matching container-level ranges must not be used for
            # per-replay attribution without same-process context evidence.
            (raw / "OBJECT_MAP.json").write_text(json.dumps({"ranges": [{"address_start_hex": "0x1000", "address_end_hex": "0x3000", "class": "WEIGHT"}]}), encoding="utf-8")
            artifacts = []
            for path in sorted(raw.rglob("*")):
                if path.is_file():
                    artifacts.append({"relative_path": str(path.relative_to(raw)), "size_bytes": path.stat().st_size, "sha256": sha256(path)})
            manifest = raw / "RUN_MANIFEST.json"; manifest.write_text(json.dumps({"artifacts": artifacts}), encoding="utf-8")
            manifest_sha = sha256(manifest); entries = root / "catalog" / "entries"; entries.mkdir(parents=True)
            (entries / f"{run_id}.json").write_text(json.dumps({"raw_path": str(raw), "raw_manifest_sha256": manifest_sha}), encoding="utf-8")
            static_sha = hashlib.sha256(json.dumps(selected, separators=(",", ":")).encode()).hexdigest()
            result = ingest_container(root, run_id, manifest_sha, static_sha, 2, "parser", "producer", ["test"])
            fingerprint = result["fingerprint"]
            self.assertEqual(fingerprint["absolute_va_aggregate_semantics"], "REPLAY_UNION_DIAGNOSTIC")
            self.assertEqual(fingerprint["cross_shard_object_union"], "UNSUPPORTED")
            self.assertEqual(fingerprint["object_attribution"], {"UNKNOWN_RUNTIME": 2})
            receipt = json.loads(Path(result["receipt"]).read_text(encoding="utf-8"))
            self.assertIn("created_at_utc", receipt)
            self.assertEqual(receipt["parser_config"]["cross_shard_absolute_va"], "REPLAY_UNION_DIAGNOSTIC")
            for item in receipt["outputs"]:
                path = Path(item["path"])
                self.assertEqual((path.stat().st_size, sha256(path)), (item["size_bytes"], item["sha256"]))


if __name__ == "__main__": unittest.main()
